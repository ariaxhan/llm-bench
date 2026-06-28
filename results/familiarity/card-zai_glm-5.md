# Model Card — `zai.glm-5`

> **Outcome reached: 5/6** (cold 3/3 · guided 2/3) · confidence **Low** (pilot, n=6) · generated 2026-06-27
> Detailed replay profile. Every quote below is the model's own output, verbatim.

## At a glance
- **Reached the root cause:** 5/6 cells
- **Cold vs guided:** 3/3 unaided · 2/3 after a bare "still broken" follow-up
- **Latency:** 9519 ms median (4198–19388)
- **Answer length:** 404 output tokens median
- **Cost/task:** unknown (no public pricing recorded — not fabricated)
- ⚠️ **Judge/spine disagreements:** 1 (surfaced, not hidden)

## Signature quirks
_Behavioural tics, each anchored to a count from the runs._

- **Terse** — median 404 output tokens/answer, 0.6× the roster median (712).
- **Commits to one fix** — rarely enumerates alternatives (avg 0.7 option blocks/answer).
- **Regresses on a nudge** — flipped right→wrong once pushed on: ios_zoom (the vague follow-up made it worse).

## Task by task

### aspect-ratio crop (CSS layout)
- **cold** — ✅ reached (better). The model answer correctly identifies the aspect-ratio mismatch and explains the effect of `object-fit: cover`, reaching the known-correct outcome. It goes further by offering two valid solutions—using `object-fit: contain` or changing the container's aspect ratio—providing a more complete and…
  > The issue is caused by a conflict between the aspect ratio of the image container and the aspect ratio of the image itself, combined with the CSS property object-fit: cover.
- **guided** — ✅ reached (better). The model answer correctly identifies the aspect-ratio mismatch and provides the correct fix, while also including a clear mathematical comparison of the ratios and a detailed explanation of how object-fit: cover behaves, which enhances clarity and understanding beyond the known-correct outcome.
  > The reason it is still broken is that you are forcing a 9:16 image into a 3:4 box.

### iOS WKWebView auto-zoom (mobile-web)
- **cold** — ✅ reached (better). The model answer correctly identifies the root cause (iOS auto-zoom on inputs with font-size < 16px) and the proper fix (set font-size to >=16px), aligning with the known-correct outcome. It goes further by elaborating on accessibility tradeoffs in both directions—highlighting that the zoom is an…
  > The root cause is iOS WebKit's accessibility heuristic.
- **guided** — ❌ missed (worse). The model answer incorrectly presents the viewport-lock fix (maximum-scale=1.0, user-scalable=no) as a valid fallback, even though the known-correct outcome explicitly states it is inferior and harms accessibility. It also fails to clearly prioritize the font-size fix as the only correct solution,…
  > The root cause is iOS WebKit's accessibility heuristic.

### per-month price bug (payments logic)
- **cold** — ✅ reached (better). The model correctly identifies the bug in assigning the full annual price string to pricePerMonth and provides the correct fix by computing the monthly price as price/12. It improves upon the known-correct outcome by including handling for both annual and monthly cases, addressing currency…
  > The bug is in the pricePerMonth assignment.
- **guided** — ✅ reached (better). The model answer correctly identifies the bug in assigning the full annual priceString to pricePerMonth and provides a fix that computes the monthly value by dividing the numeric price by 12. It improves upon the known-correct outcome by including proper currency formatting using toLocaleString…
  > The bug is in the pricePerMonth assignment.

## Failure modes
- **ios_zoom / guided** (worse): The model answer incorrectly presents the viewport-lock fix (maximum-scale=1.0, user-scalable=no) as a valid fallback, even though the known-correct outcome explicitly states it is inferior and harms accessibility. It also fails to clearly…

## Provenance
- n = 6 cells (3 real mined bugs × cold/guided). Pilot, not powered.
- Outcomes judged by an LLM judge anchored to the objective root cause, floor-tested live before the run (garbage→missed, differently-worded-correct→reached).
- Quirks are computed deterministically from the saved outputs (token counts, regex tallies, cold↔guided flips) — no LLM-as-judge in the quirk layer.
- Trust resets on any model-version change.