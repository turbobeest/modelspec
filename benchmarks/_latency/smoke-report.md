# MODEL-60 smoke report: agentic latency pilot

Run date: 2026-09-15. Harness host: `apple_macbook_pro_m5_max`, one run at a time.
Raw records: [`runs/smoke.jsonl`](runs/smoke.jsonl). State: [`smoke-state.json`](smoke-state.json).
Raw CLI streams stay in the run sandbox and are not committed.
Spec: [`docs/agentic-latency-benchmark.md`](../../docs/agentic-latency-benchmark.md).

This is a pilot of 1 task and 1 run per setup. It shows only that the harness works. It is not a ranking.

## Pilot roster (Jamie, 2026-09-15)

| Setup | Inference host |
|---|---|
| Claude Code, `claude-opus-5` | Anthropic |
| Codex, `gpt-5.6-sol` | OpenAI |
| opencode, `qwen3:30b-a3b-instruct-2507-q4_K_M` | DGX Spark, Ollama |
| opencode, `qwen3:32b` | DGX Spark, Ollama |
| opencode, `mistral-large:123b-instruct-2411-q4_K_M` | DGX Spark, Ollama |
| opencode, `nemotron-3-nano:latest` (24.3 GB) | DGX Spark, Ollama |
| opencode, `nemotron-3-super:latest` (86.8 GB) | DGX Spark, Ollama |

Dropped: Grok 4.6, Gemini 3.8 Flash, and all Google models (`gemma4:26b`, `gemma4:31b`). Their smoke records are kept with status `dropped`. No substitutes were added. The two Nemotron models were added by Jamie later the same day; they were already installed on the Spark, and nothing was pulled or updated.

## Task set

- **Aider polyglot benchmark, Python track** (`https://github.com/Aider-AI/polyglot-benchmark`),
  commit `7e0611e77b54e2dea774cdc0aa00cf9f7ed6144f` (2024-12-22).
- 20 tasks: the first 20 `python/exercises/practice/*` directories by name, from `affine-cipher` to `pov`. The selection is deterministic.
- Task-set hash: `b9d1b251884edf2f4d0df195585f2b7b850ca95a6e65751da032b284c8fa5ed3`. It is the sha256 over each file's path and sha256, for every file in the 20 directories.
- Smoke task: `affine-cipher`.
- Grading: the exercise's own unittest file, restored from the pinned checkout. It runs in `python:3.12-slim` with `--network none` and `--read-only`. The reference solution (`.meta/`) is never copied to the agent.

Why this set, measured against the spec:

- It is a named, pinned, public benchmark. The exercises come from Exercism, whose tracks are MIT-licensed; the repo itself has no LICENSE file.
- The tools are deterministic: the tasks use only the Python standard library, and grading is offline in Docker.
- Loop lengths vary, from `beer-song` to `forth`, `poker` and `pov`.
- Every task is graded by tests, and each is small enough for hundreds of rollouts.

Terminal-Bench was rejected because the agent's shell must be inside the task container, and the subscription CLIs keep their logins on the Mac. SWE-bench was rejected because it needs heavy per-repo images.

## Smoke results (current roster)

| Setup | Status | Total s | Startup s | Model s | Tool s | Turns | Tool calls | Tokens in / out | Tests |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| Claude Code 2.1.272 / claude-opus-5 (confined) | ok | 22.2 | 0.5 | 20.3 | 1.2 | 5 | 4 | 73,708 / 1,411 | **pass** |
| Codex 0.153.4 / gpt-5.6-sol | usage limit | | | | | | | | not run |
| opencode 1.18.30 / qwen3:30b-a3b-instruct-2507-q4_K_M | ok | 27.5 | 12.2 | 1.3 | 0.02 | 4 | 3 | 33,151 / 935 | **pass** |
| opencode 1.18.30 / qwen3:32b | timeout | 570.0 | 57.7 | n/a | n/a | 0 | 0 | | fail (no edit) |
| opencode 1.18.30 / mistral-large:123b-instruct-2411-q4_K_M | ok | 498.9 | 72.0 | 419.5 | 0.005 | 2 | 1 | 10,209 / 1,127 | fail |
| opencode 1.18.30 / nemotron-3-nano:latest | ok | 106.5 | 15.7 | 83.2 | 0.1 | 7 | 6 | 65,258 / 6,182 | **pass** |
| opencode 1.18.30 / nemotron-3-super:latest | timeout | 570.0 | 64.1 | 347.4 (partial) | 0.05 | 5 | 5 | 51,536 / 7,459 (partial) | fail |

