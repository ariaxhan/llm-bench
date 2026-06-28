# Model Card — `us.amazon.nova-2-lite-v1:0`

> **Outcome reached: 5/6** (cold 2/3 · guided 3/3) · confidence **Low** (pilot, n=6) · generated 2026-06-27
> Detailed replay profile. Every quote below is the model's own output, verbatim.

## At a glance
- **Reached the root cause:** 5/6 cells
- **Cold vs guided:** 2/3 unaided · 3/3 after a bare "still broken" follow-up
- **Latency:** 5344 ms median (3423–8034)
- **Answer length:** 1076 output tokens median
- **Cost/task:** unknown (no public pricing recorded — not fabricated)
- ⚠️ **Judge/spine disagreements:** 1 (surfaced, not hidden)

## Signature quirks
_Behavioural tics, each anchored to a count from the runs._

- **Sprays options** — listed up to 4 separate fixes in one answer (avg 2.3/answer); offers a menu rather than committing.
- **Decorates** — uses emoji/symbols in every answer.
- **Recovers on a nudge** — flipped wrong→right after the bare "still broken" follow-up on: revenuecat_permonth.

## Task by task

### aspect-ratio crop (CSS layout)
- **cold** — ✅ reached (better). The model answer correctly identifies the aspect-ratio mismatch and recommends changing the container to 9:16, matching the known-correct outcome. It goes further by offering multiple alternative solutions (contain, object-position, padding hack), making it more comprehensive and actionable than…
  > What's Happening: Why the Cover Image is Cropped Top and Bottom
- **guided** — ✅ reached (better). The model answer correctly identifies the aspect-ratio mismatch and recommends setting the container to 9:16, matching the known-correct outcome. It goes further by offering additional context, visual explanations, alternative fixes, debugging tips, and potential pitfalls, making it more…
  > You're seeing top and bottom cropping on the cover image of a photo strip inside a .cover-card, while the photo strips themselves (which are 9:16 aspect ratio) look fine elsewhere.

### iOS WKWebView auto-zoom (mobile-web)
- **cold** — ✅ reached (better). The model answer correctly identifies the root cause (iOS auto-zoom on inputs with font size <16px) and recommends the correct fix (set font-size to 16px or larger), while also explicitly warning against the accessibility-damaging viewport-lock solutions. It goes further than the known-correct…
  > Root Cause of the Zoom Issue on iOS (WKWebView)
- **guided** — ✅ reached (better). The model answer correctly identifies the root cause (iOS auto-zoom on inputs with font-size < 16px) and prioritizes the correct fix (setting font-size >=16px). It goes further by explicitly comparing multiple solutions, highlighting accessibility trade-offs in detail, and warning against the…
  > Root Cause of the Zoom Issue on iOS (WKWebView + Capacitor)

### per-month price bug (payments logic)
- **cold** — ❌ missed (worse). The model answer incorrectly claims the bug is in the `price` field's suffix handling and suggests using `pkg.product.priceString` directly for both `price` and `pricePerMonth`. However, the known-correct outcome states that `pkg.product.priceString` is the full annual price ($79.99/year), not a…
  > Bug Location and Explanation
- **guided** — ✅ reached (better). The model correctly identifies the bug in using priceString for pricePerMonth and provides the known-correct fix of computing the per-month value. It goes further by suggesting the use of RevenueCat's built-in priceStringMonthly field and offering a fallback calculation strategy, making the answer…
  > You're encountering a misleading price display on your React Native paywall when using RevenueCat for subscriptions.

## Failure modes
- **revenuecat_permonth / cold** (worse): The model answer incorrectly claims the bug is in the `price` field's suffix handling and suggests using `pkg.product.priceString` directly for both `price` and `pricePerMonth`. However, the known-correct outcome states that…

## Provenance
- n = 6 cells (3 real mined bugs × cold/guided). Pilot, not powered.
- Outcomes judged by an LLM judge anchored to the objective root cause, floor-tested live before the run (garbage→missed, differently-worded-correct→reached).
- Quirks are computed deterministically from the saved outputs (token counts, regex tallies, cold↔guided flips) — no LLM-as-judge in the quirk layer.
- Trust resets on any model-version change.