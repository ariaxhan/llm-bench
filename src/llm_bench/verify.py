"""Programmatic verification functions for benchmark tests.

Every test has a verifier. No vibes scoring.
"""

from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path


def verify_tag_extraction(output: str, expected: dict) -> tuple[float, dict]:
    """Verify structured tag extraction from article text."""
    try:
        parsed = _extract_json(output)
        if not parsed:
            return 0.0, {"reason": "no valid JSON found"}

        expected_tags = set(expected["tags"])
        got_tags = set(parsed.get("tags", parsed.get("domains", [])))

        if not got_tags:
            return 0.0, {"reason": "no tags field in output"}

        precision = len(expected_tags & got_tags) / len(got_tags) if got_tags else 0
        recall = len(expected_tags & got_tags) / len(expected_tags) if expected_tags else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

        # Bonus for getting the format right
        has_title = "title" in parsed or "name" in parsed
        has_summary = "summary" in parsed or "description" in parsed
        format_bonus = 0.1 * (has_title + has_summary)

        score = min(1.0, f1 + format_bonus)
        return score, {
            "expected_tags": sorted(expected_tags),
            "got_tags": sorted(got_tags),
            "precision": round(precision, 2),
            "recall": round(recall, 2),
            "f1": round(f1, 2),
        }
    except Exception as e:
        return 0.0, {"reason": f"verification error: {e}"}


def verify_novelty_rating(output: str, expected: dict) -> tuple[float, dict]:
    """Verify novelty rating with justification."""
    expected_rating = expected["rating"]
    expected_min_reasons = expected.get("min_reasons", 1)

    # Find star rating
    stars = _count_stars(output)
    rating_match = re.search(r'(\d)[/\s]*(?:out of\s*)?[/\s]*(?:3|stars?|★)', output, re.I)
    numeric = int(rating_match.group(1)) if rating_match else stars

    if numeric == 0:
        # Try to find just a number 1-3
        simple = re.search(r'\b([1-3])\b', output[:100])
        numeric = int(simple.group(1)) if simple else 0

    rating_correct = numeric == expected_rating
    rating_score = 1.0 if rating_correct else (0.5 if abs(numeric - expected_rating) == 1 else 0.0)

    # Check for justification
    sentences = [s.strip() for s in re.split(r'[.!?\n]', output) if len(s.strip()) > 20]
    justification_score = min(1.0, len(sentences) / max(expected_min_reasons, 1))

    score = 0.6 * rating_score + 0.4 * justification_score
    return score, {
        "expected_rating": expected_rating,
        "got_rating": numeric,
        "rating_correct": rating_correct,
        "justification_sentences": len(sentences),
    }


def verify_fluff_strip(output: str, expected: dict) -> tuple[float, dict]:
    """Verify compression: output should be shorter and keep key facts."""
    max_words = expected["max_words"]
    required_facts = expected["required_facts"]

    word_count = len(output.split())
    under_limit = word_count <= max_words
    length_score = 1.0 if under_limit else max(0, 1.0 - (word_count - max_words) / max_words)

    facts_found = 0
    for fact in required_facts:
        if fact.lower() in output.lower():
            facts_found += 1
    fact_score = facts_found / len(required_facts) if required_facts else 1.0

    score = 0.4 * length_score + 0.6 * fact_score
    return score, {
        "word_count": word_count,
        "max_words": max_words,
        "under_limit": under_limit,
        "facts_found": facts_found,
        "facts_required": len(required_facts),
    }


