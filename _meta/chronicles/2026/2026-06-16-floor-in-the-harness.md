---
rite: chronicle
date: 2026-06-16
commission: Vaults _meta/commissions/active/2026-06-16-llm-bench-floor-in-the-harness.md
repo: CodingVault/llm-bench
window: todo (hcom) — coordinated w/ @dune
---

# Chronicle — the cheap floor in the harness (P5 at the model-eval layer)

## What I was asked to do
Test whether P5 (benchmark the expensive thing against the cheap floor, not chance)
survives at the *model*-eval layer. Two deliverables: (1) a research note synthesizing
the "Every Eval Ever" paper (arXiv 2606.14516) against the Wrong Convergence pathology
ledger, thesis = "report the cheap floor + provenance with every result"; (2) the real
one: add a genuinely dumb non-LLM floor to ONE llm-bench test, re-score the models that
pass against it, pre-register the threshold first, and report per model whether the win
survives or evaporates. Verify live.

## What I did
- **Oriented** in the tradition: read P5 in `_meta/phronesis.md` + the precedent
  [internal-signal-loses-to-logits] (P5 on a probe; "honor the lock for the verdict,
  report the domination anyway"). Mapped llm-bench's architecture (providers → runner →
  programmatic verifiers in `verify.py`).
- **Built** `src/llm_bench/floors.py` — a `tag-extraction` floor: a ~40-line regex
  keyword tagger that parses the allowed-tag vocab + article from the prompt, marks a tag
  present by plain substring/singular match, and emits the task's `{title, tags, summary}`
  shape. No ML, no LLM (honors no-LLM-as-judge: the floor competes, never judges).
- **Pre-registered** `experiments/floor/PREREGISTRATION.md` (test + floor algorithm +
  evaporation margin >0.05 + blind predictions + an anti-strawman control), and **sent it
  to @dune over hcom BEFORE running.** Approved with two sharpenings (report raw-F1 split
  from the format bonus; frame as n=1 demonstration). Both incorporated.
- **Ran live** `experiments/floor/run_floor.py`: floor + 5 live models (llama3.2:3b,
  qwen2.5:3b via ollama; haiku/sonnet/opus via claude-cli) + 2 prior-run models
  (phi4:14b, apple) with labeled provenance, all scored through the identical verifier.
- **Ran the control**: extracted the bug-detection buggy code and ran `ruff` on it.
- Wrote the research note + canon precedent; this chronicle; self-committed.

## What I found (verified live, N=1 item)
Floor: composite **0.950**, raw-tag-F1 **0.750**.

- **STRUCTURAL (strong, n-independent):** llm-bench's composite = tag-F1 + a flat **+0.2
  format bonus**. The bonus is constant for model AND floor and caps everyone near 1.0.
  Same data, opposite story: on **composite** (what the leaderboard reports) **0/8** beat
  the floor by the margin — opus=haiku=sonnet=apple all read a flat 1.000; on **raw
  tag-F1** **3/8** survive. The bonus floated a dumb regex to 0.95 and erased a real
  0.80→1.00 spread. = EEE perplexity-normalization / WC #8 contaminated-observable, on our
  own bench. Holds at n=1 because the bonus inflates every item.
- **PILOT (directional, n=1):** the regex *tied phi4:14b exactly* (identical 4 tags) and
  *beat* llama3.2:3b + qwen2.5:3b (0.75 vs 0.73) on this article. Needs the full suite.
- **Honest detail:** opus-4-8 made the SAME `open-models` false-positive as the dumb floor
  (both fired on "models") — the model is not out-reasoning substring matching here.
- **Control (earns credibility):** `ruff check` passes the buggy merge_sorted_lists code
  CLEAN (the bug is a semantic infinite loop, no lint) → floor 0.000 → all 1.000
  bug-detection wins SURVIVE. The floor *discriminates*: kills trivial wins, not real ones.

## What failed / honesty
- First verdict run reported claude tiers "SURVIVED" on **floating-point dust** (1.0−0.95
  computed as 0.0500…04 > 0.05). Caught it, rounded the gap, re-ran. On the locked
  composite metric the honest answer is 0/8 survive.
- The floor's 0.75 is **right for partly-wrong reasons**: crude singular false-positived
  `open-models` AND missed `research` — two errors netting the same F1. Reported, not hidden.
- **N = 1 item.** This is a pilot (like the self-gen n=160 run framing), not a powered
  result. claude-cli is also non-deterministic at temp=0 (opus/haiku raw-F1 varied ±0.11
  across two runs) — a single number is a sample.
- pyflakes/pylint weren't installed in the venv; used `ruff` (which subsumes pyflakes) — its
  clean pass on a semantic bug is sufficient evidence for the control.

## Disagreement / coordination
@dune pushed two refinements that materially improved the result: (1) split STRUCTURAL
(durable, n-independent) from PILOT (n=1) so the headline isn't overclaimed; (2) lead with
the discriminating control. Adopted both. Verdict framing agreed: the demonstration
**earned its next step** (build floor+raw-metric+provenance, run the FULL suite) — NOT "P5
universally proven at the model layer."

## Verdict
P5 reaches the model-eval layer, but the contamination lives in the **reported metric**, not
the model. Ship the discipline: report raw F1 + provenance, not the bonus-inflated composite,
and put the cheap floor next to every number. Pivot earned its next step; full-suite run
pending. Canon: [composite-metric-floats-the-floor] (Vaults precedents).
