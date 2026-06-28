# Model Card — `moonshot.kimi-k2-thinking`

> **Outcome reached: 6/6** (cold 3/3 · guided 3/3) · confidence **Low** (pilot, n=6) · generated 2026-06-27
> Detailed replay profile. Every quote below is the model's own output, verbatim.

## At a glance
- **Reached the root cause:** 6/6 cells
- **Cold vs guided:** 3/3 unaided · 3/3 after a bare "still broken" follow-up
- **Latency:** 12284 ms median (6690–35731)
- **Answer length:** 1757 output tokens median
- **Cost/task:** unknown (no public pricing recorded — not fabricated)

## Signature quirks
_Behavioural tics, each anchored to a count from the runs._

- **Verbose** — median 1757 output tokens/answer, 2.5× the roster median (712).
- **Thinks out loud (hidden)** — emits a reasoning block on 6/6 cells, avg 7904 chars of scratchpad the judge never sees.
- **Commits to one fix** — rarely enumerates alternatives (avg 0.0 option blocks/answer).

## Task by task

### aspect-ratio crop (CSS layout)
- **cold** — ✅ reached (better). The model answer correctly identifies the aspect-ratio mismatch and explains the cropping due to object-fit: cover, aligning with the known-correct outcome. It goes further by offering multiple valid solutions—using object-fit: contain, object-fit: fill, and changing the container's…
  > The strip’s native aspect ratio is 9 : 16 (≈ 0.56) while the cover card is forced to 3 : 4 (≈ 0.75).
- **guided** — ✅ reached (better). The model answer correctly identifies the aspect-ratio mismatch and the effect of `object-fit: cover`, and provides two valid fixes: using `object-fit: contain` with background fill for compatibility, and the preferred solution of matching the container's aspect-ratio to 9/16. The latter fully…
  > The cropping happens because your 9:16 image is taller than the 3:4 container, and object-fit: cover fills the space by cropping the excess.

### iOS WKWebView auto-zoom (mobile-web)
- **cold** — ✅ reached (better). The model answer correctly identifies the root cause (iOS auto-zoom on inputs with font-size < 16px) and the correct fix (set font-size >=16px), while explicitly rejecting the inferior viewport-lock approach. It goes further by offering a nuanced hybrid solution with transform scaling and…
  > iOS Safari/WKWebView automatically zooms into any <input> or <textarea> that has a computed font-size smaller than 16px when it receives focus.
- **guided** — ✅ reached (better). The model answer correctly identifies the root cause (font-size < 16px triggering iOS zoom) and prescribes the correct fix (set font-size >=16px), while also warning against the inferior viewport-lock approach. It goes further by offering a mobile-only workaround using @supports and including…
  > iOS Safari/WKWebView automatically zooms into <input> and <textarea> elements when their font-size is less than 16px.

### per-month price bug (payments logic)
- **cold** — ✅ reached (better). The model answer correctly identifies the bug in using priceString for pricePerMonth and provides a complete fix that computes the monthly price by dividing the numeric price by 12 and formatting it with the correct currency. It improves upon the known-correct outcome by including proper currency…
  > Bug location: The pricePerMonth field is incorrectly using pkg.product.priceString (the full period price) instead of calculating the monthly equivalent for annual plans.
- **guided** — ✅ reached (better). The model answer correctly identifies the bug in assigning the full-period priceString to pricePerMonth and provides the fix by computing the monthly value via division by 12. It improves upon the known-correct outcome by offering a more complete solution that includes currency symbol handling,…
  > The bug is in the pricePerMonth field.

## Failure modes
- None — reached every cell in this pilot.

## Provenance
- n = 6 cells (3 real mined bugs × cold/guided). Pilot, not powered.
- Outcomes judged by an LLM judge anchored to the objective root cause, floor-tested live before the run (garbage→missed, differently-worded-correct→reached).
- Quirks are computed deterministically from the saved outputs (token counts, regex tallies, cold↔guided flips) — no LLM-as-judge in the quirk layer.
- Trust resets on any model-version change.