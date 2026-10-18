# MODEL-404-sync billing merge resolution

Resolved only `tests/replay_billing_launch.py` and `tests/test_billing_launch.py` while merging main `8971608aab849862b4a4870f1bc06e46fc9e7dd2` into approved branch source `7b833056a4cb8aa10c0f56cf6001b13224634ada`. Root subsequently committed the merged source as `61e8dbfa2e69077f6ed72940eaf0789d558188df`.

Both sides independently repaired the same replay isolation bug: restoring all of `sys.modules` removed newly imported Pydantic modules. The branch used `ExitStack`; main #824 used a missing-value sentinel and `try/finally`. Both restore only the `js`, `workers`, and `bundled_data` entries. The resolved helper is byte-identical to main, including restoration of absent entries and entries whose previous value was `None`. Main history for #808, #824, #825, and the intervening fixture fixes was inspected; #824 is the only incoming commit that changes these two files.

The test import conflict retains the union of required imports. All test bodies and decorators from both sides remain unchanged: main's three cold-process cases for absent/module/`None` runtime stubs, plus the branch's cold-process decision/OpenAPI hardware-fit schema regression. An AST comparison against the original merge-side blobs verified every original top-level function, including every assertion. There are 11 functions on each original side and 12 after combining them.

The first focused run passed 39 tests and failed five agent-guide cases because `qa/fixtures/mcp-tools.json` still contained merge markers. No behavior changed in response. After the artifact owner completed regeneration, the same focused pair passed all 44 tests with direct exit 0. Resource load before the rerun was 2.67 / 1.92 / 1.74. No full suite, build, or browser run was started by this agent; no staging or commits were performed by this agent.

Commands, exit codes, and compact output are in [results.txt](results.txt). The preliminary artifact-only failures are retained in [billing-agent-focused.txt](billing-agent-focused.txt); the final focused output is [billing-agent-focused-green.txt](billing-agent-focused-green.txt).
