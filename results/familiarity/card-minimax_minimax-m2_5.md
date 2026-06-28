# Model Card — minimax.minimax-m2.5

> Confidence: **Low (pilot, n=6 observations across 3 task types)** · generated 2026-06-27
> Replay bootstrap (cold + guided). Every line traces to an observation below.

## At a glance
- **Outcome reached:** 4/6 observations
  - cold: 1/3 · guided: 3/3
- **Divergence mix:** {'worse': 2, 'equivalent': 1, 'better': 3}
- **Avg latency:** 51709.3 ms
- **Avg cost/task:** unknown (no public pricing recorded — not fabricated)

## Role signal (tentative — pilot n)
- debugger / implementer (CSS layout)
- debugger / implementer (mobile front-end)
- debugger / reviewer (API + business logic)

## Strengths (reached the outcome)
- **mobile-web debugging (iOS WKWebView)** (ios_zoom) — cold:worse, guided:equivalent
- **CSS layout / aspect-ratio debugging** (cover_crop) — cold:worse, guided:better
- **payments-logic / API-semantics debugging** (revenuecat_permonth) — cold:better, guided:better

## Failure modes
- **mobile-web debugging (iOS WKWebView)** (ios_zoom, cold): model produced no answer text (empty output)
- **CSS layout / aspect-ratio debugging** (cover_crop, cold): model produced no answer text (empty output)

## Best pairings
- Insufficient data — pairings need multi-model co-runs (phase 2). Not inferred.

## Provenance
- n = 6 observations (3 real mined tasks x 2 conditions).
- Outcomes judged by an LLM judge anchored to the objective outcome, floor-tested live (garbage -> not-reached; differently-worded-correct -> reached).
- Pilot != powered. Trust resets on model version change.