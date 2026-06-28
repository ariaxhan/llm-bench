# Model Card — `nvidia.nemotron-nano-12b-v2`

> **Outcome reached: 2/6** (cold 1/3 · guided 1/3) · confidence **Low** (pilot, n=6) · generated 2026-06-27
> Detailed replay profile. Every quote below is the model's own output, verbatim.

## At a glance
- **Reached the root cause:** 2/6 cells
- **Cold vs guided:** 1/3 unaided · 1/3 after a bare "still broken" follow-up
- **Latency:** 2770 ms median (2604–3200)
- **Answer length:** 480 output tokens median
- **Cost/task:** unknown (no public pricing recorded — not fabricated)
- ⚠️ **Judge/spine disagreements:** 4 (surfaced, not hidden)

## Signature quirks
_Behavioural tics, each anchored to a count from the runs._

- **Commits to one fix** — rarely enumerates alternatives (avg 0.0 option blocks/answer).

## Task by task

### aspect-ratio crop (CSS layout)
- **cold** — ✅ reached (better). The model answer correctly identifies the aspect-ratio mismatch and prescribes the correct fix of setting the container to 9/16. It goes further by offering a well-reasoned alternative with `object-fit: contain` and explaining trade-offs, making it more complete and user-aware than the…
  > The issue arises because the .cover-card is styled with an aspect-ratio: 3/4 (3:4), which is wider than the photo strip's 9:16 aspect ratio (tall and narrow).
- **guided** — ✅ reached (better). The model answer correctly identifies the aspect-ratio mismatch and provides the correct fix of changing the cover-card to 9/16. It goes further by clearly explaining the root cause, illustrating with example dimensions, and presenting complete corrected code, making it more comprehensive than the…
  > The issue arises because the .cover-card is styled with an aspect-ratio: 3/4 (3:4), which is wider than the 9:16 (tall and narrow) photo strip.

### iOS WKWebView auto-zoom (mobile-web)
- **cold** — ❌ missed (worse). The model incorrectly identifies the root cause as a combination of viewport settings and font inheritance, and recommends the inferior 'user-scalable=no' fix despite acknowledging its accessibility downsides. The known-correct outcome states that iOS auto-zooms specifically when input font size is…
  > The root cause of the zoom behavior when tapping the note input field on iOS is the combination of the viewport meta tag and the font: inherit property on the .desk-input element.
- **guided** — ❌ missed (worse). The model incorrectly identifies the root cause as the combination of `initial-scale=1.0` and font inheritance, and recommends removing `initial-scale=1.0`, which is not the issue. The known-correct outcome states the real cause is iOS auto-zooming on inputs with font size under 16px, and the…
  > The root cause of the zoom behavior is the combination of initial-scale=1.0 in the viewport meta tag and the font: inherit property on the input field.

### per-month price bug (payments logic)
- **cold** — ❌ missed (worse). The model incorrectly assumes that pkg.product.priceString represents a monthly price and that the bug is in the 'price' field formatting. However, the known-correct outcome states that priceString is the full-period price (e.g., $79.99/year for annual), and the real bug is assigning this…
  > The bug lies in the price field of the returned object.
- **guided** — ❌ missed (worse). The model answer incorrectly assumes RevenueCat's priceString for annual plans is already a per-month value (e.g., $6.67/mo), but the known-correct outcome states that priceString is the full-period price ($79.99/year). The model's fix retains priceString unmodified, which perpetuates the bug by…
  > The bug is in the price field of the returned object.

## Failure modes
- **ios_zoom / cold** (worse): The model incorrectly identifies the root cause as a combination of viewport settings and font inheritance, and recommends the inferior 'user-scalable=no' fix despite acknowledging its accessibility downsides. The known-correct outcome…
- **ios_zoom / guided** (worse): The model incorrectly identifies the root cause as the combination of `initial-scale=1.0` and font inheritance, and recommends removing `initial-scale=1.0`, which is not the issue. The known-correct outcome states the real cause is iOS…
- **revenuecat_permonth / cold** (worse): The model incorrectly assumes that pkg.product.priceString represents a monthly price and that the bug is in the 'price' field formatting. However, the known-correct outcome states that priceString is the full-period price (e.g.,…
- **revenuecat_permonth / guided** (worse): The model answer incorrectly assumes RevenueCat's priceString for annual plans is already a per-month value (e.g., $6.67/mo), but the known-correct outcome states that priceString is the full-period price ($79.99/year). The model's fix…

## Provenance
- n = 6 cells (3 real mined bugs × cold/guided). Pilot, not powered.
- Outcomes judged by an LLM judge anchored to the objective root cause, floor-tested live before the run (garbage→missed, differently-worded-correct→reached).
- Quirks are computed deterministically from the saved outputs (token counts, regex tallies, cold↔guided flips) — no LLM-as-judge in the quirk layer.
- Trust resets on any model-version change.