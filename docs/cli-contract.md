# The ModelSpec CLI contract

MODEL-307. `modelspec-dev` 0.3.0 is a thin keyed client for the hosted API.
The command is `modelspec`. Version 0.2.0 was yanked. Release publication is
an operator step after review; this repository does not publish to PyPI.

ModelSpec is an analysis of alternatives for AI models: it decides which models fit a job from your requirements, sourced benchmarks and real cost, and shows its work.

There are three ways in: this CLI, [remote MCP](https://api.modelspec.dev/mcp),
and the [HTTP API](https://api.modelspec.dev/v1/decide).
Only human lookup on the [board](https://modelspec.dev/decide/) is free.
Decisions require a ModelSpec API key. No data download and no local decision
cache. The CLI does not include the engine, registry, model cards, or offline
and snapshot commands. Repository tooling retains the
[historical offline contract](history/offline-cli-contract.md), unchanged under
its own versions, through `python -m cli.modelspec.legacy`.

## Install and orient

```sh
uvx --from modelspec-dev modelspec
pipx install modelspec-dev
pip install modelspec-dev
```

`pip install modelspec` is an unrelated project. Use `modelspec-dev`.

```sh
modelspec
modelspec --json
modelspec help agent
modelspec help agent --json
modelspec key --json
modelspec setup mcp --client claude-desktop
modelspec auth set
modelspec auth set --stdin
```

With no arguments, and with `help agent`, the CLI gives the same compact agent
orientation: the entity sentence, aggregate coverage counts dated to the bundled
public image, what it can answer, the three ways in, key procurement, install
paths, and a neutral message to relay to the human. It returns no model data,
rankings, vocabulary, or decisions. These commands work without a network.

The price data comes from `pipeline.pricing.procurement_data` and the site's
`api/worker/tiers.json`. At the current published prices the cheapest answer is
from $0.0017. `modelspec key` explains existing keys, plans, packs, checkout
availability and contact for access or invoicing. It does not promise that a
payment rail is enabled. Its human message offers an existing key, the pricing
page, and manual lookup, without urgency or persuasion.

## MCP setup

`modelspec setup mcp --client CLIENT [--config FILE] [--write] [--yes] [--json]`
supports `claude-code`, `claude-desktop`, `codex`, `gemini`, `grok`, `cursor`,
and `generic`. It prints that client's native snippet or command, its source,
and the guide link. Keys remain placeholders or environment references.
Claude Desktop uses the `mcp-remote` stdio bridge, not an unsupported native
HTTP entry. It needs Node.js/npx and `MODELSPEC_AUTH_HEADER` in Desktop's
server `env` block, with the placeholder `Bearer <MODELSPEC_API_KEY>`.
macOS GUI apps do not inherit the shell environment. Explicitly replace the
placeholder with the key to configure Desktop; doing so stores the key in
that config. Setup never copies a saved or environment key into the config.

Without `--write`, no file is read or changed. With `--write`, the CLI reads
the target JSON or TOML config, prepares a change to only `modelspec`, and
prints a redacted unified diff to stderr. It writes atomically after interactive
confirmation or `--yes`. JSON mode requires `--yes` to write; it keeps stdout a
single JSON document. Other servers and settings retain their values and bytes.
An unusual inline TOML definition is refused with manual setup as the next step.
A config that changes after the diff is prepared is refused. Generic clients
need `--config FILE` to write. The CLI never invokes a client management command.

Before replacing an existing config, `--write` saves its exact original bytes
in a sibling `<name>.modelspec-bak` with mode 0600. If that backup exists,
the new backup gets a UTC timestamp suffix; existing backups are never
overwritten. The text output reports the backup path. Successful JSON writes
include `backup`, the path or `null` when creating a new config. Cancelled and
unchanged configurations create no backup. If creating a backup fails, the
original config stays unchanged.

MCP clients must receive the referenced environment variables themselves.
`auth set` configures this CLI and does not change another client's environment.
Grok expands its environment reference when loading the config. Generic clients
use an explicit credential placeholder; complete it in the client's secret settings.

## Credentials and privacy

`MODELSPEC_API_KEY` takes precedence, including when set to an empty value.
Otherwise the CLI reads `api-key` under the user's config directory: XDG when
set, `~/Library/Application Support/modelspec` on macOS, `%APPDATA%/modelspec`
on Windows, and `~/.config/modelspec` on other platforms. A stored key must be a
regular file. POSIX requires mode 0600; Windows relies on the user-profile
directory ACL because it cannot report POSIX modes. `auth set` accepts a
hidden prompt or `--stdin`, writes atomically with 0600 permissions where
supported, and never echoes the key. There is no key
argument to put in command history. API keys travel only in an Authorization
header, never a URL. The client follows no redirects.

No telemetry. The CLI never uses, sends or logs your provider API keys. It writes no decision,
vocabulary, outcome log, or snapshot, and sends no installation or machine
identifier. Legal files remain subject to Jamie's approval; the MODEL-307 report
lists sentences that describe the former CLI and need review before release.

## Keyed commands

```sh
modelspec decide --spec FILE.yaml --json
modelspec decide --spec - --json
modelspec decide --template ID --json
modelspec vocab [SECTION] [--section SECTION] [--search TEXT] [--id ID]
                [--ids ID ...] [--detail compact|full] [--offset N] [--limit 1..20] [--json]
modelspec feedback [DECISION_ID] --rating RATING [--note TEXT]
                  [--trying-to-decide TEXT] [--template ID] [--json]
```

All three require a key before reading the Spec or contacting the API.
`decide` requires exactly one of `--spec` and `--template`. It parses JSON or
YAML, validates structure against the bundled published
[`DecideRequest` schema](decision-contract.schema.json), and sends exactly that
Spec as the body of `POST /v1/decide`. It injects no defaults, constraints,
weights, task text, or wrapper. The server validates semantics and is the
authority. The request is at most 64 KB. A template comes from a keyed
`GET /v1/vocabulary?section=templates&id=ID&detail=full`, never a bundled or
cached registry; its Spec is validated and sent unchanged.

`vocab` calls keyed `GET /v1/vocabulary`, using the MCP lookup parameters.
The default section is `starter`. `--ids` may repeat and also accepts commas.
There are at most 100 IDs; offset is nonnegative and compact limit is 1 to 20.
There is no public-export fallback and no local vocabulary cache.

With `--search`, `--id` or `--ids`, the default or explicit `starter` section
searches every vocabulary section except the coverage summary. An explicit
non-starter section keeps the lookup scoped to that section. Search covers ids,
labels and names, definitions and purposes, template categories and tiers, and
facet values. It ignores case and treats runs of underscores, hyphens, dots,
slashes and whitespace as one space. A substring or all query tokens can match;
benchmark domain links are excluded. IDs remain exact and case-sensitive.
Combining search with IDs intersects the two filters.

Lookup responses add `matches`, `total` and `searched`. Matches rank exact ids
first, then id text, labels and names, definitions and purposes, and values.
Ties use section order, then source order. Cross-section `--offset` and `--limit`
page those matches, including with full detail or IDs; each section contains
only its rows on that page. `starter` retains starter facets on that page and
its minimal Spec. Compact facets retain every allowed value. Section-scoped
rows keep their source order and existing full-detail pagination behavior.
An empty lookup adds up to five `suggestions` from all sections and a `message`
that explains the search, with a next hint to retry. A suggestion drawn from a
facet value names the facet in `id` and the value in `value`, so retrying with
that `id` resolves. Search text and each ID are at most 128 characters; a search
of only separators matches nothing. Suggestions compare
normalized ids, id segments and labels using Levenshtein similarity, keeping
scores of at least 0.4 and breaking ties by section order, then id. The
pass is bounded: it compares at most two needles, each cut to 32 characters,
and stops after 300,000 edit-distance cells, so a long miss may draw its
suggestions only from the earlier sections. Plain
vocabulary requests and a plain starter request keep their existing bodies.

`feedback` accepts the MCP fields, with `client: "cli"`. The published feedback
schema supplies rating, identifier and text limits. It requires a key locally;
like the MCP feedback tool, it forwards no Authorization to the feedback
endpoint, which reads no key. Feedback storage and its existing flags are
unchanged. The API's `recorded` or `not_recorded` response is passed through.

## Output and recovery

`--json` works before the command or on the command. Successful keyed output
is the API response body itself, without an envelope or extra fields. CLI-owned
orientation and procurement are guidance objects with `guide_version` and
`next`. CLI-owned errors use `schema_version: "2.0"`, `command`, `error`, and
`next: [...]` on stdout. Hosted refusals keep the API body and add `next`.
Human errors and their next steps go to stderr. Every failure, including usage,
validation, key storage, config writing, non-JSON HTTP errors and network errors,
ends with an actionable next step.

| Exit | Meaning | Next step |
| --- | --- | --- |
| 0 | Guidance or a successful API answer | Act on the response's evidence and limits |
| 1 | Usage, validation, local file, network, server or upgrade error | Follow `next` |
| 2 | Out of coverage or no matching answer | State the unsupported requirement; read coverage and guide |
| 5 | Missing, unreadable, invalid or refused key | `modelspec key`, then `auth set` or MODELSPEC_API_KEY; relay the human message |
| 6 | HTTP 402 or 429 | Credits and pricing; honor Retry-After |

Network failures link to `https://api.modelspec.dev/v1/health`. Coverage
refusals include what ModelSpec can answer, aggregate bundled counts and
`https://modelspec.dev/api/coverage.json` and `https://modelspec.dev/agents.md`.
The API's additive `coverage` explanation is retained on refusals and uses exit 2,
including when the existing status is `partial` or error code is `invalid_spec`. Key errors include procurement and the neutral
human message. Old-version refusals include upgrade commands.

All new agent-facing CLI text comes from `pipeline/agent_copy.py`. Run
`python -m pipeline.agent_copy write` to generate the MCP copy, agent guide,
Worker constants, and CLI bundle. The build refuses a stale bundle. Each API
response's `x-modelspec-guide-version` is compared with the bundled version.
A mismatch adds an upgrade and guide-refresh suggestion on stderr, as a JSON
notice in JSON mode, without changing a successful API body. HTTP error `next`
also contains the upgrade suggestion when versions differ.

```sh
uvx --refresh --from modelspec-dev modelspec
pipx upgrade modelspec-dev
pip install --upgrade modelspec-dev
```

Guide: https://modelspec.dev/agents.md. OpenAPI: https://modelspec.dev/openapi.yaml.
Pricing and keys: https://modelspec.dev/pricing/.

## Contract versioning, MODEL-59

A change that widens a field's range, such as nullable, a new enum value, or a
field becoming optional, bumps that contract's major version. New fields may be
added. Renaming or removing a field, changing its type or units, changing an
exit code's meaning, or changing the result shape also requires a major bump.

MODEL-318 refuses a condition or preference value outside its facet's
vocabulary with HTTP 400 `invalid_spec`. Before, `= proprietary` on
`model.weights_openness` answered 200 `no_feasible`. This change needs no
version bump of its own; the decision contract stays at 2.14. Jamie accepted
the exception below on 2026-10-04 at 11:21 ET, when the contract was at 2.13:

- The response side is additive. `error.code` stays `invalid_spec` and the
  status stays 400. Such an issue gains the optional keys `value`,
  `value_type`, `allowed_values` and `next`, and MODEL-59 allows new fields.
  Successful responses do not change.
- The input side is an exception to the rule that refusing a spec that used
  to be accepted is a major change. Every sourced snapshot fact is checked
  against the registry when the snapshot is built, so an unregistered value
  matches no model. Offering identity facets (provider, region, tier) are the
  one gap, and a follow-up closes it. `=` and `in` with such a value matched nothing, `!=`
  and `not in` matched every model and so constrained nothing, and a
  non-number on a number facet raised a server error. A client that sent one
  got an answer that ignored or misread its requirement. The vocabulary always
  listed the allowed values, and an unregistered enum preference was already
  refused. `offering.provider` accepts registered providers and vendors,
  because a subscription's provider is its plan owner.
- A major bump would make every 2.x decoder, the decide page's included,
  refuse every answer, to cover input no correct client sends. A minor bump
  signals an addition, which this is not. `error.recovery` (MODEL-285) set the
  precedent of adding optional error keys without a bump.

The new client error contract is 2.0 because it replaces the retired offline
CLI. It does not change the decision API contract, the legacy CLI envelope
1.0, or `build.export_schema_version` 3.0. Those remain separately versioned.
