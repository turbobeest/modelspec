# Agent scenarios

This catalogue asks whether agents can express real model-selection requests through ModelSpec and explain the evidence accurately. It contains 74 scenarios covering Jamie's four families and every one of the 40 decide templates. The harness reports results; fixture success rates do not gate model quality.

## Run offline

Use the repository's test environment:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m qa.agent_harness --dry-run
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest tests/test_agent_harness.py -q
```

The default report directory is `qa/reports`. `--date YYYY-MM-DD` controls the filename. `--agent claude`, `--agent openai`, and `--agent gemini` restrict the selected agents; repeat the flag to select several. Repeat `--scenario <id>` to select tasks. Caps are `--turn-cap`, `--tool-call-cap`, and `--spend-cap`.

Dry-run reads compressed fixtures and makes no network requests. API fixtures are recorded from the real decision engine using public repository inputs. Agent turns, judge replies, token counts and errors introduced into requests are scripted. Each local engine duration is captured once and replayed. They are not API network latency measurements. The fixture judge deliberately fails the full rubric because the short scripted answers lack offering-level evidence. Its configured model id identifies which judge would run live; `mode: scripted` distinguishes the replay.

To inspect or regenerate fixtures:

```sh
gzip -dc qa/fixtures/replay.json.gz > /tmp/model-268-fixtures.json
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m qa.record_fixtures
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m qa.contracts
```

The generator uses the same public premier snapshot builder as recall, records any completeness gaps, and never reads keys or calls HTTP. It records full engine responses; it does not derive recommendations from approved expectations. The MCP capture follows the descriptions registered in `mcp/src/server.ts`, including the generated `mcp/src/agent-copy.json` source, takes the decision schema from the committed contract, and mirrors the other registered Zod inputs. Source hashes include the generated copy when present, and a test rejects drift. Changes to a Zod input require reviewing the mirror in `qa/contracts.py` before refreshing it.

## Run against a nonproduction deployment

Set `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`, and `MODELSPEC_API_KEY` in your environment. Configure the API and static export origins and model ids in a copy of `qa/config.yaml`. Only the selected agents' and routed judges' keys are required. By default, Claude and Gemini answers go to the OpenAI judge, and OpenAI answers go to the Claude judge. Judge routes use the model, price and fallback profiles in `agents`. Self-judging is refused before any paid call.

```sh
python -m qa.agent_harness --config /tmp/model-268-staging.yaml \
  --api-base-url https://your-staging-worker.example \
  --export-base-url https://your-staging-export.example \
  --output-dir /tmp/model-268-private-reports
```

The runner refuses known production ModelSpec hosts and follows no redirects. It uses plain HTTP with Anthropic Messages, OpenAI Responses, and Gemini `generateContent`. The agent receives the user request and constraints, a short ModelSpec system note, the generated runtime guide and seven MCP tools. Every MCP arm, including Gemini, also receives the server's generated initialize instructions. Expectations, rubrics, source specs and gap annotations are withheld. Tools forward to configured origins and preserve origin envelopes, validation errors and unknowns. The shim mirrors the MCP's split-data setting and nested Zod field stripping. `data_split: false` and `vocabulary_path: /api/decision/vocabulary.json` select the static export path.

The live judge is a separate stateless model call with the final answer, tool evidence, scenario rubric and any approved expected evidence. It extracts the final top recommendation or tied set, then assesses constraints, ties and uncertainty. A run succeeds only when the rubric passes and its recommendation is acceptable where independent evidence exists. Recall's acceptable sets are unordered; any nonempty top subset can match. The rubric handles confidence, prohibited candidates and unknown candidates. An abstention matches recall only where an explicit rule permits it. Scenarios with `expected: null` are judged by their rubric alone.

For an independent two-judge panel, configure both other families for every route:

```yaml
judge:
  mode: panel
  routes:
    claude: [openai, gemini]
    openai: [claude, gemini]
    gemini: [claude, openai]
