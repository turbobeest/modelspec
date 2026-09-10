# MODEL-32 ranking evidence (from cached pages)

Verified against `benchmarks/_census/ranking_evidence/raw/` on 2026-09-09.
No live Firecrawl. Attachments went through `scripts/attach_evidence.py` and
`LEDGER_TO_CARD` only.

## Ranked benchmark set

78 keys: every `benchmark_weights` entry on `USE_CASE_PROFILES` after
`_apply_verified_additions()` (the live set ranking actually uses).

Classic profile keys plus the seven verified additions: `aa_briefcase`,
`aa_lcr`, `aider_polyglot`, `aime_2025`, `aime_2026`, `alpaca_eval`,
`arc_challenge`, `arena_elo_coding`, `arena_elo_hard_prompts`, `arena_elo_math`,
`arena_elo_overall`, `arena_elo_style_control`, `arena_elo_vision`,
`automationbench_aa`, `bbh`, `bbq`, `beir`, `chartqa`, `clip_score`, `critpt`,
`docvqa`, `fid`, `finbench`, `finqa`, `flores`, `gdp_pdf_aa`, `gdpval_aa`,
`gpqa_diamond`, `gsm8k`, `hellaswag`, `helm_safety`, `humaneval`, `ifeval`,
`legalbench`, `live_code_bench`, `math_500`, `mathvista`, `medmcqa`, `medqa`,
`mgsm`, `miracl`, `mmlu_astronomy`, `mmlu_biology`, `mmlu_business_ethics`,
`mmlu_chemistry`, `mmlu_clinical_knowledge`, `mmlu_computer_science`,
`mmlu_jurisprudence`, `mmlu_physics`, `mmlu_pro`, `mmlu_professional_accounting`,
`mmlu_professional_law`, `mmmu`, `mos_tts`, `mt_bench`, `mteb_classification`,
`mteb_clustering`, `mteb_overall`, `mteb_retrieval`, `multipl_e`,
`multipl_e_cpp`, `multipl_e_go`, `multipl_e_java`, `multipl_e_javascript`,
`multipl_e_python`, `multipl_e_rust`, `multipl_e_typescript`, `pubmedqa`,
`scicode`, `swe_bench_agent`, `swe_bench_verified`, `tau_bench`,
`terminal_bench`, `toxigen`, `truthfulqa`, `web_arena`, `wer_librispeech`,
`wildbench`.

`terminal_bench` is Terminal-Bench 1.0 (superseded). `live_code_bench` is
unversioned LiveCodeBench. Those identities were not stretched to later
variants.

## Overlap

The prior run's "7 AA pairs on GPT-6 Astra, including gpqa_diamond / mmlu_pro /
swe_bench_verified" is **stale**. Those three classic keys were not verified
before this attach. The live 7 were the census additions on Astra only.

| | pairs | models | ranked keys covered |
| --- | ---: | ---: | --- |
| Before | **7** | 1 (`openai/gpt-6-astra`) | `aa_briefcase`, `aa_lcr`, `automationbench_aa`, `critpt`, `gdp_pdf_aa`, `gdpval_aa`, `scicode` |
| After | **44** | 14 | the 7 above plus `aime_2025`, `aime_2026`, `chartqa`, `docvqa`, `gpqa_diamond`, `ifeval`, `math_500`, `mathvista`, `mgsm`, `mmlu_pro`, `mmmu`, `swe_bench_verified` |

+37 new verified (model, ranked-benchmark) pairs. Classic keys still missing
on most cards include `humaneval`, `terminal_bench` (v1.0), `live_code_bench`
(unversioned), `swe_bench_agent`, `tau_bench` (original τ-bench), and the
Arena Elo family.

## Attached table

