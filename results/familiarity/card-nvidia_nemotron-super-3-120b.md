# Model Card — `nvidia.nemotron-super-3-120b`

> **Outcome reached: 4/6** (cold 3/3 · guided 1/3) · confidence **Low** (pilot, n=6) · generated 2026-06-27
> Detailed replay profile. Every quote below is the model's own output, verbatim.

## At a glance
- **Reached the root cause:** 4/6 cells
- **Cold vs guided:** 3/3 unaided · 1/3 after a bare "still broken" follow-up
- **Latency:** 13693 ms median (8810–69868)
- **Answer length:** 1341 output tokens median
- **Cost/task:** unknown (no public pricing recorded — not fabricated)
- ⚠️ **Judge/spine disagreements:** 2 (surfaced, not hidden)

## Signature quirks
_Behavioural tics, each anchored to a count from the runs._

- **Verbose** — median 1341 output tokens/answer, 1.9× the roster median (712).
- **Regresses on a nudge** — flipped right→wrong once pushed on: cover_crop, revenuecat_permonth (the vague follow-up made it worse).

## Task by task

### aspect-ratio crop (CSS layout)
- **cold** — ✅ reached (better). The model answer correctly identifies the aspect-ratio mismatch and the effect of object-fit: cover, matching the known-correct outcome. It goes further by providing multiple viable solutions (contain, adjusting aspect-ratio, object-position), detailed visual examples, and UX recommendations,…
  > You're seeing the top and bottom of the photo strip cropped in the cover card because of a mismatch in aspect ratios between the image and the container, combined with object-fit: cover.
- **guided** — ❌ missed (worse). The model incorrectly identifies 'object-fit: contain' as the fix, but the known-correct outcome states the root issue is the aspect-ratio mismatch and the correct fix is to change the container's aspect-ratio to 9/16 to match the image. Using 'contain' would preserve the entire image but within…
  > You're seeing the cover image cropped (top and bottom cut off) because of a mismatch in aspect ratios between the image and the container, combined with object-fit: cover.

### iOS WKWebView auto-zoom (mobile-web)
- **cold** — ✅ reached (better). The model answer correctly identifies the root cause (iOS auto-zoom on inputs with font-size < 16px) and the correct fix (increase font-size to ≥16px), matching the known-correct outcome. It goes further by offering multiple implementation options, discussing accessibility trade-offs in depth, and…
  > The zoom occurs because iOS Safari (and WKWebView) automatically zooms into any form control (input, textarea, select) whose computed font-size is less than 16 px when the element receives focus.
- **guided** — ✅ reached (better). The model answer correctly identifies the root cause (font size < 16px triggering iOS auto-zoom) and prescribes the correct fix (set font-size ≥16px or 1rem), aligning with the known-correct outcome. It goes further by elaborating on accessibility tradeoffs, offering multiple implementation…
  > You're experiencing a well-known iOS Safari/WKWebView bug: when an input field has a computed font size smaller than 16px, iOS automatically zooms the page to ~150% on focus to make the text readable, and this zoom does not allow pinch-to-zoom out back to…

### per-month price bug (payments logic)
- **cold** — ✅ reached (better). The model answer correctly identifies the bug in assigning priceString directly to pricePerMonth and provides the fix by computing the monthly equivalent via division by 12. It goes further than the known-correct outcome by offering a complete, production-ready code solution that handles currency…
  > The bug is in the pricePerMonth field assignment in the revenueCat.ts file.
- **guided** — ❌ missed (worse). The model incorrectly concludes the bug is in the UI, not the mapping code, and recommends keeping the flawed `pricePerMonth: pkg.product.priceString` assignment. The known-correct outcome states the bug is exactly there — `priceString` is the full-period price, so assigning it directly to…
  > You're seeing the wrong price ($79.99/mo) for an annual plan because the bug is in how pricePerMonth is being interpreted and displayed in the UI — not in the revenueCat.ts mapping code you shared.

## Failure modes
- **cover_crop / guided** (worse): The model incorrectly identifies 'object-fit: contain' as the fix, but the known-correct outcome states the root issue is the aspect-ratio mismatch and the correct fix is to change the container's aspect-ratio to 9/16 to match the image.…
- **revenuecat_permonth / guided** (worse): The model incorrectly concludes the bug is in the UI, not the mapping code, and recommends keeping the flawed `pricePerMonth: pkg.product.priceString` assignment. The known-correct outcome states the bug is exactly there — `priceString` is…

## Provenance
- n = 6 cells (3 real mined bugs × cold/guided). Pilot, not powered.
- Outcomes judged by an LLM judge anchored to the objective root cause, floor-tested live before the run (garbage→missed, differently-worded-correct→reached).
- Quirks are computed deterministically from the saved outputs (token counts, regex tallies, cold↔guided flips) — no LLM-as-judge in the quirk layer.
- Trust resets on any model-version change.