def verify_thread_match(output: str, expected: dict) -> tuple[float, dict]:
    """Verify correct thread matching from options."""
    correct_threads = set(expected["correct_threads"])
    output_lower = output.lower()

    matched = set()
    for thread in correct_threads:
        if thread.lower() in output_lower:
            matched.add(thread)

    # Penalize wrong matches
    all_threads = set(expected.get("all_threads", []))
    wrong_matches = set()
    for thread in all_threads - correct_threads:
        if thread.lower() in output_lower:
            wrong_matches.add(thread)

    total = len(matched) + len(wrong_matches)
    precision = len(matched) / total if total else 0
    recall = len(matched) / len(correct_threads) if correct_threads else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    return f1, {
        "correct_threads": sorted(correct_threads),
        "matched": sorted(matched),
        "wrong_matches": sorted(wrong_matches),
    }


def verify_collision_detect(output: str, expected: dict) -> tuple[float, dict]:
    """Verify cross-domain connection detection."""
    required_connections = expected["connections"]
    output_lower = output.lower()

    found = 0
    for conn in required_connections:
        keywords = conn.get("keywords", [])
        keyword_hits = sum(1 for k in keywords if k.lower() in output_lower)
        if keyword_hits >= len(keywords) * 0.5:
            found += 1

    connection_score = found / len(required_connections) if required_connections else 0

    # Check if explanation exists (not just listing)
    has_reasoning = len(output.split()) > 30 and any(
        w in output_lower
        for w in ["because", "since", "implies", "suggests", "connects", "overlap"]
    )
    reasoning_bonus = 0.2 if has_reasoning else 0

    score = min(1.0, connection_score + reasoning_bonus)
    return score, {
        "connections_found": found,
        "connections_required": len(required_connections),
        "has_reasoning": has_reasoning,
    }


def verify_draft_email(output: str, expected: dict) -> tuple[float, dict]:
    """Verify email draft quality: tone, length, key points."""
    min_words = expected.get("min_words", 30)
    max_words = expected.get("max_words", 200)
    required_points = expected.get("required_points", [])
    tone = expected.get("tone", "professional")

    word_count = len(output.split())
    length_ok = min_words <= word_count <= max_words
    length_score = 1.0 if length_ok else max(0, 0.5)

    points_found = 0
    output_lower = output.lower()
    for point in required_points:
        if any(kw.lower() in output_lower for kw in point.get("keywords", [])):
            points_found += 1
    point_score = points_found / len(required_points) if required_points else 1.0

    # Tone check — crude but functional
    casual_markers = ["hey", "lol", "gonna", "wanna", "nah", "yo"]
    formal_markers = ["dear", "sincerely", "regards", "hereby"]
    casual_count = sum(1 for m in casual_markers if m in output_lower)
    formal_count = sum(1 for m in formal_markers if m in output_lower)

    tone_score = 1.0
    if tone == "professional" and casual_count > 1:
        tone_score = 0.5
    elif tone == "casual" and formal_count > 1:
        tone_score = 0.5

    score = 0.3 * length_score + 0.5 * point_score + 0.2 * tone_score
    return score, {
        "word_count": word_count,
        "length_ok": length_ok,
        "points_found": points_found,
        "tone_score": tone_score,
    }


