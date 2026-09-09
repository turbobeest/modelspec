---
id: superglue_ax_g
name: "SuperGLUE AX-g (Winogender Schema Diagnostics)"
aliases:
  - "AX-g"
  - "AXg"
  - "SuperGLUE_AX_g"
  - "AX_g"
  - "Winogender (SuperGLUE)"
page_kind: benchmark
category: safety
subcategory: "Winogender-as-NLI gender-parity diagnostic (SuperGLUE)"
status: unknown
summary: "SuperGLUE Winogender diagnostic: 356 English premise–hypothesis pairs that test whether pronoun gender flips an entailment decision."
measures: >
  AX-g recasts Winogender (Rudinger et al., 2018) as two-way textual entailment using the Diverse
  Natural Language Inference Collection (Poliak et al., 2018). Each item is an English premise with
  a male or female pronoun and a hypothesis that names one possible antecedent (occupation or
  participant). Minimal pairs differ only in pronoun gender. The model must say entailment or
  not_entailment. SuperGLUE reports accuracy and a gender parity score: the share of pairs with the
  same prediction after the gender swap. High parity with chance accuracy is the trivial solution
  of always guessing one class. The set is a diagnostic, not one of the eight SuperGLUE score tasks.
task_format: >
  Binary premise–hypothesis classification. Official metrics are accuracy and GPS, scaled by 100 in
  Table 3. OpenCompass generation asks A/B on premise then hypothesis; perplexity configs compare
  Yes/No continuations. OpenCompass scores accuracy only.
metric:
  name: "accuracy and gender parity score (GPS); OpenCompass reports accuracy only"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 50.0
  human_baseline: 99.7
  baseline_note: >
    SuperGLUE Table 3 (PDF, scaled by 100): most-frequent GPS/Acc 100.0/50.0, CBoW 100.0/50.0,
    BERT 97.8/51.7, BERT++ 99.4/51.4, human 99.3/99.7. Prose human estimates: 99.7% accuracy and
    0.99 GPS. Official zip is balanced 178 entailment / 178 not_entailment. A perfect GPS with ~50
    accuracy is the constant-class cheat.
dataset:
  size: 356
  size_note: >
    SuperGLUE v2 AX-g.zip AX-g.jsonl: 356 lines, counted directly. Hugging Face `aps/super_glue`
    config `axg` test split 356. Labels public in the file. pair_id is unique per row (356 ids).
    Premises in this dump use he/him/his on 178 rows and she/her on 178; no they/them in a simple
    pronoun scan, matching the paper's note that this dump omits gender-neutral they. Original
    Winogender schema counts were not read from the NAACL PDF in this pass.
  url: "https://huggingface.co/datasets/aps/super_glue"
  license: other
  languages:
    - en
  modalities:
    - text
  splits: "test-only 356 labelled pairs in the SuperGLUE v2 zip and in Hugging Face axg"
  public_test_set: true
publisher:
  org: "New York University (SuperGLUE packaging); Winogender from Rudinger et al.; DNC recast from Poliak et al."
  authors:
    - "Alex Wang"
    - "Yada Pruksachatkun"
    - "Nikita Nangia"
    - "Amanpreet Singh"
    - "Julian Michael"
    - "Felix Hill"
    - "Omer Levy"
    - "Samuel R. Bowman"
  url: "https://super.gluebenchmark.com/"
paper:
  title: "SuperGLUE: A Stickier Benchmark for General-Purpose Language Understanding Systems"
  arxiv: "1905.00537"
  url: "https://arxiv.org/abs/1905.00537"
  year: 2019
leaderboard_url: "https://super.gluebenchmark.com/"
repo_url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/SuperGLUE_AX_g"
released: "2019-05"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants:
    - superglue_ax_b
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    2019 BERT++ accuracy is 51.4 with GPS 99.4, i.e. near-constant predictions. Human accuracy 99.7.
    No later official pair of GPS/accuracy figures was read. OpenCompass accuracy alone cannot show
    the cheat.
contamination:
  risk: high
  note: >
    The 356 labelled pairs have been public in the SuperGLUE v2 zip and on Hugging Face since 2019.
    Winogender templates are short and widely copied. A high accuracy on this file can be
    memorisation rather than unbiased coreference.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "SuperGLUE_AX_g (abbr AX_g; gen SuperGLUE_AX_g_gen_68aac7.py and ppl configs on ./data/SuperGLUE/AX-g/AX-g.jsonl)"
  bigbench: ""
  other: "lm-evaluation-harness lm_eval/tasks/super_glue listing opened here has no axg task."
tags:
  - gender-bias
  - winogender
  - nli
  - diagnostic
  - superglue
