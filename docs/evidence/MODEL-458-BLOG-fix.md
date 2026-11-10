# MODEL-458-BLOG execution evidence

Base: `a29bf9c6d12b0ca093b42a2f662e0a53150014ca`.
Implementation SHA: `779d99eaf1d729fbba8daef6fc484b718d8c5ec9`.
The evidence commit is the PR head.

Environment: Python 3.14.4, pytest 9.1.1, httpx 0.28.1, PyYAML 6.0.3, Git 2.50.1.
Commands ran from `/Users/terbeest/dev/worktrees/model-458-blog`.
Pytest prefix: `env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider`.
Tests ran serially, with no `-n`.

## AUD-14-F4

A reading whose unit differs from the lab figure stays off the shared claims chart. The chart states that unit reason. The table still shows the reading's value. Same-unit readings, including a different setup, still share the chart.

`tests/test_release_blog.py -k test_not_comparable_reading_does_not_receive_shared_scale` recorded `1 failed, 46 deselected`, exit 1, before the change. The chart section had two bars. After the change, `tests/test_release_blog.py tests/test_release_pipeline.py` recorded `80 passed`, exit 0. Commit `e00a03dfe9985b1e046fccbc998d0bdbc227d36f`.

## AUD-14-F5

The post shows a lab limitation, an independent-reading limitation, and a quality flag beside that claim or reading. A limitation that contains a digit stays inside a code span. Each caveat line cites its record in a footnote.

`tests/test_release_blog.py -k test_qualified_readings_keep_limits_and_flags_in_post` recorded `1 failed, 47 deselected`, exit 1, before the change. The breakdown held the three strings and the post omitted them. After the change, the same two files recorded `81 passed`, exit 0. Commit `ecaa9312bdb1ad5ba7d809fe8ab53abf7f6f8ee2`.

## AUD-14-F11

A zero cost renders as `$0.00` with finite chart coordinates. An all-zero non-percent claims chart uses a positive axis length. A free offering beside a paid offering keeps both costs.

`tests/test_release_blog.py -k 'test_zero_cost_offering_renders or test_mixed_free_and_paid_offerings_keep_their_costs or test_all_zero_non_percent_claims_stay_finite'` recorded `2 failed, 1 passed, 48 deselected`, exit 1, before the change. The two failures were `ZeroDivisionError`. The mixed-cost test passed. After the change, the two files recorded `84 passed`, exit 0. Commit `824573b19d3e88e655cb99d13ee7d76048ff0adb`.

## AUD-14-F12

The render command rejects an excluded host, a signal-only source URL, and excluded publisher text before it creates a post or a chart. A valid serialized breakdown still renders.

`tests/test_release_blog.py -k render_cli` recorded `7 failed, 1 passed, 51 deselected`, exit 1, before the change. The failures returned exit code 0 and wrote the post and the charts. The valid breakdown passed. After the change, `tests/test_release_blog.py tests/test_release_pipeline.py tests/test_removed_sources.py` recorded `138 passed, 1 skipped`, exit 0. Commit `779d99eaf1d729fbba8daef6fc484b718d8c5ec9`.

## Final focused run

On that implementation commit, `tests/test_release_blog.py tests/test_release_pipeline.py` recorded `92 passed`, exit 0.

## Not observed

No full local suite, site build, Worker memory probe, production request, deployment, or release tag was run. No ranking floor, legal text, price, plan, Worker variable, production switch, frozen catalogue file, source-terms class, or contract version was changed.
