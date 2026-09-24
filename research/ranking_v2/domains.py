"""Benchmark -> domain tags, and use cases as domain mixes.

This is the proposal for the `domains:` field on benchmark pages (see
docs/design/ranking-v2.md, "Domain tagging"). No benchmark page carries the
field yet, so the prototype derives tags in this order:

1. a page's own `domains:` list, when a page has one (none do today);
2. `OVERRIDES` below, for benchmarks whose page `category` is too coarse;
3. `CATEGORY_DEFAULTS`, from the page's existing `category`.

A tag says *what a benchmark measures*, never how much it matters. How much a
benchmark counts is learned from the data (its discrimination and its residual
noise), and which domains a use case needs is `USE_CASES`. Nothing here names a
benchmark as required for anything.
"""

from __future__ import annotations

#: The latent capability domains. Each is a factor beside the general factor g.
DOMAINS: tuple[str, ...] = (
    "coding", "agentic", "reasoning", "math", "knowledge", "chat",
    "vision", "long_context", "retrieval", "speech", "safety", "multilingual",
)

#: Page `category` -> default tags.
CATEGORY_DEFAULTS: dict[str, tuple[str, ...]] = {
    "coding": ("coding",),
    "agentic": ("agentic",),
    "reasoning": ("reasoning",),
    "math": ("math",),
    "knowledge": ("knowledge",),
    "domain": ("knowledge",),
    "instruction-following": ("chat",),
    "human-preference": ("chat",),
    "multimodal": ("vision",),
    "long-context": ("long_context",),
    "embedding": ("retrieval",),
    "translation": ("multilingual",),
    "safety": ("safety",),
    "generation": ("chat",),
    "composite": ("reasoning", "knowledge"),
}

#: Benchmarks whose page category undersells or misstates what they measure.
#: Two tags at most; the first is the primary one used when reporting errors.
OVERRIDES: dict[str, tuple[str, ...]] = {
    # Agentic software engineering: an agent loop over a real repository.
    "swe_bench_verified": ("coding", "agentic"),
    "swe_bench_pro": ("coding", "agentic"),
    "swe_bench_multilingual": ("coding", "agentic"),
    "swe_bench_multimodal": ("coding", "vision"),
    "swe_bench_agent": ("coding", "agentic"),
    "terminal_bench": ("agentic", "coding"),
    "terminal_bench_2": ("agentic", "coding"),
    "terminal_bench_v2_1": ("agentic", "coding"),
    "terminal_bench_3_0": ("agentic", "coding"),
    "terminal_bench_v4_0": ("agentic", "coding"),
    "terminal_bench_science": ("agentic", "reasoning"),
    "metr_time_horizon_50": ("agentic", "coding"),
    "metr_time_horizon_80": ("agentic", "coding"),
    "cybergym": ("agentic", "coding"),
    "scicode": ("coding", "reasoning"),
    # Visual maths is vision first.
    "mathvista": ("vision", "math"),
    "charxiv_reasoning": ("vision", "reasoning"),
    "charxiv_reasoning_tools": ("vision", "reasoning"),
    "arc_agi_2": ("reasoning",),
    "hle": ("reasoning", "knowledge"),
    "hle_tools": ("reasoning", "agentic"),
    "gpqa_diamond": ("reasoning", "knowledge"),
    "mmlu_pro": ("knowledge", "reasoning"),
    "mgsm": ("math", "multilingual"),
    "mmmlu": ("knowledge", "multilingual"),
    "browsecomp": ("agentic", "retrieval"),
    "osworld": ("agentic", "vision"),
    "screenspot_pro": ("vision", "agentic"),
    "ifeval": ("chat",),
    "mt_bench": ("chat",),
    "alpaca_eval": ("chat",),
    "wildbench": ("chat",),
    "musr": ("reasoning", "long_context"),
    "truthfulqa": ("knowledge", "safety"),
}

