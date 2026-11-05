# MODEL-453 freshness diagnosis and fix

Assessment date: 2026-11-05. Base SHA: `187117e902c266b3c63b5861af1f57189cf4f30a`.
Final implementation SHA: `e1c06d985379d4369891b6bb0ba9f33e22237fc0`.
The subsequent evidence-only commit is the final PR head. Its exact SHA is recorded
in the PR body and executor completion marker; resolve it in the PR checkout with
`git rev-parse HEAD`. This separation avoids a self-referential commit hash.

## Diagnosis

The public PR job checked the intentionally frozen public image against today's
30-day live-reading limit. It did not read private data. All 872 public live
readings were 36 days old, so all 872 failed. Other PR accuracy layers passed.
The current private checkout passed with 880 live readings when classified with
its own source registry. This is a public orchestration defect, not evidence of
872 stale readings in the current private catalogue.

The first private comparison used `--root` with the unchanged script and reported
876 readings, zero failures. That path still loaded the public source registry.
The independent probe and fixed command use the private registry and count 880.
Both comparisons use the same assessment date and the existing 30-day window.

The freshness loop checks admitted benchmark evidence only. Price, plan,
governance and speed facts contribute zero live readings. There were no undated
live readings and no lineup models missing admitted domain evidence in either
checkout. The public image has 910 unique admitted domain records: 872 live and
38 static. Private data has 906: 880 live and 26 static. Static results do not
expire merely because their evaluation date is old.

| Measurement | Public image | Private checkout, own registry |
| --- | ---: | ---: |
| Lineup models | 44 | 44 |
| Live benchmark evidence | 872 | 880 |
| Verified live records | 865 | 873 |
| Cited-only live records | 7 | 7 |
| Stale live records | 872 | 0 |
| Undated live records | 0 | 0 |
| Missing-evidence models | 0 | 0 |
| Records dated by `record.observed_at` | 872 | 880 |

| Age in days | Public readings | Private readings | Days relative to the 30-day limit |
| --- | ---: | ---: | --- |
| 17 | 0 | 872 | 13 below |
| 24 | 0 | 8 | 6 below |
| 36 | 872 | 0 | 6 above |

All private details in this public evidence are aggregate counts. Private claim
values, identifiers, source URLs, source text, run URLs and PR titles are omitted.
The source and benchmark labels below come from the public frozen image.

## Public source and board breakdown

Each table sums to 872. All entries are stale at the assessment date. The source
host table groups 34 registered public source IDs across 15 hosts. The benchmark
table separates all 59 public benchmark groups, including individual board cuts.

| Public source host | Failed live readings |
| --- | ---: |
| `huggingface.co` | 687 |
| `epoch.ai` | 45 |
| `matharena.ai` | 25 |
| `andonlabs.com` | 19 |
| `labs.scale.com` | 14 |
| `cognition.com` | 13 |
| `mteb-leaderboard-backend.hf.space` | 13 |
| `deepswe.datacurve.ai` | 12 |
| `sierra-tau-bench-public.s3.us-west-2.amazonaws.com` | 9 |
| `www.tbench.ai` | 9 |
| `finbenchmark.ai` | 8 |
| `cursor.com` | 7 |
| `metr.org` | 6 |
| `osworld-v2.xlang.ai` | 3 |
| `www.swebench.com` | 2 |
| Total | 872 |

