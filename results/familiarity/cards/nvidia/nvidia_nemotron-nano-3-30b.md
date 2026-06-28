# Model Card — nvidia.nemotron-nano-3-30b

> Provider: **nvidia** · generated 2026-06-28
> One card per model, updated in place. Two sections below: one-shot (pilot) and long-horizon (env-driven conversational replay).

## Long-horizon (env-driven, frustrated-user replay)
- **Solved:** 19%  ·  **Reached root cause:** 38%  ·  **Fell for trap:** 56% (lower better)
- **Mean turns-to-fix:** 4.0  ·  **LHCR behaviour score:** 4.75/10  (n=16)
- **Behaviour dims (0–2):** convergence 0.62 · no-regression 1.81 · layer-switching 0.62 · verification-seeking 1.06 · state-holding 0.62

### Per challenge
| challenge | solved | reached | trap | lhcr |
|---|---|---|---|---|
| `camera_track_killed_by_hide` | 0/2 | 0/2 | 2/2 | 2.0 |
| `hidden_button_layers` | 0/2 | 0/2 | 2/2 | 3.0 |
| `iap_entitlement_phantom` | 0/2 | 2/2 | 1/2 | 9.5 |
| `launchd_exit126_phantom` | 0/2 | 1/2 | 0/2 | 6.0 |
| `ota_never_applies` | 0/2 | 0/2 | 2/2 | 2.0 |
| `reset_specificity_override` | 1/2 | 0/2 | 2/2 | 2.5 |
| `silent_dead_engine` | 1/2 | 1/2 | 0/2 | 6.5 |
| `wix_regen_green_tests_blind` | 1/2 | 2/2 | 0/2 | 6.5 |

### Where it struggled
- ota_never_applies: The model repeatedly asked for logs and code without advancing the diagnosis, stuck on layer 1 (network/version/hash) despite the user confirming downloads succeed. It fell for the trap by focusing on hash mismatches, cache-busting, and version checks — all network/download-layer issues — while never reaching the true root cause: the downloaded bundle is not promoted to active or reloaded. It forgot prior confirmations of successful download and regressed to basic checks, never proposing to verify which bundle path actually runs at launch.
- hidden_button_layers: The model repeatedly re-asserted the same JS-centric fixes (JSX hidden prop, re-renders) across all turns, failing to switch layers despite user rejection, thus never addressing the real CSS specificity issue. It fell for the trap by insisting on re-editing the JS, which was already correct, and never correctly identified or prioritized the computed style override by CSS. While it consistently avoided contradicting itself (no_regression=2), it did not progress toward the known root cause and re-litigated the same points, ignoring deployed state and cache implications after initial mentions.
- hidden_button_layers: The model repeatedly re-asserted the same JS fix (adding `hidden={configType !== 'event'}`) across all turns, falling directly into THE TRAP by focusing exclusively on JavaScript logic despite user feedback that it had no effect. It never progressed beyond layer 1 (JS rendering) to consider CSS specificity, cache, or deploy gaps, and failed to adapt when the fix was rejected. While it consistently suggested checking the DOM and network (verification_seeking), it did not switch layers or incorporate user feedback, regressing to the same solution each time and failing to reach the known-correct outcome.
- ota_never_applies: The model repeatedly chased network, caching, and manifest issues (Layer 1: network/download) despite the user confirming 200s and successful download, falling for the trap. It never addressed Layer 2 (staged but not promoted) or Layer 3 (activation+reload ordering), instead reiterating the same reload-and-persist advice. It proposed logging and checks but failed to shift focus to runtime bundle activation state, and regressed by re-asking to verify manifest MIME types after the user confirmed download success. The correct root cause — that the new bundle is staged but never marked active or properly relaunched — was never articulated.

## One-shot (replay pilot — 3 bugs × cold/guided)
- **Outcome reached:** 4/6 observations  ·  cold 1/3 · guided 3/3
- **Divergence mix:** {'worse': 2, 'better': 4}
- **Avg latency:** 5465.2 ms

**Reached:**
- mobile-web debugging (iOS WKWebView)
- CSS layout / aspect-ratio debugging
- payments-logic / API-semantics debugging

**One-shot failure modes:**
- mobile-web debugging (iOS WKWebView) (ios_zoom, cold): The model answer incorrectly identifies the root cause and proposes suboptimal or incorrect fixes. It suggests workarounds like changing input type to 'search', using JavaScript to scroll, or temporarily increasing font size on focus, but misses the known-correct solution: setting the input's font-size to ≥16px permanently in CSS. It also incorrectly implies that viewport locking is the only way to prevent zoom, while the correct fix is adjusting font size, preserving accessibility. The model overcomplicates the solution and fails to identify the actual root cause: iOS auto-zooming on inputs with computed font size below 16px.
- payments-logic / API-semantics debugging (revenuecat_permonth, cold): The model answer incorrectly identifies the bug as appending '/yr' or '/mo' to priceString, when the real issue is that pricePerMonth is set to priceString (the full annual price) instead of the computed per-month value. The known-correct outcome states that pkg.product.priceString is the total period price (e.g. $79.99/year), not a per-month amount, and the fix is to compute price/12 for annual plans. The model suggests multiple options but misdiagnoses the core issue, leading to unnecessary complexity and incorrect solutions like relying on a non-existent pricePerMonth field in RevenueCat's product object.

## Provenance
- Long-horizon: env-driven LHCR, judge + environment floor-gated on all challenges; every cell a real frustrated-user conversation.
- One-shot: replay pilot, LLM judge anchored to the objective outcome.
- Pilot-scale, not powered. Trust resets on a model version change.