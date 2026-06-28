"""LHCR sweep — run the long-horizon conversational challenges through the top models.

Pipeline (mirrors pilot.py's discipline):

  floor-gate the LHCR judge  ->  run each challenge as a full multi-turn conversation
  through each subject model  ->  judge each transcript on the 5 LHCR dims + final reached
  ->  write transcripts + verdicts + a comparison table.

Run: ``AWS_PROFILE=keystone python -u -m llm_bench.familiarity.lhcr``

The floor gate is hard: a synthetic THRASH transcript must score not-reached and a synthetic
CONVERGE transcript must score reached. If the judge can't tell them apart, the run aborts
before producing any result — an unproven judge is worse than no result.

Subjects = the TOP 10 from the one-shot pilot sweep (ranked by outcomes reached, then cost).
The judge (qwen3-235b) is not a subject; it can't grade itself.
"""

from __future__ import annotations

import asyncio
import datetime
import json
from pathlib import Path

from llm_bench.familiarity.challenges import get_challenge, load_challenges
from llm_bench.familiarity.conversation import Conversation, Turn, run_conversation
from llm_bench.familiarity.judge import DEFAULT_JUDGE_MODEL
from llm_bench.familiarity.lhcr_judge import _DIMS, judge_conversation
from llm_bench.providers import get_provider

# Top 10 from the 2026-06-27 one-shot pilot (results/familiarity/comparison.md),
# ranked by outcomes reached then cost. These are the strongest one-shot debuggers —
# the question LHCR asks is whether one-shot strength survives a frustrated long horizon.
TOP10_MODELS = [
    "us.deepseek.r1-v1:0",
    "moonshot.kimi-k2-thinking",
    "moonshotai.kimi-k2.5",
    "openai.gpt-oss-120b-1:0",
    "qwen.qwen3-coder-480b-a35b-v1:0",
    "deepseek.v3.2",
    "minimax.minimax-m2.1",
    "mistral.devstral-2-123b",
    "mistral.mistral-large-3-675b-instruct",
    "openai.gpt-oss-20b-1:0",
]

OUT_DIR = Path(__file__).resolve().parents[3] / "results" / "familiarity"


# --- LHCR judge floor: synthetic transcripts the judge MUST classify correctly ---

def _floor_conversations() -> list[tuple[str, str, Conversation]]:
    """(kind, challenge_id, convo). kind ∈ {'thrash','converge'}."""
    out: list[tuple[str, str, Conversation]] = []

    # THRASH on hidden_button_layers: model loops on the JS, never finds CSS/deploy. -> not reached
    thrash = Conversation(challenge_id="hidden_button_layers", model="_floor_thrash")
    th_user = ["(initial)", "still there", "still there", "still there", "still there"]
    th_asst = [
        "Set the hidden attribute on the button in your JS for venues. That will hide it.",
        "Double-check the JS runs — add the hidden attribute again, maybe it didn't apply.",
        "Try setting el.hidden = true in the JS once more, and console.log to confirm.",
        "Re-check your JS condition for venue vs event; set hidden in the JS.",
        "It should be hidden once the JS sets the attribute. Verify the JS executes.",
    ]
    for i, (u, a) in enumerate(zip(th_user, th_asst, strict=True)):
        thrash.turns.append(Turn(index=2 * i, role="user", text=u))
        thrash.turns.append(Turn(index=2 * i + 1, role="assistant", text=a))
    out.append(("thrash", "hidden_button_layers", thrash))

    # CONVERGE on hidden_button_layers: model peels layers, names CSS override, verifies live. -> reached
    conv = Conversation(challenge_id="hidden_button_layers", model="_floor_converge")
    cv_user = ["(initial)", "still there", "still there", "still there", "clean it up"]
    cv_asst = [
        "First make sure the fix shipped: did you push to main so the CDN redeploys? A local "
        "commit won't reach production.",
        "If it's pushed, the CDN/browser may be serving a stale asset — bump the ?v= cache-buster "
        "(stamp it from the commit SHA) and reload with a fresh query string.",
        "Since the attribute is in the HTML but the button still shows, inspect the element's "
        "COMPUTED style: a CSS rule like .primary { display: inline-flex } is overriding the "
        "[hidden] attribute. Add [hidden] { display: none !important } so the attribute wins.",
        "Confirmed by checking computed style on the live rendered element, not the JS. The real "
        "cause was CSS display overriding the hidden attribute, on top of the push + cache layers.",
        "Now remove the per-client special-case stylesheet and collapse to exactly two paths: "
        "event and venue.",
    ]
    for i, (u, a) in enumerate(zip(cv_user, cv_asst, strict=True)):
        conv.turns.append(Turn(index=2 * i, role="user", text=u))
        conv.turns.append(Turn(index=2 * i + 1, role="assistant", text=a))
    out.append(("converge", "hidden_button_layers", conv))

    return out


async def run_lhcr_floor(provider, judge_model: str) -> tuple[bool, list]:
    results = []
    for kind, cid, convo in _floor_conversations():
        ch = get_challenge(cid)
        v = await judge_conversation(ch, convo, provider, judge_model=judge_model)
        if kind == "thrash":
            passed = v.reached is False
        else:
            passed = v.reached is True
        results.append((kind, cid, v.reached, v.lhcr_score, passed, v.how))
    overall = all(r[4] for r in results)
    return overall, results


