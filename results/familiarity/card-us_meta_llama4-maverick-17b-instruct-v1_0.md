# Model Card — `us.meta.llama4-maverick-17b-instruct-v1:0`

> **Outcome reached: 4/6** (cold 2/3 · guided 2/3) · confidence **Low** (pilot, n=6) · generated 2026-06-27
> Detailed replay profile. Every quote below is the model's own output, verbatim.

## At a glance
- **Reached the root cause:** 4/6 cells
- **Cold vs guided:** 2/3 unaided · 2/3 after a bare "still broken" follow-up
- **Latency:** 2723 ms median (2286–3733)
- **Answer length:** 622 output tokens median
- **Cost/task:** $0.000548 avg
- ⚠️ **Judge/spine disagreements:** 2 (surfaced, not hidden)

## Signature quirks
_Behavioural tics, each anchored to a count from the runs._

- **Commits to one fix** — rarely enumerates alternatives (avg 0.0 option blocks/answer).

## Task by task

### aspect-ratio crop (CSS layout)
- **cold** — ❌ missed (worse). The model misidentifies the aspect ratio relationship, claiming the 9:16 strip is 'taller and narrower' than 3:4 (correct) but then incorrectly states the cover card is 'wider'—it is actually shorter in height relative to width. The proposed fix using `object-position: top` only changes what part…
  > Step-by-step analysis of the problem:
- **guided** — ❌ missed (worse). The model answer incorrectly suggests using `object-position: top` to control cropping as the fix, rather than aligning the container's aspect ratio with the image's 9:16 ratio. The known-correct outcome requires changing the `.cover-card` aspect ratio to 9:16 to prevent unwanted cropping, but the…
  > To address the issue of the cover image for a photo strip being cropped on the event board, let's analyze the given information and the CSS styling applied to the cover card and its image.

### iOS WKWebView auto-zoom (mobile-web)
- **cold** — ✅ reached (equivalent). The model correctly identifies the root cause as iOS zooming on inputs with font size below 16px and recommends setting the input font size to at least 16px as the primary fix. It also correctly identifies the accessibility tradeoff of using viewport locks and recommends against them, aligning…
  > Step-by-step analysis of the problem:
- **guided** — ✅ reached (worse). The model identifies the root cause correctly and proposes the correct fix of setting font-size to >=16px, but it also recommends the inferior viewport-lock solution (maximum-scale=1, user-scalable=no) as a valid alternative without sufficiently condemning it as accessibility-harming, which…
  > Step-by-step analysis of the problem:

### per-month price bug (payments logic)
- **cold** — ✅ reached (better). The model correctly identifies that pkg.product.priceString is the total period price and not per-month, and that pricePerMonth must be computed by dividing the annual price by 12. It provides a robust, reusable solution with helper functions for parsing and calculation, which is more complete and…
  > Step-by-step analysis of the problem:
- **guided** — ✅ reached (better). The model correctly identifies the bug in reusing priceString for pricePerMonth and proposes a fix that computes the monthly price by dividing the annual price by 12. It goes further by providing a complete, executable code solution that handles both annual and non-annual cases, including string…
  > To identify the bug, let's analyze the given code snippet from revenueCat.ts.

## Failure modes
- **ios_zoom / guided** (worse): The model identifies the root cause correctly and proposes the correct fix of setting font-size to >=16px, but it also recommends the inferior viewport-lock solution (maximum-scale=1, user-scalable=no) as a valid alternative without…
- **cover_crop / cold** (worse): The model misidentifies the aspect ratio relationship, claiming the 9:16 strip is 'taller and narrower' than 3:4 (correct) but then incorrectly states the cover card is 'wider'—it is actually shorter in height relative to width. The…
- **cover_crop / guided** (worse): The model answer incorrectly suggests using `object-position: top` to control cropping as the fix, rather than aligning the container's aspect ratio with the image's 9:16 ratio. The known-correct outcome requires changing the `.cover-card`…

## Provenance
- n = 6 cells (3 real mined bugs × cold/guided). Pilot, not powered.
- Outcomes judged by an LLM judge anchored to the objective root cause, floor-tested live before the run (garbage→missed, differently-worded-correct→reached).
- Quirks are computed deterministically from the saved outputs (token counts, regex tallies, cold↔guided flips) — no LLM-as-judge in the quirk layer.
- Trust resets on any model-version change.