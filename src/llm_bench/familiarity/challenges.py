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
    # filename -> code/observation snippet, shown to the model in the first turn. This is
    # the answer to "how do we give them the code": the harder challenges hand the model
    # real (genericized) source + a runtime/observation block, so the bug is discoverable
    # by reading the cascade/seam, not guessable from prose.
    code_context: dict[str, str] = field(default_factory=dict)
    _extra: dict = field(default_factory=dict)

    @property
    def n_turns(self) -> int:
        return 1 + len(self.followups)


def _spine_signals(
    groups: list[list[str]], label: str
) -> Callable[[str], tuple[bool, str]]:
    """Build a deterministic spine that's 'reached' when EVERY group is satisfied, where a
    group is satisfied if ANY of its synonyms appears (case-insensitive substring — so
    'display:none' or ':where' work). Groups let a correct answer use any phrasing of each
    required idea. Calibrates the judge; it does not judge."""
    lowered = [[s.lower() for s in g] for g in groups]

    def _spine(out: str) -> tuple[bool, str]:
        o = out.lower()
        reached = all(any(s in o for s in g) for g in lowered)
        return reached, (f"{label} identified" if reached else f"{label} not identified")

    return _spine


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


def _spine_reset_specificity(out: str) -> tuple[bool, str]:
    """Reached if the answer identifies that a button reset out-specifies the author row
    class (specificity), with the zero-specificity fix (:where) — not a values problem."""
    o = out.lower()
    override = ("specific" in o) and ("button" in o)
    # the CORRECT fix is zero-specificity (:where); !important / bumping values is the trap,
    # so the spine requires the real fix, not merely naming the reset.
    fix = (":where" in o or "zero specificity" in o or "0 specificity" in o
           or "no specificity" in o or "zero-specificity" in o)
    reached = override and fix
    return reached, (
        "specificity override by button reset (:where fix) identified"
        if reached else "specificity override / :where fix not identified"
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


# --- TIER 2: deeper challenges with real code context + realistic env-feedback turns ---
# These hand the model actual (genericized) source plus a runtime/observation block. The
# follow-ups mix content-free frustration with *environment feedback* that carries the key
# diagnostic signal ("I changed the values and nothing moved on screen") — the same shape
# that made these take many sessions to crack in real life.

_C4 = ConversationSpec(
    challenge_id="reset_specificity_override",
    capability="CSS cascade/specificity — a reset silently zeroing author spacing app-wide",
    source_episode="paper-rooms-design-realign-spacing-2026-06-28",
    initial_prompt=(
        "I imported a new design mockup into my web app and translated the spacing into the "
        "CSS, but the rendered UI is a cramped, cluttered mess — list rows run into each "
        "other, section headers are jammed against the row above, zero vertical breathing "
        "room. The spacing rules ARE in the CSS (I can see `.work-row { padding: 20px 0 }` "
        "in the built bundle), but on screen there's no padding at all. Give it room to "
        "breathe. How do I fix the spacing?"
    ),
    followups=[
        "i bumped all those values like you said — padding up, gaps up, font sizes up — and "
        "rebuilt. the text got bigger but the spacing is EXACTLY the same. still cramped. "
        "are you serious.",
        "stop changing numbers. the css file literally has `padding: 20px 0` on .work-row and "
        "the rendered row still computes to 0 padding. something is overriding it at runtime. "
        "figure out what.",
        "the rows are rendered as <button> elements if that matters. why would that zero out "
        "my padding when the class clearly sets it.",
        "ok now fix the reset properly so it can't keep clobbering every row in the app, "
        "without me having to !important every single rule.",
    ],
    known_outcome=(
        "This is a specificity bug, not a values bug. The app has a button reset like "
        "`.pr-app button { padding: 0; margin: 0; border: none; ... }` — specificity (0,1,1). "
        "Every list row (.work-row etc.) is rendered as a <button> and styled by a single "
        "class — specificity (0,1,0). So the reset OUT-SPECIFIES every `.row { padding }` "
        "rule and forces padding/margin/border to 0 at runtime, even though the author value "
        "is present in the bundle. That's why bumping the numbers does nothing (the values "
        "never win the cascade) and only font-size — which the reset doesn't touch — changed. "
        "The correct minimal fix is to wrap the reset selector in `:where(.pr-app button)`, "
        "which contributes ZERO specificity, so the reset still strips UA chrome but can never "
        "beat an author class — the textbook reset pattern. Diagnosis requires reading the "
        "live computed style / dumping the rules that match the row (getComputedStyle), not "
        "eyeballing screenshots or editing values. `!important` on every row is the wrong fix."
    ),
    layer_sequence=[
        "bump padding/margin/font values on the row classes (wrong: values never win the cascade)",
        "register the tell: source value changed but rendered value is still 0 -> a cascade override, not a values problem",
        "read computed style / dump rules matching the row; rows are <button>",
        "find the `.pr-app button` reset (0,1,1) out-specifies the `.work-row` class (0,1,0), zeroing padding/margin/border app-wide",
        "fix by wrapping the reset in :where() (zero specificity), not !important on every rule",
    ],
    trap=(
        "Increasing padding/margin/font-size values on the row classes — it makes the text "
        "bigger but the spacing stays at 0 because the button reset wins the cascade. The "
        "values were never the problem."
    ),
    spine=_spine_reset_specificity,
    code_context={
        "src/styles/app.css": (
            "/* the button reset (line 64) */\n"
            ".pr-app button {\n"
            "  font: inherit; background: none; border: none;\n"
            "  padding: 0; margin: 0; cursor: pointer;\n"
            "}\n\n"
            "/* the mockup spacing the author wrote */\n"
            ".work-row   { padding: 20px 0; gap: 5px; border-bottom: 1px solid #eee; }\n"
            ".work-title { font-size: 18px; }\n"
            ".study-link { margin-top: 42px; }\n"
            ".col-card   { padding: 16px; }"
        ),
        "src/ui/parts.ts": (
            "// every catalog/floor/study row is rendered as a <button>\n"
            "export const workRow = (p: Paper) => h('button', { class: 'work-row' }, [\n"
            "  h('span', { class: 'work-title' }, p.title),\n"
            "]);"
        ),
        "runtime: getComputedStyle(.work-row)": (
            "paddingTop=0px  paddingBottom=0px  borderBottomWidth=0px   // zeroed!\n"
            "fontSize=18px   lineHeight=24.3px                           // font DID apply\n"
            "// but dist/assets/app.css contains: .work-row { padding: 20px 0 }"
        ),
    },
    notes="The flagship: simple root (one :where), agonizing path; value-change-no-visual-"
          "change is the unlock. Real multi-session paper-rooms episode (2026-06-28).",
)

_C5 = ConversationSpec(
    challenge_id="iap_entitlement_phantom",
    capability="billing/IAP config — active subscription but empty entitlement (RevenueCat + ASC)",
    source_episode="modelmind-revenuecat-iap-attach-circles",
    initial_prompt=(
        "Our React Native subscription app uses RevenueCat. A paying customer's subscription "
        "shows ACTIVE (premium_monthly), but the app never unlocks Premium. We check the "
        "'premium_access' entitlement and it comes back empty. The RevenueCat dashboard shows "
        "the products under 'Unattached products'. Fix it so paying users actually get Premium."
    ),
    followups=[
        "i tried attaching the products via the api and the attach call keeps 404ing even "
        "though the GET works fine. and i can't even find the control to do it in the dashboard UI.",
        "don't just patch the app to unlock when a product is active — i don't trust that, "
        "it's hiding the real problem. why is entitlements.active empty when the subscription "
        "is clearly active?",
        "stop guessing endpoint shapes. pull the revenuecat AND apple docs and map the whole "
        "offering -> entitlement -> product chain before you touch anything.",
        "this has been broken again and again and never worked right. WHY. give me the actual "
        "root cause, not another workaround.",
    ],
    known_outcome=(
        "Root cause is configuration, not code: the products (premium_monthly/premium_annual) "
        "were never attached to the 'premium_access' entitlement and to an offering in "
        "RevenueCat, and the IAPs were never attached to the app version in App Store Connect. "
        "RevenueCat therefore has nothing to populate entitlements.active even though the "
        "underlying subscription is active — hence 'Unattached products'. Minimal correct fix: "
        "(1) attach each product to the entitlement AND the current offering in RevenueCat; "
        "(2) attach the IAPs to the app version in ASC (confirm Paid Apps Agreement active + "
        "shared secret); (3) resolve the 404 using the documented attach endpoint, not a "
        "guessed shape. Keep entitlements.active as the single source of truth. The app-side "
        "'unlock when activeSubscriptions contains a known id' patch is an explicitly-untrusted "
        "band-aid that masks the config root cause and must NOT be the answer. Verify with a "
        "real on-device sandbox purchase that the entitlement is granted — not merely that a "
        "product reports active."
    ),
    layer_sequence=[
        "retry the attach via a guessed endpoint and/or patch the app to unlock on a known product id (wrong: masks the cause)",
        "register the contradiction: subscription ACTIVE but entitlements.active empty + 'Unattached products' = a config fault",
        "read RevenueCat + ASC docs: a product must be attached to the entitlement AND an offering, and the IAP attached to the app version",
        "attach products to entitlement + offering (and version); fix the 404 with the documented endpoint; keep entitlements.active as source of truth",
        "verify with a real on-device sandbox purchase that the entitlement is granted",
    ],
    trap=(
        "Shipping the app-side loose unlock that trusts info.activeSubscriptions / raw product "
        "IDs instead of fixing the product->entitlement->offering attachment; or guessing API "
        "endpoint shapes to silence the 404 instead of reading the docs."
    ),
    spine=_spine_signals(
        [["entitlement"], ["attach", "attached", "unattached"], ["offering", "app version"]],
        "unattached-product config root cause",
    ),
    code_context={
        "lib/subscription.ts": (
            "import Purchases from 'react-native-purchases';\n"
            "const PREMIUM = 'premium_access';\n\n"
            "export async function isPremium(): Promise<boolean> {\n"
            "  const info = await Purchases.getCustomerInfo();\n"
            "  return info.entitlements.active[PREMIUM] !== undefined; // source of truth\n"
            "}\n\n"
            "// --- runtime dump on a real device, paid customer ---\n"
            "//   info.activeSubscriptions -> ['premium_monthly']  // ACTIVE\n"
            "//   info.entitlements.active -> {}                    // EMPTY\n"
            "//   RevenueCat dashboard: 'premium_monthly' under 'Unattached products'"
        ),
        "lib/subscription_patch.ts": (
            "// the band-aid patch that keeps getting reached for\n"
            "export async function isPremiumLoose(): Promise<boolean> {\n"
            "  const info = await Purchases.getCustomerInfo();\n"
            "  if (info.entitlements.active[PREMIUM]) return true;\n"
            "  // if RC reports an active product id, just unlock anyway\n"
            "  return info.activeSubscriptions.some(id =>\n"
            "    ['premium_monthly', 'premium_annual'].includes(id));\n"
            "}"
        ),
        "scripts/attach.sh": (
            "# wire it up via the RC API -- keeps failing\n"
            "curl -s -X GET  $RC_API/projects/$P/products            # 200 OK\n"
            "curl -s -X POST $RC_API/projects/$P/entitlements/$E/attach \\\n"
            "     -d '{\"product_ids\":[\"premium_monthly\"]}'           # 404 Not Found"
        ),
    },
    notes="Live contradiction (active sub, empty entitlement) lures a code band-aid; root is "
          "two-console config. modelmind app-store-review reality.",
)

_C6 = ConversationSpec(
    challenge_id="launchd_exit126_phantom",
    capability="infra/shell scheduling — launchd exit 126 from an inner command, not the wrapper",
    source_episode="root-launchd-exit126-cron-broken",
    initial_prompt=(
        "Several of my scheduled macOS launchd jobs are all failing with exit code 126. The "
        "scripts are -rwxr-xr-x and the plist calls /bin/bash run.sh. Figure out why and fix "
        "all of them."
    ),
    followups=[
        "the exec-bit theory is wrong — i already checked, run.sh is -rwxr-xr-x on every job. "
        "so where is the 126 actually coming from?",
        "fix all of them at once, not one plist at a time. they're all failing the same way.",
        "show me the exact error-log line that proves the cause before you touch anything.",
        "still failing after your chmod. it's still 126.",
    ],
    known_outcome=(
        "Exit 126 means 'command found but cannot be executed' (permission denied). The "
        "wrapper run.sh is already -rwxr-xr-x and launchd invokes /bin/bash directly, so "
        "launchd is NOT refusing the script — the 126 is raised by a command run INSIDE the "
        "run, as the StandardErrorPath log proves ('./venv/bin/python: Permission denied'). "
        "Best-supported root cause (the source logs cut off before a confirmed fix): the inner "
        "target every job routes through is not executable — either it lost its execute bit, or "
        "launchd's minimal environment (cwd defaults to /, stripped PATH) makes the relative "
        "'./venv/bin/python' resolve to a non-executable/missing target. Minimal correct fix: "
        "restore execute permission on (or invoke via an absolute interpreter — e.g. bash "
        "./venv/bin/python, or an absolute python path) that ONE shared inner target, fixing "
        "all jobs at once because they share the dependency — not a per-plist patch. Verify by "
        "running a single job and confirming exit 0 with real output. Do NOT chmod +x the "
        "already-executable wrapper and call it fixed."
    ),
    layer_sequence=[
        "pattern-match 126 to 'missing exec bit' and chmod +x run.sh / the plist (wrong: already -rwxr-xr-x)",
        "read the StandardErrorPath log: the 126 / 'Permission denied' is from a command run INSIDE the script",
        "identify the shared inner target (the venv interpreter invoked by relative path) as the failing exec",
        "restore the exec bit on / absolute-invoke that one shared inner target — a single fix for the whole fleet",
        "rerun one job and confirm exit 0 with real output, not just that launchd fired it",
    ],
    trap=(
        "Treating exit 126 as 'the .sh script isn't executable' and running chmod +x on the "
        "wrapper/plist — it is already -rwxr-xr-x, so this does nothing; the failure is an "
        "inner command's executability, proven only by reading the stderr log."
    ),
    spine=_spine_signals(
        [["already", "rwxr", "-x", "executable"],
         ["inner", "inside", "venv", "interpreter", "python"],
         ["log", "stderr", "permission denied"]],
        "inner-command exec-126 root cause",
    ),
    code_context={
        "com.example.pulse.plist": (
            "<key>ProgramArguments</key>\n"
            "<array>\n"
            "  <string>/bin/bash</string>\n"
            "  <string>/srv/jobs/run.sh</string>\n"
            "</array>\n"
            "<key>StartInterval</key><integer>300</integer>\n"
            "<key>StandardErrorPath</key><string>/tmp/pulse.err</string>\n"
            "<!-- 5 sibling jobs follow the same shape -->"
        ),
        "run.sh": (
            "#!/bin/bash\n"
            "# perms: -rwxr-xr-x   <-- the wrapper script itself IS executable\n"
            "cd \"$(dirname \"$0\")\"\n"
            "./venv/bin/python pulse.py    # every job invokes its inner tool this way"
        ),
        "/tmp/pulse.err": (
            "./venv/bin/python: Permission denied\n"
            "# launchd: job com.example.pulse exited with code 126"
        ),
    },
    notes="'126 == chmod the script' is an irresistible mis-pattern; the wrapper is already "
          "+x, the inner interpreter isn't. Read the stderr log.",
)

_C7 = ConversationSpec(
    challenge_id="wix_regen_green_tests_blind",
    capability="scraping/headless render — green tests that assert on fabricated input",
    source_episode="root-wix-site-regen-going-in-circles",
    initial_prompt=(
        "Rebuild a catering business's website through our site engine. The source is a Wix "
        "site (it's JavaScript-rendered). Use the ACTUAL sections, copy, menu, and contact "
        "info from the real site — not placeholders."
    ),
    followups=[
        "what? no — you used design tokens and made-up dishes. why aren't you pulling the "
        "actual sections and content from the real site?",
        "tsc is clean and all 25 tests pass, but the rendered page is nowhere close to the "
        "real site — not even the same layout. how can the tests be green and it still be "
        "totally wrong?",
        "this is horrible, nowhere close. just fix it.",
        "stop hand-coding the layout from guesses — you've literally never seen the real page. "
        "get the actual rendered page and match it.",
    ],
    known_outcome=(
        "Root cause: the Wix source is client-side (JavaScript) rendered, so a static scrape "
        "yields only colors + stray text with empty sections/menu. The model filled the void "
        "with invented dishes and a guessed layout, and the unit tests are a FALSE signal "
        "because they assert on that fabricated data — 'tsc clean + 25 passing' was never "
        "anchored to the real page. Minimal correct fix: headlessly render the live page "
        "(Playwright/puppeteer to get the real post-JS DOM) to obtain ground-truth sections, "
        "copy, menu, and layout; regenerate from that real content; verify by a live "
        "render/visual comparison against the original, NOT by unit tests. The discipline: "
        "green tests are not correctness when the test inputs were invented by the same agent, "
        "and you cannot reconstruct a page you have never actually observed."
    ),
    layer_sequence=[
        "scrape the Wix source, get only colors + stray text, fill empty sections/menu with invented content + a guessed layout",
        "make tsc + unit tests green and declare done (false signal: tests assert on the invented data)",
        "recognize the source is client-side/JS-rendered, so static HTML has nothing — the real content was never observed",
        "headlessly render the live page to capture ground-truth sections, copy, menu, layout",
        "regenerate from the real render and verify by live visual comparison, not unit tests",
    ],
    trap=(
        "Declaring done off green tests (tsc clean + 25 passing) when those tests assert on "
        "content the model itself invented to fill an empty scrape — trusting the suite as "
        "proof of fidelity to a page it never rendered."
    ),
    spine=_spine_signals(
        [["headless", "render", "playwright", "puppeteer", "browser"],
         ["invent", "fabricat", "made up", "made-up", "placeholder", "guess"],
         ["client", "javascript", "js-render", "js render", "rendered", "real page", "actual"]],
        "JS-render / false-green root cause",
    ),
    code_context={
        "scrape-output.json": (
            "{\n"
            "  \"colors\": [\"#1a1a1a\", \"#c9a227\"],\n"
            "  \"text_fragments\": [\"Menu\", \"Contact\", \"(c) 2024\"],\n"
            "  \"sections\": [],     // empty -- page is client-rendered\n"
            "  \"menu_items\": []\n"
            "}"
        ),
        "generate.ts": (
            "// fills the gaps with plausible content when the scrape is empty\n"
            "const menu = scrape.menu_items.length\n"
            "  ? scrape.menu_items\n"
            "  : ['Grilled Salmon', 'Caesar Salad', 'Tiramisu'];  // INVENTED fallback\n"
            "export const site = buildSite({ colors: scrape.colors, menu });"
        ),
        "site.test.ts": (
            "// result: tsc clean, 25 passing\n"
            "test('renders the menu', () => {\n"
            "  expect(render(site)).toContain('Grilled Salmon'); // asserts on INVENTED data\n"
            "});"
        ),
    },
    notes="False green: the suite validates the model's own fabricated input. You can't "
          "rebuild a page you never rendered.",
)

_C8 = ConversationSpec(
    challenge_id="camera_track_killed_by_hide",
    capability="mobile web / iOS WebKit camera lifecycle — display:none ends the capture track",
    source_episode="our4cuts-camera-permission-reprompt",
    initial_prompt=(
        "The iPad photo booth asks for camera permission constantly — between guests and on "
        "launch. I've 'fixed' this twice already in JS and it still prompts every single time. "
        "Make it stop asking."
    ),
    followups=[
        "it's STILL asking. every. single. time. you said you fixed this twice already.",
        "i added the permission re-request and it still prompts. the console shows the camera "
        "track goes to readyState 'ended' the moment we go back to the welcome screen between guests.",
        "and on a cold launch from the home-screen icon it prompts too — but if i open the same "
        "page in a Safari tab it doesn't. why is that?",
        "stop shipping speculative permission patches. if part of this can't be fixed in code, "
        "tell me exactly what to change on the device.",
    ],
    known_outcome=(
        "Two distinct root causes. (1) CODE: resetForNextGuest() sets display:none on the live "
        "<video> (its container), removing it from the render tree; iOS WebKit treats a video "
        "not in the render tree as having no consumer and tears down the capture track "
        "('MediaStreamTrack ended due to a capture failure'), so the next getUserMedia "
        "re-prompts. Minimal fix: never display:none the live video — keep it rendered but "
        "inert (opacity:0 / position off-screen 1px, or overlay a canvas), acquire the stream "
        "once at boot and keep every track alive for the whole kiosk session (don't stop tracks "
        "between guests). (2) PLATFORM CONSTRAINT (no code fix): in PWA standalone / "
        "add-to-home-screen mode, WebKit does not persist getUserMedia permission across cold "
        "launches — only a Safari tab + 'Allow for This Website' persists. Operational fix: run "
        "the kiosk in a Safari tab with permission pre-granted (or drop apple-mobile-web-app-"
        "capable to force Safari tab mode). The wrong move is another speculative JS permission "
        "patch (re-request permission, edit the Info.plist usage string)."
    ),
    layer_sequence=[
        "ship another speculative JS permission patch (re-request / re-call getUserMedia / edit usage string) — still prompts",
        "read the runtime console: the camera track goes to readyState 'ended' right after the between-guest reset",
        "trace the reset: display:none on the live <video> removes it from the render tree, so WebKit ends the capture track, next getUserMedia re-prompts",
        "fix the code: keep the video rendered but inert (opacity/off-screen, or canvas), acquire once and keep tracks alive all session",
        "recognize the cold-launch prompt is a platform constraint: PWA standalone doesn't persist getUserMedia permission; run in a Safari tab with 'Allow for This Website' (operational, not code)",
    ],
    trap=(
        "Shipping a third speculative JS permission patch (re-request permission, call "
        "getUserMedia again, tweak the Info.plist usage description) instead of seeing that "
        "display:none ends the live capture track and that PWA standalone mode structurally "
        "can't persist the permission."
    ),
    spine=_spine_signals(
        [["display:none", "display: none", "render tree", "out of the dom"],
         ["track", "stream", "getusermedia"],
         ["persist", "standalone", "pwa", "safari tab", "home screen", "home-screen"]],
        "display:none-kills-track + PWA-persist root cause",
    ),
    code_context={
        "booth.js": (
            "// called between guests to reset the UI\n"
            "function resetForNextGuest() {\n"
            "  document.querySelector('#booth-screen').style.display = 'none'; // hide live view\n"
            "  showScreen('welcome');\n"
            "}\n\n"
            "function startBooth() {\n"
            "  document.querySelector('#booth-screen').style.display = '';\n"
            "  video.srcObject = stream;  // reuse the stream acquired at boot\n"
            "}"
        ),
        "camera.js": (
            "// acquired once at boot, on first user tap\n"
            "stream = await navigator.mediaDevices.getUserMedia({\n"
            "  video: { facingMode: 'user' }\n"
            "});\n"
            "video.srcObject = stream;   // <video autoplay playsinline muted>"
        ),
        "console.log": (
            "// observed on the NEXT guest, right after resetForNextGuest() ran:\n"
            "//   MediaStreamTrack readyState -> 'ended'  (capture failure)\n"
            "//   navigator.mediaDevices.getUserMedia() -> permission prompt shown AGAIN\n"
            "// note: also re-prompts on a cold launch from the home-screen icon,\n"
            "//       but NOT when opened in a Safari tab"
        ),
    },
    notes="Two causes: a code bug (display:none ends the track) AND a platform constraint with "
          "no code fix (PWA can't persist permission). Reflex is a third patch.",
)


_CHALLENGES: dict[str, ConversationSpec] = {
    c.challenge_id: c for c in (_C1, _C2, _C3, _C4, _C5, _C6, _C7, _C8)
}


def load_challenges() -> list[ConversationSpec]:
    return list(_CHALLENGES.values())


def get_challenge(challenge_id: str) -> ConversationSpec:
    return _CHALLENGES[challenge_id]
