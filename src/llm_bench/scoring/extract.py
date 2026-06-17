"""Bridge a real `llm-bench run` result onto the earned-certainty scorer.

This is the integration layer the consolidation note called a gap. A benchmark
result (`TestResult`, or a per-test dict from a saved results file) does NOT
carry the structured provenance/evidence/baseline fields the earned-certainty
scorer reads. This module maps what a run *does* carry onto a scorer claim:

  - `raw_output` (when present)   -> passthrough; drives `performed_authority`
                                     (text-only, works without any extra fields).
  - verifier `passed` / `score`   -> the STRONG, reliable axis: llm-bench's own
                                     ground truth on whether the output was right.
  - a few COARSE text-derived support cues (citations, comparison language,
    date cues) -> a weak supplement to `earned_support`, explicitly labeled
    coarse. NOT a measurement.

Honesty discipline (load-bearing — see docs/metrics-hygiene.md):
The reliable signal on a benchmark run is the verifier ground truth, not the
text-derived support. The support cues here are heuristics over raw text; they
are a coarse proxy, never dressed as a measured `earned_support`. Genuinely
undeterminable fields — `instrument_type`, `faithfulness_class`, `fitting_factor`
— are LEFT AT THE SCORER'S NEUTRAL DEFAULTS BY DESIGN, not guessed. The unique
product signal this bridge unlocks is *confident-but-wrong*: a high performed
authority on an output the verifier marked wrong.

Pure standard library.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from llm_bench.scoring import score_claim

# Confident-but-wrong thresholds. The verifier verdict (`passed`) is the
# ground-truth axis; performed authority (text-only) is the discriminator that
# separates a confident wrong answer from an appropriately-hedged wrong answer.
# Boolean `passed` is the primary "wrong" signal because it IS the verifier's
# actual verdict; `SCORE_FLOOR` gives a tunable numeric fallback for partial
# scores when a caller prefers a cutoff over the boolean.
AUTHORITY_FLAG = 0.45     # performed authority at/above this reads as "confident"
SCORE_FLOOR = 0.5         # score at/below this reads as "wrong" when used

# --- coarse text-derived support cues (a weak proxy, NOT a measurement) ------

# Citation / provenance cues: bracketed refs, URLs, "according to", DOIs, "[1]".
_CITATION_PATTERNS = (
    re.compile(r"\[\d+\]"),                       # [1], [23]
    re.compile(r"https?://"),                     # URLs
    re.compile(r"\baccording to\b", re.I),
    re.compile(r"\bcit(?:ed|ation|es)\b", re.I),
    re.compile(r"\bsource[:s]?\b", re.I),
    re.compile(r"\bper the\b", re.I),
    re.compile(r"\bdoi[:/]", re.I),
    re.compile(r"\bRFC\s*\d+", re.I),
)

# Baseline / comparison cues — was the claim set against an incumbent?
_BASELINE_PATTERNS = (
    re.compile(r"\bcompared to\b", re.I),
    re.compile(r"\bcompared with\b", re.I),
    re.compile(r"\bvs\.?\b", re.I),
    re.compile(r"\bversus\b", re.I),
    re.compile(r"\bbaseline\b", re.I),
    re.compile(r"\brelative to\b", re.I),
    re.compile(r"\bin comparison\b", re.I),
    re.compile(r"\bbenchmark(?:ed)?\b", re.I),
)

# Freshness cues — explicit "as of <year>" / standalone modern years.
_FRESHNESS_AS_OF = re.compile(r"\bas of\s+(?:\w+\s+)?(20\d{2})\b", re.I)
_FRESHNESS_YEAR = re.compile(r"\b(20\d{2})\b")


def _count_hits(text: str, patterns) -> int:
    return sum(1 for p in patterns if p.search(text))


def _coarse_provenance_depth(text: str) -> int:
    """COARSE proxy: number of distinct citation-style cues found in the text.

    Capped at 3 (the scorer saturates provenance at depth 3). This counts
    *surface cues*, not verified sources — a model can fabricate a `[1]`.
    """
    return min(_count_hits(text, _CITATION_PATTERNS), 3)


def _coarse_baseline_used(text: str) -> bool:
    """COARSE proxy: did the text use any comparison/baseline language?"""
    return _count_hits(text, _BASELINE_PATTERNS) > 0


def _coarse_freshness(text: str) -> Optional[float]:
    """COARSE proxy: explicit recency cues -> a freshness hint in [0,1], else None.

    "as of <recent year>" is the strongest cue; a bare recent year is weaker.
    Returns None when there is no date cue at all, so the scorer keeps its own
    neutral default rather than us inventing a number.
    """
    m = _FRESHNESS_AS_OF.search(text)
    if m:
        return 0.85
    years = _FRESHNESS_YEAR.findall(text)
    if years:
        # any explicit year is a mild freshness signal; recent ones a bit more
        newest = max(int(y) for y in years)
        return 0.7 if newest >= 2024 else 0.5
    return None


def result_to_claim(record: Dict[str, Any], *, claim_id: str = "") -> Dict[str, Any]:
    """Map a run result record (dict) onto an earned-certainty scorer claim.

    `record` is a per-test result dict: at minimum `test_id`, `score`, `passed`;
    `raw_output` when the run kept it in memory (saved community files STRIP it,
    see _save_results in cli.py). Returns a claim dict ready for `score_claim`.

    What this honestly derives:
      - raw_output passthrough (drives performed_authority; text-only).
      - COARSE support cues from raw_output: provenance_depth (citation cues),
        baseline_used (comparison language), source_freshness (date cues).
    What it deliberately LEAVES NEUTRAL (the scorer's defaults):
      - instrument_type, faithfulness_class, fitting_factor, conflict_level —
        genuinely undeterminable from a task output; guessing them would fake
        precision. The scorer falls back to ~0.5 neutral for each.
    """
    raw = record.get("raw_output")
    has_text = isinstance(raw, str) and raw.strip() != ""
    text = raw if has_text else ""

    claim: Dict[str, Any] = {
        "claim_id": claim_id or str(record.get("test_id", "?")),
        # raw_output passthrough — authority is text-only and degrades to "" cleanly.
        "raw_output": text,
    }

    # COARSE text-derived support cues — only added when we actually have text.
    if has_text:
        claim["provenance_depth"] = _coarse_provenance_depth(text)
        claim["baseline_used"] = _coarse_baseline_used(text)
        fresh = _coarse_freshness(text)
        if fresh is not None:
            claim["source_freshness"] = fresh

    return claim


def score_result(record: Dict[str, Any], *, claim_id: str = "") -> Dict[str, Any]:
    """Score one run result and fold in the verifier ground truth.

    Returns the full `score_claim` breakdown PLUS:
      - `test_id`, `passed`, `score` (verifier ground truth, carried through),
      - `has_raw_output` (False when the saved file stripped it — the report
        must say so rather than pretend),
      - `confident_but_wrong` + `confident_but_wrong_reason` (the headline
        signal: high performed authority on a verifier-failed output).

    confident_but_wrong is grounded on the verifier verdict (the reliable axis),
    NOT on the coarse text-derived support. It is only computable when raw_output
    is present (authority needs the text); when text is absent it is None and the
    reason explains the limitation.
    """
    claim = result_to_claim(record, claim_id=claim_id)
    scored = score_claim(claim)

    has_text = bool(claim["raw_output"])
    passed = record.get("passed")
    score = record.get("score")

    scored["test_id"] = record.get("test_id", claim.get("claim_id"))
    scored["passed"] = passed
    scored["score"] = score
    scored["has_raw_output"] = has_text
    scored["raw_output"] = claim["raw_output"]

    cbw, reason = _confident_but_wrong(
        performed=scored["performed_authority"],
        passed=passed,
        score=score,
        has_text=has_text,
    )
    scored["confident_but_wrong"] = cbw
    scored["confident_but_wrong_reason"] = reason
    return scored


def _confident_but_wrong(
    *,
    performed: float,
    passed: Any,
    score: Any,
    has_text: bool,
) -> tuple[Optional[bool], str]:
    """Decide the confident-but-wrong flag from ground truth + performed authority.

    Returns (flag, reason). flag is None (not False) when it can't be computed —
    e.g. no raw_output (authority unknown) or no verifier verdict — so the report
    distinguishes "not confident-wrong" from "couldn't tell".
    """
    if not has_text:
        return None, "no raw_output in saved record — authority not computable"

    # "wrong" per the verifier: prefer the boolean verdict; fall back to score.
    if isinstance(passed, bool):
        is_wrong = not passed
        verdict = f"verifier passed={passed}"
    elif isinstance(score, (int, float)):
        is_wrong = float(score) <= SCORE_FLOOR
        verdict = f"score={score} (<= {SCORE_FLOOR})"
    else:
        return None, "no verifier ground truth (passed/score) on this record"

    is_confident = performed >= AUTHORITY_FLAG
    if is_confident and is_wrong:
        return True, (
            f"performed_authority={performed:.2f} >= {AUTHORITY_FLAG} "
            f"AND {verdict}: confident voice on a wrong answer"
        )
    if is_wrong and not is_confident:
        return False, (
            f"wrong ({verdict}) but appropriately hedged "
            f"(performed_authority={performed:.2f} < {AUTHORITY_FLAG})"
        )
    return False, f"not flagged (performed_authority={performed:.2f}, {verdict})"


def iter_run_records(data: Dict[str, Any]):
    """Yield (group, provider, record) for every per-test record in a results file.

    Handles the two on-disk shapes llm-bench produces:
      1. community files: top-level groups (`standard_results`, `hard_results`,
         `agentic_adversarial_messy_results`, `opencode_full_results`, ...), each
         a {provider: {model, results: [...]}} map.
      2. `_save_results` output: {"runs": [{model, provider, results: [...]}, ...]}.

    Records lacking a `results` list are skipped. Robust to extra keys.
    """
    if isinstance(data.get("runs"), list):
        for run in data["runs"]:
            if isinstance(run, dict) and isinstance(run.get("results"), list):
                provider = run.get("provider") or run.get("model") or "?"
                for rec in run["results"]:
                    if isinstance(rec, dict):
                        yield "runs", provider, rec
        return

    for group, payload in data.items():
        if not isinstance(payload, dict):
            continue
        # a group is {provider: {results: [...]}}
        for provider, run in payload.items():
            if isinstance(run, dict) and isinstance(run.get("results"), list):
                for rec in run["results"]:
                    if isinstance(rec, dict):
                        yield group, provider, rec


def score_run_file(path: str) -> List[Dict[str, Any]]:
    """Load a saved results JSON and score every per-test record.

    Each returned dict is a `score_result` breakdown with a `group` and
    `provider` tag prepended to `test_id` so records stay distinguishable across
    suites/providers in one file. Saved community files strip `raw_output`, so
    most rows will report `has_raw_output=False` and a non-computable
    confident-but-wrong — that limitation is surfaced honestly, not faked.
    """
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    scored: List[Dict[str, Any]] = []
    for group, provider, rec in iter_run_records(data):
        tid = rec.get("test_id", "?")
        claim_id = f"{provider}/{tid}"
        s = score_result(rec, claim_id=claim_id)
        s["group"] = group
        s["provider"] = provider
        s["test_id"] = claim_id
        scored.append(s)
    return scored
