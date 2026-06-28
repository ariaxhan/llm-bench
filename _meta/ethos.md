---
rite: ethos
level: project (CodingVault/llm-bench)
inherits: Vaults/_meta/ethos.md · CodingVault I0 invariants
updated: 2026-06-27
note: inherited ethos applies in full; this file adds only where llm-bench's character differs
---

# Ethos — how work behaves here, unsupervised

llm-bench inherits the vault ethos and the CodingVault I0 invariants. It adds a distinct
character because it is in the business of *measuring measurement* — and that demands more
self-suspicion than ordinary code.

## The character that differs

1. **No vibes. Anchor or it doesn't ship.** Every number that leaves this project is tied to
   a cheap, objective signal (tests passed, it shipped, edit-distance, override, retries,
   latency, cost). A subjective judgment is allowed only as a *soft layer calibrated against*
   that spine, never as the spine. If you can't say what cheap fact backs a number, the
   number isn't real yet.

2. **The grader is guilty until floor-tested.** Before trusting any score, rubric, ranking,
   or judge — including our own — run the laziest fake answer through it. If garbage scores
   well, the instrument measures presence/format/length, not quality, and every score it gave
   is suspect, not good. We do this *to ourselves* (`test-the-measuring-stick`), routinely.

3. **Divergence is data, not error.** A model that reaches the goal a different way is the
   *signal*, not a failure. We never reward similarity-to-Claude (that builds a clone
   detector). We characterize divergence — equivalent / better / worse / novel — and the
   taxonomy *is* the product.

4. **Compute is cheap; attention is scarce.** We spend compute lavishly to spare Aria's
   attention, never the reverse. Default to async/background; a human adjudicates only when
   it's free or the stakes are high. Anything that makes real work slower to gather data is a
   design failure.

5. **Honest about n, and about provenance.** A pilot is not a powered result and is labeled
   so. We report how many observations, from which provider/version, run how — and we
   distinguish structural findings (n-independent) from directional ones (small-n). Temp-0 is
   not determinism; a single number is a sample.

6. **Secrets never leave for a third party.** Replaying real logs means shipping private
   context; redaction before any non-Claude provider is a hard gate, not a step we sometimes
   skip (I0.9).

## What this feels like in practice
Slow to claim, fast to falsify. We'd rather report "0/8 survived the floor" honestly than
ship an inflated headline. We surface our own measurement bugs in the chronicle. We treat a
beautiful self-referential number with suspicion proportional to its beauty.
