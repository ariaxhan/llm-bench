#!/usr/bin/env python3
"""Floor experiment — does a model's tag-extraction "win" survive the dumb floor?

P5 at the model-eval layer. Scores the cheap regex floor (floors.py) and a set
of models on ONE test (tag-extraction) through the IDENTICAL verifier, then
applies the pre-registered evaporation rule:

    a model's win SURVIVES iff  model_score - floor_score > MARGIN
    otherwise it EVAPORATES (the dumb regex ties or beats it).

Pre-registration: experiments/floor/PREREGISTRATION.md (written + sent before
this ran). MARGIN and the verdict bar live there and are mirrored below.

Live models run now (ollama + claude-cli). Prior-run models are read from
results/community with explicit provenance — never silently merged.
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from llm_bench.floors import get_floor
from llm_bench.providers import get_provider
from llm_bench.tests.suite import get_test
from llm_bench.verify import VERIFIERS

TEST_ID = "tag-extraction"

# Pre-registered (see PREREGISTRATION.md) — DO NOT edit after the run.
MARGIN = 0.05          # "meaningful win" band; ties within +/-MARGIN = evaporated
STRICT_TIE = 0.0       # any model_score <= floor_score = evaporated outright

# Models to run LIVE this session.
OLLAMA_MODELS = ["llama3.2:3b", "qwen2.5:3b"]
CLAUDE_MODELS = ["claude-haiku-4-5", "claude-sonnet-4-6", "claude-opus-4-8"]

ROOT = Path(__file__).resolve().parents[2]
COMMUNITY = ROOT / "results" / "community" / "ariaxhan-m4pro-24gb.json"


def score_output(test, output: str) -> tuple[float, dict]:
    return VERIFIERS[test.verify](output, test.metadata)


async def run_model(provider_name: str, model: str, test) -> dict:
    p = get_provider(provider_name)
    if not await p.is_available():
        return {"model": model, "provider": provider_name, "error": "unavailable"}
    try:
        resp = await p.complete(
            model=model,
            system_prompt=test.system_prompt,
            user_prompt=test.user_prompt,
            max_tokens=test.max_tokens,
            temperature=0.0,
        )
        score, details = score_output(test, resp.content)
        return {
            "model": model,
            "provider": provider_name,
            "score": round(score, 4),
            "details": details,
            "raw_output": resp.content,
            "provenance": "live-2026-06-16",
        }
    except Exception as e:  # noqa: BLE001
        return {"model": model, "provider": provider_name, "error": str(e)}


def load_community(test_id: str) -> list[dict]:
    if not COMMUNITY.exists():
        return []
    d = json.loads(COMMUNITY.read_text())
    hw = d.get("hardware", {})
    prov = f"prior-run {hw.get('date','?')} {hw.get('chip','?')}"
    out = []
    for _, info in d.get("standard_results", {}).items():
        for r in info["results"]:
            if r["test_id"] == test_id:
                out.append({
                    "model": info["model"],
                    "provider": info["provider"],
                    "score": round(r["score"], 4),
                    "details": r.get("details", {}),
                    "raw_output": None,
                    "provenance": prov,
                })
    return out


def verdict(model_score: float, floor_score: float) -> str:
    # round to kill float dust (1.0 - 0.95 == 0.0500000004 would fake a survive)
    gap = round(model_score - floor_score, 6)
    if gap <= STRICT_TIE:
        return "EVAPORATED (<=floor)"
    if gap <= MARGIN:
        return "EVAPORATED (within margin)"
    return "SURVIVED"


async def main() -> None:
    test = get_test(TEST_ID)
    if test is None:
        sys.exit(f"unknown test {TEST_ID}")

    floor_fn = get_floor(TEST_ID)
    floor_out = floor_fn(test)
    floor_score, floor_details = score_output(test, floor_out)

    rows: list[dict] = []
    for m in OLLAMA_MODELS:
        rows.append(await run_model("ollama", m, test))
    for m in CLAUDE_MODELS:
        rows.append(await run_model("claude-cli", m, test))
    rows.extend(load_community(TEST_ID))

    # Decompose: the +format-bonus composite is what the leaderboard reports,
    # but it is constant noise for model AND floor. The real contest is raw
    # tag-F1 (dune sharpening #1). Verdict on BOTH; composite is the locked one.
    floor_f1 = float(floor_details.get("f1", 0.0))
    for r in rows:
        if "score" in r:
            r["verdict"] = verdict(r["score"], floor_score)
            r["f1"] = float(r.get("details", {}).get("f1", 0.0))
            r["verdict_rawf1"] = verdict(r["f1"], floor_f1)

    scored = [r for r in rows if "score" in r]
    report = {
        "test_id": TEST_ID,
        "n_items": 1,  # ONE article — a demonstration / pilot, not a powered verdict
        "framing": "n=1 item. Claim is 'on THIS item the floor ties/beats models', "
                   "a pilot like self-gen n=160, not a statistically powered result.",
        "margin": MARGIN,
        "floor": {
            "output": floor_out,
            "composite_score": round(floor_score, 4),
            "raw_tag_f1": floor_f1,
            "details": floor_details,
            "note": "crude-singular substring false-positived 'open-models' off "
                    "the word 'models'; also missed 'research'. floor is right for "
                    "partly-wrong reasons — reported honestly.",
        },
        "models": rows,
    }
    out_path = Path(__file__).resolve().parent / "results.json"
    out_path.write_text(json.dumps(report, indent=2))

    # ── console table ──
    print(f"\nTEST: {TEST_ID}   (N=1 item — demonstration, not a powered verdict)")
    print(f"FLOOR (dumb regex): composite={floor_score:.3f}  raw-tag-F1={floor_f1:.3f}  "
          f"tags={floor_details.get('got_tags')}")
    print(f"  P={floor_details.get('precision')} R={floor_details.get('recall')} "
          f"(false-pos 'open-models', missed 'research')\n")
    print(f"{'model':24s} {'prov':6s} {'comp':>5s} {'verdict(comp)':18s} "
          f"{'rawF1':>5s} {'verdict(rawF1)':18s}")
    print("-" * 86)
    for r in sorted(scored, key=lambda x: (-x["f1"], -x["score"])):
        prov = "live" if str(r.get("provenance", "")).startswith("live") else "prior"
        print(f"{r['model']:24s} {prov:6s} {r['score']:5.3f} {r['verdict']:18s} "
              f"{r['f1']:5.3f} {r['verdict_rawf1']:18s}")
    for r in rows:
        if "error" in r:
            print(f"{r['model']:24s} ERROR: {r['error']}")
    surv_c = sum(1 for r in scored if r["verdict"] == "SURVIVED")
    surv_f = sum(1 for r in scored if r["verdict_rawf1"] == "SURVIVED")
    print(f"\nComposite (locked, format-bonus inflated): {surv_c}/{len(scored)} SURVIVED")
    print(f"Raw tag-F1 (the real contest):             {surv_f}/{len(scored)} SURVIVED")
    print(f"report -> {out_path}")


if __name__ == "__main__":
    asyncio.run(main())
