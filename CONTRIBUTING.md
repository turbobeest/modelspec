# Contributing to ModelSpec

Contributions are welcome, and the bar is about evidence rather than volume.

## Before your first pull request

Read [CLA.md](CLA.md). You keep the copyright in what you write; the agreement gives the project
permission to publish it, including under different licence terms in future. Agree to it by signing
off each commit:

```bash
git commit -s -m "your message"
```

## The licences

| Part | Licence |
| --- | --- |
| Code | MIT |
| Data (`models/`, `benchmarks/`) | CC BY-SA 4.0 |

If you redistribute the corpus or something derived from it, credit ModelSpec and publish yours under
the same terms. Full text in [LICENSE](LICENSE) and [LICENSE-DATA](LICENSE-DATA).

## The one rule that matters

**Every fact carries a source and the date you read it. Unknown means empty.**

Leave a field blank and write "not established" in the prose rather than guessing, and where two
sources disagree, record both readings with their sources. A page that says it does not know
something is worth more than a page that is confidently wrong, because the next reader can check it.

This is not a style preference. The corpus exists so that somebody deciding whether to trust a
benchmark number can see where it came from and how old it is.

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
