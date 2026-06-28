# Model Card — us.meta.llama4-scout-17b-instruct-v1:0

> Provider: **meta** · generated 2026-06-28
> One card per model, updated in place. Two sections below: one-shot (pilot) and long-horizon (env-driven conversational replay).

## Long-horizon (env-driven, frustrated-user replay)
- **Solved:** 12%  ·  **Reached root cause:** 19%  ·  **Fell for trap:** 75% (lower better)
- **Mean turns-to-fix:** 3.0  ·  **LHCR behaviour score:** 2.0/10  (n=16)
- **Behaviour dims (0–2):** convergence 0.25 · no-regression 0.69 · layer-switching 0.25 · verification-seeking 0.56 · state-holding 0.25

### Per challenge
| challenge | solved | reached | trap | lhcr |
|---|---|---|---|---|
| `camera_track_killed_by_hide` | 0/2 | 0/2 | 2/2 | 0.0 |
| `hidden_button_layers` | 0/2 | 0/2 | 2/2 | 0.0 |
| `iap_entitlement_phantom` | 0/2 | 1/2 | 2/2 | 4.0 |
| `launchd_exit126_phantom` | 1/2 | 1/2 | 0/2 | 5.0 |
| `ota_never_applies` | 0/2 | 0/2 | 1/2 | 0.5 |
| `reset_specificity_override` | 1/2 | 0/2 | 2/2 | 1.0 |
| `silent_dead_engine` | 0/2 | 1/2 | 1/2 | 4.5 |
| `wix_regen_green_tests_blind` | 0/2 | 0/2 | 2/2 | 1.0 |

### Where it struggled
- hidden_button_layers: The model repeatedly proposed re-editing the JS or adding more aggressive CSS overrides (like !important), which is THE TRAP of focusing on JS when the real issue is CSS specificity overriding the `hidden` attribute. It never identified the deploy gap, cache-buster stale version, or the core CSS layer where `.primary { display: inline-flex }` beats `[hidden]`. It regressed by re-proposing the same fixes despite user feedback, failed to verify computed styles, and did not switch layers beyond superficial changes to CSS selectors.
- hidden_button_layers: The model repeatedly focused on JavaScript fixes (setting class, style, !important via JS) despite user rejections, never identifying the real cause: CSS specificity overriding the `hidden` attribute. It failed to inspect computed styles or consider deploy/cache layers, re-litigated the same JS-centric solutions, and fell into the trap of re-editing JS when the issue was in CSS precedence and asset delivery.
- ota_never_applies: The model never identified the core issue: the downloaded bundle is not being promoted to active or relaunched in the correct order. It repeatedly suggested cache clearing, JS engine restarts, and configuration checks—none of which address the activation and reload sequencing. It failed to progress through the known layers, instead reasserting variations of the same ineffective fixes and ignoring the fact that the download succeeds (layer 1 ruled out). No verification of which bundle is actually loaded at runtime was ever proposed.
- silent_dead_engine: The model eventually identified the core issue in turn 11 — that the producer emits candidates but the scorer receives an empty list — aligning with layer 2 (trace a real tick) and layer 3 (seam mismatch). It consistently sought verification via logging and debugging, satisfying verification_seeking. However, it took 11 turns to reach this, repeating generic advice (logging, testing components) without progressing through the known layers efficiently, showing poor convergence and layer_switching. It did not fall for the trap of accepting 'green build + exit 0' as healthy. While it reached the correct outcome, it failed to propose the full fix (integration test, liveness assertion) from the known outcome, making its resolution incomplete — hence 'worse' despite reaching the root cause.

## One-shot (replay pilot — 3 bugs × cold/guided)
- **Outcome reached:** 4/6 observations  ·  cold 2/3 · guided 2/3
- **Divergence mix:** {'worse': 3, 'better': 3}
- **Avg latency:** 3586.3 ms

**Reached:**
- mobile-web debugging (iOS WKWebView)
- CSS layout / aspect-ratio debugging
- payments-logic / API-semantics debugging

**One-shot failure modes:**
- mobile-web debugging (iOS WKWebView) (ios_zoom, cold): The model incorrectly identifies the root cause as WKWebView ignoring viewport settings, when it is actually iOS Safari/WKWebView auto-zooming due to a font size below 16px. The model recommends the inferior viewport-lock fix (maximum-scale=1, user-scalable=no), which contradicts the known-correct outcome that this harms accessibility and is not the correct solution. The correct fix—setting the input font-size to >=16px—is mentioned but downplayed and mixed with incorrect advice.
- mobile-web debugging (iOS WKWebView) (ios_zoom, guided): The model answer correctly identifies the root cause (font size < 16px triggering zoom) and suggests setting font-size to 16px, which aligns with the known-correct outcome. However, it also recommends the inferior viewport-lock fix (maximum-scale=1, user-scalable=no), which harms accessibility and is explicitly called out in the known-correct outcome as suboptimal. This inclusion of a harmful workaround makes the answer materially worse despite partial correctness.
- CSS layout / aspect-ratio debugging (cover_crop, guided): The model answer incorrectly suggests changing object-fit to 'contain' to fix the cropping, but the known-correct outcome identifies that the root issue is an aspect-ratio mismatch and the fix is to align the cover card's aspect ratio with the image's 9:16. Changing to 'contain' would prevent cropping but likely introduce unwanted letterboxing, rather than fixing the layout to match the image.

## Provenance
- Long-horizon: env-driven LHCR, judge + environment floor-gated on all challenges; every cell a real frustrated-user conversation.
- One-shot: replay pilot, LLM judge anchored to the objective outcome.
- Pilot-scale, not powered. Trust resets on a model version change.