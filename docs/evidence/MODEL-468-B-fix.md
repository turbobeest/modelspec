# MODEL-468-B processing evidence

Branch `model-468-b`. Draft pull request 1049. The head is the commit that last updates this file. Read it with `git log -1 --format=%H -- docs/evidence/MODEL-468-B-fix.md`.

This branch merged `origin/main` after pull request 1048. That merge brought the watcher unwrap. This pull request does not edit `release_signals/watch.py`.

Focused pytest was serial, with `-q -p no:cacheprovider` and no `-n`. Exit codes were read directly. Commands below use the repository virtualenv through `env PYTHONPATH=$PWD python -m pytest`.

## What the pull request does

An existing card stays existing when a later source cannot restate the lab. Zero models.dev rows are `not_listed`. Several matching rows stay uncertain. A signal id that starts with `test-` returns `ignored` and writes no card, offering, or audit. An out-of-scope name returns `out_of_scope` before resolve.

A not-listed signal whose identity is new uses its own first-seen page when that host is a registered lab host. The result sets `models_dev` to `not_listed` and `primary_host` to that host. `evidence_urls` omits the models.dev URL, and the card omits `last_scraped_models_dev`. A listed row still records the models.dev scrape date and URL.

`resolve_signal` matches exact aliases only. A dotted successor such as `Orbit 6.1`, with only `Orbit 6` carded, resolves as `new` and does not write the predecessor's card.

Scope rules read the normalised model name. A lab name is not part of that match. A token `image` is out of scope unless the name also has `vl`, `vlm`, `vision`, `omni`, `multimodal`, `embed`, `embedding`, `embeddings`, `captioning`, `clip`, or `text`. The name `text-to-image` stays out of scope through its own rule.

A registered host matches exactly. A subdomain matches only when the registry entry is written as a wildcard (`*.example.com`). Hosts for the signal's provider text are united with hosts for the resolved lab slug.

The pending job reserves up to 7 signals and up to 3 due re-checks, backfills the unused reserve, and keeps the total at `MAX_RELEASE_SIGNAL_WORK_ITEMS`. A group larger than its slots starts at `GITHUB_RUN_NUMBER` modulo the group size and wraps. Per-job artifact names use `strategy.job-index` with a fixed prefix per kind. The result, price-copy, and audit uploads set `overwrite` to true.

The review job sets `GH_REPO` to `github.repository`. It opens one issue titled `release signals needing identity review`. Uncertain results stay under "Signals whose identity could not be resolved." A `closed_unmerged` result is listed under "New-model pull requests closed without merge". An empty heading is omitted. The issue still opens when the only results are `closed_unmerged`. `ignored` stays out of the issue.

The process job has `contents: write` and `pull-requests: write`. It does not have `issues: write`. No process step runs `gh label` or `gh issue`. The review job has `issues: write` and creates the `new-model` label.

A re-check row stored by `acknowledge` is `signal_id`, `due`, `day`, `pr_url`, and `signal`. The earlier result is on the audit record only. The pending job therefore still gives those re-checks a matrix slot, including when the first result was `ignored` or `out_of_scope`. No worker file was edited.

## Review fixes

### Trailing suffix

`test_a_dotted_successor_stays_new_when_only_the_predecessor_is_carded` failed with `assert 'existing' == 'new'`. `test_a_dotted_name_does_not_attach_to_unsuffixed_cards` failed with `assert 'uncertain' == 'new'`. 2 failed, 1 passed, exit 1. After the suffix branch was removed, 4 passed in 0.53s, exit 0. Commit `94d01bd3`.

### Artifact names

`test_per_job_artifact_names_keep_signal_punctuation_out` failed because a rendered name contained `:`. 1 failed in 0.45s, exit 1. After names used `strategy.job-index`, that test and the cap, hourly, price, engine-pin, and writer-isolation tests passed, 427 passed in 15.55s, exit 0. Commit `2b0ce4d1`.

### Review job repository

`test_review_job_gh_calls_name_the_repository` failed because `GH_REPO` was absent from the label command's environment. 1 failed in 0.45s, exit 1. After the job environment was set, 3 passed in 0.51s, exit 0. Commit `b71b7723`.

### Pending rotation

`test_pending_selection_rotates_instead_of_blocking_the_queue` failed with `assert ['s00', 's01', ...] == ['s01', 's02', ...]`. 1 failed in 0.47s, exit 1. After the rotating window, 4 passed in 0.86s, exit 0. Commit `49b36658`.

### Scope

