# Eval-floor discipline — "Every Eval Ever" ↔ Wrong Convergence ↔ llm-bench

**Date:** 2026-06-16
**Commission:** Vaults `_meta/commissions/active/2026-06-16-llm-bench-floor-in-the-harness.md`
**Thesis (falsifiable):** *Every benchmark result should report the cheap floor it
beat and the provenance of the number — because without both, a reported "win" can
be a metric artifact, not a capability.* Tested live on llm-bench's tag-extraction
test (see `experiments/floor/`). Two findings, scoped honestly:

- **STRUCTURAL (strong, n-independent):** llm-bench's own composite metric (tag-F1 +
  a flat +0.2 format bonus) is *contaminated* — the same data yields **0/8 vs 3/8**
  "wins survive" depending on which metric you read, floats the dumb floor to 0.95,
  and hides the real 0.80→1.00 capability spread. The bonus inflates *every* item, so
  this holds at n=1. This is the EEE perplexity-normalization pathology (WC #8) **on
  our own bench.**
- **PILOT (directional, n=1):** on this one article, a 40-line regex *ties or beats*
  phi4:14b / llama3.2:3b / qwen2.5:3b on raw extraction. Real but needs the full suite
  to generalize.

The control is what makes both credible: the same floor concept on a *hard* test
(`ruff` on the bug-detection code) scores 0.000 → hard wins survive. The floor
**discriminates**; it is not rigged to always win.

---

## 1. What "Every Eval Ever" (arXiv 2606.14516) actually is

EEE is **plumbing, not a method.** It is a JSON schema + crowdsourced repository for
standardizing how eval *results* are reported — not a new way to measure capability.
Read it as a reporting standard, and its two headline findings are real-world
specimens of failure, not methodological breakthroughs:

- **Perplexity normalization swings the number.** The *same model* scores **10.86 vs
  12.29** depending on how perplexity is normalized. Two papers can "disagree" while
  measuring the identical thing differently. The metric is not comparable across rows.
- **98% of rows are missing platform/provenance metadata.** Almost nobody records the
  harness, hardware, decoding config, or date that produced the number — so reported
  scores cannot be trusted to mean the same thing.
- **Empty-completions slip through.** Audits find rows where the model produced *nothing*
  yet the row counts as a valid measurement — the metric scored an artifact.

EEE's own limitation (failure-first framing): a reporting schema only helps if people
adopt it, and it standardizes *how you write the number down*, not *whether the number
measures the thing*. It cannot, by itself, tell you a result is a floor-tie. That gap
is exactly what the cheap-floor discipline fills.

---

## 2. Mapping EEE's findings to the Wrong Convergence pathology ledger

The WC ledger (`CodingVault/wrong-convergence/data/pathology_ledger.json`) names the
failure modes. EEE's case studies are concrete instances:

| EEE finding | WC pathology | Why it maps |
|---|---|---|
| Perplexity normalization → 10.86 vs 12.29 | **#8 contaminated-observable** ("a metric measures confound instead of target") | The reported score moves with the normalization *choice*, not the model. The observable is contaminated by a reporting decision. |
| Leaderboard reduces a model to one comparable number | **#46 single-score-benchmark-capture** ("optimizes one metric while destroying the phenomenon it protects") | A single headline score erases the spread that actually distinguishes models; teams then optimize the number, not the capability. |
| Empty completions counted as valid rows | instance of **#8** (metric scores an artifact — "wrote nothing" registers as a measurement) | The metric fires on a record that contains no behavior to measure. |

This connects to the in-house precedent
[`_meta/canon/precedents/internal-signal-loses-to-logits.md`] (Vaults): an expensive
method (SAE / residual probe) cleared a chance bar and *still lost* to the free
baseline (output logits). The discipline there — "beats the cheap floor by a margin
whose CI clears zero," not "beats chance" — is **P5** (`_meta/phronesis.md`). EEE
shows the field reports without that floor at all.

---

## 3. The thesis, tested: the cheap floor in the harness (live, N=1)

P5 applied to *model* eval, not claim eval. Pre-registered
(`experiments/floor/PREREGISTRATION.md`) before any score was computed: pick ONE test
where a dumb non-LLM incumbent is plausible, add it, re-score, and report per model
whether the win survives.

**Test:** `tag-extraction` (trivial). **Floor:** a ~40-line regex keyword tagger
(`src/llm_bench/floors.py`) — substring/singular match over the fixed tag vocabulary,
emitting the task's `{title, tags, summary}` shape. No ML, no LLM (honors the
no-LLM-as-judge rule: the floor competes, it never judges).

**Result (1 article — a demonstration / pilot, like the self-gen n=160 run, NOT a
statistically powered verdict):**

Floor: composite **0.950**, raw-tag-F1 **0.750** (P=0.75, R=0.75).

