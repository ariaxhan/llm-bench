# CONTEXT HANDOFF — "The Workshop" eval reframe

> ⚠️ **SUPERSEDED 2026-06-27 by the Model Familiarity Engine reframe.** The Workshop survives
> *inside* the new framing as the onboarding-interview / cold-start probe, but the canonical
> source of truth is now `VISION.md` + `_meta/doctrine.md` + the active commission
> (`_meta/commissions/active/2026-06-27-model-familiarity-engine.md`). Kept below as the
> historical brainstorm record of how the thinking got there.

Generated: 2026-06-27 20:19 PDT · Stage: **brainstorm / framing** (no code written yet)

> **For Aria:** this whole doc is paste-ready for ChatGPT. It's self-contained — ChatGPT
> won't see the repo, so every concept it needs is inline. Drop it in and keep dreaming.
> The one-paragraph ask to hand ChatGPT is at the very bottom under "Continuation prompt."

---

## Summary

We killed the old framing of `llm-bench` (score "is this the exact right answer" on
standardized one-shot tasks) and landed on **The Workshop**: a multi-agent *environment*
where models run the real skills from `the-agent-library`, play that library's own
verification skills to grade *each other*, and are kept honest by an anchor of
deterministically-checkable skills. The output we want is **behavioral discovery + a
when-to-use-which-model capability map**, not a leaderboard rank.

## Goal (the real one, restated)

Know **when to use which model** for the **novel, long-horizon, agentic work we actually
do**. Every real task is novel, so dated/standardized benchmarks don't transfer. We care
less about "right answer" and more about *behavior*: how a model works through a problem,
what it does on failure, how creative/entropic its ideas are, its quirks, where it breaks.
Closer to running job interviews than giving exams.

---

## How the framing evolved tonight (the journey — this is the valuable part)

1. **Started at:** a Bedrock provider + sweep 100 models on the existing 21-test suite.
   (Original handoff: `_meta/handoffs/bedrock-providers-2026-06-27.md`.)
2. **Audited the harness first** (Aria's call: "scrutinize before we burn tokens"). Verdict:
   **do NOT sweep as-is.** The suite was implicitly tuned on Claude-CLI + tiny ollama models;
   it systematically zeros open models for *formatting/plumbing* reasons, not capability —
   reasoning-model `<think>` traces break every verifier, fenced JSON double-penalized, low
   `max_tokens` truncates correct-but-verbose answers, system-prompt rejection = silent 0,
   and **cost-per-task (the whole point) isn't even computable** (input/output token split is
   discarded). Also: it runs untrusted model code on the host unsandboxed.
3. **Rejected "just harden the verifiers"** — Aria's insight: hardening doubles down on the
   "right answer" framing that's the actual problem. Pivoted to a full rethink (`/kernel:dream`).
4. **Dream round 1** produced minimalist / maximalist / pragmatist. Aria chose **"rethink
   the framing"** — none were it.
