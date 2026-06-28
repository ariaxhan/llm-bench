"""Replay-bootstrap pilot — the smallest honest loop, run end to end.

floor-gate the judge -> replay 3 real tasks through 2 non-Claude models (cold + guided)
-> judge each against the objective outcome -> render Model Cards from real observations.

Run: ``AWS_PROFILE=keystone python -m llm_bench.familiarity.pilot``

The floor gate is hard: if the judge fails its live floor test, the run aborts before
producing any card. A card built on an unproven judge is worse than no card.
"""

from __future__ import annotations

import asyncio
import datetime
import json
from pathlib import Path

from llm_bench.familiarity.card import Observation, build_card, render_card_md
from llm_bench.familiarity.floor import run_floor
from llm_bench.familiarity.judge import DEFAULT_JUDGE_MODEL, judge
from llm_bench.familiarity.replay import CONDITIONS, replay_task
from llm_bench.familiarity.tasks import load_tasks
from llm_bench.providers import get_provider

SUBJECT_MODELS = ["deepseek.v3.2", "minimax.minimax-m2"]
OUT_DIR = Path(__file__).resolve().parents[3] / "results" / "familiarity"


async def run_pilot(subjects: list[str] | None = None, judge_model: str = DEFAULT_JUDGE_MODEL):
    subjects = subjects or SUBJECT_MODELS
    provider = get_provider("bedrock")
    today = datetime.date.today().isoformat()

    # --- HARD GATE: prove the judge before trusting any verdict ---
    print("floor-testing judge:", judge_model)
    floor_ok, floor_results = await run_floor(provider, judge_model)
    for r in floor_results:
        print(f"  {r.task_id:10} {r.kind:13} reached={r.reached} {r.divergence:11} "
              f"{'PASS' if r.passed else 'FAIL'}")
    if not floor_ok:
        raise SystemExit("JUDGE FAILED FLOOR — aborting. (commission -> canon/failures/)")
    print("floor: PASS\n")

    # --- replay x judge -> observations ---
    tasks = load_tasks()
    observations: list[Observation] = []
    replays_dump: list[dict] = []
    verdicts_dump: list[dict] = []

    for model in subjects:
        for task in tasks:
            for condition in CONDITIONS:
                # Reasoning models (e.g. MiniMax M2) spend a large budget thinking before
                # emitting an answer; 4096 left them with empty content. 12000 gives headroom.
                rep = await replay_task(task, provider, model, condition, max_tokens=12000)
                v = await judge(task, rep.output, provider, judge_model=judge_model)
                observations.append(
                    Observation(
                        task_id=task.task_id,
                        capability=task.capability,
                        model=model,
                        condition=condition,
                        reached=v.reached,
                        divergence=v.divergence,
                        how=v.how,
                        latency_ms=rep.latency_ms,
                        cost_usd=rep.cost_usd,
                        agrees_with_spine=v.agrees_with_spine,
                    )
                )
                replays_dump.append(rep.to_dict())
                verdicts_dump.append(v.to_dict())
                flag = "" if v.agrees_with_spine else "  ⚠ spine-disagree"
                print(f"{model:20} {task.task_id:10} {condition:7} "
                      f"reached={str(v.reached):5} {v.divergence:11}{flag}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "observations.json").write_text(
        json.dumps([o.to_dict() for o in observations], indent=2)
    )
    (OUT_DIR / "replays.json").write_text(json.dumps(replays_dump, indent=2))
    (OUT_DIR / "verdicts.json").write_text(json.dumps(verdicts_dump, indent=2))

    # --- render a card per subject (deliverable: >=1) ---
    print()
    for model in subjects:
        card = build_card(model, observations, today)
        md = render_card_md(card)
        safe = model.replace(".", "_").replace(":", "_").replace("/", "_")
        (OUT_DIR / f"card-{safe}.md").write_text(md)
        (OUT_DIR / f"card-{safe}.json").write_text(json.dumps(card, indent=2))

    # print the first subject's card to stdout
    first = build_card(subjects[0], observations, today)
    print(render_card_md(first))
    print(f"\nwrote cards + observations to {OUT_DIR}")


def main():
    asyncio.run(run_pilot())


if __name__ == "__main__":
    main()
