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

Set `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`, and `MODELSPEC_API_KEY` in your environment. Configure the API and static export origins and model ids in a copy of `qa/config.yaml`. Only the selected agents' keys and the separate judge's key are required. The default judge uses OpenAI, so a Claude-only run also needs `OPENAI_API_KEY`.

```sh
python -m qa.agent_harness --config /tmp/model-268-staging.yaml \
  --api-base-url https://your-staging-worker.example \
  --export-base-url https://your-staging-export.example \
  --output-dir /tmp/model-268-private-reports
```

The runner refuses known production ModelSpec hosts and follows no redirects. It uses plain HTTP with Anthropic Messages, OpenAI Responses, and Gemini `generateContent`. The agent receives only the user request and constraints, a short ModelSpec system note, the committed OpenAPI document, and the seven MCP tools. Expectations, rubrics, source specs and gap annotations are withheld. Tools forward to configured origins and preserve origin envelopes, validation errors and unknowns. The shim mirrors the MCP's split-data setting and nested Zod field stripping. `data_split: false` and `vocabulary_path: /api/decision/vocabulary.json` select the static export path.

The live judge is a separate stateless model call with the final answer, tool evidence, scenario rubric and any approved expected evidence. It extracts the final top recommendation or tied set, then assesses constraints, ties and uncertainty. A run succeeds only when the rubric passes and its recommendation is acceptable where independent evidence exists. Recall's acceptable sets are unordered; any nonempty top subset can match. The rubric handles confidence, prohibited candidates and unknown candidates. An abstention matches recall only where an explicit rule permits it. Scenarios with `expected: null` are judged by their rubric alone.

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

