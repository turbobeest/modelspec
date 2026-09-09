# Data-quality findings from the benchmark wiki work

Kept here so they become tickets and card fixes rather than getting lost in agent reports.

## 2026-09-07: ambiguous `mmlu_<category>` keys on frontier cards

`mmlu_physics`, `mmlu_biology`, `mmlu_chemistry` and `mmlu_computer_science` appear on 40 frontier cards
(for example `models/google/gemini-2-5-pro.md`) that came through the llm-stats / intlpull enrichment with no
`benchmark_notes`. None of those cards carries the classic four-option subject keys (`mmlu_high_school_physics`
and friends), and the values sit next to `mmlu_pro` scores of similar magnitude. Two readings are possible:
MMLU-Pro per-category scores (MMLU-Pro has physics, biology, chemistry and computer science categories) that lost
the `pro_` in their key, or a roll-up of classic MMLU subjects. The same cards also carry `mmlu_astronomy`,
`mmlu_business_ethics`, `mmlu_clinical_knowledge` and `mmlu_jurisprudence`, which are classic subject names and
not MMLU-Pro categories, so the pull may mix both. Evidence sharpened 2026-09-08 while writing the pages: all 40 of those cards also carry `mmlu_astronomy`, which the
paper's own STEM roll-up would already absorb, so the roll-up reading is weak; the Hugging Face config list for
`cais/mmlu` has no bare `physics` config; and MMLU-Pro's harness task is literally named `mmlu_pro_physics`. The
evidence leans to a lost `pro_` prefix without confirming it. Action: trace the intlpull source for these 40 cards, re-key
the MMLU-Pro categories to `mmlu_pro_<category>`, and re-run the wiki queue. Until then the pages for these ids say
so and carry `status: unknown`.

## 2026-09-08: `artificial_analysis_quality_index` names something Artificial Analysis does not publish

The card key is `artificial_analysis_quality_index`, but Artificial Analysis has called its composite
the **Intelligence Index** in every version back to v1.0 (January 2024); "Quality Index" appears nowhere
on the live site. The page documents the Intelligence Index under this id with an alias and says so in prose.
Action: confirm which figure the cards actually carry, then either re-key to `artificial_analysis_intelligence_index`
or record the alias in the card schema. Related: `artificial_analysis_speed_index` — AA publishes no single blended
speed index either; the page documents Output Speed (tokens per second) as the closest published figure.

## 2026-09-08: `charm` hint in `_census/next_batch.json` points at the wrong paper

The `charm` entry's `urls` list in `benchmarks/_census/next_batch.json` cites `https://arxiv.org/abs/2609.01352v1`.
That id resolves, but to an unrelated September 2026 paper, "CHARM: Character Hallucination for Multicultural Role
Play Benchmark" (Sunkyung Han et al.), a role-play-hallucination benchmark that only shares the acronym CHARM with
the batch's actual target. The task instructions for this batch separately named the correct paper directly —
"Benchmarking Chinese Commonsense Reasoning of LLMs: From Chinese-Specifics to Reasoning-Memorization Correlations"
(Sun et al., arXiv:2403.14112, opendatalab/CHARM on GitHub, ACL 2024) — which `benchmarks/charm.md` documents. The
harness hint (`opencompass: "CHARM"`) is correct and matches the intended benchmark's own OpenCompass configs.
Action: whatever harvester populated this hint (likely a keyword search on "CHARM" with no disambiguation against
the `opencompass`/`arxiv` source pairing already present in the same record) should prefer the arXiv id implied by
a matching harness source over a bare name search, or at minimum flag a mismatch when a hint's own `sources` list
carries other, disagreeing signals. Re-check other `_census` hint records for the same failure mode, especially
short, generic, or reused acronyms.

## 2026-09-08: `benchmarks/math_500.md`'s "How to run it" section understates current lm-evaluation-harness coverage

Written while researching `benchmarks/math.md` (not modified, per this batch's instructions not to touch a page
outside the assigned id list). `math_500.md`'s "How to run it" section states: "No task specific to the 500-item
split was confirmed in lm-evaluation-harness's current task list, which lists `hendrycks_math` and `minerva_math`
for the full MATH set." As of 2026-09-08, that is no longer accurate: the live
`EleutherAI/lm-evaluation-harness` repository ships `lm_eval/tasks/hendrycks_math/hendrycks_math500.yaml`
(`dataset_path: HuggingFaceH4/MATH-500`, the exact dataset `math_500.md` documents) and a parallel
`lm_eval/tasks/minerva_math/minerva_math500.yaml`, both alongside the full-set `hendrycks_math`/`minerva_math`
groups in the same directories. Whether this task existed but was missed, or was added to the harness after
`math_500.md`'s 2026-09-07 research date, was not established here. Action: whoever next reviews or refreshes
`math_500.md` should update its "How to run it" section to name `hendrycks_math500` and `minerva_math500`
directly, rather than saying no such task was confirmed. `benchmarks/math.md`'s own "How to run it" section
documents this finding correctly for the family page.

