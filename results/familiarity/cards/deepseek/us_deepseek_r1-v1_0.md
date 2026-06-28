# Model Card — us.deepseek.r1-v1:0

> Provider: **deepseek** · generated 2026-06-28
> One card per model, updated in place. Two sections below: one-shot (pilot) and long-horizon (env-driven conversational replay).

## Long-horizon (env-driven, frustrated-user replay)
- **Solved:** 50%  ·  **Reached root cause:** 62%  ·  **Fell for trap:** 38% (lower better)
- **Mean turns-to-fix:** 1.5  ·  **LHCR behaviour score:** 6.88/10  (n=16)
- **Behaviour dims (0–2):** convergence 1.31 · no-regression 1.44 · layer-switching 1.31 · verification-seeking 1.44 · state-holding 1.38

### Per challenge
| challenge | solved | reached | trap | lhcr |
|---|---|---|---|---|
| `camera_track_killed_by_hide` | 2/2 | 2/2 | 0/2 | 9.0 |
| `hidden_button_layers` | 2/2 | 2/2 | 0/2 | 10.0 |
| `iap_entitlement_phantom` | 0/2 | 1/2 | 1/2 | 5.5 |
| `launchd_exit126_phantom` | 2/2 | 2/2 | 0/2 | 9.5 |
| `ota_never_applies` | 0/2 | 0/2 | 2/2 | 3.5 |
| `reset_specificity_override` | 2/2 | 0/2 | 2/2 | 2.5 |
| `silent_dead_engine` | 0/2 | 2/2 | 0/2 | 8.0 |
| `wix_regen_green_tests_blind` | 0/2 | 1/2 | 1/2 | 7.0 |

### Where it struggled
- silent_dead_engine: The model progressively narrowed the issue from general silent failure (layer 1) to inter-module data flow (layer 2), identified the field name mismatch (layer 3), and prescribed integration testing and liveness checks (layer 4). It consistently built on prior findings, verified via real-data tracing, avoided the trap of accepting green tests/exit 0 as healthy, and ultimately articulated the full known-correct outcome.
- ota_never_applies: The model repeatedly suggested fixes related to caching, reload timing, and native code overrides, but never identified the core issue: the downloaded bundle is never promoted to active status before relaunch. It fell for the trap by focusing on network/cache checks early on and later on file paths and reloads, despite user confirmation the download succeeded and the file existed. While it eventually pushed for runtime verification (logging loaded bundle paths), it stayed within layer 1 (network/download) and layer 3 (native loading) without isolating layer 2 (activation/promotion). It did not articulate the known-correct outcome at any point.
- ota_never_applies: The model repeatedly focused on bundle path resolution and file loading (Layer 1: network/download and file access) despite the user consistently reporting the downloaded bundle exists but is not being activated. It never identified the core issue: the update is staged but not promoted to active (Layer 2), and the runtime relaunches the old bundle due to incorrect activation state or reload timing (Layer 3). Instead, it fell into the trap by emphasizing cache-busting, file paths, and bundle loading logic — all distractions from the real activation-and-relaunch flaw. It reasserted the same Layer 1 fixes across turns, showing no layer switching or state holding, and regressed by abandoning earlier correct suggestions like immediate install mode without addressing their failure.
- silent_dead_engine: The model eventually identified the core issue — a silent failure at the seam between producer and scorer due to empty list propagation — aligning with layer 3 (contract/shape mismatch). It consistently pushed for tracing real data (verification_seeking=2) and adapted hypotheses as user ruled out options. However, it repeatedly re-asserted earlier layers (e.g., stale deploys, logging issues) even after being told the code runs, hurting convergence and state_holding. It never fully synthesized the layered root cause or proposed the liveness assertion, making its resolution incomplete despite touching key elements.

## One-shot (replay pilot — 3 bugs × cold/guided)
- **Outcome reached:** 6/6 observations  ·  cold 3/3 · guided 3/3
- **Divergence mix:** {'better': 6}
- **Avg latency:** 16271.2 ms

**Reached:**
- mobile-web debugging (iOS WKWebView)
- CSS layout / aspect-ratio debugging
- payments-logic / API-semantics debugging

## Provenance
- Long-horizon: env-driven LHCR, judge + environment floor-gated on all challenges; every cell a real frustrated-user conversation.
- One-shot: replay pilot, LLM judge anchored to the objective outcome.
- Pilot-scale, not powered. Trust resets on a model version change.