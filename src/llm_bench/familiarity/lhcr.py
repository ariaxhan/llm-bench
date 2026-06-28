"""LHCR sweep — env-driven long-horizon conversational replay across the pilot models.

Pipeline:

  floor-gate the judge AND the environment (every challenge)  ->  for each (model, challenge,
  sample) run a live conversation where a held-out LLM role-plays the frustrated user (gives
  source, withholds runtime diagnostics until asked, ends on the correct fix)  ->  judge the
  transcript on 5 behaviour dims + reached + trap  ->  checkpoint after every sample.

Run: ``AWS_PROFILE=keystone python -u -m llm_bench.familiarity.lhcr [all|top10|<m1,m2>|rebuild] [k]``

Two hard floors: the judge must score a synthetic correct answer reached and the trap not-
reached on every challenge; the environment must accept the correct fix and reject the trap
without leaking a probe on every challenge. Either failing aborts before any verdict.

Resume is automatic and at SAMPLE granularity — a killed run re-run with the same args skips
every (model, challenge, sample) already recorded, so no completed work is ever lost.
"""

from __future__ import annotations

import asyncio
import datetime
import json
from pathlib import Path

from llm_bench.familiarity.challenges import load_challenges
from llm_bench.familiarity.conversation import Conversation, Turn, run_conversation_env
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


def _all_pilot_models() -> list[str]:
    """Every subject from the one-shot pilot, top-10 first then the rest, deduped.
    The judge model is never a subject (it can't grade itself)."""
    from llm_bench.familiarity.pilot import SUBJECT_MODELS

    ordered = list(TOP10_MODELS) + [m for m in SUBJECT_MODELS if m not in TOP10_MODELS]
    return [m for m in ordered if m != DEFAULT_JUDGE_MODEL]


def rebuild_comparison(today: str, out_tag: str = "") -> None:
    """Re-render the comparison from the canonical env verdicts shard (e.g. after a run was
    killed before its final render, or to regenerate the table)."""
    verdicts_path = OUT_DIR / f"{OUT_PREFIX}_verdicts{out_tag}.json"
    if not verdicts_path.exists():
        print(f"no verdicts shard at {verdicts_path}")
        return
    verdicts = json.loads(verdicts_path.read_text())
    order = _all_pilot_models()
    present = {v["model"] for v in verdicts}
    ordered = [m for m in order if m in present] + [m for m in present if m not in order]
    comparison = render_comparison(verdicts, ordered, load_challenges(), today)
    (OUT_DIR / f"{OUT_PREFIX}_comparison{out_tag}.md").write_text(comparison)
    print("\n" + comparison)
    print(f"\nrebuilt comparison from {len(verdicts)} verdicts across {len(present)} models")


# env-mode results live in their own file family (the schema + measurement differ from the
# old scripted-followup runs, so they are never merged together).
OUT_PREFIX = "lhcr_env"
DEFAULT_ENV_MODEL = DEFAULT_JUDGE_MODEL  # held-out infra model; never a subject


# --- floors: prove the judge AND the environment on EVERY challenge before any run ---

def _synth_convo(challenge, assistant_text: str, tag: str) -> Conversation:
    c = Conversation(challenge_id=challenge.challenge_id, model=tag)
    c.turns.append(Turn(index=0, role="user", text=challenge.initial_prompt))
    c.turns.append(Turn(index=1, role="assistant", text=assistant_text))
    return c


async def run_judge_floor(provider, judge_model: str) -> tuple[bool, list]:
    """For every challenge: a synthetic correct answer must score reached, the trap must not."""
    results = []
    for ch in load_challenges():
        conv = _synth_convo(ch, f"{ch.fix_summary}\n\n{ch.known_outcome}", "_converge")
        thr = _synth_convo(ch, ch.trap, "_thrash")
        vc = await judge_conversation(ch, conv, provider, judge_model=judge_model)
        vt = await judge_conversation(ch, thr, provider, judge_model=judge_model)
        results.append(("converge", ch.challenge_id, vc.reached, vc.reached is True))
        results.append(("thrash", ch.challenge_id, vt.reached, vt.reached is False))
    return all(r[3] for r in results), results


