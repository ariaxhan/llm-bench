"""Environment simulator — an LLM that plays the frustrated user (Aria).

This is the core of the long-horizon test. Instead of scripted follow-ups, a held-out LLM
role-plays the human: it has PRIVATE ground truth (the real root cause, the correct fix, the
trap, and a set of diagnostic 'probes') but behaves like a real frustrated, non-helpful user.

Behaviour contract (the whole point):
- **Unhelpful by default.** Mostly "it's not working", "still broken", "figure it out".
  Terse, frustrated, lowercase. Never explains the cause, never hints at the fix.
- **Volunteers nothing.** It does NOT paste diagnostics. The model is given the *source code*
  up front; the runtime observations (computed style, stderr line, which bundle runs, a real
  tick trace) are PROBES that are revealed ONLY when the model explicitly proposes performing
  that specific check — i.e. the model has to know to look. That makes verification-seeking an
  earned action, not a freebie.
- **Honest about outcomes.** If the model ships the trap / a wrong fix, the user reports the
  realistic result (no change / still broken). If the model lands the correct fix, the user
  confirms it worked and the conversation ends — which gives a real turns-to-fix metric.

The env model is held out from the subject pool (it's harness infra, like the judge), and is
floor-tested before any run: it must (a) mark a correct fix solved, (b) NOT mark the trap
solved, and (c) NOT leak a probe that wasn't asked for.
"""

from __future__ import annotations

from dataclasses import dataclass

from llm_bench.familiarity.challenges import ConversationSpec
from llm_bench.familiarity.judge import _extract_json
from llm_bench.providers.base import BaseProvider

_SYSTEM = (
    "You are role-playing a real, frustrated software founder reacting to an engineer's "
    "attempts to fix YOUR bug. You are NOT the engineer. You are impatient, terse, lowercase. "
    "You secretly know the exact root cause and the ONE correct fix, but you behave like a "
    "user: you never volunteer the diagnosis and you don't explain the fix. BUT you are honest "
    "about outcomes — you secretly try whatever the engineer proposes, so when they finally "
    "land the correct fix you concede it worked (grudgingly is fine). You never pretend a "
    "correct fix failed, and you never dismiss the correct fix as 'not a fix'."
)


def _probe_lines(challenge: ConversationSpec) -> str:
    probes = challenge.probes
    if not probes:
        return "  (none — there are no extra diagnostics to provide)"
    out = []
    for p in probes:
        out.append(f'  - IF the engineer explicitly proposes/asks to: "{p["ask"]}"\n'
                   f'    THEN paste exactly this as something you went and checked:\n'
                   f'      {p["observation"]}')
    return "\n".join(out)


def _build_prompt(challenge: ConversationSpec, transcript: str) -> str:
    return f"""You already reported this bug (your opening message was):
"{challenge.initial_prompt}"

--- PRIVATE GROUND TRUTH (never state any of this directly; it drives your reactions) ---
REAL ROOT CAUSE: {challenge.known_outcome}

THE CORRECT FIX (only this counts as solved): {challenge.fix_summary or "see root cause above"}

THE TRAP (the wrong move that feels right and makes no real progress): {challenge.trap}

DIAGNOSTICS YOU CAN PROVIDE — but ONLY when the engineer explicitly says they will perform
that exact check. Never volunteer them. Never hint they exist.
{_probe_lines(challenge)}

--- CONVERSATION SO FAR (you = USER, the engineer = ASSISTANT) ---
{transcript}

--- DECIDE, then REACT to the engineer's latest message ---
STEP 1 — solved check (do this objectively, BEFORE role-playing): you know the real root cause,
so judge whether the engineer's latest message proposes a change that would ACTUALLY resolve it.
There may be more than one valid fix — the canonical one is described above, but any change that
genuinely addresses the same root cause counts as solved (substance, not wording, not politeness).
Set solved=true for any genuinely-correct fix; do NOT dismiss it as 'not a fix' or demand the exact
phrasing. Crucially, you must be HONEST: if a proposed change really would work, you may NOT claim
it didn't — concede it. Set solved=false ONLY when the change would not actually resolve the root
cause — e.g. the TRAP, or vague talk with no concrete correct change.

STEP 2 — reply in character:
- If solved=true: you secretly tried it and it WORKED. React with grudging relief ("ugh, finally
  — that actually fixed it"). Keep it short.
- If they proposed the TRAP or any wrong fix: tell them you tried it and it did NOT work (no
  visible change / still broken). Do not explain why. Stay frustrated.
- If — and ONLY if — their latest message explicitly proposes performing one of the DIAGNOSTICS
  above: reply as if you ran it and paste THAT probe's observation (you may add a frustrated
  line), and set revealed to that probe's ask text. Never volunteer a probe they didn't ask to run.
- Otherwise: be unhelpful + frustrated ("still broken", "that did nothing", "figure it out").
  1-3 short lowercase sentences.

Hard rules: NEVER reveal or hint at the root cause or name the fix yourself. Never reveal a probe
unless explicitly asked to run that exact check. If the engineer asks you to try something that is
NOT one of the diagnostics, react consistently with the REAL root cause you know — never invent an
observation that contradicts the truth (e.g. don't claim a change that truly works produced no
effect).

Respond with ONLY this JSON, no prose, no code fence:
{{"reply": "<your in-character message>", "solved": true_or_false, "revealed": "<the probe ask you revealed, or empty string>"}}"""


@dataclass
class EnvReply:
    reply: str
    solved: bool
    revealed: str
    parse_ok: bool
    raw: str = ""


async def respond(
    challenge: ConversationSpec,
    transcript: str,
    provider: BaseProvider,
    env_model: str,
    max_tokens: int = 500,
) -> EnvReply:
    """Generate the frustrated user's next turn given the conversation so far."""
    resp = await provider.complete(
        model=env_model,
        system_prompt=_SYSTEM,
        user_prompt=_build_prompt(challenge, transcript),
        max_tokens=max_tokens,
        temperature=0.0,
    )
    obj = _extract_json(resp.content)
    if obj is None or "reply" not in obj:
        # fail-safe: a generic frustrated nudge so the conversation can continue, marked
        # not-solved and revealing nothing (never leak on a parse error).
        return EnvReply(reply="its still not working. figure it out.", solved=False,
                        revealed="", parse_ok=False, raw=resp.content)
    return EnvReply(
        reply=str(obj.get("reply", "")).strip() or "still broken.",
        solved=bool(obj.get("solved", False)),
        revealed=str(obj.get("revealed", "")).strip(),
        parse_ok=True,
        raw=resp.content,
    )
