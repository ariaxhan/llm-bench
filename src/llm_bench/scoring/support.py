"""Earned support — how much the evidence actually backs a model output.

Earned support is the counter-weight to performed authority. An output earns
the right to settle into certainty through:

    provenance depth, source directness/freshness, source agreement (vs conflict),
    baseline comparison, domain/task-sector fit, and instrument fit.

Returns a float in [0, 1]. The gap performed_authority - earned_support is the
authority-support lag, the primary overconfidence signal.

Ported (logic-identical, stdlib) from wrong-convergence/scoring/support.py.
"""

from __future__ import annotations

from typing import Any, Dict

# Faithfulness classes ranked by how much they justify a `full` voice.
_FAITHFULNESS_WEIGHT = {
    "full": 1.0,
    "wrapper": 0.85,
    "reduced_core": 0.6,
    "inferred": 0.4,
    "placeholder": 0.15,
    "ornamental": 0.1,
    "out_of_bank": 0.05,
}

_INSTRUMENT_FIT = {
    # whether the instrument can adjudicate the claim
    "appropriate": 1.0,
    "direct_measurement": 1.0,
    "retrieval": 0.85,
    "calculation": 0.8,
    "model_inference": 0.5,
    "analogy": 0.3,
    "vibes": 0.1,
    "wrong_instrument": 0.0,
}


def _num(claim: Dict[str, Any], key: str, default: float = 0.0) -> float:
    v = claim.get(key, default)
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _provenance(claim: Dict[str, Any]) -> float:
    """Depth of the evidence chain: how many real, traceable sources stand
    behind the claim. provenance_depth is an int (0 = none, 3+ = well-sourced)."""
    depth = _num(claim, "provenance_depth")
    items = claim.get("evidence_items")
    n_items = len(items) if isinstance(items, (list, tuple)) else 0
    depth = max(depth, n_items)
    return min(depth / 3.0, 1.0)


def _freshness(claim: Dict[str, Any]) -> float:
    """source_freshness in [0,1] already, or derived. A claim that needs current
    info but cites stale sources earns little freshness credit."""
    fresh = claim.get("source_freshness")
    if isinstance(fresh, (int, float)):
        return min(max(float(fresh), 0.0), 1.0)
    # qualitative fallback
    return {
        "current": 1.0, "recent": 0.8, "dated": 0.4,
        "stale": 0.1, "unknown": 0.3,
    }.get(str(fresh).lower(), 0.5)


def _agreement(claim: Dict[str, Any]) -> float:
    """High source agreement = high earned support; conflict erodes it.
    conflict_level in [0,1] (0 = full agreement, 1 = sources contradict)."""
    conflict = _num(claim, "conflict_level", default=0.5)
    conflict = min(max(conflict, 0.0), 1.0)
    agreement = claim.get("source_agreement")
    if isinstance(agreement, (int, float)):
        return min(max(float(agreement), 0.0), 1.0)
    return 1.0 - conflict


def _baseline(claim: Dict[str, Any]) -> float:
    """Was the claim compared against an incumbent baseline? (Reliability
    without a decision-time comparison earns no mandate.)"""
    used = claim.get("baseline_used")
    if isinstance(used, bool):
        return 1.0 if used else 0.0
    if isinstance(used, (int, float)):
        return min(max(float(used), 0.0), 1.0)
    return 0.0


def _fit(claim: Dict[str, Any]) -> float:
    """Domain / task-sector fit: does the claim sit inside a regime the system
    actually covers, or is it out-of-bank?"""
    ff = claim.get("fitting_factor")
    if isinstance(ff, (int, float)):
        return min(max(float(ff), 0.0), 1.0)
    # task_sector match to a known-covered sector
    sector_fit = claim.get("task_sector_fit")
    if isinstance(sector_fit, (int, float)):
        return min(max(float(sector_fit), 0.0), 1.0)
    return 0.5


def _instrument(claim: Dict[str, Any]) -> float:
    """Can the named instrument adjudicate this claim?"""
    inst = str(claim.get("instrument_type", "")).lower()
    if inst in _INSTRUMENT_FIT:
        return _INSTRUMENT_FIT[inst]
    fit = claim.get("instrument_fit")
    if isinstance(fit, (int, float)):
        return min(max(float(fit), 0.0), 1.0)
    return 0.5


def _faithfulness(claim: Dict[str, Any]) -> float:
    fc = str(claim.get("faithfulness_class", "")).lower()
    return _FAITHFULNESS_WEIGHT.get(fc, 0.5)


def earned_support(claim: Dict[str, Any]) -> float:
    """Return earned support of a claim in [0, 1].

    A well-sourced, fresh, agreeing, baseline-compared, in-domain claim measured
    with the right instrument scores near 1.0. A confident hallucination with no
    provenance, no baseline, an out-of-bank task and the wrong instrument scores
    near 0.0.
    """
    provenance = _provenance(claim)
    freshness = _freshness(claim)
    agreement = _agreement(claim)
    baseline = _baseline(claim)
    fit = _fit(claim)
    instrument = _instrument(claim)
    faithfulness = _faithfulness(claim)

    score = (
        0.24 * provenance
        + 0.13 * freshness
        + 0.13 * agreement
        + 0.13 * baseline
        + 0.13 * fit
        + 0.12 * instrument
        + 0.12 * faithfulness
    )
    return round(min(max(score, 0.0), 1.0), 4)
