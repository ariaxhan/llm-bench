# Model Card — deepseek.v3.2

> Provider: **deepseek** · generated 2026-06-28
> One card per model, updated in place. Two sections below: one-shot (pilot) and long-horizon (env-driven conversational replay).

## Long-horizon (env-driven, frustrated-user replay)
- **Solved:** 62%  ·  **Reached root cause:** 75%  ·  **Fell for trap:** 31% (lower better)
- **Mean turns-to-fix:** 1.2  ·  **LHCR behaviour score:** 7.44/10  (n=16)
- **Behaviour dims (0–2):** convergence 1.5 · no-regression 1.62 · layer-switching 1.38 · verification-seeking 1.31 · state-holding 1.62

### Per challenge
| challenge | solved | reached | trap | lhcr |
|---|---|---|---|---|
| `camera_track_killed_by_hide` | 2/2 | 2/2 | 0/2 | 9.0 |
| `hidden_button_layers` | 2/2 | 2/2 | 0/2 | 10.0 |
| `iap_entitlement_phantom` | 0/2 | 1/2 | 2/2 | 2.5 |
| `launchd_exit126_phantom` | 2/2 | 2/2 | 0/2 | 10.0 |
| `ota_never_applies` | 1/2 | 2/2 | 0/2 | 8.0 |
| `reset_specificity_override` | 2/2 | 0/2 | 2/2 | 5.0 |
| `silent_dead_engine` | 0/2 | 2/2 | 0/2 | 10.0 |
| `wix_regen_green_tests_blind` | 1/2 | 1/2 | 1/2 | 5.0 |

### Where it struggled
- silent_dead_engine: The model progressively narrowed the issue from general silent failure (layer 1) to data flow between modules (layer 2), identified the seam contract mismatch (layer 3), and proposed fixes and tests to catch it (layer 4). It consistently built on prior findings, sought runtime verification via tracing and logging, and never regressed or fell for the trap of accepting green tests/exit 0 as proof of health.
- silent_dead_engine: The model progressively narrowed from general failure modes to the specific inter-module seam issue, consistently building on user feedback. It correctly identified the silent drop at the producer-scorer boundary (layer 2), diagnosed contract/shape mismatch (layer 3), and emphasized tracing real data end-to-end. It never regressed, avoided the trap of accepting exit 0 as success, and ultimately prescribed integration testing and liveness checks (layer 4), matching the known-correct outcome.
- ota_never_applies: The model eventually identified that the downloaded bundle must be actively loaded at launch (layer 2: activation/promotion), and correctly focused on native-level bundle loading via getJSBundleFile. It consistently verified the active bundle path through user feedback and proposed live checks. However, it fixated on complex native workarounds (reflection, source patching) rather than the simpler state-based activation and reload sequencing, and failed to fully integrate the ordering issue (layer 3) cleanly, leading to overcomplicated solutions despite reaching the core insight.
- iap_entitlement_phantom: The model repeatedly recommended a code-level fallback using activeSubscriptions as a workaround, which directly implements the seductive trap of trusting raw product IDs instead of fixing the configuration. It never fully articulated the need to attach products to both the entitlement and an offering in RevenueCat, nor mentioned App Store Connect attachment or the documented attach endpoint. The model regressed by re-asserting the same flawed fix across turns, failed to verify with on-device testing, and ignored the accumulating user signal that the dashboard state remained unchanged, indicating no progress on the actual config root cause.

## One-shot (replay pilot — 3 bugs × cold/guided)
- **Outcome reached:** 5/6 observations  ·  cold 2/3 · guided 3/3
- **Divergence mix:** {'better': 4, 'worse': 2}
- **Avg latency:** 5464.1 ms

**Reached:**
- mobile-web debugging (iOS WKWebView)
- CSS layout / aspect-ratio debugging
- payments-logic / API-semantics debugging

**One-shot failure modes:**
- mobile-web debugging (iOS WKWebView) (ios_zoom, guided): The model answer correctly identifies the root cause and the primary fix (setting font-size to >=16px), but then recommends a viewport meta tag with maximum-scale=1 and user-scalable=no as a fallback, which the known-correct outcome explicitly rejects as inferior due to accessibility harm. It also introduces unnecessary JavaScript solutions, which are not part of the correct fix and could introduce side effects. While it acknowledges the accessibility tradeoff, it still promotes a less-accessible solution as an option, making the advice less correct overall.
- payments-logic / API-semantics debugging (revenuecat_permonth, cold): The model answer incorrectly assumes RevenueCat's priceString includes period information and misidentifies the root cause. The known-correct outcome states that priceString contains only the raw price (e.g., '$79.99') without any period suffix, and the bug is in directly assigning priceString to pricePerMonth. The model's proposed fix incorrectly relies on introPrice and does not address the core issue: for annual plans, pricePerMonth must be derived by dividing the annual price by 12, not copied from priceString.

## Provenance
- Long-horizon: env-driven LHCR, judge + environment floor-gated on all challenges; every cell a real frustrated-user conversation.
- One-shot: replay pilot, LLM judge anchored to the objective outcome.
- Pilot-scale, not powered. Trust resets on a model version change.