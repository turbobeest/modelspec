"""MODEL-74: coverage is the share of type-applicable fields that are filled."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from schema.card import (
    Capabilities,
    EmbeddingDetail,
    ImageGenDetail,
    ModelCard,
    RerankingDetail,
    TextDetail,
    VisionDetail,
)
from schema.enums import ModelType, Tier

ROOT = Path(__file__).resolve().parents[1]
OLD_NAME = "card_" + "completeness"


def _unscoped_count(obj: BaseModel) -> tuple[int, int]:
    """The pre-MODEL-74 walk: every nested field, regardless of model_type."""
    filled = 0
    total = 0
    for field_name in type(obj).model_fields:
        value = getattr(obj, field_name)
        if field_name == "authoring_guide":
            continue
        if isinstance(value, BaseModel):
            f, t = _unscoped_count(value)
            filled += f
            total += t
        elif isinstance(value, list):
            total += 1
            if value:
                filled += 1
        elif isinstance(value, dict):
            total += 1
            if value:
                filled += 1
        elif field_name.startswith("card_") or field_name in ("prose_body", "authoring_guide"):
            continue
        else:
            total += 1
            if value is not None and value != "" and value is not False:
                filled += 1
    return filled, total


def _unscoped_coverage(card: ModelCard) -> float:
    filled, total = _unscoped_count(card)
    return round((filled / total) * 100, 1) if total else 0.0


def _card(model_type: ModelType | None, subtypes: list[ModelType] | None = None) -> ModelCard:
    return ModelCard(
        identity={
            "model_id": "test/coverage",
            "display_name": "Coverage",
            "provider": "test",
            "model_type": model_type,
            "model_subtypes": subtypes or [],
        }
    )


def test_well_researched_llm_is_materially_higher_than_unscoped() -> None:
    card = ModelCard.from_yaml_file(ROOT / "models/zhipu/glm-5-3-flash.md")
    old = _unscoped_coverage(card)
    new = card.applicable_field_coverage
    assert new > old, (new, old)
    assert new - old >= 1.0, (new, old)


def test_constructed_llm_is_not_diluted_by_empty_type_y_sections() -> None:
    card = _card(ModelType.LLM_CHAT)
    card.modalities.text.context_window = 128_000
    card.capabilities.coding.overall = Tier.TIER_1
    card.capabilities.reasoning.overall = Tier.TIER_1
    old = _unscoped_coverage(card)
    new = card.applicable_field_coverage
    assert new > old, (new, old)


def test_embedding_is_not_penalised_for_llm_or_image_fields() -> None:
    card = _card(ModelType.EMBEDDING_TEXT)
    base, base_total = card.applicable_field_coverage, card.applicable_field_counts()[1]
    card.modalities.text.context_window = 8192
    card.capabilities.coding.overall = Tier.TIER_1
    card.modalities.image_generation.supported = True
    card.modalities.audio.input_supported = True
    card.modalities.video.output_supported = True
    card.modalities.reranking.max_input_pairs = 100
    assert card.applicable_field_coverage == base
    assert card.applicable_field_counts()[1] == base_total
    card.modalities.embeddings.dimensions = 1536
    assert card.applicable_field_coverage > base


def test_llm_is_not_penalised_for_embedding_or_image_fields() -> None:
    card = _card(ModelType.LLM_CHAT)
    base, base_total = card.applicable_field_coverage, card.applicable_field_counts()[1]
    card.modalities.embeddings.dimensions = 1536
    card.modalities.reranking.supported = True
    card.modalities.image_generation.max_resolution = "1024x1024"
    card.modalities.audio.tts_voices = 12
    card.modalities.video.max_fps = 24
    assert card.applicable_field_coverage == base
    assert card.applicable_field_counts()[1] == base_total
    card.modalities.text.context_window = 128_000
    assert card.applicable_field_coverage > base


def test_embedding_denominator_is_smaller_than_the_whole_schema() -> None:
    llm = _card(ModelType.LLM_CHAT)
    emb = _card(ModelType.EMBEDDING_TEXT)
    _, unscoped = _unscoped_count(llm)
    _, llm_total = llm.applicable_field_counts()
    _, emb_total = emb.applicable_field_counts()
    assert llm_total < unscoped
    assert emb_total < unscoped
    assert emb_total < llm_total


def test_section_declarations_come_from_model_type_values() -> None:
    embedding = EmbeddingDetail.__applicable_model_types__
    assert embedding == {
        ModelType.EMBEDDING_TEXT,
        ModelType.EMBEDDING_MULTIMODAL,
        ModelType.EMBEDDING_CODE,
    }
    assert ModelType.LLM_CHAT not in embedding
    assert ModelType.LLM_CHAT in TextDetail.__applicable_model_types__
    assert ModelType.EMBEDDING_TEXT not in TextDetail.__applicable_model_types__
    assert ModelType.LLM_CHAT in Capabilities.__applicable_model_types__
    assert ModelType.EMBEDDING_TEXT not in Capabilities.__applicable_model_types__
    assert ModelType.VLM in VisionDetail.__applicable_model_types__
    assert ModelType.LLM_CHAT not in VisionDetail.__applicable_model_types__
    assert ModelType.IMAGE_GENERATION in ImageGenDetail.__applicable_model_types__
    assert ModelType.RERANKER in RerankingDetail.__applicable_model_types__
    assert ModelType.RERANKER not in EmbeddingDetail.__applicable_model_types__


def test_subtype_adds_that_type_sections() -> None:
    plain = _card(ModelType.QUANTIZED_VARIANT)
    with_vlm = _card(ModelType.QUANTIZED_VARIANT, subtypes=[ModelType.VLM])
    _, plain_total = plain.applicable_field_counts()
    _, vlm_total = with_vlm.applicable_field_counts()
    assert vlm_total > plain_total
    base = plain.applicable_field_coverage
    plain.modalities.vision.max_image_resolution = "4k"
    assert plain.applicable_field_coverage == base
    before = with_vlm.applicable_field_coverage
    with_vlm.modalities.vision.max_image_resolution = "4k"
    assert with_vlm.applicable_field_coverage > before


def test_untyped_card_counts_only_common_sections() -> None:
    card = _card(None)
    base, base_total = card.applicable_field_coverage, card.applicable_field_counts()[1]
    _, unscoped = _unscoped_count(card)
    assert base_total < unscoped
    card.modalities.embeddings.dimensions = 1536
    card.capabilities.coding.overall = Tier.TIER_1
    card.modalities.text.context_window = 8192
    assert card.applicable_field_coverage == base
    assert card.applicable_field_counts()[1] == base_total


def test_to_yaml_does_not_emit_coverage() -> None:
    text = _card(ModelType.LLM_CHAT).to_yaml()
    assert "applicable_field_coverage" not in text
    assert OLD_NAME not in text


def test_owned_consumers_do_not_use_the_old_name() -> None:
    allowed_alias = ROOT / "schema" / "card.py"
    this_file = Path(__file__).resolve()
    roots = [
        ROOT / "schema" / "card.py",
        ROOT / "schema" / "graph.py",
        ROOT / "cli" / "modelspec",
        ROOT / "api" / "ranking" / "engine.py",
        ROOT / "docs" / "cli-contract.md",
        ROOT / "docs" / "graph-ontology.md",
        ROOT / "tests",
    ]
    leftover: list[str] = []
    for root in roots:
        paths = [root] if root.is_file() else sorted(root.rglob("*"))
        for path in paths:
            if not path.is_file() or path.suffix not in {".py", ".md"}:
                continue
            if path.resolve() == this_file:
                continue
            text = path.read_text(encoding="utf-8")
            if OLD_NAME not in text:
                continue
            if path.resolve() == allowed_alias:
                # The deprecated alias for scripts/** this ticket does not own.
                assert f"def {OLD_NAME}(self)" in text
                continue
            leftover.append(str(path.relative_to(ROOT)))
    assert leftover == []
