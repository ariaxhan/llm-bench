# Model Card — `qwen.qwen3-32b-v1:0`

> **Outcome reached: 3/6** (cold 2/3 · guided 1/3) · confidence **Low** (pilot, n=6) · generated 2026-06-27
> Detailed replay profile. Every quote below is the model's own output, verbatim.

## At a glance
- **Reached the root cause:** 3/6 cells
- **Cold vs guided:** 2/3 unaided · 1/3 after a bare "still broken" follow-up
- **Latency:** 4475 ms median (2415–5697)
- **Answer length:** 664 output tokens median
- **Cost/task:** unknown (no public pricing recorded — not fabricated)
- ⚠️ **Judge/spine disagreements:** 3 (surfaced, not hidden)

## Signature quirks
_Behavioural tics, each anchored to a count from the runs._

- **Commits to one fix** — rarely enumerates alternatives (avg 0.3 option blocks/answer).
- **Decorates** — uses emoji/symbols in every answer.
- **Regresses on a nudge** — flipped right→wrong once pushed on: ios_zoom (the vague follow-up made it worse).

## Task by task

### aspect-ratio crop (CSS layout)
- **cold** — ✅ reached (better). The model answer correctly identifies the aspect-ratio mismatch and provides the exact fix of aligning the container's aspect ratio to 9:16, matching the known-correct outcome. It goes further by offering a second valid alternative (object-fit: contain) and a detailed comparison of options, making…
  > The issue you're encountering is due to a mismatch in aspect ratios between the photo strip image and the cover card container.
- **guided** — ✅ reached (better). The model answer correctly identifies the aspect-ratio mismatch and provides the known-correct fix of aligning the container's aspect ratio to 9:16. It goes further by offering an additional valid solution using `object-fit: contain`, making it more complete and flexible than the outcome, which…
  > The issue is due to a mismatch between the aspect ratio of the photo strip image (9:16) and the aspect ratio of the container (3:4).

### iOS WKWebView auto-zoom (mobile-web)
- **cold** — ✅ reached (better). The model answer correctly identifies the root cause (font size < 16px triggering iOS auto-zoom) and prescribes the correct fix (set font-size to at least 16px). It goes further by explicitly warning against the inferior viewport-lock fix and discussing accessibility tradeoffs, making it more…
  > The issue you're encountering — zooming on input focus in a Capacitor + WKWebView iOS app — is a known behavior in iOS Safari and WKWebView when certain input fields are focused and have font sizes below a certain threshold.
- **guided** — ❌ missed (worse). The model answer recommends the inferior viewport-lock fix (maximum-scale=1.0, user-scalable=no), which the known-correct outcome explicitly warns against because it harms accessibility by disabling pinch-zoom app-wide. While it does suggest increasing font-size to 16px (a correct fix), it pairs it…
  > Thanks for the follow-up — I'll give you a direct fix that should work reliably in Capacitor + WKWebView on iOS, and explain the root cause and accessibility considerations afterward.

### per-month price bug (payments logic)
- **cold** — ❌ missed (worse). The model incorrectly identifies the bug as appending '/yr' to priceString, but the real issue is assigning the full annual priceString to pricePerMonth without dividing by 12. The model's fix leaves pricePerMonth unchanged, which perpetuates the bug by showing $79.99/mo for an annual plan. The…
  > The bug lies in how the price is being constructed in your revenueCat.ts file.
- **guided** — ❌ missed (worse). The model misidentifies the root cause, claiming `priceString` contains the per-period price when it actually contains the full-period price. It incorrectly suggests using `pricePerMonth` as if it were already correct, while the known-correct outcome states that `pricePerMonth` must be computed as…
  > The issue is in how the price is being displayed in the paywall — specifically, the suffix (/yr or /mo) is being added to the priceString, which already includes the per-period price (e.g., $79.99 for an annual plan).

## Failure modes
- **ios_zoom / guided** (worse): The model answer recommends the inferior viewport-lock fix (maximum-scale=1.0, user-scalable=no), which the known-correct outcome explicitly warns against because it harms accessibility by disabling pinch-zoom app-wide. While it does…
- **revenuecat_permonth / cold** (worse): The model incorrectly identifies the bug as appending '/yr' to priceString, but the real issue is assigning the full annual priceString to pricePerMonth without dividing by 12. The model's fix leaves pricePerMonth unchanged, which…
- **revenuecat_permonth / guided** (worse): The model misidentifies the root cause, claiming `priceString` contains the per-period price when it actually contains the full-period price. It incorrectly suggests using `pricePerMonth` as if it were already correct, while the…

## Provenance
- n = 6 cells (3 real mined bugs × cold/guided). Pilot, not powered.
- Outcomes judged by an LLM judge anchored to the objective root cause, floor-tested live before the run (garbage→missed, differently-worded-correct→reached).
- Quirks are computed deterministically from the saved outputs (token counts, regex tallies, cold↔guided flips) — no LLM-as-judge in the quirk layer.
- Trust resets on any model-version change.