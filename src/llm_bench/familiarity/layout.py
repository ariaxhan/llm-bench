"""Canonical on-disk layout for familiarity results. One place, so every writer agrees.

    results/familiarity/
      cards/<provider>/<model>.{json,md}     one unified card per model (one-shot + long-horizon)
      leaderboards/
        one-shot.md            cross-model one-shot table
        one-shot-detailed.md   quote-backed deep dive
        long-horizon.md        env-driven LHCR table
      runs/
        one-shot/      observations.json · replays.json · verdicts.json · errors.json · pilot_corpus.json
        long-horizon/  verdicts.json · transcripts.json (gitignored) · errors.json
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3] / "results" / "familiarity"

CARDS = ROOT / "cards"
LEADERBOARDS = ROOT / "leaderboards"
RUNS = ROOT / "runs"
ONE_SHOT = RUNS / "one-shot"
LONG_HORIZON = RUNS / "long-horizon"


def ensure() -> None:
    for d in (CARDS, LEADERBOARDS, ONE_SHOT, LONG_HORIZON):
        d.mkdir(parents=True, exist_ok=True)
