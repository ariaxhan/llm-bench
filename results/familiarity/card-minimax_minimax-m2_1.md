# Model Card — `minimax.minimax-m2.1`

> **Outcome reached: 5/6** (cold 3/3 · guided 2/3) · confidence **Low** (pilot, n=6) · generated 2026-06-27
> Detailed replay profile. Every quote below is the model's own output, verbatim.

## At a glance
- **Reached the root cause:** 5/6 cells
- **Cold vs guided:** 3/3 unaided · 2/3 after a bare "still broken" follow-up
- **Latency:** 20408 ms median (14801–91916)
- **Answer length:** 2720 output tokens median
- **Cost/task:** unknown (no public pricing recorded — not fabricated)

## Signature quirks
_Behavioural tics, each anchored to a count from the runs._

- **Verbose** — median 2720 output tokens/answer, 3.8× the roster median (712).
- **Thinks out loud (hidden)** — emits a reasoning block on 6/6 cells, avg 17216 chars of scratchpad the judge never sees.
- **Commits to one fix** — rarely enumerates alternatives (avg 0.6 option blocks/answer).
- **Overflow risk** — emitted NO answer on 1 cell(s) (ios_zoom/guided); reasoning likely ate the token budget.
- **Regresses on a nudge** — flipped right→wrong once pushed on: ios_zoom (the vague follow-up made it worse).

## Task by task

### aspect-ratio crop (CSS layout)
- **cold** — ✅ reached (better). The model answer correctly identifies the aspect-ratio mismatch and provides the recommended fix of aligning the container's aspect ratio with the image's 9:16. It goes further by offering a well-reasoned alternative (object-fit: contain) and justifying why the primary solution is superior, adding…
  > Why the Cover Image is Cropped
- **guided** — ✅ reached (better). The model answer correctly identifies the aspect-ratio mismatch and provides the correct fix of changing the container to 9/16. It goes further by offering troubleshooting steps and an alternative solution with `object-fit: contain`, making it more complete and helpful than the known-correct…
  > Why the Cover Image is Cropped

### iOS WKWebView auto-zoom (mobile-web)
- **cold** — ✅ reached (better). The model answer correctly identifies the root cause (iOS zooming on inputs with font size <16px) and provides the correct fix (set font-size to >=16px). It goes further by offering an alternative solution using CSS transform for visual consistency and discussing accessibility tradeoffs in more…
  > The zoom behavior is caused by iOS Safari's accessibility feature that automatically zooms in when a text input field is focused and its font size is below 16px.
- **guided** — ❌ missed (worse). model produced no answer text (empty output)
  > _(no answer — model emitted empty content)_

### per-month price bug (payments logic)
- **cold** — ✅ reached (better). The model answer correctly identifies the bug in assigning the annual priceString directly to pricePerMonth and provides a fix that computes the monthly equivalent by dividing the annual price by 12. It goes further than the known-correct outcome by offering two implementation options, including…
  > Looking at your code, the bug is in the pricePerMonth field calculation.
- **guided** — ✅ reached (better). The model answer correctly identifies the core bug—misusing priceString for pricePerMonth on annual plans—and goes further by eliminating reliance on an external 'annual' flag, using RevenueCat's billingPeriod instead. It also provides a more robust, complete fix with proper monthly price…
  > The bug is in the revenueCat.ts file where the code uses a separate annual flag to determine the period string for the price display.

## Failure modes
- **ios_zoom / guided** (worse): model produced no answer text (empty output)

## Provenance
- n = 6 cells (3 real mined bugs × cold/guided). Pilot, not powered.
- Outcomes judged by an LLM judge anchored to the objective root cause, floor-tested live before the run (garbage→missed, differently-worded-correct→reached).
- Quirks are computed deterministically from the saved outputs (token counts, regex tallies, cold↔guided flips) — no LLM-as-judge in the quirk layer.
- Trust resets on any model-version change.