"""Cards with an empty HF pipeline_tag that were mistyped as LLMs (MODEL-53 follow-up).

MODEL-53 retyped cards whose pipeline_tag implied a non-token model. Cards whose
pipeline_tag was empty were never touched by that fix, so encoders, diffusion
pipelines and audio components kept an llm-* type and got impossible decode
tok/s from `offline fit`. Each card below was retyped from its Hugging Face
config.json / library_name / tags (cited in the card's
availability.huggingface.notes), not from its name.

Cards no specific ModelType fits honestly are typed miscellaneous (MODEL-58).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from pipeline.hardware import is_token_generating  # noqa: E402
from schema.card import ModelCard  # noqa: E402
from schema.enums import ModelType  # noqa: E402

EXPECTED: dict[str, ModelType | None] = {
    "google/bert-uncased-l-2-h-128-a-2": ModelType.TEXT_ENCODER,
    "google/bert-uncased-l-4-h-256-a-4": ModelType.TEXT_ENCODER,
    "google/electra-small-discriminator": ModelType.TEXT_ENCODER,
    "google/electra-base-discriminator": ModelType.TEXT_ENCODER,
    "google/mobilebert-uncased": ModelType.TEXT_ENCODER,
    "google/rembert": ModelType.TEXT_ENCODER,
    "google/bigbird-roberta-base": ModelType.TEXT_ENCODER,
    "google/fnet-base": ModelType.TEXT_ENCODER,
    "google/bert-for-seq-generation-l-24-bbc-encoder": ModelType.TEXT_ENCODER,
    "allen-ai/biomed-roberta-base": ModelType.TEXT_ENCODER,
    "allen-ai/scibert-scivocab-uncased": ModelType.TEXT_ENCODER,
    "allen-ai/longformer-base-4096": ModelType.TEXT_ENCODER,
    "microsoft/layoutlmv2-base-uncased": ModelType.TEXT_ENCODER,
    "microsoft/layoutlmv3-base": ModelType.TEXT_ENCODER,
    "microsoft/markuplm-base": ModelType.TEXT_ENCODER,
    "jina/jina-bert-flash-implementation": ModelType.TEXT_ENCODER,
    "baai/seggpt-vit-large": ModelType.VISION_ENCODER,
    "salesforce/blip-itm-base-coco": ModelType.EMBEDDING_MULTIMODAL,
    "jina/jina-colbert-v2": ModelType.EMBEDDING_TEXT,
    "black-forest-labs/flux-1-fill-dev": ModelType.IMAGE_GENERATION,
    "black-forest-labs/flux-1-redux-dev": ModelType.IMAGE_GENERATION,
    "black-forest-labs/flux-1-canny-dev-lora": ModelType.IMAGE_GENERATION,
    "black-forest-labs/flux-1-depth-dev-lora": ModelType.IMAGE_GENERATION,
    "stability/stable-diffusion-x4-upscaler": ModelType.IMAGE_GENERATION,
    "stability/sd-x2-latent-upscaler": ModelType.IMAGE_GENERATION,
    "stability/sd-vae-ft-ema": ModelType.MISCELLANEOUS,
    "stability/sd-vae-ft-mse": ModelType.MISCELLANEOUS,
    "stability/sdxl-vae": ModelType.MISCELLANEOUS,
    "nvidia/speakerverification-en-titanet-large": ModelType.MISCELLANEOUS,
    "zhipu/glm-4-voice-tokenizer": ModelType.MISCELLANEOUS,
}


@pytest.mark.parametrize("model_id", sorted(EXPECTED))
def test_empty_tag_card_is_not_typed_as_a_token_generator(model_id: str) -> None:
    card = ModelCard.from_yaml_file(REPO_ROOT / "models" / f"{model_id}.md")
    assert card.identity.pipeline_tag == ""
    assert card.identity.model_type == EXPECTED[model_id]
    assert not is_token_generating(card.identity.model_type)
    assert "read 2026-09-14" in card.availability.huggingface.notes
