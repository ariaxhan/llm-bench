---
rite: commission
date: 2026-06-27
repo: CodingVault/llm-bench
slug: model-familiarity-engine
status: complete — replay-bootstrap shipped (feat/replay-bootstrap)
chronicle: _meta/chronicles/2026/2026-06-27-replay-bootstrap.md
---

# Commission — bootstrap the Model Familiarity Engine (replay first)

> Authority and context, not a recipe. Outcomes are yours to solve; the locked facts below
> are not. If you start writing steps, stop and state the outcome.

## Telos of this commission
Turn `llm-bench` from a benchmark into the **Model Familiarity Engine** (`VISION.md`) by
shipping the smallest loop that is *already useful*: replay Aria's real past tasks through
other models, characterize how they diverge from the known-good result, and render one
evidence-backed Model Card. This proves the honest-signal plumbing before any interview rig,
routing, or live shadow-execution is built.

## Authority granted
- Full reign over `CodingVault/llm-bench` source: new `providers/bedrock.py`, a log-mining +
  redaction module, a replay harness, a divergence judge, a card renderer.
- Add deps (boto3, an embedding lib if needed). Install into the venv.
- Spend Bedrock credits on the 3 currently-ACTIVE models (cheap; credit-covered).
- Run git worktree / `git checkout <commit>` to reconstruct repo state for code-task replays.
- Proceed past ambiguity using `doctrine.md`; log the call in the chronicle.

## Boundaries (hard limits)
- **Secrets never leave for a non-Claude provider.** Redact `.jsonl` content (file bodies,
  tokens, keys, private context) BEFORE any replay to Bedrock/OpenAI/etc. This gate ships
  before the first external replay, not after. (I0.9)
- **Never reward similarity-to-Claude.** The judge scores *outcome reached + divergence type*,
  never stylistic resemblance to the reference. A clone detector is a failed build.
- **No number without a floor.** Every score is floor-tested with a dummy answer before it's
  trusted or reported (ethos #2).
- **Leave the unrelated dirty files alone** (`_meta/.session_id`, `_meta/agentdb/agent.db.json`,
  `experiments/floor/*`) — not ours.
- Don't enable new Bedrock models yourself — that's Aria's console click (see Known facts).

## Context (the gift — what you can't easily discover)
- The full reframe arc + rationale: `VISION.md`, this date's chronicle, and the canon
  breakthrough story. Read them first; they hold *why*, not just *what*.
- Prior brainstorm handoffs (historical, now superseded by VISION): `_meta/handoffs/
  workshop-eval-reframe-2026-06-27.md` and `bedrock-providers-2026-06-27.md`.
- A harness audit already found the OLD suite systematically zeros open models for formatting/
  plumbing reasons (reasoning `<think>` traces, fenced JSON, low max_tokens, system-prompt
  rejection → silent 0) and that cost-per-task isn't computable (input/output token split
  discarded). Relevant when you reuse `verify.py` checks as the deterministic layer (D10).
- Frontier grounding (cite in design): regret≈off-policy/contextual-bandit; reference-anchored
  judging (HealthBench) vs free-floating (JudgeBench near chance); divergence taxonomy;
  Benchmarks→Skills low-rank result justifies profiling on a small subset.

## Desired outcomes (end states, not tasks)
- **O1 — Excavated, redacted task corpus.** OUTCOME: a set of `{prompt, trajectory,
  known-outcome, repo-state-ref}` tuples mined from Claude `.jsonl` logs, secrets scrubbed.
  LOOK AT: the jsonl transcript dirs; the project chronicles/git history to label "this
  shipped." VERIFIED: spot-check that a redacted tuple carries zero secrets and still enough
  context to replay.
- **O2 — Replay harness, both conditions.** OUTCOME: re-run a task through ≥2 non-Claude
  models in isolation — cold-prompt AND guided-trajectory (D5b) — with code tasks reconstructed
  at the session's commit in a worktree. VERIFIED: live run on ≥3 real tasks; the original
  Claude result reproduces as the reference.
- **O3 — Reference-anchored divergence judge.** OUTCOME: given prompt + Claude trajectory +
  known outcome + model X output, emit `{reached_outcome, divergence ∈ equivalent|better|
  worse|novel, how}`. VERIFIED: passes the dummy-answer floor; agrees with the cheap objective
  spine where one exists (tests/ship/edit-distance).
- **O4 — One Model Card.** OUTCOME: a rendered card for one model (roles, needs, failure
  modes, pairings, confidence + n), backed entirely by O1–O3 observations. VERIFIED: every
  claim on the card traces to ≥1 observation; confidence reflects real n.
- **(Enabling) Bedrock provider.** boto3 Converse `BedrockProvider`, registered, recording
  input/output token split + cost. Reuse the proven call shape (Known facts).

## Known facts (trust these; do not re-derive)
- AWS profile **`keystone`**, account 114829893009, region **us-west-2**, credit-covered.
- boto3 is **not** installed in the venv — add it.
- Converse call shape & enumeration are documented in `_meta/handoffs/bedrock-providers-
  2026-06-27.md` (use inference-profile ids, not base ids; sync → wrap in `asyncio.to_thread`).
- Only **3 profiles ACTIVE** today: `us.meta.llama4-maverick-17b-instruct-v1:0`,
  `us.meta.llama4-scout-17b-instruct-v1:0`, `us.deepseek.r1-v1:0`. More require Aria's console
  enablement (us-west-2 → Model access). deepseek.r1 emits `<think>` traces — strip before
  judging.

## Questions to challenge (ask before acting; act on the better answer, log why)
- Is regret actually measurable from passive replay, or only with deliberate exploration?
  What's the cheapest *revealed* regret signal in the logs (edits? overrides? retries?)?
- Cold-prompt or guided-trajectory as the primary baseline — or is the *gap* the real metric?
- Where does the similarity-to-Claude trap sneak back in, and how do you prove it didn't?
- Is N-way divergence judging affordable in *attention*, or must the spine auto-decide and the
  human see only finalists?
- Is replaying worth it at all vs just starting the live shadow flywheel? (Argue both.)

## Verification standard
Verified **live**, never off a commit. "Done" = ran the replay, saw the reference reproduce,
saw the judge pass its floor, saw the card render from real observations. Anything that can't
be checked headlessly → a `DEFERRED-*.md` naming the exact human residual.

## Expected chronicle
`_meta/chronicles/2026/<date>-replay-bootstrap.md`. Record: the prompt-vs-trajectory decision,
any divergence the judge called "novel-better" (and whether it held up), and every place the
similarity trap or a floor failure was caught.

## Canon / phronesis extraction rule
- A judge that passed its floor but still rewarded similarity-to-Claude → `canon/failures/`.
- A model that diverged *novel-better* and was right → `canon/breakthroughs/`.
- The replay-vs-shadow tradeoff, once it has real evidence, → candidate `phronesis`.
