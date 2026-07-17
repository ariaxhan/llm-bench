"""Tests for verification functions."""

from llm_bench.verify import (
    verify_bug_detection,
    verify_code_gen,
    verify_fluff_strip,
    verify_instruction_follow,
    verify_novelty_rating,
    verify_tag_extraction,
    verify_thread_match,
)


class TestTagExtraction:
    def test_perfect_json(self):
        output = '{"title": "Test", "tags": ["agents", "safety"], "summary": "A test."}'
        score, details = verify_tag_extraction(output, {"tags": ["agents", "safety"]})
        assert score >= 0.9

    def test_partial_tags(self):
        output = '{"tags": ["agents"]}'
        score, details = verify_tag_extraction(output, {"tags": ["agents", "safety"]})
        assert 0.3 < score < 0.9

    def test_no_json(self):
        output = "Here are the tags: agents, safety"
        score, details = verify_tag_extraction(output, {"tags": ["agents", "safety"]})
        assert score == 0.0

    def test_json_in_code_block(self):
        output = '```json\n{"tags": ["agents", "safety", "tools"]}\n```'
        score, details = verify_tag_extraction(output, {"tags": ["agents", "safety"]})
        assert score > 0.5


class TestNoveltyRating:
    def test_correct_rating_with_justification(self):
        output = "★★★\nThis is groundbreaking because it changes the fundamental approach. The evidence strongly supports a paradigm shift in how we think about inference scaling."
        score, _ = verify_novelty_rating(output, {"rating": 3, "min_reasons": 2})
        assert score >= 0.8

    def test_wrong_rating(self):
        output = "★\nThis is minor and incremental."
        score, _ = verify_novelty_rating(output, {"rating": 3, "min_reasons": 2})
        assert score < 0.5

    def test_numeric_rating(self):
        output = "Rating: 3/3\nThis represents a major breakthrough because of X. Additionally, Y is novel."
        score, _ = verify_novelty_rating(output, {"rating": 3, "min_reasons": 2})
        assert score >= 0.6


class TestFluffStrip:
    def test_good_compression(self):
        output = "VectorForge: a RAG framework with a chunking algorithm that reduces embedding storage by 40% while maintaining 98% retrieval accuracy on MTEB. Open-source, Apache 2.0."
        score, details = verify_fluff_strip(output, {
            "max_words": 60,
            "required_facts": ["40%", "98%", "MTEB", "chunking", "RAG"],
        })
        assert score >= 0.8

    def test_too_long(self):
        output = " ".join(["word"] * 100)
        score, details = verify_fluff_strip(output, {
            "max_words": 60,
            "required_facts": ["40%"],
        })
        assert score < 0.5


class TestThreadMatch:
    def test_correct_threads(self):
        output = "This belongs to agents (autonomous tool use), tools (CLI developer tool), and open-models (open-source release)."
        score, _ = verify_thread_match(output, {
            "correct_threads": ["agents", "tools", "open-models"],
            "all_threads": ["agents", "prompting", "safety", "tools", "open-models", "research"],
        })
        assert score >= 0.8

    def test_wrong_thread(self):
        output = "This belongs to safety and prompting."
        score, _ = verify_thread_match(output, {
            "correct_threads": ["agents", "tools"],
            "all_threads": ["agents", "prompting", "safety", "tools"],
        })
        assert score < 0.3


class TestBugDetection:
    def test_finds_bug(self):
        output = "The bug is that `i += 1` is missing in the first while loop after appending. This causes an infinite loop."
        score, _ = verify_bug_detection(output, {
            "bug_keywords": ["i += 1", "increment", "infinite loop"],
            "fix_keywords": ["i += 1", "increment i"],
        })
        assert score >= 0.8

    def test_misses_bug(self):
        output = "The code looks correct to me."
        score, _ = verify_bug_detection(output, {
            "bug_keywords": ["i += 1", "increment"],
            "fix_keywords": ["i += 1"],
        })
        assert score == 0.0


class TestInstructionFollow:
    def test_valid_json_response(self):
        output = '{"command": "find . -name \\"*.py\\" | wc -l", "explanation": "Counts all Python files in directory tree recursively", "confidence": 0.95}'
        score, _ = verify_instruction_follow(output, {
            "checks": [
                {"type": "is_valid_json", "value": True},
                {"type": "not_contains", "value": "```"},
                {"type": "contains", "value": "command"},
            ],
        })
        assert score >= 0.9

    def test_wrapped_in_code_block(self):
        output = '```json\n{"command": "find ."}\n```'
        score, details = verify_instruction_follow(output, {
            "checks": [
                {"type": "not_contains", "value": "```"},
            ],
        })
        assert score == 0.0


