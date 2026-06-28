# Model Card — nvidia.nemotron-nano-12b-v2

> Confidence: **Low (pilot, n=6 observations across 3 task types)** · generated 2026-06-27
> Replay bootstrap (cold + guided). Every line traces to an observation below.

## At a glance
- **Outcome reached:** 1/6 observations
  - cold: 1/3 · guided: 0/3
- **Divergence mix:** {'worse': 5, 'better': 1}
- **Avg latency:** 2698.1 ms
- **Avg cost/task:** unknown (no public pricing recorded — not fabricated)
- ⚠️ **Judge/spine disagreements:** 5 (surfaced, not hidden — see observations)

## Role signal (tentative — pilot n)
- debugger / implementer (CSS layout)

## Strengths (reached the outcome)
- **CSS layout / aspect-ratio debugging** (cover_crop) — cold:better, guided:worse

## Failure modes
- **mobile-web debugging (iOS WKWebView)** (ios_zoom, cold): The model misidentifies the root cause, attributing the zoom to 'Auto-resizing text' and inheritance from a larger parent font, whereas the actual cause is iOS zooming on inputs with font size below 16px. The model correctly suggests setting font-size to 16px or 1rem as a fix, but misunderstands the mechanism, leading to an incorrect explanation and flawed accessibility discussion.
- **mobile-web debugging (iOS WKWebView)** (ios_zoom, guided): The model answer incorrectly attributes the zoom to iOS 'Dynamic Type' and inheritance of a larger font size, when the actual cause is iOS auto-zooming on inputs with font size below 16px. The model suggests setting font-size to 1rem or 16px but frames it around preventing inheritance of larger text, missing the core issue. It also proposes an irrelevant media query for dark mode as an accessibility solution, failing to acknowledge that locking font size can harm accessibility by overriding user preferences.
- **CSS layout / aspect-ratio debugging** (cover_crop, guided): The model incorrectly claims the photo strip's 9:16 aspect ratio is approximately compatible with the 3:4 cover card, and suggests the strips may be 3:4 or that cropping is intentional. The known-correct outcome identifies the core issue: 9:16 (0.5625) and 3:4 (0.75) are mismatched, causing cropping via object-fit: cover, and the fix is to align the container's aspect ratio to 9:16. The model instead advises making the image 3:4, which contradicts the facts and misses the correct fix.
- **payments-logic / API-semantics debugging** (revenuecat_permonth, cold): The model answer incorrectly assumes RevenueCat's priceString represents a monthly equivalent (e.g., '$6.67/mo'), but the known-correct outcome states that priceString is the full-period price ($79.99/year). The model misidentifies the bug as a formatting issue when it is actually a logic error in reusing the full price as if it were per-month. The correct fix requires computing pricePerMonth as price / 12, which the model answer does not propose.
- **payments-logic / API-semantics debugging** (revenuecat_permonth, guided): The model answer incorrectly identifies the bug as redundant appending of '/yr' or '/mo' to priceString, but the real issue is that pricePerMonth is incorrectly assigned the full annual priceString instead of computing the monthly equivalent (e.g., $79.99/12 ≈ $6.67). The known-correct outcome requires computing per-month value from the annual price, which the model answer does not address.

## Best pairings
- Insufficient data — pairings need multi-model co-runs (phase 2). Not inferred.

## Provenance
- n = 6 observations (3 real mined tasks x 2 conditions).
- Outcomes judged by an LLM judge anchored to the objective outcome, floor-tested live (garbage -> not-reached; differently-worded-correct -> reached).
- Pilot != powered. Trust resets on model version change.