# Model Card — `us.writer.palmyra-x5-v1:0`

> **Outcome reached: 1/1** (cold 1/1 · guided 0/0) · confidence **Low** (pilot, n=1) · generated 2026-06-27
> Detailed replay profile. Every quote below is the model's own output, verbatim.

## At a glance
- **Reached the root cause:** 1/1 cells
- **Cold vs guided:** 1/1 unaided · 0/0 after a bare "still broken" follow-up
- **Latency:** 3307 ms median (3307–3307)
- **Answer length:** 266 output tokens median
- **Cost/task:** unknown (no public pricing recorded — not fabricated)

## Signature quirks
_Behavioural tics, each anchored to a count from the runs._

- **Terse** — median 266 output tokens/answer, 0.4× the roster median (712).
- **Commits to one fix** — rarely enumerates alternatives (avg 0.0 option blocks/answer).

## Task by task

### iOS WKWebView auto-zoom (mobile-web)
- **cold** — ✅ reached (better). The model answer correctly identifies the root cause (iOS auto-zoom on <16px font) and the proper fix (set font-size >=16px), while also acknowledging the inferiority of viewport locking and its accessibility impact. It goes further by suggesting a visual workaround using transform and explicitly…
  > The root cause is iOS Safari’s (and thus WKWebView’s) automatic text zoom on focus when an input field has a font size smaller than 16px.
- **guided:** _no data (cell errored)_

## Failure modes
- None — reached every cell in this pilot.

## Provenance
- n = 1 cells (3 real mined bugs × cold/guided). Pilot, not powered.
- Outcomes judged by an LLM judge anchored to the objective root cause, floor-tested live before the run (garbage→missed, differently-worded-correct→reached).
- Quirks are computed deterministically from the saved outputs (token counts, regex tallies, cold↔guided flips) — no LLM-as-judge in the quirk layer.
- Trust resets on any model-version change.