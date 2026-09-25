# Release-chart fixtures

One YAML file per page. `scripts/chart_check.py` rebuilds every bar from the
evidence rows on the cards and writes a report outside the repository. Nothing
here is exported. Do not put chart images in this directory: the image is the
publisher's, and the file belongs in the chart cache, named by its sha256.

A fixture:

- `page_url`, `publisher`, `read_on` (ISO date).
- `phase` — the reading pass this page belongs to: `phase1`, `phase2a`,
  `phase2b-1`, `phase2b-2`, `phase2b-3`, or `phase2b-4`. The confirmation
  tally groups by it.
- `charts`: each chart has `title`, `footnotes`, `competitor_numbers`
  (`official_reports`, `vendor_run`, or `unstated`), `readings`
  (`reader`, `date`), and `bars`.
- An image chart has `image_url` and `image_sha256` (64 hex digits, no file
  extension). An HTML or Markdown table is `kind: html_table`. A number stated
  in prose, with no chart behind it, is `kind: text`.
- `document_sha256` on the page is the sha256 of a PDF the page was read from.
  A second reading names that PDF file. The manifest maps the file name to
  this digest. Reconcile does not match a PDF name by similarity.
- `needs_reading: true` means this pass did not transcribe bars. That is not a
  green bar.

Each bar:

- `model_as_labelled` — the label on the page.
- `model_id` — a card id such as `openai/gpt-6-astra`, or null when no card exists.
- `benchmark_id` — a page under `benchmarks/`, or a score key already on a card.
- `score`, `unit`, `printed` (true when the digit is printed, not estimated).
- `configuration` — the setting that would change the number.
- `role` — `subject` when the model is the publisher's own, `evaluated` on an
  independent evaluator's page, otherwise `competitor`.
- `metric` — optional. Absent means the benchmark's headline score. A
  non-headline metric such as `tasks_completed` is `other_metric`.
- `benchmark_as_labelled` — required when `benchmark_id` is null. That bar is
  `no_benchmark_page`.
- `known_mismatch` — optional `{ticket, note}` for a bar that disagrees with
  the card and is waiting on its own fix. Remove it once the bar is not a
  mismatch.
- `disputed` — optional list of `{reader, value}` when two readings disagree.
- `resolution` — optional, in place of `disputed`. `rule: two_of_three` and
  `readings` (`reader`, `value`). A value counts only when two independent
  readers agree within the printed precision. The bar's `score` is that value.
  A third reading that agrees with neither leaves the bar `disputed`.
- `confirmed_by` — the readers whose reading of this bar agrees with the
  stored score. A pair that agrees names both readers. A two-of-three
  resolution names the two who agree. A bar only one reader recorded names
  that reader. Every name is one of the chart's `readings`. One name does
  not fail the check.

`score` is written on its own line so the printed precision survives YAML
(`78.2` is ±0.05, `78` is ±0.5).

Every bar is compared with evidence rows of the same benchmark cited from
this `page_url` first (a trailing slash does not matter). Only a bar with no
same-source row falls through: a subject bar is `not_held`, and a competitor
or evaluated bar follows `competitor_numbers`. `official_reports` is compared
with the rival card's `provider_self_report` rows only: a match is `matched`, a
different self-report is `mismatched`, and no self-report row is `not_held`,
with the card's other rows shown as context. `vendor_run` is a gap. `unstated`
stays unresolved.

Two or more bars for the same model, benchmark, and metric are sibling
configurations. When a same-source row equals one of them, that bar is
`matched` and the others are `other_configuration`. When it equals none of
them, all of them are `mismatched`. A different unit is `unit_differs`. An
unprinted bar is low confidence, never a match. Two readings that disagree
are disputed. A third reading settles the bar when it agrees with one of
them within the printed precision, and the score is that agreed value. A
third reading that agrees with neither leaves the bar disputed. One reading
is `single_read`, which does not fail the check.

`python scripts/chart_check.py reconcile --reader-b <dir> --out <dir>`
compares a second reading. `--write-fixtures` records that reader and marks
disagreements `disputed`.

## In CI

`Check evidence against release charts` in `.github/workflows/chart-check.yml`
runs on every pull request and is a required check on `main`. A pull request
that changes no model card and no file in this directory reports "nothing to
check" and passes. The job runs `python scripts/chart_check_pr.py --base origin/main`.

The job classifies evidence rows the pull request adds or changes.

A row is `verified` when a fixture bar from the same page agrees, within the
printed precision, for the same model and benchmark, and that bar's
`confirmed_by` names at least two readers. Sibling configurations count as
agreement when any one of them matches. When the agreeing bar names fewer
than two readers, the outcome is `verified_single_read`.

These block the job:

- `mismatch`, a same-source bar for that model and benchmark that does not agree.
- `disputed`, a matching bar that is still disputed.
- A bar added or changed in a fixture the pull request adds or changes, when
  `confirmed_by` names fewer than two distinct readers and neither the bar nor
  its chart has a non-empty `single_read_reason`. A reason on the chart covers
  every bar in that chart.
- A `disputed` bar on such a fixture.
- A `resolution` that does not satisfy the two-of-three rule.

These do not block:

- `verified_single_read`. Warning. The same bar blocks when the pull request
  also adds or changes it, by the rule above.
- `no_bar`. The fixture exists and has no bar for this model and benchmark. Warning.
- `no_fixture`. The page has no fixture yet. Warning, for now.
- `no_fixture_dataset`. The source is machine-readable. Informational.
  MODEL-111 layer 2 checks those sources.
- A removed bar. Informational.

A bar is changed when its score, unit, labels, `model_id`, `benchmark_id`,
metric, configuration, role, or `confirmed_by` differs from the base. Bars
match on the fixture, the chart title, `model_as_labelled`, the benchmark id
or label, the metric, and the configuration. When more than one bar shares
that key, the check pairs those bars in the order they appear in the chart.

The report groups blocking bars by fixture and chart and gives each chart's
count. It lists at most 50 of those bars.

Fixtures the pull request does not change are left alone. A single-read bar
on an unchanged fixture does not block. A single-read bar left unchanged does
not block when another bar in the same fixture changes.

To clear `no_fixture`, add a fixture for that page with two independent
readings. MODEL-113 new-model pull requests are the ones this warning is for.
The new card cites a page, and this directory does not have that page yet.
