# Model Card — `openai.gpt-oss-20b-1:0`

> **Outcome reached: 5/6** (cold 2/3 · guided 3/3) · confidence **Low** (pilot, n=6) · generated 2026-06-27
> Detailed replay profile. Every quote below is the model's own output, verbatim.

## At a glance
- **Reached the root cause:** 5/6 cells
- **Cold vs guided:** 2/3 unaided · 3/3 after a bare "still broken" follow-up
- **Latency:** 4387 ms median (2270–12050)
- **Answer length:** 1399 output tokens median
- **Cost/task:** unknown (no public pricing recorded — not fabricated)
- ⚠️ **Judge/spine disagreements:** 1 (surfaced, not hidden)

## Signature quirks
_Behavioural tics, each anchored to a count from the runs._

- **Verbose** — median 1399 output tokens/answer, 2.0× the roster median (712).
- **Thinks out loud (hidden)** — emits a reasoning block on 6/6 cells, avg 3996 chars of scratchpad the judge never sees.
- **Commits to one fix** — rarely enumerates alternatives (avg 0.8 option blocks/answer).
- **Recovers on a nudge** — flipped wrong→right after the bare "still broken" follow-up on: revenuecat_permonth.

## Task by task

### aspect-ratio crop (CSS layout)
- **cold** — ✅ reached (better). The model answer correctly identifies the aspect-ratio mismatch and the effect of `object-fit: cover`, matching the known-correct outcome. It goes further by offering multiple valid solutions (matching aspect ratio, using `contain`, and background-image approach), providing a more complete and…
  > Why the top‑and‑bottom crop happens
- **guided** — ✅ reached (better). The model answer correctly identifies the aspect-ratio mismatch and the effect of object-fit: cover, matching the known-correct outcome. It goes further by offering two well-explained, practical solutions (matching aspect ratios or using object-fit: contain), including implementation code, use-case…
  > Why the strip is getting cropped

### iOS WKWebView auto-zoom (mobile-web)
- **cold** — ✅ reached (better). The model answer correctly identifies the root cause (iOS auto-zoom on inputs with font size < 16px) and the proper fix (set font size ≥16px), while explicitly warning against the accessibility-damaging viewport-lock workaround. It goes beyond the known-correct outcome by offering two concrete CSS…
  > On iOS Safari (and the WKWebView that ships with Capacitor) the browser will auto‑zoom whenever an <input> (or <textarea>) is focused and its computed font size is less than 16 px.
- **guided** — ✅ reached (better). The model answer correctly identifies the root cause (iOS auto-zoom on inputs with font size < 16px) and recommends the correct fix (set input font-size ≥16px), while also explicitly calling out the accessibility trade-off of disabling zoom via viewport meta. It goes further than the known-correct…
  > On iOS Safari (and the embedded WKWebView that Capacitor uses) the browser will auto‑zoom any form control that has a font size smaller than 16 px.

### per-month price bug (payments logic)
- **cold** — ❌ missed (worse). The model answer incorrectly assumes RevenueCat's product object has a pricePerMonth field that can be used directly, but the known-correct outcome states that the comment in the code is wrong — pkg.product.priceString is the full-period price and there is no indication that pricePerMonth exists in…
  > In the mapping that turns a RevenueCat Package into the data the pay‑wall card uses, the per‑month field is being set to the same value that is used for the main price:
- **guided** — ✅ reached (better). The model answer correctly identifies the bug in reusing priceString for pricePerMonth and provides the known-correct outcome of computing the monthly price from the annual price. It improves upon the expected answer by suggesting the use of RevenueCat's built-in pricePerMonth field and including…
  > In the revenueCat.ts helper you map a RevenueCat Package to the data that the pay‑wall card consumes:

## Failure modes
- **revenuecat_permonth / cold** (worse): The model answer incorrectly assumes RevenueCat's product object has a pricePerMonth field that can be used directly, but the known-correct outcome states that the comment in the code is wrong — pkg.product.priceString is the full-period…

## Provenance
- n = 6 cells (3 real mined bugs × cold/guided). Pilot, not powered.
- Outcomes judged by an LLM judge anchored to the objective root cause, floor-tested live before the run (garbage→missed, differently-worded-correct→reached).
- Quirks are computed deterministically from the saved outputs (token counts, regex tallies, cold↔guided flips) — no LLM-as-judge in the quirk layer.
- Trust resets on any model-version change.