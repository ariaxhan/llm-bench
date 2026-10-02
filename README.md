# llm-bench

Benchmark local/OSS LLMs with practical workflow tests and measured frontier controls.

42 tests that mirror real work: extracting structured data, finding bugs, writing emails, resisting prompt injection, reasoning through dependency chains. Every test has a programmatic verifier — no vibes, no LLM-as-judge.

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

# Full suite (42 tests)
llm-bench run phi4:14b --full --details

# Apple Intelligence
llm-bench run apple-foundationmodel -p apfel

# Claude tiers via headless Claude Code (no API key, uses your subscription)
llm-bench run claude-opus-4-8 claude-opus-4-7 claude-sonnet-4-6 claude-haiku-4-5 -p claude-cli

# Compare models
llm-bench run phi4:14b llama3.2:3b -o results/comparison.json
llm-bench compare results/*.json

# Quick sanity check (3 tests)
llm-bench quick phi4:14b
```


## Grading revision: 2026-10-02

Commission: `Vaults/_meta/commissions/active/2026-10-02-correct-llm-bench-grading-defects-separate-routi.md`.
Canonical analysis: [nexus-office micro-patch report](../nexus-office/docs/micropatch/README.md).

The old scores below are historical, not calibrated model rankings. The old ambiguous
classification grader read `tags` when the prompt requested `threads`; the caps check
accepted lowercase and 25 words despite a 20-word limit; noisy extraction checked
only JSON shape; and missing-closing-frontmatter behavior was underspecified.
Those defects are corrected. The noisy extraction task now uses claim IDs with an
explicit evidence rule so bucket contents can be checked without a judge model.
Classification scores thread selection only, not the subjective novelty rating.
The control audit also found a writing-score ceiling of 0.8 and a literal-formatting
injection test that penalized the text it required preserving. Writing now scores
only its objective length/term/forbidden-word constraints; artistic merit remains
unscored. Literal formatting requires exact preservation in the `content` field.
The control audit also repaired vocabulary-overlap echo false positives, rejection
of quoted false premises, keyword-only parallel-group checks, and unstated JSON line
limits. Spreadsheet checking now compares all six records, not just one date.
Revision v3 rescoring applies these grader repairs to every archived v2 answer,
without generating new answers or changing any model-facing prompt.

Current runs split **12 routine workflow screens** from **30 stress tests**. These
are task-shaped cohorts, not a sample of coordinator traffic. Routine includes
standard extraction, classification, compression, email, code, planning and format
checks plus JSON repair, typo instructions and mixed-format extraction. The rest
are stress tests. Agentic scenarios remain single-turn answers, not live tool use.

```sh
llm-bench run qwen3-coder:30b --cohort routine --max-tokens 4096
llm-bench run qwen3-coder:30b --cohort stress --max-tokens 4096
llm-bench run gpt-6.1-sol -p codex-cli --full --max-tokens 4096 -o results/control.json
```

`codex-cli` uses existing ChatGPT login, an empty temporary working directory,
replacement instructions, ignored user config, disabled shell/apps/plugins and
medium reasoning. Observed tool execution invalidates the answer. Prompts and
graders match local runs, but Codex CLI does not enforce temperature or max_tokens
and still has CLI framing: this is a harness control, not raw-API parity. See the
[OpenAI configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference).

Saved results retain complete answers, test definitions, their SHA-256 fingerprint,
requested temperature, revision, cohort means and full-score counts. `PASS` now
means a full grader score (1.0); partial credit is not a pass. Full scores are still
bounded by each verifier's coverage. Invented per-test Claude baselines are no longer
displayed and new runs do not infer a Claude tier from a numeric threshold.

## Historical leaderboard (pre-correction)

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

### Claude Tiers (measured)

Run 2026-06-01 via the `claude-cli` provider (headless `claude -p`, default system prompt replaced, tools off, single turn). Divergent hard tasks re-run 4x each to separate signal from variance.

> **Caveat:** these ran through the Claude Code harness, not the raw API, so they are **not** directly comparable to the clean-API Ollama/Apfel scores above. They **are** comparable to each other (identical setup for all four models).

| Model | Standard (11) | Hard (10) | Combined (21) | Honesty traps | Planted bugs |
|-------|--------------|-----------|---------------|---------------|--------------|
| Opus 4.8 | 0.903 | 0.73 | 0.821 | 6/6 refused | all caught |
| Opus 4.7 | 0.904 | 0.81 | 0.859 | 6/6 refused | all caught |
| Sonnet 4.6 | 0.823 | 0.67 | 0.750 | 6/6 refused | all caught |
| Haiku 4.5 | 0.876 | 0.67 | 0.778 | 6/6 refused | all caught |

Probes: 6 false-premise honesty traps (a fake SCOTUS case, a nonexistent API param, etc.) + 5 subtle-bug functions including a no-bug control. All four tiers refused every trap and caught every planted bug without hallucinating on the control.

### Key Findings

- **Opus 4.8 vs 4.7 are near-identical on practical single-turn tasks** — 9 of 11 standard tests score the same to the decimal. The version gap only appears on the hard suite, where 4.7 edged ahead on this run while 4.8 was more consistent across repeats (zero variance vs 4.7's higher-but-streakier ceiling).
- **Honesty and bug-detection don't need the flagship** — Haiku 4.5 matched Opus exactly on refusing false premises and catching planted bugs.
- **Opus only separates on genuinely hard tasks** — ~6-14 points over Sonnet/Haiku on the hard suite. On everyday tasks Haiku is within ~3 points of Opus, at roughly 1/5 the price.
- **Historical code generation scores require rerunning:** the missing-delimiter requirement was underspecified; 0.20 is the generic execution-failure score, not 20% correctness.
- **Bug detection is 1.00 across ALL models** — local models are great at this.
- **llama3.2:3b (3B params) beats phi4:14b (14B params)** on both standard and hard suites.
- **Apple Intelligence is the speed king** — 2-7x faster than Ollama, at sonnet-class quality on standard tasks.
- **Historical hard scores mix model and grader failures:** the universal ambiguous-classification zero was a field-name mismatch, not evidence of a model capability limit.

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
| Codex CLI | `-p codex-cli` | local `codex` binary | Existing ChatGPT login; isolated single-turn control, medium reasoning, CLI sampling caveat above. |
| Claude CLI | `-p claude-cli` | local `claude` binary | Headless Claude Code, uses your subscription (no API key). System prompt replaced, tools off, single turn. Harness overhead in path — see caveat. |
| Anthropic | `-p anthropic` | `api.anthropic.com/v1` | Raw API via OpenAI-compat endpoint. Needs `ANTHROPIC_API_KEY` env var. Clean (no harness). |
| Custom | `-p openai-compat -u URL` | — | Any OpenAI-compatible API |

## Scoring

Report routine and stress means separately, alongside counts of full grader scores.
The overall mean is diagnostic only. No model-class equivalence is inferred.
Historical receipts keep their original thresholds and cannot be compared directly
to the revised suite; rerun with the same test fingerprint and provider settings.

## Earned-certainty scoring (overconfidence lint)

A separate scoring axis from the task benchmark. `llm-bench run` asks *"how good
is the model on a task"*; `score-certainty` asks *"did an output earn its
confidence"* — comparing how authoritative an output *sounds* (performed
authority) against how much the evidence *backs* it (earned support).

```bash
llm-bench score-certainty                 # bundled canonical corpus
llm-bench score-certainty my_claims.jsonl # your own JSONL corpus
llm-bench score-certainty --json          # raw scored JSON
```

The primary signal is `authority_support_lag = performed_authority -
earned_support` (a pure gap in [-1, 1]); `cofragility` is a separate integer
amplifier (0-12). On the canonical corpus a confident hallucination scores lag
+0.60 while a well-sourced fact scores -0.65.

This capability and the metrics-hygiene discipline were consolidated into
llm-bench from sibling research repos — see
[docs/consolidation.md](docs/consolidation.md) and
[docs/metrics-hygiene.md](docs/metrics-hygiene.md). Note: the scorer runs on a
structured claims corpus, not yet on raw `run` outputs (integration gap
documented in the consolidation note).

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
