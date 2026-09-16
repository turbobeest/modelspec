# Contributing to ModelSpec

Contributions are welcome, and the bar is about evidence rather than volume.

## Before your first pull request

Sign off each commit:

```bash
git commit -s
```

That adds a `Signed-off-by` line, which certifies the **Developer Certificate of Origin 1.1**
— reproduced verbatim in [DCO](DCO) at the root of this repository. In short: you are
certifying that you wrote the contribution, or that you have the right to submit it under the
licence the project already uses.

**It is not a copyright assignment and it grants no relicensing right.** You keep everything
you write. A CI check enforces the sign-off on pull requests.

To sign off a branch you have already written:

```bash
git rebase --signoff main
```

### When a signed agreement is also needed

For a substantial or ongoing contribution, the project may additionally ask you to sign
[CLA.md](CLA.md) — the unmodified Harmony Individual Contributor License Agreement v1.0. It
is not required for ordinary pull requests, and it is also not a copyright assignment.

## The licences

| Part | Licence |
| --- | --- |
| Code | MIT |
| Data (`models/`, `benchmarks/`, `hardware/`, `hosts/`) | CC BY-SA 4.0 |

If you redistribute the corpus or something derived from it, credit ModelSpec and publish yours under
the same terms. Full text in [LICENSE](LICENSE) and [LICENSE-DATA](LICENSE-DATA).

## What this project does not accept from contributors

These are boundaries of the project, not judgements about your work.

1. **Policy determinations.** `commercial_use`, `data_residency`, and licence or origin
   analysis are researched in-house from primary sources and are not accepted through pull
   requests. Where a card shows one of these as unresearched, that is not an invitation.
2. **Private submissions.** Contributions arrive as public pull requests. Material sent
   privately will not be read or merged, so that what the project holds and what it publishes
   never diverge without a record.
3. **Third-party material you cannot point at.** See the sourcing rule below.

## The one rule that matters

**Every fact carries a source and the date you read it. Unknown means empty.**

Leave a field blank and write "not established" in the prose rather than guessing, and where two
sources disagree, record both readings with their sources. A page that says it does not know
something is worth more than a page that is confidently wrong, because the next reader can check it.

This is not a style preference. The corpus exists so that somebody deciding whether to trust a
benchmark number can see where it came from and how old it is.

## Third-party material

Any third-party material inside a contribution must be identified with its source and its
licence, and that licence must permit the use being made of it. This matters more here than in
most projects: the cards and pages record facts drawn from papers, repositories and
leaderboards.

If you do not own the copyright in the whole of what you are submitting, say so in the pull
request, name the part you did not write, and give its source and licence. If its terms do not
allow redistribution here, do not include it — cite it instead.

## Benchmark pages

Read [benchmarks/AUTHORING.md](benchmarks/AUTHORING.md) first. It defines the schema, the required
sections and the sourcing rules. Validate before you open the pull request:

```bash
python3 scripts/benchmarks/validate.py benchmarks/<id>.md
```

Names collide constantly in this field. Before writing a page, open the source and confirm it
describes the benchmark your id names. Several pages in this repository exist because a writer found
that a registry entry, a paper and a leaderboard were three different projects sharing an acronym.

## Model cards

The schema in `schema/card.py` is the source of truth; the front matter is the schema. Use
`modelspec gaps` to find what needs research and `modelspec research <model_id>` to start.

## What gets rejected

Facts without sources. Numbers copied from an aggregator that were never read at the publisher.
Confident claims about a benchmark whose leaderboard has been dead for three years. Pages written
from memory. Material you are not free to publish.
