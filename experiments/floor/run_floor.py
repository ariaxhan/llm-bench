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
    if model_score <= floor_score + STRICT_TIE:
        return "EVAPORATED (<=floor)"
    if model_score - floor_score <= MARGIN:
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

    for r in rows:
        if "score" in r:
            r["verdict"] = verdict(r["score"], floor_score)

    report = {
        "test_id": TEST_ID,
        "margin": MARGIN,
        "floor": {
            "output": floor_out,
            "score": round(floor_score, 4),
            "details": floor_details,
        },
        "models": rows,
    }
    out_path = Path(__file__).resolve().parent / "results.json"
    out_path.write_text(json.dumps(report, indent=2))

    # ── console table ──
    print(f"\nTEST: {TEST_ID}")
    print(f"FLOOR (dumb regex): score={floor_score:.3f}  tags={floor_details.get('got_tags')}")
    print(f"  floor output: {floor_out}\n")
    print(f"{'model':28s} {'prov':10s} {'score':>6s}  verdict")
    print("-" * 70)
    scored = [r for r in rows if "score" in r]
    for r in sorted(scored, key=lambda x: -x["score"]):
        prov = "live" if str(r.get("provenance", "")).startswith("live") else "prior"
        print(f"{r['model']:28s} {prov:10s} {r['score']:6.3f}  {r['verdict']}")
    for r in rows:
        if "error" in r:
            print(f"{r['model']:28s} ERROR: {r['error']}")
    survived = sum(1 for r in scored if r["verdict"] == "SURVIVED")
    print(f"\n{survived}/{len(scored)} model-results SURVIVED the floor "
          f"(margin>{MARGIN}). report -> {out_path}")


if __name__ == "__main__":
    asyncio.run(main())
