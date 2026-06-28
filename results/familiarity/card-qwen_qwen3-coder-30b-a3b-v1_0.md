# Model Card — `qwen.qwen3-coder-30b-a3b-v1:0`

> **Outcome reached: 3/6** (cold 1/3 · guided 2/3) · confidence **Low** (pilot, n=6) · generated 2026-06-27
> Detailed replay profile. Every quote below is the model's own output, verbatim.

## At a glance
- **Reached the root cause:** 3/6 cells
- **Cold vs guided:** 1/3 unaided · 2/3 after a bare "still broken" follow-up
- **Latency:** 1860 ms median (971–56996)
- **Answer length:** 516 output tokens median
- **Cost/task:** unknown (no public pricing recorded — not fabricated)
- ⚠️ **Judge/spine disagreements:** 3 (surfaced, not hidden)

## Signature quirks
_Behavioural tics, each anchored to a count from the runs._

- **Sprays options** — listed up to 4 separate fixes in one answer (avg 1.2/answer); offers a menu rather than committing.
- **Recovers on a nudge** — flipped wrong→right after the bare "still broken" follow-up on: ios_zoom.

## Task by task

### aspect-ratio crop (CSS layout)
- **cold** — ✅ reached (worse). The model initially misanalyzed the cropping direction, stating the card is wider and would crop sides, but then corrected to top/bottom. Despite arriving at the correct fix (matching aspect ratios), the confusion in reasoning and incorrect intermediate logic makes the explanation less reliable…
  > The issue is with the aspect ratio mismatch between the photo strip and the cover card container.
- **guided** — ✅ reached (equivalent). The model correctly identifies the aspect ratio mismatch between the 9:16 image and 3:4 container causing the cropping with object-fit: cover, and prescribes the fix of changing the container's aspect-ratio to 9/16 to match the image, which aligns exactly with the known-correct outcome.
  > The issue is with the aspect ratio mismatch between your photo strip (9:16) and the cover card container (3:4).

### iOS WKWebView auto-zoom (mobile-web)
- **cold** — ❌ missed (worse). The model answer incorrectly identifies the root cause as iOS failing to restore zoom after keyboard dismissal, rather than correctly identifying that iOS auto-zooms on focus for inputs with font-size below 16px. It recommends the inferior viewport-lock fix (maximum-scale=1.0, user-scalable=no),…
  > The issue is caused by iOS Safari's automatic zoom behavior when an input field gains focus.
- **guided** — ✅ reached (better). The model answer identifies both the root cause (iOS auto-zoom on small font inputs) and provides two fixes: a viewport lock (with noted accessibility tradeoffs) and the preferred, correct fix of setting font-size to 16px. It explicitly acknowledges the accessibility downside of the viewport…
  > The root cause is that iOS Safari automatically zooms to fit input fields when they gain focus, but your viewport meta tag isn't properly configured to prevent this behavior.

### per-month price bug (payments logic)
- **cold** — ❌ missed (worse). The model answer incorrectly assumes that pkg.product.priceString includes the period (like '/yr') and focuses on parsing or replacing it, but the known-correct outcome states that priceString is just the full-period price amount (e.g., $79.99) without any '/yr' suffix. The model overcomplicates…
  > The bug is in how the pricePerMonth is being set.
- **guided** — ❌ missed (worse). The model incorrectly assumes RevenueCat provides a pricePerMonth field. The known-correct outcome states that pkg.product.priceString is the full-period price and must be divided by 12 for annual plans to get the monthly equivalent. The model's proposed fix relies on a non-existent or unverified…
  > Looking at the code, I can see the bug clearly now.

## Failure modes
- **ios_zoom / cold** (worse): The model answer incorrectly identifies the root cause as iOS failing to restore zoom after keyboard dismissal, rather than correctly identifying that iOS auto-zooms on focus for inputs with font-size below 16px. It recommends the inferior…
- **cover_crop / cold** (worse): The model initially misanalyzed the cropping direction, stating the card is wider and would crop sides, but then corrected to top/bottom. Despite arriving at the correct fix (matching aspect ratios), the confusion in reasoning and…
- **revenuecat_permonth / cold** (worse): The model answer incorrectly assumes that pkg.product.priceString includes the period (like '/yr') and focuses on parsing or replacing it, but the known-correct outcome states that priceString is just the full-period price amount (e.g.,…
- **revenuecat_permonth / guided** (worse): The model incorrectly assumes RevenueCat provides a pricePerMonth field. The known-correct outcome states that pkg.product.priceString is the full-period price and must be divided by 12 for annual plans to get the monthly equivalent. The…

## Provenance
- n = 6 cells (3 real mined bugs × cold/guided). Pilot, not powered.
- Outcomes judged by an LLM judge anchored to the objective root cause, floor-tested live before the run (garbage→missed, differently-worded-correct→reached).
- Quirks are computed deterministically from the saved outputs (token counts, regex tallies, cold↔guided flips) — no LLM-as-judge in the quirk layer.
- Trust resets on any model-version change.