# Audit: card merges of 2026-09-24 (MODEL-127)

Score-only PRs merged automatically on 2026-09-24 (MODEL-123 decision). This
is the manual audit promised for them: #171, #172, #176–#197 and #200.

Read date for every source: 2026-09-24.

## Method

1. Every changed value was extracted by diffing each PR's merge commit against
   its parent: `benchmarks.scores` changes and every new `benchmarks.evidence`
   row.
2. Each evidence row was then checked against current `main`. Rows that a later
   PR had already removed are listed, but not re-audited.
3. Each remaining row was compared with its own `source_url`. The checks were:
   - the value, to the stated rounding;
   - the model identity, meaning the row named on the source is this card's
     model and not a sibling variant;
   - the effort and conditions, including the MODEL-123 highest-effort rule
     where a board lists several efforts;
   - the date.

   Machine-readable sources were checked by script for every row. These were the
   Arena dataset, Epoch `benchmark_data.zip`, the MTEB backend JSON, the Open
   LLM Leaderboard result files and `contents` dataset, and the τ-bench
   submission JSON. Board pages (MathArena, Scale Labs, tbench.ai, CursorBench)
   were parsed from their served HTML and payload. Provider documents (system
   cards, model cards, READMEs, launch posts) were read and every value found in
   them.
4. **Nothing was sampled. Every surviving row in every PR was checked**, so the
   error rates below are exact, not estimates. That is more than the brief
   asked for: the premier set in full, plus about 10% elsewhere.

Plain HTTP was used throughout except for two openai.com pages that return
403. Firecrawl fetched those two, for 2 of the 50 allowed credits.

## Result in one paragraph

