# Model Card — qwen.qwen3-coder-30b-a3b-v1:0

> Provider: **qwen** · generated 2026-06-28
> One card per model, updated in place. Two sections below: one-shot (pilot) and long-horizon (env-driven conversational replay).

## Long-horizon (env-driven, frustrated-user replay)
- **Solved:** 25%  ·  **Reached root cause:** 38%  ·  **Fell for trap:** 81% (lower better)
- **Mean turns-to-fix:** 3.5  ·  **LHCR behaviour score:** 3.62/10  (n=16)
- **Behaviour dims (0–2):** convergence 0.62 · no-regression 0.81 · layer-switching 0.62 · verification-seeking 0.88 · state-holding 0.69

### Per challenge
| challenge | solved | reached | trap | lhcr |
|---|---|---|---|---|
| `camera_track_killed_by_hide` | 1/2 | 0/2 | 2/2 | 3.0 |
| `hidden_button_layers` | 1/2 | 2/2 | 1/2 | 8.0 |
| `iap_entitlement_phantom` | 0/2 | 0/2 | 2/2 | 0.0 |
| `launchd_exit126_phantom` | 0/2 | 1/2 | 2/2 | 2.5 |
| `ota_never_applies` | 0/2 | 1/2 | 2/2 | 3.5 |
| `reset_specificity_override` | 0/2 | 0/2 | 2/2 | 1.0 |
| `silent_dead_engine` | 2/2 | 2/2 | 0/2 | 10.0 |
| `wix_regen_green_tests_blind` | 0/2 | 0/2 | 2/2 | 1.0 |

### Where it struggled
- hidden_button_layers: The model eventually reached the real cause (CSS overriding `hidden`) in turn 11 by asking for computed styles, which would reveal `display: inline-flex`. It proposed live checks (computed style, element inspection) and progressed through layers (JS logic → selection → CSS → DOM timing). However, it fell for the trap early by repeatedly suggesting JS rewrites and CSS class fixes instead of immediately inspecting rendered state, and regressed by re-asking basic questions after debugging steps were confirmed failed. While it reached the correct outcome, it did so inefficiently and with redundant suggestions, making it worse than optimal.
- ota_never_applies: The model repeatedly suggested cache clearing, file path checks, and reload mechanisms, all of which align with the TRAP of focusing on download and loading mechanics despite the user confirming the download succeeds. It never identified the core issue—failure to promote the staged bundle to active and ensure the runtime picks it up on relaunch—and instead regressed to earlier suggestions, re-asking for code and reiterating file path checks even after the user confirmed attempts. It failed to advance through the known layers, staying stuck on layer 1 (network/download) and superficial aspects of layer 2, without ever diagnosing the activation state or reload ordering.
- ota_never_applies: The model eventually identified that the downloaded bundle was not being loaded (layer 2: not promoted/activated), confirmed by user logging the active bundle path. It proposed native code changes to redirect bundle loading, which touches the correct layer. However, it fell for the trap early by focusing on cache and retries, and repeatedly suggested reloads without consistently diagnosing the activation state, showing regression and poor state-holding across turns.
- reset_specificity_override: The model repeatedly proposed increasing specificity with !important and changing element types, falling directly into the trap of treating it as a values problem rather than diagnosing the cascade. It never identified the specificity conflict from the .pr-app button reset, failed to suggest inspecting computed styles or rule precedence, and regressed by suggesting increasingly invasive fixes like inline styles and div replacement after earlier attempts failed. It did not reach the correct outcome of using :where() to neutralize the reset's specificity.

## One-shot (replay pilot — 3 bugs × cold/guided)
- **Outcome reached:** 3/6 observations  ·  cold 1/3 · guided 2/3
- **Divergence mix:** {'worse': 4, 'better': 1, 'equivalent': 1}
- **Avg latency:** 10971.7 ms

**Reached:**
- mobile-web debugging (iOS WKWebView)
- CSS layout / aspect-ratio debugging

**One-shot failure modes:**
- mobile-web debugging (iOS WKWebView) (ios_zoom, cold): The model answer incorrectly identifies the root cause as iOS failing to restore zoom after keyboard dismissal, rather than correctly identifying that iOS auto-zooms on focus for inputs with font-size below 16px. It recommends the inferior viewport-lock fix (maximum-scale=1.0, user-scalable=no), which the known-correct outcome explicitly warns against due to accessibility harm. While it suggests setting font-size to 16px, it buries this within incorrect advice and promotes a harmful workaround, failing to prioritize the correct, accessibility-preserving solution.
- CSS layout / aspect-ratio debugging (cover_crop, cold): The model initially misanalyzed the cropping direction, stating the card is wider and would crop sides, but then corrected to top/bottom. Despite arriving at the correct fix (matching aspect ratios), the confusion in reasoning and incorrect intermediate logic makes the explanation less reliable than the known-correct outcome.
- payments-logic / API-semantics debugging (revenuecat_permonth, cold): The model answer incorrectly assumes that pkg.product.priceString includes the period (like '/yr') and focuses on parsing or replacing it, but the known-correct outcome states that priceString is just the full-period price amount (e.g., $79.99) without any '/yr' suffix. The model overcomplicates the fix with string parsing and multiple options, while the correct fix is simply to divide the annual price by 12 to compute pricePerMonth, not reuse priceString directly.
- payments-logic / API-semantics debugging (revenuecat_permonth, guided): The model incorrectly assumes RevenueCat provides a pricePerMonth field. The known-correct outcome states that pkg.product.priceString is the full-period price and must be divided by 12 for annual plans to get the monthly equivalent. The model's proposed fix relies on a non-existent or unverified pricePerMonth field, which does not align with the actual solution of computing price / 12.

## Provenance
- Long-horizon: env-driven LHCR, judge + environment floor-gated on all challenges; every cell a real frustrated-user conversation.
- One-shot: replay pilot, LLM judge anchored to the objective outcome.
- Pilot-scale, not powered. Trust resets on a model version change.