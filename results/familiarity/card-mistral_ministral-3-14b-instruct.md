# Model Card — `mistral.ministral-3-14b-instruct`

> **Outcome reached: 2/6** (cold 1/3 · guided 1/3) · confidence **Low** (pilot, n=6) · generated 2026-06-27
> Detailed replay profile. Every quote below is the model's own output, verbatim.

## At a glance
- **Reached the root cause:** 2/6 cells
- **Cold vs guided:** 1/3 unaided · 1/3 after a bare "still broken" follow-up
- **Latency:** 2391 ms median (1648–3470)
- **Answer length:** 542 output tokens median
- **Cost/task:** unknown (no public pricing recorded — not fabricated)
- ⚠️ **Judge/spine disagreements:** 3 (surfaced, not hidden)

## Signature quirks
_Behavioural tics, each anchored to a count from the runs._

- **Sprays options** — listed up to 6 separate fixes in one answer (avg 1.0/answer); offers a menu rather than committing.

## Task by task

### aspect-ratio crop (CSS layout)
- **cold** — ✅ reached (better). The model answer correctly identifies the aspect ratio mismatch and the effect of object-fit: cover, then provides multiple valid solutions including the exact fix from the known-correct outcome (matching aspect ratios). It goes further by offering additional options and context, making it more…
  > The cropping issue you're seeing is due to a mismatch between the aspect ratio of the cover card and the aspect ratio of the photo strip image, combined with how object-fit: cover behaves.
- **guided** — ✅ reached (worse). The model eventually identifies the correct fix—changing the aspect ratio to 9/16—but initially confuses the aspect ratio direction multiple times, incorrectly suggesting 16/9 and providing misleading explanations about container dimensions. This creates confusion and reduces clarity, despite…
  > This is a classic aspect ratio mismatch issue between the container and the image.

### iOS WKWebView auto-zoom (mobile-web)
- **cold** — ❌ missed (worse). The model answer incorrectly recommends using `maximum-scale=1.0` and `user-scalable=no` as part of the primary solution, which contradicts the known-correct outcome that identifies this as an inferior fix that harms accessibility. While it does suggest setting the font size to 16px, it undermines…
  > iOS WKWebView Zoom Issue Analysis
- **guided** — ❌ missed (worse). The model answer incorrectly identifies the root cause and recommends disabling user scaling and using text-size-adjust, which contradicts the known-correct outcome that the issue is due to font size <16px triggering iOS auto-zoom. The correct fix is increasing font-size to >=16px, but the model…
  > iOS WKWebView Zoom Issue Fix

### per-month price bug (payments logic)
- **cold** — ❌ missed (worse). The model incorrectly assumes the issue is duplicate period suffixes (e.g., '/yr/yr') and that priceString already includes the correct period, but the known-correct outcome states that priceString is the full-period price without per-month conversion. The model preserves the incorrect assignment…
  > The bug is in how you're constructing the price string in your revenueCat.ts file.
- **guided** — ❌ missed (worse). The model answer incorrectly suggests using `pricePerMonth` from RevenueCat for the `price` field in annual plans, but the known-correct outcome states that `pkg.product.priceString` is the full-period price and `pricePerMonth` should be computed as `price / 12`. The model assumes RevenueCat…
  > The bug is in how you're constructing the price string in your revenueCat.ts file.

## Failure modes
- **ios_zoom / cold** (worse): The model answer incorrectly recommends using `maximum-scale=1.0` and `user-scalable=no` as part of the primary solution, which contradicts the known-correct outcome that identifies this as an inferior fix that harms accessibility. While…
- **ios_zoom / guided** (worse): The model answer incorrectly identifies the root cause and recommends disabling user scaling and using text-size-adjust, which contradicts the known-correct outcome that the issue is due to font size <16px triggering iOS auto-zoom. The…
- **cover_crop / guided** (worse): The model eventually identifies the correct fix—changing the aspect ratio to 9/16—but initially confuses the aspect ratio direction multiple times, incorrectly suggesting 16/9 and providing misleading explanations about container…
- **revenuecat_permonth / cold** (worse): The model incorrectly assumes the issue is duplicate period suffixes (e.g., '/yr/yr') and that priceString already includes the correct period, but the known-correct outcome states that priceString is the full-period price without…
- **revenuecat_permonth / guided** (worse): The model answer incorrectly suggests using `pricePerMonth` from RevenueCat for the `price` field in annual plans, but the known-correct outcome states that `pkg.product.priceString` is the full-period price and `pricePerMonth` should be…

## Provenance
- n = 6 cells (3 real mined bugs × cold/guided). Pilot, not powered.
- Outcomes judged by an LLM judge anchored to the objective root cause, floor-tested live before the run (garbage→missed, differently-worded-correct→reached).
- Quirks are computed deterministically from the saved outputs (token counts, regex tallies, cold↔guided flips) — no LLM-as-judge in the quirk layer.
- Trust resets on any model-version change.