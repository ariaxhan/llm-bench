# Model Card — `us.deepseek.r1-v1:0`

> **Outcome reached: 6/6** (cold 3/3 · guided 3/3) · confidence **Low** (pilot, n=6) · generated 2026-06-27
> Detailed replay profile. Every quote below is the model's own output, verbatim.

## At a glance
- **Reached the root cause:** 6/6 cells
- **Cold vs guided:** 3/3 unaided · 3/3 after a bare "still broken" follow-up
- **Latency:** 15290 ms median (7757–27607)
- **Answer length:** 2580 output tokens median
- **Cost/task:** $0.015325 avg

## Signature quirks
_Behavioural tics, each anchored to a count from the runs._

- **Verbose** — median 2580 output tokens/answer, 3.6× the roster median (712).
- **Thinks out loud (hidden)** — emits a reasoning block on 6/6 cells, avg 10473 chars of scratchpad the judge never sees.
- **Commits to one fix** — rarely enumerates alternatives (avg 0.0 option blocks/answer).

## Task by task

### aspect-ratio crop (CSS layout)
- **cold** — ✅ reached (better). The model answer correctly identifies the aspect-ratio mismatch and provides the exact fix of setting the container to 9/16. It also improves upon the known-correct outcome by offering alternative solutions (changing image aspect ratio or using object-fit: contain) in case the container dimensions…
  > The issue arises because the container's aspect ratio (3:4 = 0.75) doesn't match the image's (9:16 ≈ 0.5625).
- **guided** — ✅ reached (better). The model answer correctly identifies the aspect-ratio mismatch and provides the exact fix by changing the container to 9/16. It goes further by explaining why the fix works and adding troubleshooting steps for potential follow-up issues, making it more complete and helpful than the known-correct…
  > The issue arises because the container's aspect ratio (3:4 = 0.75) doesn't match the image's (9:16 = 0.5625).

### iOS WKWebView auto-zoom (mobile-web)
- **cold** — ✅ reached (better). The model answer correctly identifies the root cause (iOS auto-zoom on inputs with font size <16px) and provides the correct fix (set font-size to >=16px). It improves upon the known-correct outcome by explicitly warning against the viewport-lock alternative and clearly articulating the…
  > The root cause is iOS automatically zooming into inputs with font sizes smaller than 16px to improve readability.
- **guided** — ✅ reached (better). The model answer correctly identifies the root cause (iOS auto-zoom on inputs with font size <16px) and prescribes the correct fix (set font-size to 16px). It improves upon the known-correct outcome by additionally recommending 'text-size-adjust: 100%' to prevent iOS font scaling, which is a best…
  > iOS automatically zooms into form inputs with font sizes smaller than 16px to improve readability.

### per-month price bug (payments logic)
- **cold** — ✅ reached (better). The model answer correctly identifies the bug and provides a fix that computes the per-month price by dividing the annual price by 12. It improves upon the known-correct outcome by including proper formatting with `/mo` and handling both annual and monthly cases explicitly, making the solution more…
  > The bug occurs because the pricePerMonth is incorrectly using the annual package's priceString (e.g., "$79.99") instead of calculating the monthly equivalent.
- **guided** — ✅ reached (better). The model answer correctly identifies the core bug in pricePerMonth assignment and provides a fix that computes the monthly value by dividing the annual price by 12, matching the known-correct outcome. It goes further by suggesting a robust formatting solution using Intl.NumberFormat and tying the…
  > The issue arises from two problems in the code:

## Failure modes
- None — reached every cell in this pilot.

## Provenance
- n = 6 cells (3 real mined bugs × cold/guided). Pilot, not powered.
- Outcomes judged by an LLM judge anchored to the objective root cause, floor-tested live before the run (garbage→missed, differently-worded-correct→reached).
- Quirks are computed deterministically from the saved outputs (token counts, regex tallies, cold↔guided flips) — no LLM-as-judge in the quirk layer.
- Trust resets on any model-version change.