"""Curated pilot tasks — intelligently selected once, not an automated pipeline.

These three are REAL bugs Aria hit in her own product repos (paper-rooms, our4cuts,
modelmind), reconstructed from the session logs. Each is a self-contained
bug-diagnosis with a definite, code-expressible root cause — so it replays cleanly
(no repo rebuild) and the outcome is checkable. They span three debugging domains:

- ``ios_zoom``            — mobile-web debugging: iOS WKWebView auto-zoom on <16px inputs
- ``cover_crop``          — CSS layout: aspect-ratio mismatch + object-fit cover
- ``revenuecat_permonth`` — payments logic: whole-period price used as per-month value

For each, this module pairs the reconstructed+redacted prompt/reference (from
``results/familiarity/pilot_corpus.json``) with three things authored from ground
truth, not guessed:

- ``known_outcome`` — the objective answer the judge anchors to (NOT Claude's wording).
- ``guidance``      — a *method hint* for the guided-replay condition. Deliberately a
  nudge toward the approach, never Claude's answer, so the guided condition can't
  smuggle the similarity trap back in.
- ``spine``         — a cheap deterministic check (D10). It does NOT judge; it
  *calibrates* the LLM judge: where the spine has a verdict, the judge must agree
  (commission O3), and disagreement is surfaced.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

_CORPUS_PATH = (
    Path(__file__).resolve().parents[3] / "results" / "familiarity" / "pilot_corpus.json"
)


@dataclass
class TaskSpec:
    task_id: str
    capability: str
    prompt: str
    known_outcome: str
    guidance: str
    claude_reference: str
    repo_ref: dict
    spine: Callable[[str], tuple[bool, str]]


# --- deterministic spine checks (calibration anchors, not the judge) ---


def _spine_ios_zoom(out: str) -> tuple[bool, str]:
    o = out.lower()
    mentions_16 = "16px" in o or "16 px" in o or "16-pixel" in o or "16 pixel" in o
    reached = mentions_16 and ("zoom" in o) and ("font" in o or "input" in o)
    return reached, "16px-font iOS-zoom identified" if reached else "root cause not identified"


def _spine_cover_crop(out: str) -> tuple[bool, str]:
    o = out.lower()
    ratios = ("3:4" in o or "3/4" in o or "3 / 4" in o) and (
        "9:16" in o or "9/16" in o or "9 / 16" in o
    )
    aspect_words = "aspect" in o and ("ratio" in o or "mismatch" in o)
    reached = (
        (aspect_words and ("object-fit" in o or "cover" in o))
        or ratios
        or ("object-fit" in o and "cover" in o and ("crop" in o or "cut" in o))
    )
    return reached, "aspect-ratio mismatch identified" if reached else "root cause not identified"


def _spine_revenuecat(out: str) -> tuple[bool, str]:
    o = out.lower()
    reached = (
        ("pricestring" in o or "price string" in o or "pricestring" in o)
        and (
            "per-period" in o
            or "per period" in o
            or "whole" in o
            or "annual" in o
            or "yearly" in o
            or "/12" in o
            or "divide" in o
            or "per month" in o
            or "per-month" in o
        )
    ) or ("/ 12" in o or "/12" in o) and "month" in o
    detail = "whole-period-as-per-month identified" if reached else "root cause not identified"
    return reached, detail


_SPINES: dict[str, Callable[[str], tuple[bool, str]]] = {
    "ios_zoom": _spine_ios_zoom,
    "cover_crop": _spine_cover_crop,
    "revenuecat_permonth": _spine_revenuecat,
}

_META = {
    "ios_zoom": {
        "capability": "mobile-web debugging (iOS WKWebView)",
        "known_outcome": (
            "iOS Safari/WKWebView auto-zooms the page when a focused input has a computed "
            "font-size under 16px. The .desk-input inherits ~13px, so focusing it triggers "
            "the zoom; with no maximum-scale in the viewport the user can't pinch back. The "
            "correct fix is to set the input font-size to >=16px. The viewport-lock fix "
            "(maximum-scale=1 / user-scalable=no) is inferior — it kills pinch-zoom app-wide "
            "and harms accessibility."
        ),
        "guidance": (
            "Think about how iOS WKWebView/Safari treats focused form inputs at small "
            "font sizes."
        ),
    },
    "cover_crop": {
        "capability": "CSS layout / aspect-ratio debugging",
        "known_outcome": (
            "Aspect-ratio mismatch: the cover card is 3:4 but the strip image is 9:16. With "
            "object-fit: cover the taller 9:16 image is scaled to fill the 3:4 box, cropping "
            "the excess height off the top and bottom. The fix is to make the cover card's "
            "aspect-ratio match the strip's 9:16 so the whole image shows."
        ),
        "guidance": (
            "Compare the aspect ratio of the image to its container, and recall what "
            "object-fit: cover does when they differ."
        ),
    },
    "revenuecat_permonth": {
        "capability": "payments-logic / API-semantics debugging",
        "known_outcome": (
            "pkg.product.priceString is the whole-period price (for the annual package, "
            "$79.99/year), not a per-month value — the trailing comment is wrong. Assigning "
            "it to pricePerMonth makes the annual plan render '$79.99/mo'. The fix is to "
            "compute per-month from the annual price (price / 12, same currency) rather than "
            "reusing priceString — $79.99/yr -> $6.67/mo."
        ),
        "guidance": (
            "Check what priceString actually represents for an annual package versus what "
            "pricePerMonth is supposed to display."
        ),
    },
}


def load_tasks() -> list[TaskSpec]:
    corpus = json.loads(_CORPUS_PATH.read_text())
    tasks: list[TaskSpec] = []
    for tid, meta in _META.items():
        c = corpus[tid]
        tasks.append(
            TaskSpec(
                task_id=tid,
                capability=meta["capability"],
                prompt=c["prompt"],
                known_outcome=meta["known_outcome"],
                guidance=meta["guidance"],
                claude_reference=c["claude_reference"],
                repo_ref=c.get("repo_ref", {}),
                spine=_SPINES[tid],
            )
        )
    return tasks


def get_task(task_id: str) -> TaskSpec:
    for t in load_tasks():
        if t.task_id == task_id:
            return t
    raise KeyError(task_id)