| Public benchmark group | Failed live readings |
| --- | ---: |
| `aime_2026` | 9 |
| `arena_elo_coding` | 6 |
| `arena_elo_overall` | 8 |
| `arena_elo_style_control` | 21 |
| `arena_sc_business` | 21 |
| `arena_sc_chinese` | 22 |
| `arena_sc_coding` | 21 |
| `arena_sc_creative_writing` | 21 |
| `arena_sc_document` | 14 |
| `arena_sc_english` | 23 |
| `arena_sc_expert` | 21 |
| `arena_sc_factuality` | 21 |
| `arena_sc_french` | 20 |
| `arena_sc_german` | 18 |
| `arena_sc_hard_prompts` | 21 |
| `arena_sc_industry_entertainment_sports_media` | 23 |
| `arena_sc_industry_mathematical` | 22 |
| `arena_sc_industry_software_it_services` | 23 |
| `arena_sc_instruction_following` | 21 |
| `arena_sc_japanese` | 17 |
| `arena_sc_korean` | 18 |
| `arena_sc_legal` | 21 |
| `arena_sc_longer_query` | 21 |
| `arena_sc_math` | 19 |
| `arena_sc_medicine` | 21 |
| `arena_sc_multi_turn` | 21 |
| `arena_sc_non_english` | 21 |
| `arena_sc_polish` | 17 |
| `arena_sc_russian` | 23 |
| `arena_sc_science` | 21 |
| `arena_sc_spanish` | 18 |
| `arena_sc_vision` | 13 |
| `arena_sc_vision_diagram` | 15 |
| `arena_sc_vision_homework` | 14 |
| `arena_sc_vision_ocr` | 15 |
| `arena_sc_writing` | 21 |
| `arena_webdev` | 24 |
| `arxivmath` | 8 |
| `brokenarxiv` | 8 |
| `cursorbench_4` | 7 |
| `deepswe_v1_1` | 12 |
| `finance_benchmark_v2` | 8 |
| `frontiercode_v1_1` | 13 |
| `frontiermath_tiers_1_3_v2` | 18 |
| `gpqa_diamond` | 20 |
| `hle` | 9 |
| `metr_time_horizon_50` | 3 |
| `metr_time_horizon_80` | 3 |
| `mteb_eng_v2` | 4 |
| `mteb_multilingual_v2` | 3 |
| `mteb_v2_reranking` | 2 |
| `mteb_v2_retrieval` | 4 |
| `osworld_2` | 3 |
| `swe_bench_multilingual` | 1 |
| `swe_bench_pro` | 5 |
| `swe_bench_verified` | 8 |
| `tau3_banking` | 9 |
| `terminal_bench_v4_0` | 9 |
| `vending_bench_2` | 19 |
| Total | 872 |

The same 59 public groups account for 872 fresh private readings. Eight additional
private readings are counted without disclosing their board identifiers.

## Rule and history

`accuracy.yaml` keeps the live-reading maximum at 30 days and lineup evidence grace
at seven days. `check_freshness` fails when age is strictly greater than 30; day 30
passes. Registered live sources and explicit live source kinds use observation
metadata, preferring `observed_at`, then `retrieved_at`, then `verified_at`.
An explicit `date_type: observed` can use the evidence date. `evaluated` alone
does not classify a static benchmark result as live.

- `031e453513d0bad77ebd5d513bcee2c4fb8dfa4e`, MODEL-111, introduced the 7/30-day
  configuration and observation-date handling.
- `023ceaab4f7a09764272a2d90e710a73ab70f3d3`, MODEL-124, added registered source
  volatility and weekly re-confirmation of unchanged evidence.
- `31263b638243ae742c10bb8c40888e69c6d55da8`, MODEL-231, changed nightly fidelity
  budgets while leaving these freshness limits unchanged.
- `7e3d8ba6c95eac6f03e438366686c5299499b6bc`, MODEL-436, admitted cited evidence
  without exempting it from the live-age check.

`docs/method/coverage-slo.md` specifies 30 days for live readings and seven days
for offering prices/plans. `docs/method/data-trust-audit.md` makes the same
separation. A 30-day limit allows multiple weekly refresh opportunities and
matches the published method. The inspected history does not provide a more
precise numerical derivation. There is no evidence here for changing the limit.

The public PR workflow checks out only this repository. Before this change,
`--private-data-root` affected fidelity corrections only, and the nightly profile
omitted freshness even though that workflow already checked out private data.

## Writer and merge status

The read-only query returned 99 main-branch workflow runs and 130 PRs. This is the
retrieved history, not a claim about all historical runs.

| Writer | Observed runs | Latest result | Pending refresh PRs | Pending age in whole days |
| --- | --- | --- | ---: | ---: |
| Leaderboard refresh | 5 success | Success | 1 | 9 |
| Price and plan re-read | 9 failure, 1 cancelled | Failure, 317 facts could not be re-read | 1 | 8 |
| Rendered re-read | 3 failure | Failure, 5 unresolved, 0 skipped | 1 draft | 9 |

A green leaderboard run can contain partial fetch failures if some rows updated.
It does not prove complete coverage. The direct private freshness probe is the
separate evidence that the admitted live readings meet the age limit today.
The price and rendered jobs reached their alert gates and updated their PRs.
Their downloaded logs do not identify the individual source-level causes.

