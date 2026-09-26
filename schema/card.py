"""ModelSpec Universal Model Card Schema — V3

Pydantic models for every section of the model intelligence card.
This is the source of truth. The YAML template, graph ingestion,
API responses, and CLI output all derive from these models.

Usage:
    from schema.card import ModelCard
    card = ModelCard.from_yaml("models/qwen/qwen3-30b-a3b.md")
    card.validate()
    print(card.applicable_field_coverage)
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import date, datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, ClassVar, Literal

import yaml
from pydantic import BaseModel, Field, computed_field, field_validator, model_validator

from .applicability import FIELD_RULES, model_types
from .enums import (
    ArchitectureType,
    AttentionType,
    BaseModelRelation,
    BenchmarkCategory,
    ConfidenceLevel,
    DisclosureState,
    EUAIActRisk,
    EvalStatus,
    LicenseType,
    ModelStatus,
    ModelType,
    Modality,
    OrgType,
    PlatformCategory,
    PositionalEncoding,
    QuantFormat,
    ResistanceLevel,
    RiskTier,
    Tier,
    TokenizerType,
    TrainingMethod,
    UsePermission,
)


# ═══════════════════════════════════════════════════════════════
# Section 1: Identity
# ═══════════════════════════════════════════════════════════════

class Identity(BaseModel):
    model_id: str = Field(..., description="Canonical ID: provider/model-name")
    display_name: str
    provider: str = Field(..., description="Provider slug (lowercase)")
    provider_display: str = ""
    family: str = ""
    version: str = ""
    release_date: str = ""
    last_updated: str = ""
    status: ModelStatus = ModelStatus.ACTIVE
    model_type: ModelType | None = None
    model_subtypes: list[ModelType] = []
    tags: list[str] = []
    pipeline_tag: str = ""


# ═══════════════════════════════════════════════════════════════
# Section 2: Architecture
# ═══════════════════════════════════════════════════════════════

class Architecture(BaseModel):
    type: ArchitectureType | None = None
    total_parameters: int | None = None
    #: How `total_parameters` was obtained. `safetensors` is an exact Hub
    #: count; values starting `model_card_published:` are a README figure.
    #: Empty means unknown — either still null, or a legacy fill.
    total_parameters_source: str = ""
    active_parameters: int | None = None
    num_experts: int | None = None
    experts_per_token: int | None = None
    num_layers: int | None = None
    hidden_size: int | None = None
    intermediate_size: int | None = None
    attention_type: AttentionType | None = None
    num_attention_heads: int | None = None
    num_kv_heads: int | None = None
    positional_encoding: PositionalEncoding | None = None
    rope_theta: float | None = None
    vocab_size: int | None = None
    tokenizer_type: TokenizerType | None = None
    embedding_dimensions: int | None = None
    activation_function: str = ""
    precision_native: str = ""
    flash_attention: bool | None = None
    tie_word_embeddings: bool | None = None
    sliding_window_size: int | None = None
    # Vision encoder
    vision_encoder: str = ""
    vision_resolution_max: str = ""
    vision_patch_size: int | None = None
    # Diffusion
    diffusion_scheduler: str = ""
    diffusion_steps_default: int | None = None
    vae_type: str = ""

    @model_validator(mode="after")
    def _active_cannot_exceed_total(self) -> Architecture:
        """A stored active count larger than the stored total is a catalogue bug.

        That is how Mixtral-8x7B and GLM-4.5 were filed as 7B / 9B and told they
        fitted on hardware that cannot hold the weights. Null on either side
        stays legal — unknown is not a contradiction.
        """
        if (
            self.active_parameters is not None
            and self.total_parameters is not None
            and self.active_parameters > self.total_parameters
        ):
            raise ValueError(
                f"active_parameters ({self.active_parameters}) exceeds "
                f"total_parameters ({self.total_parameters})"
            )
        return self


# ═══════════════════════════════════════════════════════════════
# Section 3: Lineage
# ═══════════════════════════════════════════════════════════════

class Lineage(BaseModel):
    base_model: str = ""
    base_model_relation: BaseModelRelation | None = None
    merge_models: list[str] = []
    adapter_type: str = ""
    adapter_rank: int | None = None
    training_datasets: list[str] = []
    training_data_tokens: int | None = None
    training_data_cutoff: str = ""
    training_compute_flops: float | None = None
    training_hardware: str = ""
    training_time: str = ""
    training_cost_estimate: str = ""
    training_method: TrainingMethod | None = None
    co2_emissions_kg: float | None = None
    co2_source: str = ""
    energy_kwh: float | None = None
    library_name: str = ""


# ═══════════════════════════════════════════════════════════════
# Section 4: Licensing
# ═══════════════════════════════════════════════════════════════

#: Source kinds a policy determination may cite. `legacy-import` is the one
#: kind that is *not* evidence: see `PolicySource` below.
PolicySourceKind = Literal[
    "license",
    "terms_of_service",
    "acceptable_use_policy",
    "provider_documentation",
    "provider_statement",
    "legacy-import",
]


class PolicySource(BaseModel):
    """The document a policy determination was read from, and the day it was read.

    A policy answer is only worth anything if the reader can go and check it,
    and licences are rewritten without notice — so the date is as load-bearing
    as the URL. This mirrors `BenchmarkEvidence`: everything needed to recheck
    the claim, or it is not a claim.

    `legacy-import` is the single exception and it is deliberately ugly. Eight
    cards carried `commercial_use: true` with no citation from before this
    shape existed. Discarding those values would lose information; dressing
    them up with a plausible licence URL would manufacture evidence that was
    never read. So they keep the value and carry a source that says, in the
    published JSON, that nobody cited anything — the same thing
    `evidence_basis: unverified-legacy` says about benchmark scores. It is
    frozen to those eight by
    `tests/test_policy_shape.py::test_legacy_import_is_frozen_to_the_migrated_eight`;
    a ninth card cannot quietly use it.
    """

    kind: PolicySourceKind
    url: str = ""
    #: The day the document at `url` was read. ISO `YYYY-MM-DD`.
    read_on: str = ""
    #: Optional. The operative clause, verbatim and short, so a reader can see
    #: what the determination was made from without refetching the document.
    quote: str = ""

    @model_validator(mode="after")
    def _evidence_or_an_admission(self) -> PolicySource:
        if self.kind == "legacy-import":
            if self.url or self.read_on or self.quote:
                raise ValueError(
                    "a legacy-import source is the admission that nothing was "
                    "cited; it cannot carry a url, a read date or a quote. "
                    "If a document was actually read, cite it with a real kind."
                )
            return self
        if not self.url.startswith(("http://", "https://")):
            raise ValueError(
                "url must be the document the determination was read from; "
                "a policy answer without one cannot be rechecked"
            )
        try:
            date.fromisoformat(self.read_on)
        except ValueError as exc:
            raise ValueError(
                f"read_on must be the exact ISO date the document was read, "
                f"got {self.read_on!r}. Licence terms change; an undated "
                f"reading cannot be trusted later."
            ) from exc
        return self

    @property
    def is_evidence(self) -> bool:
        """False for `legacy-import`, which is a value with no citation."""
        return self.kind != "legacy-import"


#: The `commercial_use` values that assert something about the world, and so
#: require a source. `UNSPECIFIED` and `WITHHELD` assert nothing about the
#: licence — they describe this file's contents.
DETERMINED_PERMISSIONS = frozenset({
    UsePermission.ALLOWED,
    UsePermission.RESTRICTED,
    UsePermission.PROHIBITED,
})


class Licensing(BaseModel):
    open_weights: bool = False
    license_type: LicenseType | None = None
    license_url: str = ""
    tos_url: str = ""
    acceptable_use_policy_url: str = ""
    not_for_all_audiences: bool = False
    #: Was `bool | None` until MODEL-77, which could not express the answer for
    #: 169 cards whose licence grants commercial use *up to a threshold*
    #: (llama-community, gemma, deepseek). That is neither true nor false; it
    #: is `restricted`, with the threshold in `commercial_use_conditions`.
    commercial_use: UsePermission = UsePermission.UNSPECIFIED
    #: Required whenever `commercial_use` is a determination; forbidden when it
    #: is not, so an empty value can never look sourced.
    commercial_use_source: PolicySource | None = None
    #: Where a `restricted` grant's condition lives: one short line stating the
    #: threshold or carve-out ("free below 700M MAU; a licence is required
    #: above it"), not prose buried in the card body where no consumer reads it.
    commercial_use_conditions: str = ""
    defense_use: UsePermission = UsePermission.UNSPECIFIED
    government_use: UsePermission = UsePermission.UNSPECIFIED
    medical_use: UsePermission = UsePermission.UNSPECIFIED
    academic_use: UsePermission = UsePermission.UNSPECIFIED
    geographic_restrictions: list[str] = []
    export_control_notes: str = ""
    origin_country: str = ""
    origin_org_type: OrgType | None = None

    @field_validator("commercial_use", mode="before")
    @classmethod
    def _reject_the_old_boolean(cls, value: Any) -> Any:
        """A pre-MODEL-77 card fails loudly rather than being guessed at.

        `True`/`False` are not silently mapped: `False` in particular could
        have meant "prohibited" or "restricted in a way the author could not
        express", and picking one would invent a determination.
        """
        if isinstance(value, bool):
            raise ValueError(
                "commercial_use is a UsePermission since MODEL-77, not a bool. "
                "true became 'allowed'; false is ambiguous between 'prohibited' "
                "and 'restricted' and must be re-read from the licence."
            )
        if value is None:
            raise ValueError(
                "commercial_use is no longer nullable: use 'unspecified' for "
                "not-yet-researched, or 'withheld' for determined-not-published."
            )
        return value

    @model_validator(mode="after")
    def _a_determination_carries_its_source(self) -> Licensing:
        determined = self.commercial_use in DETERMINED_PERMISSIONS
        if determined and self.commercial_use_source is None:
            raise ValueError(
                f"commercial_use is {self.commercial_use.value!r} with no "
                "commercial_use_source. Standing rule 1: an uncited policy "
                "answer is not an answer."
            )
        if not determined and self.commercial_use_source is not None:
            raise ValueError(
                f"commercial_use is {self.commercial_use.value!r} but carries a "
                "commercial_use_source. Nothing has been published to cite; a "
                "withheld determination keeps its source in the enrichment "
                "record, not on the public card."
            )
        if self.commercial_use is UsePermission.RESTRICTED and not self.commercial_use_conditions.strip():
            raise ValueError(
                "commercial_use is 'restricted' with no commercial_use_conditions. "
                "'Restricted' without the restriction is unusable: it is the "
                "condition that tells a reader whether they are inside it."
            )
        if self.commercial_use is not UsePermission.RESTRICTED and self.commercial_use_conditions.strip():
            raise ValueError(
                f"commercial_use is {self.commercial_use.value!r} but carries "
                "commercial_use_conditions. Conditions belong to a restricted "
                "grant; anywhere else they contradict the value."
            )
        return self


# ═══════════════════════════════════════════════════════════════
# Section 5: Modalities
# ═══════════════════════════════════════════════════════════════
#
# Nested modality and capability models declare ``__applicable_model_types__``.
# ``ModelCard.applicable_field_coverage`` counts a nested section only when the
# card's ``model_type`` (or a ``model_subtype``) is in that set. Sections with
# no declaration count for every type. The field *sets* are the nested models'
# own fields — not a hand list of paths.


#: Shared with the field-level table in `schema/applicability.py`, which is the
#: same idea one level down: sections here, named fields there.
_model_types = model_types


_LLM_TYPES = _model_types("llm-")
_EMBEDDING_TYPES = _model_types("embedding-")
_AUDIO_TYPES = _model_types("audio-")
_IMAGE_TYPES = _model_types("image-generation", "image-editing")
#: `decision-model` (MODEL-98) reads text state, so `max_input_tokens` and
#: `context_window` are real questions for it. It is deliberately absent from
#: `_GENERATIVE_TEXT_TYPES` below — it writes no text — and the output-shaped
#: fields inside this subtree are excluded field by field in
#: `schema/applicability.py`, which is finer than a whole-section gate can be.
_TEXT_TYPES = _LLM_TYPES | _model_types(
    "vlm", "agent-model", "medical", "legal", "financial",
    "router", "reward-model", "safety-classifier", "text-encoder", "document-ocr",
    "decision-model",
)
_GENERATIVE_TEXT_TYPES = _LLM_TYPES | _model_types(
    "vlm", "agent-model", "medical", "legal", "financial",
    "router", "reward-model", "safety-classifier",
)
_VISION_TYPES = _IMAGE_TYPES | _model_types(
    "vlm", "vision-encoder", "document-ocr", "embedding-multimodal",
)


class VisionDetail(BaseModel):
    __applicable_model_types__: ClassVar[frozenset[ModelType]] = _VISION_TYPES
    supported: bool = False
    ocr: bool = False
    chart_reading: bool = False
    spatial_reasoning: bool = False
    handwriting: bool = False
    object_detection: bool = False
    object_counting: bool = False
    visual_grounding: bool = False
    max_image_resolution: str = ""
    max_images_per_request: int | None = None
    video_frames: bool = False


class AudioDetail(BaseModel):
    __applicable_model_types__: ClassVar[frozenset[ModelType]] = _AUDIO_TYPES
    input_supported: bool = False
    output_supported: bool = False
    realtime_streaming: bool = False
    asr_languages: list[str] = []
    tts_languages: list[str] = []
    tts_voices: int | None = None
    voice_cloning: bool = False
    speaker_diarization: bool = False
    music_understanding: bool = False
    music_generation: bool = False
    max_audio_duration_sec: int | None = None


class VideoDetail(BaseModel):
    __applicable_model_types__: ClassVar[frozenset[ModelType]] = _model_types("video-generation")
    input_supported: bool = False
    output_supported: bool = False
    max_input_duration_sec: int | None = None
    max_output_duration_sec: int | None = None
    max_resolution: str = ""
    max_fps: int | None = None
    audio_sync: bool = False
    temporal_reasoning: bool = False


class DocumentDetail(BaseModel):
    __applicable_model_types__: ClassVar[frozenset[ModelType]] = _model_types(
        "document-ocr", "vlm",
    )
    pdf_native: bool = False
    table_extraction: bool = False
    form_understanding: bool = False
    max_pages: int | None = None
    layout_analysis: bool = False


class ImageGenDetail(BaseModel):
    __applicable_model_types__: ClassVar[frozenset[ModelType]] = _IMAGE_TYPES
    supported: bool = False
    max_resolution: str = ""
    aspect_ratios: list[str] = []
    inpainting: bool = False
    outpainting: bool = False
    img2img: bool = False
    text_rendering_quality: str = ""
    style_control: bool = False
    controlnet_support: bool = False
    lora_support: bool = False


class EmbeddingDetail(BaseModel):
    __applicable_model_types__: ClassVar[frozenset[ModelType]] = _EMBEDDING_TYPES
    supported: bool = False
    dimensions: int | None = None
    dimensions_configurable: bool = False
    dimension_options: list[int] = []
    max_input_tokens: int | None = None
    similarity_metric: str = ""
    normalized: bool | None = None
    batch_size_max: int | None = None
    instruction_aware: bool = False


class RerankingDetail(BaseModel):
    __applicable_model_types__: ClassVar[frozenset[ModelType]] = _model_types("reranker")
    supported: bool = False
    max_input_pairs: int | None = None
    max_input_length: int | None = None
    cross_encoder: bool | None = None


class TextDetail(BaseModel):
    __applicable_model_types__: ClassVar[frozenset[ModelType]] = _TEXT_TYPES
    max_input_tokens: int | None = None
    max_output_tokens: int | None = None
    context_window: int | None = None
    streaming: bool | None = None
    fill_in_middle: bool | None = None
    json_mode: bool | None = None
    system_prompt: bool | None = None


class Modalities(BaseModel):
    input: list[Modality] = []
    output: list[Modality] = []
    text: TextDetail = TextDetail()
    vision: VisionDetail = VisionDetail()
    audio: AudioDetail = AudioDetail()
    video: VideoDetail = VideoDetail()
    document: DocumentDetail = DocumentDetail()
    image_generation: ImageGenDetail = ImageGenDetail()
    embeddings: EmbeddingDetail = EmbeddingDetail()
    reranking: RerankingDetail = RerankingDetail()


# ═══════════════════════════════════════════════════════════════
# Section 6: Capabilities
# ═══════════════════════════════════════════════════════════════

class CodingCapability(BaseModel):
    overall: Tier | None = None
    languages: list[str] = []
    agentic_coding: bool = False
    code_review: bool = False
    refactoring: bool = False
    debugging: bool = False
    test_generation: bool = False
    documentation: bool = False
    code_completion: bool = False
    multi_file_editing: bool = False
    fill_in_middle: bool = False
    lsp_integration: bool = False
    repository_understanding: bool = False


class ReasoningCapability(BaseModel):
    overall: Tier | None = None
    mathematical: bool = False
    logical: bool = False
    scientific: bool = False
    planning: bool = False
    multi_step: bool = False
    chain_of_thought: bool = False
    self_correction: bool = False
    spatial: bool = False
    temporal: bool = False
    causal: bool = False
    think_budget_control: bool = False


class ToolUseCapability(BaseModel):
    overall: Tier | None = None
    function_calling: bool = False
    mcp_compatible: bool = False
    parallel_tool_calls: bool = False
    tool_selection_accuracy: ConfidenceLevel | None = None
    multi_turn_tool_use: bool = False
    tool_error_recovery: bool = False
    computer_use: bool = False


class LanguageCapability(BaseModel):
    multilingual: bool = False
    num_languages: int | None = None
    strong_languages: list[str] = []
    translation_quality: Tier | None = None
    long_context_retrieval: Tier | None = None


class CreativeCapability(BaseModel):
    writing: Tier | None = None
    summarization: Tier | None = None
    instruction_following: Tier | None = None
    storytelling: Tier | None = None
    technical_writing: Tier | None = None


class SafetyAlignment(BaseModel):
    alignment_approach: str = ""
    refusal_rate: ConfidenceLevel | None = None
    jailbreak_resistance: ConfidenceLevel | None = None
    content_safety_tier: Tier | None = None
    guardrail_builtin: bool = False


class DomainCapability(BaseModel):
    medical_knowledge: Tier | None = None
    legal_knowledge: Tier | None = None
    financial_knowledge: Tier | None = None
    scientific_knowledge: Tier | None = None


class AgentCapability(BaseModel):
    autonomous_execution: bool = False
    web_browsing: bool = False
    file_system_access: bool = False
    code_execution: bool = False
    long_running_tasks: bool = False
    memory_management: bool = False
    self_delegation: bool = False


class Capabilities(BaseModel):
    __applicable_model_types__: ClassVar[frozenset[ModelType]] = _GENERATIVE_TEXT_TYPES
    coding: CodingCapability = CodingCapability()
    reasoning: ReasoningCapability = ReasoningCapability()
    tool_use: ToolUseCapability = ToolUseCapability()
    language: LanguageCapability = LanguageCapability()
    creative: CreativeCapability = CreativeCapability()
    safety_alignment: SafetyAlignment = SafetyAlignment()
    domain_specific: DomainCapability = DomainCapability()
    agent_capabilities: AgentCapability = AgentCapability()


# ═══════════════════════════════════════════════════════════════
# Section 7: Cost
# ═══════════════════════════════════════════════════════════════

class Cost(BaseModel):
    input: float | None = None
    output: float | None = None
    reasoning: float | None = None
    cache_read: float | None = None
    cache_write: float | None = None
    input_audio: float | None = None
    output_audio: float | None = None
    input_image: float | None = None
    output_image: float | None = None
    output_video_per_sec: float | None = None
    batch_input: float | None = None
    batch_output: float | None = None
    embedding_per_million: float | None = None
    reranking_per_million: float | None = None
    finetune_per_million_tokens: float | None = None
    finetune_hosting_per_hour: float | None = None
    free_tier: bool = False
    free_tier_limits: str = ""
    note: str = ""


# ═══════════════════════════════════════════════════════════════
# Section 8: Availability
# ═══════════════════════════════════════════════════════════════

class PlatformEntry(BaseModel):
    """A single platform where a model may be available."""
    available: bool = False
    model_id: str = ""
    url: str = ""
    fine_tuning: bool = False
    gated: bool = False
    regions: list[str] = []
    notes: str = ""


class PrimaryProvider(BaseModel):
    name: str = ""
    platform_url: str = ""
    api_endpoint: str = ""
    npm_package: str = ""
    env_vars: list[str] = []
    model_id_on_platform: str = ""
    rate_limit_rpm: int | None = None
    rate_limit_tpm: int | None = None
    sla_uptime: str = ""
    regions: list[str] = []
    #: Where the provider commits to processing data. `null` until it is a
    #: determination — see `data_residency_disclosure`. Was `list[str] = []`
    #: until MODEL-77, where the default was indistinguishable from an answer
    #: and sat on all 1,339 cards while being researched on none of them.
    data_residency: list[str] | None = None
    data_residency_disclosure: DisclosureState = DisclosureState.UNRESEARCHED
    #: Required when the disclosure is `published`; forbidden otherwise, for
    #: the same reason as `commercial_use_source`.
    data_residency_source: PolicySource | None = None
    hipaa_eligible: bool = False
    fedramp_authorized: bool = False
    soc2_compliant: bool = False
    free_tier: bool = False
    free_tier_details: str = ""

    @model_validator(mode="after")
    def _residency_states_are_not_interchangeable(self) -> PrimaryProvider:
        state = self.data_residency_disclosure
        if state is DisclosureState.PUBLISHED:
            if self.data_residency is None:
                raise ValueError(
                    "data_residency_disclosure is 'published' but data_residency "
                    "is null. An empty list is a legitimate published answer "
                    "('no residency commitment'); null is not an answer at all."
                )
            if self.data_residency_source is None:
                raise ValueError(
                    "data_residency is published with no data_residency_source. "
                    "Standing rule 1: an uncited policy answer is not an answer."
                )
            return self
        if self.data_residency is not None:
            raise ValueError(
                f"data_residency_disclosure is {state.value!r} but data_residency "
                "carries a value. Only a published determination has one; set "
                "the disclosure to 'published' and cite it, or clear the value."
            )
        if self.data_residency_source is not None:
            raise ValueError(
                f"data_residency_disclosure is {state.value!r} but carries a "
                "data_residency_source. Nothing has been published to cite."
            )
        return self


class Availability(BaseModel):
    primary_provider: PrimaryProvider = PrimaryProvider()
    # Cloud platforms
    aws_bedrock: PlatformEntry = PlatformEntry(url="https://aws.amazon.com/bedrock/")
    azure_ai_foundry: PlatformEntry = PlatformEntry(url="https://ai.azure.com/")
    google_vertex_ai: PlatformEntry = PlatformEntry(url="https://cloud.google.com/vertex-ai")
    nvidia_nim: PlatformEntry = PlatformEntry(url="https://build.nvidia.com/")
    ibm_watsonx: PlatformEntry = PlatformEntry(url="https://www.ibm.com/watsonx")
    snowflake_cortex: PlatformEntry = PlatformEntry(url="https://www.snowflake.com/en/data-cloud/cortex/")
    # Inference providers
    groq: PlatformEntry = PlatformEntry(url="https://groq.com/")
    together_ai: PlatformEntry = PlatformEntry(url="https://www.together.ai/")
    fireworks_ai: PlatformEntry = PlatformEntry(url="https://fireworks.ai/")
    replicate: PlatformEntry = PlatformEntry(url="https://replicate.com/")
    deepinfra: PlatformEntry = PlatformEntry(url="https://deepinfra.com/")
    cerebras: PlatformEntry = PlatformEntry(url="https://www.cerebras.ai/")
    sambanova: PlatformEntry = PlatformEntry(url="https://sambanova.ai/")
    # Aggregators
    openrouter: PlatformEntry = PlatformEntry(url="https://openrouter.ai/")
    # AI apps
    cursor: PlatformEntry = PlatformEntry(url="https://cursor.com/")
    github_copilot: PlatformEntry = PlatformEntry(url="https://github.com/features/copilot")
    perplexity: PlatformEntry = PlatformEntry(url="https://www.perplexity.ai/")
    raycast: PlatformEntry = PlatformEntry(url="https://www.raycast.com/")
    poe: PlatformEntry = PlatformEntry(url="https://poe.com/")
    # Consumer chat
    chatgpt: PlatformEntry = PlatformEntry(url="https://chat.openai.com/")
    claude_ai: PlatformEntry = PlatformEntry(url="https://claude.ai/")
    gemini_app: PlatformEntry = PlatformEntry(url="https://gemini.google.com/")
    grok_xai: PlatformEntry = PlatformEntry(url="https://x.ai/")
    meta_ai: PlatformEntry = PlatformEntry(url="https://www.meta.ai/")
    copilot_microsoft: PlatformEntry = PlatformEntry(url="https://copilot.microsoft.com/")
    # Provider platforms
    mistral_plateforme: PlatformEntry = PlatformEntry(url="https://console.mistral.ai/")
    cohere: PlatformEntry = PlatformEntry(url="https://cohere.com/")
    ai21_labs: PlatformEntry = PlatformEntry(url="https://www.ai21.com/")
    stability_ai: PlatformEntry = PlatformEntry(url="https://stability.ai/")
    # Chinese platforms
    deepseek: PlatformEntry = PlatformEntry(url="https://platform.deepseek.com/")
    qwen_alibaba: PlatformEntry = PlatformEntry(url="https://www.alibabacloud.com/en/solutions/generative-ai/qwen")
    baidu_ernie: PlatformEntry = PlatformEntry(url="https://cloud.baidu.com/")
    bytedance_doubao: PlatformEntry = PlatformEntry(url="https://www.volcengine.com/")
    tencent_hunyuan: PlatformEntry = PlatformEntry(url="https://cloud.tencent.com/")
    zhipu_glm: PlatformEntry = PlatformEntry(url="https://www.zhipuai.cn/")
    moonshot_kimi: PlatformEntry = PlatformEntry(url="https://www.moonshot.cn/")
    minimax: PlatformEntry = PlatformEntry(url="https://www.minimax.chat/")
    zero_one_ai: PlatformEntry = PlatformEntry(url="https://www.01.ai/")
    # Regional
    tii_falcon: PlatformEntry = PlatformEntry(url="https://falconllm.tii.ae/")
    samsung_gauss: PlatformEntry = PlatformEntry(url="https://www.samsung.com/")
    upstage_solar: PlatformEntry = PlatformEntry(url="https://www.upstage.ai/")
    # Local
    ollama: PlatformEntry = PlatformEntry(url="https://ollama.com/")
    lm_studio: PlatformEntry = PlatformEntry(url="https://lmstudio.ai/")
    gpt4all: PlatformEntry = PlatformEntry(url="https://gpt4all.io/")
    jan_ai: PlatformEntry = PlatformEntry(url="https://jan.ai/")
    mlx_community: PlatformEntry = PlatformEntry(url="https://huggingface.co/mlx-community")
    open_webui: PlatformEntry = PlatformEntry(url="https://openwebui.com/")
    # Model hubs
    huggingface: PlatformEntry = PlatformEntry(url="https://huggingface.co/")
    modelscope: PlatformEntry = PlatformEntry(url="https://modelscope.cn/")
    kaggle_models: PlatformEntry = PlatformEntry(url="https://www.kaggle.com/models")
    # Overflow
    other_platforms: list[PlatformEntry] = []

    def platforms_available(self) -> list[str]:
        """Return names of all platforms where this model is available."""
        available = []
        for field_name, field_value in self:
            if isinstance(field_value, PlatformEntry) and field_value.available:
                available.append(field_name)
        return available


# ═══════════════════════════════════════════════════════════════
# Section 9: Benchmarks
# ═══════════════════════════════════════════════════════════════

class BenchmarkEvidence(BaseModel):
    """One score, with everything needed to check it.

    The flat `scores` dict below carries one collection date for a whole card
    and a comma-joined source list, so no individual number can be attributed,
    dated or rechecked. This record is the shape the benchmark catalogue's
    evidence contract requires, and it mirrors the census evidence ledger so the
    two can be reconciled rather than diverging.

    Every field here is required. A record that cannot say where a number came
    from or when is not evidence, and admitting a partial one would quietly
    reintroduce exactly the problem this replaces.
    """

    benchmark_id: str
    model_id_as_evaluated: str
    score: float
    unit: str
    source_url: str
    #: benchmark author, independent evaluator, or the provider's own claim.
    #: Provider self-report is legitimate and must be visibly distinguishable.
    source_kind: Literal["benchmark_author", "independent_evaluator", "provider_self_report"]
    evidence_date: str
    #: `evaluated` when the run date is disclosed; `published` when only the
    #: publication date is. Never infer a run date from a retrieval timestamp.
    date_type: Literal["evaluated", "published"]
    verified_at: str
    benchmark_version: str = ""
    configuration: str = ""
    limitations: str = ""
    #: A published uncertainty interval on the same scale as ``score``.
    interval: tuple[float, float] | None = None
    #: The published observation count behind the measurement, when disclosed.
    n: int | None = Field(default=None, ge=1)
    #: Structured reasons this measurement is not a clean direct answer.
    quality_flags: list[Literal["deprecated", "contamination_warning"]] = Field(
        default_factory=list
    )

    @field_validator("source_url")
    @classmethod
    def _url_must_be_real(cls, value: str) -> str:
        if not value.startswith(("http://", "https://")):
            raise ValueError("source_url must be a URL; a score without one is not evidence")
        return value

    @field_validator("evidence_date", "verified_at")
    @classmethod
    def _dates_must_be_iso(cls, value: str) -> str:
        from datetime import date as _date
        try:
            _date.fromisoformat(value)
        except ValueError as exc:
            raise ValueError(f"must be an exact ISO date YYYY-MM-DD, got {value!r}") from exc
        return value

    @model_validator(mode="after")
    def _valid_uncertainty_and_quality(self) -> BenchmarkEvidence:
        if self.interval is not None:
            low, high = self.interval
            if not all(float("-inf") < value < float("inf") for value in (low, high)):
                raise ValueError("interval bounds must be finite")
            if low > high:
                raise ValueError("interval lower bound must not exceed the upper bound")
            if not low <= self.score <= high:
                raise ValueError("evidence score must fall within its interval")
        if len(self.quality_flags) != len(set(self.quality_flags)):
            raise ValueError("quality_flags must not contain duplicates")
        return self


class Benchmarks(BaseModel):
    # All benchmark scores in a single open-ended dictionary.
    # Keys are benchmark identifiers (e.g. "humaneval", "mmlu_pro",
    # "multipl_e_rust", "mmlu_chemistry", "pubmedqa", "flores_en_zh").
    # No fixed schema — any benchmark can be added without code changes.
    #: V2 quarantine: the decision engine never reads benchmarks.scores.
    #: MODEL-118 re-sources these values; v1 retains its existing behavior.
    scores: dict[str, float] = {}

    #: Verified, per-score evidence. Everything in `scores` above that has no
    #: matching record here is unverified-legacy and must be presented as such.
    evidence: list[BenchmarkEvidence] = []

    # Meta. These describe `scores` only, and are the reason it cannot be
    # attributed: one date and one source list for the whole card.
    benchmark_source: str = ""
    benchmark_as_of: str = ""
    benchmark_notes: str = ""

    def filled_count(self) -> int:
        return len(self.scores)

    def verified_ids(self) -> set[str]:
        return {e.benchmark_id for e in self.evidence}

    def is_verified(self, benchmark_id: str) -> bool:
        return benchmark_id in self.verified_ids()


# ═══════════════════════════════════════════════════════════════
# Section 10: Hardware & Deployment
# ═══════════════════════════════════════════════════════════════

class HardwareProfile(BaseModel):
    fits: bool | None = None
    best_quant: str = ""
    vram_usage_gb: float | None = None
    ram_usage_gb: float | None = None
    tokens_per_sec: float | None = None
    prompt_tps: float | None = None
    ttft_ms: float | None = None
    max_context_at_quant: int | None = None
    inference_engine: str = ""
    notes: str = ""


class Runtimes(BaseModel):
    gguf: bool = False
    ollama: bool = False
    ollama_tag: str = ""
    lm_studio: bool = False
    vllm: bool = False
    trt_llm: bool = False
    mlx: bool = False
    llama_cpp: bool = False
    sglang: bool = False
    transformers: bool = False
    exllamav2: bool = False
    core_ml: bool = False
    onnx: bool = False
    triton: bool = False
    nim: bool = False


class Deployment(BaseModel):
    api_only: bool = False
    local_inference: bool = False
    self_hostable: bool = False
    fine_tuning_supported: bool = False
    fine_tuning_methods: list[str] = []
    quantizations_available: list[str] = []
    hardware_profiles: dict[str, HardwareProfile] = Field(default_factory=lambda: {
        "nvidia_5090_32gb": HardwareProfile(),
        "dgx_spark_128gb": HardwareProfile(),
        "macbook_m4_pro_64gb": HardwareProfile(),
        "macbook_air_m4_24gb": HardwareProfile(),
    })
    custom_hardware: list[HardwareProfile] = []
    runtimes: Runtimes = Runtimes()


# ═══════════════════════════════════════════════════════════════
# Section 11-14: Risk, Performance, Adoption, Downselect
# ═══════════════════════════════════════════════════════════════

class BiasEvaluation(BaseModel):
    conducted: bool = False
    methodology: str = ""
    results_summary: str = ""
    known_biases: list[str] = []


class PrivacyPosture(BaseModel):
    data_retention_policy: str = ""
    pii_handling: str = ""
    training_data_pii_scrubbed: bool | None = None
    data_processing_location: list[str] = []
    gdpr_compliant: bool | None = None
    hipaa_eligible: bool | None = None
    ccpa_compliant: bool | None = None


class SupplyChain(BaseModel):
    training_data_transparency: str = ""
    model_provenance_documented: bool = False
    third_party_dependencies: list[str] = []
    ai_bom_available: bool = False
    reproducible: bool = False


class RegulatoryAlignment(BaseModel):
    eu_ai_act_risk_level: EUAIActRisk | None = None
    nist_rmf_profile: str = ""
    iso_42001_certified: bool | None = None
    soc2_type2: bool | None = None
    fedramp_level: str = ""


class RiskGovernance(BaseModel):
    valid_and_reliable: str = ""
    safe: str = ""
    secure_and_resilient: str = ""
    accountable_and_transparent: str = ""
    explainable_and_interpretable: str = ""
    privacy_enhanced: str = ""
    fair_with_bias_managed: str = ""
    bias_evaluation: BiasEvaluation = BiasEvaluation()
    adversarial_robustness: ResistanceLevel = ResistanceLevel.UNTESTED
    privacy: PrivacyPosture = PrivacyPosture()
    supply_chain: SupplyChain = SupplyChain()
    incident_history: list[str] = []
    known_failure_modes: list[str] = []
    regulatory: RegulatoryAlignment = RegulatoryAlignment()


class InferencePerformance(BaseModel):
    api_latency_p50_ms: float | None = None
    api_latency_p99_ms: float | None = None
    api_ttft_ms: float | None = None
    api_tps_output: float | None = None
    api_tps_input: float | None = None
    context_speed_degradation: str = ""
    generation_time_sec: float | None = None
    quality_per_dollar: float | None = None
    quality_per_watt: float | None = None


class Adoption(BaseModel):
    huggingface_downloads: int | None = None
    huggingface_likes: int | None = None
    ollama_pulls: int | None = None
    community_forks: int | None = None
    is_common_distillation_teacher: bool = False
    is_common_finetune_base: bool = False
    openrouter_ranking: int | None = None
    open_webui_ranking: int | None = None
    notable_users: list[str] = []


class Downselect(BaseModel):
    compliance_tags: list[str] = []
    clearance_tags: list[str] = []
    defense_tags: list[str] = []
    sovereignty_tags: list[str] = []
    use_case_tags: list[str] = []
    eval_status: EvalStatus | None = None
    risk_tier: RiskTier | None = None
    cost_tier: str = ""
    custom_score: float | None = None
    custom_notes: str = ""
    reviewed_by: str = ""
    review_date: str = ""
    approval_authority: str = ""
    next_review_date: str = ""


# ═══════════════════════════════════════════════════════════════
# Section 15: Sources & Metadata
# ═══════════════════════════════════════════════════════════════

class Sources(BaseModel):
    models_dev_url: str = ""
    provider_docs_url: str = ""
    huggingface_url: str = ""
    arxiv_url: str = ""
    paper_url: str = ""
    github_url: str = ""
    ollama_url: str = ""
    artificial_analysis_url: str = ""
    arena_url: str = ""
    # Freshness tracking
    last_scraped_models_dev: str = ""
    last_scraped_huggingface: str = ""
    last_scraped_benchmarks: str = ""
    last_scraped_pricing: str = ""



# ═══════════════════════════════════════════════════════════════
# Section 16: Authoring Guide (MODEL-8)
# ═══════════════════════════════════════════════════════════════
#
# How to write for one model: what helps, what wastes tokens. Every claim is a
# short paraphrase of the provider's own guidance, dated and sourced. A guide is
# pinned to the card's `version` (the provider's API model string); when that
# changes, the guide must be re-reviewed or marked `stale`. Stale is never kept
# silently.

GuideSourceKind = Literal["provider-guidance", "system-card", "release-notes", "model-docs"]
GUIDE_SECTIONS = (
    "prompt_shape", "system_message", "reasoning_and_tools",
    "formatting", "failure_modes", "retry_advice",
)


def _iso_date(value: str, what: str) -> str:
    try:
        date.fromisoformat(str(value))
    except ValueError:
        raise ValueError(f"{what} must be an ISO date (YYYY-MM-DD), got {value!r}") from None
    return str(value)


class GuideSource(BaseModel):
    url: str
    title: str = ""
    accessed: str
    kind: GuideSourceKind

    @field_validator("url")
    @classmethod
    def _url_must_be_real(cls, value: str) -> str:
        if not str(value).startswith(("http://", "https://")):
            raise ValueError(f"guide source url must be http(s), got {value!r}")
        return value

    @field_validator("accessed", mode="before")
    @classmethod
    def _accessed_iso(cls, value: Any) -> str:
        return _iso_date(value, "guide source accessed")


class GuideClaim(BaseModel):
    text: str
    sources: list[GuideSource]

    @model_validator(mode="after")
    def _needs_source(self) -> "GuideClaim":
        if not self.text.strip():
            raise ValueError("guide claim text is empty")
        if not self.sources:
            raise ValueError(f"guide claim has no source: {self.text[:60]!r}")
        return self


class GuideAppliesTo(BaseModel):
    model_id: str
    version: str


class GuideSections(BaseModel):
    prompt_shape: list[GuideClaim] = []
    system_message: list[GuideClaim] = []
    reasoning_and_tools: list[GuideClaim] = []
    formatting: list[GuideClaim] = []
    failure_modes: list[GuideClaim] = []
    retry_advice: list[GuideClaim] = []


class AuthoringGuide(BaseModel):
    applies_to: GuideAppliesTo
    as_of: str
    status: Literal["current", "stale"]
    sections: GuideSections = GuideSections()

    @field_validator("as_of", mode="before")
    @classmethod
    def _as_of_iso(cls, value: Any) -> str:
        return _iso_date(value, "authoring_guide.as_of")


# ═══════════════════════════════════════════════════════════════
# THE COMPLETE MODEL CARD
# ═══════════════════════════════════════════════════════════════

class ModelCard(BaseModel):
    """Universal Model Intelligence Card — V3.

    This is the root object. It composes all sections into a single
    schema that covers every model type. Null fields = not yet researched.
    """
    # Sections
    identity: Identity
    architecture: Architecture = Architecture()
    lineage: Lineage = Lineage()
    licensing: Licensing = Licensing()
    modalities: Modalities = Modalities()
    capabilities: Capabilities = Capabilities()
    cost: Cost = Cost()
    availability: Availability = Availability()
    benchmarks: Benchmarks = Benchmarks()
    deployment: Deployment = Deployment()
    risk_governance: RiskGovernance = RiskGovernance()
    inference_performance: InferencePerformance = InferencePerformance()
    adoption: Adoption = Adoption()
    downselect: Downselect = Downselect()
    sources: Sources = Sources()
    # Optional, additive (MODEL-8). Absent guides serialize and count as before.
    authoring_guide: AuthoringGuide | None = None

    # Card metadata
    card_schema_version: str = "3.0"
    card_author: str = ""
    card_created: str = ""
    card_updated: str = ""
    prose_body: str = ""  # The markdown content below the YAML frontmatter

    @model_validator(mode="after")
    def _guide_matches_card(self) -> "ModelCard":
        guide = self.authoring_guide
        if guide is None:
            return self
        if guide.applies_to.model_id != self.identity.model_id:
            raise ValueError(
                f"authoring_guide.applies_to.model_id {guide.applies_to.model_id!r} "
                f"does not match card model_id {self.identity.model_id!r}")
        if guide.status != "stale" and guide.applies_to.version != self.identity.version:
            raise ValueError(
                f"authoring_guide was written for version {guide.applies_to.version!r} "
                f"but the card is now {self.identity.version!r}: re-review the guide "
                "against current provider guidance, or set status: stale")
        return self

    def _coverage_types(self) -> frozenset[ModelType]:
        types: set[ModelType] = set()
        ident = self.identity
        if ident.model_type is not None:
            types.add(ident.model_type)
        types.update(ident.model_subtypes)
        return frozenset(types)

    def _section_applies(self, obj: BaseModel) -> bool:
        applicable = getattr(type(obj), "__applicable_model_types__", None)
        if applicable is None:
            return True
        return bool(self._coverage_types() & applicable)

    def warnings(self) -> list[str]:
        """Non-fatal catalogue checks. CI reports these; they do not invalidate the card."""
        out: list[str] = []
        if (
            self.licensing.open_weights is True
            and self.licensing.license_type is LicenseType.PROPRIETARY
        ):
            out.append(
                "open_weights is true with license_type proprietary: "
                "a proprietary licence does not distribute downloadable weights"
            )
        return out

    @property
    def inapplicable_fields(self) -> tuple[str, ...]:
        """Dotted paths this card's *class* cannot answer (MODEL-97).

        Derived from `model_type` and `model_subtypes`, never stored, so it
        cannot drift from the card and cannot be lost in a YAML round-trip.
        A plain property rather than a `computed_field`: it is not card data
        and must not appear in `model_dump()` or `to_yaml()`.

        An entry may be a field (`modalities.text.max_output_tokens`) or a
        subtree (`capabilities`), in which case every field beneath it is
        inapplicable. These are **not** the same as unresearched nulls: there
        is nothing here to research.

        **The card wins.** A path where this card carries an actual value is
        never reported inapplicable, whatever the class table says: a
        `llm-reasoning` card with `modalities.vision.supported: true` is a
        model that sees, and publishing "vision does not apply" over its own
        data would be a false claim rather than a missing one. The pruning can
        only ever *remove* a claim, so it cannot invent applicability.
        """
        return _answered_removed(
            inapplicable_paths(self.identity.model_type, self.identity.model_subtypes), self)

    @computed_field
    @property
    def applicable_field_coverage(self) -> float:
        """Internal statistic: percent of type-applicable schema fields filled.

        Not published. It is not a Model node property, not in the graph
        export, and not shown by ``modelspec info`` or ``modelspec stats``.
        Nested modality details and the Capabilities block declare
        ``__applicable_model_types__``; those subtrees count only when the
        card's ``model_type`` or a ``model_subtype`` is in the set. Untagged
        sections count for every type. ``card_*`` metadata, ``prose_body`` and
        ``authoring_guide`` never count.
        """
        filled, total = self._count_fields(self)
        return round((filled / total) * 100, 1) if total > 0 else 0.0

    @property
    def card_completeness(self) -> float:
        """Deprecated alias of ``applicable_field_coverage`` for scripts/**."""
        return self.applicable_field_coverage

    def applicable_field_counts(self) -> tuple[int, int]:
        """Filled and total fields that apply to this card's type."""
        return self._count_fields(self)

    def _count_fields(self, obj: BaseModel, _depth: int = 0,
                      _prefix: str = "",
                      _inapplicable: frozenset[str] | None = None) -> tuple[int, int]:
        """Recursively count filled vs type-applicable fields."""
        filled = 0
        total = 0
        inapplicable = (frozenset(self.inapplicable_fields)
                        if _inapplicable is None else _inapplicable)
        for field_name, field_info in type(obj).model_fields.items():
            value = getattr(obj, field_name)
            if field_name == "authoring_guide":
                continue  # guidance, not model facts: never moves coverage
            # A field this class cannot answer is outside the denominator: it
            # is not a gap, and counting it would be a permanent deduction for
            # a question that has no answer (MODEL-97).
            if f"{_prefix}{field_name}" in inapplicable:
                continue
            if isinstance(value, BaseModel):
                if not self._section_applies(value):
                    continue
                f, t = self._count_fields(value, _depth + 1, f"{_prefix}{field_name}.",
                                          inapplicable)
                filled += f
                total += t
            elif isinstance(value, list):
                total += 1
                if len(value) > 0:
                    filled += 1
            elif isinstance(value, dict):
                total += 1
                if len(value) > 0:
                    filled += 1
            elif field_name.startswith("card_") or field_name in ("prose_body", "authoring_guide"):
                continue  # Skip metadata fields
            else:
                total += 1
                if value is not None and value != "" and value is not False:
                    filled += 1
        return filled, total

    # ─── Serialization ─────────────────────────────────────────

    @classmethod
    def from_yaml_file(cls, path: str | Path) -> "ModelCard":
        """Load a model card from a YAML+Markdown file."""
        path = Path(path)
        content = path.read_text(encoding="utf-8")
        return cls.from_yaml_string(content)

    @classmethod
    def from_yaml_string(cls, content: str) -> "ModelCard":
        """Parse a model card from a string with YAML frontmatter."""
        parts = content.split("---", 2)
        if len(parts) >= 3:
            yaml_str = parts[1]
            prose = parts[2].strip()
        else:
            yaml_str = content
            prose = ""

        data = yaml.safe_load(yaml_str) or {}

        # Map flat YAML to nested Pydantic structure
        identity_data = {
            k: data.pop(k)
            for k in list(data.keys())
            if k in Identity.model_fields
        }

        card_data = {
            "identity": identity_data,
            "prose_body": prose,
        }

        # Map remaining top-level keys to sections
        section_map = {
            "architecture": Architecture,
            "lineage": Lineage,
            "licensing": Licensing,
            "modalities": Modalities,
            "capabilities": Capabilities,
            "cost": Cost,
            "availability": Availability,
            "benchmarks": Benchmarks,
            "deployment": Deployment,
            "risk_governance": RiskGovernance,
            "inference_performance": InferencePerformance,
            "adoption": Adoption,
            "downselect": Downselect,
            "sources": Sources,
            "authoring_guide": AuthoringGuide,
        }

        for section_key, section_cls in section_map.items():
            if section_key in data:
                card_data[section_key] = data.pop(section_key)

        # Remaining flat keys go to card metadata
        for k in ("card_schema_version", "card_author", "card_created", "card_updated"):
            if k in data:
                card_data[k] = data.pop(k)

        return cls(**card_data)

    def to_yaml(self) -> str:
        """Serialize back to YAML frontmatter + Markdown.

        The inverse of `from_yaml_string`: identity fields flat at the top
        level, every other section nested, enums as their string values.
        """
        data = self.model_dump(
            mode="json",
            exclude_none=False,
            exclude={"prose_body", "applicable_field_coverage"},
        )
        if self.authoring_guide is None:
            data.pop("authoring_guide", None)
        out = data.pop("identity")
        for key in ModelCard.model_fields:
            if key in data:
                out[key] = data.pop(key)
        yaml_str = yaml.dump(out, default_flow_style=False, sort_keys=False, allow_unicode=True)
        return f"---\n{yaml_str}---\n\n{self.prose_body}"


# ═══════════════════════════════════════════════════════════════
# Applicability: the *other* kind of null (MODEL-97)
# ═══════════════════════════════════════════════════════════════
#
# Two sources, one answer. `__applicable_model_types__` gates whole sections
# and predates this; `schema.applicability.FIELD_RULES` gates named fields
# inside sections that do apply. Both are pure functions of the card's class,
# so this is cached per class rather than computed per card.


def _coerce_types(model_type: Any, model_subtypes: Iterable[Any] = ()) -> frozenset[ModelType]:
    """Card class plus subtypes, from enum members or from raw YAML strings.

    An unrecognised string is dropped rather than raising: a card carrying a
    type this build does not know is a card whose class we do not know, and an
    unknown class must assert nothing about what does or does not apply.
    """
    found: set[ModelType] = set()
    for raw in [model_type, *(model_subtypes or ())]:
        if raw is None or raw == "":
            continue
        if isinstance(raw, ModelType):
            found.add(raw)
            continue
        try:
            found.add(ModelType(str(raw)))
        except ValueError:
            continue
    return frozenset(found)


def _gated_sections(model_cls: type[BaseModel], prefix: str,
                    types: frozenset[ModelType], out: list[str]) -> None:
    for name, info in model_cls.model_fields.items():
        annotation = info.annotation
        if not (isinstance(annotation, type) and issubclass(annotation, BaseModel)):
            continue  # a list, a dict, an optional union: not a gated section
        path = f"{prefix}{name}"
        gate = getattr(annotation, "__applicable_model_types__", None)
        if gate is not None and not (types & gate):
            out.append(path)  # the whole subtree, named once
            continue
        _gated_sections(annotation, f"{path}.", types, out)


@lru_cache(maxsize=None)
def _inapplicable_paths(types: frozenset[ModelType]) -> tuple[str, ...]:
    if not types:
        return ()
    sections: list[str] = []
    _gated_sections(ModelCard, "", types, sections)
    fields = [rule.path for rule in FIELD_RULES if not (types & rule.applies_to)]
    # A field inside an already-named subtree is redundant: the subtree says it.
    # Naming both would make a consumer's `not_applicable` list disagree with
    # itself about how specific it is.
    covered = tuple(f"{path}." for path in sections)
    fields = [path for path in fields if not path.startswith(covered)]
    return tuple(sorted(set(sections) | set(fields)))


def inapplicable_paths(model_type: Any,
                       model_subtypes: Iterable[Any] = ()) -> tuple[str, ...]:
    """Dotted paths a card of this class cannot answer, sorted.

    Accepts `ModelType` members or the raw strings a published card carries, so
    the export and the site renderer can call it with a front-matter dict
    without paying to build a `ModelCard`.

    A card with no `model_type` gets `()`. Unknown class is unknown: it must
    never be turned into "there is nothing to know".
    """
    return _inapplicable_paths(_coerce_types(model_type, model_subtypes))


def _value_at(obj: Any, path: str) -> Any:
    """Follow a dotted path through a mapping or a model. None when absent."""
    current = obj
    for part in path.split("."):
        if isinstance(current, dict):
            current = current.get(part)
        elif isinstance(current, BaseModel):
            current = getattr(current, part, None)
        else:
            return None
        if current is None:
            return None
    return current


def _is_answered(value: Any) -> bool:
    """Whether a value — or anything beneath a section — is a real answer.

    The same test coverage uses: `None`, `""`, `False` and an empty collection
    are all "nobody filled this in", not data.
    """
    if value is None or value == "" or value is False:
        return False
    if isinstance(value, BaseModel):
        return any(_is_answered(getattr(value, name, None))
                   for name in type(value).model_fields)
    if isinstance(value, dict):
        return any(_is_answered(item) for item in value.values())
    if isinstance(value, (list, tuple, set)):
        return len(value) > 0
    return True


def _answered_removed(paths: Iterable[str], card: Any) -> tuple[str, ...]:
    """Drop any path this card actually answers. The card outranks the table.

    One-way: it can only remove an inapplicability claim, never add one, so a
    card can never talk the catalogue into asserting that a question has no
    answer.
    """
    return tuple(path for path in paths if not _is_answered(_value_at(card, path)))


def applicability_block(model_type: Any,
                        model_subtypes: Iterable[Any] = (),
                        card: Any = None) -> dict[str, Any]:
    """The derived block published beside a card in `/api/models/<id>.json`.

    Additive: it adds information rather than widening any card field, so it is
    not a contract break on its own (see `docs/cli-contract.md`). `card` is the
    card's frontmatter (or a `ModelCard`); pass it so a path the card answers
    is never published as one it cannot have.
    """
    paths = inapplicable_paths(model_type, model_subtypes)
    if card is not None:
        paths = _answered_removed(paths, card)
    return {
        "basis": "model_type",
        "model_type": getattr(model_type, "value", model_type) or None,
        "not_applicable": list(paths),
    }
