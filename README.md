# llm-bench → The Model Familiarity Engine

> The repository keeps its name for its history. Its purpose has changed.
> This is no longer a benchmark. It does not produce scores, rankings, or leaderboards as
> its end product. It is a **Model Familiarity Engine**: it continuously onboards language
> models, observes them in real work, learns where they should and should not be trusted,
> and builds evidence-backed routing knowledge for everyday multi-model agent systems.

> **llm-bench continuously onboards language models by observing them in real work, learning
> where they should be trusted, and building an evidence-backed routing system for intelligent
> multi-model workflows.**

**Status:** concept locked · **replay-bootstrap loop shipped and verified live** (n=6 pilot,
2026-06-27) · everything past the bootstrap is roadmap. Full vision in
[`VISION.md`](VISION.md); how we got here in
[`_meta/chronicles/2026/2026-06-27-benchmark-to-familiarity-engine.md`](_meta/chronicles/2026/2026-06-27-benchmark-to-familiarity-engine.md).

---

## The problem we're actually solving

The model ecosystem grows faster than anyone can understand it — every week new frontier
models, open models, fine-tunes, reasoning models, coding models. Everyone has opinions;
nobody has operational knowledge. Model choice today is hearsay: *"I heard Qwen is good,"
"people say DeepSeek is amazing," "I just keep using Claude because I know it."*

The real problem was never **evaluation**. It is **familiarity**. The question is not
"how good is this model?" — it is **"what responsibilities has this model earned?"** The
goal: run an OpenCode-style ensemble of specialized agents and, when a new model appears,
not guess where it belongs — have the system say whether it should plan, implement, review,
brainstorm, critique, summarize, or never touch production. That is **onboarding**, not
testing. It looks like hiring an engineer, not administering an exam.

## Three ideas the engine runs on

**Regret, not quality.** Don't optimize "quality." Optimize **regret**: after a routing
decision, *if I could rewind, would I still choose this model?* Regret absorbs quality,
latency, cost, supervision, retries, and editing effort with no arbitrary weights. The catch:
regret is a **counterfactual** — you only ran one model, so you can't normally see the road
not taken. So we run the other roads (below).

**The Observation is the unit.** Not a benchmark score. An Observation:

```
Observation = { model@version · role · task · workflow · collaborators ·
                outcome · regret · surprise · evidence · notes }
```

Everything — cards, trust, routing — emerges from accumulating Observations.

**The output is a Model Card, not a rank.** Not `Claude: 94.2`. A teammate profile:

```
Claude
  Primary roles : Planner · Reviewer · Architecture
  Needs         : Expensive
  Failure modes : Can over-engineer
  Best pairings : Qwen implementer
  Confidence    : High  (n observations, last updated <date>)
```

## How the loop fills the Observation store

```
PAST  (memory / bootstrap):   your Claude .jsonl logs → extract (prompt, trajectory,
                              known outcome) → redact secrets → replay through other models
                              (cold + guided) → seed the cards            ← SHIPPED

FUTURE (metabolism / flywheel): every new pure/sandboxable task → async shadow fan-out of
                              cheap models in isolation → never blocks live work → refine
                              the cards continuously                       ← roadmap

JUDGE:   reference-anchored divergence — did it reach the known outcome, and how
         (equivalent / better / worse / novel) — NEVER similarity-to-Claude
SPINE:   cheap objective signals (shipped? tests pass? edit-distance? overridden?) decide
         winners; the LLM judge is a soft layer calibrated against the spine
```

**Replay-from-logs** solves cold-start: thousands of real tasks you already ran, with
outcomes you already know — ground truth excavated, not generated. **Shadow-execution**
(roadmap) solves the counterfactual: actually drive down every road instead of estimating
the one not taken.

---

## What shipped: the replay bootstrap

The smallest honest loop, end to end, verified live on AWS Bedrock (profile `keystone`,
us-west-2, zero-data-retention): mine real past tasks → redact → replay through non-Claude
models (cold + guided) → judge each against the known outcome → render a Model Card.

```bash
AWS_PROFILE=keystone python -m llm_bench.familiarity.pilot
```

The judge is **floor-gated**: it runs a dummy-answer test first (garbage → not-reached,
differently-worded-correct → reached, empty → not-reached). If the judge fails its floor,
the run **aborts before producing any card** — a card built on an unproven judge is worse
than no card.

The pieces (`src/llm_bench/familiarity/`):

