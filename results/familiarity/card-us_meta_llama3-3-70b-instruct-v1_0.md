# Model Card — `us.meta.llama3-3-70b-instruct-v1:0`

> **Outcome reached: 4/6** (cold 2/3 · guided 2/3) · confidence **Low** (pilot, n=6) · generated 2026-06-27
> Detailed replay profile. Every quote below is the model's own output, verbatim.

## At a glance
- **Reached the root cause:** 4/6 cells
- **Cold vs guided:** 2/3 unaided · 2/3 after a bare "still broken" follow-up
- **Latency:** 3388 ms median (2703–4904)
- **Answer length:** 450 output tokens median
- **Cost/task:** unknown (no public pricing recorded — not fabricated)
- ⚠️ **Judge/spine disagreements:** 2 (surfaced, not hidden)

## Signature quirks
_Behavioural tics, each anchored to a count from the runs._

- **Commits to one fix** — rarely enumerates alternatives (avg 0.0 option blocks/answer).

## Task by task

### aspect-ratio crop (CSS layout)
- **cold** — ✅ reached (better). The model answer correctly identifies the aspect-ratio mismatch and the effect of object-fit: cover, and provides two valid solutions: changing to object-fit: contain or adjusting the container's aspect-ratio to 9/16. The known-correct outcome only specifies adjusting the aspect ratio, but the…
  > The issue arises from the mismatch between the aspect ratio of the photo strip image (9:16) and the aspect ratio of the cover card (.cover-card) which is set to 3/4.
- **guided** — ✅ reached (worse). The model answer identifies the aspect-ratio mismatch correctly and suggests matching the cover card's aspect ratio to 9:16 as a valid fix, which aligns with the known-correct outcome. However, it also suggests using `object-fit: contain` or a complex padding-based workaround as alternatives, which…
  > The issue arises from the mismatch between the aspect ratio of the photo strip (9:16) and the aspect ratio of the cover card (3/4).

### iOS WKWebView auto-zoom (mobile-web)
- **cold** — ❌ missed (worse). The model answer incorrectly promotes the viewport-lock fix (maximum-scale=1.0, user-scalable=no) as a valid solution, despite the known-correct outcome explicitly stating it is inferior and harms accessibility. While it does mention increasing font size to 16px, it presents the two solutions as…
  > Step-by-step analysis of the problem:
- **guided** — ❌ missed (worse). The model answer incorrectly presents the viewport-lock fix (maximum-scale=1.0, user-scalable=no) as a valid solution, which the known-correct outcome explicitly states is inferior and harms accessibility. While it does mention setting font-size to 16px, it fails to identify that as the root cause…
  > Step-by-step analysis of the problem:

### per-month price bug (payments logic)
- **cold** — ✅ reached (equivalent). The model correctly identifies the bug in assigning the annual price string directly to pricePerMonth and fixes it by computing the monthly price as annual price divided by 12, matching the known-correct outcome in substance and approach.
  > Step-by-step analysis of the problem:
- **guided** — ✅ reached (equivalent). The model correctly identifies that pkg.product.priceString represents the full-period price and should not be used directly for pricePerMonth in annual plans. It fixes the issue by computing the monthly price as annual price divided by 12, matching the known-correct outcome in substance.
  > Step-by-step analysis of the problem:

## Failure modes
- **ios_zoom / cold** (worse): The model answer incorrectly promotes the viewport-lock fix (maximum-scale=1.0, user-scalable=no) as a valid solution, despite the known-correct outcome explicitly stating it is inferior and harms accessibility. While it does mention…
- **ios_zoom / guided** (worse): The model answer incorrectly presents the viewport-lock fix (maximum-scale=1.0, user-scalable=no) as a valid solution, which the known-correct outcome explicitly states is inferior and harms accessibility. While it does mention setting…
- **cover_crop / guided** (worse): The model answer identifies the aspect-ratio mismatch correctly and suggests matching the cover card's aspect ratio to 9:16 as a valid fix, which aligns with the known-correct outcome. However, it also suggests using `object-fit: contain`…

## Provenance
- n = 6 cells (3 real mined bugs × cold/guided). Pilot, not powered.
- Outcomes judged by an LLM judge anchored to the objective root cause, floor-tested live before the run (garbage→missed, differently-worded-correct→reached).
- Quirks are computed deterministically from the saved outputs (token counts, regex tallies, cold↔guided flips) — no LLM-as-judge in the quirk layer.
- Trust resets on any model-version change.