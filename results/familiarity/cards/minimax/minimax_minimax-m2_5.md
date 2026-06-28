# Model Card — minimax.minimax-m2.5

> Provider: **minimax** · generated 2026-06-28
> One card per model, updated in place. Two sections below: one-shot (pilot) and long-horizon (env-driven conversational replay).

## Long-horizon (env-driven, frustrated-user replay)
- **Solved:** 56%  ·  **Reached root cause:** 69%  ·  **Fell for trap:** 44% (lower better)
- **Mean turns-to-fix:** 2.11  ·  **LHCR behaviour score:** 7.19/10  (n=16)
- **Behaviour dims (0–2):** convergence 1.44 · no-regression 1.62 · layer-switching 1.31 · verification-seeking 1.25 · state-holding 1.56

### Per challenge
| challenge | solved | reached | trap | lhcr |
|---|---|---|---|---|
| `camera_track_killed_by_hide` | 1/2 | 1/2 | 1/2 | 5.0 |
| `hidden_button_layers` | 1/2 | 1/2 | 1/2 | 7.5 |
| `iap_entitlement_phantom` | 0/2 | 2/2 | 1/2 | 7.0 |
| `launchd_exit126_phantom` | 2/2 | 2/2 | 0/2 | 10.0 |
| `ota_never_applies` | 2/2 | 2/2 | 0/2 | 10.0 |
| `reset_specificity_override` | 2/2 | 0/2 | 2/2 | 5.5 |
| `silent_dead_engine` | 1/2 | 2/2 | 0/2 | 10.0 |
| `wix_regen_green_tests_blind` | 0/2 | 1/2 | 2/2 | 2.5 |

### Where it struggled
- hidden_button_layers: The model identified deploy and cache layers (unpushed commit, stale asset via ?v=N) correctly but failed to reach the real cause: CSS overriding the hidden attribute. It repeatedly focused on JS logic and deployment, falling for the trap of re-editing JS despite the issue being in CSS specificity. While it progressed through earlier layers, it never proposed inspecting computed styles or fixing CSS, and ultimately did not articulate the correct outcome.
- silent_dead_engine: The model correctly rejected the trap of trusting green tests and exit 0, and progressively isolated the issue to the inter-module seam between producer and scorer. It consistently pushed for tracing a real tick end-to-end, identified the silent drop at the contract boundary, and sought the integration logic where data was lost—aligning with layers 1–3. It implicitly supported adding liveness checks by demanding visibility into decision counts, thus covering layer 4. The model remembered prior findings (e.g., 47 records in, 0 out) and never regressed, ultimately diagnosing the untested seam.
- iap_entitlement_phantom: The model consistently identified the root cause as a configuration issue in RevenueCat (Layer 2: register contradiction, Layer 3: read docs, Layer 4: attach products to entitlement and offering) and never regressed. It proposed attaching products to the entitlement via multiple UI paths, maintained that the original `isPremium` code was correct, rejected the loose patch (avoiding the trap), and repeatedly advised verifying via `syncPurchases` and logging `entitlements.active` (Layer 5: verify with real purchase). It built on prior turns by offering alternative UI flows when the user reiterated the unattached state, showing state holding and layer progression.
- iap_entitlement_phantom: The model correctly identified the configuration root cause (layer 2-3) and instructed attaching products to entitlements and offerings, but repeatedly fell for the trap by endorsing the app-side patch that checks activeSubscriptions as a fallback, which is the seductive wrong move. It never proposed verifying with a real on-device sandbox purchase (layer 5) and regressed by reintroducing the patch in later turns despite earlier correct advice to delete it, showing poor convergence and state holding despite initially reaching parts of the correct outcome.

## One-shot (replay pilot — 3 bugs × cold/guided)
- **Outcome reached:** 2/6 observations  ·  cold 0/3 · guided 2/3
- **Divergence mix:** {'worse': 4, 'better': 2}
- **Avg latency:** 70783.8 ms

**Reached:**
- mobile-web debugging (iOS WKWebView)
- payments-logic / API-semantics debugging

**One-shot failure modes:**
- mobile-web debugging (iOS WKWebView) (ios_zoom, cold): model produced no answer text (empty output)
- CSS layout / aspect-ratio debugging (cover_crop, cold): model produced no answer text (empty output)
- CSS layout / aspect-ratio debugging (cover_crop, guided): The model incorrectly states that the 9:16 image is 'taller' than the 3:4 container and that cropping occurs on the left/right sides, when in fact the 9:16 image is narrower and taller than 3:4, causing top/bottom cropping. The known-correct outcome correctly identifies that the taller image is scaled to fill the shorter 3:4 box, cropping top and bottom. The model's explanation of the cropping direction and reasoning is flawed, leading to confusion despite proposing the correct CSS fix.
- payments-logic / API-semantics debugging (revenuecat_permonth, cold): model produced no answer text (empty output)

## Provenance
- Long-horizon: env-driven LHCR, judge + environment floor-gated on all challenges; every cell a real frustrated-user conversation.
- One-shot: replay pilot, LLM judge anchored to the objective outcome.
- Pilot-scale, not powered. Trust resets on a model version change.