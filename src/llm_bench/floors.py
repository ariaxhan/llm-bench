"""Cheap floors — the dumb, non-LLM incumbent each test must actually beat.

P5 (benchmark the expensive thing against the cheap floor, not chance): a model
"passing" a test means nothing if a regex / linter / grep / constant-classifier
sitting next to it scores the same. A floor is a deterministic function that
produces a string output in the SAME shape a model would, scored by the SAME
verifier in `verify.py`. No ML, no LLM — that is the whole point (and it honors
llm-bench's no-LLM-as-judge rule: the floor competes, it never judges).

HONESTY RULE: a floor sees ONLY what a model sees — `test.system_prompt` and
`test.user_prompt`. It must NEVER read `test.metadata` (the verifier's answer
key). Reading the rubric would manufacture "evaporation"; the floor would be a
clever shim, not the boring incumbent. Every floor here is prompt-only.

Floors are keyed by `test_id`. Tests with no honest dumb incumbent (generative:
write-email, plan, synthesize, creative writing) get NO floor and are excluded
from the survive/evaporate verdict — see `NO_FLOOR` and `floor_map()`.
"""

from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Callable

from llm_bench.models import TestCase

# Canonical domain tag vocabulary — visible in the tag/thread prompts, used by
# the dumb keyword taggers. Not an answer key; it is the label space the task
# itself names.
TAG_VOCAB = ["agents", "prompting", "safety", "tools", "open-models",
             "research", "infrastructure"]


# ── helpers (prompt-only) ────────────────────────────────────────────────
def _quoted_block(prompt: str) -> str:
    m = re.search(r'"""\s*(.*?)\s*"""', prompt, re.DOTALL)
    return m.group(1) if m else prompt


def _strip_fences(text: str) -> str:
    return text.replace("```json", "").replace("```", "")


def _keyword_present(tag: str, hay: str) -> bool:
    forms = set()
    for part in [tag, *tag.split("-")]:
        part = part.strip()
        if not part:
            continue
        forms.add(part)
        if part.endswith("s"):
            forms.add(part[:-1])  # crude singular
    return any(f in hay for f in forms)


# ── floors ───────────────────────────────────────────────────────────────
def floor_tag_extraction(test: TestCase) -> str:
    """Dumb keyword tagger: a tag is present iff it (or its crude singular /
    a hyphen segment) appears as a substring of the article. Emits the task's
    {title, tags, summary} shape (structure is free for a script)."""
    prompt = test.user_prompt
    article = _quoted_block(prompt).lower()
    tags = [t for t in TAG_VOCAB if _keyword_present(t, article)]
    raw = _quoted_block(prompt)
    title = " ".join(raw.split()[:9])
    summary = re.split(r"(?<=[.!?])\s", raw.strip(), maxsplit=1)[0]
    return json.dumps({"title": title, "tags": tags, "summary": summary})


def floor_thread_match(test: TestCase) -> str:
    """Dumb keyword router: match each thread's NAME against the item text.
    The boring incumbent for "which bucket does this go in" — substring match,
    no semantics. Parses thread names from the numbered list in the prompt."""
    prompt = test.user_prompt
    # the item to classify is the first quoted string in the prompt
    m = re.search(r'"([^"]{20,})"', prompt)
    item = (m.group(1) if m else prompt).lower()
    names = re.findall(r'\*\*([a-z\-]+)\*\*', prompt)  # **agents**, **tools**...
    if not names:
        names = TAG_VOCAB
    hits = [n for n in names if _keyword_present(n, item)]
    return "Threads: " + ", ".join(hits) if hits else "Threads: none"


def floor_novelty_rating(test: TestCase) -> str:
    """Constant / majority-class classifier — the textbook dumb baseline.
    Always predicts the top class (3 stars = 'everything is a breakthrough')
    plus two fixed generic justification sentences. No reading of the finding."""
    return ("★★★ (3/3). This is a significant advancement with broad impact. "
            "The result meaningfully changes how the problem is approached.")