## 2026-09-08: `benchmarks/mmmu.md` says test-set answer availability is unconfirmed; the publisher has since released them

Found while researching `mmmu_pro` (not modified, per this batch's instructions not to touch a page
outside the assigned id list). `mmmu.md`'s front matter currently carries `contamination.risk: unknown`
and `dataset.public_test_set: null`, with prose stating "Whether the 10,500-question test split ships
with public answers, or is held out and scored through the EvalAI submission platform ... was not
confirmed from a source opened during this research." The official MMMU benchmark homepage
(https://mmmu-benchmark.github.io/, fetched 2026-09-08 for this batch) carries a news item dated
2026-02-12: "We have released the answers for the MMMU test set! You can now evaluate your models on
the test set locally!" -- meaning the test-set answers that were unconfirmed as of `mmmu.md`'s
2026-09-07 research date have since been made public by the publisher, roughly one week after that
page's freshness date. This would raise `contamination.risk` from `unknown` toward at least `medium`
(the answers are now public, though only since February 2026, so exposure window is shorter than an
old benchmark's) and would let `dataset.public_test_set` be set to `true`. Action: whoever next
reviews or refreshes `mmmu.md` should update `contamination`, `dataset.public_test_set`, and the
"Dataset and licence" / "Saturation and contamination" prose to reflect the February 2026 answer
release, citing the homepage's news section directly.

## 2026-09-08: MATH-500 harness claim (RESOLVED)

A batch-2 writer found that `benchmarks/math_500.md` claimed no lm-evaluation-harness task existed for the
500-item split. Verified against the harness's own task directory: `hendrycks_math/hendrycks_math500.yaml` and
`minerva_math/minerva_math500.yaml` both exist and load `HuggingFaceH4/MATH-500`. The page and its `harness.lm_eval`
field have been corrected. No further action.

### Resolved 2026-09-08: the MMMU staleness finding above

Verified against mmmu-benchmark.github.io directly: the site's own banner reads "[2026-02-12] We have released the
answers for the MMMU test set!" and the earlier EvalAI submission-server line is struck through. `benchmarks/mmmu.md`
now records contamination risk as high with that date, sets `dataset.public_test_set: true`, and carries the current
leaderboard position (86.9 as of 2026-07-01, above the 85.4 human-expert approximation, mostly self-reported).

## 2026-09-08: `physics` hint record conflates two unrelated benchmarks under one slug

`benchmarks/_census/next_batch.json` and `queue_p2.json` both carry a single hint record for slug `physics` with
`aliases: ["PHYSICS"]` and `harness: {"bigbench": "physics", "opencompass": "PHYSICS"}` -- as if the BIG-bench task
and the OpenCompass dataset were the same benchmark under two harness names. They are not. BIG-bench's `physics`
(`google/BIG-bench/tree/main/bigbench/benchmark_tasks/physics`) is a 229-item, high-school-level, multiple-choice
"which formula solves this word problem" task authored by two individual contributors (Gloria Wang, Zirui Wang)
during BIG-bench's 2021-2022 crowdsourcing drive, with a GPT-2-era dummy-model baseline near random chance.
OpenCompass's `PHYSICS` (`open-compass/opencompass/tree/main/opencompass/configs/datasets/PHYSICS`) loads
`opencompass/PHYSICS-textonly` and is a completely different, much larger benchmark: 1,297 expert-annotated,
PhD-qualifying-exam-level physics problems from Feng et al., "PHYSICS: Benchmarking Foundation Models on
University-Level Physics Problem Solving" (arXiv:2503.21821, Yale/NYU, March 2025), scored with a SymPy-plus-LLM-judge
pipeline, where the best model in the paper (o3-mini) reached only 59.9% accuracy. Same near-identical name
(lowercase vs. uppercase), same generic subject word, otherwise unrelated: different authors, different era,
different task format, different difficulty level, no shared data. Likely cause: a name-matching harvester that
does not disambiguate a bare, extremely generic subject word like "physics" across sources the way it can for a
more distinctive acronym. `benchmarks/physics.md` documents the OpenCompass/Feng-et-al. benchmark as the primary
subject (it is the actively used, harder, better-evidenced of the two) and names the BIG-bench task explicitly in
its "What it measures" and "Lineage" sections so the two are not conflated; it does not get its own page here.
Action: whoever next touches this hint file should split the `physics` record into two (e.g. `physics` for the
OpenCompass/Feng-et-al. benchmark and a distinctly named record such as `bigbench_physics` for the BIG-bench task),
and re-check other bare, generic single-word hint slugs in the same file for the same collision pattern.

## 2026-09-08: AIME series carries two id conventions

`benchmarks/aime_2025.md` uses the id `aime_2025` (underscore before the year). This batch's
`benchmarks/aime2024.md` and `benchmarks/aime2026.md` use no underscore, matching the ids as assigned for
this batch. All three document the same annual American Invitational Mathematics Examination series under an
otherwise identical schema, problem format and scoring approach, and each page's Lineage section cross-references
the other two by id (`aime2024.md` and `aime2026.md` name `aime_2025` explicitly and note the spelling
difference in prose; `aime_2025.md` was not modified, per this batch's instructions, so it does not link forward
to `aime2026`). The inconsistency is a naming-convention artefact from how ids were assigned across batches, not
a substantive difference in what the pages cover. Action: normalise the three ids to one convention (either add
underscores to `aime2024`/`aime2026` or drop the underscore from `aime_2025`), then update any model-card
benchmark keys and cross-page links that reference whichever id(s) change.

### Resolved 2026-09-08: AIME id convention normalised

The series now uses one convention, `aime_2024` / `aime_2025` / `aime_2026`, matching the `aime_2025` key the model
cards already carry (29 cards). The harness spellings `aime2024` and `aime2026` are kept as aliases on their pages,
and the slicer's variant collapsing means the aliased spellings will not be re-queued as separate benchmarks.

## 2026-09-08: Bangla task hints in `_census/next_batch.json` point at nonexistent per-task URLs and the wrong harness ids

The `bangla_boolqa`, `bangla_commonsenseqa`, `bangla_piqa` and `bangla_openbookqa` entries' `urls` fields each name
a task-specific GitHub directory (for example `.../lm_eval/tasks/bangla_boolQA`) that returns 404. The live
`EleutherAI/lm-evaluation-harness` repository has never had per-task directories for these four tasks: the PR that
added them (#3454, "Multiple Bangla Benchmark datasets added," merged 2026-01-13) placed all five Bangla task YAMLs
(including `bangla_mmlu`, not in this batch) directly in one shared `lm_eval/tasks/bangla/` directory from the
start — confirmed both by reading that PR's file list and by an empty commit history for every one of the hinted
per-task paths. The hints' `name` and `harness.lm_eval` fields (`bangla_boolQA`, `bangla_commonsenseQA`,
`bangla_piQA`, `bangla_poenbookQA`) trace instead to the harness's own top-level `lm_eval/tasks/README.md`
registry table, which uses those same camelCase labels (including the `poenbookQA` typo) as link text pointing at
`bangla/README.md` — but none of the four is the task's actual runnable `--tasks` name. Each task's own YAML gives
the real names as `boolqa_bn`, `bangla_commonsenseqa`, `piqa_bn` and `openbookqa_bn` respectively; only the
CommonsenseQA one happens to match its hint. A harvester that takes a harness README's display label as both the
runnable task name and a valid directory-listing URL will reproduce this failure for any other harness task that
lives in a shared, multi-task directory rather than one of its own.
Action: whatever harvester populates `harness.lm_eval` and `urls` for lm-evaluation-harness-sourced hints should
read each task's own YAML `task:` field rather than a top-level README's display label, and should confirm a
`urls` entry actually resolves before writing it. The four `bangla_*` pages in this repository already record the
correct runnable names and the registry typo directly; this note is so the next harvest pass fixes the hint file
itself instead of repeating the error for a future id.

## 2026-09-08: `aexams` and `arabic_exams` are the same benchmark under two harness names

Both hints named a batch-4 id each, `aexams` (lm-evaluation-harness) and `arabic_exams` (HELM), with no indication
in `_census/next_batch.json` that they were related. Reading both task definitions confirmed they are the same
benchmark. lm-evaluation-harness's `aexams` group loads `Hennara/aexams`, whose own loading script names its
homepage as `github.com/FreedomIntelligence/AceGPT/.../EXAMS_Arabic`. HELM's `arabic_exams` scenario loads
`OALL/Arabic_EXAMS`, whose docstring describes it as "the Open Arabic LLM Leaderboard (OALL) version mirror of the
Arabic subset of EXAMS, which is in turn based on the AceGPT version" — the same AceGPT source. Both cover the
identical five subjects (Islamic Studies, Biology, Physics, Science, Social). Unzipping `Hennara/aexams`'s
underlying data file and counting items directly gave 537 test + 25 dev = 562, which matches `OALL/Arabic_EXAMS`'s
reported 537 test + 25 validation exactly, and matches the original `exams-qa` repository's own per-language table
(Arabic: 562). Per this batch's instructions, one page was written under `arabic_exams`, with `aexams` recorded in
its `aliases`; `aexams` was skipped as a separate id rather than getting its own page.
Action: add `aexams: arabic_exams` to `_census/aliases.yaml` so the fold is picked up automatically for any future
census pass, the way `arc_c`/`arc_e` already are.

## 2026-09-08: `autobencher_capabilities` and `autobencher_safety` hints carry an identical, unverifiable `score`

Both hint records in `_census/next_batch.json` carry `"score": 18.0` — exactly the same value, to one decimal
place, for two different HELM scenarios that measure different things on different scales (capabilities is
model-judged QA correctness; safety is effectively a refusal rate). Neither `autobencher_capabilities_scenario.py`
nor `autobencher_safety_scenario.py` on GitHub, nor HELM's `schema_autobencher.yaml`, nor HELM's own homepage list
of hosted leaderboards, nor the direct `crfm.stanford.edu/helm/autobencher/latest/` URL (which 404s), turned up any
rendered source with a score for either scenario — so 18.0 could not be traced to anything for this research, for
either id. An identical score across two unrelated metrics is the signature of a harvester bug (for example, both
records inheriting one shared/aggregate number from HELM's parent `autobencher_scenarios` run-group instead of
each child scenario's own figure, if such a figure exists anywhere) rather than two coincidentally-equal
measurements. Both `benchmarks/autobencher_capabilities.md` and `benchmarks/autobencher_safety.md` leave
`saturation.top_score` empty and say why in prose, rather than repeating this figure.
Action: whatever harvester populates `score` for HELM-sourced hints should confirm it is reading each child
run-group's own number rather than a parent group's, and should drop the field (or flag it) when the same value
recurs identically across sibling ids with different metrics. Re-check other multi-scenario HELM run-groups
(`schema_autobencher.yaml`'s pattern of one parent group with named subgroups is not unique to AutoBencher) for
the same failure mode.

### Resolved 2026-09-08: the AutoBencher "identical score 18.0" report

Not a harvester bug and not a benchmark number. The `score` field in the census queues is the ranking score the
census computes for a candidate name (source count, whether a curated source vouches for it, whether the name looks
like a benchmark, and dataset downloads), so two unrelated benchmarks vouched for by the same kinds of sources will
often tie. The field is now emitted as `census_rank_score` with a note attached, so no writer mistakes it for a
result again. Nothing in the AutoBencher pages needs changing.

## 2026-09-08: `humaneval_multi` is OpenCompass's name for MultiPL-E's HumanEval-derived subset, not a separate benchmark

Assigned as one of six `humaneval_*` ids in this batch, alongside a hint pointing at OpenCompass's `humaneval_multi`
config directory. Reading `opencompass/configs/datasets/humaneval_multi/humaneval_multi_gen_82cf85.py` shows it is
not an independent benchmark: its dataset path is `./data/multi-data/humaneval_multipl-e/`, its docstring is copied
verbatim from nuprl/MultiPL-E's own Hugging Face dataset card (the "SRCDATA-LANG-keep / -transform / -reworded /
-removed" prompt-variant language, confirmed by diffing against `huggingface.co/datasets/nuprl/MultiPL-E`'s
README), and it runs the "reworded" variant across the same ~19 MultiPL-E language codes (cpp, cs, d, go, java, jl,
js, lua, php, pl, py, r, rb, rkt, rs, scala, sh, swift, ts) already covered by this repository's `multipl_e` family
page. It also does not report under one aggregate name: each language gets its own column,
`humaneval_multiple-<lang>`, the same shape as `multipl_e`'s own per-language subset pages. Per this batch's
instructions, no `benchmarks/humaneval_multi.md` page was written; it is the same benchmark as `multipl_e`,
restricted to the HumanEval-derived (not MBPP-derived) half of that family and the "reworded" prompt variant
specifically.
Action: `humaneval_multi: multipl_e` added to `_census/aliases.yaml` so the fold is picked up automatically for any
future census pass. `multipl_e.md`'s own `aliases` field was not edited by this batch (out of scope: it was not one
of this batch's assigned ids), so a future pass on that page should add `humaneval_multi` there too, and may want to
note in its Lineage section that OpenCompass reports the HumanEval-derived half of the family under that name.
