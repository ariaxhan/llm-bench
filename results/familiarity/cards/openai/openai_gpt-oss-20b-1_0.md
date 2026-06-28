# Model Card — openai.gpt-oss-20b-1:0

> Provider: **openai** · generated 2026-06-28
> One card per model, updated in place. Two sections below: one-shot (pilot) and long-horizon (env-driven conversational replay).

## Long-horizon (env-driven, frustrated-user replay)
- **Solved:** 38%  ·  **Reached root cause:** 88%  ·  **Fell for trap:** 19% (lower better)
- **Mean turns-to-fix:** 1.5  ·  **LHCR behaviour score:** 7.31/10  (n=16)
- **Behaviour dims (0–2):** convergence 1.25 · no-regression 1.81 · layer-switching 1.25 · verification-seeking 1.75 · state-holding 1.25

### Per challenge
| challenge | solved | reached | trap | lhcr |
|---|---|---|---|---|
| `camera_track_killed_by_hide` | 2/2 | 2/2 | 0/2 | 9.5 |
| `hidden_button_layers` | 0/2 | 1/2 | 1/2 | 6.5 |
| `iap_entitlement_phantom` | 0/2 | 2/2 | 0/2 | 7.0 |
| `launchd_exit126_phantom` | 0/2 | 2/2 | 0/2 | 7.5 |
| `ota_never_applies` | 1/2 | 2/2 | 0/2 | 8.0 |
| `reset_specificity_override` | 2/2 | 1/2 | 1/2 | 8.0 |
| `silent_dead_engine` | 1/2 | 2/2 | 1/2 | 8.5 |
| `wix_regen_green_tests_blind` | 0/2 | 2/2 | 0/2 | 3.5 |

### Where it struggled
- hidden_button_layers: The model correctly identified the CSS override of the `hidden` attribute by `display: inline-flex` in every response after the user provided computed style evidence, consistently guiding toward inspecting DevTools, identifying specificity issues, and applying `!important` overrides or attribute-based guards. It avoided the trap of re-editing JS, maintained prior findings, and progressively refined the solution across layers (CSS, CDN, DOM readiness), aligning fully with the known-correct outcome.
- silent_dead_engine: The model progressively narrowed the issue from general checks to the specific inter-module seam (producer 'prob' vs scorer 'probability'), consistently using live tracing and logging to verify each layer. It avoided the trap of blaming infrastructure or mocks, instead focusing on contract mismatches, and ultimately identified the silent filtering due to field name mismatch — aligning with layer 3 of the known cause. It proposed end-to-end tracing and later suggested adding liveness checks, matching the full known-correct outcome.
- hidden_button_layers: The model repeatedly re-asserted the same CSS override fix without progressing through the known layers, ignoring deploy and cache gaps. It fell for the trap by pushing JavaScript fixes and redundant CSS rules instead of identifying the real cause: CSS specificity overriding the `hidden` attribute. While it consistently urged DevTools inspection (verification_seeking=2), it failed to recognize or integrate user feedback that each attempt failed, regressing to earlier suggestions and never converging on the correct solution.
- iap_entitlement_phantom: The model consistently identified the root cause as unattached products in RevenueCat and correctly prescribed attaching them to both an offering and the 'premium_access' entitlement. It maintained focus on the configuration issue (layer 3 and 4), never regressed, rejected the app-side patch as a long-term solution, and repeatedly urged verification via live customer info checks. The solution matched the known-correct outcome in substance across all turns.

## One-shot (replay pilot — 3 bugs × cold/guided)
- **Outcome reached:** 5/6 observations  ·  cold 2/3 · guided 3/3
- **Divergence mix:** {'better': 5, 'worse': 1}
- **Avg latency:** 5430.7 ms

**Reached:**
- mobile-web debugging (iOS WKWebView)
- CSS layout / aspect-ratio debugging
- payments-logic / API-semantics debugging

**One-shot failure modes:**
- payments-logic / API-semantics debugging (revenuecat_permonth, cold): The model answer incorrectly assumes RevenueCat's product object has a pricePerMonth field that can be used directly, but the known-correct outcome states that the comment in the code is wrong — pkg.product.priceString is the full-period price and there is no indication that pricePerMonth exists in the SDK. The correct fix is to compute the monthly price by dividing the annual price by 12, not to use a non-existent or assumed field.

## Provenance
- Long-horizon: env-driven LHCR, judge + environment floor-gated on all challenges; every cell a real frustrated-user conversation.
- One-shot: replay pilot, LLM judge anchored to the objective outcome.
- Pilot-scale, not powered. Trust resets on a model version change.