`test_named_modalities_are_out_of_scope_and_ordinary_names_stay_in` failed with `assert 'robotics or embodied checkpoint' is None`. `test_review_names_follow_the_normalised_model_name` failed with `assert 'speech' == 'image generation'`. 2 failed, 1 passed in 0.33s, exit 1. After rules used the normalised model name, 3 passed in 0.32s, exit 0. Commit `02926348`.

### Lab page without a models.dev citation

`test_not_listed_uses_a_registered_lab_page_and_names_other_host_classes` failed with `KeyError: 'models_dev'`. 1 failed in 1.37s, exit 1. After the result named the gap and the host, 6 passed in 1.08s, exit 0. Commit `0f5882eb`.

### Lab hosts

`test_a_lab_host_matches_exactly_or_a_registered_wildcard` failed with `assert 'lab' == 'unregistered'`. `test_a_display_provider_uses_the_resolved_lab_hosts` failed with `assert 'uncertain' == 'new'`. 2 failed, exit 1. After exact-or-wildcard matching and the resolved lab slug, those tests plus the not-listed regressions passed, 4 passed in 0.74s, exit 0. The release-signal file then passed, 189 passed in 1.41s, exit 0. Commit `36e5d89e`.

### Roll-up and process permissions

`test_the_roll_up_lists_a_closed_unmerged_result_under_its_own_heading` failed with `assert 'New-model pull requests closed without merge' in 'Signals whose identity could not be resolved.\n\n- s-a: two cards\n'`. `test_the_process_job_cannot_open_issues` failed with `assert 'issues' not in {'contents': 'write', 'pull-requests': 'write', 'issues': 'write'}`. 2 failed in 0.59s, exit 1. After the heading and the permission removal, those tests plus the existing roll-up, repository, cap, and hourly tests passed, 6 passed in 0.75s, exit 0. Commit `d7a2a2c0`.

## Earlier processing, still in force

The first processing commits on this branch keep an existing card when the source refresh misses the lab, treat zero models.dev rows as not listed, accept a lab page that names the model, ignore `test-` ids, and skip out-of-scope names. The first check of pull request 1049 failed `tests/test_ci_workflows.py::test_shard_timings_cover_the_current_suite_and_browser_modules` because `tests/test_release_scope.py` had no row in `tests/shard_durations.json`. That row is 0.003 seconds. The same check's decide-page browser failure was on an old-board link and a `#s=` hash. This branch does not change the decide page.

## Round 3

The base of this round was `4df22b1852fd0e44741212bfd05d653ee000c407`. The branch was one commit behind `origin/main`. Merge commit `1ef38c16111337cc50e63729910d3eaddc82e3de` brought `8d34a8c44f210b6baf5a4406ad27f47739b04caa` (MODEL-467, pull request 1047). That merge edits `tests/test_release_signals.py` only to accept keyword arguments on the leaderboard stub.

Python 3.14.4. pytest 9.1.1. Git 2.50.1.

### Process label

`test_the_process_job_cannot_open_issues` failed because a process step still ran `gh label create`. 1 failed in 0.55s, exit 1. After that step was removed, that test and `test_review_job_gh_calls_name_the_repository` passed. 2 passed in 0.48s, exit 0. Commit `d9558caac89055990859e80d6fa2bd503c84cf96`.

### Image token

`test_an_image_token_keeps_embedding_captioning_and_text_models` failed with `assert 'image generation' is None` for `amazon.titan-embed-image-v1`. 1 failed in 0.36s, exit 1. After `embed`, `embedding`, `embeddings`, `captioning`, `clip`, and `text` joined the image-token exceptions, that test and the two existing name tests passed. 3 passed in 0.35s, exit 0. Commit `1839db97833593249657508800e2948beeaad09f`.

`amazon.titan-embed-image-v1`, `blip-image-captioning-large`, `nomic-embed-image-v2`, and `image-text-to-text-7b` stay in scope. `flux-3-image-klein`, `gpt-image-2-6`, `minimax-h3-image`, and `text-to-image-xl` stay out of scope.

### Artifact overwrite

`test_per_job_artifact_names_keep_signal_punctuation_out` failed because the result upload had no `overwrite` key. 1 failed in 0.51s, exit 1. After the result, price-copy, and audit uploads set `overwrite` to true, 1 passed in 0.48s, exit 0. Commit `0f76235dca7b02a8d5b4d4bcb283ee0bf6f9614f`. The pending-work upload is unchanged.

### Focused suite

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_signals.py tests/test_release_scope.py
```

195 passed in 1.78s, exit 0.

## Not observed

No full pytest suite. No site build. No worker memory probe. No production fetch. No Linear write. No Ruff run. The round-2 check is not in this file. The check of pull request 1049 after this push is not in this file.