| model | benchmark | value | source URL | evidence_date | date_type |
| --- | --- | ---: | --- | --- | --- |
| openai/gpt-6-astra | gpqa_diamond | 96.0 | https://openai.com/index/gpt-6-astra/ | 2026-09-03 | published |
| openai/gpt-5-6-sol | gpqa_diamond | 94.6 | https://openai.com/index/gpt-5-6/ | 2026-07-09 | published |
| openai/gpt-5-6-terra | gpqa_diamond | 92.9 | https://openai.com/index/gpt-5-6/ | 2026-07-09 | published |
| openai/gpt-5-6-luna | gpqa_diamond | 92.3 | https://openai.com/index/gpt-5-6/ | 2026-07-09 | published |
| anthropic/claude-opus-4-8 | swe_bench_verified | 88.6 | https://www.anthropic.com/claude-opus-4-8-system-card | 2026-05-28 | published |
| anthropic/claude-opus-4-8 | gpqa_diamond | 93.6 | https://www.anthropic.com/claude-opus-4-8-system-card | 2026-05-28 | published |
| anthropic/claude-opus-5 | swe_bench_verified | 96.0 | https://www.anthropic.com/claude-opus-5-system-card | 2026-07-24 | published |
| anthropic/claude-sonnet-5 | swe_bench_verified | 85.2 | https://www.anthropic.com/claude-sonnet-5-system-card | 2026-06-30 | published |
| google/gemma-4-31b-it | mmlu_pro | 85.2 | https://huggingface.co/google/gemma-4-31B-it | 2026-07-02 | published |
| google/gemma-4-31b-it | aime_2026 | 89.2 | https://huggingface.co/google/gemma-4-31B-it | 2026-07-02 | published |
| google/gemma-4-31b-it | gpqa_diamond | 84.3 | https://huggingface.co/google/gemma-4-31B-it | 2026-07-02 | published |
| zhipu/glm-5-1 | aime_2026 | 95.3 | https://z.ai/blog/glm-5.1 | 2026-04-07 | published |
| zhipu/glm-5-1 | gpqa_diamond | 86.2 | https://z.ai/blog/glm-5.1 | 2026-04-07 | published |
| meta/llama-4-scout-17b-16e-instruct | mmlu_pro | 74.3 | https://huggingface.co/meta-llama/Llama-4-Scout-17B-16E-Instruct | 2025-04-05 | published |
| meta/llama-4-scout-17b-16e-instruct | gpqa_diamond | 57.2 | same | 2025-04-05 | published |
| meta/llama-4-scout-17b-16e-instruct | chartqa | 88.8 | same | 2025-04-05 | published |
| meta/llama-4-scout-17b-16e-instruct | docvqa | 94.4 | same | 2025-04-05 | published |
| meta/llama-4-scout-17b-16e-instruct | mmmu | 69.4 | same | 2025-04-05 | published |
| meta/llama-4-scout-17b-16e-instruct | mathvista | 70.7 | same | 2025-04-05 | published |
| meta/llama-4-scout-17b-16e-instruct | mgsm | 90.6 | same | 2025-04-05 | published |
| meta/llama-4-maverick-17b-128e-instruct | mmlu_pro | 80.5 | https://huggingface.co/meta-llama/Llama-4-Maverick-17B-128E-Instruct | 2025-04-05 | published |
| meta/llama-4-maverick-17b-128e-instruct | gpqa_diamond | 69.8 | same | 2025-04-05 | published |
| meta/llama-4-maverick-17b-128e-instruct | chartqa | 90.0 | same | 2025-04-05 | published |
| meta/llama-4-maverick-17b-128e-instruct | docvqa | 94.4 | same | 2025-04-05 | published |
| meta/llama-4-maverick-17b-128e-instruct | mmmu | 73.4 | same | 2025-04-05 | published |
| meta/llama-4-maverick-17b-128e-instruct | mathvista | 73.7 | same | 2025-04-05 | published |
| meta/llama-4-maverick-17b-128e-instruct | mgsm | 92.3 | same | 2025-04-05 | published |
| qwen/qwen3-32b | gpqa_diamond | 68.4 | https://arxiv.org/abs/2505.09388 | 2025-05-14 | published |
| qwen/qwen3-32b | ifeval | 85.0 | same | 2025-05-14 | published |
| qwen/qwen3-32b | math_500 | 97.2 | same | 2025-05-14 | published |
| qwen/qwen3-32b | aime_2025 | 72.9 | same | 2025-05-14 | published |
| deepseek/deepseek-v4-pro | mmlu_pro | 87.5 | https://arxiv.org/abs/2606.19348 | 2026-04-26 | published |
| deepseek/deepseek-v4-pro | gpqa_diamond | 90.1 | same | 2026-04-26 | published |
| deepseek/deepseek-v4-pro | swe_bench_verified | 80.6 | same | 2026-04-26 | published |
| deepseek/deepseek-v4-flash | mmlu_pro | 86.2 | same | 2026-04-26 | published |
| deepseek/deepseek-v4-flash | gpqa_diamond | 88.1 | same | 2026-04-26 | published |
| deepseek/deepseek-v4-flash | swe_bench_verified | 79.0 | same | 2026-04-26 | published |

