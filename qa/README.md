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

`qa.tui_harness` uses headless agent CLIs with subscription logins that Jamie
creates in dedicated test homes. It shares the catalogue, compact guide, judge
rubric, recall matching and aggregation with the API runner. Scenarios use the
remote Streamable HTTP MCP at `https://api.modelspec.dev/mcp`. Each scenario and
judge gets a fresh temporary workspace. Judges receive the rubric and tool
evidence, with no ModelSpec connection or built-in tools.

The harness never opens, copies or creates credentials. CLI processes handle
login and token refresh themselves. Children receive a small environment
allowlist, a dedicated `HOME`, dedicated XDG directories and the CLI's home
override. Vendor API keys, agent customization variables and shell startup
overrides are excluded. Claude must attest subscription authentication through
init `apiKeySource`, accepting `none`, `subscription` or `oauth`. Missing or
API-key sources refuse the result and revoke eligibility.

Decision tools separately use the ModelSpec connection credential described in
[`mcp/README.md`](../mcp/README.md). Native MCP configurations reference the
configured `MODELSPEC_*` variable; its value never enters argv or a config file.
All `MODELSPEC_*` environment values are redacted in reports. Without a ModelSpec
credential, decision calls may return `missing_api_key`.

### Home overrides and evidence, 2026-10-03

No CLI is eligible by default. The earlier claim that Claude's hook canary
passed is withdrawn. Its probes were in an ancestor directory that Claude did
not search for project hooks or skills, and it had no positive control. That
run did not prove hook or skill isolation. This follow-up used help commands
with empty temporary homes, installed source/bundled docs and official docs.
It made no signed-in CLI calls and opened no existing credential files.

| CLI inspected | Dedicated home mechanism | macOS storage caveat |
| --- | --- | --- |
| Claude Code 2.1.283 | `HOME=<home>` and `CLAUDE_CONFIG_DIR=<home>/.claude` | The documented Keychain item is keyed to the config directory. A separate login is required. |
| Codex 0.160.0 adapter from the original PR | `HOME=<home>` and `CODEX_HOME=<home>/.codex` | Codex supports file and OS credential-store modes. A home override alone does not establish whether a store item is shared. Shared subscription login is acceptable. |
| Gemini CLI 0.60.0 | `HOME=<home>` and `GEMINI_CLI_HOME=<home>`; Gemini appends `.gemini` | Installed OAuth storage uses service `gemini-cli-oauth` and account `main-account`, so homes can share a Keychain login. File fallback follows the dedicated home. |
| Grok Build 1.0.46 | `HOME=<home>` and `GROK_HOME=<home>/.grok` | Bundled authentication docs describe file storage in the relocated Grok home. No shared Keychain login was established for this version. |