All six open bot PRs, grouped without private identifiers, have the following
ages at 2026-11-05 00:00 UTC:

| Purpose | Count | Age in days |
| --- | ---: | ---: |
| Data trust report | 1 | 2.72 |
| Price reconfirmation | 1 | 8.67 |
| Leaderboard refresh | 1 | 9.71 |
| Rendered report, draft | 1 | 9.71 |
| Data trust report | 1 | 9.71 |
| Daily research | 1 | 16.73 |

None of the six has a queued auto-merge request. The three refresh PRs have no
reported checks in the retrieved check rollups. The retrieved history includes
merged leaderboard and price-reconfirm PRs, but no merged rendered-report PR.
The newest rendered report predecessor was closed without merging.

The ticket's auto-merge premise differs from the installed private configuration.
The public `automerge.yml` has score-only/reconfirm eligibility and excludes
changed-price, research, workflow and other protected changes. The inspected
private main has 14 workflows and no auto-merge workflow. Its README assigns data
PR review and merging to a person, consistent with `docs/design/data-split.md`.
The older auto-merge description in `docs/method/coverage-slo.md` does not describe
the private installation. This investigation did not inspect branch-protection
settings or attempt to change merge policy.

The weekly leaderboard writer and its pending refresh PR maintain current
benchmark observations. Price reconfirmation and rendered reports require their
own review and follow-up. None of those private PRs can repair the public job's
choice of frozen input. No refresh was fabricated or dispatched for this ticket,
and no private data was edited.

## Change

Freshness now gates the trusted nightly profile. When `--private-data-root` is
supplied, it builds a separate snapshot and loads that checkout's source registry.
It publishes only counts and a verdict. Private row details, snapshot IDs, parser
errors and snapshot-loader warnings stay out of public reports and logs. Missing,
empty or malformed private input fails with a fixed error message.

The PR profile retains deterministic correctness, frozen-image recall and output
parity. Recall remains gated against its approved public baseline, and PR reports
retain their public snapshot ID. Nightly reference agreement and recall continue
to use public inputs, with recall report-only. Explicit freshness runs without a
private root still check the selected public root and can fail.

The change does not alter thresholds, observation dates, data, production switches,
Worker exports or contracts. The Worker memory probe and re-vendoring requirement
therefore do not apply.

## Red and green evidence

All exit codes were read directly from the command result, without a pipeline.
Tests ran serially without xdist. The repository-wide pytest suite was not run.

| Reproduction or test | Before | After |
| --- | --- | --- |
| Full `--profile pr` on the public checkout | Exit 1; only freshness failed, 872/872 | Exit 0; deterministic correctness, frozen-image recall and parity pass |
| Explicit public freshness layer | Exit 1; 872 failures | Exit 1; still 872 failures, outside frozen PR defaults |
| Private freshness, correct registry | Independent probe: 880 checked, 0 failures | Nightly freshness command exits 0; 880 checked, 0 failures |
| `test_private_freshness_uses_current_data_and_its_registry_without_disclosure`, ages 3, 30, 31 and undated | Four failures; private data/registry ignored | All pass; stale and undated inputs still fail the gate |
| `test_private_freshness_rejects_unreadable_inputs_without_disclosure`, missing, empty, malformed | Three failures; no private-input validation | All pass; sanitized errors |
| `test_nightly_private_freshness_keeps_reference_and_recall_on_public_inputs` | Fails; nightly has no freshness layer | Passes; public reference and recall inputs preserved |
| `test_accuracy_workflows_split_pr_and_nightly_layers` | Fails against new behavioral profile assertion | Passes; freshness belongs to nightly |
| Private logger sentinel assertions in the four age cases | Four failures after first fix; warnings disclosed sentinel identifiers | All pass with scoped log suppression |
| `test_pr_checks_frozen_engine_without_a_current_data_age_gate` | Fails after profile move; report lost snapshot ID | Passes; public snapshot metadata preserved |

Initial red summary: `9 failed, 71 deselected in 1.33s`.
Privacy red summary: `4 failed, 76 deselected in 0.73s`.
A negative end-to-end check assessed the unchanged private checkout at the future
date 2026-12-06. It exited 1 with 880 freshness failures while publishing no row
details or private snapshot ID. This changes only the assessment date and proves
that the private gate still rejects stale data. No observation dates were changed.

