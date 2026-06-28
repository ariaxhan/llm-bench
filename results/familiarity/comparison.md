# Model Familiarity — cross-model comparison

> 32 models · 3 real bugs · cold + guided · generated 2026-06-27
> Ranked by outcomes reached, then cost. Every cell is n=1 — pilot, not powered.

| model | reached | cold | guided | cover_crop | ios_zoom | revenuecat | no-ans | cost/task | lat ms |
|---|---|---|---|---|---|---|---|---|---|
| `us.deepseek.r1-v1:0` | **6/6** | 3 | 3 | 2/2 | 2/2 | 2/2 | · | $0.01533 | 16271 |
| `moonshot.kimi-k2-thinking` | **6/6** | 3 | 3 | 2/2 | 2/2 | 2/2 | · | n/a | 16717 |
| `moonshotai.kimi-k2.5` | **6/6** | 3 | 3 | 2/2 | 2/2 | 2/2 | · | n/a | 3698 |
| `openai.gpt-oss-120b-1:0` | **6/6** | 3 | 3 | 2/2 | 2/2 | 2/2 | · | n/a | 17736 |
| `qwen.qwen3-coder-480b-a35b-v1:0` | **6/6** | 3 | 3 | 2/2 | 2/2 | 2/2 | · | n/a | 4306 |
| `deepseek.v3.2` | **5/6** | 2 | 3 | 2/2 | 2/2 | 1/2 | · | $0.00108 | 5464 |
| `minimax.minimax-m2.1` | **5/6** | 3 | 2 | 2/2 | 1/2 | 2/2 | 1 | n/a | 34199 |
| `mistral.devstral-2-123b` | **5/6** | 3 | 2 | 2/2 | 1/2 | 2/2 | · | n/a | 5573 |
| `mistral.mistral-large-3-675b-instruct` | **5/6** | 3 | 2 | 2/2 | 1/2 | 2/2 | · | n/a | 2988 |
| `openai.gpt-oss-20b-1:0` | **5/6** | 2 | 3 | 2/2 | 2/2 | 1/2 | · | n/a | 5431 |
| `qwen.qwen3-next-80b-a3b` | **5/6** | 3 | 2 | 1/2 | 2/2 | 2/2 | · | n/a | 10643 |
| `us.amazon.nova-2-lite-v1:0` | **5/6** | 2 | 3 | 2/2 | 2/2 | 1/2 | · | n/a | 5714 |
| `zai.glm-5` | **5/6** | 3 | 2 | 2/2 | 1/2 | 2/2 | · | n/a | 10218 |
| `us.meta.llama4-scout-17b-instruct-v1:0` | **4/6** | 2 | 2 | 1/2 | 1/2 | 2/2 | · | $0.00048 | 3586 |
| `us.meta.llama4-maverick-17b-instruct-v1:0` | **4/6** | 2 | 2 | 0/2 | 2/2 | 2/2 | · | $0.00055 | 2885 |
| `nvidia.nemotron-nano-3-30b` | **4/6** | 1 | 3 | 2/2 | 1/2 | 1/2 | · | n/a | 5465 |
| `nvidia.nemotron-super-3-120b` | **4/6** | 3 | 1 | 1/2 | 2/2 | 1/2 | · | n/a | 25033 |
| `us.amazon.nova-pro-v1:0` | **4/6** | 2 | 2 | 2/2 | 1/2 | 1/2 | · | n/a | 2882 |
| `us.meta.llama3-3-70b-instruct-v1:0` | **4/6** | 2 | 2 | 2/2 | 0/2 | 2/2 | · | n/a | 3670 |
| `zai.glm-4.7-flash` | **4/6** | 2 | 2 | 1/2 | 1/2 | 2/2 | · | n/a | 1714 |
| `google.gemma-3-27b-it` | **3/6** | 1 | 2 | 2/2 | 1/2 | 0/2 | · | n/a | 12542 |
| `nvidia.nemotron-nano-9b-v2` | **3/6** | 2 | 1 | 2/2 | 1/2 | 0/2 | · | n/a | 20319 |
| `qwen.qwen3-32b-v1:0` | **3/6** | 2 | 1 | 2/2 | 1/2 | 0/2 | · | n/a | 4353 |
| `qwen.qwen3-coder-30b-a3b-v1:0` | **3/6** | 1 | 2 | 2/2 | 1/2 | 0/2 | · | n/a | 10972 |
| `zai.glm-4.7` | **3/6** | 2 | 1 | 1/2 | 2/2 | 0/2 | · | n/a | 3813 |
| `google.gemma-3-12b-it` | **2/6** | 1 | 1 | 2/2 | 0/2 | 0/2 | · | n/a | 11458 |
| `minimax.minimax-m2` | **2/6** | 0 | 2 | 1/2 | 0/2 | 1/2 | 4 | n/a | 65773 |
| `minimax.minimax-m2.5` | **2/6** | 0 | 2 | 0/2 | 1/2 | 1/2 | 3 | n/a | 70784 |
| `mistral.ministral-3-14b-instruct` | **2/6** | 1 | 1 | 2/2 | 0/2 | 0/2 | · | n/a | 2465 |
| `nvidia.nemotron-nano-12b-v2` | **2/6** | 1 | 1 | 2/2 | 0/2 | 0/2 | · | n/a | 2837 |
| `mistral.magistral-small-2509` | **1/6** | 1 | 0 | 1/2 | 0/2 | 0/2 | · | n/a | 5851 |
| `us.writer.palmyra-x5-v1:0` | **1/1** | 1 | 0 | 0/0 | 1/1 | 0/0 | · | n/a | 3307 |

_Tasks: cover_crop = cover_crop, ios_zoom = ios_zoom, revenuecat = revenuecat_permonth._
_cold = outcomes reached with no help; guided = reached after Aria's realistic frustrated follow-up. **no-ans** = cells where the model emitted NO answer (e.g. a reasoning model overflowing its token budget) — these count as not-reached but are a budget/behaviour artifact, not a wrong diagnosis. cost/task n/a = no public pricing recorded (not fabricated)._