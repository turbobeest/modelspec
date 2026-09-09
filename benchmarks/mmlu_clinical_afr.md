---
id: mmlu_clinical_afr
name: "MMLU clinical African languages (HELM)"
aliases:
  - "mmlu_cm_ck_vir"
  - "Bridging-the-Gap MMLU-Clinical"
page_kind: benchmark
category: knowledge
subcategory: "human-translated MMLU clinical subjects in 11 African languages"
status: unknown
summary: "HELM wrap of human-translated MMLU clinical knowledge, college medicine, and virology items in 11 African languages, scored by exact match."
measures: >
  mmlu_clinical_afr is HELM's multiple-choice wrap of three MMLU health subjects
  translated into 11 African languages. Each item is a four-option question in the
  target language. Default constructor arguments are subject clinical_knowledge and
  lang af (Afrikaans). The run spec also accepts college_medicine and virology, and
  ISO codes af, zu, xh, am, bm, ig, nso, sn, st, tn, ts. It is text-only. It is not
  English MMLU, not MMLU-ProX, and not Global-MMLU.
task_format: >
  Joint multiple-choice. Instruction: "The following are multiple choice questions
  (with answers) about {subject} in {language}." Input noun Question, output noun
  Answer. Adapter default max_train_instances is 5; HELM maps the 5-item dev csv
  to TRAIN_SPLIT, so the usual protocol is 5-shot from dev. Main metric exact_match
  on test.
metric:
  name: exact_match
  direction: higher_is_better
  unit: ""
  max_score: 1
  random_baseline: 0.25
  human_baseline: null
  baseline_note: >
    Four options, so chance is 0.25 if labels are balanced. No subject-language
    human baseline is given in the opened HELM files. The translation paper reports
    LLM English-versus-African gaps, not a clinician ceiling for these items.
    HELM metadata names exact_match on test; the run spec attaches
    get_exact_match_metric_specs().
dataset:
  size: 265
  size_note: >
    Front-matter size is the clinical_knowledge test split HELM scores for one
    language (265), matching English MMLU and Hugging Face
    Institute-Disease-Modeling/mmlu-winogrande-afr. The same hub configs give
    college_medicine test 173 and virology test 166. Every language config has
    dev 5; validation is 29 (clinical knowledge), 22 (college medicine) and 18
    (virology). A full 3-subject x 11-language sweep therefore scores 6,644 test
    items. HELM downloads evaluation_benchmarks_afr_release.zip and reads
    mmlu_cm_ck_vir/{subject}_{split}_{lang}.csv.
  url: https://huggingface.co/datasets/Institute-Disease-Modeling/mmlu-winogrande-afr
  license: "MIT (translation release; MMLU source also MIT)"
  languages:
    - af
    - am
    - bm
    - ig
    - nso
    - sn
    - st
    - tn
    - ts
    - xh
    - zu
  modalities:
    - text
  splits: "per subject-language: dev 5 / val 18-29 / test 166-265; HELM maps dev to train"
  public_test_set: true
publisher:
  org: "Institute for Disease Modeling, Bill & Melinda Gates Foundation, and Ghamut Corporation; HELM wrap by Stanford CRFM"
  authors:
    - "Tuka Alhanai"
    - "Adam Kasumovic"
    - "Mohammad Ghassemi"
    - "Aven Zitzelberger"
    - "Jessica Lundin"
    - "Guillaume Chabot-Couture"
  url: https://github.com/InstituteforDiseaseModeling/Bridging-the-Gap-Low-Resource-African-Languages
paper:
  title: "Bridging the Gap: Enhancing LLM Performance for Low-Resource African Languages with New Benchmarks, Fine-Tuning, and Cultural Adjustments"
  arxiv: "2412.12417"
  url: https://arxiv.org/abs/2412.12417
  year: 2024
leaderboard_url: ""
repo_url: https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/mmlu_clinical_afr_scenario.py
released: "2024-12"
last_updated: "2024-12"
lineage:
  family: mmlu
  predecessor: ""
  successors: []
  variants:
    - mmlu_clinical_knowledge
    - mmlu_college_medicine
    - mmlu_virology
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    No HELM run_entries file for this scenario was found in the opened presentation
    directory. The translation paper reports English-African gaps and fine-tuning
    lifts, not a current HELM leaderboard cell.
contamination:
  risk: high
  note: >
    English MMLU items have been public since 2020. Human translations and csvs
    have been public on GitHub and Hugging Face since December 2024, including
    labelled test splits.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "mmlu_clinical_afr:subject={clinical_knowledge|college_medicine|virology},lang={af|zu|xh|am|bm|ig|nso|sn|st|tn|ts}"
  opencompass: ""
  bigbench: ""
  other: >
    Scenario metadata name is hardcoded mmlu_clinical_afr_clinical_knowledge_{lang}
    even when subject is college_medicine or virology. Hugging Face configs are
    mmlu_{subject}_{lang}. The same paper also releases Winogrande translations;
    those are not this id.
