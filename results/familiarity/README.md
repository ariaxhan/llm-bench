# Familiarity results — layout

Two evaluations, one card per model.

```
familiarity/
├── cards/<provider>/<model>.{json,md}   ← ONE card per model, updated in place.
│                                          Has a long-horizon section + a one-shot section.
├── leaderboards/
│   ├── long-horizon.md     env-driven conversational replay (the headline benchmark)
│   ├── one-shot.md         replay pilot, cross-model table
│   └── one-shot-detailed.md  quote-backed deep dive
└── runs/                   raw run data (regenerate cards/leaderboards from here)
    ├── long-horizon/  verdicts.json · errors.json  (transcripts.json is gitignored — 13MB)
    └── one-shot/      observations.json · replays.json · verdicts.json · pilot_corpus.json
```

## Finding things

- **One model's full profile** → `cards/<provider>/<model>.md` (e.g. `cards/openai/openai_gpt-oss-120b-1_0.md`).
- **Who's best at long-horizon debugging** → `leaderboards/long-horizon.md`.
- **The two evals explained** → `_meta/research/lhcr-results-2026-06-28.md`.

## Regenerating

Everything under `cards/` and `leaderboards/` is derived from `runs/`. After a new run, or to
rebuild from saved data:

```bash
AWS_PROFILE=keystone python -u -m llm_bench.familiarity.lhcr all 2   # full long-horizon run
python -m llm_bench.familiarity.lhcr rebuild                          # re-render from saved verdicts
```

Both refresh the per-model cards and the long-horizon leaderboard. The one-shot pilot
(`python -m llm_bench.familiarity.pilot`) refreshes the one-shot leaderboard and folds its data
into the same cards.

Providers: amazon · deepseek · google · meta · minimax · mistral · moonshot · nvidia · openai ·
qwen · writer · zai.
