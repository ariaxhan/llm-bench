# llm-bench → The Model Familiarity Engine

> The repository keeps its name for its history. Its purpose has changed.
> This is no longer a benchmark. It does not produce scores, rankings, or leaderboards.
> It is a **Model Familiarity Engine**: it continuously onboards language models, observes
> them in real work, learns where they should and should not be trusted, and builds
> evidence-backed routing knowledge for everyday multi-model agent systems.

Status: **concept locked, implementation at stage 0.** Reframed 2026-06-27 (see
`_meta/chronicles/2026/2026-06-27-benchmark-to-familiarity-engine.md` for how we got here,
and `_meta/canon/breakthroughs/2026-06-27-benchmark-to-familiarity-engine.md` for the story).

---

## The problem we're actually solving

The model ecosystem grows faster than anyone can understand it — every week new frontier
models, open models, fine-tunes, reasoning models, coding models. Everyone has opinions;
nobody has operational knowledge. Model choice today is hearsay: *"I heard Qwen is good,"
"people say DeepSeek is amazing," "I just keep using Claude because I know it."*

The real problem was never **evaluation**. It is **familiarity**. The question is not
"how good is this model?" — it is **"what responsibilities has this model earned?"**

## The user

One user: **Aria.** The concrete need: *stop defaulting to Claude/OpenAI because they're
familiar.* The goal is to comfortably run an OpenCode-style ensemble of specialized agents
and, when a new model appears, not guess where it belongs — have the system say: should it
plan? implement? review? brainstorm? critique? summarize? never touch production? That is
**onboarding**, not testing. It looks like hiring an engineer, not administering an exam.

## The metric: regret, not quality

Don't optimize "quality." Optimize **regret**: after a routing decision, *if I could rewind,
would I still choose this model?* Low regret = yes. Regret absorbs quality, latency, cost,
supervision, frustration, retries, maintainability, and editing effort with **no arbitrary
weights**. Future routing minimizes expected regret.

The catch, and the design that answers it: regret is a **counterfactual** — you only ran one
model, so you can't normally *see* the road not taken. So we run the other roads (below).

## The core object: the Observation

The fundamental unit is no longer a benchmark. It is an **Observation**:

```
Observation = { model@version · role · task · workflow · collaborators ·
                outcome · regret · surprise · evidence · notes }
```

Everything else — cards, trust, routing — emerges from accumulating observations.

## The output: Model Cards, not ranks

Not `Claude: 94.2`. A teammate profile:

```
Claude
  Primary roles : Planner · Reviewer · Architecture
  Needs         : Expensive
  Failure modes : Can over-engineer
  Best pairings : Qwen implementer
  Confidence    : High  (n observations, last updated <date>)
```

And — because real work is collaborative, not independent — **organizational** knowledge:
which reviewer makes another model better, which planner hands off well, which builder
responds to critique, which *pairings* beat stronger individuals.

## The mechanism: a memory and a metabolism

Two engines fill the Observation store. Together they close the loop.

```
PAST  (memory / bootstrap):
  your Claude .jsonl logs → extract (prompt, trajectory, known outcome, repo-state)
  → redact secrets → replay through other models (cold + guided) → seed the cards

FUTURE (metabolism / flywheel):
  every new pure/sandboxable task → async shadow fan-out of cheap models in isolation
  (worktrees) → never blocks live work → refine the cards continuously

JUDGE:
  reference-anchored divergence characterization — did it reach the known outcome,
  and how did it diverge (equivalent / better / worse / novel) — NEVER similarity-to-Claude

SPINE:
  cheap objective signals (shipped? tests pass? edit-distance? overridden? retries?)
  decide winners automatically; LLM-judgment is a soft layer calibrated against the spine

OUTPUT:
  evidence-backed Model Cards → role assignment → routing → minimize regret →
  continuous re-evaluation (trust is never final)
```

**Replay-from-logs** solves cold-start: thousands of real tasks you already ran, with
outcomes you already know — ground truth excavated, not generated. **Shadow-execution**
solves the counterfactual: stop *estimating* the road not taken and actually drive down all
of them, since open-model compute is cheap. Selection bias, sparse data, and unobservable
regret all dissolve because every task becomes a real N-way experiment.

## The discipline (non-negotiable — this is what keeps it honest)

- **No vibes.** Every number anchors to a cheap objective signal, or it doesn't ship.
- **Divergence is data, not error.** A model doing it *differently* is the signal. Never
  punish a model for not being Claude — that builds a clone detector, the dumbest possible
  outcome.
- **The grader is suspect until floor-tested.** Run a dummy answer through any judge; if
  garbage scores well, the judge measures nothing (`test-the-measuring-stick`, on ourselves).
- **Compute is cheap; attention is scarce.** Spend compute lavishly to spare Aria's
  attention — never the reverse. Async by default; humans adjudicate only when it's cheap or
  the stakes are high.
- **Secrets never leave for a third party.** `.jsonl` logs hold private context; redact
  before any replay to a non-Claude provider (I0.9). Hard gate.
- **Honest about n.** Pilot ≠ powered. Report provenance and confidence intervals; trust
  decays and resets on version change.

## The first build (start here — data you already have)

The **replay bootstrap**. Not the interview rig, not routing — the smallest loop that is
already useful: mine your own logs, replay a handful of real tasks through ≥2 other models
in isolation, characterize divergence against the known outcome, and render **one Model Card
for one model.** It proves the honest-signal plumbing before anything fancy.
Commission: `_meta/commissions/active/2026-06-27-model-familiarity-engine.md`.

## Open questions (carried, not yet answered)

1. **Can roles emerge?** Start with a fixed taxonomy (planner/builder/reviewer/critic); let
   clusters of observations that fit no role *nominate* new ones (e.g. "contrarian reviewer,"
   "context compressor"). Don't pre-engineer emergence.
2. **How does confidence decay?** Model versions are discrete jumps, not smooth decay —
   *reset/discount* priors on a new release, keyed on `model@version`.
3. **How is surprise modeled?** As an exploration bonus (Thompson/UCB): high surprise = high
   info gain = explore that model more. Track expectation violations, not just outcomes.
4. **Does onboarding ever end?** No. It's a perpetual contextual bandit — promotion,
   demotion, new evidence, version changes, all continuous.
5. **Prompt vs trajectory baseline?** Replaying the *initial prompt* tests cold one-shot
   under-specification; replaying the *whole trajectory* tests "could it do what Claude did
   with the same guidance." Different measurements — run both, the gap is itself a trait.

## The sentence

> **llm-bench continuously onboards language models by observing them in real work, learning
> where they should be trusted, and building an evidence-backed routing system for intelligent
> multi-model workflows.**
