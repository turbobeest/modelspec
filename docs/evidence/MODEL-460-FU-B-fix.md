# MODEL-460-FU-B execution evidence

Base: `4b10eb58112f92f4ae94fea32f3e5e34cfc29f85`.
Head before this evidence commit: `198ad82dc96e66316213f3a063efa5ce56b700a9`.

Environment: Python 3.14.4, pytest 9.1.1, httpx 0.28.1, PyYAML 6.0.3, Git 2.50.1.
Commands ran from the worktree root. The interpreter is the repository Python named in AGENTS.md.
Pytest prefix: `env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD python -m pytest -q -p no:cacheprovider`.
Tests ran serially, with no `-n`.

## Record text stays one line

Record text placed in a code span is flattened with `" ".join(text.split())` before the span is written. A line break in that text cannot open a heading, a list item, or an outbound link.

`tests/test_release_blog.py -k 'test_record_text_with_a_line_break_is_one_code_span or test_record_text_with_a_blank_line_does_not_open_a_heading_or_list or test_record_text_with_a_line_break_before_a_link_adds_no_outbound_link'` recorded `3 failed, 66 deselected`, exit 1, before the change. One case missed the single-line span, one still produced a heading line, and one raised `ValueError: outbound link is not a breakdown source`. After the change, `-k record_text` recorded `5 passed, 64 deselected`, exit 0. Commit `3a78af0dcd2b5b20863d889086d020c07bc4b13b`.

## Post-level output guard

`guard_output` runs on the breakdown object and again on the finished post. Two quality flags whose letters form an excluded publisher only when joined are refused by the post check. The object check accepts the same breakdown.

`tests/test_release_blog.py -k test_render_cli_rejects_excluded_text_joined_only_in_the_post` recorded `1 passed, 69 deselected`, exit 0, with both calls present. Removing only `guard_output(b.sources, post)` in `release_blog/render.py` recorded `1 failed, 69 deselected`, exit 1 (`assert 0 == 2`, and the post was written). The call was restored. The same selector then recorded `1 passed, 69 deselected`, exit 0. Commit `0e28d4ea60450ba16e891c4922eeac777fe7a940`.

## Backtick replacement

A backtick inside record text is replaced with an apostrophe (`'`).

`tests/test_release_blog.py -k test_record_text_replaces_a_backtick_with_an_apostrophe` recorded `1 passed, 70 deselected`, exit 0. Replacing the backtick with an empty string instead recorded `1 failed, 1 passed, 69 deselected`, exit 1, together with `test_record_text_with_a_backtick_and_a_digit_is_one_code_span` (that older test passed). The replacement was restored. The apostrophe selector then recorded `1 passed, 70 deselected`, exit 0. Commit `ec53d37d368f5b73f2a93b0d550656856e1e67a2`.

## Malformed release_url

A `release_url` that is not an absolute `https` URL with a host is ignored. It is not a primary source. A homepage that is a usable primary is still used, and `main()` returns 0. When that `release_url` is the only primary field, the run raises the same `ValueError` as a listing that omits the field (`does not name a primary provider source`). A prohibited `https` release URL still raises `ValueError`. `RequiredSourceError` is still not a `ValueError`.

The selectors were `test_malformed_release_url_is_not_a_primary_source` and `test_malformed_release_url_matches_a_missing_field`, covering a relative path, a `javascript:` value, an `https` URL with no host, a non-string value, and a 100000-character string. A sibling model row in the same payload carries the long string.

Before the change, both selectors recorded `10 failed, 133 deselected`, exit 1. The success-path cases raised `ValueError: source is not an HTTP URL` (relative path, `javascript:`, non-string, and the long string) or fetched the no-host URL. The missing-field cases returned without raising, because the fixture had no catalogue card and the lab never resolved. After the catalogue card was added, and before the fix, the four short missing-field cases recorded `4 failed, 139 deselected`, exit 1: three message mismatches against `does not name a primary provider source`, and a fetch of the no-host URL. After the change, `-k 'malformed_release_url or prohibited_release_url or models_dev_cannot_make_x'` recorded `12 passed, 131 deselected`, exit 0. Commit `557ae0e579fa0c0d52c98ec9665995bbadfa93f4`.

## Unreadable JSON-LD

A JSON-LD block nested deeper than `_JSON_LD_MAX_DEPTH` (64), or holding an integer longer than `_JSON_LD_MAX_INTEGER_DIGITS` (1000 digits), is skipped. Any error from `json.loads` on that block is also skipped. A later readable block on the same page is still read. The tested inputs are an integer of 5000 digits and a block nested 2000 levels.

`tests/test_release_signals.py -k 'json_ld_with_a_long_integer or json_ld_nested_past'` recorded `2 failed, 143 deselected`, exit 1, before the change. The integer case raised `ValueError` for a 5000-digit conversion. The nested case finished `uncertain` because the deep block was read. After the change, the same selector plus `production_shaped_models_dev or exact_visible_identity_drafts or bad_required_source` recorded `21 passed, 124 deselected`, exit 0. Commit `198ad82dc96e66316213f3a063efa5ce56b700a9`.

## Focused runs

```bash
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD python -m pytest -q -p no:cacheprovider tests/test_release_blog.py tests/test_release_signals.py tests/test_release_signal_prices.py tests/test_release_watch_filter.py
```

That command recorded `284 passed in 52.48s`, exit 0.

The same four files were run again with `socket.socket.connect` and `socket.create_connection` raising `OSError` and counting each call. That run recorded `284 passed in 49.98s`, exit 0, and 0 connect attempts.

## Not observed

No full local suite, site build, Worker memory probe, production fetch, deployment, or release tag was run. No ranking floor, legal text, price, plan, Worker variable, production switch, frozen catalogue file, source-terms class, or contract version was changed.

## Follow-ups

None. Each of the five items is enforced as written.
