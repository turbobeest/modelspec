# MODEL-468-I review fixes

Base `1fa95e40d4218237096be9c0ed42ad2c7281e1df`. `origin/main` was `60a3fe19768345086f9582b499e14cfb8030eea5` and the merge was already up to date. Code commits `9da8d3df5cad090488b0ee2b7ee52479cd10ecd7` and `d51d8f5f01adafb7090ed8bd1ee3230fe9d33bde`. This note is the next commit.

Python 3.14.4, pytest 9.1.1, ruff 0.16.6, Git 2.50.1. Serial pytest, `-q -p no:cacheprovider`, no `-n`. Exit codes were read from the shell. No live watch run, Worker deploy, network call, or full local suite. CI is the full run and is checked after the push.

The generation task tags are the generation and multimodal members of `_TASK_TAGS_THAT_KEEP`: `text-generation`, `image-text-to-text`, `any-to-any`, `audio-text-to-text`. That set also contains `feature-extraction`, `sentence-similarity`, and `text-ranking`. Those three do not keep a missing pipeline. The check uses `_folded`, the same fold `_keeping_task_tag` uses.

Kept when the pipeline tag is another in-scope task, or when the pipeline tag is missing and a generation task tag is present. Rejected when the pipeline tag is missing and no generation task tag is present. Rejected when the pipeline tag is `feature-extraction`, including when a generation tag is also present, because that pipeline tag is the stated task. Catalogue replay cannot test this rule. Cards do not carry Hugging Face artefact tags. The guard is the unit tests. The catalogue assertion in `tests/test_release_scope.py` still matched `_CATALOGUE_SCOPE_EXCEPTIONS`.

## Missing pipeline with a generation task tag

`test_a_generation_task_tag_keeps_a_missing_pipeline_the_way_main_did` failed first. `tag_scope(None, ("text-generation", "interpretability"))` returned `TagDecision(True, "interpretability artefact (tag: interpretability)", "interpretability")`. Main returns `TagDecision(False)`. Exit 1. 1 failed in 0.39s.

Command:

`env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_scope.py::test_a_generation_task_tag_keeps_a_missing_pipeline_the_way_main_did`

After the skip, the same file reported 62 passed in 3.14s. `(None, ("image-text-to-text", "sae"))`, `(None, ("any-to-any", "transcoder"))`, and `(None, ("audio-text-to-text", "sae-lens"))` return `TagDecision(False)`. `(None, ("interpretability", "transcoder"))`, `(None, ("sentence-similarity", "transcoder"))`, `(None, ("text-ranking", "sae"))`, and `("feature-extraction", ("text-generation", "transcoder"))` reject.

## One summary line

`test_interpretability_artefact_reasons_share_one_summary_line` failed first. The summary did not contain `- interpretability artefact: 2`. Exit 1. 1 failed in 0.26s.

`_report_reason` now groups `interpretability artefact (tag: ...)` under `interpretability artefact`. The rejected table uses the original reason, so each row keeps the tag. The new test and `test_huggingface_filter_drops_out_of_scope_tags_derivatives_and_untagged_names` then reported 2 passed in 0.26s.

## Underscore pipeline tag, not changed

`feature_extraction` alone is `TagDecision(True, None, "feature_extraction")`, an unknown kept tag. `feature_extraction` plus `transcoder` rejects. A candidate test, `test_an_underscore_feature_extraction_pipeline_agrees_with_the_unknown_tag_path`, failed on that second call. Exit 1.

Comparing the pipeline tag with `_folded`, the comparison the rest of `tag_scope` uses, made that candidate pass and changed `test_artefact_tags_fold_case_and_underscores`. `tag_scope("Feature_Extraction", ("interpretability",))` returned `TagDecision(True, None, "Feature_Extraction")` instead of the artefact rejection. Exit 1. 1 failed, 2 passed in 0.36s. The existing test was left as it is. The candidate test was not added. The pipeline comparison remains `_artefact_key`.

## Focused run

`env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_scope.py tests/test_release_watch.py tests/test_release_watch_filter.py tests/test_release_watch_precision.py tests/test_release_watch_triage.py tests/test_writer_isolation.py`

Exit 0. 596 passed in 61.13s.

`ruff check release_signals/scope.py scripts/release_watch.py` reported no findings. `ruff check tests/test_release_watch_filter.py` still reports the pre-existing import-order finding. This round did not change that import block.
