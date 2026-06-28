# Model Card — mistral.devstral-2-123b

> Confidence: **Low (pilot, n=6 observations across 3 task types)** · generated 2026-06-27
> Replay bootstrap (cold + guided). Every line traces to an observation below.

## At a glance
- **Outcome reached:** 5/6 observations
  - cold: 2/3 · guided: 3/3
- **Divergence mix:** {'worse': 1, 'better': 5}
- **Avg latency:** 5997.0 ms
- **Avg cost/task:** unknown (no public pricing recorded — not fabricated)
- ⚠️ **Judge/spine disagreements:** 1 (surfaced, not hidden — see observations)

## Role signal (tentative — pilot n)
- debugger / implementer (CSS layout)
- debugger / implementer (mobile front-end)
- debugger / reviewer (API + business logic)

## Strengths (reached the outcome)
- **mobile-web debugging (iOS WKWebView)** (ios_zoom) — cold:worse, guided:better
- **CSS layout / aspect-ratio debugging** (cover_crop) — cold:better, guided:better
- **payments-logic / API-semantics debugging** (revenuecat_permonth) — cold:better, guided:better

## Failure modes
- **mobile-web debugging (iOS WKWebView)** (ios_zoom, cold): The model incorrectly identifies multiple 'solutions' and recommends combining maximum-scale with font size increase, while the known-correct outcome states that viewport locks (like maximum-scale) are inferior and harm accessibility. The model fails to recognize that setting font-size >=16px alone is the correct fix, and instead presents disabling zoom as an acceptable practice, which contradicts the accessibility guidance in the known outcome.

## Best pairings
- Insufficient data — pairings need multi-model co-runs (phase 2). Not inferred.

## Provenance
- n = 6 observations (3 real mined tasks x 2 conditions).
- Outcomes judged by an LLM judge anchored to the objective outcome, floor-tested live (garbage -> not-reached; differently-worded-correct -> reached).
- Pilot != powered. Trust resets on model version change.