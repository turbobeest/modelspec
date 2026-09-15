# MODEL-60 smoke report: 9 setups x 1 task x 1 run

Run date: 2026-09-15. Harness host: `apple_macbook_pro_m5_max`, one run at a time.
Raw records: [`runs/smoke.jsonl`](runs/smoke.jsonl). State: [`smoke-state.json`](smoke-state.json).
Raw CLI streams stay in the run sandbox and are not committed.
Spec: [`docs/agentic-latency-benchmark.md`](../../docs/agentic-latency-benchmark.md).

This is a pilot of 1 task and 1 run per setup. It shows only that the harness works. It is not a ranking.
Totals from different setups are not comparable yet.

## Task set

- **Aider polyglot benchmark, Python track** (`https://github.com/Aider-AI/polyglot-benchmark`),
  commit `7e0611e77b54e2dea774cdc0aa00cf9f7ed6144f` (2024-12-22).
- 20 tasks: the first 20 `python/exercises/practice/*` directories by name, from `affine-cipher` to `pov`.
  The selection is deterministic, not cherry-picked.
- Task-set hash: `b9d1b251884edf2f4d0df195585f2b7b850ca95a6e65751da032b284c8fa5ed3`. It is the sha256 over each file's path and sha256, for every file in the 20 directories.
- Smoke task: `affine-cipher`.
- Grading: the exercise's own unittest file, restored from the pinned checkout. It runs in `python:3.12-slim` with `--network none` and `--read-only`.

Why this set, measured against the spec:

| Spec requirement | How this set meets it |
|---|---|
| Named, versioned, public benchmark with a known licence | A published benchmark (Aider leaderboard). Exercises come from Exercism, whose tracks are MIT-licensed. The repo has no LICENSE file, so this is a caveat. |
| Tools deterministic, local containers, no live web | Pure standard-library Python. Grading is offline in Docker. |
| Mix of short and long loops | The exercises range from `beer-song` to `forth`, `poker` and `pov`. |
| Graded by tests | Every exercise ships a unittest file, and the reference solution (`.meta/`) is withheld from the agent. |
| Cheap enough for 540 rollouts | Each task is small, and a run takes seconds to minutes. |

Terminal-Bench was rejected. Its tasks need the agent's shell inside the task container, and the four subscription CLIs run on the Mac host and cannot be moved into a Linux container without moving their keychain or OAuth auth. SWE-bench subsets were rejected because each needs a heavy per-repo image, and a single run would take much longer.

## Results

| Setup | Status | Total s | Startup s | Model s | Tool s | Turns | Tool calls | Tokens in / out | Tests |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| claude-code / claude-opus-5 | ok | 18.9 | 0.7 | 17.7 | 0.3 | 5 | 4 | 83,846 / 1,141 | **pass** |
| codex / GPT-5.6 | skipped | | | | | | | | model id ambiguous |
| grok / grok-4.6 | usage limit | 8.3 | | n/a | n/a | 0 | 0 | | not run (HTTP 402) |
| gemini / Gemini 3.8 Flash | skipped | | | | | | | | CLI uses API-key auth |
| opencode / qwen3:32b | skipped | | | | | | | | not on Spark |
| opencode / gemma4:31b | skipped | | | | | | | | not on Spark |
| opencode / gemma4:26b | ok | 156.1 | 37.4 | 112.2 | 0.1 | 7 | 6 | 60,885 / 7,393 | fail (5/16) |
| opencode / mistral-large:123b-instruct-2411-q4_K_M | skipped | | | | | | | | not on Spark |
| opencode / qwen3:30b-a3b-instruct-2507-q4_K_M | ok | 27.5 | 12.2 | 1.3 | 0.02 | 4 | 3 | 33,151 / 935 | **pass** |

Status and timing notes:

- **Claude.** The CLI's own `duration_api_ms` is 18,393 against a derived model_s of 17.66 s. The CLI figure is slightly larger than wall time, which suggests auxiliary API calls counted in parallel.
- **gemma4:26b.** One write step took about 106 s to emit 6,918 output tokens. The startup of 37 s includes the first request to the Spark, and the model was probably loading there.
- **qwen3:30b-a3b.** About 14 s falls after the last step_finish (shutdown and exit) and is not model time.
- **Grok.** It returned `API error (status 402 Payment Required): Grok Build usage balance exhausted` before any event. The setup is stopped in state.
  The first run of the limit regex missed this wording and logged the run as `error`. The regex now matches 402, "balance exhausted" and "payment required", and the record was relabelled `rate_limited` by hand, as noted in the record.

## Skipped setups

- **Codex.** `codex debug models` lists `gpt-5.6-sol`, `gpt-5.6-terra` and `gpt-5.6-luna`. "GPT-5.6" is ambiguous, so per the ticket no model was guessed. The CLI is logged in with ChatGPT.
- **Gemini.** `~/.gemini/settings.json` has `security.auth.selectedType = gemini-api-key`. That is API-key auth, not a subscription login, which the ticket forbids. No `gemini-3.8*` model id string was found in the installed CLI (0.59.0) either.
- **qwen3:32b, gemma4:31b, mistral-large:123b-instruct-2411-q4_K_M.** These are not in `http://100.127.37.30:11434/api/tags` at run time. Present were gemma4:26b, qwen3:30b-a3b-instruct-2507-q4_K_M, and models outside the scope.

