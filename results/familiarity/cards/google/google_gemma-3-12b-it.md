# Model Card — google.gemma-3-12b-it

> Provider: **google** · generated 2026-06-28
> One card per model, updated in place. Two sections below: one-shot (pilot) and long-horizon (env-driven conversational replay).

## Long-horizon (env-driven, frustrated-user replay)
- **Solved:** 25%  ·  **Reached root cause:** 19%  ·  **Fell for trap:** 81% (lower better)
- **Mean turns-to-fix:** 2.25  ·  **LHCR behaviour score:** 2.75/10  (n=16)
- **Behaviour dims (0–2):** convergence 0.44 · no-regression 0.62 · layer-switching 0.44 · verification-seeking 0.62 · state-holding 0.62

### Per challenge
| challenge | solved | reached | trap | lhcr |
|---|---|---|---|---|
| `camera_track_killed_by_hide` | 0/2 | 0/2 | 2/2 | 0.0 |
| `hidden_button_layers` | 1/2 | 1/2 | 1/2 | 5.0 |
| `iap_entitlement_phantom` | 0/2 | 0/2 | 2/2 | 0.0 |
| `launchd_exit126_phantom` | 0/2 | 0/2 | 2/2 | 0.0 |
| `ota_never_applies` | 0/2 | 0/2 | 2/2 | 0.0 |
| `reset_specificity_override` | 2/2 | 0/2 | 2/2 | 8.0 |
| `silent_dead_engine` | 1/2 | 2/2 | 0/2 | 9.0 |
| `wix_regen_green_tests_blind` | 0/2 | 0/2 | 2/2 | 0.0 |

### Where it struggled
- hidden_button_layers: The model repeatedly focused on JavaScript execution, caching, and deployment issues (layers 1 and 2) while completely missing the real cause: CSS specificity overriding the `hidden` attribute (layer 3). It fell for the trap by insisting on re-editing and re-verifying the JS logic across all turns, even proposing increasingly extreme debugging steps, without ever inspecting computed styles or suggesting a CSS fix. It failed to switch layers meaningfully, re-litigated basic steps, and never held state across user rejections.
- ota_never_applies: The model repeatedly focused on network, caching, and manifest issues (Layer 1) despite the user confirming downloads succeed with 200s and checksums match, falling directly into THE TRAP. It never addressed Layer 2 (staged but not activated) or Layer 3 (reload vs. activation order), instead regressing to increasingly speculative and irrelevant suggestions like native module interference and device corruption. It failed to propose checking which bundle actually runs at launch or the activation state, and ignored all user-confirmed exclusions, showing no state holding or layer progression.
- ota_never_applies: The model repeatedly chased network, caching, and manifest issues (Layer 1: network/download) despite the user confirming downloads succeed with 200s, thus falling for THE TRAP. It never addressed Layer 2 (staged update not promoted) or Layer 3 (activation+reload ordering), instead regressing to generic debugging, ignoring ruled-out causes, and failing to propose checking which bundle actually runs at launch. The correct root cause — promotion and relaunch logic — was never articulated.
- silent_dead_engine: The model correctly identified the need to trace a real tick (layer 2) and verified the producer-scoring seam failure, but fixated on Kafka partitioning (a specific mechanism) rather than the general contract/shape mismatch (layer 3). It reached the outcome's core—silent failure at a seam—via user-guided tracing but failed to generalize to the root cause of untested interfaces or propose liveness checks, offering infrastructure-specific fixes instead.

## One-shot (replay pilot — 3 bugs × cold/guided)
- **Outcome reached:** 2/6 observations  ·  cold 1/3 · guided 1/3
- **Divergence mix:** {'worse': 4, 'better': 2}
- **Avg latency:** 11457.9 ms

**Reached:**
- CSS layout / aspect-ratio debugging

**One-shot failure modes:**
- mobile-web debugging (iOS WKWebView) (ios_zoom, cold): The model answer incorrectly identifies the root cause as a general WKWebView zoom behavior without pinpointing the specific iOS rule that triggers zoom on inputs with font-size < 16px. It then recommends suboptimal fixes like CSS transform or JavaScript zoom manipulation, while the correct fix—setting input font-size to >=16px—is not mentioned. It wrongly treats viewport locking (maximum-scale=1.0) as a viable alternative, despite the known-correct outcome explicitly stating it is inferior and harms accessibility.
- mobile-web debugging (iOS WKWebView) (ios_zoom, guided): The model incorrectly identifies the root cause as WKWebView's general focus behavior rather than the specific iOS rule that inputs with font-size below 16px trigger auto-zoom. It recommends setting viewport maximum-scale=1.0 as the most reliable fix, which contradicts the known-correct outcome that this approach harms accessibility by disabling pinch-zoom. The correct fix—setting input font-size to >=16px—is not mentioned.
- payments-logic / API-semantics debugging (revenuecat_permonth, cold): The model misidentifies the bug as an issue with RevenueCat's `priceString` including '/mo' and suggests parsing a raw `price` field and using a `period` enum, but the known-correct outcome states the real bug is using `priceString` directly for `pricePerMonth` without dividing the annual price by 12. The correct fix is computing monthly price as `price / 12`, not reconstructing strings from raw values that aren't even mentioned in the original code.
- payments-logic / API-semantics debugging (revenuecat_permonth, guided): The model misidentifies the bug as a string formatting issue and proposes parsing the priceString, when the actual bug is using the full annual priceString directly for pricePerMonth. The known-correct outcome requires computing pricePerMonth as price / 12, but the model incorrectly retains pkg.product.priceString for pricePerMonth, leaving the core bug unaddressed.

## Provenance
- Long-horizon: env-driven LHCR, judge + environment floor-gated on all challenges; every cell a real frustrated-user conversation.
- One-shot: replay pilot, LLM judge anchored to the objective outcome.
- Pilot-scale, not powered. Trust resets on a model version change.