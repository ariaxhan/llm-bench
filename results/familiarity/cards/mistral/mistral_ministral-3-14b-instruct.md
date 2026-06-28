# Model Card — mistral.ministral-3-14b-instruct

> Provider: **mistral** · generated 2026-06-28
> One card per model, updated in place. Two sections below: one-shot (pilot) and long-horizon (env-driven conversational replay).

## Long-horizon (env-driven, frustrated-user replay)
- **Solved:** 12%  ·  **Reached root cause:** 38%  ·  **Fell for trap:** 81% (lower better)
- **Mean turns-to-fix:** 2.5  ·  **LHCR behaviour score:** 3.12/10  (n=16)
- **Behaviour dims (0–2):** convergence 0.5 · no-regression 0.62 · layer-switching 0.62 · verification-seeking 0.81 · state-holding 0.56

### Per challenge
| challenge | solved | reached | trap | lhcr |
|---|---|---|---|---|
| `camera_track_killed_by_hide` | 0/2 | 0/2 | 2/2 | 0.0 |
| `hidden_button_layers` | 0/2 | 1/2 | 2/2 | 3.0 |
| `iap_entitlement_phantom` | 0/2 | 1/2 | 2/2 | 2.5 |
| `launchd_exit126_phantom` | 0/2 | 1/2 | 1/2 | 6.5 |
| `ota_never_applies` | 1/2 | 1/2 | 2/2 | 2.5 |
| `reset_specificity_override` | 0/2 | 0/2 | 2/2 | 1.0 |
| `silent_dead_engine` | 1/2 | 2/2 | 0/2 | 9.5 |
| `wix_regen_green_tests_blind` | 0/2 | 0/2 | 2/2 | 0.0 |

### Where it struggled
- hidden_button_layers: The model repeatedly proposed JavaScript-based fixes (e.g., MutationObserver, style overrides, nuclear JS) despite user feedback that they failed, indicating it never correctly identified the real cause: CSS specificity overriding the `hidden` attribute. It fell for the trap by re-asserting JS-centric solutions even after the user revealed the deploy gap, and it failed to switch layers meaningfully or retain prior refutations. While it occasionally suggested DevTools inspection (verification_seeking), it did not focus on computed styles or CSS precedence, and it regressed by re-litigating earlier abandoned approaches.
- hidden_button_layers: The model eventually identified the deploy gap after the user revealed it, and suggested inspecting live state via DevTools, but spent multiple turns pushing JS-centric fixes (the trap) like re-asserting hidden in JS or MutationObserver, which ignored the real CSS specificity issue. It failed to diagnose the CSS layer override early, despite the user repeatedly ruling out each proposed fix, and did not coherently chain the known layers (deploy, cache, CSS, cleanup) until the final turn when the user disclosed the deploy gap.
- ota_never_applies: The model repeatedly chased caching, reload calls, and Hermes issues—layers unrelated to the true root cause. It fell for the trap by focusing on network/cache headers and retry logic early on, and never correctly identified that the downloaded bundle fails to be promoted to active or that the runtime relaunches the old bundle. It ignored the known-correct outcome entirely, reasserting the same fixes across turns without progressing through the known layers or verifying runtime bundle state.
- reset_specificity_override: The model repeatedly proposed increasing padding values and using !important, which is the seductive trap of treating it as a values/specificity war rather than a reset design flaw. It never identified the :where() solution or diagnosed that the button reset's specificity (0,1,1) beats the row class (0,1,0). It regressed by abandoning correct debugging steps like inspecting computed styles and instead escalated to nuclear !important and JavaScript overrides, failing to build on prior turns or recognize that source values were present but overridden by cascade order.

## One-shot (replay pilot — 3 bugs × cold/guided)
- **Outcome reached:** 2/6 observations  ·  cold 1/3 · guided 1/3
- **Divergence mix:** {'worse': 5, 'better': 1}
- **Avg latency:** 2465.3 ms

**Reached:**
- CSS layout / aspect-ratio debugging

**One-shot failure modes:**
- mobile-web debugging (iOS WKWebView) (ios_zoom, cold): The model answer incorrectly recommends using `maximum-scale=1.0` and `user-scalable=no` as part of the primary solution, which contradicts the known-correct outcome that identifies this as an inferior fix that harms accessibility. While it does suggest setting the font size to 16px, it undermines the correct approach by promoting viewport locking, and adds unnecessary JavaScript and styling that are not required. The root cause is identified partially, but the recommended solution prioritizes the wrong fix.
- mobile-web debugging (iOS WKWebView) (ios_zoom, guided): The model answer incorrectly identifies the root cause and recommends disabling user scaling and using text-size-adjust, which contradicts the known-correct outcome that the issue is due to font size <16px triggering iOS auto-zoom. The correct fix is increasing font-size to >=16px, but the model instead suggests viewport and JavaScript workarounds that harm accessibility, failing to address the actual cause.
- CSS layout / aspect-ratio debugging (cover_crop, guided): The model eventually identifies the correct fix—changing the aspect ratio to 9/16—but initially confuses the aspect ratio direction multiple times, incorrectly suggesting 16/9 and providing misleading explanations about container dimensions. This creates confusion and reduces clarity, despite arriving at the right outcome.
- payments-logic / API-semantics debugging (revenuecat_permonth, cold): The model incorrectly assumes the issue is duplicate period suffixes (e.g., '/yr/yr') and that priceString already includes the correct period, but the known-correct outcome states that priceString is the full-period price without per-month conversion. The model preserves the incorrect assignment of priceString to pricePerMonth, failing to fix the core bug: annual price must be divided by 12 to compute per-month value.
- payments-logic / API-semantics debugging (revenuecat_permonth, guided): The model answer incorrectly suggests using `pricePerMonth` from RevenueCat for the `price` field in annual plans, but the known-correct outcome states that `pkg.product.priceString` is the full-period price and `pricePerMonth` should be computed as `price / 12`. The model assumes RevenueCat provides a correct `pricePerMonth`, but the bug is that it does not — the fix requires manual calculation, not using RevenueCat's field.

## Provenance
- Long-horizon: env-driven LHCR, judge + environment floor-gated on all challenges; every cell a real frustrated-user conversation.
- One-shot: replay pilot, LLM judge anchored to the objective outcome.
- Pilot-scale, not powered. Trust resets on a model version change.