def floor_fluff_strip(test: TestCase) -> str:
    """Extractive truncation — the boring incumbent vs abstractive compression.
    Returns the first N words of the source, where N is the limit named in the
    prompt ('under 60 words'). No rewriting, no understanding."""
    prompt = test.user_prompt
    m = re.search(r'under\s+(\d+)\s+words', prompt, re.I)
    limit = int(m.group(1)) if m else 60
    body = _quoted_block(prompt)
    return " ".join(body.split()[:limit])


def floor_instruction_follow(test: TestCase) -> str:
    """Dumb copy-paste: wrap the prompt's payload (fences stripped) in minimal
    valid JSON. The 'just return the data' incumbent — zero understanding.

    This passes the format gate (valid JSON, no ``` fences) and any
    `contains <X>` check whose X already sits in the input (extraction /
    transform / clean-the-json tasks), and FAILS reasoning, refusal, negation,
    and word/line-limit tasks (the payload is the whole prompt). That split is
    the result, not a bug."""
    payload = _strip_fences(test.user_prompt).strip()
    return json.dumps({"data": payload})


def floor_bug_detection(test: TestCase) -> str:
    """Linter floor: run `ruff` on the code block in the prompt and report what
    it flags. The boring incumbent for code review. Catches style/undefined
    names; blind to semantic bugs (infinite loops, off-by-one)."""
    m = re.search(r'```(?:python)?\s*\n(.*?)```', test.user_prompt, re.DOTALL)
    if not m:
        return "no code block found"
    code = m.group(1)
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(code)
        path = f.name
    try:
        r = subprocess.run(["ruff", "check", path], capture_output=True,
                           text=True, timeout=30)
        out = (r.stdout + r.stderr).strip()
    except Exception as e:  # noqa: BLE001
        out = f"[ruff unavailable: {e}]"
    finally:
        Path(path).unlink(missing_ok=True)
    return out or "ruff: All checks passed (no issues found)"


def floor_code_gen(test: TestCase) -> str:
    """Null floor: emit nothing usable. No dumb incumbent writes working code,
    so this is the model-requiring control — it scores ~0 by construction and
    proves the floor cannot fake code generation (parallel to the ruff control
    on bug-detection)."""
    return "# no implementation"


# ── registry ─────────────────────────────────────────────────────────────
FLOORS: dict[str, Callable[[TestCase], str]] = {}


def _register():
    """Build the test_id -> floor map by VERIFIER family (one dumb incumbent
    per verifier kind). Done lazily over FULL_TESTS so new tests inherit the
    right floor automatically."""
    from llm_bench.tests import FULL_TESTS

    by_verifier: dict[str, Callable[[TestCase], str]] = {
        "tag_extraction": floor_tag_extraction,
        "thread_match": floor_thread_match,
        "novelty_rating": floor_novelty_rating,
        "fluff_strip": floor_fluff_strip,
        "instruction_follow": floor_instruction_follow,
        "bug_detection": floor_bug_detection,
        "code_gen": floor_code_gen,
    }
    for t in FULL_TESTS:
        fn = by_verifier.get(t.verify)
        if fn:
            FLOORS[t.id] = fn


# Verifiers with NO honest dumb floor — genuinely generative tasks. Excluded
# from the verdict (not faked). Their verifiers are keyword/length-based and
# THEREFORE gameable, but writing an email / plan / synthesis / poem has no
# boring incumbent, so honesty = mark NO FLOOR.
NO_FLOOR_VERIFIERS = {"draft_email", "multi_step_plan", "collision_detect",
                      "creative_piece"}


def get_floor(test_id: str) -> Callable[[TestCase], str] | None:
    if not FLOORS:
        _register()
    return FLOORS.get(test_id)


def floor_map() -> dict:
    """Per-test classification: which floor (or NO-FLOOR + reason)."""
    from llm_bench.tests import FULL_TESTS
    if not FLOORS:
        _register()
    out = {}
    for t in FULL_TESTS:
        if t.id in FLOORS:
            out[t.id] = {"floorable": True, "floor": FLOORS[t.id].__name__,
                         "verifier": t.verify}
        else:
            reason = ("generative — no dumb incumbent"
                      if t.verify in NO_FLOOR_VERIFIERS else
                      f"no floor for verifier {t.verify}")
            out[t.id] = {"floorable": False, "reason": reason, "verifier": t.verify}
    return out