```

Panel members receive identical evidence and no earlier judge opinion. Success requires both to pass and agree on the extracted answer kind and top model set. A missing, invalid or disagreeing judgement fails. Each run's `judges` records the actual model, family and individual verdict, including fallback identity. `judge` contains the aggregate result. Billing reservations name failed judge attempts too, with `role: judge` and their family. Dry runs replay the scripted opinion for each configured judge and do not measure panel quality.

## Re-score saved transcripts

```sh
python -m qa.agent_harness --rescore /path/to/private/report.json \
  --config /path/to/judge-config.yaml --spend-cap 25 \
  --output-dir /path/to/private/rescored
```

This evaluates saved final answers with the configured cross-family judges. It restores tool results from the input report's `tool_responses` locally and never runs an agent or calls ModelSpec. Only judge keys are required. Missing saved evidence is an error, not a reason to fetch it. Select runs with `--agent` and `--scenario`; capped or failed agents remain in the denominator without judge calls. An old agent spend-cap status does not stop re-scoring later transcripts.

The source report stays untouched. `previous_evaluation` preserves its verdict, and metadata pins its hash and original metadata. New spending and billing reservations cover only the new judges; historical agent calls remain in the transcript. Use `--dry-run --rescore ...` to test the complete path with fixture judges, no keys and no network. That verifies plumbing and does not produce a new quality measurement. Keep all reports with private transcripts outside this public checkout.

## Measure the first request offline

```sh
python -m qa.agent_harness --first-turn-breakdown
```

This builds the exact first HTTP request for every selected provider and reports the largest request over the selected public scenarios. It needs no keys and makes no HTTP calls. Components separate the system note, runtime guide, MCP initialize instructions, tool descriptions, provider schemas, user request and protocol framing. The live sender and offline builder share the same payload construction and HTTPX JSON encoding.

The test budget is 10,000 estimated tokens for each MCP arm. The count uses `cl100k_base` when installed, otherwise `ceil(characters / 4)`, and records the method. Components count standalone JSON values; protocol framing includes token-boundary differences so the table sums to the total. This is a reproducible offline estimate, not a vendor-native billable token count. The runtime guide retains decision and reporting rules, minifies worked Specs, and omits client installation instructions and planning tables. The full guide remains published at https://modelspec.dev/agents.md.

## Spend reservations

The $25 default cap applies to the entire invocation, including judges. The price table stores USD per million tokens. A call reserves a conservative UTF-8-byte input bound plus protocol overhead and the output cap at ceiling rates before HTTP. Successful calls settle using reported tokens, including cached input and reasoning output. Contexts over 200,000 input tokens use ceiling rates. Rejected HTTP 4xx calls release their reservation when usage is absent or explicitly zero. HTTP 408, ambiguous or positive usage, HTTP 5xx, missing usage on a successful response, and transport failures retain the reservation. A provider failure after the documented attempts ends that scenario. There are no hidden SDK retries. Update both price and ceiling tables from vendor docs before a paid run. This is an estimated token-spend limit, not a substitute for vendor account limits or a cap on separately priced ModelSpec credits.

### Gemini overload retries (MODEL-286)

The 2026-10-02 private run used `gemini-3.8-flash`, a current stable ID in
[Google's model list](https://ai.google.dev/gemini-api/docs/models). Two runs
returned HTTP 503 with a high-demand message; two failed near the 60-second
client timeout. The latter report entries lack exception types, so timeout is
an inference. The sanitised declarations use Google's documented
[`parametersJsonSchema`](https://ai.google.dev/api/generate-content#FunctionDeclaration)
field and pass offline schema validation. No request-shape defect was found.

Gemini now makes at most three HTTP attempts per `step()`, including fallback.
Only HTTP 429, 503 and client timeouts permit retries (a timed-out attempt
keeps its reservation charged), with exponential waits of `1 + U(0,1)`
and `2 + U(0,1)` seconds. The final attempt can use `agents.gemini.fallback`
before the first successful reply; it stays selected thereafter. A fallback
requires its own model, price and ceiling_price settings. The default is the
current `gemini-3.7-flash`, with the same documented text rates as 3.8 Flash.
Remove the fallback setting to retry only the primary. Once a model has replied,
its thought signatures prevent a model switch, so subsequent retries keep it.
Other transport errors and HTTP statuses do not retry. Safe transport exception
types now enter private diagnostics to distinguish future timeouts.

Every attempt reserves against the shared invocation budget before HTTP.
Reservations for unknown usage remain charged. A rejected 429 releases its
reservation only when usage is absent or explicitly zero. A cap refusal prevents
the next HTTP request and retains the partial report. `runs[].model` records the
last model actually sent, including failed attempts; successful agent and judge
`model_calls` and all billing reservations also name their actual model.
Configured primary and fallback profiles remain in metadata. The fixture in
`qa/fixtures/gemini-responses.json` and `tests/test_gemini_driver.py` verify retries,
reservation ordering, fallback, cap stops, wire schemas and report identity
without network access.

### Tool schemas and the first-call HTTP 400

The captured `decide` input has `$schema`, `$defs` and `$ref` at its root, without a literal `type: "object"`. The old Claude builder forwarded that root unchanged. Anthropic's [tool input schema](https://platform.claude.com/docs/en/api/messages/create) uses an object root. This is an offline request defect consistent with the first-call 400; the original run did not retain the error body, so the live cause cannot be confirmed. The first fixture request has nonempty user content, a string system prompt and valid tool names. Its configured `claude-sonnet-5` model and 4,096 output tokens match the [model's documented ID and 128K output limit](https://platform.claude.com/docs/en/models/sonnet-5/overview). The request is below 1 MB. Neither that size nor those fields explains the failure.

`qa/schemas.py` requires an object root for every provider and shows each local definition once. Repeated and recursive references use a typed value with a short instruction to follow the named definition. This avoids expanding the same condition grammar repeatedly in `where` and inventory profile rules. [OpenAI tools explicitly disable strict mode](https://developers.openai.com/api/docs/guides/function-calling#strict-mode), so optional fields and map parameters stay optional. Gemini uses [`parametersJsonSchema`](https://ai.google.dev/api/generate-content#FunctionDeclaration) with a conservative subset of the documented Schema vocabulary. It omits references, map keywords and tuple or exclusive-bound constraints, and retains their meaning in descriptions. Google's JSON Schema field documents `additionalProperties`, so its removal is a compatibility choice, not a claim that every Gemini endpoint rejects it. The OpenAPI-style `parameters` field has a different vocabulary.

These provider schemas guide argument generation. The tool shim still validates arguments against the complete original MCP schema, including recursion and constraints described in prose. Tests build all three providers' exact first payloads, validate their schemas, preserve representative valid MCP arguments and check every public scenario against the first-turn budget. They do not prove live provider acceptance.

Provider HTTP errors keep a generic family/status summary. Only the private JSON run's `provider_error` field receives the HTTP status, error type and message. Type and message are redacted for configured secrets and recognizable key forms, then limited to 300 characters each. Response headers, URLs and unrelated body fields are excluded. The CLI summary and Markdown report omit these diagnostics.

Model defaults and prices were checked on 2026-10-01 against [Anthropic Sonnet 5](https://platform.claude.com/docs/en/models/sonnet-5/overview), [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing), [OpenAI GPT-6.1 Sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol), and [Gemini models and pricing](https://ai.google.dev/gemini-api/docs/pricing). OpenAI uses Responses because GPT-6.1 Sol's Chat Completions endpoint does not support tools. It preserves encrypted reasoning items; Gemini preserves thought signatures between tool turns.

## Inspect reports

The Markdown report summarizes success per family and agent, mean tool calls, nearest-rank p50/p95 latency, misuse counts, and contract gaps with proposed fixes. The JSON includes each family × agent intersection and every run's ordered calls, retries, errors, tokens, wall time, costs, final answer, judge model and result. Tool response bodies are stored once in `tool_responses`; each call's `response_ref` identifies its response. `unknown_facets` contains ids confirmed unknown by API validation. `unadvertised_facets` records attempted ids absent from a fetched vocabulary, which need not be invalid. Local MCP validation failures do not enter API latency percentiles.

Completed, failed and capped runs all enter the success denominator. Expected-match rates include only cases with approved expectations and a parsed judgement. The gap list is sourced catalogue analysis of requirements the current contract cannot express completely. It distinguishes missing task interpretation or quantization-specific fit from unavailable evidence. A 503 alone is not a capability gap.

The committed report is a public fixture run. Live reports can contain prompts, corporate policies, available providers and API replies. Keep future live reports in the private checkout or a private output directory. This PR adds no workflow or schedule.

The sole production exception is a single keyless vocabulary smoke:

```sh
python -m qa.agent_harness --smoke-vocabulary
```

It sends exactly one GET to `https://api.modelspec.dev/v1/vocabulary`, attaches no key, follows no redirects, and stores only counts, snapshot, status and latency. It does not run any scenarios.

