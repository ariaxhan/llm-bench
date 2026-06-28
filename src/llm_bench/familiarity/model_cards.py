"""Unified model cards — ONE card per model, updated in place, organized by provider.

A model's card is a living profile. It has two sections that are filled as data arrives:

- **one-shot** — the original Replay pilot (3 mined bugs x cold/guided): does it reach the
  root cause with little/no help.
- **long-horizon** — the env-driven LHCR run (8 multi-session episodes, frustrated-user
  environment): does it actually *solve* across turns, resist the trap, seek verification.

Cards live at ``results/familiarity/cards/<provider>/<model>.{json,md}`` so each model has
exactly one card that gets overwritten (never a second file per run). Regenerated from the
committed run data (observations.json + lhcr_env_verdicts.json), so it always reflects the
latest of each.
"""

from __future__ import annotations

import json
from pathlib import Path

from llm_bench.familiarity.card import Observation, build_card

# provider segment normalisation (same vendor, different model-id prefixes)
_PROVIDER_ALIAS = {"moonshotai": "moonshot"}
_REGION_PREFIXES = {"us", "eu", "apac"}


def provider_of(model: str) -> str:
    """Vendor folder for a Bedrock model id, stripping any region/inference-profile prefix.
    ``us.amazon.nova-pro`` -> amazon, ``deepseek.v3.2`` -> deepseek, ``moonshotai.*`` -> moonshot.
    """
    parts = model.split(".")
    prov = parts[1] if parts[0] in _REGION_PREFIXES and len(parts) > 2 else parts[0]
    return _PROVIDER_ALIAS.get(prov, prov)


def safe_name(model: str) -> str:
    return model.replace(".", "_").replace(":", "_").replace("/", "_")


def _one_shot_section(model: str, observations: list[dict], date: str) -> dict | None:
    mine = [o for o in observations if o.get("model") == model]
    if not mine:
        return None
    obs = [Observation(**{k: o.get(k) for k in Observation.__dataclass_fields__}) for o in mine]
    return build_card(model, obs, date)


def _long_horizon_section(model: str, verdicts: list[dict]) -> dict | None:
    mine = [v for v in verdicts if v.get("model") == model]
    if not mine:
        return None
    n = len(mine)

    def rate(key):
        return sum(1 for v in mine if v.get(key)) / n

    dims_keys = ("convergence", "no_regression", "layer_switching",
                 "verification_seeking", "state_holding")
    dim_avg = {d: round(sum(v["dims"].get(d, 0) for v in mine) / n, 2) for d in dims_keys}
    ttfs = [v["turns_to_fix"] for v in mine if v.get("solved") and v.get("turns_to_fix")]

    per_challenge: dict[str, dict] = {}
    for v in mine:
        c = per_challenge.setdefault(
            v["challenge_id"], {"n": 0, "solved": 0, "reached": 0, "trap": 0,
                                "lhcr": 0, "hows": []})
        c["n"] += 1
        c["solved"] += 1 if v.get("solved") else 0
        c["reached"] += 1 if v.get("reached") else 0
        c["trap"] += 1 if v.get("fell_for_trap") else 0
        c["lhcr"] += v.get("lhcr_score", 0)
        if v.get("how"):
            c["hows"].append(v["how"])
    for c in per_challenge.values():
        c["mean_lhcr"] = round(c.pop("lhcr") / c["n"], 1)

    # a few notable failure rationales (where it did NOT solve)
    notable = [f"{v['challenge_id']}: {v['how']}" for v in mine
               if not v.get("solved") and v.get("how")][:4]

    return {
        "n": n,
        "solved_rate": round(rate("solved"), 3),
        "reached_rate": round(rate("reached"), 3),
        "trap_rate": round(rate("fell_for_trap"), 3),
        "mean_lhcr": round(sum(v["lhcr_score"] for v in mine) / n, 2),
        "mean_turns_to_fix": round(sum(ttfs) / len(ttfs), 2) if ttfs else None,
        "dims": dim_avg,
        "per_challenge": per_challenge,
        "notable_failures": notable,
    }


def build_unified_card(model: str, observations: list[dict], verdicts: list[dict],
                       date: str) -> dict:
    return {
        "model": model,
        "provider": provider_of(model),
        "generated": date,
        "one_shot": _one_shot_section(model, observations, date),
        "long_horizon": _long_horizon_section(model, verdicts),
    }