async def run_env_floor(provider, env_model: str) -> tuple[bool, list]:
    """For every challenge: the env must accept the correct fix (solved), and must reject the
    trap WITHOUT leaking a probe (solved False, revealed empty)."""
    from llm_bench.familiarity import environment as env
    from llm_bench.familiarity.conversation import _env_transcript

    results = []
    for ch in load_challenges():
        good = _synth_convo(ch, ch.fix_summary, "_good")
        rg = await env.respond(ch, _env_transcript(good.turns), provider, env_model)
        results.append(("accept-fix", ch.challenge_id, rg.solved, rg.solved is True))
        bad = _synth_convo(ch, ch.trap, "_bad")
        rb = await env.respond(ch, _env_transcript(bad.turns), provider, env_model)
        ok = (rb.solved is False) and (rb.revealed == "")
        results.append(("reject-trap+noleak", ch.challenge_id,
                        f"solved={rb.solved} leak={bool(rb.revealed)}", ok))
    return all(r[3] for r in results), results


async def run_sweep(
    subjects: list[str] | None = None,
    judge_model: str = DEFAULT_JUDGE_MODEL,
    env_model: str = DEFAULT_ENV_MODEL,
    concurrency: int = 6,
    out_tag: str = "",
    challenge_ids: list[str] | None = None,
    k: int = 2,
    max_turns: int = 6,
):
    subjects = subjects or TOP10_MODELS
    provider = get_provider("bedrock")
    today = datetime.date.today().isoformat()

    # --- HARD GATE: prove the judge AND the environment on every challenge ---
    print("floor-testing judge:", judge_model)
    jok, jres = await run_judge_floor(provider, judge_model)
    for kind, cid, val, passed in jres:
        print(f"  judge {kind:9} {cid:26} reached={str(val):5} {'PASS' if passed else 'FAIL'}")
    print("floor-testing environment:", env_model)
    eok, eres = await run_env_floor(provider, env_model)
    for kind, cid, val, passed in eres:
        print(f"  env   {kind:18} {cid:26} {str(val):18} {'PASS' if passed else 'FAIL'}")
    if not (jok and eok):
        raise SystemExit("FLOOR FAILED (judge or env) — aborting (commission -> canon/failures/).")
    print("floor: PASS\n")

    challenges = load_challenges()
    if challenge_ids:
        wanted = set(challenge_ids)
        challenges = [c for c in challenges if c.challenge_id in wanted]
    print(f"challenges: {[c.challenge_id for c in challenges]}")
    print(f"subjects: {len(subjects)} models · k={k} samples · max_turns={max_turns} "
          f"· {len(subjects) * len(challenges) * k} cells\n")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    verdicts_path = OUT_DIR / f"{OUT_PREFIX}_verdicts{out_tag}.json"
    transcripts_path = OUT_DIR / f"{OUT_PREFIX}_transcripts{out_tag}.json"

    # --- RESUME at SAMPLE granularity: (model, challenge, sample) already recorded -> skip ---
    verdicts_dump: list[dict] = (
        json.loads(verdicts_path.read_text()) if verdicts_path.exists() else []
    )
    convos_dump: list[dict] = (
        json.loads(transcripts_path.read_text()) if transcripts_path.exists() else []
    )
    errors: list[dict] = []
    done = {(v["model"], v["challenge_id"], v.get("sample", 0)) for v in verdicts_dump}
    if done:
        print(f"resume: {len(done)} sample(s) already recorded, skipping them")

    sem = asyncio.Semaphore(concurrency)
    write_lock = asyncio.Lock()
    cells = [(m, c, s) for m in subjects for c in challenges for s in range(k)
             if (m, c.challenge_id, s) not in done]

    async def _checkpoint():
        for path, data in ((verdicts_path, verdicts_dump), (transcripts_path, convos_dump)):
            tmp = path.with_suffix(".json.tmp")
            tmp.write_text(json.dumps(data, indent=2))
            tmp.replace(path)

    async def run_cell(model: str, challenge, sample: int):
        async with sem:
            try:
                convo = await run_conversation_env(
                    challenge, provider, model, provider, env_model, max_turns=max_turns)
                if convo.error:
                    print(f"{model:40} {challenge.challenge_id:24} s{sample} "
                          f"CONVO-ERR {convo.error[:34]}")
                    async with write_lock:
                        errors.append({"model": model, "challenge": challenge.challenge_id,
                                       "sample": sample, "error": convo.error})
                    return
                v = await judge_conversation(challenge, convo, provider, judge_model=judge_model)
            except Exception as e:  # noqa: BLE001
                print(f"{model:40} {challenge.challenge_id:24} s{sample} ERROR {type(e).__name__}")
                async with write_lock:
                    errors.append({"model": model, "challenge": challenge.challenge_id,
                                   "sample": sample, "error": f"{type(e).__name__}: {e}"})
                return
            ttf = convo.turns_to_fix if convo.solved else "-"
            trap = "TRAP" if v.fell_for_trap else "    "
            print(f"{model:40} {challenge.challenge_id:24} s{sample} "
                  f"solved={str(convo.solved):5} ttf={str(ttf):3} reached={str(v.reached):5} "
                  f"lhcr={v.lhcr_score:2} {trap}")
            rec_v = v.to_dict()
            rec_v["sample"] = sample
            rec_c = convo.to_dict()
            rec_c["sample"] = sample
            async with write_lock:
                verdicts_dump.append(rec_v)
                convos_dump.append(rec_c)
                await _checkpoint()

    await asyncio.gather(*[run_cell(m, c, s) for m, c, s in cells])

    if errors:
        (OUT_DIR / f"{OUT_PREFIX}_errors{out_tag}.json").write_text(json.dumps(errors, indent=2))
        print(f"\n{len(errors)} cell(s) errored (recorded in {OUT_PREFIX}_errors{out_tag}.json)")

    comparison = render_comparison(verdicts_dump, subjects, challenges, today)
    (OUT_DIR / f"{OUT_PREFIX}_comparison{out_tag}.md").write_text(comparison)
    print("\n" + comparison)
    print(f"\nwrote {len(verdicts_dump)} verdicts + comparison to {OUT_DIR}")