Final targeted regressions: 10 passed.
Final focused suites: `137 passed, 1 skipped in 53.26s`.
The skipped test requires `MODELSPEC_DIST` pointing to a built site. No built site
was requested for this harness-only change.

The original full PR run reported `1307 passed in 45.71s` for deterministic
correctness, all 20 recall verdicts matching, and passing CLI/Worker/web parity.
The only red layer was freshness. The final full PR run exited 0: 1307 deterministic tests passed in 45.89s,
all 20 recall verdicts matched, 678 Python parity tests passed with one skip,
and 228 web parity tests passed. The public snapshot ID was preserved.

## Commands and environment

Worktree: `/Users/terbeest/dev/worktrees/model-453`, branch `model-453-codex`.
Python 3.14.4; pytest 9.1.1; Node v22.22.3; npm 10.9.8; git 2.50.1;
GitHub CLI 2.102.0. CI uses Python 3.11 and Node 24 for this profile, so those exact
runtime versions were not reproduced locally.

The scratch clone and every private log/report are deleted after the diagnosis.
The complete count probe is included below so its command remains reproducible.
It reads local files only and prints aggregate counts. Recreate the scratch clone
before rerunning it. Raw accuracy output is kept under scratch, never committed.

```bash
git clone --single-branch --branch main https://github.com/turbobeest/modelspec-data.git /tmp/model-453-scratch/modelspec-data
mkdir -p /tmp/model-453-scratch/executor
# Initial failing layer and private comparison, run before changing code.
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/accuracy.py --profile pr --layers freshness --date 2026-11-05 --output-dir /tmp/model-453-scratch/executor/public-red > /tmp/model-453-scratch/executor/public-red.log 2>&1
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/accuracy.py --profile pr --layers freshness --root /tmp/model-453-scratch/modelspec-data --date 2026-11-05 --output-dir /tmp/model-453-scratch/executor/private-red > /tmp/model-453-scratch/executor/private-red.log 2>&1
# Install web test dependencies in web/ using the required Node version.
(cd web && env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm ci --ignore-scripts --no-audit --no-fund)
# Run from the repository root. The initial and final runs used public-full-red
# and public-final-green as output directory/log names respectively.
env PYTHONPATH=$PWD PYTEST_ADDOPTS='-p no:cacheprovider' PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH /Users/terbeest/dev/modelspec/.venv/bin/python scripts/accuracy.py --profile pr --date 2026-11-05 --output-dir /tmp/model-453-scratch/executor/public-final-green > /tmp/model-453-scratch/executor/public-final-green.log 2>&1
# New tests, first against unchanged implementation and then after the fix.
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_accuracy.py -k 'private_freshness or accuracy_workflows_split'
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_accuracy.py -k 'private_freshness_uses'
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_accuracy.py -k 'pr_checks_frozen'
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_accuracy.py -k 'private_freshness or accuracy_workflows_split or pr_checks_frozen'
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_accuracy.py tests/test_accuracy_alert.py tests/test_cite_only_accuracy.py tests/test_removed_sources.py
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/accuracy.py --profile nightly --layers freshness --private-data-root /tmp/model-453-scratch/modelspec-data --date 2026-11-05 --output-dir /tmp/model-453-scratch/executor/private-final-green > /tmp/model-453-scratch/executor/private-final-green.log 2>&1
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/accuracy.py --profile nightly --layers freshness --private-data-root /tmp/model-453-scratch/modelspec-data --date 2026-12-06 --output-dir /tmp/model-453-scratch/executor/private-future-red > /tmp/model-453-scratch/executor/private-future-red.log 2>&1
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/accuracy.py --profile pr --layers freshness --date 2026-11-05 --output-dir /tmp/model-453-scratch/executor/public-final-red > /tmp/model-453-scratch/executor/public-final-red.log 2>&1
# Rule history, no remote calls.
git log -S 'live_leaderboard_max_age_days' --format='%h %ad %s' --date=iso-strict -- scripts/accuracy.py accuracy.yaml
git log --format='%h %ad %s' --date=iso-strict -G 'observation|_LIVE_SOURCE_KINDS|live_rows|check_freshness' -- scripts/accuracy.py
git show 023ceaab -- scripts/accuracy.py accuracy.yaml
git show 7e3d8ba6 -- scripts/accuracy.py
git show 31263b638 -- accuracy.yaml
git blame -L 218,264 187117e9 -- scripts/accuracy.py
git blame -L 3,6 -- accuracy.yaml
```

