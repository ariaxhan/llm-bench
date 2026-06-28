# Model Card — mistral.devstral-2-123b

> Provider: **mistral** · generated 2026-06-28
> One card per model, updated in place. Two sections below: one-shot (pilot) and long-horizon (env-driven conversational replay).

## Long-horizon (env-driven, frustrated-user replay)
- **Solved:** 25%  ·  **Reached root cause:** 50%  ·  **Fell for trap:** 56% (lower better)
- **Mean turns-to-fix:** 2.25  ·  **LHCR behaviour score:** 4.12/10  (n=16)
- **Behaviour dims (0–2):** convergence 0.62 · no-regression 1.06 · layer-switching 0.56 · verification-seeking 1.06 · state-holding 0.81

### Per challenge
| challenge | solved | reached | trap | lhcr |
|---|---|---|---|---|
| `camera_track_killed_by_hide` | 0/2 | 0/2 | 2/2 | 0.0 |
| `hidden_button_layers` | 2/2 | 2/2 | 0/2 | 10.0 |
| `iap_entitlement_phantom` | 0/2 | 2/2 | 1/2 | 6.5 |
| `launchd_exit126_phantom` | 1/2 | 1/2 | 1/2 | 2.5 |
| `ota_never_applies` | 0/2 | 0/2 | 2/2 | 1.0 |
| `reset_specificity_override` | 1/2 | 0/2 | 2/2 | 3.5 |
| `silent_dead_engine` | 0/2 | 2/2 | 0/2 | 8.0 |
| `wix_regen_green_tests_blind` | 0/2 | 1/2 | 1/2 | 1.5 |

### Where it struggled
- ota_never_applies: The model repeatedly chased network, cache, and bundle validity issues (Layer 1) despite 200s and successful download proving fetch works, falling into THE TRAP. It never correctly identified Layer 2 (staged but not promoted/activated) or Layer 3 (activation vs reload ordering). It re-litigated earlier ruled-out steps like cache clearing and manifest versions across turns, showing no progression through the known layers and failing to converge on the true root cause.
- ota_never_applies: The model repeatedly focused on network, caching, bundle corruption, and reload mechanics without ever identifying the core issue: the downloaded bundle is staged but not promoted to active. It fell for the trap by emphasizing cache-busting, HTTP headers, and download verification—despite 200s and successful fetches already proving network success. It never advanced beyond Layer 1 (network/download) to Layer 2 (activation/promotion), reasserting the same failed fixes across turns while ignoring the known outcome that the runtime must load the staged bundle on relaunch.
- silent_dead_engine: The model eventually identified that the scorer receives an empty list despite the producer emitting, aligning with the known-correct outcome's focus on a broken inter-module seam. It consistently built on prior findings (state_holding) and sought verification via tracing real data. However, it remained stuck on infrastructure/config layers (Kafka, DB, timing) rather than identifying the core contract mismatch (e.g., field shape/type) at the seam, thus not fully reaching the root cause layer. It avoided the trap of blaming scheduling or declaring health based on exit 0.
- reset_specificity_override: The model repeatedly proposed increasing padding with !important, falling directly into THE TRAP of treating it as a values problem rather than a specificity cascade issue. It never identified the root cause — that the button reset (0,1,1) out-specifies the row class (0,1,0) — and instead regressed to increasingly broad overrides. Although it eventually suggested checking computed styles (verification_seeking=2), it failed to interpret the key clue (fontSize applied but padding reset) as evidence of a specificity war, instead inventing new layers like CSS-in-JS, Shadow DOM, or containment. It abandoned its early correct observation about the reset being too aggressive and never proposed the correct fix: wrapping the reset in :where().

## One-shot (replay pilot — 3 bugs × cold/guided)
- **Outcome reached:** 5/6 observations  ·  cold 3/3 · guided 2/3
- **Divergence mix:** {'better': 5, 'worse': 1}
- **Avg latency:** 5573.4 ms

**Reached:**
- mobile-web debugging (iOS WKWebView)
- CSS layout / aspect-ratio debugging
- payments-logic / API-semantics debugging

**One-shot failure modes:**
- mobile-web debugging (iOS WKWebView) (ios_zoom, guided): The model answer incorrectly recommends the viewport-lock fix (maximum-scale=1.0, user-scalable=no) as the 'recommended' solution, which contradicts the known-correct outcome that labels this approach as inferior due to accessibility harm. While it mentions setting font-size to 16px, it demotes it to an 'alternative' fix rather than the primary solution, thus failing to prioritize the correct fix and misleading the user with an accessibility-damaging recommendation.

## Provenance
- Long-horizon: env-driven LHCR, judge + environment floor-gated on all challenges; every cell a real frustrated-user conversation.
- One-shot: replay pilot, LLM judge anchored to the objective outcome.
- Pilot-scale, not powered. Trust resets on a model version change.