Notes:

- **Claude.** This is the confined re-run. The CLI reports `duration_api_ms` 21,261. An earlier run under weaker confinement (18.9 s, pass) is kept as `superseded`.
- **Codex.** The confinement probe returned `You've hit your usage limit … try again at Sep 19th, 2026 6:22 AM` (ChatGPT plan) before any tool ran.
  The login worked under the outer Seatbelt profile, because the request reached the API. Per stop-on-first-limit, the smoke was not attempted. Confinement is therefore not yet proven by a live tool call; re-probe after the reset.
- **qwen3:32b.** Killed at the 570 s cap. Its first step never finished, and no step_finish was emitted, so no model/tool split exists. Startup, including the cold model load on the Spark, was 57.7 s.
  This looks like extended thinking. The ticket forbids effort levels, so whether to disable thinking is Jamie's call.
- **mistral-large.** One tool call, and the edited solution fails the tests. The run spent 419.5 s on model time for 1,127 output tokens, about 2.7 tokens/s including prefill. Startup, including the cold load, was 72 s.
- **nemotron-3-super.** Killed at the 570 s cap in the middle of a step. It had completed 5 steps (347 s of model time, 7,459 output tokens). The model and token figures cover the completed steps only; the open step's time is not counted. Startup, including the cold load, was 64 s.
- **nemotron-3-nano.** Passed. It emitted 6,182 output tokens over 7 steps, likely mostly reasoning.
- **qwen3:30b-a3b.** About 14 s falls after the last step (CLI shutdown) and is not model time.

Dropped setups, historical:

- Grok 4.6: HTTP 402, "usage balance exhausted".
- Gemini 3.8 Flash: skipped, because the CLI uses API-key auth.
- gemma4:26b: 156.1 s, failed the tests.

The gemma4:31b smoke also ran, for 339.5 s, and passed. It was run before the Google drop reached this worker, and its record is marked `dropped`.

## Confinement per adapter

All adapters share these properties:

- The working directory is a fresh copy of the task (stub, tests and `.docs`, no `.meta`) under `/private/tmp`. The runner refuses `$HOME`.
- The environment is an allowlist: `PATH HOME USER LOGNAME LANG LC_ALL TERM SHELL`. Tokens, API keys, `SSH_AUTH_SOCK`, `OP_*` and `ANTHROPIC_BASE_URL` are dropped.
- No global CLI config is modified. The Gemini settings were not touched.

### Claude Code

```
sandbox-exec -p <claude profile> <claude binary> -p <prompt> --model claude-opus-5 \
  --output-format stream-json --verbose --dangerously-skip-permissions --no-session-persistence \
  --strict-mcp-config --setting-sources project --settings '<run settings>'
```

**Run-settings deny rules.** `//` marks an absolute path. There are no allow rules.

```
Read(//Users/**)  Edit(//Users/**)  Write(//Users/**)  Glob(//Users/**)  Grep(//Users/**)  NotebookEdit(//Users/**)
WebFetch  WebSearch
```

**Outer Seatbelt profile.**

- Reads under `/Users` are denied, except:
  - the claude install directory
  - `~/.claude`
  - `~/.claude.json*`
  - `~/Library/Keychains`, for the claude.ai login
  - the literal directories `/Users` and `$HOME`
- Writes are allowed only to:
  - the run sandbox
  - `/private/var/folders`
  - `/private/tmp/claude-501`
  - `/private/tmp/srt-*`
  - `~/.claude`
  - `~/.claude.json*`
  - `/dev/null` and `/dev/tty`

**Inner Bash sandbox is disabled (`sandbox.enabled: false`).** Seatbelt cannot nest: every Bash call failed with `sandbox_apply: Operation not permitted`. The outer profile confines Bash instead, and it also denies Bash reads under `/Users`.

A harmless side effect: `/tmp/claude-*-cwd` cannot be written, so Bash prints one "operation not permitted" line per command.

**Probe on 2026-09-15.** No contents were recorded, and a check found no content from `~/.zshrc` or `~/Documents` in any event.

