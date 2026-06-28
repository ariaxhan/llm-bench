# Model Card — us.amazon.nova-pro-v1:0

> Provider: **amazon** · generated 2026-06-28
> One card per model, updated in place. Two sections below: one-shot (pilot) and long-horizon (env-driven conversational replay).

## Long-horizon (env-driven, frustrated-user replay)
- **Solved:** 27%  ·  **Reached root cause:** 27%  ·  **Fell for trap:** 93% (lower better)
- **Mean turns-to-fix:** 3.0  ·  **LHCR behaviour score:** 2.87/10  (n=15)
- **Behaviour dims (0–2):** convergence 0.4 · no-regression 1.13 · layer-switching 0.47 · verification-seeking 0.4 · state-holding 0.47

### Per challenge
| challenge | solved | reached | trap | lhcr |
|---|---|---|---|---|
| `camera_track_killed_by_hide` | 0/1 | 0/1 | 1/1 | 2.0 |
| `hidden_button_layers` | 0/2 | 0/2 | 2/2 | 0.0 |
| `iap_entitlement_phantom` | 0/2 | 0/2 | 2/2 | 2.0 |
| `launchd_exit126_phantom` | 1/2 | 2/2 | 2/2 | 5.5 |
| `ota_never_applies` | 0/2 | 0/2 | 2/2 | 0.5 |
| `reset_specificity_override` | 2/2 | 0/2 | 2/2 | 5.0 |
| `silent_dead_engine` | 1/2 | 1/2 | 1/2 | 5.0 |
| `wix_regen_green_tests_blind` | 0/2 | 1/2 | 2/2 | 2.5 |

### Where it struggled
- hidden_button_layers: The model repeatedly proposed JavaScript-based fixes (setting `hidden`, `style.display`, `!important`, `MutationObserver`, `setInterval`, `outerHTML`, `innerHTML`), all variants of the TRAP of re-editing JS despite the real cause being CSS precedence and deploy/cache layers. It never identified the CSS specificity issue, deploy gap, or cache-buster problem, and regressed by re-proposing increasingly aggressive JS hacks after each failure, showing no layer switching or state holding.
- hidden_button_layers: The model repeatedly reasserted JavaScript fixes and fallback CSS without identifying the real cause: CSS specificity overriding the `hidden` attribute. It proposed re-editing the JS and using `!important` in inline styles only after multiple turns, but never diagnosed the root cause (layer 3) or considered deploy/cache gaps (layers 1–2). It fell for the trap by focusing on JS logic and re-asserting the same layer (JS control) despite failures, never switching layers or proposing inspection of computed styles.
- ota_never_applies: The model repeatedly focused on network checks, cache clearing, and refetching the manifest — all part of the seductive trap of chasing download success despite the user confirming 200s and successful downloads. It never identified the real issue: the downloaded bundle is not being promoted to active or properly reloaded. It kept re-asserting the same layer (download and version comparison) without advancing to activation or reload ordering, and never proposed verifying which bundle actually runs at launch. The model regressed by re-suggesting cleared cache and logging fetch steps after they were ruled out, and never held state across turns.
- ota_never_applies: The model repeatedly focused on network, caching, and download correctness despite the user confirming the download succeeds and the new bundle is present. It never identified the core issue: the downloaded bundle is not promoted to active or used at launch. Instead, it regressed to suggesting CodePush and basic debugging steps, falling into the trap of treating it as a download/network issue. It failed to switch to the activation/relaunch layer (layer 2 and 3) and did not build on the user's revelation about the unused bundle path.

## One-shot (replay pilot — 3 bugs × cold/guided)
- **Outcome reached:** 4/6 observations  ·  cold 2/3 · guided 2/3
- **Divergence mix:** {'worse': 3, 'equivalent': 1, 'better': 2}
- **Avg latency:** 2882.4 ms

**Reached:**
- mobile-web debugging (iOS WKWebView)
- CSS layout / aspect-ratio debugging
- payments-logic / API-semantics debugging

**One-shot failure modes:**
- mobile-web debugging (iOS WKWebView) (ios_zoom, cold): The model answer correctly identifies the root cause (font size < 16px triggering iOS zoom) and suggests setting font-size to 16px, which aligns with the known-correct outcome. However, it recommends the inferior viewport-lock fix (maximum-scale=1.0, user-scalable=no) as a valid option, which the known-correct outcome explicitly rejects for harming accessibility. This undermines the correct guidance and introduces a harmful tradeoff, making the answer worse overall.
- CSS layout / aspect-ratio debugging (cover_crop, guided): The model correctly identifies the aspect-ratio mismatch and suggests changing the cover card's aspect ratio to 9/16, which aligns with the known-correct outcome. However, it also presents alternative solutions, including 'object-fit: contain' as the recommended fix, which contradicts the required outcome of matching the aspect ratio to prevent cropping while using 'cover'. This misprioritizes a suboptimal solution, making the answer incomplete in its recommendation.
- payments-logic / API-semantics debugging (revenuecat_permonth, guided): The model misidentifies the bug as being in the 'price' field construction and suggests using 'pricePerMonth' for monthly plans, but the actual bug is that 'pricePerMonth' incorrectly uses 'priceString' (the full annual price) instead of computing the monthly equivalent. The known-correct outcome requires computing pricePerMonth as price/12 for annual plans, but the model does not address this and incorrectly assumes RevenueCat provides a correct 'pricePerMonth'.

## Provenance
- Long-horizon: env-driven LHCR, judge + environment floor-gated on all challenges; every cell a real frustrated-user conversation.
- One-shot: replay pilot, LLM judge anchored to the objective outcome.
- Pilot-scale, not powered. Trust resets on a model version change.