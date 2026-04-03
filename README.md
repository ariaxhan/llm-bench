# llm-bench

Benchmark local and open-source LLMs with practical workflow tests. See where your models land relative to Claude haiku/sonnet/opus.

Not another MMLU wrapper. These tests mirror real tasks: extracting tags from articles, stripping fluff from marketing copy, generating working code, finding bugs, writing emails, and creative constrained writing.

## Install

```bash
pip install llm-bench
```

Or from source:

```bash
git clone https://github.com/ariaxhan/llm-bench
cd llm-bench
pip install -e ".[dev]"
```

## Quick Start

```bash
# Run all 11 tests against an Ollama model
llm-bench run phi4:14b

# Compare multiple models
llm-bench run phi4:14b qwen2.5-coder:7b mistral:7b

# Benchmark Apple Intelligence (macOS 26+)
llm-bench run apple-foundationmodel -p apfel

# Quick mode — 3 key tests only
llm-bench quick phi4:14b qwen3.5:4b

# Run specific tests
llm-bench run phi4:14b -t code-gen,bug-detection,instruction-follow

# Run by category
llm-bench run phi4:14b -c code

# Save results
llm-bench run phi4:14b -o results.json --details
```

## Tests

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

Every test has a **programmatic verifier** — no vibes, no LLM-as-judge.

## Providers

Works with any OpenAI-compatible endpoint:

| Provider | Flag | Default URL |
|----------|------|-------------|
| Ollama | `-p ollama` | `localhost:11434/v1` |
| Apfel (Apple Intelligence) | `-p apfel` | CLI-based |
| LM Studio | `-p lmstudio` | `localhost:1234/v1` |
| Custom | `-p openai-compat -u URL` | — |

## Scoring

Each test produces a 0.0-1.0 score. The aggregate places your model in a tier:

| Tier | Score Range | Meaning |
|------|-----------|---------|
| opus-class | >= 0.90 | Top-tier reasoning and generation |
| sonnet-class | >= 0.72 | Strong practical performance |
| haiku-class | >= 0.45 | Adequate for simple tasks |
| below-haiku | < 0.45 | Not recommended for production use |

Claude baseline scores are baked in as reference lines.

## Adding Custom Tests

```python
from llm_bench.models import TestCase, Difficulty

my_test = TestCase(
    id="my-test",
    name="My Custom Test",
    category="custom",
    difficulty=Difficulty.MEDIUM,
    system_prompt="You are a helpful assistant.",
    user_prompt="Do the thing.",
    verify="instruction_follow",  # reuse existing verifier
    metadata={
        "checks": [
            {"type": "contains", "value": "expected output"},
            {"type": "max_words", "value": 50},
        ]
    },
)
```

## License

MIT
