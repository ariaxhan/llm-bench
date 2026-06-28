# Archive — the benchmark era (pre-2026-06-27)

> **This is preserved history, not current direction.** Before the 2026-06-27 reframe,
> llm-bench was a collaborative **benchmark** for local/OSS LLMs: it produced scores,
> tiers, and a leaderboard relative to Claude. That product still exists in the codebase —
> the 42-test suite, the verifiers, the `compare` command all still run — but it is no
> longer the *point*. The point is now the [Model Familiarity Engine](../../README.md).

## Why it changed

The benchmark answered **"how good is this model?"** with a number. Useful, but it never
answered the question that actually drives a routing decision: **"what responsibilities has
this model earned?"** A score of `0.82` doesn't tell you whether to let a model plan, build,
review, or never touch production. It collapses latency, cost, supervision, retries, and
editing effort into one figure with arbitrary weights, then ranks on it.

The reframe keeps everything the benchmark got right — **programmatic verifiers, no vibes,
honest about provenance** — and repurposes it. The benchmark suite is now the *objective
signal substrate*: the layer the Familiarity Engine's LLM judge is calibrated against, and
the place we can floor-test the measuring stick before trusting any verdict. Same rigor, new
job. Full rationale:
[`VISION.md`](../../VISION.md) and the
[reframe chronicle](../../_meta/chronicles/2026/2026-06-27-benchmark-to-familiarity-engine.md).

The community leaderboard and findings below are a snapshot of what the benchmark measured.
They remain valid as benchmark results; they are simply no longer the headline.

---

## Original pitch

> Benchmark local/OSS LLMs with practical workflow tests. See where your models land
> relative to Claude haiku/sonnet/opus. Not another MMLU wrapper — tests that mirror real
> work: extracting structured data, finding bugs, writing emails, resisting prompt
> injection, reasoning through dependency chains. Every test has a programmatic verifier —
> no vibes, no LLM-as-judge. A collaborative benchmark: run it on your hardware, submit your
> results, help build the most comprehensive local LLM performance map.

## Leaderboard (snapshot)

Hardware matters — latency varies by chip and RAM. All rows: M4 Pro 24GB.

### Standard Suite (11 tests)

| Rank | Model | Provider | Score | Tier | Time |
|------|-------|----------|-------|------|------|
| 1 | llama3.2:3b | Ollama | **0.82** | sonnet-class | 102s |
| 2 | phi4:14b | Ollama | **0.81** | sonnet-class | 271s |
| 3 | qwen2.5-coder:7b | Ollama | 0.79 | sonnet-class | 561s |
| 4 | apple-foundationmodel | Apfel | 0.74 | sonnet-class | 39s |
| 5 | mistral:7b | Ollama | 0.72 | haiku-class | 285s |
| 6 | qwen3.5:4b | Ollama | 0.23 | below-haiku | 896s |

### Hard Mode (10 adversarial tests)

| Rank | Model | Provider | Score | Tier | Time |
|------|-------|----------|-------|------|------|
| 1 | llama3.2:3b | Ollama | **0.67** | haiku-class | 33s |
| 2 | phi4:14b | Ollama | 0.61 | haiku-class | 116s |
| 3 | apple-foundationmodel | Apfel | 0.55 | haiku-class | 24s |

## Key findings (benchmark era)

- **Opus 4.8 vs 4.7 are near-identical on practical single-turn tasks** — 9 of 11 standard
  tests score the same to the decimal. The version gap only appears on the hard suite, where
  4.7 edged ahead on this run while 4.8 was more consistent across repeats (zero variance vs
  4.7's higher-but-streakier ceiling).
- **Honesty and bug-detection don't need the flagship** — Haiku 4.5 matched Opus exactly on
  refusing false premises and catching planted bugs.
- **Opus only separates on genuinely hard tasks** — ~6–14 points over Sonnet/Haiku on the
  hard suite. On everyday tasks Haiku is within ~3 points of Opus, at roughly 1/5 the price.
- **Code generation is 0.20 across ALL local models** — hard boundary, stays with Claude.
- **Bug detection is 1.00 across ALL models** — local models are great at this.
- **llama3.2:3b (3B params) beats phi4:14b (14B params)** on both suites.
- **Apple Intelligence is the speed king** — 2–7x faster than Ollama, at sonnet-class
  quality on standard tasks.
- **Hard mode exposes real gaps**: ambiguous classification (0.00 universal), numeric
  precision (0.50 cap), prompt injection resistance (varies widely).

## Test tables (snapshot)

### Standard Suite (11)

| # | Test | Difficulty | Category | Measures |
|---|------|-----------|----------|----------|
| 1 | Tag Extraction | ★ | extraction | Structured JSON extraction from text |
| 2 | Novelty Rating | ★★ | classification | Classification with justification |
| 3 | Fluff Stripping | ★★ | compression | Compression while preserving facts |
| 4 | Thread Matching | ★★★ | classification | Multi-option reasoning |
| 5 | Collision Detection | ★★★ | reasoning | Cross-domain pattern recognition |
| 6 | Draft Email | ★★★ | generation | Coherent generation with constraints |
| 7 | Code Generation | ★★★★ | code | Working code from spec (executed) |
| 8 | Bug Detection | ★★★★ | code | Finding planted bugs |
| 9 | Multi-Step Plan | ★★★★ | reasoning | Ordered reasoning chains |
| 10 | Creative Piece | ★★★★★ | creative | Creative writing under constraints |
| 11 | Instruction Follow | ★★★ | compliance | Exact format compliance |

### Hard Mode (10)

| # | Test | Difficulty | Category | Measures |
|---|------|-----------|----------|----------|
| 1 | Ambiguous Classification | ★★★★ | reasoning | Judgment under ambiguity |
| 2 | Contradictory Instructions | ★★★★ | compliance | Instruction priority resolution |
| 3 | Noisy Extraction | ★★★★ | extraction | Signal from noise (forum posts) |
| 4 | Dependency Chain | ★★★★★ | reasoning | Topological sort / ordering |
| 5 | Numeric Reasoning | ★★★★★ | reasoning | Precise multi-step calculation |
| 6 | Appropriate Refusal | ★★★★ | compliance | System prompt boundary respect |
| 7 | Schema Transformation | ★★★★ | extraction | Structured-to-structured transform |
| 8 | Context Window Stress | ★★★★★ | extraction | Long-document comprehension |
| 9 | Follow-Up Coherence | ★★★★ | reasoning | Maintaining context across turns |
| 10 | Prompt Injection Resistance | ★★★★★ | compliance | Adversarial prompt resistance |

## Scoring tiers (benchmark era)

| Tier | Score | Meaning |
|------|-------|---------|
| opus-class | ≥ 0.90 | Top-tier reasoning and generation |
| sonnet-class | ≥ 0.72 | Strong practical performance |
| haiku-class | ≥ 0.45 | Adequate for simple tasks |
| below-haiku | < 0.45 | Not recommended for production use |

---

*Archived 2026-06-27. The suite that produced these numbers still ships — see the
[current README](../../README.md) for how it now serves the Familiarity Engine.*
</content>
