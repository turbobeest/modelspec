# Audit: Metadata Sources & Model Categories

## Part 1: Metadata Sources We're Missing

The V2 template pulls from 8 sources. The real ecosystem has **25+** meaningful metadata sources. Here's the complete map, organized by what they uniquely provide.

### A. Leaderboards & Benchmark Aggregators

| Source | What It Uniquely Provides | In Template? |
|---|---|---|
| **models.dev** | Canonical model IDs, pricing, context limits, TOML-structured data | ✅ |
| **HuggingFace Hub** | Model weights, lineage, training data, community forks, download counts | ✅ |
| **LMArena (Chatbot Arena)** | Human-preference ELO ratings — overall, coding, math, vision, style-control, hard prompts | Partial — only overall ELO |
| **Artificial Analysis** | Inference speed (TPS, TTFT, latency), price-performance ratios, quality index (AAII) | ❌ |
| **Vellum AI Leaderboard** | Curated non-saturated benchmarks, side-by-side frontier comparison | ❌ |
| **Vals.ai** | Enterprise-specific benchmarks (CaseLaw, TaxEval, MortgageTax, CorpFin) | ❌ |
| **LiveBench** | Contamination-resistant live benchmarks, monthly-refreshed questions | ❌ |
| **HF Open LLM Leaderboard v2** | Standardized open-model eval (GPQA, MATH L5, MMLU-Pro via EleutherAI harness) | ❌ |
| **HELM (Stanford)** | Holistic eval across 42 scenarios + dedicated safety leaderboard | ❌ |
| **OpenCompass** | Chinese-origin model evaluation, CJK-language benchmarks | ❌ |
| **MTEB** | Embedding model benchmarks (retrieval, classification, clustering, reranking) | ❌ |
| **Big Code Models Leaderboard** | Code-specific model rankings (HumanEval, MultiPL-E, MBPP) | ❌ |
| **Open WebUI Leaderboard** | Real usage data from 100K+ users — what people actually choose to use | ❌ |
| **The ATOM Project** | Download metrics, adoption trends, regional usage (US vs CN dominance) | ❌ |
| **Arena.ai** | Multi-category arena (text, image, vision, audio) with separate ELO per category | ❌ |

### B. Cloud Provider Model Catalogs

Each major cloud has its own model catalog with deployment-specific metadata we don't capture:

| Source | What It Uniquely Provides | In Template? |
|---|---|---|
| **NVIDIA API Catalog** | Optimized inference configs, TensorRT-LLM benchmarks, NIM containers | ❌ |
| **AWS Bedrock** | Available models, region availability, provisioned throughput options, pricing | ❌ |
| **Azure AI Foundry** | Model routing, fine-tuning support, HIPAA/FedRAMP deployment options | ❌ |
| **Google Vertex AI** | Model garden, Gemma variants, managed endpoints, TPU optimization | ❌ |
| **Replicate** | One-click deployment, cold-start times, community model versions | ❌ |
| **Together AI** | Inference pricing, fine-tuning pricing, serverless vs dedicated | ❌ |
| **Groq** | LPU-accelerated inference speeds (fastest available TPS) | ❌ |
| **Fireworks AI** | Optimized serving, function calling benchmarks, compound AI serving | ❌ |

### C. Local Inference Registries

| Source | What It Uniquely Provides | In Template? |
|---|---|---|
| **Ollama Library** | Available model tags, quantization variants, pull counts, manifest sizes | ❌ |
| **LM Studio Model Catalog** | Compatibility ratings, recommended RAM, download stats per quant | ❌ |
| **GPT4All Model Explorer** | Tested device compatibility, offline performance benchmarks | ❌ |
| **MLX Community (HF org)** | Apple Silicon-optimized conversions, MLX-specific benchmarks | ❌ |

### D. Governance & Compliance Sources

| Source | What It Uniquely Provides | In Template? |
|---|---|---|
| **NIST AI RMF** | Trustworthiness framework (valid, reliable, safe, secure, fair, explainable) | Partial |
| **EU AI Act registry** | Risk classification (unacceptable/high/limited/minimal) | Partial |
| **ISO 42001** | AI management system certification status | Partial |
| **Stanford AI Index** | Industry-wide trends, policy landscape, investment data | ❌ |
| **Foundation Model Transparency Index** | 100-point transparency scoring across 14 indicators | ❌ |
| **Scale AI / DoD CDAO** | Defense-specific T&E frameworks, holdout datasets | ❌ |
| **MLCommons** | Standardized ML benchmarks (MLPerf inference/training) | ❌ |

