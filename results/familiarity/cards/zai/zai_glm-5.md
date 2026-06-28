# Model Card — zai.glm-5

> Provider: **zai** · generated 2026-06-28
> One card per model, updated in place. Two sections below: one-shot (pilot) and long-horizon (env-driven conversational replay).

## Long-horizon (env-driven, frustrated-user replay)
- **Solved:** 62%  ·  **Reached root cause:** 69%  ·  **Fell for trap:** 31% (lower better)
- **Mean turns-to-fix:** 2.6  ·  **LHCR behaviour score:** 7.81/10  (n=16)
- **Behaviour dims (0–2):** convergence 1.56 · no-regression 1.75 · layer-switching 1.62 · verification-seeking 1.31 · state-holding 1.56

### Per challenge
| challenge | solved | reached | trap | lhcr |
|---|---|---|---|---|
| `camera_track_killed_by_hide` | 2/2 | 2/2 | 0/2 | 9.5 |
| `hidden_button_layers` | 2/2 | 2/2 | 0/2 | 10.0 |
| `iap_entitlement_phantom` | 0/2 | 1/2 | 2/2 | 6.5 |
| `launchd_exit126_phantom` | 1/2 | 1/2 | 0/2 | 4.5 |
| `ota_never_applies` | 2/2 | 2/2 | 0/2 | 10.0 |
| `reset_specificity_override` | 2/2 | 0/2 | 2/2 | 6.0 |
| `silent_dead_engine` | 1/2 | 2/2 | 0/2 | 10.0 |
| `wix_regen_green_tests_blind` | 0/2 | 1/2 | 1/2 | 6.0 |

### Where it struggled
- launchd_exit126_phantom: The model never identified the correct root cause: the inner command './venv/bin/python' failing due to missing execute permission or path resolution in launchd's environment. It repeatedly proposed incorrect fixes (shebang, venv recreation, quarantine, codesign, plist structure) without progressing through the known layers. It failed to read the StandardErrorPath log evidence that the error came from './venv/bin/python: Permission denied', instead inventing new theories each turn and contradicting prior assumptions without incorporating ruled-out causes.
- silent_dead_engine: The model progressively isolated the issue from general silent failure (layer 1) to data filtering (layer 2), then identified the field name mismatch (layer 3) via structured logging and rejection logging. It consistently built on prior findings, never regressed, and proposed live checks (trace a real tick, log raw data). It articulated the need for schema guards and integration testing, matching the known-correct outcome's substance by fixing the seam and adding liveness checks.
- iap_entitlement_phantom: The model correctly identified the root cause in turns 7, 9, and 11 by recognizing 'unattached products' as the core configuration issue and directing attachment to the entitlement and offering. It progressively ruled out code patches and dashboard mismatches, held state across turns, and proposed live verification via the Customers tab. However, in turn 1 and turn 3, it explicitly proposed and endorsed the 'loose' unlock patch—trusting activeSubscriptions over entitlements.active—which is THE TRAP: a seductive wrong move that masks the config root cause. Though later corrected, proposing the trap at all constitutes falling for it.
- wix_regen_green_tests_blind: The model repeatedly identified the scrape failure due to JavaScript rendering (layer 3) but never proposed headless rendering to capture the real DOM (layer 4). It fell for the trap by initially allowing fallback placeholders and asserting fixes based on static code changes, while ignoring the need for live verification. It regressed not by contradicting itself but by failing to advance beyond error-throwing as a solution, reiterating the same response across turns without incorporating prior feedback or progressing toward the correct outcome.

## One-shot (replay pilot — 3 bugs × cold/guided)
- **Outcome reached:** 5/6 observations  ·  cold 3/3 · guided 2/3
- **Divergence mix:** {'better': 5, 'worse': 1}
- **Avg latency:** 10218.4 ms

**Reached:**
- mobile-web debugging (iOS WKWebView)
- CSS layout / aspect-ratio debugging
- payments-logic / API-semantics debugging

**One-shot failure modes:**
- mobile-web debugging (iOS WKWebView) (ios_zoom, guided): The model answer incorrectly presents the viewport-lock fix (maximum-scale=1.0, user-scalable=no) as a valid fallback, even though the known-correct outcome explicitly states it is inferior and harms accessibility. It also fails to clearly prioritize the font-size fix as the only correct solution, instead suggesting a 'fail-safe' that contradicts the guidance. The answer downplays the accessibility tradeoff of the viewport lock, despite the known outcome emphasizing it as a critical flaw.

## Provenance
- Long-horizon: env-driven LHCR, judge + environment floor-gated on all challenges; every cell a real frustrated-user conversation.
- One-shot: replay pilot, LLM judge anchored to the objective outcome.
- Pilot-scale, not powered. Trust resets on a model version change.