---
rite: chronicle
date: 2026-06-27
repo: CodingVault/llm-bench
commission: 2026-06-27-model-familiarity-engine
branch: feat/replay-bootstrap
status: complete
---

# Chronicle — replay bootstrap (first build of the Model Familiarity Engine)

Honest account of building the smallest useful loop: replay real past tasks through
non-Claude models, characterize divergence from the known outcome, render a Model Card.
Includes the two corrections Aria forced mid-build and the two bugs verification caught.

## What shipped

The full loop, verified live on AWS Bedrock (profile `keystone`, us-west-2, ZDR):

1. **Redaction gate** (`familiarity/redact.py`) — fail-closed. Scrub + independent
   re-scan (`assert_clean`) that refuses to send if any secret survives. Live floor:
   redacting 40 real transcripts caught 3261 home-paths, 113 emails, **4 real secrets**,
   with **0 leaks** surviving the verifier.
2. **Bedrock provider** (`providers/bedrock.py`) — Converse, records input/output token
   split + cost, separates reasoning-model `reasoningContent` from the final answer.
3. **3 real-bug tasks** (`familiarity/tasks.py` + `pilot_corpus.json`) — reconstructed
   from real session logs of paper-rooms / our4cuts / modelmind (below).
4. **LLM judge** (`familiarity/judge.py`) — Qwen3-235B (neutral, non-subject), anchored
   to the objective outcome, with a deterministic spine cross-check.
5. **Replay harness** (`familiarity/replay.py`) — cold + guided, redaction enforced at
   the send boundary.
6. **Model Cards** (`familiarity/card.py`) — rendered from real observations, honest n.

## Challenge decisions (made before coding, per the commission)

- **Regret is NOT measurable from passive logs.** Logs hold one road (Claude's); regret
  is the counterfactual. The replay *generates* the counterfactual, so the pilot measures
  **divergence**, not regret — and the card carries no "regret score." Cheapest revealed
  signal in logs = edits/overrides/retries on Claude (left for phase 2).
- **The gap (cold vs guided) is the metric, but n=3 is too small to score it.** Reported
  qualitatively. For these one-shot diagnosis tasks the gap is thin by construction; rich
  trajectory-replay needs multi-step tasks (phase 2).
- **Similarity trap doors:** the judge prompt, the outcome label, and the
  reference-reproduce step. Closed by anchoring the judge to the *objective outcome* (never
  Claude's text) and floor-testing with a differently-worded-correct probe.
- **Replay-first justified by judge-proving, not just cold-start:** the one place we have
  ground truth to floor-test the measuring stick before trusting the live flywheel.

## Two corrections Aria forced (both right)

1. **"shouldn't the judge be an LLM call, not a script?"** — Yes. The first design made the
   judge a deterministic string-matcher and called blindfolding it "anti-trap." That's a
   clone-detector-by-another-name and it cannot do the actual product job (characterize
   *how* a model diverged, catch novel-better). Corrected: spine stays a script as the
   **calibration anchor**; the **judge is an LLM** anchored to the outcome, floor-tested.
2. **"I don't like the tasks — they're weird."** — Right again. The first task set
   (`gpu_cost`, `avg_bug`, `einstein`) were **eval fixtures** from llm-bench's own logs —
   replaying our own benchmark, not real work. Corrected to **real bugs Aria hit** in her
   product repos. (→ canon/phronesis: mine product repos, never the bench's own logs.)

## The three real tasks (excavated, not generated)

- `ios_zoom` (paper-rooms) — iOS WKWebView auto-zoom on inputs <16px. Domain: mobile CSS.
- `cover_crop` (our4cuts) — 3:4 cover card vs 9:16 strip + object-fit cover crops it.
- `revenuecat_permonth` (modelmind) — `priceString` (whole-period $79.99/yr) assigned to
  `pricePerMonth` → renders "$79.99/mo"; fix is ÷12. Domain: payments/API semantics.

## Two bugs verification caught (the discipline working)

1. **MiniMax M2 produced empty answers.** As a reasoning model it spent the entire 4096
   output-token budget on `reasoningContent` and emitted no final text. Its whole first
   card was built on empty answers. Fix: budget → 12000 (it answers fine at 8000).
2. **Judge answer-key leak on empty input.** The judge scored *some* empty answers
   `reached=True` — reading the known-correct outcome from its own prompt and rubber-
   stamping it onto nothing. The floor test never probed empty input, so it missed this.
   Fix: empty output short-circuits to `worse` *before* the LLM call; added empty-answer
   floor probes. **This was a real floor GAP** — floor tests must include degenerate
   (empty/blank) inputs, not just garbage and correct-but-different.

## Findings (n=6 per model — pilot, not powered)

- **Judge floor: PASS** — garbage→not-reached, differently-worded-correct→reached,
  empty→not-reached. No similarity trap: differently-worded-correct scored equivalent/
  better, never worse-for-not-looking-like-Claude.
- **DeepSeek V3.2: 6/6 reached, all "better."** Strong debugger across all 3 domains.
  ~7.5s latency, ~$0.0011/task.
- **MiniMax M2: 5/6 reached.** Misdiagnosed the RevenueCat bug **cold** (blamed a wrong
  `annual` flag, not the `priceString`→`pricePerMonth` assignment); got it **with guidance**.
- **The RevenueCat-cold cell is the discriminator** — the subtlest task (API semantics).
  Cold performance there is unstable (DeepSeek failed it run 1, passed run 2) — n=1 per
  cell, do not over-trust a single cell.
- **Every spine/judge disagreement was a spine error the judge corrected** (the keyword
  spine both false-positives and false-negatives on free-form answers). Empirically
  validates LLM-judge-over-script — the exact correction Aria forced.

## Honest limitations

- n=6 per model. Pilot, not powered. Two models, three tasks, one judge.
- One-shot tasks make the cold/guided gap thin; "guided" is a method hint, not a real
  multi-step trajectory.
- The judge is a single model (Qwen); no judge-ensemble or judge-vs-judge yet.
- Cold-cell nondeterminism observed; powered runs need repeats per cell.

## Canon / phronesis candidates

- **Floor tests must include degenerate inputs** (empty/blank), not only garbage and
  correct-but-different — the answer-key-leak gap is invisible otherwise. (→ phronesis)
- **Replay tasks come from product repos, never the bench's own eval logs.** (→ canon)
- The judge passed its floor *including the trap probe* → no `canon/failures` entry; the
  anti-similarity-trap design held.
