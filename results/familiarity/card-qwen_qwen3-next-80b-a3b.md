# Model Card — `qwen.qwen3-next-80b-a3b`

> **Outcome reached: 5/6** (cold 3/3 · guided 2/3) · confidence **Low** (pilot, n=6) · generated 2026-06-27
> Detailed replay profile. Every quote below is the model's own output, verbatim.

## At a glance
- **Reached the root cause:** 5/6 cells
- **Cold vs guided:** 3/3 unaided · 2/3 after a bare "still broken" follow-up
- **Latency:** 11373 ms median (8176–13096)
- **Answer length:** 927 output tokens median
- **Cost/task:** unknown (no public pricing recorded — not fabricated)
- ⚠️ **Judge/spine disagreements:** 1 (surfaced, not hidden)

## Signature quirks
_Behavioural tics, each anchored to a count from the runs._

- **Commits to one fix** — rarely enumerates alternatives (avg 0.0 option blocks/answer).
- **Decorates** — uses emoji/symbols in every answer.
- **Regresses on a nudge** — flipped right→wrong once pushed on: cover_crop (the vague follow-up made it worse).

## Task by task

### aspect-ratio crop (CSS layout)
- **cold** — ✅ reached (better). The model answer correctly identifies the aspect-ratio mismatch and explains the cropping due to object-fit: cover, but goes further by offering two valid solutions—using object-fit: contain or changing the container's aspect-ratio to 9:16—whereas the known-correct outcome only mentions the latter.…
  > This is a classic aspect ratio mismatch issue caused by object-fit: cover.
- **guided** — ❌ missed (worse). The model answer incorrectly concludes that using `object-fit: contain` with `height: 100%` and `width: auto` is the fix, which would show the full image but introduce side letterboxing. The known-correct outcome identifies the actual issue as an aspect-ratio mismatch and correctly states that the…
  > You're seeing the top and bottom cropped because the aspect ratio of the container (3:4) does not match the aspect ratio of the image (9:16), and object-fit: cover forces the image to fill the container while preserving its aspect ratio — which means it…

### iOS WKWebView auto-zoom (mobile-web)
- **cold** — ✅ reached (better). The model answer correctly identifies the root cause (font size < 16px triggering iOS auto-zoom) and the correct fix (setting font-size >=16px), as in the known-correct outcome. It goes further by offering a detailed, accessibility-preserving solution using `transform: scale()` and explains why…
  > The root cause of the unwanted zoom on iOS WKWebView is iOS Safari’s automatic text-input zoom behavior, which is triggered when a <input> or <textarea> element has a computed font size below 16px.
- **guided** — ✅ reached (better). The model answer correctly identifies the root cause (iOS auto-zoom on inputs with font <16px) and prescribes the correct fix (set font-size to 16px or more), matching the known-correct outcome. It goes further by offering a bonus workaround with `transform: scale()`, discussing its tradeoffs, and…
  > You're dealing with iOS WKWebView’s automatic zoom-on-focus behavior — a well-known, frustrating quirk that happens even with correct viewport settings.

### per-month price bug (payments logic)
- **cold** — ✅ reached (better). The model correctly identifies the bug in reusing priceString for pricePerMonth and provides the fix by computing the monthly equivalent via price/12. It goes further by suggesting improved formatting with toFixed(2), using the numeric price field for calculations, and offering enhanced solutions…
  > You're using pkg.product.priceString for both the price and pricePerMonth fields — but they mean different things:
- **guided** — ✅ reached (better). The model answer correctly identifies the bug — misusing `priceString` as a per-month value when it represents the total period price — and prescribes the fix of computing per-month price from `pkg.product.price / 12` for annual plans. It goes further than the known-correct outcome by providing…
  > You're encountering a critical misunderstanding of how RevenueCat returns pricing data — and your current code is misinterpreting what pkg.product.priceString actually represents.

## Failure modes
- **cover_crop / guided** (worse): The model answer incorrectly concludes that using `object-fit: contain` with `height: 100%` and `width: auto` is the fix, which would show the full image but introduce side letterboxing. The known-correct outcome identifies the actual…

## Provenance
- n = 6 cells (3 real mined bugs × cold/guided). Pilot, not powered.
- Outcomes judged by an LLM judge anchored to the objective root cause, floor-tested live before the run (garbage→missed, differently-worded-correct→reached).
- Quirks are computed deterministically from the saved outputs (token counts, regex tallies, cold↔guided flips) — no LLM-as-judge in the quirk layer.
- Trust resets on any model-version change.