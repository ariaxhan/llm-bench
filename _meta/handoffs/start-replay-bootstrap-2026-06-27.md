# START HERE — execute the replay-bootstrap commission

Generated: 2026-06-27 · For: a fresh session picking up the first build of the Model
Familiarity Engine. This is an ignition brief, not the spec — the spec is the commission.

## Read first (in order)
1. `_meta/commissions/active/2026-06-27-model-familiarity-engine.md` — the commission. Outcomes
   O1→O4, authority, boundaries, known facts, questions-to-challenge. **This is the contract.**
2. `VISION.md` — why (Model Familiarity Engine; regret; observations; Model Cards).
3. `_meta/doctrine.md` — the falsifiable bets you're building on (D1–D10).
4. `_meta/handoffs/bedrock-providers-2026-06-27.md` — the proven Bedrock Converse call shape.

## The job, in one breath
Build the smallest honest loop: mine Aria's Claude `.jsonl` logs → **redact secrets** →
replay ~3 real tasks through ≥2 non-Claude models in isolation (cold-prompt + guided-trajectory)
→ judge divergence against the **known** outcome (reached? equivalent/better/worse/novel) →
render **one Model Card** from real observations. Verified live, every number floor-tested.

## First concrete moves (T2/T3 — orchestrate, don't freestyle)
1. `agentdb read-start`; re-read this + the commission.
2. **Challenge the commission's questions BEFORE coding** (regret measurable from passive logs?
   prompt vs trajectory baseline? where does the similarity trap re-enter?). Act on the better
   answer, log why. This is required, not optional.
3. Locate the `.jsonl` transcript dirs; prototype the **redaction gate first** (O1) — nothing
   leaves for Bedrock until secrets are scrubbed (I0.9, hard boundary).
4. Add boto3 + `providers/bedrock.py` (Converse, record input/output token split + cost).
5. Then O2 replay → O3 divergence judge (floor-test it) → O4 one card.

## Non-negotiables (carry across the window)
- Secrets never leave for a non-Claude provider — redact before any external replay.
- Never reward similarity-to-Claude; characterize divergence. Clone detector = failed build.
- No number trusted without a dummy-answer floor test.
- Verified **live**, never off a commit. Pilot ≠ powered; report n + provenance.
- Leave the unrelated dirty files alone (`_meta/.session_id`, `agentdb/agent.db.json`,
  `experiments/floor/*`). Only 3 Bedrock profiles ACTIVE — don't enable more (Aria's console).

## Done =
Ran the replay live, the original Claude result reproduced as reference, the judge passed its
floor, and one Model Card rendered with every claim tracing to a real observation. Then:
chronicle → `_meta/chronicles/2026/2026-06-27-replay-bootstrap.md`, move the commission to
`complete/`, `agentdb write-end`.
