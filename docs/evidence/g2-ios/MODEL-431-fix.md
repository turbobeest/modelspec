# MODEL-431 Kimi plan reader evidence

The reader verifies the four named legacy plans, reads each new plan's labelled
description, and uses pricing-table billing headers to exclude annual monthly
equivalents. Distinct CNY prices without enough billing information produce no
reading. Agent-use readings preserve exclusions and all sentences in the plan's
description.

## Revisions and tools

- Base SHA: `3c8042a11aa47e8577559e01f71379119bda2cec`.
- Final code/test SHA: `031035ab0a249af3898a3e790b1375998b8c59ec`.
  The following commit adds only this evidence and its replay script/logs.
  The PR body and executor completion record identify the final branch SHA.
- Final `decision/verify.py` SHA-256:
  `b7563c77ed04ffc94e88f9fe81b45b86c2ed6d82cd75a1763b677abae51b149d`.
- Private data revision: `a6f8fd798d7d6f40b35ed08320796b773f29df9a`.
- Python 3.14.4, pytest 9.1.1, Ruff 0.16.6, Git 2.50.1, GitHub CLI 2.102.0.
- Worktree: `/Users/terbeest/dev/worktrees/model-431`.
- Branch: `model-431-kimi-plan-reader`.

## Red before green

All fixtures are synthetic. They reproduce the retained page's structure:
a plan-row pricing table, `Plan: description` lines, and a list of legacy tier
names. Prices and benefit descriptions in the fixtures are invented.

The first regression run used unchanged production code at the base SHA.
It exited 1 with **18 failed, 34 passed**. The full output is in
[MODEL-431-reader-red.txt.gz](MODEL-431-reader-red.txt.gz).

| Defect | Red test | Observed red result | Green result |
| --- | --- | --- | --- |
| Legacy list not read | `test_legacy_list_verifies_each_named_plan` | All four plans were `skipped` on the standalone list fixture instead of `verified` | All four verify |
| Plan descriptions not read | `test_named_plan_line_preserves_agent_entitlement_and_restrictions` | Empty readings for all five plans | Complete description read for each plan, including the Go exclusion |
| Credit allowances not read | `test_named_plan_line_reads_its_own_allowance` | Empty readings for Pro, Max, Ultra | Each plan's own description read |
| Annual equivalent accepted | `test_price_table_uses_billing_headers_to_exclude_annual_equivalent` | Both monthly-rate amounts returned in both column orders | Only the monthly-billed amount returned |
| Ambiguous CNY prices accepted | `test_unlabelled_price_alternatives_produce_no_reading` | Both amounts returned when billing labels were missing | No reading |

The initial fix passed all 52 cases. A source review then identified two
additional scoping defects. Tests reproduced them before correction:

- `test_legacy_list_rejects_reported_or_negated_propositions` caught a later
  plan name inside a reported or negated proposition being read as legacy.
- `test_unlabelled_price_alternatives_produce_no_reading` caught an unlabelled
  price being discarded when only the competing price carried `/month`.

That run exited 1 with **4 failed, 5 passed, 48 deselected**. Its full output is
in [MODEL-431-scoping-red.txt.gz](MODEL-431-scoping-red.txt.gz).
The final suite contains 57 new cases. The combined focused run exited 0 with
**811 passed in 8.91s**. Full output:
[MODEL-431-focused-green.txt](MODEL-431-focused-green.txt).

Exact test commands, run from the assigned worktree:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_kimi_plan_reader.py > /tmp/model-431-scratch/root/reader-red.txt 2>&1

env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_kimi_plan_reader.py > /tmp/model-431-scratch/root/reader-green.txt 2>&1

env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_kimi_plan_reader.py -k 'legacy_list_rejects_reported or unlabelled_price_alternatives' > /tmp/model-431-scratch/root/scoping-red.txt 2>&1

env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_kimi_plan_reader.py tests/test_subscription_availability_reader.py tests/test_decision_verify.py tests/test_model380_subscription_quotes.py tests/test_model380_cursor_wording.py tests/test_price_reread.py tests/test_price_reread_fallback.py tests/test_subscription_availability.py tests/test_subscription_sources.py tests/test_subscription_source_expectations.py > /tmp/model-431-scratch/root/focused-green.txt 2>&1

