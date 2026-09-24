# Audit: rankings are frozen at April 2026 (MODEL-108)

**Date:** 2026-09-23. **Code and data:** `main` at `d020f07`. The live export
`https://modelspec.dev/api/rank/rankings.json` reports the same commit, built
2026-09-24T01:06Z.
**External observations:** 2026-09-23 US Eastern (2026-09-24 02:00–02:12 UTC).
Every live-board figure below is dated by that observation unless a row gives
its own date.
**Firecrawl:** the balance was 3,109 before this audit and 3,107 after it. The
audit made one scrape call (the MTEB leaderboard shell), billed 1 credit. The
other credit was not spent by this audit; the team key is shared. Every other
source was read over plain HTTP.

This is an audit. It changes no card, no weight, no bound and no floor. Section
8 holds the **proposals**, and each one is Jamie's decision.

## Summary

1. **The complaint is right. The cause is structural, not only a missing
   backfill.** The live coding ranking puts `gemini-2-5-pro` (released 2025-03)
   first. On the current capability boards, Gemini 2.5 Pro ranks 69th to 150th
   and Claude Sonnet 4.5 ranks 23rd to 136th. Claude Opus 4.6 is mixed. It ranks
   25th on Epoch ECI, 44th on the AA Intelligence Index and 28th on Arena WebDev.
   On the Arena text preference boards it is still in the top 5 (section 2).
2. **Even a perfect backfill cannot rank a new frontier model in most profiles.**
   The profiles weight benchmarks that nobody runs on new models any more:
   HumanEval, MATH-500, BBH, IFEval, MT-Bench, AlpacaEval, Aider Polyglot,
   LiveCodeBench and Terminal-Bench 1.0. Suppose a model released after mid-2026
   got every benchmark that still has a current source. It would clear the 0.50
   CLI floor in **1 of 51 profiles**, which is `science`. The best case, which
   also reads the Arena style-control boards as the category Elo keys, is **8 of
   51**. The coding profile tops out at 0.36 (0.56 in the best case). Chat tops
   out at 0.20 (0.50). Vision and embedding top out at 0.00 (0.25 and 0.00).
   MODEL-109's done-criterion therefore cannot be met by backfill alone.
3. **No pipeline ingests scores. Confirmed.** Daily research (MODEL-5) writes
   identity, pricing and context from models.dev, and only for new cards. The
   curation loop (MODEL-10) edits `benchmarks/*.md` pages, never card scores.
   The only live harvest ran by hand, once, on 2026-09-10.
4. **The normalization bounds clip the frontier flat.** 94 cards exceed the
   GPQA Diamond ceiling of 80. 61 cards exceed the LiveCodeBench ceiling of 60,
   and 22 exceed the SWE-bench Verified ceiling of 70. Every Arena key uses a
   ceiling of 1400, and current boards top out between 1506 and 1793. The top of
   each weighted benchmark collapses to 100.
5. **The input data has quality defects.** 80 cards in 25 groups share an
   identical coding-score vector with other cards. One vector is shared by 13
   OpenAI cards, including `gpt-5-4-nano`, `gpt-5-2` and `gpt-5-3-codex-spark`.
   The `general` #1, `claude-mythos-preview`, runs on scores that were imputed
   from Opus 4.6 in commit `ccbc149`.
6. **The catalogue has gaps that are not about scores.** Muse Spark 1.1, 1.2
   and 1.3, MiMo-V2.6-Pro and 7 of the MTEB(eng, v2) top 10 have no card.
   Discovery reads only models.dev.
7. **One claim in the brief needs a correction.** All 88 cards released since
   2026-05 have an empty flat `benchmarks.scores` block. That part is true. But
   60 of the 88 carry reviewed `evidence` rows from the 2026-09-10 AA and Arena
   harvest, and the ranker merges those rows. They stay unranked because the
   evidence falls on benchmarks that the profiles barely weight (for example,
   `gpt-6-astra` has 20% coding coverage). An empty flat block is not the reason.

## 1. Evidence re-verified

The analysis loaded all 1,346 cards through `schema.card.ModelCard`, and 1,332
remain after rehosts are dropped. Candidates were built with
`pipeline.ranking.build_candidates` and ranked with `rank_report` at the CLI
floor.

| Claim in the brief | Result |
|---|---|
| 549 cards carry flat scores. `benchmark_as_of`: 2026-04 = 392, 2025-03 = 77, 2024-07 = 64, none = 16 | **Confirmed**, exactly |
| 88 models released since 2026-05 have no score | Flat block empty for all 88: **confirmed**. 60 of the 88 have `evidence` rows: **corrected** |
| Live `/v1/rank` coding top 3 = gemini-2-5-pro, claude-opus-4-6, claude-sonnet-4-5 | **Confirmed**, both in the live `rankings.json` and locally |
| Unscored models are dropped silently (`unranked_count` only) | **Confirmed**. MODEL-110 covers it |
| Coding weights `humaneval` at 0.20. Reasoning weights `math_500`, `bbh` and `ifeval` | **Confirmed**. After `_apply_verified_additions` the effective weights are 0.16, 0.16, 0.08 and 0.04 |

Evidence dates: 1,143 of 1,223 evidence rows are dated 2026-09-03 to
2026-09-10, and 1,122 of those are dated 2026-09-10. No evidence row is newer
than 2026-09-10. `claude-opus-5-5` (released 2026-09-22) is already on the AA
board and has no evidence.

The live `rankings.json` uses the wizard floor (0.25), so it ranks 206 models
for coding. The CLI floor ranks 126. The top of the list is the same at both
floors.

## 2. Where the three named models sit today

The rank is 1 plus the number of distinct products that score higher. Effort
variants are collapsed to the best row per product. AA rows marked `deprecated`
are included here only so that the three models can be found.

