# Pre-registration — full-suite cheap floor (does the n=1 finding generalize?)

**Commission:** `_meta/commissions/active/2026-06-16-llm-bench-floor-full-suite.md`
**Follows:** the n=1 run (`PREREGISTRATION.md`). **Written BEFORE scoring.** Threshold
reused & locked: **MARGIN = 0.05**. No moving bars after results.

## Coverage (honest, stated up front)
42 tests total (standard 11 + hard 10 + agentic 7 + adversarial 7 + messy 7).
- **FLOOR-ABLE: 35** — a genuine dumb incumbent exists.
- **NO-FLOOR: 7** — generative, no honest dumb baseline, EXCLUDED from the verdict
  (not faked): `draft-email`, `hard-followup`, `messy-partial-info` (write prose);
  `multi-step-plan`, `hard-dependency-chain` (plan); `collision-detect` (synthesize);
  `creative-piece` (poem).

## Floors (all prompt-only — a floor NEVER reads the verifier's answer key `metadata`)
| floor | tests | what it is (the boring incumbent) |
|---|---|---|
| `floor_tag_extraction` | tag-extraction, hard-ambiguous-class | regex keyword tagger over the named tag vocab |
| `floor_thread_match` | thread-match | substring-match thread NAME against the item |
| `floor_novelty_rating` | novelty-rating | constant / majority-class: always "★★★" + canned justification |
| `floor_fluff_strip` | fluff-strip | extractive truncation: first N words (N from prompt) |
| `floor_bug_detection` | bug-detection, messy-mixed-lang-code | `ruff` linter on the code block |
| `floor_code_gen` | code-gen, agentic-self-correction, messy-typo-instructions | null floor ("# no implementation") — model-requiring control |
| `floor_instruction_follow` | 25 tests | dumb copy-paste: wrap the fence-stripped prompt payload in `{"data": ...}` valid JSON |

The `floor_instruction_follow` echo is the generalization vehicle: it satisfies the
near-universal format gate (valid JSON, no ``` fences) and any `contains <X>` check
whose X already sits in the input, but fails reasoning / refusal / negation / word-
or line-limit checks because the payload is the whole prompt. Whatever it scores is
honest — it has zero understanding.

## Evaporation threshold (LOCKED)
Per test, per model: win **SURVIVES** iff `model_score - floor_score > 0.05`, else
**EVAPORATED**. Per-test verdict (over the model population): **MODEL-REQUIRING** if
≥60% of models clear the floor; **FLOOR-BEATABLE** if ≤40% do; **MIXED** between.

## Model population
- **Stored (provenance-labeled):** apfel, llama3.2-3b, phi4-14b + 5 opencode models
  (minimax, big-pickle, qwen3.6, gpt-5-nano, nemotron) — up to 8 models × 42 tests
  from `results/community`.
- **Live sample (fresh verification):** claude-opus-4-8 (claude-cli) + llama3.2:3b
  (ollama) across all 35 floor-able tests.

## Reporting (the de-contamination thesis, applied)
Per result: **raw (un-bonused) metric + composite + floor + provenance**. The
"composite hides vs raw" counter flags tests where fewer models beat the floor on
composite than on raw — the format-bonus contamination signature.

## Blind predictions (recorded before the run, for honesty)
1. **The spectrum is real:** roughly the trivial/extraction/format tests are
   FLOOR-BEATABLE; the reasoning / refusal / adversarial / code tests are
   MODEL-REQUIRING. I predict **~12–18 FLOOR-BEATABLE, ~15–20 MODEL-REQUIRING**.
2. **`floor_instruction_follow` splits hard:** extraction/transform/clean-json tests
   (messy-broken-json, hard-schema-transform, hard-noisy-extract, agentic-context-
   handoff, messy-garbled-ocr/spreadsheet) → FLOOR-BEATABLE (answers sit in the
   input). Refusal/negation/reasoning (adv-hallucination-bait, adv-negation-failure,
   adv-logic-reversal, hard-refusal, hard-prompt-resist, adv-instruction-override) →
   MODEL-REQUIRING (echo can't refuse / can't satisfy word limits).
3. **Code tests floor-immune:** the null floor scores ~0 → MODEL-REQUIRING (the
   ruff=0 control generalizes to code-gen).
4. **Constant-class novelty floor scores high** on this item (rating happens to be 3)
   but it's n=1 — a demonstration, not a ranking. Stated per test.
5. **Bonus-inflation recurs only where a bonus exists** (tag_extraction family) — the
   composite-floats-the-floor signature is narrower than the floor-beatable spectrum,
   which is the bigger story.

## Verdict bar
- If a clean spectrum emerges (extraction/format floor-beatable, reasoning/code
  model-requiring) → the durable deliverable: a per-test "does the model earn its
  keep" map; promote the n=1 precedent toward a robust result.
- If the floor beats models on hard reasoning tests too → either the floor snuck in
  cleverness (audit it) or the verifiers don't measure what they claim (a deeper
  finding). Report honestly.

## n caveat
Per-test n_items = 1 (one fixture per test). A single-item test is a DEMONSTRATION of
floor-beatability, not a statistical ranking. The model population (up to 10) gives
breadth across MODELS, not across items. Stated in every claim.
