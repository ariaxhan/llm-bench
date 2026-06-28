# Model Card — `zai.glm-4.7-flash`

> **Outcome reached: 4/6** (cold 2/3 · guided 2/3) · confidence **Low** (pilot, n=6) · generated 2026-06-27
> Detailed replay profile. Every quote below is the model's own output, verbatim.

## At a glance
- **Reached the root cause:** 4/6 cells
- **Cold vs guided:** 2/3 unaided · 2/3 after a bare "still broken" follow-up
- **Latency:** 1480 ms median (1394–2533)
- **Answer length:** 346 output tokens median
- **Cost/task:** unknown (no public pricing recorded — not fabricated)
- ⚠️ **Judge/spine disagreements:** 2 (surfaced, not hidden)

## Signature quirks
_Behavioural tics, each anchored to a count from the runs._

- **Terse** — median 346 output tokens/answer, 0.5× the roster median (712).
- **Commits to one fix** — rarely enumerates alternatives (avg 1.0 option blocks/answer).
- **Recovers on a nudge** — flipped wrong→right after the bare "still broken" follow-up on: ios_zoom.
- **Regresses on a nudge** — flipped right→wrong once pushed on: cover_crop (the vague follow-up made it worse).

## Task by task

### aspect-ratio crop (CSS layout)
- **cold** — ✅ reached (better). The model answer correctly identifies the aspect-ratio mismatch and the effect of `object-fit: cover`, and provides the correct fix of changing the container to 9/16. It goes further by offering additional context, visual math, and evaluating alternative options, making it more comprehensive and…
  > The issue is caused by a conflict between the aspect ratios of the image and the container.
- **guided** — ❌ missed (worse). The model incorrectly states that the card is wider than the photo, when 3:4 (0.75) is actually taller than 9:16 (0.5625). The core explanation of the cropping cause is wrong. The recommended fix (changing the image to 3:4) contradicts the known-correct outcome, which states the card should match…
  > The issue is caused by the object-fit: cover property combined with the 9:16 aspect ratio of the photo strip.

### iOS WKWebView auto-zoom (mobile-web)
- **cold** — ❌ missed (worse). The model answer incorrectly attributes the zoom to a viewport-to-font-size ratio calculation involving 375px width and 13px text, which is not how iOS auto-zoom works. The known-correct outcome states the actual cause: iOS auto-zooms when an input's computed font-size is below 16px, regardless of…
  > The root cause is a font-size mismatch between the viewport and the CSS.
- **guided** — ✅ reached (better). The model answer correctly identifies the root cause (font size <16px triggering iOS zoom) and the proper fix (set font-size to 16px), aligning with the known-correct outcome. It improves upon it by explicitly naming WCAG compliance and framing 16px as a positive accessibility standard, thus better…
  > The root cause is a font-size mismatch between the browser's default and your CSS.

### per-month price bug (payments logic)
- **cold** — ✅ reached (better). The model answer correctly identifies the bug in assigning priceString directly to pricePerMonth and provides a precise fix using parseFloat and division by 12. It goes further than the known-correct outcome by including implementation details like toFixed(2) and explicitly explaining the parsing…
  > The bug is in the pricePerMonth line.
- **guided** — ✅ reached (better). The model answer correctly identifies the bug in pricePerMonth assignment and provides a fix that computes the monthly price by dividing the annual price by 12. It improves upon the known-correct outcome by including proper type conversion (parseFloat) and formatting (.toFixed(2)), and adds a…
  > The bug is in the pricePerMonth calculation.

## Failure modes
- **ios_zoom / cold** (worse): The model answer incorrectly attributes the zoom to a viewport-to-font-size ratio calculation involving 375px width and 13px text, which is not how iOS auto-zoom works. The known-correct outcome states the actual cause: iOS auto-zooms when…
- **cover_crop / guided** (worse): The model incorrectly states that the card is wider than the photo, when 3:4 (0.75) is actually taller than 9:16 (0.5625). The core explanation of the cropping cause is wrong. The recommended fix (changing the image to 3:4) contradicts the…

## Provenance
- n = 6 cells (3 real mined bugs × cold/guided). Pilot, not powered.
- Outcomes judged by an LLM judge anchored to the objective root cause, floor-tested live before the run (garbage→missed, differently-worded-correct→reached).
- Quirks are computed deterministically from the saved outputs (token counts, regex tallies, cold↔guided flips) — no LLM-as-judge in the quirk layer.
- Trust resets on any model-version change.