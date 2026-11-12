"""Release signals outside the catalogue's scope are skipped (MODEL-468)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from release_signals.contract import ReleaseSignal
from release_signals.pipeline import FetchResult
from release_signals.scope import (
    IN_SCOPE_PIPELINE_TAGS,
    OUT_OF_SCOPE_PIPELINE_TAGS,
    TagDecision,
    derivative_reason,
    out_of_scope_reason,
    tag_scope,
)
from scripts import process_release_signals as processor


def test_named_modalities_are_out_of_scope_and_ordinary_names_stay_in() -> None:
    assert out_of_scope_reason("Acme", "acme-embodied-walker") == (
        "robotics or embodied checkpoint"
    )
    assert out_of_scope_reason("Acme", "acme-robotics-arm") == (
        "robotics or embodied checkpoint"
    )
    assert out_of_scope_reason("Embodied", "Orbit 2") is None
    assert out_of_scope_reason("Voice AI", "Orbit 2") is None
    assert out_of_scope_reason("Voice AI", "grok-voice-3-0") == "speech"
    assert out_of_scope_reason("Acme", "Stable Diffusion 4") == "image generation"
    assert out_of_scope_reason("Acme", "Time Series Transformer") == "time series"
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
    assert out_of_scope_reason("Acme", "image") == "image generation"
    assert out_of_scope_reason("Acme", "qwen-vl-image") is None
    for name in (
        "Orbit 2",
        "gpt-5.1",
        "acme-embeddings",
        "acme-whisper",
        "invoice",
        "https",
        "video",
    ):
        assert out_of_scope_reason("Acme", name) is None


def test_review_names_follow_the_normalised_model_name() -> None:
    out = {
        "flux-3-image-klein": "image generation",
        "gpt-image-2-6": "image generation",
        "minimax-h3-image": "image generation",
        "gemini-nano-banana-2-1": "image generation",
        "timestral-209m": "time series",
        "internvideo2-clip-anomaly-detection": "anomaly detection",
        "grok-imagine-video-1-5-lite": "image or video generation",
        "voxtral-mini-tts-3-0": "speech",
        "voxtral-mini-transcribe-realtime-3-0": "speech",
        "grok-voice-3-0": "speech",
        "apriel-voice-27b-preview": "speech",
        "mistral-ocr-4": "ocr",
        "minicpm-ocr-1-0": "ocr",
        "cosmos3-nano-libero10-sdg-export-d2-s43": "training or dataset artefact",
        "gr00t-n1-7-appletoplate-cosine40k-checkpoint-15000": "training or dataset artefact",
        "qwen3-30b-a3b-moe-sae": "training or dataset artefact",
    }
    for name, reason in out.items():
        assert out_of_scope_reason("Voice AI", name) == reason
    for name in (
        "molmo2-4b-tb",
        "gemini-omni-1-1-flash",
        "d1-omni-2b",
        "lfm-3-vl-2b",
        "mage-vl-cowork",
        "nemotron-3-5-super-vl-120b-a12b",
        "wevisone-vl-2b",
        "embed-v5-0-fast",
        "rerank-v5-0-pro",
        "nemotron-3-5-rerank-8b",
        "gemini-decision-1",
        "gpt-6-cyber",
        "hy-simulmt-30b-a3b",
        "granite-switch-4-1-30b",
        "glm-5-3-flashx-legal",
        "qwen3-vl",
        "minicpm-v",
        "grok-vision",
        "gpt-6-omni",
    ):
        assert out_of_scope_reason("Voice AI", name) is None


def test_imagine_is_image_or_video_generation() -> None:
    assert out_of_scope_reason("Acme", "grok-imagine-video-1-5-lite") == (
        "image or video generation"
    )
    assert out_of_scope_reason("Acme", "acme-imagine") == "image or video generation"
    assert out_of_scope_reason("Acme", "Stable Diffusion 4") == "image generation"
    assert out_of_scope_reason("Acme", "acme-flux") == "image generation"


def test_an_image_token_keeps_embedding_captioning_and_text_models() -> None:
    for name in (
        "amazon.titan-embed-image-v1",
        "blip-image-captioning-large",
        "nomic-embed-image-v2",
        "image-text-to-text-7b",
    ):
        assert out_of_scope_reason("Acme", name) is None
    for name in (
        "flux-3-image-klein",
        "gpt-image-2-6",
        "minimax-h3-image",
        "text-to-image-xl",
    ):
        assert out_of_scope_reason("Acme", name) == "image generation"


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


@pytest.mark.parametrize("tag", sorted(IN_SCOPE_PIPELINE_TAGS))
def test_listed_pipeline_tags_are_in_scope(tag: str) -> None:
    assert tag_scope(tag) == TagDecision(True, None, tag)


@pytest.mark.parametrize("tag", sorted(OUT_OF_SCOPE_PIPELINE_TAGS))
def test_listed_pipeline_tags_are_out_of_scope_with_the_tag_as_the_reason(tag: str) -> None:
    assert tag_scope(tag) == TagDecision(True, tag, tag)


def test_an_audio_prefix_and_an_unknown_tag_follow_the_tag_rules() -> None:
    assert "audio-text-to-text" not in OUT_OF_SCOPE_PIPELINE_TAGS
    assert tag_scope("audio-text-to-text") == TagDecision(
        True, "audio-text-to-text", "audio-text-to-text",
    )
    assert tag_scope("graph-ml", ("robotics",)) == TagDecision(True, None, "graph-ml")
    assert tag_scope("Robotics", ("text-generation",)) == TagDecision(True, "Robotics", "Robotics")


def test_no_pipeline_tag_falls_back_unless_a_task_tag_decides() -> None:
    assert tag_scope(None, ()) == TagDecision(False)
    assert tag_scope("", ("en", "license:mit", "transformers")) == TagDecision(False)
    assert tag_scope("  ", ()) == TagDecision(False)
    assert tag_scope(None, ("en", "reinforcement-learning")) == TagDecision(
        True, "reinforcement-learning", "reinforcement-learning",
    )
    assert tag_scope(None, ("text-generation", "robotics")) == TagDecision(
        True, "robotics", "robotics",
    )
    assert tag_scope(None, ("transformers", "text-generation")) == TagDecision(
        True, None, "text-generation",
    )
    assert tag_scope("text-generation", ("robotics",)) == TagDecision(
        True, None, "text-generation",
    )


def test_a_derivative_is_an_artefact_named_after_another_labs_base() -> None:
    assert derivative_reason(
        "acme-lab/orbit-1-sparse", "other-lab/Orbit-1",
    ) == "derivative of other-lab/Orbit-1"
    assert derivative_reason("acme-lab/flagship", "other-lab/Orbit-1") is None
    assert derivative_reason(
        "acme-lab/siglip-vl", ("acme-lab/flagship", "other-lab/siglip"),
    ) is None
    assert derivative_reason("acme-lab/orbit-1-tune", "acme-lab/Orbit-1") is None
    assert derivative_reason("Acme-Lab/orbit-1-tune", "acme-lab/Orbit-1") is None
    assert derivative_reason("acme-lab/orbit-1-sparse", None) is None
    assert derivative_reason("acme-lab/orbit-1-sparse", "") is None
    assert derivative_reason("acme-lab/orbit-1-sparse", "not-a-repository") is None
    assert derivative_reason(
        "acme-lab/orbit-1-sparse", ("not-a-repository", "other-lab/Orbit-1"),
    ) == "derivative of other-lab/Orbit-1"
    assert derivative_reason("acme-lab/orbit-10-sparse", "other-lab/Orbit-1") is None