sources:
  - url: "https://arxiv.org/abs/1905.00537"
    title: "SuperGLUE (Wang et al., arXiv:1905.00537)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/1905.00537"
    title: "SuperGLUE HTML (Winogender diagnostic, human 99.7% / 0.99 GPS)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/pdf/1905.00537.pdf"
    title: "SuperGLUE PDF Table 3 (AXg GPS/Acc: majority 100.0/50.0, BERT 97.8/51.7, BERT++ 99.4/51.4, human 99.3/99.7)"
    accessed: "2026-09-08"
  - url: "https://dl.fbaipublicfiles.com/glue/superglue/data/v2/AX-g.zip"
    title: "Official SuperGLUE v2 AX-g.zip (356 labelled jsonl rows)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/aps/super_glue"
    title: "aps/super_glue dataset card (axg 356 test rows, licence other)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=aps/super_glue&config=axg"
    title: "datasets-server size for axg (356 rows)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/SuperGLUE_AX_g/SuperGLUE_AX_g_gen_68aac7.py"
    title: "OpenCompass SuperGLUE_AX_g generation config (premise/hypothesis, AccEvaluator)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/SuperGLUE_AX_g/SuperGLUE_AX_g_ppl_66caf3.py"
    title: "OpenCompass SuperGLUE_AX_g perplexity config (Yes/No)"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/super_glue"
    title: "lm-eval super_glue task list (no axg)"
    accessed: "2026-09-08"
  - url: "https://super.gluebenchmark.com/"
    title: "SuperGLUE homepage"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/N18-2002/"
    title: "Winogender NAACL 2018 page (Rudinger et al.; PDF not parsed in this pass)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-007 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-007"
---

## What it measures

AX-g is SuperGLUE's gender-bias diagnostic, not a scored SuperGLUE task. The model reads an English premise with a gendered pronoun and a hypothesis that names one candidate antecedent, then chooses entailment or not_entailment. Pairs come in gender-swapped twins. SuperGLUE uses the DNC NLI recast of Winogender, not the original fill-in-the-blank schemas and not GLUE WNLI. The paper states that this dump does not cover they or non-binary pronouns; the v2 jsonl scan in this pass found 178 male-pronoun and 178 female-pronoun premises. It is not [superglue_wsc](superglue_wsc.md) and not [winogrande](winogrande.md).

## How it is scored

Official SuperGLUE reports accuracy and GPS, both ×100 in Table 3. BERT++ is 99.4 GPS and 51.4 accuracy: almost the constant-class cheat. Human estimates are 99.3 GPS / 99.7 accuracy in that table (prose: 99.7% and 0.99). GPS without accuracy is meaningless. OpenCompass `SuperGLUE_AX_g` scores accuracy only, so it cannot show the cheat. AX-g is excluded from the SuperGLUE average.

## Dataset and licence

The SuperGLUE v2 zip `AX-g/AX-g.jsonl` has 356 labelled rows (178/178), matching Hugging Face `axg`. Fields are premise, hypothesis, idx, pair_id, label. Labels are public. Hugging Face licence is "other". Original Winogender item counts were not taken from the NAACL PDF here; this page uses the SuperGLUE dump.

## Who publishes it

Winogender: Rachel Rudinger, Jason Naradowsky, Brian Leonard, Benjamin Van Durme (NAACL 2018). NLI recast: Poliak et al., 2018 (DNC). SuperGLUE packaging: Wang et al., May 2019. Site: super.gluebenchmark.com. The leaderboard did not return scores as static HTML.

## Lineage

Winogender is a coreference bias probe. SuperGLUE keeps the DNC entailment form as AX-g beside the linguistic diagnostic [superglue_ax_b](superglue_ax_b.md). GLUE's WNLI is a different WSC recast and is not this file. This repository has no standalone Winogender page. Other SuperGLUE task pages: [boolq](boolq.md), [superglue_cb](superglue_cb.md), [superglue_copa](superglue_copa.md), [superglue_rte](superglue_rte.md), [superglue_wic](superglue_wic.md), [superglue_wsc](superglue_wsc.md). No SuperGLUE family page.

## Saturation and contamination

2019 systems sat at chance accuracy with near-perfect GPS. That is failure, not saturation. Later official GPS/accuracy pairs were not readable. Contamination risk is high: 356 public labelled templates since 2019. A modern accuracy near 100 on `AX-g.jsonl` needs a GPS next to it, or it is uninterpretable.

## How to run it

Official path: SuperGLUE v2 `AX-g.zip`, score accuracy and GPS on the 356 pairs. OpenCompass directory `SuperGLUE_AX_g`, abbreviation `AX_g`, file `./data/SuperGLUE/AX-g/AX-g.jsonl`, generation (`SuperGLUE_AX_g_gen_68aac7.py`) and perplexity configs. Reader columns are `hypothesis` and `premise`. lm-eval `super_glue` has no `axg` task in the listing opened here. Always report GPS with accuracy.

## Reading the numbers

A useful AX-g result is high accuracy and high GPS together, as in the 99.7 / 0.99 human pair. High GPS alone is the constant guess. High accuracy on the public jsonl can be memorisation of 356 templates. The diagnostic only flags bias that appears as a gender swap on this NLI recast; a good score does not prove a model is unbiased. Read it beside [superglue_wsc](superglue_wsc.md) and [superglue_ax_b](superglue_ax_b.md), not as a SuperGLUE headline.
