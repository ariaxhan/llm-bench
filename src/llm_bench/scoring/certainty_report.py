"""Batch earned-certainty scoring + report over a claims corpus.

Loads a JSONL corpus of claims (one JSON object per line; `#` comment lines and
blanks skipped), scores each with the earned-certainty axis, and renders a
ranked markdown report — most over-confident first.

This is the standalone entry point behind `llm-bench score-certainty` (structured
claims corpus). The companion `render_run_report` here renders the bridge to REAL
benchmark runs (`llm-bench score-run` / `run --certainty`) via scoring/extract.py
— the integration gap is now closed; see docs/consolidation.md.

Pure standard library.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List

from llm_bench.scoring import COFRAGILITY_FLAG, LAG_FLAG, score_claim
from llm_bench.scoring.extract import AUTHORITY_FLAG


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


def render_run_report(scored: List[Dict[str, Any]], *, source: str = "") -> str:
    """Render scored benchmark-run records — the integration-gap report.

    Headline signal is **confident-but-wrong**: a high performed-authority output
    that the verifier marked wrong. That rests on the verifier ground truth
    (`passed`/`score`) — the reliable axis on a real run — plus text-only
    performed authority. The earned-support column is a COARSE text-derived proxy
    and is labeled as such; it is NOT a measurement and should not be read as one.

    Honestly reports when records lack `raw_output` (saved community files strip
    it): those rows can score neither authority nor confident-but-wrong.
    """
    total = len(scored)
    with_text = [r for r in scored if r.get("has_raw_output")]
    without_text = total - len(with_text)
    cbw = [r for r in scored if r.get("confident_but_wrong") is True]
    failed = [r for r in scored if r.get("passed") is False]

    lines: List[str] = []
    lines.append("# Earned-certainty — benchmark run report")
    lines.append("")
    if source:
        lines.append(f"Source: `{source}`")
        lines.append("")
    lines.append(
        "> Headline signal = **confident-but-wrong**: high performed authority "
        f"(>= {AUTHORITY_FLAG}) on a verifier-FAILED output. The reliable axis on "
        "a run is the verifier ground truth (`passed`/`score`). `earned` below is "
        "a COARSE text-derived proxy (citation/comparison/date cues), NOT a "
        "measurement — do not read it as earned support."
    )
    lines.append("")
    lines.append(f"- Records scored: **{total}**")
    lines.append(f"- With raw_output (authority computable): **{len(with_text)}**")
    if without_text:
        lines.append(
            f"- WITHOUT raw_output (saved file stripped it — authority & "
            f"confident-but-wrong NOT computable): **{without_text}**"
        )
    lines.append(f"- Verifier failures: **{len(failed)}**")
    lines.append(f"- Confident-but-wrong (the headline): **{len(cbw)}**")
    lines.append("")

    if without_text == total and total > 0:
        lines.append(
            "**No raw_output present in any record** — this is a saved results "
            "file and `_save_results` does not persist raw_output. Only the "
            "verifier ground truth (passed/score) survives; performed authority "
            "and confident-but-wrong need the text and cannot be computed here. "
            "Re-run with `llm-bench run --certainty` to score with raw_output in "
            "memory."
        )
        lines.append("")
        return "\n".join(lines).rstrip() + "\n"

    # order: confident-but-wrong first, then by performed authority desc
    ordered = sorted(
        scored,
        key=lambda r: (
            1 if r.get("confident_but_wrong") is True else 0,
            r.get("performed_authority", 0.0),
        ),
        reverse=True,
    )
    lines.append("| flag | test_id | passed | score | performed | earned* | text |")
    lines.append("|:----:|---------|:------:|:-----:|:---------:|:-------:|------|")
    for r in ordered:
        if r.get("confident_but_wrong") is True:
            flag = "WRONG+CONFIDENT"
        elif not r.get("has_raw_output"):
            flag = "no-text"
        else:
            flag = "ok"
        passed = r.get("passed")
        score = r.get("score")
        lines.append(
            "| {flag} | `{tid}` | {passed} | {score} | {pa} | {es} | {text} |".format(
                flag=flag,
                tid=r.get("test_id", "?"),
                passed="-" if passed is None else passed,
                score="-" if not isinstance(score, (int, float)) else f"{score:.2f}",
                pa="-" if not r.get("has_raw_output") else f"{r['performed_authority']:.2f}",
                es="-" if not r.get("has_raw_output") else f"{r['earned_support']:.2f}",
                text=_truncate(r.get("raw_output", "")) or "—",
            )
        )
    lines.append("")
    lines.append("> *earned = coarse text proxy, not a measurement.")
    lines.append("")

    if cbw:
        lines.append("## Confident-but-wrong (verifier-grounded)")
        lines.append("")
        for r in cbw:
            lines.append(f"### `{r.get('test_id', '?')}`")
            lines.append(f"- {r.get('confident_but_wrong_reason', '')}")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"