`qa/schemas.py` now inlines local references and requires an object root for every provider. Claude and OpenAI retain JSON Schema constraints; [OpenAI tools explicitly disable strict mode](https://developers.openai.com/api/docs/guides/function-calling#strict-mode), so optional fields and map parameters stay optional. Gemini uses [`parametersJsonSchema`](https://ai.google.dev/api/generate-content#FunctionDeclaration) with a conservative subset of the documented Schema vocabulary. It omits references, map keywords and tuple or exclusive-bound constraints, and retains their meaning in descriptions. Google's JSON Schema field documents `additionalProperties`, so its removal is a compatibility choice, not a claim that every Gemini endpoint rejects it. The OpenAPI-style `parameters` field has a different vocabulary.

Recursive inputs are expanded once before recursive children become descriptions. These provider schemas guide argument generation. The tool shim still validates arguments against the complete original MCP schema, including recursion and constraints described in prose. Tests build all three providers' real first-scenario payloads, validate their schemas, preserve representative valid MCP arguments and check bounded request size. They do not prove live provider acceptance.

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

`qa.tui_harness` uses headless agent CLIs and their existing subscription logins.
It shares this catalogue, the compact guide, judge rubric, judgement parser,
recall matching and report aggregation with the API runner. It configures the
remote Streamable HTTP MCP at `https://api.modelspec.dev/mcp`, rather than the
API runner's HTTP shim. Each scenario and judge gets a new temporary workspace.
Agent prompts contain the request and constraints; the judge alone receives
rubrics, recall expectations and tool evidence. Judges have no MCP servers or
built-in tools.

Agent-vendor API keys and customization environment variables are excluded from
child processes. The runner does not open, copy, symlink or log auth files. It
keeps HOME unchanged and lets the CLI load its own subscription login. Decision
tools separately require a ModelSpec credential, as documented in
[`mcp/README.md`](../mcp/README.md). If `MODELSPEC_API_KEY` is set, the runner uses
Claude's native `${MODELSPEC_API_KEY}` header expansion; the secret never enters
argv or generated configuration. Without it, the connection is anonymous and
decision calls can return `missing_api_key`. This does not enable vendor API
billing or change the deployed auth guard.

### Isolation findings, 2026-10-03

Only Claude is currently eligible to launch. A supported flag must exclude
discovery, not merely hide its output. Configuration cannot turn an unsupported
adapter on. Updating support requires reviewing the new CLI's controls and
passing its canary. Headless argument builders and synthetic format fixtures
exist for all four families; the launch guard prevents unsupported processes.

| CLI inspected | Configured model / effort | Isolation result |
| --- | --- | --- |
| Claude Code 2.1.283 | `fable` / `high` (the private probe resolved `claude-fable-5-1`) | Eligible; parent instruction and hook canary passed |
| ChatGPT.app Codex 0.160.0 | `gpt-6.1-sol` / `max` | Unsupported; ignoring config retains global skill roots |
| Gemini CLI 0.60.0 | `gemini-3.8-pro` | Unsupported; changing context filenames retains default memory |
| Grok 1.0.46 | `grok-4.7` / `xhigh` | Unsupported; no verified exclusive configuration mode |

Claude uses `--setting-sources ''`, `--disable-slash-commands`,
`--strict-mcp-config`, `--no-session-persistence`, `--no-chrome` and
`--tools ''`. Inline settings disable all hooks, auto memory, connectors and
command plugin sources. `CLAUDE_CODE_DISABLE_CLAUDE_MDS=1` excludes user,
project and automatic instruction files. The environment also disables auto
memory, prompt history, claude.ai MCP discovery and MCP tool search. Its startup
inventory must contain no skills, non-builtin plugins, other MCP servers or
built-in tools. A scenario additionally requires a connected ModelSpec server.
The built-in `agents-md` plugin remains visible in inventory, with instruction
discovery disabled; the planted AGENTS.md is part of the canary. See the
[Claude flags](https://code.claude.com/docs/en/cli-reference) and
[environment reference](https://code.claude.com/docs/en/env-vars).

Claude's `--safe-mode` cannot serve this task: the installed CLI also drops
explicit HTTP MCP servers in that mode. `--bare` excludes OAuth/keychain auth
and therefore cannot use Jamie's subscription. Neither is used by the runner.

Codex `exec --ignore-user-config` preserves login, but its
[loader](https://github.com/openai/codex/blob/main/codex-rs/config/src/loader/mod.rs)
returns an empty `User` layer. The
[skill-root resolver](https://github.com/openai/codex/blob/main/codex-rs/ext/skills/src/host_roots.rs)
still derives `$CODEX_HOME/skills` and `~/.agents/skills` from that layer.
`skills.include_instructions=false` suppresses the catalog without excluding
discovery. Profiles layer configuration over the same home. A fresh CODEX_HOME
relocates login state too. No auth-copying alternative is implemented.

Gemini's installed `setGeminiMdFilename` adds configured names to the default
`GEMINI.md` list, even for `context.fileName=[]`. `--extensions none`, disabled
skills/hooks and an MCP allowlist do not resolve that memory issue.
`GEMINI_CLI_HOME` relocates both memory and OAuth state. See
[Gemini configuration](https://geminicli.com/docs/reference/configuration/).
Grok's `GROK_CONFIG`/`GROK_CONFIG_PATH` overrides selected settings over its
existing configuration; `--system-prompt-override` and `GROK_MEMORY=0` do not
establish that plugins, hooks, rules and other MCP servers are excluded.
`GROK_HOME` relocates login as well. See
[Grok settings](https://docs.x.ai/build/settings) and the
[headless reference](https://docs.x.ai/build/cli/headless-scripting).

The supported CLI runs one non-MCP canary before scenarios. It plants instruction
files, an always-use skill and a hook in a temporary parent directory, then
starts from a fresh child directory and asks for exactly `OK`. It checks all
stdout/stderr for the planted marker, checks the hook's filesystem side effect,
requires a successful answer and validates startup inventory. No real user
instruction files are edited. Empty piped stdin prevents the launching shell's
heredoc from becoming extra CLI context. Canaries are not ModelSpec scenarios.

### Commands and reports

`--out` is mandatory and names a private directory. The runner rejects this
public checkout, other worktrees sharing its git directory, symlink aliases and
symlink report files. It never defaults to `qa/reports`. Raw transcripts remain
in memory; JSON contains final answers and ordered tool calls with deduplicated
results, while Markdown contains aggregates and statuses. Child session history
is disabled for the supported adapter.

```sh
# Offline preview. Unsupported CLIs have reasons instead of runnable commands.
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m qa.tui_harness \
  --dry-run --scenario budget-approved --max-runs-per-cli 1 --out /tmp/tui-preview

# One tiny non-MCP canary; no scenarios or judges.
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m qa.tui_harness \
  --verify-isolation --cli claude --out /tmp/tui-isolation

# Smoke refuses before scenarios if a selected CLI or judge is unsupported.
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m qa.tui_harness \
  --smoke --max-runs-per-cli 1 --quiet-hours --out /tmp/tui-smoke

PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest \
  tests/test_tui_harness.py -q
```

`--cli` and `--scenario` can be repeated. Models, effort and judge routes live in
`qa/tui_config.yaml`; `--judge claude=codex` overrides one route. A same-family
judge is rejected before launch. With the current support findings there is no
eligible cross-family judge for Claude, so ordinary live invocations record
`judge_unavailable` before spending a scenario call. `--smoke` fixes the scenario
to `budget-approved`, requires all selected CLIs and judges to pass isolation,
and fixes the quota to one. The current all-CLI smoke is refused, not measured.

The runner is serial, giving concurrency one per CLI. `--max-runs-per-cli`
counts scenario and judge subprocesses together, including failed starts;
each supported CLI has one separate preflight canary. That overhead and each
role's count appear in the report. Shared judges consume the same quota as
their own scenarios. A usage-limit error or an explicitly configured limit
exit code stops that family for both roles; other families continue. Generic
exit code 1 does not imply a quota failure, and a ModelSpec tool's rate limit
does not imply a vendor subscription limit. There are no harness retries.
`--quiet-hours` refuses new CLI starts from 08:00 through 21:59 local;
`--force` overrides only that guard. Dry-run can run at any time.

Dry-run prints exact argv, cwd, stdin, an environment policy and MCP JSON;
temporary preview workspaces are removed on return. Judge prompts depend on
answers captured at runtime, so their route is reported without inventing an
answer or a judge command. Dry-run creates reports with zero executed runs.

Reports retain the API harness's `runs`, `tool_responses`, `overall`,
`per_family`, `per_agent`, `per_family_agent`, `misuse_patterns` and `gap_list`
shape, and add `isolation`, `cli_invocations`, `stopped_clis` and `per_cli`.
Every run records CLI exit status, wall time, turns with their counting basis,
MCP calls, the one-based index of the first `decide`, final answer and exposed
usage/cost. Unavailable measurements are null; tool response latency is not
inferred from whole-run wall time. Subscription token-equivalent cost does not
establish money charged. A missing judgement is a failed evaluation. Unsupported,
capped and skipped rows remain explicit in aggregate denominators.

`qa/fixtures/tui-streams.json` contains handwritten, synthetic protocol samples.
Claude keys were checked against a private tiny print probe; the other adapters
use the vendors' documented streams because their isolation is unsupported.
No live transcript or real scenario answer is committed. Offline tests exercise
command construction, stream decoding, limits, routing, recall, aggregation,
private output checks, canary failures and launch refusal.