GitHub budget: four diagnostic calls for private metadata/logs, one local
`gh --version`, and one draft PR creation, six total. Private run IDs are omitted
from this public record; the two `run view` calls selected the latest failed
price and rendered runs returned by the single run-list query. No polling.

```bash
# Run in /tmp. These two calls returned all 99 runs and 130 PRs in the queried window.
gh run list -R turbobeest/modelspec-data --branch main --limit 300 --json databaseId,workflowName,conclusion,status,createdAt,updatedAt,headSha,event,displayTitle > /tmp/model-453-scratch/executor/private-runs.json
gh pr list -R turbobeest/modelspec-data --state all --limit 300 --json number,title,state,isDraft,author,createdAt,updatedAt,closedAt,mergedAt,headRefName,baseRefName,autoMergeRequest,statusCheckRollup,mergeStateStatus > /tmp/model-453-scratch/executor/private-prs.json
gh run view <latest-price-run-id> -R turbobeest/modelspec-data --log-failed > /tmp/model-453-scratch/executor/price-failed.log
gh run view <latest-rendered-run-id> -R turbobeest/modelspec-data --log-failed > /tmp/model-453-scratch/executor/rendered-failed.log
# Push from the assigned worktree after focused checks.
CI_LOCAL_SKIP=1 git push -u origin model-453-codex
# Create in /tmp, with the reviewed body in scratch.
gh pr create -R turbobeest/modelspec --draft --base main --head model-453-codex --title 'MODEL-453: check freshness against current private data' --body-file /tmp/model-453-scratch/executor/pr-body.md
```

## What was not observed

No live source pages, provider APIs, Firecrawl calls, device sessions or paid
measurements were performed. The source-retention hold remained intact. No
private data files were rewritten. The full nightly network profile, CI results,
branch-protection settings, and individual source causes behind the writer alerts
were not observed. The public full PR profile and offline private freshness layer
were run locally. No production switch or merge policy was changed. The draft PR
requires independent review and has not been merged.

## Reproducible count probe

Create its directory with `mkdir -p /tmp/model-453-scratch/rule-review`. Save the
following as `/tmp/model-453-scratch/rule-review/freshness_counts.py`, then run
the exact command used for the count evidence:

```bash
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python /tmp/model-453-scratch/rule-review/freshness_counts.py > /tmp/model-453-scratch/rule-review/freshness-counts.json
```