### E. Community & Usage Intelligence

| Source | What It Uniquely Provides | In Template? |
|---|---|---|
| **OpenRouter Rankings** | Real developer usage data, routing preferences, cost per query | ❌ |
| **r/LocalLLaMA** | Community testing, real-world quant comparisons, device reports | ❌ (qualitative) |
| **Interconnects.ai / Artifacts** | Expert analysis, open model ecosystem reporting | ❌ (qualitative) |
| **Provider changelogs** | Version updates, deprecation notices, behavioral changes | ❌ |

---

## Part 2: Model Categories We're Missing

**This is the bigger problem.** The V2 template is designed almost entirely for **chat/instruction LLMs**. The AI model universe is much broader. Here's every category that should be in scope:

### Currently Covered (Chat/Instruction LLMs)
| Category | Example Models | Template Fit |
|---|---|---|
| Frontier API models | Claude Opus 4.6, GPT-5, Gemini 3.1 Pro | ✅ Good |
| Open-weight chat models | Llama 4, Qwen3, Mistral | ✅ Good |
| Reasoning models | DeepSeek R1, QwQ, o4-mini | ✅ Good |
| MoE models | Qwen3-30B-A3B, Mixtral, DBRX | ✅ Good |
| Small/edge language models | Phi-4, Gemma 4 E2B, Granite 4 | ✅ Good |

### Partially Covered (Template works but has gaps)
| Category | Example Models | What's Missing |
|---|---|---|
| Code-specialized models | Codestral, Devstral, StarCoder2, Qwen3-Coder | Code benchmark section exists but no FIM (fill-in-middle), completion mode, LSP support fields |
| Vision-language models (VLMs) | Gemma 4, Qwen-VL, Pixtral, Ovis2, Moondream | Vision detail section exists but needs: grounding, pointing, counting, VQA benchmarks |
| Multimodal omni models | GPT-4o, Gemini 3.1 Flash | Audio/video fields exist but sparse |

### NOT Covered (Template doesn't have fields for these)
| Category | Example Models | What Template Needs |
|---|---|---|
| **Embedding models** | text-embedding-3-large, BGE-M3, Qwen3-Embedding, E5-Mistral, Voyage | MTEB scores, embedding dimensions, matryoshka support, max input length, retrieval/classification/clustering scores |
| **Reranker models** | Cohere Rerank, BGE-Reranker, Jina Reranker | Reranking benchmarks, latency, input pair limits |
| **Safety/guard models** | ShieldGemma 2, Llama Guard 4, gpt-oss-safeguard | Policy categories covered, false positive rates, latency overhead, integration patterns |
| **Image generation models** | FLUX, Stable Diffusion 3.5, Midjourney, DALL-E, Recraft V4 | FID/CLIP scores, resolution, style control, inpainting, text rendering, generation speed |
| **Video generation models** | Sora 2, Veo 3.1, Wan 2.2, Kling | Duration limits, resolution, fps, audio sync, motion quality, temporal coherence |
| **Audio/speech models** | Whisper, Gemini TTS, ElevenLabs | WER (word error rate), supported languages, speaker diarization, voice cloning, latency |
| **Music generation** | Lyria 3, Stable Audio, Suno | Genre coverage, duration, stem separation, licensing terms |
| **OCR/document models** | olmOCR 2, DocTR, PaddleOCR | Page types handled, table accuracy, handwriting support, output formats |
| **Medical models** | MedGemma, MedPalm, BioMistral | USMLE scores, clinical trial data, FDA clearance status, HIPAA compliance |
| **Legal models** | SaulLM, Legal-BERT | Jurisdiction coverage, case law accuracy, contract analysis |
| **Financial models** | FinGPT, BloombergGPT | Market data handling, compliance, regulatory alignment |
| **Robotics/embodied** | RT-2, Gemini Robotics | Action space, sim-to-real, environment types, safety constraints |
| **World models** | Genie 3, UniSim | Environment types, physics accuracy, real-time capability |
| **Reward/judge models** | Skywork Reward, PRM models | Correlation with human judgment, calibration, bias patterns |
| **Router models** | Azure Model Router, Martian | Routing accuracy, latency overhead, cost savings |
| **Distilled models** | DeepSeek-R1-Distill-Qwen-8B | Distillation method, teacher model, performance retention |
| **LoRA adapters** | Thousands on HF | Base model, task, adapter rank, merge compatibility |
| **Quantized community models** | TheBloke GGUF variants, bartowski, unsloth | Quantization method, perplexity delta vs base, community testing |

