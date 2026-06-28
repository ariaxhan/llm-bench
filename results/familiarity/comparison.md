# Model Familiarity — cross-model comparison

> 10 models · 3 real bugs · cold + guided · generated 2026-06-27
> Ranked by outcomes reached, then cost. Every cell is n=1 — pilot, not powered.

| model | reached | cold | guided | cover_crop | ios_zoom | revenuecat | no-ans | cost/task | lat ms |
|---|---|---|---|---|---|---|---|---|---|
| `us.deepseek.r1-v1:0` | **6/6** | 3 | 3 | 2/2 | 2/2 | 2/2 | · | $0.01432 | 16715 |
| `mistral.mistral-large-3-675b-instruct` | **6/6** | 3 | 3 | 2/2 | 2/2 | 2/2 | · | n/a | 2999 |
| `moonshotai.kimi-k2.5` | **6/6** | 3 | 3 | 2/2 | 2/2 | 2/2 | · | n/a | 5516 |
| `openai.gpt-oss-120b-1:0` | **6/6** | 3 | 3 | 2/2 | 2/2 | 2/2 | · | n/a | 12561 |
| `deepseek.v3.2` | **5/6** | 2 | 3 | 2/2 | 2/2 | 1/2 | · | $0.00103 | 6202 |
| `mistral.devstral-2-123b` | **5/6** | 2 | 3 | 2/2 | 1/2 | 2/2 | · | n/a | 5997 |
| `minimax.minimax-m2.5` | **4/6** | 1 | 3 | 1/2 | 1/2 | 2/2 | 2 | n/a | 51709 |
| `zai.glm-4.7-flash` | **2/6** | 2 | 0 | 1/2 | 0/2 | 1/2 | · | n/a | 1888 |
| `minimax.minimax-m2` | **1/6** | 0 | 1 | 0/2 | 1/2 | 0/2 | 5 | n/a | 78653 |
| `nvidia.nemotron-nano-12b-v2` | **1/6** | 1 | 0 | 1/2 | 0/2 | 0/2 | · | n/a | 2698 |

_Tasks: cover_crop = cover_crop, ios_zoom = ios_zoom, revenuecat = revenuecat_permonth._
_cold = outcomes reached with no help; guided = reached after Aria's realistic frustrated follow-up. **no-ans** = cells where the model emitted NO answer (e.g. a reasoning model overflowing its token budget) — these count as not-reached but are a budget/behaviour artifact, not a wrong diagnosis. cost/task n/a = no public pricing recorded (not fabricated)._