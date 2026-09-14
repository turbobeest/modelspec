"""MODEL-53: an unmatched HF pipeline_tag must not default to llm-chat.

`determine_model_type` used to fall through to `ModelType.LLM_CHAT` for any
pipeline_tag it did not recognise. That mistyped ~62 non-token cards
(time-series forecasters, vision encoders, text encoders) as chat models,
which then led `offline fit` with impossible decode speeds computed from a
handful of megabytes of weights. See scripts/retype_non_token_cards.py for the
one-off corpus fix and pipeline/hardware.py for the decode-prediction gate.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from schema.enums import ModelType  # noqa: E402
from scripts.seed_huggingface import determine_model_type  # noqa: E402


def _hf(pipeline_tag: str, model_id: str = "org/model", tags: list[str] | None = None) -> dict:
    return {"id": model_id, "modelId": model_id, "pipeline_tag": pipeline_tag,
            "tags": tags or []}


# ── the named defect: these must not become llm-chat ────────────────────────

def test_time_series_forecasting_is_not_llm_chat() -> None:
    result = determine_model_type(_hf("time-series-forecasting", "ibm-granite/granite-timeseries-patchtst"))
    assert result == ModelType.TIME_SERIES
    assert result != ModelType.LLM_CHAT


def test_image_classification_is_not_llm_chat() -> None:
    result = determine_model_type(_hf("image-classification", "google/vit-base-patch16-224"))
    assert result == ModelType.VISION_ENCODER
    assert result != ModelType.LLM_CHAT


def test_fill_mask_is_not_llm_chat() -> None:
    result = determine_model_type(_hf("fill-mask", "microsoft/deberta-v3-base"))
    assert result == ModelType.TEXT_ENCODER
    assert result != ModelType.LLM_CHAT


def test_image_segmentation_is_not_llm_chat() -> None:
    result = determine_model_type(_hf("image-segmentation", "nvidia/segformer-b0"))
    assert result == ModelType.VISION_ENCODER
    assert result != ModelType.LLM_CHAT


def test_zero_shot_object_detection_is_not_llm_chat() -> None:
    result = determine_model_type(_hf("zero-shot-object-detection", "google/owlvit-base-patch32"))
    assert result == ModelType.VISION_ENCODER
    assert result != ModelType.LLM_CHAT


# ── siblings folded into the same fix ────────────────────────────────────────

def test_object_detection_reuses_vision_encoder() -> None:
    assert determine_model_type(_hf("object-detection")) == ModelType.VISION_ENCODER


def test_token_classification_reuses_text_encoder() -> None:
    assert determine_model_type(_hf("token-classification")) == ModelType.TEXT_ENCODER


def test_zero_shot_image_classification_reuses_embedding_multimodal() -> None:
    """CLIP/SigLIP-style dual encoders: reuse the existing embedding type."""
    assert determine_model_type(_hf("zero-shot-image-classification")) == ModelType.EMBEDDING_MULTIMODAL


# ── the null contract: an unmatched tag is never guessed ────────────────────

def test_unmatched_pipeline_tag_stays_null_not_llm_chat() -> None:
    assert determine_model_type(_hf("some-tag-nobody-has-seen-before")) is None


def test_unmatched_tag_warning_is_logged(capsys) -> None:
    determine_model_type(_hf("audio-to-audio", "vendor/mystery-model"))
    captured = capsys.readouterr()
    assert "audio-to-audio" in captured.err
    assert "vendor/mystery-model" in captured.err


def test_empty_pipeline_tag_still_defaults_to_llm_chat() -> None:
    """Unchanged pre-existing behaviour: no pipeline_tag at all is not the MODEL-53 defect."""
    assert determine_model_type(_hf("")) == ModelType.LLM_CHAT


# ── genuine token-generating tags are left alone ─────────────────────────────

def test_text_generation_still_defaults_to_llm_chat() -> None:
    assert determine_model_type(_hf("text-generation", "meta/some-chat-model")) == ModelType.LLM_CHAT


def test_image_text_to_text_is_still_vlm() -> None:
    assert determine_model_type(_hf("image-text-to-text")) == ModelType.VLM


def test_feature_extraction_is_still_embedding_text() -> None:
    assert determine_model_type(_hf("feature-extraction")) == ModelType.EMBEDDING_TEXT
