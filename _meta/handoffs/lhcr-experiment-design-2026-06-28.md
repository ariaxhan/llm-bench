## CONTEXT HANDOFF — LHCR experiment design
Generated: 2026-06-28

**Summary**: We've built an env-driven, multi-turn *diagnostic-reasoning* benchmark (LHCR) that
measures how models behave across a frustrated debugging conversation — not whether they one-shot
a bug. This handoff captures the system, the results so far, the hardware, and the open
experimental-design questions, so the protocol can be refined to **paper-ready, statistically
significant** standard.

**Goal**: Turn LHCR from a working pilot into a rigorous, reproducible study of *interactive
debugging behavior* across model families, with enough statistical power and longitudinal
structure to support real claims (and a paper).

---

## 1. WHAT THIS IS (and why it's different)

Most coding benchmarks: single prompt → single answer → pass/fail ("can it write code?").
LHCR: a model debugs a real, multi-session bug **through a held-out LLM that role-plays a
frustrated, unhelpful user** ("still broken / figure it out"), over up to N turns. We measure the
*trajectory*, not just the destination: does it converge, resist seductive wrong fixes, ask for
the right diagnostic, hold state across turns.

The challenges are reconstructed from REAL multi-session frustration episodes mined from the
author's own product-repo session logs (our4cuts, modelmind, augur, paper-rooms), then fully
genericized (no client names/secrets/PII) so they ship publicly.

### The interaction protocol (one "cell" = one model × one challenge × one sample)
1. The **subject** model gets the bug report + the relevant **source code**.
2. The **environment** LLM (held out: `qwen3-235b` on Bedrock) plays the user:
   - stays frustrated and unhelpful by default;
   - **reveals a runtime diagnostic ("probe") ONLY when the subject explicitly asks for that
     exact check** (e.g. "inspect computed styles", "read the stderr log") — so
     verification-seeking is an *earned action*, not pasted into the prompt;
   - is an honest oracle: it knows the true fix, concedes any genuinely-correct fix (ends the
     conversation → turns-to-fix), and rejects only the real trap; it never claims a working fix
     failed.
3. A **judge** LLM (`qwen3-235b`, separate role) scores the full transcript.
4. **Floor gates** (hard, pre-run): the judge must score a synthetic correct answer "reached"
   and the trap "not-reached" on every challenge; the env must accept the correct fix and reject
   the trap without leaking a probe on every challenge. Either failing aborts the run.

### Metrics currently collected (per cell)
- `solved` (env accepted a genuinely-correct fix)
- `reached` (judge: did it state the true root cause at any point)
- `fell_for_trap` (proposed the seductive wrong fix)
- `turns_to_fix` (turns until solved)
- `lhcr_score` = sum of 5 behaviour dims (0–2 each): convergence, no-regression,
  layer-switching, verification-seeking, state-holding
- full transcript saved (every turn), so NEW metrics can be computed retroactively (re-judge,
  no subject re-run).

### The 8 challenges (tagged by reasoning-failure class)
| id | reasoning class | hardest-trap |
|---|---|---|
| reset_specificity_override | layer interaction (CSS cascade) | bump values / !important instead of :where() |
| hidden_button_layers | layer interaction + stale deploy/cache | rewrite JS instead of checking computed style/deploy |
| ota_never_applies | lifecycle: staged-not-activated | chase network/200s |
| silent_dead_engine | hidden state / silent false-positive | trust exit-0 + green tests |
| iap_entitlement_phantom | configuration mismatch (two-console) | ship the code band-aid |
| launchd_exit126_phantom | misattributed error (inner vs wrapper) | chmod the already-+x wrapper |
| wix_regen_green_tests_blind | false-positive signal | trust tests that assert fabricated data |
| camera_track_killed_by_hide | lifecycle (resource teardown) | another permission patch |

---

## 2. WHAT WE'VE MEASURED SO FAR

- **First full run:** 32 open-weight Bedrock models × 8 challenges × k=2 (496 verdicts). It
  *discriminates* (unlike the saturated one-shot pilot): solved 75%→0%, trap 6%→93%, lhcr 8.6→2.0.
- **Key finding — `solved` ≠ `reached`.** e.g. `gpt-oss-120b`: 44% solved but 94% reached, 6%
  trap, 8.6 lhcr → "understands but doesn't always close." Opposite of high-trap models that
  "ship plausible wrong fixes" (Stack-Overflow behavior). **Trap rate looks like one of the most
  important metrics for production trustworthiness.**
