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

`qa.tui_harness` uses headless subscription CLIs and Jamie's dedicated login
profiles. It shares the catalogue and scoring code with the API harness.
Scenarios use `https://api.modelspec.dev/mcp`; judges have no ModelSpec connection.
Every ordinary launch requires a passing doctor receipt for that CLI build.

The harness never opens, copies, moves or creates credentials. Only native CLI
processes handle saved logins and token refresh. The environment allowlist
excludes vendor API keys, agent customization variables and shell startup
variables. ModelSpec configuration contains only an environment reference to
`MODELSPEC_API_KEY`, and reports redact `MODELSPEC_*` values.

### HOME and native configuration roots

Children inherit `HOME` unchanged on every platform. On macOS, redirecting HOME
can make the Security framework look for a different Keychain. Login and doctor
refuse to start Claude, Codex or Gemini with a different HOME. Grok 1.0.46's
bundled authentication docs describe file storage; it also keeps HOME unchanged.
Dedicated XDG roots remain separate from the OS Keychain. TMPDIR, TMP and TEMP
point to a private sibling of the dedicated home, so Codex's helper directory
is outside its temporary root.

| CLI | Dedicated configuration root | Source audit and remaining HOME discovery |
| --- | --- | --- |
| Claude 2.1.283 | `CLAUDE_CONFIG_DIR=<home>/.claude` | Official docs relocate settings, history and plugins. The Keychain item is keyed by this directory. Instruction suppression, empty setting sources, disabled commands/hooks and strict MCP configuration must exclude real `~/.claude/CLAUDE.md`, skills, settings hooks and global MCP state. The native stream init must attest empty skills/plugins and exactly the permitted MCP servers/tools. |
| Codex 0.160.0 | `CODEX_HOME=<home>/.codex` | Native config and AGENTS.md follow CODEX_HOME. Real `~/.agents/skills` still appears in skills/list. The harness disables each non-system skill by its native path, repeats discovery, and checks the effective prompt. App plugin discovery is independent; an enabled plugin listing prevents certification even with `plugins={}`. |
| Gemini 0.62.0 | `GEMINI_CLI_HOME=<home>`; Gemini appends `.gemini` | The installed `homedir()` helper relocates global GEMINI.md, settings and skill roots. Native dotenv discovery walks cwd ancestors; an empty private cwd `.env` stops that search, including version checks and manual login. Existing nonempty or symlinked barriers refuse startup without being opened. `SandboxPolicyManager` still uses OS HOME for `.gemini/policies/sandbox.toml`. The native settings probe must attest that this fallback file is absent, otherwise Gemini is unsupported. The context filename setter still retains default cwd GEMINI.md discovery, which the cwd canary tests. |
| Grok 1.0.46 | `GROK_HOME=<home>/.grok` | Native config follows GROK_HOME. Compatibility environment flags suppress Claude/Cursor instruction, skill, hook and MCP consumers. Native `.agents` skill and Claude plugin discovery can still use real HOME. `inspect --json` must report no active user skills/plugins/hooks/instruction files and exactly the allowed MCP servers, otherwise Grok is unsupported. |

These are source and native-inventory checks, not a claim that the harness traces
every filesystem read. The real home's files are never changed. The natural
canary catalogue uses only path metadata, including existing skill paths and
instruction/settings locations. It never opens the global CLI state file, which
may mix customization and authentication. Metadata changes invalidate receipts.

