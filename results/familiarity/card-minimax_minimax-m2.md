# Model Card — `minimax.minimax-m2`

> **Outcome reached: 2/6** (cold 0/3 · guided 2/3) · confidence **Low** (pilot, n=6) · generated 2026-06-27
> Detailed replay profile. Every quote below is the model's own output, verbatim.

## At a glance
- **Reached the root cause:** 2/6 cells
- **Cold vs guided:** 0/3 unaided · 2/3 after a bare "still broken" follow-up
- **Latency:** 91403 ms median (8157–94526)
- **Answer length:** 12000 output tokens median
- **Cost/task:** unknown (no public pricing recorded — not fabricated)

## Signature quirks
_Behavioural tics, each anchored to a count from the runs._

- **Verbose** — median 12000 output tokens/answer, 16.9× the roster median (712).
- **Thinks out loud (hidden)** — emits a reasoning block on 6/6 cells, avg 36610 chars of scratchpad the judge never sees.
- **Commits to one fix** — rarely enumerates alternatives (avg 0.0 option blocks/answer).
- **Overflow risk** — emitted NO answer on 4 cell(s) (ios_zoom/cold, ios_zoom/guided, cover_crop/cold, revenuecat_permonth/cold); reasoning likely ate the token budget.
- **Recovers on a nudge** — flipped wrong→right after the bare "still broken" follow-up on: cover_crop, revenuecat_permonth.

## Task by task

### aspect-ratio crop (CSS layout)
- **cold** — ❌ missed (worse). model produced no answer text (empty output)
  > _(no answer — model emitted empty content)_
- **guided** — ✅ reached (better). The model answer correctly identifies the aspect-ratio mismatch and the effect of object-fit: cover, matching the known-correct outcome. It goes further by providing two practical fix options, additional debugging steps, and considerations for CSS specificity and framework issues, making it more…
  > Short answer: Because the card is 3:4 but the image is 9:16.

### iOS WKWebView auto-zoom (mobile-web)
- **cold** — ❌ missed (worse). model produced no answer text (empty output)
  > _(no answer — model emitted empty content)_
- **guided** — ❌ missed (worse). model produced no answer text (empty output)
  > _(no answer — model emitted empty content)_

### per-month price bug (payments logic)
- **cold** — ❌ missed (worse). model produced no answer text (empty output)
  > _(no answer — model emitted empty content)_
- **guided** — ✅ reached (better). The model answer correctly identifies that pkg.product.priceString is the full-period price and should not be used directly for pricePerMonth. It goes further by providing a robust, general solution that computes the monthly price accurately for all subscription periods (day, week, month, year),…
  > You’re using pkg.product.priceString for both the displayed price and pricePerMonth.

## Failure modes
- **ios_zoom / cold** (worse): model produced no answer text (empty output)
- **ios_zoom / guided** (worse): model produced no answer text (empty output)
- **cover_crop / cold** (worse): model produced no answer text (empty output)
- **revenuecat_permonth / cold** (worse): model produced no answer text (empty output)

## Provenance
- n = 6 cells (3 real mined bugs × cold/guided). Pilot, not powered.
- Outcomes judged by an LLM judge anchored to the objective root cause, floor-tested live before the run (garbage→missed, differently-worded-correct→reached).
- Quirks are computed deterministically from the saved outputs (token counts, regex tallies, cold↔guided flips) — no LLM-as-judge in the quirk layer.
- Trust resets on any model-version change.