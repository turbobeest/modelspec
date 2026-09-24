"""ModelSpec Ranking Engine — 4-stage pipeline.

Queries FalkorDB directly, scores models against use-case profiles,
and returns ranked results with human-readable explanations.
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("modelspec.ranking")


# ═══════════════════════════════════════════════════════════════
# Benchmark normalization ranges
# ═══════════════════════════════════════════════════════════════
# Maps benchmark_id -> (min_plausible, max_plausible) for 0-100 normalization.
# Scores below min map to 0, above max map to 100.
#
# MODEL-123 (Jamie, 2026-09-23, audit §8.2): a percentage benchmark's ceiling is
# its natural 100. A ceiling below 100 clipped the frontier flat — 94 cards sat
# above GPQA Diamond's old 80 and tied there. `tests/test_profile_refresh.py`
# reads each benchmark page's unit and fails on a percentage ceiling below 100.
#
# Arena keys that a profile weights are not here at all: they are normalised
# within one pinned snapshot (`ARENA_SNAPSHOT`, below), never against a fixed
# Elo bound. The raw `arena_elo_*` entries that remain are unweighted legacy
# keys from the April 2026 scrape.

BENCHMARK_RANGES: dict[str, tuple[float, float]] = {
    # Knowledge & Reasoning (percentage-based, 0-100)
    "mmlu_pro":         (20.0, 100.0),
    "gpqa_diamond":     (20.0, 100.0),
    "hle":              (0.0, 100.0),
    "arc_challenge":    (40.0, 100.0),
    "hellaswag":        (40.0, 100.0),
    "truthfulqa":       (20.0, 100.0),
    "bbh":              (20.0, 100.0),
    "ifeval":           (20.0, 100.0),
    "musr":             (10.0, 100.0),
    "winogrande":       (50.0, 100.0),
    # Math
    "math_500":         (10.0, 100.0),
    "aime_2025":        (0.0, 100.0),
    "aime_2026":        (0.0, 100.0),
    "gsm8k":            (20.0, 100.0),
    "mgsm":             (10.0, 100.0),
    # Coding
    "humaneval":        (10.0, 100.0),
    "humaneval_plus":   (10.0, 100.0),
    "swe_bench_verified": (0.0, 100.0),
    "live_code_bench":  (0.0, 100.0),
    "aider_polyglot":   (0.0, 100.0),
    "terminal_bench":   (0.0, 100.0),
    "mbpp":             (20.0, 100.0),
    "multipl_e":        (10.0, 100.0),
    # Multimodal
    "mmmu":             (20.0, 100.0),
    "mathvista":        (20.0, 100.0),
    "docvqa":           (40.0, 100.0),
    "chartqa":          (40.0, 100.0),
    # Safety
    "helm_safety":      (30.0, 100.0),
    "bbq":              (30.0, 100.0),
    "toxigen":          (30.0, 100.0),
    # Human preference, raw (not style-controlled) Arena view. Unweighted since
    # MODEL-123; kept so an old snapshot's values still normalise the same way.
    "arena_elo_overall":       (1000.0, 1400.0),
    "arena_elo_coding":        (1000.0, 1400.0),
    "arena_elo_math":          (1000.0, 1400.0),
    "arena_elo_vision":        (1000.0, 1400.0),
    "arena_elo_hard_prompts":  (1000.0, 1400.0),
    "mt_bench":         (5.0, 10.0),
    "alpaca_eval":      (0.0, 100.0),
    "wildbench":        (-100.0, 100.0),
    # Embedding (percentage or ratio-based)
    "mteb_overall":       (30.0, 100.0),
    "mteb_retrieval":     (20.0, 100.0),
    "mteb_classification": (40.0, 100.0),
    "mteb_clustering":    (20.0, 100.0),
    "mteb_reranking":     (20.0, 100.0),
    "mteb_sts":           (40.0, 100.0),
    "mteb_pair_classification": (50.0, 100.0),
    "mteb_summarization": (20.0, 100.0),
    "beir":               (20.0, 70.0),
    "miracl":             (10.0, 100.0),
    # Agentic
    "swe_bench_agent":  (0.0, 100.0),
    "swe_bench_pro":    (0.0, 100.0),
    "swe_bench_multilingual": (0.0, 100.0),
    "swe_bench_multimodal":   (0.0, 100.0),
    "tau_bench":        (0.0, 100.0),
    "web_arena":        (0.0, 50.0),
    "osworld":          (0.0, 100.0),
    # Agentic search. (`hle` is defined once, above; MODEL-108 §5 found it
    # twice, and the later entry silently won.)
    "browsecomp":       (0.0, 100.0),
    "hle_tools":        (0.0, 100.0),
    # Multimodal (advanced)
    "charxiv_reasoning":       (20.0, 100.0),
    "charxiv_reasoning_tools": (20.0, 95.0),
    "lab_bench_figqa":         (20.0, 100.0),
    "lab_bench_figqa_tools":   (20.0, 100.0),
    "screenspot_pro":          (10.0, 100.0),
    "screenspot_pro_tools":    (10.0, 100.0),
    # Long context
    "graphwalks_bfs_256k_1m":     (0.0, 100.0),
    "graphwalks_parents_256k_1m": (0.0, 100.0),
    # Math (competition)
    "usamo_2026":       (0.0, 100.0),
    "ipho_2025_theory": (0.0, 100.0),
    # Agentic research
    "deepsearchqa":             (0.0, 80.0),
    "frontierscience_research": (0.0, 100.0),
    # Health / Medical (advanced)
    "healthbench_hard":         (0.0, 100.0),
    "medxpertqa_multimodal":    (20.0, 100.0),
    # Visual reasoning
    "zerobench":        (0.0, 100.0),
    "ai2d":             (40.0, 100.0),
    "ocrbench":         (0.0, 100.0),
    "realworldqa":      (30.0, 100.0),
    # AGI benchmarks
    "arc_agi_2":        (0.0, 100.0),
    # Multilingual knowledge
    "mmmlu":            (40.0, 100.0),
    # Per-language MultiPL-E (percentage-based, 0-100)
    "multipl_e_python":     (10.0, 100.0),
    "multipl_e_rust":       (10.0, 100.0),
    "multipl_e_cpp":        (10.0, 100.0),
    "multipl_e_java":       (10.0, 100.0),
    "multipl_e_typescript": (10.0, 100.0),
    "multipl_e_go":         (10.0, 100.0),
    "multipl_e_javascript": (10.0, 100.0),
    "multipl_e_csharp":     (10.0, 100.0),
    "multipl_e_php":        (10.0, 100.0),
    "multipl_e_ruby":       (10.0, 100.0),
    "multipl_e_swift":      (10.0, 100.0),
    "multipl_e_kotlin":     (10.0, 100.0),
    "multipl_e_scala":      (10.0, 100.0),
    "multipl_e_r":          (10.0, 100.0),
    "multipl_e_julia":      (10.0, 100.0),
    "multipl_e_perl":       (10.0, 100.0),
    "multipl_e_lua":        (10.0, 100.0),
    # Terminal-Bench 2.0 (percentage-based, 0-100)
    "terminal_bench_2":     (0.0, 100.0),
    # MMLU subject scores (percentage-based, 0-100)
    # All 57 MMLU (hendrycksTest) subjects from the evaluation harness
    "mmlu_abstract_algebra":                    (20.0, 100.0),
    "mmlu_anatomy":                             (20.0, 100.0),
    "mmlu_astronomy":                           (20.0, 100.0),
    "mmlu_business_ethics":                     (20.0, 100.0),
    "mmlu_clinical_knowledge":                  (20.0, 100.0),
    "mmlu_college_biology":                     (20.0, 100.0),
    "mmlu_college_chemistry":                   (20.0, 100.0),
    "mmlu_college_computer_science":            (20.0, 100.0),
    "mmlu_college_mathematics":                 (20.0, 100.0),
    "mmlu_college_medicine":                    (20.0, 100.0),
    "mmlu_college_physics":                     (20.0, 100.0),
    "mmlu_computer_security":                   (20.0, 100.0),
    "mmlu_conceptual_physics":                  (20.0, 100.0),
    "mmlu_econometrics":                        (20.0, 100.0),
    "mmlu_electrical_engineering":              (20.0, 100.0),
    "mmlu_elementary_mathematics":              (20.0, 100.0),
    "mmlu_formal_logic":                        (20.0, 100.0),
    "mmlu_global_facts":                        (20.0, 100.0),
    "mmlu_high_school_biology":                 (20.0, 100.0),
    "mmlu_high_school_chemistry":               (20.0, 100.0),
    "mmlu_high_school_computer_science":        (20.0, 100.0),
    "mmlu_high_school_european_history":        (20.0, 100.0),
    "mmlu_high_school_geography":               (20.0, 100.0),
    "mmlu_high_school_government_and_politics": (20.0, 100.0),
    "mmlu_high_school_macroeconomics":          (20.0, 100.0),
    "mmlu_high_school_mathematics":             (20.0, 100.0),
    "mmlu_high_school_microeconomics":          (20.0, 100.0),
    "mmlu_high_school_physics":                 (20.0, 100.0),
    "mmlu_high_school_psychology":              (20.0, 100.0),
    "mmlu_high_school_statistics":              (20.0, 100.0),
    "mmlu_high_school_us_history":              (20.0, 100.0),
    "mmlu_high_school_world_history":           (20.0, 100.0),
    "mmlu_human_aging":                         (20.0, 100.0),
    "mmlu_human_sexuality":                     (20.0, 100.0),
    "mmlu_international_law":                   (20.0, 100.0),
    "mmlu_jurisprudence":                       (20.0, 100.0),
    "mmlu_logical_fallacies":                   (20.0, 100.0),
    "mmlu_machine_learning":                    (20.0, 100.0),
    "mmlu_management":                          (20.0, 100.0),
    "mmlu_marketing":                           (20.0, 100.0),
    "mmlu_medical_genetics":                    (20.0, 100.0),
    "mmlu_miscellaneous":                       (20.0, 100.0),
    "mmlu_moral_disputes":                      (20.0, 100.0),
    "mmlu_moral_scenarios":                     (20.0, 100.0),
    "mmlu_nutrition":                           (20.0, 100.0),
    "mmlu_philosophy":                          (20.0, 100.0),
    "mmlu_prehistory":                          (20.0, 100.0),
    "mmlu_professional_accounting":             (20.0, 100.0),
    "mmlu_professional_law":                    (20.0, 100.0),
    "mmlu_professional_medicine":               (20.0, 100.0),
    "mmlu_professional_psychology":             (20.0, 100.0),
    "mmlu_public_relations":                    (20.0, 100.0),
    "mmlu_security_studies":                    (20.0, 100.0),
    "mmlu_sociology":                           (20.0, 100.0),
    "mmlu_us_foreign_policy":                   (20.0, 100.0),
    "mmlu_virology":                            (20.0, 100.0),
    "mmlu_world_religions":                     (20.0, 100.0),
    # Legacy aliases (mapped to new names for backward compatibility)
    "mmlu_chemistry":               (20.0, 100.0),
    "mmlu_physics":                 (20.0, 100.0),
    "mmlu_biology":                 (20.0, 100.0),
    "mmlu_computer_science":        (20.0, 100.0),
    # Domain-specific extras
    "pubmedqa":     (30.0, 100.0),
    "medmcqa":      (20.0, 100.0),
    "bioasq":       (20.0, 80.0),
    "finqa":        (20.0, 90.0),
    "convfinqa":    (20.0, 80.0),
    "fpb":          (20.0, 90.0),
    # Translation
    "flores":       (10.0, 100.0),
    "flores_en_zh": (10.0, 100.0),
    "flores_en_de": (10.0, 100.0),
    "flores_en_fr": (10.0, 50.0),
    "flores_en_es": (10.0, 100.0),
    "flores_en_ja": (10.0, 100.0),
    "flores_en_ko": (10.0, 50.0),
}


# ═══════════════════════════════════════════════════════════════
# Use case profiles
# ═══════════════════════════════════════════════════════════════


#: Benchmarks whose score is better when lower. `_normalize_benchmark` assumed
#: higher-is-better for everything, which silently inverted these: a worse
#: transcriber outranked a better one. See MODEL-30.
BENCHMARK_DIRECTIONS: dict[str, str] = {
    "wer_librispeech": "lower_is_better",
    "fid": "lower_is_better",
}

#: Ranges added in MODEL-30 for benchmarks that profiles weight but that had no
#: entry above, so normalisation fell back to "assume 0-100, higher is better".
#:
#: medqa, finbench and legalbench are confirmed from their benchgraph pages —
#: all three declare higher_is_better with unit % and max_score 100, so the old
#: fallback happened to be right and this simply makes it explicit.
#:
#: wer_librispeech, fid and mos_tts have no benchgraph page. Their *direction*
#: and scale are not in doubt, and fixing those removes the inversion. The exact
#: bounds are judgement and are marked for confirmation alongside MODEL-30.
BENCHMARK_RANGES.update({
    "medqa": (0.0, 100.0),            # confirmed from page
    "finbench": (0.0, 100.0),         # confirmed from page
    "legalbench": (0.0, 100.0),       # confirmed from page
    "wer_librispeech": (1.5, 25.0),   # word error rate %, bounds unconfirmed
    "fid": (1.0, 100.0),              # Frechet distance, bounds unconfirmed
    "mos_tts": (1.0, 5.0),            # mean opinion score, 1-5 by definition
})

#: Ranges for the benchmarks MODEL-123 brought into the profiles. Each page
#: states the unit; every percentage takes its natural (0, 100). Arena keys are
#: absent on purpose: they are normalised within `ARENA_SNAPSHOT`, below.
BENCHMARK_RANGES.update({
    "terminal_bench_v4_0": (0.0, 100.0),
    "frontiermath_tiers_1_3_v2": (0.0, 100.0),
    "ifbench": (0.0, 100.0),
    "simpleqa_verified": (0.0, 100.0),
    "mmmu_pro": (0.0, 100.0),
    "osworld_2": (0.0, 100.0),
    "tau3_banking": (0.0, 100.0),
    "healthbench_professional": (0.0, 100.0),
    "deepswe_v1_1": (0.0, 100.0),
    "cursorbench_4": (0.0, 100.0),
    "frontiercode_v1_1": (0.0, 100.0),
    "mteb_eng_v2": (0.0, 100.0),
    "mteb_multilingual_v2": (0.0, 100.0),
    "mteb_v2_retrieval": (0.0, 100.0),
    "mteb_v2_classification": (0.0, 100.0),
    # US dollars, not a percentage. The floor is the $500 starting balance, so
    # a model that loses money scores 0. The board has no ceiling: its leader
    # was $15,515 on 2026-09-24 and the trend is about +$800 a month, so this
    # bound has roughly 18 months of headroom. `tests/test_profile_refresh.py`
    # fails once a card's value comes within 10% of it.
    "vending_bench_2": (500.0, 30000.0),
})


# ═══════════════════════════════════════════════════════════════
# Use case profiles (MODEL-123, 2026-09-24)
# ═══════════════════════════════════════════════════════════════
#
# The MODEL-108 audit (docs/audits/2026-09-staleness.md) found that the
# profiles weighted benchmarks nobody runs on new models (HumanEval, MATH-500,
# BBH, IFEval, MT-Bench, AlpacaEval, Aider, LiveCodeBench, Terminal-Bench 1.0),
# so a model released after mid-2026 could clear the CLI floor in 1 of 51
# profiles. Jamie approved the §8.1 sets for coding, reasoning, chat, agentic,
# embedding and vision on 2026-09-23. The minor profiles inherit the same
# substitutions:
#
# * the Arena style-control keys (`arena_elo_style_control`, `arena_sc_*`)
#   replace the raw `arena_elo_*` keys, which were read in April and clipped;
# * IFBench replaces IFEval and Terminal-Bench 4.0 replaces 1.0. The MMLU
#   subjects and MultiPL-E stay only where no current source exists, at a
#   reduced weight, and earn nothing toward the coverage guard;
# * dead keys (`web_arena`, `finqa`, `flores`, `fid`, `clip_score`, ...) are
#   retired, and a profile with no current source at all is suspended.
#
# chat's proposed `aa_omniscience` became SimpleQA Verified: both measure
# short-form factual recall, and no profile weight may depend on Artificial
# Analysis (MODEL-117).
#
# `status: suspended` means the profile is still computed (the API's use-case
# enum does not shrink), never featured, and exempt from the coverage guard.
# `suspended_reason` says why, in a sentence a reader can act on.

#: Keys some profile weighted before MODEL-123 and none weights now. Their
#: ranges stay, so an old snapshot still normalises; their card values stay,
#: because a null beats a guess and a retired key is not a wrong one.
RETIRED_FROM_PROFILES: frozenset[str] = frozenset({
    "humaneval", "live_code_bench", "aider_polyglot", "terminal_bench", "math_500", "bbh",
    "ifeval", "mt_bench", "alpaca_eval", "wildbench", "gsm8k", "hellaswag", "arc_challenge",
    "truthfulqa", "tau_bench", "web_arena", "swe_bench_agent", "finqa", "flores", "miracl",
    "beir", "mteb_overall", "mteb_retrieval", "mteb_classification", "mteb_clustering",
    "helm_safety", "pubmedqa", "multipl_e", "fid", "clip_score",
    "arena_elo_overall", "arena_elo_coding", "arena_elo_math", "arena_elo_hard_prompts",
    "arena_elo_vision",
})

USE_CASE_PROFILES: dict[str, dict[str, Any]] = {
    "coding": {
        "preferred_types": ["llm-code", "llm-chat", "llm-reasoning", "vlm"],
        "benchmark_weights": {
            "terminal_bench_v4_0": 0.30, "swe_bench_pro": 0.15, "arena_sc_coding": 0.15,
            "arena_webdev": 0.15, "arena_elo_style_control": 0.15,
            "swe_bench_verified": 0.10,
        },
        "capability_weights": {
            "coding": 0.30, "reasoning": 0.20, "tool_use": 0.15,
        },
        "cost_weight": 0.0,
        "context_weight": 0.1,
    },
    "reasoning": {
        "preferred_types": ["llm-reasoning", "llm-chat"],
        "benchmark_weights": {
            "hle": 0.25, "frontiermath_tiers_1_3_v2": 0.15, "aime_2026": 0.15,
            "arena_sc_hard_prompts": 0.15, "gpqa_diamond": 0.10, "mmlu_pro": 0.10,
            "arena_elo_style_control": 0.10,
        },
        "capability_weights": {
            "reasoning": 0.35, "coding": 0.15, "tool_use": 0.10,
        },
        "cost_weight": 0.0,
        "context_weight": 0.1,
    },
    "chat": {
        "preferred_types": ["llm-chat", "vlm", "llm-reasoning"],
        "benchmark_weights": {
            "arena_elo_style_control": 0.40, "arena_sc_hard_prompts": 0.15,
            "ifbench": 0.15, "simpleqa_verified": 0.20, "mmlu_pro": 0.10,
        },
        "capability_weights": {
            "creative": 0.20, "language": 0.20, "reasoning": 0.15, "tool_use": 0.10,
        },
        "cost_weight": 0.0,
        "context_weight": 0.1,
    },
    "embedding": {
        "preferred_types": ["embedding-text", "embedding-multimodal"],
        "benchmark_weights": {
            "mteb_eng_v2": 0.35, "mteb_multilingual_v2": 0.25, "mteb_v2_retrieval": 0.25,
            "mteb_v2_classification": 0.15,
        },
        "capability_weights": {},
        "cost_weight": 0.0,
        "context_weight": 0.05,
    },
    "vision": {
        "preferred_types": ["vlm", "llm-chat"],
        "benchmark_weights": {
            "arena_sc_vision": 0.35, "mmmu_pro": 0.25, "mmmu": 0.10, "mathvista": 0.10,
            "arena_elo_style_control": 0.10, "docvqa": 0.05, "chartqa": 0.05,
        },
        "capability_weights": {
            "reasoning": 0.15, "creative": 0.10,
        },
        "cost_weight": 0.0,
        "context_weight": 0.1,
    },
    "agentic": {
        "preferred_types": ["llm-reasoning", "llm-code", "llm-chat"],
        "benchmark_weights": {
            "terminal_bench_v4_0": 0.25, "tau3_banking": 0.20, "osworld_2": 0.15,
            "swe_bench_pro": 0.15, "vending_bench_2": 0.10, "browsecomp": 0.10,
            "arena_elo_style_control": 0.05,
        },
        "capability_weights": {
            "tool_use": 0.25, "coding": 0.20, "reasoning": 0.20,
        },
        "cost_weight": 0.0,
        "context_weight": 0.15,
    },
    "rag": {
        "preferred_types": ["embedding-text", "reranker", "llm-chat"],
        "benchmark_weights": {
            # MTEB carries 0.65 so an embedding model with all three clears the
            # 0.50 floor even while the 0.20 of verified additions stands.
            "mteb_v2_retrieval": 0.35, "mteb_multilingual_v2": 0.15, "mteb_eng_v2": 0.15,
            "arena_elo_style_control": 0.15, "simpleqa_verified": 0.10, "ifbench": 0.05,
            "mmlu_pro": 0.05,
        },
        "capability_weights": {
            "language": 0.15, "reasoning": 0.10,
        },
        "cost_weight": 0.0,
        "context_weight": 0.15,
    },
    "safety": {
        "status": "suspended",
        "suspended_reason": (
            "No benchmark with a current source covers safety classifiers. HELM Safety "
            "is saturated on its own page, and BBQ and ToxiGen are static 2022 sets."
        ),
        "preferred_types": ["safety-classifier", "reward-model"],
        "benchmark_weights": {
            "bbq": 0.50, "toxigen": 0.50,
        },
        "capability_weights": {},
        "cost_weight": 0.0,
        "context_weight": 0.05,
    },
    "general": {
        "preferred_types": ["llm-chat", "llm-reasoning", "vlm"],
        "benchmark_weights": {
            "arena_elo_style_control": 0.25, "mmlu_pro": 0.10, "gpqa_diamond": 0.10,
            "hle": 0.10, "terminal_bench_v4_0": 0.10, "swe_bench_pro": 0.10,
            "ifbench": 0.10, "simpleqa_verified": 0.10, "arena_sc_hard_prompts": 0.05,
        },
        "capability_weights": {
            "reasoning": 0.15, "coding": 0.15, "tool_use": 0.10, "creative": 0.10,
        },
        "cost_weight": 0.0,
        "context_weight": 0.1,
    },

    # ─── Sub-domain: Coding by language ──────────────────────────
    "coding_python": {
        "preferred_types": ["llm-code", "llm-chat", "llm-reasoning", "vlm"],
        "benchmark_weights": {
            "swe_bench_verified": 0.30, "terminal_bench_v4_0": 0.20, "swe_bench_pro": 0.15,
            "arena_sc_coding": 0.15, "arena_elo_style_control": 0.10,
            "multipl_e_python": 0.10,
        },
        "capability_weights": {
            "coding": 0.30, "reasoning": 0.20, "tool_use": 0.15,
        },
        "cost_weight": 0.0,
        "context_weight": 0.1,
    },
    "coding_rust": {
        "preferred_types": ["llm-code", "llm-chat", "llm-reasoning", "vlm"],
        "benchmark_weights": {
            "swe_bench_multilingual": 0.25, "terminal_bench_v4_0": 0.20,
            "swe_bench_pro": 0.15, "arena_sc_coding": 0.15,
            "arena_elo_style_control": 0.10, "multipl_e_rust": 0.10,
            "swe_bench_verified": 0.05,
        },
        "capability_weights": {
            "coding": 0.30, "reasoning": 0.20, "tool_use": 0.15,
        },
        "cost_weight": 0.0,
        "context_weight": 0.1,
    },
    "coding_go": {
        "preferred_types": ["llm-code", "llm-chat", "llm-reasoning", "vlm"],
        "benchmark_weights": {
            "swe_bench_multilingual": 0.25, "terminal_bench_v4_0": 0.20,
            "swe_bench_pro": 0.15, "arena_sc_coding": 0.15,
            "arena_elo_style_control": 0.10, "multipl_e_go": 0.10,
            "swe_bench_verified": 0.05,
        },
        "capability_weights": {
            "coding": 0.30, "reasoning": 0.20, "tool_use": 0.15,
        },
        "cost_weight": 0.0,
        "context_weight": 0.1,
    },
    "coding_typescript": {
        "preferred_types": ["llm-code", "llm-chat", "llm-reasoning", "vlm"],
        "benchmark_weights": {
            "swe_bench_multilingual": 0.25, "terminal_bench_v4_0": 0.20,
            "swe_bench_pro": 0.15, "arena_sc_coding": 0.15,
            "arena_elo_style_control": 0.10, "multipl_e_typescript": 0.10,
            "arena_webdev": 0.05,
        },
        "capability_weights": {
            "coding": 0.30, "reasoning": 0.20, "tool_use": 0.15,
        },
        "cost_weight": 0.0,
        "context_weight": 0.1,
    },
    "coding_cpp": {
        "preferred_types": ["llm-code", "llm-chat", "llm-reasoning", "vlm"],
        "benchmark_weights": {
            "swe_bench_multilingual": 0.25, "terminal_bench_v4_0": 0.20,
            "swe_bench_pro": 0.15, "arena_sc_coding": 0.15,
            "arena_elo_style_control": 0.10, "multipl_e_cpp": 0.10,
            "swe_bench_verified": 0.05,
        },
        "capability_weights": {
            "coding": 0.30, "reasoning": 0.20, "tool_use": 0.15,
        },
        "cost_weight": 0.0,
        "context_weight": 0.1,
    },
    "coding_java": {
        "preferred_types": ["llm-code", "llm-chat", "llm-reasoning", "vlm"],
        "benchmark_weights": {
            "swe_bench_multilingual": 0.25, "terminal_bench_v4_0": 0.20,
            "swe_bench_pro": 0.15, "arena_sc_coding": 0.15,
            "arena_elo_style_control": 0.10, "multipl_e_java": 0.10,
            "swe_bench_verified": 0.05,
        },
        "capability_weights": {
            "coding": 0.30, "reasoning": 0.20, "tool_use": 0.15,
        },
        "cost_weight": 0.0,
        "context_weight": 0.1,
    },
    "coding_javascript": {
        "preferred_types": ["llm-code", "llm-chat", "llm-reasoning", "vlm"],
        "benchmark_weights": {
            "swe_bench_multilingual": 0.25, "terminal_bench_v4_0": 0.20,
            "swe_bench_pro": 0.15, "arena_sc_coding": 0.15,
            "arena_elo_style_control": 0.10, "multipl_e_javascript": 0.10,
            "arena_webdev": 0.05,
        },
        "capability_weights": {
            "coding": 0.30, "reasoning": 0.20, "tool_use": 0.15,
        },
        "cost_weight": 0.0,
        "context_weight": 0.1,
    },

    # ─── Sub-domain: Medical ─────────────────────────────────────
    "medical": {
        "preferred_types": ["llm-chat", "llm-reasoning"],
        "benchmark_weights": {
            "arena_sc_medicine": 0.25, "healthbench_professional": 0.20, "medqa": 0.15,
            "medmcqa": 0.10, "gpqa_diamond": 0.10, "arena_elo_style_control": 0.10,
            "mmlu_clinical_knowledge": 0.05, "healthbench_hard": 0.05,
        },
        "capability_weights": {
            "reasoning": 0.25, "domain": 0.20, "language": 0.10,
        },
        "cost_weight": 0.0,
        "context_weight": 0.15,
    },
    "medical_clinical": {
        "preferred_types": ["llm-chat", "llm-reasoning"],
        "benchmark_weights": {
            "arena_sc_medicine": 0.30, "healthbench_professional": 0.25, "medqa": 0.15,
            "mmlu_clinical_knowledge": 0.10, "medmcqa": 0.10,
            "arena_elo_style_control": 0.10,
        },
        "capability_weights": {
            "reasoning": 0.25, "domain": 0.20, "language": 0.10,
        },
        "cost_weight": 0.0,
        "context_weight": 0.15,
    },
    "medical_radiology": {
        "preferred_types": ["vlm", "llm-reasoning", "llm-chat"],
        "benchmark_weights": {
            "arena_sc_vision": 0.25, "arena_sc_medicine": 0.20, "mmmu_pro": 0.15,
            "medqa": 0.15, "healthbench_professional": 0.10,
            "arena_elo_style_control": 0.10, "mmmu": 0.05,
        },
        "capability_weights": {
            "reasoning": 0.25, "domain": 0.15, "creative": 0.10,
        },
        "cost_weight": 0.0,
        "context_weight": 0.1,
    },

    # ─── Sub-domain: Legal ───────────────────────────────────────
    "legal": {
        "preferred_types": ["llm-chat", "llm-reasoning"],
        "benchmark_weights": {
            "arena_sc_legal": 0.40, "legalbench": 0.25, "arena_elo_style_control": 0.15,
            "ifbench": 0.10, "mmlu_professional_law": 0.05, "mmlu_pro": 0.05,
        },
        "capability_weights": {
            "reasoning": 0.25, "domain": 0.15, "language": 0.15,
        },
        "cost_weight": 0.0,
        "context_weight": 0.15,
    },

    # ─── Sub-domain: Financial ───────────────────────────────────
    "financial": {
        "preferred_types": ["llm-chat", "llm-reasoning"],
        "benchmark_weights": {
            "arena_sc_business": 0.35, "finbench": 0.20, "mmlu_pro": 0.15, "ifbench": 0.10,
            "arena_sc_math": 0.10, "arena_elo_style_control": 0.10,
        },
        "capability_weights": {
            "reasoning": 0.25, "domain": 0.15, "language": 0.10,
        },
        "cost_weight": 0.0,
        "context_weight": 0.15,
    },

    # ─── Sub-domain: Science ─────────────────────────────────────
    "science": {
        "preferred_types": ["llm-reasoning", "llm-chat"],
        "benchmark_weights": {
            "gpqa_diamond": 0.25, "arena_sc_science": 0.20, "hle": 0.15, "mmlu_pro": 0.15,
            "frontiermath_tiers_1_3_v2": 0.10, "arena_elo_style_control": 0.10, "aime_2026": 0.05,
        },
        "capability_weights": {
            "reasoning": 0.30, "domain": 0.15, "language": 0.10,
        },
        "cost_weight": 0.0,
        "context_weight": 0.1,
    },
    "science_chemistry": {
        "preferred_types": ["llm-reasoning", "llm-chat"],
        "benchmark_weights": {
            "gpqa_diamond": 0.25, "mmlu_chemistry": 0.20, "arena_sc_science": 0.20,
            "mmlu_pro": 0.15, "hle": 0.10, "arena_elo_style_control": 0.10,
        },
        "capability_weights": {
            "reasoning": 0.30, "domain": 0.15, "language": 0.10,
        },
        "cost_weight": 0.0,
        "context_weight": 0.1,
    },
    "science_physics": {
        "preferred_types": ["llm-reasoning", "llm-chat"],
        "benchmark_weights": {
            "gpqa_diamond": 0.25, "mmlu_physics": 0.20, "arena_sc_science": 0.20,
            "hle": 0.10, "mmlu_pro": 0.10, "arena_elo_style_control": 0.10,
            "frontiermath_tiers_1_3_v2": 0.05,
        },
        "capability_weights": {
            "reasoning": 0.30, "domain": 0.15, "language": 0.10,
        },
        "cost_weight": 0.0,
        "context_weight": 0.1,
    },
    "science_biology": {
        "preferred_types": ["llm-reasoning", "llm-chat"],
        "benchmark_weights": {
            "gpqa_diamond": 0.25, "mmlu_biology": 0.20, "arena_sc_science": 0.20,
            "mmlu_pro": 0.15, "hle": 0.10, "arena_elo_style_control": 0.10,
        },
        "capability_weights": {
            "reasoning": 0.30, "domain": 0.15, "language": 0.10,
        },
        "cost_weight": 0.0,
        "context_weight": 0.1,
    },

    # ─── Sub-domain: Translation ─────────────────────────────────
    "translation": {
        "preferred_types": ["llm-chat", "vlm"],
        "benchmark_weights": {
            "arena_sc_non_english": 0.40, "mmmlu": 0.20, "arena_elo_style_control": 0.15,
            "mgsm": 0.10, "ifbench": 0.10, "mmlu_pro": 0.05,
        },
        "capability_weights": {
            "language": 0.30, "creative": 0.15, "reasoning": 0.10,
        },
        "cost_weight": 0.0,
        "context_weight": 0.15,
    },

    # ─── Sub-domain: Creative Writing ────────────────────────────
    "writing_creative": {
        "preferred_types": ["llm-chat", "llm-reasoning"],
        "benchmark_weights": {
            "arena_sc_creative_writing": 0.45, "arena_elo_style_control": 0.25,
            "arena_sc_multi_turn": 0.10, "arena_sc_writing": 0.10, "ifbench": 0.10,
        },
        "capability_weights": {
            "creative": 0.30, "language": 0.20, "reasoning": 0.10,
        },
        "cost_weight": 0.0,
        "context_weight": 0.1,
    },
    "writing_technical": {
        "preferred_types": ["llm-chat", "llm-reasoning", "llm-code"],
        "benchmark_weights": {
            "arena_sc_writing": 0.30, "arena_elo_style_control": 0.20, "ifbench": 0.20,
            "mmlu_pro": 0.10, "arena_sc_instruction_following": 0.10,
            "arena_sc_expert": 0.10,
        },
        "capability_weights": {
            "creative": 0.25, "reasoning": 0.20, "language": 0.15,
        },
        "cost_weight": 0.0,
        "context_weight": 0.15,
    },
    "summarization": {
        "preferred_types": ["llm-chat", "llm-reasoning"],
        "benchmark_weights": {
            "arena_sc_writing": 0.25, "arena_elo_style_control": 0.20,
            "arena_sc_longer_query": 0.15, "arena_sc_instruction_following": 0.15,
            "ifbench": 0.15, "simpleqa_verified": 0.10,
        },
        "capability_weights": {
            "creative": 0.25, "language": 0.20, "reasoning": 0.15,
        },
        "cost_weight": 0.0,
        "context_weight": 0.2,
    },

    # ─── Sub-domain: Math (competitive / advanced) ───────────────
    "math_competition": {
        "preferred_types": ["llm-reasoning", "llm-chat"],
        "benchmark_weights": {
            "aime_2026": 0.30, "frontiermath_tiers_1_3_v2": 0.25, "arena_sc_math": 0.15,
            "aime_2025": 0.10, "hle": 0.10, "gpqa_diamond": 0.10,
        },
        "capability_weights": {
            "reasoning": 0.35, "coding": 0.10,
        },
        "cost_weight": 0.0,
        "context_weight": 0.05,
    },

    # ─── Sub-domain: Education ───────────────────────────────────
    "education": {
        "preferred_types": ["llm-chat", "llm-reasoning", "vlm"],
        "benchmark_weights": {
            "arena_elo_style_control": 0.25, "mmlu_pro": 0.20, "arena_sc_multi_turn": 0.15,
            "simpleqa_verified": 0.15, "gpqa_diamond": 0.15, "ifbench": 0.10,
        },
        "capability_weights": {
            "reasoning": 0.20, "language": 0.20, "creative": 0.15,
        },
        "cost_weight": 0.0,
        "context_weight": 0.1,
    },
    "education_stem": {
        "preferred_types": ["llm-reasoning", "llm-chat"],
        "benchmark_weights": {
            "gpqa_diamond": 0.20, "mmlu_pro": 0.15, "arena_sc_math": 0.15,
            "arena_sc_science": 0.15, "arena_elo_style_control": 0.15,
            "mmlu_physics": 0.05, "mmlu_chemistry": 0.05, "mmlu_biology": 0.05,
            "frontiermath_tiers_1_3_v2": 0.05,
        },
        "capability_weights": {
            "reasoning": 0.30, "domain": 0.15, "language": 0.10,
        },
        "cost_weight": 0.0,
        "context_weight": 0.1,
    },
    "education_humanities": {
        "preferred_types": ["llm-chat", "llm-reasoning"],
        "benchmark_weights": {
            "arena_elo_style_control": 0.25, "arena_sc_writing": 0.20,
            "arena_sc_multi_turn": 0.15, "mmlu_pro": 0.15, "simpleqa_verified": 0.15,
            "mmlu_professional_law": 0.05, "mmlu_business_ethics": 0.05,
        },
        "capability_weights": {
            "language": 0.25, "creative": 0.20, "reasoning": 0.15,
        },
        "cost_weight": 0.0,
        "context_weight": 0.1,
    },

    # ─── Sub-domain: Data Science / Analytics ────────────────────
    "data_science": {
        "preferred_types": ["llm-code", "llm-reasoning", "llm-chat"],
        "benchmark_weights": {
            "swe_bench_verified": 0.20, "arena_sc_coding": 0.20, "arena_sc_math": 0.15,
            "terminal_bench_v4_0": 0.15, "mmlu_pro": 0.10, "gpqa_diamond": 0.10,
            "multipl_e_python": 0.05, "arena_elo_style_control": 0.05,
        },
        "capability_weights": {
            "coding": 0.25, "reasoning": 0.25, "tool_use": 0.15,
        },
        "cost_weight": 0.0,
        "context_weight": 0.15,
    },

    # ─── Sub-domain: Customer Support / Chatbot ──────────────────
    "customer_support": {
        "preferred_types": ["llm-chat", "vlm"],
        "benchmark_weights": {
            "arena_elo_style_control": 0.30, "arena_sc_multi_turn": 0.20, "ifbench": 0.20,
            "arena_sc_instruction_following": 0.10, "tau3_banking": 0.10,
            "simpleqa_verified": 0.10,
        },
        "capability_weights": {
            "language": 0.25, "tool_use": 0.20, "creative": 0.10,
        },
        "cost_weight": 0.0,
        "context_weight": 0.1,
    },

    # ─── Sub-domain: Content Moderation ──────────────────────────
    "content_moderation": {
        "status": "suspended",
        "suspended_reason": (
            "Moderation rests on ToxiGen and BBQ, static 2022 sets with no current "
            "source; HELM Safety is saturated on its own page."
        ),
        "preferred_types": ["safety-classifier", "llm-chat", "reward-model"],
        "benchmark_weights": {
            "toxigen": 0.40, "bbq": 0.35, "ifbench": 0.10, "arena_elo_style_control": 0.15,
        },
        "capability_weights": {
            "safety": 0.30, "language": 0.15,
        },
        "cost_weight": 0.0,
        "context_weight": 0.05,
    },

    # ─── Sub-domain: Research Assistant ──────────────────────────
    "research_assistant": {
        "preferred_types": ["llm-reasoning", "llm-chat", "vlm"],
        "benchmark_weights": {
            "hle": 0.20, "gpqa_diamond": 0.15, "simpleqa_verified": 0.15,
            "arena_sc_expert": 0.15, "arena_sc_hard_prompts": 0.10, "mmlu_pro": 0.10,
            "browsecomp": 0.10, "arena_elo_style_control": 0.05,
        },
        "capability_weights": {
            "reasoning": 0.25, "language": 0.15, "tool_use": 0.15,
        },
        "cost_weight": 0.0,
        "context_weight": 0.2,
    },

    # ─── Sub-domain: Roleplay / Character ────────────────────────
    "roleplay": {
        "preferred_types": ["llm-chat"],
        "benchmark_weights": {
            "arena_elo_style_control": 0.35, "arena_sc_creative_writing": 0.30,
            "arena_sc_multi_turn": 0.25, "ifbench": 0.10,
        },
        "capability_weights": {
            "creative": 0.35, "language": 0.25,
        },
        "cost_weight": 0.0,
        "context_weight": 0.15,
    },

    # ─── Sub-domain: Audio ───────────────────────────────────────
    "speech_to_text": {
        "status": "suspended",
        "suspended_reason": (
            "No card holds a word error rate, and no current board is sourced yet. The "
            "old Arena, MIRACL and MGSM weights ranked LLMs, not transcribers."
        ),
        "preferred_types": ["audio-stt", "audio-multimodal"],
        "benchmark_weights": {
            "wer_librispeech": 1.00,
        },
        "capability_weights": {
            "language": 0.20,
        },
        "cost_weight": 0.0,
        "context_weight": 0.05,
    },
    "text_to_speech": {
        "status": "suspended",
        "suspended_reason": (
            "No card holds a TTS quality score. The old Arena and MT-Bench weights "
            "ranked chat LLMs (claude-opus-4-6, gpt-4-1) as speech models."
        ),
        "preferred_types": ["audio-tts", "audio-multimodal"],
        "benchmark_weights": {
            "mos_tts": 1.00,
        },
        "capability_weights": {
            "creative": 0.15, "language": 0.15,
        },
        "cost_weight": 0.0,
        "context_weight": 0.05,
    },

    # ─── Sub-domain: Image Generation ────────────────────────────
    "image_generation": {
        "preferred_types": ["image-gen", "vlm"],
        "benchmark_weights": {
            "arena_text_to_image": 0.70, "arena_image_edit": 0.30,
        },
        "capability_weights": {
            "creative": 0.30,
        },
        "cost_weight": 0.0,
        "context_weight": 0.05,
    },

    # ─── Sub-domain: Cybersecurity ───────────────────────────────
    "cybersecurity": {
        "preferred_types": ["llm-code", "llm-reasoning", "llm-chat"],
        "benchmark_weights": {
            "terminal_bench_v4_0": 0.25, "swe_bench_pro": 0.15, "arena_sc_coding": 0.15,
            "swe_bench_verified": 0.10, "mmlu_computer_science": 0.10,
            "gpqa_diamond": 0.10, "ifbench": 0.10, "arena_elo_style_control": 0.05,
        },
        "capability_weights": {
            "coding": 0.25, "reasoning": 0.25, "tool_use": 0.20,
        },
        "cost_weight": 0.0,
        "context_weight": 0.15,
    },

    # ─── Sub-domain: DevOps / Infrastructure ─────────────────────
    "devops": {
        "preferred_types": ["llm-code", "llm-chat", "llm-reasoning"],
        "benchmark_weights": {
            "terminal_bench_v4_0": 0.35, "swe_bench_verified": 0.15,
            "arena_sc_coding": 0.15, "swe_bench_pro": 0.10, "ifbench": 0.10,
            "arena_elo_style_control": 0.10, "deepswe_v1_1": 0.05,
        },
        "capability_weights": {
            "coding": 0.25, "tool_use": 0.25, "reasoning": 0.15,
        },
        "cost_weight": 0.0,
        "context_weight": 0.1,
    },

    # ─── Sub-domain: Multilingual ────────────────────────────────
    "multilingual": {
        "preferred_types": ["llm-chat", "vlm"],
        "benchmark_weights": {
            "arena_sc_non_english": 0.40, "mmmlu": 0.25, "arena_elo_style_control": 0.15,
            "mgsm": 0.10, "ifbench": 0.10,
        },
        "capability_weights": {
            "language": 0.35, "creative": 0.10, "reasoning": 0.10,
        },
        "cost_weight": 0.0,
        "context_weight": 0.15,
    },

    # ─── Sub-domain: Financial (specialties) ─────────────────────
    "financial_analysis": {
        "preferred_types": ["llm-reasoning", "llm-chat"],
        "benchmark_weights": {
            "arena_sc_business": 0.30, "finbench": 0.20, "arena_sc_math": 0.15,
            "arena_elo_style_control": 0.15, "mmlu_professional_accounting": 0.10,
            "mmlu_pro": 0.10,
        },
        "capability_weights": {
            "reasoning": 0.30, "domain": 0.15, "language": 0.10,
        },
        "cost_weight": 0.0,
        "context_weight": 0.15,
    },
    "financial_compliance": {
        "preferred_types": ["llm-chat", "llm-reasoning"],
        "benchmark_weights": {
            "arena_sc_business": 0.25, "arena_sc_legal": 0.20, "finbench": 0.15,
            "legalbench": 0.15, "arena_elo_style_control": 0.15, "ifbench": 0.10,
        },
        "capability_weights": {
            "reasoning": 0.25, "domain": 0.15, "language": 0.15,
        },
        "cost_weight": 0.0,
        "context_weight": 0.15,
    },

    # ─── Sub-domain: Science (more specialties) ──────────────────
    "science_astronomy": {
        "preferred_types": ["llm-reasoning", "llm-chat"],
        "benchmark_weights": {
            "gpqa_diamond": 0.25, "mmlu_astronomy": 0.25, "arena_sc_science": 0.20,
            "hle": 0.10, "mmlu_pro": 0.10, "arena_elo_style_control": 0.10,
        },
        "capability_weights": {
            "reasoning": 0.30, "domain": 0.15, "language": 0.10,
        },
        "cost_weight": 0.0,
        "context_weight": 0.1,
    },

    # ─── Sub-domain: Legal (specialties) ─────────────────────────
    "legal_contract_review": {
        "preferred_types": ["llm-chat", "llm-reasoning"],
        "benchmark_weights": {
            "arena_sc_legal": 0.35, "legalbench": 0.25, "arena_elo_style_control": 0.10,
            "arena_sc_instruction_following": 0.10, "ifbench": 0.10,
            "mmlu_professional_law": 0.10,
        },
        "capability_weights": {
            "reasoning": 0.25, "language": 0.20, "domain": 0.15,
        },
        "cost_weight": 0.0,
        "context_weight": 0.2,
    },

    # ─── Sub-domain: Biotech / Life Sciences ─────────────────────
    "biotech": {
        "preferred_types": ["llm-reasoning", "llm-chat"],
        "benchmark_weights": {
            "gpqa_diamond": 0.20, "arena_sc_science": 0.20, "arena_sc_medicine": 0.15,
            "healthbench_professional": 0.10, "mmlu_biology": 0.10,
            "arena_elo_style_control": 0.10, "mmlu_chemistry": 0.05, "medqa": 0.05,
            "hle": 0.05,
        },
        "capability_weights": {
            "reasoning": 0.30, "domain": 0.20, "language": 0.10,
        },
        "cost_weight": 0.0,
        "context_weight": 0.15,
    },

    # ─── Sub-domain: Accounting ──────────────────────────────────
    "accounting": {
        "preferred_types": ["llm-chat", "llm-reasoning"],
        "benchmark_weights": {
            "arena_sc_business": 0.30, "mmlu_professional_accounting": 0.20,
            "finbench": 0.15, "arena_sc_math": 0.15, "ifbench": 0.10,
            "arena_elo_style_control": 0.10,
        },
        "capability_weights": {
            "reasoning": 0.25, "domain": 0.15, "language": 0.10,
        },
        "cost_weight": 0.0,
        "context_weight": 0.1,
    },

    # ─── Sub-domain: Code Review ─────────────────────────────────
    "code_review": {
        "preferred_types": ["llm-code", "llm-reasoning", "llm-chat"],
        "benchmark_weights": {
            "swe_bench_pro": 0.20, "cursorbench_4": 0.15, "arena_sc_coding": 0.15,
            "swe_bench_verified": 0.10, "deepswe_v1_1": 0.10, "frontiercode_v1_1": 0.10,
            "terminal_bench_v4_0": 0.10, "arena_elo_style_control": 0.10,
        },
        "capability_weights": {
            "coding": 0.30, "reasoning": 0.25, "language": 0.10,
        },
        "cost_weight": 0.0,
        "context_weight": 0.15,
    },
}


# ═══════════════════════════════════════════════════════════════
# Platform classifications for hosting filter
# ═══════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════
# Verified evidence in the profiles (MODEL-32, option B)
# ═══════════════════════════════════════════════════════════════
#
# The census verifies benchmarks that publish current, dated results for
# current models. In practice that means Artificial Analysis index components,
# because those are the ones that do. The profiles below weight the classic
# benchmarks a reader expects — HumanEval, SWE-bench Verified, GPQA Diamond —
# and the two sets did not overlap at all, so no reviewed evidence could move
# any ranking.
#
# Operator decision 2026-09-09: take the verified benchmarks into the profiles
# now, and keep verifying the classic ones as the standing goal (MODEL-33).
#
# The cap is the point. One evaluator's index carries at most this share of any
# profile, so reviewed evidence is load-bearing without a single source
# deciding what "best" means. Existing weights are scaled down proportionally,
# so a profile still sums to what it did before.

#: Maximum share of any profile that one evaluator's index may carry.
VERIFIED_INDEX_WEIGHT = 0.20

#: Verified benchmarks, mapped onto profiles by the category their benchgraph
#: page declares. All seven declare higher_is_better, unit %, max_score 100,
#: which is where their ranges below come from — read, not assumed.
VERIFIED_ADDITIONS: dict[str, list[str]] = {
    "coding": ["scicode"],
    "agentic": ["aa_briefcase", "automationbench_aa", "gdpval_aa"],
    "reasoning": ["critpt"],
    "rag": ["aa_lcr", "gdp_pdf_aa"],
    "science": ["scicode", "critpt"],
    "general": ["gdpval_aa"],
}

BENCHMARK_RANGES.update({
    # Confirmed from each benchmark's page: higher_is_better, %, max 100.
    "aa_briefcase": (0.0, 100.0),
    "aa_lcr": (0.0, 100.0),
    "automationbench": (0.0, 100.0),
    "automationbench_aa": (0.0, 100.0),
    "critpt": (0.0, 100.0),
    "gdp_pdf_aa": (0.0, 100.0),
    "gdpval_aa": (0.0, 100.0),
    "scicode": (0.0, 100.0),
})


def _apply_verified_additions() -> None:
    """Fold the verified benchmarks into the profiles, under the cap."""
    for profile_key, benchmarks in VERIFIED_ADDITIONS.items():
        profile = USE_CASE_PROFILES.get(profile_key)
        if not profile:
            continue
        weights = profile.get("benchmark_weights") or {}
        # Anything already weighted is left alone; only genuinely new entries
        # take from the existing budget.
        new = [b for b in benchmarks if b not in weights]
        if not new:
            continue
        scale = 1.0 - VERIFIED_INDEX_WEIGHT
        rescaled = {k: round(v * scale, 4) for k, v in weights.items()}
        share = round(VERIFIED_INDEX_WEIGHT / len(new), 4)
        for benchmark in new:
            rescaled[benchmark] = share
        profile["benchmark_weights"] = rescaled


_apply_verified_additions()


# ═══════════════════════════════════════════════════════════════
# Current sources, the Arena snapshot and staleness (MODEL-123)
# ═══════════════════════════════════════════════════════════════

_ARENA_DATASET_URL = "https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset"

#: Where a current-generation model's score for each key comes from today,
#: other than Artificial Analysis. `tests/test_profile_refresh.py` requires every
#: active profile to put at least `MIN_BENCHMARK_COVERAGE` of its weight on keys
#: listed here, so the CLI floor can rank a model released this year from
#: current sources alone. A key missing from this table can still be weighted;
#: it just earns nothing toward that guard. MMLU-Pro, IFBench, MMMLU and the
#: MMLU subjects are absent: 2026 model cards rarely report them and no
#: independent board runs them (checked 2026-09-24).
CURRENT_SOURCES: dict[str, tuple[str, ...]] = {
    "terminal_bench_v4_0": ("https://www.tbench.ai/leaderboard",),
    "swe_bench_pro": ("https://labs.scale.com/leaderboard/swe_bench_pro_public",),
    "swe_bench_verified": ("https://epoch.ai/benchmarks/swe-bench-verified",),
    "hle": ("https://labs.scale.com/leaderboard/humanitys_last_exam",),
    "frontiermath_tiers_1_3_v2": ("https://epoch.ai/frontiermath",),
    # AIME 2025 and 2026 are absent: MathArena, their only board, lists its
    # final-answer competitions as deprecated and has no row for GPT-6 Astra,
    # Fable 5.1 or Opus 5 (read 2026-09-24).
    "gpqa_diamond": ("https://epoch.ai/benchmarks/gpqa-diamond",),
    "simpleqa_verified": ("https://epoch.ai/benchmarks/simpleqa-verified",),
    "osworld_2": ("https://osworld-v2.xlang.ai/",),
    "tau3_banking": ("https://taubench.com/",),
    "vending_bench_2": ("https://andonlabs.com/evals/vending-bench-2",),
    "deepswe_v1_1": ("https://deepswe.datacurve.ai/",),
    "cursorbench_4": ("https://cursor.com/cursorbench",),
    "frontiercode_v1_1": ("https://cognition.com/frontiercode",),
    "mteb_eng_v2": ("https://huggingface.co/spaces/mteb/leaderboard",),
    "mteb_multilingual_v2": ("https://huggingface.co/spaces/mteb/leaderboard",),
    "mteb_v2_retrieval": ("https://huggingface.co/spaces/mteb/leaderboard",),
    "mteb_v2_classification": ("https://huggingface.co/spaces/mteb/leaderboard",),
    # Provider self-reports only, which MODEL-123 admits for a key no
    # independent board carries (Jamie, 2026-09-23). Still reported for 2026
    # models in system cards.
    "browsecomp": ("https://openai.com/index/browsecomp/",),
    "mmmu_pro": ("https://mmmu-benchmark.github.io/#leaderboard",),
    "healthbench_professional": ("https://arxiv.org/abs/2604.27470",),
    "healthbench_hard": ("https://arxiv.org/abs/2505.08775",),
}

#: Keys whose current source is a provider's own report. Every other key in
#: `CURRENT_SOURCES` has an independent board, and on those a provider
#: self-report never counts, even for a model the board has not reached yet:
#: Jamie's rule (2026-09-23) is that a self-report fills a key "when no
#: independent board carries it", and the audit read "it" as the benchmark
#: (§8.3 names SWE-bench Verified, BrowseComp and MMMU). A provider's own
#: harness is not the board's harness, so mixing the two on one key would
#: compare different measurements. SWE-bench Verified is here because its
#: official board stalled in February 2026 and Epoch AI's last run was in June.
SELF_REPORTED_KEYS: frozenset[str] = frozenset({
    "swe_bench_verified", "browsecomp", "mmmu_pro", "healthbench_professional",
    "healthbench_hard",
})

#: Weighted keys whose own page marks them saturated, kept because Jamie
#: approved them by name. The guard fails on any other saturated or superseded
#: weighted key, and fails here too once a page stops saying saturated.
APPROVED_DESPITE_SATURATION: dict[str, str] = {
    "gpqa_diamond": "MODEL-123 §8.1 (Jamie, 2026-09-23): reasoning 0.10, with a 100 ceiling.",
    "mmmu_pro": "MODEL-123 §8.1 (Jamie, 2026-09-23): vision 0.25, the harder successor to MMMU.",
    "docvqa": "MODEL-123 §8.1 (Jamie, 2026-09-23): vision 0.05, shrunk for saturation.",
    "aime_2026": ("MODEL-123 §8.1 (Jamie, 2026-09-23): reasoning 0.15. Its page was marked "
                  "saturated after the approval (MathArena top 100%, competition deprecated); "
                  "replacing it is Jamie's call."),
}

#: A live reading older than this many days is flagged in every row's
#: `stale_benchmarks`. It still counts (Jamie, 2026-09-23): a dated standing is
#: evidence, and the flag lets a caller decide how much to trust it.
STALE_AFTER_DAYS = 45

#: The one Arena snapshot every ranking reads. Jamie, 2026-09-23: "Arena is
#: normalised within one snapshot instead of fixed Elo bounds, and every Arena
#: value in a ranking must share one observation date."
#:
#: Source: LMArena's `lmarena-ai/leaderboard-dataset` on Hugging Face, CC BY 4.0,
#: pinned to one revision, `latest` split. Never lmarena.ai itself. Each board
#: carries the date Arena states for it (`leaderboard_publish_date`). The text
#: and vision boards share 2026-09-13. Arena published no WebDev board that day
#: (its nearest are 09-11 and 09-22/23), and the newest date all three share is
#: 2026-08-21, which predates Fable 5.1 and Opus 5.5. So the rule is enforced
#: per board: every value of one Arena key must carry that board's pinned date,
#: or it does not count. Every board comes from the one dataset revision.
#:
#: `leader` is the top rating on that board at that date, over every row,
#: including models with no card. It is the reference point for normalisation.
ARENA_SNAPSHOT: dict[str, Any] = {
    "dataset": "lmarena-ai/leaderboard-dataset",
    "url": _ARENA_DATASET_URL,
    "license": "CC BY 4.0",
    "attribution": ("LMArena, Arena leaderboard dataset "
                    "(lmarena-ai/leaderboard-dataset), CC BY 4.0"),
    "revision": "1880dbebff5ba3e2dd3865ecf6fc43539c2099db",
    "read_on": "2026-09-24",
    "split": "latest",
    "boards": {
        "arena_elo_style_control": {"subset": "text_style_control", "category": "overall",
                                    "published": "2026-09-13", "leader": 1505.68},
        "arena_sc_coding": {"subset": "text_style_control", "category": "coding",
                            "published": "2026-09-13", "leader": 1552.39},
        "arena_sc_hard_prompts": {"subset": "text_style_control", "category": "hard_prompts",
                                  "published": "2026-09-13", "leader": 1533.13},
        "arena_sc_math": {"subset": "text_style_control", "category": "math",
                          "published": "2026-09-13", "leader": 1526.28},
        "arena_sc_creative_writing": {"subset": "text_style_control",
                                      "category": "creative_writing",
                                      "published": "2026-09-13", "leader": 1504.13},
        "arena_sc_instruction_following": {"subset": "text_style_control",
                                           "category": "instruction_following",
                                           "published": "2026-09-13", "leader": 1513.49},
        "arena_sc_multi_turn": {"subset": "text_style_control", "category": "multi_turn",
                                "published": "2026-09-13", "leader": 1520.14},
        "arena_sc_expert": {"subset": "text_style_control", "category": "expert",
                            "published": "2026-09-13", "leader": 1548.48},
        "arena_sc_longer_query": {"subset": "text_style_control", "category": "longer_query",
                                  "published": "2026-09-13", "leader": 1524.11},
        "arena_sc_non_english": {"subset": "text_style_control", "category": "non_english",
                                 "published": "2026-09-13", "leader": 1495.98},
        "arena_sc_medicine": {"subset": "text_style_control",
                              "category": "industry_medicine_and_healthcare",
                              "published": "2026-09-13", "leader": 1530.34},
        "arena_sc_legal": {"subset": "text_style_control",
                           "category": "industry_legal_and_government",
                           "published": "2026-09-13", "leader": 1541.39},
        "arena_sc_business": {
            "subset": "text_style_control",
            "category": "industry_business_and_management_and_financial_operations",
            "published": "2026-09-13", "leader": 1517.03},
        "arena_sc_science": {"subset": "text_style_control",
                             "category": "industry_life_and_physical_and_social_science",
                             "published": "2026-09-13", "leader": 1528.15},
        "arena_sc_writing": {"subset": "text_style_control",
                             "category": "industry_writing_and_literature_and_language",
                             "published": "2026-09-13", "leader": 1511.45},
        "arena_sc_vision": {"subset": "vision_style_control", "category": "overall",
                            "published": "2026-09-13", "leader": 1309.50},
        "arena_webdev": {"subset": "webdev", "category": "overall",
                         "published": "2026-09-23", "leader": 1818.41},
        "arena_text_to_image": {"subset": "text_to_image", "category": "overall",
                                "published": "2026-09-22", "leader": 1423.16},
        "arena_image_edit": {"subset": "image_edit", "category": "overall",
                             "published": "2026-09-22", "leader": 1525.98},
    },
}

for _key in ARENA_SNAPSHOT["boards"]:
    CURRENT_SOURCES[_key] = (_ARENA_DATASET_URL,)

#: Keys an independent board carries. `pipeline.ranking.select_evidence` never
#: lets a provider self-report fill one of these.
INDEPENDENT_BOARD_KEYS: frozenset[str] = frozenset(CURRENT_SOURCES) - SELF_REPORTED_KEYS


def _normalize_arena(bench_id: str, rating: float) -> float:
    """An Arena rating as twice its expected win rate against the snapshot leader.

    Arena fits a Bradley-Terry model on the Elo scale: a gap of `d` points means
    the lower model is expected to win `1 / (1 + 10 ** (d / 400))` of its votes
    against the higher one. Only gaps are meaningful. The absolute level drifts
    between snapshots and differs between boards, which is why a fixed
    (1000, 1400) bound put 76 of 147 style-control readings at the ceiling.
    Doubling puts the leader at exactly 100: a model 100 points behind scores
    72, 200 behind scores 48, 400 behind scores 18. The order within a board is
    the board's own; only the spacing is ours.
    """
    leader = ARENA_SNAPSHOT["boards"][bench_id]["leader"]
    win = 1.0 / (1.0 + 10.0 ** ((leader - rating) / 400.0))
    return max(0.0, min(100.0, 200.0 * win))


def arena_snapshot_policy() -> dict[str, Any]:
    """The snapshot, as the ranking policy publishes it."""
    return {
        "dataset": ARENA_SNAPSHOT["dataset"],
        "url": ARENA_SNAPSHOT["url"],
        "license": ARENA_SNAPSHOT["license"],
        "attribution": ARENA_SNAPSHOT["attribution"],
        "revision": ARENA_SNAPSHOT["revision"],
        "normalisation": "win_probability_vs_snapshot_leader",
        "boards": {k: {"published": b["published"], "leader": b["leader"]}
                   for k, b in ARENA_SNAPSHOT["boards"].items()},
    }


# Product defaults, not statistical confidence thresholds. The benchmark set
# stays fixed, including when a candidate or an evaluator has sparse coverage.
# CLI / API stay conservative. The wizard is a different surface: a browser
# wants breadth, dpf wants a shortlist it can defend. MODEL-34, 2026-09-11.
MIN_BENCHMARK_COVERAGE = 0.50
WIZARD_BENCHMARK_COVERAGE = 0.25
MIN_BENCHMARK_COUNT = 2


# ── the neutrality commitment (MODEL-70) ─────────────────────────────────────
#
# A floor is checkable because it is published as a number next to the answer it
# shaped. The neutrality claim was only ever prose, which means a caller had to
# trust it. It ships here, beside the floors, for the same reason the floors
# ship: so an agent can read the commitment out of the same object that carries
# the policy it acted on, rather than believe a page it never fetched.
#
# This constant is the single source. `ranking_policy()` carries it into
# `/api/rank/profiles.json`, into every `rank_report()` and therefore into
# `rankings.json`, and into the `policy` block of every `POST /v1/rank`
# response. `pipeline/legal.py` renders the published pages from the same
# values, so the prose and the JSON cannot drift apart.
#
# Source of the rule: `docs/agent-commerce-assessment.md` §3, which requires it
# to be written into the terms before any money moves.

#: Verbatim. Quoted in `docs/legal/terms-of-service.md` and rendered on
#: https://modelspec.dev/legal/terms/ — three copies of one string, checked by
#: `tests/test_legal.py`. Editing it here is editing the published terms.
HONEST_BROKER_RULE = (
    "Charging the consumer of a recommendation is compatible with being an "
    "honest broker. Charging the subjects of one is not."
)

#: Verbatim, and the word "permanently" is load-bearing: it is the difference
#: between a current price list and a commitment.
NEUTRALITY_PLEDGE = (
    "No referral fees, no paid placement, no provider-paid visibility, "
    "permanently."
)

#: Verbatim, neutrality 1.1 (2026-09-23). The case the pledge does not reach:
#: money flowing *to* a vendor we catalogue rather than from one. Quoted in
#: `docs/legal/neutrality.md`; `tests/test_legal.py` holds the two equal. The
#: mechanisms are `schema/suppliers.py` (the vendors we pay), the disclosure the
#: card page prints from it (`pipeline/render.py`), and the refusals in
#: `scripts/attribution.py` (`supplier_conflict`, `apply_policy`). MODEL-101.
VENDOR_PURCHASE_RULE = (
    "We may be a paying customer of a vendor whose models we catalogue. When we "
    "are, the card says so, and no field on that vendor's card is ever set by "
    "that vendor's own model."
)

#: Where a machine reads the long forms. Static Pages, no key, no account.
LEGAL_BASE_URL = "https://modelspec.dev/legal"


def neutrality_commitment() -> dict[str, Any]:
    """What ModelSpec will not take money for, in a shape an agent can check.

    Every `assertion` is negative on purpose. The positioning is a set of things
    the service is structurally unable to do, not a set of things it promises
    not to do, so each one is either contradicted by an observable fact or it
    holds. A new assertion is additive; flipping one of these `false` values to
    `true` is not a version bump, it is a different product.
    """
    return {
        "version": "neutrality-v1",
        "operator": "Sparks and Sawdust LLC",
        "rule": HONEST_BROKER_RULE,
        "pledge": NEUTRALITY_PLEDGE,
        "permanent": True,
        "assertions": {
            # §4.5: never charge the subjects of a recommendation.
            "accepts_referral_fees": False,
            "accepts_paid_placement": False,
            "accepts_provider_paid_visibility": False,
            # §10.1: recommend and hand off. A router earns on token volume,
            # and margin that grows with volume is a steering incentive.
            "proxies_inference_tokens": False,
            # §10.2: a request carries a profile, not a prompt. There is
            # nothing to retain, which is why this is architecture and not a
            # retention promise.
            "stores_customer_prompts": False,
            # Neutrality 1.1: buying from a vendor we catalogue. The card
            # page discloses it (`pipeline/render.py`, from
            # `schema/suppliers.py`), and `scripts/attribution.py` refuses a
            # supplier's model any field on that supplier's card.
            "conceals_purchases_from_catalogued_vendors": False,
            "lets_supplier_models_write_supplier_cards": False,
        },
        #: §10.3: neutrality past money, into sourcing. Naming the stages is the
        #: point — "neutral ranking" would leave the tie-break and the hosting
        #: suggestion unclaimed, and those are where a lean is cheapest to hide.
        "source_neutral_at": [
            "ranking",
            "tie_breaks",
            "hosting_suggestions",
            "route_advice",
        ],
        "charges": "the consumer of a recommendation, never its subjects",
        "vendor_purchases": VENDOR_PURCHASE_RULE,
        "method_source": (
            "https://github.com/turbobeest/modelspec/blob/main/api/ranking/engine.py"
        ),
        "terms_url": f"{LEGAL_BASE_URL}/terms/",
        "neutrality_url": f"{LEGAL_BASE_URL}/neutrality/",
        "privacy_url": f"{LEGAL_BASE_URL}/privacy/",
    }


def ranking_policy(*, min_benchmark_coverage: float | None = None) -> dict[str, Any]:
    """Policy for one ranking surface. Default is the CLI floor."""
    coverage = MIN_BENCHMARK_COVERAGE if min_benchmark_coverage is None else min_benchmark_coverage
    return {
        "version": "incomplete-evidence-v1",
        "ordering": "conservative_lower_bound",
        "min_benchmark_coverage": coverage,
        "cli_min_benchmark_coverage": MIN_BENCHMARK_COVERAGE,
        "wizard_min_benchmark_coverage": WIZARD_BENCHMARK_COVERAGE,
        "min_benchmark_count": MIN_BENCHMARK_COUNT,
        "limit_applies_to": "ranked_only",
        "uncertainty": "missing-benchmark bounds, not statistical confidence intervals",
        # Additive under the contract's own rule (docs/cli-contract.md: "New
        # fields may be added to any object"). No existing field widens.
        "neutrality": neutrality_commitment(),
        # MODEL-123, additive the same way: the staleness window behind each
        # row's `stale_benchmarks`, and the one Arena snapshot every Arena
        # value in this ranking was normalised against.
        "stale_after_days": STALE_AFTER_DAYS,
        "arena_snapshot": arena_snapshot_policy(),
    }


RANKING_POLICY = ranking_policy()


class IncompleteEvidenceError(ValueError):
    """Optional complete-ordering signal wrapping a rank_report().

    `rank()` returns the ranked shortlist and does not raise when other models
    lack evidence. Callers that require every candidate to be ordered may raise
    this themselves after inspecting rank_report(). `report` preserves both the
    ranked shortlist and every unranked candidate.
    """

    def __init__(self, report: dict[str, Any]):
        self.report = report
        names = []
        for row in report["unranked"]:
            if isinstance(row, dict):
                names.append(f"{row['display_name']} ({row['benchmark_coverage']:.0%} coverage)")
            else:
                names.append(f"{row.display_name} ({row.benchmark_coverage:.0%} coverage)")
        super().__init__(
            "Cannot return a total ordering. Unranked for insufficient evidence: "
            + "; ".join(names)
            + ". These models are not ranked low. Use rank_report() or "
            "`.venv/bin/python -m pipeline.ranking PROFILE` to see ranked and unranked results."
        )


def _on_arena_snapshot(bench_id: str, evidence_dates: dict[str, str] | None) -> bool:
    """True unless `bench_id` is an Arena board and this value is not from its pinned date.

    An Arena value with no date (a flat April score, or a caller that passes no
    dates) is off the snapshot by definition: nothing says which board state it
    was read from, so it cannot be put on that board's scale.
    """
    board = ARENA_SNAPSHOT["boards"].get(bench_id)
    if board is None:
        return True
    return (evidence_dates or {}).get(bench_id) == board["published"]


def _benchmark_evidence(scores: dict[str, float], profile: dict[str, Any],
                       min_coverage: float | None = None,
                       evidence_dates: dict[str, str] | None = None) -> dict[str, Any]:
    """Bound the fixed profile without guessing unmeasured benchmark values.

    All normalized benchmarks lie in [0, 100]. Missing weight therefore spans
    [0, weight * 100], rather than being a measurement of zero. Other composite
    components are held fixed; these are not bounds on real-world ability.

    `evidence_dates` maps a benchmark to the date of the reading in `scores`.
    An Arena value counts only when that date is its board's pinned snapshot
    date (MODEL-123); otherwise it is treated as missing and named in
    `off_snapshot_benchmarks`, so a caller can see why a present score did not
    count.
    """
    weights = profile.get("benchmark_weights", {})
    if any(not math.isfinite(w) or w < 0 for w in weights.values()):
        raise ValueError("Benchmark weights must be finite and nonnegative")
    weights = {b: w for b, w in weights.items() if w > 0}
    # Lists in weight order, never sets: rows are compared byte for byte across
    # processes (tests/test_rank_worker.py), and set order depends on the hash seed.
    measured = [b for b in weights
                if scores.get(b) is not None and math.isfinite(scores[b])]
    off_snapshot = sorted(b for b in measured if not _on_arena_snapshot(b, evidence_dates))
    present = {
        b: _normalize_benchmark(b, scores[b]) for b in measured if b not in off_snapshot
    }
    total_weight = sum(weights.values())
    present_weight = sum(weights[b] for b in present)
    missing = sorted(weights.keys() - present.keys())
    missing_weight = sum(weights[b] for b in missing)
    coverage = present_weight / total_weight if total_weight else 0.0
    required = min(MIN_BENCHMARK_COUNT, len(weights))
    floor = MIN_BENCHMARK_COVERAGE if min_coverage is None else min_coverage
    rankable = (total_weight > 0 and coverage + 1e-12 >= floor
                and len(present) >= required)
    lower = sum(present[b] * weights[b] for b in present) * 0.40
    return {
        "rank_status": "ranked" if rankable else "unranked",
        "unranked_reason": None if rankable else "insufficient_benchmark_evidence",
        "benchmark_coverage": coverage,
        "benchmark_count": len(present),
        "required_benchmark_count": required,
        "missing_benchmarks": missing,
        "benchmark_estimate": lower / (0.40 * present_weight) if present_weight else None,
        "benchmark_lower_bound": lower,
        "benchmark_upper_bound": lower + missing_weight * 40.0,
        "benchmark_contributions": {b: round(present[b] * weights[b], 2) for b in present},
        "off_snapshot_benchmarks": off_snapshot,
    }


def _ranking_status(ranked: list, unranked: list) -> str:
    if unranked:
        return "partial" if ranked else "unavailable"
    return "complete" if ranked else "empty"


CLOUD_PLATFORMS = {
    "aws_bedrock", "azure_ai_foundry", "google_vertex_ai", "nvidia_nim",
    "ibm_watsonx", "snowflake_cortex", "groq", "together_ai", "fireworks_ai",
    "replicate", "deepinfra", "cerebras", "sambanova", "openrouter",
}

PROVIDER_PLATFORMS = {
    "anthropic", "openai", "google", "mistral", "cohere", "xai", "deepseek",
    "claude_ai", "chatgpt", "gemini_app", "grok_xai", "meta_ai",
    "mistral_plateforme", "ai21_labs",
}

LOCAL_PLATFORMS = {
    "ollama", "lm_studio", "gpt4all", "jan_ai", "mlx_community", "open_webui",
}

# Platforms that map to runtime identifiers (used to derive runtimes from graph edges)
RUNTIME_PLATFORMS = {
    "ollama", "lm_studio", "gpt4all",
}


# ═══════════════════════════════════════════════════════════════
# Data classes
# ═══════════════════════════════════════════════════════════════

@dataclass
class ModelData:
    """All data gathered for one model during ranking."""
    model_id: str
    display_name: str
    model_type: str | None = None
    model_subtypes: list[str] = field(default_factory=list)
    status: str | None = None
    open_weights: bool | None = None
    origin_country: str | None = None
    total_parameters: int | None = None
    active_parameters: int | None = None
    context_window: int | None = None
    cost_input: float | None = None
    cost_output: float | None = None
    arena_elo_overall: float | None = None
    release_date: str | None = None
    reasoning: bool = False
    tool_call: bool = False
    vision_input: bool = False
    # Populated from graph edges
    benchmark_scores: dict[str, float] = field(default_factory=dict)
    #: Benchmark -> date of the reading (MODEL-123). The graph's SCORED_ON edges
    #: carry only the flat block, so this is empty on the graph path and no Arena
    #: value counts there; the static export path fills it from evidence.
    evidence_dates: dict[str, str] = field(default_factory=dict)
    capability_tiers: dict[str, str] = field(default_factory=dict)
    available_platforms: set[str] = field(default_factory=set)
    estimated_tps: float | None = None  # Estimated tok/s on target hardware
    concurrent_instances: int | None = None  # How many instances fit on target hardware
    hardware_fits: dict[str, dict] = field(default_factory=dict)
    # Tags and runtimes from the graph
    tags: set[str] = field(default_factory=set)
    runtimes: set[str] = field(default_factory=set)
    # Extra node props for pass-through
    provider: str | None = None


@dataclass
class ScoredModel:
    """Result of scoring a model."""
    model_id: str
    display_name: str
    model_type: str | None
    score: float | None
    benchmark_score: float
    capability_score: float
    cost_score: float
    context_score: float
    type_bonus: float
    speed_score: float = 0.0
    estimated_tps: float | None = None
    concurrent_instances: int | None = None
    reasons: list[str] = field(default_factory=list)
    benchmark_contributions: dict[str, float] = field(default_factory=dict)
    # Pass-through for the response
    arena_elo_overall: float | None = None
    total_parameters: int | None = None
    context_window: int | None = None
    cost_input: float | None = None
    cost_output: float | None = None
    open_weights: bool | None = None
    provider: str | None = None
    status: str | None = None
    rank: int | None = None
    rank_status: str = "unranked"
    unranked_reason: str | None = None
    benchmark_coverage: float = 0.0
    benchmark_count: int = 0
    required_benchmark_count: int = 0
    missing_benchmarks: list[str] = field(default_factory=list)
    benchmark_estimate: float | None = None
    benchmark_lower_bound: float = 0.0
    benchmark_upper_bound: float = 0.0
    score_lower_bound: float = 0.0
    score_upper_bound: float = 0.0
    off_snapshot_benchmarks: list[str] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════
# Ranking Engine
# ═══════════════════════════════════════════════════════════════

class RankingEngine:
    """4-stage ranking pipeline: Filter -> Score -> Rank -> Explain."""

    def __init__(self, graph):
        self.graph = graph

    # ─── Main entry point ────────────────────────────────────

    def rank(
        self,
        use_case: str | None = None,
        hardware: str | None = None,
        constraints: dict[str, Any] | None = None,
        limit: int = 10,
    ) -> list[ScoredModel]:
        """Return the models that can honestly be ordered for this profile.

        Unrankable models are the normal catalogue state, not an error. This
        returns the ranked shortlist, which may be empty when nothing has
        enough evidence. Use rank_report() to see withheld models and
        ranking_status.
        """
        return self.rank_report(use_case, hardware, constraints, limit)["ranked"]

    def rank_report(
        self,
        use_case: str | None = None,
        hardware: str | None = None,
        constraints: dict[str, Any] | None = None,
        limit: int = 10,
    ) -> dict[str, Any]:
        """Return a bounded shortlist and all unranked candidates separately."""
        if limit < 0:
            raise ValueError("limit must be nonnegative")
        constraints = constraints or {}
        profile = USE_CASE_PROFILES.get(use_case or "general", USE_CASE_PROFILES["general"])

        # Stage 0: Fetch all candidate models from the graph
        candidates = self._fetch_candidates(hardware, constraints)
        logger.info(f"Fetched {len(candidates)} candidates from graph")

        # Stage 1: Filter
        filtered = self._filter(candidates, constraints, profile)
        logger.info(f"After filtering: {len(filtered)} models remain")

        # Stage 2: Score
        scored = [self._score(m, profile) for m in filtered]

        # Stage 3: Rank (sort by score, tie-break by ELO then params)
        ranked = [s for s in scored if s.rank_status == "ranked"]
        unranked = [s for s in scored if s.rank_status == "unranked"]
        ranked.sort(key=lambda s: (
            s.score,
            s.arena_elo_overall or 0,
            s.total_parameters or 0,
        ), reverse=True)
        unranked.sort(key=lambda s: (s.display_name.lower(), s.model_id))
        for position, result in enumerate(ranked, 1):
            result.rank = position

        # Stage 4: Explain (already built into scoring, but add rank-relative info)
        self._explain(scored, profile, use_case)

        return {
            "ranking_status": _ranking_status(ranked, unranked),
            "policy": dict(RANKING_POLICY),
            "ranked_count": len(ranked), "unranked_count": len(unranked),
            "ranked": ranked[:limit], "unranked": unranked,
        }

    # ─── Stage 0: Fetch candidates ───────────────────────────

    def _fetch_candidates(
        self,
        hardware: str | None,
        constraints: dict[str, Any],
    ) -> list[ModelData]:
        """Query FalkorDB for all model nodes with their edges."""
        # Build the base query with optional hardware join
        if hardware:
            base_q = (
                "MATCH (m:Model)-[fit:FITS_ON]->(h:Hardware {id: $hw_id}) "
                "RETURN m"
            )
            params: dict[str, Any] = {"hw_id": hardware}
        else:
            base_q = "MATCH (m:Model) RETURN m"
            params = {}

        result = self.graph.query(base_q, params)
        model_ids: list[str] = []
        models_by_id: dict[str, ModelData] = {}

        for row in result.result_set:
            node = row[0]
            props = dict(node.properties) if node.properties else {}
            mid = props.get("id", "")
            if not mid:
                continue

            md = ModelData(
                model_id=mid,
                display_name=props.get("display_name", mid),
                model_type=props.get("model_type"),
                status=props.get("status"),
                open_weights=props.get("open_weights"),
                origin_country=props.get("origin_country") or None,
                total_parameters=_safe_int(props.get("total_parameters")),
                active_parameters=_safe_int(props.get("active_parameters")),
                context_window=_safe_int(props.get("context_window")),
                cost_input=_safe_float(props.get("cost_input")),
                cost_output=_safe_float(props.get("cost_output")),
                arena_elo_overall=_safe_float(props.get("arena_elo_overall")),
                release_date=props.get("release_date"),
                reasoning=bool(props.get("reasoning")),
                tool_call=bool(props.get("tool_call")),
                vision_input=bool(props.get("vision_input")),
                provider=mid.split("/")[0] if "/" in mid else None,
                model_subtypes=props.get("model_subtypes", "").split(",") if props.get("model_subtypes") else [],
            )
            models_by_id[mid] = md
            model_ids.append(mid)

        if not model_ids:
            return []

        # Batch-fetch benchmark scores via SCORED_ON edges
        bench_q = (
            "MATCH (m:Model)-[e:SCORED_ON]->(b:Benchmark) "
            "RETURN m.id, b.id, e.value"
        )
        bench_result = self.graph.query(bench_q)
        for row in bench_result.result_set:
            mid, bench_id, value = row
            if mid in models_by_id and value is not None:
                models_by_id[mid].benchmark_scores[bench_id] = float(value)

        # Batch-fetch capability tiers via HAS_CAPABILITY edges
        cap_q = (
            "MATCH (m:Model)-[e:HAS_CAPABILITY]->(c:Capability) "
            "RETURN m.id, c.id, e.tier"
        )
        cap_result = self.graph.query(cap_q)
        for row in cap_result.result_set:
            mid, cap_id, tier = row
            if mid in models_by_id and tier:
                # Keep the best tier if multiple edges exist
                existing = models_by_id[mid].capability_tiers.get(cap_id)
                if existing is None or _tier_rank(tier) < _tier_rank(existing):
                    models_by_id[mid].capability_tiers[cap_id] = tier

        # Batch-fetch platform availability via AVAILABLE_ON edges
        plat_q = (
            "MATCH (m:Model)-[:AVAILABLE_ON]->(p:Platform) "
            "RETURN m.id, p.id"
        )
        plat_result = self.graph.query(plat_q)
        for row in plat_result.result_set:
            mid, plat_id = row
            if mid in models_by_id and plat_id:
                models_by_id[mid].available_platforms.add(plat_id)
                # Derive runtime info from platform availability
                if plat_id in RUNTIME_PLATFORMS:
                    models_by_id[mid].runtimes.add(plat_id)

        # Batch-fetch tags via TAGGED_WITH edges
        tag_q = (
            "MATCH (m:Model)-[:TAGGED_WITH]->(t:Tag) "
            "RETURN m.id, t.id"
        )
        tag_result = self.graph.query(tag_q)
        for row in tag_result.result_set:
            mid, tag_id = row
            if mid in models_by_id and tag_id:
                models_by_id[mid].tags.add(tag_id)

        return list(models_by_id.values())

    # ─── Stage 1: Filter ─────────────────────────────────────

    def _filter(
        self,
        candidates: list[ModelData],
        constraints: dict[str, Any],
        profile: dict[str, Any],
    ) -> list[ModelData]:
        """Eliminate models that fail hard constraints."""
        result = []

        model_type_filter = constraints.get("model_type")
        open_weights_req = constraints.get("open_weights")
        max_cost = _safe_float(constraints.get("max_cost_input"))
        min_context = _safe_int(constraints.get("min_context"))
        min_params = _safe_int(constraints.get("min_params"))
        max_params = _safe_int(constraints.get("max_params"))
        origin_whitelist = constraints.get("origin_countries")  # list of country codes
        origin_blacklist = constraints.get("origin_blacklist")  # list of country codes
        require_reasoning = constraints.get("reasoning")
        require_tools = constraints.get("tool_use")
        require_vision = constraints.get("vision")
        provider_filter = constraints.get("provider")
        hw_memory_gb = _safe_float(constraints.get("hw_memory_gb"))
        hw_bandwidth_gbps = _safe_float(constraints.get("hw_bandwidth_gbps"))
        hw_quant = constraints.get("hw_quant", "")
        hw_tops = _safe_float(constraints.get("hw_tops"))

        for m in candidates:
            # Skip deprecated/sunset unless explicitly requested
            if m.status in ("deprecated", "sunset"):
                continue

            # Model type filter
            if model_type_filter:
                if m.model_type != model_type_filter:
                    continue

            # Open weights requirement
            if open_weights_req is True:
                if m.open_weights is not True:
                    continue

            # Max cost threshold
            if max_cost is not None and m.cost_input is not None:
                if m.cost_input > max_cost:
                    continue

            # Min context window
            if min_context is not None and m.context_window is not None:
                if m.context_window < min_context:
                    continue

            # Parameter bounds
            if min_params is not None and m.total_parameters is not None:
                if m.total_parameters < min_params:
                    continue
            if max_params is not None and m.total_parameters is not None:
                if m.total_parameters > max_params:
                    continue

            # Origin country whitelist — exclude models with unknown origin too
            if origin_whitelist:
                if not m.origin_country or m.origin_country not in origin_whitelist:
                    continue

            # Origin country blacklist
            if origin_blacklist and m.origin_country:
                if m.origin_country in origin_blacklist:
                    continue

            # Capability requirements
            if require_reasoning and not m.reasoning:
                continue
            if require_tools and not m.tool_call:
                continue
            if require_vision and not m.vision_input:
                continue

            # Provider filter
            if provider_filter and m.provider != provider_filter:
                continue

            # Hosting mode filter
            hosting_modes = constraints.get("hosting")  # list: ["local", "cloud", "provider"]
            if hosting_modes:
                passes_hosting = False
                for mode in hosting_modes:
                    if mode == "local":
                        # Must be open-weights to run locally
                        if m.open_weights:
                            passes_hosting = True
                    elif mode == "cloud":
                        # Check if available on any cloud/inference platform
                        if m.available_platforms & CLOUD_PLATFORMS:
                            passes_hosting = True
                        elif m.open_weights:
                            # Open-weight models can always be deployed to cloud
                            passes_hosting = True
                    elif mode == "provider":
                        # Check if available via provider's own API
                        if m.available_platforms & PROVIDER_PLATFORMS:
                            passes_hosting = True
                        elif not m.open_weights:
                            # API-only models are always provider-hosted
                            passes_hosting = True
                if not passes_hosting:
                    continue

            # Specific platform filter
            required_platforms = constraints.get("platforms")  # list of platform IDs
            if required_platforms:
                if not m.available_platforms & set(required_platforms):
                    # Also check by provider slug for provider platforms
                    provider_match = m.provider in required_platforms
                    if not provider_match:
                        continue

            # Runtime filter — require model to support specific runtimes
            required_runtimes = constraints.get("runtime")  # list of runtime IDs
            if required_runtimes:
                # Check explicit runtime platforms
                model_runtimes = m.runtimes | (m.available_platforms & {
                    "ollama", "lm_studio", "gpt4all", "vllm", "mlx",
                    "llama_cpp", "transformers",
                })
                # Infer runtime compatibility for open-weights models:
                # If on HuggingFace or open-weights, they can run on vllm/transformers/llama_cpp
                if m.open_weights:
                    model_runtimes |= {"vllm", "transformers", "llama_cpp"}
                    if m.available_platforms & {"ollama", "lm_studio", "gpt4all"}:
                        model_runtimes |= {"ollama", "lm_studio", "gpt4all"}
                if not model_runtimes & set(required_runtimes):
                    continue

            # OpenAI SDK compatibility filter — require "openai-compatible" tag
            if constraints.get("openai_compatible"):
                if "openai-compatible" not in m.tags:
                    continue

            # Hardware fit check — estimate if model fits and how fast it would run
            if hw_memory_gb and hw_memory_gb > 0:
                bytes_per_param = {"Q2": 0.25, "Q4": 0.5, "Q8": 1.0, "FP16": 2.0}.get(hw_quant, 0.5)
                usable_mem = hw_memory_gb * 0.85  # reserve 15% for OS/KV cache

                if m.total_parameters:
                    model_mem_gb = m.total_parameters * bytes_per_param / 1e9
                    # Hard filter: won't fit in memory
                    if model_mem_gb > usable_mem:
                        continue
                    # Concurrent instances that fit
                    m.concurrent_instances = max(1, int(usable_mem / model_mem_gb))
                    # Estimate tokens/sec from memory bandwidth
                    # tok/s ≈ bandwidth / model_memory (memory-bandwidth-bound)
                    if hw_bandwidth_gbps and hw_bandwidth_gbps > 0:
                        est_tps = hw_bandwidth_gbps / model_mem_gb
                        m.estimated_tps = round(est_tps, 1)
                        # Filter out unusably slow models (< 1 tok/s)
                        if est_tps < 1.0:
                            continue
                else:
                    # No parameter data — use heuristic: API-only models are fine,
                    # but for local hosting, unknown-size models on small hardware are risky
                    if hw_memory_gb <= 24 and m.open_weights:
                        # Small device + open weights + unknown size = skip
                        # (likely too big for an RPi or MacBook Air)
                        continue

            result.append(m)

        return result

    # ─── Stage 2: Score ──────────────────────────────────────

    def _score(self, model: ModelData, profile: dict[str, Any]) -> ScoredModel:
        """Compute weighted composite score for a model against a profile."""

        # --- Benchmark scoring (up to 40 points) ---
        evidence = _benchmark_evidence(model.benchmark_scores, profile,
                                       evidence_dates=model.evidence_dates)
        bench_score_scaled = evidence["benchmark_lower_bound"]

        # --- Capability scoring (up to 20 points) ---
        cap_weights = profile.get("capability_weights", {})
        cap_score = 0.0
        total_cap_weight = sum(cap_weights.values()) if cap_weights else 1.0

        for cap_name, weight in cap_weights.items():
            # Look for the main capability tier (e.g., "coding", "reasoning")
            tier = model.capability_tiers.get(cap_name)
            if tier:
                tier_pts = _tier_points(tier)
                cap_score += tier_pts * (weight / total_cap_weight)
            else:
                # Check for sub-capabilities (e.g., "coding:debugging")
                sub_tiers = [
                    t for cid, t in model.capability_tiers.items()
                    if cid.startswith(f"{cap_name}:")
                ]
                if sub_tiers:
                    # Average the sub-capability tiers
                    best_tier = min(sub_tiers, key=_tier_rank)
                    tier_pts = _tier_points(best_tier) * 0.7  # Discount vs explicit overall
                    cap_score += tier_pts * (weight / total_cap_weight)

        cap_score_scaled = cap_score * 2.0  # Scale to max ~20 points

        # --- Cost efficiency scoring (up to profile's cost_weight * 100 points) ---
        cost_weight = profile.get("cost_weight", 0.10)
        cost_score = 0.0
        if model.cost_input is not None:
            if model.cost_input == 0:
                cost_score = 10.0  # Free is the best
            else:
                # Log scale with floor at $0.10 to keep free always on top.
                # $0.10 -> ~9pts, $1 -> ~7pts, $5 -> ~5.6pts, $15 -> ~4.6pts
                clamped = max(model.cost_input, 0.10)
                cost_score = max(0.0, min(9.5, 9.0 + 2.0 * math.log10(0.10 / clamped)))
        cost_score_scaled = cost_score * cost_weight * 10  # Up to ~10 points

        # --- Context window scoring (log-scaled, up to profile weight) ---
        ctx_weight = profile.get("context_weight", 0.10)
        ctx_score = 0.0
        if model.context_window and model.context_window > 0:
            # log10(4K)=3.6, log10(32K)=4.5, log10(128K)=5.1, log10(1M)=6.0, log10(10M)=7.0
            ctx_score = min(10.0, max(0, (math.log10(model.context_window) - 3.5) * 3.0))
        ctx_score_scaled = ctx_score * ctx_weight * 10  # Up to ~10 points

        # --- Type match bonus (up to 15 points) ---
        # Check primary type AND subtypes against preferred types
        preferred = profile.get("preferred_types", [])
        type_bonus = 0.0
        if model.model_type:
            # Collect all types this model claims (primary + subtypes)
            all_types = [model.model_type] + list(model.model_subtypes)
            best_idx = None
            for t in all_types:
                if t in preferred:
                    idx = preferred.index(t)
                    if best_idx is None or idx < best_idx:
                        best_idx = idx
            if best_idx is not None:
                # First preferred type gets full bonus, descending
                type_bonus = max(5.0, 15.0 - best_idx * 3.0)

        # --- Speed bonus (up to 10 points, only when hardware specified) ---
        speed_score = 0.0
        if model.estimated_tps is not None:
            # Log-scale: 1 tok/s = 0, 10 tok/s = 5, 100 tok/s = 10
            speed_score = min(10.0, max(0.0, math.log10(max(1.0, model.estimated_tps)) * 5.0))

        # --- Composite score (0-100 scale) ---
        raw_total = (
            bench_score_scaled
            + cap_score_scaled
            + cost_score_scaled
            + ctx_score_scaled
            + type_bonus
            + speed_score
        )
        # Clamp to 0-100
        final_score = max(0.0, min(100.0, raw_total))
        upper_score = max(0.0, min(100.0, raw_total
                          + evidence["benchmark_upper_bound"] - bench_score_scaled))

        return ScoredModel(
            model_id=model.model_id,
            display_name=model.display_name,
            model_type=model.model_type,
            score=round(final_score, 2) if evidence["rank_status"] == "ranked" else None,
            score_lower_bound=round(final_score, 2),
            score_upper_bound=round(upper_score, 2),
            benchmark_score=round(bench_score_scaled, 2),
            capability_score=round(cap_score_scaled, 2),
            cost_score=round(cost_score_scaled, 2),
            context_score=round(ctx_score_scaled, 2),
            type_bonus=round(type_bonus, 2),
            speed_score=round(speed_score, 2),
            estimated_tps=model.estimated_tps,
            concurrent_instances=model.concurrent_instances,
            **evidence,
            arena_elo_overall=model.arena_elo_overall,
            total_parameters=model.total_parameters,
            context_window=model.context_window,
            cost_input=model.cost_input,
            cost_output=model.cost_output,
            open_weights=model.open_weights,
            provider=model.provider,
            status=model.status,
        )

    # ─── Stage 4: Explain ────────────────────────────────────

    def _explain(
        self,
        scored: list[ScoredModel],
        profile: dict[str, Any],
        use_case: str | None,
    ) -> None:
        """Generate human-readable reasons for each model's ranking. Mutates in place."""
        if not scored:
            return

        for sm in scored:
            reasons = [
                f"Benchmark coverage: {sm.benchmark_coverage:.0%}; "
                f"composite bounds {sm.score_lower_bound:.2f}–{sm.score_upper_bound:.2f} "
                "(missing benchmarks, not statistical confidence)."
            ]
            if sm.rank_status == "unranked":
                sm.reasons = ["Unranked for insufficient benchmark evidence; not ranked low.", *reasons]
                continue
            reasons.append("Ordered by conservative lower bound, not an estimate of ability.")

            # Benchmark highlights
            if sm.benchmark_contributions:
                # Find top contributing benchmarks
                sorted_benches = sorted(
                    sm.benchmark_contributions.items(),
                    key=lambda x: x[1],
                    reverse=True,
                )
                for bench_id, contrib in sorted_benches[:3]:
                    if contrib > 0.5:
                        nice_name = bench_id.replace("_", " ").title()
                        reasons.append(f"Strong {nice_name} performance")

            # Type match
            if sm.type_bonus >= 12:
                reasons.append(f"Ideal model type for {use_case or 'general'}")
            elif sm.type_bonus >= 5:
                reasons.append(f"Good model type match")

            # Capability highlights
            if sm.capability_score >= 15:
                reasons.append("Top-tier capabilities")
            elif sm.capability_score >= 8:
                reasons.append("Strong capabilities")

            # Cost efficiency
            if sm.cost_score >= 8:
                if sm.cost_input == 0:
                    reasons.append("Free tier available")
                else:
                    reasons.append("Excellent cost efficiency")
            elif sm.cost_score >= 4:
                reasons.append("Good cost/quality ratio")

            # Context window
            if sm.context_window:
                if sm.context_window >= 1_000_000:
                    reasons.append(f"{sm.context_window // 1_000_000}M token context")
                elif sm.context_window >= 128_000:
                    reasons.append(f"{sm.context_window // 1000}K token context")

            # Arena ELO
            if sm.arena_elo_overall and sm.arena_elo_overall >= 1300:
                reasons.append(f"Arena ELO: {int(sm.arena_elo_overall)}")

            # Speed estimate
            if sm.estimated_tps is not None:
                if sm.estimated_tps >= 50:
                    reasons.append(f"~{sm.estimated_tps:.0f} tok/s (fast)")
                elif sm.estimated_tps >= 10:
                    reasons.append(f"~{sm.estimated_tps:.0f} tok/s")
                elif sm.estimated_tps >= 1:
                    reasons.append(f"~{sm.estimated_tps:.1f} tok/s (slow)")

            # Open weights
            if sm.open_weights:
                reasons.append("Open weights")

            # If no reasons generated, add a generic one
            if not reasons:
                if sm.score > 0:
                    reasons.append("Matches basic criteria")
                else:
                    reasons.append("Limited data available")

            sm.reasons = reasons


