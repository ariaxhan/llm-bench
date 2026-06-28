# Model Card — `mistral.magistral-small-2509`

> **Outcome reached: 1/6** (cold 1/3 · guided 0/3) · confidence **Low** (pilot, n=6) · generated 2026-06-27
> Detailed replay profile. Every quote below is the model's own output, verbatim.

## At a glance
- **Reached the root cause:** 1/6 cells
- **Cold vs guided:** 1/3 unaided · 0/3 after a bare "still broken" follow-up
- **Latency:** 5662 ms median (5200–6849)
- **Answer length:** 422 output tokens median
- **Cost/task:** unknown (no public pricing recorded — not fabricated)
- ⚠️ **Judge/spine disagreements:** 4 (surfaced, not hidden)

## Signature quirks
_Behavioural tics, each anchored to a count from the runs._

- **Terse** — median 422 output tokens/answer, 0.6× the roster median (712).
- **Commits to one fix** — rarely enumerates alternatives (avg 0.3 option blocks/answer).
- **Regresses on a nudge** — flipped right→wrong once pushed on: cover_crop (the vague follow-up made it worse).

## Task by task

### aspect-ratio crop (CSS layout)
- **cold** — ✅ reached (better). The model answer correctly identifies the aspect-ratio mismatch and recommends the known-correct fix of aligning the container's aspect ratio with the image. It goes further by offering a second valid solution (object-fit: contain) and additional implementation alternatives, making it more…
  > The issue is caused by a mismatch between the aspect ratios of the photo strip and the cover card container.
- **guided** — ❌ missed (worse). The model incorrectly recommends changing the cover card's aspect ratio to 16/9, which is the inverse of the correct 9/16 ratio, and suggests using object-fit: contain, which would not fill the container as intended. The known-correct outcome requires matching the card's aspect ratio to the image's…
  > The issue is a mismatch between the aspect ratios of the photo strip (9:16) and the cover card (3:4).

### iOS WKWebView auto-zoom (mobile-web)
- **cold** — ❌ missed (worse). The model answer incorrectly identifies the root cause as general touch handling and suggests viewport locking or CSS workarounds, while missing the key fact that iOS auto-zooms on inputs with font-size below 16px. It recommends `maximum-scale=1.0, user-scalable=no` which is explicitly called out…
  > iOS WKWebView Zoom Issue Analysis
- **guided** — ❌ missed (worse). The model answer incorrectly identifies the root cause as general touch handling differences rather than the specific iOS behavior of zooming on inputs with font-size below 16px. It recommends the inferior viewport-lock fix (maximum-scale=1, user-scalable=no), which the known-correct outcome…
  > iOS WKWebView Zoom Issue Analysis and Fix

### per-month price bug (payments logic)
- **cold** — ❌ missed (worse). The model answer incorrectly identifies the bug as a double-appending of period units or a flag/priceString formatting issue with RevenueCat, when the actual bug is misusing the full-period priceString as a per-month value. The known-correct outcome requires computing pricePerMonth as price divided…
  > The bug is in the price string construction in the revenueCat.ts code.
- **guided** — ❌ missed (worse). The model incorrectly states that the existing code is correct and suggests no real fix is needed, even recommending logging and external checks instead of addressing the core issue. The known-correct outcome requires computing pricePerMonth as price divided by 12 for annual plans, but the model…
  > The bug is in the price string construction in your revenueCat.ts code.

## Failure modes
- **ios_zoom / cold** (worse): The model answer incorrectly identifies the root cause as general touch handling and suggests viewport locking or CSS workarounds, while missing the key fact that iOS auto-zooms on inputs with font-size below 16px. It recommends…
- **ios_zoom / guided** (worse): The model answer incorrectly identifies the root cause as general touch handling differences rather than the specific iOS behavior of zooming on inputs with font-size below 16px. It recommends the inferior viewport-lock fix…
- **cover_crop / guided** (worse): The model incorrectly recommends changing the cover card's aspect ratio to 16/9, which is the inverse of the correct 9/16 ratio, and suggests using object-fit: contain, which would not fill the container as intended. The known-correct…
- **revenuecat_permonth / cold** (worse): The model answer incorrectly identifies the bug as a double-appending of period units or a flag/priceString formatting issue with RevenueCat, when the actual bug is misusing the full-period priceString as a per-month value. The…
- **revenuecat_permonth / guided** (worse): The model incorrectly states that the existing code is correct and suggests no real fix is needed, even recommending logging and external checks instead of addressing the core issue. The known-correct outcome requires computing…

## Provenance
- n = 6 cells (3 real mined bugs × cold/guided). Pilot, not powered.
- Outcomes judged by an LLM judge anchored to the objective root cause, floor-tested live before the run (garbage→missed, differently-worded-correct→reached).
- Quirks are computed deterministically from the saved outputs (token counts, regex tallies, cold↔guided flips) — no LLM-as-judge in the quirk layer.
- Trust resets on any model-version change.