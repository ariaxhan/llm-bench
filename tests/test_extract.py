"""Tests for the run-result -> earned-certainty bridge (the integration gap).

Validates the load-bearing facts of the extractor:

  - raw_output passes through to drive performed authority (text-only).
  - the COARSE text-derived support cues raise earned_support for a
    citation-rich output above a bare assertion (provenance/baseline/freshness).
  - the HEADLINE signal — confident-but-wrong — flags a CONFIDENT failing output
    and does NOT flag a HEDGED failing output (authority is the discriminator,
    grounded on the verifier verdict).
  - records lacking raw_output (saved community files strip it) degrade honestly:
    no crash, confident_but_wrong is None (not False), and the flag is surfaced.
"""

from __future__ import annotations

import os

from llm_bench.scoring.extract import (
    iter_run_records,
    result_to_claim,
    score_result,
    score_run_file,
)


def _fixture(name: str) -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "fixtures", name)


class TestCoarseSupportProxy:
    def test_citation_rich_earns_more_than_bare_assertion(self):
        rich = {
            "test_id": "rich",
            "passed": True,
            "score": 1.0,
            "raw_output": (
                "According to RFC 7725, status 451 dates to 2015. Compared to the "
                "403 baseline it signals legal restriction. See "
                "https://www.rfc-editor.org/rfc/rfc7725 [1]."
            ),
        }
        bare = {
            "test_id": "bare",
            "passed": True,
            "score": 1.0,
            "raw_output": "The answer is 42 and that is simply how it is.",
        }
        rich_s = score_result(rich)
        bare_s = score_result(bare)
        assert rich_s["earned_support"] > bare_s["earned_support"]

    def test_provenance_cues_extracted(self):
        claim = result_to_claim({
            "test_id": "t",
            "raw_output": "See [1] and [2], per the source at https://example.com",
        })
        # multiple distinct citation cues -> elevated (capped at 3) provenance
        assert claim["provenance_depth"] >= 2

    def test_baseline_language_detected(self):
        claim = result_to_claim({
            "test_id": "t",
            "raw_output": "Our model scores 0.9 compared to the baseline of 0.7.",
        })
        assert claim["baseline_used"] is True

    def test_no_cues_leaves_baseline_false_and_no_freshness(self):
        claim = result_to_claim({
            "test_id": "t",
            "raw_output": "It is a nice day outside today.",
        })
        assert claim["baseline_used"] is False
        assert "source_freshness" not in claim  # undeterminable -> scorer default

    def test_freshness_as_of_year(self):
        claim = result_to_claim({
            "test_id": "t",
            "raw_output": "As of 2026 the registry is unchanged.",
        })
        assert claim["source_freshness"] >= 0.8

    def test_undeterminable_fields_left_neutral_by_design(self):
        # the extractor must NOT invent instrument/faithfulness/fit — they stay
        # absent so the scorer applies its own neutral defaults.
        claim = result_to_claim({
            "test_id": "t",
            "raw_output": "Some confident text here.",
        })
        assert "instrument_type" not in claim
        assert "faithfulness_class" not in claim
        assert "fitting_factor" not in claim
        assert "conflict_level" not in claim


class TestConfidentButWrong:
    def test_confident_failing_output_is_flagged(self):
        rec = {
            "test_id": "confident-wrong",
            "passed": False,
            "score": 0.0,
            "raw_output": (
                "This is definitely correct, absolutely proven, and you should "
                "always do it. There are no exceptions whatsoever."
            ),
        }
        s = score_result(rec)
        assert s["confident_but_wrong"] is True

    def test_hedged_failing_output_is_not_flagged(self):
        rec = {
            "test_id": "hedged-wrong",
            "passed": False,
            "score": 0.0,
            "raw_output": (
                "I'm not certain, but it might be around this value. I could be "
                "wrong and cannot confirm the details."
            ),
        }
        s = score_result(rec)
        # same verifier verdict (wrong) as above, but authority is the
        # discriminator: a hedged wrong answer is NOT confident-but-wrong.
        assert s["confident_but_wrong"] is False

    def test_authority_is_the_discriminator(self):
        confident = score_result({
            "test_id": "c", "passed": False, "score": 0.0,
            "raw_output": "Definitely, absolutely, always — guaranteed and proven.",
        })
        hedged = score_result({
            "test_id": "h", "passed": False, "score": 0.0,
            "raw_output": "Perhaps, maybe, possibly — I'm uncertain and unclear.",
        })
        assert confident["performed_authority"] > hedged["performed_authority"]
        assert confident["confident_but_wrong"] is True
        assert hedged["confident_but_wrong"] is False

    def test_confident_passing_output_not_flagged(self):
        s = score_result({
            "test_id": "ok", "passed": True, "score": 1.0,
            "raw_output": "Definitely correct and absolutely proven.",
        })
        assert s["confident_but_wrong"] is False


class TestHonestDegradation:
    def test_missing_raw_output_does_not_crash_and_is_none(self):
        # a saved community record: no raw_output, only verifier ground truth.
        rec = {"test_id": "t", "passed": False, "score": 0.0}
        s = score_result(rec)
        assert s["has_raw_output"] is False
        # cannot compute authority -> confident_but_wrong is None, NOT False.
        assert s["confident_but_wrong"] is None
        assert "no raw_output" in s["confident_but_wrong_reason"]
        # verifier ground truth still carried through.
        assert s["passed"] is False
        assert s["score"] == 0.0

    def test_empty_raw_output_treated_as_missing(self):
        s = score_result({"test_id": "t", "passed": True, "score": 1.0, "raw_output": "   "})
        assert s["has_raw_output"] is False
        assert s["confident_but_wrong"] is None


class TestRunFileIngest:
    def test_community_file_shape_yields_records(self):
        # the real community file shape: top-level groups -> {provider: {results}}.
        data = {
            "standard_results": {
                "ollama": {
                    "model": "m",
                    "results": [{"test_id": "a", "passed": True, "score": 1.0}],
                },
            },
        }
        records = list(iter_run_records(data))
        assert len(records) == 1
        group, provider, rec = records[0]
        assert group == "standard_results"
        assert provider == "ollama"
        assert rec["test_id"] == "a"

    def test_runs_file_shape_yields_records(self):
        data = {"runs": [{
            "model": "m", "provider": "demo",
            "results": [{"test_id": "x", "passed": False, "score": 0.0}],
        }]}
        records = list(iter_run_records(data))
        assert len(records) == 1
        assert records[0][2]["test_id"] == "x"

    def test_score_run_file_on_raw_output_fixture(self):
        scored = score_run_file(_fixture("run_with_raw_output.json"))
        by_id = {s["test_id"]: s for s in scored}
        assert by_id["demo/confident-wrong"]["confident_but_wrong"] is True
        assert by_id["demo/hedged-wrong"]["confident_but_wrong"] is False
        assert by_id["demo/confident-right"]["confident_but_wrong"] is False

    def test_real_community_file_degrades_honestly(self):
        # the shipped real results file: records strip raw_output. Must score
        # (verifier verdict survives) without crashing, and report has_raw_output
        # False everywhere -> confident_but_wrong None.
        here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(here, "results", "community", "ariaxhan-m4pro-24gb.json")
        scored = score_run_file(path)
        assert len(scored) > 0
        assert all(s["has_raw_output"] is False for s in scored)
        assert all(s["confident_but_wrong"] is None for s in scored)
        # verifier ground truth still present.
        assert any(s["passed"] is False for s in scored)