4,052 evidence rows survive on `main`. Every one has the value its source
states, and every one has the correct date. No row cites an excluded source.
No `scores` value was set: the only `scores` changes are 3,724 removals of
cloned values (MODEL-125), so no null was replaced by a guess. The one class of
error is an **effort condition**. MODEL-109 (#171, #194, #196) took the Arena
raw-`text` rows (`arena_elo_overall`, `arena_elo_coding`) from the
default-effort variant, even where the dataset lists a higher-effort variant of
the same model: 18 rows on 9 cards. #200 applied the MODEL-123
highest-effort rule to the style-controlled rows of those same cards, which
left each card mixing two variants. The 18 rows are corrected in the MODEL-127
PR to the highest-effort row of the same dataset snapshot.

## Per PR

"Checked" counts the evidence rows still on `main`. "Removed later" counts rows
this PR added that a later PR had already removed; these were not re-audited.
"Premier" counts the rows among those checked that belong to a
`premier/slice-1.yaml` model.

| PR | Scope | Checked | Premier | Right | Wrong | Error rate | Removed later | `scores` changes |
|---|---|---:|---:|---:|---:|---:|---:|---|
| #171 | Anthropic flagships (MODEL-109) | 27 | 21 | 17 | 10 | **37%** | 9 | none |
| #172 | xAI flagships (MODEL-109) | 0 | 0 | – | – | – | 1 | none |
| #176 | 01.AI Yi-Coder (MODEL-125) | 4 | 0 | 4 | 0 | 0% | 0 | 6 removed |
| #177 | Allen AI OLMoE | 4 | 0 | 4 | 0 | 0% | 0 | 6 removed |
| #178 | Anthropic incl. Mythos Preview | 23 | 0 | 23 | 0 | 0% | 0 | 74 removed |
| #179 | BAAI reranker | 0 | 0 | – | – | – | 0 | 2 removed |
| #180 | DeepSeek | 66 | 0 | 66 | 0 | 0% | 0 | 561 removed |
| #181 | Gemini 2.5 Flash, Gemma 4 | 1 | 0 | 1 | 0 | 0% | 0 | 522 removed |
| #182 | IBM Granite Embedding | 0 | 0 | – | – | – | 0 | 40 removed |
| #183 | Jina | 0 | 0 | – | – | – | 0 | 52 removed |
| #184 | Meta Llama | 2 | 0 | 2 | 0 | 0% | 0 | 376 removed |
| #185 | Mistral | 71 | 0 | 71 | 0 | 0% | 0 | 362 removed |
| #186 | Nomic | 1 | 0 | 1 | 0 | 0% | 0 | 54 removed |
| #187 | Nous Hermes 3 | 4 | 0 | 4 | 0 | 0% | 0 | 10 removed |
| #188 | OpenAI GPT-5, GPT-4o, o-series | 7 | 1 | 7 | 0 | 0% | 0 | 955 removed |
| #189 | MiniCPM-V | 7 | 0 | 7 | 0 | 0% | 0 | 14 removed |
| #190 | Qwen | 13 | 0 | 13 | 0 | 0% | 0 | 336 removed |
| #191 | TII Falcon | 4 | 0 | 4 | 0 | 0% | 0 | 24 removed |
| #192 | xAI Grok | 0 | 0 | – | – | – | 0 | 324 removed |
| #193 | Zhipu GLM-4 | 4 | 0 | 4 | 0 | 0% | 0 | 6 removed |
| #194 | OpenAI flagships (MODEL-109) | 19 | 5 | 15 | 4 | **21%** | 3 | none |
| #195 | Google flagships (MODEL-109) | 12 | 6 | 12 | 0 | 0% | 2 | none |
| #196 | DeepSeek flagships (MODEL-109) | 11 | 7 | 7 | 4 | **36%** | 3 | none |
| #197 | Qwen flagships (MODEL-109) | 3 | 0 | 3 | 0 | 0% | 0 | none |
| #200 | Refreshed profiles (MODEL-123) | 3,769 | 901 | 3,769 | 0 | 0% | 0 | none |
| **All** | | **4,052** | **941** | **4,034** | **18** | **0.44%** | 18 | 3,724 removed |

**Three PRs are above the 10% threshold: #171 (37%), #194 (21%) and #196
(36%).** All 18 errors belong to one class: the effort condition on
MODEL-109's raw Arena rows. No value in them was transcribed wrongly. The
error is mechanical and has one cause, and this audit checked every row, so
there is nothing left to widen the check to. The 18 rows are fixed in this PR.

### #171, #194, #196: what was wrong

Each of these PRs attached `arena_elo_overall` and `arena_elo_coding` from the
Arena dataset's `text` subset (split `latest`, published 2026-09-13). For nine
cards the dataset lists a higher-effort variant that the PR did not use:

| Card | Row taken | Highest-effort row |
|---|---|---|
| anthropic/claude-opus-4-20250514 | claude-opus-4-20250514 | claude-opus-4-20250514-thinking-16k |
| anthropic/claude-opus-4-5-20251101 | claude-opus-4-5-20251101 | claude-opus-4-5-20251101-high-32k |
| anthropic/claude-opus-4-6 (premier) | claude-opus-4-6 | claude-opus-4-6-high |
| anthropic/claude-sonnet-4-20250514 | claude-sonnet-4-20250514 | claude-sonnet-4-20250514-thinking-32k |
| anthropic/claude-sonnet-4-5-20250929 | claude-sonnet-4-5-20250929 | claude-sonnet-4-5-20250929-high-32k |
| openai/gpt-5-4 (premier) | gpt-5.4 | gpt-5.4-high |
| openai/o3-mini | o3-mini | o3-mini-high |
| deepseek/deepseek-v3-2-exp | deepseek-v3.2-exp | deepseek-v3.2-exp-thinking |
| deepseek/deepseek-v3-2 | deepseek-v3.2 | deepseek-v3.2-thinking |

Each value was the right number for the row it named. The row was the wrong
one under MODEL-123. #200 already moved the same cards' style-controlled rows
to the highest-effort variant. It removed the default-variant
`arena_elo_style_control` rows that MODEL-109 had added, but left the raw rows
alone. The premier set's own clause-1 evidence (`premier/slice-1.yaml`) also
names the highest-effort rows, for example `claude-opus-4-6-high`.

Everything else in these PRs was confirmed:

- **Opus 5.5 system card (dated 2026-09-22), Table 8.1.A.** SWE-bench Pro 89.9,
  Multilingual 93.9, Multimodal 61.4, Terminal-Bench 4.0 66.4, TB-Science 58.7,
  HLE 64.4 and 67.7 with tools. The card notes that Terminal-Bench 4.0 is
  reported at xhigh; the row says so. **SWE-bench Pro 89.9 is confirmed.** It
  is Anthropic's own run, and far above Scale's public board, whose top entry
  is 61.5. The row's `source_kind` says `provider_self_report`.
- **Fable 5.1 and Mythos 5.1 system card (dated 2026-09-01), section 8.** Fable
  5.1: SWE-bench Pro 81.2, Multilingual 89.1, Multimodal 54.7, TB 4.0 55.8 (15
  trials per task), TB-Science 52.6. Mythos 5.1: TB 4.0 60.9 (10 trials per
  task). **ARC-AGI-2 90.0 is confirmed.** Section 8.16 says the ARC Prize
  Foundation reports a verified 90% at max effort on the semi-private set. The
  body text attributes each value to one model by name, as the rows say.
- **DeepSeek-V4.1-Flash README, "Comparison with frontier models".** All 7
  values are in the DS-V4.1-Flash column: GPQA 90.9, HLE 36.8 (the full-set
  value, not the text-only 39.1), HLE with tools 63.9, TB 2.1 90.6, TB 3.0 30.0,
  TB 4.0 31.2, CyberGym 88.1. The model runs at `reasoning_effort=100`.
- **Gemini 3.8 Flash model card (published 2026-09-02).** TB 2.1 89.4 and
  CharXiv 86.2. The first column is confirmed as Gemini 3.8 Flash because its
  TB 4.0 figure, 19.1, matches tbench.ai's Gemini 3.8 Flash row, 19.09.
- **Scale HLE.** Gemini 3.8 Flash 44.52, entry created 2026-09-09.

The values above the old bounds were checked with extra care. SWE-bench Pro
89.9 and ARC-AGI-2 90 are confirmed as above. GPQA 95.39 (Gemini 3.8 Flash,
#195) is Epoch's `gemini-3.8-flash_high` run. A later PR had already removed
that #195 row, and the value is not on `main`. `gpqa_diamond` is a MODEL-116
key, so it was left alone.

### #172

Its one row, Grok 4.7 Terminal-Bench 4.0 at 37.58, was superseded by #200's row
with the same value and the same date. #200's row was checked and is right.

### #176–#193 (MODEL-125)

- **Open LLM Leaderboard v1 result files.** 129 rows, all matching their
  harness task, shot count and metric: arc 25-shot `acc_norm`, hellaswag
  10-shot `acc_norm`, truthfulqa `mc2`, winogrande and gsm8k 5-shot `acc`, and
  MMLU subtasks 5-shot `acc`.
- **Open LLM Leaderboard v2 `contents`.** 32 rows, all matching the `* Raw`
  column times 100.
- **Mythos Preview system card and Project Glasswing page.** 20 rows, all
  confirmed. SWE-bench Verified 93.9 is in both documents. GPQA 94.55 is in
  section 6.6. Terminal-Bench 2.0 82.0 is on the Glasswing page, and the system
  card shows 82%.
- **DeepSeek R1, V3 and V3.2-Exp READMEs; Meta Llama 3.1 and 3.3 cards;
  Nomic v2; MiniCPM-V-4; Qwen2-VL-7B; simple-evals; aider polyglot YAML;
  Anthropic's 3.5 announcement.** 27 rows, all confirmed, each in the named
  column or row.

### #195, #197

The Arena rows match the dataset, and the self-reports and the Scale HLE row
are confirmed.

### #200

3,769 rows, broken down by source below.

**Arena, from the Hugging Face dataset** (3,043 rows across 6 subsets). Every
rating matches the named row, to 2 decimal places, in the stated subset and
category, and every date equals `leaderboard_publish_date`. Model identities
were reviewed card by card, and no sibling variant was substituted: for
example, `gemini-3.5-flash-lite` stays on its own card and does not appear on
the Flash card. Where the dataset lists several efforts, #200 used the highest
in every case.

**Epoch, from `benchmark_data.zip`** (439 rows). Epoch's own runs (GPQA
Diamond, FrontierMath, SimpleQA Verified, SWE-bench Verified) match on value
and on run start. The external board copies (FrontierCode, Vending-Bench 2,
DeepSWE, OSWorld 2, Terminal-Bench 2) match on value. No row uses a
lower-effort run where a higher one exists for the same released model. Three
identity questions were checked and are right:

- Vending-Bench "DeepSeek-V3.2" is Epoch's `DeepSeek-V3.2-Exp_unknown`.
- FrontierCode "Kimi K2.7" is `kimi-k2.7-code`.
- GPT-5.5 GPQA uses `gpt-5.5_low` because the only higher runs are
  `*-pre-release`, which is not the released model.

**MTEB backend JSON** (184 rows). `meanTask` and the `scoresByTaskType`
averages match. Each task-type average covers every task of that type.

**Other boards and self-reports.** Every row matches its source:

- τ-bench submission JSON: 21 rows. `pass_1`, `evaluation_date`, effort and
  retrieval config all match.
- MathArena AIME 2025 and 2026: 62 rows. Each is the highest-effort row.
- Scale HLE and SWE-bench Pro (public): 42 rows. `createdAt` matches.
- tbench.ai Terminal-Bench 4.0: 15 rows. Each is the highest-effort row, even
  where a lower effort scored more (Opus 5 max 51.82, against xhigh 53.94).
- CursorBench 4.0: 10 rows. The max row is used, or "Extra High" where no max
  row exists.
- Opus 5.5 system card HealthBench Professional: 3 rows (Opus 5.5 65.6,
  Opus 5 59.8, Fable 5.1 62.1). Conditions are stated in figure 8.15.2.A.

## Excluded sources and nulls

- No surviving row cites a host or benchmark named in
  `tests/test_removed_sources.py`. The five rows these PRs added from those
  sources (from #171, #194 and #196) were already removed by
  MODEL-117 before this audit. The test passes.
- No `benchmarks.scores` value was set by any of the 25 PRs. MODEL-125's
  3,724 changes are removals of cloned values, which leave nulls. Every
  evidence row carries a `source_url` and an `evidence_date`.

## Left as it is (not errors)

- Twelve card and benchmark pairs carry the same value twice. A MODEL-109
  row and a #200 row both exist: 11 Arena style-control rows, and Gemini 3.8
  Flash on HLE. The values agree, so the pairs are redundant, not wrong.
  Fable 5.1 `terminal_bench_v4_0` carries two different rows on purpose:
  Anthropic's self-report 55.8 and the tbench.ai board 57.88. Deduplication is
  a separate clean-up.
- MODEL-116 keys (Open LLM Leaderboard subsets under `math_500` and
  `gpqa_diamond`) were not touched.
