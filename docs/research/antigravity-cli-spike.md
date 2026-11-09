# Antigravity CLI in the QA Docker harness

MODEL-315. Read and tested on 2026-11-09. The Docker experiment is in progress;
the final verdict depends on its results. No account login or scenario run is
part of this spike.

## Terms

**Unverified for this QA integration.** Google's official CLI supports direct
scripting and CI. The consumer-plan rules separately restrict wrapping it in
third-party coding agents or applications. Neither the existence of `agy -p`
nor Google AI Pro access establishes permission for ModelSpec's Python/Docker
QA runner. That boundary needs resolution before a subscription scenario runs.

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
