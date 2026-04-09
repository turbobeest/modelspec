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
# For ELO-based scores, the range is wider; for percentage-based, it's 0-100.

BENCHMARK_RANGES: dict[str, tuple[float, float]] = {
    # Knowledge & Reasoning (percentage-based, 0-100)
    "mmlu_pro":         (20.0, 90.0),
    "gpqa_diamond":     (20.0, 80.0),
    "hle":              (0.0, 50.0),
    "arc_challenge":    (40.0, 100.0),
    "hellaswag":        (40.0, 100.0),
    "truthfulqa":       (20.0, 90.0),
    "bbh":              (20.0, 95.0),
    "ifeval":           (20.0, 95.0),
    "musr":             (10.0, 80.0),
    "winogrande":       (50.0, 100.0),
    # Math
    "math_500":         (10.0, 100.0),
    "aime_2025":        (0.0, 80.0),
    "aime_2026":        (0.0, 80.0),
    "gsm8k":            (20.0, 100.0),
    "mgsm":             (10.0, 100.0),
    # Coding
    "humaneval":        (10.0, 100.0),
    "humaneval_plus":   (10.0, 100.0),
    "swe_bench_verified": (0.0, 70.0),
    "live_code_bench":  (0.0, 60.0),
    "aider_polyglot":   (0.0, 90.0),
    "terminal_bench":   (0.0, 80.0),
    "mbpp":             (20.0, 100.0),
    "multipl_e":        (10.0, 100.0),
    # Multimodal
    "mmmu":             (20.0, 80.0),
    "mathvista":        (20.0, 80.0),
    "docvqa":           (40.0, 100.0),
    "chartqa":          (40.0, 100.0),
    # Safety
    "helm_safety":      (30.0, 100.0),
    "bbq":              (30.0, 100.0),
    "toxigen":          (30.0, 100.0),
    # Human preference (ELO-based: typical range 900-1400)
    "arena_elo_overall":       (1000.0, 1400.0),
    "arena_elo_coding":        (1000.0, 1400.0),
    "arena_elo_math":          (1000.0, 1400.0),
    "arena_elo_vision":        (1000.0, 1400.0),
    "arena_elo_hard_prompts":  (1000.0, 1400.0),
    "arena_elo_style_control": (1000.0, 1400.0),
    "mt_bench":         (5.0, 10.0),
    "alpaca_eval":      (0.0, 60.0),
    "wildbench":        (-100.0, 100.0),
    # Embedding (percentage or ratio-based)
    "mteb_overall":       (30.0, 80.0),
    "mteb_retrieval":     (20.0, 70.0),
    "mteb_classification": (40.0, 90.0),
    "mteb_clustering":    (20.0, 60.0),
    "mteb_reranking":     (20.0, 70.0),
    "mteb_sts":           (40.0, 90.0),
    "mteb_pair_classification": (50.0, 95.0),
    "mteb_summarization": (20.0, 50.0),
    "beir":               (20.0, 70.0),
    "miracl":             (10.0, 70.0),
    # Agentic
    "swe_bench_agent":  (0.0, 60.0),
    "swe_bench_pro":    (0.0, 80.0),
    "swe_bench_multilingual": (0.0, 90.0),
    "swe_bench_multimodal":   (0.0, 60.0),
    "tau_bench":        (0.0, 80.0),
    "web_arena":        (0.0, 50.0),
    "osworld":          (0.0, 80.0),
    # Agentic search
    "browsecomp":       (0.0, 90.0),
    "hle":              (0.0, 65.0),
    "hle_tools":        (0.0, 70.0),
    # Multimodal (advanced)
    "charxiv_reasoning":       (20.0, 95.0),
    "charxiv_reasoning_tools": (20.0, 95.0),
    "lab_bench_figqa":         (20.0, 90.0),
    "lab_bench_figqa_tools":   (20.0, 90.0),
    "screenspot_pro":          (10.0, 95.0),
    "screenspot_pro_tools":    (10.0, 95.0),
    # Long context
    "graphwalks_bfs_256k_1m":     (0.0, 85.0),
    "graphwalks_parents_256k_1m": (0.0, 100.0),
    # Math (competition)
    "usamo_2026":       (0.0, 100.0),
    "ipho_2025_theory": (0.0, 100.0),
    # Agentic research
    "deepsearchqa":             (0.0, 80.0),
    "frontierscience_research": (0.0, 50.0),
    # Health / Medical (advanced)
    "healthbench_hard":         (0.0, 50.0),
    "medxpertqa_multimodal":    (20.0, 85.0),
    # Visual reasoning
    "zerobench":        (0.0, 50.0),
    "ai2d":             (40.0, 100.0),
    "ocrbench":         (0.0, 100.0),
    "realworldqa":      (30.0, 90.0),
    # AGI benchmarks
    "arc_agi_2":        (0.0, 80.0),
    # Multilingual knowledge
    "mmmlu":            (40.0, 95.0),
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
    "terminal_bench_2":     (0.0, 80.0),
    # MMLU subject scores (percentage-based, 0-100)
    # All 57 MMLU (hendrycksTest) subjects from the evaluation harness
    "mmlu_abstract_algebra":                    (20.0, 75.0),
    "mmlu_anatomy":                             (20.0, 90.0),
    "mmlu_astronomy":                           (20.0, 95.0),
    "mmlu_business_ethics":                     (20.0, 90.0),
    "mmlu_clinical_knowledge":                  (20.0, 95.0),
    "mmlu_college_biology":                     (20.0, 95.0),
    "mmlu_college_chemistry":                   (20.0, 80.0),
    "mmlu_college_computer_science":            (20.0, 95.0),
    "mmlu_college_mathematics":                 (20.0, 80.0),
    "mmlu_college_medicine":                    (20.0, 90.0),
    "mmlu_college_physics":                     (20.0, 80.0),
    "mmlu_computer_security":                   (20.0, 95.0),
    "mmlu_conceptual_physics":                  (20.0, 95.0),
    "mmlu_econometrics":                        (20.0, 85.0),
    "mmlu_electrical_engineering":              (20.0, 90.0),
    "mmlu_elementary_mathematics":              (20.0, 90.0),
    "mmlu_formal_logic":                        (20.0, 80.0),
    "mmlu_global_facts":                        (20.0, 75.0),
    "mmlu_high_school_biology":                 (20.0, 95.0),
    "mmlu_high_school_chemistry":               (20.0, 90.0),
    "mmlu_high_school_computer_science":        (20.0, 95.0),
    "mmlu_high_school_european_history":        (20.0, 95.0),
    "mmlu_high_school_geography":               (20.0, 95.0),
    "mmlu_high_school_government_and_politics": (20.0, 100.0),
    "mmlu_high_school_macroeconomics":          (20.0, 95.0),
    "mmlu_high_school_mathematics":             (20.0, 80.0),
    "mmlu_high_school_microeconomics":          (20.0, 95.0),
    "mmlu_high_school_physics":                 (20.0, 85.0),
    "mmlu_high_school_psychology":              (20.0, 98.0),
    "mmlu_high_school_statistics":              (20.0, 90.0),
    "mmlu_high_school_us_history":              (20.0, 95.0),
    "mmlu_high_school_world_history":           (20.0, 95.0),
    "mmlu_human_aging":                         (20.0, 90.0),
    "mmlu_human_sexuality":                     (20.0, 95.0),
    "mmlu_international_law":                   (20.0, 95.0),
    "mmlu_jurisprudence":                       (20.0, 90.0),
    "mmlu_logical_fallacies":                   (20.0, 95.0),
    "mmlu_machine_learning":                    (20.0, 85.0),
    "mmlu_management":                          (20.0, 95.0),
    "mmlu_marketing":                           (20.0, 95.0),
    "mmlu_medical_genetics":                    (20.0, 95.0),
    "mmlu_miscellaneous":                       (20.0, 95.0),
    "mmlu_moral_disputes":                      (20.0, 90.0),
    "mmlu_moral_scenarios":                     (20.0, 85.0),
    "mmlu_nutrition":                           (20.0, 95.0),
    "mmlu_philosophy":                          (20.0, 90.0),
    "mmlu_prehistory":                          (20.0, 95.0),
    "mmlu_professional_accounting":             (20.0, 85.0),
    "mmlu_professional_law":                    (20.0, 90.0),
    "mmlu_professional_medicine":               (20.0, 95.0),
    "mmlu_professional_psychology":             (20.0, 95.0),
    "mmlu_public_relations":                    (20.0, 90.0),
    "mmlu_security_studies":                    (20.0, 90.0),
    "mmlu_sociology":                           (20.0, 95.0),
    "mmlu_us_foreign_policy":                   (20.0, 95.0),
    "mmlu_virology":                            (20.0, 80.0),
    "mmlu_world_religions":                     (20.0, 95.0),
    # Legacy aliases (mapped to new names for backward compatibility)
    "mmlu_chemistry":               (20.0, 95.0),
    "mmlu_physics":                 (20.0, 95.0),
    "mmlu_biology":                 (20.0, 95.0),
    "mmlu_computer_science":        (20.0, 95.0),
    # Domain-specific extras
    "pubmedqa":     (30.0, 90.0),
    "medmcqa":      (20.0, 80.0),
    "bioasq":       (20.0, 80.0),
    "finqa":        (20.0, 90.0),
    "convfinqa":    (20.0, 80.0),
    "fpb":          (20.0, 90.0),
    # Translation
    "flores":       (10.0, 70.0),
    "flores_en_zh": (10.0, 50.0),
    "flores_en_de": (10.0, 50.0),
    "flores_en_fr": (10.0, 50.0),
    "flores_en_es": (10.0, 50.0),
    "flores_en_ja": (10.0, 50.0),
    "flores_en_ko": (10.0, 50.0),
}


