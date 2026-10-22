# MODEL-437 predicate warning verification

Changed only `decision/filter.py` and `tests/test_cited_score_warnings.py`.

Direct score predicates now attribute a passing or failing result to rows that
support that result. Unknown predicates contribute no score rows. Relative
references still attribute their selected threshold rows. This changes warning
provenance only, not filtering, scores or recommendations.

Red command, run before the production edit:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_cited_score_warnings.py -k 'score_predicate'
```

Exit 1. Six expected warning assertions failed; eight positive-preservation cases
passed. Output: `predicate-red.txt`.

The same command after the edit exited 0: 14 passed, 31 deselected.
Output: `predicate-green.txt`.

Broader command, run serially after that green:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_cited_score_warnings.py tests/test_cited_scores.py tests/test_cite_only_warning_scope.py tests/test_cite_only_row_warnings.py tests/test_decision_filter.py
```

Exit 0: 182 passed in 1.35 seconds. Output: `filter-warning-green.txt`.

`git diff --check -- decision/filter.py tests/test_cited_score_warnings.py` exited 0.

Coverage includes comparisons, windows, nested negation, soft penalties and a
relative model threshold. Cited-only support still warns, as do failed predicates
used by negation and soft penalties. All commands ran from
`/Users/terbeest/dev/worktrees/model-437`. No GitHub commands or commits were run.
