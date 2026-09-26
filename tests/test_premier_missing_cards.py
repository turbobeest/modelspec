"""Cards for premier-set models that had none (MODEL-109 follow-up).

The slice-1 computation listed top-10 rows with no card. These tests load
the cards added for that list and check the facts that identify them.
The second pass covers the MTEB(Multilingual, v2) rows that had none.
The GPT-5.5 pre-release checkpoints Epoch evaluated have cards too, at the
end of this file. They are not products and must never be offered.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from schema.card import ModelCard

ROOT = Path(__file__).resolve().parents[1]
READ = "2026-09-24"

# model_id, path under models/, model_type, one evidence row that must be present.
CASES = [
    ("meta/muse-spark-1-1", "meta/muse-spark-1-1.md", "llm-reasoning", "swe_bench_pro", 61.5),
    ("meta/muse-spark-1-2", "meta/muse-spark-1-2.md", "llm-reasoning", "arena_elo_overall", 1489.44),
    ("meta/muse-spark-1-3", "meta/muse-spark-1-3.md", "llm-reasoning", "arena_elo_overall", 1489.74),
    ("qwen/qwen3-8-max-0902", "qwen/qwen3-8-max-0902.md", "llm-reasoning", "arena_webdev", 1660.58),
    ("jcorners/ingot-8b-r3", "jcorners/ingot-8b-r3.md", "embedding-text", "mteb_eng_v2", 75.98),
    ("kingsoft/qzhou-embedding", "kingsoft/qzhou-embedding.md", "embedding-text", "mteb_eng_v2", 75.97),
    ("bytedance/seed1-5-embedding", "bytedance/seed1-5-embedding.md", "embedding-text", "mteb_eng_v2", 74.76),
    ("bytedance/seed1-6-embedding", "bytedance/seed1-6-embedding.md", "embedding-multimodal", "mteb_eng_v2", 74.07),
    ("infgrad/jasper-token-compression-600m", "infgrad/jasper-token-compression-600m.md", "embedding-text", "mteb_eng_v2", 74.75),
    ("annamodels/lgai-embedding-preview", "annamodels/lgai-embedding-preview.md", "embedding-text", "mteb_eng_v2", 74.12),
    ("codefuse/f2llm-4b", "codefuse/f2llm-4b.md", "embedding-text", "mteb_eng_v2", 73.67),
    ("querit/querit-4b", "querit/querit-4b.md", "reranker", "mteb_v2_reranking", 49.2),
    ("querit/querit", "querit/querit.md", "reranker", "mteb_v2_reranking", 48.27),
    ("microsoft/harrier-oss-v1-27b", "microsoft/harrier-oss-v1-27b.md", "embedding-text", "mteb_multilingual_v2", 74.27),
    ("microsoft/harrier-oss-v1-0-6b", "microsoft/harrier-oss-v1-0-6b.md", "embedding-text", "mteb_multilingual_v2", 69.01),
    ("bytedance/seed1-6-embedding-1215", "bytedance/seed1-6-embedding-1215.md", "embedding-multimodal", "mteb_multilingual_v2", 70.26),
    ("nvidia/llama-embed-nemotron-8b", "nvidia/llama-embed-nemotron-8b.md", "embedding-text", "mteb_multilingual_v2", 69.46),
    ("codefuse/f2llm-v2-14b", "codefuse/f2llm-v2-14b.md", "embedding-text", "mteb_multilingual_v2", 68.74),
    ("codefuse/f2llm-v2-8b", "codefuse/f2llm-v2-8b.md", "embedding-text", "mteb_multilingual_v2", 68.09),
]


def test_model_161_quality_metadata_is_structured_on_premier_cards() -> None:
    fable = _load("anthropic/claude-fable-5-1.md")
    arena = next(
        row for row in fable.benchmarks.evidence if row.benchmark_id == "arena_elo_overall"
    )
    assert arena.interval == (1499.43, 1515.73)
    assert arena.n == 5783

    opus = _load("anthropic/claude-opus-4-7.md")
    aime = next(row for row in opus.benchmarks.evidence if row.benchmark_id == "aime_2026")
    assert set(aime.quality_flags) == {"deprecated", "contamination_warning"}


def _load(rel: str) -> ModelCard:
    return ModelCard.from_yaml_file(ROOT / "models" / rel)


@pytest.mark.parametrize("model_id,rel,model_type,benchmark_id,score", CASES)
def test_card_loads_and_records_the_board_score(model_id, rel, model_type, benchmark_id, score):
    card = _load(rel)
    assert card.identity.model_id == model_id
    assert card.identity.model_type.value == model_type
    assert card.benchmarks.scores == {}
    matched = [row for row in card.benchmarks.evidence if row.benchmark_id == benchmark_id]
    assert matched, benchmark_id
    assert matched[0].score == score
    assert matched[0].source_url.startswith("https://")
    assert matched[0].verified_at == READ
    assert matched[0].source_kind in {
        "benchmark_author",
        "independent_evaluator",
        "provider_self_report",
    }


def test_unversioned_muse_spark_stays_a_different_card():
    """Arena and SWE-bench Pro list muse-spark apart from 1.1, 1.2 and 1.3."""
    old = _load("meta/muse-spark.md")
    assert old.identity.model_id == "meta/muse-spark"
    assert old.identity.release_date == "2026-04-08"
    for _model_id, rel, *_rest in CASES:
        if not rel.startswith("meta/muse-spark-1"):
            continue
        card = _load(rel)
        assert card.identity.model_id != old.identity.model_id
        assert "meta/muse-spark" in card.prose_body


def test_qwen_0902_is_not_the_august_card():
    august = _load("qwen/qwen3-8-max.md")
    dated = _load("qwen/qwen3-8-max-0902.md")
    assert august.identity.model_id == "qwen/qwen3-8-max"
    assert dated.identity.version == "qwen3.8-max-0902"
    assert dated.identity.release_date == "2026-09-02"
    assert dated.modalities.text.context_window == 1_000_000
    assert "qwen/qwen3-8-max" in dated.prose_body


def test_open_weight_counts_come_from_the_hub_safetensors_index():
    expected = {
        "kingsoft/qzhou-embedding.md": 7_070_619_136,
        "infgrad/jasper-token-compression-600m.md": 607_312_896,
        "annamodels/lgai-embedding-preview.md": 7_110_672_384,
        "codefuse/f2llm-4b.md": 4_022_468_096,
        "querit/querit-4b.md": 4_021_782_018,
        "querit/querit.md": 4_919_641_986,
        "microsoft/harrier-oss-v1-27b.md": 27_009_346_304,
        "microsoft/harrier-oss-v1-0-6b.md": 596_049_920,
        "codefuse/f2llm-v2-14b.md": 13_990_394_880,
        "codefuse/f2llm-v2-8b.md": 7_568_405_504,
    }
    for rel, count in expected.items():
        card = _load(rel)
        assert card.architecture.total_parameters == count
        assert card.architecture.total_parameters_source == "safetensors"
        assert card.licensing.open_weights is True
        assert card.licensing.license_type.value in {"apache-2.0", "mit"}
        # Public cards do not publish a new commercial-use determination.
        # The licence type above is the document the card names.
        assert card.licensing.commercial_use.value == "unspecified"
        assert card.licensing.commercial_use_source is None


def test_closed_models_do_not_invent_a_parameter_count():
    for rel in (
        "meta/muse-spark-1-1.md",
        "meta/muse-spark-1-2.md",
        "meta/muse-spark-1-3.md",
        "qwen/qwen3-8-max-0902.md",
        "jcorners/ingot-8b-r3.md",
        "bytedance/seed1-5-embedding.md",
        "bytedance/seed1-6-embedding.md",
        "bytedance/seed1-6-embedding-1215.md",
    ):
        card = _load(rel)
        assert card.architecture.total_parameters is None
        assert card.licensing.open_weights is False


def test_seed_1215_is_its_own_volcengine_model_id():
    """Volcengine lists doubao-embedding-vision-251215 beside -250615."""
    june = _load("bytedance/seed1-6-embedding.md")
    december = _load("bytedance/seed1-6-embedding-1215.md")
    assert june.identity.version == "doubao-embedding-vision-250615"
    assert december.identity.version == "doubao-embedding-vision-251215"
    assert december.availability.primary_provider.model_id_on_platform == "doubao-embedding-vision-251215"
    assert december.identity.model_id != june.identity.model_id
    assert "bytedance/seed1-6-embedding" in december.prose_body


def test_f2llm_v2_is_not_the_v1_card():
    v1 = _load("codefuse/f2llm-4b.md")
    for rel in ("codefuse/f2llm-v2-14b.md", "codefuse/f2llm-v2-8b.md"):
        card = _load(rel)
        assert card.identity.family == "f2llm-v2"
        assert card.identity.family != v1.identity.family
        assert card.sources.arxiv_url == "https://arxiv.org/abs/2603.19223"


def test_nemotron_names_its_nvidia_licence_and_leaves_commercial_use_open():
    card = _load("nvidia/llama-embed-nemotron-8b.md")
    assert card.architecture.total_parameters == 7_504_924_672
    assert card.architecture.total_parameters_source == "safetensors"
    assert card.licensing.open_weights is True
    assert card.licensing.license_type.value == "other"
    assert card.licensing.license_url == "https://huggingface.co/nvidia/llama-embed-nemotron-8b/blob/main/LICENSE"
    # The licence limits use to non-commercial research. The prose says so;
    # the public field stays unspecified like every other new card.
    assert card.licensing.commercial_use.value == "unspecified"
    assert "non-commercial" in card.prose_body


def test_provider_self_reports_are_labelled():
    expected = {
        "microsoft/harrier-oss-v1-27b.md": 74.3,
        "microsoft/harrier-oss-v1-0-6b.md": 69.0,
        "nvidia/llama-embed-nemotron-8b.md": 69.46,
    }
    for rel, score in expected.items():
        rows = [
            row
            for row in _load(rel).benchmarks.evidence
            if row.benchmark_id == "mteb_multilingual_v2" and row.source_kind == "provider_self_report"
        ]
        assert [row.score for row in rows] == [score], rel


@pytest.mark.parametrize("_model_id,rel,_model_type,_benchmark_id,_score", CASES[-6:])
def test_multilingual_live_readings_use_observation_dates(
    _model_id, rel, _model_type, _benchmark_id, _score
):
    rows = [row for row in _load(rel).benchmarks.evidence if row.source_kind == "benchmark_author"]
    assert rows
    for row in rows:
        assert row.date_type == "evaluated"
        assert row.evidence_date == READ


def test_multilingual_unknowns_stay_unknown():
    seed = _load("bytedance/seed1-6-embedding-1215.md")
    assert seed.identity.release_date == ""
    assert seed.modalities.embeddings.max_input_tokens is None
    assert _load("microsoft/harrier-oss-v1-27b.md").modalities.embeddings.max_input_tokens is None


@pytest.mark.parametrize("rel,mean,retrieval", [
    ("codefuse/f2llm-v2-14b.md", 73.08, 60.63),
    ("codefuse/f2llm-v2-8b.md", 72.86, 59.82),
])
def test_f2llm_v2_english_evidence(rel, mean, retrieval):
    rows = {row.benchmark_id: row.score for row in _load(rel).benchmarks.evidence}
    assert rows["mteb_eng_v2"] == mean
    assert rows["mteb_v2_retrieval"] == retrieval


# ── GPT-5.5 pre-release checkpoints (Epoch rows) ─────────────────────────────
#
# Epoch AI lists two rows as pre-release checkpoints. The cards record the
# evidence and must never make them selectable: no provider, no price, and a
# status that the v1 ranker and the premier-set script both leave out.

PRE_RELEASE = {
    "openai/gpt-5-5-pre-release": (
        "openai/gpt-5-5-pre-release.md",
        "openai/gpt-5-5",
        {"gpqa_diamond": 94.0, "swe_bench_verified": 80.58},
    ),
    "openai/gpt-5-5-pro-pre-release": (
        "openai/gpt-5-5-pro-pre-release.md",
        "openai/gpt-5-5-pro",
        {"gpqa_diamond": 93.92},
    ),
}


@pytest.mark.parametrize("model_id", sorted(PRE_RELEASE))
def test_pre_release_card_records_epochs_xhigh_rows(model_id):
    rel, released, expected = PRE_RELEASE[model_id]
    card = _load(rel)
    assert card.identity.model_id == model_id
    assert card.identity.model_type.value == "llm-reasoning"
    assert card.benchmarks.scores == {}
    rows = {row.benchmark_id: row for row in card.benchmarks.evidence}
    assert set(rows) == set(expected)
    for benchmark_id, score in expected.items():
        row = rows[benchmark_id]
        assert row.score == score
        assert row.model_id_as_evaluated.endswith("-pre-release_xhigh")
        assert "effort xhigh" in row.configuration
        assert row.source_url.startswith("https://epoch.ai/")
        assert row.source_kind == "independent_evaluator"
        assert row.date_type == "evaluated"
        assert row.verified_at == READ
        assert "CC BY 4.0" in row.limitations
    # The released product is a different card, and the prose says so.
    assert released in card.prose_body
    assert _load(released + ".md").identity.model_id == released


@pytest.mark.parametrize("model_id", sorted(PRE_RELEASE))
def test_pre_release_card_has_no_offering(model_id):
    rel = PRE_RELEASE[model_id][0]
    card = _load(rel)
    # Never selectable. The v1 ranker skips sunset and deprecated; the
    # premier-set script skips sunset.
    assert card.identity.status.value == "sunset"
    primary = card.availability.primary_provider
    assert primary.name == primary.api_endpoint == primary.model_id_on_platform == ""
    assert card.availability.platforms_available() == []
    assert card.availability.other_platforms == []
    for name, price in card.cost:
        if name in {"free_tier", "free_tier_limits", "note"}:
            continue
        assert price is None, name
    assert card.cost.free_tier is False
    assert not list(ROOT.glob(f"offerings/*/*/{model_id.split('/', 1)[1]}.yaml"))


def test_pre_release_checkpoints_stay_out_of_the_premier_set():
    import yaml

    data = yaml.safe_load((ROOT / "premier" / "slice-1.yaml").read_text())
    selected = {row["model_id"] for row in data["models"]}
    near = {row["model_id"] for row in data.get("near_misses") or []}
    missing = {row["slug"] for row in data.get("missing_cards") or []}
    for model_id in PRE_RELEASE:
        assert model_id not in selected
        assert model_id not in near
        assert model_id.split("/", 1)[1] not in missing
