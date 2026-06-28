# Model Card — `nvidia.nemotron-nano-9b-v2`

> **Outcome reached: 3/6** (cold 2/3 · guided 1/3) · confidence **Low** (pilot, n=6) · generated 2026-06-27
> Detailed replay profile. Every quote below is the model's own output, verbatim.

## At a glance
- **Reached the root cause:** 3/6 cells
- **Cold vs guided:** 2/3 unaided · 1/3 after a bare "still broken" follow-up
- **Latency:** 11036 ms median (7667–69160)
- **Answer length:** 1893 output tokens median
- **Cost/task:** unknown (no public pricing recorded — not fabricated)
- ⚠️ **Judge/spine disagreements:** 2 (surfaced, not hidden)

## Signature quirks
_Behavioural tics, each anchored to a count from the runs._

- **Verbose** — median 1893 output tokens/answer, 2.7× the roster median (712).
- **Sprays options** — listed up to 4 separate fixes in one answer (avg 0.7/answer); offers a menu rather than committing.
- **Hedges** — avg 13.0 hedge words/answer (might/could/possibly/depends).
- **Regresses on a nudge** — flipped right→wrong once pushed on: ios_zoom (the vague follow-up made it worse).

## Task by task

### aspect-ratio crop (CSS layout)
- **cold** — ✅ reached (equivalent). The model answer correctly identifies the aspect ratio mismatch between the 3:4 cover card and the 9:16 photo strip as the cause of top and bottom cropping due to object-fit: cover. It correctly recommends changing the cover card's aspect ratio to 9:16 to fix the issue, matching the known-correct…
  > Okay, let's try to figure out why the cover image is being cropped at the top and bottom.
- **guided** — ✅ reached (better). The model answer correctly identifies the aspect-ratio mismatch and the effect of object-fit: cover, and provides the correct fix of aligning the cover card's aspect ratio to 9:16. It goes further by analyzing the scaling mathematically and offering a well-reasoned alternative (object-fit:…
  > Okay, let's try to figure out why the cover image is being cropped on the top and bottom.

### iOS WKWebView auto-zoom (mobile-web)
- **cold** — ✅ reached (equivalent). The model correctly identifies the root cause as iOS auto-zooming on inputs with font sizes below 16px due to accessibility heuristics and recommends increasing the font size to 16px or higher as the preferred fix. It also acknowledges that using user-scalable=no is harmful to accessibility,…
  > Okay, let's try to figure out why the iPhone is zooming in when the user taps the input field.
- **guided** — ❌ missed (worse). The model answer incorrectly identifies the root cause as potential JavaScript interference or layout shifts, while missing the known-correct cause: iOS auto-zooms on inputs with font-size below 16px. It suggests stabilizing layout and checking JavaScript, but fails to recommend the correct…
  > Okay, let's tackle this problem.

### per-month price bug (payments logic)
- **cold** — ❌ missed (worse). The model answer incorrectly focuses on the 'annual' flag being misset or the priceString suffix logic, completely missing the core issue: pkg.product.priceString is the full annual price ($79.99), not a per-month value, so assigning it directly to pricePerMonth is wrong. The known-correct outcome…
  > Okay, let's take a look at the problem.
- **guided** — ❌ missed (worse). The model answer incorrectly identifies the bug as a misapplied 'annual' flag or suffix logic, when the known-correct outcome states the bug is in assigning the full-period priceString to pricePerMonth, causing $79.99/mo to display for an annual plan. The real fix is to compute pricePerMonth as…
  > Okay, let's tackle this problem.

## Failure modes
- **ios_zoom / guided** (worse): The model answer incorrectly identifies the root cause as potential JavaScript interference or layout shifts, while missing the known-correct cause: iOS auto-zooms on inputs with font-size below 16px. It suggests stabilizing layout and…
- **revenuecat_permonth / cold** (worse): The model answer incorrectly focuses on the 'annual' flag being misset or the priceString suffix logic, completely missing the core issue: pkg.product.priceString is the full annual price ($79.99), not a per-month value, so assigning it…
- **revenuecat_permonth / guided** (worse): The model answer incorrectly identifies the bug as a misapplied 'annual' flag or suffix logic, when the known-correct outcome states the bug is in assigning the full-period priceString to pricePerMonth, causing $79.99/mo to display for an…

## Provenance
- n = 6 cells (3 real mined bugs × cold/guided). Pilot, not powered.
- Outcomes judged by an LLM judge anchored to the objective root cause, floor-tested live before the run (garbage→missed, differently-worded-correct→reached).
- Quirks are computed deterministically from the saved outputs (token counts, regex tallies, cold↔guided flips) — no LLM-as-judge in the quirk layer.
- Trust resets on any model-version change.