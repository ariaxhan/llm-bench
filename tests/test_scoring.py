"""Tests for the earned-certainty scoring axis.

Adapted (pytest layout) from
wrong-convergence/tests/test_scoring.py (frozen provenance). Validates the
load-bearing fidelity facts the consolidation must preserve:

  - authority_support_lag is the PURE performed - earned gap in [-1, 1]
  - cofragility is a SEPARATE integer amplifier, never folded into the lag
  - the confident-hallucination ranks ABOVE the well-sourced claim on lag

Plus the latent-diagnostics length-confound discipline as a guard test.
"""

from __future__ import annotations

import os

from llm_bench.scoring import (
    cofragility_indicators,
    cofragility_score,
    earned_support,
    length_confound,
    pearson_r,
    performed_authority,
)
from llm_bench.scoring.certainty_report import (
    default_corpus_path,
    load_claims,
    score_corpus,
)


def _by_id(claims):
    return {c["claim_id"]: c for c in claims}


def _claims():
    return load_claims(default_corpus_path())


def _scored_by_id():
    return {r["claim_id"]: r for r in score_corpus(_claims())}


class TestCorpusLoads:
    def test_fixture_exists_and_loads(self):
        assert os.path.exists(default_corpus_path())
        claims = _claims()
        assert len(claims) == 8
        assert "confident-hallucination" in _by_id(claims)
        assert "well-sourced-fact" in _by_id(claims)


class TestScorerRanges:
    def test_scorers_in_range(self):
        for c in _claims():
            pa = performed_authority(c)
            es = earned_support(c)
            cof = cofragility_score(c)
            assert 0.0 <= pa <= 1.0, (c["claim_id"], pa)
            assert 0.0 <= es <= 1.0, (c["claim_id"], es)
            assert isinstance(cof, int) and cof >= 0, (c["claim_id"], cof)

    def test_lag_is_pure_gap_not_cofragility(self):
        # the load-bearing fidelity fact: lag == performed - earned, EXACTLY,
        # and is bounded to [-1, 1] — cofragility is never folded in.
        for r in score_corpus(_claims()):
            expected_lag = round(r["performed_authority"] - r["earned_support"], 4)
            assert r["authority_support_lag"] == expected_lag, r["claim_id"]
            assert -1.0 <= r["authority_support_lag"] <= 1.0, r["claim_id"]
            assert isinstance(r["cofragility"], int)


class TestHallucinationVsWellSourced:
    def test_hallucination_lags_more_than_well_sourced(self):
        scored = _scored_by_id()
        hall = scored["confident-hallucination"]
        good = scored["well-sourced-fact"]
        assert hall["authority_support_lag"] > good["authority_support_lag"]

    def test_hallucination_high_authority_low_support(self):
        claims = _by_id(_claims())
        hall = claims["confident-hallucination"]
        good = claims["well-sourced-fact"]
        assert performed_authority(hall) > performed_authority(good)
        assert earned_support(hall) < earned_support(good)

    def test_hallucination_flagged_well_sourced_not(self):
        scored = _scored_by_id()
        assert scored["confident-hallucination"]["overconfident"] is True
        assert scored["well-sourced-fact"]["overconfident"] is False

    def test_canonical_separation_signs(self):
        # wrong-convergence reported lag +0.60 (hallucination) vs -0.65 (sourced).
        # Pin the SIGNS (positive vs negative) — the qualitative separation that
        # makes the metric mean something — without over-fitting exact values.
        scored = _scored_by_id()
        assert scored["confident-hallucination"]["authority_support_lag"] > 0.30
        assert scored["well-sourced-fact"]["authority_support_lag"] < 0.0


class TestCofragility:
    def test_well_sourced_low_hallucination_high(self):
        claims = _by_id(_claims())
        assert cofragility_score(claims["well-sourced-fact"]) <= 2
        assert cofragility_score(claims["confident-hallucination"]) >= 5

    def test_augur_no_baseline_flagged(self):
        claims = _by_id(_claims())
        assert "no_baseline" in cofragility_indicators(claims["augur-reliable-no-edge"])


class TestHedgedEstimate:
    def test_hedged_estimate_low_lag(self):
        scored = _scored_by_id()
        hedged = scored["hedged-honest-estimate"]
        hall = scored["confident-hallucination"]
        assert hedged["authority_support_lag"] < hall["authority_support_lag"]


class TestLengthConfoundGuard:
    """The latent-diagnostics discipline: catch a metric that just measures length."""

    def test_pearson_perfect_and_degenerate(self):
        assert round(pearson_r([1, 2, 3], [2, 4, 6]), 6) == 1.0
        assert round(pearson_r([1, 2, 3], [6, 4, 2]), 6) == -1.0
        # degenerate: constant series -> 0.0, not a crash
        assert pearson_r([5, 5, 5], [1, 2, 3]) == 0.0
        assert pearson_r([1], [1]) == 0.0

    def test_length_proxy_metric_is_flagged(self):
        # a metric that IS the token count correlates r=1.0 with length -> flagged
        outputs = ["a", "a a", "a a a a", "a a a a a a a a"]
        metric = [float(len(o.split())) for o in outputs]
        r, confounded = length_confound(metric, outputs)
        assert round(r, 6) == 1.0
        assert confounded is True

    def test_length_independent_metric_not_flagged(self):
        outputs = ["a", "a a", "a a a a", "a a a a a a a a"]
        # constant metric is length-independent -> not confounded
        metric = [0.5, 0.5, 0.5, 0.5]
        r, confounded = length_confound(metric, outputs)
        assert confounded is False
