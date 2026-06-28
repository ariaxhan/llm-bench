# Model Card — `us.amazon.nova-pro-v1:0`

> **Outcome reached: 4/6** (cold 2/3 · guided 2/3) · confidence **Low** (pilot, n=6) · generated 2026-06-27
> Detailed replay profile. Every quote below is the model's own output, verbatim.

## At a glance
- **Reached the root cause:** 4/6 cells
- **Cold vs guided:** 2/3 unaided · 2/3 after a bare "still broken" follow-up
- **Latency:** 2855 ms median (2309–3689)
- **Answer length:** 538 output tokens median
- **Cost/task:** unknown (no public pricing recorded — not fabricated)
- ⚠️ **Judge/spine disagreements:** 2 (surfaced, not hidden)

## Signature quirks
_Behavioural tics, each anchored to a count from the runs._

- **Sprays options** — listed up to 4 separate fixes in one answer (avg 1.0/answer); offers a menu rather than committing.
- **Recovers on a nudge** — flipped wrong→right after the bare "still broken" follow-up on: ios_zoom.
- **Regresses on a nudge** — flipped right→wrong once pushed on: revenuecat_permonth (the vague follow-up made it worse).

## Task by task

### aspect-ratio crop (CSS layout)
- **cold** — ✅ reached (better). The model correctly identifies the aspect-ratio mismatch and the effect of object-fit: cover, and provides the correct fix of aligning the cover-card's aspect ratio to 9:16. It goes further by offering additional valid alternatives (contain, object-position), making the answer more complete and…
  > The issue you're encountering with the cover image being cropped on the event board is due to the CSS styles applied to the .cover-card and its child img element.
- **guided** — ✅ reached (worse). The model correctly identifies the aspect-ratio mismatch and suggests changing the cover card's aspect ratio to 9/16, which aligns with the known-correct outcome. However, it also presents alternative solutions, including 'object-fit: contain' as the recommended fix, which contradicts the required…
  > Certainly! Let's break down the issue and provide a solution.

### iOS WKWebView auto-zoom (mobile-web)
- **cold** — ❌ missed (worse). The model answer correctly identifies the root cause (font size < 16px triggering iOS zoom) and suggests setting font-size to 16px, which aligns with the known-correct outcome. However, it recommends the inferior viewport-lock fix (maximum-scale=1.0, user-scalable=no) as a valid option, which the…
  > The issue you're experiencing is a common one on iOS devices when using WKWebView and custom input fields.
- **guided** — ✅ reached (equivalent). The model correctly identifies the root cause (iOS zooming on inputs with font size <16px) and recommends setting the input font size to at least 16px, which matches the known-correct outcome. It avoids the inferior viewport-lock fix and acknowledges accessibility considerations, aligning with the…
  > Certainly! Let's break down the issue and provide a solution.

### per-month price bug (payments logic)
- **cold** — ✅ reached (better). The model answer correctly identifies the bug in using priceString directly for pricePerMonth and provides a complete fix that computes the monthly price by dividing the annual price by 12. It goes further by handling both annual and monthly cases explicitly and includes parsing and formatting…
  > The issue you're encountering is due to the way the price is being constructed in your code.
- **guided** — ❌ missed (worse). The model misidentifies the bug as being in the 'price' field construction and suggests using 'pricePerMonth' for monthly plans, but the actual bug is that 'pricePerMonth' incorrectly uses 'priceString' (the full annual price) instead of computing the monthly equivalent. The known-correct outcome…
  > Based on the provided code snippet and the issue description, the bug seems to be in the way the price is being displayed for the annual plan.

## Failure modes
- **ios_zoom / cold** (worse): The model answer correctly identifies the root cause (font size < 16px triggering iOS zoom) and suggests setting font-size to 16px, which aligns with the known-correct outcome. However, it recommends the inferior viewport-lock fix…
- **cover_crop / guided** (worse): The model correctly identifies the aspect-ratio mismatch and suggests changing the cover card's aspect ratio to 9/16, which aligns with the known-correct outcome. However, it also presents alternative solutions, including 'object-fit:…
- **revenuecat_permonth / guided** (worse): The model misidentifies the bug as being in the 'price' field construction and suggests using 'pricePerMonth' for monthly plans, but the actual bug is that 'pricePerMonth' incorrectly uses 'priceString' (the full annual price) instead of…

## Provenance
- n = 6 cells (3 real mined bugs × cold/guided). Pilot, not powered.
- Outcomes judged by an LLM judge anchored to the objective root cause, floor-tested live before the run (garbage→missed, differently-worded-correct→reached).
- Quirks are computed deterministically from the saved outputs (token counts, regex tallies, cold↔guided flips) — no LLM-as-judge in the quirk layer.
- Trust resets on any model-version change.