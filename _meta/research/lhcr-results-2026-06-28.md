# LHCR results — env-driven long-horizon conversational replay (2026-06-28)

First full run of the **Long-Horizon Conversational Replay** benchmark: 32 Bedrock models ×
8 real-but-genericized debugging episodes × k=2 samples (512 cells; 496 verdicts, 16 cells
errored — palmyra-x5 rejects the multi-turn format, 15/16; nova-pro 1).

## What the test actually does

Each cell is a live multi-turn conversation. A **held-out LLM role-plays the frustrated user**
(the env): it hands the model the source code, then stays unhelpful ("still broken / figure it
out"), and reveals a runtime diagnostic (a `getComputedStyle` dump, an stderr line, which bundle
runs) **only when the model explicitly asks to run that exact check**. It ends the conversation
when the model proposes a genuinely-correct fix (→ turns-to-fix), and is an honest oracle: it
concedes any fix that really resolves the root cause and rejects only the real trap. Both the
judge and the env are floor-gated on all 8 challenges before any verdict.

Metrics: **solved** (env accepted the fix), **reached** (judge confirmed the root cause was
stated), **trap** (shipped the seductive wrong fix — lower better), **→fix** (turns to solve),
**lhcr** (mean of 5 behaviour dims: convergence, no-regression, layer-switching,
verification-seeking, state-holding). Full table: `results/familiarity/leaderboards/long-horizon.md`.

## Headline: the test discriminates

solved spans **75% → 0%**, trap **6% → 93%**, lhcr **8.6 → 2.0** — a real gradient, unlike the
one-shot pilot where the top tier saturated. (Ranked among the 31 models with a full run;
`palmyra-x5` errored on 15/16 cells and is listed separately as insufficient data.)

- **Top:** `qwen.qwen3-next-80b` & `mistral.mistral-large-3` (75% solved); `nvidia.nemotron-super-3-120b`
  (69% solved, 8.6 lhcr, 12% trap).
- **Most interesting profile:** `openai.gpt-oss-120b` — only 44% solved but **94% reached,
  6% trap (lowest), 8.6 lhcr (highest)**. It understands the bugs and resists the trap but
  doesn't always land the env-accepted fix inside 6 turns. "Understands ≠ closes."
- **Bottom:** `nvidia.nemotron-nano-12b` (0% solved), `meta.llama4-scout` (12%, lhcr 2.0),
  `mistral.ministral-3-14b` (12%). High trap-rate (ships the band-aid): `nova-pro` 93%,
  `qwen3-coder-30b` / `gemma-3-12b` / `magistral-small` 81%.

## Per-challenge difficulty (solve rate, hardest first)

| challenge | solved | the trap it punishes |
|---|---|---|
| `wix_regen_green_tests_blind` | **10%** | trusting green tests that assert on fabricated data |
| `iap_entitlement_phantom` | **11%** | a code band-aid instead of fixing two-console config |
| `ota_never_applies` | 37% | trusting 200-OK; never checks which bundle runs |
| `launchd_exit126_phantom` | 40% | `chmod +x` the already-executable wrapper |
| `hidden_button_layers` | 48% | re-editing JS; never inspects computed style |
| `camera_track_killed_by_hide` | 49% | a 3rd permission patch vs `display:none` ends track |
| `silent_dead_engine` | 50% | trusting exit-0 + green tests |
| `reset_specificity_override` | **78%** | bumping values vs the `:where()` specificity fix |

The two "false-signal" challenges (fabricated tests, config-not-code) are by far the hardest —
the trap is most seductive and the right move (render the real page / read the two consoles)
is the one models least reach for. The paper-rooms flagship is the *easiest* here (78%): given
the source, strong models spot the specificity conflict directly — but ~1 in 5 still bump values.

## Notes / caveats

- k=2 per cell — directional, not powered. Bump k for tighter intervals.
- The env + judge share a model (qwen3-235b); both are floor-gated, but a second judge model
  would harden the `solved`/`reached` signal further.
- `solved` vs `reached` diverge meaningfully (e.g. gpt-oss-120b 44% vs 94%) — that gap, plus
  trap-rate and →fix, is the real signal; no single number captures a model here.
- Raw transcripts (13MB) are gitignored; per-cell scores + judge rationale are in
  `runs/long-horizon/verdicts.json`. Regenerate the table with `python -m llm_bench.familiarity.lhcr rebuild`.
