# Model Card — qwen.qwen3-32b-v1:0

> Provider: **qwen** · generated 2026-06-28
> One card per model, updated in place. Two sections below: one-shot (pilot) and long-horizon (env-driven conversational replay).

## Long-horizon (env-driven, frustrated-user replay)
- **Solved:** 50%  ·  **Reached root cause:** 50%  ·  **Fell for trap:** 38% (lower better)
- **Mean turns-to-fix:** 1.88  ·  **LHCR behaviour score:** 5.56/10  (n=16)
- **Behaviour dims (0–2):** convergence 1.0 · no-regression 1.38 · layer-switching 0.94 · verification-seeking 1.25 · state-holding 1.0

### Per challenge
| challenge | solved | reached | trap | lhcr |
|---|---|---|---|---|
| `camera_track_killed_by_hide` | 2/2 | 2/2 | 0/2 | 9.0 |
| `hidden_button_layers` | 2/2 | 2/2 | 0/2 | 10.0 |
| `iap_entitlement_phantom` | 1/2 | 2/2 | 0/2 | 7.0 |
| `launchd_exit126_phantom` | 0/2 | 0/2 | 2/2 | 0.0 |
| `ota_never_applies` | 0/2 | 1/2 | 0/2 | 5.5 |
| `reset_specificity_override` | 2/2 | 0/2 | 2/2 | 6.0 |
| `silent_dead_engine` | 1/2 | 1/2 | 0/2 | 7.0 |
| `wix_regen_green_tests_blind` | 0/2 | 0/2 | 2/2 | 0.0 |

### Where it struggled
- ota_never_applies: The model repeatedly focused on native module-based bundle loading and app restarts (Layer 3: relaunch), never advancing to the core issue of bundle activation state (Layer 2: staged but not marked active). Despite the user confirming the downloaded bundle is unused at launch, the model reasserted the same fix across turns without switching layers. It correctly proposed checking the live bundle path (verification), but failed to interpret that evidence as proof the activation step was missing, instead insisting on flawed reload mechanisms. It did not articulate the known-correct outcome of promotion/activation state management.
- iap_entitlement_phantom: The model correctly identified the root cause as a configuration issue in RevenueCat (Layer 2 and 3) and consistently advised attaching unattached products to the entitlement, which aligns with the known-correct outcome. It never regressed or proposed the trap (using the loose patch as a fix), and explicitly warned against it. However, it repeatedly gave the same instructions across turns without advancing the reasoning or diagnosing further (e.g., offering or App Store Connect setup), showing no layer switching and poor state holding. It mentioned verification but only generically, not requiring a real on-device sandbox purchase as specified.
- silent_dead_engine: The model repeatedly suggested logging and debugging steps but never identified the core issue: a silent contract mismatch at an inter-module seam causing zero decisions despite clean runs. It failed to progress beyond surface-level diagnostics (Layer 1 and 2 guesses) and never reached the known-correct outcome involving untested seams, integration tests, or liveness assertions. Despite correct verification-seeking by asking to trace a tick, it did not interpret the user's repeated 'traced a tick' feedback as evidence of a broken seam, instead recycling the same suggestions.
- launchd_exit126_phantom: The model repeatedly proposed chmod +x on the wrapper script and reworked the plist structure, ignoring the user's confirmation that the script is already executable and the error log points to an inner command. It never identified the real issue: the venv interpreter's missing execute bit or path resolution in launchd's environment. Instead, it regressed into increasingly incorrect fixes like using /bin/sh, rewriting the plist to use sh -c, and suggesting binary wrappers, all while ignoring the StandardErrorPath evidence of './venv/bin/python: Permission denied'. It fell for the trap by focusing on the wrapper's permissions and shebang, despite the known-correct root cause being the non-executable inner target shared across jobs.

## One-shot (replay pilot — 3 bugs × cold/guided)
- **Outcome reached:** 3/6 observations  ·  cold 2/3 · guided 1/3
- **Divergence mix:** {'better': 3, 'worse': 3}
- **Avg latency:** 4353.4 ms

**Reached:**
- mobile-web debugging (iOS WKWebView)
- CSS layout / aspect-ratio debugging

**One-shot failure modes:**
- mobile-web debugging (iOS WKWebView) (ios_zoom, guided): The model answer recommends the inferior viewport-lock fix (maximum-scale=1.0, user-scalable=no), which the known-correct outcome explicitly warns against because it harms accessibility by disabling pinch-zoom app-wide. While it does suggest increasing font-size to 16px (a correct fix), it pairs it with the harmful viewport change, failing to prioritize the accessible solution.
- payments-logic / API-semantics debugging (revenuecat_permonth, cold): The model incorrectly identifies the bug as appending '/yr' to priceString, but the real issue is assigning the full annual priceString to pricePerMonth without dividing by 12. The model's fix leaves pricePerMonth unchanged, which perpetuates the bug by showing $79.99/mo for an annual plan. The known-correct outcome requires computing pricePerMonth as price/12, which the model fails to address.
- payments-logic / API-semantics debugging (revenuecat_permonth, guided): The model misidentifies the root cause, claiming `priceString` contains the per-period price when it actually contains the full-period price. It incorrectly suggests using `pricePerMonth` as if it were already correct, while the known-correct outcome states that `pricePerMonth` must be computed as `price / 12` because `pkg.product.priceString` is the annual amount. The model fails to recognize that `pricePerMonth` is currently being incorrectly set to `priceString` and needs to be recalculated.

## Provenance
- Long-horizon: env-driven LHCR, judge + environment floor-gated on all challenges; every cell a real frustrated-user conversation.
- One-shot: replay pilot, LLM judge anchored to the objective outcome.
- Pilot-scale, not powered. Trust resets on a model version change.