# ═══════════════════════════════════════════════════════════════
# Helper functions
# ═══════════════════════════════════════════════════════════════

def _normalize_benchmark(bench_id: str, raw_value: float) -> float:
    """Normalize a benchmark score to 0-100, higher always meaning better.

    Direction is explicit rather than assumed. A lower-is-better metric such as
    word error rate is inverted here, so that the rest of the pipeline can treat
    every normalised score the same way.
    """
    if bench_id in ARENA_SNAPSHOT["boards"]:
        return _normalize_arena(bench_id, raw_value)
    range_info = BENCHMARK_RANGES.get(bench_id)
    if range_info is None:
        # Unknown benchmark: assume a 0-100 scale. This is a guess, and it is
        # wrong for any lower-is-better metric — add the benchmark to
        # BENCHMARK_RANGES and BENCHMARK_DIRECTIONS rather than relying on it.
        return max(0.0, min(100.0, raw_value))

    low, high = range_info
    if high <= low:
        return 50.0  # Degenerate range
    normalized = ((raw_value - low) / (high - low)) * 100.0
    if BENCHMARK_DIRECTIONS.get(bench_id) == "lower_is_better":
        normalized = 100.0 - normalized
    return max(0.0, min(100.0, normalized))


def _tier_points(tier: str) -> float:
    """Convert a tier string to point value."""
    return {
        "tier-1": 10.0,
        "tier-2": 6.0,
        "tier-3": 3.0,
        "n/a": 0.0,
    }.get(tier, 0.0)


def _tier_rank(tier: str) -> int:
    """Numeric rank for tier comparison (lower = better)."""
    return {
        "tier-1": 1,
        "tier-2": 2,
        "tier-3": 3,
        "n/a": 99,
    }.get(tier, 50)


def _safe_int(val) -> int | None:
    if val is None:
        return None
    try:
        return int(val)
    except (ValueError, TypeError):
        return None


def _safe_float(val) -> float | None:
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None
