"""Failure galleries — the qualitative layer on top of the scores.

A leaderboard tells you *who* solved a challenge. A failure gallery tells you *how models
fail* — the archetypal wrong moves, with real verbatim quotes, and what the solvers did
differently. People remember "everyone reached for !important before checking the cascade"
far better than "48% solved".

This reads the saved transcripts (no subject re-run) and, per challenge, asks the judge model
to cluster the attempts into failure archetypes + a "what solvers did first" note. Each
challenge is also tagged with a *reasoning-failure class* (a taxonomy across challenges), so
the galleries compose into statements like "model X struggles with lifecycle teardown bugs but
excels at layered configuration reasoning."

Run:  AWS_PROFILE=keystone python -u -m llm_bench.familiarity.galleries
"""

from __future__ import annotations

import asyncio
import json

from llm_bench.familiarity import layout
from llm_bench.familiarity.challenges import load_challenges
from llm_bench.familiarity.judge import DEFAULT_JUDGE_MODEL, _extract_json
from llm_bench.providers import get_provider

# Aria's taxonomy: label challenges by the REASONING failure they probe, not the surface tech.
REASONING_CLASS: dict[str, str] = {
    "hidden_button_layers": "layer interaction + stale deploy/cache",
    "ota_never_applies": "lifecycle: staged-but-not-activated",
    "silent_dead_engine": "hidden state / silent false-positive (green ≠ working)",
    "reset_specificity_override": "layer interaction (CSS cascade/specificity)",
    "iap_entitlement_phantom": "configuration mismatch (two-console data model)",
    "launchd_exit126_phantom": "misattributed error (inner cmd vs wrapper)",
    "wix_regen_green_tests_blind": "false-positive signal (tests assert fabricated input)",
    "camera_track_killed_by_hide": "lifecycle misunderstanding (resource teardown)",
}


def _attempts_for(challenge_id: str, transcripts: list[dict], verdicts: list[dict]) -> list[dict]:
    """One condensed record per (model, sample): did it solve, fall for the trap, and the
    engineer's own turns (truncated) so the judge can see the approach without the bulk."""
    vmap = {(v["model"], v["challenge_id"], v.get("sample", 0)): v for v in verdicts}
    out = []
    for t in transcripts:
        if t["challenge_id"] != challenge_id:
            continue
        v = vmap.get((t["model"], t["challenge_id"], t.get("sample", 0)))
        if not v:
            continue
        moves = [turn["text"] for turn in t["turns"] if turn["role"] == "assistant"]
        # opening move (where the archetype lives) + the last move (the fix they landed on)
        condensed = []
        if moves:
            condensed.append("FIRST: " + " ".join(moves[0].split())[:700])
        if len(moves) > 1:
            condensed.append("LAST: " + " ".join(moves[-1].split())[:500])
        out.append({
            "model": t["model"], "solved": bool(v.get("solved")),
            "trap": bool(v.get("fell_for_trap")), "text": "\n".join(condensed),
        })
    return out


_SYSTEM = (
    "You are analysing many independent attempts by different models to debug the SAME issue "
    "through a frustrated user. You cluster how they FAILED, citing real quotes. Be concrete "
    "and honest; do not invent quotes."
)


def _prompt(challenge, attempts: list[dict]) -> str:
    blocks = []
    for i, a in enumerate(attempts):
        tag = "SOLVED" if a["solved"] else "FAILED"
        trap = " (shipped the trap)" if a["trap"] else ""
        blocks.append(f"--- attempt {i} [{a['model']}] {tag}{trap} ---\n{a['text']}")
    body = "\n\n".join(blocks)
    n = len(attempts)
    return f"""CHALLENGE: {challenge.challenge_id}
TRUE ROOT CAUSE: {challenge.known_outcome}
THE TRAP (seductive wrong move): {challenge.trap}

{n} ATTEMPTS (each is one model's debugging turns, condensed):
{body}

Analyse the FAILED attempts. Produce:
- archetypes: 2-4 distinct *archetypal wrong approaches*, ordered by frequency. For each give:
  - "label": a short name for the wrong approach (e.g. "bump the value", "reach for !important")
  - "share": approximate fraction of ALL {n} attempts that did this, as a percent integer
  - "quote": ONE short verbatim fragment from an attempt that exemplifies it (<=160 chars)
- solvers_did: 1-2 sentences on what the SOLVED attempts did differently in their FIRST move
  (e.g. "asked to inspect computed styles / read the log before editing").
- one_liner: a single sentence a reader will remember about how models fail this challenge.

Respond with ONLY this JSON, no prose, no fence:
{{"archetypes": [{{"label": "...", "share": 0, "quote": "..."}}], "solvers_did": "...", "one_liner": "..."}}"""


