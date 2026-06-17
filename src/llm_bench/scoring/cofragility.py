"""Cofragility score — count of co-active bad-state indicators.

Cofragility detects *clustered* danger: individually tolerable weaknesses that
combine into a forbidden tuple. A single missing baseline is survivable; missing
baseline AND high authority AND high consequence AND no provenance AND a stale
cache is an overconfidence trap.

This scorer counts how many of the known bad-state indicators are co-active for
a claim, reading from its metrics / structured fields. Returns an int.

It is kept SEPARATE from the authority-support lag on purpose. The lag is the
pure performed_authority - earned_support gap in [-1, 1]; cofragility is a
0-12 integer amplifier. Folding the count into the bounded lag would let the
count swamp the named metric — a bug wrong-convergence already hit and fixed.

Ported (logic-identical, stdlib) from
wrong-convergence/src/wrong_convergence/scoring/cofragility.py (frozen provenance).

Indicators:
    low evidence, high authority, high consequence, low provenance,
    high recency need, source conflict, poor task-bank fit, memory
    contamination, no baseline, unvalidated compression, stale cache,
    human review absent.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple


def _num(claim: Dict[str, Any], key: str, default: float = 0.0) -> float:
    v = claim.get(key, default)
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _truthy(claim: Dict[str, Any], key: str) -> bool:
    v = claim.get(key)
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return v > 0
    if isinstance(v, str):
        return v.strip().lower() in ("true", "yes", "1", "high", "present")
    return False


def cofragility_indicators(claim: Dict[str, Any]) -> List[str]:
    """Return the list of bad-state indicators that are co-active for a claim."""
    active: List[str] = []

    # low evidence — few or no evidence items
    items = claim.get("evidence_items")
    n_items = len(items) if isinstance(items, (list, tuple)) else 0
    if n_items <= 1:
        active.append("low_evidence")

    # high authority — performed authority field / magnitude is high
    if _num(claim, "authority_magnitude") >= 0.6:
        active.append("high_authority")

    # high consequence — risk_level high
    risk = str(claim.get("risk_level", "")).lower()
    if risk in ("high", "critical", "severe") or _num(claim, "risk_level") >= 0.6:
        active.append("high_consequence")

    # low provenance — depth < 2
    if _num(claim, "provenance_depth") < 2 and n_items < 2:
        active.append("low_provenance")

    # high recency need but stale/unknown freshness
    needs_recency = _truthy(claim, "needs_recency") or _num(claim, "recency_need") >= 0.5
    fresh = claim.get("source_freshness")
    fresh_low = (isinstance(fresh, (int, float)) and fresh < 0.5) or \
                str(fresh).lower() in ("stale", "dated", "unknown")
    if needs_recency and fresh_low:
        active.append("high_recency_need")

    # source conflict
    if _num(claim, "conflict_level") >= 0.5:
        active.append("source_conflict")

    # poor task-bank fit
    ff = claim.get("fitting_factor")
    if isinstance(ff, (int, float)) and ff < 0.5:
        active.append("poor_task_bank_fit")
    elif str(claim.get("task_sector", "")).lower() in ("out_of_bank", "unknown"):
        active.append("poor_task_bank_fit")

    # memory contamination
    if _num(claim, "memory_dependence") >= 0.5 or _truthy(claim, "memory_contaminated"):
        active.append("memory_contamination")

    # no baseline
    used = claim.get("baseline_used")
    if used is False or (isinstance(used, (int, float)) and used <= 0) or used is None:
        active.append("no_baseline")

    # unvalidated compression — compression steps present but not audited
    steps = claim.get("compression_steps")
    if (isinstance(steps, (list, tuple)) and len(steps) > 0
            and not _truthy(claim, "compression_audited")):
        active.append("unvalidated_compression")
    elif _truthy(claim, "unvalidated_compression"):
        active.append("unvalidated_compression")

    # stale cache
    caches = claim.get("cache_dependencies")
    if isinstance(caches, (list, tuple)) and len(caches) > 0 and _truthy(claim, "cache_stale"):
        active.append("stale_cache")
    elif _truthy(claim, "stale_cache"):
        active.append("stale_cache")

    # human review absent
    if not _truthy(claim, "human_reviewed"):
        active.append("human_review_absent")

    return active


def cofragility_score(claim: Dict[str, Any]) -> int:
    """Return the cofragility score — the count of co-active bad-state indicators."""
    return len(cofragility_indicators(claim))


def cofragility_breakdown(claim: Dict[str, Any]) -> Tuple[int, List[str]]:
    """Convenience: (score, indicator names) for reporting."""
    ind = cofragility_indicators(claim)
    return len(ind), ind
