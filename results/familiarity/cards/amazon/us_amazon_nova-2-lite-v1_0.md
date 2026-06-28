# Model Card — us.amazon.nova-2-lite-v1:0

> Provider: **amazon** · generated 2026-06-28
> One card per model, updated in place. Two sections below: one-shot (pilot) and long-horizon (env-driven conversational replay).

## Long-horizon (env-driven, frustrated-user replay)
- **Solved:** 38%  ·  **Reached root cause:** 75%  ·  **Fell for trap:** 44% (lower better)
- **Mean turns-to-fix:** 1.67  ·  **LHCR behaviour score:** 6.81/10  (n=16)
- **Behaviour dims (0–2):** convergence 1.31 · no-regression 1.62 · layer-switching 1.31 · verification-seeking 1.19 · state-holding 1.38

### Per challenge
| challenge | solved | reached | trap | lhcr |
|---|---|---|---|---|
| `camera_track_killed_by_hide` | 2/2 | 2/2 | 0/2 | 9.0 |
| `hidden_button_layers` | 0/2 | 1/2 | 1/2 | 5.0 |
| `iap_entitlement_phantom` | 0/2 | 2/2 | 0/2 | 10.0 |
| `launchd_exit126_phantom` | 1/2 | 2/2 | 1/2 | 7.0 |
| `ota_never_applies` | 0/2 | 1/2 | 2/2 | 3.5 |
| `reset_specificity_override` | 2/2 | 1/2 | 1/2 | 7.5 |
| `silent_dead_engine` | 1/2 | 2/2 | 0/2 | 10.0 |
| `wix_regen_green_tests_blind` | 0/2 | 1/2 | 2/2 | 2.5 |

### Where it struggled
- hidden_button_layers: The model repeatedly focused on the deploy gap (Layer 1) and cache-buster (Layer 2), reiterating git push and version bump steps across turns 1, 3, 5, 7, 9, 11 without progressing to the real cause. It fell for the trap by initially suggesting to change the JS logic or use `style.display = 'none'`, which addresses the symptom but not the root cause. It never identified the CSS specificity issue (Layer 3) or proposed inspecting computed styles, and failed to recognize that even a correctly deployed JS fix would fail due to CSS overriding `hidden`. The model ignored the user's repeated confirmation of the deploy gap and did not switch layers or advance diagnosis.
- hidden_button_layers: The model eventually identified the real cause (CSS overriding [hidden]) and suggested valid fixes like !important and higher specificity, showing verification-seeking by directing user to DevTools. However, it remained stuck on the JS layer for too long, repeatedly suggesting JS-based solutions (style.display, MutationObserver) even after the user revealed the computed style, indicating poor layer switching and partial state holding. It reached the correct outcome but with significant thrashing and inefficiency.
- ota_never_applies: The model eventually reached the correct outcome by emphasizing bundle path loading and React instance destruction, which aligns with the activation and relaunch fix (layer 2 and 3). It proposed meaningful verification steps like logging the loaded bundle path and checking bundle content. However, it fell for the trap early by focusing on cache headers and retries (layer 1), which the user had already ruled out, and repeatedly re-asserted restart and path-override fixes without advancing beyond layer 2, showing limited layer switching and convergence despite correct elements.
- ota_never_applies: The model repeatedly focused on network caching and restart mechanics, reiterating cache-busting and restart code across turns despite user rejection, which aligns with THE TRAP of chasing network issues. It never identified the core issue: the downloaded bundle is staged but not promoted to active, and the runtime continues loading the old bundle because activation state isn't advanced. The model failed to shift to layer 2 (promotion) or layer 3 (activation+reload ordering), instead recycling the same restart and eval suggestions, showing no convergence, state holding, or layer switching.

## One-shot (replay pilot — 3 bugs × cold/guided)
- **Outcome reached:** 5/6 observations  ·  cold 2/3 · guided 3/3
- **Divergence mix:** {'better': 5, 'worse': 1}
- **Avg latency:** 5714.1 ms

**Reached:**
- mobile-web debugging (iOS WKWebView)
- CSS layout / aspect-ratio debugging
- payments-logic / API-semantics debugging

**One-shot failure modes:**
- payments-logic / API-semantics debugging (revenuecat_permonth, cold): The model answer incorrectly claims the bug is in the `price` field's suffix handling and suggests using `pkg.product.priceString` directly for both `price` and `pricePerMonth`. However, the known-correct outcome states that `pkg.product.priceString` is the full annual price ($79.99/year), not a per-month value, and that `pricePerMonth` is wrong because it reuses this full price. The correct fix requires computing `pricePerMonth` as `price / 12`, which the model answer fails to address and instead incorrectly treats `priceString` as already containing the per-month equivalent.

## Provenance
- Long-horizon: env-driven LHCR, judge + environment floor-gated on all challenges; every cell a real frustrated-user conversation.
- One-shot: replay pilot, LLM judge anchored to the objective outcome.
- Pilot-scale, not powered. Trust resets on a model version change.