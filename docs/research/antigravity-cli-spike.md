# Antigravity CLI in the QA Docker harness

MODEL-315. Read and tested on 2026-11-09.

**Overall verdict: no for restoring the subscription QA lane now.** Question 4
blocks adoption: permission for this integration remains unverified. This is
not a finding that Google prohibits all direct CLI scripting. The technical
experiment succeeded, but actual Google AI Pro login and token reuse were
intentionally not tested.

This PR retains research and [reproducible experiment evidence](../evidence/MODEL-315-fix.md)
only. The disposable prototype is not an admissible harness provider: it has
no subscription attestation, native inventory or isolation certification.
Existing provider selection and scheduled jobs are unchanged.

## 1. Credentials and headless keyring

**Verified for a dummy Secret Service value; real credentials unverified.** The official
[authentication guide](https://antigravity.google/docs/install), read
2026-11-09, names Linux Secret Service over D-Bus as the native token store.
The [troubleshooting guide](https://antigravity.google/docs/cli/troubleshooting),
read the same day, requires an active D-Bus session and unlocked keyring in a
headless environment. These statements describe the required mechanism; they
do not by themselves prove persistence. The Docker probes did: a dummy value
was stored and retrieved in one container, retrieved again from a fresh
container with the same HOME volume, and absent in an unmounted HOME. Every
probe used `--network=none`, dropped all capabilities and prevented privilege
escalation. The test volume was removed afterward. The saved-image scan found
no dummy value in any of 19 saved-image files, including gzip-decoded layer data.
A new container without the volume also returned no dummy value. No real
credential was present anywhere in this experiment. The published negative
lookup requires exit code 1, empty stdout, and empty stderr. An offline rerun
of that lookup, with all six subprocess calls mocked and no Docker, rejects a
Secret Service connection error on stderr. The container run itself was not
repeated in the review fix.

`dbus-run-session` wraps a shell that starts `gnome-keyring-daemon --unlock
--components=secrets`. Its storage is under `/home/agent/.local/share/keyrings`
in the named HOME volume. A private tmpfs creates `/tmp/model315-runtime`
before D-Bus starts; without it, startup emitted a missing-runtime-directory
warning even though the initial keyring checks passed. The dummy test uses an
empty unlock password. This proves the storage mechanism, not encryption at rest or a real-credential
unlock policy. A production design must settle that policy before login.

## 2. Distribution and pinning

**Verified on Linux ARM64.** The
[download page](https://antigravity.google/download), read 2026-11-09, showed
1.5.2, but the Linux ARM64 release manifest fetched inside Docker resolved to
1.5.3. The observed installer supports `--dir` and `--help`, fetches a
platform manifest, and checks the archive's publisher SHA-512. It did not
expose a version-selection flag.

The [installer](https://antigravity.google/cli/install.sh) was downloaded and
inspected only in a Docker `RUN`, never executed. Its SHA-256 was
`62966c07365423bd4dc209355060744058fb30d60f5323e2d360e39de64e5042`.
Its [Linux ARM64 manifest](https://antigravity-cli-auto-updater-974169037036.us-central1.run.app/manifests/linux_arm64.json)
returned the following exact artifact and publisher checksum:

- Version: `1.5.3`.
- [Versioned Linux ARM64 archive](https://storage.googleapis.com/antigravity-public/antigravity-cli/1.5.3-6604829099950080/linux-arm/cli_linux_arm64.tar.gz).
- SHA-512: `c2fac818b3c1bb224079df03a714ccba99728b6a3a41d86d247ab2feb8582a43840c5032f1c2b75e72667623d5503e7ffda2712c4f37b6ee19f99c3fcfb25bae`.

The prototype downloads that fixed URL inside the build and rejects a checksum
mismatch before installing `antigravity` as `/usr/local/bin/agy`. It does not
execute the floating installer. Runtime auto-updates are disabled with the
[documented setting](https://antigravity.google/docs/cli/troubleshooting)
`AGY_CLI_DISABLE_AUTO_UPDATE=true`; the binary is owned by root and the test
runs as an unprivileged user. The publisher checksum is an integrity pin, not
an independently verified release signature. No retention guarantee for the
versioned URL was found, and AMD64 was not tested.

The installed binary printed `1.5.3` without network access. Observed SHA-256
values were `2d50060c7b1327995e5c81ec58829c91c2564ebb9fec165d3f9f1325ec188675`
for the archive and `bc4ddea9d28bec7e0b9887bee841500a267ac5762ee36f5cdd894c487bf2eb8e`
for the installed binary. The successful image ID was
`sha256:908dcfa5e00801e13a4dbbf2feaed938e5c14ea5639245f123d9e9d4781d808c`.
The exact Dockerfiles, probes and commands are in the evidence note.

## 3. Login and restart

**Verified pre-login screen; actual login and account persistence blocked by the spike boundary.** The
[authentication guide](https://antigravity.google/docs/install), read
2026-11-09, describes silent reuse of a saved valid token. With no saved token,
local mode opens a browser. In an SSH environment it prints an authorization
URL, then accepts the code returned by a browser on the person's local machine.
The actual `1.5.3` container, with `--network=none`, displayed that it was not
signed in and offered `1. Google OAuth` and `2. Use a Google Cloud project`.
The executor stopped at that screen with two Ctrl-C presses, exit 0. No login
method was selected, no browser opened, and no authorization code was handled.
The flow after selecting OAuth, including headless/SSH detection and any
URL/code exchange, remains documentation-based and untested in Docker.

The operator runbook is **blocked**, not a completed login recipe. The missing
pieces are a real-credential keyring-unlock policy, a confirmed manual OAuth
flow in Docker, and a native subscription-status command. Supplying an exact
account-login command before those exist would overstate this experiment.
The one-time human steps, once a follow-up has supplied those technical pieces
and Jamie has resolved the terms question, are:

1. Start the isolated interactive auth container with its dedicated HOME volume
   and unlocked keyring. Its startup must reach the observed login-method menu.
   The follow-up must supply the login command; `--cli agy` is not supported today.
2. Select `1. Google OAuth`, using the personal Google AI Pro account. For the
   documented manual flow, open the displayed URL in his own local browser.
   Confirm the follow-up has established that flow in Docker before this step.
3. Paste any returned authorization code directly into the CLI, without saving
   a transcript or sharing it with an agent.
4. Exit and recreate the container with the same volume. Verify session reuse
   and subscription entitlement through a verified native status mechanism
   before a model turn. Such a status adapter is a follow-up requirement.

The keyring probe uses only a dummy value. Even a successful restart test would
not establish that Google's real token refresh and entitlement checks work.

## 4. Terms

**Unverified for this QA integration.** Google's official CLI supports direct
scripting and CI. The FAQ calls wrapping it in third-party coding agents or
applications unsupported under consumer plans. Section 6 separately restricts
third-party access. Whether those restrictions apply to this direct QA runner
remains unverified. Neither the existence of `agy -p`
nor Google AI Pro access establishes permission for ModelSpec's Python/Docker
QA runner. Jamie owns that decision, with counsel or vendor clarification as
needed. A subscription scenario waits for his decision. This note's
no-adoption verdict stays in place.

All sources below were read on 2026-11-09. The short quotations are excerpts
where the source sentence exceeds 14 words. Each excerpt has fewer than 15
words, and each source contributes fewer than 25 quoted words.

| Source | Exact quotation | What it establishes |
| --- | --- | --- |
| [Antigravity additional terms, section 6](https://antigravity.google/terms) | "You must not abuse, harm, interfere with, or disrupt the Service." | A complete sentence. The same section restricts third-party access and warns of suspension or termination. |
| [Same section](https://antigravity.google/terms) | "using the Service in connection with products not provided by us." | An excerpt from the restriction. No personal QA exception is stated. |
| [Antigravity FAQ](https://antigravity.google/docs/faq) | "is intended for direct scripting and CI workflows." | An excerpt about CLI headless mode. Direct scripting is documented. |
| [Same FAQ](https://antigravity.google/docs/faq) | "is not supported under consumer plans." | The subject is wrapping `agy` in third-party coding agents or applications, or automating account rotation. |
| [Google One additional terms, section 1](https://one.google.com/terms-of-service) | "is governed by the terms of service applicable to such benefits." | Additional benefits defer to their service terms. This page was last modified 2026-10-01. |
| [Google universal terms](https://policies.google.com/terms) | "service-specific additional terms" | Applicable additional terms must also be followed. The US page is effective 2026-07-30. |

The [headless-mode guide](https://antigravity.google/docs/cli/headless/)
documents `agy -p`, structured output and CI workflows. The
[plans page](https://antigravity.google/docs/plans/) lists Google AI Pro and
CLI access. These are verified documentation findings. Actual account
entitlement is untested. A future subscription-only runner also needs to
verify that AI Credit Overages is set to `Never` and stop at quota exhaustion.

## Harness fit

The current runner mounts a per-provider HOME volume at `/home/agent`, drops
capabilities and starts each command in a fresh container. XDG config, data
and cache directories are inside HOME. This can accommodate Linux keyring
storage without copying a host credential directory.

There is no disabled-provider switch. `CLIS` in `qa/tui_providers.py` is both
the required configuration set and the default selection. Registering `agy`
there would include it in default operations. The shared entrypoint only
accepts existing providers, and shared Dockerfile changes invalidate existing
doctor receipts. This experiment therefore uses a separate scratch build.

Binary availability alone does not establish eligibility. A follow-up needs
native subscription-authentication status, effective customization inventory,
MCP configuration, stream parsing, and the existing paired isolation controls.
The entrypoint reconstructs the environment, so any D-Bus session must start
after that reconstruction or its address will be discarded.

## Follow-up build ticket

Jamie owns the terms decision. He decides whether this direct QA runner falls
within the documented direct scripting use or the consumer application
restriction. He may take counsel or ask the vendor for clarification. That
decision is separate from technical validation.

After Jamie decides the terms allow this integration, a follow-up implementer
can add an explicitly selected provider while keeping default jobs unchanged,
bind receipts to the exact binary, image, and adapter, and arrange Jamie's
uncaptured interactive login. The implementer runs the technical checks below.
The implementer does not make the terms decision. This note's no-adoption
verdict stays in place until Jamie decides.

Before scenarios, the implementer must verify real session reuse, native
subscription-only authentication, quota handling with no paid fallback,
effective skills/hooks/plugins/MCP inventory, and both positive and isolated
controls. The implementer also needs the native output parser, Gemini-family
model selection and cross-family judge routing. The separate login and
isolation measurements must not be inferred from this dummy-secret experiment.

## Cleanup and limits

All ticket containers, the dummy auth volume and both ticket images were
removed. The local saved-image archive and ticket scratch are also removed at
completion. Shared Docker build cache was left intact because other jobs were
using the builder; no ticket image tag remains. No host installer, account
login, model request, API key, scenario, schedule or provider configuration
change occurred. The image-layer check concerns only the known dummy value.
It does not prove where a future authenticated CLI version writes real tokens.
