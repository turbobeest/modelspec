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


def test_private_data_export_check_can_be_waived_only_by_env(monkeypatch) -> None:
    from api.worker.vendor import require_consistent_modalities

    monkeypatch.setenv("MODELSPEC_ALLOW_MODALITY_CONTRADICTIONS", "1")
    require_consistent_modalities([_modality_card(input=["image"])])


def _fact(facet: str, value: list[str], state: str = "known") -> dict:
    return {"facet": facet, "value": value, "state": state}


def test_modality_lists_are_compared_with_the_filed_facts() -> None:
    card = _modality_card(input=["text", "image", "pdf"], output=["text"])
    facts = [_fact("model.input_modalities", ["text", "image"]),
             _fact("model.output_modalities", ["text"])]
    assert card.modality_fact_errors(facts) == [
        "modalities.input contains pdf but model.input_modalities does not list document"
    ]
    facts[0]["value"].append("document")
    assert card.modality_fact_errors(facts) == []


def test_filed_modality_fact_missing_from_the_list_is_a_contradiction() -> None:
    card = _modality_card(input=["text"], output=["text"])
    facts = [_fact("model.output_modalities", ["text", "embedding"])]
    assert card.modality_fact_errors(facts) == [
        "model.output_modalities lists embedding but modalities.output does not contain embeddings"
    ]


def test_modality_fact_check_skips_unknown_or_absent_facts() -> None:
    card = _modality_card(input=["text", "pdf"])
    assert card.modality_fact_errors(None) == []
    assert card.modality_fact_errors([_fact("model.input_modalities", [], state="unknown")]) == []


def test_private_data_export_only_warns_on_a_list_that_contradicts_its_facts(capsys) -> None:
    from api.worker.vendor import require_consistent_modalities

    card = _modality_card(input=["text", "pdf"])
    require_consistent_modalities([card], [[_fact("model.input_modalities", ["text"])]])
    assert "1 modality list contradiction" in capsys.readouterr().err
    require_consistent_modalities([card], [[_fact("model.input_modalities", ["text", "document"])]])
    assert capsys.readouterr().err == ""


def _write_card(root: Path, name: str, pdf: bool) -> str:
    rel = f"models/acme/{name}.md"
    (root / rel).parent.mkdir(parents=True, exist_ok=True)
    front = {"model_id": f"acme/{name}", "display_name": name, "provider": "acme",
             "modalities": {"input": ["text", "pdf"] if pdf else ["text"], "output": ["text"]},
             "facts": [_fact("model.input_modalities", ["text"])]}
    (root / rel).write_text("---\n" + yaml.safe_dump(front) + "---\n")
    return rel


def _run_main(monkeypatch, capsys, root: Path, argv: list[str], files: list[str]) -> tuple[int, dict]:
    import json

    from scripts import validate_pr

    monkeypatch.setattr(validate_pr, "REPO_ROOT", root)
    monkeypatch.setattr(validate_pr, "get_all_model_files", lambda: files)
    monkeypatch.setattr(validate_pr, "get_changed_model_files", lambda: files)
    monkeypatch.setattr(validate_pr, "get_baseline_completeness", lambda f: None)
    monkeypatch.setattr(validate_pr, "get_baseline_fields", lambda f: set())
    monkeypatch.setattr(sys, "argv", ["validate_pr.py", *argv])
    code = 0
    try:
        validate_pr.main()
    except SystemExit as exit_:
        code = int(exit_.code or 0)
    return code, json.loads(capsys.readouterr().out)


def test_all_mode_warns_on_a_contradiction_and_stays_valid(tmp_path, monkeypatch, capsys) -> None:
    rel = _write_card(tmp_path, "bad", pdf=True)
    code, out = _run_main(monkeypatch, capsys, tmp_path, ["--all"], [rel])
    assert code == 0
    assert out["valid"] == 1 and out["invalid"] == 0
    assert out["modality_fact_warnings"] == 1
    assert "model.input_modalities" in out["results"][0]["warnings"][0]


def test_pr_mode_fails_a_changed_card_and_ignores_an_unchanged_one(tmp_path, monkeypatch, capsys) -> None:
    bad = _write_card(tmp_path, "bad", pdf=True)
    good = _write_card(tmp_path, "good", pdf=False)
    code, out = _run_main(monkeypatch, capsys, tmp_path, [], [bad])
    assert code != 0 and out["invalid"] == 1
    code, out = _run_main(monkeypatch, capsys, tmp_path, [], [good])
    assert code == 0 and out["invalid"] == 0
