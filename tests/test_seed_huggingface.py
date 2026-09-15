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


def _hf(pipeline_tag: str, model_id: str = "org/model", tags: list[str] | None = None,
        library_name: str | None = None) -> dict:
    return {"id": model_id, "modelId": model_id, "pipeline_tag": pipeline_tag,
            "tags": tags or [], "library_name": library_name}


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
    """A genuine LLM with no pipeline_tag and no non-token evidence: unchanged.

    This is today's behaviour for a real card in the corpus —
    ai21labs/Jamba-tiny-dev has pipeline_tag '' and no library_name/tags, and
    is a genuine causal LM (HF config.architectures is JambaForCausalLM). A
    null library/tags check must not flip that to something else.
    """
    assert determine_model_type(_hf("", library_name=None, tags=[])) == ModelType.LLM_CHAT


# ── empty pipeline_tag: library_name/tags evidence, not the model name ──────
# MODEL-53 review: ibm/granite-timeseries-tspulse-r1 has pipeline_tag '' and
# was defaulting to llm-chat (then, worse, getting caught by the "-r1"
# reasoning-keyword heuristic before ever reaching a pipeline_tag check).

def test_empty_tag_with_granite_tsfm_library_is_time_series() -> None:
    hf = _hf("", library_name="granite-tsfm", tags=["time series", "tspulse"])
    assert determine_model_type(hf) == ModelType.TIME_SERIES


def test_empty_tag_evidence_outranks_a_reasoning_looking_name() -> None:
    """The real defect: '-r1' in the name must not beat library/tags evidence."""
    hf = _hf("", model_id="ibm-granite/granite-timeseries-tspulse-r1",
             library_name="granite-tsfm", tags=["time series", "tspulse"])
    result = determine_model_type(hf)
    assert result == ModelType.TIME_SERIES
    assert result != ModelType.LLM_REASONING


def test_empty_tag_with_bert_tag_is_text_encoder() -> None:
    hf = _hf("", library_name="transformers", tags=["bert"])
    assert determine_model_type(hf) == ModelType.TEXT_ENCODER


def test_empty_tag_with_diffusers_library_is_image_generation() -> None:
    hf = _hf("", library_name="diffusers", tags=["stable-diffusion"])
    assert determine_model_type(hf) == ModelType.IMAGE_GENERATION


def test_empty_tag_with_bare_transformers_and_no_specific_tag_stays_llm_chat() -> None:
    """library_name='transformers' alone is not evidence — it hosts everything."""
    hf = _hf("", library_name="transformers", tags=["pytorch"])
    assert determine_model_type(hf) == ModelType.LLM_CHAT


def test_a_stated_pipeline_tag_outranks_library_evidence() -> None:
    """An explicit pipeline_tag is stronger evidence than a library guess."""
    hf = _hf("text-generation", library_name="diffusers", tags=["stable-diffusion"])
    assert determine_model_type(hf) == ModelType.LLM_CHAT


# ── genuine token-generating tags are left alone ─────────────────────────────

def test_text_generation_still_defaults_to_llm_chat() -> None:
    assert determine_model_type(_hf("text-generation", "meta/some-chat-model")) == ModelType.LLM_CHAT


def test_image_text_to_text_is_still_vlm() -> None:
    assert determine_model_type(_hf("image-text-to-text")) == ModelType.VLM


def test_feature_extraction_is_still_embedding_text() -> None:
    assert determine_model_type(_hf("feature-extraction")) == ModelType.EMBEDDING_TEXT