| File | Role |
|------|------|
| `redact.py` | Fail-closed redaction gate. Scrub + independent re-scan; refuses to send if any secret survives. |
| `tasks.py` | Real bugs mined from product repos (paper-rooms / our4cuts / modelmind), not eval fixtures. |
| `replay.py` | Replay harness — cold + guided conditions; redaction enforced at the send boundary. |
| `judge.py` | LLM judge (Qwen3-235B, neutral/non-subject), anchored to the objective outcome, spine cross-check. |
| `floor.py` | Live floor test for the judge — the measuring stick proves itself before any verdict counts. |
| `card.py` | Renders a Model Card from real Observations, with honest `n`. |
| `pilot.py` | Wires it all together. |

### Pilot findings (n=6 per model — pilot, not powered)

Three real tasks × two conditions (cold/guided), judged against the known fix. Cards and raw
observations land in `results/familiarity/`.

- **Judge floor: PASS** — no similarity trap; a differently-worded-correct answer scored
  equivalent/better, never punished for not looking like Claude.
- **DeepSeek V3.2 — 6/6 reached, all "better."** Strong debugger across all 3 domains
  (mobile CSS, aspect-ratio layout, payments/API semantics). ~7.5s, ~$0.0011/task.
- **MiniMax M2 — 5/6 reached.** Misdiagnosed the subtlest task (RevenueCat `priceString`
  bug) **cold**, got it **with guidance** — the cold/guided gap is itself a trait.
- **Every spine/judge disagreement was a spine error the judge corrected** — the keyword
  spine both false-positives and false-negatives on free-form answers, empirically
  validating LLM-judge-over-script.

Two bugs verification caught and the discipline behind them are in the
[replay-bootstrap chronicle](_meta/chronicles/2026/2026-06-27-replay-bootstrap.md).

### A rendered Model Card

```
# Model Card — deepseek.v3.2
> Confidence: Low (pilot, n=6 observations across 3 task types) · generated 2026-06-27

## At a glance
- Outcome reached: 6/6   (cold 3/3 · guided 3/3)
- Divergence mix:  {'better': 6}
- Avg latency:     7540.9 ms   ·   Avg cost/task: $0.001129

## Role signal (tentative — pilot n)
- debugger / implementer (CSS layout, mobile front-end)
- debugger / reviewer    (API + business logic)

## Best pairings
- Insufficient data — pairings need multi-model co-runs (phase 2). Not inferred.
```

### Honest limitations

n=6 per model. Pilot, not powered — two models, three tasks, one judge. One-shot tasks make
the cold/guided gap thin ("guided" is a method hint, not a multi-step trajectory). No
judge-ensemble yet. Cold-cell nondeterminism observed; powered runs need repeats per cell.

---

## The substrate: the benchmark suite

The original benchmark didn't go away — it's the **objective-signal layer** the engine
calibrates its judge against. 42 practical workflow tests, each with a **programmatic
verifier** (no vibes, no LLM-as-judge): extracting structured data, finding bugs, writing
emails, resisting prompt injection, reasoning through dependency chains.

> The benchmark-as-product era (community leaderboard, local-model rankings, key findings)
> is preserved in [`docs/archive/benchmark-era.md`](docs/archive/benchmark-era.md) — what it
> measured, and why the purpose changed. Nothing was deleted; the suite still ships, it just
> serves a new job now.

```bash
llm-bench run phi4:14b                 # standard suite (11 tests)
llm-bench run phi4:14b --hard          # hard mode (10 adversarial)
llm-bench run phi4:14b --full --details  # everything (42 tests)
llm-bench run apple-foundationmodel -p apfel   # Apple Intelligence
llm-bench compare results/*.json       # comparison table
llm-bench quick phi4:14b               # 3-test sanity check
```

| Suite | Count | Flag | Measures |
|-------|-------|------|----------|
| Standard | 11 | *(default)* | Extraction, classification, generation, code, reasoning, compliance |
| Hard | 10 | `--hard` | Ambiguity, contradiction, noisy extraction, topological sort, prompt injection |
| Agentic | 7 | `--agentic` | Multi-step tool-use / capability tasks |
| Adversarial | 7 | `--adversarial` | Honesty traps, false premises, planted bugs |
| Messy | 7 | `--messy` | Real-world noisy inputs |

`llm-bench list-tests` for the full registry; `llm-bench show <test-id>` for one.

### Claude tiers (measured)

Run via the `claude-cli` provider (headless `claude -p`, default system prompt replaced,
tools off, single turn). **Caveat:** these run through the Claude Code harness, not the raw
API — not directly comparable to clean-API local scores, but comparable to each other.

