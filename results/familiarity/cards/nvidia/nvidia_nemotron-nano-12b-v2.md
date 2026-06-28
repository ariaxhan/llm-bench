# Model Card — nvidia.nemotron-nano-12b-v2

> Provider: **nvidia** · generated 2026-06-28
> One card per model, updated in place. Two sections below: one-shot (pilot) and long-horizon (env-driven conversational replay).

## Long-horizon (env-driven, frustrated-user replay)
- **Solved:** 0%  ·  **Reached root cause:** 12%  ·  **Fell for trap:** 75% (lower better)
- **Mean turns-to-fix:** — (never solved)  ·  **LHCR behaviour score:** 2.44/10  (n=16)
- **Behaviour dims (0–2):** convergence 0.19 · no-regression 1.25 · layer-switching 0.19 · verification-seeking 0.62 · state-holding 0.19

### Per challenge
| challenge | solved | reached | trap | lhcr |
|---|---|---|---|---|
| `camera_track_killed_by_hide` | 0/2 | 0/2 | 2/2 | 2.0 |
| `hidden_button_layers` | 0/2 | 1/2 | 1/2 | 5.0 |
| `iap_entitlement_phantom` | 0/2 | 0/2 | 1/2 | 3.0 |
| `launchd_exit126_phantom` | 0/2 | 0/2 | 1/2 | 1.0 |
| `ota_never_applies` | 0/2 | 0/2 | 2/2 | 1.5 |
| `reset_specificity_override` | 0/2 | 0/2 | 2/2 | 1.0 |
| `silent_dead_engine` | 0/2 | 1/2 | 1/2 | 4.0 |
| `wix_regen_green_tests_blind` | 0/2 | 0/2 | 2/2 | 2.0 |

### Where it struggled
- hidden_button_layers: The model progressively diagnosed each layer: first the unpushed commit (deploy gap), then the stale cache-buster (cache gap), and finally the CSS override of the `hidden` attribute (real cause), confirming via computed styles. It consistently built on prior findings, never regressed, and avoided the trap of re-editing JS. The fix proposed—using `!important` or specific CSS—matches the known-correct outcome.
- ota_never_applies: The model repeatedly focused on network, caching, and server-side issues despite the user confirming downloads succeed with 200s, falling for the trap of treating it as a download problem. It never addressed the activation or bundle promotion layer, instead recycling the same suggestions across turns without progressing toward the known root cause: the downloaded bundle is not being marked active or relaunched.
- hidden_button_layers: The model repeatedly reasserted JS-level fixes (e.g., re-checking the `hidden` attribute setting, debugging JS execution) despite user signals that the deploy and cache layers were addressed, failing to progress to the real CSS specificity issue. It fell for the trap by focusing exclusively on the JS logic and never correctly identified or addressed the CSS rule overriding `[hidden]`, nor did it propose inspecting computed styles. The model ignored or forgot prior user confirmations (e.g., fix pushed, cache-buster updated) and regressed to earlier debugging steps, showing no state holding or layer switching.
- ota_never_applies: The model repeatedly focused on network caching, manifest URLs, server headers, and file paths—chasing Layer 1 (network/download) despite user confirming 200s and successful download. It never advanced to Layer 2 (activation/promotion) or Layer 3 (reload ordering). Even after the user explicitly stated the downloaded bundle sits unused and the old one runs, the model reasserted manifest checks and cache busting. It fell for THE TRAP by pushing query params and cache headers, and regressed by re-litigating initial steps across turns, showing no state holding or layer switching.

## One-shot (replay pilot — 3 bugs × cold/guided)
- **Outcome reached:** 2/6 observations  ·  cold 1/3 · guided 1/3
- **Divergence mix:** {'worse': 4, 'better': 2}
- **Avg latency:** 2837.2 ms

**Reached:**
- CSS layout / aspect-ratio debugging

**One-shot failure modes:**
- mobile-web debugging (iOS WKWebView) (ios_zoom, cold): The model incorrectly identifies the root cause as a combination of viewport settings and font inheritance, and recommends the inferior 'user-scalable=no' fix despite acknowledging its accessibility downsides. The known-correct outcome states that iOS auto-zooms specifically when input font size is under 16px, and the correct fix is setting font-size >=16px—without needing viewport locks. The model mentions setting font-size: 16px but pairs it with the harmful viewport change, failing to identify that the font size alone is the proper solution.
- mobile-web debugging (iOS WKWebView) (ios_zoom, guided): The model incorrectly identifies the root cause as the combination of `initial-scale=1.0` and font inheritance, and recommends removing `initial-scale=1.0`, which is not the issue. The known-correct outcome states the real cause is iOS auto-zooming on inputs with font size under 16px, and the correct fix is setting input font-size ≥16px. The model's suggestion to remove `initial-scale` misunderstands iOS viewport behavior and could lead to unintended layout consequences, while its proposed fix does not address the core issue of sub-16px font triggering zoom.
- payments-logic / API-semantics debugging (revenuecat_permonth, cold): The model incorrectly assumes that pkg.product.priceString represents a monthly price and that the bug is in the 'price' field formatting. However, the known-correct outcome states that priceString is the full-period price (e.g., $79.99/year for annual), and the real bug is assigning this full-period price to 'pricePerMonth' without dividing by 12. The model's fix incorrectly multiplies the monthly rate by 12, which is the reverse of the correct logic and would produce wrong annual totals.
- payments-logic / API-semantics debugging (revenuecat_permonth, guided): The model answer incorrectly assumes RevenueCat's priceString for annual plans is already a per-month value (e.g., $6.67/mo), but the known-correct outcome states that priceString is the full-period price ($79.99/year). The model's fix retains priceString unmodified, which perpetuates the bug by showing $79.99/mo instead of computing $6.67/mo. The correct fix requires dividing the annual price by 12, which the model answer does not do.

## Provenance
- Long-horizon: env-driven LHCR, judge + environment floor-gated on all challenges; every cell a real frustrated-user conversation.
- One-shot: replay pilot, LLM judge anchored to the objective outcome.
- Pilot-scale, not powered. Trust resets on a model version change.