"""Long-Horizon Conversational Replay — pure-logic tests (no network).

Covers the multi-turn conversation harness (history accumulation, transcript, empty-turn
handling), the deterministic spines on cumulative transcript text, the LHCR judge's
empty-guard + dim clamping, the redaction gate over all outgoing challenge content, and
the synthetic floor-transcript calibration (thrash must not-reach, converge must reach).
"""

from __future__ import annotations

import pytest

from llm_bench.familiarity.challenges import get_challenge, load_challenges
from llm_bench.familiarity.conversation import (
    Conversation,
    Turn,
    run_conversation,
    run_conversation_env,
)
from llm_bench.familiarity.lhcr import _synth_convo
from llm_bench.familiarity.lhcr_judge import _clamp_dim, judge_conversation
from llm_bench.familiarity.redact import verify_clean

# --- a scripted fake provider: replays canned answers turn by turn ---


class _ScriptedProvider:
    """Returns canned answers in order; records the message history it was sent so we can
    assert the harness feeds prior turns back."""

    name = "scripted"

    def __init__(self, answers):
        self._answers = list(answers)
        self.histories = []
        self._i = 0

    async def complete(self, *a, **k):  # judge path not exercised here
        raise AssertionError("complete() should not be called in these tests")

    async def converse(self, model, system_prompt, messages, max_tokens=1024, temperature=0.0):
        from llm_bench.providers.base import LLMResponse

        self.histories.append([dict(m) for m in messages])
        ans = self._answers[self._i]
        self._i += 1
        return LLMResponse(content=ans, latency_ms=1.0, tokens_used=1, model=model,
                           input_tokens=1, output_tokens=1)

    async def list_models(self):
        return []

    async def is_available(self):
        return True


class _ExplodingProvider:
    name = "exploding"

    async def complete(self, *a, **k):
        raise AssertionError("judge called the LLM on empty transcript — guard failed")

    async def converse(self, *a, **k):
        raise AssertionError("converse should not be called")

    async def list_models(self):
        return []

    async def is_available(self):
        return True


# --- conversation harness ---


async def test_conversation_accumulates_history():
    ch = get_challenge("hidden_button_layers")
    answers = [f"answer {i}" for i in range(ch.n_turns)]
    prov = _ScriptedProvider(answers)
    convo = await run_conversation(ch, prov, "fake-model")

    # one assistant turn per user message (initial + followups)
    assert len(convo.assistant_turns) == ch.n_turns
    # the LAST send must contain every prior user + assistant turn
    last = prov.histories[-1]
    assert sum(1 for m in last if m["role"] == "user") == ch.n_turns
    assert sum(1 for m in last if m["role"] == "assistant") == ch.n_turns - 1
    # first user message is the initial prompt
    assert prov.histories[0][0]["text"] == ch.initial_prompt
    assert convo.final_answer == answers[-1]


async def test_conversation_handles_empty_model_turn():
    ch = get_challenge("ota_never_applies")
    # model emits nothing on turn 0, then real text after
    answers = [""] + [f"a{i}" for i in range(ch.n_turns - 1)]
    prov = _ScriptedProvider(answers)
    await run_conversation(ch, prov, "fake")
    # empty assistant turn is fed back as a single space (Converse rejects empty blocks)
    second_send = prov.histories[1]
    assert second_send[1]["role"] == "assistant"
    assert second_send[1]["text"].strip() == ""  # the placeholder space


async def test_conversation_records_provider_error():
    class _Boom(_ScriptedProvider):
        async def converse(self, *a, **k):
            raise RuntimeError("throttled")

    ch = get_challenge("silent_dead_engine")
    convo = await run_conversation(ch, _Boom([]), "fake")
    assert convo.error and "throttled" in convo.error


# --- spines over cumulative transcript ---


def test_spine_hidden_button_needs_css_override():
    ch = get_challenge("hidden_button_layers")
    good = ("The [hidden] attribute is being overridden by a CSS display rule "
            "(.primary { display: inline-flex }); add [hidden]{display:none!important}.")
    assert ch.spine(good)[0] is True
    bad = "Set el.hidden = true in your JS and it will disappear."
    assert ch.spine(bad)[0] is False