## Adapters: command, confinement, reach, and separability

All runs share these properties:

- The working directory is a fresh copy of the task: the stub, the tests and `.docs`, with no `.meta`. It lives under the session scratchpad in `/private/tmp`, never in `$HOME`, `~/dev` or a repo. The runner refuses any other root.
- The environment is an allowlist: `PATH HOME USER LOGNAME LANG LC_ALL TERM SHELL`. `SSH_AUTH_SOCK`, `GH_TOKEN`, `OP_*`, `*_API_KEY` and `ANTHROPIC_BASE_URL` are all dropped.
- The machine has `ANTHROPIC_BASE_URL` set. Dropping it means Claude used the first-party claude.ai OAuth login.
- No global CLI config was modified.

### Claude Code 2.1.272

```
claude -p <prompt> --model claude-opus-5 --output-format stream-json --verbose \
  --dangerously-skip-permissions --no-session-persistence --strict-mcp-config \
  --setting-sources project --settings '<run settings>'
```

- **Confinement.** The run settings enable the Bash sandbox (Seatbelt) with `allowUnsandboxedCommands: false`. They also deny `Read`/`Edit` of `~/.ssh`, `~/.aws`, `~/.config`, `~/.gnupg`, `~/.codex`, `~/.grok`, `~/.gemini`, `~/.claude`, `~/dev` and `~/Library`.
  User settings, hooks and MCP servers are not loaded. Auth is the CLI's own keychain login and is never copied.
- **Reach.** Sandboxed shell writes are limited to the working directory. File tools can still read other paths under `$HOME` that the deny list doesn't name. Network is available to the CLI itself.
- **Separability: yes.** The split is derived from line-receipt timestamps. A `tool_use` block opens a tool interval and the matching `tool_result` closes it. The CLI also reports `duration_api_ms`, which is recorded.

### Grok CLI 1.0.30

```
grok -p <prompt> -m grok-4.6 --output-format streaming-json --always-approve \
  --sandbox workspace --cwd <workdir> --disable-web-search
```

- **Confinement.** The built-in `workspace` sandbox profile applies. Web tools are disabled. Auth is `~/.grok` (a grok.com login).
- **Separability: not established.** No events were emitted before the 402, so there is no recorded stream to verify a parser against. Records use `parse_unverified`, which gives total time only, with model and tool time left null.

### opencode 1.18.30 (local, DGX Spark Ollama)

```
sandbox-exec -p <profile> <opencode binary> run <prompt> -m spark-ollama/<model> \
  --format json --auto --pure --dir <workdir>
```

- **Run-scoped config.** `HOME` and `XDG_*` point at a fresh directory inside the run sandbox. The provider comes from `OPENCODE_CONFIG_CONTENT`: `spark-ollama`, `@ai-sdk/openai-compatible`, base URL `http://100.127.37.30:11434/v1`, with permissions `external_directory: deny` and `webfetch: deny`.
  Project config, Claude Code imports, autoupdate and models fetch are disabled. The user's `~/.config/opencode` is never read.
- **Confinement.** The Seatbelt profile denies all reads under `/Users` except the opencode install directory. It denies all writes except the run sandbox, `/private/var/folders`, `/private/tmp/opencode` and `/dev/null` or `/dev/tty`.
- **Reach.** Read-only access to system paths outside `/Users`. Network is open, and is used for the Spark. No credentials are involved.
- **Separability: yes.** Tool time is opencode's own `state.time.start/end` for each tool part. Model time is the span from `step_start` to `step_finish`, using event `timestamp`, minus the tool spans in that step.

### Codex 0.153.4 and Gemini 0.59.0

No adapter was run. Because no stream was recorded, no parser is claimed for them.

## Estimate for the 540-run pass (9 setups x 20 tasks x 3)

This is extrapolated from one task per setup and is low confidence. Task difficulty varies widely.

| Setup | Smoke total | 60 runs, including about 3 s of grading each |
|---|---:|---:|
| Claude Opus 5 | 19 s | about 25 min |
| qwen3:30b-a3b | 27 s | about 30 min |
| gemma4:26b | 156 s | about 2.6 h |
| Codex, Grok, Gemini (not measured; assumed similar to Claude, 20–60 s) | | about 0.5–1 h each |
| qwen3:32b, gemma4:31b (dense; assumed at or above gemma4:26b) | | about 3–5 h each |
| mistral-large 123B q4 (dense; likely to hit the 570 s cap) | | up to about 9.5 h |

- **Duration.** About 20–28 h sequential, and local models dominate.
- **Usage.** Claude used about 84k input tokens (mostly cache reads) and 1.1k output per run; the CLI-reported equivalent is $0.18 per run. Over 60 runs that is about 5M input tokens, or about $11 at the CLI's equivalent price, taken from a subscription allowance.
- **Blockers.** Grok's usage balance is already exhausted. Codex and Gemini are blocked on a model id decision and on auth. Three Spark models are not pulled.
