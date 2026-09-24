"""The models.dev seeder must not re-card a model the catalogue already holds.

--new-only used to mean "no file at this provider/slug path". That re-proposed
GLM-5.2 every day as mistral/zai-glm-5-2 and qwen/glm-5-2 after it was merged
onto zhipu/glm-5-2. Identity is an explicit registry, never a display-name match.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

from scripts import seed_models_dev as seeder  # noqa: E402
from scripts.seed_models_dev import (  # noqa: E402
    KNOWN_IDENTITIES_PATH,
    already_held,
    load_known_identities,
    models_dev_identity,
    seeder_file_path,
    seeder_model_id,
)

ZHIPU_GLM = "zhipu/glm-5-2"
MISTRAL_GLM = "mistral/zai-glm-5-2"
ALIBABA_GLM = "alibaba/glm-5.2"
QWEN_GLM = "qwen/glm-5-2"


def _write_card(models_dir: Path, model_id: str) -> Path:
    provider, slug = model_id.split("/", 1)
    path = models_dir / provider / f"{slug}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"model_id: {model_id}\n", encoding="utf-8")
    return path


def _held(
    tmp_path: Path,
    *,
    models_dev_id: str,
    seeder_id: str,
    known: dict[str, str],
    new_only: bool = True,
    file_exists: bool = False,
) -> str | None:
    file_path = tmp_path / f"{seeder_id}.md"
    if file_exists:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text("existing\n", encoding="utf-8")
    return already_held(
        models_dev_id=models_dev_id,
        seeder_id=seeder_id,
        file_path=file_path,
        models_dir=tmp_path,
        known=known,
        new_only=new_only,
    )


def test_live_registry_maps_glm_5_2_and_points_at_existing_cards() -> None:
    known = load_known_identities()
    assert known[MISTRAL_GLM] == ZHIPU_GLM
    assert known[ALIBABA_GLM] == ZHIPU_GLM
    assert known[QWEN_GLM] == ZHIPU_GLM
    for canonical in set(known.values()):
        provider, slug = canonical.split("/", 1)
        assert (REPO_ROOT / "models" / provider / f"{slug}.md").is_file()


def test_glm_5_2_under_mistral_or_qwen_is_not_proposed(tmp_path: Path) -> None:
    _write_card(tmp_path, ZHIPU_GLM)
    known = {MISTRAL_GLM: ZHIPU_GLM, ALIBABA_GLM: ZHIPU_GLM, QWEN_GLM: ZHIPU_GLM}
    assert (
        _held(tmp_path, models_dev_id=MISTRAL_GLM, seeder_id=MISTRAL_GLM, known=known)
        == f"known:{ZHIPU_GLM}"
    )
    assert (
        _held(tmp_path, models_dev_id=ALIBABA_GLM, seeder_id=QWEN_GLM, known=known)
        == f"known:{ZHIPU_GLM}"
    )


def test_genuinely_new_model_is_still_proposed(tmp_path: Path) -> None:
    _write_card(tmp_path, ZHIPU_GLM)
    known = {MISTRAL_GLM: ZHIPU_GLM, ALIBABA_GLM: ZHIPU_GLM, QWEN_GLM: ZHIPU_GLM}
    assert (
        _held(
            tmp_path,
            models_dev_id="acme/brand-new-9b",
            seeder_id="acme/brand-new-9b",
            known=known,
        )
        is None
    )


def test_same_display_name_without_a_registry_row_is_still_proposed(tmp_path: Path) -> None:
    """A models.dev row named GLM-5.2 that is not in the registry stays NEW."""
    _write_card(tmp_path, ZHIPU_GLM)
    known = {MISTRAL_GLM: ZHIPU_GLM, ALIBABA_GLM: ZHIPU_GLM, QWEN_GLM: ZHIPU_GLM}
    assert (
        _held(
            tmp_path,
            models_dev_id="greenpt/glm-5.2",
            seeder_id="greenpt/glm-5-2",
            known=known,
        )
        is None
    )


def test_known_identity_without_a_canonical_card_is_still_proposed(tmp_path: Path) -> None:
    known = {MISTRAL_GLM: ZHIPU_GLM}
    assert (
        _held(tmp_path, models_dev_id=MISTRAL_GLM, seeder_id=MISTRAL_GLM, known=known)
        is None
    )


def test_new_only_still_skips_an_existing_file_at_the_seeder_path(tmp_path: Path) -> None:
    assert (
        _held(
            tmp_path,
            models_dev_id="openai/gpt-5-nano",
            seeder_id="openai/gpt-5-nano",
            known={},
            file_exists=True,
        )
        == "exists"
    )


def test_conflicting_registry_rows_are_refused(tmp_path: Path) -> None:
    path = tmp_path / "identities.yaml"
    path.write_text(
        yaml.dump(
            {
                "identities": [
                    {"models_dev": MISTRAL_GLM, "canonical": ZHIPU_GLM},
                    {"models_dev": MISTRAL_GLM, "canonical": "mistral/glm-5-2"},
                ]
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="conflicting identity"):
        load_known_identities(path)


def test_models_dev_and_seeder_ids_are_explicit() -> None:
    raw = {"id": "glm-5.2", "name": "GLM-5.2"}
    qwen = {"slug": "qwen"}
    assert models_dev_identity("alibaba", raw, "glm-5.2") == ALIBABA_GLM
    assert seeder_model_id(qwen, raw, "glm-5.2") == QWEN_GLM
    assert seeder_file_path(Path("models"), qwen, raw, "glm-5.2") == Path(
        "models/qwen/glm-5-2.md"
    )


def test_registry_file_is_next_to_the_seeder() -> None:
    assert KNOWN_IDENTITIES_PATH == REPO_ROOT / "scripts" / "models_dev_known_identities.yaml"
    assert KNOWN_IDENTITIES_PATH.is_file()


def _rehost_card(models_dir: Path) -> None:
    path = models_dir / "zhipu" / "glm-5-3.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "---\n"
        "model_id: zhipu/glm-5-3\n"
        "display_name: GLM-5.3\n"
        "provider: zhipu\n"
        "provider_display: Z.ai\n"
        "release_date: '2026-08-14'\n"
        "sources:\n"
        "  huggingface_url: https://huggingface.co/zai-org/GLM-5.3\n"
        "---\n",
        encoding="utf-8",
    )


ZHIPU_GLM_53 = "zhipu/glm-5-3"
MISTRAL_GLM_53 = "mistral/zai-glm-5-3"
_DUPLICATE_53 = (
    "POSSIBLE DUPLICATE of zhipu/glm-5-3: "
    "same normalized display name and release date"
)


def test_glm_5_3_shaped_rehost_is_proposed_and_flagged(tmp_path, monkeypatch, capsys) -> None:
    """Same display name and release date, different provider and slug, not in the registry."""
    _rehost_card(tmp_path / "models")
    raw = {
        "id": "zai-org/glm-5-3-rehost",
        "name": "GLM-5.3",
        "family": "glm",
        "release_date": "2026-08-14",
        "modalities": {"input": ["text"], "output": ["text"]},
        "reasoning": True,
        "open_weights": True,
    }
    api = {"upstage": {"name": "Upstage", "models": {"zai-org/glm-5-3-rehost": raw}}}
    monkeypatch.setattr(seeder, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(seeder, "fetch_models_dev", lambda: api)
    monkeypatch.setattr(sys, "argv", ["seed_models_dev.py", "--new-only", "--dry-run"])
    seeder.main()
    new_lines = [ln for ln in capsys.readouterr().out.splitlines() if ln.startswith("    NEW")]
    assert new_lines == [f"    NEW zhipu/zai-org-glm-5-3-rehost  {_DUPLICATE_53}"]

    # The write step pastes --attribution-report into the pull request body.
    report = tmp_path / "attribution.md"
    monkeypatch.setattr(
        sys,
        "argv",
        ["seed_models_dev.py", "--new-only", "--attribution-report", str(report)],
    )
    seeder.main()
    assert (tmp_path / "models" / "zhipu" / "zai-org-glm-5-3-rehost.md").is_file()
    assert _DUPLICATE_53 in report.read_text(encoding="utf-8")


def test_glm_5_3_mistral_listing_is_already_held(tmp_path: Path) -> None:
    known = load_known_identities()
    assert known[MISTRAL_GLM_53] == ZHIPU_GLM_53
    _write_card(tmp_path, ZHIPU_GLM_53)
    assert (
        _held(
            tmp_path,
            models_dev_id=MISTRAL_GLM_53,
            seeder_id=MISTRAL_GLM_53,
            known=known,
        )
        == f"known:{ZHIPU_GLM_53}"
    )


def test_genuinely_new_model_is_proposed_without_a_duplicate_flag(
    tmp_path, monkeypatch, capsys
) -> None:
    _rehost_card(tmp_path / "models")
    raw = {
        "id": "brand-new-9b",
        "name": "Brand New 9B",
        "release_date": "2026-01-01",
        "modalities": {"input": ["text"], "output": ["text"]},
    }
    api = {"openai": {"name": "OpenAI", "models": {"brand-new-9b": raw}}}
    monkeypatch.setattr(seeder, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(seeder, "fetch_models_dev", lambda: api)
    monkeypatch.setattr(sys, "argv", ["seed_models_dev.py", "--new-only", "--dry-run"])
    seeder.main()
    new_lines = [ln for ln in capsys.readouterr().out.splitlines() if ln.startswith("    NEW")]
    assert new_lines == ["    NEW ? openai/brand-new-9b (creator to be judged: openai)"]
    assert all("POSSIBLE DUPLICATE" not in line for line in new_lines)


def test_same_huggingface_repo_is_proposed_and_flagged(tmp_path, monkeypatch, capsys) -> None:
    _rehost_card(tmp_path / "models")
    raw = {
        "id": "zai-org/GLM-5.3",
        "name": "Totally Different",
        "release_date": "2026-09-01",
        "modalities": {"input": ["text"], "output": ["text"]},
    }
    api = {"upstage": {"name": "Upstage", "models": {"zai-org/GLM-5.3": raw}}}
    monkeypatch.setattr(seeder, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(seeder, "fetch_models_dev", lambda: api)
    monkeypatch.setattr(sys, "argv", ["seed_models_dev.py", "--new-only", "--dry-run"])
    seeder.main()
    new_lines = [ln for ln in capsys.readouterr().out.splitlines() if ln.startswith("    NEW")]
    assert new_lines == [
        "    NEW zhipu/zai-org-glm-5-3  "
        "POSSIBLE DUPLICATE of zhipu/glm-5-3: same Hugging Face repo zai-org/glm-5.3"
    ]
