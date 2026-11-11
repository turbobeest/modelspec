# First-row filing

MODEL-467, design only. The weekly refresh rewrites an evidence row that a
premier card already has. A catalogue card with no row on that board never
receives one, so the job cannot give it a clause 1 place.

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

Resolve the board's model name only through `scripts/premier_slice1.match_index`.
Build that index from the catalogue and `premier/inputs/aliases.json`. An
alias entry wins over a generated slug.

Slug the board name the way the index does, and look up that one key. One
model id files the row. Report a key the index never contained, and file
nothing. `match_index` omits a key that more than one card shares when no
alias settles it. Keep those omitted keys and report them as ambiguous,
separate from names no card carries. Leave the name unfiled. Skip the refresh
matcher's token sort.

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
- The row source URL is that reading's source URL. For Arena, the URL contains the revision the run actually read.
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
fact and can give a model a clause 1 place. A wrong alias would place that
model with no person looking. The run still writes an audit entry per filed
row, with the card, the benchmark, the board name, the match key, the source
URL, and whether the cap stopped later rows. A person merges that pull
request. A value update of a row that already exists stays on the score-only
auto-merge path.

## Cap

The job writes at most 25 new rows in one run. The constant lives in
`scripts/refresh_leaderboards.py`. Further candidates are listed in the report
and not written. Twenty-five covers a week of new cards appearing on boards
the job already reads, and one bad read cannot file a whole board.

## Tests

- A `permits` or `restricts` host can file a row. An `unclear` host, a `forbids` host, and a missing host cannot.
- An exact alias match files one row on an active card outside the premier set. An ambiguous name and an unmatched name are reported and write nothing. A match whose card is inactive writes nothing.
- The guard accepts one new evidence row from the weekly job. It refuses a new card, a change to any other field, a row from another writer, and a row from a non-qualifying host.
- The 25th new row is written. The 26th is reported and not written.
- A diff that only adds these rows is classed for human review. A score-only update of an existing row stays auto-merge.

This ticket does not implement the design.
