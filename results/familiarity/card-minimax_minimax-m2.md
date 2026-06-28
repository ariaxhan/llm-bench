# Model Card — minimax.minimax-m2

> Confidence: **Low (pilot, n=6 observations across 3 task types)** · generated 2026-06-27
> Replay bootstrap (cold + guided). Every line traces to an observation below.

## At a glance
- **Outcome reached:** 5/6 observations
  - cold: 2/3 · guided: 3/3
- **Divergence mix:** {'better': 5, 'worse': 1}
- **Avg latency:** 42416.4 ms
- **Avg cost/task:** unknown (no public pricing recorded — not fabricated)
- ⚠️ **Judge/spine disagreements:** 1 (surfaced, not hidden — see observations)

## Role signal (tentative — pilot n)
- debugger / implementer (CSS layout)
- debugger / implementer (mobile front-end)
- debugger / reviewer (API + business logic)

## Strengths (reached the outcome)
- **mobile-web debugging (iOS WKWebView)** (ios_zoom) — cold:better, guided:better
- **CSS layout / aspect-ratio debugging** (cover_crop) — cold:better, guided:better
- **payments-logic / API-semantics debugging** (revenuecat_permonth) — cold:worse, guided:better

## Failure modes
- **payments-logic / API-semantics debugging** (revenuecat_permonth, cold): The model incorrectly identifies the bug as being in the `price` field construction due to a wrong `annual` flag, but the known-correct outcome states the bug is in assigning `priceString` directly to `pricePerMonth` without dividing by 12 for annual plans. The model misdiagnoses the root cause and overcomplicates the fix, while the correct fix only requires computing `pricePerMonth` as `price / 12` for annual plans.

## Best pairings
- Insufficient data — pairings need multi-model co-runs (phase 2). Not inferred.

## Provenance
- n = 6 observations (3 real mined tasks x 2 conditions).
- Outcomes judged by an LLM judge anchored to the objective outcome, floor-tested live (garbage -> not-reached; differently-worded-correct -> reached).
- Pilot != powered. Trust resets on model version change.