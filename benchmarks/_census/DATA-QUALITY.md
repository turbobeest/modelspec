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
not MMLU-Pro categories, so the pull may mix both. Action: trace the intlpull source for these 40 cards, re-key
the MMLU-Pro categories to `mmlu_pro_<category>`, and re-run the wiki queue. Until then the pages for these ids say
so and carry `status: unknown`.
