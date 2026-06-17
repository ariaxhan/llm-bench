# Consolidation — llm-bench is the home for the LLM-eval theme

As of 2026-06-17, `llm-bench` is the single home for the LLM-evaluation /
instrumentation theme. The theme had respawned across four sibling repos for
essentially one negative research result, each time re-philosophized into a new
repo-shaped object. This note records what was absorbed here and from where.

The sibling repos are **NOT deleted**. They remain as frozen provenance — read
their git history for the full derivation. We harvested the worthwhile, working
capability into the one repo with a shippable shape (CLI + passing tests +
leaderboard + MIT).

## What was absorbed, from each sibling

### wrong-convergence → the earned-certainty scorer (grafted, code)
Source: `wrong-convergence/src/wrong_convergence/scoring/{authority,support,cofragility}.py`
plus its canonical claims corpus (`data/example_claims.jsonl`).

Now lives in `src/llm_bench/scoring/`:
- `authority.py` — `performed_authority(claim) -> [0,1]`: how certain/prescriptive an output *sounds*.
- `support.py` — `earned_support(claim) -> [0,1]`: how much the evidence actually backs it.
- `cofragility.py` — `cofragility_score(claim) -> int (0-12)`: count of co-active bad-state indicators.
- `__init__.py` — `score_claim(claim)` ties them together.

**Load-bearing fidelity fact (preserved, do not undo):**

    authority_support_lag = performed_authority - earned_support   # PURE gap, [-1, 1]

`cofragility` is a **separate** integer amplifier (0-12), never folded into the
lag. The risk flag is `lag >= 0.30 OR cofragility >= 4`. A prior wrong-convergence
bug folded cofragility into the lag, and the named bounded metric silently became
an unbounded cofragility count. The split is the whole point — see
`docs/metrics-hygiene.md`.

Verified on the canonical corpus: the confident-hallucination scores lag **+0.60**
(cofragility 10, flagged); the well-sourced fact scores lag **-0.65** (cofragility
0, not flagged) — matching the wrong-convergence reference separation.

### latent-diagnostics → the length-confound discipline (lesson, not code)
Source: `latent-diagnostics` (model-internals probing). Its headline result is
NEGATIVE — internals geometry does not detect hallucination (effect size ~0.05),
and most apparent "signal" was **text length**: the raw active-feature count
correlated **r = 0.98** with token length.

We did NOT port its torch / SAE / statsmodels pipeline (heavy deps, negative
result). What we kept is the *discipline*, as:
- `docs/metrics-hygiene.md` — the documented lesson + the r ≈ 0.98 trap, concretely.
- `src/llm_bench/scoring/confound.py` — a stdlib `length_confound(metric, outputs)`
  helper (Pearson r by hand) so the check is a one-liner. This is freshly written
  to the lesson, not a port of the heavy experiment code.

### neural-polygraph → nothing (confirmed)
Byte-identical archived ancestor of latent-diagnostics. Confirmed it carries
nothing unique beyond what latent-diagnostics already contributed. Ignored.

## How to run the absorbed scorer

```bash
llm-bench score-certainty                 # score the bundled canonical corpus
llm-bench score-certainty my_claims.jsonl # score your own JSONL corpus
llm-bench score-certainty --json          # raw scored JSON instead of markdown
```

Corpus format: one JSON claim per line (`#` comment lines and blanks skipped).
The bundled canonical corpus lives at `tests/fixtures/earned_certainty_claims.jsonl`.

## Integration gap (stated plainly — not faked)

The earned-certainty scorer and llm-bench's task verifiers are **different
layers**:
- `llm-bench run` verifiers answer *"how good is the model on this task"* — they
  take `(output: str, expected: dict)` and need a known-correct answer.
- the earned-certainty scorer answers *"did this output earn its confidence"* —
  it reads structured claim fields (`provenance_depth`, `evidence_items`,
  `baseline_used`, `instrument_type`, ...) and needs no ground-truth reference.

**The scorer does NOT yet run on raw `llm-bench run` outputs.** A real task run
produces raw text plus a verifier score, not the structured authority/support
fields the scorer reads. Bridging the two would require an extractor that infers
those fields from a model's raw output (or a task schema that carries them).
That extractor is **not built** — so the scorer ships as a standalone subcommand
over a structured claims corpus, with this gap documented rather than faked.

## Remaining punch list to shippable (NOT acted on in this commission)

- [ ] PyPI publish (Aria triggers — out of scope here).
- [ ] An adapter that derives claim fields from real `llm-bench run` outputs, so
      `score-certainty` can score live benchmark runs (closes the integration gap).
- [ ] A README section pointing at `score-certainty` and this consolidation note.
- [ ] Decide whether the scorer's text heuristics (confidence/caveat/scope word
      lists) should be tunable/configurable rather than hard-coded.
