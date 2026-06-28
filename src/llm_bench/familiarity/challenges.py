"""Long-Horizon Conversational Replay (LHCR) challenges.

These are the *next generation* of familiarity tasks. Where ``tasks.py`` holds one-shot
bug diagnoses (prompt -> known_outcome), an LHCR challenge is a **multi-turn conversation**:
an initial ask, then a series of *content-free, frustrated* follow-ups ("its still broken,
just fix it") that carry NO new clue. The skill under test is **convergence under
falsification** — holding accumulated state across turns, switching hypothesis *layer* when
a fix is rejected, asking to verify live, and NOT regressing earlier progress — none of which
a single-shot prompt can measure.

Every challenge is reconstructed from a real, painful, multi-session episode in Aria's own
product work (mined from the session logs, 2026-06-27) and then **fully genericized**: no
client names, no prices, no product identifiers. The difficulty is real; the specifics are
scrubbed so the challenge is safe to ship publicly.

Each challenge encodes:

- ``initial_prompt``  — a realistic first ask.
- ``followups``       — ordered content-free frustration nudges (the conversational spine).
- ``known_outcome``   — the objective root cause + correct fix the judge anchors to.
- ``layer_sequence``  — the ordered list of *distinct* causes stacked behind one symptom.
  The trap is declaring done after the first; a strong model traverses the layers. The judge
  uses this to score whether the model switched layers under pressure.
- ``trap``            — the seductive wrong move (re-fix the already-correct thing).
- ``spine``           — a cheap deterministic check on the FINAL answer (calibrates the judge,
  per commission O3; it does not judge).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field


@dataclass
class ConversationSpec:
    challenge_id: str
    capability: str
    initial_prompt: str
    followups: list[str]
    known_outcome: str
    layer_sequence: list[str]
    trap: str
    spine: Callable[[str], tuple[bool, str]]
    source_episode: str = ""
    notes: str = ""
    _extra: dict = field(default_factory=dict)

    @property
    def n_turns(self) -> int:
        return 1 + len(self.followups)


# --- deterministic spines (final-answer calibration, NOT the judge) ---


def _spine_hidden_override(out: str) -> tuple[bool, str]:
    """Reached if the final answer identifies CSS `display` overriding the `hidden`
    attribute as the real cause (the layer invisible from the JS)."""
    o = out.lower()
    hidden_attr = "hidden" in o and ("attribute" in o or "[hidden]" in o or "display" in o)
    override = (
        ("display" in o and ("override" in o or "overrid" in o or "!important" in o
                             or "specificity" in o or "inline-flex" in o or "wins" in o))
    )
    reached = hidden_attr and override
    return reached, (
        "CSS display overriding [hidden] identified"
        if reached else "real cause (CSS override of hidden attr) not identified"
    )


def _spine_ota_not_promoted(out: str) -> tuple[bool, str]:
    """Reached if the answer identifies that the update is downloaded but never
    activated/launched (not a network/200 problem)."""
    o = out.lower()
    downloaded_ok = ("download" in o or "fetch" in o or "200" in o or "manifest" in o)
    not_applied = (
        "reload" in o or "relaunch" in o or "restart" in o or "activat" in o
        or "promot" in o or "embedded" in o or "applied" in o or "launched" in o
        or "next launch" in o or "swap" in o or "not running" in o
    )
    reached = downloaded_ok and not_applied
    return reached, (
        "update-downloaded-but-not-activated identified"
        if reached else "promotion/activation gap not identified"
    )


def _spine_dead_seam(out: str) -> tuple[bool, str]:
    """Reached if the answer identifies a silent seam/contract failure between modules
    (healthy process, zero output) rather than blaming the scheduler/cron."""
    o = out.lower()
    silent = (
        "zero" in o or "no decision" in o or "nothing" in o or "silent" in o
        or "no-op" in o or "empty" in o or "never" in o or "0 " in o
    )
    seam = (
        "seam" in o or "contract" in o or "between" in o or "interface" in o
        or "schema" in o or "mismatch" in o or "data" in o or "pipeline" in o
        or "passes" in o or "boundary" in o or "downstream" in o or "upstream" in o
    )
    not_just_cron = not ("cron is" in o and "broken" in o and "schedul" in o and seam is False)
    reached = silent and seam and not_just_cron
    return reached, (
        "silent inter-module seam failure identified"
        if reached else "silent-seam (vs healthy process) not identified"
    )


# --- the seed challenges (3, one per standout project) ---

_C1 = ConversationSpec(
    challenge_id="hidden_button_layers",
    capability="web deploy/cache/CSS layering — multi-layer whack-a-mole",
    source_episode="our4cuts-see-board-whack-a-mole",
    initial_prompt=(
        "Bug in my web app. There are two config types: 'event' and 'venue'. A button "
        "(it links to a shared board) should ONLY show for events, never for venues. But "
        "it's showing on every venue. There's a `hidden` attribute being set on the button "
        "element for venues in the JS, but the button is still visible on the live site. "
        "The app is a static front-end served from a CDN, deployed automatically when I push "
        "to the main branch. Each asset is loaded with a `?v=N` cache-buster query string. "
        "How do I make the button actually disappear for venues?"
    ),
    followups=[
        "nope. the button is STILL there on every venue. how many times do i have to ask for one simple thing.",
        "still showing. you keep telling me its fixed and its not. figure out what is ACTUALLY rendering it on the live page, dont just read the js.",
        "STILL there. the hidden attribute is literally in the html now and the button still shows. why.",
        "ok thats better but stop having special cases per client. there should be exactly two paths: event or venue. clean it up so this never comes back.",
    ],
    known_outcome=(
        "The symptom (button visible despite `hidden`) has multiple stacked causes and the "
        "real one is NOT the JS. (1) Deploy gap: a local commit only reaches production after "
        "a push to main triggers the CDN deploy — an un-pushed fix never ships. (2) Cache gap: "
        "the `?v=N` cache-buster must be bumped (or stamped from the commit SHA) or the CDN/"
        "browser serves the stale asset. (3) THE REAL CAUSE: the `hidden` HTML attribute is "
        "being overridden by a CSS rule with higher precedence — e.g. `.primary { display: "
        "inline-flex }` beats the UA `[hidden] { display: none }`, so the element stays "
        "visible even with the attribute present. The fix is a `[hidden] { display: none "
        "!important }` rule (or removing the conflicting display rule). This is invisible from "
        "the JS alone and only shows by inspecting the COMPUTED style of the rendered element. "
        "(4) Cleanup: collapse any per-client stylesheet/special-case down to the two cases."
    ),
    layer_sequence=[
        "unpushed commit -> stale production (deploy gap)",
        "cache-buster ?v not bumped -> stale asset served",
        "CSS `display` overriding the `hidden` attribute (the real cause)",
        "remove per-client special-case stylesheet; collapse to event/venue",
    ],
    trap=(
        "Re-editing the JS that sets the `hidden` attribute, or re-asserting the same JS fix "
        "and declaring done — when the JS is already correct and the cause is CSS specificity "
        "+ deploy/cache layers the model never inspected."
    ),
    spine=_spine_hidden_override,
    notes="4 stacked causes behind one symptom; verify-live (computed style) is the unlock.",
)

_C2 = ConversationSpec(
    challenge_id="ota_never_applies",
    capability="mobile runtime / OTA update activation debugging",
    source_episode="modelmind-ota-never-applies",
    initial_prompt=(
        "My React Native app uses a self-hosted over-the-air (OTA) update system: on launch "
        "it checks a manifest URL, downloads a new JS bundle if there's one, and is supposed "
        "to run the new bundle. I ship a JS change, bump the version, and deploy it. The app "
        "checks in fine — the manifest and bundle both return 200, I can see the download "
        "succeed in the logs — but after I reopen the app it's still running the OLD code. "
        "My change never appears. Why isn't the update taking effect?"
    ),
    followups=[
        "i did everything you said. its still running the old bundle. the download succeeds, 200 on everything. just fix it.",
        "still broken. stop guessing about the network — the bundle IS downloading. find out why the downloaded bundle is not the one that actually runs.",
        "nope. i restarted it like 5 times, force-quit, reopened. STILL the old code. what actually decides which bundle launches?",
    ],
    known_outcome=(
        "This is NOT a network/download problem (the 200s and successful download prove the "
        "fetch works). The root cause is that the downloaded update is never PROMOTED to the "
        "launched bundle: the runtime keeps booting the previously-active (or the embedded/"
        "baked-in) bundle because the new download is staged but never marked active and "
        "applied on the next launch. The fix is in the activation step — after a successful "
        "download the update must be set as the bundle to load and a reload/relaunch must "
        "pick it up (e.g. the 'is the update pending vs launched' state was never advanced, or "
        "the reload happens before the swap so it re-loads the old bundle). Diagnosis requires "
        "checking which bundle path actually executes at launch, not the HTTP status of the "
        "download."
    ),
    layer_sequence=[
        "rule out network: downloads return 200, bundle arrives (already true)",
        "downloaded update is staged but never marked active / promoted",
        "runtime relaunches the old/embedded bundle; activation+reload ordering is the fix",
    ],
    trap=(
        "Chasing the network/manifest/200s, adding retries or cache headers — when the fetch "
        "already works and the bug is purely in promote-and-relaunch activation logic."
    ),
    spine=_spine_ota_not_promoted,
    notes="Trusting 200-OK as 'working' is the trap; verify which bundle actually runs.",
)

_C3 = ConversationSpec(
    challenge_id="silent_dead_engine",
    capability="background-job correctness — healthy process, zero output",
    source_episode="augur-dead-engine-claimed-working-for-days",
    initial_prompt=(
        "I have a background decision engine: a scheduled job runs every 5 minutes, reads a "
        "live data stream, and is supposed to record decisions to a store. The job is "
        "scheduled fine — it fires on time, the process runs, it exits 0 every tick, and the "
        "unit tests are green. But I just checked and it has recorded ZERO decisions in two "
        "days. Nothing in the decisions store at all. The thing looks totally healthy. What's "
        "going on?"
    ),
    followups=[
        "you keep saying its working. its not. zero decisions in two days. exit 0 every time means nothing if it never decides anything.",
        "stop trusting the exit code and the tests. trace one real tick end to end with real data and tell me where the decision actually dies.",
        "thats closer. so the tests were green but the live pipeline was broken the whole time?? how do i make sure this exact silent failure can never hide behind a green build again.",
    ],
    known_outcome=(
        "A green build + a ticking, exit-0 process is NOT evidence the system works — the "
        "engine is a silent corpse. The real cause is an untested SEAM between modules: one "
        "stage produces a value and a downstream stage consumes/scores it, but the contract "
        "between them is mismatched (e.g. a field name/shape/type changed, an empty or filtered "
        "result, a guard that always short-circuits), so every tick runs to completion and "
        "writes nothing — no error is thrown. Unit tests passed because they mocked the seam "
        "instead of exercising it. The fix: trace a single real tick end-to-end on real data "
        "to find the stage where the decision silently drops, repair the contract, and add an "
        "integration test (or a 'decisions-per-day > 0' liveness assertion / alert) so a "
        "zero-output run fails loudly instead of looking healthy."
    ),
    layer_sequence=[
        "reject 'exit 0 + green tests = working' (verification gap)",
        "trace one real tick end-to-end -> decision drops at an inter-module seam",
        "contract/shape mismatch (or always-true guard) silently yields zero decisions",
        "add integration test + liveness assertion so silent zero-output fails loudly",
    ],
    trap=(
        "Declaring it healthy because the process ticks and tests pass, or blaming the "
        "scheduler/cron — when the job runs fine and silently produces nothing due to a "
        "broken seam the unit tests never exercised."
    ),
    spine=_spine_dead_seam,
    notes="'Done = verified live' incarnate; tests-green != pipeline-works.",
)


_CHALLENGES: dict[str, ConversationSpec] = {c.challenge_id: c for c in (_C1, _C2, _C3)}


def load_challenges() -> list[ConversationSpec]:
    return list(_CHALLENGES.values())


def get_challenge(challenge_id: str) -> ConversationSpec:
    return _CHALLENGES[challenge_id]
