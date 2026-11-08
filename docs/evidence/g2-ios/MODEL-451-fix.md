MODEL-451 execution evidence

Base SHA: `6815544116839f991c10904772e7357f12d5b566`.
Final implementation SHA: `8b4a7efa37b4924409770918c8c5a4723a498b5a`.
Branch: `model-451-codex`.
Worktree: `/Users/terbeest/dev/worktrees/model-451`.

The final handoff commit adds this report on top of the implementation SHA.
Its hash cannot be embedded in its own contents. The PR body and executor result
record the exact final head; `git rev-parse model-451-codex` resolves it locally.

The daily seeder now recognizes four reviewed serving identities and excludes
the Gemini rolling alias by its exact models.dev ID. Canonical mappings still
require a card on disk. The alias has a separate reasoned skip and requires no
canonical card. No substring or display-name matching was added.

All commands below ran from the worktree unless a different directory is shown.
Tests ran serially. No full local suite ran.

Verified source identities

The identity audit read these five cards from modelspec-data commit
`68f3a7748f8695e0bcb67ad3e38d55302f487897`, the head reviewed in REV-data99.

| Card path under models/ | Exact models.dev identity | Source fields |
| --- | --- | --- |
| deepseek/deepseek-v4-1-flash-1017.md | mistral/deepseek-v4-1-flash-1017 | Mistral availability model_id at line 468; models_dev_url at line 814 |
| google/gemini-pro-latest.md | google/gemini-pro-latest | version at line 7; models_dev_url at line 818 |
| mistral/mistral-large-4-0-8.md | mistral/mistral-large-4-0-8 | version at line 7; models_dev_url at line 816 |
| moonshot/kimi-k3-1-pro-highspeed.md | moonshotai/kimi-k3.1-pro-highspeed | version at line 7; models_dev_url at line 816 |
| zhipu/zai-glm-5-3-flash.md | mistral/zai-glm-5-3-flash | Mistral availability model_id at line 471; models_dev_url at line 817 |

The three cards without populated availability IDs preserve the raw ID in
`version`. The seeder assigns `version=raw.get("id", "")` and constructs
`sources.models_dev_url` from the source provider. The Kimi source ID contains
a dot, which its filename does not preserve.

The audit cloned the private repository without checking out its files:

```sh
mkdir -p /tmp/model-451-scratch/verify-ids
env GIT_TERMINAL_PROMPT=0 git clone --no-checkout \
  https://github.com/turbobeest/modelspec-data.git \
  /tmp/model-451-scratch/verify-ids/modelspec-data
```

It used this extraction with
`/Users/terbeest/dev/modelspec/.venv/bin/python`:

```python
import json, subprocess, yaml

repo = "/tmp/model-451-scratch/verify-ids/modelspec-data"
sha = "68f3a7748f8695e0bcb67ad3e38d55302f487897"
paths = [
    "deepseek/deepseek-v4-1-flash-1017",
    "google/gemini-pro-latest",
    "mistral/mistral-large-4-0-8",
    "moonshot/kimi-k3-1-pro-highspeed",
    "zhipu/zai-glm-5-3-flash",
]
for path in paths:
    raw = subprocess.check_output(
        ["git", "-C", repo, "show", f"{sha}:models/{path}.md"],
        text=True,
    )
    card = yaml.safe_load(raw.split("---", 2)[1])
    ids = {
        key: value.get("model_id") or value.get("model_id_on_platform")
        for key, value in card["availability"].items()
        if isinstance(value, dict)
        and (value.get("model_id") or value.get("model_id_on_platform"))
    }
    print(json.dumps({
        "card": path,
        "version": card["version"],
        "availability_ids": ids,
        "models_dev_url": card["sources"]["models_dev_url"],
    }))
```

The audit also used `git cat-file -e <revision>:models/<canonical>.md`.
At the clone's main revision `c26a2d7b67039dd0ed2490cd740766680c9e454d`,
the DeepSeek, Mistral Large 4 and Zhipu canonical cards existed, with exit 0.
Kimi K3.1 Pro was absent, with exit 128, but existed at the reviewed head,
with exit 0. The audit deleted its clone with `shutil.rmtree` and verified
that `/tmp/model-451-scratch/verify-ids` no longer existed. No private card
or retained source copy was added to this public repository.

Red-first reproduction

The tests were added before any production-code or registry changes.
The regression seam is the seeder's CLI survey using a fixture catalogue and
a substituted models.dev response. It runs the real identity check and
attribution code without making network or provider calls.

Each parameter of
`test_reviewed_daily_rows_are_skipped_with_reasons` represents one defect:

| models.dev identity | Expected survey output after the fix |
| --- | --- |
| mistral/deepseek-v4-1-flash-1017 | SKIP mistral/deepseek-v4-1-flash-1017 (already deepseek/deepseek-flash) |
| google/gemini-pro-latest | SKIP google/gemini-pro-latest (not a model: rolling alias with no fixed model identity) |
| mistral/mistral-large-4-0-8 | SKIP mistral/mistral-large-4-0-8 (already mistral/mistral-large-4) |
| moonshotai/kimi-k3.1-pro-highspeed | SKIP moonshotai/kimi-k3.1-pro-highspeed (already moonshot/kimi-k3-1-pro) |
| mistral/zai-glm-5-3-flash | SKIP mistral/zai-glm-5-3-flash (already zhipu/glm-5-3-flash) |

Command, exit 1:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_seed_models_dev.py -k 'reviewed_daily_rows or new_ids_from_the_reviewed_orgs' --tb=short
```

Captured red output:

```text
FFFFF.....                                                               [100%]
=================================== FAILURES ===================================
_ test_reviewed_daily_rows_are_skipped_with_reasons[mistral/deepseek-v4-1-flash-1017-already deepseek/deepseek-flash] _
tests/test_seed_models_dev.py:339: in test_reviewed_daily_rows_are_skipped_with_reasons
    assert f"    SKIP {models_dev_id} ({reason})" in output
E   assert '    SKIP mistral/deepseek-v4-1-flash-1017 (already deepseek/deepseek-flash)' in "Fetching models.dev API...\n  Fetched 1 providers from API\n  SKIP: provider 'openai' not found in API\n  SKIP: provi...t-119/test_reviewed_daily_rows_are_s0/models\n======================================================================\n"
_ test_reviewed_daily_rows_are_skipped_with_reasons[google/gemini-pro-latest-not a model: rolling alias with no fixed model identity] _
tests/test_seed_models_dev.py:339: in test_reviewed_daily_rows_are_skipped_with_reasons
    assert f"    SKIP {models_dev_id} ({reason})" in output
E   assert '    SKIP google/gemini-pro-latest (not a model: rolling alias with no fixed model identity)' in "Fetching models.dev API...\n  Fetched 1 providers from API\n  SKIP: provider 'openai' not found in API\n  SKIP: provi...t-119/test_reviewed_daily_rows_are_s1/models\n======================================================================\n"
_ test_reviewed_daily_rows_are_skipped_with_reasons[mistral/mistral-large-4-0-8-already mistral/mistral-large-4] _
tests/test_seed_models_dev.py:339: in test_reviewed_daily_rows_are_skipped_with_reasons
    assert f"    SKIP {models_dev_id} ({reason})" in output
E   assert '    SKIP mistral/mistral-large-4-0-8 (already mistral/mistral-large-4)' in "Fetching models.dev API...\n  Fetched 1 providers from API\n  SKIP: provider 'openai' not found in API\n  SKIP: provi...t-119/test_reviewed_daily_rows_are_s2/models\n======================================================================\n"
_ test_reviewed_daily_rows_are_skipped_with_reasons[moonshotai/kimi-k3.1-pro-highspeed-already moonshot/kimi-k3-1-pro] _
tests/test_seed_models_dev.py:339: in test_reviewed_daily_rows_are_skipped_with_reasons
    assert f"    SKIP {models_dev_id} ({reason})" in output
E   assert '    SKIP moonshotai/kimi-k3.1-pro-highspeed (already moonshot/kimi-k3-1-pro)' in "Fetching models.dev API...\n  Fetched 1 providers from API\n  SKIP: provider 'openai' not found in API\n  SKIP: provi...t-119/test_reviewed_daily_rows_are_s3/models\n======================================================================\n"
_ test_reviewed_daily_rows_are_skipped_with_reasons[mistral/zai-glm-5-3-flash-already zhipu/glm-5-3-flash] _
tests/test_seed_models_dev.py:339: in test_reviewed_daily_rows_are_skipped_with_reasons
    assert f"    SKIP {models_dev_id} ({reason})" in output
