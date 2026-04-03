# Contributing to llm-bench

This is a collaborative benchmark. We want results from diverse hardware, models, and configurations. Two ways to contribute: submit results and add new tests.

## Submitting Results

### 1. Run the benchmarks

```bash
pip install -e ".[dev]"

# Standard suite (11 tests)
llm-bench run <your-model> -o results/my-standard.json

# Hard mode (10 tests)
llm-bench run <your-model> --hard -o results/my-hard.json
```

### 2. Create your community results file

Name it: `results/community/<github-username>-<chip>-<ram>gb.json`

Example: `results/community/jdoe-m3max-36gb.json`

Structure:

```json
{
  "hardware": {
    "contributor": "<your-github-username>",
    "machine": "MacBook Pro 16\" 2025",
    "chip": "Apple M3 Max",
    "memory_gb": 36,
    "gpu": "integrated",
    "os": "macOS 15.4",
    "date": "2026-04-05",
    "notes": "optional — anything unusual about your setup"
  },
  "benchmark_version": "0.1.0",
  "standard_results": { ... },
  "hard_results": { ... }
}
```

You can generate this manually or use the helper:

```bash
llm-bench submit --contributor jdoe \
  --chip "Apple M3 Max" --memory 36 --os "macOS 15.4" \
  --standard results/my-standard.json \
  --hard results/my-hard.json \
  -o results/community/jdoe-m3max-36gb.json
```

### 3. Open a PR

```bash
git checkout -b results/<your-username>
git add results/community/<your-file>.json
git commit -m "results: <username> <chip> <ram>GB"
git push origin results/<your-username>
gh pr create --title "results: <chip> <ram>GB" --body "New benchmark results from <hardware description>"
```

### What makes a good submission

- Run ALL tests (standard + hard) — partial results are still accepted but noted
- Include accurate hardware info — chip, RAM, and OS matter for latency comparisons
- Run each model individually (not concurrently) for accurate latency numbers
- Note any non-default ollama settings (context size, quantization level, etc.)
- If you have the same hardware as an existing submission, still submit — reproducibility data is valuable

## Adding New Tests

### Test anatomy

Every test needs:
1. A clear, unambiguous prompt
2. A programmatic verifier (no vibes scoring)
3. A difficulty rating that reflects actual challenge
4. Metadata that the verifier uses to score

### Where to add tests

- Standard tests: `src/llm_bench/tests/suite.py`
- Hard tests: `src/llm_bench/tests/hard_suite.py`
- New categories: create `src/llm_bench/tests/<category>_suite.py`

### Adding a test

```python
from llm_bench.models import TestCase, Difficulty

MY_TEST = TestCase(
    id="category-descriptive-name",    # kebab-case, unique
    name="Human Readable Name",
    category="reasoning",              # existing or new category
    difficulty=Difficulty.HARD,        # TRIVIAL, EASY, MEDIUM, HARD, EXTREME
    system_prompt="...",
    user_prompt="...",
    verify="instruction_follow",       # name of verifier function
    metadata={                         # passed to the verifier
        "checks": [
            {"type": "contains", "value": "expected"},
            {"type": "is_valid_json", "value": True},
        ]
    },
)
```

Then add it to the appropriate list (`ALL_TESTS`, `HARD_TESTS`) and register it.

### Available verifiers

| Verifier | What it checks | Metadata fields |
|----------|---------------|-----------------|
| `tag_extraction` | JSON with correct tags | `tags: list[str]` |
| `novelty_rating` | Star rating + justification | `rating: int`, `min_reasons: int` |
| `fluff_strip` | Compression with fact retention | `max_words: int`, `required_facts: list[str]` |
| `thread_match` | Correct thread assignment | `correct_threads`, `all_threads` |
| `collision_detect` | Cross-domain connections | `connections: list[{keywords}]` |
| `draft_email` | Email quality scoring | `min_words`, `max_words`, `required_points`, `tone` |
| `code_gen` | Executes code, runs assertions | `test_code: str` |
| `bug_detection` | Finds planted bugs | `bug_keywords`, `fix_keywords` |
| `multi_step_plan` | Ordered step verification | `required_steps: list[{keywords}]` |
| `creative_piece` | Constraint satisfaction | `constraints: {min_words, max_words, required_elements, forbidden_phrases}` |
| `instruction_follow` | Format compliance checks | `checks: list[{type, value}]` |

### Writing a new verifier

Add to `src/llm_bench/verify.py`:

```python
def verify_my_thing(output: str, expected: dict) -> tuple[float, dict]:
    """Return (score 0.0-1.0, details dict)."""
    # Your verification logic
    score = ...
    details = {"what_happened": ...}
    return score, details
```

Then register in `VERIFIERS` dict at the bottom of the file.

### Test quality guidelines

- Every test must have ONE correct answer (or a clearly bounded set)
- Verifiers must be deterministic — same output always gets same score
- Don't test trivia or knowledge — test capability
- Hard tests should expose real failure modes, not just be longer
- Include the test in unit tests (`tests/test_verify.py`)

## For Claude Code Users

If you're using Claude Code to contribute, here's the workflow:

```
# Fork and clone
gh repo fork ariaxhan/llm-bench --clone

# Run benchmarks
cd llm-bench && pip install -e ".[dev]"
llm-bench run <model> -o results/standard.json
llm-bench run <model> --hard -o results/hard.json

# Create submission (Claude can help with this)
# Ask Claude: "Create a community results file from my benchmark results"

# PR
git checkout -b results/<your-username>
git add results/community/
git commit -m "results: <your-chip> <ram>GB"
git push && gh pr create
```

Claude Code agents can run the full benchmark suite autonomously. Just tell it which models to test.

## Code Style

- Python 3.10+
- Ruff for linting (config in pyproject.toml)
- pytest for testing
- Type hints encouraged but not required for test data
