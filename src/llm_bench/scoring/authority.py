"""Performed authority — how certain / prescriptive a model output *sounds*.

Performed authority is the voice of the output, independent of whether the
evidence backs it. A high-authority output delivered with low earned support is
an overconfidence candidate: it crystallized into a confident `full` voice
before its support saturated.

Signals: confidence language, specificity, actionability, lack of caveats,
prescriptive tone, claimed scope, implied certainty.

All signals are derived heuristically from the claim dict and its `raw_output`
text. Returns a float in [0, 1].

Ported (logic-identical, stdlib) from wrong-convergence/scoring/authority.py.
"""

from __future__ import annotations

import re
from typing import Any, Dict

# Words that perform certainty without earning it.
_CONFIDENCE_WORDS = (
    "definitely", "certainly", "undoubtedly", "clearly", "obviously",
    "always", "never", "guaranteed", "proven", "proves", "must",
    "will", "ensures", "the fact is", "without a doubt", "absolutely",
    "exactly", "precisely", "100%", "perfect", "best", "optimal",
)

# Hedges that lower performed authority (a claim that caveats itself performs
# less authority — appropriately).
_CAVEAT_WORDS = (
    "might", "may", "could", "possibly", "perhaps", "likely", "probably",
    "appears", "seems", "suggests", "approximately", "roughly", "around",
    "estimate", "uncertain", "unclear", "i think", "i believe", "to my knowledge",
    "as of", "based on available", "no data", "cannot confirm", "unverified",
)

# Prescriptive / directive markers — telling the reader to *act*.
_PRESCRIPTIVE_WORDS = (
    "you should", "you must", "do this", "always use", "never use",
    "make sure", "be sure to", "recommend", "advise", "the right way",
    "the correct", "instead", "stop", "avoid", "switch to",
)

# Scope-claiming markers — universal/total reach.
_SCOPE_WORDS = (
    "all", "every", "everyone", "everything", "any", "in general",
    "universally", "across the board", "in all cases", "globally",
    "no exceptions", "anyone",
)


def _text(claim: Dict[str, Any]) -> str:
    return str(claim.get("raw_output", "")).lower()


def _hit_ratio(text: str, words) -> float:
    """Fraction of the marker vocabulary that appears at least once, lightly
    boosted by repeats. Bounded to [0, 1]."""
    if not text:
        return 0.0
    hits = sum(1 for w in words if w in text)
    base = hits / len(words)
    # small boost for sheer volume of confident markers
    total = sum(text.count(w) for w in words)
    volume = min(total / 6.0, 1.0)
    return min(1.0 * base * 3.0 + 0.4 * volume, 1.0)


def _specificity(claim: Dict[str, Any], text: str) -> float:
    """Concrete numbers, dates, named entities, units read as specificity —
    precision performs authority regardless of correctness."""
    numbers = len(re.findall(r"\d", text))
    units = len(re.findall(r"%|\$|kg|km|ms|gb|mb|x\b|°|years?|days?", text))
    decimals = len(re.findall(r"\d+\.\d+", text))
    score = (min(numbers / 12.0, 1.0) * 0.6
             + min(units / 3.0, 1.0) * 0.2
             + min(decimals / 2.0, 1.0) * 0.2)
    # an explicit authority_magnitude field, if present, nudges it
    mag = claim.get("authority_magnitude")
    if isinstance(mag, (int, float)):
        score = max(score, min(float(mag), 1.0) * 0.5 + score * 0.5)
    return min(score, 1.0)


def performed_authority(claim: Dict[str, Any]) -> float:
    """Return performed authority of a claim in [0, 1].

    Combines confidence language, specificity, actionability, prescriptive
    tone, claimed scope and *lack* of caveats. A loud, hedge-free, prescriptive,
    universal, specific claim scores near 1.0; a hedged, narrow, descriptive
    claim scores near 0.0.
    """
    text = _text(claim)

    confidence = _hit_ratio(text, _CONFIDENCE_WORDS)
    prescriptive = _hit_ratio(text, _PRESCRIPTIVE_WORDS)
    scope_text = _hit_ratio(text, _SCOPE_WORDS)
    specificity = _specificity(claim, text)

    # Caveats *reduce* performed authority.
    caveat = _hit_ratio(text, _CAVEAT_WORDS)
    lack_of_caveats = 1.0 - caveat

    # Structured fields back the text signals when present.
    scope_field = {
        "single": 0.1, "narrow": 0.25, "local": 0.3, "domain": 0.5,
        "broad": 0.75, "universal": 1.0, "global": 1.0,
    }.get(str(claim.get("scope", "")).lower(), None)
    if scope_field is not None:
        scope = max(scope_text, scope_field)
    else:
        scope = scope_text

    action_field = {
        "none": 0.0, "informational": 0.15, "suggestive": 0.4,
        "recommended": 0.7, "directive": 0.9, "mandatory": 1.0,
    }.get(str(claim.get("actionability", "")).lower(), None)
    actionability = max(prescriptive, action_field) if action_field is not None else prescriptive

    # Weighted blend. Lack-of-caveats and confidence dominate because they are
    # the loudest tells of an unearned `full` voice.
    score = (
        0.26 * confidence
        + 0.22 * lack_of_caveats
        + 0.16 * actionability
        + 0.14 * specificity
        + 0.12 * scope
        + 0.10 * prescriptive
    )
    return round(min(max(score, 0.0), 1.0), 4)
