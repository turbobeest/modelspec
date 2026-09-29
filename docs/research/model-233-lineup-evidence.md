# Lineup evidence gaps (MODEL-233)

Read on 2026-09-29. The MODEL-215 coverage audit found 19 lineup models with
admitted evidence on fewer than two benchmarks (`thin-evidence`), and two
models whose reasoning-and-maths clause had no admitted row
(`lineup-domain-evidence`). MODEL-232 then closed Gemini 2.5 Flash, so this
change starts from 18. This note records what primary sources closed, what
they could not close, and why.

The collector is [`scripts/model_233_evidence.py`](../../scripts/model_233_evidence.py).
It has two passes:

- `--boards MODEL_ID ...` runs the weekly board refresh
  (`scripts/refresh_leaderboards.py`) with `add_missing`, scoped to the named
  models. It re-reads each card's legacy board rows against this week's
  registered board reading and adds a row where a board lists the model under
  its card name. A few board rows use a name the card does not carry, so
  `BOARD_NAMES` lists them literally. Deterministic extractors verify every
  row.
- `--self-reports` reads four provider pages, retains each copy, and checks
  every value is in the cited region before filing a claim. The collector is
  Claude, so `modelspec verify --llm-reader mistral` read the claims.

Plain HTTP only. Firecrawl usage was zero.

## Result

| Measure | Before | After |
| --- | ---: | ---: |
| `thin-evidence` findings (lineup models under two benchmarks) | 18 | 8 |
| `lineup-domain-evidence` findings (claimed domain with no evidence) | 2 | 1 |
| Thin templates: no leader, every ranked model is thin | 10 | 10 |
| Templates with no leader at all (thin or nothing ranked) | 22 of 40 | 22 of 40 |

Measured on `origin/main` at `1f5dfc9d` and on this change, with MODEL-215's
`python -m scripts.slo report` and
[`scripts/model_233_thin_templates.py`](../../scripts/model_233_thin_templates.py),
both as of 2026-09-29. The recall set's verdicts are unchanged on all 20
questions.

The thin-template count did not move. The 10 thin templates are four Writing
templates, four Documents templates and two Maths ones (each group's Fastest
template ranks nobody). They now rank more models (Writing, best available:
21 to 23), but every model's writing-capability interval is still wider than
`THIN_INTERVAL_WIDTH`. That is a property of the writing evidence across the
lineup, not of these 18 models. The other 12 templates rank nobody: the Fastest templates wait on
speed measurements, the EU-only templates find no offering, and two
Retrieval templates find no priced candidate.

## Per model

Admitted benchmarks, and the domains that gained evidence.

| Model | Before | After | Domains gained |
| --- | ---: | ---: | --- |
| anthropic/claude-opus-5-5 | 2 | 6 | maths, agentic_tool_use, finance, software_engineering |
| bytedance/seed1-5-embedding | 1 | 2 | retrieval |
| deepseek/deepseek-flash | 1 | 1 | none (see gaps) |
| deepseek/deepseek-v3-1 | 0 | 27 | chat_preference, multilingual, writing, maths, software_engineering, engineering_stem, finance, legal, medical |
| google/gemini-2-5-flash | 20 | 37 | chat_preference, multilingual, writing, maths, reasoning, software_engineering, vision_documents |
| google/gemma-4-26b-a4b-it | 1 | 9 | maths, reasoning, engineering_stem, multilingual |
| google/gemma-4-31b-it | 1 | 10 | maths, reasoning, engineering_stem, multilingual |
| google/gemma-4-e2b-it | 0 | 6 | maths, reasoning, engineering_stem, multilingual |
| google/gemma-4-e4b-it | 0 | 6 | maths, reasoning, engineering_stem, multilingual |
| microsoft/harrier-oss-v1-27b | 1 | 1 | none (see gaps) |
| microsoft/phi-4 | 1 | 27 | chat_preference, multilingual, writing, maths, reasoning, software_engineering, engineering_stem, finance, legal, medical |
| openai/gpt-6-luna | 0 | 0 | none (see gaps) |
| openai/gpt-6-sol | 1 | 2 | agentic_tool_use, finance; reasoning-and-maths still open |
| querit/querit | 1 | 1 | none (see gaps) |
| querit/querit-4b | 1 | 1 | none (see gaps) |
| qwen/qwen3-8-flash-next | 1 | 4 | maths, reasoning, engineering_stem |
| qwen/qwen3-8-max-0902 | 1 | 1 | none (see gaps) |
| qwen/qwen3-embedding-8b | 1 | 3 | retrieval, multilingual |
| tencent/kalm-embedding-gemma3-12b-2511 | 1 | 1 | none (see gaps) |
| typesafe/jev-1-13 | 0 | 0 | none (see gaps) |

