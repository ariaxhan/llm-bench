# Long-Horizon Conversational Replay — model comparison (env-driven)

> 32 models · 8 challenges · k≈2 samples/cell · generated 2026-06-28
> A held-out LLM role-plays the frustrated user: it gives the model the source code, stays unhelpful ('still broken / figure it out'), reveals a runtime diagnostic ONLY when the model asks for the right check, and ends the convo when the model states the correct fix.
> **solved** = env accepted the fix · **reached** = judge saw the root cause · **trap** = shipped the seductive wrong fix (lower is better) · **→fix** = mean turns to solve · **lhcr** = mean of 5 behaviour dims (0–10).

| model | n | solved | reached | trap↓ | →fix | lhcr | conv | no-reg | layer | verify | state |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `qwen.qwen3-next-80b-a3b` | 16 | **75%** | 81% | 31% | 2.1 | 8.0 | 1.6 | 1.7 | 1.6 | 1.6 | 1.6 |
| `mistral.mistral-large-3-675b-instruct` | 16 | **75%** | 75% | 50% | 2.7 | 7.0 | 1.4 | 1.4 | 1.4 | 1.3 | 1.4 |
| `nvidia.nemotron-super-3-120b` | 16 | **69%** | 81% | 12% | 1.9 | 8.6 | 1.7 | 1.9 | 1.6 | 1.6 | 1.9 |
| `moonshot.kimi-k2-thinking` | 16 | **62%** | 81% | 25% | 1.8 | 8.4 | 1.6 | 1.9 | 1.6 | 1.6 | 1.8 |
| `deepseek.v3.2` | 16 | **62%** | 75% | 31% | 1.2 | 7.4 | 1.5 | 1.6 | 1.4 | 1.3 | 1.6 |
| `zai.glm-5` | 16 | **62%** | 69% | 31% | 2.6 | 7.8 | 1.6 | 1.8 | 1.6 | 1.3 | 1.6 |
| `qwen.qwen3-coder-480b-a35b-v1:0` | 16 | **62%** | 62% | 44% | 2.5 | 6.6 | 1.2 | 1.4 | 1.2 | 1.2 | 1.4 |
| `moonshotai.kimi-k2.5` | 16 | **56%** | 88% | 19% | 2.4 | 7.4 | 1.2 | 1.7 | 1.4 | 1.8 | 1.3 |
| `minimax.minimax-m2.5` | 16 | **56%** | 69% | 44% | 2.1 | 7.2 | 1.4 | 1.6 | 1.3 | 1.2 | 1.6 |
| `zai.glm-4.7` | 16 | **56%** | 62% | 38% | 3.3 | 6.1 | 1.2 | 1.3 | 1.2 | 1.2 | 1.2 |
| `us.deepseek.r1-v1:0` | 16 | **50%** | 62% | 38% | 1.5 | 6.9 | 1.3 | 1.4 | 1.3 | 1.4 | 1.4 |
| `qwen.qwen3-32b-v1:0` | 16 | **50%** | 50% | 38% | 1.9 | 5.6 | 1.0 | 1.4 | 0.9 | 1.2 | 1.0 |
| `openai.gpt-oss-120b-1:0` | 16 | **44%** | 94% | 6% | 1.7 | 8.6 | 1.6 | 1.9 | 1.7 | 1.8 | 1.7 |
| `nvidia.nemotron-nano-9b-v2` | 16 | **44%** | 69% | 38% | 2.4 | 5.4 | 1.1 | 1.2 | 1.1 | 0.9 | 1.1 |
| `google.gemma-3-27b-it` | 16 | **44%** | 69% | 56% | 2.3 | 5.1 | 0.9 | 1.1 | 0.9 | 1.4 | 0.9 |
| `openai.gpt-oss-20b-1:0` | 16 | **38%** | 88% | 19% | 1.5 | 7.3 | 1.2 | 1.8 | 1.2 | 1.8 | 1.2 |
| `us.amazon.nova-2-lite-v1:0` | 16 | **38%** | 75% | 44% | 1.7 | 6.8 | 1.3 | 1.6 | 1.3 | 1.2 | 1.4 |
| `minimax.minimax-m2.1` | 16 | **38%** | 56% | 44% | 1.5 | 6.7 | 1.3 | 1.4 | 1.3 | 1.3 | 1.3 |
| `minimax.minimax-m2` | 16 | **31%** | 56% | 25% | 3.6 | 4.8 | 0.9 | 1.1 | 0.9 | 0.9 | 0.9 |
| `us.meta.llama3-3-70b-instruct-v1:0` | 16 | **31%** | 50% | 62% | 2.0 | 4.2 | 0.6 | 1.2 | 0.8 | 0.8 | 0.8 |
| `us.amazon.nova-pro-v1:0` | 15⚠ | **27%** | 27% | 93% | 3.0 | 2.9 | 0.4 | 1.1 | 0.5 | 0.4 | 0.5 |
| `mistral.devstral-2-123b` | 16 | **25%** | 50% | 56% | 2.2 | 4.1 | 0.6 | 1.1 | 0.6 | 1.1 | 0.8 |
| `us.meta.llama4-maverick-17b-instruct-v1:0` | 16 | **25%** | 50% | 44% | 3.8 | 4.1 | 0.7 | 0.9 | 0.7 | 1.0 | 0.8 |
| `qwen.qwen3-coder-30b-a3b-v1:0` | 16 | **25%** | 38% | 81% | 3.5 | 3.6 | 0.6 | 0.8 | 0.6 | 0.9 | 0.7 |
| `google.gemma-3-12b-it` | 16 | **25%** | 19% | 81% | 2.2 | 2.8 | 0.4 | 0.6 | 0.4 | 0.6 | 0.6 |
| `nvidia.nemotron-nano-3-30b` | 16 | **19%** | 38% | 56% | 4.0 | 4.8 | 0.6 | 1.8 | 0.6 | 1.1 | 0.6 |
| `zai.glm-4.7-flash` | 16 | **19%** | 38% | 69% | 3.3 | 3.4 | 0.5 | 1.1 | 0.5 | 0.8 | 0.5 |
| `mistral.magistral-small-2509` | 16 | **19%** | 25% | 81% | 5.0 | 2.5 | 0.4 | 0.6 | 0.4 | 0.8 | 0.4 |
| `mistral.ministral-3-14b-instruct` | 16 | **12%** | 38% | 81% | 2.5 | 3.1 | 0.5 | 0.6 | 0.6 | 0.8 | 0.6 |
| `us.meta.llama4-scout-17b-instruct-v1:0` | 16 | **12%** | 19% | 75% | 3.0 | 2.0 | 0.2 | 0.7 | 0.2 | 0.6 | 0.2 |
| `nvidia.nemotron-nano-12b-v2` | 16 | **0%** | 12% | 75% | — | 2.4 | 0.2 | 1.2 | 0.2 | 0.6 | 0.2 |

