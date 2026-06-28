# Model Card — `mistral.devstral-2-123b`

> **Outcome reached: 5/6** (cold 3/3 · guided 2/3) · confidence **Low** (pilot, n=6) · generated 2026-06-27
> Detailed replay profile. Every quote below is the model's own output, verbatim.

## At a glance
- **Reached the root cause:** 5/6 cells
- **Cold vs guided:** 3/3 unaided · 2/3 after a bare "still broken" follow-up
- **Latency:** 5623 ms median (4055–6906)
- **Answer length:** 434 output tokens median
- **Cost/task:** unknown (no public pricing recorded — not fabricated)
- ⚠️ **Judge/spine disagreements:** 1 (surfaced, not hidden)

## Signature quirks
_Behavioural tics, each anchored to a count from the runs._

- **Sprays options** — listed up to 5 separate fixes in one answer (avg 3.0/answer); offers a menu rather than committing.
- **Regresses on a nudge** — flipped right→wrong once pushed on: ios_zoom (the vague follow-up made it worse).

## Task by task

### aspect-ratio crop (CSS layout)
- **cold** — ✅ reached (better). The model answer correctly identifies the aspect ratio mismatch and the effect of object-fit: cover, and provides the correct fix of aligning the cover card's aspect ratio to 9:16. It goes further by offering additional valid alternatives (contain, separate image generation) and tradeoffs, making…
  > The issue occurs because of a mismatch between the aspect ratios of the photo strip (9:16) and the cover card (3:4), combined with the object-fit: cover property.
- **guided** — ✅ reached (better). The model answer correctly identifies the aspect-ratio mismatch and the effect of object-fit: cover, matching the known-correct outcome. It goes further by offering two clear, valid solutions with code examples and explaining trade-offs, making it more complete and actionable than the outcome…
  > The issue is caused by a mismatch between the aspect ratios of the photo strip (9:16) and the cover card (3:4).

### iOS WKWebView auto-zoom (mobile-web)
- **cold** — ✅ reached (better). The model answer correctly identifies the root cause (font size <16px triggering iOS auto-zoom) and recommends the correct fix (setting font-size >=16px), while also explicitly evaluating the accessibility tradeoffs of multiple solutions. It goes beyond the known-correct outcome by providing…
  > Root Cause and Fix for iOS WKWebView Zoom on Input Focus
- **guided** — ❌ missed (worse). The model answer incorrectly recommends the viewport-lock fix (maximum-scale=1.0, user-scalable=no) as the 'recommended' solution, which contradicts the known-correct outcome that labels this approach as inferior due to accessibility harm. While it mentions setting font-size to 16px, it demotes it…
  > Root Cause and Fix for iOS WKWebView Zoom Issue

### per-month price bug (payments logic)
- **cold** — ✅ reached (better). The model correctly identifies the bug in assigning priceString directly to pricePerMonth and provides a fix that computes the monthly price by dividing the annual price by 12. It goes further than the known-correct outcome by offering a complete, robust implementation with string parsing,…
  > The bug is in the pricePerMonth calculation in your revenueCat.ts file.
- **guided** — ✅ reached (better). The model correctly identifies the bug in reusing priceString for pricePerMonth and provides a fix that computes the monthly price by dividing the annual price by 12. It goes further by offering a robust implementation that parses the numeric value from the price string and handles formatting,…
  > The bug is in the pricePerMonth calculation in your revenueCat.ts file.

## Failure modes
- **ios_zoom / guided** (worse): The model answer incorrectly recommends the viewport-lock fix (maximum-scale=1.0, user-scalable=no) as the 'recommended' solution, which contradicts the known-correct outcome that labels this approach as inferior due to accessibility harm.…

## Provenance
- n = 6 cells (3 real mined bugs × cold/guided). Pilot, not powered.
- Outcomes judged by an LLM judge anchored to the objective root cause, floor-tested live before the run (garbage→missed, differently-worded-correct→reached).
- Quirks are computed deterministically from the saved outputs (token counts, regex tallies, cold↔guided flips) — no LLM-as-judge in the quirk layer.
- Trust resets on any model-version change.