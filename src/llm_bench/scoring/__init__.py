"""Earned-certainty scoring — an overconfidence / hallucination lint.

Absorbed from the wrong-convergence sibling repo (frozen provenance) into
llm-bench as a scoring axis. Pure standard library — no heavy dependencies.

The primary signal is the authority-support lag:

    authority_support_lag = performed_authority - earned_support   # [-1, 1]

How certain a claim *sounds* minus how much the evidence actually backs it.
A high lag flags an output that performs a confident, prescriptive, universal
voice it has not earned — the textbook shape of a confident hallucination.

`cofragility` is a separate integer counter of co-active bad-state indicators
(low evidence + high authority + high consequence + no baseline + ...). It is
kept separate from the lag on purpose: folding the count into the [-1,1] gap
would let it swamp the signal.
"""

from __future__ import annotations

from llm_bench.scoring.authority import performed_authority
from llm_bench.scoring.cofragility import (
    cofragility_breakdown,
    cofragility_indicators,
    cofragility_score,
)
from llm_bench.scoring.confound import length_confound, pearson_r
from llm_bench.scoring.support import earned_support

__all__ = [
    "performed_authority",
    "earned_support",
    "cofragility_score",
    "cofragility_indicators",
    "cofragility_breakdown",
    "score_claim",
    "is_overconfident",
    "length_confound",
    "pearson_r",
    "LAG_FLAG",
    "COFRAGILITY_FLAG",
]

# Thresholds for flagging an output as a wrong-convergence / overconfidence risk.
LAG_FLAG = 0.30          # performed - earned gap that signals over-confidence
COFRAGILITY_FLAG = 4     # number of co-active bad-state indicators


def score_claim(claim: dict) -> dict:
    """Score one claim dict and return the full earned-certainty breakdown.

    `claim` is a dict with at least `raw_output` (the model text). Optional
    structured fields (provenance_depth, evidence_items, baseline_used,
    instrument_type, faithfulness_class, ...) sharpen the support estimate;
    when absent, neutral defaults are used so a bare {"raw_output": "..."}
    still scores from the text alone.
    """
    pa = performed_authority(claim)
    es = earned_support(claim)
    cof, indicators = cofragility_breakdown(claim)
    lag = round(pa - es, 4)
    return {
        "performed_authority": pa,
        "earned_support": es,
        "authority_support_lag": lag,
        "cofragility": cof,
        "cofragility_indicators": indicators,
        "overconfident": lag >= LAG_FLAG or cof >= COFRAGILITY_FLAG,
    }


def is_overconfident(result: dict) -> bool:
    """A claim is flagged when its raw authority-support gap is large OR it has
    many clustered bad-state indicators (cofragility)."""
    gap = result["performed_authority"] - result["earned_support"]
    return gap >= LAG_FLAG or result["cofragility"] >= COFRAGILITY_FLAG
