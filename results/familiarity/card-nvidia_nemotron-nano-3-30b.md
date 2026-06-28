# Model Card — `nvidia.nemotron-nano-3-30b`

> **Outcome reached: 4/6** (cold 1/3 · guided 3/3) · confidence **Low** (pilot, n=6) · generated 2026-06-27
> Detailed replay profile. Every quote below is the model's own output, verbatim.

## At a glance
- **Reached the root cause:** 4/6 cells
- **Cold vs guided:** 1/3 unaided · 3/3 after a bare "still broken" follow-up
- **Latency:** 4918 ms median (2401–8796)
- **Answer length:** 1436 output tokens median
- **Cost/task:** unknown (no public pricing recorded — not fabricated)
- ⚠️ **Judge/spine disagreements:** 2 (surfaced, not hidden)

## Signature quirks
_Behavioural tics, each anchored to a count from the runs._

- **Verbose** — median 1436 output tokens/answer, 2.0× the roster median (712).
- **Sprays options** — listed up to 8 separate fixes in one answer (avg 3.2/answer); offers a menu rather than committing.
- **Recovers on a nudge** — flipped wrong→right after the bare "still broken" follow-up on: ios_zoom, revenuecat_permonth.

## Task by task

### aspect-ratio crop (CSS layout)
- **cold** — ✅ reached (better). The model answer correctly identifies the aspect-ratio mismatch and the effect of `object-fit: cover`, matching the known-correct outcome. It goes further by providing multiple practical solutions (matching aspect ratio, using `contain`, pre-cropping), explaining trade-offs, and offering copy-paste…
  > Why the cover image is being cropped on the top and bottom
- **guided** — ✅ reached (better). The model answer correctly identifies the aspect-ratio mismatch and provides the core fix of aligning the container's aspect ratio with the image's 9:16. It goes further by offering two well-explained alternatives (using `contain` or adjusting `object-position`), including practical code examples…
  > Why the image is being cropped at the top and bottom

### iOS WKWebView auto-zoom (mobile-web)
- **cold** — ❌ missed (worse). The model answer incorrectly identifies the root cause and proposes suboptimal or incorrect fixes. It suggests workarounds like changing input type to 'search', using JavaScript to scroll, or temporarily increasing font size on focus, but misses the known-correct solution: setting the input's…
  > The page is zoomed because iOS Safari automatically enlarges the viewport when a text‑input receives focus (the “input‑zoom‑on‑focus” behaviour).
- **guided** — ✅ reached (better). The model correctly identifies the root cause (iOS auto-zoom on focus for inputs with font size <16px, not 13px) and recommends setting font-size to 16px, aligning with the known-correct outcome. It improves upon it by noting the actual threshold is effectively 16px (not ~13px) and provides a more…
  > iOS Safari (the WKWebView that powers Capacitor) treats a focus event on an input/textarea as a cue to “zoom to make the caret visible”.

### per-month price bug (payments logic)
- **cold** — ❌ missed (worse). The model answer incorrectly identifies the bug as appending '/yr' or '/mo' to priceString, when the real issue is that pricePerMonth is set to priceString (the full annual price) instead of the computed per-month value. The known-correct outcome states that pkg.product.priceString is the total…
  > Bug: The price string is built with the raw pkg.product.priceString and then a hard‑coded suffix (/yr or /mo) is appended.
- **guided** — ✅ reached (better). The model answer correctly identifies that pkg.product.priceString represents the full annual price and should not be used directly for pricePerMonth, and it proposes multiple valid fixes including using subscriptionPeriod for accurate conversion. It goes beyond the known-correct outcome by…
  > The bug is in the price (and consequently pricePerMonth) calculation inside the RevenueCat‑to‑paywall mapper:

## Failure modes
- **ios_zoom / cold** (worse): The model answer incorrectly identifies the root cause and proposes suboptimal or incorrect fixes. It suggests workarounds like changing input type to 'search', using JavaScript to scroll, or temporarily increasing font size on focus, but…
- **revenuecat_permonth / cold** (worse): The model answer incorrectly identifies the bug as appending '/yr' or '/mo' to priceString, when the real issue is that pricePerMonth is set to priceString (the full annual price) instead of the computed per-month value. The known-correct…

## Provenance
- n = 6 cells (3 real mined bugs × cold/guided). Pilot, not powered.
- Outcomes judged by an LLM judge anchored to the objective root cause, floor-tested live before the run (garbage→missed, differently-worded-correct→reached).
- Quirks are computed deterministically from the saved outputs (token counts, regex tallies, cold↔guided flips) — no LLM-as-judge in the quirk layer.
- Trust resets on any model-version change.