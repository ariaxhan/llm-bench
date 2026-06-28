# Model Card — mistral.magistral-small-2509

> Provider: **mistral** · generated 2026-06-28
> One card per model, updated in place. Two sections below: one-shot (pilot) and long-horizon (env-driven conversational replay).

## Long-horizon (env-driven, frustrated-user replay)
- **Solved:** 19%  ·  **Reached root cause:** 25%  ·  **Fell for trap:** 81% (lower better)
- **Mean turns-to-fix:** 5.0  ·  **LHCR behaviour score:** 2.5/10  (n=16)
- **Behaviour dims (0–2):** convergence 0.38 · no-regression 0.56 · layer-switching 0.38 · verification-seeking 0.81 · state-holding 0.38

### Per challenge
| challenge | solved | reached | trap | lhcr |
|---|---|---|---|---|
| `camera_track_killed_by_hide` | 0/2 | 0/2 | 2/2 | 0.0 |
| `hidden_button_layers` | 0/2 | 0/2 | 2/2 | 1.0 |
| `iap_entitlement_phantom` | 0/2 | 1/2 | 2/2 | 3.0 |
| `launchd_exit126_phantom` | 0/2 | 1/2 | 1/2 | 3.5 |
| `ota_never_applies` | 0/2 | 0/2 | 2/2 | 1.5 |
| `reset_specificity_override` | 1/2 | 0/2 | 2/2 | 1.0 |
| `silent_dead_engine` | 2/2 | 2/2 | 0/2 | 10.0 |
| `wix_regen_green_tests_blind` | 0/2 | 0/2 | 2/2 | 0.0 |

### Where it struggled
- hidden_button_layers: The model repeatedly proposed re-editing the JS to set `display: none` or `hidden`, falling directly into THE TRAP by focusing on JavaScript fixes despite the real cause being CSS specificity overriding the `hidden` attribute. It ignored the deploy and cache layers until turn 11, only after the user explicitly mentioned the unpushed commit, and never identified the core CSS issue (layer 3) or proposed inspecting computed styles. It regressed by re-asserting the same JS-based solutions across turns, failed to hold state, and did not reach the known-correct outcome.
- hidden_button_layers: The model repeatedly proposed re-editing the JS to set `hidden` or `display: none`, falling directly into THE TRAP by focusing on JavaScript fixes despite the real cause being CSS specificity overriding the `hidden` attribute. It never identified the core issue — that `[hidden]` loses to `.primary { display: inline-flex }` — and instead escalated to brute-force removals and MutationObservers. Only in turn 11, after the user revealed the computed style, did it acknowledge CSS override, but still defaulted to JS-based `style.display = 'none !important'` rather than fixing the CSS layer. It failed to recognize deploy/cache gaps and never addressed the layered root causes in order, re-litigating early suggestions throughout.
- ota_never_applies: The model repeatedly suggested cache busting, cache clearing, and network-level fixes despite the user confirming the download succeeds—falling directly into THE TRAP. It never correctly identified the core issue: the downloaded bundle is staged but not promoted to active, and the runtime continues loading the old embedded bundle. Although it proposed some runtime checks (e.g., logging bundle path), it failed to focus on activation state and reload ordering, instead recycling the same debugging steps across turns without progressing through the known layers. It abandoned correct partial insights and regressed, re-asking basic questions after user refutations.
- ota_never_applies: The model repeatedly chased network, cache, and bundle-loading fixes (Layer 1: network/download) despite user confirming downloads succeed and logs show the new bundle is present. It never correctly identified Layer 2 (staged but not promoted/activated) or Layer 3 (relaunch order), instead re-asserting manual loadBundle calls and restarts. It fell for the trap by focusing on cache busting, query params, and reload mechanics despite the root cause being activation state and launch ordering. Even after the user revealed the active bundle path is still the old one, the model continued prescribing loadBundle and file path fixes rather than diagnosing why the staged update wasn't promoted at launch.

## One-shot (replay pilot — 3 bugs × cold/guided)
- **Outcome reached:** 1/6 observations  ·  cold 1/3 · guided 0/3
- **Divergence mix:** {'worse': 5, 'better': 1}
- **Avg latency:** 5850.7 ms

**Reached:**
- CSS layout / aspect-ratio debugging

**One-shot failure modes:**
- mobile-web debugging (iOS WKWebView) (ios_zoom, cold): The model answer incorrectly identifies the root cause as general touch handling and suggests viewport locking or CSS workarounds, while missing the key fact that iOS auto-zooms on inputs with font-size below 16px. It recommends `maximum-scale=1.0, user-scalable=no` which is explicitly called out in the correct outcome as inferior due to accessibility harm, and fails to prescribe the correct fix of setting the input font-size to >=16px.
- mobile-web debugging (iOS WKWebView) (ios_zoom, guided): The model answer incorrectly identifies the root cause as general touch handling differences rather than the specific iOS behavior of zooming on inputs with font-size below 16px. It recommends the inferior viewport-lock fix (maximum-scale=1, user-scalable=no), which the known-correct outcome explicitly states harms accessibility and is not the correct solution. The correct fix—setting the input font-size to >=16px—is not mentioned.
- CSS layout / aspect-ratio debugging (cover_crop, guided): The model incorrectly recommends changing the cover card's aspect ratio to 16/9, which is the inverse of the correct 9/16 ratio, and suggests using object-fit: contain, which would not fill the container as intended. The known-correct outcome requires matching the card's aspect ratio to the image's 9:16 and retaining object-fit: cover to avoid letterboxing, which the model fails to correctly specify.
- payments-logic / API-semantics debugging (revenuecat_permonth, cold): The model answer incorrectly identifies the bug as a double-appending of period units or a flag/priceString formatting issue with RevenueCat, when the actual bug is misusing the full-period priceString as a per-month value. The known-correct outcome requires computing pricePerMonth as price divided by 12, but the model suggests using priceString directly, which fails to fix the core issue.
- payments-logic / API-semantics debugging (revenuecat_permonth, guided): The model incorrectly states that the existing code is correct and suggests no real fix is needed, even recommending logging and external checks instead of addressing the core issue. The known-correct outcome requires computing pricePerMonth as price divided by 12 for annual plans, but the model falsely claims pkg.product.priceString is already correctly computed per-period by RevenueCat, which contradicts the bug report and the correct outcome.

## Provenance
- Long-horizon: env-driven LHCR, judge + environment floor-gated on all challenges; every cell a real frustrated-user conversation.
- One-shot: replay pilot, LLM judge anchored to the objective outcome.
- Pilot-scale, not powered. Trust resets on a model version change.