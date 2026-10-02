# Weekly data trust audit

MODEL-267 measures served invariant violations and disagreements with freshly
read primary sources. The public engine contains the audit and synthetic tests.
The private data repository contains the weekly workflow, reports and defect log.

```sh
python -m scripts.data_trust data --data-dir /path/to/modelspec-data --json
python -m scripts.data_trust sample --data-dir /path/to/modelspec-data --n 60 --seed 2026-W40 --json
python -m scripts.data_trust run --data-dir /path/to/modelspec-data --n 60 \
  --output-dir /path/to/modelspec-data/reports/data-trust \
  --defect-log /path/to/modelspec-data/reports/data-trust/defects.jsonl --summary-only
```

The data-split overlay composes private data with public vocabulary. Missing
private data never falls back to the frozen public image. The audit writes no
cards, offerings, source copies or verification status.

## Two populations

The served tier uses `decision.snapshot.collect_repo` and `_compile`, the same
collector and admission rules as `build_from_repo`. It includes independently
verified v2 facts with resolving sources, admitted benchmark evidence, metered
and subscription facts, hardware-fit and parameter facts, and licence, origin
and provider-policy facts. Unknowns, quarantined records, excluded sources and
unclassified evidence do not enter. All callable catalogue models and archived
records are covered, without limiting the audit to the featured lineup.

Record counts and structural counts are separate. Models, offerings, sources,
benchmark domain tags and registry vocabulary are checked as serving inputs.
Structural identities need no fabricated provenance. Computed decisions depend
on admitted inputs; they are not additional independently collected claims.
The five-nines accuracy target applies to served claims. Only served invariant
errors fail the job, including a failure to collect or compile those inputs.

The other tier is legacy card scalars and filed records the compiler does not
admit. Report only their per-field provenance coverage, grouped by field family.
Null and empty values make no claim. Card-wide source lists cannot establish
which source supports a field. `benchmarks.scores` never enters the decision
snapshot. Legacy range diagnostics are listed with their benchmark classes,
but they produce no invariant errors, defect entries or job failure.

## Served invariants

Every finding has `id`, `field`, `rule` and `severity`. Errors cover provenance,
read dates, schemas, resolving references, finite numeric values, numeric
bounds, benchmark bounds and discount ordering. Read dates come from the
compiler's winning verification for the current value hash. Expired field SLOs,
cross-source contradictions, unbounded benchmark metrics and benchmark unit
disagreements are warnings.

An unknown benchmark date is permitted by `_Compiler.add_evidence` and by
ordinary decisions. `LoadedSnapshot.evidence(after=...)` excludes undated rows
when a caller asks for a date filter, and the capability fit skips undated rows.
The audit checks malformed or future stated dates; it does not require a date
that admission permits to be absent.

`offering_or_verified_open_weights` is a warning while MODEL-266's engine rule
in PR #456 is unmerged. Promote it to an error when that rule merges. The report
states this dependency. An offering route or independently verified, sourced
open weights satisfies it. A subscription model-coverage fact establishes an
offering route too.

Freshness follows `scripts/slo/targets.yaml`: benchmark readings age after
30 days; prices and subscription facts after 7 days. Speed checks respect the
published `in_force` switch. Fields without a published SLO need a read date but
have no invented expiry. Price bounds are 0 to 1,000,000 in the declared USD
unit; token/context bounds are 0 to 100,000,000. Benchmark bounds come from each
board's metric, and missing upper bounds cannot establish range compliance.

## Sampling and reader coverage

Sample only served claims with a primary URL, without replacement. A seeded
round-robin draw balances joint strata of field type, provider and read age.
Ages are 0 to 7 days, 8 to 30 days, over 30 days and undated. Groups and rows are
shuffled with the seed. If strata outnumber sample slots, randomly selected
strata receive the slots. The default seed is the audit date's ISO week.

Fresh reads preserve collectors' source labels, published model aliases, units
and conditions when the collected value hash still matches the served record.
All cited primary URLs are attempted, with each URL fetched once per run.
Plain HTTP uses the existing deterministic extractors, including for facts
originally verified by an LLM. Existing Open LLM, Arena, MTEB and supported HTML
board projections are rebuilt from fresh bytes. Raw HTML uses the HTML
normaliser even when the retained source was a text projection. No Firecrawl
or LLM runs. Arena's existing reader needs the optional `pyarrow` dependency.

Artificial Analysis and Zapier are excluded, including redirect destinations.
URLs containing credentials or secret query parameters are refused. Ordinary
queries and fragments are valid source URLs. Fetch failures and unreadable
regions or values are `unreadable` with reasons, never evidence of mismatch.
A value, identity or stated condition disagreement is `mismatched`.
For live evidence dated by evaluation, a date-only change to today's observation
date is `matched` with reason `observation_date_advanced`. Re-reading a live row
advances its observation date; it does not make an unchanged value wrong.
The MTEB projector adds the audit's read date rather than a primary row date;
that generated date cannot disprove a stored publication date either.
Static row dates and differences in value or other qualifiers still count.

Reader coverage is a separate capability metric over every served record.
An existing deterministic verification proves a reader for its field and cited
region. Other records are probed against their retained regions with the same
LLM-free extractors. Missing retained copies leave capability unknown. Coverage
is reported overall and per field; it does not certify that a live page remains
readable. Reader gaps and unreadable sample results never fail the job. The
calibration goal is at least 40 readable claims in the sample of 60.

The error estimate is mismatches divided by matched plus mismatched claims.
The Wilson 95% interval uses that readable denominator; zero readable claims
means no estimate. This is a pooled stratified sample, not a population-weighted
accuracy estimate. Differential readability limits inference. Even sixty
readable matches leave a 95% upper error bound around 6%, so this sample cannot
demonstrate five-nines accuracy.

## Private artifacts and job result

The dated Markdown and format-version-2 JSON contain both tiers, reader
coverage, strata, range classes and sampled outcomes. JSON references a
compressed JSONL companion preserving all served findings. Reports contain
no stored values, source URLs, fetched bytes or exception text.

The defect log appends each served invariant error and source mismatch once
per rule, subject and field. Files rotate at 32 MiB. Existing entries and guard
assignments remain intact. Entries have a root-cause guess, first-seen date and
an initially null guard. A guard becomes non-null only after a preventive fix
has a test. Finding a defect does not resolve it. An uncommitted first-run log
that classified legacy coverage gaps as defects must be replaced by the
calibrated report before submission; committed history is append-only.

Run the workflow only in `turbobeest/modelspec-data`. It uses that repository's
`GITHUB_TOKEN`, publishes aggregate summaries, opens a private report PR, then
fails on served invariant errors. Source mismatches alone do not affect exit
status. Sample subjects and detailed reports must never enter public PRs or
public Actions logs.
