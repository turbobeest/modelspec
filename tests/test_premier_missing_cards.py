"""Cards for premier-set models that had none (MODEL-109 follow-up).

The slice-1 computation listed top-10 rows with no card. These tests load
the cards added for that list and check the facts that identify them.
GPT-5.5 pre-release rows are not products and have no card here.
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
]


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
    ):
        card = _load(rel)
        assert card.architecture.total_parameters is None
        assert card.licensing.open_weights is False