async def _gallery_for(challenge, attempts, provider, model) -> dict:
    if not attempts:
        return {"archetypes": [], "solvers_did": "", "one_liner": "(no attempts)"}
    resp = await provider.complete(
        model=model, system_prompt=_SYSTEM, user_prompt=_prompt(challenge, attempts),
        max_tokens=1200, temperature=0.0,
    )
    obj = _extract_json(resp.content) or {}
    return {
        "archetypes": obj.get("archetypes", []),
        "solvers_did": str(obj.get("solvers_did", "")).strip(),
        "one_liner": str(obj.get("one_liner", "")).strip(),
        "raw_ok": bool(obj),
    }


def _render(challenge, cls: str, stats: dict, g: dict) -> str:
    out = [f"## `{challenge.challenge_id}`", "",
           f"> Reasoning class: **{cls}**  ·  {challenge.capability}",
           f"> {stats['solved']}/{stats['n']} solved · {stats['trap']}/{stats['n']} fell for the trap",
           ""]
    if g.get("one_liner"):
        out += [f"**{g['one_liner']}**", ""]
    if g["archetypes"]:
        out += ["**Common failures:**"]
        for a in g["archetypes"]:
            q = a.get("quote", "").strip().strip('"')
            out.append(f"- **{a.get('label','?')}** (~{a.get('share','?')}%) — "
                       + (f'_"{q}"_' if q else ""))
        out.append("")
    if g.get("solvers_did"):
        out += [f"**What solvers did first:** {g['solvers_did']}", ""]
    return "\n".join(out)


async def build(provider=None, model: str = DEFAULT_JUDGE_MODEL) -> str:
    provider = provider or get_provider("bedrock")
    transcripts = json.loads((layout.LONG_HORIZON / "transcripts.json").read_text())
    verdicts = json.loads((layout.LONG_HORIZON / "verdicts.json").read_text())
    challenges = load_challenges()

    sections, payload = [], {}
    for ch in challenges:
        attempts = _attempts_for(ch.challenge_id, transcripts, verdicts)
        stats = {"n": len(attempts),
                 "solved": sum(a["solved"] for a in attempts),
                 "trap": sum(a["trap"] for a in attempts)}
        g = await _gallery_for(ch, attempts, provider, model)
        cls = REASONING_CLASS.get(ch.challenge_id, "—")
        sections.append(_render(ch, cls, stats, g))
        payload[ch.challenge_id] = {"reasoning_class": cls, "stats": stats, **g}
        print(f"  gallery: {ch.challenge_id:28} {stats['solved']}/{stats['n']} solved")

    header = [
        "# Failure galleries — how models fail each challenge", "",
        "> The qualitative layer: archetypal wrong moves (with real quotes) and what solvers "
        "did differently. Mined from the saved conversation transcripts — not a re-run.",
        "> Challenges are tagged by **reasoning-failure class** (the kind of uncertainty they "
        "probe), so failures compose across challenges into a debugging profile.", "",
    ]
    md = "\n".join(header) + "\n" + "\n".join(sections)
    layout.ensure()
    (layout.LEADERBOARDS / "failure-galleries.md").write_text(md)
    (layout.LONG_HORIZON / "galleries.json").write_text(json.dumps(payload, indent=2))
    print(f"\nwrote failure-galleries.md ({len(challenges)} challenges)")
    return md


def main():
    asyncio.run(build())


if __name__ == "__main__":
    main()
