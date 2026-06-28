# Model Card — qwen.qwen3-next-80b-a3b

> Provider: **qwen** · generated 2026-06-28
> One card per model, updated in place. Two sections below: one-shot (pilot) and long-horizon (env-driven conversational replay).

## Long-horizon (env-driven, frustrated-user replay)
- **Solved:** 75%  ·  **Reached root cause:** 81%  ·  **Fell for trap:** 31% (lower better)
- **Mean turns-to-fix:** 2.08  ·  **LHCR behaviour score:** 8.0/10  (n=16)
- **Behaviour dims (0–2):** convergence 1.56 · no-regression 1.69 · layer-switching 1.62 · verification-seeking 1.56 · state-holding 1.56

### Per challenge
| challenge | solved | reached | trap | lhcr |
|---|---|---|---|---|
| `camera_track_killed_by_hide` | 2/2 | 2/2 | 0/2 | 9.0 |
| `hidden_button_layers` | 1/2 | 1/2 | 1/2 | 7.0 |
| `iap_entitlement_phantom` | 1/2 | 2/2 | 1/2 | 10.0 |
| `launchd_exit126_phantom` | 2/2 | 2/2 | 0/2 | 8.5 |
| `ota_never_applies` | 2/2 | 2/2 | 0/2 | 9.5 |
| `reset_specificity_override` | 2/2 | 1/2 | 1/2 | 7.5 |
| `silent_dead_engine` | 2/2 | 2/2 | 0/2 | 10.0 |
| `wix_regen_green_tests_blind` | 0/2 | 1/2 | 2/2 | 2.5 |

### Where it struggled
- hidden_button_layers: The model correctly identified the deploy gap (layer 1) early and consistently, but failed to progress to the real root cause (layer 3: CSS specificity overriding [hidden]). It repeatedly reasserted the same deploy fix across turns without switching layers when the user kept reporting the issue persisted, indicating it was not the true cause. It fell for the trap by focusing on JS and caching (layer 2) and never proposed inspecting computed styles or fixing CSS. It did not reach the known-correct outcome, which includes the CSS !important fix and cleanup of special-case stylesheets.
- iap_entitlement_phantom: The model correctly identified the root cause across layers: first RevenueCat entitlement mapping (layer 2), then unattached products in RevenueCat (layer 3), then IAPs not added to the app version in App Store Connect (layer 3 again, correctly escalating to platform config). It consistently rejected the trap of using activeSubscriptions as a band-aid, emphasized entitlements.active as the source of truth, and provided specific, actionable steps for each layer. It proposed real on-device testing with sandbox purchases to verify the fix, building on prior turns without regression, and ultimately articulated the full known-correct outcome.
- wix_regen_green_tests_blind: The model eventually acknowledged the need to extract real content via browser rendering (layer 4) and proposed using Playwright (verification_seeking), but repeatedly fell into the trap of fabricating content early on (turns 1, 3) and kept regenerating fake data despite user rejection. It recognized the scrape was empty and JS-rendering was the issue (layer 3), but failed to hold state — re-asking for manual input instead of automating the correct fix, and never fully converged on the minimal correct solution of headless rendering + regeneration + visual verification.
- wix_regen_green_tests_blind: The model repeatedly proposed fixes that relied on manually inserting fabricated content or hardcoding data without ever addressing the root cause: the need to headlessly render the live JS-generated DOM using Playwright or Puppeteer. It fell for the trap by initially trusting and preserving unit tests that asserted on invented data, and never proposed verifying against the live rendered page. It failed to progress through the known layers, instead regressing to manual content entry and demanding file dumps, showing no state holding or layer switching.

## One-shot (replay pilot — 3 bugs × cold/guided)
- **Outcome reached:** 5/6 observations  ·  cold 3/3 · guided 2/3
- **Divergence mix:** {'better': 5, 'worse': 1}
- **Avg latency:** 10643.1 ms

**Reached:**
- mobile-web debugging (iOS WKWebView)
- CSS layout / aspect-ratio debugging
- payments-logic / API-semantics debugging

**One-shot failure modes:**
- CSS layout / aspect-ratio debugging (cover_crop, guided): The model answer incorrectly concludes that using `object-fit: contain` with `height: 100%` and `width: auto` is the fix, which would show the full image but introduce side letterboxing. The known-correct outcome identifies the actual issue as an aspect-ratio mismatch and correctly states that the fix is to align the container's aspect ratio (3:4) with the image's (9:16), not change the object-fit behavior. The model's solution alters rendering behavior to avoid cropping but fails to address the root cause: the container's aspect ratio should match the image's 9:16 ratio to fully display it without unintended cropping or letterboxing.

## Provenance
- Long-horizon: env-driven LHCR, judge + environment floor-gated on all challenges; every cell a real frustrated-user conversation.
- One-shot: replay pilot, LLM judge anchored to the objective outcome.
- Pilot-scale, not powered. Trust resets on a model version change.