def render_comparison(verdicts: list[dict], subjects, challenges, today: str) -> str:
    """Env-mode leaderboard. Each cell is a frustrated-user conversation; aggregated over k
    samples per (model, challenge). Primary metric = solved-rate (the env accepted the fix)."""
    by_model: dict[str, list[dict]] = {}
    for v in verdicts:
        by_model.setdefault(v["model"], []).append(v)

    def _mean(xs):
        xs = list(xs)
        return sum(xs) / len(xs) if xs else 0.0

    rows = []
    for model, vs in by_model.items():
        n = len(vs)
        # map every verdict to 0/1 (do NOT filter — filtering drops the False cases and makes
        # any model with >=1 hit read 100%).
        solved_rate = _mean(1 if v.get("solved") else 0 for v in vs)
        reached_rate = _mean(1 if v.get("reached") else 0 for v in vs)
        trap_rate = _mean(1 if v.get("fell_for_trap") else 0 for v in vs)
        lhcr_mean = _mean(v["lhcr_score"] for v in vs)
        ttfs = [v["turns_to_fix"] for v in vs if v.get("solved") and v.get("turns_to_fix")]
        ttf = f"{_mean(ttfs):.1f}" if ttfs else "—"
        dim_avg = {d: _mean(v["dims"].get(d, 0) for v in vs) for d in _DIMS}
        rows.append((model, solved_rate, reached_rate, trap_rate, lhcr_mean, ttf, dim_avg, n))

    # sort by solved-rate, then reached-rate, then mean lhcr; trap-rate breaks ties (lower better)
    rows.sort(key=lambda r: (r[1], r[2], r[4], -r[3]), reverse=True)

    n_models = len({v["model"] for v in verdicts})
    samples = max((len([1 for v in verdicts
                        if v["model"] == m and v["challenge_id"] == c.challenge_id])
                   for m in by_model for c in challenges), default=0)

    out = ["# Long-Horizon Conversational Replay — model comparison (env-driven)", ""]
    out.append(f"> {n_models} models · {len(challenges)} challenges · k≈{samples} samples/cell "
               f"· generated {today}")
    out.append("> A held-out LLM role-plays the frustrated user: it gives the model the source "
               "code, stays unhelpful ('still broken / figure it out'), reveals a runtime "
               "diagnostic ONLY when the model asks for the right check, and ends the convo when "
               "the model states the correct fix.")
    out.append("> **solved** = env accepted the fix · **reached** = judge saw the root cause · "
               "**trap** = shipped the seductive wrong fix (lower is better) · **→fix** = mean "
               "turns to solve · **lhcr** = mean of 5 behaviour dims (0–10).")
    out.append("")
    out.append("| model | n | solved | reached | trap↓ | →fix | lhcr | conv | no-reg | layer | "
               "verify | state |")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    full_n = len(challenges) * samples
    for model, sr, rr, tr, lh, ttf, da, n in rows:
        nflag = f"{n}" if n >= full_n else f"{n}⚠"  # ⚠ = partial (errored cells)
        out.append(
            f"| `{model}` | {nflag} | **{sr*100:.0f}%** | {rr*100:.0f}% | {tr*100:.0f}% | {ttf} | "
            f"{lh:.1f} | {da['convergence']:.1f} | {da['no_regression']:.1f} | "
            f"{da['layer_switching']:.1f} | {da['verification_seeking']:.1f} | "
            f"{da['state_holding']:.1f} |"
        )
    out.append("")
    out.append(f"_**n**=verdicts (full = {full_n}: {len(challenges)} challenges × {samples} "
               "samples); ⚠ = partial (some cells errored, treat with caution). "
               "**solved**=env accepted the correct fix · **reached**=judge confirmed the root "
               "cause was stated · **trap↓**=rate of shipping the seductive wrong fix (lower "
               "better) · **→fix**=mean turns to solve (fewer better) · **lhcr**=mean 0–10 over "
               "convergence/no-regression/layer-switching/verification-seeking/state-holding._")
    out.append("")
    out.append("_Challenges (real, genericized, multi-session episodes):_")
    for c in challenges:
        out.append(f"_- `{c.challenge_id}` — {c.capability}_")
    return "\n".join(out)


def main(argv: list[str] | None = None):
    """Usage: python -m llm_bench.familiarity.lhcr [all|top10|<m1,m2,...>|rebuild] [k]

    All modes write the single canonical env shard (resume-by-sample, so a killed run just
    continues where it stopped). Default: all 32 pilot models, k=2.
    """
    import sys

    args = argv if argv is not None else sys.argv[1:]
    mode = args[0] if args else "all"
    k = int(args[1]) if len(args) > 1 else 2
    today = datetime.date.today().isoformat()

    if mode == "rebuild":
        rebuild_comparison(today)
    elif mode == "top10":
        asyncio.run(run_sweep(subjects=TOP10_MODELS, k=k))
    elif mode == "all":
        asyncio.run(run_sweep(subjects=_all_pilot_models(), k=k))
    else:
        subjects = [m.strip() for m in mode.split(",") if m.strip()]
        asyncio.run(run_sweep(subjects=subjects, k=k))


if __name__ == "__main__":
    main()
