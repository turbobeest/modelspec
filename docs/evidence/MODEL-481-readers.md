# MODEL-481: two faults in the weekly price re-read's readers

Public note. Providers, models and prices in the tests and in this note are invented.
The tests are `tests/test_price_reread_readers.py`; the code is `scripts/price_reread.py`
(`reread_fact`) and `decision/verify.py` (`OfferingPriceExtractor`,
`undisclosed_confirmation`).

## Fault 1: a `not_disclosed` price reported unreadable every week

A price fact filed `not_disclosed` (value null) on a table that has no column for that
price kind (for example no Batch column) was read like any other fact. No reader had a
cell to compare, so `verify` returned `skipped`, the re-read reported `unreadable` and
raised an alert every week, although nothing had changed.

Rule now. In `reread_fact`, when `verify` returns `skipped` for a fact in state
`not_disclosed`, `undisclosed_confirmation` checks the same cited regions. The fact is
confirmed (`unchanged`, reason `still not disclosed`, a dated verification logged) only
when every cited region resolved and one region shows, in the same read:

1. a table with a header row, and the model's rows are all that header's width;
2. the model's row, found by the exact subject match `extract` uses for the other kinds;
3. a dollar amount on that row;
4. another price kind of that model read by `extract` as a number;
5. no column, label or row type for the claimed kind (for a batch kind: no cell
   anywhere in the region that says "batch"; for another kind: no header naming it).

A table with a `Type` column is never confirmed (stays unreadable). When the page now
states a value, the existing mismatch path proposes it and the reason starts
`disclosed: page now states a value`; it is an alert and nothing is written.

What the re-read reports per fact state:

| State | Before | After |
| --- | --- | --- |
| `known` | read and compared; a missing column is unreadable | unchanged |
| `not_disclosed` | `unreadable` when no cell; `needs_review` when a value is now read | `unchanged` ("still not disclosed") on the positive evidence above; `needs_review` ("disclosed: page now states a value") when a value is read; otherwise `unreadable` or `unreachable` as before |
| `not_offered` | read like any fact: a "N/A" cell or a missing column is `unreadable`; a value now read is `needs_review` | unchanged: no confirmation is added |
| `unknown` | not tracked (`tracked_facts` skips it), not re-read | unchanged |

An explicit not-available cell in a column that is present is not confirmed for
`not_disclosed`: the page states "not available", which is a `not_offered` claim, so it
stays `unreadable` for a person to re-file.

## Fault 2: one fact read from two cells

In the Vertex-style branch (price kind in a `Type` column) a wanted kind ending in
"output" accepted any row type containing "output", so `output` also read the Batch
Output row and `batch_output` also read the Output row. `verify` passes when any one
reading matches, so a changed price whose other cell equalled the filed number would
read `unchanged`.

Rule now: the row type must equal the kind's expected type exactly (`output`, `batch
output`, `input`, `batch input`, `cache hit`). If the page prints that row more than
once for one model, the readings must be the same amount, or the reader raises and the
fact is `unreadable` with a reason saying the cells disagree.

## Reader branches examined for fault 2

| Branch of `OfferingPriceExtractor.extract` | Pattern | Verdict |
| --- | --- | --- |
| Heading tables, `simple_label` | exact label equality, returns the first match | safe: exact |
| "price per btok per mtok" row | exact label equality | safe: exact |
| Prose caching price | exact model name, first match returned | safe |
| Named sections (Standard / Batch / Flex) | line starts with the label, mode must match, first match then stop | safe: one reading per section, mode-gated |
| `Batch`-qualified subject rows | header contains the kind, first batch column wins | safe: one reading per row |
| Labelled prices inside one cell (Azure-style) | label regex with word boundary, one match per cell; every non-batch column is read for a non-batch kind | one reading per cell, so not this fault; reading several columns for one kind (for example Pricing and Priority) is a related any-match weakness, not changed here |
| Vertex-style `Type` column | `startswith` or contains | same fault, fixed (exact match, agreement for repeats) |
| Column-header scan (AWS-style) | substring of the header, first match then break | safe: one reading per row |
| Band-tiered tables | exact column choice by `_band_price_column` | safe |
| Peak-price tables | exact kind labels | safe |
| Grouped-header tables | separate reader, exact model name | not changed |

## Existing test whose expectation changed

`tests/test_price_reread.py::test_a_value_the_page_did_not_state_is_reviewed_not_written`
now expects the reason to start `disclosed: page now states a value; was not_disclosed;`.
It did not rely on the contains fault; only the wording of the alert gained the outcome
name.

## What the confirmation can still match wrongly

- A region that now holds a different table for the same model with no Batch column,
  while the real batch table sits outside the cited region. The check cannot see
  outside the region. It stays within the cited region by design, and the weekly
  diff of the region shows the change.
- A table of another model family in the same region: its rows are never the claim
  model's, so they do not confirm; they only fail to disprove.
- A row matched by a looser name: not possible, the match is the reader's exact name
  match.
