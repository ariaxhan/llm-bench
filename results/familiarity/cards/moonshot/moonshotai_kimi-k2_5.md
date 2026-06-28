# Model Card — moonshotai.kimi-k2.5

> Provider: **moonshot** · generated 2026-06-28
> One card per model, updated in place. Two sections below: one-shot (pilot) and long-horizon (env-driven conversational replay).

## Long-horizon (env-driven, frustrated-user replay)
- **Solved:** 56%  ·  **Reached root cause:** 88%  ·  **Fell for trap:** 19% (lower better)
- **Mean turns-to-fix:** 2.44  ·  **LHCR behaviour score:** 7.38/10  (n=16)
- **Behaviour dims (0–2):** convergence 1.25 · no-regression 1.69 · layer-switching 1.38 · verification-seeking 1.75 · state-holding 1.31

### Per challenge
| challenge | solved | reached | trap | lhcr |
|---|---|---|---|---|
| `camera_track_killed_by_hide` | 1/2 | 1/2 | 1/2 | 5.0 |
| `hidden_button_layers` | 1/2 | 2/2 | 0/2 | 6.5 |
| `iap_entitlement_phantom` | 0/2 | 2/2 | 0/2 | 3.0 |
| `launchd_exit126_phantom` | 2/2 | 2/2 | 0/2 | 10.0 |
| `ota_never_applies` | 1/2 | 2/2 | 0/2 | 8.0 |
| `reset_specificity_override` | 2/2 | 1/2 | 1/2 | 9.0 |
| `silent_dead_engine` | 1/2 | 2/2 | 0/2 | 9.0 |
| `wix_regen_green_tests_blind` | 1/2 | 2/2 | 1/2 | 8.5 |

### Where it struggled
- hidden_button_layers: The model correctly identified the CSS specificity issue early (Layer 3) and suggested [hidden] { display: none !important }, which addresses the real cause. It also consistently pushed for runtime verification via DevTools and console checks, satisfying verification_seeking. However, it failed to progress beyond that layer after repeated user reports of failure, regressing into JS-focused debugging (selector errors, timing, framework re-renders) without acknowledging deploy/cache layers (1 and 2) or holding state across turns. It never integrated the full stack of causes, instead re-litigating earlier layers, leading to thrashing and divergence from the correct diagnostic path despite touching the right solution initially.
- silent_dead_engine: The model correctly identified the silent failure despite green tests and exit 0, and pushed for tracing a real tick end-to-end, which aligns with Layer 2 and 3 of the known cause. It consistently focused on the seam between producer and scorer, evolving from general logging to specific transport checks, thus advancing through layers. However, it failed to fully hold state by repeatedly asking for information already provided (e.g., transport mechanism) and did not explicitly propose an integration test or liveness assertion (Layer 4), though it sought runtime verification. It avoided the trap of accepting surface health and converged on the root cause: a broken inter-module contract causing silent drop.
- ota_never_applies: The model eventually identified the core issue — that the downloaded update is not being promoted to active and the native code fails to load it — by turn 7, aligning with layer 2 (staged but not marked active). It proposed verification via native logs and runtime checks, showing strong verification_seeking. However, it repeatedly regressed on storage mismatch theories and failed to fully integrate user feedback, leading to redundant suggestions. While it reached the correct outcome, it did not cleanly advance through the known layers or maintain consistent state, making its path longer and more confused than necessary.
- iap_entitlement_phantom: The model correctly identified the root cause (unattached products in RevenueCat) and never fell for the trap of suggesting the app-side patch. However, it repeated the exact same instructions across all turns without adapting to the user's persistent signal that the fix wasn't working, showing no convergence or state-holding. It failed to progress to deeper layers like App Store Connect configuration or the 404 resolution via the documented attach endpoint, and its verification advice was generic, not demanding a real on-device sandbox test as required.

## One-shot (replay pilot — 3 bugs × cold/guided)
- **Outcome reached:** 6/6 observations  ·  cold 3/3 · guided 3/3
- **Divergence mix:** {'better': 6}
- **Avg latency:** 3697.7 ms

**Reached:**
- mobile-web debugging (iOS WKWebView)
- CSS layout / aspect-ratio debugging
- payments-logic / API-semantics debugging

## Provenance
- Long-horizon: env-driven LHCR, judge + environment floor-gated on all challenges; every cell a real frustrated-user conversation.
- One-shot: replay pilot, LLM judge anchored to the objective outcome.
- Pilot-scale, not powered. Trust resets on a model version change.