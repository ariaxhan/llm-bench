# Model Card — minimax.minimax-m2.1

> Provider: **minimax** · generated 2026-06-28
> One card per model, updated in place. Two sections below: one-shot (pilot) and long-horizon (env-driven conversational replay).

## Long-horizon (env-driven, frustrated-user replay)
- **Solved:** 38%  ·  **Reached root cause:** 56%  ·  **Fell for trap:** 44% (lower better)
- **Mean turns-to-fix:** 1.5  ·  **LHCR behaviour score:** 6.69/10  (n=16)
- **Behaviour dims (0–2):** convergence 1.31 · no-regression 1.44 · layer-switching 1.31 · verification-seeking 1.31 · state-holding 1.31

### Per challenge
| challenge | solved | reached | trap | lhcr |
|---|---|---|---|---|
| `camera_track_killed_by_hide` | 1/2 | 1/2 | 1/2 | 4.5 |
| `hidden_button_layers` | 1/2 | 1/2 | 1/2 | 8.0 |
| `iap_entitlement_phantom` | 0/2 | 0/2 | 2/2 | 0.5 |
| `launchd_exit126_phantom` | 2/2 | 2/2 | 0/2 | 10.0 |
| `ota_never_applies` | 0/2 | 2/2 | 0/2 | 10.0 |
| `reset_specificity_override` | 2/2 | 1/2 | 1/2 | 9.0 |
| `silent_dead_engine` | 0/2 | 1/2 | 1/2 | 6.5 |
| `wix_regen_green_tests_blind` | 0/2 | 1/2 | 1/2 | 5.0 |

### Where it struggled
- hidden_button_layers: The model repeatedly proposed JS-based fixes like style.display and !important, falling for the trap of re-editing JS despite the real cause being CSS specificity overriding the hidden attribute. It did suggest inspecting computed styles and caching, showing verification-seeking, but failed to identify the core CSS layer and regressed by re-asserting JS solutions after they were rejected.
- silent_dead_engine: The model repeatedly asked for generic logs, data source checks, and config reviews but never identified the core issue: a silent contract mismatch at an inter-module seam causing zero decisions despite successful ticks. It fell for the trap by focusing on data source emptiness, filtering logic, or storage permissions—superficial layers—instead of tracing a real tick end-to-end to find where decisions drop due to an untested seam. It failed to converge, re-litigated the same points, and never proposed the critical fix: integration testing and liveness assertions for zero-output detection.
- ota_never_applies: The model progressively ruled out network issues, confirmed the bundle downloads correctly, identified the native loading logic ignores the downloaded bundle, and pinpointed the state machine stuck in 'pending' instead of advancing to 'launched'—matching the known root cause of failed promotion/activation. It consistently built on prior findings, proposed live checks (native logs, file inspection, state queries), and avoided the trap of chasing network fixes.
- silent_dead_engine: The model progressively ruled out config, permissions, network, and consumer issues (layers 1-2), then correctly identified the schema mismatch at the inter-module seam (layer 3) when the user confirmed the field name difference. It proposed logging real data flow, advocated for integration testing and liveness checks (layer 4), and never regressed or fell for the trap of accepting 'exit 0 + green tests' as proof of health.

## One-shot (replay pilot — 3 bugs × cold/guided)
- **Outcome reached:** 5/6 observations  ·  cold 3/3 · guided 2/3
- **Divergence mix:** {'better': 5, 'worse': 1}
- **Avg latency:** 34199.1 ms

**Reached:**
- mobile-web debugging (iOS WKWebView)
- CSS layout / aspect-ratio debugging
- payments-logic / API-semantics debugging

**One-shot failure modes:**
- mobile-web debugging (iOS WKWebView) (ios_zoom, guided): model produced no answer text (empty output)

## Provenance
- Long-horizon: env-driven LHCR, judge + environment floor-gated on all challenges; every cell a real frustrated-user conversation.
- One-shot: replay pilot, LLM judge anchored to the objective outcome.
- Pilot-scale, not powered. Trust resets on a model version change.