## Grow the catalogue past 100

Add one YAML file per scenario under `qa/scenarios`, with `id`, `family`, `persona`, `request`, `constraints`, `expected`, and `rubric`. Use `sources` for provenance and `prompt` for F2. Use `gaps` only for a demonstrated contract limitation; each entry needs `reason`, `suggested_fix`, and `source`.

Copy established expected rows verbatim from `tests/recall/expected.yaml` and set `expected_source: tests/recall/expected.yaml#Qxx`. Keep `expected: null` for every other scenario. A shortlist returned by the API or a judge is not independent ground truth.

Add at least 26 variants across real personas and constraints to reach 100. Useful axes include ambiguous and complete hardware descriptions, exhausted subscription plans, approved-provider intersections, contradictory policy requirements, prompt languages, output formats, workloads and no-feasible budgets. Preserve meaningful differences between requests. For a new variant without an existing recall or template recipe, add `fixture_spec` containing a valid structured Spec for the recorder. This field never enters agent context and is not an expected answer. Add successful, failing and abstaining replay cases, regenerate fixtures, and run the offline tests. Avoid real private prompts in this public catalogue.

MODEL-291 defaults to the generated compact agent guide and captured MCP definitions.
The full OpenAPI stays at https://modelspec.dev/openapi.yaml. Use
`--control-full-spec` to inject the current full document for comparison. Use
`--interface http` for thin HTTP operation adapters with unconstrained object
arguments; the API validates those bodies, and the adapter does not apply MCP
Zod field stripping. The MCP arm uses the captured input schemas and stripping
rules. Both arms use the existing HTTP execution shim, not a live MCP transport.
Reports record interface, control_full_spec and guide_version. Dry runs replay
scripted turns and do not measure a live agent's reaction to either prompt arm.

