# MODEL-460-FU-C verification

Base SHA: `4b10eb58112f92f4ae94fea32f3e5e34cfc29f85` (matches `origin/main` at start).
Implementation SHA: `e944f8a14abc47702f036525e1131e803c997b0f`. This file is the next commit. Its full SHA is the executor completion line.

Environment: Python 3.14.4, pytest 9.1.1, git 2.50.1, gh 2.103.3. Tests ran serially from this worktree with `PYTHONDONTWRITEBYTECODE=1` and `PYTHONPATH=$PWD`. No local full suite.

## Optional social images

The parser accepts a baseline line only when the name is in `ORIGINAL_OPTIONAL_SOCIAL_IMAGES` (42 names). The checked-in list may be a subset. The declared count must equal the list length, and that count must be at or under `OPTIONAL_SOCIAL_IMAGE_CEILING` (42). A same-count replacement is rejected. The checked-in list is unchanged.

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_pipeline.py -k 'optional_social_image_baseline'
```

Red, before the membership check: exit 1. `test_optional_social_image_baseline_rejects_a_replaced_name` did not raise. 1 failed, 4 passed, 83 deselected in 0.37s. The drop, the checked-in list, the declared-count pin, and the growth rejection already passed.

Green: exit 0. 8 passed, 80 deselected in 0.40s (the same filter plus the present-image cases).

## Blog preview

A preview runs the correction date check and the published-revision check before it writes HTML. A future correction date, a missing revision, and an unpublished revision raise `ValueError`. A historical correction on a published revision still previews.

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_blog.py -k 'preview_rejects_invalid_corrections or preview_accepts_a_historical_correction'
```

Red: exit 1. `future_date` and `absent_revision` did not raise. `unpublished_revision` raised `FileNotFoundError` for `r2/breakdown.json` before any correction error. 3 failed, 1 passed, 23 deselected in 0.38s. The historical preview already passed.

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_blog.py -k 'preview or invalid_corrections or corrections_update'
```

Green: exit 0. 9 passed, 18 deselected in 0.37s.

## Delayed-image sentence

`DELAYED_IMAGE_POLICY` in `pipeline/build.py` is the sentence `llms.txt` already used. The pricing page and the homepage dataset description use that constant. Neither contains "about nine months". `cli/modelspec/agent-bundle.json` was regenerated with `python -m pipeline.agent_copy write`. The diff is the `pipeline/pricing.py` hash only: `79d7da2cf887ddfcb973da89b687e49330a812569beba0703e51108144ce7b52`. `python -m pipeline.agent_copy check` exited 0. No other generated file changed.

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_pricing_page.py::test_pricing_page_uses_the_delayed_image_policy_sentence tests/test_structured_data.py::test_homepage_dataset_uses_the_delayed_image_policy_sentence tests/test_llms_txt.py
```

Red, after the constant existed and before the two pages used it: exit 1. Both new tests still found "about nine months". 2 failed, 6 passed in 21.13s.

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_pricing_page.py tests/test_structured_data.py tests/test_llms_txt.py
```

Green: exit 0. 38 passed in 0.76s.

## Focused suite and site build

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_pipeline.py tests/test_blog.py tests/test_agent_ready.py tests/test_entity.py tests/test_pricing_page.py tests/test_structured_data.py tests/test_llms_txt.py tests/test_agent_copy.py tests/test_generated_pins.py
```

Exit 0. 295 passed in 169.03s.

```sh
~/.codex-g2/heavy.sh env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.build --out /tmp/MODEL-460-FU-C-scratch/dist
```

Exit 0. Built pricing page, homepage, and `llms.txt` contain `DELAYED_IMAGE_POLICY` and do not contain "about nine months". The scratch directory was removed after this record.

## Not observed

No local full pytest suite. `web/` was not changed, so npm was not run. Legal pages, the frozen benchmark note, ranking floors, and Worker vars were not edited.

## Follow-ups

A missing baseline image is still tolerated on every page that names that file. The checked-in list records filenames, not the pages those absences were counted on. Limiting each absence to the page it was recorded for needs a new record and a change to `missing_social_images`.