tags:
  - knowledge
  - multiple-choice
  - mmlu
  - african-languages
  - helm
  - medical
sources:
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/mmlu_clinical_afr_scenario.py
    title: "HELM mmlu_clinical_afr_scenario.py"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/mmlu_clinical_afr_run_specs.py
    title: "HELM mmlu_clinical_afr_run_specs.py"
    accessed: "2026-09-08"
  - url: https://github.com/InstituteforDiseaseModeling/Bridging-the-Gap-Low-Resource-African-Languages
    title: "Bridging-the-Gap African-languages repository README"
    accessed: "2026-09-08"
  - url: https://arxiv.org/abs/2412.12417
    title: "Alhanai et al. 2024, arXiv:2412.12417"
    accessed: "2026-09-08"
  - url: https://export.arxiv.org/api/query?id_list=2412.12417
    title: "arXiv API for 2412.12417 (comment: Accepted to AAAI 2025)"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/Institute-Disease-Modeling/mmlu-winogrande-afr
    title: "Hugging Face mmlu-winogrande-afr dataset card"
    accessed: "2026-09-08"
  - url: https://datasets-server.huggingface.co/info?dataset=Institute-Disease-Modeling/mmlu-winogrande-afr
    title: "mmlu-winogrande-afr datasets-server split counts"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/Institute-Disease-Modeling/mmlu-winogrande-afr/raw/main/LICENSE.md
    title: "Translation release MIT licence (Gates Foundation copyright line)"
    accessed: "2026-09-08"
  - url: https://arxiv.org/abs/2009.03300
    title: "MMLU paper (Hendrycks et al.)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-058 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-058"
---

## What it measures

`mmlu_clinical_afr` is HELM's wrap of three MMLU subjects translated into African languages. The model sees a four-option question in Afrikaans, Zulu, Xhosa, Amharic, Bambara, Igbo, Sepedi, Shona, Sesotho, Setswana or Tsonga, and must pick the labelled answer. Default HELM arguments are clinical knowledge in Afrikaans. The same file also loads college medicine and virology. The skill is translated medical knowledge, not English MMLU and not Winogrande.

The translation paper created about one million human-translated words in eight low-resource languages, and reused earlier Afrikaans, Zulu and Xhosa clinical MMLU translations. HELM's language map includes all eleven codes.

## How it is scored

HELM uses joint multiple-choice exact match on the test csv. Chance is 0.25 with four options. Five-shot examples come from the five-row dev split. No clinician baseline for these translations was stated in the opened HELM files. Report subject, language and shot count with the number. HELM `get_metadata` always prints a Clinical Knowledge display name, even when `subject` is college_medicine or virology; trust the run-spec arguments, not that display string.

## Dataset and licence

Hugging Face `Institute-Disease-Modeling/mmlu-winogrande-afr` publishes parallel csvs. For every language, clinical knowledge is 5/29/265 (dev/val/test), college medicine 5/22/173, virology 5/18/166. HELM unzips `evaluation_benchmarks_afr_release.zip` and reads the same layout under `mmlu_cm_ck_vir/`. The translation release licence is MIT. English MMLU is also MIT. Test labels are public.

## Who publishes it

Tuka Alhanai, Adam Kasumovic, Mohammad Ghassemi, Aven Zitzelberger, Jessica Lundin and Guillaume Chabot-Couture released the translations (arXiv:2412.12417, 16 December 2024). The arXiv API comment on that record is "Accepted to AAAI 2025." IDM, the Gates Foundation and Ghamut Corporation share the GitHub repo. Stanford CRFM added the HELM scenario. There is no dedicated HELM leaderboard URL for this wrap in the opened presentation files.

## Lineage

English parents in this repository are [mmlu_clinical_knowledge](mmlu_clinical_knowledge.md), [mmlu_college_medicine](mmlu_college_medicine.md) and [mmlu_virology](mmlu_virology.md), under family [mmlu](mmlu.md). This is not [mmlu_prox](mmlu_prox.md) (translated MMLU-Pro, ten options, 29 languages) and not [global_mmlu](global_mmlu.md). The same African release includes Winogrande csvs; those are a different eval. Preexisting ZA clinical translations live in `winogrande-mmlu-clinical-za`; this HELM id consumes the later combined zip.

## Saturation and contamination

Saturation is unknown. Contamination risk is high: English items are old and public, and labelled translations have been public since December 2024.

## How to run it

```
mmlu_clinical_afr:subject=clinical_knowledge,lang=af
```

Swap `subject` and `lang` as listed above. No `run_entries_*.conf` line for this spec was found in the opened HELM presentation listing. Compare only matched subject-language pairs. Do not quote a metadata name that says clinical knowledge for a virology run.

## Reading the numbers

An exact-match score here is accuracy on one translated MMLU subject in one language, usually 5-shot from five dev items. It does not measure the other 54 MMLU subjects, clinical skills, or translation quality. A drop from the English sibling may be language, script, or medical vocabulary. Pair it with the English subject page and with a native-language clinical set if one exists.