Claude Opus 5.5's reasoning-and-maths clause is now backed by Epoch AI's own
run, FrontierMath Tiers 1-3 (v2), 91.2 for `claude-opus-5-5_max`. Epoch's GPQA
Diamond row for it (90.6) is held back: admitting it moves recall question Q06
from pass to fail, because Q06's approved answer requires Opus 5.5 to be
flagged for want of that row. The proposed change to the approved answer is in
[`docs/recall/2026-09-29-model-233-q06.md`](../recall/2026-09-29-model-233-q06.md).
GPT-6 Sol's clause is not backed (see gaps).

## Sources read

| Source | Region | Rows | Verified |
| --- | --- | ---: | ---: |
| [Google Gemma 4 model card](https://ai.google.dev/gemma/docs/core/model_card_4) | Benchmark Results table | 30 | 30 |
| [Claude Opus 5.5 system card](https://www.anthropic.com/claude-opus-5-5-system-card), page 174 | Table 8.1.A | 7 | 1 |
| [DeepSeek-V4.1-Flash model card](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash) | Comparison with frontier models (Max reasoning effort) | 7 | 0 |
| [Qwen3.8-Flash-Next model card](https://huggingface.co/Qwen/Qwen3.8-Flash-Next) | Benchmark Results, Language | 3 | 3 |
| Registered boards: LMArena (pinned dataset revision), Epoch AI, MTEB, Scale HLE, Vending-Bench 2, CursorBench | rows | 44 added, 68 re-confirmed | 112 |

The Opus 5.5 PDF is retained as `pypdf` layout text of page 174, with a
provenance header naming the PDF's SHA-256. Each run of two or more spaces
between columns is written as ` | `.

The Opus 5.5, DeepSeek and Qwen tables print bare numbers. A source that
states no unit confirms none, so those 17 claims carry no unit; the card rows
keep the benchmark's `percent`. The Gemma table prints `%`, and its claims
carry it.

The board pass did not add four rows: Arena's non-style-controlled text
overall and coding values for DeepSeek V3.1 and Phi-4. The cards that carry
those two boards disagree on the unit, so the refresh has no unambiguous
template. The style-controlled rows for both models were added.

What the collector left out on purpose:

- Gemma 4: "Tau2 (average over 3)", because the page does not say whether the
  average is over domains or runs. "HLE with search", because `hle_tools` is
  scored with general tools, not search alone. The vision rows for E2B and
  E4B, which are carded as `llm-chat`. Rows with no benchmark page:
  LiveCodeBench v6, Codeforces, OmniDocBench 1.5, MATH-Vision, CoVoST, FLEURS.
- Opus 5.5: HealthBench Professional. Its value is length-adjusted (section
  8.15.2) and stays with MODEL-191's filing.
- Qwen3.8-Flash-Next: the coding rows, whose footnotes name a harness per row
  or the best of two.
- DeepSeek-V4.1-Flash: its Base-model table, which scores a different
  checkpoint.

## Gaps, and why

Each model below is still under two admitted benchmarks, or still without
reasoning-and-maths evidence.

1. **deepseek/deepseek-flash** and six **Opus 5.5** system-card rows. The
   source states the effort once, in the table heading ("Max reasoning
   effort") or caption ("adaptive thinking at max effort"). Mistral read the
   right value for the right model and left its effort empty. Its cached
   reply for DeepSeek's HLE with tools, for example, is subject `DS-V4.1-Flash`,
   value `63.9`, effort `null`. The verifier rejects a max-effort claim against
   a value with no stated effort. `verification/log.jsonl` records the first
   extractor's mismatch, a deterministic one, so Mistral's diff is not in the
   log. The claims were not weakened to match: they stay quarantined. A
   verifier change is proposed separately. Opus 5.5's Terminal-Bench 4.0 row,
   whose own caption sentence gives xhigh, did verify.
2. **openai/gpt-6-sol**, reasoning-and-maths. Its clause cites MathArena's
   expected-performance board. MathArena now scores current models only on
   BrokenArXiv and ArXivMath. Its AIME, HMMT and USAMO tables are marked
   deprecated and do not list GPT-6 Sol. ModelSpec has no benchmark page for
   BrokenArXiv or ArXivMath. OpenAI publishes no GPQA, AIME or HLE value for
   it, and Scale's HLE board does not list it. The approved premier spec is
   not edited here. Proposed: benchmark pages and a reader for the two
   MathArena competitions.
3. **openai/gpt-6-luna**. No permitted source has a value ModelSpec can map.
   The LMArena dataset revision the refresh pins predates its text listing (a
   later revision lists `gpt-6-luna-max` in the style-controlled math
   categories). MathArena does not list it. OpenAI's launch page answers plain
   HTTP with a challenge and gives Luna only a relative improvement.
4. **microsoft/harrier-oss-v1-27b**, **tencent/kalm-embedding-gemma3-12b-2511**.
   Scored only on MTEB(Multilingual, v2), which is already admitted. Their
   other MTEB scores are task-type slices of sub-boards (Europe, Indic,
   FollowIR) that have no benchmark page. Their own model cards report only
   the same MTEB(Multilingual, v2) value.
5. **querit/querit**, **querit/querit-4b**. Rerankers, scored only on the
   Reranking task type of several MTEB boards. Only the English v2 one
   (`mteb_v2_reranking`) has a page. Querit's model card reports no numbers.
   Querit-4B's reports 71.09 on "MTEB Multilingual v2 reranking tasks"
   averaged over six tasks. That does not match the live board's 69.45, and
   has no page. Proposed: pages for the MTEB sub-boards.
6. **qwen/qwen3-8-max-0902**. An API-only snapshot. Qwen's launch post is
   rendered in the browser only, the Model Studio page for the dated snapshot
   is missing, and the Hugging Face repository is gated. LMArena lists only
   the undated `qwen3.8-max` outside the WebDev board, and tracks it as a
   different snapshot.
7. **typesafe/jev-1-13**. A decision model. No public benchmark with a public
   definition scores it. TypeSafe's own "workflow evals" grade against a
   consensus of two other models, not a checked answer, and publish no task
   set.

## Candidates for ModelSpec's own runs (ADR 0004 step 3)

Where no public evidence exists at all, only a ModelSpec measurement would
close the gap:

- typesafe/jev-1-13: a decision-model evaluation with a checked answer key.
- openai/gpt-6-luna: any maths, reasoning or coding benchmark in the registry.
- qwen/qwen3-8-max-0902: any benchmark in the registry.
- querit/querit and querit/querit-4b, microsoft/harrier-oss-v1-27b and
  tencent/kalm-embedding-gemma3-12b-2511: a second retrieval or reranking
  benchmark, if the MTEB sub-board pages do not close them first.

## Two fixes to the refresh's add path

The weekly refresh can add a row to a card, for release signals. Before this
change, every added row was quarantined, and the snapshot could not load it:

- It stamped the observation date as the evidence date. The verifier reads
  the board row's own date from the projection, so every added row
  mismatched on date. It now uses the board row's date, as updates do.
- It wrote no `measured_by`, which the snapshot requires. It now takes it from
  the template row's source kind.

It also appends to the card's evidence list as text, where it used to
re-serialise the whole front matter.