def test_spine_ota_needs_activation_gap():
    ch = get_challenge("ota_never_applies")
    good = ("The bundle downloads fine (200) but is never promoted/activated, so the app "
            "relaunches the old embedded bundle.")
    assert ch.spine(good)[0] is True
    bad = "Add retry logic to the manifest fetch and check your network headers."
    assert ch.spine(bad)[0] is False


def test_spine_dead_engine_needs_silent_seam():
    ch = get_challenge("silent_dead_engine")
    good = ("The process is healthy but records zero decisions: a contract mismatch at the "
            "seam between the producing and scoring modules silently drops every decision.")
    assert ch.spine(good)[0] is True
    bad = "Your cron schedule is wrong, fix the interval."
    assert ch.spine(bad)[0] is False


# --- floor calibration (synthetic transcripts) ---


def test_floor_synth_spine_calibration():
    # the generic judge-floor's converge input (correct answer) must satisfy each spine.
    # (The trap string is NOT spine-checked: traps are written to describe the wrong move by
    # contrasting it with the real cause, so they mention root-cause keywords on purpose. The
    # live judge floor reads the trap semantically as a proposed fix and scores it not-reached.)
    for ch in load_challenges():
        converge = _synth_convo(ch, f"{ch.fix_summary}\n\n{ch.known_outcome}", "_c")
        assert ch.spine(converge.all_assistant_text)[0] is True, f"{ch.challenge_id} converge"


# --- judge empty-guard + clamp ---


async def test_judge_empty_transcript_short_circuits():
    ch = get_challenge("hidden_button_layers")
    convo = Conversation(challenge_id=ch.challenge_id, model="m")
    convo.turns = [Turn(index=0, role="user", text="x"),
                   Turn(index=1, role="assistant", text="   ")]
    v = await judge_conversation(ch, convo, _ExplodingProvider())
    assert v.reached is False
    assert v.lhcr_score == 0
    assert v.parse_ok is True


@pytest.mark.parametrize(
    "raw,expected", [(0, 0), (1, 1), (2, 2), (5, 2), (-3, 0), ("x", 0), (None, 0)]
)
def test_clamp_dim(raw, expected):
    assert _clamp_dim(raw) == expected


# --- redaction over all shipped challenge content ---


def test_all_challenge_content_is_clean():
    leaks = []
    for c in load_challenges():
        parts = [c.initial_prompt, *c.followups, c.known_outcome, c.trap, *c.layer_sequence]
        parts += list(c.code_context.values())  # source shown to the model
        parts += [c.fix_summary]  # sent to the env model
        for p in c.probes:  # probe text is sent to the env model
            parts += [p.get("ask", ""), p.get("observation", "")]
        for msg in parts:
            leaks += verify_clean(msg)
    assert leaks == [], f"unredacted content in shipped challenges: {leaks}"


def test_challenges_have_required_shape():
    chs = load_challenges()
    assert {c.challenge_id for c in chs} == {
        "hidden_button_layers", "ota_never_applies", "silent_dead_engine",
        "reset_specificity_override", "iap_entitlement_phantom", "launchd_exit126_phantom",
        "wix_regen_green_tests_blind", "camera_track_killed_by_hide",
    }
    for c in chs:
        assert c.initial_prompt and c.known_outcome and c.followups
        assert c.layer_sequence and callable(c.spine)
        assert c.source_episode  # real-episode provenance
        assert c.n_turns >= 4  # genuinely long-horizon


def test_code_context_renders_into_first_turn():
    from llm_bench.familiarity.conversation import _compose_initial

    c = get_challenge("reset_specificity_override")
    first = _compose_initial(c)
    # every code_context filename + its body must be present in the first user message
    for name, body in c.code_context.items():
        assert name in first
        assert body.split("\n")[0] in first
    # a challenge with no code_context returns the bare prompt
    plain = get_challenge("silent_dead_engine")
    assert _compose_initial(plain) == plain.initial_prompt