def verify_code_gen(output: str, expected: dict) -> tuple[float, dict]:
    """Verify generated code actually runs and produces correct output."""
    test_code = expected["test_code"]

    # Extract code block from output
    code = _extract_code(output)
    if not code:
        return 0.0, {"reason": "no code block found"}

    # Write and execute
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code + "\n\n" + test_code)
        f.flush()
        try:
            result = subprocess.run(
                ["python3", f.name],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                return 1.0, {"executed": True, "stdout": result.stdout[:200]}
            else:
                return 0.2, {
                    "executed": False,
                    "error": result.stderr[:300],
                    "code_found": True,
                }
        except subprocess.TimeoutExpired:
            return 0.1, {"reason": "execution timed out"}
        except Exception as e:
            return 0.0, {"reason": f"execution error: {e}"}
        finally:
            Path(f.name).unlink(missing_ok=True)


def verify_bug_detection(output: str, expected: dict) -> tuple[float, dict]:
    """Verify the model found the planted bug."""
    bug_keywords = expected["bug_keywords"]
    fix_keywords = expected.get("fix_keywords", [])
    output_lower = output.lower()

    # Did it identify the bug?
    bug_found = any(kw.lower() in output_lower for kw in bug_keywords)
    bug_score = 1.0 if bug_found else 0.0

    # Did it suggest the right fix?
    fix_found = any(kw.lower() in output_lower for kw in fix_keywords) if fix_keywords else True
    fix_score = 1.0 if fix_found else 0.0

    # Penalty for false positives — claiming bugs that don't exist
    false_bug_markers = expected.get("false_positives", [])
    false_hits = sum(1 for m in false_bug_markers if m.lower() in output_lower)
    false_positive_penalty = min(0.3, false_hits * 0.15)

    score = max(0, 0.7 * bug_score + 0.3 * fix_score - false_positive_penalty)
    return score, {
        "bug_found": bug_found,
        "fix_found": fix_found,
        "false_positives": false_hits,
    }


def verify_multi_step_plan(output: str, expected: dict) -> tuple[float, dict]:
    """Verify a multi-step plan has correct ordering and key steps."""
    required_steps = expected["required_steps"]
    output_lower = output.lower()

    steps_found = []
    for i, step in enumerate(required_steps):
        keywords = step.get("keywords", [])
        found = any(kw.lower() in output_lower for kw in keywords)
        steps_found.append(found)

    coverage = sum(steps_found) / len(required_steps)

    # Check ordering — found steps should appear in order
    positions = []
    for step in required_steps:
        for kw in step.get("keywords", []):
            pos = output_lower.find(kw.lower())
            if pos >= 0:
                positions.append(pos)
                break

    if len(positions) > 1:
        ordered = all(
            positions[k] <= positions[k + 1] for k in range(len(positions) - 1)
        )
    else:
        ordered = True
    order_score = 1.0 if ordered else 0.5

    score = 0.7 * coverage + 0.3 * order_score
    return score, {
        "steps_found": sum(steps_found),
        "steps_required": len(required_steps),
        "ordering_correct": ordered,
    }


def verify_creative_piece(output: str, expected: dict) -> tuple[float, dict]:
    """Verify creative output meets constraints while being non-generic."""
    constraints = expected.get("constraints", {})
    min_words = constraints.get("min_words", 20)
    max_words = constraints.get("max_words", 150)
    required_elements = constraints.get("required_elements", [])
    forbidden_phrases = constraints.get("forbidden_phrases", [])

    word_count = len(output.split())
    length_ok = min_words <= word_count <= max_words
    length_score = 1.0 if length_ok else 0.3

    output_lower = output.lower()
    elements_found = sum(1 for el in required_elements if el.lower() in output_lower)
    element_score = elements_found / len(required_elements) if required_elements else 1.0

    forbidden_found = sum(1 for f in forbidden_phrases if f.lower() in output_lower)
    forbidden_penalty = min(0.5, forbidden_found * 0.25)

    # Creativity heuristic: low repetition, varied sentence length
    sentences = [s.strip() for s in re.split(r'[.!?\n]', output) if s.strip()]
    if len(sentences) > 2:
        lengths = [len(s.split()) for s in sentences]
        avg_len = sum(lengths) / len(lengths)
        variance = sum((x - avg_len) ** 2 for x in lengths) / len(lengths)
        variety_score = min(1.0, variance / 20)  # Higher variance = more varied
    else:
        variety_score = 0.5

    raw = 0.25 * length_score + 0.35 * element_score + 0.2 * variety_score
    score = max(0, raw - forbidden_penalty)
    return score, {
        "word_count": word_count,
        "length_ok": length_ok,
        "elements_found": elements_found,
        "forbidden_found": forbidden_found,
        "variety_score": round(variety_score, 2),
    }


def verify_instruction_follow(output: str, expected: dict) -> tuple[float, dict]:
    """Verify exact instruction following — format, constraints, no extras.

    Two upgrades over the original substring-only version (2026-06-16, after the
    floor audit found a content-free prompt-echo scored 1.00 on hard tests):

    1. ECHO-REJECTION GUARD: if the caller injects `_user_prompt` and the output
       is essentially the prompt copied back (long verbatim overlap), the whole
       score is 0 — a copy-paste answers nothing. Deterministic, no LLM.
    2. STRUCTURAL CHECK TYPES: `json_field_contains`, `json_has_keys`,
       `json_field_numeric_close`, `json_array_of_objects`, `contains_any_of`
       verify the actual answer (right field / computed value / parsed shape)
       instead of "is the token present somewhere in the text".
    """
    checks = expected.get("checks", [])
    output_stripped = output.strip()

    # --- echo-rejection guard (only when the prompt is available) ---
    prompt = expected.get("_user_prompt")
    if prompt and _is_prompt_echo(output_stripped, prompt):
        return 0.0, {"reason": "content-free prompt echo rejected",
                     "echo_overlap": round(_prompt_echo_ratio(output_stripped, prompt), 3)}

    # Lenient parse: a correct answer inside ```json fences must not score
    # identical to garbage — JSON checks measure the transformation/extraction
    # capability; bare-output compliance has its own dedicated checks.
    parsed = _try_json(output_stripped)
    if parsed is None:
        parsed = _extract_json(output_stripped)
    passed = 0
    details = {}
    for check in checks:
        check_type = check["type"]
        if check_type == "max_lines":
            lines = output_stripped.count("\n") + 1
            ok = lines <= check["value"]
            details["lines"] = lines
        elif check_type == "starts_with":
            ok = output_stripped.startswith(check["value"])
        elif check_type == "contains":
            ok = check["value"].lower() in output_stripped.lower()
        elif check_type == "not_contains":
            ok = check["value"].lower() not in output_stripped.lower()
        elif check_type == "is_valid_json":
            ok = parsed is not None
        elif check_type == "regex_match":
            ok = bool(re.search(check["value"], output_stripped))
        elif check_type == "max_words":
            ok = len(output_stripped.split()) <= check["value"]
        elif check_type == "json_field_contains":
            # parsed JSON has `field` whose stringified value contains `value`
            ok = _json_field_contains(parsed, check["field"], check["value"])
        elif check_type == "json_has_keys":
            ok = _json_has_keys(parsed, check["value"])
        elif check_type == "json_field_numeric_close":
            ok = _json_field_numeric_close(parsed, check["field"], check["value"],
                                          check.get("tol", 0.02))
        elif check_type == "json_array_of_objects":
            ok = _json_array_of_objects(parsed, check.get("min_len", 1),
                                       check.get("required_keys", []))
        elif check_type == "contains_any_of":
            low = output_stripped.lower()
            hit = sum(1 for v in check["value"] if v.lower() in low)
            ok = hit >= check.get("min", 1)
            details["contains_any_hits"] = hit
        else:
            ok = False

        details[f"check_{check_type}"] = ok
        if ok:
            passed += 1

    score = passed / len(checks) if checks else 0
    return score, details


# --- Helpers: echo guard + structural checks (2026-06-16 verifier fix) ---

def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.lower()).strip()


