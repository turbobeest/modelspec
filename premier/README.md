# Slice-1 premier set

Status: pending Jamie's approval. This list is a proposal. It is not the premier set until Jamie says so.

The rule is the one in the decision-engine design, section 5. A model is in the set if any of these holds:

1. It is in the top 10 of its class on a slice-1 board.
2. Its lab had a model in clause 1, and this model was released on or after 2026-06-26, ninety days before the read date.
3. At least three major providers offer it, counted only from providers the card already records.
4. A reviewer added it. The MODEL-136 brief requires one decision model, so the set includes `typesafe/jev-1-13`.

Retired models leave the set. The only `sunset` cards the rule reaches are the two GPT-5.5 pre-release checkpoints Epoch AI evaluated, `openai/gpt-5-5-pre-release` and `openai/gpt-5-5-pro-pre-release`. They were never offered, and `sunset` is the closest existing status, so they are the whole of `archived` in the YAML. Deprecated models would stay, with a retirement date when the card records one. None of the selected cards are deprecated.

## Method

`scripts/premier_slice1.py` reads the snapshots in `premier/inputs/` and writes `premier/slice-1.yaml`. It does not fetch the network. Effort settings of one model, such as high and max, collapse to one row before the rank. A tie with the 10th score stays in the top 10.

Names match cards by a folded key, then by `premier/inputs/aliases.json` where the word order differs. An unmatched top-10 name is listed under `missing_cards` and is not given a guessed card.

The engine class comes from `api.classes.class_for_model_type`. Slice-1 group names are the balance buckets in the brief. Domain ids are the brief's slice-1 names. MODEL-133's registry uses the section 8 launch names, and those ids get reconciled when that registry merges.

| Slice-1 domain | Section 8 name to reconcile |
|---|---|
| software-engineering | software engineering |
| reasoning-and-maths | maths, and engineering and STEM where GPQA and Humanity's Last Exam also cover science |
| chat-or-preference | no section 8 name yet |
| retrieval-and-embedding | no section 8 name yet |
| vision | vision and documents |

## The cut

Clause 1 matches 49 cards. The cap keeps 29.

Within each group the script keeps the models with the best rank on a fresh board, then the newer release. The official SWE-bench Verified bash table stops at 2026-02-26, so it does not lead that sort. A clause-1 model released on or after 2026-09-01 stays even when the group is already full. That is why Grok 4.7 is in the frontier group past the quota of 12.

The four strongest models on the Arena vision board are the vision balance. They are general generators. Their engine class stays `text-generator`, and their clauses still list every board they lead. The vision board's top 10 does not contain a `vlm` card.

Quotas: frontier generation 12, open-weights generation 6, embedding 4, rerank 2, vision 4, decision 1. Rerank stops at one card because the embedding leaderboard publishes a reranking score for only a few cross-encoders, and only Jina Reranker v3 has a card.

Clause 2 is recorded on models that are already in through clause 1 and were released inside the window. It did not add a model the quota had no room for. Clause 3 added nobody. Frontier cards do not record three of the lab API, Bedrock, Vertex, Azure, or the main inference providers.

## Inputs, read 2026-09-24

| File | Board | URL |
|---|---|---|
| `swebench-verified.json` | SWE-bench Verified, bash-only mini-SWE-agent rows | https://www.swebench.com/ |
| `swebench-pro.json` | SWE-bench Pro public table | https://labs.scale.com/leaderboard/swe_bench_pro |
| `terminal-bench-4.0.json` | Terminal-Bench 4.0 | https://www.tbench.ai/ |
| `arena-text.json`, `arena-webdev.json`, `arena-vision.json` | Arena overall, CC BY 4.0, publish dates 2026-09-13, 2026-09-23, 2026-09-13 | https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset |
| `mteb-eng-v2.json`, `mteb-multilingual-v2.json` | MTEB English v2 and Multilingual v2 | https://mteb-leaderboard-backend.hf.space/ |
| `matharena-expected.json` | MathArena expected performance | https://matharena.ai/ |
| `epoch-frontiermath_tiers_1_3_v2.csv` | Epoch FrontierMath Tiers 1-3 v2, CC BY 4.0 | https://epoch.ai/benchmarks/use-this-data |
| `epoch-gpqa_diamond.csv` | Epoch GPQA Diamond, CC BY 4.0 | same |
| `epoch-swe_bench_verified.csv` | Epoch's own SWE-bench Verified runs, CC BY 4.0 | same |
| `scale-hle.json` | Scale SEAL, Humanity's Last Exam | https://labs.scale.com/leaderboard/humanitys_last_exam |

Epoch's composite capability index is not a board. Superseded FrontierMath files are not boards. Epoch files whose names end in `_external` keep their original licences and are not used.

## Near misses and missing cards

`near_misses` in the YAML names every clause-1 card the quota cut, and the three newest in-window releases per qualifying lab that did not get a seat. Qwen3.8 Max is the sharpest cut. It is 5th on Arena vision and 6th on Arena webdev, and the frontier seats were already filled by higher ranks.

`missing_cards` names top-10 rows with no card. The ones that change the top of a board are Muse Spark 1.1, first on SWE-bench Pro, and Muse Spark 1.3, inside the Arena top 10. The English embedding top 10 is mostly models with no card, including the first place. The reranker top is Querit, which has no card.