Astra's seven pre-existing AA rows are unchanged. `evidence_date` 2026-09-03 for
Astra GPQA is OpenAI's own dating of https://openai.com/index/gpt-6-astra/
("Research Sep 3, 2026") on the GPT-5.6 article in this cache; the Astra
markdown itself has no dateline. Gemma 4's day is the technical-report date
printed on the HF card (`2607.02770`, 2026-07-02), confirmed from arXiv
`citation_date`.

Qwen3-32B scores are **thinking mode** (the paper's default for that table).
DeepSeek SWE-Verified was run in DeepSeek's internal bash+file-edit harness;
that is recorded on the evidence `configuration` field, not treated as a
different benchmark key.

## Refusals

### Variant unpinned / wrong variant (not forced into a ranked key)

- Terminal-Bench 2.0 / 2.1 / 4.0 / Science 0.1 (OpenAI, Anthropic, GLM, Gemini,
  Qwen, DeepSeek, Grok). Ranked key is `terminal_bench` = Terminal-Bench 1.0.
- SWE-bench Pro / Multilingual / Multimodal (OpenAI, Anthropic, GLM, Qwen).
  Ranked key is `swe_bench_verified`.
- LiveCodeBench v5 (Qwen3 tech report), v6 (Gemma 4, DeepSeek), Pro (Gemini 3.1),
  and Llama 4's 2024-10-01–2025-02-01 window. Ranked key is unversioned
  `live_code_bench`.
- MMLU vs MMLU-Pro vs MMLU-Redux vs MMMLU. Only pinned MMLU-Pro was taken.
- GPQA vs GPQA Diamond. Only Diamond was taken. SuperGPQA refused.
- AIME 2024 / AIME'24. Ranked keys are `aime_2025` and `aime_2026`.
- MMMU-Pro (OpenAI, Gemini, Gemma, Llama). Ranked key is `mmmu`.
- τ2-bench / τ³-Bench. Ranked key is original `tau_bench` (superseded).
- ChartQAPro vs `chartqa`.
- AutomationBench (Zapier pass rate) vs ranked `automationbench_aa` (AA protocol).
- gdp.pdf / GDP.PDF vs ranked `gdp_pdf_aa`.
- SciCode on Gemini 3.1 Pro: 59%, protocol unpinned (AA subproblem pass@1 vs
  publisher main-problem resolve rate).

### Date unpinned

- Gemini 3.1 Pro product page: GPQA Diamond 94.3% no tools, SWE-bench Verified
  80.6% single attempt. No publication day on the cached page or the
  evals-methodology page.
- Gemini 3.8 Flash model card: "Results as of September, 2026" — month only.
- Qwen3.8 HF card: GPQA Diamond 92.6 (table and eval widget). Only "Updated 27
  days ago".
- Fable 5.1 launch post: no dateline in the cache (system card is 2026-09-01
  and was used for capability checks; it still has no ranked classic scores).

### Competitor table

Every provider comparison column was dropped. Examples: OpenAI tables of Claude
and Gemini; Anthropic tables of GPT and Gemini; GLM / Qwen / DeepSeek / Grok
tables of other labs; Gemma 4 columns for Gemma 3 27B.

### Unit mismatch (would poison ranking ranges)

- GDPval-AA / GDPVal-AA v2 reported as raw Elo (OpenAI 1747.8, Grok 1753,
  Anthropic 1890 / 1861 / 1618, Gemini 1317 / 1545). Ranked `gdpval_aa` is
  AA's normalized Elo percent on (0, 100). No conversion applied.
- AA-Briefcase reported as Elo (Grok 1577, Opus 5 1720). Ranked `aa_briefcase`
  on Astra is already verified as normalized percent from the AA article.

### No score present (charts, 404, empty)

See "cached pages that yielded nothing" below.

## Candidate keys seen in the wild (catalogue may already have the page)

These are **not** ranked today. Do not fold them into a nearby ranked id.

| seen | nearest existing catalogue id | ranked? |
| --- | --- | --- |
| Terminal-Bench 2.0 | `terminal_bench_2_0` | no |
| Terminal-Bench 2.1 | `terminal_bench_v2_1` | no |
| Terminal-Bench 4.0 | `terminal_bench_v4_0` | no |
| Terminal-Bench Science 0.1 | `terminal_bench_science` | no |
| SWE-bench Pro | `swe_bench_pro` | no |
| LiveCodeBench v5 | none | no |
| LiveCodeBench v6 | none | no |
| LiveCodeBench Pro | `livecodebench_pro` | no |
| MMMU-Pro | `mmmu_pro` | no |
| OSWorld 2.0 / OSWorld-Verified | `osworld` | no |
| τ2-bench / τ³-Bench | successors of `tau_bench` | no |
| AutomationBench (Zapier) | `automationbench` | no |
| FrontierCode, CursorBench, DeepSWE, ARC-AGI-3, HLE, BrowseComp | various | no |

## Cached pages that yielded nothing, and why

27 files. Several are pairs (launch post + system card, blog + HF).

| file | why |
| --- | --- |
| `anthropic-fable-5-1.md` | No dateline; scores in images; Terminal-Bench 4.0 / Science 0.1 are not ranked keys |
| `anthropic-fable-5-1-system-card.md` | Dated 2026-09-01, but no SWE-bench Verified or GPQA Diamond; reports Pro / TB 4.0 |
| `anthropic-opus-4-8.md` | Dated 2026-05-28; capability numbers are an image. Extracted from the system card instead |
| `anthropic-opus-5.md` | Dated 2026-07-24; numbers in images. Extracted from the system card instead |
| `anthropic-sonnet-5.md` | Dated 2026-06-30; numbers in an image. Extracted from the system card instead |
| `deepseek-v4-pdf.md` | Hugging Face 404 |
| `deepseek-v4-report.md` | Empty "Entry not found" HTML |
| `gemini-3-1-pro-page.md` | Ranked scores present (GPQA Diamond, SWE-bench Verified) but **no publication day** |
| `gemini-3-8-flash-card.md` | Month-only date ("September, 2026"); remaining numbers are unranked variants or Elo |
| `google-gemini-3-8-flash-blog.md` | Dated 2026-09-02; evals are images, no extractable ranked numbers |
| `meta-llama-4-blog.md` | Dated 2025-04-05; no Scout/Maverick numeric table for ranked keys (Behemoth mention only). Model card used instead |
| `openai-gpt-6-astra.md` | Same launch article as `-full.md`; scores taken once |
| `qwen-3-8-hf.md` | Qwen3.8-Max / 2.4T-A95B GPQA Diamond 92.6 present; date unpinned |
| `qwen3-32b-hf.md` | No ranked scores (points at the blog; LEXam only) |
| `qwen3-blog.md` | Dated 2025-04-29; scores are images |
| `xai-grok-4-6.md` | Dated 2026-08-12; AA Intelligence / GDPVal-AA Elo / Terminal-Bench v3.0 / AA-Briefcase Elo — none are attachable ranked cells |
| `glm-5-1-hf.md` | Duplicate of the dated blog table; blog used as the source |

Pages that **did** yield attached rows: `openai-gpt-6-astra-full.md` /
`openai-gpt-5-6.md`, the three Anthropic system cards, `gemma-4-31b-hf.md`,
`glm-5-1-blog.md`, `meta-llama-4-model-card.md`, `qwen3-tech-report.md`,
`deepseek-v4-arxiv.md`.

## Attach path

Ledger: `benchmarks/_census/ranking_evidence/accepted.json` (37 results).
`scripts/attach_evidence.py` now loads that file alongside the eligibility
census report. `LEDGER_TO_CARD` was extended explicitly; GLM-5.3 (max) remains
unmapped. 14 cards updated. `verified_at` is 2026-09-09.

## Pytest

`.venv/bin/python -m pytest -q tests/` → **1 failed, 226 passed** in 170.53s.

The failure is
`tests/test_incomplete_evidence_ranking.py::test_real_astra_is_visible_unranked_instead_of_ranked_low[reasoning-critpt-32.0]`:
Astra reasoning coverage is now 0.36 rather than 0.20 because `gpqa_diamond` is
verified. Astra remains unranked (coverage still under 0.50). That test file is
outside this ticket's allowed edit set. The coding parametrization of the same
test still passes. `tests/test_attach_evidence.py` passed.
