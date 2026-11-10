"""The validator must treat only real cards as cards.

`models/` also holds prose (LICENSE.md). Validating that as a model card failed
CI on every pull request that touched it, which is a defect in the validator
rather than in the data.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from schema.card import Identity, Licensing, ModelCard  # noqa: E402
from schema.enums import LicenseType  # noqa: E402
from scripts.validate_pr import is_model_card, validate_card  # noqa: E402


def test_licence_prose_in_models_is_not_a_card() -> None:
    assert (REPO_ROOT / "models/LICENSE.md").is_file()
    assert is_model_card("models/LICENSE.md") is False


def test_a_real_card_is_a_card() -> None:
    assert is_model_card("models/anthropic/claude-haiku-4-5.md") is True


def test_missing_file_is_not_a_card() -> None:
    assert is_model_card("models/nope/does-not-exist.md") is False


def test_every_model_card_file_is_detected() -> None:
    """The models tree is cards plus a single licence file."""
    md = sorted(p for p in (REPO_ROOT / "models").rglob("*.md"))
    detected = [p for p in md if is_model_card(str(p.relative_to(REPO_ROOT)))]
    assert len(detected) == len(md) - 1


def _lic_card(*, open_weights: bool, license_type: LicenseType | None) -> ModelCard:
    return ModelCard(
        identity=Identity(
            model_id="acme/test",
            display_name="Test",
            provider="acme",
        ),
        licensing=Licensing(open_weights=open_weights, license_type=license_type),
    )


def test_open_weights_true_with_proprietary_warns() -> None:
    warns = _lic_card(
        open_weights=True, license_type=LicenseType.PROPRIETARY
    ).warnings()
    assert warns
    assert "open_weights" in warns[0]
    assert "proprietary" in warns[0]


def test_open_weights_true_with_apache_does_not_warn() -> None:
    warns = _lic_card(
        open_weights=True, license_type=LicenseType.APACHE_2_0
    ).warnings()
    assert warns == []


def test_open_weights_false_with_proprietary_does_not_warn() -> None:
    warns = _lic_card(
        open_weights=False, license_type=LicenseType.PROPRIETARY
    ).warnings()
    assert warns == []


def test_validate_card_attaches_warnings_and_stays_valid() -> None:
    result = validate_card("models/anthropic/claude-haiku-4-5.md", compute_diff=False)
    assert result["status"] == "valid"
    assert result["warnings"] == []


@pytest.mark.parametrize(
    "kind,direction,section,flag",
    [
        ("video", "input", "video", "input_supported"),
        ("video", "output", "video", "output_supported"),
        ("audio", "input", "audio", "input_supported"),
        ("audio", "output", "audio", "output_supported"),
        ("image", "input", "vision", "supported"),
        ("image", "output", "image_generation", "supported"),
    ],
)
@pytest.mark.parametrize(
    "listed,supported,rejected",
    [(True, False, True), (False, True, True), (True, True, False), (False, False, False)],
    ids=["listed-but-false", "unlisted-but-true", "consistent-true", "consistent-false"],
)
def test_modality_list_flag_consistency(
    tmp_path, kind, direction, section, flag, listed, supported, rejected
) -> None:
    path = tmp_path / "fixture.md"
    data = {
        "model_id": "fixture/model",
        "display_name": "Fixture",
        "provider": "fixture",
        "modalities": {direction: [kind] if listed else [], section: {flag: supported}},
    }
    path.write_text("---\n" + yaml.safe_dump(data) + "---\n", encoding="utf-8")

    result = validate_card(str(path), compute_diff=False)

    if rejected:
        assert result["status"] == "invalid"
        error = result["error"]
        assert f"modalities.{section}.{flag}" in error
        assert f"modalities.{direction}" in error
        assert kind in error
        assert str(supported).lower() in error
    else:
        assert result["status"] == "valid"
        assert result["warnings"] == []


def test_listed_video_with_default_support_flag_is_rejected(tmp_path) -> None:
    path = tmp_path / "fixture.md"
    path.write_text(
        "---\nmodel_id: fixture/video\ndisplay_name: Video\nprovider: fixture\n"
        "modalities:\n  input: [text, video]\n---\n",
        encoding="utf-8",
    )

    result = validate_card(str(path), compute_diff=False)

    assert result["status"] == "invalid"
    assert "modalities.video.input_supported" in result["error"]


def _modality_card(**modalities: object) -> ModelCard:
    return ModelCard.model_validate({
        "identity": {"model_id": "acme/test", "display_name": "Test", "provider": "acme"},
        "modalities": modalities,
    })


def test_private_data_export_stops_on_a_contradicting_card() -> None:
    from api.worker.vendor import require_consistent_modalities

    require_consistent_modalities([_modality_card(input=["image"], vision={"supported": True})])
    with pytest.raises(SystemExit, match="acme/test: modalities.vision.supported is false"):
        require_consistent_modalities([_modality_card(input=["image"])])


def test_modality_errors_are_not_warnings() -> None:
    card = _modality_card(output=["audio"])
    assert card.modality_errors() == [
        "modalities.audio.output_supported is false but modalities.output contains audio"
    ]
    assert card.warnings() == []
