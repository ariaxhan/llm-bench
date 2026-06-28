# Model Card — nvidia.nemotron-super-3-120b

> Provider: **nvidia** · generated 2026-06-28
> One card per model, updated in place. Two sections below: one-shot (pilot) and long-horizon (env-driven conversational replay).

## Long-horizon (env-driven, frustrated-user replay)
- **Solved:** 69%  ·  **Reached root cause:** 81%  ·  **Fell for trap:** 12% (lower better)
- **Mean turns-to-fix:** 1.91  ·  **LHCR behaviour score:** 8.62/10  (n=16)
- **Behaviour dims (0–2):** convergence 1.69 · no-regression 1.88 · layer-switching 1.62 · verification-seeking 1.56 · state-holding 1.88

### Per challenge
| challenge | solved | reached | trap | lhcr |
|---|---|---|---|---|
| `camera_track_killed_by_hide` | 2/2 | 2/2 | 0/2 | 9.0 |
| `hidden_button_layers` | 2/2 | 1/2 | 1/2 | 8.0 |
| `iap_entitlement_phantom` | 0/2 | 2/2 | 0/2 | 9.5 |
| `launchd_exit126_phantom` | 1/2 | 1/2 | 0/2 | 5.5 |
| `ota_never_applies` | 2/2 | 2/2 | 0/2 | 10.0 |
| `reset_specificity_override` | 2/2 | 2/2 | 0/2 | 10.0 |
| `silent_dead_engine` | 2/2 | 2/2 | 0/2 | 10.0 |
| `wix_regen_green_tests_blind` | 0/2 | 1/2 | 1/2 | 7.0 |

### Where it struggled
- iap_entitlement_phantom: The model correctly identified the root cause as a configuration issue (Layer 2: contradiction) and consistently progressed to Layer 4: attaching products to entitlement and offering in RevenueCat. It rejected the trap of using the app-side patch and emphasized fixing the dashboard. Each response built on prior turns, avoided repetition, and included specific verification steps like clearing app data and logging entitlements. The full correct outcome was articulated across turns, aligning with the known truth.
- wix_regen_green_tests_blind: The model initially recognized the scraper returns empty data due to JavaScript rendering (touching layer 3), but then fell into the trap by generating plausible content in turn 1 without verifying against the live site. It repeatedly demanded the scrape output but never proposed headless rendering to capture the real DOM (layer 4), nor suggested visual comparison for verification. Instead, it fixated on obtaining the same broken scrape data, failing to advance beyond layer 1 and 2, and ultimately regressing into a communication deadlock while trusting invented data as valid fallback.
- iap_entitlement_phantom: The model correctly identified the root cause as a configuration issue in RevenueCat (Layer 2: register contradiction, Layer 3: read docs, Layer 4: attach products to entitlement and offering) and consistently guided the user to fix the attachment in the dashboard across all turns. It never regressed, avoided the trap of endorsing the app-side patch, and built on prior turns by reinforcing the same correct path. However, it only vaguely suggested testing via restore purchases rather than mandating a real on-device sandbox purchase to verify entitlement grant (missing Layer 5 verification), so verification_seeking is 1.
- launchd_exit126_phantom: The model never identified the true root cause: the inner target './venv/bin/python' lacks execute permission or fails due to launchd's minimal environment. Instead, it cycled through layers 1, 2, and 5 repeatedly—blaming the wrapper script's execution, environment, BOM, mounts, dyld—without ever isolating the shared inner executable as the single point of failure. It proposed logging and verification but failed to maintain state or progress toward the known-correct outcome.

## One-shot (replay pilot — 3 bugs × cold/guided)
- **Outcome reached:** 4/6 observations  ·  cold 3/3 · guided 1/3
- **Divergence mix:** {'better': 4, 'worse': 2}
- **Avg latency:** 25032.7 ms

**Reached:**
- mobile-web debugging (iOS WKWebView)
- CSS layout / aspect-ratio debugging
- payments-logic / API-semantics debugging

**One-shot failure modes:**
- CSS layout / aspect-ratio debugging (cover_crop, guided): The model incorrectly identifies 'object-fit: contain' as the fix, but the known-correct outcome states the root issue is the aspect-ratio mismatch and the correct fix is to change the container's aspect-ratio to 9/16 to match the image. Using 'contain' would preserve the entire image but within the wrong container shape, potentially introducing unwanted letterboxing, rather than aligning the container with the image's natural aspect ratio as intended.
- payments-logic / API-semantics debugging (revenuecat_permonth, guided): The model incorrectly concludes the bug is in the UI, not the mapping code, and recommends keeping the flawed `pricePerMonth: pkg.product.priceString` assignment. The known-correct outcome states the bug is exactly there — `priceString` is the full-period price, so assigning it directly to `pricePerMonth` is wrong. The fix must compute `pricePerMonth` as `price / 12` for annual plans, not rely on the UI to correct a semantically broken field.

## Provenance
- Long-horizon: env-driven LHCR, judge + environment floor-gated on all challenges; every cell a real frustrated-user conversation.
- One-shot: replay pilot, LLM judge anchored to the objective outcome.
- Pilot-scale, not powered. Trust resets on a model version change.