## Subscription CLI runner (MODEL-301)

`qa.tui_harness` runs the subscription CLIs in separate local Docker images. It
shares scenarios and scoring with the API harness. Agents connect to
`https://api.modelspec.dev/mcp`; cross-family judges have no ModelSpec connection.
Every scenario and judge needs a passing doctor receipt for its built image.

The TUI runner uses subscription login only. Host vendor API keys are never
inherited. The command builder, image inspection and Linux entrypoint refuse
vendor API-key or token environment variables, including empty variables. Native
status must report subscription authentication before any model prompt. Claude's
stream `apiKeySource` must also attest subscription authentication. The API runner
described earlier in this README is a separate executable.

### Build the images locally

```sh
python -m qa.tui_harness build-images
# Build one image:
python -m qa.tui_harness build-images --cli codex
```

The exact versions are in `qa/tui_config.yaml`:

| CLI | Version | Official installation |
| --- | --- | --- |
| Claude Code | 2.1.289 | `@anthropic-ai/claude-code` |
| Codex | 0.160.0 | `@openai/codex`; versions below 0.160.0 are refused |
| Gemini CLI | 0.62.0 | `@google/gemini-cli` |
| Grok Build | 1.0.46 | xAI's versioned `https://x.ai/cli/grok-<version>-linux-<architecture>.gz` artifact |