| Board (URL) | Products | Gemini 2.5 Pro | Claude Opus 4.6 | Claude Sonnet 4.5 |
|---|---:|---:|---:|---:|
| AA Intelligence Index, [artificialanalysis.ai/leaderboards/models](https://artificialanalysis.ai/leaderboards/models) | 463 | 150 | 44 | 118 |
| AA HLE (same page) | 439 | 112 | 37 | 136 |
| Epoch Capabilities Index, [epoch.ai/data/benchmark_data.zip](https://epoch.ai/data/benchmark_data.zip), file dated to 2026-09-09 | 245 | 79 | 25 | 64 |
| Arena WebDev, [lmarena.ai/leaderboard](https://lmarena.ai/leaderboard) | 116 | 109 | 28 | 73 |
| Arena text, overall, style control (same page) | 183 | 68 | 2 | 49 |
| Arena text, coding, style control, [lmarena.ai/leaderboard/text/coding](https://lmarena.ai/leaderboard/text/coding) | 378 | 105 | 3 | 27 |
| Arena text, hard prompts, style control, [lmarena.ai/leaderboard/text/hard-prompts](https://lmarena.ai/leaderboard/text/hard-prompts) | 383 | 81 | 1 | 41 |
| Epoch SWE-bench Verified runs (last run 2026-06-25) | 32 | 30 | 4 | 23 |
| Epoch Vending-Bench 2 | 57 | 45 | 8 | 33 |

Verdict. For Gemini 2.5 Pro and Sonnet 4.5, the "30s–40s" estimate is
generous. For Opus 4.6 it holds on the capability indexes (25th–44th). It does
not hold on human-preference boards, where Opus 4.6 is still near the top. The
coding profile's own two Arena keys would therefore keep Opus 4.6 high even
after a refresh. The agentic coding benchmarks are what move it down.

## 3. Benchmark set health

### 3.1 Every weighted benchmark

The table covers every key that any profile weights. The MMLU subject keys (10)
and the MultiPL-E keys (8) are grouped below it. Column definitions:

- **Cards** counts the cards with a value from the flat block or from evidence.
- **Top-20 spread** is the first value minus the 20th value on the cards. It is
  saturation as our own data shows it.
- **Newest reading** is the newest `benchmark_as_of` or `evidence_date` on any
  card. A 2026-04 value is the April scrape label.
- **Live board** is whether a source that is maintained today carries this
  exact benchmark for new models.

| Benchmark | Profiles | Cards | Top card value | Top-20 spread | Newest reading | Live board |
|---|---:|---:|---:|---:|---|---|
| `arena_elo_overall` | 49 | 211 | 1467.4 | 77.4 | 2026-04 | Board is live, but only the style-control view is server-rendered |
| `ifeval` | 26 | 354 | 92.5 | 0.7 | 2026-04 | No (AA carries IFBench instead) |
| `mmlu_pro` | 24 | 356 | 87.5 | 2.7 | 2026-07 | Not checked (TIGER-Lab space) |
| `gpqa_diamond` | 13 | 580 | 96 | 4.89 | 2026-09 | Yes: AA and Epoch |
| `humaneval` | 13 | 200 | 93.8 | 1.7 | 2026-04 | No |
| `math_500` | 13 | 354 | 97.5 | 2 | 2026-04 | No (no longer in the AA payload) |
| `swe_bench_verified` | 13 | 125 | 96 | 24.8 | 2026-07 | Stale: the official board's last entry is 2026-02-26 and Epoch's last run is 2026-06-25. Providers still self-report |
| `arena_elo_coding` | 12 | 210 | 1520.3 | 110.3 | 2026-04 | Yes: Arena (style control) |
| `mt_bench` | 12 | 46 | 9.4 | 0.4 | 2026-04 | No |
| `aider_polyglot` | 11 | 116 | 83.1 | 11 | 2026-04 | Dead: newest run 2025-10-03 |
| `alpaca_eval` | 7 | 56 | 55.2 | 6.7 | 2026-04 | Not checked |
| `arena_elo_style_control` | 6 | 147 | 1507.16 | 39.05 | 2026-09 | Yes: Arena |
| `miracl` | 5 | 90 | 67.8 | 9.6 | 2026-04 | Derivable from MTEB per-task JSON |
| `terminal_bench` | 5 | 53 | 58.2 | 9.4 | 2026-04 | Superseded: this is v1, and the live board is v4.0. Our own page says `superseded` |
| `wildbench` | 5 | 45 | 82.5 | 8.7 | 2026-04 | Not checked |
| `finbench` | 4 | 13 | 71.2 | 16 | 2026-04 | Not checked |
| `medqa` | 4 | 51 | 96.5 | 13.6 | 2026-04 | Not checked |
| `pubmedqa` | 4 | 4 | 76.8 | 3.4 | 2026-04 | Not checked (page: saturated) |
| `truthfulqa` | 4 | 50 | 68.3 | 16.2 | 2026-04 | Not checked |
| `arena_elo_vision` | 3 | 55 | 1310 | 103 | 2026-04 | Yes: Arena (style control) |
| `finqa` | 3 | **0** | – | – | – | No card holds it |
| `legalbench` | 3 | 20 | 89.4 | 30.9 | 2026-04 | Not checked |
| `mgsm` | 3 | 45 | 92.3 | 3 | 2026-04 | Not checked |
| `aime_2025` | 2 | 30 | 95.3 | 22 | 2026-04 | MathArena. The problem set is fixed, and Epoch's OTIS mock AIME is at 100% |
| `bbq` | 2 | 66 | 88.2 | 3.7 | 2026-04 | Not checked |
| `beir` | 2 | 69 | 58.5 | 5 | 2026-04 | Derivable from MTEB per-task JSON |
| `critpt` | 2 | 255 | 32.29 | 20.29 | 2026-09 | Yes: AA |
| `flores` | 2 | **0** | – | – | – | No card holds it |
| `gdpval_aa` | 2 | 124 | 61.75 | 23.8 | 2026-09 | Yes: AA |
| `helm_safety` | 2 | 71 | 95.2 | 5.7 | 2026-04 | Not checked (page: saturated) |
| `medmcqa` | 2 | 4 | 74.2 | 18.5 | 2026-04 | Not checked |
| `mmmu` | 2 | 68 | 73.4 | 4.3 | 2026-04 | No (AA carries MMMU-Pro) |
| `mteb_overall` | 2 | 96 | 70.1 | 5.6 | 2026-04 | MTEB v2 JSON is live. Our key is v1 |
| `mteb_retrieval` | 2 | 96 | 68.5 | 7.3 | 2026-04 | As `mteb_overall` |
| `scicode` | 2 | 90 | 59.49 | 8.91 | 2026-09 | Yes: AA and Epoch |
| `toxigen` | 2 | 71 | 97.5 | 4.7 | 2026-04 | Not checked |
| `aa_briefcase` | 1 | 2 | 53 | 2 | 2026-09 | Yes: AA |
| `aa_lcr` | 1 | 254 | 88.67 | 9.34 | 2026-09 | Yes: AA |
| `aime_2026` | 1 | 2 | 95.3 | 6.1 | 2026-07 | Yes: MathArena |
| `arc_challenge` | 1 | 50 | 72.7 | 9.6 | 2026-04 | No. Our own page says `superseded` |
| `arena_elo_hard_prompts` | 1 | 103 | 1534.7 | 78.7 | 2026-04 | Yes: Arena (style control) |
| `arena_elo_math` | 1 | 209 | 1458.3 | 58.3 | 2026-04 | Yes: Arena (style control) |
| `automationbench_aa` | 1 | 2 | 68.5 | 6.3 | 2026-09 | Yes: AA |
| `bbh` | 1 | 221 | 68.7 | 5.9 | 2026-04 | No |
| `chartqa` | 1 | 64 | 90.8 | 5.3 | 2026-04 | No |
| `clip_score` | 1 | **0** | – | – | – | No page and no range |
| `docvqa` | 1 | 67 | 96.5 | 3.3 | 2026-04 | No (page: saturated) |
| `fid` | 1 | **0** | – | – | – | No page |
| `gdp_pdf_aa` | 1 | 2 | 33 | 21 | 2026-09 | Yes: AA |
| `gsm8k` | 1 | 130 | 97.3 | 2.3 | 2026-04 | No (page: saturated) |
| `hellaswag` | 1 | 50 | 89.1 | 6.5 | 2026-04 | No (page: saturated) |
| `live_code_bench` | 1 | 144 | 91.7 | 7.1 | 2026-04 | Stale: the official JSON's newest problems date from 2025-04 |
| `mathvista` | 1 | 66 | 73.7 | 8.2 | 2026-04 | No |
| `mos_tts` | 1 | **0** | – | – | – | No page |
| `mteb_classification` | 1 | 94 | 73.5 | 3.7 | 2026-04 | MTEB v2 JSON (v1 key) |
| `mteb_clustering` | 1 | 94 | 53.8 | 5.6 | 2026-04 | MTEB v2 JSON (v1 key) |
| `swe_bench_agent` | 1 | 61 | 62.8 | 7.6 | 2026-04 | Undefined (page status `unknown`) |
| `tau_bench` | 1 | 54 | 70.6 | 12.1 | 2026-04 | Superseded by τ² and τ³ (both on AA). Our own page says `superseded` |
| `web_arena` | 1 | **0** | – | – | – | No card holds it |
| `wer_librispeech` | 1 | **0** | – | – | – | No page |

Grouped keys:

- **MMLU subjects.** `mmlu_biology`, `mmlu_chemistry`, `mmlu_physics`,
  `mmlu_clinical_knowledge`, `mmlu_professional_law` and 5 more carry 40–90
  cards each, with a top-20 spread of 2.3–15.2 points. All readings date from
  2026-04, and no live board exists.
- **MultiPL-E.** `multipl_e` and 7 per-language keys carry 37 cards each, with a
  spread of 10–15. All date from 2026-04. The top value on each language key is
  Opus 4.6's, and no live board exists.

Saturation reading: IFEval (0.7), MT-Bench (0.4), HumanEval (1.7), MATH-500
(2.0), GSM8K (2.3) and MMLU-Pro (2.7) no longer separate the top 20. Those six
keys carry 0.35–0.60 of the weight in coding, reasoning, chat and `general`.

### 3.2 Where the frontier moved, and whether we hold it

| Benchmark (current version) | Card key(s) present | Cards | Page | Weighted? | Current source |
|---|---|---:|---|---|---|
| SWE-bench Verified | `swe_bench_verified` | 125 | yes | yes | Saturating: provider reports reach 96% |
| SWE-bench Pro | `swe_bench_pro` | 5 | yes | **no** | Scale, public and commercial sets |
| Terminal-Bench 4.0 | `terminal_bench_v4_0` (1 evidence row), `terminal_bench_2` (29), `terminal_bench_3_0` page | 1 / 29 | yes | **no** | tbench.ai and AA |
| LiveCodeBench (recent) | `live_code_bench`, `livecodebench_pro` page | 144 / 0 | yes | yes (stale) | The official board is frozen |
| Aider Polyglot | `aider_polyglot` | 116 | yes | yes (dead) | – |
| HLE / HLE-Rolling | `hle` (6), `hle_tools` (5) | 6 | yes | **no** | AA and Scale. CAIS released HLE-Rolling on 2026-09-17 |
| GPQA Diamond | `gpqa_diamond` | 580 | yes | yes | AA and Epoch (saturating, 96%) |
| AIME 2025 / 2026 | `aime_2025` (30), `aime_2026` (2) | – | yes | yes | MathArena |
| FrontierMath | none | 0 | yes | **no** | Epoch (`frontiermath_tiers_1_3_v2.csv`) |
| ARC-AGI-2 | `arc_agi_2` | 2 | yes | **no** | Epoch copy of ARC Prize data. The top is at 95%, so it is saturating |
| τ²-bench / τ³-banking | `tau2` page. No key on cards | 0 | yes | **no** | AA (`tau2`, `tauBanking`) and taubench.com |
| BrowseComp | `browsecomp` | 4 | yes | **no** | Provider reports only (static) |
| OSWorld-Verified / OSWorld 2.0 | `osworld` | 3 | yes | **no** | Epoch. OSWorld 2.0 was released 2026-06-26 |
| Arena category boards | `arena_elo_*` (April raw values) | 55–211 | yes | yes | Arena. Style control is now the default view |
| Arena WebDev | none (the harvest refused the mapping) | 0 | no | **no** | Arena |
| AA Intelligence Index | `artificial_analysis_quality_index` (130 cards, April) | 130 | yes | **no** (no range either) | AA |
| MMMU-Pro | `mmmu_pro` page. No key on cards | 0 | yes | **no** | AA |
| MTEB(eng, v2) / Multilingual v2 | v1 keys only | 96 | yes | v1 only | MTEB backend JSON |

## 4. The top 10 each major profile should show today

For each major profile, the top 10 products come from the single live board
that fits the profile best. The board is named and linked above each table.
Effort variants are collapsed to the best row.

- **Card** names the card that holds the product. "none" means we have no card.
- **Our status** is the model's position in our ranking today at the CLI floor.
  A percentage is the benchmark coverage of an unranked model.
- **Needs** lists the profile keys the card lacks.

The profiles in their current form cannot rank most of these models, whatever
the backfill. See §3 and §8.

### 4.1 Coding

Board: AA, Terminal-Bench 4.0 column (AA's own harness),
[artificialanalysis.ai/leaderboards/models](https://artificialanalysis.ai/leaderboards/models),
observed 2026-09-23. Scores are percent.

| # | Product | TB 4.0 | Card | Our status | Needs |
|---:|---|---:|---|---|---|
| 1 | GPT-6 Astra | 59.6 | `openai/gpt-6-astra` | unranked (20%) | the 7 legacy keys (a) |
| 2 | Claude Opus 5.5 | 59.6 | `anthropic/claude-opus-5-5` | unranked (0%) | (a) + `scicode` |
| 3 | Claude Fable 5.1 | 55.1 | `anthropic/claude-fable-5-1` | unranked (0%) | (a) + `scicode` |
| 4 | GPT-6 Sol | 43.9 | `openai/gpt-6-sol` | unranked (0%) | (a) + `scicode` |
| 5 | GLM-5.3 | 41.9 | `zhipu/glm-5-3` | unranked (20%) | (a) |
| 6 | Qwen3.8 Max (0902) | 38.9 | `qwen/qwen3-8-max` | unranked (20%) | (a) |
| 7 | GPT-5.6 Terra | 35.4 | `openai/gpt-5-6-terra` | unranked (20%) | (a) |
| 8 | MiMo-V2.6-Pro | 34.8 | none | – | a card, then (a) + `scicode` |
| 9 | Step 5 Preview | 33.3 | `stepfun/step-5-preview` | unranked (0%) | (a) + `scicode` |
| 10 | Muse Spark 1.3 | 33.3 | none | – | a card, then (a) + `scicode` |

(a) The 7 legacy keys are `humaneval`, `swe_bench_verified`,
`live_code_bench`, `aider_polyglot`, `arena_elo_coding`, `arena_elo_overall`
and `terminal_bench`. Four of the seven have no source for a 2026 model:
HumanEval, Aider, LiveCodeBench and Terminal-Bench 1.0.

Cross-checks from the same observation:

- **tbench.ai, Terminal-Bench 4.0**
  ([www.tbench.ai/leaderboard](https://www.tbench.ai/leaderboard); run dates
  per row): GPT-6 Astra 58.2 (2026-09-03), Fable 5.1 57.9 (2026-09-01), Opus 5
  53.9 (2026-07-24), Fable 5 44.6, GLM-5.3 41.8, Grok 4.7 37.6 (2026-09-21).
  Opus 5.5 is not on this board yet.
- **Arena WebDev:** GPT-6 Astra 1793, Fable 5.1 1753, Opus 5 1691, GPT-6 Sol
  1689, Qwen3.8 Max 1671.
- **Arena text, coding, style control:** Fable 5 1552, Opus 4.7 1552, Opus 4.6
  1551, GPT-6 Astra 1543, Kimi K3 1538.

**What we rank now:**

1. `gemini-2-5-pro` 74.68
2. `claude-opus-4-6` 73.11
3. `claude-sonnet-4-5-20250929` 72.71
4. `gpt-5-4` 72.28
5. `gpt-5-4-pro` 72.28
6. `gpt-5-1` 71.29
7. `gpt-5` 71.02
8. `gpt-5-pro` 71.02
9. `gpt-5-2` 71.02
10. `gpt-5-2-pro` 71.02

All ten have `scores_as_of` 2026-04. Positions 7–10 tie because the cards share
one score vector (§7.5).

### 4.2 Reasoning

Board: AA Intelligence Index (same page), observed 2026-09-23.

| # | Product | Index | Card | Our status | Needs |
|---:|---|---:|---|---|---|
| 1 | Claude Opus 5.5 | 57.6 | `anthropic/claude-opus-5-5` | unranked (0%) | all 8 keys (b) |
| 2 | Claude Fable 5.1 | 53.4 | `anthropic/claude-fable-5-1` | unranked (0%) | all 8 keys (b) |
| 3 | GPT-6 Astra | 52.7 | `openai/gpt-6-astra` | unranked (36%) | `math_500`, `bbh`, `ifeval`, `aime_2025`, `mmlu_pro`, `arena_elo_overall` |
| 4 | Muse Spark 1.3 | 48.1 | none | – | a card, then (b) |
| 5 | GPT-6 Sol | 47.5 | `openai/gpt-6-sol` | unranked (0%) | (b) |
| 6 | Grok 4.7 | 46.4 | `xai/grok-4-7` | unranked (0%) | (b) |
| 7 | MiMo-V2.6-Pro | 46.3 | none | – | a card, then (b) |
| 8 | Qwen3.8 Max (0902) | 45.4 | `qwen/qwen3-8-max` | unranked (36%) | as GPT-6 Astra |
| 9 | GLM-5.3 | 44.8 | `zhipu/glm-5-3` | unranked (36%) | as GPT-6 Astra |
| 10 | Grok 4.6 | 44.3 | `xai/grok-4-6` | unranked (0%) | (b) |

(b) The 8 keys are `gpqa_diamond`, `math_500`, `aime_2025`, `mmlu_pro`,
`arena_elo_overall`, `bbh`, `ifeval` and `critpt`. Only `gpqa_diamond`,
`critpt` and possibly `mmlu_pro` and `aime_2025` can still be filled for a new
model. That caps coverage at 0.48, which is below the floor.

Cross-checks:

- **Epoch ECI**, file dated to 2026-09-09: GPT-6 Astra 166.6, Fable 5.1 165.0,
  Fable 5 163.6, Opus 5 162.7, GPT-5.5 Pro 162.4.
- **HLE, Scale**
  ([scale.com/leaderboard/humanitys_last_exam](https://scale.com/leaderboard/humanitys_last_exam)):
  GPT-6 Astra 54.8 (2026-09-09), Fable 5.1 46.5, Gemini 3.1 Pro Preview 46.4,
  Gemini 3.8 Flash 44.5, GPT-5.4 Pro 44.3.

**What we rank now:**

1. `claude-opus-4-6` 71.66
2. `gemini-2-5-pro` 70.49
3. `gemini-2-5-pro-preview-05-06` 68.95
4. `gemini-2-5-pro-preview-06-05` 68.95
5. `o3-pro` 68.64
6. `o3` 68.57
7. `claude-opus-4-20250514` 68.51
8. `o3-deep-research` 68.48
9. `claude-opus-4-5-20251101` 67.32
10. `gemini-2-5-flash` 67.25

### 4.3 Chat

Board: Arena text, overall, style control
([lmarena.ai/leaderboard](https://lmarena.ai/leaderboard)), observed 2026-09-23.

| # | Product | Elo | Card | Our status | Needs |
|---:|---|---:|---|---|---|
| 1 | Claude Fable 5 | 1505.7 | `anthropic/claude-fable-5` | unranked (10%) | (c) |
| 2 | Claude Opus 4.6 | 1504.6 | `anthropic/claude-opus-4-6` | **#1** | – |
| 3 | Claude Opus 4.7 | 1501.7 | `anthropic/claude-opus-4-7` | unranked (10%) | (c) |
| 4 | Muse Spark 1.2 | 1499.6 | none | – | a card, then (c) |
| 5 | Claude Fable 5.1 | 1498.5 | `anthropic/claude-fable-5-1` | unranked (10%) | (c) |
| 6 | Muse Spark 1.3 | 1493.1 | none | – | a card, then (c) |
| 7 | Gemini 3.8 Flash | 1493.0 | `google/gemini-3-8-flash` | unranked (0%) | (c) + `arena_elo_style_control` |
| 8 | Claude Opus 5 | 1492.9 | `anthropic/claude-opus-5` | unranked (10%) | (c) |
| 9 | Muse Spark 1.1 | 1492.6 | none | – | a card, then (c) |
| 10 | Gemini 3.7 Flash | 1489.8 | `google/gemini-3-7-flash` | unranked (0%) | (c) + `arena_elo_style_control` |

(c) The keys are `arena_elo_overall`, `mt_bench`, `alpaca_eval`, `ifeval`,
`mmlu_pro` and `wildbench`. Every one except `arena_elo_overall` is dead for new
models. Chat is the clearest case: the models that lead the chat board sit on
unranked cards, because under the strict mapping 80% of the profile's weight is
on keys that no current source fills.

**What we rank now:**

1. `claude-opus-4-6` 62.31
2. `gpt-4-1` 61.39
3. `gemini-2-5-pro` 60.98
4. `claude-opus-4-20250514` 60.21
5. `deepseek-v3-2` 59.78
6. `deepseek-v3-2-exp` 59.78
7. `claude-sonnet-4-20250514` 58.53
8. `claude-sonnet-4-5-20250929` 58.17
9. `gpt-4-1-mini` 57.47
10. `gemini-2-5-pro-preview-05-06` 55.75

### 4.4 Agentic and tool use

Board: AA GDPval-AA (same AA page), observed 2026-09-23. Scores are percent.

| # | Product | GDPval-AA | Card | Our status | Needs |
|---:|---|---:|---|---|---|
| 1 | Claude Opus 5.5 | 67.3 | `anthropic/claude-opus-5-5` | unranked (0%) | all 10 keys (d) |
| 2 | Claude Fable 5.1 | 61.7 | `anthropic/claude-fable-5-1` | unranked (0%) | (d) |
| 3 | Grok 4.7 | 59.8 | `xai/grok-4-7` | unranked (0%) | (d) |
| 4 | Muse Spark 1.3 | 58.7 | none | – | a card, then (d) |
| 5 | MiMo-V2.6-Pro | 58.7 | none | – | a card, then (d) |
| 6 | Qwen3.8 Max (0902) | 58.4 | `qwen/qwen3-8-max` | unranked (7%) | (d) less `gdpval_aa` |
| 7 | GLM-5.3 | 57.3 | `zhipu/glm-5-3` | unranked (20%) | the 7 legacy keys of (d) |
| 8 | GLM 5.3 Flash | 57.0 | `zhipu/glm-5-3-flash` | unranked (7%) | (d) less `gdpval_aa` |
| 9 | Grok 4.6 | 56.6 | `xai/grok-4-6` | unranked (0%) | (d) |
| 10 | Qwen3.8-Flash-Next | 55.6 | `qwen/qwen3-8-flash-next` | unranked (7%) | (d) less `gdpval_aa` |

(d) The 10 keys are `swe_bench_agent`, `tau_bench`, `web_arena`,
`swe_bench_verified`, `arena_elo_overall`, `terminal_bench`, `ifeval`,
`aa_briefcase`, `automationbench_aa` and `gdpval_aa`. `web_arena` is on no card
at all. `tau_bench` and `terminal_bench` are superseded. `swe_bench_agent` has
no defined source.

Cross-checks:

- **Terminal-Bench 4.0:** see §4.1.
- **AA τ³-banking:** Grok 4.6 50.7, Muse Spark 1.3 50.5, GLM-5.3 50.3.
- **Epoch OSWorld 2.0:** Opus 5 31.4, GPT-5.6 Sol 27.3, Opus 4.8 20.6.
- **Epoch Vending-Bench 2:** GPT-6 Astra $15,510, Opus 5 $11,180, Opus 4.7
  $10,940.

**What we rank now:**

1. `claude-opus-4-6` 71.65
2. `gpt-5-4` 70.19
3. `gpt-5-4-pro` 70.19
4. `gemini-2-5-pro` 69.69
5. `claude-opus-4-20250514` 68.50
6. `gpt-5-1` 68.50
7. `o3-pro` 68.43
8. `o3` 68.39
9. `o3-deep-research` 68.39
10. `gpt-5` 68.30

Only 52 models rank for this profile at all.

### 4.5 Embedding

Board: MTEB(eng, v2), ordered by its own Borda rank. Source:
`https://mteb-leaderboard-backend.hf.space/v1/benchmarks/MTEB(eng,%20v2)/scores`
(plain JSON), observed 2026-09-23. **Mean** is the mean task score.

| # | Model | Mean | Card | Our status |
|---:|---|---:|---|---|
| 1 | jcorners/ingot-8b-r3 | 76.0 | none | – |
| 2 | infgrad/Jasper-Token-Compression-600M | 74.7 | none | – |
| 3 | Kingsoft-LLM/QZhou-Embedding | 76.0 | none | – |
| 4 | ByteDance-Seed/Seed1.5-Embedding | 74.8 | none | – |
| 5 | Qwen/Qwen3-Embedding-8B | 75.2 | `qwen/qwen3-embedding-8b` | #3 |
| 6 | annamodels/LGAI-Embedding-Preview | 74.1 | none | – |
| 7 | Qwen/Qwen3-Embedding-4B | 74.6 | `qwen/qwen3-embedding-4b` | #15 |
| 8 | Bytedance/Seed1.6-embedding | 74.1 | none | – |
| 9 | google/gemini-embedding-001 | 73.3 | `google/gemini-embedding-001` | #13 |
| 10 | codefuse-ai/F2LLM-v2-8B | 72.9 | none | – |

The 7 models without a card need a card first. After that, the profile's keys
(`mteb_overall`, `mteb_retrieval`, `mteb_classification`, `beir`, `miracl`,
`mteb_clustering`) are MTEB **v1** figures, and the live board publishes v2.
Nothing current can fill a v1 key without relabelling v2 as v1, which this audit
does not propose.

On the Multilingual v2 board the top 5 are harrier-oss-v1-27b,
KaLM-Embedding-Gemma3-12B, llama-embed-nemotron-8b, Qwen3-Embedding-8B and
gemini-embedding-001.

**What we rank now:**

1. `nv-embed-v2` (released 2024-08)
2. `bge-m3`
3. `qwen3-embedding-8b`
4. `qwen3-vl-embedding-8b`
5. `jina-embeddings-v4`
6. `jina-embeddings-v4-vllm-retrieval`
7. `voyage-3`
8. `jina-embeddings-v3`
9. `snowflake-arctic-embed-l-v2-0`
10. `e5-mistral-7b-instruct`

The current top `mteb_overall` value on any card belongs to a **reranker**,
`baai/bge-reranker-v2-m3` (70.1). That value should be checked (MODEL-111).

### 4.6 Vision

Board: Arena vision, overall, style control
([lmarena.ai/leaderboard](https://lmarena.ai/leaderboard)), observed 2026-09-23.

| # | Product | Elo | Card | Our status | Needs |
|---:|---|---:|---|---|---|
| 1 | Claude Fable 5 | 1309.5 | `anthropic/claude-fable-5` | unranked (0%) | all 6 keys (e) |
| 2 | Qwen3.8 Max | 1301.8 | `qwen/qwen3-8-max` | unranked (0%) | (e) |
| 3 | Claude Opus 4.7 | 1300.9 | `anthropic/claude-opus-4-7` | unranked (0%) | (e) |
| 4 | Claude Opus 4.6 | 1298.9 | `anthropic/claude-opus-4-6` | #22 | – |
| 5 | Muse Spark 1.3 | 1294.1 | none | – | a card, then (e) |
| 6 | Muse Spark | 1293.7 | `meta/muse-spark` | unranked (0%) | (e) |
| 7 | Muse Spark 1.2 | 1291.5 | none | – | a card, then (e) |
| 8 | Claude Opus 5 | 1289.0 | `anthropic/claude-opus-5` | unranked (0%) | (e) |
| 9 | Claude Fable 5.1 | 1288.9 | `anthropic/claude-fable-5-1` | unranked (0%) | (e) |
| 10 | Gemini 3 Pro | 1288.7 | none. Only `google/gemini-3-pro-preview` has a card | – | a GA card, then (e) |

(e) The keys are `mmmu`, `mathvista`, `docvqa`, `chartqa`, `arena_elo_vision`
and `arena_elo_overall`. The first four are static provider figures. The Arena
keys are live but hold style-control values under a raw-Elo name.

Cross-check, AA MMMU-Pro: Opus 5.5 87.7, GPT-6 Astra 86.9, Gemini 3.8 Flash
85.6.

**What we rank now:**

1. `gpt-4-1` 66.60
2. `llama-4-maverick-17b-128e-instruct` 61.56
3. `gpt-4-1-mini` 61.23
4. `llama-4-scout-17b-16e-instruct` 59.78
5. `gpt-4-1-nano` 59.03
6. `gpt-4o` 58.39
7. `gpt-4o-2024-05-13` 58.39
8. `gpt-4o-2024-08-06` 58.39
9. `gpt-4o-2024-11-20` 58.39
10. `llama-4-scout-17b-16e` 57.88

Only 66 models rank. No model released after April 2025 is in the top 10.

### 4.7 Every profile, grouped

Column definitions:

- **Ranked** counts the models ranked at the CLI floor.
- **No card data** is the share of the profile's weight on keys that no card
  holds.
- **Not read since April** is the share of the weight on keys with no reading
  after 2026-04.
- **Max new-model coverage** is the best coverage a post-mid-2026 model can
  reach. *Strict* counts only exact keys with a current source: AA and Epoch
  evidence keys, `arena_elo_style_control`, and the provider-reported
  `swe_bench_verified`, `mmlu_pro` and `aime_2026`. *Lenient* also reads the
  Arena style-control category boards as `arena_elo_{coding, math,
  hard_prompts, vision, overall}`.

| Profile | Ranked | Ranked #1 (release) | No card data | Not read since April | Max new-model coverage (strict / lenient) |
|---|---:|---|---:|---:|---|
| `coding` | 126 | `gemini-2-5-pro` (2025-03) | 0.00 | 0.64 | 0.36 / 0.56 |
| `reasoning` | 345 | `claude-opus-4-6` (2026-02) | 0.00 | 0.52 | 0.48 / 0.60 |
| `chat` | 191 | `claude-opus-4-6` (2026-02) | 0.00 | 0.80 | 0.20 / 0.50 |
| `agentic` | 52 | `claude-opus-4-6` (2026-02) | 0.12 | 0.68 | 0.32 / 0.44 |
| `embedding` | 96 | `nv-embed-v2` (2024-08) | 0.00 | 1.00 | 0.00 / 0.00 |
| `vision` | 66 | `gpt-4-1` (2025-04) | 0.00 | 1.00 | 0.00 / 0.25 |
| `general` | 191 | `claude-mythos-preview` (2026-04, imputed) | 0.00 | 0.52 | 0.48 / 0.68 |
| `rag` | 67 | `text-embedding-3-large` (2024-01) | 0.00 | 0.72 | 0.18 / 0.30 |
| `safety` | 70 | `claude-opus-4-6` (2026-02) | 0.00 | 1.00 | 0.00 / 0.20 |
| `research_assistant` | 345 | `claude-opus-4-6` (2026-02) | 0.00 | 0.65 | 0.35 / 0.60 |
| `math_competition` | 74 | `gemini-2-5-pro` (2025-03) | 0.00 | 0.75 | 0.25 / 0.35 |
| `data_science` | 202 | `claude-opus-4-6` (2026-02) | 0.00 | 0.80 | 0.20 / 0.40 |
| `code_review` | 191 | `claude-opus-4-6` (2026-02) | 0.00 | 0.75 | 0.25 / 0.50 |
| `cybersecurity` | 191 | `claude-opus-4-6` (2026-02) | 0.00 | 0.75 | 0.25 / 0.45 |
| `devops` | 191 | `claude-opus-4-6` (2026-02) | 0.00 | 0.85 | 0.15 / 0.40 |
| `coding_{python, rust, go, typescript, cpp, java, javascript}` (7) | 108 each | `claude-opus-4-6` (2026-02) | 0.00 | 0.85 | 0.15 / 0.30 |
| `science` | 196 | `gemini-2-5-pro` (2025-03) | 0.00 | 0.44 | **0.56** / 0.64 |
| `science_{chemistry, physics}` | 347 | `claude-opus-4-6` (2026-02) | 0.00 | 0.65 | 0.35 / 0.45 |
| `science_biology` | 235 | `claude-opus-4-6` (2026-02) | 0.00 | 0.65 | 0.35 / 0.50 |
| `science_astronomy` | 235 | `claude-opus-4-6` (2026-02) | 0.00 | 0.70 | 0.30 / 0.40 |
| `education` | 232 | `claude-mythos-preview` (imputed) | 0.00 | 0.75 | 0.25 / 0.40 |
| `education_stem` | 194 | `claude-opus-4-6` (2026-02) | 0.00 | 0.70 | 0.30 / 0.45 |
| `education_humanities` | 108 | `claude-opus-4-6` (2026-02) | 0.00 | 0.85 | 0.15 / 0.35 |
| `medical` | 43 | `gpt-4-1` (2025-04) | 0.00 | 0.90 | 0.10 / 0.20 |
| `medical_clinical` | 20 | `claude-opus-4-6` (2026-02) | 0.00 | 0.90 | 0.10 / 0.20 |
| `medical_radiology` | 54 | `gpt-4-1` (2025-04) | 0.00 | 1.00 | 0.00 / 0.30 |
| `biotech` | 64 | `claude-opus-4-6` (2026-02) | 0.00 | 0.75 | 0.25 / 0.35 |
| `legal` | 83 | `claude-opus-4-6` (2026-02) | 0.00 | 0.90 | 0.10 / 0.20 |
| `legal_contract_review` | 100 | `claude-opus-4-6` (2026-02) | 0.00 | 0.85 | 0.15 / 0.25 |
| `financial` | 191 | `claude-opus-4-6` (2026-02) | 0.20 | 0.85 | 0.15 / 0.30 |
| `financial_analysis` | 40 | `claude-opus-4-6` (2026-02) | 0.25 | 0.90 | 0.10 / 0.25 |
| `financial_compliance` | 41 | `claude-opus-4-6` (2026-02) | 0.00 | 1.00 | 0.00 / 0.15 |
| `accounting` | 82 | `claude-opus-4-6` (2026-02) | 0.15 | 1.00 | 0.00 / 0.15 |
| `writing_creative` | 54 | `claude-opus-4-6` (2026-02) | 0.00 | 0.85 | 0.15 / 0.25 |
| `writing_technical` | 192 | `claude-opus-4-6` (2026-02) | 0.00 | 0.85 | 0.15 / 0.30 |
| `summarization` | 56 | `claude-opus-4-6` (2026-02) | 0.00 | 0.85 | 0.15 / 0.30 |
| `customer_support` | 111 | `gpt-4-1` (2025-04) | 0.00 | 0.85 | 0.15 / 0.35 |
| `roleplay` | 109 | `deepseek-v3-2` (2025-12) | 0.00 | 0.75 | 0.25 / 0.40 |
| `content_moderation` | 70 | `gpt-4` (2023-11) | 0.00 | 1.00 | 0.00 / 0.15 |
| `translation` | 36 | `llama-4-maverick-17b-128e-instruct` (2025-04) | 0.30 | 0.90 | 0.10 / 0.20 |
| `multilingual` | 36 | `llama-4-maverick-17b-128e-instruct` (2025-04) | 0.20 | 0.90 | 0.10 / 0.25 |
| `speech_to_text` | **0** | none | 0.50 | 1.00 | 0.00 / 0.20 |
| `text_to_speech` | 26 | `claude-opus-4-6` (2026-02), an LLM | 0.50 | 0.85 | 0.15 / 0.35 |
| `image_generation` | **0** | none | 0.60 | 1.00 | 0.00 / 0.40 |

Group notes:

- **Coding variants.** The 7 per-language profiles, plus `code_review`,
  `devops` and `cybersecurity`, inherit coding's dead keys. They also weight
  MultiPL-E, which has no reading after 2026-04.
- **Domain profiles.** The medical, legal, financial, accounting, science
  sub-profiles and `biotech` rest on MMLU subjects, MedQA, PubMedQA, LegalBench,
  FinBench and FinQA. FinQA and FLORES are on no card. None of these keys has a
  source that covers 2026 models.
- **Writing, chat-adjacent and support profiles.** `writing_*`,
  `summarization`, `customer_support`, `roleplay` and `education_humanities`
  rest on MT-Bench, AlpacaEval, WildBench and IFEval. All four are dead or
  saturated.
- **Profiles that rank nothing, or the wrong class.** `speech_to_text` and
  `image_generation` rank no model, because their primary keys (WER, FID, CLIP
  score) are on no card. `text_to_speech` ranks LLMs, because only its Arena and
  MT-Bench keys have data.

## 5. Normalization bounds that clip

Formula: `_normalize_benchmark` maps `(value − low) / (high − low)` onto 0–100
and clamps it. A value above `high` scores 100, so every model above the bound
ties.

| Key | Bound (low, high) | Top value on a card | Cards above `high` | Current frontier value (source) |
|---|---|---:|---:|---|
| `arena_elo_overall` | (1000, 1400) | 1467.4 | 9 | 1505.7, text overall style control (Arena) |
| `arena_elo_coding` | (1000, 1400) | 1520.3 | 21 | 1552.4, text coding style control. WebDev 1793.1 |
| `arena_elo_math` | (1000, 1400) | 1458.3 | 12 | 1526.3, text math style control |
| `arena_elo_hard_prompts` | (1000, 1400) | 1534.7 | 51 of 103 | 1533.1 |
| `arena_elo_style_control` | (1000, 1400) | 1507.2 | 76 of 147 | 1505.7 |
| `arena_elo_vision` | (1000, 1400) | 1310.0 | 0 | 1309.5. Not clipping yet, with 90 points of headroom |
| `gpqa_diamond` | (20, 80) | 96.0 | **94** | 96.3 (AA), 95.8 (Epoch) |
| `swe_bench_verified` | (0, 70) | 96.0 | 22 | 96.0 (Anthropic system card, Opus 5); 83.5 (Epoch, Opus 4.7) |
| `live_code_bench` | (0, 60) | 91.7 | **61** | Board frozen |
| `aime_2025` | (0, 80) | 95.3 | 15 | 100 (Epoch OTIS mock AIME) |
| `aime_2026` | (0, 80) | 95.3 | 2 | MathArena |
| `swe_bench_agent` | (0, 60) | 62.8 | 6 | Undefined source |
| `mmlu_pro` | (20, 90) | 87.5 | 0 | Our page records 91.16, so the next reading clips |
| `mathvista` | (20, 80) | 73.7 | 0 | Our page records 85.2, so the next reading clips |
| `arc_agi_2` (not weighted) | (0, 80) | – | – | 95.0 (Epoch) |
| `terminal_bench_2` (not weighted) | (0, 80) | – | – | 91.4 (AA, TB 2.1) |
| `hle` (not weighted) | (0, 65) | 40.0 | 0 | 61.4 (AA). Close to the ceiling |

How much the top flattens: among coding candidates, 21 score 100 on
`arena_elo_coding`, 22 score 100 on `swe_bench_verified` and 61 score 100 on
`live_code_bench`. Those three keys carry 0.40 of coding's effective weight.

Two further defects:

- **`hle` is defined twice** in the `BENCHMARK_RANGES` literal, first as
  (0, 50) and then as (0, 65). The later entry silently wins.
- **The Arena scale drifts and mixes views.** Opus 4.6's card reads
  `arena_elo_overall` 1410 (April, raw view). Today the same model reads 1504.6
  on the default style-control view. A fixed Elo bound compares readings from
  different dates and different views as if they shared a scale.

## 6. Source map

**Live** means a board whose row is "this model's standing on that date",
dated by the observation. **Static** means a published result that needs its
own publication day. **Plain** means a plain HTTP GET was enough on
2026-09-23. **FC** means Firecrawl or a browser would be needed.

| Benchmark(s) | Primary source | Kind | Fetch |
|---|---|---|---|
| `gpqa_diamond`, `scicode`, `critpt`, `aa_lcr`, `gdpval_aa`; and unweighted `hle`, `tau2`, `tauBanking`, TB 2.1 / 4.0 / Hard, `ifbench`, `mmmuPro`, Intelligence Index | [artificialanalysis.ai/leaderboards/models](https://artificialanalysis.ai/leaderboards/models) (Next.js flight payload, 674 rows) | Live | Plain |
| `aa_briefcase`, `automationbench_aa`, `gdp_pdf_aa` | `artificialanalysis.ai/evaluations/<id>` (URLs on our pages) | Live | Not in the models payload. Not fetched this session |
| `arena_elo_style_control`, and Arena text coding, math and hard-prompts, vision, WebDev | [lmarena.ai/leaderboard](https://lmarena.ai/leaderboard) and `lmarena.ai/leaderboard/text/<category>`. Each category URL server-renders its own snapshot | Live | Plain |
| `arena_elo_overall` (raw view) | Arena. The raw view is not in the server HTML | Live | FC, or accept style control (§8) |
| Terminal-Bench 4.0 | [www.tbench.ai/leaderboard](https://www.tbench.ai/leaderboard) (flight payload, per-row dates) | Live | Plain |
| SWE-bench Verified, Lite, Multimodal and Multilingual | [SWE-bench leaderboards.json](https://raw.githubusercontent.com/SWE-bench/swe-bench.github.io/master/data/leaderboards.json) (per-row dates; newest 2026-02-26) | Live board, now stalled | Plain |
| SWE-bench Pro, HLE | [scale.com/leaderboard/swe_bench_pro_public](https://scale.com/leaderboard/swe_bench_pro_public), [humanitys_last_exam](https://scale.com/leaderboard/humanitys_last_exam) (`entries` JSON with `createdAt`) | Live | Plain |
| `aider_polyglot` | [polyglot_leaderboard.yml](https://raw.githubusercontent.com/Aider-AI/aider/main/aider/website/_data/polyglot_leaderboard.yml) (newest 2025-10-03) | Live board, now dead | Plain |
| `live_code_bench` | [performances_generation.json](https://livecodebench.github.io/performances_generation.json) (problems to 2025-04) | Live board, now dead | Plain |
| `gpqa_diamond`, `swe_bench_verified`, FrontierMath, OTIS AIME, OSWorld 2.0, ARC-AGI-2, HLE, SimpleQA Verified, Vending-Bench 2, WebDev Arena, CursorBench, ECI | [epoch.ai/data/benchmark_data.zip](https://epoch.ai/data/benchmark_data.zip) (CSV, CC-BY, per-run `Started at`) | Live (Epoch runs); `_external` files copy third-party results | Plain |
| `aime_2025`, `aime_2026` | [matharena.ai](https://matharena.ai/) (model rows in the HTML) | Live | Plain |
| `mteb_*`, `beir`, `miracl` | [MTEB backend JSON](https://mteb-leaderboard-backend.hf.space/v1/benchmarks/MTEB(eng,%20v2)/scores) (v2 benchmarks, per-task scores). The `hf.space` page is a SvelteKit shell | Live | Plain (the JSON API) |
| `tau_bench` → τ²/τ³ | [taubench.com](https://taubench.com/) (top 3 in the HTML) and AA | Live | Plain for AA. Full Sierra board not checked |
| OSWorld | [os-world.github.io](https://os-world.github.io/). OSWorld 2.0 since 2026-06-26 | Live | Via Epoch CSV |
| ARC-AGI-2 | [arcprize.org](https://arcprize.org/media/data/models.json) (model list). The evaluations JSON path returned 404 | Live | Via Epoch CSV |
| `humaneval`, `math_500`, `bbh`, `ifeval`, `mt_bench`, `gsm8k`, `hellaswag`, `arc_challenge`, `truthfulqa`, `mmlu_*`, `multipl_e*`, `mgsm`, `mmmu`, `mathvista`, `docvqa`, `chartqa`, `medqa`, `pubmedqa`, `medmcqa`, `legalbench`, `finbench`, `browsecomp`, provider `swe_bench_verified` | Papers, model cards and system cards | Static | Plain for most provider pages. Each needs its stated day |
| `alpaca_eval`, `wildbench`, `mmlu_pro`, `helm_safety`, `bbq`, `toxigen` | Their own leaderboards or HF spaces | Live-ish | Not checked this session |

Every core source is reachable over plain HTTP or JSON. Firecrawl is needed
only as a fallback.

## 7. Root causes

### 7.1 There is no score-ingestion pipeline. Confirmed

- `.github/workflows/daily-research.yml` (MODEL-5) runs
  `scripts/seed_models_dev.py --new-only`. It writes identity, pricing, context
  and modalities for models that have no card yet, and never touches
  `benchmarks`. Its own PR text says the cards are "Typically around 10%
  completeness".
- `.github/workflows/curation-benchmarks.yml` (MODEL-10) watches the sources
  cited by `benchmarks/*.md` pages and drafts edits to **those pages**. It
  classifies a `leaderboard_movement` but writes nothing to a card
  (`docs/curation-loop.md`: "The loop edits Markdown, never the graph").
- `scripts/fetch_ranking_leaderboards.py`, the AA and Arena harvest, is invoked
  by no workflow. It ran by hand, once (commit `dec15e7`, 2026-09-10).
- Every flat score has `benchmark_as_of` ≤ 2026-04. The later commits that
  touch `benchmark_as_of` add new cards with empty blocks.

### 7.2 Silent exclusion. Confirmed, with a second effect

`rank_report` keeps an `unranked` list, but a ranked top-N shows none of it.
MODEL-110 covers that. There is a second, quieter effect: ordering uses the
`conservative_lower_bound`. A missing benchmark counts as 0 toward the score
that orders ranked rows. So a new model that clears the floor still sorts below
an old model with full coverage of dead benchmarks. `gemini-2-5-pro` is #1 in
coding partly because it carries `scicode` evidence (coverage 1.0) and
`claude-opus-4-6` does not (coverage 0.8).

### 7.3 One-time live readings. Confirmed

No evidence row is dated after 2026-09-10. Of 1,223 evidence rows, 1,122 come
from one day. Nothing re-reads a board, so every live reading is stale from the
moment it lands. The newest models (Opus 5.5, GPT-6 Sol, GPT-6 Luna, Grok 4.7)
are already on AA and Arena and have no reading on their cards.

### 7.4 Saturated and dead weights. Confirmed, and larger than stated

- **Saturated:** see §3.1. Six high-weight keys have a top-20 spread of 2.7 or
  less.
- **Dead at source:** Aider (2025-10), LiveCodeBench (2025-04),
  Terminal-Bench 1.0 and τ-bench are superseded. Our own benchmark pages already
  mark `terminal_bench`, `tau_bench` and `arc_challenge` as `superseded`, yet
  the profiles still weight them.
- **Structural:** under the strict mapping, 1 of 51 profiles can rank a new
  model (§4.7). This is the cause that the backfill (MODEL-109) cannot reach.

### 7.5 Additional causes found

- **Clipping bounds** flatten the top (§5).
- **Cloned scores.** 80 of 116 cards that hold 4 or more coding keys share an
  identical coding vector with another card. The groups span 25 vectors:
  - 13 OpenAI cards (`gpt-5-2`, `gpt-5-2-codex`, `gpt-5-3-codex-spark`,
    `gpt-5-4-mini`, `gpt-5-4-nano`, …).
  - 6 Gemini 2.5 Flash cards, including `-image` and `-preview-tts`.
  - 6 Grok 4 cards.
  - 4 GPT-4o snapshots.

  Some are true aliases, such as a dated id and `-latest`. Many are
  family-level copy-downs onto distinct products. 82 cards in 33 groups share
  an identical *full* score block of 8 or more keys.
- **Imputation.** Commit `ccbc149` (2026-04-08) set Claude Mythos Preview's
  `arena_elo`, `mmlu_pro`, `humaneval`, `math_500`, `ifeval` and `mt_bench` "at
  Opus 4.6 floor values". Those scores make it #1 in `general` and `education`.
  This breaks the rule that a null beats a guess.
- **Catalogue gaps.** Discovery reads only models.dev. These models lack cards:
  Muse Spark 1.1, 1.2 and 1.3 (Meta), MiMo-V2.6-Pro (Xiaomi), Gemini 3 Pro
  (GA), and 7 of the MTEB(eng, v2) top 10.
- **Variant refusals.** The 2026-09-10 harvest correctly refused to fold
  style-control category boards into raw-Elo keys, and refused `(high)` and
  `(xhigh)` rows. But Arena's server-rendered default is now style control.
  Until the key definitions change, the raw category keys cannot be refreshed
  over plain HTTP.

## 8. Proposals for Jamie

**These are proposals, and nothing here is implemented.** Changing a weight, a
bound or a floor is Jamie's call. Weights are shown before
`_apply_verified_additions` rescales them (the rescale is ×0.8 where a profile
has verified additions).

### 8.1 Profile benchmark sets and weights

| Profile | Drop | Proposed weights (sum 1.0) |
|---|---|---|
| `coding` | `humaneval`, `aider_polyglot`, `live_code_bench`, `terminal_bench` (v1) | `terminal_bench_4` 0.30, `swe_bench_pro` 0.15, `arena_sc_coding` 0.15, `arena_webdev` 0.15, `arena_elo_style_control` 0.15, `swe_bench_verified` 0.10 |
| `reasoning` | `math_500`, `bbh`, `ifeval`, `aime_2025` | `hle` 0.25, `frontiermath` 0.15, `aime_2026` 0.15, `arena_sc_hard_prompts` 0.15, `gpqa_diamond` 0.10, `mmlu_pro` 0.10, `arena_elo_style_control` 0.10 |
| `chat` | `mt_bench`, `alpaca_eval`, `wildbench`, `ifeval` | `arena_elo_style_control` 0.40, `arena_sc_hard_prompts` 0.15, `ifbench` 0.15, `simpleqa_verified` 0.10, `aa_omniscience` 0.10, `mmlu_pro` 0.10 |
| `agentic` | `web_arena`, `tau_bench`, `swe_bench_agent`, `terminal_bench` (v1), `ifeval` | `terminal_bench_4` 0.25, `tau3_banking` 0.20, `osworld_2` 0.15, `swe_bench_pro` 0.15, `vending_bench_2` 0.10, `browsecomp` 0.10, `arena_elo_style_control` 0.05 |
| `embedding` | the v1 keys | `mteb_eng_v2` 0.35, `mteb_multilingual_v2` 0.25, `mteb_v2_retrieval` 0.25, `mteb_v2_classification` 0.15 (new keys, not relabelled v1) |
| `vision` | `docvqa` and `chartqa` shrink (saturated) | `arena_sc_vision` 0.35, `mmmu_pro` 0.25, `mmmu` 0.10, `mathvista` 0.10, `arena_elo_style_control` 0.10, `docvqa` 0.05, `chartqa` 0.05 |

Under these weights, a frontier model that AA and Arena already list would
reach roughly 0.7–1.0 coverage in each profile from plain-HTTP sources alone.
Examples: coding reaches 0.85 without SWE-bench Pro, reasoning 0.90 and
embedding 1.0 for any model on MTEB.

The minor profiles should inherit the same substitutions. The Arena
style-control keys replace `arena_elo_overall` in all 49 profiles that use it.
IFBench replaces IFEval. MultiPL-E and the MMLU subjects stay only where no
current source exists, and their weight should be flagged as such.
`speech_to_text` and `image_generation` should be suspended or re-sourced; the
Arena text-to-image and image-edit boards are live.

The new keys need new benchmark pages and `BENCHMARK_RANGES` entries. Arena
style-control scores get **new** keys (`arena_sc_*`) rather than being written
under the raw-Elo names, which preserves the harvest's refusal rule.

### 8.2 Bounds

1. Give percentage benchmarks the natural ceiling of 100: GPQA (20, 100),
   SWE-bench Verified, LiveCodeBench, AIME, ARC-AGI-2, Terminal-Bench 2,
   MMLU-Pro and MathVista.
2. Stop fixed-Elo normalization for Arena. Normalize within one snapshot, as
   the gap to the snapshot leader or a percentile. Require every Arena value in
   one ranking to share an observation date. If fixed bounds stay, use
   (1100, 1600) for the text keys and (1100, 1850) for WebDev, and review them
   quarterly.
3. Remove the duplicate `hle` entry.

### 8.3 Floor and policy questions

- **The floors are not the problem.** Do not lower the 0.50 CLI floor. With
  §8.1 in place, new models clear it.
- **Staleness policy.** Should a live reading older than N days (proposed: 45)
  be flagged in the output, or stop counting? Should the ranking publish the
  oldest `evidence_date` it used?
- **Effort variants.** The harvest takes `(max)` as the product row. Confirm
  that rule, or adopt "best published effort, named in `configuration`".
- **Provider self-reports.** Confirm they may fill a profile key, labelled
  `provider_self_report`, when no independent board carries the benchmark
  (SWE-bench Verified, BrowseComp, MMMU).

## 9. Fix list

| Fix | Ticket |
|---|---|
| Backfill evidence for the 88 post-May models from AA, the Arena category URLs, tbench.ai, Epoch, MathArena and Scale, all plain HTTP. Re-read the live boards for every model in any profile's current top 30 on one observation date | **MODEL-109** |
| Tell MODEL-109 that its done-criterion (current-generation models in the coding, reasoning and chat top 10) cannot be met without §8.1. Under today's profiles, coding and chat top out at 0.36 and 0.20 coverage for new models | **MODEL-109**, blocked by the new profile ticket |
| Add cards for Muse Spark 1.1, 1.2 and 1.3, MiMo-V2.6-Pro, Gemini 3 Pro (GA) and the MTEB leaders | **MODEL-109** (one-time), then **MODEL-113** (ongoing) |
| Show unranked models with release date and coverage. Say when a model is unranked because the profile weights dead benchmarks. Publish `scores_as_of` and the oldest evidence date | **MODEL-110** |
| Check the cloned score vectors (13-card OpenAI group, Gemini 2.5 Flash, Grok 4, GPT-4o) against sources. Null what cannot be sourced. Remove the Mythos imputation. Check the reranker's `mteb_overall` | **MODEL-111** |
| Add a harness assertion: no two distinct products share an identical score block unless the cards are declared aliases | **MODEL-111** |
| Gather step: use the §6 source map (plain-HTTP fetchers first). Re-check at +1, +7 and +30 days | **MODEL-113** |
| Discovery beyond models.dev (Meta, Xiaomi, embedding labs) | **MODEL-113** |
| **New: scheduled leaderboard refresh.** Generalize `scripts/fetch_ranking_leaderboards.py` to AA, the Arena category URLs, tbench.ai, Epoch, MTEB JSON, MathArena and Scale. Run it weekly in CI and open a human-reviewed PR, like research PRs. This covers *existing* models; MODEL-113 is triggered by new releases | new ticket |
| **New: profile refresh** (§8.1). Jamie decides the sets and weights, then engine.py changes. Add a guard test: each profile's strict live coverage must stay ≥ `MIN_BENCHMARK_COVERAGE`, and no weighted key may be on a page marked `superseded` or `saturated` | new ticket |
| **New: bounds** (§8.2), including the duplicate `hle` key | new ticket, or fold into the profile refresh |
| **New: dead keys.** `web_arena`, `finqa`, `flores`, `clip_score`, `fid`, `mos_tts` and `wer_librispeech` are on no card. `speech_to_text` and `image_generation` rank nothing | fold into the profile refresh |

## Method and reproduction

- Card analysis used the repository's own loaders and `rank_report` at `main`
  `d020f07`.
- The AA and Arena payloads were parsed with `iter_next_f_strings`,
  `parse_aa_models` and `parse_arena_snapshots` from
  `scripts/fetch_ranking_leaderboards.py`.
- Products were collapsed by stripping effort qualifiers and keeping the best
  row.
- Raw pages were cached outside the repository and are not committed.
- Every figure above can be reproduced by re-fetching the URLs in §6. A live
  figure is valid only for its observation date.