#: Arena boards (config/category) -> tags. The text boards are conversation
#: preference, so each carries `chat` first, plus its prompt slice; "people like
#: talking to it" then reaches the coding factor only where coding-specific
#: evidence agrees. WebDev, vision, agent, search and document boards are
#: preference *about a task's output*, so they are tagged with the task, not
#: with `chat`: a strong WebDev rating must not stand in for chat evidence.
ARENA_BOARDS: dict[str, tuple[str, ...]] = {
    "text_style_control/overall": ("chat",),
    "text_style_control/coding": ("chat", "coding"),
    "text_style_control/math": ("chat", "math"),
    "text_style_control/hard_prompts": ("chat", "reasoning"),
    "text_style_control/expert": ("chat", "knowledge"),
    "text_style_control/creative_writing": ("chat",),
    "text_style_control/instruction_following": ("chat",),
    "text_style_control/multi_turn": ("chat",),
    "text_style_control/longer_query": ("chat", "long_context"),
    "vision_style_control/overall": ("vision",),
    "webdev/overall": ("coding",),
    "agent/overall": ("agentic",),
    "search_style_control/overall": ("retrieval",),
    "document_style_control/overall": ("vision", "long_context"),
}


def tags_for(benchmark_id: str, page: dict | None) -> tuple[str, ...]:
    """Domain tags for one benchmark id, most specific source first."""
    if benchmark_id in ARENA_BOARDS:
        return ARENA_BOARDS[benchmark_id]
    page = page or {}
    own = page.get("domains")
    if isinstance(own, list) and own:
        return tuple(d for d in own if d in DOMAINS)[:2]
    if benchmark_id in OVERRIDES:
        return OVERRIDES[benchmark_id]
    if benchmark_id.startswith("mmlu_"):
        return ("knowledge",)
    if benchmark_id.startswith(("multipl_e", "humaneval", "mbpp")):
        return ("coding",)
    if benchmark_id.startswith(("mteb", "beir", "miracl")):
        return ("retrieval",)
    if benchmark_id.startswith("flores"):
        return ("multilingual",)
    return CATEGORY_DEFAULTS.get(str(page.get("category") or ""), ())


#: Use cases as domain mixes, plus the hard filters that apply *before* any
#: scoring. `classes` are `api/classes.py` class ids; a model outside them is
#: never a candidate, whatever its evidence (independent audit, Critical 3).
#: Mixes are proposals: Jamie owns them the way he owns the floors today.
USE_CASES: dict[str, dict] = {
    "coding": {"mix": {"coding": 0.6, "agentic": 0.3, "reasoning": 0.1},
               "classes": ("text-generator",)},
    "agentic": {"mix": {"agentic": 0.6, "coding": 0.25, "reasoning": 0.15},
                "classes": ("text-generator", "actor")},
    "reasoning": {"mix": {"reasoning": 0.6, "math": 0.25, "knowledge": 0.15},
                  "classes": ("text-generator",)},
    "math": {"mix": {"math": 0.8, "reasoning": 0.2}, "classes": ("text-generator",)},
    "chat": {"mix": {"chat": 0.8, "knowledge": 0.1, "reasoning": 0.1},
             "classes": ("text-generator",)},
    "general": {"mix": {"chat": 0.3, "reasoning": 0.2, "coding": 0.2, "knowledge": 0.15,
                        "agentic": 0.15}, "classes": ("text-generator",)},
    "vision": {"mix": {"vision": 0.8, "reasoning": 0.2}, "classes": ("text-generator",),
               "requires": ("image_input",)},
    "rag_generator": {"mix": {"long_context": 0.4, "knowledge": 0.3, "chat": 0.3},
                      "classes": ("text-generator",), "min_context": 128_000},
    "research_assistant": {"mix": {"reasoning": 0.4, "agentic": 0.3, "knowledge": 0.3},
                           "classes": ("text-generator",)},
    "embedding": {"mix": {"retrieval": 1.0}, "classes": ("vectoriser",)},
}

#: The primary domain of a use case: the one a model must have direct evidence
#: in before it can be `ranked` rather than `provisional`.
def primary_domain(use_case: str) -> str:
    mix = USE_CASES[use_case]["mix"]
    return max(mix, key=mix.get)
