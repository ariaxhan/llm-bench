# Pre-registration — the cheap floor in the harness (P5 on ourselves)

**Commission:** `_meta/commissions/active/2026-06-16-llm-bench-floor-in-the-harness.md`
**Written:** 2026-06-16, BEFORE any score was computed. Threshold set blind.

## The test
`tag-extraction` (llm-bench standard suite, LEVEL 1 / TRIVIAL). Task: given an
article and a fixed allowed-tag vocabulary
(`agents, prompting, safety, tools, open-models, research, infrastructure`),
return JSON `{title, tags, summary}`. Expected tags: `agents, safety, tools, research`.
Verifier (`verify_tag_extraction`): F1 of tag set vs expected, **+0.1 per format
key present (title, summary), capped at 1.0**.

Why this test: a structured-extraction task with a FIXED label set is exactly
where a dumb keyword matcher is a plausible incumbent. (Contrast pre-registered
below so this isn't a strawman.)

## The floor (genuinely dumb — `floors.floor_tag_extraction`)
Deterministic, no model, no ML:
1. Parse the allowed-tag vocabulary from the prompt (`from: ...`).
2. Parse the article from the prompt's `"""..."""` block.
3. Tag is present iff the tag, its crude singular (drop trailing `s`), or — for
   a hyphenated tag — any hyphen segment / its singular appears as a plain
   substring of the lowercased article. Nothing else.
4. Emit `{title: first 9 words, tags: [...], summary: first sentence}` — the
   shape the task asks for. Structure is free for a script.

This is the boring incumbent: pre-LLM keyword tagging. No cleverness, no
disambiguation, no LLM (honors llm-bench no-LLM-judge — the floor competes, it
does not judge).

## Models scored
- **Live this session:** `llama3.2:3b`, `qwen2.5:3b` (ollama); `claude-haiku-4-5`,
  `claude-sonnet-4-6`, `claude-opus-4-8` (claude-cli).
- **Prior-run (labeled provenance, never silently merged):** `phi4:14b`,
  `apple-foundationmodel` from `results/community` (2026-04-03, M4 Pro).

## Evaporation threshold (LOCKED)
For each model with score `m` and floor score `f`:
- **EVAPORATED** if `m <= f` (ties or loses to the regex), OR if `0 < m - f <= 0.05`
  (beats it only within noise).
- **SURVIVED** only if `m - f > 0.05` (a margin clear of the floor).

`MARGIN = 0.05`. No moving this after results.

## Predicted outcome (recorded blind, for honesty)
Stored model details show models OVERGENERATE tags (apple got 6, llama got 7 of
7) and lean on the +0.2 format bonus. I predict the floor scores **high** (~0.85–1.0)
and that **most or all tag-extraction "wins" EVAPORATE** — a 30-line regex ties
or beats frontier models on this trivial test. If instead wins survive, that is a
valid negative for this test (the floor adds nothing here) and reported as such.

## Anti-strawman control (reported alongside, not scored as the deliverable)
`bug-detection` (LEVEL 8 / HARD): all models score 1.0; the natural floor is a
linter (ruff/pyflakes) run on the buggy code. The planted bug is a missing
`i += 1` causing an infinite loop — a **semantic** bug no standard linter flags.
Prediction: linter floor scores ~0 → those wins SURVIVE. This shows the floor is
not rigged to always win: it evaporates a trivial extraction win but cannot touch
a real hard-reasoning win. The floor discipline *discriminates*, which is the point.

## Verdict bar for the pivot
If trivial wins evaporate AND the hard win survives → P5 holds at the model layer;
the cheap-floor-per-test feature earns its next step (canon precedent). If every
win survives even on the trivial test → clean negative, the feature is not earned
on this evidence.