def _words(s: str) -> set:
    return set(re.findall(r"[a-z0-9]+", s.lower()))


def _prompt_echo_ratio(output: str, prompt: str) -> float:
    """Fraction of the prompt's distinct vocabulary reproduced in the output.
    A content-free echo copies the prompt back → reproduces ~all of it → ratio
    ≈ 1. A real answer is restructured/shorter and shares only the few values it
    needs → low ratio. Word-coverage (not contiguous substring) so it survives
    JSON re-escaping of newlines/quotes. Deterministic."""
    pw = _words(prompt)
    if len(pw) < 10:          # too short to judge — don't guess
        return 0.0
    ow = _words(output)
    return len(pw & ow) / len(pw)


def _is_prompt_echo(output: str, prompt: str) -> bool:
    """Reject outputs that reproduce most of the prompt's vocabulary — a
    copy-paste answers nothing. Threshold 0.75 leaves wide room for a legit
    answer that quotes the input values it needs, while a whole-prompt echo
    (~1.0 coverage) fails."""
    return _prompt_echo_ratio(output, prompt) >= 0.75


def _try_json(text: str):
    try:
        return json.loads(text.strip())
    except (json.JSONDecodeError, ValueError):
        return None


def _json_field_contains(parsed, field: str, value: str) -> bool:
    """True if `field`'s stringified value contains `value` — in a dict, or in
    ANY object of a list of dicts (so it works for JSON arrays of records)."""
    needle = str(value).lower()
    if isinstance(parsed, dict):
        return field in parsed and needle in str(parsed[field]).lower()
    if isinstance(parsed, list):
        return any(isinstance(x, dict) and field in x and needle in str(x[field]).lower()
                   for x in parsed)
    return False


