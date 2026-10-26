# Draft a Model Week

`scripts/model_week.py` compares committed catalogue records across a seven-day
UTC interval and writes separate public and private Markdown drafts. It does
not build a site, create a blog post, publish, or contact a social platform.
Jamie must approve publication under ModelSpec's name and decide which fresh
facts may enter a public publication bundle.

Run the command from the public code checkout with a complete local history
and an `origin/main` remote-tracking ref. Fetch `origin main` before running
if that ref needs refreshing. The generator makes no network requests.
The private input is optional. For the week beginning 2026-10-13:

```bash
env PYTHONPATH="$PWD" /Users/terbeest/dev/modelspec/.venv/bin/python \
  scripts/model_week.py \
  --week 2026-10-13 \
  --private-repo /tmp/model-434-scratch/executor/modelspec-data \
  --out-dir /tmp/model-434-scratch/executor/model-week-2026-10-13
```

The output directory must be new and outside every Git worktree. The command
refuses existing directories and paths that resolve through symlinks into a
repository. It creates the output directory
with owner-only access and writes `public.md` and `public-appendix.md`. When a
private checkout is supplied, it also writes `private.md` and
`private-appendix.md`. Every file has owner-only permissions. A refusal exits
with status 2 and prints a generic diagnostic that does not quote private input.

Each summary includes at most 10 entries per category by default, followed by
"and N more" for omitted entries and a link to its full-list appendix. The
appendix retains all eligible entries with their citations. Limits do not
change the ordering, full category counts, or withheld-change counts.
Repeat `--limit 'CATEGORY=N'` to override individual categories, for example:

```bash
--limit 'Models added=5' --limit 'Benchmark movers=15' --limit 'Lineup changes=0'
```

Category names are exactly those listed under Coverage below. Limits must be
nonnegative integers. Zero hides that category's entries in the summary while
preserving its overflow count and appendix. Unspecified categories retain the
default of 10. The same limits apply independently to public and private drafts.

Successful stdout is JSON containing category counts and withheld-change counts
for each section. It contains no model identities, scores, prices, source URLs,
or private draft text. Public review material may include `public.md` and its
appendix. Describe the private section only by its counts; never attach
`private.md` or `private-appendix.md` to a public PR, log, artifact, or site.

## Inputs and dates

The CLI fixes its public input to the checkout containing the script. It reads
`refs/remotes/origin/main` explicitly and refuses if that ref is missing.
Local-only commits and a different or detached `HEAD` cannot supply public
records. It also ignores working-tree edits, `MODELSPEC_DATA_DIR`, and
inherited `GIT_*` environment variables. The
public source boundary is the committed frozen data image that feeds public
exports. It is not the decision engine's verification-admission boundary, and
the generated draft is not a signed or verified engine export. The generator
changes no snapshot fields or export formats.

The private checkout's `HEAD` supplies only the private draft and appendix.
All fresh private records stay out of both public files, including records for
model IDs or values that also occur in the public image. No private value
participates in public selection, comparison, wording, citations, or counts.

`--week` is the first day of the interval, with no weekday restriction. For
`2026-10-13`, the interval begins at 2026-10-13 00:00:00 UTC and ends just before
2026-10-20 00:00:00 UTC. The command follows first-parent history from public
`origin/main` and private `HEAD`, selecting the latest commit before each
boundary. Both checkouts need complete history and a baseline before the
requested start.

The draft reports net differences between those two committed trees. A change
that was reverted before the endpoint does not appear. Commit timestamps date
catalogue observations, not provider announcements. Each entry cites its before
and after catalogue revision and UTC commit date, plus the upstream sources
recorded with the relevant evidence or fact. New models, catalogue status
changes, and premier membership changes also cite the card's
`sources.provider_docs_url` when present, where cards record provider release,
announcement, or documentation links. Membership-only edits read the unchanged
member cards from the corresponding history endpoint. Cards without that link
retain their catalogue citation. Evidence dates and price-effective dates
remain visible as record values.

These are catalogue records, not independently checked provider claims. An empty
public draft means that the frozen public catalogue has no eligible net changes
for that interval. It does not mean that no models or prices changed elsewhere.

## Coverage

The draft has four categories:

- Models added: identities newly recorded in model cards. Identity edits and
  removals appear under lineup changes.
- Benchmark movers: changes to dated evidence observations. Comparisons require
  matching model, benchmark, source, version, evaluated model name, unit, and
  measurement configuration. A changed configuration appears as separate
  observations. The draft does not infer ranks, improvements, or equivalent
  evaluation conditions.
- Price and plan changes: structured API price facts and an explicit allowlist
  of subscription facts. Price records retain `effective_from` and
  `effective_until`; distinct effective windows remain distinct records.
- Lineup changes: catalogue status, lifecycle facts, structural subscription
  coverage, and membership in the tracked premier set.

The subscription allowlist covers availability, price, price in CNY, billing
period, covered models and families, access surfaces, and structured allowance
fields for a relative plan, multiplier, window, and tokens. Free-text plan
quotes and allowance descriptions are excluded. Legacy flat benchmark scores
are also excluded.

Missing or excluded sources withhold a change and increment the withheld count.
The source guard refuses excluded providers of evidence and X/Twitter URLs,
including card links. Both summary and appendix use the same filtered entries.
The generator reads local structured records only; it fetches no pages and
retains no source-page copies.

This is a record-change digest. It does not detect a scheduled price taking
effect without a catalogue edit, or a source-registry-only change with no change
to a tracked catalogue file.

## Private handling

Keep the private clone, generated private draft and appendix in local scratch storage.
Do not place either in this public checkout, another Git worktree, `blog/`, or
a site output directory. The command does not produce a combined draft and
has no publication command.

After review, delete the private clone, `private.md` and `private-appendix.md`
from the scratch directory. Remove other temporary private copies from the same run too.
Retain only the public draft and private counts in public review material.
