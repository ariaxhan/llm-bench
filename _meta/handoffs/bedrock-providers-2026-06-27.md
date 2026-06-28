## CONTEXT HANDOFF
Generated: 2026-06-27

**Summary**: Add a Bedrock provider to llm-bench and run the 21-test suite across the full AWS Bedrock model catalog (DeepSeek, Llama, Qwen, Mistral, Moonshot, MiniMax, Z.AI, etc.) on Aria's credit-covered AWS account.

**Goal**: Treat open/hosted models as first-class — measure quality + latency + cost-per-task of every Bedrock-available text model against the existing Claude/local baselines, using llm-bench's programmatic verifiers (no LLM-as-judge). Strategic frame: Claude for brainstorming, open models for fast execution; this bench is how we pick the execution models on data, not vibes.

**Current state**: llm-bench is mature (21 tests, programmatic verifiers, earned-certainty scorer, results/ + experiments/). It has a clean `providers/` plugin system but **no Bedrock provider**. The Bedrock side is proven working from the dify-meta session: a live `converse` call to Llama 4 Maverick returned correct code in 0.99s round-trip on this exact account.

**Branch**: main (llm-bench repo; was dirty with unrelated `_meta/agentdb/agent.db.json` + `experiments/floor/*` changes — leave those alone, not ours).

**Tier**: 2 — moderate (new provider file + registry wiring + a sweep runner + boto3 dep; ~3–5 files).

**AWS facts (verified live this session)**:
- Profile **`keystone`**, account **114829893009**, region **us-west-2**. boto3 picks it up via `AWS_PROFILE=keystone` or `boto3.Session(profile_name="keystone")`.
- Cost: **100% covered by AWS credits** right now. Post-credits still cheap (DeepSeek V3.2 $0.62/$1.85 per 1M in/out; Maverick ~$0.24/$0.80; vs Opus ~$15/$75). Bench should record token usage so cost-per-task is computable.
- Working call shape (the unified Converse API — same shape for every provider):
  ```python
  client = boto3.Session(profile_name="keystone").client("bedrock-runtime", region_name="us-west-2")
  resp = client.converse(
      modelId="us.meta.llama4-maverick-17b-instruct-v1:0",   # inference-profile id, NOT base id
      messages=[{"role": "user", "content": [{"text": user_prompt}]}],
      system=[{"text": system_prompt}],                       # omit if empty
      inferenceConfig={"maxTokens": max_tokens, "temperature": temperature},
  )
  text   = resp["output"]["message"]["content"][0]["text"]
  tokens = resp["usage"]["totalTokens"]
  ```
- Enumerate invocable IDs: `bedrock` client `list_inference_profiles()` (filter status==ACTIVE). Catalog (incl. non-invocable): `list_foundation_models()`.

**Decisions made**:
- Use **boto3 `bedrock-runtime` Converse API**, not the OpenAI-compat provider — Bedrock isn't OpenAI-shaped, and Converse normalizes across all 17 providers so one code path covers everything. (Rejected: routing through the existing `opencode` provider — adds latency + obscures true model latency.)
- boto3 is sync → wrap the call in `asyncio.to_thread(...)` to satisfy the `async def complete` interface.
- Handoff doc lives in llm-bench (not dify-meta) so it's present on session open.

**Artifacts created**:
- `_meta/handoffs/bedrock-providers-2026-06-27.md` (this file)

**The implementation (next session, in order)**:
1. **Add boto3 dep**: `boto3` is NOT in the venv (confirmed — import fails). Add to `pyproject.toml` deps, `pip install -e ".[dev]"`.
2. **`src/llm_bench/providers/bedrock.py`**: `class BedrockProvider(BaseProvider)` implementing the interface in `providers/base.py`:
   - `complete(model, system_prompt, user_prompt, max_tokens=1024, temperature=0.0) -> LLMResponse` — Converse call above, time with `time.perf_counter()`, return `LLMResponse(content, latency_ms, tokens_used, model, raw=resp)`.
   - `list_models()` → `list_inference_profiles()` ACTIVE ids.
   - `is_available()` → cheap `list_inference_profiles()` ok / catch.
3. **Register in `providers/__init__.py`**: add `"bedrock": lambda: BedrockProvider(profile="keystone", region="us-west-2")` to the `get_provider` factory + `__all__`.
4. **Sweep runner**: iterate ACTIVE inference profiles, run the 21-test suite per model, dump to `results/bedrock/<model>.json` (mirror the existing `results/` shape so `compare.py` works).

**Big 5 Status** (for the implementation):
- [ ] Input validation — pending (validate model id is an active profile before run; clear error if access not enabled)
- [ ] Edge cases — pending (reasoning models e.g. `deepseek.r1` emit thinking + may reject `temperature`; empty system prompt → omit `system`; throttling/`ThrottlingException` → backoff)
- [ ] Error handling — pending (`ValidationException` = wrong/disabled model id; `AccessDeniedException` = model access not enabled in console)
- [ ] Duplication — n/a (new provider follows existing pattern)
- [ ] Complexity — keep one Converse path; don't special-case per provider unless a test proves it's needed

**Open threads**:
- BLOCKER (partial): **Model access must be enabled in the Bedrock console** (us-west-2) before a model is invocable — listing ≠ access. Only **3 profiles ACTIVE** today: `us.meta.llama4-maverick-17b-instruct-v1:0`, `us.meta.llama4-scout-17b-instruct-v1:0`, `us.deepseek.r1-v1:0`. To bench DeepSeek V3.2, Qwen, Mistral Devstral, Moonshot/Kimi, MiniMax, Z.AI/GLM, OpenAI-gpt-oss → **Aria enables them in console → Model access** (her AWS login; one-time clicks).
- TODO: **Filter non-text providers out of the sweep.** The catalog counts (AI21 2, Amazon 15, Anthropic 12, Cohere 6, DeepSeek 2, Google 3, Meta 11, MiniMax 3, Mistral 13, Moonshot 2, NVIDIA 4, OpenAI 4, Qwen 5, Stability 13, TwelveLabs 3, Writer 3, Z.AI 3) include image/video/embeddings — **Stability (image), TwelveLabs (video), Luma (video), Titan-image/embeddings** can't run text-workflow tests. Filter by `outputModalities` contains `TEXT` from `list_foundation_models()`.
- TODO: record per-run token usage so cost-per-task lands in results (pricing table above).

**Warnings**:
- Base model ids (e.g. `deepseek.v3.2`, `us.deepseek.v3.2`) throw `ValidationException: The provided model identifier is invalid` — **must** use an active inference-profile id from `list_inference_profiles()`.
- Don't sweep the repo's pre-existing dirty files (`_meta/agentdb/agent.db.json`, `experiments/floor/*`) into implementation commits — unrelated.

**Continuation prompt**:
> /kernel:ingest Add a Bedrock provider to llm-bench and sweep the 21-test suite across all ACTIVE Bedrock models on AWS profile `keystone` (us-west-2). Provider interface in src/llm_bench/providers/base.py, register in providers/__init__.py. Read _meta/handoffs/bedrock-providers-2026-06-27.md first.