```python
"""Count admitted freshness inputs without printing private records or values."""
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from datetime import date
import json
import logging
from pathlib import Path
from urllib.parse import urlsplit

from decision.sources import load_sources
from scripts import accuracy

PUBLIC = Path('/Users/terbeest/dev/worktrees/model-453')
PRIVATE = Path('/tmp/model-453-scratch/modelspec-data')
DAY = date(2026, 11, 5)
CONFIG = accuracy.load_config(PUBLIC / 'accuracy.yaml').freshness
PUBLIC_SOURCES = load_sources(PUBLIC / 'registry/sources.yaml')
logging.disable(logging.CRITICAL)


def source_ids(row, record):
    ids = set(getattr(row, 'source_ids', ()) or ())
    refs = record.get('sources')
    if isinstance(refs, Sequence) and not isinstance(refs, (str, bytes)):
        ids.update(str(ref['source_id']) for ref in refs
                   if isinstance(ref, Mapping) and ref.get('source_id'))
    return sorted(ids)


def observation_field(row, record, sources):
    ids = source_ids(row, record)
    kind = getattr(row, 'source_kind', None) or record.get('source_kind')
    if not any(getattr(sources.get(sid), 'volatility', 'static') == 'live' for sid in ids) and kind not in accuracy._LIVE_SOURCE_KINDS:
        return 'evidence_date:observed'
    containers = [('record', record)]
    if isinstance(record.get('source_snapshot'), Mapping):
        containers.append(('source_snapshot', record['source_snapshot']))
    refs = record.get('sources')
    if isinstance(refs, Sequence) and not isinstance(refs, (str, bytes)):
        containers.extend(('source_ref', ref) for ref in refs if isinstance(ref, Mapping))
    for key in ('observed_at', 'retrieved_at'):
        for location, container in containers:
            if accuracy._day(container.get(key)) is not None:
                return f'{location}.{key}'
    if accuracy._day(record.get('verified_at')) is not None:
        return 'record.verified_at'
    return 'undated'


def record_rows(snapshot):
    result = {}
    for model, candidates in sorted(accuracy._model_candidates(snapshot).items()):
        for candidate in candidates:
            for domain in snapshot.domain_ids():
                for row in snapshot.evidence_for_domain(candidate, domain):
                    if not (getattr(row, 'verified', False) or getattr(row, 'cited', False)):
                        continue
                    key = row.record_id or f'{model}:{row.benchmark_id}:{row.date}:{row.value}'
                    result.setdefault(key, row)
    return result


public_snapshot = accuracy._load_snapshot(PUBLIC, None, DAY)
public_rows = record_rows(public_snapshot)
public_boards = {row.benchmark_id for row in public_rows.values()}


def count(root, snapshot, private):
    sources = load_sources(root / 'registry/sources.yaml')
    verdict = accuracy.check_freshness(snapshot, as_of=DAY, config=CONFIG, sources=sources)
    rows = record_rows(snapshot)
    boards = defaultdict(Counter)
    hosts = defaultdict(Counter)
    ids_counts = defaultdict(Counter)
    ages = Counter()
    over_window = Counter()
    selected_fields = Counter()
    static_count = 0
    kinds = Counter()
    admission = Counter()
    for row in rows.values():
        live, observed = accuracy._live_observation_date(snapshot, row, sources)
        if not live:
            static_count += 1
            continue
        record = accuracy._evidence_record(snapshot, row)
        kind = 'benchmark_evidence' if 'benchmark_id' in record else 'fact' if 'facet' in record else 'other'
        kinds[kind] += 1
        admission['verified' if getattr(row, 'verified', False) else 'cited_only'] += 1
        age = (DAY - observed).days if observed else None
        state = 'undated' if age is None else 'stale' if age > CONFIG.live_leaderboard_max_age_days else 'fresh'
        ages['undated' if age is None else str(age)] += 1
        over_window['undated' if age is None else str(age - CONFIG.live_leaderboard_max_age_days)] += 1
        selected_fields[observation_field(row, record, sources)] += 1
        board = row.benchmark_id if not private or row.benchmark_id in public_boards else 'other_private_board'
        boards[board][state] += 1
        board_ids = source_ids(row, record)
        known_ids = [sid for sid in board_ids if sid in PUBLIC_SOURCES]
        safe_ids = known_ids + (['other_private_source'] if len(known_ids) < len(board_ids) else [])
        if not safe_ids:
            safe_ids = ['no_registered_source']
        safe_hosts = sorted({urlsplit(str(PUBLIC_SOURCES[sid].url)).hostname
                             for sid in known_ids})
        if len(known_ids) < len(board_ids):
            safe_hosts.append('other_private_source')
        if not safe_hosts:
            safe_hosts = ['no_registered_source']
        for sid in safe_ids:
            ids_counts[sid][state] += 1
        for host in safe_hosts:
            hosts[host][state] += 1
    assert sum(kinds.values()) == verdict.counts['live_readings']
    assert len(rows) == static_count + verdict.counts['live_readings']
    return {
        'status': verdict.status,
        'counts': dict(verdict.counts),
        'reason_counts': dict(Counter(row['reason'] for row in verdict.details)),
        'unique_admitted_domain_records': len(rows),
        'static_excluded_records': static_count,
        'live_fact_kind': dict(kinds),
        'live_admission': dict(admission),
        'live_observation_fields': dict(selected_fields),
        'live_age_days': dict(sorted(ages.items(), key=lambda pair: int(pair[0]) if pair[0] != 'undated' else 100000)),
        'live_days_over_30_day_window': dict(sorted(over_window.items(), key=lambda pair: int(pair[0]) if pair[0] != 'undated' else 100000)),
        'by_board': {key: dict(value) for key, value in sorted(boards.items())},
        'by_public_source_host': {key: dict(value) for key, value in sorted(hosts.items())},
        'by_public_source_id': {key: dict(value) for key, value in sorted(ids_counts.items())},
    }


result = {'assessment_date': DAY.isoformat(), 'window_days': CONFIG.live_leaderboard_max_age_days,
          'public': count(PUBLIC, public_snapshot, False),
          'private': count(PRIVATE, accuracy._load_snapshot(PRIVATE, None, DAY), True)}
print(json.dumps(result, indent=2, sort_keys=False))
```
