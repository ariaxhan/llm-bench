"""Batch earned-certainty scoring + report over a claims corpus.

Loads a JSONL corpus of claims (one JSON object per line; `#` comment lines and
blanks skipped), scores each with the earned-certainty axis, and renders a
ranked markdown report — most over-confident first.

This is the standalone entry point behind `llm-bench score-certainty`. It runs
on a structured claims corpus, NOT yet on raw llm-bench task outputs — those do
not carry the provenance / evidence / baseline fields the scorer reads. See
docs/consolidation.md for the integration gap.

Pure standard library.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List

from llm_bench.scoring import COFRAGILITY_FLAG, LAG_FLAG, score_claim


def default_corpus_path() -> str:
    """Repo-bundled canonical corpus, derived from this file's location.

    Lives under tests/fixtures/ — it is the hand-built demo/validation corpus
    (8 claims with known expected separation), not user data.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(here, "..", "..", ".."))
    return os.path.join(repo_root, "tests", "fixtures", "earned_certainty_claims.jsonl")


def load_claims(path: str) -> List[Dict[str, Any]]:
    """Load claims from a JSONL file (`#` comments and blank lines skipped)."""
    claims: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                claims.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{lineno}: invalid JSON: {exc}") from exc
    return claims


def score_corpus(claims: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Score every claim; carries claim_id + raw_output through for reporting."""
    results = []
    for c in claims:
        r = score_claim(c)
        r["claim_id"] = c.get("claim_id", "?")
        r["raw_output"] = c.get("raw_output", "")
        r["note"] = c.get("note")
        results.append(r)
    return results


def _truncate(text: str, n: int = 56) -> str:
    text = " ".join(str(text).split())
    return text if len(text) <= n else text[: n - 1] + "…"


def render_report(results: List[Dict[str, Any]]) -> str:
    """Render scored claims to a ranked markdown report (most over-confident first).

    `authority_support_lag` is the PRIMARY sort key — the pure performed-earned
    gap. `cofragility` is shown alongside as a separate integer amplifier, never
    folded into the lag.
    """
    ordered = sorted(results, key=lambda r: r["authority_support_lag"], reverse=True)
    flagged = [r for r in ordered if r["overconfident"]]

    lines: List[str] = []
    lines.append("# Earned-certainty report")
    lines.append("")
    lines.append(
        "> `authority_support_lag = performed_authority - earned_support` "
        "(PRIMARY, [-1,1]); `cofragility` is a SEPARATE integer amplifier (0-12) "
        "— never folded into the lag. Risk flag = lag >= "
        f"{LAG_FLAG:.2f} OR cofragility >= {COFRAGILITY_FLAG}."
    )
    lines.append("")
    lines.append(f"- Claims scored: **{len(ordered)}**")
    lines.append(f"- Overconfidence risks flagged: **{len(flagged)}**")
    lines.append("")
    lines.append("| risk | claim_id | performed | earned | lag | cofrag | claim |")
    lines.append("|:----:|----------|:---------:|:------:|:---:|:------:|-------|")
    for r in ordered:
        flag = "RISK" if r["overconfident"] else "ok"
        lines.append(
            "| {flag} | `{cid}` | {pa:.2f} | {es:.2f} | **{lag:+.2f}** | {cof} | {claim} |".format(
                flag=flag,
                cid=r["claim_id"],
                pa=r["performed_authority"],
                es=r["earned_support"],
                lag=r["authority_support_lag"],
                cof=r["cofragility"],
                claim=_truncate(r["raw_output"]),
            )
        )
    lines.append("")

    if flagged:
        lines.append("## Flagged claims")
        lines.append("")
        for r in flagged:
            lines.append(f"### `{r['claim_id']}`  (lag {r['authority_support_lag']:+.2f}, "
                         f"cofragility {r['cofragility']})")
            inds = r.get("cofragility_indicators") or []
            if inds:
                lines.append(f"- co-active indicators: {', '.join(inds)}")
            if r.get("note"):
                lines.append(f"- note: {r['note']}")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"
