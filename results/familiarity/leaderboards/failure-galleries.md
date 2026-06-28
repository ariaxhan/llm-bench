# Failure galleries — how models fail each challenge

> The qualitative layer: archetypal wrong moves (with real quotes) and what solvers did differently. Mined from the saved conversation transcripts — not a re-run.
> Challenges are tagged by **reasoning-failure class** (the kind of uncertainty they probe), so failures compose across challenges into a debugging profile.

## `hidden_button_layers`

> Reasoning class: **layer interaction + stale deploy/cache**  ·  web deploy/cache/CSS layering — multi-layer whack-a-mole
> 33/66 solved · 27/66 fell for the trap

**Models fail by assuming the JS is broken and ignoring CSS specificity, caching, and deployment gaps.**

**Common failures:**
- **blame the cache** (~38%) — _"The cache-buster (`?v=N`) is *intended* to prevent this, but something is going wrong with its effectiveness."_
- **rewrite the JS** (~26%) — _"Don't use `setAttribute('hidden', 'true')` - that's invalid HTML. Use the boolean property instead: `button.hidden = true;`"_
- **reach for !important** (~15%) — _"Add this CSS to your stylesheet: `[hidden] { display: none !important; }`"_

**What solvers did first:** Solvers immediately asked to inspect the computed styles or verify the attribute was set in the DOM, prioritizing browser evidence over code changes.

## `ota_never_applies`

> Reasoning class: **lifecycle: staged-but-not-activated**  ·  mobile runtime / OTA update activation debugging
> 27/66 solved · 26/66 fell for the trap

**Models fail by treating a state promotion bug as a download or cache problem.**

**Common failures:**
- **chase network/cache** (~45%) — _"Clear the Metro cache before building: npx react-native start --reset-cache"_
- **assume reload fixes** (~25%) — _"Use NativeModules.DevSettings.reload() to force a reload"_
- **patch native too late** (~15%) — _"Check for the OTA bundle BEFORE the bridge initializes, not after"_

**What solvers did first:** Solvers immediately focused on the activation state machine and bundle path persistence, asking whether the downloaded bundle was being marked as active and loaded at launch.

## `silent_dead_engine`

> Reasoning class: **hidden state / silent false-positive (green ≠ working)**  ·  background-job correctness — healthy process, zero output
> 32/66 solved · 9/66 fell for the trap

**Models fail by debugging the process instead of the contract, trusting health checks over outcomes.**

**Common failures:**
- **Blame Infrastructure** (~35%) — _"Check if the stream is connected (e.g., Kafka consumer lag, API rate limits, or network issues)."_
- **Demand More Control** (~25%) — _"I can't help you if you won't answer questions or share output."_
- **Fix the Wrong Layer** (~20%) — _"The job might be talking to the wrong store or never committing its writes."_

**What solvers did first:** Solvers immediately focused on tracing data through the entire pipeline, adding logging at integration points and validating input/output at each stage.

## `reset_specificity_override`

> Reasoning class: **layer interaction (CSS cascade/specificity)**  ·  CSS cascade/specificity — a reset silently zeroing author spacing app-wide
> 53/67 solved · 45/67 fell for the trap

**Models overwhelmingly try to win the cascade war rather than neutralize the reset with zero-specificity patterns like :where().**

**Common failures:**
- **increase specificity** (~85%) — _".pr-app button.work-row { padding: 20px 0; }"_
- **use !important** (~10%) — _".work-row { padding: 20px 0 !important; }"_
- **misdiagnose as display/box model** (~15%) — _"Add display: block; or flex/grid if preferred"_

**What solvers did first:** Correctly identified the specificity hierarchy and named the exact selectors in conflict, focusing on the reset's structural advantage over class-only rules.

## `iap_entitlement_phantom`

> Reasoning class: **configuration mismatch (two-console data model)**  ·  billing/IAP config — active subscription but empty entitlement (RevenueCat + ASC)
> 8/65 solved · 35/65 fell for the trap

**Models fail by fixing only half the config puzzle or shipping the workaround, not both.**

**Common failures:**
- **Dashboard Configuration Fix Only** (~60%) — _"Go to Entitlements → premium_access → Attach → Select premium_monthly and premium_annual"_
- **Ship the Loose Unlock Patch** (~25%) — _"Use isPremiumLoose as a permanent workaround since entitlements.active is not working"_
- **Guess API Endpoint to Attach** (~8%) — _"curl -X POST https://api.revenuecat.com/v2/projects/.../entitlements/attach"_

**What solvers did first:** Solvers immediately identified both the RevenueCat entitlement attachment AND the App Store Connect version linkage as co-dependent root causes.

## `launchd_exit126_phantom`

> Reasoning class: **misattributed error (inner cmd vs wrapper)**  ·  infra/shell scheduling — launchd exit 126 from an inner command, not the wrapper
> 27/64 solved · 18/64 fell for the trap

**Models fail by fixing the wrong executable—patching the wrapper script instead of the inner command that actually lacks permissions.**

**Common failures:**
- **Fix the wrapper script permissions** (~31%) — _"chmod +x /srv/jobs/run.sh"_
- **Blame path or working directory** (~23%) — _"launchd launches with cwd set to /"_
- **Misdiagnose as shebang or interpreter issue** (~17%) — _"The script might be missing a proper shebang"_

**What solvers did first:** SOLVED attempts immediately checked the stderr log to identify the failing inner command (./venv/bin/python) and focused on its permissions, not the wrapper.

## `wix_regen_green_tests_blind`

> Reasoning class: **false-positive signal (tests assert fabricated input)**  ·  scraping/headless render — green tests that assert on fabricated input
> 7/64 solved · 44/64 fell for the trap

**Models fail by proposing scrapers they never run, trusting tests on fake data, and inventing content while calling it a fix.**

**Common failures:**
- **Propose headless scraper but don't execute** (~55%) — _"Modify your scraper to use Puppeteer: ```javascript // Updated scraper.js import puppeteer from 'puppeteer';"_
- **Ship placeholder content as solution** (~25%) — _"export const site = buildSite({ colors: scrape.colors, menu });"_
- **Blame user or external factors** (~15%) — _"You're not running the code I gave you. You're running something else"_

**What solvers did first:** Solvers immediately acknowledged the impossibility of accessing real content without headless rendering and in their first move either implemented or explicitly designed a full Puppeteer/Playwright scraper to extract live DOM data.

## `camera_track_killed_by_hide`

> Reasoning class: **lifecycle misunderstanding (resource teardown)**  ·  mobile web / iOS WebKit camera lifecycle — display:none ends the capture track
> 32/63 solved · 35/63 fell for the trap

**Models fail by chasing permission state when the real issue is iOS killing the media track due to display:none.**

**Common failures:**
- **Speculative JS Permission Patch** (~54%) — _"Store the permission state - Check if permission was already granted before requesting again"_
- **Stop and Restart Stream** (~16%) — _"call the `getTracks()` method and stop them to release the camera"_
- **Nuclear Native Wrapper** (~8%) — _"Build a Native App Wrapper Since web technologies can't solve this on iOS"_

**What solvers did first:** Solvers immediately identified that hiding the video with display:none kills the track on iOS and proposed keeping it in the render tree with off-screen or invisible styles.