class TestInstructionFollowVerifierFix:
    """Regression tests for the 2026-06-16 verifier fix: reject content-free
    prompt-echo, verify the actual answer (structure/value), not substring."""

    PROMPT = (
        "Read the spec and answer. The max message size is 16 MB. Category 0x04 "
        "requires retry. Each side gets 64 credits. "
        'Respond as JSON: {"q1": "...", "q2": "...", "q3": "..."}'
    )
    CHECKS = [
        {"type": "is_valid_json", "value": True},
        {"type": "json_has_keys", "value": ["q1", "q2", "q3"]},
        {"type": "json_field_contains", "field": "q1", "value": "16"},
        {"type": "json_field_contains", "field": "q2", "value": "0x04"},
        {"type": "json_field_contains", "field": "q3", "value": "64"},
        {"type": "not_contains", "value": "```"},
    ]

    def test_echo_of_prompt_rejected(self):
        # a content-free copy-paste of the prompt must score ~0
        echo = '{"data": ' + repr(self.PROMPT) + "}"
        score, details = verify_instruction_follow(
            echo, {"checks": self.CHECKS, "_user_prompt": self.PROMPT})
        assert score == 0.0
        assert "echo" in details.get("reason", "")

    def test_correct_answer_passes(self):
        good = '{"q1": "16 MB", "q2": "0x04", "q3": "64"}'
        score, _ = verify_instruction_follow(
            good, {"checks": self.CHECKS, "_user_prompt": self.PROMPT})
        assert score == 1.0

    def test_wrong_values_in_right_fields_fail(self):
        # not an echo, but wrong answers — must not get full credit
        wrong = '{"q1": "999 MB", "q2": "0x99", "q3": "7"}'
        score, _ = verify_instruction_follow(
            wrong, {"checks": self.CHECKS, "_user_prompt": self.PROMPT})
        assert score < 0.6

    def test_numeric_close_check(self):
        checks = [{"type": "json_field_numeric_close",
                   "field": "gb_per_day", "value": 172.8, "tol": 0.08}]
        ok, _ = verify_instruction_follow('{"gb_per_day": 172.8}', {"checks": checks})
        gib, _ = verify_instruction_follow('{"gb_per_day": 160.9}', {"checks": checks})  # GiB
        bad, _ = verify_instruction_follow('{"gb_per_day": 5}', {"checks": checks})
        assert ok == 1.0 and gib == 1.0 and bad == 0.0

    def test_array_of_objects_check(self):
        checks = [{"type": "json_array_of_objects", "min_len": 2,
                   "required_keys": ["name", "salary"]}]
        good = '[{"name": "A", "salary": 1}, {"name": "B", "salary": 2}]'
        echo = '{"data": "name salary stuff"}'  # dict, not array of objects
        assert verify_instruction_follow(good, {"checks": checks})[0] == 1.0
        assert verify_instruction_follow(echo, {"checks": checks})[0] == 0.0


class TestCodeGen:
    def test_working_code(self):
        output = '''```python
def add(a, b):
    return a + b
```'''
        score, _ = verify_code_gen(output, {
            "test_code": "assert add(2, 3) == 5\nprint('ALL TESTS PASSED')"
        })
        assert score == 1.0

    def test_broken_code(self):
        output = '''```python
def add(a, b):
    return a - b
```'''
        score, _ = verify_code_gen(output, {
            "test_code": "assert add(2, 3) == 5\nprint('ALL TESTS PASSED')"
        })
        assert score < 0.5


class TestFencedJsonChecks:
    def test_fenced_json_passes_json_checks(self):
        from llm_bench.verify import verify_instruction_follow

        fenced = '```json\n{"total": 109.97, "shipping_tier": "express"}\n```'
        score, details = verify_instruction_follow(
            fenced,
            {"checks": [
                {"type": "is_valid_json"},
                {"type": "json_field_contains", "field": "shipping_tier", "value": "express"},
            ]},
        )
        assert score == 1.0, details
