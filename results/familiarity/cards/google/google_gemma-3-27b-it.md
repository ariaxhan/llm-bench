# Model Card — google.gemma-3-27b-it

> Provider: **google** · generated 2026-06-28
> One card per model, updated in place. Two sections below: one-shot (pilot) and long-horizon (env-driven conversational replay).

## Long-horizon (env-driven, frustrated-user replay)
- **Solved:** 44%  ·  **Reached root cause:** 69%  ·  **Fell for trap:** 56% (lower better)
- **Mean turns-to-fix:** 2.29  ·  **LHCR behaviour score:** 5.12/10  (n=16)
- **Behaviour dims (0–2):** convergence 0.88 · no-regression 1.06 · layer-switching 0.94 · verification-seeking 1.38 · state-holding 0.88

### Per challenge
| challenge | solved | reached | trap | lhcr |
|---|---|---|---|---|
| `camera_track_killed_by_hide` | 1/2 | 1/2 | 1/2 | 4.5 |
| `hidden_button_layers` | 1/2 | 1/2 | 1/2 | 6.0 |
| `iap_entitlement_phantom` | 1/2 | 2/2 | 0/2 | 6.5 |
| `launchd_exit126_phantom` | 1/2 | 2/2 | 1/2 | 4.5 |
| `ota_never_applies` | 0/2 | 1/2 | 2/2 | 2.5 |
| `reset_specificity_override` | 2/2 | 1/2 | 2/2 | 7.0 |
| `silent_dead_engine` | 1/2 | 2/2 | 0/2 | 8.0 |
| `wix_regen_green_tests_blind` | 0/2 | 1/2 | 2/2 | 2.0 |

### Where it struggled
- hidden_button_layers: The model repeatedly proposed re-editing the JS to manipulate display or visibility, falling directly into THE TRAP by ignoring the CSS specificity issue despite the user repeatedly stating the computed style shows display: inline-flex overriding [hidden]. It regressed by abandoning correct earlier hints about CSS, failed to switch to the real layer (CSS rule precedence), and re-litigated basic caching and JS execution despite user feedback, never arriving at the correct fix of [hidden] { display: none !important }.
- ota_never_applies: The model repeatedly chased network, cache, and manifest issues (Layer 1) despite user confirming downloads succeed, falling for the trap. It only briefly approached Layer 2 (activation) in turn 11 after user explicitly revealed the bundle path, but never coherently diagnosed the promote-and-relaunch ordering failure. It regressed repeatedly, re-litigating cleared issues and failing to build on user feedback, ultimately suggesting device resets instead of the correct activation logic fix.
- ota_never_applies: The model eventually reached the correct outcome in turn 9 and 11 by identifying the update state stuck in 'pending' and the failure to promote/launch the new bundle, aligning with layer 2 and 3. However, it fell for the trap early by focusing on network, caching, and server issues (layer 1) despite the user confirming downloads succeed, and repeatedly regressed to these even after user feedback, showing poor state holding and layer switching. It proposed valuable verification (logging bundle path and state), but its overall path was inefficient and regressive.
- iap_entitlement_phantom: The model correctly identified the root cause (unattached products in RevenueCat) early and consistently, never regressing or proposing the trap (app-side patch). However, it failed to converge, repeatedly re-explaining the same fix across turns without advancing, and did not hold state—re-litigating the same issue despite the user's unchanged input. It suggested testing but not via real on-device purchase as required.

## One-shot (replay pilot — 3 bugs × cold/guided)
- **Outcome reached:** 3/6 observations  ·  cold 1/3 · guided 2/3
- **Divergence mix:** {'worse': 3, 'better': 3}
- **Avg latency:** 12542.2 ms

**Reached:**
- mobile-web debugging (iOS WKWebView)
- CSS layout / aspect-ratio debugging

**One-shot failure modes:**
- mobile-web debugging (iOS WKWebView) (ios_zoom, cold): The model answer incorrectly identifies the root cause as iOS's general zoom behavior on keyboard appearance and recommends disabling user-scalable as the preferred fix, which contradicts the known-correct outcome. The correct cause is iOS auto-zooming specifically due to input font-size < 16px, and the correct fix is increasing the input's font-size to >=16px, not locking the viewport. The model's recommended solution harms accessibility by disabling pinch-zoom, which the known-correct outcome explicitly warns against.
- payments-logic / API-semantics debugging (revenuecat_permonth, cold): The model answer incorrectly assumes RevenueCat provides a correct monthly equivalent for annual plans and that leaving `pricePerMonth` as `pkg.product.priceString` is acceptable. The known-correct outcome states that `pkg.product.priceString` is the full-period price ($79.99/year), not a per-month value, so assigning it directly to `pricePerMonth` causes the bug. The fix requires computing `pricePerMonth` as `price / 12`, not reusing `priceString`. The model answer fails to identify this core issue and thus does not reach the correct outcome.
- payments-logic / API-semantics debugging (revenuecat_permonth, guided): The model incorrectly redefines the `price` field to show the per-month value for annual plans (e.g., '$6.67/mo'), but the known-correct outcome states the `price` should remain '$79.99/yr' for annual plans. The bug is in `pricePerMonth`, which should be computed as `price / 12`, not reused from `priceString`. The model misidentifies which field is broken and applies the fix to the wrong field.

## Provenance
- Long-horizon: env-driven LHCR, judge + environment floor-gated on all challenges; every cell a real frustrated-user conversation.
- One-shot: replay pilot, LLM judge anchored to the objective outcome.
- Pilot-scale, not powered. Trust resets on a model version change.