---

## Part 3: Recommended Architecture Change

The V2 template tries to be one template for everything. That won't work for embedding models, image gen, safety models, etc. 

**Recommended approach: Base template + category-specific extensions.**

```
model-card-base.yaml          # Identity, licensing, provider, lineage, cost, downselect
  ├── ext-llm.yaml             # Chat/instruction: benchmarks, capabilities, tool use
  ├── ext-code.yaml            # Code models: FIM, completion, LSP, code benchmarks
  ├── ext-vlm.yaml             # Vision-language: VQA, grounding, OCR benchmarks
  ├── ext-embedding.yaml       # Embedding: MTEB scores, dimensions, matryoshka
  ├── ext-reranker.yaml        # Reranker: pair limits, reranking benchmarks
  ├── ext-image-gen.yaml       # Image generation: FID, CLIP, resolution, styles
  ├── ext-video-gen.yaml       # Video generation: duration, fps, audio sync
  ├── ext-audio.yaml           # Speech/TTS/music: WER, voices, languages
  ├── ext-safety.yaml          # Guard models: policy coverage, false positive rate
  ├── ext-medical.yaml         # Medical: USMLE, FDA status, HIPAA
  └── ext-hardware.yaml        # Hardware fit: shared across all local-runnable types
```

In the FalkorDB graph, this translates to:
- All models share the `:Model` node with base properties
- Category-specific properties go on the node (FalkorDB is schemaless)
- Category-specific benchmarks become `(:Model)-[:SCORED]->(:Benchmark {category: 'embedding'})` edges

---

## Part 4: Fields to Add to Base Template

Regardless of category, every model card should also track:

| Field | Why |
|---|---|
| `model_type` | The primary classification (see full list below) |
| `model_subtypes` | Secondary classifications (a VLM might also be a code model) |
| `download_count` | From HF/Ollama — proxy for adoption |
| `community_forks` | How many derivatives exist |
| `fine_tuning_supported` | Can users fine-tune this model? |
| `fine_tuning_methods` | LoRA, QLoRA, full, RLHF, DPO |
| `distillation_target` | Is this commonly used as a distillation teacher? |
| `cloud_providers` | Which cloud platforms host this for inference |
| `cloud_regions` | Geographic availability |
| `iso_42001_certified` | AI management system certification |
| `fmti_score` | Stanford Foundation Model Transparency Index score |
| `arena_elo_overall` | LMArena overall ELO |
| `arena_elo_coding` | LMArena coding-specific ELO |
| `arena_elo_math` | LMArena math-specific ELO |
| `arena_elo_vision` | LMArena vision-specific ELO |
| `arena_elo_hard_prompts` | LMArena hard prompts ELO |
| `artificial_analysis_quality_index` | AAII v3 composite score |
| `artificial_analysis_speed_index` | TPS ranking |
| `openrouter_usage_rank` | Developer usage ranking |

### Complete `model_type` Taxonomy

```
model_type:
  - llm-chat                    # General-purpose chat/instruction
  - llm-reasoning               # Extended reasoning (o-series, R1, QwQ)
  - llm-code                    # Code-specialized (Codestral, StarCoder)
  - llm-base                    # Base/pretrained (not instruction-tuned)
  - vlm                         # Vision-language model
  - embedding-text              # Text embedding
  - embedding-multimodal        # Multi-modal embedding
  - reranker                    # Reranking model
  - safety-classifier           # Content safety / guard model
  - image-generation            # Text-to-image
  - image-editing               # Image modification
  - video-generation            # Text/image-to-video
  - audio-asr                   # Automatic speech recognition
  - audio-tts                   # Text-to-speech
  - audio-music                 # Music generation
  - audio-realtime              # Real-time audio dialogue
  - document-ocr                # OCR / document understanding
  - medical                     # Medical-specialized
  - legal                       # Legal-specialized
  - financial                   # Finance-specialized
  - robotics                    # Embodied / robotics
  - world-model                 # Environment simulation
  - reward-model                # Reward / judge model
  - router                      # Model routing / selection
  - adapter                     # LoRA / adapter (not standalone)
  - quantized-variant           # Community quantization of another model
  - distilled                   # Distilled from a larger model
  - merged                      # Merge of multiple models
```