E   assert '    SKIP mistral/zai-glm-5-3-flash (already zhipu/glm-5-3-flash)' in "Fetching models.dev API...\n  Fetched 1 providers from API\n  SKIP: provider 'openai' not found in API\n  SKIP: provi...t-119/test_reviewed_daily_rows_are_s4/models\n======================================================================\n"
=========================== short test summary info ============================
FAILED tests/test_seed_models_dev.py::test_reviewed_daily_rows_are_skipped_with_reasons[mistral/deepseek-v4-1-flash-1017-already deepseek/deepseek-flash]
FAILED tests/test_seed_models_dev.py::test_reviewed_daily_rows_are_skipped_with_reasons[google/gemini-pro-latest-not a model: rolling alias with no fixed model identity]
FAILED tests/test_seed_models_dev.py::test_reviewed_daily_rows_are_skipped_with_reasons[mistral/mistral-large-4-0-8-already mistral/mistral-large-4]
FAILED tests/test_seed_models_dev.py::test_reviewed_daily_rows_are_skipped_with_reasons[moonshotai/kimi-k3.1-pro-highspeed-already moonshot/kimi-k3-1-pro]
FAILED tests/test_seed_models_dev.py::test_reviewed_daily_rows_are_skipped_with_reasons[mistral/zai-glm-5-3-flash-already zhipu/glm-5-3-flash]
5 failed, 5 passed, 14 deselected in 0.56s
```

All five new-ID controls passed before the fix. They cover new DeepSeek,
Gemini, Mistral, Kimi and Zhipu IDs on the same source-provider pages,
including an ID containing `latest` and a new Kimi speed-tier ID.

Green verification

After the implementation, the first complete seeder run reported
`1 failed, 23 passed in 0.43s`, exit 1. All five regressions passed.
The remaining failure was the old assertion that every registry target
exists in the frozen public catalogue. Mistral Large 4 and Kimi K3.1 Pro
belong to the private catalogue. The test now asserts the exact set of
absent targets, preserving the existence checks for every earlier target.

Additional tests verify all four mappings with the canonical card absent
and then present, an alias skip with no canonical card in either update
mode, exact source-ID matching, the actual alias write path, and required
nonempty review reasons. The write-path test clears provider credentials.

Command, exit 0:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_seed_models_dev.py
```

```text
...................................                                      [100%]
35 passed in 0.55s
```

Related suites, with provider credentials removed from the test environment:

```sh
env -u TYPESAFE_API_KEY -u TEXT_MODEL_API_KEY PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_seed_models_dev.py tests/test_research_failure_safety.py tests/test_research_workflow.py tests/test_attribution.py tests/test_guide_staleness.py tests/test_license_defaults.py tests/test_removed_sources.py
```

Exit 0:

```text
203 passed, 1 skipped in 63.58s (0:01:03)
```

The skip is the existing built-distribution check, which requires
`MODELSPEC_DIST`. The tracked-file source guard and catalogue/export source
checks passed.

The report was then staged and checked with:

```sh
env -u TYPESAFE_API_KEY -u TEXT_MODEL_API_KEY PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_removed_sources.py::test_no_tracked_file_names_a_removed_source
git diff --check
git diff --cached --check
```

The report source guard exited 0 with `1 passed in 33.53s`. Both final
diff checks exited 0. The staged diff check first caught a trailing blank
line in this report, which was removed before the successful check.

Tool versions were Git 2.50.1, Python 3.14.4, pytest 9.1.1, PyYAML 6.0.3,
Pydantic 2.13.5, httpx 0.28.1 and GitHub CLI 2.102.0.
Versions were read with `git --version`, `gh --version`, `sys.version`
and `importlib.metadata.version`.

Implementation commit:

```sh
git diff --check
git add scripts/seed_models_dev.py scripts/models_dev_known_identities.yaml tests/test_seed_models_dev.py
git commit -m 'MODEL-451: stop re-proposing reviewed models.dev aliases' -m 'Co-Authored-By: ChatGPT Codex <noreply@openai.com>'
git rev-parse HEAD
```

All exited 0. A separate read-only review of the diff found no blocking issue.

Handoff commands:

```sh
git add docs/evidence/g2-ios/MODEL-451-fix.md
git commit -m 'MODEL-451: record reproduction and verification evidence' -m 'Co-Authored-By: ChatGPT Codex <noreply@openai.com>'
env CI_LOCAL_SKIP=1 GIT_TERMINAL_PROMPT=0 git push -u origin model-451-codex
```

The draft PR is created from `/tmp`, with its prepared body passed as a file:

```sh
gh pr create -R turbobeest/modelspec --draft --base main --head model-451-codex --title 'MODEL-451: skip reviewed models.dev aliases' --body-file /tmp/model-451-scratch/executor/pr-body.md
```

Rollout and observation limits

This change only reaches daily research after modelspec-data's
`.engine-pin` includes it. MODEL-446 handles that pin update. The Kimi
highspeed mapping additionally waits for `moonshot/kimi-k3-1-pro` to
exist in the data catalogue, as the registry has always required.

The assertions about source identity come from the reviewed cards and
REV-data99, not a fresh external release audit. No live models.dev response,
production daily run, engine-pin update, or hosted CI outcome was observed.
The full local suite and site builds were not run, per the ticket's focused
test requirement. Worker exports and serving code were not changed, so the
private-data Worker memory probe was not applicable.

The PR is submitted as a draft. External cross-model review remains pending.
