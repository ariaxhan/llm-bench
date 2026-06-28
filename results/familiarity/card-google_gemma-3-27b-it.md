# Model Card — `google.gemma-3-27b-it`

> **Outcome reached: 3/6** (cold 1/3 · guided 2/3) · confidence **Low** (pilot, n=6) · generated 2026-06-27
> Detailed replay profile. Every quote below is the model's own output, verbatim.

## At a glance
- **Reached the root cause:** 3/6 cells
- **Cold vs guided:** 1/3 unaided · 2/3 after a bare "still broken" follow-up
- **Latency:** 12765 ms median (9452–13965)
- **Answer length:** 1086 output tokens median
- **Cost/task:** unknown (no public pricing recorded — not fabricated)
- ⚠️ **Judge/spine disagreements:** 3 (surfaced, not hidden)

## Signature quirks
_Behavioural tics, each anchored to a count from the runs._

- **Hedges** — avg 4.7 hedge words/answer (might/could/possibly/depends).
- **Recovers on a nudge** — flipped wrong→right after the bare "still broken" follow-up on: ios_zoom.

## Task by task

### aspect-ratio crop (CSS layout)
- **cold** — ✅ reached (better). The model answer correctly identifies the aspect-ratio mismatch and the effect of `object-fit: cover`, matching the known-correct outcome. It goes further by offering multiple well-explained solutions with trade-offs, prioritizing the best fix, and asking clarifying questions to guide…
  > Okay, this is a classic aspect ratio mismatch problem.
- **guided** — ✅ reached (better). The model answer correctly identifies the aspect-ratio mismatch and the effect of `object-fit: cover`, providing the correct fix of changing the container's aspect ratio to 9/16. It goes further by offering a secondary fix with `object-fit: contain`, explaining trade-offs, and thoroughly addressing…
  > Okay, this is a classic aspect ratio mismatch problem, compounded by object-fit: cover.

### iOS WKWebView auto-zoom (mobile-web)
- **cold** — ❌ missed (worse). The model answer incorrectly identifies the root cause as iOS's general zoom behavior on keyboard appearance and recommends disabling user-scalable as the preferred fix, which contradicts the known-correct outcome. The correct cause is iOS auto-zooming specifically due to input font-size < 16px,…
  > Okay, this is a classic issue with WKWebView and input fields on iOS, especially when dealing with a hand-rolled DOM.
- **guided** — ✅ reached (better). The model answer correctly identifies the root cause (iOS auto-zoom on small font inputs) and prioritizes the correct fix (setting font-size >=16px) as the preferred solution, while also acknowledging the inferior viewport-lock fix and its accessibility tradeoff. It goes further than the…
  > Okay, this is a classic WKWebView/iOS viewport issue, especially when dealing with hand-rolled DOM and focusing on input fields.

### per-month price bug (payments logic)
- **cold** — ❌ missed (worse). The model answer incorrectly assumes RevenueCat provides a correct monthly equivalent for annual plans and that leaving `pricePerMonth` as `pkg.product.priceString` is acceptable. The known-correct outcome states that `pkg.product.priceString` is the full-period price ($79.99/year), not a per-month…
  > Okay, this is a classic RevenueCat data mapping issue.
- **guided** — ❌ missed (worse). The model incorrectly redefines the `price` field to show the per-month value for annual plans (e.g., '$6.67/mo'), but the known-correct outcome states the `price` should remain '$79.99/yr' for annual plans. The bug is in `pricePerMonth`, which should be computed as `price / 12`, not reused from…
  > Okay, this is a classic RevenueCat pricing display issue.

## Failure modes
- **ios_zoom / cold** (worse): The model answer incorrectly identifies the root cause as iOS's general zoom behavior on keyboard appearance and recommends disabling user-scalable as the preferred fix, which contradicts the known-correct outcome. The correct cause is iOS…
- **revenuecat_permonth / cold** (worse): The model answer incorrectly assumes RevenueCat provides a correct monthly equivalent for annual plans and that leaving `pricePerMonth` as `pkg.product.priceString` is acceptable. The known-correct outcome states that…
- **revenuecat_permonth / guided** (worse): The model incorrectly redefines the `price` field to show the per-month value for annual plans (e.g., '$6.67/mo'), but the known-correct outcome states the `price` should remain '$79.99/yr' for annual plans. The bug is in `pricePerMonth`,…

## Provenance
- n = 6 cells (3 real mined bugs × cold/guided). Pilot, not powered.
- Outcomes judged by an LLM judge anchored to the objective root cause, floor-tested live before the run (garbage→missed, differently-worded-correct→reached).
- Quirks are computed deterministically from the saved outputs (token counts, regex tallies, cold↔guided flips) — no LLM-as-judge in the quirk layer.
- Trust resets on any model-version change.