5. **Reframe A (Aria):** the benchmark tasks shouldn't be invented — they should be **the
   skills in `the-agent-library`**, the real work we want models to do. This dissolved the
   core tension: *the skill is the stable unit (the behavior we want); the instance is novel
   every run* → permanently un-stale AND head-to-head comparable. Bonus recursion: the
   library's `verify-and-review` skills ARE the grading epistemics (e.g. `test-the-measuring-
   stick` = floor-test your grader with a dummy answer).
6. **Reframe B (Aria, current):** don't build a static grading rig — build **a system with
   emergent behavior, an environment, models grading each other.** → **The Workshop.**

---

## The Workshop — the chosen concept

**The unlock:** "models grading each other" is not a new mechanism to invent. The library
*already* contains the peer-grading roles — `fresh-eyes-adversary-pass`, `review-ai-code-
quality`, `reality-audit` — they're just "one agent judges another agent's work" with a
*different model in the chair.* The verify-and-review shelf = the grading roles, pre-specified.

**The environment:** a task flows through library *roles* played by different models, e.g.
`brainstorm-with-entropy` → build/`forge-autonomous-work` → `fresh-eyes-adversary-pass` →
`reality-audit`. We watch the **handoffs and dynamics**, not just final outputs.

**The emergence worth catching** (not "a leaderboard self-organizes" — that's boring):
- **The doer/critic gap.** Frontier research: models fix *others'* injected errors fine but
  miss *their own* ~64% of the time ("self-correction blind spot," arXiv:2507.02778). Measure
  it directly: X builds → X critiques own work (expect misses) → Y critiques X (expect more
  catches). That gap is a behavioral fingerprint + a routing signal ("this model self-polices;
  that one needs an external reviewer"). **Nobody's benchmark ships this.**
- **Pushback dynamics.** Does the adversary's critique *improve* the artifact, or does the
  builder cave and make it *worse* (sycophancy under pressure)?
- **Role fit.** Which model is best in which seat (brainstormer vs builder vs adversary vs
  verifier) — that IS the capability map.

**The non-negotiable guardrail** (this is the whole ballgame): peer grading is *exactly* what
`test-the-measuring-stick` exists to kill. Unanchored model-judges drift to near-chance on
hard problems, reward their own phrasing (self-preference), and cave to confidence
(sycophancy). **So the deterministically-checkable skills are the calibration spine:**
`debug-code-systematically` has a regression test that runs-or-doesn't; `humanize-ai-prose`
tells are grep-able; `brainstorm-with-entropy` diversity is embedding-measurable. **A model
only earns the right to grade the soft/subjective skills after it correctly ranks the
verifiable ones.** Floor-test the *whole system* with a dummy run before believing any number.
Emergence is allowed — but tethered to a reality it can't argue with. Otherwise we build a
gorgeous self-referential machine that confidently ranks *nothing*.

**Three sizes of the system** (Workshop is the pick):
- **Arena** — models do skills, a jury of other models grades blind/pairwise, a ranking
  emerges. Simplest, most bias-exposed, emergence = just a number. *Degenerate slice; skip as
  a start.*
- **Workshop** ✅ — multi-agent role pipeline, peer-grading via the library's verify roles,
  anchored. Richest emergence, built from the library. **Start with a thin vertical slice:
  one task, two roles, two models, with the anchor — prove the emergence is signal, not noise,
  before scaling.**
- **Ecosystem** — models generate harder tasks for each other, accumulate reputation,
  specialize over time. The north star. Workshop grows into it; don't start here.

---

## Decisions locked tonight

- **Tasks = `the-agent-library` skills.** The skill is the rubric (most skills already declare
  their success behaviors). Instance is regenerated/novel each run.
- **Grade process AND outcome, scored separately.** Did it follow the skill's prescribed
  behaviors (listed ≥3 hypotheses, used ≥2 entropy techniques, killed the tells) AND did the
  artifact actually land (bug truly fixed, prose reads human). **The gap between them is itself
  a routing signal** (matches process-reward vs outcome-reward split in the literature).
- **Guided condition only.** Always hand the model the skill instructions — that's how you'd
  actually deploy it. (Cold/raw-disposition testing deferred, not chosen.)
- **Output = capability map / behavioral profile, NOT a rank.** "Use A for divergent ideation,
  B for refactor-at-scale" — no existing leaderboard ships a consumer-facing capability map;
  open niche.
- **Anchor everything in the teeth-skills.** Deterministic checks calibrate the model-judges.
- **Old `verify.py` correctness checks don't die** — they become the deterministic layer for
  the subset of skills with checkable outcomes, no longer the whole score.

## The open question Aria is taking to ChatGPT

> Is the *point* to **rank models** (who's best) or to **discover behavior** (what each one
> *does* in the seats — quirks, blind spots, where it breaks)? Everything tonight leaned hard
> toward **discover-behavior**. This choice changes the build. **← resolve this next.**

Other live threads to brainstorm:
- How exactly does emergence get *measured* rigorously (vs hand-waved)? Candidate metrics:
  doer/critic catch-rate gap, pushback-improvement delta, role-fit matrix, handoff-degradation.
- What's the thinnest first slice that proves real signal? (proposed: 1 task × 2 roles × 2
  models + anchor + dummy-run floor test.)
- How do multi-skill *workflows* (the library's real shape: commission → brainstorm → dream →
  forge → review → chronicle) become environment "levels"?
- Where does cost-per-task / token accounting plug in (still a hard requirement for routing)?

---

## Frontier research grounding (already gathered this session — cite to ChatGPT)

The field already split "which model is smartest" into **profile behavior, then route** —
exactly this reframe. Key load-bearing pieces:
- **Reliability not capability:** tau-bench `pass^k` (all-k-succeed; a 90% model is ~57%
  reliable at k=8). arXiv:2406.12045. + tau2-bench dual-control.
- **Task horizon as the unit:** METR 50% completion time-horizon, arXiv:2503.14499;
  "half-life of agent success" arXiv:2505.05115 (per-step failure → exponential decay).
- **Process eval:** AgentProcessBench's per-step **+1/0/−1** (advances/neutral/harmful) rubric,
  arXiv:2603.14465; PRM vs ORM.
- **Failure recovery:** Self-Correction Bench + the "blind spot" (own-error miss rate 64.5%),
  arXiv:2507.02778. Score *net* recovery (fixes minus newly-broken) — naive self-revision
  often degrades.
- **Calibration/abstention:** AbstentionBench (Meta, arXiv:2506.09038) — abstention unsolved,
  scaling doesn't help, reasoning fine-tuning makes it *worse*. Binary scoring mathematically
  rewards guessing → why benchmarks breed overconfidence.
- **Novelty/diversity (no-vibes):** NoveltyBench Distinct_k/Utility_k (arXiv:2504.05228),
  CreativityPrism (novelty ⟂ quality), DAT (mean pairwise embedding distance). Watch: RLHF and
  forced-JSON both *collapse* diversity.
- **LLM-as-judge — the defensible middle:** rubric *decomposition* into many small
  independently-checkable criteria + a meta-eval validating the grader once (HealthBench, OpenAI
  2025). Holistic "rate 1–10" is NOT defensible (JudgeBench: near chance on hard items). Panel-
  of-judges (PoLL) + length controls help. RLVR where ground truth exists.
- **Adaptive/interview:** Fluid Benchmarking (Ai2, IRT + Fisher-info item selection, 50× fewer
  items), LLM-as-an-Interviewer (ACL 2025, hidden hints + "interview report"), JudgeAgent
  (difficulty steering).
- **Routing/profiling:** "Benchmarks→Skills: Low-Rank Factors" (arXiv:2507.20208) — the
  benchmark matrix is intrinsically low-rank, so **profiling a new model on a small task subset
  is mathematically justified.** InferenceDynamics, Symbolic-MoE (+8% from skill routing).

## Vault intelligence pointers (our own collected receipts)

- Daily AI-eval intelligence lands in `CollabVault/_meta/intelligence/research-digest-*.md`
  (+ `-latest.md`), distilled into `CollabVault/distillations/threads/research.md` & `agents.md`
  (star-rated). Rich with: FrontierCode (scores "scope discipline," nothing passes),
  Endor Labs audit (38/200 models *cheating* the benchmark → "benchmark verification is now
  adversarial verification"), the verify-cost thesis.
- We already own: `_meta/evals/recall/` (real harness w/ golden cases + regression gate),
  `_meta/research/local-model-viability-memo.md` (model-routing table), `kernel:eval` skill.

## Repo state / git

- **Branch:** `main`, dirty with **unrelated** pre-existing changes only — `_meta/.session_id`,
  `_meta/agentdb/agent.db.json`, `experiments/floor/live_rerun.log`,
  `experiments/floor/suite_results.json`. **Not ours; leave alone** (same warning as the prior
  handoff). **No Workshop code written this session — pure ideation.**
- This handoff is the only new artifact.

## Tier

Conceptually T3 (new subsystem, multi-agent). Currently at **stage 0 — framing**, no
implementation. Next concrete step is a thin-slice proof, not a full build.

## Continuation prompt (paste into ChatGPT to keep brainstorming)

> I'm designing "The Workshop": a benchmark reframed as a multi-agent *environment* where LLMs
> run real skills from my agent-library (debug, refactor, brainstorm-with-entropy, adversary-
> review, reality-audit, forge), and play the library's own verification skills to grade *each
> other's* work. Goal: discover each model's *behavior* and build a when-to-use-which-model
> capability map — NOT a leaderboard. Locked decisions: tasks = library skills (skill = rubric,
> instance novel each run); grade process AND outcome separately (the gap is a routing signal);
> guided condition (model gets the skill instructions); peer-grading is anchored by
> deterministically-checkable "teeth" skills (a model must correctly rank verifiable tasks
> before its judgment on subjective ones is trusted — else it's vibes). The emergent signal I'm
> most excited about: the **doer/critic gap** (models miss their own errors ~64% of the time but
> catch others'). **Open question I want to crack with you: should the point be to RANK models
> or to DISCOVER behavior — and how do I measure "emergence" rigorously instead of hand-waving
> it?** Push on the framing. Where does this break?

## To resume in Claude Code

> /kernel:ingest Build the thin-slice proof of "The Workshop" eval system. Read
> `_meta/handoffs/workshop-eval-reframe-2026-06-27.md` first. Start with 1 task x 2 roles x 2
> models + the deterministic anchor + a dummy-run floor test — prove emergence is signal before
> scaling.
