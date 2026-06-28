# Model Card — `google.gemma-3-12b-it`

> **Outcome reached: 2/6** (cold 1/3 · guided 1/3) · confidence **Low** (pilot, n=6) · generated 2026-06-27
> Detailed replay profile. Every quote below is the model's own output, verbatim.

## At a glance
- **Reached the root cause:** 2/6 cells
- **Cold vs guided:** 1/3 unaided · 1/3 after a bare "still broken" follow-up
- **Latency:** 11079 ms median (10467–13457)
- **Answer length:** 1296 output tokens median
- **Cost/task:** unknown (no public pricing recorded — not fabricated)
- ⚠️ **Judge/spine disagreements:** 2 (surfaced, not hidden)

## Signature quirks
_Behavioural tics, each anchored to a count from the runs._

- **Verbose** — median 1296 output tokens/answer, 1.8× the roster median (712).
- **Sprays options** — listed up to 4 separate fixes in one answer (avg 1.2/answer); offers a menu rather than committing.
- **Hedges** — avg 6.7 hedge words/answer (might/could/possibly/depends).

## Task by task

### aspect-ratio crop (CSS layout)
- **cold** — ✅ reached (better). The model answer correctly identifies the aspect-ratio mismatch and the role of `object-fit: cover` in causing the cropping, matching the known-correct outcome. It goes further by offering multiple well-explained solutions, including fallbacks and debugging tips, making it more comprehensive and…
  > Okay, this is a classic CSS aspect ratio and object-fit problem.
- **guided** — ✅ reached (better). The model answer correctly identifies the aspect-ratio mismatch and prescribes the correct fix—changing the cover card's aspect-ratio to 9/16. It goes further by proactively addressing potential reasons the fix might still fail (e.g., CSS specificity, caching, JavaScript interference), offering…
  > Okay, this is a classic CSS aspect ratio problem.

### iOS WKWebView auto-zoom (mobile-web)
- **cold** — ❌ missed (worse). The model answer incorrectly identifies the root cause as a general WKWebView zoom behavior without pinpointing the specific iOS rule that triggers zoom on inputs with font-size < 16px. It then recommends suboptimal fixes like CSS transform or JavaScript zoom manipulation, while the correct…
  > Okay, this is a classic and frustrating issue with WKWebView and iOS, especially when dealing with hand-rolled DOM and input fields.
- **guided** — ❌ missed (worse). The model incorrectly identifies the root cause as WKWebView's general focus behavior rather than the specific iOS rule that inputs with font-size below 16px trigger auto-zoom. It recommends setting viewport maximum-scale=1.0 as the most reliable fix, which contradicts the known-correct outcome…
  > Okay, this is a classic and frustrating WKWebView/iOS zoom issue.

### per-month price bug (payments logic)
- **cold** — ❌ missed (worse). The model misidentifies the bug as an issue with RevenueCat's `priceString` including '/mo' and suggests parsing a raw `price` field and using a `period` enum, but the known-correct outcome states the real bug is using `priceString` directly for `pricePerMonth` without dividing the annual price by…
  > Okay, this is a common and frustrating issue with RevenueCat and how it handles price strings.
- **guided** — ❌ missed (worse). The model misidentifies the bug as a string formatting issue and proposes parsing the priceString, when the actual bug is using the full annual priceString directly for pricePerMonth. The known-correct outcome requires computing pricePerMonth as price / 12, but the model incorrectly retains…
  > Okay, let's break down this RevenueCat bug and how to fix it.

## Failure modes
- **ios_zoom / cold** (worse): The model answer incorrectly identifies the root cause as a general WKWebView zoom behavior without pinpointing the specific iOS rule that triggers zoom on inputs with font-size < 16px. It then recommends suboptimal fixes like CSS…
- **ios_zoom / guided** (worse): The model incorrectly identifies the root cause as WKWebView's general focus behavior rather than the specific iOS rule that inputs with font-size below 16px trigger auto-zoom. It recommends setting viewport maximum-scale=1.0 as the most…
- **revenuecat_permonth / cold** (worse): The model misidentifies the bug as an issue with RevenueCat's `priceString` including '/mo' and suggests parsing a raw `price` field and using a `period` enum, but the known-correct outcome states the real bug is using `priceString`…
- **revenuecat_permonth / guided** (worse): The model misidentifies the bug as a string formatting issue and proposes parsing the priceString, when the actual bug is using the full annual priceString directly for pricePerMonth. The known-correct outcome requires computing…

## Provenance
- n = 6 cells (3 real mined bugs × cold/guided). Pilot, not powered.
- Outcomes judged by an LLM judge anchored to the objective root cause, floor-tested live before the run (garbage→missed, differently-worded-correct→reached).
- Quirks are computed deterministically from the saved outputs (token counts, regex tallies, cold↔guided flips) — no LLM-as-judge in the quirk layer.
- Trust resets on any model-version change.