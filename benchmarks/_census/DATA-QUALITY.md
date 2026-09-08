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
