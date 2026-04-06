"""Controlled vocabularies for the ModelRank schema.

Every constrained field in the model card maps to an enum here.
This is the single source of truth for valid values.
"""

from enum import Enum


class ModelType(str, Enum):
    """Primary model classification."""
    LLM_CHAT = "llm-chat"
    LLM_REASONING = "llm-reasoning"
    LLM_CODE = "llm-code"
    LLM_BASE = "llm-base"
    VLM = "vlm"
    EMBEDDING_TEXT = "embedding-text"
    EMBEDDING_MULTIMODAL = "embedding-multimodal"
    EMBEDDING_CODE = "embedding-code"
    RERANKER = "reranker"
    SAFETY_CLASSIFIER = "safety-classifier"
    IMAGE_GENERATION = "image-generation"
    IMAGE_EDITING = "image-editing"
    VIDEO_GENERATION = "video-generation"
    AUDIO_ASR = "audio-asr"
    AUDIO_TTS = "audio-tts"
    AUDIO_MUSIC = "audio-music"
    AUDIO_REALTIME = "audio-realtime"
    DOCUMENT_OCR = "document-ocr"
    MEDICAL = "medical"
    LEGAL = "legal"
    FINANCIAL = "financial"
    ROBOTICS = "robotics"
    WORLD_MODEL = "world-model"
    REWARD_MODEL = "reward-model"
    ROUTER = "router"
    AGENT_MODEL = "agent-model"
    ADAPTER = "adapter"
    QUANTIZED_VARIANT = "quantized-variant"
    DISTILLED = "distilled"
    MERGED = "merged"


class ModelStatus(str, Enum):
    ACTIVE = "active"
    BETA = "beta"
    ALPHA = "alpha"
    DEPRECATED = "deprecated"
    SUNSET = "sunset"
    PREVIEW = "preview"


class ArchitectureType(str, Enum):
    DENSE_TRANSFORMER = "dense-transformer"
    MOE = "MoE"
    SSM = "SSM"
    HYBRID_SSM_TRANSFORMER = "hybrid-SSM-transformer"
    DIFFUSION = "diffusion"
    GAN = "GAN"
    FLOW_MATCHING = "flow-matching"
    ENCODER_DECODER = "encoder-decoder"
    ENCODER_ONLY = "encoder-only"
    DECODER_ONLY = "decoder-only"
    OTHER = "other"


class AttentionType(str, Enum):
    MHA = "MHA"
    GQA = "GQA"
    MQA = "MQA"
    MLA = "MLA"
    LINEAR = "linear"
    SLIDING_WINDOW = "sliding-window"
    NONE = "none"


class PositionalEncoding(str, Enum):
    ROPE = "RoPE"
    ALIBI = "ALiBi"
    NTK_AWARE_ROPE = "NTK-aware-RoPE"
    YARN = "YaRN"
    ABSOLUTE = "absolute"
    RELATIVE = "relative"
    NONE = "none"


class TokenizerType(str, Enum):
    BPE = "BPE"
    SENTENCEPIECE = "SentencePiece"
    TIKTOKEN = "tiktoken"
    UNIGRAM = "Unigram"
    OTHER = "other"


class BaseModelRelation(str, Enum):
    ORIGINAL = "original"
    FINETUNE = "finetune"
    ADAPTER = "adapter"
    QUANTIZED = "quantized"
    MERGE = "merge"
    DISTILLATION = "distillation"
    CONTINUATION = "continuation"


class TrainingMethod(str, Enum):
    PRETRAINING = "pretraining"
    SFT = "SFT"
    RLHF = "RLHF"
    DPO = "DPO"
    GRPO = "GRPO"
    RLAIF = "RLAIF"
    CONTRASTIVE = "contrastive"
    OTHER = "other"


class LicenseType(str, Enum):
    PROPRIETARY = "proprietary"
    APACHE_2_0 = "apache-2.0"
    MIT = "mit"
    LLAMA_COMMUNITY = "llama-community"
    QWEN = "qwen"
    DEEPSEEK = "deepseek"
    GEMMA = "gemma"
    CC_BY_4_0 = "cc-by-4.0"
    CC_BY_NC_4_0 = "cc-by-nc-4.0"
    OPENRAIL = "openrail"
    GPL_3_0 = "gpl-3.0"
    OTHER = "other"


class UsePermission(str, Enum):
    ALLOWED = "allowed"
    RESTRICTED = "restricted"
    PROHIBITED = "prohibited"
    UNSPECIFIED = "unspecified"


class OrgType(str, Enum):
    PRIVATE = "private"
    STATE_BACKED = "state-backed"
    ACADEMIC = "academic"
    OPEN_COLLECTIVE = "open-collective"
    GOVERNMENT = "government"
    NONPROFIT = "nonprofit"


class Tier(str, Enum):
    TIER_1 = "tier-1"
    TIER_2 = "tier-2"
    TIER_3 = "tier-3"
    NA = "n/a"


class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ResistanceLevel(str, Enum):
    RESISTANT = "resistant"
    MODERATE = "moderate"
    VULNERABLE = "vulnerable"
    UNTESTED = "untested"


class EvalStatus(str, Enum):
    EVAL_COMPLETE = "eval-complete"
    EVAL_PENDING = "eval-pending"
    EVAL_FAILED = "eval-failed"
    NOT_STARTED = "not-started"


class RiskTier(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PlatformCategory(str, Enum):
    CLOUD = "cloud"
    INFERENCE = "inference"
    AGGREGATOR = "aggregator"
    AI_APP = "ai-app"
    PROVIDER = "provider"
    CN_PLATFORM = "cn-platform"
    REGIONAL = "regional"
    LOCAL = "local"
    MODEL_HUB = "model-hub"


class BenchmarkCategory(str, Enum):
    KNOWLEDGE = "knowledge"
    MATH = "math"
    CODING = "coding"
    MULTIMODAL = "multimodal"
    SAFETY = "safety"
    HUMAN_PREFERENCE = "human-preference"
    EMBEDDING = "embedding"
    GENERATION = "generation"
    DOMAIN = "domain"
    AGENTIC = "agentic"
    COMPOSITE = "composite"


class QuantFormat(str, Enum):
    GGUF = "gguf"
    AWQ = "awq"
    GPTQ = "gptq"
    EXL2 = "exl2"
    FP16 = "fp16"
    BF16 = "bf16"
    FP8 = "fp8"
    INT8 = "int8"
    INT4 = "int4"


class Modality(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    PDF = "pdf"
    THREE_D = "3d"
    TABULAR = "tabular"
    CODE = "code"
    EMBEDDINGS = "embeddings"
    ACTIONS = "actions"
    CLASSIFICATIONS = "classifications"
    SCORES = "scores"


class EUAIActRisk(str, Enum):
    UNACCEPTABLE = "unacceptable"
    HIGH = "high"
    LIMITED = "limited"
    MINIMAL = "minimal"
    NA = "n/a"
