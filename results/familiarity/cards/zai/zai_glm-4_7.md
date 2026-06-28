# Model Card — zai.glm-4.7

> Provider: **zai** · generated 2026-06-28
> One card per model, updated in place. Two sections below: one-shot (pilot) and long-horizon (env-driven conversational replay).

## Long-horizon (env-driven, frustrated-user replay)
- **Solved:** 56%  ·  **Reached root cause:** 62%  ·  **Fell for trap:** 38% (lower better)
- **Mean turns-to-fix:** 3.33  ·  **LHCR behaviour score:** 6.12/10  (n=16)
- **Behaviour dims (0–2):** convergence 1.25 · no-regression 1.31 · layer-switching 1.19 · verification-seeking 1.19 · state-holding 1.19

### Per challenge
| challenge | solved | reached | trap | lhcr |
|---|---|---|---|---|
| `camera_track_killed_by_hide` | 2/2 | 2/2 | 1/2 | 7.0 |
| `hidden_button_layers` | 1/2 | 1/2 | 1/2 | 6.0 |
| `iap_entitlement_phantom` | 1/2 | 2/2 | 0/2 | 6.5 |
| `launchd_exit126_phantom` | 0/2 | 0/2 | 1/2 | 0.5 |
| `ota_never_applies` | 1/2 | 2/2 | 0/2 | 10.0 |
| `reset_specificity_override` | 2/2 | 1/2 | 1/2 | 9.0 |
| `silent_dead_engine` | 2/2 | 2/2 | 0/2 | 10.0 |
| `wix_regen_green_tests_blind` | 0/2 | 0/2 | 2/2 | 0.0 |

### Where it struggled
- hidden_button_layers: The model repeatedly proposed JS-centric fixes like adding classes, using !important, or removing the element via JavaScript—falling directly into THE TRAP of re-editing JS despite the real cause being CSS specificity overriding the `hidden` attribute. It never identified the core issue (CSS `display: inline-flex` beating `[hidden]`) or the deploy/cache layers, instead escalating to increasingly extreme and incorrect theories like Shadow DOM and overlays. Although it suggested inspecting computed styles indirectly via DevTools, it failed to connect this to the actual root cause and regressed by re-litigating basic targeting long after user feedback ruled out simple mis-targeting.
- ota_never_applies: The model correctly moved from network (ruled out) to activation (pending vs launched) to relaunch ordering, consistently building on prior turns. It identified the need to mark the update as active via native storage (SharedPreferences/NSUserDefaults) and trigger reload, matching the known root cause. It proposed concrete runtime verification (native logs, file checks) and never regressed or fell for the network trap.
- iap_entitlement_phantom: The model correctly identified the root cause (unattached products in RevenueCat) and never regressed, but failed to progress beyond Layer 3 despite repeated user re-statements of the same problem. It never advanced to Layer 4 (attaching to offering/version) or Layer 5 (verification via real purchase), and did not adapt its response or seek runtime verification, instead repeating the same instructions across turns.
- launchd_exit126_phantom: The model initially identified the inner command as the source of the 126 but immediately regressed to chmod +x on the venv binaries, which is a variant of the trap. It then repeatedly fixated on external factors (architecture, quarantine, network mounts) without ever correctly isolating the minimal root cause: the shared inner target's execute bit or invocation method. It ignored the fact that the wrapper is already executable and failed to propose verifying or fixing the single shared dependency via absolute path or proper chmod on the interpreter itself. The model abandoned its early correct direction and never returned to the core issue revealed by the stderr log.

## One-shot (replay pilot — 3 bugs × cold/guided)
- **Outcome reached:** 3/6 observations  ·  cold 2/3 · guided 1/3
- **Divergence mix:** {'better': 3, 'worse': 3}
- **Avg latency:** 3813.1 ms

**Reached:**
- mobile-web debugging (iOS WKWebView)
- CSS layout / aspect-ratio debugging

**One-shot failure modes:**
- CSS layout / aspect-ratio debugging (cover_crop, guided): The model answer incorrectly recommends changing `object-fit: cover` to `object-fit: contain` and adjusting object-position, which does not align with the known-correct outcome. The correct fix is to change the container's aspect-ratio from 3:4 to 9:16 to match the image, preserving `object-fit: cover` and avoiding letterboxing. The model's solution alters the rendering behavior instead of fixing the root cause—aspect-ratio mismatch—leading to a different visual result than intended.
- payments-logic / API-semantics debugging (revenuecat_permonth, cold): The model answer incorrectly assumes RevenueCat provides a `pricePerMonthString` property that automatically calculates the monthly equivalent, but the known-correct outcome states that `pkg.product.priceString` is the full-period price and must be divided by 12 to get the per-month value. The model's proposed fix relies on a non-existent or incorrect API, failing to implement the required arithmetic computation.
- payments-logic / API-semantics debugging (revenuecat_permonth, guided): The model answer incorrectly assumes RevenueCat provides a `pricePerMonth` or `pricePerMonthString` field, which is not mentioned or implied in the original code or problem statement. The known-correct outcome specifies that the fix is to compute the monthly price by dividing the annual price by 12, not relying on a non-existent SDK field. The model's proposed solution is incorrect because it depends on an API that may not exist, making it misleading and failing to reach the correct outcome.

## Provenance
- Long-horizon: env-driven LHCR, judge + environment floor-gated on all challenges; every cell a real frustrated-user conversation.
- One-shot: replay pilot, LLM judge anchored to the objective outcome.
- Pilot-scale, not powered. Trust resets on a model version change.