Sources: [Claude environment](https://code.claude.com/docs/en/env-vars),
[Claude settings](https://code.claude.com/docs/en/settings),
[Codex skills](https://developers.openai.com/codex/skills/),
[Codex configuration](https://developers.openai.com/codex/config-advanced/),
[Gemini configuration](https://geminicli.com/docs/reference/configuration/), and
[Grok inspect](https://docs.x.ai/build/cli/reference).
Gemini's installed active entry imports `gemini-J6X2T2ZI.js`,
`chunk-3VMO3WD7.js` and `chunk-MLY4WQFO.js`. The settings-module probe follows
reachable imports, excluding leftover chunks from older installations. Grok's
binary embeds its authentication, discovery and configuration documentation.

### Setup, login and doctor

Each profile defaults to `~/.modelspec-harness/<cli>/home`. Setup requires an
empty private directory, creates native ModelSpec MCP configuration and a setup
receipt, then measures the binary under the harness environment. Repeating setup
preserves native state. It never imports a real user's configuration or login.

```sh
python -m qa.tui_harness setup --cli codex
python -m qa.tui_harness login --cli codex
python -m qa.tui_harness doctor --cli codex --out /tmp/tui-codex-doctor
```

Jamie runs login manually. Claude uses `auth login --claudeai`; Codex and Grok
use `login`. Gemini starts its interactive CLI; select Google sign-in, then
exit. Login inherits terminal I/O and is never captured or logged. The harness
never runs login or logout during doctor.

Executables resolve through `shutil.which`. Codex prefers the ChatGPT app build
when the profile says `codex`. `TUI_CLAUDE_BIN`, `TUI_CODEX_BIN`, `TUI_GEMINI_BIN`
and `TUI_GROK_BIN` override the configured binary. Gemini's profile persists
this machine's native npm bundle and Node 20.19.3 paths. `TUI_GEMINI_NODE` can
override Node; its directory is prepended to the child PATH. Gemini identity
includes the resolved Node, bundle entry and JavaScript source metadata.

Doctor checks authentication before version, inventory or model canaries. It
records only `logged_in`, `auth_method`, status checks and a safe reason. Account
identifiers such as emails and organization IDs never enter the receipt. Claude
uses `auth status`; Codex uses `login status`. Gemini uses native ACP initialize
and session/new, with no model turn and browser login suppressed. Its known
authenticated `UNSUPPORTED_CLIENT` refusal is recorded separately from missing
login. Grok uses ACP initialization for the native cached auth method and an
authenticated `models` listing. Unknown status formats stop doctor.

Doctor then verifies the effective native inventory and runs two tiny cwd
canaries, a relaxed positive control and an isolated run. It plants an instruction,
SKILL.md, SessionStart hook and local stdio MCP server only in a private cwd.
Claude requires instruction, skill, hook and native project MCP positive controls.
The others require the instruction control and their separate native inventories.
The isolated answer must be exactly OK, with no marker, hook, canary side effect
or unauthorized tool. Doctor never plants a skill in the dedicated configuration
home and expects it to disappear. Existing real-home customization is the natural
canary for user-level isolation. Inventory failures stop before model calls.

Gemini 0.62 rejects user-owned system-settings files. The adapter instead
supplies its policy in the dedicated user settings layer, restoring the original
settings by rename without reading them. Cwd canary settings remain in place.
A lock serializes this temporary configuration. Each home's doctor lock also
prevents overlapping doctor writes; a stale lock gives its exact cleanup command.

| CLI | Inventory evidence |
| --- | --- |
| Claude | Native stream init with list-valued skills, plugins, MCP servers and tools, plus hook events and subscription authentication. |
| Codex | app-server skills/list before and after native skill disabling; mcp list --json; plugin list --json; features list; debug prompt-input. Only known skills/changed and remoteControl/status/changed notifications are accepted. |
| Gemini | mcp list, extensions list --output-format json and skills list. Exact listing grammars are accepted on stdout or stderr. Unknown lines, diagnostics, inconsistent status glyphs, duplicates and malformed JSON fail closed. loadSettings().merged must report disabled skills/hooks, no settings errors, the dedicated user settings path and no real-home sandbox policy. |
| Grok | inspect --json with list-valued skills, plugins, hooks, projectInstructions and mcpServers. Disabled compatibility entries may appear; active user entries, ambiguous configuration and incorrect MCP endpoints refuse certification. |

Raw status/listing output and prompt previews stay in memory. Inventories retain
command labels, names and enablement evidence. They are separate from model
stream init, not fabricated init fields. A failed or interrupted repeat doctor
revokes the previous receipt. Doctor receipts use schema 3; setup receipts remain
schema 2. Existing doctor receipts cannot authorize a launch. The binding includes
binary/runtime identity, configuration, adapter sources, HOME and natural-canary
metadata. No YAML flag or `--force` can bypass the evidence gate.

### Current live observations, 2026-10-03

The fourth pass observed Gemini 0.62.0, despite the earlier report naming 0.60.
Its MCP listing and extension JSON use stderr. Its skills command can also emit
MCP lifecycle messages outside the listing grammar; those are not silently
accepted. Code Assist rejected the cached OAuth session with UNSUPPORTED_CLIENT.
Codex's PATH-alias warning disappears with the corrected temporary root, and all
native inventory commands run; enabled app plugins still prevent certification.
Grok's original config-home skill result tested the wrong boundary, since that
was its intended configuration root. Its cancelled positive control provides no
isolation evidence. The cwd MCP failure also included the dedicated ModelSpec
server, because Grok did not consume the generated empty MCP file. Keeping HOME
unchanged now exposes actual real-home `.agents` skills and Claude plugins in
native discovery; this is grounds for refusing the current adapter. Claude's
status reports not logged in and doctor stops before any model canary.

### Reports and ordinary runs

Doctor and run require a private `--out` outside this public checkout and its
other worktrees. Symlink output files are refused. Reports contain measurements,
statuses, authentication summaries, inventory and isolation evidence. Unsupported,
limited, capped and skipped rows remain explicit. Raw transcripts are not saved.
No scenario or judge runs occur in doctor or dry-run.

```sh
python -m qa.tui_harness --dry-run --scenario budget-approved --out /tmp/tui-preview
python -m qa.tui_harness --smoke --max-runs-per-cli 1 --quiet-hours --out /tmp/tui-smoke
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest tests/test_tui_harness.py -q
```

The runner is serial. Quotas count both scenario and judge starts, including
failures. Doctor's model canaries are separate. Vendor usage limits stop further
starts for that CLI, without retries. `--quiet-hours` refuses new starts between
08:00 and 21:59 local; `--force` overrides only that guard. Native inventories are
rechecked at ordinary launches and invalid evidence revokes eligibility.
Offline tests cover every existing credential read/copy/move guard, unchanged
credential sentinels, macOS HOME preservation and refusal guards, account-free
auth summaries, real-home metadata canaries, stdout/stderr listing grammar,
positive controls, receipt staleness and faked end-to-end launches.
