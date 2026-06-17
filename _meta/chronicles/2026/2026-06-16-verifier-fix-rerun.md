---
rite: chronicle
date: 2026-06-16
commission: Vaults _meta/commissions/active/2026-06-16-llm-bench-verifier-fix-rerun.md
follows: 2026-06-16-floor-full-suite.md (which proved the verifiers were broken)
repo: CodingVault/llm-bench
window: todo (hcom) — coordinated w/ @dune
---

# Chronicle — fixing the broken verifiers, then proving the hole is closed

## What I was asked to do
The full-suite audit proved 6 HARD/EXTREME `instruction_follow` tests scored a
content-free prompt-echo 1.00 (live opus tied or lost) because `contains(X)` matched
expected tokens that already sit in the prompt. Build the real fix so the echo FAILS and
the task is actually verified, re-run, and report the honest before/after — including any
model "win" that evaporates once the loophole closes. Stay deterministic (no LLM judge),
behavior-preserving for the 13 model-requiring tests, no over-correction.

## What I did (the fix — two layers, deterministic)
1. **Echo-rejection guard** in `verify_instruction_follow` (generic, all 25 tests): if
   the output reproduces ≥75% of the prompt's distinct vocabulary, score = 0. Word-
   coverage, not contiguous substring (survives JSON re-escaping of newlines — my first
   LCS attempt failed exactly there). Prompt injected at the 3 call sites (runner + both
   experiment scripts); no-op when the prompt is absent (unit tests unaffected).
2. **Real structural / value checks** replacing bare `contains()` on the 6 broken +
   hard-schema-transform: `json_has_keys`, `json_field_contains` (right field, dict or
   list-of-records), `json_field_numeric_close` (COMPUTED value — gb_per_day≈172.8,
   total_monthly≈350.78, schema total 109.97), `json_array_of_objects`, `contains_any_of`.
3. Added 5 regression unit tests (echo rejected, correct passes, wrong-values fail,
   numeric GB-vs-GiB tolerance, array-of-objects).

## Confirming the two dune asks
- **(1) No false-rejects on the ~19 unfixed instruction_follow tests.** The generic guard
  is the one place a blanket rule could bite. <!-- FALSE-REJECT-CONFIRM slotted after re-run -->
- **(2) hard-noisy-extract is echo-closed but NOT fully semantically graded.** Its fix is
  structural-only (`json_has_keys` + echo guard). Which fact belongs in confirmed vs
  unverified vs contradiction is not deterministically gradable without an LLM judge,
  which we DECLINED (no-LLM-judge invariant). So this test now rejects a content-free echo
  but does not check that the *right* facts were bucketed — recorded so it is never later
  mistaken for fully fixed.

## Before / after (verified live)
<!-- AFTER-TABLE slotted here after the re-run completes -->

## What failed / honesty
- **First echo guard (LCS) didn't fire** — `json.dumps` escapes newlines to `\n`, so the
  longest contiguous shared run broke at every line and the echo slipped under threshold.
  Caught it in local smoke (echo still 0.33–1.00), switched to word-coverage. Lesson: test
  the guard against the actual echo output, not the idea of it.
- **hard-noisy-extract** left structurally-graded only (above) — an honest ceiling, not a
  full fix.
- **Pre-existing ruff E501s** in `tests/test_verify.py` (long test-prompt strings, lines
  38–109) predate this work; my added code is ruff-clean.
- **Stored-model "after" is partly unavailable:** the 6 stored-only models (apfel + 5
  opencode) have no saved raw outputs, so they cannot be re-scored under the new verifier.
  The true before/after for MODELS is the live opus/llama re-run; stored numbers are
  pre-fix and labelled as such.

## Coordination
@dune green-lit the fix as essentially proven from the local smoke, and added the two
confirm-not-change asks (false-reject check folded into the run; hard-noisy-extract honesty
label). Said leave the 0.75 threshold and numeric tolerances as set (healthy margins).

## Verdict
<!-- VERDICT slotted after re-run -->
