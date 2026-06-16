"""Cheap floors — the dumb, non-LLM incumbent each test must actually beat.

P5 (benchmark the expensive thing against the cheap floor, not chance): a model
"passing" a test means nothing if a 30-line regex / linter / grep sitting next
to it scores the same. A floor is a deterministic function that produces a
string output in the SAME shape a model would, scored by the SAME verifier in
`verify.py`. No ML, no LLM — that is the whole point (and it honors llm-bench's
no-LLM-as-judge rule: the floor is a competitor, never a judge).

Each floor is keyed by `test_id`. Re-scoring lives in
`experiments/floor/run_floor.py`.
"""

from __future__ import annotations

import json
import re
from typing import Callable

from llm_bench.models import TestCase


# ── helpers ──────────────────────────────────────────────────────────────
def _article_block(prompt: str) -> str:
    """Pull the quoted source block out of a test prompt.

    Tests wrap their source text in a triple-quoted ``\"\"\" ... \"\"\"`` block.
    Falls back to the whole prompt if no block is found.
    """
    m = re.search(r'"""\s*(.*?)\s*"""', prompt, re.DOTALL)
    return m.group(1) if m else prompt


def _candidate_tags(prompt: str) -> list[str]:
    """Parse the allowed-tag vocabulary out of the tag-extraction prompt.

    The prompt names them inline: ``... domain tags from: a, b, c) ...``.
    """
    m = re.search(r'from:\s*([a-z0-9 ,\-]+)\)', prompt, re.I)
    if not m:
        return []
    return [t.strip() for t in m.group(1).split(",") if t.strip()]


# ── floors ───────────────────────────────────────────────────────────────
def floor_tag_extraction(test: TestCase) -> str:
    """Dumb keyword tagger — the boring incumbent for structured extraction.

    Algorithm (deterministic, no model):
      1. Read the allowed-tag vocabulary straight from the prompt.
      2. Read the article text from the prompt's quoted block.
      3. A tag is "present" iff the tag token, its singular (drop trailing s),
         or — for a hyphenated tag like ``open-models`` — ANY hyphen segment
         (or that segment's singular) appears as a plain substring of the
         lowercased article. That is all. No semantics, no disambiguation.
      4. Emit the JSON shape the task asks for: title = first 9 words of the
         article; summary = its first sentence. (Structure is free for a
         script — which is exactly why the verifier's format bonus is suspect.)
    """
    prompt = test.user_prompt
    article = _article_block(prompt).lower()
    vocab = _candidate_tags(prompt)

    def present(tag: str) -> bool:
        forms = set()
        for part in [tag, *tag.split("-")]:
            part = part.strip()
            if not part:
                continue
            forms.add(part)
            if part.endswith("s"):
                forms.add(part[:-1])  # crude singular
        return any(f in article for f in forms)

    tags = [t for t in vocab if present(t)]

    raw = _article_block(prompt)
    words = raw.split()
    title = " ".join(words[:9])
    first_sentence = re.split(r"(?<=[.!?])\s", raw.strip(), maxsplit=1)[0]

    return json.dumps({"title": title, "tags": tags, "summary": first_sentence})


# ── registry ─────────────────────────────────────────────────────────────
# Maps test_id -> floor function. Only tests with a genuinely dumb incumbent
# belong here; generative tasks (email, creative) have no clean floor and are
# deliberately absent.
FLOORS: dict[str, Callable[[TestCase], str]] = {
    "tag-extraction": floor_tag_extraction,
}


def get_floor(test_id: str) -> Callable[[TestCase], str] | None:
    return FLOORS.get(test_id)