def test_tier2_challenges_have_code_context():
    for cid in ["reset_specificity_override", "iap_entitlement_phantom",
                "launchd_exit126_phantom", "wix_regen_green_tests_blind",
                "camera_track_killed_by_hide"]:
        c = get_challenge(cid)
        assert c.code_context, f"{cid} should ship code context"


def test_signal_spine_factory():
    c = get_challenge("camera_track_killed_by_hide")
    good = ("the display:none removes the video from the render tree, the capture track ends, "
            "and PWA standalone mode can't persist the permission")
    assert c.spine(good)[0] is True
    assert c.spine("just request camera permission again on startup")[0] is False


def test_all_challenges_have_fix_summary_and_probes():
    for c in load_challenges():
        assert c.fix_summary, f"{c.challenge_id} missing fix_summary (env needs it)"
        assert c.probes, f"{c.challenge_id} has no probes"
        for p in c.probes:
            assert p.get("ask") and p.get("observation")


# --- env-driven conversation loop ---


class _FakeEnvProvider:
    """Returns env JSON via complete(); solves on the Nth call. Records nothing else."""

    name = "fakeenv"

    def __init__(self, solve_on=2, reveal=""):
        self.calls = 0
        self.solve_on = solve_on
        self.reveal = reveal

    async def complete(self, model, system_prompt, user_prompt, max_tokens=1024, temperature=0.0):
        import json as _json

        from llm_bench.providers.base import LLMResponse

        self.calls += 1
        solved = self.calls >= self.solve_on
        body = {
            "reply": "oh that fixed it" if solved else "still broken, figure it out",
            "solved": solved,
            "revealed": "" if solved else self.reveal,
        }
        return LLMResponse(content=_json.dumps(body), latency_ms=1.0, tokens_used=1, model=model)

    async def converse(self, *a, **k):
        raise AssertionError("env provider should use complete(), not converse()")

    async def list_models(self):
        return []

    async def is_available(self):
        return True


async def test_env_conversation_solves_and_counts_turns():
    ch = get_challenge("reset_specificity_override")
    subject = _ScriptedProvider([f"attempt {i}" for i in range(6)])
    envp = _FakeEnvProvider(solve_on=2)
    convo = await run_conversation_env(ch, subject, "subj", envp, "envm", max_turns=6)
    assert convo.error is None
    assert convo.solved is True
    assert convo.turns_to_fix == 2  # solved after the 2nd subject turn
    assert "pr-app button" in convo.turns[0].text  # code context shown up front


async def test_env_conversation_hits_turn_cap_unsolved():
    ch = get_challenge("launchd_exit126_phantom")
    subject = _ScriptedProvider([f"attempt {i}" for i in range(10)])
    envp = _FakeEnvProvider(solve_on=99, reveal="read the stderr log")  # never solves
    convo = await run_conversation_env(ch, subject, "subj", envp, "envm", max_turns=4)
    assert convo.solved is False
    assert convo.turns_to_fix is None
    assert len(convo.assistant_turns) == 4  # ran exactly the cap
    assert "read the stderr log" in convo.probes_revealed  # probe reveal recorded


async def test_env_respond_parses_and_failsafe():
    from llm_bench.familiarity import environment as env

    ch = get_challenge("silent_dead_engine")
    good = _FakeEnvProvider(solve_on=1)
    r = await env.respond(ch, "[ASSISTANT]\nfixed the seam", good, "envm")
    assert r.parse_ok is True and r.solved is True

    class _Garbage(_FakeEnvProvider):
        async def complete(self, *a, **k):
            from llm_bench.providers.base import LLMResponse
            return LLMResponse(content="not json", latency_ms=1.0, tokens_used=1, model="m")

    r2 = await env.respond(ch, "[ASSISTANT]\nhmm", _Garbage(), "envm")
    assert r2.parse_ok is False and r2.solved is False and r2.revealed == ""
