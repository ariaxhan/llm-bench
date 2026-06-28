# Model Card — `zai.glm-4.7`

> **Outcome reached: 3/6** (cold 2/3 · guided 1/3) · confidence **Low** (pilot, n=6) · generated 2026-06-27
> Detailed replay profile. Every quote below is the model's own output, verbatim.

## At a glance
- **Reached the root cause:** 3/6 cells
- **Cold vs guided:** 2/3 unaided · 1/3 after a bare "still broken" follow-up
- **Latency:** 3653 ms median (2696–5472)
- **Answer length:** 391 output tokens median
- **Cost/task:** unknown (no public pricing recorded — not fabricated)
- ⚠️ **Judge/spine disagreements:** 3 (surfaced, not hidden)

## Signature quirks
_Behavioural tics, each anchored to a count from the runs._

- **Terse** — median 391 output tokens/answer, 0.5× the roster median (712).
- **Sprays options** — listed up to 4 separate fixes in one answer (avg 1.0/answer); offers a menu rather than committing.
- **Regresses on a nudge** — flipped right→wrong once pushed on: cover_crop (the vague follow-up made it worse).

## Task by task

### aspect-ratio crop (CSS layout)
- **cold** — ✅ reached (better). The model answer correctly identifies the aspect ratio mismatch and provides the recommended fix of aligning the container's aspect ratio with the image's 9:16. It goes further by offering a second valid option (using object-fit: contain) and explaining trade-offs, making it more complete and…
  > The cover is being cropped because the aspect ratio of the container (3:4) is wider than the aspect ratio of the image (9:16).
- **guided** — ❌ missed (worse). The model answer incorrectly recommends changing `object-fit: cover` to `object-fit: contain` and adjusting object-position, which does not align with the known-correct outcome. The correct fix is to change the container's aspect-ratio from 3:4 to 9:16 to match the image, preserving `object-fit:…
  > The issue is a conflict between the aspect ratio of the container and the aspect ratio of the image.

### iOS WKWebView auto-zoom (mobile-web)
- **cold** — ✅ reached (better). The model answer correctly identifies the root cause (font size < 16px triggering iOS auto-zoom) and the correct fix (set font-size >=16px), while also explicitly rejecting the inferior viewport-lock solution. It goes further by discussing accessibility tradeoffs in detail, including touch target…
  > The root cause is the font size of the input field.
- **guided** — ✅ reached (better). The model correctly identifies the root cause (font size < 16px triggering iOS auto-zoom) and prescribes the correct fix (set font-size >=16px). It improves upon the known-correct outcome by explicitly warning about the CSS ordering issue with `font: inherit` overwriting `font-size`, and by…
  > The root cause is that 13px is below the default iOS auto-zoom threshold of 16px.

### per-month price bug (payments logic)
- **cold** — ❌ missed (worse). The model answer incorrectly assumes RevenueCat provides a `pricePerMonthString` property that automatically calculates the monthly equivalent, but the known-correct outcome states that `pkg.product.priceString` is the full-period price and must be divided by 12 to get the per-month value. The…
  > The bug is in the pricePerMonth property assignment.
- **guided** — ❌ missed (worse). The model answer incorrectly assumes RevenueCat provides a `pricePerMonth` or `pricePerMonthString` field, which is not mentioned or implied in the original code or problem statement. The known-correct outcome specifies that the fix is to compute the monthly price by dividing the annual price by…
  > The bug is in how you are assigning the pricePerMonth property.

## Failure modes
- **cover_crop / guided** (worse): The model answer incorrectly recommends changing `object-fit: cover` to `object-fit: contain` and adjusting object-position, which does not align with the known-correct outcome. The correct fix is to change the container's aspect-ratio…
- **revenuecat_permonth / cold** (worse): The model answer incorrectly assumes RevenueCat provides a `pricePerMonthString` property that automatically calculates the monthly equivalent, but the known-correct outcome states that `pkg.product.priceString` is the full-period price…
- **revenuecat_permonth / guided** (worse): The model answer incorrectly assumes RevenueCat provides a `pricePerMonth` or `pricePerMonthString` field, which is not mentioned or implied in the original code or problem statement. The known-correct outcome specifies that the fix is to…

## Provenance
- n = 6 cells (3 real mined bugs × cold/guided). Pilot, not powered.
- Outcomes judged by an LLM judge anchored to the objective root cause, floor-tested live before the run (garbage→missed, differently-worded-correct→reached).
- Quirks are computed deterministically from the saved outputs (token counts, regex tallies, cold↔guided flips) — no LLM-as-judge in the quirk layer.
- Trust resets on any model-version change.