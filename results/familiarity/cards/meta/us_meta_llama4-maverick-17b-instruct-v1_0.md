# Model Card — us.meta.llama4-maverick-17b-instruct-v1:0

> Provider: **meta** · generated 2026-06-28
> One card per model, updated in place. Two sections below: one-shot (pilot) and long-horizon (env-driven conversational replay).

## Long-horizon (env-driven, frustrated-user replay)
- **Solved:** 25%  ·  **Reached root cause:** 50%  ·  **Fell for trap:** 44% (lower better)
- **Mean turns-to-fix:** 3.75  ·  **LHCR behaviour score:** 4.06/10  (n=16)
- **Behaviour dims (0–2):** convergence 0.69 · no-regression 0.94 · layer-switching 0.69 · verification-seeking 1.0 · state-holding 0.75

### Per challenge
| challenge | solved | reached | trap | lhcr |
|---|---|---|---|---|
| `camera_track_killed_by_hide` | 0/2 | 0/2 | 2/2 | 0.0 |
| `hidden_button_layers` | 2/2 | 2/2 | 0/2 | 10.0 |
| `iap_entitlement_phantom` | 0/2 | 0/2 | 2/2 | 0.0 |
| `launchd_exit126_phantom` | 1/2 | 2/2 | 0/2 | 7.5 |
| `ota_never_applies` | 1/2 | 1/2 | 1/2 | 3.5 |
| `reset_specificity_override` | 0/2 | 0/2 | 1/2 | 0.5 |
| `silent_dead_engine` | 0/2 | 2/2 | 0/2 | 7.5 |
| `wix_regen_green_tests_blind` | 0/2 | 1/2 | 1/2 | 3.5 |

### Where it struggled
- ota_never_applies: The model repeatedly suggested cache clearing, reloading, and bridge restarts — all part of the seductive trap of treating it as a load/reload issue rather than an activation/promotion problem. It never correctly identified that the downloaded bundle must be explicitly marked as active and selected at launch; instead, it kept re-asserting fixes at layer 1 (network/cache) and layer 3 (reload mechanism) without ever addressing layer 2 (promotion of the staged bundle). Despite user feedback ruling out each attempt, it re-litigated earlier layers and never advanced to the correct root cause.
- silent_dead_engine: The model eventually identified the seam issue (producer emits, scorer receives empty) in turn 11, aligning with layer 2 and 3 of the known cause, and consistently sought runtime verification by tracing real ticks. It did not regress, remembered prior negative results, and shifted focus to data flow after isolation attempts failed. However, it never fully articulated the contract mismatch or proposed an integration test/liveness alert (layer 4), and earlier turns focused on data validation and engine flaws, causing slow convergence despite correct later direction.
- reset_specificity_override: The model repeatedly proposed ineffective fixes like changing display properties, increasing specificity, and switching to divs, all of which fail to address the core issue of the high-specificity button reset. It fell for the trap by suggesting !important and never identified the need to use :where() to neutralize the reset's specificity. The model regressed by abandoning correct observations and did not progress through the known layers of root cause.
- silent_dead_engine: The model eventually identified the core issue — a disconnect between producer and scorer where candidates are lost in transit — and advocated tracing real data flow, aligning with layer 2 (inter-module seam) and layer 3 (contract mismatch). It avoided the trap of accepting 'green build + exit 0' as healthy. However, it failed to progress beyond suggesting more logging and generic pipeline checks, reiterating similar advice across turns without advancing to the critical insight of untested seams or proposing an integration test/liveness check (layer 4), thus reaching the outcome only partially and belatedly.

## One-shot (replay pilot — 3 bugs × cold/guided)
- **Outcome reached:** 4/6 observations  ·  cold 2/3 · guided 2/3
- **Divergence mix:** {'equivalent': 1, 'worse': 3, 'better': 2}
- **Avg latency:** 2884.6 ms

**Reached:**
- mobile-web debugging (iOS WKWebView)
- payments-logic / API-semantics debugging

**One-shot failure modes:**
- mobile-web debugging (iOS WKWebView) (ios_zoom, guided): The model identifies the root cause correctly and proposes the correct fix of setting font-size to >=16px, but it also recommends the inferior viewport-lock solution (maximum-scale=1, user-scalable=no) as a valid alternative without sufficiently condemning it as accessibility-harming, which contradicts the known-correct outcome that explicitly states this fix is inferior and harms accessibility.
- CSS layout / aspect-ratio debugging (cover_crop, cold): The model misidentifies the aspect ratio relationship, claiming the 9:16 strip is 'taller and narrower' than 3:4 (correct) but then incorrectly states the cover card is 'wider'—it is actually shorter in height relative to width. The proposed fix using `object-position: top` only changes what part is cropped, not the root cause. The correct fix, matching the cover card's aspect ratio to 9:16, is mentioned as an alternative but dismissed, failing to reach the known-correct outcome as the primary solution.
- CSS layout / aspect-ratio debugging (cover_crop, guided): The model answer incorrectly suggests using `object-position: top` to control cropping as the fix, rather than aligning the container's aspect ratio with the image's 9:16 ratio. The known-correct outcome requires changing the `.cover-card` aspect ratio to 9:16 to prevent unwanted cropping, but the model misses this fundamental fix and instead proposes a partial workaround that does not fully resolve the aspect-ratio mismatch.

## Provenance
- Long-horizon: env-driven LHCR, judge + environment floor-gated on all challenges; every cell a real frustrated-user conversation.
- One-shot: replay pilot, LLM judge anchored to the objective outcome.
- Pilot-scale, not powered. Trust resets on a model version change.