---
rite: canon
kind: breakthrough
date: 2026-06-27
repo: CodingVault/llm-bench
generalizes: true   # the *method* (let each objection's fix become the next reframe) travels
---

# Canon — from benchmark to familiarity engine

## The story
We opened intending to add a Bedrock provider and sweep ~100 open models through the existing
21-test suite. Aria's instinct stopped it: *"scrutinize the harness before we burn tokens."*
An audit confirmed the suite would produce a confidently-wrong ranking — it zeroed open and
reasoning models for formatting/plumbing reasons, and the cost axis (the whole point) wasn't
even computable.

The fix was not to harden the verifiers. Aria saw that hardening *doubled down* on the broken
frame ("is this the exact right answer"). So we tore up the frame instead — and then watched
it reframe itself, five times, each new idea solving the previous one's fatal objection:

1. **Benchmark → behavior.** Score "what behavior do we want," not "right answer."
2. **Behavior → the library.** The tasks shouldn't be invented; they're the real skills in
   `the-agent-library`. *The skill is the stable unit; the instance is novel each run* —
   dissolving the "novel work can't be benchmarked" tension. Bonus: the library's own
   verify-and-review skills ARE the grading epistemics.
3. **Static rig → environment.** Don't grade; build a system with emergent behavior, models
   grading each other (the verify skills, with a different model in the chair). The signal
   worth catching: the *doer/critic gap*.
4. **Environment → familiarity engine.** The real question isn't "how good is this model" but
   *"what responsibilities has it earned?"* Optimize **regret**, not quality. The unit is the
   **Observation**; the output is a **Model Card**, not a rank.
5. **The counterfactual crack.** Regret is a road-not-taken you can't see — so *run every
   road.* Cheap open-model compute means never run a task once; fan out across models in
   isolation. Counterfactual, sparse-data, and selection bias all die at once.
6. **The cold-start crack.** The flywheel starts empty — so *excavate the past.* Replay real
   `.jsonl` logs through other models; the outcome is free because it already happened. And
   **divergence shouldn't be punished** — which finally gives the LLM-judge a narrow,
   reference-anchored, defensible job.

## Why it's preserved
Two durable lessons:

- **The method:** when a frame breaks, don't patch it — let each objection's *solution* become
  the next reframe. Six turns of "yes, and that breaks because… — oh, then *this*" produced a
  more correct project than any upfront plan would have. The adversary pass wasn't friction;
  it was the engine.
- **The result:** "measure the model" was the wrong question the entire time. "What has it
  *earned*?" reorganizes everything downstream — metric (regret), unit (observation), output
  (card), even the data source (your own history). A subtle shift in the question paid out
  across the whole architecture.

## The trap we named (so we don't fall in it)
Rewarding **similarity-to-Claude** turns the whole engine into a clone detector — it would
punish every model for not being Claude, the exact opposite of the goal. The judge
characterizes *divergence*; it never scores resemblance. Watch for this every time judgment
re-enters.

See: `VISION.md`, `_meta/doctrine.md`, the commission, and the chronicle of this date.
