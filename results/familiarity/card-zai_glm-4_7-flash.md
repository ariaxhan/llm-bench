# Model Card — zai.glm-4.7-flash

> Confidence: **Low (pilot, n=6 observations across 3 task types)** · generated 2026-06-27
> Replay bootstrap (cold + guided). Every line traces to an observation below.

## At a glance
- **Outcome reached:** 2/6 observations
  - cold: 2/3 · guided: 0/3
- **Divergence mix:** {'worse': 4, 'better': 1, 'equivalent': 1}
- **Avg latency:** 1888.5 ms
- **Avg cost/task:** unknown (no public pricing recorded — not fabricated)
- ⚠️ **Judge/spine disagreements:** 3 (surfaced, not hidden — see observations)

## Role signal (tentative — pilot n)
- debugger / implementer (CSS layout)
- debugger / reviewer (API + business logic)

## Strengths (reached the outcome)
- **CSS layout / aspect-ratio debugging** (cover_crop) — cold:better, guided:worse
- **payments-logic / API-semantics debugging** (revenuecat_permonth) — cold:equivalent, guided:worse

## Failure modes
- **mobile-web debugging (iOS WKWebView)** (ios_zoom, cold): The model misidentifies the root cause as a 'font-size mismatch' and a viewport scaling calculation based on 375px width, which is incorrect. The actual cause is iOS Safari/WKWebView's behavior of auto-zooming on inputs with font-size below 16px, regardless of viewport width math. The model's fix of setting html/body to 16px may work but is based on flawed reasoning, and it fails to explicitly identify the 16px threshold rule or reject the inferior viewport-lock fix as harmful to accessibility.
- **mobile-web debugging (iOS WKWebView)** (ios_zoom, guided): The model answer incorrectly identifies the viewport meta tag as the root cause and recommends adding `user-scalable=no`, which is explicitly stated in the known-correct outcome as an inferior fix that harms accessibility. The correct root cause is the input's font size being below 16px, requiring a font-size fix, not disabling user scaling.
- **CSS layout / aspect-ratio debugging** (cover_crop, guided): The model incorrectly states that the 9:16 image is 'narrower' and 'taller' than the 3:4 container and claims cropping occurs on the sides, when in fact 9:16 is taller (more vertical) than 3:4, causing top/bottom cropping under object-fit: cover. The fix of changing aspect-ratio to 9/16 is correct, but the explanation misrepresents the aspect ratio comparison, contradicting the known-correct outcome.
- **payments-logic / API-semantics debugging** (revenuecat_permonth, guided): The model answer incorrectly suggests setting `pricePerMonth` to a string expression `${pkg.product.priceString} / 12`, which would result in a literal string like '79.99 / 12' instead of the computed value. The correct fix requires dividing the numeric price by 12 and formatting it properly, not concatenating a string with '/ 12'. This fails to reach the known-correct outcome of computing $6.67/mo from $79.99/yr.

## Best pairings
- Insufficient data — pairings need multi-model co-runs (phase 2). Not inferred.

## Provenance
- n = 6 observations (3 real mined tasks x 2 conditions).
- Outcomes judged by an LLM judge anchored to the objective outcome, floor-tested live (garbage -> not-reached; differently-worded-correct -> reached).
- Pilot != powered. Trust resets on model version change.