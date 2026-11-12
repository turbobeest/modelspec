# First-row filing

MODEL-467, design only. The weekly refresh rewrites an evidence row that a
premier card already has. A catalogue card with no row on that board never
receives one, so the job cannot give it a clause 1 place.

`run(add_missing=True)` is a separate first-row path. It appends a row when
exactly one board row matches the card's display name, version, or model id,
and existing rows for that benchmark supply one unit and one source kind.
The release-signal path for a new model calls it, scoped to that model id.
`scripts/model_233_evidence.py` calls it too. The weekly workflow does not,
and the CLI has no `--add-missing` flag. This design is the weekly job's own
filing: every active card, the matcher below, a cap of 25, and human review.
It does not replace `add_missing`.

## Boards

A board qualifies when `scripts/refresh_leaderboards.py` already reads it and
the reader host is `permits` or `restricts` in the data repository file
`registry/source-terms.json`. The key is the canonical host of the fetch URL,
the same host key `scripts/admission_drafter.py` uses.

The ticket names two such readers. Arena comes from the Hugging Face dataset
`lmarena-ai/leaderboard-dataset`. MTEB comes from
`mteb-leaderboard-backend.hf.space`. A host classed `unclear` or `forbids`,
and a host absent from the file, receives no new row on this path. This
design does not change a host's class.

## Identity

`scripts/premier_slice1.match_index` is not the matcher for this filing.

That function builds keys from `slug(display_name)` and `slug(model_id)`,
each with `strip=False` and `strip=True`. One model id for a key wins at
once. A shared key is not omitted. The function keeps undated model ids,
those whose id contains no `20` plus six digits, then cards whose status is
`active`, then a card whose `strip=True` slug of the model id or display
name equals the key. It omits the key only when more than one card remains.
Alias entries then overwrite the key.

`slug(strip=True)` drops a trailing effort token. That list includes
`thinking` and `non-thinking`. It also drops a trailing `20` plus six
digits, and a trailing year, month, and day. A board row for a dated
variant or a `thinking` variant can land on the base card.

`slug(strip=False)` still deletes text in parentheses and any `org/` prefix.
`Claude Opus 4.1 (thinking)` becomes `claude-opus-4-1`. `otherlab/Foo-1`
becomes `foo-1`. The comparison never sees the dropped text.

First-row filing refuses a board name that contains parentheses. It refuses
a board name whose publisher prefix is not the card's lab. The publisher
prefix is the text before the first `/` when the name has one and is not a
URL. The card's lab is the text before the first `/` in its model id. A name
with no publisher prefix is not refused on this rule. A refused name is
unmatched. Report it and write nothing.

A name that passes those checks is normalised with `slug(strip=False)`.
File the row only when that key equals `slug(strip=False)` of exactly one
card, on its display name or its model id. Any other result is unmatched.
Report it and write nothing. Do not use `match_index`. Do not use the
refresh matcher's token sort.

File only when the matched card's status is `active`. Report an inactive card
and leave it unchanged.

## Scope

The job considers every active card in the catalogue. It creates no card.

## Diff guard

`check_score_only` refuses a change in the evidence row count. The weekly job
in the data repository calls that check before it opens a pull request. The
guard must allow one added evidence row on a card that already exists when
every condition below holds.

- The weekly job wrote the row in this run.
- The benchmark is one that run read, and the reader host is `permits` or `restricts`.
- The row `source_url` is the form the refresh matches on. For Arena that is the dataset root `https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset`. The revision that was read stays in the audit record and the retained projection.
- The collector is the weekly refresh collector.
- Existing rows change only the score, dates, id, and source snapshot the guard already allows.
- Card prose is unchanged.
- The only new files are the verification log lines the refresh already appends.

The guard refuses a new card, a deleted card, an identity or licence edit, a
row from any other writer, and a row whose host is `unclear`, `forbids`, or
missing.

## Merge class

Human review. A score-only refresh auto-merges on the day it opens because
the guard proved that no evidence row was added. See
`docs/method/coverage-slo.md` under `refresh-pr-merged`. A first row is a new
fact and can give a model a clause 1 place. An exact normalised name that
points at the wrong card would place that model with no person looking. The
run still writes an audit entry per filed row, with the card, the benchmark,
the board name, the match key, the source URL, and whether the cap stopped
later rows. A person merges that pull request. A value update of a row that
already exists stays on the score-only auto-merge path.

## Cap

The job writes at most 25 new rows in one run. The constant lives in
`scripts/refresh_leaderboards.py`. Further candidates are listed in the report
and not written. Twenty-five covers a week of new cards appearing on boards
the job already reads, and one bad read cannot file a whole board.

## Tests

- A `permits` or `restricts` host can file a row. An `unclear` host, a `forbids` host, and a missing host cannot.
- An exact normalised name files one row on an active card outside the premier set. An alias that is not that name, a name shared by more than one card, and an unmatched name are reported and write nothing. A match whose card is inactive writes nothing.
- The guard accepts one new evidence row from the weekly job. It refuses a new card, a change to any other field, a row from another writer, and a row from a non-qualifying host.
- The 25th new row is written. The 26th is reported and not written.
- A diff that only adds these rows is classed for human review. A score-only update of an existing row stays auto-merge.

This ticket does not implement the design.
