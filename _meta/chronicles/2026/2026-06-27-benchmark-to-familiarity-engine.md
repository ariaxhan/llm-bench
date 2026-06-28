---
rite: chronicle
date: 2026-06-27
commission: _meta/commissions/active/2026-06-27-model-familiarity-engine.md
repo: CodingVault/llm-bench
window: solo session (Aria + main agent), pure ideation — no code shipped
---

# Chronicle — the night llm-bench stopped being a benchmark

## What I was asked to do
Start as: add a Bedrock provider and sweep ~100 open models through the 21-test suite (per
`_meta/handoffs/bedrock-providers-2026-06-27.md`). Aria attached one condition up front:
*"the testing harness itself needs scrutiny before we burn tokens."* That condition ate the
whole session — and turned the project into something else.

## What I did
- **Audited the harness before spending** (Aria's call). Spawned a Plan-agent deep read of
  `verify.py`, the 5 suites, `scoring/`, `floors.py`, the floor experiments. Verdict: do NOT
  sweep as-is — the suite was tuned on Claude-CLI + tiny ollama models and systematically
  zeros open/reasoning models for *formatting/plumbing* reasons (reasoning `<think>` traces
  break every verifier, fenced JSON double-penalized, low `max_tokens` truncates correct
  answers, system-prompt rejection → silent 0), and **cost-per-task isn't computable** (the
  input/output token split is discarded). Also: it executes untrusted model code unsandboxed.
- **Confirmed the Bedrock ground truth:** boto3 not installed; only 3 ACTIVE profiles today;
  the rest need Aria's console enablement.
- **Offered the obvious fix (harden the verifiers) — Aria rejected it** as doubling down on the
  broken "right answer" frame. Pivoted to `/kernel:dream`.
- **Gathered grounding in parallel:** one agent mined our own vault eval intelligence
  (`CollabVault/distillations/threads/research.md`, the daily `research-digest` flow, the
  `_meta/evals/recall/` harness we already own); another swept the 2025-26 frontier (τ-bench
  pass^k, METR time-horizon, AgentProcessBench, Self-Correction blind spot, NoveltyBench,
  HealthBench, Fluid Benchmarking, Benchmarks→Skills low-rank). Both came back rich; cited
  throughout `doctrine.md` and `VISION.md`.
- **Ran the dream + five further reframes** as a live adversary↔builder loop with Aria (see the
  canon story for the chain). My role was the adversary pass each turn; Aria cracked each
  objection. Net result: a coherent system, not a patched benchmark.
- **Captured everything in the tradition** (this is what "no code, but real work" looks like):
  wrote `VISION.md`, `telos.md`, `ethos.md`, `doctrine.md` (D1–D10), the active commission, a
  canon breakthrough story, and this chronicle. Superseded the two brainstorm handoffs with a
  pointer. Created `_meta/commissions/` + `_meta/canon/` scaffolding.

## What I found (the reframe, in one line each)
- The wrong question was *"how good is this model?"*; the right one is *"what has it earned?"*
- Optimize **regret**, not quality. Regret is a counterfactual → so **run every road** (cheap
  open-model fan-out in isolation) instead of estimating it.
- Cold-start the engine by **replaying real `.jsonl` logs** — outcomes already known.
- **Divergence is data, not error** — which finally gives LLM-judging a defensible,
  reference-anchored job, and exposes the clone-detector trap (never reward similarity).
- The core object is the **Observation**; the product is a **Model Card**, not a rank.

## What failed / honesty
- **My first instinct was wrong.** I was ready to spend the session hardening verifiers — the
  exact move Aria correctly killed as solving the wrong problem. The good outcome came from her
  reframes, not my initial plan. Logged because the lesson (patching a broken frame vs
  replacing it) is the whole point of the canon entry.
- **One AskUserQuestion got rejected mid-flow** when Aria wanted to redirect rather than pick
  from my options. Right call by her; the menu would have railroaded a live brainstorm.
- **The secret-scanner blocked a handoff write** on a false positive ("ta**sk-completion-time**"
  matched the `sk-…` key pattern). Reworded, re-wrote. The gate did its job; no bypass.
- **No code exists.** This is a stage-0 concept session. Every claim about the *build* is a
  bet in `doctrine.md`, not a verified result. Calling this "done" would violate our own
  verify-live ethos — it's *captured*, not *built*.

## Disagreement / coordination
The entire value came from disagreement held productively: I pushed hard on every reframe
(counterfactual-regret is unobservable; isolation is a filesystem lie not a side-effect lie;
the similarity-detector trap; secrets leaving for Bedrock; prompt ≠ trajectory). Aria's
answers turned each objection into the next design layer. Neither of us could have reached the
familiarity-engine framing alone — it's a genuine adversary/builder co-product.

## Verdict
llm-bench is no longer a benchmark. It is a **Model Familiarity Engine** (`VISION.md`),
captured in the tradition and scoped to a first build (the replay bootstrap,
`commissions/active/2026-06-27-model-familiarity-engine.md`). The pivot **earned its next
step** — it is not proven. Next session: build the smallest honest loop (mine logs → redact →
replay 3 real tasks through 2 models → divergence-judge against known outcomes → render one
Model Card), verified live, anchored to cheap objective signal, floor-tested before any number
is believed.
