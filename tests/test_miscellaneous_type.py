"""MODEL-58: the miscellaneous model type and the five cards that use it."""

from pathlib import Path

import pytest

from pipeline.hardware import TOKEN_GENERATING_MODEL_TYPES, is_token_generating
from schema.card import ModelCard
from schema.enums import ModelType

REPO_ROOT = Path(__file__).resolve().parents[1]

MISC_CARDS = [
    "stability/sd-vae-ft-ema",
    "stability/sd-vae-ft-mse",
    "stability/sdxl-vae",
    "nvidia/speakerverification-en-titanet-large",
    "zhipu/glm-4-voice-tokenizer",
]


def test_miscellaneous_is_not_token_generating():
    assert ModelType.MISCELLANEOUS.value == "miscellaneous"
    assert is_token_generating("miscellaneous") is False
    assert is_token_generating(ModelType.MISCELLANEOUS) is False
    assert "miscellaneous" not in {getattr(t, "value", t) for t in TOKEN_GENERATING_MODEL_TYPES}


@pytest.mark.parametrize("model_id", MISC_CARDS)
def test_card_loads_as_miscellaneous(model_id):
    card = ModelCard.from_yaml_file(REPO_ROOT / "models" / f"{model_id}.md")
    assert getattr(card.identity.model_type, "value", card.identity.model_type) == "miscellaneous"
