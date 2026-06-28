# Model Card — qwen.qwen3-coder-480b-a35b-v1:0

> Provider: **qwen** · generated 2026-06-28
> One card per model, updated in place. Two sections below: one-shot (pilot) and long-horizon (env-driven conversational replay).

## Long-horizon (env-driven, frustrated-user replay)
- **Solved:** 62%  ·  **Reached root cause:** 62%  ·  **Fell for trap:** 44% (lower better)
- **Mean turns-to-fix:** 2.5  ·  **LHCR behaviour score:** 6.56/10  (n=16)
- **Behaviour dims (0–2):** convergence 1.25 · no-regression 1.44 · layer-switching 1.25 · verification-seeking 1.25 · state-holding 1.38

### Per challenge
| challenge | solved | reached | trap | lhcr |
|---|---|---|---|---|
| `camera_track_killed_by_hide` | 1/2 | 1/2 | 1/2 | 5.0 |
| `hidden_button_layers` | 2/2 | 2/2 | 1/2 | 8.5 |
| `iap_entitlement_phantom` | 0/2 | 0/2 | 2/2 | 0.0 |
| `launchd_exit126_phantom` | 1/2 | 2/2 | 0/2 | 7.5 |
| `ota_never_applies` | 2/2 | 2/2 | 0/2 | 10.0 |
| `reset_specificity_override` | 2/2 | 0/2 | 2/2 | 6.5 |
| `silent_dead_engine` | 1/2 | 2/2 | 0/2 | 10.0 |
| `wix_regen_green_tests_blind` | 1/2 | 1/2 | 1/2 | 5.0 |

### Where it struggled
- silent_dead_engine: The model progressively isolated the issue from infrastructure to data flow to logic, culminating in turn 11 by identifying that data enters but decisions are empty—pinpointing the inter-module seam failure. It advocated tracing a real tick end-to-end, exposed the silent drop at the scorer, and implicitly revealed the contract mismatch, aligning with the known root cause layers. It avoided the trap of blaming scheduling or declaring health due to green tests.
- launchd_exit126_phantom: The model correctly identified the inner command (./venv/bin/python) as the source of the 126 error and avoided the trap of re-chmoding the wrapper. It progressively explored symlink, directory, and extended attribute issues. However, it failed to recognize that the core issue was the relative path resolution in launchd's minimal environment (cwd=/) or the missing exec bit on the inner target, instead overcomplicating with quarantine attributes and venv recreation. It sought verification via logs and testing but did not propose the minimal fix of using an absolute path or restoring the exec bit on the single shared target.
- iap_entitlement_phantom: The model immediately proposed the trap solution in turn 1 by endorsing the app-side patch that unlocks based on activeSubscriptions, which explicitly trusts raw product IDs over entitlements.active. It never correctly identified the configuration root cause (products not attached to entitlement + offering in RevenueCat, IAPs not attached in ASC). Across all turns, it repeatedly regressed to the same dashboard configuration guess without progressing through the known layers, failed to propose verifying with a real on-device sandbox purchase, and ignored the critical 404 and attachment endpoint issue. It never reached the known-correct outcome.
- iap_entitlement_phantom: The model repeatedly advocated for the app-side patch (trusting activeSubscriptions) which is THE TRAP, explicitly rejecting the entitlements.active source of truth. It never identified the configuration root cause (products not attached to entitlement/offering), failed to progress through the known layers, and regressed by re-asserting the same flawed fix across turns despite user rejection. It did not propose verifying with a real on-device purchase or using the documented attach endpoint.

## One-shot (replay pilot — 3 bugs × cold/guided)
- **Outcome reached:** 6/6 observations  ·  cold 3/3 · guided 3/3
- **Divergence mix:** {'better': 5, 'worse': 1}
- **Avg latency:** 4306.4 ms

**Reached:**
- mobile-web debugging (iOS WKWebView)
- CSS layout / aspect-ratio debugging
- payments-logic / API-semantics debugging

**One-shot failure modes:**
- CSS layout / aspect-ratio debugging (cover_crop, guided): The model correctly identifies the aspect-ratio mismatch and suggests fixing the container to 9/16, which aligns with the known-correct outcome. However, it unnecessarily changes object-fit to 'contain', which would prevent cropping but may introduce letterboxing; 'cover' would work fine with matching aspect ratios. The fix is partially correct but includes an incorrect recommendation that deviates from the optimal solution.

## Provenance
- Long-horizon: env-driven LHCR, judge + environment floor-gated on all challenges; every cell a real frustrated-user conversation.
- One-shot: replay pilot, LLM judge anchored to the objective outcome.
- Pilot-scale, not powered. Trust resets on a model version change.