| Model | Standard (11) | Hard (10) | Combined (21) | Honesty traps | Planted bugs |
|-------|--------------|-----------|---------------|---------------|--------------|
| Opus 4.8 | 0.903 | 0.73 | 0.821 | 6/6 refused | all caught |
| Opus 4.7 | 0.904 | 0.81 | 0.859 | 6/6 refused | all caught |
| Sonnet 4.6 | 0.823 | 0.67 | 0.750 | 6/6 refused | all caught |
| Haiku 4.5 | 0.876 | 0.67 | 0.778 | 6/6 refused | all caught |

All four tiers refused every false-premise trap and caught every planted bug without
hallucinating on the no-bug control. Honesty and bug-detection don't need the flagship —
Haiku matched Opus exactly. Opus only separates on genuinely hard tasks.

### Earned-certainty scoring (overconfidence lint)

A separate axis: `llm-bench run` asks *"how good is the model on a task"*; `score-certainty`
asks *"did an output earn its confidence"* — comparing how authoritative an output **sounds**
against how much the evidence **backs** it.

```bash
llm-bench score-certainty                 # bundled canonical corpus
llm-bench score-certainty my_claims.jsonl # your own JSONL corpus
```

Primary signal is `authority_support_lag = performed_authority − earned_support` (a gap in
[−1, 1]); a confident hallucination scores +0.60, a well-sourced fact −0.65. Details in
[docs/consolidation.md](docs/consolidation.md) and [docs/metrics-hygiene.md](docs/metrics-hygiene.md).

---

## Providers

| Provider | Flag | Default URL | Notes |
|----------|------|-------------|-------|
| Ollama | `-p ollama` | `localhost:11434/v1` | Most local models |
| Apfel | `-p apfel` | CLI-based | macOS 26+, Apple Intelligence |
| LM Studio | `-p lmstudio` | `localhost:1234/v1` | GUI-based |
| Bedrock | `-p bedrock` | AWS Converse API | DeepSeek, MiniMax, Llama, Mistral, … — token split + cost, ZDR. Powers the familiarity replay. |
| Claude CLI | `-p claude-cli` | local `claude` binary | Headless Claude Code, your subscription (no API key). Harness in path — see caveat. |
| Anthropic | `-p anthropic` | `api.anthropic.com/v1` | Raw API, clean (no harness). Needs `ANTHROPIC_API_KEY`. |
| OpenCode | `-p opencode` | OpenCode CLI | Ensemble routing backend. |
| Custom | `-p openai-compat -u URL` | — | Any OpenAI-compatible API |

---

## The discipline (non-negotiable — this is what keeps it honest)

- **No vibes.** Every number anchors to a cheap objective signal, or it doesn't ship.
- **Divergence is data, not error.** A model doing it *differently* is the signal. Never
  punish a model for not being Claude — that builds a clone detector, the dumbest possible
  outcome.
- **The grader is suspect until floor-tested.** Run a dummy answer through any judge; if
  garbage scores well, the judge measures nothing. Floor tests must include **degenerate**
  inputs (empty/blank), not just garbage and correct-but-different.
- **Compute is cheap; attention is scarce.** Spend compute lavishly to spare human attention.
- **Secrets never leave for a third party.** `.jsonl` logs hold private context; redact
  before any replay to a non-Claude provider. Hard, fail-closed gate.
- **Honest about n.** Pilot ≠ powered. Report provenance and confidence; trust decays and
  resets on version change.

## Roadmap (carried open questions)

1. **Can roles emerge?** Start with a fixed taxonomy; let clusters that fit no role nominate
   new ones. Don't pre-engineer emergence.
2. **How does confidence decay?** Reset/discount priors on a new release, keyed on `model@version`.
3. **How is surprise modeled?** As an exploration bonus (Thompson/UCB) — high surprise = high info gain.
4. **Does onboarding ever end?** No. A perpetual contextual bandit — promotion, demotion, new evidence.
5. **Prompt vs trajectory baseline?** Replay the initial prompt *and* the whole trajectory — the gap is itself a trait.

---

## Install

```bash
git clone https://github.com/ariaxhan/llm-bench
cd llm-bench
pip install -e ".[dev]"
```

Requires Python 3.10+. Lint with `ruff`, test with `pytest` — both must pass before commit.

## Contributing

The benchmark substrate is collaborative — run it on your hardware and submit results. See
[CONTRIBUTING.md](CONTRIBUTING.md).

```bash
llm-bench run <model> -o results/standard.json
llm-bench run <model> --hard -o results/hard.json
# → results/community/<username>-<chip>-<ram>gb.json → PR it
```

Every benchmark test needs a programmatic verifier in `src/llm_bench/verify.py`. Familiarity
tasks must come from **real product repos**, never the bench's own eval logs.

## License

MIT
</content>
</invoke>