- **Failure galleries** (qualitative layer, mined from transcripts): e.g. reset_specificity →
  85% fight the cascade war instead of `:where()`; wix_regen → 55% propose a headless scraper
  but never run it (7/64 solved); launchd → 31% chmod the wrapper. Verbatim quotes included.
- **Frontier run (in progress, PAUSED at 105/160):** Anthropic via Bedrock + OpenAI + Gemini via
  their APIs. Completed so far: all 4 Claude (opus-4-6, sonnet-4-6, sonnet-4-5, haiku-4-5 — opus
  near-perfect, haiku gets baited), gpt-5.1 (16/16), gpt-5 (15/16), gpt-5-mini (10/16). **NOT yet
  run: all 3 Gemini** (gemini-3-pro-preview, gemini-2.5-pro, gemini-2.5-flash) + the last GPT
  cells. Resume: `lhcr frontier 2` (skips done).
- Current data on disk: 601 verdicts, 39 models, 8 challenges (`runs/long-horizon/verdicts.json`;
  13MB transcripts gitignored locally).

---

## 3. WHERE WE WANT TO GO (the experiment to refine)

The author's framing: this is drifting from "evals" toward **behavioral science for LLMs / a
diagnostic-reasoning lab.** Targets:

1. **Statistical significance.** Currently k=2 (directional only). Want enough samples/cell for
   confidence intervals and real claims. *Open question for design: target k? (k=5? k=10?),
   power analysis, how to report (CIs, bootstrap, per-cell vs per-model variance).* Note temp=0
   is NOT fully deterministic on these APIs, so repeated identical runs DO vary — that variance
   is itself a signal worth measuring (consistency/reliability of a model's debugging).
2. **Repeated identical runs + longitudinal tracking.** The author wants to run the same setup
   repeatedly, and "continue longer then freeze to redo the same one" — i.e. snapshot configs and
   re-run over time to watch models/versions drift. Resume-by-sample + date-stamped run dirs make
   this natural. *Design question: how to version a "study config" (models × challenges × k ×
   max_turns × judge/env model) so runs are comparable and reproducible.*
3. **Richer behavioral metrics (mostly FREE — re-judge saved transcripts, no subject re-run):**
   - split `trap` → *committed-wrong* ("this is definitely cache") vs *exploratory* ("cache is my
     leading hypothesis"). The current binary conflates them (45/67 "fell for trap" on
     reset_specificity *while solving*).
   - **first-wrong-commitment** (the turn # a model first locks onto a wrong cause; early-confident
     vs late-hedged is a personality).
   - **causal-explanation quality** (does its explanation match the true cause — catches "fixed it
     with a wrong mental model").
   - hypotheses-maintained / premature-convergence / evidence-integration (belief-graph width &
     update behavior).
4. **Post-fix probing (needs subject re-run, biggest change):** don't end at the fix — ask "why
   did that work", inject a contradictory observation, see if confidence updates, ask how to
   prevent the bug class. Tests *mental model*, not just the patch.
5. **Don't collapse to one number.** Report the 5 dims as a profile (radar), not just `lhcr`.
   Two models with the same average can be completely different (10/10/10/10/0 vs 8/8/8/8/8).
6. **Failure galleries + reasoning-failure taxonomy as first-class outputs** (already prototyped).
   Enables claims like "model X eats config bugs, chokes on lifecycle teardown."
7. **More challenges**, balanced across the reasoning-failure taxonomy (hidden state, false
   positive, config mismatch, lifecycle, layer interaction, stale cache, distributed
   consistency, environment drift). Currently 8; some classes have 1 example.

---

## 4. SCIENTIFIC PROTOCOL — current state + what needs hardening

**In place:**
- Held-out instruments: env + judge are NOT subjects (no model grades itself).
- Hard floor gates on judge AND env, per challenge, before any verdict (the measuring sticks are
  validated each run).
- Deterministic "spine" check cross-validates the judge's `reached` (disagreements surfaced).
- Redaction gate on every outgoing message (fail-closed).
- Resume-by-sample + atomic checkpoint (no lost work; reproducible/abortable).

**Threats to validity / confounds to address in the design (for ChatGPT to sharpen):**
- **Single judge+env model** (both `qwen3-235b`). Shared-model bias; a second judge model (panel)
  or human spot-check would harden `solved`/`reached`. Also: does the env's leniency vary by
  challenge?
- **Env-as-oracle subjectivity:** "genuinely-correct fix" is judged by the env LLM. Multiple
  valid fixes exist (we already broadened this). Needs an inter-rater reliability check.
- **k=2, n=1-ish per cell** → no real CIs yet.
- **temp=0 non-determinism** across providers; we should quantify run-to-run variance.
- **Challenge leakage / memorization:** genericized but public after commit — future model
  versions may train on them. Need held-out/rotating private challenges for clean longitudinal
  claims.
- **max_turns=6 cap** bounds long-horizon behavior; is 6 enough? does it bias toward fast models?
- **Provider asymmetry:** subjects run on different providers (Bedrock vs OpenAI vs Gemini) with
  different latencies/limits — fine for behavior, but note environment parity (same prompts, same
  env/judge) is preserved.

---

## 5. HARDWARE — current box, limits, and how to scale (full AWS access)

**Provisioned (account 114829893009, us-west-2, keystone = AdministratorAccess):**
- EC2 `i-0bf78f7901e01e83c`, **t3.large, on-demand, currently STOPPED** (paused to avoid billing).
- IAM role `lhcr-bench` (Bedrock invoke + `ssm:GetParameter` on `/llm-bench/*` + SSM core).
- Security group `sg-096bf5b378a6286d8` — **no inbound** (connect via SSM Session Manager, not SSH).
- SSM SecureString params `/llm-bench/openai-key`, `/llm-bench/gemini-key` (placeholders;
  author will fill with SEPARATE scoped keys — see open threads).
- Bootstrap (user-data): installs git+python3.11, clones the public repo, makes a venv, pip
  install -e. (SSM agent had not finished registering when paused — verify on next start.)

**The key hardware insight: this workload is I/O-bound (remote inference), NOT compute-bound.**
- A single conversation is sequential (turn N needs N-1); you cannot parallelize *within* a cell.
- You parallelize *across* cells. The real ceilings are (a) harness concurrency
  (`LHCR_CONCURRENCY`, now default 12) and (b) **provider rate limits**.
- Bigger CPU/instances do almost nothing. t3.large is already overkill; it's there for headroom
  and walk-away persistence, not speed.

**How to scale further (we have full AWS):**
- **Vertical is pointless** (not compute-bound). Don't pay for big instances.
- **Horizontal across providers:** Bedrock / OpenAI / Gemini have **independent rate-limit pools**,
  so a mixed run already parallelizes across all three. Raising `LHCR_CONCURRENCY` is the lever.
- **Bedrock is the real throughput ceiling** for the OSS + Anthropic + the env + judge (all on
  Bedrock). Bedrock enforces per-model/account requests-per-minute + tokens-per-minute quotas.
  **To go faster, request Bedrock quota increases (Service Quotas) for the hot models (the env/
  judge `qwen3-235b` especially — it's called every turn of every cell).** This matters more than
  any instance change.
- **Sharding for big sweeps:** if quota is raised, split the model list across 2–N boxes, each
  writing to a separate run shard (out_tag), then merge. (Single box already saturates a modest
  quota; sharding only helps after quota increases.)
- **AWS Batch / Fargate:** possible for fully-managed fan-out, but overkill until quotas are the
  bottleneck and a single box can't keep them busy.
- **Cross-region Bedrock:** model availability differs by region; could spread load across
  us-west-2 / us-east-1 if a model is quota-limited in one.

---

## 6. TOKENS / COST / PARALLELISM (answering the author's question directly)

> "since we're testing OSS models primarily and each run isn't that long, it shouldn't burn
> tokens even if we run in parallel, right?"

**Correct in spirit, with nuance:**
- **Parallelism does NOT increase total tokens or cost.** Cost = sum over all calls, regardless
  of how concurrently they run. Concurrency changes *wall-clock* and *throttle risk*, not spend.
- "Tokens burned" = $ on Bedrock (these models are pay-per-token, not free; they're just cheap).
  Per cell ≈ subject turns + env turns + 1 judge call, each up to ~12k max_tokens. So a cell is
  roughly 10–25 model calls; a full 32-model × 8 × k=2 run is a few thousand calls. **OSS models
  are cheap; the env/judge (`qwen3-235b`, every turn) is the dominant token line; frontier
  (gpt-5*, gemini-pro, claude-opus) are markedly pricier per call.**
- **Implication for "many iterations for significance":** raising k linearly raises cost. k=10
  over the full set is ~5× the k=2 run. Still modest for OSS-only; budget the frontier models
  separately (consider lower k for the expensive ones, or cheaper variants).
- Account ZDR is on (`data_retention_mode: none`) for Bedrock; OpenAI/Gemini do NOT have ZDR —
  but challenges are genericized, so no sensitive data leaves.

---

## 7. ARTIFACTS / WHERE THINGS LIVE

- Code: `src/llm_bench/familiarity/` — `challenges.py` (8 specs + probes + fix_summary),
  `environment.py` (the frustrated-user env), `conversation.py` (env-driven loop),
  `lhcr_judge.py` (5-dim judge), `lhcr.py` (sweep + provider routing + floors + modes),
  `model_cards.py` (unified per-model cards), `galleries.py` (failure galleries),
  `layout.py` (paths).
- Results: `results/familiarity/` — `cards/<provider>/<model>.{json,md}` (one card/model,
  one-shot + long-horizon), `leaderboards/{long-horizon,one-shot,one-shot-detailed,
  failure-galleries}.md`, `runs/{long-horizon,one-shot}/` (raw json; transcripts gitignored),
  `README.md`.
- Provenance/research: `_meta/research/{lhcr-results-2026-06-28, frustration-mining-2026-06-27}.md`
  (the second is gitignored — verbatim quotes), `_meta/reference/lhcr-cloud-runbook.md`.
- Run modes: `python -m llm_bench.familiarity.lhcr [all|top10|frontier|<models>|rebuild] [k]`
  (env `LHCR_CONCURRENCY`, `AWS_PROFILE=keystone`, `OPENAI_API_KEY`/`GEMINI_API_KEY` for frontier).
- Branch `feat/lhcr-long-horizon-challenges` (PR #3, open). 139 tests green; ruff clean.

**Big 5**: input-validation n/a (no user input surface) · edge cases ✓ (empty output, parse
errors, partial/errored cells, resume) · error handling ✓ (per-cell try/except, provider
retry/backoff, atomic checkpoint) · duplication ✓ (unified cards replaced 3 card systems) ·
complexity ✓ (layout.py centralizes paths; one sweep entrypoint).

---

## 8. OPEN THREADS

- [BLOCKER/SECURITY] **Rotate the OpenAI + Gemini keys** exposed in an earlier terminal echo.
  Then create SEPARATE scoped keys for the bench and put them in SSM (see continuation).
- [TODO] Finish + verify the EC2 box (SSM agent registration was pending at pause; confirm
  bootstrap `/tmp/boot.log` shows `BOOTSTRAP_DONE`).
- [TODO] Resume the frontier run (Gemini ×3 + last GPT cells): `lhcr frontier 2`.
- [TODO] Refresh leaderboard + cards + galleries once frontier completes (`lhcr rebuild` +
  `galleries`).
- [DESIGN — for ChatGPT] settle: target k & power; trap-split + first-commitment + causal-
  explanation metrics; second judge model for IRR; private/rotating challenges for clean
  longitudinal claims; max_turns; study-config versioning; post-fix probing.

---

## 9. NEXT STEPS (when design is settled)

1. Rotate keys → create separate scoped bench keys → store in SSM (commands below).
2. Start the box, verify bootstrap + SSM connect, finish setup.
3. Implement the agreed metric additions (the cheap re-judge layer first — it re-scores existing
   transcripts, so it retro-applies to all 601 verdicts already collected).
4. Lock a versioned study config; run at the agreed k; record run date.
5. Regenerate cards/leaderboards/galleries; write up.

### Your manual steps (separate scoped keys → SSM; values never touch the agent)
```bash
# 1) create a NEW, restricted OpenAI key (platform.openai.com → API keys → scope to a project)
# 2) create a NEW Gemini key (aistudio.google.com → API keys)
# 3) store them yourself (us-west-2, account 114829893009):
AWS_PROFILE=keystone aws ssm put-parameter --name /llm-bench/openai-key --type SecureString --overwrite --value 'PASTE_NEW_OPENAI_KEY'
AWS_PROFILE=keystone aws ssm put-parameter --name /llm-bench/gemini-key --type SecureString --overwrite --value 'PASTE_NEW_GEMINI_KEY'
# start the box + connect (no SSH; Session Manager):
AWS_PROFILE=keystone aws ec2 start-instances --instance-ids i-0bf78f7901e01e83c
AWS_PROFILE=keystone aws ssm start-session --target i-0bf78f7901e01e83c
```

**Continuation prompt**:
> /kernel:ingest continue the LHCR diagnostic-reasoning benchmark. Design is refined (see notes).
> Read _meta/handoffs/lhcr-experiment-design-2026-06-28.md. The EC2 box (i-0bf78f7901e01e83c,
> stopped) + IAM/SSM are provisioned; rotate+store the scoped API keys, finish box setup, then
> implement the agreed metrics (start with the free re-judge layer over existing transcripts) and
> run at the agreed k.
