# MODEL-481: two faults in the weekly price re-read's readers

Public note. Providers, models and prices in the tests and in this note are invented.
The tests are `tests/test_price_reread_readers.py`; the code is `scripts/price_reread.py`
(`reread_fact`, the report) and `decision/verify.py` (`OfferingPriceExtractor`,
`read_not_disclosed`).

Round 2 replaced the first design. Round 1 confirmed "still not disclosed" from a table
with no column for the kind, and matched a row type exactly. The review showed that an
absence cannot be confirmed from a page (a column named `Asynchronous`, a footnote
sentence, a `Prompt caching` column, a second table and a partial render all fooled it),
that the confirmation wrote a `verified` record for it, and that exact matching dropped
real labels such as `Input (text, image, video, audio)`.

## Fault 1: a `not_disclosed` price reported unreadable every week

A price filed `not_disclosed` (value null) on a page with no cell for that kind skipped
every reader, so the re-read reported `unreadable` and raised an alert each week although
nothing had changed. The re-read now says what it saw and claims nothing.

What the re-read reports for a `not_disclosed` fact:

| What the page shows | Outcome |
| --- | --- |
| a cited region did not resolve, or the fetch failed | `unreadable` or `unreachable`, as before (an alert) |
| the page did not read as a price table, or the model is not on it | `unreadable`, as before |
| the region read, the model is on it, and a number reads for the kind | `needs_review`, reason starts `disclosed: page now states a value` (an alert); nothing written |
| the region read and a cell for the kind says not available | `needs_review`, reason says the page states it is not available and a person may re-file it as `not_offered`; never the "disclosed" prefix |
| the region read, the model is on it, and nothing reads for the kind | new outcome `not_disclosed_no_value`: own count, own report table (fact, source and region read); not unchanged, not unreadable, not an alert |

The new outcome writes nothing: no verification record, no queue event, no change to the
fact. It does not say the price is still undisclosed. It only stops treating "nothing to
read" as a failure for a fact that claims nothing. What it does not catch: a page that now
states the price under a label or in a place the reader does not know (a column with
another name, a sentence, a second table, a part of the page the cited region does not
hold). That fact stays quiet here, and only a person reading the page finds it, which is
why the report lists each source and region read, so a spot check is cheap.

Other states: `unknown` is not tracked (`tracked_facts` skips it) and is not re-read.
`not_offered` is re-read like any filed fact, as on `main`: an "N/A" cell or a missing
column is `unreadable`, a number now read is `needs_review`. A `known` fact whose column
vanished stays `unreadable`.

## Fault 2: one fact read from two cells

In the Vertex-style branch (price kind in a `Type` column) a wanted kind ending in
"output" accepted any row type containing "output", so `output` also read the Batch
Output row and `batch_output` the Output row. `verify` passes when any one reading
matches, so a changed price whose other cell equalled the filed number read `unchanged`.

Rule now: a row's type label (normalised as before) fits the wanted kind when it names
that kind and no other. It may equal the expected type or extend it
(`Input (text, image, video, audio)`, `Text output (response and reasoning)`). Words
that name a kind:

| Kind | Words |
| --- | --- |
| input | input, inputs, prompt |
| output | output, outputs, response, completion |
| batch | batch, flex, priority |
| cache | cache, cached, caching |
| write | write, writes |
| read | read, reads |

A label must name exactly the kinds its wanted kind needs: `input` {input}; `output`
{output}; `batch_input` {batch, input} (or {input} on a table whose columns are already
batch or flex); `batch_output` likewise; `cached_input` {cache} with the word `hit`, or
{input} when the table has no `Cache hit` row. Several rows that fit must print the same
amount (rows with a different region or other label cell are kept apart), otherwise the
reader raises and the fact is `unreadable` with a reason saying the cells disagree.

The column-header scan (an AWS-style table with one column per kind) was the same
pattern: a header containing `input tokens` counted, so `Cache write input tokens`
could be read as input, and the first such header won. Now a header counts only when it
names the kind's required words and no other kind (`cached_input`: cache and read, and
input is allowed), and every header that counts must hold the same cell.

## Reader branches examined

| Branch of `OfferingPriceExtractor.extract` | Pattern | Verdict |
| --- | --- | --- |
| Heading tables, `simple_label` | exact label equality, first match returned | safe: exact |
| "price per btok per mtok" row | exact label equality | safe: exact |
| Prose caching price | exact model name, first match returned | safe |
| Named sections (Standard / Batch / Flex) | line starts with the label, mode must match, first match then stop | safe: one reading per section, mode-gated |
| `Batch`-qualified subject rows | header contains the kind, first batch column wins | safe: one reading per row |
| Labelled prices inside one cell (Azure-style) | label regex with word boundary, one match per cell; every non-batch column is read for a non-batch kind | not this fault; reading several non-batch columns for one kind (Pricing and Priority) is a related any-match weakness, not changed here |
| Vertex-style `Type` column | contains | same fault, fixed (kind words, agreement) |
| Column-header scan | substring of the header, first match then break | same pattern, fixed (kind words, agreement) |
| Band-tiered, peak-price, grouped-header | exact column choice or exact names | safe |

## Measured on real facts

One fetch each of ten registered price sources (Type-column pages, the column-header
page, rendered and plain pages) was re-read in memory on `main` and on this branch, with
nothing written, for every price fact that cites them: 185 facts. No fact that read
`unchanged` on `main` reads anything else on this branch (103 stay `unchanged`). The only
differences are eight `not_disclosed` facts that moved from `unreadable` to
`not_disclosed_no_value`. The 45 facts read by the Type-column branch and the 15 read by
the column-header scan all stay `unchanged`. The other `unreadable` facts are `unreadable`
on both.
