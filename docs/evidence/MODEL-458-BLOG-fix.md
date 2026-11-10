# MODEL-458-BLOG execution evidence

Base: `a29bf9c6d12b0ca093b42a2f662e0a53150014ca`.
Implementation SHA: `779d99eaf1d729fbba8daef6fc484b718d8c5ec9`.
Round 1 evidence commit: `58a4460bab01e8cd6c24ed183f2a17e4f1853a9a`.

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

## Round 2

Merged `origin/main` as `e1ac49d0decdbda062ead8af315816a8beff424b` before the other edits. The five focused files recorded `257 passed, 1 skipped`, exit 0.

Pytest prefix, from the worktree root: `env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider`.

### Omitted-scale reason

The existing chart test asserts `unit fraction is not percent`. A second test, `test_omitted_note_states_the_subcategory_difference`, uses a reading whose `differs_in` is `unit` and `subcategory` and asserts `subcategory differs`.

On the unchanged renderer those two tests recorded `2 passed, 58 deselected`, exit 0. With the unit clause replaced by the words "a different unit", the same selector recorded `2 failed, 58 deselected`, exit 1. Both missed `unit fraction is not percent`. With the extra-difference clause disabled, the selector recorded `1 failed, 1 passed, 58 deselected`, exit 1. `test_omitted_note_states_the_subcategory_difference` missed `subcategory differs`. The renderer was restored. The selector then recorded `2 passed, 58 deselected`, exit 0. Commit `0eb5ec60896386c08d686aac7caccb1f1e59664a`.

### Caveat lines

`test_each_reading_limitation_cites_its_own_record` puts two limitations on one claim. Each line appears and cites its own footnote. `test_lab_limitation_appears_without_readings` puts a lab limitation on a row with no readings. The lab line appears with the claim's footnote.

On the unchanged renderer the selector recorded `2 passed, 60 deselected`, exit 0. Keeping only the first reading recorded `1 failed, 1 passed, 60 deselected`, exit 1 (`StopIteration` in `test_each_reading_limitation_cites_its_own_record`). Emitting the lab line only when the row has readings recorded `1 failed, 1 passed, 60 deselected`, exit 1 (`StopIteration` in `test_lab_limitation_appears_without_readings`). The renderer was restored. The selector then recorded `2 passed, 60 deselected`, exit 0. Commit `f6bb569833bd44b60e9039cdc19757f2f2b129fd`.

### Record text

Record text is one code span. A backtick in that text is written as an apostrophe (`'`), so the span stays one span. The site renderer then puts the quotation in one `code` element and emits no anchor for an autolink or a markdown link inside it.

Before that change, `test_record_text_with_a_backtick_and_a_digit_is_one_code_span` failed: the caveat item's `20` sat outside `code`. `test_record_text_with_markup_and_no_digit_stays_literal` failed with `ValueError: outbound link is not a breakdown source`. `test_refused_word_in_an_independent_reading_blocks_the_render` passed. The three-test selector recorded `2 failed, 1 passed, 62 deselected`, exit 1. A record's text can block a draft.

After the change, `tests/test_release_blog.py` recorded `65 passed`, exit 0. The blog fixture at `tests/fixtures/blog/posts/2026-09-26-alpha/r1/breakdown.json` rendered with exit 0 before and after, and the post bytes were identical. The fixture's limitation fields are null. Commit `1954b327a47f7d367068a438aa00c8d6b8df7316`.

### Cost-chart proportions

`test_mixed_free_and_paid_offerings_keep_their_costs` asserts the paid bar is wider than the free bar, no wider than the 300-wide bar span, and wider than half that span.

On the unchanged renderer the selector recorded `1 passed, 64 deselected`, exit 0. With `_extent` returning `1.0` for every input, the selector recorded `1 failed, 64 deselected`, exit 1 (`assert 33.6 > (300.0 / 2)`). The renderer was restored. The selector then recorded `1 passed, 64 deselected`, exit 0. Commit `cfd06168b3bff53189d4e4cf174068d8edf1adf1`.

### Excluded text the post does not render

`test_render_cli_rejects_excluded_text_the_post_does_not_show` puts excluded publisher text in `headline.rule`. The rendered post does not contain that text. The render command exits 2 and writes no post and no charts directory. Both `guard_output` calls stay.

On the unchanged writer the selector recorded `1 passed, 65 deselected`, exit 0. With the breakdown-dump `guard_output` call removed, the selector recorded `1 failed, 65 deselected`, exit 1 (`assert 0 == 2`), and the command wrote the post and the charts. The call was restored. `tests/test_release_blog.py -k render_cli` then recorded `9 passed, 57 deselected`, exit 0. Commit `9febec31a4dda322d45566d68c1f0c0670bd79b1`.

### Round 2 focused run

The five files `tests/test_release_blog.py tests/test_release_blog_platforms.py tests/test_release_pipeline.py tests/test_removed_sources.py tests/test_blog.py` recorded `264 passed, 1 skipped`, exit 0.

No full local suite, site build, Worker memory probe, production request, deployment, or release tag was run for this round. No ranking floor, legal text, price, plan, Worker variable, production switch, frozen catalogue file, source-terms class, or contract version was changed.
