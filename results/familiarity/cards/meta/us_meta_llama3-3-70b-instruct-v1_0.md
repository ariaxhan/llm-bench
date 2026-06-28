# Model Card — us.meta.llama3-3-70b-instruct-v1:0

> Provider: **meta** · generated 2026-06-28
> One card per model, updated in place. Two sections below: one-shot (pilot) and long-horizon (env-driven conversational replay).

## Long-horizon (env-driven, frustrated-user replay)
- **Solved:** 31%  ·  **Reached root cause:** 50%  ·  **Fell for trap:** 62% (lower better)
- **Mean turns-to-fix:** 2.0  ·  **LHCR behaviour score:** 4.19/10  (n=16)
- **Behaviour dims (0–2):** convergence 0.62 · no-regression 1.25 · layer-switching 0.75 · verification-seeking 0.81 · state-holding 0.75

### Per challenge
| challenge | solved | reached | trap | lhcr |
|---|---|---|---|---|
| `camera_track_killed_by_hide` | 0/2 | 0/2 | 2/2 | 0.0 |
| `hidden_button_layers` | 0/2 | 0/2 | 2/2 | 2.5 |
| `iap_entitlement_phantom` | 0/2 | 1/2 | 2/2 | 3.0 |
| `launchd_exit126_phantom` | 2/2 | 2/2 | 0/2 | 9.0 |
| `ota_never_applies` | 1/2 | 2/2 | 0/2 | 8.0 |
| `reset_specificity_override` | 2/2 | 1/2 | 1/2 | 5.0 |
| `silent_dead_engine` | 0/2 | 1/2 | 1/2 | 5.0 |
| `wix_regen_green_tests_blind` | 0/2 | 1/2 | 2/2 | 1.0 |

### Where it struggled
- hidden_button_layers: The model repeatedly proposed JavaScript-based fixes (e.g., using display: none, CSS classes, !important) despite the real cause being CSS specificity overriding the [hidden] attribute, which requires inspecting computed styles. It fell for the trap by re-editing JS and asserting fixes that wouldn't work, never identifying the CSS layer as the root cause. It did not progress through the known layers (deploy, cache, CSS, cleanup) and re-litigated the same JS solutions across turns.
- hidden_button_layers: The model repeatedly proposed JavaScript-based fixes (setting display, visibility, !important, classes) which is THE TRAP, ignoring the real CSS specificity issue with the [hidden] attribute. It never identified the deploy gap, cache-buster, or the need for [hidden] { display: none !important } despite multiple failures, re-litigating the same layer each time and failing to progress through the known layers of root cause.
- ota_never_applies: The model eventually identified that the downloaded bundle is not being activated (layer 2) and suggested `activateUpdate()`, aligning with the known-correct outcome. It progressively incorporated user feedback, avoided network red herrings, and proposed runtime checks like logging the active bundle path. However, it took five turns to reach this point, repeatedly suggested ineffective reloads, and did not clearly distinguish between download, activation, and reload ordering until late, making it slower and less precise than ideal.
- silent_dead_engine: The model eventually identified the core issue — a silent failure at the seam between producer and scorer where data is lost despite clean execution — and consistently refined its focus on data flow, serialization, and configuration. It avoided the trap of accepting green tests and exit 0 as proof of health, and from turn 7 onward, correctly centered on the inter-module contract. It proposed tracing real data, added meaningful logging, and converged on the known-correct outcome by emphasizing end-to-end validation and silent drop detection, though it repeated some suggestions.

## One-shot (replay pilot — 3 bugs × cold/guided)
- **Outcome reached:** 4/6 observations  ·  cold 2/3 · guided 2/3
- **Divergence mix:** {'worse': 3, 'better': 1, 'equivalent': 2}
- **Avg latency:** 3669.9 ms

**Reached:**
- CSS layout / aspect-ratio debugging
- payments-logic / API-semantics debugging

**One-shot failure modes:**
- mobile-web debugging (iOS WKWebView) (ios_zoom, cold): The model answer incorrectly promotes the viewport-lock fix (maximum-scale=1.0, user-scalable=no) as a valid solution, despite the known-correct outcome explicitly stating it is inferior and harms accessibility. While it does mention increasing font size to 16px, it presents the two solutions as equally viable options rather than identifying the font-size fix as the correct and preferred solution, thus failing to fully reach the known-correct outcome.
- mobile-web debugging (iOS WKWebView) (ios_zoom, guided): The model answer incorrectly presents the viewport-lock fix (maximum-scale=1.0, user-scalable=no) as a valid solution, which the known-correct outcome explicitly states is inferior and harms accessibility. While it does mention setting font-size to 16px, it fails to identify that as the root cause and primary correct fix, instead treating it as one of several options including the discouraged viewport change.
- CSS layout / aspect-ratio debugging (cover_crop, guided): The model answer identifies the aspect-ratio mismatch correctly and suggests matching the cover card's aspect ratio to 9:16 as a valid fix, which aligns with the known-correct outcome. However, it also suggests using `object-fit: contain` or a complex padding-based workaround as alternatives, which do not achieve the intended visual result of a fully covered, uncropped 9:16 image in a properly sized container—making the response partially incorrect and potentially misleading.

## Provenance
- Long-horizon: env-driven LHCR, judge + environment floor-gated on all challenges; every cell a real frustrated-user conversation.
- One-shot: replay pilot, LLM judge anchored to the objective outcome.
- Pilot-scale, not powered. Trust resets on a model version change.