# Dated comparisons for a job

MODEL-219 part 2 adds `/compare/` and worked comparisons from the frozen
public image. It reuses the use-case templates, snapshot, engine decisions,
HTML shell, engine values, and image date.

## Pair selection and measured size

Start with the answered, indexable use-case templates. For each, take the
engine's `bands.leader` and compare it with the other members of `best`, in
the engine's band order, followed by the first eligible member of `rest`.
Keep at most five pairs. Both entries must have capability estimates with
at least one measured benchmark on every weighted capability. Never select
`thin`, an unanswered template, or a pair without objective evidence.

Every pair contains the leader because the engine's `p_beats_leader` and
band membership establish that comparison. Two other members of the best
band need not be tied with each other. Selection does not sort by cost,
brand, popularity, or a second ranking formula.

Measured at base `7908f238465ea88f0568738f13d8e8bbec949deb`, the public image
date is `2026-09-23`. Its 18 answered templates yield 40 comparison pages
across 17 jobs, plus the index. `retrieval-private` has no eligible second
model. The counts by template are:

| Template | Pages |
| --- | ---: |
| coding-best | 4 |
| coding-balanced | 2 |
| budget-coding | 1 |
| coding-private | 2 |
| maths | 2 |
| maths-reasoning-budget | 3 |
| retrieval-embeddings | 1 |
| retrieval-private | 0 |
| assistant-best | 1 |
| assistant-balanced | 5 |
| assistant-budget | 2 |
| private-self-host | 1 |
| high-volume-best | 4 |
| high-volume-balanced | 5 |
| high-volume | 2 |
| regulated-best | 1 |
| regulated-data | 1 |
| regulated-budget | 3 |

## Engine path and meaning of the numbers

`/v1/compare` compares snapshots. `/v1/compare-models` returns sourced facts
for named models without an objective. Extract its pure fact collector into
`decision/` and reuse it from the Worker and static build. Keep the Worker's
validation, access control, byte budget, and response shape unchanged. The
static generator calls the collector locally and retains complete records.
It never imports or calls the Worker and never contacts the network.

The existing `decide(parse_spec(template.spec), public_snapshot)` supplies
the objective scores, intervals, costs, estimates, and probabilities. These
are the template's full-ranked-lineup values, not a newly normalized pair ranking.
Display that scope beside P(best). Thin ranked models are included; models
with unknown objective values remain unranked and outside this probability.
Also show the challenger's
`p_beats_leader`, labelled as its chance of matching or beating
the leader's objective score. Do not calculate a complementary probability
or invent a probability when the engine returns null.

When the challenger is in `best`, say "The evidence can't separate them for
this job." When it is in `rest`, say that the evidence separates them and
name the leader, the template objective, date, and its full-lineup P(best).
Only separated pages explain that separation from this challenger does not
necessarily establish a unique best model across the full job lineup.

Probabilities are formatted for human readers. Interpret the engine number's
decimal representation, multiply by 100, and round to the nearest whole
percentage point, with halves rounded up. Values below 0.01, including zero,
display as "under 1%" before rounding. Null displays as "Unavailable".
For example, 0.63671875 displays as 64%, 0.3852 as 39%, 0.015 as 2%, and
0.0102030405 as 1%. A rounded 100% retains its exact value in the trace.
This changes presentation only; selection, bands, and engine values are untouched.

Each probability span carries the exact JSON number in `data-probability`,
its model ID in `data-model`, and its engine field in `data-field`. A JSON-LD
Dataset linked to the Article repeats those exact values as PropertyValue
entries. Each `propertyID` is `<model-id>:<engine-field>`, and `unitText` is
"probability". The Dataset's `about` entries retain model IDs and display names.
Trace tests compare these values with the response and apply the formatting
rule to visible text. Mutation tests change the input probabilities and check
both the new text and exact values, including values within one rounding bucket.

## URLs and discovery

The canonical URL is `/compare/<template-id>/<model-a>-vs-<model-b>/`.
Sort full `lab/model` IDs alphabetically before constructing it. Encode the
slash in each ID as `--`, preserving the lab identity without path segments.
Model IDs already use single hyphens, so this encoding is unambiguous for
the public image. Fail on a URL collision rather than overwrite a page.
Never emit the reversed pair. The index groups links by template, links
back to the dated use-case answer, and states the public-image date.
The method page and use-case shell link to the comparison index.

All selected comparisons, including ties, are indexable: "the evidence
can't separate them" is a useful, honest answer to a model comparison search.
Pairs without objective evidence have no page or index entry. If a rendered
fixture has no supported comparison, it says so and is noindex. Only
indexable pages enter the sitemap. The live Pages composition retains the
directory and copies its source sitemap dates exactly.

## Page anatomy

Each page contains the shared entity lead, the two model display names and template
name, registry purpose and tradeoff, image date, plain verdict, and a neutral
table with equal styling for both models. The table shows exact scores,
score intervals, formatted P(best), selected offerings, cost per task in USD, and
capability estimates with their intervals and benchmark coverage. Missing
values say "Unavailable". Task-size assumptions stay visible.

Names come from the frozen public cards' `display_name` field, the same source
used by Decide's vocabulary. A missing name falls back to the unchanged ID.
Load the cards from the explicit public root even if a private overlay is set.
Names are escaped as text; canonical URLs, pair order and engine lookups keep
the IDs. Table rows retain `data-model`. Index links use the same display names.
Template names retain their words, with a comma-separated qualifier placed in
parentheses, such as "General assistant (best available)".

Requirements, their registry reasons, preferences, the applied template spec,
and the template lesson explain the job. Missing model facts and missing
facts on the selected offerings come from the shared comparison response's
states. Evidence, measurement conditions and citations come from that response
and are limited to the job's measured capability benchmarks. Conditions retain
effort, harness, subcategory, measurement origin and sample size when returned.
No third model or competitor
product is promoted or disparaged in page copy. The neutrality link and
keyed CLI, API, and MCP access line appear on every page.

Round 2 merged `origin/main` at `b4a7074f`, then its revert at `34c6dbef`;
MODEL-404 had not merged. Link to
`/decide/?template=<id>`. The board reads the template query but has no URL
support for model pins. Say the link applies the template to the current
lineup; do not claim it pins the pair or add ignored query parameters.

JSON-LD uses the shared dated Article and breadcrumb helpers with comparison
breadcrumbs. Its headline, description, and date match visible text. No
ratings, fabricated measurements, or instructions addressed to AI appear.

## Verification and boundaries

Red-first tests observe generated HTML, the public snapshot build, the shared
comparison response, lint findings, and the static/live sitemap. They cover
selection, missing evidence, ties, precision, provenance, public-root isolation,
registry restoration, no network, keyed access, neutrality, structured data,
and byte-identical repeated comparison builds. The existing Worker comparison
tests guard the extracted collector's wire behavior. Run the static build,
web build and tests, live composition, and full pytest suite under the shared
lock. Regenerate affected pins with their generators.

No decision contract, ranking algorithm, ranking floor, legal text, frozen
data, production switch, or board state changes are part of this slice.
