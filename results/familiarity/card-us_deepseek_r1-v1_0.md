# Model Card — us.deepseek.r1-v1:0

> Confidence: **Low (pilot, n=6 observations across 3 task types)** · generated 2026-06-27
> Replay bootstrap (cold + guided). Every line traces to an observation below.

## At a glance
- **Outcome reached:** 6/6 observations
  - cold: 3/3 · guided: 3/3
- **Divergence mix:** {'better': 5, 'equivalent': 1}
- **Avg latency:** 16714.8 ms
- **Avg cost/task:** $0.014319

## Role signal (tentative — pilot n)
- debugger / implementer (CSS layout)
- debugger / implementer (mobile front-end)
- debugger / reviewer (API + business logic)

## Strengths (reached the outcome)
- **mobile-web debugging (iOS WKWebView)** (ios_zoom) — cold:better, guided:better
- **CSS layout / aspect-ratio debugging** (cover_crop) — cold:equivalent, guided:better
- **payments-logic / API-semantics debugging** (revenuecat_permonth) — cold:better, guided:better

## Failure modes
- none observed in this pilot

## Best pairings
- Insufficient data — pairings need multi-model co-runs (phase 2). Not inferred.

## Provenance
- n = 6 observations (3 real mined tasks x 2 conditions).
- Outcomes judged by an LLM judge anchored to the objective outcome, floor-tested live (garbage -> not-reached; differently-worded-correct -> reached).
- Pilot != powered. Trust resets on model version change.