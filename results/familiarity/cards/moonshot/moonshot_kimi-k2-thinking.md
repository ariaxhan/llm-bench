# Model Card — moonshot.kimi-k2-thinking

> Provider: **moonshot** · generated 2026-06-28
> One card per model, updated in place. Two sections below: one-shot (pilot) and long-horizon (env-driven conversational replay).

## Long-horizon (env-driven, frustrated-user replay)
- **Solved:** 62%  ·  **Reached root cause:** 81%  ·  **Fell for trap:** 25% (lower better)
- **Mean turns-to-fix:** 1.8  ·  **LHCR behaviour score:** 8.44/10  (n=16)
- **Behaviour dims (0–2):** convergence 1.56 · no-regression 1.88 · layer-switching 1.62 · verification-seeking 1.62 · state-holding 1.75

### Per challenge
| challenge | solved | reached | trap | lhcr |
|---|---|---|---|---|
| `camera_track_killed_by_hide` | 2/2 | 2/2 | 0/2 | 9.5 |
| `hidden_button_layers` | 2/2 | 2/2 | 1/2 | 10.0 |
| `iap_entitlement_phantom` | 0/2 | 2/2 | 0/2 | 10.0 |
| `launchd_exit126_phantom` | 1/2 | 2/2 | 0/2 | 9.0 |
| `ota_never_applies` | 1/2 | 2/2 | 0/2 | 10.0 |
| `reset_specificity_override` | 2/2 | 1/2 | 1/2 | 9.0 |
| `silent_dead_engine` | 2/2 | 1/2 | 1/2 | 9.0 |
| `wix_regen_green_tests_blind` | 0/2 | 1/2 | 1/2 | 1.0 |

### Where it struggled
- ota_never_applies: The model progressively ruled out network, save path, native persistence, and bundle integrity, aligning with the known layers. It culminated in identifying the activation/relaunch ordering issue—specifically that the native bridge initializes before the OTA path is checked, causing the old bundle to load. It proposed live verification (survival marker, path logging) and preserved prior exclusions, ultimately articulating the correct outcome: the downloaded bundle is staged but never promoted into active use due to initialization timing.
- iap_entitlement_phantom: The model correctly identified the root cause as unattached products in RevenueCat from turn 1 and consistently directed the user to attach products to the entitlement and offering, never regressing or suggesting the dangerous patch as a solution. It maintained focus on the configuration fix across all turns, proposed concrete verification steps including uninstalling the app and checking live logs, and built on prior responses by refining instructions without re-litigating earlier points.
- iap_entitlement_phantom: The model correctly identified the root cause as a configuration issue in RevenueCat (Layer 2: register contradiction) and consistently guided the user to attach products to the entitlement and offering (Layer 4: attach products), which aligns with the known-correct outcome. It avoided the trap of endorsing the app-side patch, insisted on using entitlements.active as the source of truth, and included live verification steps like calling syncPurchases() and logging runtime state. Each turn built on the previous, maintaining state and progressing toward the full fix without regression.
- launchd_exit126_phantom: The model correctly identified the inner command execution failure (layer 2) and focused on the venv's python binary (layer 3), avoiding the trap of chmod +x on the wrapper. It progressed through layers by ruling out quarantine attrs and considering symlink targets and permissions. However, it never fully grasped the shared dependency aspect — all jobs fail due to one common inner target — and instead recommended recreating each venv individually, which is a broader, less precise fix than restoring execute permission on the single shared interpreter or using an absolute path. It proposed manual testing but not verification via a single job's real output.

## One-shot (replay pilot — 3 bugs × cold/guided)
- **Outcome reached:** 6/6 observations  ·  cold 3/3 · guided 3/3
- **Divergence mix:** {'better': 6}
- **Avg latency:** 16717.5 ms

**Reached:**
- mobile-web debugging (iOS WKWebView)
- CSS layout / aspect-ratio debugging
- payments-logic / API-semantics debugging

## Provenance
- Long-horizon: env-driven LHCR, judge + environment floor-gated on all challenges; every cell a real frustrated-user conversation.
- One-shot: replay pilot, LLM judge anchored to the objective outcome.
- Pilot-scale, not powered. Trust resets on a model version change.