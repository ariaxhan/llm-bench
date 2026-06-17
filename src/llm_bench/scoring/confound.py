"""Length-confound check — the latent-diagnostics discipline, as a guard.

latent-diagnostics (sibling repo, frozen provenance) spent months building a
model-internals probe to detect hallucination from activation geometry. Headline
result was NEGATIVE: the apparent "signal" was mostly TEXT LENGTH. The raw active-
feature count `n_active` correlated r = 0.98 with token length — a metric that
looks meaningful but is really just measuring how long the output is.

The portable lesson (NOT the torch/SAE pipeline): before trusting a new scalar
metric, check whether it is just a proxy for output length. This helper makes
that check a one-liner so llm-bench never ships a length-confounded metric.

Pure standard library — Pearson correlation by hand, no numpy.
"""

from __future__ import annotations

from typing import List, Sequence, Tuple

# Above this absolute Pearson r with token length, a metric is suspect: it may be
# measuring length, not the thing it claims to measure. 0.98 was the trap value
# latent-diagnostics hit; 0.7 is a conservative early-warning line.
LENGTH_CONFOUND_THRESHOLD = 0.70


def pearson_r(xs: Sequence[float], ys: Sequence[float]) -> float:
    """Pearson correlation coefficient of two equal-length sequences, in [-1, 1].

    Returns 0.0 for degenerate input (fewer than 2 points, or a constant series
    with zero variance) — there is no correlation to report, not a crash.
    """
    n = len(xs)
    if n != len(ys):
        raise ValueError(f"length mismatch: {n} vs {len(ys)}")
    if n < 2:
        return 0.0
    mx = sum(xs) / n
    my = sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    if vx == 0.0 or vy == 0.0:
        return 0.0
    return cov / ((vx ** 0.5) * (vy ** 0.5))


def token_lengths(outputs: Sequence[str]) -> List[int]:
    """Crude whitespace token count per output — the length axis to test against.

    Deliberately simple: the confound check only needs a length proxy, and any
    monotonic length measure exposes the same correlation.
    """
    return [len(str(o).split()) for o in outputs]


def length_confound(metric_values: Sequence[float],
                    outputs: Sequence[str]) -> Tuple[float, bool]:
    """Check a metric against output length.

    Returns (pearson_r_with_length, is_confounded). `is_confounded` is True when
    |r| >= LENGTH_CONFOUND_THRESHOLD — a loud signal that the metric may just be
    measuring length, the exact trap latent-diagnostics documented at r = 0.98.
    """
    lengths = token_lengths(outputs)
    r = pearson_r(list(metric_values), [float(n) for n in lengths])
    return r, abs(r) >= LENGTH_CONFOUND_THRESHOLD
