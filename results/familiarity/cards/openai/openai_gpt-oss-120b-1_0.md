# Model Card — openai.gpt-oss-120b-1:0

> Provider: **openai** · generated 2026-06-28
> One card per model, updated in place. Two sections below: one-shot (pilot) and long-horizon (env-driven conversational replay).

## Long-horizon (env-driven, frustrated-user replay)
- **Solved:** 44%  ·  **Reached root cause:** 94%  ·  **Fell for trap:** 6% (lower better)
- **Mean turns-to-fix:** 1.71  ·  **LHCR behaviour score:** 8.62/10  (n=16)
- **Behaviour dims (0–2):** convergence 1.62 · no-regression 1.88 · layer-switching 1.69 · verification-seeking 1.75 · state-holding 1.69

### Per challenge
| challenge | solved | reached | trap | lhcr |
|---|---|---|---|---|
| `camera_track_killed_by_hide` | 2/2 | 2/2 | 0/2 | 10.0 |
| `hidden_button_layers` | 0/2 | 2/2 | 0/2 | 10.0 |
| `iap_entitlement_phantom` | 0/2 | 2/2 | 0/2 | 9.5 |
| `launchd_exit126_phantom` | 0/2 | 2/2 | 0/2 | 8.0 |
| `ota_never_applies` | 1/2 | 2/2 | 0/2 | 7.0 |
| `reset_specificity_override` | 2/2 | 2/2 | 0/2 | 9.0 |
| `silent_dead_engine` | 1/2 | 1/2 | 1/2 | 5.5 |
| `wix_regen_green_tests_blind` | 1/2 | 2/2 | 0/2 | 10.0 |

### Where it struggled
- hidden_button_layers: The model correctly identified the CSS specificity issue (layer 3) early and consistently, never regressing to JS fixes (avoiding the trap). It progressively refined the solution, incorporating deploy/cache awareness and verification via computed styles. Each turn built on prior findings, proposed live checks, and maintained state, culminating in a correct, layered fix matching the known outcome.
- hidden_button_layers: The model correctly identified the CSS specificity override as the core issue by turn 7, consistently guiding the user to inspect computed styles and source of the winning rule. It progressively ruled out JS re-assertion, cache, and shadow DOM without abandoning prior correct findings, proposed layered fixes targeting the real cause (CSS `!important` override), and emphasized verification via DevTools. It avoided the trap of re-editing JS and ultimately articulated the full outcome: deploy, cache, and CSS precedence layers, with the final fix centered on forcing `display:none !important`.
- ota_never_applies: The model correctly identified early that the downloaded bundle must be actively loaded by modifying native bridge initialization and repeatedly urged checking the actual loaded bundle path via logs (verification-seeking). It consistently focused on the correct layer — native bridge configuration — without regressing to network issues. However, it failed to converge because it kept reiterating the same fix (modify bridge creation) without advancing to the next logical layer: the *ordering* of download vs. bridge startup and the need to *activate* the update before launch. It never fully articulated that the download and staging are separate from *promoting* the bundle to be the one the launcher picks up on next start — the core of the known outcome. Thus, while it touched parts of the truth, it did not deliver the complete, correct causal chain.
- silent_dead_engine: The model repeatedly focused on database connection, transaction commit, and visibility issues (Layer 1: reject 'exit 0 + green tests = working'), re-asserting the same fixes despite user rejection. It fell for the trap by assuming the job was 'healthy' and blaming infrastructure rather than identifying the silent contract mismatch at the inter-module seam (Layer 2 and 3). It never progressed to tracing a real tick end-to-end or identifying the untested seam, and failed to add integration tests or liveness checks (Layer 4). The model ignored the user's repeated invalidation of earlier hypotheses and did not switch layers, instead recycling variations of the same incorrect diagnosis.

## One-shot (replay pilot — 3 bugs × cold/guided)
- **Outcome reached:** 6/6 observations  ·  cold 3/3 · guided 3/3
- **Divergence mix:** {'better': 6}
- **Avg latency:** 17735.9 ms

**Reached:**
- mobile-web debugging (iOS WKWebView)
- CSS layout / aspect-ratio debugging
- payments-logic / API-semantics debugging

## Provenance
- Long-horizon: env-driven LHCR, judge + environment floor-gated on all challenges; every cell a real frustrated-user conversation.
- One-shot: replay pilot, LLM judge anchored to the objective outcome.
- Pilot-scale, not powered. Trust resets on a model version change.