Sources: [Claude environment](https://code.claude.com/docs/en/env-vars) and
[authentication](https://code.claude.com/docs/en/authentication),
[Codex config/state locations](https://developers.openai.com/codex/config-advanced/)
and [authentication/storage modes](https://developers.openai.com/codex/auth/),
[Gemini home configuration](https://geminicli.com/docs/reference/configuration/),
[Gemini enterprise isolation](https://geminicli.com/docs/cli/enterprise/),
[Grok home/settings reference](https://docs.x.ai/build/settings/reference).
Gemini 0.60's installed `bundle/chunk-M6NSK26M.js` contains `homedir()` at
251981, `Storage.getGlobalGeminiDir()` at 253138 and
`OAuthCredentialStorage` at 278715. Grok 1.0.46's binary embeds
`02-authentication.md` and `12-project-rules.md`. These are source inspections,
not observations of saved account data.

`HOME` also contains secondary discovery paths, including Codex and Grok's
`.agents` skills, Grok's Claude/Cursor compatibility paths and Gemini's `.env`
lookup. The environment redirects those known roots. This source review does
not claim to trace every filesystem read a signed-in CLI could make. Shared OS
credential stores are permitted; the harness never queries them.

Binaries resolve through `shutil.which`. The default `codex` prefers
`/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex` when present.
This machine's app binary reports `0.160.0`; its PATH binary reports `0.153.4`
and is below the configured minimum. `TUI_CLAUDE_BIN`, `TUI_CODEX_BIN`,
`TUI_GEMINI_BIN` and `TUI_GROK_BIN` override selection, including that app default.
An explicit executable path in the profile also takes precedence over the default.
Use a native CLI executable. The inspected local Gemini wrapper looks for npm under
`$HOME/.nvm`, so it cannot start after `HOME` changes. Set `TUI_GEMINI_BIN` to the
npm installation's `bin/gemini` or `bundle/gemini.js` and keep Node on `PATH`.
There are no machine-specific binary paths in `qa/tui_config.yaml`.

### Setup, manual login and doctor

Each profile has `harness_home`, defaulting to
`~/.modelspec-harness/<cli>/home`, and its native `config_dir` name. Setup
requires an empty private directory. It creates only the native ModelSpec MCP
configuration inside that home, plus a setup receipt beside it. Repeating setup
preserves state created by the CLI. It never imports a real user's config or
login. Setup and doctor run `<resolved-bin> --version` under the harness environment
with the dedicated home as cwd. The setup receipt records `path`, the reported
`version`, `size` in bytes and `mtime` in nanoseconds. Setup prints the version.
Profiles may set a numeric `min_version`; Codex defaults to `"0.160"` and refuses
older builds. Gemini also binds the resolved Node executable and its version,
the native bundle entry and a digest of the bundle's JavaScript file metadata.
The harness does not run login during setup. Jamie runs the printed short command.

```sh
python -m qa.tui_harness setup --cli codex
python -m qa.tui_harness login --cli codex
python -m qa.tui_harness doctor --cli codex --out /tmp/tui-codex-doctor
```

The four login commands are below. A custom configuration adds
`--config /absolute/path/to/tui_config.yaml`; setup prints that option when needed.
Login builds the same environment and cwd as setup, adds `TERM`, then replaces
the harness process with the CLI using inherited stdin, stdout and stderr.
The harness never captures, logs or redacts login output. Claude runs
`auth login --claudeai`; Codex and Grok run `login`. Gemini opens its interactive
CLI; choose "Sign in with Google", then exit.

```sh
python -m qa.tui_harness login --cli claude
python -m qa.tui_harness login --cli codex
python -m qa.tui_harness login --cli gemini
python -m qa.tui_harness login --cli grok
```

Doctor runs four tiny probes: a relaxed positive control and an isolated run
for cwd, then the same pair for the config home. It plants instructions,
`SKILL.md`, a SessionStart hook and a harmless local stdio MCP server at native
discovery locations. Claude uses `CLAUDE.md`, `.claude/skills`,
`.claude/settings.json` and `.mcp.json` in cwd, and their config-directory
counterparts. Its cwd control relies on native `.mcp.json` discovery with
`enableAllProjectMcpServers` in project settings. It never supplies that file
through `--mcp-config` in the relaxed control. Claude's config-home control does
not require MCP startup because `.mcp.json` is a project discovery file; its
instruction, skill and hook controls still must fire. The receipt states this scope.
Codex uses `AGENTS.md`, cwd `.agents/skills`, `CODEX_HOME/skills`, native
`hooks.json` and MCP config tables. Gemini uses `GEMINI.md`, `.gemini/skills`
and `.gemini/settings.json`. Grok uses `AGENTS.md`, `.grok/skills`,
`.grok/hooks/*.json` and `.grok/config.toml`. Home-level counterparts live in
each CLI's relocated config directory. Existing config files are temporarily
renamed and restored without reading their contents. Doctor serializes writes
to each home and removes its probes and side effects on exit. An existing
`tui-doctor.lock` refuses doctor with its exact `rmdir` command. Clear it only
after confirming that no doctor is running.

Eligibility requires both a native inventory and a passing behavioural canary
with a positive control. Every CLI must emit the planted instruction marker in
both relaxed answers and answer exactly `OK` in both isolated runs. The isolated
runs must show no marker, hook event or canary filesystem effect. Claude also
requires its positive skill inventory and hook effects, plus native cwd MCP startup.
Other CLIs record those supplementary observations but require the instruction
control and their separate inventories. They do not need Claude's init keys.

| CLI | Inventory source under the exact launch environment, home and cwd |
| --- | --- |
| Claude | Its native stream init must include list-valued `skills`, `plugins`, `mcp_servers` and `tools`. Non-builtin plugins, skills and hook events refuse launch. Scenario init must attest a connected ModelSpec server and subscription authentication. |
| Codex | The local app-server `skills/list` RPC discovers skills without a model turn. Native `skills.config` overrides disable each non-system skill by its reported path, then a second RPC verifies no enabled user, repo or admin skill. The same override reaches `exec`. `mcp list --json`, `plugin list --json`, `features list` and `debug prompt-input` verify MCP names, plugins, disabled hooks and absent skill instructions using the shared config overrides. |
| Gemini | `mcp list`, `extensions list --output-format json` and `skills list`. The installed bundle's exported `loadSettings().merged`, called with the bound Node, must report global skills and hooks disabled and no settings-load errors. The receipt distinguishes discovered skills from globally disabled effective skills. |
| Grok | `inspect --json` must report list-valued `skills`, `plugins`, `hooks`, `projectInstructions` and `mcpServers` for the exact cwd. Enabled user skills, plugins, hooks, config warnings and MCP config problems refuse launch. Built-in skills may remain. |

No adapter uses the inventory-free exception: all four have an inventory source.
For the three separate sources, doctor checks the normal ModelSpec configuration
before planting probes, then each isolated probe checks its empty MCP allowlist.
Ordinary starts repeat native inventory checks with only ModelSpec allowed for
scenarios and no MCP server allowed for judges. Disabled entries can appear in
discovery output; they must be disabled in the CLI's reported effective state.
Inventory observations remain separate from the vendor's model stream. They are
not fabricated init fields. Raw listing output and prompt previews stay in memory;
receipts retain command labels, observed names and enablement evidence.

Missing or unknown inventory formats, a positive control that does not fire,
failed launches, limits and ambiguous evidence produce `unproven`. Invalid runtime
evidence revokes eligibility. In this pass, command discovery used help, official
docs and package/source inspection; version checks used empty temporary homes.
No signed-in run certifies any CLI here. Gemini 0.60's installed context filename
setter still retains default `GEMINI.md` discovery, and Grok's home override alone
does not exclude native rules or hooks. A failing canary therefore remains
`unproven` even when its independent inventory is complete.

Sources for the inventory interfaces: [Codex app-server skills/list](https://developers.openai.com/codex/app-server/),
[Grok inspect](https://docs.x.ai/build/cli/reference), and the installed Gemini
0.60 bundle's native listing commands and exported `loadSettings` implementation.

A successful doctor receipt is bound to the resolved executable's build
identity including every recorded version and file attribute, profile, home,
MCP settings and adapter source hashes. Setup and doctor receipts use schema 2;
older doctor receipts cannot enable launch. Existing schema 1 setup markers can
be upgraded by repeating setup without reading or replacing CLI state. Ordinary
runs reuse the canary result, so positive controls are paid only during doctor for a new
CLI build or changed adapter/configuration, or an explicit repeat doctor.
Missing, stale, incomplete or failed receipts refuse launch. YAML eligibility
flags and `--force` cannot enable a CLI. `--verify-isolation --cli X` is retained
as an alias for doctor. Doctor calls no ModelSpec scenario or judge; its local
MCP probe is separate from the ModelSpec service. Native listing commands may
check configured MCP connectivity; doctor runs no scenario or judge.

### Commands and reports

Run and doctor require a private `--out` directory. The runner rejects this
public checkout, other worktrees sharing its git directory, symlink aliases and
symlink report files. Raw transcripts stay in memory. JSON contains final
answers and ordered tool calls with deduplicated results; Markdown contains
aggregates and statuses. Models, effort and judge routes live in
`qa/tui_config.yaml`; `--judge claude=codex` overrides one cross-family route.

```sh
python -m qa.tui_harness --dry-run --scenario budget-approved --out /tmp/tui-preview
python -m qa.tui_harness --smoke --max-runs-per-cli 1 --quiet-hours --out /tmp/tui-smoke
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest tests/test_tui_harness.py -q
```

Dry-run starts no CLI or network calls and reports unproven adapters without
runnable commands. `--smoke` fixes the scenario to `budget-approved` and quota
to one, and requires eligible selected CLIs and cross-family judges before any
scenario starts. There are no eligible defaults until manual login and doctor.

The runner is serial. `--max-runs-per-cli` counts scenario and judge starts
together, including failed starts. Doctor's four control calls are separate and
reported individually with status, timing, usage and exposed cost. A vendor
usage-limit error stops that CLI for both roles and stops doctor immediately;
other families can continue. Generic exit code 1 and ModelSpec rate limits do
not establish a vendor subscription limit. There are no harness retries.
`--quiet-hours` refuses new starts from 08:00 through 21:59 local; `--force`
overrides only that guard. Dry-run can run at any time.

Reports retain the API harness's aggregation and evidence shape and add
`isolation`, `cli_invocations`, `stopped_clis` and `per_cli`. Missing measurements
are null. Tool latency is not inferred from whole-run wall time. CLI token cost
does not establish money charged. Missing judgements, unsupported, capped and
skipped rows stay explicit in aggregate denominators.

`qa/fixtures/tui-streams.json` contains synthetic protocol samples, with no live
transcript or real scenario answer. Offline tests cover every credential read,
copy and move entry point, plant dummy credential files through setup, doctor and
launch, reject credential-path literals in `qa/tui_*.py`, test
positive controls and incomplete inventories, preserve configuration without
reads, reject stale receipts, and exercise setup, doctor and a full `main` run
with faked launches. They do not certify a signed-in vendor session.