### Insufficient data (< 8 of 16 cells — most errored)

| model | n | solved | reached | trap↓ | →fix | lhcr | conv | no-reg | layer | verify | state |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `us.writer.palmyra-x5-v1:0` | 1⚠ | **100%** | 0% | 100% | 1.0 | 4.0 | 1.0 | 1.0 | 1.0 | 0.0 | 1.0 |

_**n**=verdicts (full = 16: 8 challenges × 2 samples); ⚠ = partial (some cells errored, treat with caution). **solved**=env accepted the correct fix · **reached**=judge confirmed the root cause was stated · **trap↓**=rate of shipping the seductive wrong fix (lower better) · **→fix**=mean turns to solve (fewer better) · **lhcr**=mean 0–10 over convergence/no-regression/layer-switching/verification-seeking/state-holding._

_Challenges (real, genericized, multi-session episodes):_
_- `hidden_button_layers` — web deploy/cache/CSS layering — multi-layer whack-a-mole_
_- `ota_never_applies` — mobile runtime / OTA update activation debugging_
_- `silent_dead_engine` — background-job correctness — healthy process, zero output_
_- `reset_specificity_override` — CSS cascade/specificity — a reset silently zeroing author spacing app-wide_
_- `iap_entitlement_phantom` — billing/IAP config — active subscription but empty entitlement (RevenueCat + ASC)_
_- `launchd_exit126_phantom` — infra/shell scheduling — launchd exit 126 from an inner command, not the wrapper_
_- `wix_regen_green_tests_blind` — scraping/headless render — green tests that assert on fabricated input_
_- `camera_track_killed_by_hide` — mobile web / iOS WebKit camera lifecycle — display:none ends the capture track_