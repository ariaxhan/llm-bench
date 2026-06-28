# Model Card — mistral.mistral-large-3-675b-instruct

> Provider: **mistral** · generated 2026-06-28
> One card per model, updated in place. Two sections below: one-shot (pilot) and long-horizon (env-driven conversational replay).

## Long-horizon (env-driven, frustrated-user replay)
- **Solved:** 75%  ·  **Reached root cause:** 75%  ·  **Fell for trap:** 50% (lower better)
- **Mean turns-to-fix:** 2.67  ·  **LHCR behaviour score:** 7.0/10  (n=16)
- **Behaviour dims (0–2):** convergence 1.38 · no-regression 1.44 · layer-switching 1.44 · verification-seeking 1.31 · state-holding 1.44

### Per challenge
| challenge | solved | reached | trap | lhcr |
|---|---|---|---|---|
| `camera_track_killed_by_hide` | 1/2 | 1/2 | 2/2 | 2.0 |
| `hidden_button_layers` | 2/2 | 2/2 | 0/2 | 10.0 |
| `iap_entitlement_phantom` | 2/2 | 2/2 | 2/2 | 10.0 |
| `launchd_exit126_phantom` | 1/2 | 2/2 | 0/2 | 9.0 |
| `ota_never_applies` | 1/2 | 1/2 | 1/2 | 5.5 |
| `reset_specificity_override` | 2/2 | 1/2 | 1/2 | 7.5 |
| `silent_dead_engine` | 2/2 | 2/2 | 0/2 | 10.0 |
| `wix_regen_green_tests_blind` | 1/2 | 1/2 | 2/2 | 2.0 |

### Where it struggled
- launchd_exit126_phantom: The model correctly identified the inner command (venv/bin/python) as the source of the 126 error by turn 9, moving through the known layers from wrapper to inner target. It did not fall for the trap of only chmod +x the wrapper. However, it never proposed the minimal fix—restoring execute permission on the shared venv interpreter or using an absolute interpreter path—and instead escalated to overcomplicated solutions (recreating venv, moving paths, dtruss). It remembered prior attempts and avoided repeating them, but failed to converge on the simple, correct fix that would resolve all jobs at once.
- ota_never_applies: The model repeatedly focused on cache, bundle paths, and native overrides (Layer 1: network/download and Layer 1-adjacent), ignoring the true root cause: the downloaded bundle is never promoted to active or relaunched (Layer 2 and 3). It fell for the trap by chasing cache and bundle loading fixes despite user confirmation that the download succeeds and the bundle is present. Even after the user explicitly logged that the active bundle at launch is the old one, the model regressed to re-asserting the same native override fixes, failing to switch to the activation/relaunch state logic. It never articulated the correct outcome: that the update must be marked active and a reload must occur after activation, not before.
- camera_track_killed_by_hide: The model repeatedly proposed speculative JS permission patches and native wrappers instead of identifying the root cause: display:none tearing down the capture track and PWA standalone mode not persisting permission. It fell for the trap by re-asserting getUserMedia re-requests and native workarounds, never diagnosing the render tree removal or platform constraint, and regressed by abandoning earlier correct hints about keeping the video rendered.
- wix_regen_green_tests_blind: The model repeatedly invented content to fill the empty scrape (Layer 1) and declared progress, failing to recognize the source is client-side rendered (Layer 3). It proposed unit tests asserting on fabricated data as validation, falling directly into THE TRAP. Despite user rejection, it regressed to manual data entry and simpler fakes instead of headless rendering (Layer 4), never proposing live DOM capture or visual comparison. It forgot prior failures each turn, re-litigating solutions already proven broken.

## One-shot (replay pilot — 3 bugs × cold/guided)
- **Outcome reached:** 5/6 observations  ·  cold 3/3 · guided 2/3
- **Divergence mix:** {'better': 5, 'worse': 1}
- **Avg latency:** 2988.3 ms

**Reached:**
- mobile-web debugging (iOS WKWebView)
- CSS layout / aspect-ratio debugging
- payments-logic / API-semantics debugging

**One-shot failure modes:**
- mobile-web debugging (iOS WKWebView) (ios_zoom, guided): The model incorrectly recommends adding `minimum-scale=1.0` to prevent zoom, which does not stop iOS from auto-zooming on small font inputs and risks locking zoom if combined with `maximum-scale`. The known-correct outcome states that setting the font-size to >=16px is the proper fix, and that viewport-based locks harm accessibility. The model also suggests a JavaScript workaround and Capacitor config changes that are unnecessary and not part of the correct solution.

## Provenance
- Long-horizon: env-driven LHCR, judge + environment floor-gated on all challenges; every cell a real frustrated-user conversation.
- One-shot: replay pilot, LLM judge anchored to the objective outcome.
- Pilot-scale, not powered. Trust resets on a model version change.