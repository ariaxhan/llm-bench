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

## Integration gap — CLOSED (2026-06-17)

The earned-certainty scorer and llm-bench's task verifiers are **different
layers**:
- `llm-bench run` verifiers answer *"how good is the model on this task"* — they
  take `(output: str, expected: dict)` and need a known-correct answer.
- the earned-certainty scorer answers *"did this output earn its confidence"* —
  it reads structured claim fields (`provenance_depth`, `evidence_items`,
  `baseline_used`, `instrument_type`, ...) and needs no ground-truth reference.

The bridge is now built: `src/llm_bench/scoring/extract.py` maps a real run
result (`TestResult` / a results-file dict) onto a scorer claim. Two entry points:

```bash
llm-bench score-run results/community/<file>.json   # re-score a saved run
llm-bench run <model> --certainty                    # score a fresh run inline
```

### The headline signal: confident-but-wrong

The unique value of scoring a real run (vs a toy corpus) is the verifier ground
truth. **confident-but-wrong** = high performed authority (text-only, `>= 0.45`)
on an output the verifier marked **wrong** (`passed == False`, or `score` below a
tunable floor). Authority is the discriminator: a *hedged* wrong answer is NOT
flagged, a *confident* wrong answer is. This rests on the reliable axis — the
verifier verdict — not on heuristics.

### What the extractor honestly derives vs leaves neutral

| signal | source | honesty |
|--------|--------|---------|
| performed_authority | `raw_output` text | text-only, real (the scorer was always text-capable here) |
| passed / score | verifier | **ground truth — the reliable axis** |
| provenance_depth | citation cues (`[1]`, URLs, "according to", RFC, DOI) | **COARSE proxy** — counts surface cues, a model can fabricate a `[1]` |
| baseline_used | comparison language ("compared to", "vs", "baseline") | **COARSE proxy** |
| source_freshness | date cues ("as of 2026", explicit years) | **COARSE proxy** |
| instrument_type, faithfulness_class, fitting_factor, conflict_level | — | **LEFT NEUTRAL by design** — genuinely undeterminable from a task output; guessing them would fake precision |

The `earned_support` number on a run report is therefore a **coarse text-derived
proxy, not a measurement** — it is labeled that way in code and in every report
header. Do not read it as measured support. The metric you can trust on a run is
the verifier verdict; confident-but-wrong is built on that.

### Residual (stated plainly)

`_save_results` (and the committed community files) **strip `raw_output`** — only
`test_id/score/passed/latency/tokens/details` persist. So `score-run` on a real
community file reports **0 records with raw_output**, says so explicitly, and
cannot compute authority or confident-but-wrong for them (only the verifier-
failure count survives). The full confident-but-wrong path is exercised on
`tests/fixtures/run_with_raw_output.json` (a synthetic run that kept raw_output)
and on `run --certainty` (raw_output is in memory there). To make `score-run`
fully useful on saved files, a future change would persist `raw_output` in
`_save_results` (a `--keep-raw` option) — that is the remaining residual, named
rather than faked.

## Remaining punch list to shippable

- [ ] PyPI publish (Aria triggers — out of scope here).
- [x] An adapter that derives claim fields from real `llm-bench run` outputs
      (`scoring/extract.py` + `score-run` / `run --certainty`) — gap closed.
- [ ] Persist `raw_output` in `_save_results` (`--keep-raw`) so `score-run` can
      compute confident-but-wrong on saved community files, not just live runs.
- [ ] A README section pointing at `score-certainty` / `score-run` and this note.
- [ ] Decide whether the scorer's text heuristics (confidence/caveat/scope word
      lists) should be tunable/configurable rather than hard-coded.
