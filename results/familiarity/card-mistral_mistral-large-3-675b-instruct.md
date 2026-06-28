# Model Card — `mistral.mistral-large-3-675b-instruct`

> **Outcome reached: 5/6** (cold 3/3 · guided 2/3) · confidence **Low** (pilot, n=6) · generated 2026-06-27
> Detailed replay profile. Every quote below is the model's own output, verbatim.

## At a glance
- **Reached the root cause:** 5/6 cells
- **Cold vs guided:** 3/3 unaided · 2/3 after a bare "still broken" follow-up
- **Latency:** 2948 ms median (2432–3682)
- **Answer length:** 586 output tokens median
- **Cost/task:** unknown (no public pricing recorded — not fabricated)
- ⚠️ **Judge/spine disagreements:** 1 (surfaced, not hidden)

## Signature quirks
_Behavioural tics, each anchored to a count from the runs._

- **Sprays options** — listed up to 6 separate fixes in one answer (avg 1.8/answer); offers a menu rather than committing.
- **Regresses on a nudge** — flipped right→wrong once pushed on: ios_zoom (the vague follow-up made it worse).

## Task by task

### aspect-ratio crop (CSS layout)
- **cold** — ✅ reached (better). The model answer correctly identifies the aspect-ratio mismatch and the effect of `object-fit: cover`, matching the known-correct outcome. It goes further by providing multiple viable solutions with pros and cons, and a clear recommendation, making it more comprehensive and actionable than the…
  > The issue stems from a mismatch between the aspect ratio of the photo strip and the aspect ratio of the .cover-card container, combined with object-fit: cover.
- **guided** — ✅ reached (better). The model correctly identifies the aspect-ratio mismatch and the effect of `object-fit: cover`, but goes further by offering two clear solutions (`contain` and adjusting the container aspect ratio), evaluating trade-offs, and providing debugging tips—making it more complete and actionable than the…
  > The issue stems from a mismatch between the image's aspect ratio and the container's aspect ratio, combined with object-fit: cover.

### iOS WKWebView auto-zoom (mobile-web)
- **cold** — ✅ reached (better). The model answer correctly identifies the root cause (font size <16px triggering iOS zoom) and the proper fix (setting font-size to >=16px), while also explicitly warning against the inferior viewport-lock solution. It goes further by offering a JavaScript workaround and discussing accessibility…
  > This is a common issue with iOS WKWebView (and Safari) when focusing on input fields with small font sizes.
- **guided** — ❌ missed (worse). The model incorrectly recommends adding `minimum-scale=1.0` to prevent zoom, which does not stop iOS from auto-zooming on small font inputs and risks locking zoom if combined with `maximum-scale`. The known-correct outcome states that setting the font-size to >=16px is the proper fix, and that…
  > This is a common iOS WKWebView behavior when tapping an input field with a font size smaller than 16px.

### per-month price bug (payments logic)
- **cold** — ✅ reached (better). The model correctly identifies the bug in reusing priceString for pricePerMonth and provides a fix that computes the monthly value by dividing the annual price by 12. It goes further than the known-correct outcome by offering two implementation options, including formatting considerations and…
  > The bug is in how you're handling the pricePerMonth value in your mapping code.
- **guided** — ✅ reached (better). The model correctly identifies the bug in reusing priceString for pricePerMonth and provides the correct fix by computing the monthly price as annual price divided by 12. It goes further by offering a robust implementation that handles string parsing and suggests a fallback using RevenueCat's…
  > The bug is in how you're handling the pricePerMonth field in your revenueCat.ts mapping.

## Failure modes
- **ios_zoom / guided** (worse): The model incorrectly recommends adding `minimum-scale=1.0` to prevent zoom, which does not stop iOS from auto-zooming on small font inputs and risks locking zoom if combined with `maximum-scale`. The known-correct outcome states that…

## Provenance
- n = 6 cells (3 real mined bugs × cold/guided). Pilot, not powered.
- Outcomes judged by an LLM judge anchored to the objective root cause, floor-tested live before the run (garbage→missed, differently-worded-correct→reached).
- Quirks are computed deterministically from the saved outputs (token counts, regex tallies, cold↔guided flips) — no LLM-as-judge in the quirk layer.
- Trust resets on any model-version change.