# ═══════════════════════════════════════════════════════════════
# Use case profiles
# ═══════════════════════════════════════════════════════════════

USE_CASE_PROFILES: dict[str, dict[str, Any]] = {
    "coding": {
        "preferred_types": ["llm-code", "llm-chat", "llm-reasoning", "vlm"],
        "benchmark_weights": {
            "humaneval": 0.20, "swe_bench_verified": 0.20, "live_code_bench": 0.15,
            "aider_polyglot": 0.15, "arena_elo_coding": 0.15, "arena_elo_overall": 0.10,
            "terminal_bench": 0.05,
        },
        "capability_weights": {
            "coding": 0.30, "reasoning": 0.20, "tool_use": 0.15,
        },
        "cost_weight": 0.0,
        "context_weight": 0.10,
    },
    "reasoning": {
        "preferred_types": ["llm-reasoning", "llm-chat"],
        "benchmark_weights": {
            "gpqa_diamond": 0.20, "math_500": 0.20, "aime_2025": 0.15,
            "mmlu_pro": 0.15, "arena_elo_overall": 0.15, "bbh": 0.10,
            "ifeval": 0.05,
        },
        "capability_weights": {
            "reasoning": 0.35, "coding": 0.15, "tool_use": 0.10,
        },
        "cost_weight": 0.0,
        "context_weight": 0.10,
    },
    "chat": {
        "preferred_types": ["llm-chat", "vlm", "llm-reasoning"],
        "benchmark_weights": {
            "arena_elo_overall": 0.30, "mt_bench": 0.15, "alpaca_eval": 0.15,
            "ifeval": 0.15, "mmlu_pro": 0.10, "arena_elo_style_control": 0.10,
            "wildbench": 0.05,
        },
        "capability_weights": {
            "creative": 0.20, "language": 0.20, "reasoning": 0.15, "tool_use": 0.10,
        },
        "cost_weight": 0.0,
        "context_weight": 0.10,
    },
    "embedding": {
        "preferred_types": ["embedding-text", "embedding-multimodal"],
        "benchmark_weights": {
            "mteb_overall": 0.30, "mteb_retrieval": 0.25, "mteb_classification": 0.15,
            "beir": 0.15, "miracl": 0.10, "mteb_clustering": 0.05,
        },
        "capability_weights": {},
        "cost_weight": 0.0,
        "context_weight": 0.05,
    },
    "vision": {
        "preferred_types": ["vlm", "llm-chat"],
        "benchmark_weights": {
            "mmmu": 0.25, "mathvista": 0.20, "docvqa": 0.15, "chartqa": 0.15,
            "arena_elo_vision": 0.15, "arena_elo_overall": 0.10,
        },
        "capability_weights": {
            "reasoning": 0.15, "creative": 0.10,
        },
        "cost_weight": 0.0,
        "context_weight": 0.10,
    },
    "agentic": {
        "preferred_types": ["llm-reasoning", "llm-code", "llm-chat"],
        "benchmark_weights": {
            "swe_bench_agent": 0.20, "tau_bench": 0.15, "web_arena": 0.15,
            "swe_bench_verified": 0.15, "arena_elo_overall": 0.15,
            "terminal_bench": 0.10, "ifeval": 0.10,
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
            "mteb_retrieval": 0.25, "beir": 0.20, "mteb_overall": 0.15,
            "arena_elo_overall": 0.15, "ifeval": 0.10, "mmlu_pro": 0.10,
            "miracl": 0.05,
        },
        "capability_weights": {
            "language": 0.15, "reasoning": 0.10,
        },
        "cost_weight": 0.0,
        "context_weight": 0.15,
    },
    "safety": {
        "preferred_types": ["safety-classifier", "reward-model"],
        "benchmark_weights": {
            "helm_safety": 0.30, "bbq": 0.25, "toxigen": 0.25,
            "arena_elo_overall": 0.20,
        },
        "capability_weights": {},
        "cost_weight": 0.0,
        "context_weight": 0.05,
    },
    "general": {
        "preferred_types": ["llm-chat", "llm-reasoning", "vlm"],
        "benchmark_weights": {
            "arena_elo_overall": 0.25, "mmlu_pro": 0.15, "gpqa_diamond": 0.10,
            "humaneval": 0.10, "math_500": 0.10, "ifeval": 0.10,
            "mt_bench": 0.10, "swe_bench_verified": 0.10,
        },
        "capability_weights": {
            "reasoning": 0.15, "coding": 0.15, "tool_use": 0.10, "creative": 0.10,
        },
        "cost_weight": 0.0,
        "context_weight": 0.10,
    },

    # ─── Sub-domain: Coding by language ───────────────────────
    "coding_python": {
        "preferred_types": ["llm-code", "llm-chat", "llm-reasoning", "vlm"],
        "benchmark_weights": {
            "multipl_e_python": 0.30, "humaneval": 0.15, "swe_bench_verified": 0.15,
            "aider_polyglot": 0.15, "arena_elo_coding": 0.10, "multipl_e": 0.10,
            "arena_elo_overall": 0.05,
        },
        "capability_weights": {
            "coding": 0.30, "reasoning": 0.20, "tool_use": 0.15,
        },
        "cost_weight": 0.0,
        "context_weight": 0.10,
    },
    "coding_rust": {
        "preferred_types": ["llm-code", "llm-chat", "llm-reasoning", "vlm"],
        "benchmark_weights": {
            "multipl_e_rust": 0.30, "humaneval": 0.15, "swe_bench_verified": 0.15,
            "aider_polyglot": 0.15, "arena_elo_coding": 0.10, "multipl_e": 0.10,
            "arena_elo_overall": 0.05,
        },
        "capability_weights": {
            "coding": 0.30, "reasoning": 0.20, "tool_use": 0.15,
        },
        "cost_weight": 0.0,
        "context_weight": 0.10,
    },
    "coding_go": {
        "preferred_types": ["llm-code", "llm-chat", "llm-reasoning", "vlm"],
        "benchmark_weights": {
            "multipl_e_go": 0.30, "humaneval": 0.15, "swe_bench_verified": 0.15,
            "aider_polyglot": 0.15, "arena_elo_coding": 0.10, "multipl_e": 0.10,
            "arena_elo_overall": 0.05,
        },
        "capability_weights": {
            "coding": 0.30, "reasoning": 0.20, "tool_use": 0.15,
        },
        "cost_weight": 0.0,
        "context_weight": 0.10,
    },
    "coding_typescript": {
        "preferred_types": ["llm-code", "llm-chat", "llm-reasoning", "vlm"],
        "benchmark_weights": {
            "multipl_e_typescript": 0.30, "humaneval": 0.15, "swe_bench_verified": 0.15,
            "aider_polyglot": 0.15, "arena_elo_coding": 0.10, "multipl_e": 0.10,
            "arena_elo_overall": 0.05,
        },
        "capability_weights": {
            "coding": 0.30, "reasoning": 0.20, "tool_use": 0.15,
        },
        "cost_weight": 0.0,
        "context_weight": 0.10,
    },
    "coding_cpp": {
        "preferred_types": ["llm-code", "llm-chat", "llm-reasoning", "vlm"],
        "benchmark_weights": {
            "multipl_e_cpp": 0.30, "humaneval": 0.15, "swe_bench_verified": 0.15,
            "aider_polyglot": 0.15, "arena_elo_coding": 0.10, "multipl_e": 0.10,
            "arena_elo_overall": 0.05,
        },
        "capability_weights": {
            "coding": 0.30, "reasoning": 0.20, "tool_use": 0.15,
        },
        "cost_weight": 0.0,
        "context_weight": 0.10,
    },
    "coding_java": {
        "preferred_types": ["llm-code", "llm-chat", "llm-reasoning", "vlm"],
        "benchmark_weights": {
            "multipl_e_java": 0.30, "humaneval": 0.15, "swe_bench_verified": 0.15,
            "aider_polyglot": 0.15, "arena_elo_coding": 0.10, "multipl_e": 0.10,
            "arena_elo_overall": 0.05,
        },
        "capability_weights": {
            "coding": 0.30, "reasoning": 0.20, "tool_use": 0.15,
        },
        "cost_weight": 0.0,
        "context_weight": 0.10,
    },
    "coding_javascript": {
        "preferred_types": ["llm-code", "llm-chat", "llm-reasoning", "vlm"],
        "benchmark_weights": {
            "multipl_e_javascript": 0.30, "humaneval": 0.15, "swe_bench_verified": 0.15,
            "aider_polyglot": 0.15, "arena_elo_coding": 0.10, "multipl_e": 0.10,
            "arena_elo_overall": 0.05,
        },
        "capability_weights": {
            "coding": 0.30, "reasoning": 0.20, "tool_use": 0.15,
        },
        "cost_weight": 0.0,
        "context_weight": 0.10,
    },

    # ─── Sub-domain: Medical ──────────────────────────────────
    "medical": {
        "preferred_types": ["llm-chat", "llm-reasoning"],
        "benchmark_weights": {
            "medqa": 0.30, "pubmedqa": 0.20, "medmcqa": 0.15,
            "mmlu_clinical_knowledge": 0.15, "mmlu_pro": 0.10,
            "arena_elo_overall": 0.10,
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
            "medqa": 0.25, "mmlu_clinical_knowledge": 0.25, "pubmedqa": 0.15,
            "medmcqa": 0.15, "mmlu_pro": 0.10, "arena_elo_overall": 0.10,
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
            "medqa": 0.20, "mmmu": 0.20, "mmlu_clinical_knowledge": 0.15,
            "pubmedqa": 0.15, "arena_elo_vision": 0.15, "arena_elo_overall": 0.15,
        },
        "capability_weights": {
            "reasoning": 0.25, "domain": 0.15, "creative": 0.10,
        },
        "cost_weight": 0.0,
        "context_weight": 0.10,
    },

    # ─── Sub-domain: Legal ────────────────────────────────────
    "legal": {
        "preferred_types": ["llm-chat", "llm-reasoning"],
        "benchmark_weights": {
            "legalbench": 0.35, "mmlu_professional_law": 0.20,
            "mmlu_jurisprudence": 0.15, "ifeval": 0.10,
            "mmlu_pro": 0.10, "arena_elo_overall": 0.10,
        },
        "capability_weights": {
            "reasoning": 0.25, "domain": 0.15, "language": 0.15,
        },
        "cost_weight": 0.0,
        "context_weight": 0.15,
    },

    # ─── Sub-domain: Financial ────────────────────────────────
    "financial": {
        "preferred_types": ["llm-chat", "llm-reasoning"],
        "benchmark_weights": {
            "finbench": 0.30, "finqa": 0.20, "mmlu_pro": 0.15,
            "ifeval": 0.10, "math_500": 0.10, "arena_elo_overall": 0.15,
        },
        "capability_weights": {
            "reasoning": 0.25, "domain": 0.15, "language": 0.10,
        },
        "cost_weight": 0.0,
        "context_weight": 0.15,
    },

    # ─── Sub-domain: Science ──────────────────────────────────
    "science": {
        "preferred_types": ["llm-reasoning", "llm-chat"],
        "benchmark_weights": {
            "gpqa_diamond": 0.25, "mmlu_pro": 0.20, "math_500": 0.15,
            "mmlu_chemistry": 0.10, "mmlu_physics": 0.10, "mmlu_biology": 0.10,
            "arena_elo_overall": 0.10,
        },
        "capability_weights": {
            "reasoning": 0.30, "domain": 0.15, "language": 0.10,
        },
        "cost_weight": 0.0,
        "context_weight": 0.10,
    },
    "science_chemistry": {
        "preferred_types": ["llm-reasoning", "llm-chat"],
        "benchmark_weights": {
            "mmlu_chemistry": 0.30, "gpqa_diamond": 0.20, "mmlu_pro": 0.15,
            "math_500": 0.15, "arena_elo_overall": 0.10, "ifeval": 0.10,
        },
        "capability_weights": {
            "reasoning": 0.30, "domain": 0.15, "language": 0.10,
        },
        "cost_weight": 0.0,
        "context_weight": 0.10,
    },
    "science_physics": {
        "preferred_types": ["llm-reasoning", "llm-chat"],
        "benchmark_weights": {
            "mmlu_physics": 0.30, "gpqa_diamond": 0.20, "math_500": 0.15,
            "mmlu_pro": 0.15, "arena_elo_overall": 0.10, "ifeval": 0.10,
        },
        "capability_weights": {
            "reasoning": 0.30, "domain": 0.15, "language": 0.10,
        },
        "cost_weight": 0.0,
        "context_weight": 0.10,
    },
    "science_biology": {
        "preferred_types": ["llm-reasoning", "llm-chat"],
        "benchmark_weights": {
            "mmlu_biology": 0.30, "gpqa_diamond": 0.20, "mmlu_pro": 0.15,
            "mmlu_clinical_knowledge": 0.10, "arena_elo_overall": 0.15,
            "ifeval": 0.10,
        },
        "capability_weights": {
            "reasoning": 0.30, "domain": 0.15, "language": 0.10,
        },
        "cost_weight": 0.0,
        "context_weight": 0.10,
    },

    # ─── Sub-domain: Translation ──────────────────────────────
    "translation": {
        "preferred_types": ["llm-chat", "vlm"],
        "benchmark_weights": {
            "flores": 0.30, "mgsm": 0.20, "miracl": 0.20,
            "mmlu_pro": 0.10, "arena_elo_overall": 0.10, "ifeval": 0.10,
        },
        "capability_weights": {
            "language": 0.30, "creative": 0.15, "reasoning": 0.10,
        },
        "cost_weight": 0.0,
        "context_weight": 0.15,
    },

    # ─── Sub-domain: Creative Writing ─────────────────────────
    "writing_creative": {
        "preferred_types": ["llm-chat", "llm-reasoning"],
        "benchmark_weights": {
            "alpaca_eval": 0.25, "wildbench": 0.20, "mt_bench": 0.20,
            "arena_elo_style_control": 0.15, "arena_elo_overall": 0.10,
            "ifeval": 0.10,
        },
        "capability_weights": {
            "creative": 0.30, "language": 0.20, "reasoning": 0.10,
        },
        "cost_weight": 0.0,
        "context_weight": 0.10,
    },
    "writing_technical": {
        "preferred_types": ["llm-chat", "llm-reasoning", "llm-code"],
        "benchmark_weights": {
            "mt_bench": 0.20, "ifeval": 0.20, "alpaca_eval": 0.15,
            "mmlu_pro": 0.15, "arena_elo_overall": 0.15, "wildbench": 0.15,
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
            "mt_bench": 0.20, "alpaca_eval": 0.20, "arena_elo_overall": 0.15,
            "ifeval": 0.15, "wildbench": 0.15, "arena_elo_style_control": 0.15,
        },
        "capability_weights": {
            "creative": 0.25, "language": 0.20, "reasoning": 0.15,
        },
        "cost_weight": 0.0,
        "context_weight": 0.20,
    },

    # ─── Sub-domain: Math (competitive / advanced) ────────
    "math_competition": {
        "preferred_types": ["llm-reasoning", "llm-chat"],
        "benchmark_weights": {
            "aime_2025": 0.30, "math_500": 0.25, "aime_2026": 0.15,
            "gpqa_diamond": 0.10, "arena_elo_math": 0.10, "gsm8k": 0.10,
        },
        "capability_weights": {
            "reasoning": 0.35, "coding": 0.10,
        },
        "cost_weight": 0.0,
        "context_weight": 0.05,
    },

    # ─── Sub-domain: Education ────────────────────────────
    "education": {
        "preferred_types": ["llm-chat", "llm-reasoning", "vlm"],
        "benchmark_weights": {
            "mmlu_pro": 0.25, "arc_challenge": 0.15, "hellaswag": 0.10,
            "mt_bench": 0.15, "ifeval": 0.10, "arena_elo_overall": 0.15,
            "truthfulqa": 0.10,
        },
        "capability_weights": {
            "reasoning": 0.20, "language": 0.20, "creative": 0.15,
        },
        "cost_weight": 0.0,
        "context_weight": 0.10,
    },
    "education_stem": {
        "preferred_types": ["llm-reasoning", "llm-chat"],
        "benchmark_weights": {
            "mmlu_pro": 0.15, "mmlu_physics": 0.15, "mmlu_chemistry": 0.15,
            "mmlu_biology": 0.10, "math_500": 0.15, "gpqa_diamond": 0.15,
            "arena_elo_overall": 0.15,
        },
        "capability_weights": {
            "reasoning": 0.30, "domain": 0.15, "language": 0.10,
        },
        "cost_weight": 0.0,
        "context_weight": 0.10,
    },
    "education_humanities": {
        "preferred_types": ["llm-chat", "llm-reasoning"],
        "benchmark_weights": {
            "mmlu_pro": 0.15, "mmlu_professional_law": 0.10,
            "mmlu_business_ethics": 0.10, "truthfulqa": 0.15,
            "alpaca_eval": 0.15, "mt_bench": 0.15, "arena_elo_overall": 0.20,
        },
        "capability_weights": {
            "language": 0.25, "creative": 0.20, "reasoning": 0.15,
        },
        "cost_weight": 0.0,
        "context_weight": 0.10,
    },

    # ─── Sub-domain: Data Science / Analytics ─────────────
    "data_science": {
        "preferred_types": ["llm-code", "llm-reasoning", "llm-chat"],
        "benchmark_weights": {
            "multipl_e_python": 0.20, "humaneval": 0.15, "math_500": 0.15,
            "mmlu_pro": 0.10, "aider_polyglot": 0.10, "arena_elo_coding": 0.15,
            "gpqa_diamond": 0.10, "arena_elo_overall": 0.05,
        },
        "capability_weights": {
            "coding": 0.25, "reasoning": 0.25, "tool_use": 0.15,
        },
        "cost_weight": 0.0,
        "context_weight": 0.15,
    },

    # ─── Sub-domain: Customer Support / Chatbot ───────────
    "customer_support": {
        "preferred_types": ["llm-chat", "vlm"],
        "benchmark_weights": {
            "arena_elo_overall": 0.20, "mt_bench": 0.20, "ifeval": 0.20,
            "alpaca_eval": 0.15, "arena_elo_style_control": 0.15,
            "truthfulqa": 0.10,
        },
        "capability_weights": {
            "language": 0.25, "tool_use": 0.20, "creative": 0.10,
        },
        "cost_weight": 0.0,
        "context_weight": 0.10,
    },

    # ─── Sub-domain: Content Moderation ───────────────────
    "content_moderation": {
        "preferred_types": ["safety-classifier", "llm-chat", "reward-model"],
        "benchmark_weights": {
            "helm_safety": 0.30, "toxigen": 0.25, "bbq": 0.20,
            "ifeval": 0.10, "arena_elo_overall": 0.15,
        },
        "capability_weights": {
            "safety": 0.30, "language": 0.15,
        },
        "cost_weight": 0.0,
        "context_weight": 0.05,
    },

    # ─── Sub-domain: Research Assistant ───────────────────
    "research_assistant": {
        "preferred_types": ["llm-reasoning", "llm-chat", "vlm"],
        "benchmark_weights": {
            "gpqa_diamond": 0.20, "mmlu_pro": 0.15, "math_500": 0.10,
            "arena_elo_overall": 0.15, "mt_bench": 0.10, "ifeval": 0.10,
            "truthfulqa": 0.10, "arena_elo_hard_prompts": 0.10,
        },
        "capability_weights": {
            "reasoning": 0.25, "language": 0.15, "tool_use": 0.15,
        },
        "cost_weight": 0.0,
        "context_weight": 0.20,
    },

    # ─── Sub-domain: Roleplay / Character ─────────────────
    "roleplay": {
        "preferred_types": ["llm-chat"],
        "benchmark_weights": {
            "arena_elo_style_control": 0.25, "alpaca_eval": 0.20,
            "wildbench": 0.15, "mt_bench": 0.15, "arena_elo_overall": 0.15,
            "ifeval": 0.10,
        },
        "capability_weights": {
            "creative": 0.35, "language": 0.25,
        },
        "cost_weight": 0.0,
        "context_weight": 0.15,
    },

    # ─── Sub-domain: Audio ────────────────────────────────
    "speech_to_text": {
        "preferred_types": ["audio-stt", "audio-multimodal"],
        "benchmark_weights": {
            "wer_librispeech": 0.50, "arena_elo_overall": 0.20,
            "miracl": 0.15, "mgsm": 0.15,
        },
        "capability_weights": {
            "language": 0.20,
        },
        "cost_weight": 0.0,
        "context_weight": 0.05,
    },
    "text_to_speech": {
        "preferred_types": ["audio-tts", "audio-multimodal"],
        "benchmark_weights": {
            "mos_tts": 0.50, "arena_elo_overall": 0.20,
            "arena_elo_style_control": 0.15, "mt_bench": 0.15,
        },
        "capability_weights": {
            "creative": 0.15, "language": 0.15,
        },
        "cost_weight": 0.0,
        "context_weight": 0.05,
    },

    # ─── Sub-domain: Image Generation ─────────────────────
    "image_generation": {
        "preferred_types": ["image-gen", "vlm"],
        "benchmark_weights": {
            "fid": 0.30, "clip_score": 0.30,
            "arena_elo_overall": 0.20, "arena_elo_vision": 0.20,
        },
        "capability_weights": {
            "creative": 0.30,
        },
        "cost_weight": 0.0,
        "context_weight": 0.05,
    },

    # ─── Sub-domain: Cybersecurity ────────────────────────
    "cybersecurity": {
        "preferred_types": ["llm-code", "llm-reasoning", "llm-chat"],
        "benchmark_weights": {
            "humaneval": 0.15, "swe_bench_verified": 0.15,
            "mmlu_computer_science": 0.15, "terminal_bench": 0.15,
            "arena_elo_coding": 0.10, "gpqa_diamond": 0.10,
            "arena_elo_overall": 0.10, "ifeval": 0.10,
        },
        "capability_weights": {
            "coding": 0.25, "reasoning": 0.25, "tool_use": 0.20,
        },
        "cost_weight": 0.0,
        "context_weight": 0.15,
    },

    # ─── Sub-domain: DevOps / Infrastructure ──────────────
    "devops": {
        "preferred_types": ["llm-code", "llm-chat", "llm-reasoning"],
        "benchmark_weights": {
            "terminal_bench": 0.25, "humaneval": 0.15, "swe_bench_verified": 0.15,
            "aider_polyglot": 0.10, "arena_elo_coding": 0.15,
            "ifeval": 0.10, "arena_elo_overall": 0.10,
        },
        "capability_weights": {
            "coding": 0.25, "tool_use": 0.25, "reasoning": 0.15,
        },
        "cost_weight": 0.0,
        "context_weight": 0.10,
    },

    # ─── Sub-domain: Multilingual ─────────────────────────
    "multilingual": {
        "preferred_types": ["llm-chat", "vlm"],
        "benchmark_weights": {
            "mgsm": 0.25, "miracl": 0.20, "flores": 0.20,
            "mmlu_pro": 0.10, "arena_elo_overall": 0.15, "ifeval": 0.10,
        },
        "capability_weights": {
            "language": 0.35, "creative": 0.10, "reasoning": 0.10,
        },
        "cost_weight": 0.0,
        "context_weight": 0.15,
    },

    # ─── Sub-domain: Financial (specialties) ──────────────
    "financial_analysis": {
        "preferred_types": ["llm-reasoning", "llm-chat"],
        "benchmark_weights": {
            "finbench": 0.25, "finqa": 0.25, "math_500": 0.15,
            "mmlu_professional_accounting": 0.10, "mmlu_pro": 0.10,
            "arena_elo_overall": 0.15,
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
            "finbench": 0.20, "legalbench": 0.20, "mmlu_professional_law": 0.15,
            "mmlu_professional_accounting": 0.15, "ifeval": 0.15,
            "arena_elo_overall": 0.15,
        },
        "capability_weights": {
            "reasoning": 0.25, "domain": 0.15, "language": 0.15,
        },
        "cost_weight": 0.0,
        "context_weight": 0.15,
    },

    # ─── Sub-domain: Science (more specialties) ───────────
    "science_astronomy": {
        "preferred_types": ["llm-reasoning", "llm-chat"],
        "benchmark_weights": {
            "mmlu_astronomy": 0.30, "gpqa_diamond": 0.20, "mmlu_physics": 0.15,
            "math_500": 0.15, "mmlu_pro": 0.10, "arena_elo_overall": 0.10,
        },
        "capability_weights": {
            "reasoning": 0.30, "domain": 0.15, "language": 0.10,
        },
        "cost_weight": 0.0,
        "context_weight": 0.10,
    },

    # ─── Sub-domain: Legal (specialties) ──────────────────
    "legal_contract_review": {
        "preferred_types": ["llm-chat", "llm-reasoning"],
        "benchmark_weights": {
            "legalbench": 0.30, "mmlu_professional_law": 0.20,
            "ifeval": 0.15, "arena_elo_overall": 0.10,
            "mt_bench": 0.10, "mmlu_pro": 0.15,
        },
        "capability_weights": {
            "reasoning": 0.25, "language": 0.20, "domain": 0.15,
        },
        "cost_weight": 0.0,
        "context_weight": 0.20,
    },

    # ─── Sub-domain: Biotech / Life Sciences ──────────────
    "biotech": {
        "preferred_types": ["llm-reasoning", "llm-chat"],
        "benchmark_weights": {
            "mmlu_biology": 0.20, "mmlu_chemistry": 0.15, "medqa": 0.15,
            "pubmedqa": 0.15, "gpqa_diamond": 0.15, "mmlu_pro": 0.10,
            "arena_elo_overall": 0.10,
        },
        "capability_weights": {
            "reasoning": 0.30, "domain": 0.20, "language": 0.10,
        },
        "cost_weight": 0.0,
        "context_weight": 0.15,
    },

    # ─── Sub-domain: Accounting ───────────────────────────
    "accounting": {
        "preferred_types": ["llm-chat", "llm-reasoning"],
        "benchmark_weights": {
            "mmlu_professional_accounting": 0.30, "finbench": 0.20,
            "finqa": 0.15, "math_500": 0.10, "ifeval": 0.10,
            "arena_elo_overall": 0.15,
        },
        "capability_weights": {
            "reasoning": 0.25, "domain": 0.15, "language": 0.10,
        },
        "cost_weight": 0.0,
        "context_weight": 0.10,
    },

    # ─── Sub-domain: Code Review ──────────────────────────
    "code_review": {
        "preferred_types": ["llm-code", "llm-reasoning", "llm-chat"],
        "benchmark_weights": {
            "swe_bench_verified": 0.25, "humaneval": 0.15, "aider_polyglot": 0.15,
            "arena_elo_coding": 0.15, "terminal_bench": 0.10,
            "ifeval": 0.10, "arena_elo_overall": 0.10,
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
    card_completeness: float | None = None
    release_date: str | None = None
    reasoning: bool = False
    tool_call: bool = False
    vision_input: bool = False
    # Populated from graph edges
    benchmark_scores: dict[str, float] = field(default_factory=dict)
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
    score: float
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
        """Run the full 4-stage pipeline and return ranked models."""
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
        scored.sort(key=lambda s: (
            s.score,
            s.arena_elo_overall or 0,
            s.total_parameters or 0,
        ), reverse=True)

        # Stage 4: Explain (already built into scoring, but add rank-relative info)
        self._explain(scored, profile, use_case)

        return scored[:limit]

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
                card_completeness=_safe_float(props.get("card_completeness")),
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
        bench_weights = profile.get("benchmark_weights", {})
        bench_score = 0.0
        bench_contributions: dict[str, float] = {}
        total_bench_weight = 0.0
        available_bench_weight = 0.0

        for bench_id, weight in bench_weights.items():
            total_bench_weight += weight
            raw = model.benchmark_scores.get(bench_id)
            if raw is not None:
                normalized = _normalize_benchmark(bench_id, raw)
                contribution = normalized * weight
                bench_score += contribution
                bench_contributions[bench_id] = round(contribution, 2)
                available_bench_weight += weight

        # Scale benchmark score: if we only have some benchmarks,
        # scale proportionally but cap at what's available.
        # Models with more benchmark data naturally score higher because
        # missing benchmarks contribute 0.
        # Max possible = 40 points (sum of all weights * 100 * (40/100))
        bench_score_scaled = bench_score * 0.40  # 40 points max

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

        return ScoredModel(
            model_id=model.model_id,
            display_name=model.display_name,
            model_type=model.model_type,
            score=round(final_score, 2),
            benchmark_score=round(bench_score_scaled, 2),
            capability_score=round(cap_score_scaled, 2),
            cost_score=round(cost_score_scaled, 2),
            context_score=round(ctx_score_scaled, 2),
            type_bonus=round(type_bonus, 2),
            speed_score=round(speed_score, 2),
            estimated_tps=model.estimated_tps,
            concurrent_instances=model.concurrent_instances,
            benchmark_contributions=bench_contributions,
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

        top_score = scored[0].score if scored else 1.0

        for sm in scored:
            reasons: list[str] = []

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
    """Normalize a benchmark score to 0-100 range."""
    range_info = BENCHMARK_RANGES.get(bench_id)
    if range_info is None:
        # Unknown benchmark: assume 0-100 scale
        return max(0.0, min(100.0, raw_value))

    low, high = range_info
    if high <= low:
        return 50.0  # Degenerate range
    normalized = ((raw_value - low) / (high - low)) * 100.0
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