async def run_sweep(
    subjects: list[str] | None = None,
    judge_model: str = DEFAULT_JUDGE_MODEL,
    concurrency: int = 5,
):
    subjects = subjects or TOP10_MODELS
    provider = get_provider("bedrock")
    today = datetime.date.today().isoformat()

    # --- HARD GATE: prove the LHCR judge before any verdict ---
    print("floor-testing LHCR judge:", judge_model)
    floor_ok, floor_results = await run_lhcr_floor(provider, judge_model)
    for kind, cid, reached, score, passed, how in floor_results:
        print(f"  {kind:9} {cid:22} reached={str(reached):5} score={score:2} "
              f"{'PASS' if passed else 'FAIL'}")
    if not floor_ok:
        raise SystemExit("LHCR JUDGE FAILED FLOOR — aborting (commission -> canon/failures/).")
    print("floor: PASS\n")

    challenges = load_challenges()
    print(f"challenges: {[c.challenge_id for c in challenges]}")
    print(f"subjects:   {len(subjects)} models, {sum(c.n_turns for c in challenges)} "
          f"turns/model\n")

    convos_dump: list[dict] = []
    verdicts_dump: list[dict] = []
    errors: list[dict] = []

    sem = asyncio.Semaphore(concurrency)
    cells = [(m, c) for m in subjects for c in challenges]

    async def run_cell(model: str, challenge):
        async with sem:
            try:
                convo = await run_conversation(challenge, provider, model, max_tokens=12000)
                if convo.error:
                    print(f"{model:42} {challenge.challenge_id:22} CONVO-ERR {convo.error[:40]}")
                    return ("err", model, challenge, convo.error)
                v = await judge_conversation(challenge, convo, provider, judge_model=judge_model)
            except Exception as e:  # noqa: BLE001
                print(f"{model:42} {challenge.challenge_id:22} ERROR {type(e).__name__}")
                return ("err", model, challenge, f"{type(e).__name__}: {e}")
            flag = "" if v.agrees_with_spine else "  ⚠ spine-disagree"
            dims = "/".join(str(v.dims[d]) for d in _DIMS)
            print(f"{model:42} {challenge.challenge_id:22} reached={str(v.reached):5} "
                  f"lhcr={v.lhcr_score:2} dims[{dims}]{flag}")
            return ("ok", model, challenge, convo, v)

    cell_results = await asyncio.gather(*[run_cell(m, c) for m, c in cells])

    for res in cell_results:
        if res[0] == "err":
            _, model, challenge, err = res
            errors.append({"model": model, "challenge": challenge.challenge_id, "error": err})
            continue
        _, model, challenge, convo, v = res
        convos_dump.append(convo.to_dict())
        verdicts_dump.append(v.to_dict())

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "lhcr_transcripts.json").write_text(json.dumps(convos_dump, indent=2))
    (OUT_DIR / "lhcr_verdicts.json").write_text(json.dumps(verdicts_dump, indent=2))
    if errors:
        (OUT_DIR / "lhcr_errors.json").write_text(json.dumps(errors, indent=2))
        print(f"\n{len(errors)} cell(s) errored (recorded in lhcr_errors.json)")

    comparison = render_comparison(verdicts_dump, subjects, challenges, today)
    (OUT_DIR / "lhcr_comparison.md").write_text(comparison)
    print("\n" + comparison)
    print(f"\nwrote {len(verdicts_dump)} verdicts + comparison to {OUT_DIR}")


def render_comparison(verdicts: list[dict], subjects, challenges, today: str) -> str:
    by_model: dict[str, list[dict]] = {}
    for v in verdicts:
        by_model.setdefault(v["model"], []).append(v)

    n_ch = len(challenges)
    rows = []
    for model in subjects:
        vs = by_model.get(model, [])
        if not vs:
            continue
        reached = sum(1 for v in vs if v["reached"])
        score = sum(v["lhcr_score"] for v in vs)
        max_score = 10 * len(vs)
        dim_avg = {
            d: (sum(v["dims"].get(d, 0) for v in vs) / len(vs)) for d in _DIMS
        }
        rows.append((model, reached, score, max_score, dim_avg, len(vs)))

    # sort by reached, then total lhcr score
    rows.sort(key=lambda r: (r[1], r[2]), reverse=True)

    out = ["# Long-Horizon Conversational Replay — model comparison", ""]
    out.append(f"> {len(rows)} models · {n_ch} multi-turn challenges · generated {today}")
    out.append("> Each challenge is a real, genericized, multi-session frustration episode "
               "(our4cuts / modelmind / augur).")
    out.append("> `reached` = final answer hit the true root cause. `lhcr` = sum of 5 "
               "behaviour dims (0–2 each) across challenges. Every cell n=1 — pilot, not powered.")
    out.append("")
    out.append("| model | reached | lhcr score | conv | no-reg | layer | verify | state |")
    out.append("|---|---|---|---|---|---|---|---|")
    for model, reached, score, max_score, dim_avg, n in rows:
        out.append(
            f"| `{model}` | **{reached}/{n}** | {score}/{max_score} | "
            f"{dim_avg['convergence']:.1f} | {dim_avg['no_regression']:.1f} | "
            f"{dim_avg['layer_switching']:.1f} | {dim_avg['verification_seeking']:.1f} | "
            f"{dim_avg['state_holding']:.1f} |"
        )
    out.append("")
    out.append("_Dims (avg 0–2 across challenges): **conv**=convergence, **no-reg**=no-regression, "
               "**layer**=layer-switching when a fix is rejected, **verify**=verification-seeking "
               "(propose checking live/rendered/runtime state), **state**=state-holding across turns._")
    out.append("")
    out.append("_Challenges: `hidden_button_layers` (deploy/cache/CSS 4-layer whack-a-mole), "
               "`ota_never_applies` (downloaded-but-not-activated), `silent_dead_engine` "
               "(healthy process, zero output via an untested seam)._")
    return "\n".join(out)


def main():
    asyncio.run(run_sweep())


if __name__ == "__main__":
    main()
