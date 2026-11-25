# MODEL-467-WRITER-FU

Base `478dc59960f85d9af38c3cc12eaacd455f0f6ab3` on `model-467-writer-fu`.

Commits on this branch:

- `f97f28baa460f9b2117fa5805b04d94c181f52cf` drops ISO dates and ticket ids from the stale check, and stops watching the old rank.
- `a00af4befa8bb0813c15b127bb14886c123495fb` pins every character outside a checked number token and an ISO date.
- `026f4f5072132250f31afdf97adf88c267727cc7` runs the writer on each Arena fixture row and passes that before and after to the guard.

The head is the commit that adds this file.

Environment: Python 3.14.4, pytest 9.1.1, PyYAML 6.0.3. Tests are serial and offline.

## Red, then green

`test_an_old_rank_equal_to_a_date_part_or_ticket_id_is_written` ran against the unchanged writer.

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_leaderboard_refresh.py::test_an_old_rank_equal_to_a_date_part_or_ticket_id_is_written --tb=line
```

Exit 1. 3 failed. Each reason was `configuration still quotes the previous reading`. The rows were old rank 11 with publication date 2026-11-02, old rank 2 with publication date 2026-11-02, and old rank 191 beside `MODEL-191`.

After that change, the same test and the nearby writer tests passed. Exit 0. 7 passed in 0.39s.

`test_score_only_check_refuses_an_unchecked_figure_on_an_arena_row` ran before the guard change.

Exit 1. 5 failed. The guard returned ok for `32k` to `16k`, `v2` to `v3`, `32.` to `16.`, serial `1234567` to `7654321`, and revision `aaaaaaa` to `bbbbbbb`. `test_score_only_check_accepts_a_writer_shaped_arena_sentence` passed on that same run.

After the guard change, those refusal cases, the writer-shaped sentence, and the existing figures test passed. Exit 0. 17 passed in 0.40s.

The three focused files then passed. Exit 0. 179 passed in 9.44s. That run was before the fixture-through-guard test.

`test_the_guard_accepts_the_writers_arena_fixture_row` passed on its first run. Exit 0. 8 passed in 0.52s.

The three focused files on this branch:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_leaderboard_refresh.py tests/test_arena_revision.py tests/test_model_160_evidence.py
```

Exit 0. 187 passed in 10.15s.

## Not observed

No network. No weekly catalogue run. The per-class skip split from the earlier proof stays withdrawn until the next real run.
