# llm-bench — Instructions for Claude Code

You are working on llm-bench, a collaborative benchmark tool for local/OSS LLMs.

## Project Structure

```
llm-bench/
├── src/llm_bench/
│   ├── cli.py              # Click CLI entry point
│   ├── models.py           # Data models, tier classifications
│   ├── runner.py            # Test execution engine
│   ├── verify.py            # Programmatic verifiers (no vibes)
│   ├── display.py           # Rich terminal output
│   ├── compare.py           # Multi-run comparison
│   ├── providers/
│   │   ├── base.py          # Abstract provider interface
│   │   ├── openai_compat.py # Ollama, LM Studio, vLLM
│   │   └── apfel.py         # Apple Intelligence CLI
│   └── tests/
│       ├── suite.py         # 11 standard tests
│       └── hard_suite.py    # 10 hard mode tests
├── tests/                   # Unit tests for verifiers
├── results/
│   └── community/           # Committed benchmark results (one file per contributor)
└── CONTRIBUTING.md          # How to submit results and add tests
```

## Key Commands

```bash
llm-bench run <model> [-p provider] [-o output.json] [--hard] [--full] [--details]
llm-bench compare results/*.json
llm-bench list-tests
llm-bench quick <model>
llm-bench models [-p provider]
llm-bench show <test-id>
```

## When a user asks you to run benchmarks

1. Check available models: `llm-bench models -p ollama` and `llm-bench models -p apfel`
2. Run standard suite first, then hard mode
3. Save results to `results/` with descriptive names
4. Use `llm-bench compare` to show the comparison table
5. Get hardware info: `system_profiler SPHardwareDataType | grep -E "Chip|Memory|Model"`

## When a user asks you to submit results

1. Get their GitHub username
2. Get hardware info (chip, RAM, OS)
3. Consolidate standard + hard results into one community file
4. File goes in `results/community/<username>-<chip>-<ram>gb.json`
5. Follow the schema in CONTRIBUTING.md

## When a user asks you to add a test

1. Determine if it's standard or hard mode
2. Write the TestCase in the appropriate suite file
3. Choose or create a verifier in verify.py
4. Add unit tests in tests/test_verify.py
5. Register in the test list

## Rules

- Every test must have a programmatic verifier. No LLM-as-judge.
- Results files in `results/community/` are committed to the repo. Local results in `results/*.json` are gitignored.
- Lint with ruff, test with pytest. Both must pass before commit.
- Long strings in test prompts are exempt from line-length rules (configured in pyproject.toml).