/Users/terbeest/dev/modelspec/.venv/bin/python -m ruff check tests/test_kimi_plan_reader.py docs/evidence/g2-ios/MODEL-431-replay.py
git diff --check
```

Exit codes were checked directly. The output redirections do not pipe pytest
through another command. Ruff and the whitespace check exited 0.

## Retained-data replay

[MODEL-431-replay.py](MODEL-431-replay.py) replays queued claims against the
existing operator CopyStore. It verifies that the queued claims match the
private YAML facts, compares base and final readers, and probes the ten unknown
facts separately. It does not file claims, write verification records, fetch
pages, or copy page bytes. Its generated reports stay in scratch; prose values
are represented by hashes and lengths.

The private data inventory contains 58 Kimi facts: 48 filed claims and ten
unknown facts without filed claims. Both cited CopyStore snapshots were present,
hash-valid, and readable. The base replay produced 44 verified claims and four
mismatches. The final replay produced 48 verified claims. These are every
verification outcome change:

| Fact ID | Base outcome | Final outcome |
| --- | --- | --- |
| `moonshot/subscription/andante#offering.subscription.availability` | mismatch | verified |
| `moonshot/subscription/moderato#offering.subscription.availability` | mismatch | verified |
| `moonshot/subscription/allegretto#offering.subscription.availability` | mismatch | verified |
| `moonshot/subscription/allegro#offering.subscription.availability` | mismatch | verified |

Each of the new Go, Plus, Pro, Max, and Ultra `offering.subscription.price_cny`
facts now has exactly one reading matching its filed monthly price. Go reads
`49`; the annual-equivalent `39` is absent. All five price verification outcomes
remain `verified`, because the old verifier already accepted any matching
reading among the candidates.

Two other filed facts have additional readings without an outcome change:
`moonshot/subscription/allegretto#offering.subscription.programmatic_or_agent_use`
and
`moonshot/subscription/allegro#offering.subscription.programmatic_or_agent_use`.
Recognizing Kimi Claw adds a candidate from the older retained copy. Both remain
verified.

The following unknown facts gain candidate readings. These are extraction
results, not new filed or verified facts:

| Plan ID suffix under `moonshot/subscription/` | Facet suffix under `offering.subscription.` |
| --- | --- |
| `go` | `programmatic_or_agent_use` |
| `plus` | `programmatic_or_agent_use` |
| `pro` | `programmatic_or_agent_use`, `usage_allowance` |
| `max` | `programmatic_or_agent_use`, `usage_allowance` |
| `ultra` | `programmatic_or_agent_use`, `usage_allowance` |

Go and Plus allowance descriptions contain features without an allowance
statement. Their `usage_allowance` candidate lists remain empty. All ten unknown
facts remain unknown and unfiled; no private data was changed.

Exact replay commands, both exiting 0:

```bash
git clone https://github.com/turbobeest/modelspec-data.git /tmp/model-431-scratch/modelspec-data

env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -B docs/evidence/g2-ios/MODEL-431-replay.py --data /tmp/model-431-scratch/modelspec-data --base-ref 3c8042a1 --output /tmp/model-431-scratch/root/baseline.json > /tmp/model-431-scratch/root/replay-baseline.txt

env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -B docs/evidence/g2-ios/MODEL-431-replay.py --data /tmp/model-431-scratch/modelspec-data --output /tmp/model-431-scratch/root/after.json --compare /tmp/model-431-scratch/root/baseline.json --expect-fixed > /tmp/model-431-scratch/root/replay-after.txt
```

The final replay reports `fixed_assertions_passed: true`. It asserts that the
only outcome changes are the four legacy facts, all 48 claims verify, the five
new CNY prices have one matching reading each, and the expected eight candidate
facets have readings. Reproduction requires the private data revision above
and both existing operator CopyStore copies.

The source-terms audit was read from private commit `8fb320a`, path
`research/model-409/source-terms-audit.md`. It classifies `www.kimi.com` as
`restricts-with-conditions`. The retained-copy decision and page inventory are
recorded in `research/model-425-reread-changes.md`. This task used those existing
copies only. The private clone and generated private reports were removed after
the replay.

## Limits of observation

- No live Kimi page was fetched. This proves behavior on synthetic fixtures and
  the retained copies, not on any subsequent page change.
- No unknown fact was promoted or written to private data.
- The full local pytest suite, sites, and wsl gate were not run. The ticket
  requires focused serial tests and leaves the full pytest shards to CI.
- No CI result or independent cross-model review is claimed.
- No Worker exports, snapshots, rank rows, or runtime code changed.
  `decision/verify.py` is absent from the Worker vendor map, so the conditional
  Worker memory probe and re-vendoring requirement did not apply.
- No provider API, Firecrawl, production switch, real secret, or real tmux
  session was used. No background process from this task remains.