`qa/docker/Dockerfile` has one target per CLI over a shared, digest-pinned slim
Node 22.20.0 base with Python, git, bubblewrap and ripgrep. The build context
includes only the Dockerfile and fixed container helpers/settings. Builds contain
no login state. The image user has the host user's numeric UID so private
workspaces remain readable without widening their permissions. Images stay local
as `modelspec-harness-<cli>:<version>` and are never pushed.

The builder verifies native `--version` output against the configured pin.
Doctor measures it again, records the immutable image ID, and binds its receipt to
that ID, the UID, profile, MCP endpoint and adapter/build sources. Rebuilding an
image or changing the adapter invalidates the receipt. Native binaries installed
on the Mac and `TUI_*_BIN` overrides are no longer used.

### Login manually

Each CLI's HOME is `/home/agent`, backed only by its named volume
`modelspec-harness-<cli>-home`. The native CLI owns all credentials and refreshes.
The harness never inspects, reads, copies or prints volume contents. Status and
inventory come from native CLI commands, with only method, enablement and name
summaries retained. Linux uses file-based login storage; Codex explicitly selects
its file store.

Run these commands yourself from this worktree:

| CLI | Exact harness command | Container login method |
| --- | --- | --- |
| Claude Pro/Max | `python -m qa.tui_harness login --cli claude` | URL: `claude auth login --claudeai`; open the displayed URL on the Mac and complete the CLI's code flow |
| ChatGPT | `python -m qa.tui_harness login --cli codex` | Device code: `codex -c 'cli_auth_credentials_store="file"' login --device-auth` |
| Google AI account | `python -m qa.tui_harness login --cli gemini` | URL: `gemini` with `NO_BROWSER=true`; choose Google sign-in, open its displayed URL on the Mac, return the requested code, then exit |
| SuperGrok/X | `python -m qa.tui_harness login --cli grok` | Device code: `grok login --device-auth` |

