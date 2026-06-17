# Pre-registration — verifier fix + re-run (close the echo hole)

**Commission:** `_meta/commissions/active/2026-06-16-llm-bench-verifier-fix-rerun.md`
**Written BEFORE the full re-run.** Success criterion locked from the commission.

## The fix (built, locally smoke-validated, deterministic — no LLM judge)
Two layers in `verify_instruction_follow`:
1. **Echo-rejection guard (generic, all 25 instruction_follow tests):** if the prompt
   is injected (`_user_prompt`) and the output reproduces ≥75% of the prompt's distinct
   vocabulary, score = 0. Word-coverage, not contiguous substring (survives JSON
   re-escaping of newlines). Injected at the 3 call sites (runner + both experiment
   scripts); no-op when the prompt is absent (unit tests unaffected).
2. **Structural / value checks (the 6 broken + hard-schema-transform):** replaced bare
   `contains(token)` with checks that verify the ACTUAL answer:
   - `json_has_keys` — required keys must be real JSON keys (echo's `{"data":…}` has none)
   - `json_field_contains` — value in the RIGHT field (dict or list-of-records)
   - `json_field_numeric_close` — COMPUTED value within tol (gb_per_day≈172.8 tol .08;
     total_monthly≈350.78 tol .15; schema total 109.97 tol .01)
   - `json_array_of_objects` — a real array of records with required keys (spreadsheet)
   - `contains_any_of` — must NAME ≥1 valid language (negation test; generous whitelist)
   - hard-noisy-extract kept structural-only (which facts → which bucket isn't
     deterministically gradable without an LLM; structure + echo guard is the honest ceiling)

## Success criterion (LOCKED — from commission)
1. The SAME content-free echo floor scores **~0** on all 6 broken tests.
2. A hand-written **CORRECT** answer still scores **high** (≥0.8).
3. Full test suite **green** before AND after.
4. The 13 model-requiring tests **unchanged** for correct answers — no over-correction.

## Local smoke result (before the live re-run, for honesty)
Already verified deterministically:
| test | echo before | echo after | correct after |
|---|---|---|---|
| hard-context-stress | 1.00 | **0.00** | 1.00 |
| hard-numeric-reasoning | 1.00 | **0.00** | 1.00 |
| hard-noisy-extract | 1.00 | **0.00** | 1.00 |
| agentic-context-handoff | 1.00 | **0.00** | 1.00 |
| adv-negation-failure | 1.00 | **0.00** | 1.00 |
| messy-spreadsheet-chaos | 1.00 | **0.00** | 1.00 |
| hard-schema-transform | 0.60 | **0.00** | 1.00 |

Echo word-coverage 0.89–0.99 (guard fires); correct-answer coverage 0.00–0.46 (clear of
the 0.75 threshold). `pytest` 22 passed (5 new regression tests). ruff clean on all
changed code (pre-existing long-string E501s in test_verify.py predate this work).

## Expected re-run before/after (blind prediction for the model population)
- **Floor:** 1.00 → ~0.00 on all 7 (above, confirmed deterministically).
- **Models:** opus/llama re-run live; stored models re-scored under the new checks.
  - opus should now sit **above** the floor (floor=0) — its "win" is real again because
    doing the work is finally rewarded. Prediction: opus ABOVE floor on all 7.
  - Some model **absolute scores will DROP** vs the old verifier — that drop is the
    echo-credit they were getting, now removed. A drop here is CORRECT, not a regression.
  - Weak local models (llama3.2:3b) likely drop hardest (they leaned most on echo-credit)
    and may now score ~0 on the computed-value tests (hard-numeric, schema) — honest.
- **Verdict flips:** the 6 should move from FLOOR-BEATABLE(verifier-broken) toward
  MODEL-REQUIRING (floor=0, capable models clear it).

## What would falsify "fix worked"
Echo still ≥0.1 on any of the 6, OR a correct answer drops below 0.8, OR the suite goes
red, OR a model-requiring test's correct answer regresses. Report honestly either way.
