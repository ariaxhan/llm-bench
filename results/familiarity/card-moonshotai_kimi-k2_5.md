# Model Card — `moonshotai.kimi-k2.5`

> **Outcome reached: 6/6** (cold 3/3 · guided 3/3) · confidence **Low** (pilot, n=6) · generated 2026-06-27
> Detailed replay profile. Every quote below is the model's own output, verbatim.

## At a glance
- **Reached the root cause:** 6/6 cells
- **Cold vs guided:** 3/3 unaided · 3/3 after a bare "still broken" follow-up
- **Latency:** 3229 ms median (2664–6187)
- **Answer length:** 410 output tokens median
- **Cost/task:** unknown (no public pricing recorded — not fabricated)

## Signature quirks
_Behavioural tics, each anchored to a count from the runs._

- **Terse** — median 410 output tokens/answer, 0.6× the roster median (712).
- **Commits to one fix** — rarely enumerates alternatives (avg 0.3 option blocks/answer).

## Task by task

### aspect-ratio crop (CSS layout)
- **cold** — ✅ reached (better). The model correctly identifies the aspect-ratio mismatch and the effect of `object-fit: cover`, aligning with the known-correct outcome. It goes further by offering multiple valid solutions (contain, matching aspect ratio, object-position) and recommending the most user-appropriate fix, providing a…
  > The cropping happens because of conflicting aspect ratios:
- **guided** — ✅ reached (better). The model correctly identifies the aspect-ratio mismatch and the cropping due to object-fit: cover, and provides the correct fix of aligning the container's aspect-ratio to 9:16. It goes further by offering additional valid alternatives (contain, height:auto) and contextual trade-offs, making the…
  > I see the issue. Let me analyze:

### iOS WKWebView auto-zoom (mobile-web)
- **cold** — ✅ reached (better). The model answer correctly identifies the root cause (iOS auto-zoom on sub-16px font inputs) and the proper fix (ensuring font-size >=16px), while also explicitly calling out the accessibility tradeoff of viewport-based solutions. It goes further than the known-correct outcome by offering a…
  > iOS WKWebView auto-zooms when focusing input fields with font-size < 16px
- **guided** — ✅ reached (better). The model answer correctly identifies the root cause (font-size < 16px triggering iOS zoom) and prescribes the correct fix (set font-size to 16px), while also acknowledging the accessibility tradeoff. It goes further by offering mitigation strategies (transform scaling), checking viewport settings,…
  > iOS Safari/WKWebView auto-zooms when focusing any input with font-size < 16px.

### per-month price bug (payments logic)
- **cold** — ✅ reached (better). The model answer correctly identifies that the bug is using the full annual priceString for pricePerMonth and provides a fix that computes the monthly price by dividing the annual price by 12. It goes further than the known-correct outcome by offering two clear, well-typed code solutions and…
  > Looking at this code, I can spot the bug immediately.
- **guided** — ✅ reached (better). The model correctly identifies that priceString represents the full annual price and must not be reused for monthly display. It provides a precise fix by computing the monthly equivalent via division by 12, matching the known-correct outcome. Additionally, it offers two clear implementation options…
  > Looking at your code, I can see the bug.

## Failure modes
- None — reached every cell in this pilot.

## Provenance
- n = 6 cells (3 real mined bugs × cold/guided). Pilot, not powered.
- Outcomes judged by an LLM judge anchored to the objective root cause, floor-tested live before the run (garbage→missed, differently-worded-correct→reached).
- Quirks are computed deterministically from the saved outputs (token counts, regex tallies, cold↔guided flips) — no LLM-as-judge in the quirk layer.
- Trust resets on any model-version change.