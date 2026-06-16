#!/usr/bin/env python3
"""Full-suite floor run — does the n=1 finding generalize?

Scores the dumb floor (floors.py) on every FLOOR-ABLE test through the IDENTICAL
verifier, and re-scores a model population (stored + optional live) against it.
Answers the two questions n=1 could not:
  (1) does the composite metric float the floor across MANY tests?
  (2) which tests are FLOOR-BEATABLE (model adds nothing) vs MODEL-REQUIRING?

Pre-registration: experiments/floor/PREREGISTRATION-suite.md (floors + threshold
+ blind predictions, written + sent before this ran). MARGIN reused from n=1.

Usage:
  python experiments/floor/run_suite.py            # floors + stored models
  python experiments/floor/run_suite.py --live     # also run a live model sample
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from llm_bench.floors import floor_map, get_floor
from llm_bench.providers import get_provider
from llm_bench.tests import FULL_TESTS
from llm_bench.verify import VERIFIERS

MARGIN = 0.05  # locked from the n=1 run
LIVE_SAMPLE = [("claude-cli", "claude-opus-4-8"), ("ollama", "llama3.2:3b")]

ROOT = Path(__file__).resolve().parents[2]
COMMUNITY = ROOT / "results" / "community" / "ariaxhan-m4pro-24gb.json"
TESTS = {t.id: t for t in FULL_TESTS}


def raw_metric(verifier: str, score: float, details: dict) -> float:
    """The un-bonused metric where the verifier adds a structure bonus;
    otherwise the score IS the raw metric."""
    if verifier == "tag_extraction" and "f1" in details:
        return float(details["f1"])
    return float(score)


def score_floor(test) -> dict:
    out = get_floor(test.id)(test)
    score, details = VERIFIERS[test.verify](out, test.metadata)
    return {"score": round(score, 4),
            "raw": round(raw_metric(test.verify, score, details), 4),
            "output": out[:200], "details": details}


def load_stored() -> dict:
    """test_id -> list of {model, score, raw, provenance} from community file."""
    by_test: dict[str, list] = {}
    if not COMMUNITY.exists():
        return by_test
    d = json.loads(COMMUNITY.read_text())
    hw = d.get("hardware", {})
    for suite, blob in d.items():
        if not isinstance(blob, dict):
            continue
        for _, info in blob.items():
            if not isinstance(info, dict) or "results" not in info:
                continue
            for r in info["results"]:
                tid = r["test_id"]
                t = TESTS.get(tid)
                if not t:
                    continue
                by_test.setdefault(tid, []).append({
                    "model": info.get("model", "?"),
                    "score": round(r["score"], 4),
                    "raw": round(raw_metric(t.verify, r["score"], r.get("details", {})), 4),
                    "provenance": f"prior {hw.get('date','?')}",
                })
    return by_test


async def run_live_sample(floorable: list[str]) -> dict:
    by_test: dict[str, list] = {}
    for prov_name, model in LIVE_SAMPLE:
        p = get_provider(prov_name)
        if not await p.is_available():
            print(f"  [skip live {model}: provider unavailable]")
            continue
        for tid in floorable:
            t = TESTS[tid]
            try:
                resp = await p.complete(model=model, system_prompt=t.system_prompt,
                                        user_prompt=t.user_prompt,
                                        max_tokens=t.max_tokens, temperature=0.0)
                s, det = VERIFIERS[t.verify](resp.content, t.metadata)
                by_test.setdefault(tid, []).append({
                    "model": model, "score": round(s, 4),
                    "raw": round(raw_metric(t.verify, s, det), 4),
                    "provenance": "live-2026-06-16",
                })
                print(f"  live {model} {tid}: {s:.3f}")
            except Exception as e:  # noqa: BLE001
                print(f"  live {model} {tid}: ERROR {str(e)[:80]}")
    return by_test


def classify(floor_score: float, model_scores: list[float]) -> str:
    """A test is MODEL-REQUIRING if most models clear the floor by MARGIN;
    FLOOR-BEATABLE if most do not (a dumb baseline competes)."""
    if not model_scores:
        return "NO-DATA"
    beat = sum(1 for m in model_scores if round(m - floor_score, 6) > MARGIN)
    frac = beat / len(model_scores)
    if frac >= 0.6:
        return "MODEL-REQUIRING"
    if frac <= 0.4:
        return "FLOOR-BEATABLE"
    return "MIXED"


def validity_flag(floor_score: float, difficulty: str) -> str:
    """dune's interpretation rule: when a no-understanding echo scores HIGH,
    is the TASK trivial (case a: model adds nothing) or is the VERIFIER weak
    (case b: it rewards format over instruction-following — a benchmark-DESIGN
    contaminated-observable, WC #46)? A high floor on a HARD/EXTREME test is the
    alarm: the test claims to measure a hard skill but a content-free echo passes."""
    if floor_score >= 0.6:
        if difficulty in ("HARD", "EXTREME"):
            return "VERIFIER-WEAK"      # case (b): test does not measure its claim
        return "trivial-task-ok"        # case (a): easy task, floor fairly competes
    return "ok"                          # floor genuinely struggles — verifier has teeth


async def main() -> None:
    live = "--live" in sys.argv
    fmap = floor_map()
    floorable = [tid for tid, v in fmap.items() if v["floorable"]]
    no_floor = {tid: v["reason"] for tid, v in fmap.items() if not v["floorable"]}

    stored = load_stored()
    live_scores = await run_live_sample(floorable) if live else {}

    rows = []
    for tid in floorable:
        t = TESTS[tid]
        fl = score_floor(t)
        models = list(stored.get(tid, [])) + list(live_scores.get(tid, []))
        comp = [m["score"] for m in models]
        raws = [m["raw"] for m in models]
        verdict = classify(fl["score"], comp)
        vflag = validity_flag(fl["score"], t.difficulty.name)
        # bonus-inflation check: does the floor look more competitive on
        # composite than on raw? (the contamination signature)
        beat_comp = sum(1 for m in comp if round(m - fl["score"], 6) > MARGIN)
        beat_raw = sum(1 for m in raws if round(m - fl["raw"], 6) > MARGIN)
        rows.append({
            "test": tid, "verifier": t.verify, "difficulty": t.difficulty.name,
            "n_models": len(models),
            "floor_composite": fl["score"], "floor_raw": fl["raw"],
            "models_beat_floor_composite": beat_comp,
            "models_beat_floor_raw": beat_raw,
            "verdict": verdict, "validity_flag": vflag,
            "models": models, "floor_details": fl["details"],
        })

    floorbeatable = [r for r in rows if r["verdict"] == "FLOOR-BEATABLE"]
    modelreq = [r for r in rows if r["verdict"] == "MODEL-REQUIRING"]
    mixed = [r for r in rows if r["verdict"] == "MIXED"]
    # contamination: tests where composite hides what raw reveals
    inflated = [r for r in rows
                if r["models_beat_floor_composite"] < r["models_beat_floor_raw"]]
    verifier_weak = [r["test"] for r in rows if r["validity_flag"] == "VERIFIER-WEAK"]

    report = {
        "margin": MARGIN,
        "coverage": {"floorable": len(floorable), "no_floor": len(no_floor),
                     "total": len(fmap), "no_floor_detail": no_floor},
        "summary": {
            "FLOOR_BEATABLE": len(floorbeatable),
            "MODEL_REQUIRING": len(modelreq),
            "MIXED": len(mixed),
            "composite_hides_vs_raw": len(inflated),
            "VERIFIER_WEAK_tests": verifier_weak,
        },
        "rows": sorted(rows, key=lambda r: (r["verdict"], -r["floor_composite"])),
    }
    out = Path(__file__).resolve().parent / "suite_results.json"
    out.write_text(json.dumps(report, indent=2))

    # ── console ──
    print(f"\n{'='*78}\nFULL-SUITE FLOOR RUN  (margin>{MARGIN})")
    print(f"coverage: {len(floorable)} floor-able / {len(no_floor)} NO-FLOOR / {len(fmap)} total")
    print(f"models per test: stored 8 + live {len(LIVE_SAMPLE) if live else 0}")
    print(f"\n{'test':26s} {'diff':7s} {'flr':>4s} {'beat':>5s} {'verdict':16s} validity")
    print("-" * 82)
    for r in report["rows"]:
        print(f"{r['test']:26s} {r['difficulty'][:6]:7s} {r['floor_composite']:4.2f} "
              f"{r['models_beat_floor_composite']:>2d}/{r['n_models']:<2d} {r['verdict']:16s} "
              f"{r['validity_flag']}")
    s = report["summary"]
    print(f"\nVERDICT: FLOOR-BEATABLE={s['FLOOR_BEATABLE']}  "
          f"MODEL-REQUIRING={s['MODEL_REQUIRING']}  MIXED={s['MIXED']}")
    print(f"composite hides signal vs raw on {s['composite_hides_vs_raw']} test(s) "
          f"(bonus-inflation recurrence)")
    print(f"VERIFIER-WEAK (echo scores high on a HARD/EXTREME test — WC#46 design flaw): "
          f"{len(s['VERIFIER_WEAK_tests'])}")
    for tid in s["VERIFIER_WEAK_tests"]:
        print(f"   ! {tid}")
    print(f"report -> {out}")


if __name__ == "__main__":
    asyncio.run(main())
