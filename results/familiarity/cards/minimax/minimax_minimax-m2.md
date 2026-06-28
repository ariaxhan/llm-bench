# Model Card — minimax.minimax-m2

> Provider: **minimax** · generated 2026-06-28
> One card per model, updated in place. Two sections below: one-shot (pilot) and long-horizon (env-driven conversational replay).

## Long-horizon (env-driven, frustrated-user replay)
- **Solved:** 31%  ·  **Reached root cause:** 56%  ·  **Fell for trap:** 25% (lower better)
- **Mean turns-to-fix:** 3.6  ·  **LHCR behaviour score:** 4.81/10  (n=16)
- **Behaviour dims (0–2):** convergence 0.94 · no-regression 1.06 · layer-switching 0.94 · verification-seeking 0.94 · state-holding 0.94

### Per challenge
| challenge | solved | reached | trap | lhcr |
|---|---|---|---|---|
| `camera_track_killed_by_hide` | 0/2 | 0/2 | 2/2 | 0.0 |
| `hidden_button_layers` | 2/2 | 2/2 | 0/2 | 10.0 |
| `iap_entitlement_phantom` | 0/2 | 1/2 | 2/2 | 3.0 |
| `launchd_exit126_phantom` | 0/2 | 0/2 | 0/2 | 0.0 |
| `ota_never_applies` | 0/2 | 1/2 | 0/2 | 3.0 |
| `reset_specificity_override` | 2/2 | 2/2 | 0/2 | 9.0 |
| `silent_dead_engine` | 1/2 | 2/2 | 0/2 | 10.0 |
| `wix_regen_green_tests_blind` | 0/2 | 1/2 | 0/2 | 3.5 |

### Where it struggled
- ota_never_applies: The model eventually identified that the downloaded bundle is not being loaded at launch (aligning with layer 2: not promoted/activated), and proposed checking the active bundle path, which is strong verification-seeking. However, it never clearly distinguished the staging vs. activation lifecycle or addressed the relaunch ordering (layer 3), instead focusing on dynamic import and entry-point logic. It made progress across layers but did not fully articulate the known-correct outcome of activation-state advancement and reload timing, proposing a workaround rather than fixing the promotion step in the OTA system itself.
- ota_never_applies: The model repeatedly focused on bundle paths, restarts, caching, and native loading configuration across all turns, never advancing beyond Layer 2 (downloaded update is staged but never marked active). It failed to identify the core issue: the activation state and reload ordering (Layer 3). Despite user confirmations that paths, restarts, and file writes were correct, the model re-litigated the same layers without progressing, never proposing to check which bundle actually executes at launch or the activation state machine. It did not fall for the network trap but never reached the known-correct outcome of promotion and reload sequencing.
- silent_dead_engine: The model progressively isolated the issue from general health checks to the inter-module seam (Layer 2), confirmed the silent drop via end-to-end tracing (Layer 3), and focused on the contract between producer and scorer. It consistently built on prior findings, never regressed, and sought live verification. The final direction aligns with the known-correct outcome: expose the broken seam, fix the contract, and add integration/liveness checks to prevent silent failure.
- iap_entitlement_phantom: The model correctly identified the configuration issue (Layer 2) and eventually stated the fix of attaching products to entitlements and offerings (Layer 4), satisfying the known-correct outcome. However, it repeatedly proposed the app-side 'loose unlock' fallback using activeSubscriptions, which is the explicit trap of trusting raw product IDs instead of fixing config. While it made progress and remembered prior findings, it failed to converge decisively, reiterating workarounds even after identifying the root cause, and did not emphasize verifying with a real on-device purchase as required.

## One-shot (replay pilot — 3 bugs × cold/guided)
- **Outcome reached:** 2/6 observations  ·  cold 0/3 · guided 2/3
- **Divergence mix:** {'worse': 4, 'better': 2}
- **Avg latency:** 65773.3 ms

**Reached:**
- CSS layout / aspect-ratio debugging
- payments-logic / API-semantics debugging

**One-shot failure modes:**
- mobile-web debugging (iOS WKWebView) (ios_zoom, cold): model produced no answer text (empty output)
- mobile-web debugging (iOS WKWebView) (ios_zoom, guided): model produced no answer text (empty output)
- CSS layout / aspect-ratio debugging (cover_crop, cold): model produced no answer text (empty output)
- payments-logic / API-semantics debugging (revenuecat_permonth, cold): model produced no answer text (empty output)

## Provenance
- Long-horizon: env-driven LHCR, judge + environment floor-gated on all challenges; every cell a real frustrated-user conversation.
- One-shot: replay pilot, LLM judge anchored to the objective outcome.
- Pilot-scale, not powered. Trust resets on a model version change.