| Attempt | Result |
|---|---|
| Read tool on `/Users/terbeest/.zshrc` | denied by the permission rules |
| Bash with literal `/Users/...` paths | denied by the permission rules; the command did not run |
| Bash with the path hidden from the checker (`a=/Us; b=ers/...`) | ran, but Seatbelt denied `ls ~/Documents` and reading `~/.zshrc`. Writing to the run directory succeeded. |

**Separability: yes.** The split is derived from line-receipt timestamps: a `tool_use` block opens an interval, and its `tool_result` closes it. The CLI's `duration_api_ms` is also recorded.

### Codex

```
sandbox-exec -p <codex profile> <codex binary> exec -m gpt-5.6-sol --json \
  --dangerously-bypass-approvals-and-sandbox --ephemeral --ignore-user-config --ignore-rules \
  --skip-git-repo-check --color never -C <workdir> <prompt>
```

**Outer Seatbelt profile.**

- Reads under `/Users` are denied, except `~/.codex` and the literal directories `/Users` and `$HOME`.
  `~/.codex` is CODEX_HOME. It holds the install (under `packages/standalone/releases`), the ChatGPT login (`auth.json`) and Codex's own session history, so Codex can read its own state.
- Writes are allowed only to the run sandbox, `~/.codex`, `/private/var/folders`, `/dev/null` and `/dev/tty`.

Codex's own sandbox also uses Seatbelt and cannot nest, so it is bypassed, and the outer profile confines the whole process.

**Caveat.** `--ignore-user-config` did not stop a plugin MCP client from starting: stderr showed an OAuth-required error from a Cloudflare MCP server.

**Probe:** blocked by the usage limit, so there is no tool-level result yet.

**Separability: unknown.** No tool-bearing `--json` stream has been recorded. Records use the unverified parser, which gives total time only.

### opencode (DGX Spark Ollama)

```
sandbox-exec -p <profile> <opencode binary> run <prompt> -m spark-ollama/<model> \
  --format json --auto --pure --dir <workdir>
```

- **Run-scoped config.** `HOME` and `XDG_*` point at a fresh directory. The provider comes from `OPENCODE_CONFIG_CONTENT` (base URL `http://100.127.37.30:11434/v1`), with permissions `external_directory: deny` and `webfetch: deny`.
- **Seatbelt.** Reads under `/Users` are denied except the opencode install. Writes are allowed only to the run sandbox, `/private/var/folders`, `/private/tmp/opencode` and `/dev/null` or `/dev/tty`.
- **Separability: yes.** Tool time comes from opencode's own `state.time` for each tool part. Model time is the span from `step_start` to `step_finish`, using event timestamps, minus the tool spans in that step.

## Estimate for the full pass (7 setups x 20 tasks x 3 reps = 420 runs)

This is low confidence: it is based on one task per setup. The 570 s cap bounds every run, and each includes about 3 s of grading.

| Setup | Smoke | 60 runs |
|---|---:|---:|
| Claude Opus 5 | 22 s, pass | about 25 min |
| Codex gpt-5.6-sol | not measured (assumed 20–60 s) | about 0.5–1 h |
| qwen3:30b-a3b | 27 s, pass | about 30 min |
| nemotron-3-nano | 106 s, pass | about 1.8 h |
| mistral-large 123B | 499 s, fail | about 8.3–9.6 h |
| qwen3:32b | 570 s timeout | up to about 9.6 h (every run at the cap) |
| nemotron-3-super | 570 s timeout | up to about 9.6 h (every run at the cap) |

- **Duration.** About 30–32 h run one at a time. The three slow local models (mistral-large, qwen3:32b, nemotron-3-super) make up about 90% of it.
- **Usage.** Claude uses about 74k input tokens (mostly cache reads) and 1.4k output per run, which is about 4.4M input tokens over 60 runs. The CLI-equivalent price is $0.16 per run, about $10, from the subscription.
  Codex usage is unmeasured, and its plan is exhausted until 2026-09-19 06:22. Local models cost only Spark time.
- **Before the full pass:**
  - Codex must reset, and then be re-probed and smoked.
  - Jamie should decide about the cap and about thinking for qwen3:32b and nemotron-3-super, which both timed out on the easiest-sorted task. At the current cap, most of their runs would be recorded as timeouts rather than times.
  - Jamie should consider a higher cap for mistral-large as well.
