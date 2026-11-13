"""Release signals outside the catalogue's scope are skipped (MODEL-468)."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest
import yaml

from release_signals.contract import ReleaseSignal
from release_signals.pipeline import FetchResult
from release_signals.scope import (
    IN_SCOPE_PIPELINE_TAGS,
    OUT_OF_SCOPE_PIPELINE_TAGS,
    TagDecision,
    derivative_reason,
    hub_metadata,
    known_pipeline_tag,
    out_of_scope_reason,
    relevant_hub_tags,
    tag_scope,
)
from release_signals.watch import ROOT, Seen, Source, load_registry
from scripts import process_release_signals as processor
from scripts.release_watch_filter import _hub_scope_reason

# Language, embedding, reranker and neighbouring types the catalogue ranks.
# Modality types the watcher is built to skip stay out of this replay.
_IN_SCOPE_MODEL_TYPES = frozenset({
    "llm-chat", "llm-reasoning", "llm-code", "llm-base", "vlm",
    "embedding-text", "embedding-multimodal", "embedding-code", "reranker",
    "safety-classifier", "medical", "legal", "financial",
    "reward-model", "router", "agent-model", "decision-model",
    "adapter", "quantized-variant", "distilled", "merged", "text-encoder",
})

# 42 public cards stay rejected. 28 are named after another lab's base.
# 14 carry an out-of-scope pipeline tag or an out-of-scope name.
_CATALOGUE_SCOPE_EXCEPTIONS: dict[str, str] = {
    "nvidia/bigvgan-v2-22khz-80band-256x": "audio-to-audio",
    "nvidia/bigvgan-v2-44khz-128band-512x": "audio-to-audio",
    "nvidia/deepseek-r1-0528-nvfp4-v2": "derivative of deepseek-ai/DeepSeek-R1-0528",
    "nvidia/gemma-4-31b-it-nvfp4": "derivative of google/gemma-4-31B-it",
    "nvidia/glm-5-nvfp4": "derivative of zai-org/GLM-5",
    "nvidia/kimi-k2-5-nvfp4": "derivative of moonshotai/Kimi-K2.5",
    "nvidia/llama-3-1-8b-instruct-fp8": "derivative of meta-llama/Llama-3.1-8B-Instruct",
    "nvidia/llama-3-1-8b-instruct-nvfp4": "derivative of meta-llama/Llama-3.1-8B-Instruct",
    "nvidia/llama-3-3-70b-instruct-nvfp4": "derivative of meta-llama/Llama-3.3-70B-Instruct",
    "nvidia/personaplex-7b-v1": "audio-to-audio",
    "nvidia/qwen3-14b-nvfp4": "derivative of Qwen/Qwen3-14B",
    "nvidia/qwen3-30b-a3b-nvfp4": "derivative of Qwen/Qwen3-30B-A3B",
    "nvidia/qwen3-32b-nvfp4": "derivative of Qwen/Qwen3-32B",
    "nvidia/qwen3-5-397b-a17b-nvfp4": "derivative of Qwen/Qwen3.5-397B-A17B",
    "qwen/qwen-vl-ocr": "ocr",
    "stability/stable-audio-open-1-0": "text-to-audio",
    "stability/stable-video-diffusion-img2vid-xt-1-1": "image-to-video",
    "stability/stable-video-diffusion-img2vid-xt": "image-to-video",
    "stability/stable-video-diffusion-img2vid": "image-to-video",
    "stability/stable-virtual-camera": "image-to-video",
    "tencent/songgeneration": "text-to-audio",
    "unsloth/deepseek-ocr-2": "derivative of deepseek/deepseek-ocr-2",
    "unsloth/gemma-4-26b-a4b-it-gguf": "derivative of google/gemma-4-26b-a4b-it",
    "unsloth/gemma-4-31b-it-gguf": "derivative of google/gemma-4-31b-it",
    "unsloth/gemma-4-e4b-it-gguf": "derivative of google/gemma-4-e4b-it",
    "unsloth/glm-4-7-flash-fp8-dynamic": "derivative of zhipu/glm-4-7-flash",
    "unsloth/gpt-oss-20b-gguf": "derivative of openai/gpt-oss-20b",
    "unsloth/llama-3-1-8b-instruct": "derivative of meta/llama-3-1-8b-instruct",
    "unsloth/ltx-2-3-gguf": "image-to-video",
    "unsloth/mistral-7b-v0-3-bnb-4bit": "derivative of mistral/mistral-7b-v0-3",
    "unsloth/qwen3-0-6b": "derivative of Qwen/Qwen3-0.6B",
    "unsloth/qwen3-5-0-8b-gguf": "derivative of qwen/qwen3-5-0-8b",
    "unsloth/qwen3-5-122b-a10b-gguf": "derivative of qwen/qwen3-5-122b-a10b",
    "unsloth/qwen3-5-27b-gguf": "derivative of qwen/qwen3-5-27b",
    "unsloth/qwen3-5-2b-gguf": "derivative of qwen/qwen3-5-2b",
    "unsloth/qwen3-5-35b-a3b-gguf": "derivative of qwen/qwen3-5-35b-a3b",
    "unsloth/qwen3-5-4b-gguf": "derivative of qwen/qwen3-5-4b",
    "unsloth/qwen3-5-9b-gguf": "derivative of qwen/qwen3-5-9b",
    "unsloth/qwen3-coder-next-gguf": "derivative of qwen/qwen3-coder-next",
    "zhipu/cogvideox-5b-i2v": "image-to-video",
    "zhipu/cogvideox1-5-5b-i2v": "image-to-video",
    "zhipu/glm-4-voice-9b": "speech",
}


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


def test_multimodal_tags_stay_in_scope_and_can_keep_a_speech_pipeline_tag() -> None:
    for tag in (
        "audio-text-to-text",
        "zero-shot-image-classification",
        "image-feature-extraction",
    ):
        assert tag not in OUT_OF_SCOPE_PIPELINE_TAGS
        assert tag not in IN_SCOPE_PIPELINE_TAGS
        assert not known_pipeline_tag(tag)
        assert tag_scope(tag) == TagDecision(True, None, tag)
    assert tag_scope("audio-classification") == TagDecision(
        True, "audio-classification", "audio-classification",
    )
    assert tag_scope("graph-ml", ("robotics",)) == TagDecision(True, None, "graph-ml")
    assert tag_scope("Robotics", ("en",)) == TagDecision(True, "Robotics", "Robotics")
    assert tag_scope("text-to-speech", ("image-text-to-text",)) == TagDecision(
        True, None, "image-text-to-text",
    )
    assert tag_scope("automatic-speech-recognition", ("audio-text-to-text",)) == TagDecision(
        True, None, "audio-text-to-text",
    )
    assert tag_scope("Robotics", ("text-generation", "en")) == TagDecision(
        True, None, "text-generation",
    )


def test_no_pipeline_tag_lets_the_name_rules_decide() -> None:
    assert tag_scope(None, ()) == TagDecision(False)
    assert tag_scope("", ("en", "license:mit", "transformers")) == TagDecision(False)
    assert tag_scope("  ", ()) == TagDecision(False)
    assert tag_scope(None, ("en", "reinforcement-learning")) == TagDecision(
        True, "reinforcement-learning", "reinforcement-learning",
    )
    assert tag_scope(None, ("text-generation", "robotics")) == TagDecision(False)
    assert tag_scope(None, ("transformers", "text-generation")) == TagDecision(False)
    assert tag_scope(None, ("audio",)) == TagDecision(False)
    assert tag_scope("audio") == TagDecision(True, None, "audio")
    assert not known_pipeline_tag("audio")
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


def _text(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    text = value.strip()
    return text or None


def _huggingface_repo(url: object) -> str | None:
    if not isinstance(url, str) or "huggingface.co/" not in url:
        return None
    path = url.split("huggingface.co/", 1)[1].strip().strip("/").split("?", 1)[0]
    parts = [part for part in path.split("/") if part]
    if not parts or parts[0] in {"datasets", "spaces", "collections"}:
        return None
    if len(parts) < 2 or not parts[0] or not parts[1]:
        return None
    return f"{parts[0]}/{parts[1]}"


def _catalogue_scope_rejections() -> dict[str, str]:
    """Watcher scope for each in-scope card under a registered Hugging Face lab."""
    loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
    by_dir: dict[str, tuple[Source, str]] = {}
    for source in load_registry().sources:
        if source.kind != "huggingface":
            continue
        authors = parse_qs(urlsplit(source.url).query, keep_blank_values=True).get("author", [])
        org = authors[0] if authors else ""
        by_dir.setdefault(source.provider, (source, org))
        if org:
            by_dir.setdefault(org.casefold(), (source, org))
    rejected: dict[str, str] = {}
    for path in sorted((ROOT / "models").glob("*/*.md")):
        lab = path.parent.name
        if lab not in by_dir:
            continue
        parts = path.read_text(encoding="utf-8").split("---", 2)
        if len(parts) < 3:
            continue
        front = yaml.load(parts[1], Loader=loader)
        if not isinstance(front, dict):
            continue
        model_type = _text(front.get("model_type")) or ""
        if model_type not in _IN_SCOPE_MODEL_TYPES:
            continue
        source, org = by_dir[lab]
        model_id = _text(front.get("model_id")) or f"{lab}/{path.stem}"
        sources = front.get("sources") if isinstance(front.get("sources"), dict) else {}
        repo = _huggingface_repo(sources.get("huggingface_url")) or f"{org}/{path.stem}"
        tags = tuple(tag for tag in (front.get("tags") or []) if isinstance(tag, str))
        lineage = front.get("lineage") if isinstance(front.get("lineage"), dict) else {}
        seen = Seen(
            repo, repo.partition("/")[2], source.provider,
            f"https://huggingface.co/{repo}",
            pipeline_tag=_text(front.get("pipeline_tag")),
            tags=tags,
            base_model=_text(lineage.get("base_model")),
        )
        reason = _hub_scope_reason(seen, source)
        if reason:
            rejected[model_id] = reason
    return rejected


def test_catalogue_cards_under_huggingface_labs_stay_in_scope() -> None:
    source = Source(
        "hf-acme", "huggingface",
        "https://huggingface.co/api/models?author=acme-lab", 0.7, provider="Acme",
    )

    def decide(repo: str, name: str, **fields: object) -> str | None:
        return _hub_scope_reason(Seen(
            repo, name, "Acme", f"https://huggingface.co/{repo}", **fields,
        ), source)

    assert decide(
        "acme-lab/orbit-1-sparse", "orbit-1-sparse",
        pipeline_tag="text-generation", base_model="other-lab/Orbit-1",
    ) == "derivative of other-lab/Orbit-1"
    assert decide("acme-lab/walker", "walker", pipeline_tag="robotics") == "robotics"
    assert decide(
        "acme-lab/pong", "pong", pipeline_tag="reinforcement-learning",
    ) == "reinforcement-learning"
    assert _catalogue_scope_rejections() == _CATALOGUE_SCOPE_EXCEPTIONS


# Whole tags only. Matched after the same fold the scope module already uses.
_INTERPRETABILITY_ARTEFACT_TAGS = (
    "interpretability",
    "mechanistic-interpretability",
    "transcoder",
    "cross-layer-transcoder",
    "sparse-autoencoder",
    "sparse-autoencoders",
    "sae",
    "saelens",
    "sae-lens",
    "crosscoder",
)


def _artefact(tag: str) -> TagDecision:
    return TagDecision(True, f"interpretability artefact (tag: {tag})", tag)


@pytest.mark.parametrize("tag", _INTERPRETABILITY_ARTEFACT_TAGS)
def test_interpretability_artefact_tags_are_out_of_scope(tag: str) -> None:
    decision = _artefact(tag)
    assert tag_scope("feature-extraction", (tag,)) == decision
    assert tag_scope(None, (tag,)) == decision
    assert tag_scope("", (tag,)) == decision
    assert tag_scope("  ", (tag,)) == decision


def test_an_in_scope_pipeline_tag_keeps_a_card_that_mentions_interpretability() -> None:
    assert tag_scope("text-generation", ("interpretability",)) == TagDecision(
        True, None, "text-generation",
    )
    assert tag_scope("image-text-to-text", ("transcoder", "sae")) == TagDecision(
        True, None, "image-text-to-text",
    )
    assert tag_scope("text_generation", ("interpretability",)) == TagDecision(
        True, None, "text_generation",
    )
    assert tag_scope("text-to-speech", ("feature-extraction", "transcoder")) == TagDecision(
        True, None, "feature-extraction",
    )


def test_feature_extraction_without_an_artefact_tag_stays_in_scope() -> None:
    assert tag_scope("feature-extraction") == TagDecision(True, None, "feature-extraction")
    assert tag_scope("feature-extraction", ("en", "transformers", "license:mit")) == TagDecision(
        True, None, "feature-extraction",
    )


@pytest.mark.parametrize("tag", ("sae-j3016", "disaese", "my-sae-lens", "transcoder-v2"))
def test_a_tag_that_only_contains_an_artefact_word_stays_in_scope(tag: str) -> None:
    assert tag_scope("feature-extraction", (tag,)) == TagDecision(
        True, None, "feature-extraction",
    )
    assert tag_scope(None, (tag,)) == TagDecision(False)


def test_artefact_tags_fold_case_and_underscores() -> None:
    assert tag_scope("Feature-Extraction", ("Transcoder",)) == _artefact("Transcoder")
    assert tag_scope("Feature_Extraction", ("interpretability",)) == _artefact("interpretability")
    assert tag_scope(None, ("SPARSE_AUTOENCODER",)) == _artefact("SPARSE_AUTOENCODER")
    assert tag_scope("feature-extraction", ("  SAE-Lens  ",)) == _artefact("SAE-Lens")
    assert tag_scope(None, ("feature-extraction", "cross_layer_transcoder")) == _artefact(
        "cross_layer_transcoder",
    )
    assert tag_scope("feature-extraction", ("cross_coder",)) == TagDecision(
        True, None, "feature-extraction",
    )


def test_a_keeping_task_tag_does_not_keep_an_interpretability_artefact() -> None:
    assert tag_scope(
        "feature-extraction", ("text-generation", "transcoder"),
    ) == _artefact("transcoder")
    assert tag_scope(None, ("feature-extraction", "crosscoder")) == _artefact("crosscoder")


def test_artefact_tags_survive_relevant_hub_tags() -> None:
    raw = [
        "transformers",
        "license:mit",
        "en",
        "arxiv:1234.5678",
        "feature-extraction",
        "base_model:finetune:other-lab/Orbit-1",
        *_INTERPRETABILITY_ARTEFACT_TAGS,
        "SPARSE_AUTOENCODER",
    ]
    kept = relevant_hub_tags(raw, "transformers", "feature-extraction")
    for tag in (*_INTERPRETABILITY_ARTEFACT_TAGS, "SPARSE_AUTOENCODER"):
        assert tag in kept
    assert "license:mit" not in kept
    assert "en" not in kept
    assert "arxiv:1234.5678" not in kept
    pipeline, tags, base, bases = hub_metadata(
        {
            "pipeline_tag": "feature-extraction",
            "library_name": "transformers",
            "tags": [
                "transformers",
                "feature-extraction",
                "interpretability",
                "transcoder",
                "license:mit",
                "en",
                "arxiv:1234.5678",
                "base_model:other-lab/Orbit-1",
                "base_model:finetune:other-lab/Orbit-1",
            ],
        },
        "acme-lab/probe",
    )
    assert pipeline == "feature-extraction"
    assert "transcoder" in tags
    assert "license:mit" not in tags
    assert base == "other-lab/Orbit-1"
    assert bases == ("other-lab/Orbit-1",)
    assert tag_scope(pipeline, tags) == _artefact("interpretability")


def test_the_watcher_reports_an_interpretability_artefact() -> None:
    source = Source(
        "hf-acme", "huggingface",
        "https://huggingface.co/api/models?author=acme-lab", 0.7, provider="Acme",
    )
    assert _hub_scope_reason(Seen(
        "acme-lab/probe", "probe", "Acme", "https://huggingface.co/acme-lab/probe",
        pipeline_tag="feature-extraction", tags=("transformers", "transcoder"),
    ), source) == "interpretability artefact (tag: transcoder)"
    assert _hub_scope_reason(Seen(
        "acme-lab/orbit", "orbit", "Acme", "https://huggingface.co/acme-lab/orbit",
        pipeline_tag="text-generation", tags=("text-generation", "interpretability"),
    ), source) is None
    assert _hub_scope_reason(Seen(
        "acme-lab/embed", "embed", "Acme", "https://huggingface.co/acme-lab/embed",
        pipeline_tag="feature-extraction", tags=("transformers", "feature-extraction"),
    ), source) is None
