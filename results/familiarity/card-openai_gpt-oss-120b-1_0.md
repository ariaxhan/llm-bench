# Model Card — `openai.gpt-oss-120b-1:0`

> **Outcome reached: 6/6** (cold 3/3 · guided 3/3) · confidence **Low** (pilot, n=6) · generated 2026-06-27
> Detailed replay profile. Every quote below is the model's own output, verbatim.

## At a glance
- **Reached the root cause:** 6/6 cells
- **Cold vs guided:** 3/3 unaided · 3/3 after a bare "still broken" follow-up
- **Latency:** 17942 ms median (8392–25675)
- **Answer length:** 2080 output tokens median
- **Cost/task:** unknown (no public pricing recorded — not fabricated)

## Signature quirks
_Behavioural tics, each anchored to a count from the runs._

- **Verbose** — median 2080 output tokens/answer, 2.9× the roster median (712).
- **Thinks out loud (hidden)** — emits a reasoning block on 6/6 cells, avg 2027 chars of scratchpad the judge never sees.
- **Sprays options** — listed up to 11 separate fixes in one answer (avg 3.7/answer); offers a menu rather than committing.

## Task by task

### aspect-ratio crop (CSS layout)
- **cold** — ✅ reached (better). The model answer correctly identifies the aspect-ratio mismatch and the role of object-fit: cover in causing the cropping, aligning with the known-correct outcome. It goes further by offering multiple valid solutions (matching aspect-ratio, using contain, adjusting object-position, background-image…
  > The strip is being cropped because the container (.cover‑card) has a different aspect‑ratio (3 : 4) than the image (9 : 16) and the CSS object‑fit: cover tells the browser to fill the container, discarding any overflow.
- **guided** — ✅ reached (better). The model answer correctly identifies the aspect-ratio mismatch and the effect of `object-fit: cover`, and provides the correct fix of aligning the container's aspect-ratio to 9:16. It goes further by offering additional context, alternatives (like `contain`), implementation details, and debugging…
  > The strip is being cropped because the container (.cover‑card) has a different aspect‑ratio (3 : 4) than the image it holds (9 : 16).

### iOS WKWebView auto-zoom (mobile-web)
- **cold** — ✅ reached (better). The model answer correctly identifies the root cause (iOS auto-zoom on inputs with font-size < 16px) and recommends the correct fix (set font-size ≥16px), while also thoroughly evaluating alternatives and their accessibility trade-offs. It goes beyond the known-correct outcome by providing a…
  > iOS (Safari + WKWebView) has a built‑in “focus‑zoom” rule: when an <input>, <textarea> or any other editable element receives focus and its computed font‑size is smaller than 16 px, the browser automatically zooms the page until the text is rendered at…
- **guided** — ✅ reached (better). The model answer correctly identifies the root cause (iOS auto-zoom on inputs with font-size < 16px) and the correct fix (set font-size ≥16px), matching the known-correct outcome. It goes further by offering a visual workaround using `transform: scale()` to maintain design aesthetics, explicitly…
  > Why it happens: iOS (Safari / WKWebView) automatically zooms the page when an <input> (or <textarea>) receives focus and its computed font‑size is < 16 px.

### per-month price bug (payments logic)
- **cold** — ✅ reached (better). The model answer correctly identifies the bug in reusing priceString for pricePerMonth and provides a comprehensive fix using RevenueCat's built-in pricePerMonthString, while also offering a fallback calculation strategy if that field isn't available. It goes beyond the known-correct outcome by…
  > pkg.product.priceString is the price of the whole subscription period (e.g.
- **guided** — ✅ reached (better). The model answer correctly identifies the bug in the data-mapping layer and provides the exact fix by using RevenueCat's `pricePerMonthString` or computing the monthly value from the annual price. It goes further than the known-correct outcome by offering two robust implementation strategies, unit…
  > The bug is not in the UI, it is in the data‑mapping layer.

## Failure modes
- None — reached every cell in this pilot.

## Provenance
- n = 6 cells (3 real mined bugs × cold/guided). Pilot, not powered.
- Outcomes judged by an LLM judge anchored to the objective root cause, floor-tested live before the run (garbage→missed, differently-worded-correct→reached).
- Quirks are computed deterministically from the saved outputs (token counts, regex tallies, cold↔guided flips) — no LLM-as-judge in the quirk layer.
- Trust resets on any model-version change.