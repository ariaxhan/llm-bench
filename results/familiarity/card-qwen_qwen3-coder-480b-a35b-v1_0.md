# Model Card — `qwen.qwen3-coder-480b-a35b-v1:0`

> **Outcome reached: 6/6** (cold 3/3 · guided 3/3) · confidence **Low** (pilot, n=6) · generated 2026-06-27
> Detailed replay profile. Every quote below is the model's own output, verbatim.

## At a glance
- **Reached the root cause:** 6/6 cells
- **Cold vs guided:** 3/3 unaided · 3/3 after a bare "still broken" follow-up
- **Latency:** 4417 ms median (2196–6207)
- **Answer length:** 326 output tokens median
- **Cost/task:** unknown (no public pricing recorded — not fabricated)

## Signature quirks
_Behavioural tics, each anchored to a count from the runs._

- **Terse** — median 326 output tokens/answer, 0.5× the roster median (712).
- **Commits to one fix** — rarely enumerates alternatives (avg 0.0 option blocks/answer).

## Task by task

### aspect-ratio crop (CSS layout)
- **cold** — ✅ reached (better). The model correctly identifies the aspect ratio mismatch and provides the exact fix of changing the cover card to 9/16. It additionally offers a valid alternative solution using `object-fit: contain`, which is a meaningful improvement by addressing a potential design constraint not in the original…
  > The issue is an aspect ratio mismatch between the photo strip (9:16) and the cover card (3:4).
- **guided** — ✅ reached (worse). The model correctly identifies the aspect-ratio mismatch and suggests fixing the container to 9/16, which aligns with the known-correct outcome. However, it unnecessarily changes object-fit to 'contain', which would prevent cropping but may introduce letterboxing; 'cover' would work fine with…
  > The issue is that your CSS is forcing the image to fit a 3:4 aspect ratio container using object-fit: cover, which crops the 9:16 image to fill the space.

### iOS WKWebView auto-zoom (mobile-web)
- **cold** — ✅ reached (better). The model answer correctly identifies the root cause (iOS zooming on inputs with font size <16px) and prescribes the correct fix (set font-size to >=16px). It goes further than the known-correct outcome by elaborating on accessibility tradeoffs and offering nuanced alternatives, including…
  > The zoom occurs because iOS Safari automatically zooms into form fields when their font size is less than 16px.
- **guided** — ✅ reached (better). The model answer correctly identifies the root cause (iOS auto-zoom on inputs with font size <16px due to accessibility) and provides the correct fix (set font-size to >=16px). It goes further than the known-correct outcome by explicitly warning against the inferior viewport-lock workaround and…
  > The issue is that iOS Safari automatically zooms into input fields when their font size is less than 16px.

### per-month price bug (payments logic)
- **cold** — ✅ reached (better). The model correctly identifies that pkg.product.priceString is the total period price, not per-month, and that the comment is wrong. It provides a precise fix by calculating per-month price as total price divided by 12 for annual plans, matching the known-correct outcome. Additionally, it offers a…
  > The problem: pkg.product.priceString always contains the total price for the entire subscription period, not the per-month price.
- **guided** — ✅ reached (better). The model correctly identifies that pkg.product.priceString represents the total period price and should not be used directly for pricePerMonth. It provides a fix that computes the monthly price by dividing the annual price by 12, matching the known-correct outcome. Additionally, it offers a more…
  > Looking at your code, the bug is that you're using pkg.product.priceString directly for both the total price and the per-month calculation.

## Failure modes
- **cover_crop / guided** (worse): The model correctly identifies the aspect-ratio mismatch and suggests fixing the container to 9/16, which aligns with the known-correct outcome. However, it unnecessarily changes object-fit to 'contain', which would prevent cropping but…

## Provenance
- n = 6 cells (3 real mined bugs × cold/guided). Pilot, not powered.
- Outcomes judged by an LLM judge anchored to the objective root cause, floor-tested live before the run (garbage→missed, differently-worded-correct→reached).
- Quirks are computed deterministically from the saved outputs (token counts, regex tallies, cold↔guided flips) — no LLM-as-judge in the quirk layer.
- Trust resets on any model-version change.