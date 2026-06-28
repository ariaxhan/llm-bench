# Model Card — zai.glm-4.7-flash

> Provider: **zai** · generated 2026-06-28
> One card per model, updated in place. Two sections below: one-shot (pilot) and long-horizon (env-driven conversational replay).

## Long-horizon (env-driven, frustrated-user replay)
- **Solved:** 19%  ·  **Reached root cause:** 38%  ·  **Fell for trap:** 69% (lower better)
- **Mean turns-to-fix:** 3.33  ·  **LHCR behaviour score:** 3.38/10  (n=16)
- **Behaviour dims (0–2):** convergence 0.5 · no-regression 1.12 · layer-switching 0.5 · verification-seeking 0.75 · state-holding 0.5

### Per challenge
| challenge | solved | reached | trap | lhcr |
|---|---|---|---|---|
| `camera_track_killed_by_hide` | 0/2 | 0/2 | 2/2 | 0.0 |
| `hidden_button_layers` | 0/2 | 2/2 | 1/2 | 5.5 |
| `iap_entitlement_phantom` | 1/2 | 2/2 | 1/2 | 6.0 |
| `launchd_exit126_phantom` | 0/2 | 0/2 | 1/2 | 0.0 |
| `ota_never_applies` | 1/2 | 1/2 | 1/2 | 6.0 |
| `reset_specificity_override` | 0/2 | 0/2 | 2/2 | 2.0 |
| `silent_dead_engine` | 1/2 | 1/2 | 1/2 | 6.5 |
| `wix_regen_green_tests_blind` | 0/2 | 0/2 | 2/2 | 1.0 |

### Where it struggled
- hidden_button_layers: The model eventually identified CSS specificity overriding the [hidden] attribute (Layer 3) and suggested inspecting computed styles, fulfilling verification_seeking. However, it repeatedly fell for the trap by prioritizing JS fixes (Layers 1-2) and re-asserting cache/deploy issues even after user rejection, showing poor convergence and layer_switching. It reached the correct outcome late but contradicted earlier correct directions, and proposed the seductive JS fix multiple times.
- hidden_button_layers: The model correctly identified the deploy gap (layer 1) and cache issues (layer 2) and persisted on those, but never addressed the real cause—CSS specificity overriding the hidden attribute (layer 3). It repeatedly advised JS and deployment fixes, failing to propose inspecting computed styles or adjusting CSS with !important. While it ruled out client-side caching and execution issues, it did not progress to the actual root cause, making its resolution incomplete despite correct partial findings.
- ota_never_applies: The model repeatedly asserted the same fix (dynamic loading, entry point issues) across all turns without progressing through the known layers of root cause. It never addressed the actual issue—activation and relaunch state management—instead fixating on bundle loading mechanics. It failed to incorporate user feedback that fixes were tried and ineffective, showing no state holding or layer switching.
- silent_dead_engine: The model repeatedly proposed surface-level fixes (e.g., logging, mocks, file pointers) without progressing through the known layers of root cause. It fell for the trap by initially accepting 'green tests and exit 0 = healthy' and later suggesting mock stores and silent writes, which aligns with the seductive wrong move. Despite the user repeatedly confirming data enters the system and the scorer receives an empty list, the model reasserted the same layer (e.g., filtering, type mismatch) without advancing to the seam contract mismatch. It did propose tracing a real tick (verification_seeking=2), but failed to interpret the result as a broken inter-module seam, instead regressing to file and buffer theories. It did not articulate the known-correct outcome of an untested seam with a contract mismatch and a missing liveness check.

## One-shot (replay pilot — 3 bugs × cold/guided)
- **Outcome reached:** 4/6 observations  ·  cold 2/3 · guided 2/3
- **Divergence mix:** {'worse': 2, 'better': 4}
- **Avg latency:** 1713.6 ms

**Reached:**
- mobile-web debugging (iOS WKWebView)
- CSS layout / aspect-ratio debugging
- payments-logic / API-semantics debugging

**One-shot failure modes:**
- mobile-web debugging (iOS WKWebView) (ios_zoom, cold): The model answer incorrectly attributes the zoom to a viewport-to-font-size ratio calculation involving 375px width and 13px text, which is not how iOS auto-zoom works. The known-correct outcome states the actual cause: iOS auto-zooms when an input's computed font-size is below 16px, regardless of viewport width math. The model's proposed fix of setting html/body font-size to 16px may indirectly help but misdiagnoses the core issue, which is specifically the input's inherited 13px font-size triggering zoom on focus.
- CSS layout / aspect-ratio debugging (cover_crop, guided): The model incorrectly states that the card is wider than the photo, when 3:4 (0.75) is actually taller than 9:16 (0.5625). The core explanation of the cropping cause is wrong. The recommended fix (changing the image to 3:4) contradicts the known-correct outcome, which states the card should match the image's 9:16 ratio.

## Provenance
- Long-horizon: env-driven LHCR, judge + environment floor-gated on all challenges; every cell a real frustrated-user conversation.
- One-shot: replay pilot, LLM judge anchored to the objective outcome.
- Pilot-scale, not powered. Trust resets on a model version change.