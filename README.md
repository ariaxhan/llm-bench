# llm-bench

Benchmark local/OSS LLMs with practical workflow tests. See where your models land relative to Claude haiku/sonnet/opus.

Not another MMLU wrapper. 21 tests that mirror real work: extracting structured data, finding bugs, writing emails, resisting prompt injection, reasoning through dependency chains. Every test has a programmatic verifier — no vibes, no LLM-as-judge.

**This is a collaborative benchmark.** Run it on your hardware, submit your results, and help build the most comprehensive local LLM performance map.

## Install

```bash
pip install llm-bench         # from PyPI (coming soon)
```

From source:

```bash
git clone https://github.com/ariaxhan/llm-bench
cd llm-bench
pip install -e ".[dev]"
```

Requires Python 3.10+.

## Quick Start

```bash
# Standard suite (11 tests)
llm-bench run phi4:14b

# Hard mode (10 adversarial tests)
llm-bench run phi4:14b --hard

# Full suite (21 tests)
llm-bench run phi4:14b --full --details

# Apple Intelligence
llm-bench run apple-foundationmodel -p apfel

# Compare models
llm-bench run phi4:14b llama3.2:3b -o results/comparison.json
llm-bench compare results/*.json

# Quick sanity check (3 tests)
llm-bench quick phi4:14b
```

## Leaderboard

Results from community benchmarks. Hardware matters — latency varies by chip and RAM.

### Standard Suite (11 tests)

| Rank | Model | Provider | Score | Tier | Time | Hardware |
|------|-------|----------|-------|------|------|----------|
| 1 | llama3.2:3b | Ollama | **0.82** | sonnet-class | 102s | M4 Pro 24GB |
| 2 | phi4:14b | Ollama | **0.81** | sonnet-class | 271s | M4 Pro 24GB |
| 3 | qwen2.5-coder:7b | Ollama | 0.79 | sonnet-class | 561s | M4 Pro 24GB |
| 4 | apple-foundationmodel | Apfel | 0.74 | sonnet-class | 39s | M4 Pro 24GB |
| 5 | mistral:7b | Ollama | 0.72 | haiku-class | 285s | M4 Pro 24GB |
| 6 | qwen3.5:4b | Ollama | 0.23 | below-haiku | 896s | M4 Pro 24GB |

### Hard Mode (10 adversarial tests)

| Rank | Model | Provider | Score | Tier | Time | Hardware |
|------|-------|----------|-------|------|------|----------|
| 1 | llama3.2:3b | Ollama | **0.67** | haiku-class | 33s | M4 Pro 24GB |
| 2 | phi4:14b | Ollama | 0.61 | haiku-class | 116s | M4 Pro 24GB |
| 3 | apple-foundationmodel | Apfel | 0.55 | haiku-class | 24s | M4 Pro 24GB |

### Claude Reference Baselines

| Tier | Estimated Score | Role |
|------|----------------|------|
| opus | 0.94 | Planning, creative, architecture |
| sonnet | 0.78 | Implementation, synthesis |
| haiku | 0.52 | Validation, triage |

### Key Findings

- **Code generation is 0.20 across ALL local models** — hard boundary, stays with Claude
- **Bug detection is 1.00 across ALL models** — local models are great at this
- **llama3.2:3b (3B params) beats phi4:14b (14B params)** on both standard and hard suites
- **Apple Intelligence is the speed king** — 2-7x faster than Ollama, at sonnet-class quality on standard tasks
- **Hard mode exposes real gaps**: ambiguous classification (0.00 universal), numeric precision (0.50 cap), prompt injection resistance (varies widely)

## Tests

### Standard Suite (11 tests)

| # | Test | Difficulty | Category | What It Measures |
|---|------|-----------|----------|-----------------|
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

### Hard Mode (10 adversarial tests)

| # | Test | Difficulty | Category | What It Measures |
|---|------|-----------|----------|-----------------|
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

## Providers

| Provider | Flag | Default URL | Notes |
|----------|------|-------------|-------|
| Ollama | `-p ollama` | `localhost:11434/v1` | Most models |
| Apfel | `-p apfel` | CLI-based | macOS 26+, Apple Intelligence |
| LM Studio | `-p lmstudio` | `localhost:1234/v1` | GUI-based |
| Custom | `-p openai-compat -u URL` | — | Any OpenAI-compatible API |

## Scoring

| Tier | Score | Meaning |
|------|-------|---------|
| opus-class | >= 0.90 | Top-tier reasoning and generation |
| sonnet-class | >= 0.72 | Strong practical performance |
| haiku-class | >= 0.45 | Adequate for simple tasks |
| below-haiku | < 0.45 | Not recommended for production use |

## Contributing

We want your results. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

**Quick version:**

```bash
# 1. Run benchmarks
llm-bench run <model> -o results/standard.json
llm-bench run <model> --hard -o results/hard.json

# 2. Create community file
# results/community/<username>-<chip>-<ram>gb.json

# 3. PR it
git checkout -b results/<username>
git add results/community/
git commit -m "results: <chip> <ram>GB"
gh pr create
```

### Adding Tests

Tests go in `src/llm_bench/tests/`. Every test needs a programmatic verifier in `src/llm_bench/verify.py`. See CONTRIBUTING.md for the full guide.

## License

MIT