def _json_has_keys(parsed, keys: list) -> bool:
    """All keys present (in the dict, or in every object of a list of dicts)."""
    if isinstance(parsed, dict):
        return all(k in parsed for k in keys)
    if isinstance(parsed, list) and parsed and all(isinstance(x, dict) for x in parsed):
        return all(all(k in x for k in keys) for x in parsed)
    return False


def _json_field_numeric_close(parsed, field: str, value: float, tol: float) -> bool:
    if not isinstance(parsed, dict) or field not in parsed:
        return False
    try:
        got = float(parsed[field])
    except (TypeError, ValueError):
        return False
    return abs(got - value) <= abs(value) * tol + 1e-9


def _json_array_of_objects(parsed, min_len: int, required_keys: list) -> bool:
    if not isinstance(parsed, list) or len(parsed) < min_len:
        return False
    if not all(isinstance(x, dict) for x in parsed):
        return False
    return all(all(k in x for k in required_keys) for x in parsed)


# --- Helpers ---

def _extract_json(text: str) -> dict | None:
    """Extract first JSON object from text."""
    # Try the whole thing first
    try:
        return json.loads(text.strip())
    except (json.JSONDecodeError, ValueError):
        pass

    # Try to find JSON in code blocks
    match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except (json.JSONDecodeError, ValueError):
            pass

    # Try to find raw JSON object
    match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except (json.JSONDecodeError, ValueError):
            pass

    return None


def _extract_code(text: str) -> str | None:
    """Extract code from markdown code blocks or raw text."""
    match = re.search(r'```(?:python)?\s*\n(.*?)```', text, re.DOTALL)
    if match:
        return match.group(1).strip()

    # If no code block, try the whole thing if it looks like code
    lines = text.strip().split("\n")
    code_lines = [ln for ln in lines if not ln.startswith("#") or ln.startswith("# ")]
    if any("def " in ln or "import " in ln for ln in code_lines):
        return text.strip()

    return None


def _count_stars(text: str) -> int:
    """Count star rating in various formats."""
    star_match = re.search(r'(★+)', text)
    if star_match:
        return len(star_match.group(1))
    emoji_match = re.search(r'(⭐+)', text)
    if emoji_match:
        return len(emoji_match.group(1))
    return 0


# Registry of verification functions
VERIFIERS = {
    "tag_extraction": verify_tag_extraction,
    "novelty_rating": verify_novelty_rating,
    "fluff_strip": verify_fluff_strip,
    "thread_match": verify_thread_match,
    "collision_detect": verify_collision_detect,
    "draft_email": verify_draft_email,
    "code_gen": verify_code_gen,
    "bug_detection": verify_bug_detection,
    "multi_step_plan": verify_multi_step_plan,
    "creative_piece": verify_creative_piece,
    "instruction_follow": verify_instruction_follow,
}