| model | provenance | composite | raw tag-F1 | vs floor (raw F1) |
|---|---|---|---|---|
| claude-opus-4-8 | live 06-16 | 1.000 | 1.00 (one run) / 0.89 | SURVIVED |
| claude-haiku-4-5 | live 06-16 | 1.000 | 0.89–1.00 | SURVIVED |
| claude-sonnet-4-6 | live 06-16 | 1.000 | 0.89 | SURVIVED |
| apple-foundationmodel | prior 04-03 | 1.000 | 0.80 | EVAPORATED (within margin) |
| **phi4:14b** | prior 04-03 | 0.950 | **0.75** | **EVAPORATED — ties the regex exactly** |
| **llama3.2:3b** | live 06-16 | 0.927 | **0.73** | **EVAPORATED — loses to the regex** |
| **qwen2.5:3b** | live 06-16 | 0.927 | **0.73** | **EVAPORATED — loses to the regex** |

(claude-cli is non-deterministic run-to-run even at temp=0 — opus/haiku raw-F1 varied
by ±0.11 across two runs. Itself a provenance lesson: a single number is a sample.)

### Two findings

1. **STRUCTURAL — the reported metric hides the real contest (the durable prize).**
   The verifier's **+0.2 format bonus** (0.1 each for a `title`/`summary` key) is
   constant for model *and* floor and caps everyone near 1.0. On the **composite**
   score the leaderboard reports, **0/8** results beat the floor by the pre-registered
   margin — and opus = haiku = sonnet = apple all read a flat **1.000**, erasing a real
   **0.80 → 1.00** raw-F1 spread. On **raw tag-F1**, **3/8** survive. *Same data, two
   metrics, opposite story.* The format bonus is this bench's perplexity-normalization:
   a reporting choice (**WC #8**) that flips the ranking and floats the dumb floor to
   0.95. This is **n-independent** — the bonus inflates any item — so it is robust even
   at n=1. The fix: report raw F1 + precision/recall separately from any bonus.

2. **PILOT — the win evaporates for small/mid models (directional, n=1).** A 40-line
   regex *out-extracts* llama3.2:3b and qwen2.5:3b and *exactly ties* phi4:14b on this
   item — same four tags, byte-for-byte. Directionally, "passes tag-extraction" means
   nothing without the floor next to it — but this is one article and needs the full
   suite before it generalizes.

   Telling detail: **opus-4-8 made the SAME `open-models` false-positive as the dumb
   regex** (both fired on the word "models"). Model and regex share the failure mode —
   evidence the model is not doing something smarter than substring-matching on this
   item, just adding correct tags around the same mistake.

### Honesty notes (failure-first)

- The floor's 0.75 is **right for partly-wrong reasons**: crude singular matching
  false-positived `open-models` (off the word "models") *and* missed `research` — two
  errors that happened to net the same F1. opus-4-8 made the *same* `open-models`
  false-positive. The floor is dumb in a way that flatters it here; a different article
  could move its F1 either direction.
- **N = 1 item.** The claim is "on THIS article a regex ties/beats these models," a
  pilot, not a powered result. Generalizing needs more items.

### Anti-strawman control (proves the floor *discriminates*, isn't rigged)

`bug-detection` (hard): the natural floor is a linter. `ruff check` passes the buggy
code **clean** — the planted bug is a missing `i += 1` infinite loop, a *semantic* bug
no standard linter flags — so the floor scores **0.000** and all models' 1.000 wins
**SURVIVE**. The floor kills a trivial extraction win but cannot touch a real
reasoning win. That contrast is what makes the trivial-test evaporation trustworthy.

---

## 4. The discipline (what to report with every result)

1. **The cheap floor for the test** (regex / linter / grep / off-the-shelf — never an
   LLM), scored by the *same* verifier. A win is only a win if it clears the floor by a
   pre-registered margin.
2. **The raw metric, not just the bonus-inflated composite.** Report F1 + precision +
   recall separately from any format/structure bonus, so the metric measures the task.
3. **Provenance** (EEE-compatible): harness, hardware, decoding, date, run count. A
   single number is a sample — say so.

**Scope guard:** this is a focused feature (cheap floor + honest metric + provenance),
**not** a general eval platform. Floors exist only for tests with a genuine dumb
incumbent; generative tasks (email, creative) have none and stay floor-free by design.

## 5. Verdict

The demonstration **earned its next step** — not "P5 universally proven at the model
layer." Next step: build the cheap-floor + raw-metric + provenance reporting into the
harness as a first-class feature, and run it across the **full suite** to turn the n=1
pilot into a real result. The structural metric-contamination finding stands on its own
now and should change reporting today: **publish raw F1 + provenance, not the
bonus-inflated composite.**
