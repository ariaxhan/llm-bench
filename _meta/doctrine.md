---
rite: doctrine
level: project (CodingVault/llm-bench)
updated: 2026-06-27
status: provisional — every belief below is a falsifiable bet, held until evidence kills it
---

# Doctrine — current best beliefs (provisional, falsifiable)

These are the design bets the Model Familiarity Engine rests on. Each is held *because it
hasn't been falsified yet*, not because it's proven. Each names what would kill it.

**D1 — The unit is the Observation, not the test.**
Trust emerges from accumulating `{model@version, role, task, outcome, regret, surprise,
evidence}`, not from a fixed task battery.
*Falsified if* observations prove too sparse/noisy to ever yield a stable card and a fixed
suite would have converged faster.

**D2 — Regret is the optimization target, not quality.**
Regret absorbs quality, cost, latency, supervision, and editing effort with no arbitrary
weights. We minimize expected regret.
*Falsified if* regret can't be measured cheaply enough to beat a simple quality+cost score in
practice.

**D3 — Counterfactuals are run, not estimated.**
Open-model compute is cheap, so instead of off-policy guessing we fan tasks out across
multiple models in isolation (worktrees) and observe the actual alternatives.
*Falsified if* fan-out cost (tokens + worktree overhead + adjudication attention) exceeds the
value of the counterfactual for most task types.

**D4 — Cold-start is solved by replaying historical logs.**
Aria's `.jsonl` logs are thousands of real tasks with *already-known* outcomes — ground truth
to excavate, not generate. The engine is born knowing things.
*Falsified if* the initial-prompt-vs-trajectory gap (D5b) or environment-reconstruction
fidelity makes replayed results un-comparable to the original run.

**D5 — LLM-judging is defensible only as reference-anchored divergence characterization.**
Given the prompt + Claude's trajectory + the known outcome + model X's output, the judge
answers a *bounded comparative* question (reached the outcome? how did it diverge?). This is
the HealthBench-style defensible middle, not free-floating "rate 1–10" (JudgeBench: near
chance on hard items).
*Falsified if* even reference-anchored judges fail the dummy-answer floor or disagree with the
cheap objective spine.

**D5b — Prompt-replay and trajectory-replay measure different things; run both.**
Replaying the *initial prompt* tests cold one-shot under-specification (how little
hand-holding a model needs). Replaying the *whole trajectory* tests "could it have done what
Claude did with the same guidance." The gap between them is itself a model trait.

**D6 — The divergence taxonomy is the product.**
`equivalent / better / worse / novel`, per model per task-class, *is* the behavioral
fingerprint and the routing knowledge. A scalar rank is a lossy projection of it.

**D7 — Async-shadow by default; best-of-N is opt-in.**
The live path runs the trusted model and returns immediately; shadows run in the background
and land as observations later. Real work is never blocked on the experiment. Sync best-of-N
(wait, take the winner) is a deliberate "this one matters" switch.
*Falsified if* async observations arrive too late/decoupled to be attributable, forcing sync.

**D8 — Routing is explore-exploit; treat it as a contextual bandit.**
This hands clean answers to the open questions: **surprise** = exploration bonus (Thompson/
UCB); **version change** = prior reset, not smooth decay; **onboarding never ends**; deliberate
exploration (sometimes route against current belief) is required or the engine learns a map of
its own habits, not the models.

**D9 — The fan-out boundary is purity, not just the filesystem.**
Worktrees isolate *files*; they do not isolate *side effects* (emails, paid APIs, deploys,
DB writes). Automatic fan-out is for **pure/sandboxable** tasks only; side-effecting tasks are
gated, dry-run/mocked, or fan out only their reversible prefix.

**D10 — The old correctness verifiers survive as the deterministic layer.**
`verify.py`'s programmatic checks aren't discarded — they become the cheap objective spine for
the subset of skills/tasks with checkable outcomes. They are no longer the *whole* score.

---
*Promotion rule:* a belief that survives repeated real evidence graduates toward
`phronesis`; one that gets falsified is struck here with a dated note and its story goes to
`canon/failures/`.
