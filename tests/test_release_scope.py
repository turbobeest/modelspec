"""Release signals outside the catalogue's scope are skipped (MODEL-468)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from release_signals.contract import ReleaseSignal
from release_signals.pipeline import FetchResult
from release_signals.scope import out_of_scope_reason
from scripts import process_release_signals as processor


def test_named_modalities_are_out_of_scope_and_ordinary_names_stay_in() -> None:
    assert out_of_scope_reason("Acme", "acme-embodied-walker") == (
        "robotics or embodied checkpoint"
    )
    assert out_of_scope_reason("Acme", "acme-robotics-arm") == (
        "robotics or embodied checkpoint"
    )
    assert out_of_scope_reason("Embodied", "Orbit 2") == (
        "robotics or embodied checkpoint"
    )
    for name in (
        "acme-text-to-image",
        "acme-image-generation",
        "acme-imagen",
        "acme-dall-e",
        "acme-stable-diffusion",
        "acme-sdxl",
    ):
        assert out_of_scope_reason("Acme", name) == "image generation"
    for name in (
        "acme-text-to-video",
        "acme-video-generation",
        "acme-veo",
        "acme-sora",
    ):
        assert out_of_scope_reason("Acme", name) == "video generation"
    for name in ("acme-transcribe", "acme-tts", "acme-voice"):
        assert out_of_scope_reason("Acme", name) == "speech"
    assert out_of_scope_reason("Acme", "acme-ocr") == "ocr"
    assert out_of_scope_reason("Acme", "acme-time-series") == "time series"
    assert out_of_scope_reason("Acme", "acme-timeseries") == "time series"
    for name in ("acme-checkpoint-12", "acme-sdg-export", "acme-residual-sae"):
        assert out_of_scope_reason("Acme", name) == "training or dataset artefact"
    for name in (
        "Orbit 2",
        "gpt-5.1",
        "acme-embeddings",
        "acme-whisper",
        "invoice",
        "https",
        "image",
        "video",
    ):
        assert out_of_scope_reason("Acme", name) is None


def test_an_out_of_scope_alias_writes_nothing_and_does_not_resolve(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    card = tmp_path / "models" / "acme" / "walker.md"
    card.parent.mkdir(parents=True)
    card.write_text(
        "---\n"
        "model_id: acme/walker\n"
        "display_name: acme-embodied-walker\n"
        "provider: acme\n"
        "provider_display: Acme\n"
        "version: walker\n"
        "---\n",
        encoding="utf-8",
    )
    before = card.read_bytes()
    pending = tmp_path / "pending.json"
    result_path = tmp_path / "result.json"
    audit_path = tmp_path / "audit.json"
    row = {
        "model_name": "acme-embodied-walker",
        "provider": "Acme",
        "first_seen_url": "https://x.com/acme/status/123456789",
        "timestamp": "2026-09-26T13:14:15Z",
        "confidence": 0.97,
        "signal_id": "grok-embodied-walker",
    }
    ReleaseSignal.parse(row)
    pending.write_text(json.dumps({"signals": [row]}))
    fetched: list[str] = []

    def fetch(url: str) -> FetchResult:
        fetched.append(url)
        raise AssertionError(f"fetched {url}")

    monkeypatch.setattr(processor, "_fetch", fetch)

    result = processor.process(
        pending, result_path, root=tmp_path, audit_path=audit_path,
    )

    assert result["status"] == "out_of_scope"
    assert result["reason"] == "robotics or embodied checkpoint"
    assert result["model_id"] is None
    assert fetched == []
    assert card.read_bytes() == before
    assert not audit_path.exists()
    assert json.loads(result_path.read_text(encoding="utf-8"))["status"] == "out_of_scope"
    assert not (tmp_path / "offerings").exists()
