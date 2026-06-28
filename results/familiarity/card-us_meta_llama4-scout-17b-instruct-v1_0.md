# Model Card — `us.meta.llama4-scout-17b-instruct-v1:0`

> **Outcome reached: 4/6** (cold 2/3 · guided 2/3) · confidence **Low** (pilot, n=6) · generated 2026-06-27
> Detailed replay profile. Every quote below is the model's own output, verbatim.

## At a glance
- **Reached the root cause:** 4/6 cells
- **Cold vs guided:** 2/3 unaided · 2/3 after a bare "still broken" follow-up
- **Latency:** 3612 ms median (3091–4083)
- **Answer length:** 688 output tokens median
- **Cost/task:** $0.000475 avg
- ⚠️ **Judge/spine disagreements:** 2 (surfaced, not hidden)

## Signature quirks
_Behavioural tics, each anchored to a count from the runs._

- **Commits to one fix** — rarely enumerates alternatives (avg 0.0 option blocks/answer).
- **Recovers on a nudge** — flipped wrong→right after the bare "still broken" follow-up on: ios_zoom.
- **Regresses on a nudge** — flipped right→wrong once pushed on: cover_crop (the vague follow-up made it worse).

## Task by task

### aspect-ratio crop (CSS layout)
- **cold** — ✅ reached (better). The model answer correctly identifies the aspect-ratio mismatch and provides the core fix of changing the cover card to 9/16, as in the known-correct outcome. It goes further by offering additional context, alternative solutions, and improved usability with object-fit: contain, making it more…
  > Step-by-step analysis of the problem:
- **guided** — ❌ missed (worse). The model answer incorrectly suggests changing object-fit to 'contain' to fix the cropping, but the known-correct outcome identifies that the root issue is an aspect-ratio mismatch and the fix is to align the cover card's aspect ratio with the image's 9:16. Changing to 'contain' would prevent…
  > Step-by-step analysis of the problem:

### iOS WKWebView auto-zoom (mobile-web)
- **cold** — ❌ missed (worse). The model incorrectly identifies the root cause as WKWebView ignoring viewport settings, when it is actually iOS Safari/WKWebView auto-zooming due to a font size below 16px. The model recommends the inferior viewport-lock fix (maximum-scale=1, user-scalable=no), which contradicts the known-correct…
  > Step-by-step analysis of the problem:
- **guided** — ✅ reached (worse). The model answer correctly identifies the root cause (font size < 16px triggering zoom) and suggests setting font-size to 16px, which aligns with the known-correct outcome. However, it also recommends the inferior viewport-lock fix (maximum-scale=1, user-scalable=no), which harms accessibility and…
  > Step-by-step analysis of the problem:

### per-month price bug (payments logic)
- **cold** — ✅ reached (better). The model correctly identifies that pkg.product.priceString is the full-period price and must be divided by 12 for annual plans to compute pricePerMonth. It provides a working fix with string parsing and division, and additionally suggests a more robust approach using RevenueCat's potential…
  > Step-by-step analysis of the problem:
- **guided** — ✅ reached (better). The model answer correctly identifies that pkg.product.priceString represents the full-period price and should not be used directly for pricePerMonth in annual plans. It goes further by providing a complete, robust fix with proper calculation of monthly price (dividing by 12), handling formatting,…
  > Step-by-step analysis of the problem:

## Failure modes
- **ios_zoom / cold** (worse): The model incorrectly identifies the root cause as WKWebView ignoring viewport settings, when it is actually iOS Safari/WKWebView auto-zooming due to a font size below 16px. The model recommends the inferior viewport-lock fix…
- **ios_zoom / guided** (worse): The model answer correctly identifies the root cause (font size < 16px triggering zoom) and suggests setting font-size to 16px, which aligns with the known-correct outcome. However, it also recommends the inferior viewport-lock fix…
- **cover_crop / guided** (worse): The model answer incorrectly suggests changing object-fit to 'contain' to fix the cropping, but the known-correct outcome identifies that the root issue is an aspect-ratio mismatch and the fix is to align the cover card's aspect ratio with…

## Provenance
- n = 6 cells (3 real mined bugs × cold/guided). Pilot, not powered.
- Outcomes judged by an LLM judge anchored to the objective root cause, floor-tested live before the run (garbage→missed, differently-worded-correct→reached).
- Quirks are computed deterministically from the saved outputs (token counts, regex tallies, cold↔guided flips) — no LLM-as-judge in the quirk layer.
- Trust resets on any model-version change.