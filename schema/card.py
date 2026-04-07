"""ModelSpec Universal Model Card Schema — V3

Pydantic models for every section of the model intelligence card.
This is the source of truth. The YAML template, graph ingestion,
API responses, and CLI output all derive from these models.

Usage:
    from schema.card import ModelCard
    card = ModelCard.from_yaml("models/qwen/qwen3-30b-a3b.md")
    card.validate()
    print(card.card_completeness)
"""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, computed_field, model_validator

from .enums import (
    ArchitectureType,
    AttentionType,
    BaseModelRelation,
    BenchmarkCategory,
    ConfidenceLevel,
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

class Licensing(BaseModel):
    open_weights: bool = False
    license_type: LicenseType | None = None
    license_url: str = ""
    tos_url: str = ""
    acceptable_use_policy_url: str = ""
    not_for_all_audiences: bool = False
    commercial_use: bool | None = None
    defense_use: UsePermission = UsePermission.UNSPECIFIED
    government_use: UsePermission = UsePermission.UNSPECIFIED
    medical_use: UsePermission = UsePermission.UNSPECIFIED
    academic_use: UsePermission = UsePermission.UNSPECIFIED
    geographic_restrictions: list[str] = []
    export_control_notes: str = ""
    origin_country: str = ""
    origin_org_type: OrgType | None = None


# ═══════════════════════════════════════════════════════════════
# Section 5: Modalities
# ═══════════════════════════════════════════════════════════════

class VisionDetail(BaseModel):
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
    input_supported: bool = False
    output_supported: bool = False
    max_input_duration_sec: int | None = None
    max_output_duration_sec: int | None = None
    max_resolution: str = ""
    max_fps: int | None = None
    audio_sync: bool = False
    temporal_reasoning: bool = False


class DocumentDetail(BaseModel):
    pdf_native: bool = False
    table_extraction: bool = False
    form_understanding: bool = False
    max_pages: int | None = None
    layout_analysis: bool = False


class ImageGenDetail(BaseModel):
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
    supported: bool = False
    max_input_pairs: int | None = None
    max_input_length: int | None = None
    cross_encoder: bool | None = None


class TextDetail(BaseModel):
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
    data_residency: list[str] = []
    hipaa_eligible: bool = False
    fedramp_authorized: bool = False
    soc2_compliant: bool = False
    free_tier: bool = False
    free_tier_details: str = ""


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

class Benchmarks(BaseModel):
    # All benchmark scores in a single open-ended dictionary.
    # Keys are benchmark identifiers (e.g. "humaneval", "mmlu_pro",
    # "multipl_e_rust", "mmlu_chemistry", "pubmedqa", "flores_en_zh").
    # No fixed schema — any benchmark can be added without code changes.
    scores: dict[str, float] = {}

    # Meta
    benchmark_source: str = ""
    benchmark_as_of: str = ""
    benchmark_notes: str = ""

    def filled_count(self) -> int:
        return len(self.scores)


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

    # Card metadata
    card_schema_version: str = "3.0"
    card_author: str = ""
    card_created: str = ""
    card_updated: str = ""
    prose_body: str = ""  # The markdown content below the YAML frontmatter

    @computed_field
    @property
    def card_completeness(self) -> float:
        """Calculate what percentage of applicable fields are filled."""
        filled, total = self._count_fields(self)
        return round((filled / total) * 100, 1) if total > 0 else 0.0

    def _count_fields(self, obj: BaseModel, _depth: int = 0) -> tuple[int, int]:
        """Recursively count filled vs total fields."""
        filled = 0
        total = 0
        for field_name, field_info in obj.model_fields.items():
            value = getattr(obj, field_name)
            if isinstance(value, BaseModel):
                f, t = self._count_fields(value, _depth + 1)
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
            elif field_name.startswith("card_") or field_name == "prose_body":
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
        """Serialize back to YAML frontmatter + Markdown."""
        data = self.model_dump(
            exclude_none=False,
            exclude={"prose_body", "card_completeness"},
        )
        yaml_str = yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True)
        return f"---\n{yaml_str}---\n\n{self.prose_body}"
