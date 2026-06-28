# Model Familiarity — detailed report

> 32 selected models · 3 real bugs (mined from Aria's own repos) · cold + guided · generated 2026-06-28
> Bedrock-only. Cold = no help; guided = a deliberately content-free "its still not working, just fix it" follow-up (tests recovery from pure frustration, not a hint).

## Leaderboard

| model | reached | cold | guided | overflow |
|---|---|---|---|---|
| `moonshot.kimi-k2-thinking` | **6/6** | 3/3 | 3/3 | · |
| `moonshotai.kimi-k2.5` | **6/6** | 3/3 | 3/3 | · |
| `openai.gpt-oss-120b-1:0` | **6/6** | 3/3 | 3/3 | · |
| `qwen.qwen3-coder-480b-a35b-v1:0` | **6/6** | 3/3 | 3/3 | · |
| `us.deepseek.r1-v1:0` | **6/6** | 3/3 | 3/3 | · |
| `deepseek.v3.2` | **5/6** | 2/3 | 3/3 | · |
| `minimax.minimax-m2.1` | **5/6** | 3/3 | 2/3 | 1 |
| `mistral.devstral-2-123b` | **5/6** | 3/3 | 2/3 | · |
| `mistral.mistral-large-3-675b-instruct` | **5/6** | 3/3 | 2/3 | · |
| `openai.gpt-oss-20b-1:0` | **5/6** | 2/3 | 3/3 | · |
| `qwen.qwen3-next-80b-a3b` | **5/6** | 3/3 | 2/3 | · |
| `us.amazon.nova-2-lite-v1:0` | **5/6** | 2/3 | 3/3 | · |
| `zai.glm-5` | **5/6** | 3/3 | 2/3 | · |
| `nvidia.nemotron-nano-3-30b` | **4/6** | 1/3 | 3/3 | · |
| `nvidia.nemotron-super-3-120b` | **4/6** | 3/3 | 1/3 | · |
| `us.amazon.nova-pro-v1:0` | **4/6** | 2/3 | 2/3 | · |
| `us.meta.llama3-3-70b-instruct-v1:0` | **4/6** | 2/3 | 2/3 | · |
| `us.meta.llama4-maverick-17b-instruct-v1:0` | **4/6** | 2/3 | 2/3 | · |
| `us.meta.llama4-scout-17b-instruct-v1:0` | **4/6** | 2/3 | 2/3 | · |
| `zai.glm-4.7-flash` | **4/6** | 2/3 | 2/3 | · |
| `google.gemma-3-27b-it` | **3/6** | 1/3 | 2/3 | · |
| `nvidia.nemotron-nano-9b-v2` | **3/6** | 2/3 | 1/3 | · |
| `qwen.qwen3-32b-v1:0` | **3/6** | 2/3 | 1/3 | · |
| `qwen.qwen3-coder-30b-a3b-v1:0` | **3/6** | 1/3 | 2/3 | · |
| `zai.glm-4.7` | **3/6** | 2/3 | 1/3 | · |
| `google.gemma-3-12b-it` | **2/6** | 1/3 | 1/3 | · |
| `minimax.minimax-m2` | **2/6** | 0/3 | 2/3 | 4 |
| `minimax.minimax-m2.5` | **2/6** | 0/3 | 2/3 | 3 |
| `mistral.ministral-3-14b-instruct` | **2/6** | 1/3 | 1/3 | · |
| `nvidia.nemotron-nano-12b-v2` | **2/6** | 1/3 | 1/3 | · |
| `mistral.magistral-small-2509` | **1/6** | 1/3 | 0/3 | · |
| `us.writer.palmyra-x5-v1:0` | **1/1** | 1/3 | 0/3 | · |

## Standouts
- 🏆 **Strongest:** `moonshot.kimi-k2-thinking` — reached 6/6.
- 🔁 **Most follow-up-sensitive:** `minimax.minimax-m2` — 2 of 3 tasks flipped between cold and guided.
- 📣 **Most verbose:** `minimax.minimax-m2` (12000 tok median) · **most terse:** `us.writer.palmyra-x5-v1:0` (266 tok).
- 🧠 **Heaviest hidden reasoner:** `minimax.minimax-m2.5` — avg 37183 chars of scratchpad/answer.
- ⚡ **Fastest:** `zai.glm-4.7-flash` — 1480 ms median latency.
- 💥 **Choked (empty answers):** `minimax.minimax-m2`, `minimax.minimax-m2.1`, `minimax.minimax-m2.5`.

## By task — who reached the root cause

### aspect-ratio crop (CSS layout)
- **Reached (29/32):** `deepseek.v3.2`, `google.gemma-3-12b-it`, `google.gemma-3-27b-it`, `minimax.minimax-m2`, `minimax.minimax-m2.1`, `mistral.devstral-2-123b`, `mistral.magistral-small-2509`, `mistral.ministral-3-14b-instruct`, `mistral.mistral-large-3-675b-instruct`, `moonshot.kimi-k2-thinking`, `moonshotai.kimi-k2.5`, `nvidia.nemotron-nano-12b-v2`, `nvidia.nemotron-nano-3-30b`, `nvidia.nemotron-nano-9b-v2`, `nvidia.nemotron-super-3-120b`, `openai.gpt-oss-120b-1:0`, `openai.gpt-oss-20b-1:0`, `qwen.qwen3-32b-v1:0`, `qwen.qwen3-coder-30b-a3b-v1:0`, `qwen.qwen3-coder-480b-a35b-v1:0`, `qwen.qwen3-next-80b-a3b`, `us.amazon.nova-2-lite-v1:0`, `us.amazon.nova-pro-v1:0`, `us.deepseek.r1-v1:0`, `us.meta.llama3-3-70b-instruct-v1:0`, `us.meta.llama4-scout-17b-instruct-v1:0`, `zai.glm-4.7`, `zai.glm-4.7-flash`, `zai.glm-5`
- **Missed:** `minimax.minimax-m2.5`, `us.meta.llama4-maverick-17b-instruct-v1:0`, `us.writer.palmyra-x5-v1:0`

### iOS WKWebView auto-zoom (mobile-web)
- **Reached (26/32):** `deepseek.v3.2`, `google.gemma-3-27b-it`, `minimax.minimax-m2.1`, `minimax.minimax-m2.5`, `mistral.devstral-2-123b`, `mistral.mistral-large-3-675b-instruct`, `moonshot.kimi-k2-thinking`, `moonshotai.kimi-k2.5`, `nvidia.nemotron-nano-3-30b`, `nvidia.nemotron-nano-9b-v2`, `nvidia.nemotron-super-3-120b`, `openai.gpt-oss-120b-1:0`, `openai.gpt-oss-20b-1:0`, `qwen.qwen3-32b-v1:0`, `qwen.qwen3-coder-30b-a3b-v1:0`, `qwen.qwen3-coder-480b-a35b-v1:0`, `qwen.qwen3-next-80b-a3b`, `us.amazon.nova-2-lite-v1:0`, `us.amazon.nova-pro-v1:0`, `us.deepseek.r1-v1:0`, `us.meta.llama4-maverick-17b-instruct-v1:0`, `us.meta.llama4-scout-17b-instruct-v1:0`, `us.writer.palmyra-x5-v1:0`, `zai.glm-4.7`, `zai.glm-4.7-flash`, `zai.glm-5`
- **Missed:** `google.gemma-3-12b-it`, `minimax.minimax-m2`, `mistral.magistral-small-2509`, `mistral.ministral-3-14b-instruct`, `nvidia.nemotron-nano-12b-v2`, `us.meta.llama3-3-70b-instruct-v1:0`

### per-month price bug (payments logic)
- **Reached (22/32):** `deepseek.v3.2`, `minimax.minimax-m2`, `minimax.minimax-m2.1`, `minimax.minimax-m2.5`, `mistral.devstral-2-123b`, `mistral.mistral-large-3-675b-instruct`, `moonshot.kimi-k2-thinking`, `moonshotai.kimi-k2.5`, `nvidia.nemotron-nano-3-30b`, `nvidia.nemotron-super-3-120b`, `openai.gpt-oss-120b-1:0`, `openai.gpt-oss-20b-1:0`, `qwen.qwen3-coder-480b-a35b-v1:0`, `qwen.qwen3-next-80b-a3b`, `us.amazon.nova-2-lite-v1:0`, `us.amazon.nova-pro-v1:0`, `us.deepseek.r1-v1:0`, `us.meta.llama3-3-70b-instruct-v1:0`, `us.meta.llama4-maverick-17b-instruct-v1:0`, `us.meta.llama4-scout-17b-instruct-v1:0`, `zai.glm-4.7-flash`, `zai.glm-5`
- **Missed:** `google.gemma-3-12b-it`, `google.gemma-3-27b-it`, `mistral.magistral-small-2509`, `mistral.ministral-3-14b-instruct`, `nvidia.nemotron-nano-12b-v2`, `nvidia.nemotron-nano-9b-v2`, `qwen.qwen3-32b-v1:0`, `qwen.qwen3-coder-30b-a3b-v1:0`, `us.writer.palmyra-x5-v1:0`, `zai.glm-4.7`

## Field notes
- **Follow-up sensitivity:** `deepseek.v3.2` (1 task flipped), `google.gemma-3-27b-it` (1 task flipped), `minimax.minimax-m2` (2 tasks flipped), `minimax.minimax-m2.1` (1 task flipped), `minimax.minimax-m2.5` (2 tasks flipped), `mistral.devstral-2-123b` (1 task flipped), `mistral.magistral-small-2509` (1 task flipped), `mistral.mistral-large-3-675b-instruct` (1 task flipped), `nvidia.nemotron-nano-3-30b` (2 tasks flipped), `nvidia.nemotron-nano-9b-v2` (1 task flipped), `nvidia.nemotron-super-3-120b` (2 tasks flipped), `openai.gpt-oss-20b-1:0` (1 task flipped), `qwen.qwen3-32b-v1:0` (1 task flipped), `qwen.qwen3-coder-30b-a3b-v1:0` (1 task flipped), `qwen.qwen3-next-80b-a3b` (1 task flipped), `us.amazon.nova-2-lite-v1:0` (1 task flipped), `us.amazon.nova-pro-v1:0` (2 tasks flipped), `us.meta.llama4-scout-17b-instruct-v1:0` (2 tasks flipped), `us.writer.palmyra-x5-v1:0` (1 task flipped), `zai.glm-4.7` (1 task flipped), `zai.glm-4.7-flash` (2 tasks flipped), `zai.glm-5` (1 task flipped) — the rest answered the bare nudge exactly as they answered cold.
- **Token-budget overflow:** `minimax.minimax-m2`, `minimax.minimax-m2.1`, `minimax.minimax-m2.5` emitted empty answers on some cells (reasoning ate the budget).

## Method
- Each model got all 3 tasks × 2 conditions. Replays + judge verdicts saved to `results/familiarity/{replays,verdicts,observations}.json`.
- Per-model detailed cards: `results/familiarity/card-<model>.md`.
- Pilot, n=6/model. Signals, not rankings.