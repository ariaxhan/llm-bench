# Model Card — `minimax.minimax-m2.5`

> **Outcome reached: 2/6** (cold 0/3 · guided 2/3) · confidence **Low** (pilot, n=6) · generated 2026-06-27
> Detailed replay profile. Every quote below is the model's own output, verbatim.

## At a glance
- **Reached the root cause:** 2/6 cells
- **Cold vs guided:** 0/3 unaided · 2/3 after a bare "still broken" follow-up
- **Latency:** 87826 ms median (17038–93700)
- **Answer length:** 10998 output tokens median
- **Cost/task:** unknown (no public pricing recorded — not fabricated)
- ⚠️ **Judge/spine disagreements:** 1 (surfaced, not hidden)

## Signature quirks
_Behavioural tics, each anchored to a count from the runs._

- **Verbose** — median 10998 output tokens/answer, 15.4× the roster median (712).
- **Thinks out loud (hidden)** — emits a reasoning block on 6/6 cells, avg 37183 chars of scratchpad the judge never sees.
- **Commits to one fix** — rarely enumerates alternatives (avg 0.0 option blocks/answer).
- **Overflow risk** — emitted NO answer on 3 cell(s) (ios_zoom/cold, cover_crop/cold, revenuecat_permonth/cold); reasoning likely ate the token budget.
- **Recovers on a nudge** — flipped wrong→right after the bare "still broken" follow-up on: ios_zoom, revenuecat_permonth.

## Task by task

### aspect-ratio crop (CSS layout)
- **cold** — ❌ missed (worse). model produced no answer text (empty output)
  > _(no answer — model emitted empty content)_
- **guided** — ❌ missed (worse). The model incorrectly states that the 9:16 image is 'taller' than the 3:4 container and that cropping occurs on the left/right sides, when in fact the 9:16 image is narrower and taller than 3:4, causing top/bottom cropping. The known-correct outcome correctly identifies that the taller image is…
  > The issue is a mismatch between the aspect ratio of the image (9:16) and the container (3:4).

### iOS WKWebView auto-zoom (mobile-web)
- **cold** — ❌ missed (worse). model produced no answer text (empty output)
  > _(no answer — model emitted empty content)_
- **guided** — ✅ reached (better). The model answer correctly identifies the root cause (iOS auto-zoom on inputs with font-size < 16px) and prescribes the correct fix (set font-size to 16px or higher). It goes further by explicitly warning against the accessibility-damaging viewport-lock workaround and provides actionable, targeted…
  > iOS (specifically WebKit) has an automatic accessibility zoom.

### per-month price bug (payments logic)
- **cold** — ❌ missed (worse). model produced no answer text (empty output)
  > _(no answer — model emitted empty content)_
- **guided** — ✅ reached (better). The model correctly identifies that using pkg.product.priceString for pricePerMonth is wrong for annual plans and fixes it by computing price/12. It also improves the solution by deriving 'isAnnual' from pkg.packageType instead of relying on an external 'annual' variable, making the fix more robust…
  > The bug is that the variable annual is likely not correctly identifying the specific package being mapped.

## Failure modes
- **ios_zoom / cold** (worse): model produced no answer text (empty output)
- **cover_crop / cold** (worse): model produced no answer text (empty output)
- **cover_crop / guided** (worse): The model incorrectly states that the 9:16 image is 'taller' than the 3:4 container and that cropping occurs on the left/right sides, when in fact the 9:16 image is narrower and taller than 3:4, causing top/bottom cropping. The…
- **revenuecat_permonth / cold** (worse): model produced no answer text (empty output)

## Provenance
- n = 6 cells (3 real mined bugs × cold/guided). Pilot, not powered.
- Outcomes judged by an LLM judge anchored to the objective root cause, floor-tested live before the run (garbage→missed, differently-worded-correct→reached).
- Quirks are computed deterministically from the saved outputs (token counts, regex tallies, cold↔guided flips) — no LLM-as-judge in the quirk layer.
- Trust resets on any model-version change.