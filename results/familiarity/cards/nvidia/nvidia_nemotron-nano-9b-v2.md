# Model Card — nvidia.nemotron-nano-9b-v2

> Provider: **nvidia** · generated 2026-06-28
> One card per model, updated in place. Two sections below: one-shot (pilot) and long-horizon (env-driven conversational replay).

## Long-horizon (env-driven, frustrated-user replay)
- **Solved:** 44%  ·  **Reached root cause:** 69%  ·  **Fell for trap:** 38% (lower better)
- **Mean turns-to-fix:** 2.43  ·  **LHCR behaviour score:** 5.38/10  (n=16)
- **Behaviour dims (0–2):** convergence 1.06 · no-regression 1.25 · layer-switching 1.06 · verification-seeking 0.94 · state-holding 1.06

### Per challenge
| challenge | solved | reached | trap | lhcr |
|---|---|---|---|---|
| `camera_track_killed_by_hide` | 1/2 | 0/2 | 2/2 | 0.0 |
| `hidden_button_layers` | 0/2 | 1/2 | 1/2 | 5.0 |
| `iap_entitlement_phantom` | 0/2 | 2/2 | 0/2 | 8.0 |
| `launchd_exit126_phantom` | 0/2 | 1/2 | 2/2 | 0.0 |
| `ota_never_applies` | 2/2 | 2/2 | 0/2 | 8.0 |
| `reset_specificity_override` | 2/2 | 2/2 | 0/2 | 9.0 |
| `silent_dead_engine` | 2/2 | 2/2 | 0/2 | 10.0 |
| `wix_regen_green_tests_blind` | 0/2 | 1/2 | 1/2 | 3.0 |

### Where it struggled
- hidden_button_layers: The model fixated exclusively on the deploy gap (layer 1) and cache-buster (layer 2), repeatedly regressing to push instructions despite the user re-stating the same fact. It never advanced to the real cause—CSS overriding `hidden` (layer 3)—and instead proposed re-editing the JS logic, falling directly into THE TRAP. It failed to suggest inspecting computed styles or CSS specificity, and showed no state holding by re-litigating the same deploy issue across all turns.
- hidden_button_layers: The model progressively diagnosed each layer: first the unpushed commit (deploy gap), then the stale cache due to unchanged cache-buster (cache gap), and finally the CSS specificity issue where `display: inline-flex` overrides `[hidden]`—the real cause. It consistently built on prior findings, never regressed, and correctly identified the need to inspect computed styles. It avoided the trap of re-editing JS and reached the known-correct outcome by diagnosing all four layers, including the critical CSS fix with `!important` or specificity adjustment.
- iap_entitlement_phantom: The model consistently identified the root cause as unattached products in RevenueCat (Layer 3) and correctly prescribed attaching them to the entitlement and offering (Layer 4). It never regressed, avoided the trap of endorsing the app-side patch, and progressively refined instructions with verification steps like testing with a new user and checking logs. By turn 3, it had articulated the full correct fix and built on prior turns with deeper configuration details, demonstrating full state holding and convergence on the known-correct outcome.
- iap_entitlement_phantom: The model correctly identified the root cause (unattached products in RevenueCat) and never suggested the trap (app-side loose unlock). It consistently focused on attaching products to the entitlement, which aligns with layer 4. However, it failed to mention attaching products to an offering or the App Store Connect configuration, and did not propose verification via a real on-device sandbox purchase as required. It repeated the same advice across turns without advancing to deeper layers or incorporating all elements of the known-correct outcome.

## One-shot (replay pilot — 3 bugs × cold/guided)
- **Outcome reached:** 3/6 observations  ·  cold 2/3 · guided 1/3
- **Divergence mix:** {'equivalent': 2, 'worse': 3, 'better': 1}
- **Avg latency:** 20318.9 ms

**Reached:**
- mobile-web debugging (iOS WKWebView)
- CSS layout / aspect-ratio debugging

**One-shot failure modes:**
- mobile-web debugging (iOS WKWebView) (ios_zoom, guided): The model answer incorrectly identifies the root cause as potential JavaScript interference or layout shifts, while missing the known-correct cause: iOS auto-zooms on inputs with font-size below 16px. It suggests stabilizing layout and checking JavaScript, but fails to recommend the correct fix—setting the input font-size to >=16px. It also discusses accessibility tradeoffs correctly but in the context of the wrong solution, making the response incomplete and misleading.
- payments-logic / API-semantics debugging (revenuecat_permonth, cold): The model answer incorrectly focuses on the 'annual' flag being misset or the priceString suffix logic, completely missing the core issue: pkg.product.priceString is the full annual price ($79.99), not a per-month value, so assigning it directly to pricePerMonth is wrong. The known-correct outcome requires computing pricePerMonth as price / 12, which the model never identifies.
- payments-logic / API-semantics debugging (revenuecat_permonth, guided): The model answer incorrectly identifies the bug as a misapplied 'annual' flag or suffix logic, when the known-correct outcome states the bug is in assigning the full-period priceString to pricePerMonth, causing $79.99/mo to display for an annual plan. The real fix is to compute pricePerMonth as price / 12, not reuse priceString. The model's proposed fix does not address this core issue and instead focuses on the display suffix, which is not the problem.

## Provenance
- Long-horizon: env-driven LHCR, judge + environment floor-gated on all challenges; every cell a real frustrated-user conversation.
- One-shot: replay pilot, LLM judge anchored to the objective outcome.
- Pilot-scale, not powered. Trust resets on a model version change.