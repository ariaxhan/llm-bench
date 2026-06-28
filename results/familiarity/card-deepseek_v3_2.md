# Model Card — `deepseek.v3.2`

> **Outcome reached: 5/6** (cold 2/3 · guided 3/3) · confidence **Low** (pilot, n=6) · generated 2026-06-27
> Detailed replay profile. Every quote below is the model's own output, verbatim.

## At a glance
- **Reached the root cause:** 5/6 cells
- **Cold vs guided:** 2/3 unaided · 3/3 after a bare "still broken" follow-up
- **Latency:** 5222 ms median (4712–7274)
- **Answer length:** 505 output tokens median
- **Cost/task:** $0.001084 avg
- ⚠️ **Judge/spine disagreements:** 1 (surfaced, not hidden)

## Signature quirks
_Behavioural tics, each anchored to a count from the runs._

- **Sprays options** — listed up to 5 separate fixes in one answer (avg 1.5/answer); offers a menu rather than committing.
- **Recovers on a nudge** — flipped wrong→right after the bare "still broken" follow-up on: revenuecat_permonth.

## Task by task

### aspect-ratio crop (CSS layout)
- **cold** — ✅ reached (better). The model correctly identifies the aspect ratio mismatch and the effect of object-fit: cover, matching the known-correct outcome. It goes further by offering multiple valid solutions with clear trade-offs, including recommendations and visual explanation, making it more comprehensive and actionable…
  > The issue is a mismatch in aspect ratios between your photo strip and the cover card container.
- **guided** — ✅ reached (better). The model answer correctly identifies the aspect-ratio mismatch and the effect of `object-fit: cover`, matching the known-correct outcome, and additionally provides multiple alternative fixes (`contain`, `scale-down`) with practical CSS examples, making it more complete and helpful than the outcome…
  > The problem is that you have two conflicting aspect ratios and object-fit: cover is causing the top/bottom crop.

### iOS WKWebView auto-zoom (mobile-web)
- **cold** — ✅ reached (better). The model answer correctly identifies the root cause (font size below 16px triggering iOS auto-zoom) and the correct fix (set font-size ≥16px), while also providing additional context, multiple solution options, accessibility tradeoffs, and Capacitor-specific considerations. It goes beyond the…
  > The root cause is iOS Safari's "text field zoom" behavior triggered when:
- **guided** — ✅ reached (worse). The model answer correctly identifies the root cause and the primary fix (setting font-size to >=16px), but then recommends a viewport meta tag with maximum-scale=1 and user-scalable=no as a fallback, which the known-correct outcome explicitly rejects as inferior due to accessibility harm. It also…
  > Root cause: iOS Safari (and WKWebView) automatically zooms into any input field with a font size less than 16px when tapped, to improve readability.

### per-month price bug (payments logic)
- **cold** — ❌ missed (worse). The model answer incorrectly assumes RevenueCat's priceString includes period information and misidentifies the root cause. The known-correct outcome states that priceString contains only the raw price (e.g., '$79.99') without any period suffix, and the bug is in directly assigning priceString to…
  > The bug is in your price formatting logic.
- **guided** — ✅ reached (better). The model answer correctly identifies the core bug — misusing priceString for pricePerMonth — and provides a more complete fix by handling both annual and monthly cases with proper formatting. It also adds valuable debugging advice not in the known-correct outcome, making it meaningfully superior.
  > The bug is in your code. You're incorrectly appending "/yr" or "/mo" to the full price string from RevenueCat, which already includes its own frequency suffix.

## Failure modes
- **ios_zoom / guided** (worse): The model answer correctly identifies the root cause and the primary fix (setting font-size to >=16px), but then recommends a viewport meta tag with maximum-scale=1 and user-scalable=no as a fallback, which the known-correct outcome…
- **revenuecat_permonth / cold** (worse): The model answer incorrectly assumes RevenueCat's priceString includes period information and misidentifies the root cause. The known-correct outcome states that priceString contains only the raw price (e.g., '$79.99') without any period…

## Provenance
- n = 6 cells (3 real mined bugs × cold/guided). Pilot, not powered.
- Outcomes judged by an LLM judge anchored to the objective root cause, floor-tested live before the run (garbage→missed, differently-worded-correct→reached).
- Quirks are computed deterministically from the saved outputs (token counts, regex tallies, cold↔guided flips) — no LLM-as-judge in the quirk layer.
- Trust resets on any model-version change.