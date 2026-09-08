# Writing a benchmark page

One Markdown file per benchmark at `benchmarks/<id>.md`. The front matter is the `BenchmarkCard`
schema in `schema/benchmark.py`; the body is a short encyclopedia article for someone who has to
decide whether to trust a number. Validate every page with
`python3 scripts/benchmarks/validate.py benchmarks/<id>.md` before you call it done.

## Rules that are not negotiable

1. **Use the id you were given.** It is the key the model cards use for scores; do not rename it.
2. **Every fact has a source.** A paper, the official repository, the dataset page, the leaderboard
   or the publisher's own page. Put each one in `sources` with the date you read it. Prefer the
   paper and the repository over blog posts and vendor pages. Never cite a page you did not open.
3. **Unknown means empty.** Leave a field empty or `null` and say "not established" in the prose.
   Do not infer a dataset size, a licence, a release date or a baseline from memory. Do not round a
   number you did not read.
4. **No authored `models_covered`.** The site derives that from the model cards.
5. **No marketing.** Say what the benchmark measures, how it is scored, what a good score does and
   does not tell you. Sentence case, plain verbs, sentences under 25 words where you can.
6. **Do not run git.** Write the file, validate it, move on. The coordinator commits.

## Front matter

Fill every key of `BenchmarkCard` you can source. Notes on the hard ones:

- `category` is one of: knowledge, math, coding, multimodal, safety, human-preference, embedding,
  generation, domain, agentic, composite, reasoning, instruction-following, long-context, translation.
- `page_kind`: `benchmark` for a standalone benchmark, `family` for a page that many subsets point to
  (`mmlu`, `multipl_e`, `mteb`, `arena_elo`, `swe_bench`, `flores`), `subset` for a member of a family
  (an MMLU subject, a MultiPL-E language, an MTEB task, an Arena category). Subset pages must set
  `lineage.family` to the family id and may be short.
- `status`: `active` if still reported for new models; `saturated` if top models sit at the ceiling;
  `superseded` if a successor replaced it; `deprecated` if the publisher retired it; `proposed` if
  announced but not yet reported; `unknown` otherwise.
- `saturation.status`: `saturated` when leading scores sit within a few points of the maximum or the
  human baseline; `watch` when the spread among top models has collapsed or a harder successor exists;
  `open` when scores still separate models; `unknown` when you could not establish it. Give
  `top_score` and `as_of` only when you read them from a source.
- `contamination.risk`: `high` if the test set is public and old enough to be in training data and
  the publisher has said so or the community has shown it; `medium` if public but recent or partially
  held out; `low` if answers are held out or refreshed; `unknown` otherwise. Say why in `note`.
- `metric.direction`: `lower_is_better` for latency, cost, perplexity, error rate.
- `harness`: the exact task name in lm-evaluation-harness, inspect_evals, HELM, OpenCompass or
  BIG-bench when you can confirm it from their task lists.
- `released` is `YYYY` or `YYYY-MM` from the paper or repository, not the arXiv v1 date guessed.
- `freshness.researched` is today's date; `freshness.researched_by` is the agent label you were given.

## Body sections

For `benchmark` and `family` pages, exactly these headings, in this order:

```
## What it measures
## How it is scored
## Dataset and licence
## Who publishes it
## Lineage
## Saturation and contamination
## How to run it
## Reading the numbers
```

For `subset` pages: `## What it measures` and `## Reading the numbers`, plus a first line that
points to the family page: "Part of the [MMLU](mmlu.md) family."

What each section holds:

- **What it measures.** The task in plain words: what the model is given, what it must produce, what
  skill that exercises. Name the modality and language. Two short paragraphs at most.
- **How it is scored.** The metric, the maximum, baselines, the evaluation protocol (zero-shot,
  few-shot, pass@k, LLM judge, human votes), and known protocol differences between reporters.
- **Dataset and licence.** Size, source of the items, how they were made or filtered, the licence
  as published, whether answers are public.
- **Who publishes it.** The organisation, the authors, the paper, when it appeared, and who maintains
  the leaderboard today.
- **Lineage.** Where it came from and what came after; name the ids of predecessors, successors and
  variants that exist in this repository, and mention ones that do not yet have a page.
- **Saturation and contamination.** Is the ceiling reached, are the numbers still separating models,
  is the test set likely in training data, what the publisher did about it.
- **How to run it.** The harness task names, the reference implementation, and anything that makes
  reported numbers hard to compare (prompt formats, shot counts, judge models, tool access).
- **Reading the numbers.** Three to six sentences: what a strong score means in practice, what it
  does not tell you, and what to look at alongside it.

Length: a benchmark page runs 350 to 900 words in the body; a subset page 120 to 250.

## Tools you have

- Web fetch for papers, repositories, dataset cards and leaderboards. Web search has a session-wide budget that
  earlier agents may already have spent, so do not depend on it: go straight to the sources you can name
  (arxiv.org/abs/<id>, ar5iv.org/abs/<id> for HTML when the PDF will not read, the GitHub repository, the
  Hugging Face dataset card, `huggingface.co/api/datasets/<id>` and the datasets-server for exact split counts,
  the publisher's leaderboard).
- `python3 scripts/benchmarks/fetch.py <url>` renders JavaScript-heavy pages (leaderboards,
  Hugging Face spaces) to Markdown through Firecrawl, cached locally. `--links` lists a page's links.
- The model cards in `models/` show which models report the benchmark and where those scores came
  from (`benchmarks.benchmark_source`, `benchmarks.benchmark_notes`); `grep -rl "<id>:" models/`
  finds them. Use that to learn which leaderboards carry the benchmark, not as a citation.

## The census hints are leads, not citations

`benchmarks/_census/next_batch.json` and `queue_p1.json` carry urls, arXiv ids and harness names gathered by
name matching across registries, papers and lists. Names collide: two unrelated papers can share an acronym, and
a hint's arXiv id may belong to the wrong one. Open the source and confirm it actually describes the benchmark
your id names before you cite it. When two projects share a name, say so in Lineage and name the one your page
documents. Never cite a hint url you did not open. A hint's harness task name is the name in a registry table,
not necessarily a directory: several harness tasks share one directory, and the task's own `task:` field in its
YAML is the runnable name. Confirm both from the harness repository before you record them.

## Recording a number you cannot verify

If a leaderboard will not render, a licence is stated two different ways, or two sources disagree, that is a
finding, not a blocker. Leave the field empty, say both readings in the prose with their sources, and put a
line in `benchmarks/_census/DATA-QUALITY.md` if the problem is in this repository's own data rather than in
the world. A page that says "not established" with its evidence is worth more than a confident wrong number.

## Before you finish

Run the validator on every file you wrote. Fix what it reports. Then report back with the ids you
completed, the ids you skipped, and one line on why for each skip.