Login replaces the harness process with `docker run -it --rm`, inherits terminal
stdio, and mounts only that CLI's HOME volume. It captures no output and needs no
ModelSpec key. Codex device login may need enabling in ChatGPT security settings.
[OpenAI's authentication docs](https://developers.openai.com/codex/auth/) and
[xAI's CLI reference](https://docs.x.ai/build/cli/reference) describe the device
flows. [Claude's CLI reference](https://code.claude.com/docs/en/cli-reference) and
[Gemini's authentication guide](https://geminicli.com/docs/get-started/authentication/)
cover the subscription URL flows. Doctor never starts login or logout.

### Container boundary and doctor

Every native command gets a fresh `docker run --rm`. It sees its HOME volume and
one private temporary workspace beneath `--out`, mounted at `/work`. It sees no
host HOME, repository, configuration, Docker socket or shell environment. The
container runs without added capabilities or host networking; ordinary outbound
network access is allowed. Only `TERM`, `LANG` and `MODELSPEC_MCP_URL` are passed.
The configured ModelSpec key is passed by environment name only when an agent
needs it, never in Docker argv, image layers, login, doctor controls or judge
containers. Other CLI controls are fixed inside the image. Docker client activity
files use a temporary client configuration connected to the existing local Unix
socket, without copying the host's Docker configuration.

Use the same private `--out` for doctor and subsequent runs:

```sh
python -m qa.tui_harness doctor --cli codex --out /tmp/modelspec-tui
python -m qa.tui_harness doctor --cli claude --out /tmp/modelspec-tui
python -m qa.tui_harness --smoke --cli codex --max-runs-per-cli 1 --out /tmp/modelspec-tui
```

Doctor checks native subscription status before inventory or model controls.
Claude uses `auth status`, Codex uses `login status`, and Grok uses ACP auth-method
initialization and `models`. Gemini first asks its installed CLI settings loader
for `selectedType` and permits only `oauth-personal`; then ACP initialize and
session/new verify cached Google authentication without a model turn. API-key,
Vertex, third-party and unknown methods refuse certification. Account identifiers
and raw status output never enter reports.

Doctor retains the paired positive/isolated canary checks inside the container.
Both use the same image, volume and mounted workspace. The positive instruction
must affect the answer; the isolated answer must be exactly `OK`, without canary
hooks, servers or instructions. Claude must also prove positive skill, hook and
MCP discovery. Grok's positive control disables the folder-trust gate for that
process, without using the persistent `--trust` grant. Its isolated control
enables the gate, uses a generated gitignore for instructions, and requires
native inventory to show no active skills or hooks. Existing trust grants that
activate customizations cause refusal. A vacuous positive control fails.

| CLI | Effective inventory required for certification |
| --- | --- |
| Claude | Stream init lists skills, plugins, MCP servers and exposed tools; hook events are rejected. A standalone plugin listing is preliminary only. |
| Codex | Native app-server `skills/list` discovery and effective disabling, `mcp list --json`, `plugin list --json`, `features list`, and `debug prompt-input`. Enabled plugins block certification even if `plugins={}` was requested. Names, enabled state and account scope are recorded when the CLI reports that scope. Account-level apps may reappear after login. |
| Gemini | Native MCP, extension and skill listings plus its installed settings loader's effective enablement. Root-owned settings disable skills, hooks and context files without overriding the stored auth type. Five exact ModelSpec MCP lifecycle messages are recognized; unknown diagnostics still fail. |
| Grok | `inspect --json` must show no active instruction files, user skills, plugins or hooks, and exactly the configured ModelSpec MCP servers. |

Receipts use schema 4 under `<out>/.tui-state/<cli>/tui-isolation.json`. Earlier
native-home receipts cannot authorize Docker runs. A failed or interrupted repeat
doctor revokes the previous receipt. Each ordinary launch rechecks authentication
and native inventory; invalid evidence revokes eligibility. `--force` overrides
quiet hours only, never evidence or authentication.

Unauthenticated inventories can be inspected without touching login volumes:

```sh
python -m qa.tui_harness inventory --out /tmp/modelspec-tui-inventory
```

This action uses temporary container HOME filesystems, runs no login or model
prompt, and never certifies a CLI. The local Linux/arm64 builds and native version,
help and inventory commands were checked on 2026-10-04. Subscription login,
authenticated account-plugin inventories and model canaries still need Jamie's
manual login and doctor. Unauthenticated inventory success is preliminary.

### Reports and pacing

Doctor and run require private output outside this public checkout and its other
worktrees. Symlink output files are refused. Reports retain measurements, method
summaries and isolation evidence. Raw transcripts are not saved. Dry-run prints
Docker command previews without consulting Docker or running CLIs. Doctor runs
its model controls but no scenarios or cross-family judges.

```sh
python -m qa.tui_harness --dry-run --scenario budget-approved --out /tmp/tui-preview
python -m qa.tui_harness --smoke --max-runs-per-cli 1 --quiet-hours --out /tmp/modelspec-tui
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest tests/test_tui_harness.py -q
```

Execution is serial. Quotas count scenario and judge starts, including failures.
Doctor controls are separate. Vendor usage limits stop further starts for that
CLI without retries. `--quiet-hours` refuses starts between 08:00 and 21:59 local;
`--force` overrides only that guard. Timeouts remove the named container so a
killed Docker client cannot leave an agent running.

Offline tests use fake Docker runners for command construction, mounts, the
allowlist, vendor-key and auth-method refusals, uncaptured login exec, image-bound
receipts, doctor controls, pacing and cross-family judging. Every existing
credential read/copy/move guard remains and also covers volume paths and
`/home/agent`. Dummy credential sentinels survive doctor and launch unchanged.

### Migrate from the macOS homes

The `setup` action and `~/.modelspec-harness` homes are retired. Build the images
and complete fresh subscription login inside each volume. No login is copied
from the Mac. Jamie can delete `~/.modelspec-harness` himself when he no longer
needs it. This change does not delete or alter that folder.

## Local scheduled jobs (MODEL-309)

Agent scenarios, cold-browser UX tasks and AEO visibility now run locally through
the Docker subscription CLIs. Perplexity keeps its existing AEO API adapter,
1Password reference, prices, retries and monthly spend cap. The manual speed
probe is unchanged. Subscription logins never enter GitHub Actions.

The local entry points are:

```sh
python -m qa.subscription_jobs scenarios --data-repo ~/dev/modelspec-data
python -m qa.subscription_jobs ux --data-repo ~/dev/modelspec-data
python -m qa.subscription_jobs aeo --business-repo ~/dev/modelspec-business
```

Add `--dry-run` to any command. Previews make no model, browser, search,
credential or PR call and write only beneath `<state-dir>/dry-run`. `--state-dir`
defaults to `~/Library/Application Support/ModelSpec/subscription-jobs`; use that
same directory for the CLI doctor's `--out`. For validation in this worktree,
choose a temporary private state directory instead of the default. Dry runs can
read the old business config before the private patch is applied; live AEO
requires the migrated subscription config.

Scheduled runs always enforce quiet hours. They refuse starts between 08:00 and
22:00 local. Every required CLI and judge must have a passing receipt less than
30 days old, bound to its immutable image, UID, model profile and current
adapter/build sources. All receipts and native subscription statuses are checked
before the first task, and every launch rechecks status and inventory. Missing
or changed evidence refuses the job. Vendor API-key/token environment variables,
including empty variables, refuse all jobs and dry runs. There is no API fallback
for the four subscription vendors. No job starts login or refreshes doctor for you.

Execution is serial and uses the existing quota and usage-limit checks. Job
quotas default to 400 CLI starts per family for all 74 scenarios, 40 for the UX
jobs and 64 for AEO. Scenario quotas include cross-family judges. These caps cover
the full catalogue; `--max-runs-per-cli` can lower them for manual trials. A
vendor limit stops that CLI without a retry. Skipped and unjudged scenario rows
remain in the denominator. A shared process lock prevents local jobs from
running together. launchd does not load overlapping copies of a job.

Scenarios keep `reports/agent-scenarios/<UTC-day>.json` and `.md` in a fresh
modelspec-data worktree. They use the same catalogue, independent recall scoring,
rubric, response deduplication and aggregate fields as the API harness. Codex
results keep the `openai` label; actual CLI and model identities are recorded.
Unknown tool latency stays unknown. API spend is zero; native token-equivalent
costs are separate. Reports identify the change in transport.

UX keeps the private twenty-task catalogue, DOM collector, judge rubric and
aggregation functions. Default visitors remain OpenAI and Grok, now Codex and
Grok CLIs, with a separate Claude CLI judge. Only UX images carry pinned official
`@playwright/mcp@0.0.83` and that package's Chromium build. Each task gets a new
headless context, no saved cookies or previous browser state. A wrapper exposes
ordinary browser actions and collects screenshots, DOM checks and geometry
independently. It excludes JavaScript, file and extraction tools, restricts
keyboard tasks to keyboard navigation, blocks human verification and other
writes, and refuses unavailable human-status evidence. Visitor claims cannot
satisfy DOM checks. Judges receive the unchanged private rubric, page states and
attached screenshots. Reports keep schema version 1 at
`reports/ux/<UTC-day>.json` and `.md`, with private evidence beneath
`<day>/<run-id>/`. Findings remain for human triage.

AEO uses Claude WebSearch/WebFetch, Codex live web search, Gemini's
`google_web_search` grounding and Grok web/X search. A search counts only when
the CLI transcript records a successful native search tool, not when the answer
claims it searched. Four vendor API references are removed from the business
config. Subscription models match the shared doctor-certified profiles; the
old low-cost API profiles are not silently used as fallbacks. Perplexity alone
calls its unchanged API adapter. Dated `runs.jsonl`, `engines.json`,
`summary.json`, `report.md`, `raw/` and `BASELINE` retain their format. The surface
field records subscription versus API; comparing the old baseline also compares
transport and model profiles.

Every live job fetches the private repository's main branch, creates a new
worktree and branch, stages only the existing report paths, pushes that branch
and opens a private PR. It never changes the main checkout's branch. A failed
publication retains its worktree and prints its path for recovery. The shell
wrapper used by schedules also runs the merged public engine from a fresh
detached worktree. No reports or private task definitions enter this public tree.

### First manual run and schedules

Build the ordinary images, then the two browser images. Login remains Jamie's
manual step, using the commands earlier in this README. Authentication volumes
are shared between each CLI's ordinary and UX variants; receipts are separate.

```sh
python -m qa.tui_harness build-images
python -m qa.tui_harness build-images --ux-image --cli codex --cli grok
# After Jamie logs in, certify all four ordinary images:
python -m qa.tui_harness doctor --cli claude --out "$STATE"
python -m qa.tui_harness doctor --cli codex --out "$STATE"
python -m qa.tui_harness doctor --cli gemini --out "$STATE"
python -m qa.tui_harness doctor --cli grok --out "$STATE"
# Then certify the visitor images:
python -m qa.tui_harness doctor --ux-image --cli codex --out "$STATE"
python -m qa.tui_harness doctor --ux-image --cli grok --out "$STATE"
```

Set `STATE` to the private state directory chosen above. Doctor makes model
canary calls; only Jamie or an authorized later session runs these commands.
Perform the first manual run of each job before loading its schedule. The
private business and data patches must be applied first for live jobs.

`qa/launchd/` provides these calendar schedules in the Mac's local timezone:

| Job | Calendar |
| --- | --- |
| Agent scenarios | Tuesday 03:23 |
| UX visitors | Wednesday 04:37 |
| AEO | 1st of each month, 06:00 |

Tuesday and Wednesday preserve the old 07:23 and 08:37 UTC overnight slots in
America/New_York daylight time. launchd keeps those local hours across daylight
saving changes. `StartCalendarInterval` fires a missed run on wake; the job's
quiet-hours guard still applies. No template uses `RunAtLoad` or `KeepAlive`.
The AEO label replaces the previous `dev.modelspec.aeo-visibility` template;
replacing its file does not reload an already-loaded job.

After merging, render/install against the stable public main checkout:

```sh
python -m qa.install_subscription_jobs --repo ~/dev/modelspec --dry-run
python -m qa.install_subscription_jobs --repo ~/dev/modelspec
```

The installer only writes the three plist files and log directories. It never
calls `launchctl`, loads jobs, or runs a task. Jamie or the orchestrator loads
them after each first successful manual run. Keep the stable public checkout's
venv installed with the existing harness dependencies.

Offline coverage:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest \
  tests/test_subscription_jobs.py tests/test_tui_harness.py tests/test_aeo_visibility.py -q
```

The UX contract integration checks use the private helper files read-only on
Jamie's Mac and synthetic tasks. Other checks run without a private checkout.
The official MCP package's exported `createConnection` and context getter are
used by the wrapper; installation and transport documentation are in the
[official Playwright MCP repository](https://github.com/microsoft/playwright-mcp).
