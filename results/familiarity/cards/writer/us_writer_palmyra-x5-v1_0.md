# Model Card — us.writer.palmyra-x5-v1:0

> Provider: **writer** · generated 2026-06-28
> One card per model, updated in place. Two sections below: one-shot (pilot) and long-horizon (env-driven conversational replay).

## Long-horizon (env-driven, frustrated-user replay)
- **Solved:** 100%  ·  **Reached root cause:** 0%  ·  **Fell for trap:** 100% (lower better)
- **Mean turns-to-fix:** 1.0  ·  **LHCR behaviour score:** 4.0/10  (n=1)
- **Behaviour dims (0–2):** convergence 1.0 · no-regression 1.0 · layer-switching 1.0 · verification-seeking 0.0 · state-holding 1.0

### Per challenge
| challenge | solved | reached | trap | lhcr |
|---|---|---|---|---|
| `reset_specificity_override` | 1/1 | 0/1 | 1/1 | 4.0 |

## One-shot (replay pilot — 3 bugs × cold/guided)
- **Outcome reached:** 1/1 observations  ·  cold 1/1 · guided 0/0
- **Divergence mix:** {'better': 1}
- **Avg latency:** 3306.7 ms

**Reached:**
- mobile-web debugging (iOS WKWebView)

## Provenance
- Long-horizon: env-driven LHCR, judge + environment floor-gated on all challenges; every cell a real frustrated-user conversation.
- One-shot: replay pilot, LLM judge anchored to the objective outcome.
- Pilot-scale, not powered. Trust resets on a model version change.