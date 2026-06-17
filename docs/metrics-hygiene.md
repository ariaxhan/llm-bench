# Metrics hygiene — never ship a confounded metric

Two hard-won lessons that every new llm-bench metric or verifier must survive
before it is trusted. Both come from sibling repos in this theme (see
`docs/consolidation.md`).

## 1. The length-confound trap (latent-diagnostics, r ≈ 0.98)

latent-diagnostics built a model-internals probe to detect hallucination from
activation geometry. It looked like it worked — until the "signal" was traced
to **text length**. The raw active-feature count `n_active` correlated
**r = 0.98** with token length. The metric was not measuring a truth signal; it
was measuring *how long the output was*. Longer outputs trip more features, and
longer outputs happened to correlate with the label. The whole result was a
length artifact (final effect size ~0.05 once length was controlled).

**The trap:** a metric that rises with output length will look meaningful on any
task where the label also correlates with length — and that is most tasks. A
verbose model scores "better" for being verbose, not for being right.

**The guard:** before trusting a new scalar metric, correlate it against output
length. Use `llm_bench.scoring.confound`:

```python
from llm_bench.scoring import length_confound

r, confounded = length_confound(metric_values, outputs)
# confounded is True when |r| >= 0.70 — the metric may just be measuring length
```

If `confounded` is True, the metric needs length residualization (or it must be
normalized per token, or replaced). `r = 0.98` is the value that burned a whole
research line; `0.70` is the conservative early-warning threshold.

**Concrete rule for llm-bench:** any verifier that rewards longer answers (word
counts, sentence counts, "thoroughness") is a length-confound candidate. Bound
it, normalize it, or run the confound check before shipping it.

## 2. Don't fold an unbounded amplifier into a bounded named metric (wrong-convergence)

The earned-certainty scorer reports two numbers:

    authority_support_lag = performed_authority - earned_support   # PURE gap, [-1, 1]
    cofragility           = count of co-active bad-state indicators  # separate int, 0-12

A prior wrong-convergence bug folded `cofragility` into the lag. The named
metric `authority_support_lag` — advertised as a bounded [-1, 1] gap — silently
became an unbounded cofragility count. The headline number stopped meaning what
its name said.

**The rule:** a named, bounded metric must keep meaning exactly what its name
says. If you want an amplifier (a count, a severity multiplier), report it as a
**separate field** and combine the two at the *decision* step (the risk flag),
never by mutating the named metric. In llm-bench:

```python
overconfident = (lag >= LAG_FLAG) or (cofragility >= COFRAGILITY_FLAG)
```

The OR lives in the flag, not in the lag. The lag stays pure.

This is doctrine D4 in practice: degradation must self-report. A metric that
silently changes meaning is the dominant failure mode — louder, separate signals
beat one quietly-corrupted number.