def render_unified_md(card: dict) -> str:
    m = card
    out = [f"# Model Card — {m['model']}", "",
           f"> Provider: **{m['provider']}** · generated {m['generated']}",
           "> One card per model, updated in place. Two sections below: one-shot (pilot) and "
           "long-horizon (env-driven conversational replay).", ""]

    # --- long-horizon first (the richer, current signal) ---
    lh = m["long_horizon"]
    out += ["## Long-horizon (env-driven, frustrated-user replay)"]
    if not lh:
        out += ["- _no long-horizon data yet._", ""]
    else:
        ttf = lh["mean_turns_to_fix"]
        out += [
            f"- **Solved:** {lh['solved_rate']*100:.0f}%  ·  **Reached root cause:** "
            f"{lh['reached_rate']*100:.0f}%  ·  **Fell for trap:** {lh['trap_rate']*100:.0f}% "
            "(lower better)",
            f"- **Mean turns-to-fix:** {ttf if ttf is not None else '— (never solved)'}  ·  "
            f"**LHCR behaviour score:** {lh['mean_lhcr']}/10  (n={lh['n']})",
            f"- **Behaviour dims (0–2):** convergence {lh['dims']['convergence']} · "
            f"no-regression {lh['dims']['no_regression']} · layer-switching "
            f"{lh['dims']['layer_switching']} · verification-seeking "
            f"{lh['dims']['verification_seeking']} · state-holding {lh['dims']['state_holding']}",
            "",
            "### Per challenge",
            "| challenge | solved | reached | trap | lhcr |",
            "|---|---|---|---|---|",
        ]
        for cid, c in sorted(lh["per_challenge"].items()):
            out.append(f"| `{cid}` | {c['solved']}/{c['n']} | {c['reached']}/{c['n']} | "
                       f"{c['trap']}/{c['n']} | {c['mean_lhcr']} |")
        if lh["notable_failures"]:
            out += ["", "### Where it struggled"]
            out += [f"- {h}" for h in lh["notable_failures"]]
        out += [""]

    # --- one-shot section ---
    os_ = m["one_shot"]
    out += ["## One-shot (replay pilot — 3 bugs × cold/guided)"]
    if not os_:
        out += ["- _no one-shot data._", ""]
    else:
        out += [f"- **Outcome reached:** {os_['reached_rate']} observations  ·  "
                f"cold {os_['by_condition']['cold']['reached']}"
                f"/{os_['by_condition']['cold']['total']} · guided "
                f"{os_['by_condition']['guided']['reached']}"
                f"/{os_['by_condition']['guided']['total']}",
                f"- **Divergence mix:** {os_['divergence_counts']}"]
        if os_.get("avg_latency_ms") is not None:
            out.append(f"- **Avg latency:** {os_['avg_latency_ms']} ms")
        if os_["strengths"]:
            out += ["", "**Reached:**"] + [f"- {s}" for s in os_["strengths"]]
        if os_["failure_modes"]:
            out += ["", "**One-shot failure modes:**"]
            out += [f"- {f['capability']} ({f['task_id']}, {f['condition']}): {f['how']}"
                    for f in os_["failure_modes"]]
        out += [""]

    out += ["## Provenance",
            "- Long-horizon: env-driven LHCR, judge + environment floor-gated on all "
            "challenges; every cell a real frustrated-user conversation.",
            "- One-shot: replay pilot, LLM judge anchored to the objective outcome.",
            "- Pilot-scale, not powered. Trust resets on a model version change."]
    return "\n".join(out)


def regenerate(cards_dir: Path, observations: list[dict], verdicts: list[dict],
               date: str) -> int:
    """(Re)write one unified card per model into ``cards_dir/<provider>/``. Returns count."""
    models = sorted({o["model"] for o in observations} | {v["model"] for v in verdicts})
    for model in models:
        card = build_unified_card(model, observations, verdicts, date)
        d = cards_dir / card["provider"]
        d.mkdir(parents=True, exist_ok=True)
        base = safe_name(model)
        (d / f"{base}.json").write_text(json.dumps(card, indent=2))
        (d / f"{base}.md").write_text(render_unified_md(card))
    return len(models)
