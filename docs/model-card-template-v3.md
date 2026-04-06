---
# ╔═══════════════════════════════════════════════════════════════════════╗
# ║  MODEL INTELLIGENCE CARD — V3 UNIVERSAL TEMPLATE                     ║
# ║  Single schema for every AI model type. Null fields = not yet        ║
# ║  researched. Every field is a potential knowledge graph edge.         ║
# ║  Schema version: 3.0                                                 ║
# ╚═══════════════════════════════════════════════════════════════════════╝
#
# DESIGN PRINCIPLES:
#   1. One template for ALL model types — embedding, LLM, image gen, etc.
#   2. Null = "not yet researched" (the backend researcher fills these in)
#   3. Every field maps to a FalkorDB node property or edge
#   4. Fields are grouped by concern, not by model type
#   5. The template IS the graph schema — it's the forcing function
#
# MODEL TYPE TAXONOMY (primary classification):
#   llm-chat | llm-reasoning | llm-code | llm-base | vlm | 
#   embedding-text | embedding-multimodal | embedding-code |
#   reranker | safety-classifier | image-generation | image-editing |
#   video-generation | audio-asr | audio-tts | audio-music |
#   audio-realtime | document-ocr | medical | legal | financial |
#   robotics | world-model | reward-model | router | agent-model |
#   adapter | quantized-variant | distilled | merged

# ═══════════════════════════════════════════════════════════════════════
# SECTION 1: IDENTITY
# Every model has these. No exceptions.
# ═══════════════════════════════════════════════════════════════════════
model_id: ""                                   # canonical ID (models.dev format: "provider/model-name")
display_name: ""
provider: ""                                   # provider slug (lowercase)
provider_display: ""                           # human-readable provider name
family: ""                                     # model family (e.g. "claude-4.6", "qwen3", "flux")
version: ""
release_date: ""                               # YYYY-MM-DD or YYYY-MM
last_updated: ""
status: "active"                               # active | beta | alpha | deprecated | sunset | preview

model_type: ""                                 # primary type from taxonomy above
model_subtypes: []                             # secondary types (a VLM that's also good at code)
tags: []                                       # freeform discoverability tags
pipeline_tag: ""                               # HuggingFace pipeline tag (text-generation, feature-extraction, etc.)

# ═══════════════════════════════════════════════════════════════════════
# SECTION 2: ARCHITECTURE & TECHNICAL SPECS
# What this model IS, structurally.
# ═══════════════════════════════════════════════════════════════════════
architecture:
  type: ""                                     # dense-transformer | MoE | SSM | hybrid-SSM-transformer | diffusion | GAN | flow-matching | encoder-decoder | encoder-only | decoder-only | other
  total_parameters: null                       # total param count (e.g. 70_000_000_000)
  active_parameters: null                      # for MoE: active per forward pass
  num_experts: null                            # MoE total experts
  experts_per_token: null                      # MoE experts routed per token
  num_layers: null
  hidden_size: null
  intermediate_size: null
  attention_type: ""                           # MHA | GQA | MQA | MLA | linear | sliding-window | none
  num_attention_heads: null
  num_kv_heads: null                           # for GQA/MQA
  positional_encoding: ""                      # RoPE | ALiBi | NTK-aware-RoPE | absolute | relative | YaRN | none
  rope_theta: null                             # RoPE base frequency
  vocab_size: null
  tokenizer_type: ""                           # BPE | SentencePiece | tiktoken | Unigram | other
  embedding_dimensions: null                   # output embedding dims (for embedding/multimodal models)
  activation_function: ""                      # SwiGLU | GELU | ReLU | GeGLU | etc.
  precision_native: ""                         # FP32 | BF16 | FP16 | FP8
  flash_attention: null                        # true | false
  tie_word_embeddings: null                    # true | false
  sliding_window_size: null                    # for sliding window attention

  # Vision encoder (for VLMs / multimodal)
  vision_encoder: ""                           # e.g. "SigLIP-400M", "ViT-L/14", "InternViT-6B"
  vision_resolution_max: ""                    # e.g. "4096x4096"
  vision_patch_size: null                      # e.g. 14

  # Diffusion/generation specifics
  diffusion_scheduler: ""                      # DDPM | DDIM | Euler | DPM-Solver | flow-matching
  diffusion_steps_default: null
  vae_type: ""                                 # for image/video gen models
  unet_channels: null

# ═══════════════════════════════════════════════════════════════════════
# SECTION 3: MODEL LINEAGE
# Where this model came from. Critical for trust and compliance.
# ═══════════════════════════════════════════════════════════════════════
lineage:
  base_model: ""                               # parent model ID
  base_model_relation: ""                      # original | finetune | adapter | quantized | merge | distillation | continuation
  merge_models: []                             # if merged: list of constituent model IDs
  adapter_type: ""                             # LoRA | QLoRA | DoRA | IA3 | prefix-tuning | none
  adapter_rank: null                           # LoRA rank (r value)

  training_datasets: []                        # dataset identifiers or descriptions
  training_data_tokens: null                   # approximate total training tokens
  training_data_cutoff: ""                     # when training data collection ended
  training_compute_flops: null                 # estimated total training FLOPs
  training_hardware: ""                        # e.g. "16,384x H100"
  training_time: ""                            # e.g. "~90 days"
  training_cost_estimate: ""                   # if publicly disclosed
  training_method: ""                          # pretraining | SFT | RLHF | DPO | GRPO | RLAIF | contrastive | etc.
  
  co2_emissions_kg: null                       # carbon footprint of training
  co2_source: ""                               # methodology for carbon estimate
  energy_kwh: null                             # total energy consumed

  library_name: ""                             # transformers | diffusers | vllm | mlx | sentence-transformers | etc.

# ═══════════════════════════════════════════════════════════════════════
# SECTION 4: ACCESS, LICENSING & PROVENANCE
# Who can use this, how, and where it came from.
# ═══════════════════════════════════════════════════════════════════════
open_weights: false
license_type: ""                               # proprietary | apache-2.0 | mit | llama-community | qwen | deepseek | gemma | cc-by-4.0 | cc-by-nc-4.0 | openrail | other
license_url: ""
tos_url: ""
acceptable_use_policy_url: ""
not_for_all_audiences: false                   # HF content safety flag

commercial_use: null                           # true | false | conditional
defense_use: ""                                # allowed | restricted | prohibited | unspecified
government_use: ""                             # allowed | restricted | prohibited | unspecified
medical_use: ""                                # allowed | restricted | prohibited | unspecified
academic_use: ""                               # allowed | restricted | prohibited | unspecified
geographic_restrictions: []                    # ISO country codes
export_control_notes: ""

origin_country: ""                             # ISO country code
origin_org_type: ""                            # private | state-backed | academic | open-collective | government | nonprofit

# ═══════════════════════════════════════════════════════════════════════
# SECTION 5: MODALITIES
# What goes in, what comes out, and how well.
# ═══════════════════════════════════════════════════════════════════════
modalities:
  input: []                                    # text | image | audio | video | pdf | 3d | tabular | code | embeddings
  output: []                                   # text | image | audio | video | embeddings | actions | classifications | scores

modalities_detail:
  text:
    max_input_tokens: null
    max_output_tokens: null
    context_window: null
    streaming: null                            # true | false
    fill_in_middle: null                       # for code models
    json_mode: null                            # structured JSON output
    system_prompt: null                        # supports system messages
    
  vision:
    supported: false
    ocr: false
    chart_reading: false
    spatial_reasoning: false
    handwriting: false
    object_detection: false
    object_counting: false
    visual_grounding: false                    # can point to/localize objects
    max_image_resolution: ""
    max_images_per_request: null
    video_frames: false                        # can process video as frame sequence
    
  audio:
    input_supported: false
    output_supported: false
    realtime_streaming: false                  # bidirectional audio
    asr_languages: []
    tts_languages: []
    tts_voices: null                           # number of available voices
    voice_cloning: false
    speaker_diarization: false
    music_understanding: false
    music_generation: false
    max_audio_duration_sec: null
    
  video:
    input_supported: false
    output_supported: false
    max_input_duration_sec: null
    max_output_duration_sec: null
    max_resolution: ""
    max_fps: null
    audio_sync: false                          # generates synchronized audio
    temporal_reasoning: false
    
  document:
    pdf_native: false
    table_extraction: false
    form_understanding: false
    max_pages: null
    layout_analysis: false

  image_generation:
    supported: false
    max_resolution: ""
    aspect_ratios: []
    inpainting: false
    outpainting: false
    img2img: false
    text_rendering_quality: ""                 # none | poor | good | excellent
    style_control: false
    controlnet_support: false
    lora_support: false
    steps_range: ""                            # e.g. "1-50"
    cfg_range: ""

  embeddings:
    supported: false
    dimensions: null                           # output vector dimensions
    dimensions_configurable: false             # Matryoshka / variable dimension support
    dimension_options: []                      # e.g. [256, 512, 768, 1024]
    max_input_tokens: null
    similarity_metric: ""                      # cosine | dot | euclidean
    normalized: null                           # true | false
    batch_size_max: null
    instruction_aware: false                   # different prompts for query vs document
    
  reranking:
    supported: false
    max_input_pairs: null
    max_input_length: null
    cross_encoder: null                        # true | false

# ═══════════════════════════════════════════════════════════════════════
# SECTION 6: CAPABILITIES (qualitative assessment)
# Tier ratings + boolean flags for what this model can do.
# ═══════════════════════════════════════════════════════════════════════
capabilities:
  coding:
    overall: ""                                # tier-1 | tier-2 | tier-3 | n/a
    languages: []
    agentic_coding: false
    code_review: false
    refactoring: false
    debugging: false
    test_generation: false
    documentation: false
    code_completion: false
    multi_file_editing: false
    fill_in_middle: false
    lsp_integration: false                     # language server protocol support
    repository_understanding: false            # can navigate full repos

  reasoning:
    overall: ""
    mathematical: false
    logical: false
    scientific: false
    planning: false
    multi_step: false
    chain_of_thought: false
    self_correction: false
    spatial: false
    temporal: false
    causal: false
    think_budget_control: false                # user can control reasoning depth

  tool_use:
    overall: ""
    function_calling: false
    mcp_compatible: false
    parallel_tool_calls: false
    tool_selection_accuracy: ""                # high | medium | low
    multi_turn_tool_use: false
    tool_error_recovery: false
    computer_use: false                        # can control GUI/browser
    
  language:
    multilingual: false
    num_languages: null
    strong_languages: []
    translation_quality: ""
    long_context_retrieval: ""                 # needle-in-haystack tier

  creative:
    writing: ""
    summarization: ""
    instruction_following: ""
    storytelling: ""
    technical_writing: ""

  safety_alignment:
    alignment_approach: ""
    refusal_rate: ""                           # low | moderate | high
    jailbreak_resistance: ""
    content_safety_tier: ""
    guardrail_builtin: false                   # has built-in safety classifier

  domain_specific:
    medical_knowledge: ""                      # tier or n/a
    legal_knowledge: ""
    financial_knowledge: ""
    scientific_knowledge: ""
    
  agent_capabilities:
    autonomous_execution: false                # can run multi-step tasks independently  
    web_browsing: false
    file_system_access: false
    code_execution: false
    long_running_tasks: false
    memory_management: false
    self_delegation: false                     # can spawn sub-tasks

# ═══════════════════════════════════════════════════════════════════════
# SECTION 7: COST
# What it costs to use. $0 for open-weight local inference.
# ═══════════════════════════════════════════════════════════════════════
cost:
  # Text token pricing (USD per million tokens)
  input: null
  output: null
  reasoning: null                              # separate reasoning token billing
  cache_read: null
  cache_write: null
  
  # Multimodal pricing
  input_audio: null                            # per million audio tokens
  output_audio: null
  input_image: null                            # per image or per million image tokens
  output_image: null                           # per generated image
  output_video_per_sec: null                   # per second of generated video
  
  # Batch/discount pricing
  batch_input: null
  batch_output: null
  
  # Embedding/reranking pricing
  embedding_per_million: null
  reranking_per_million: null
  
  # Fine-tuning pricing
  finetune_per_million_tokens: null
  finetune_hosting_per_hour: null

  # Free tier
  free_tier: false
  free_tier_limits: ""

  note: ""

# ═══════════════════════════════════════════════════════════════════════
# SECTION 8: AVAILABILITY — WHERE CAN YOU USE THIS MODEL?
# Every platform, service, and application where this model is offered.
# Each entry: boolean (available?) + optional metadata (url, model_id, 
# pricing_url, notes). The graph creates :AVAILABLE_ON edges from these.
# ═══════════════════════════════════════════════════════════════════════
availability:

  # --- Model maker's own platform (first-party) ---
  primary_provider:
    name: ""                                   # e.g. "Anthropic", "OpenAI", "Google"
    platform_url: ""                           # e.g. "https://console.anthropic.com"
    api_endpoint: ""                           # e.g. "https://api.anthropic.com/v1"
    npm_package: ""                            # AI SDK package name
    env_vars: []                               # auth env variable names
    model_id_on_platform: ""                   # exact string to pass in API calls
    rate_limit_rpm: null
    rate_limit_tpm: null
    sla_uptime: ""
    regions: []
    data_residency: []                         # where data is processed geographically
    hipaa_eligible: false
    fedramp_authorized: false
    soc2_compliant: false
    free_tier: false
    free_tier_details: ""

  # --- Major cloud infrastructure (managed endpoints) ---
  cloud_platforms:
    aws_bedrock:
      available: false
      model_id: ""
      regions: []
      fine_tuning: false
      url: "https://aws.amazon.com/bedrock/"
    azure_ai_foundry:
      available: false
      model_id: ""
      regions: []
      fine_tuning: false
      url: "https://ai.azure.com/"
    google_vertex_ai:
      available: false
      model_id: ""
      regions: []
      fine_tuning: false
      url: "https://cloud.google.com/vertex-ai"
    nvidia_nim:
      available: false
      model_id: ""
      url: "https://build.nvidia.com/"
    oracle_cloud_ai:
      available: false
      url: "https://www.oracle.com/artificial-intelligence/"
    ibm_watsonx:
      available: false
      url: "https://www.ibm.com/watsonx"
    salesforce_einstein:
      available: false
      url: "https://www.salesforce.com/einstein/"
    snowflake_cortex:
      available: false
      url: "https://www.snowflake.com/en/data-cloud/cortex/"

  # --- Inference-as-a-service (API hosting, optimized serving) ---
  inference_providers:
    groq:
      available: false
      model_id: ""
      url: "https://groq.com/"
      notes: ""                                # e.g. "LPU-accelerated, fastest TPS available"
    together_ai:
      available: false
      model_id: ""
      fine_tuning: false
      url: "https://www.together.ai/"
    fireworks_ai:
      available: false
      model_id: ""
      fine_tuning: false
      url: "https://fireworks.ai/"
    replicate:
      available: false
      model_id: ""
      url: "https://replicate.com/"
    deepinfra:
      available: false
      model_id: ""
      url: "https://deepinfra.com/"
    anyscale:
      available: false
      model_id: ""
      url: "https://www.anyscale.com/"
    lepton_ai:
      available: false
      url: "https://www.lepton.ai/"
    modal:
      available: false
      url: "https://modal.com/"
    baseten:
      available: false
      url: "https://www.baseten.co/"
    fal_ai:
      available: false
      url: "https://fal.ai/"
    cerebras:
      available: false
      url: "https://www.cerebras.ai/"
    sambanova:
      available: false
      url: "https://sambanova.ai/"

  # --- Aggregators & routers (access many models through one API) ---
  aggregators:
    openrouter:
      available: false
      model_id: ""
      url: "https://openrouter.ai/"
    martian:
      available: false
      url: "https://withmartian.com/"
    portkey:
      available: false
      url: "https://portkey.ai/"
    litellm:
      available: false
      url: "https://www.litellm.ai/"

  # --- AI-native applications (model embedded in a product) ---
  ai_applications:
    # Developer tools
    cursor:
      available: false
      url: "https://cursor.com/"
      notes: ""                                # e.g. "Available as coding model"
    github_copilot:
      available: false
      url: "https://github.com/features/copilot"
    codeium_windsurf:
      available: false
      url: "https://codeium.com/"
    replit:
      available: false
      url: "https://replit.com/"
    sourcegraph_cody:
      available: false
      url: "https://sourcegraph.com/cody"
    # Search & research
    perplexity:
      available: false
      url: "https://www.perplexity.ai/"
    you_com:
      available: false
      url: "https://you.com/"
    elicit:
      available: false
      url: "https://elicit.com/"
    # Productivity & assistants
    raycast:
      available: false
      url: "https://www.raycast.com/"
    notion_ai:
      available: false
      url: "https://www.notion.so/"
    # Chat interfaces / direct consumer access
    chatgpt:
      available: false
      url: "https://chat.openai.com/"
    claude_ai:
      available: false
      url: "https://claude.ai/"
    gemini_app:
      available: false
      url: "https://gemini.google.com/"
    copilot_microsoft:
      available: false
      url: "https://copilot.microsoft.com/"
    grok_xai:
      available: false
      url: "https://x.ai/"
    meta_ai:
      available: false
      url: "https://www.meta.ai/"
    poe:
      available: false
      url: "https://poe.com/"

  # --- Model provider platforms (where the org publishes their own models) ---
  provider_platforms:
    anthropic:
      available: false
      url: "https://console.anthropic.com/"
    openai:
      available: false
      url: "https://platform.openai.com/"
    google_ai_studio:
      available: false
      url: "https://aistudio.google.com/"
    mistral_la_plateforme:
      available: false
      url: "https://console.mistral.ai/"
    cohere:
      available: false
      url: "https://cohere.com/"
    ai21_labs:
      available: false
      url: "https://www.ai21.com/"
    inflection_ai:
      available: false
      url: "https://inflection.ai/"
    stability_ai:
      available: false
      url: "https://stability.ai/"
    recraft:
      available: false
      url: "https://www.recraft.ai/"

  # --- Chinese / Asian platforms ---
  cn_platforms:
    deepseek:
      available: false
      url: "https://platform.deepseek.com/"
    qwen_alibaba:
      available: false
      url: "https://www.alibabacloud.com/en/solutions/generative-ai/qwen"
    baidu_ernie:
      available: false
      url: "https://cloud.baidu.com/"
    bytedance_doubao:
      available: false
      url: "https://www.volcengine.com/"
    tencent_hunyuan:
      available: false
      url: "https://cloud.tencent.com/"
    zhipu_glm:
      available: false
      url: "https://www.zhipuai.cn/"
    moonshot_kimi:
      available: false
      url: "https://www.moonshot.cn/"
    minimax:
      available: false
      url: "https://www.minimax.chat/"
    zero_one_ai:
      available: false
      url: "https://www.01.ai/"
    stepfun:
      available: false
      url: "https://www.stepfun.com/"
    baichuan:
      available: false
      url: "https://www.baichuan-ai.com/"
    iflytek_spark:
      available: false
      url: "https://www.iflytek.com/"

  # --- Middle East / Other regional ---
  regional_platforms:
    tii_falcon:
      available: false
      url: "https://falconllm.tii.ae/"
      notes: ""                                # Technology Innovation Institute, UAE
    samsung_gauss:
      available: false
      url: "https://www.samsung.com/"
    naver_hyperclova:
      available: false
      url: "https://clova.ai/"
    kakao_brain:
      available: false
      url: "https://www.kakaobrain.com/"
    upstage_solar:
      available: false
      url: "https://www.upstage.ai/"

  # --- Local inference platforms ---
  local_platforms:
    ollama:
      available: false
      model_tag: ""                            # exact tag name (e.g. "qwen3:30b-a3b")
      url: "https://ollama.com/"
    lm_studio:
      available: false
      url: "https://lmstudio.ai/"
    gpt4all:
      available: false
      url: "https://gpt4all.io/"
    jan_ai:
      available: false
      url: "https://jan.ai/"
    llamafile:
      available: false
      url: "https://github.com/Mozilla-Ocho/llamafile"
    mlx_community:
      available: false
      hf_org_url: "https://huggingface.co/mlx-community"
    apple_core_ml:
      available: false
      url: "https://developer.apple.com/machine-learning/"
    nvidia_chat_with_rtx:
      available: false
      url: "https://www.nvidia.com/en-us/ai-on-rtx/"
    open_webui:
      available: false
      url: "https://openwebui.com/"

  # --- Model hubs & registries (where weights are downloadable) ---
  model_hubs:
    huggingface:
      available: false
      repo_id: ""                              # e.g. "Qwen/Qwen3-30B-A3B"
      url: ""
      downloads: null
      gated: false                             # requires access request
    github:
      available: false
      repo_url: ""
    modelscope:
      available: false
      model_id: ""
      url: "https://modelscope.cn/"            # Chinese model hub (Alibaba)
    civitai:
      available: false
      url: "https://civitai.com/"              # for image gen models
    kaggle_models:
      available: false
      url: "https://www.kaggle.com/models"

  # --- Catch-all for platforms not listed above ---
  other_platforms: []                          # list of {name, url, available, model_id, notes}

# ═══════════════════════════════════════════════════════════════════════
# SECTION 9: BENCHMARKS
# Quantitative scores. Organized by domain, not by model type.
# Null = not tested or not applicable.
# ═══════════════════════════════════════════════════════════════════════
benchmarks:
  # --- General Knowledge & Reasoning ---
  mmlu_pro: null
  gpqa_diamond: null
  hle: null                                    # Humanity's Last Exam
  arc_challenge: null
  hellaswag: null
  truthfulqa: null
  bbh: null                                    # Big-Bench Hard
  ifeval: null                                 # Instruction Following Eval
  musr: null                                   # Multi-step Soft Reasoning
  superglue: null
  winogrande: null

  # --- Mathematics ---
  math_500: null
  aime_2025: null
  aime_2026: null
  gsm8k: null
  mgsm: null                                  # Multilingual Grade School Math
  minerva_math: null

  # --- Coding ---
  humaneval: null
  humaneval_plus: null
  swe_bench_verified: null
  live_code_bench: null
  aider_polyglot: null
  terminal_bench: null
  terminal_bench_hard: null
  mbpp: null
  multipl_e: null                              # Multi-language code eval
  sci_code: null
  tau2_bench: null

  # --- Multimodal / Vision ---
  mmmu: null
  mathvista: null
  vqa_v2: null
  docvqa: null
  chartqa: null
  realworldqa: null
  ai2d: null

  # --- Safety & Bias ---
  helm_safety: null
  bbq: null
  toxigen: null
  stereoset: null
  crows_pairs: null

  # --- Human Preference ---
  arena_elo_overall: null
  arena_elo_coding: null
  arena_elo_math: null
  arena_elo_vision: null
  arena_elo_hard_prompts: null
  arena_elo_style_control: null
  mt_bench: null
  alpaca_eval: null
  alpaca_eval_lc: null                         # length-controlled
  wildbench: null

  # --- Embedding & Retrieval ---
  mteb_overall: null                           # Massive Text Embedding Benchmark
  mteb_retrieval: null
  mteb_classification: null
  mteb_clustering: null
  mteb_reranking: null
  mteb_sts: null                               # Semantic Textual Similarity
  beir: null
  miracl: null                                 # multilingual retrieval

  # --- Image Generation ---
  fid: null                                    # Fréchet Inception Distance
  clip_score: null
  image_reward: null
  hps_v2: null                                 # Human Preference Score
  dpg_bench: null                              # dense prompt graph

  # --- Video Generation ---
  vbench: null
  eval_crafter: null

  # --- Audio/Speech ---
  wer_librispeech: null                        # Word Error Rate
  wer_common_voice: null
  mos_tts: null                                # Mean Opinion Score for TTS
  music_caps: null

  # --- Domain-Specific ---
  medqa: null
  usmle: null
  pubmedqa: null
  legalbench: null
  finbench: null
  caselaw: null
  tax_eval: null

  # --- Agentic ---
  swe_bench_agent: null                        # agentic SWE-bench (not just patch gen)
  tau_bench: null
  web_arena: null
  os_world: null

  # --- Composite / Aggregated ---
  artificial_analysis_quality_index: null       # AAII v3 composite
  artificial_analysis_speed_index: null
  openrouter_usage_rank: null
  open_llm_leaderboard_v2: null                # HF composite score
  fmti_score: null                             # Stanford Foundation Model Transparency Index

  # --- Meta ---
  benchmark_source: ""
  benchmark_as_of: ""
  benchmark_notes: ""

# ═══════════════════════════════════════════════════════════════════════
# SECTION 10: HARDWARE & DEPLOYMENT
# Where and how you can run this model.
# ═══════════════════════════════════════════════════════════════════════
deployment:
  api_only: false
  local_inference: false
  self_hostable: false
  fine_tuning_supported: false
  fine_tuning_methods: []                      # LoRA | QLoRA | full | DPO | RLHF | SFT

  quantizations_available: []                  # Q2_K | Q3_K_M | Q4_K_M | Q5_K_M | Q6_K | Q8_0 | FP16 | BF16 | AWQ | GPTQ | EXL2 | GGUF | FP8

  # --- Per-hardware fit profiles ---
  # Each target hardware gets: does it fit, best quant, actual resource usage, speed
  hardware_profiles:
    nvidia_5090_32gb:
      fits: null
      best_quant: ""
      vram_usage_gb: null
      tokens_per_sec: null
      ttft_ms: null
      max_context_at_quant: null
      notes: ""
    dgx_spark_128gb:
      fits: null
      best_quant: ""
      vram_usage_gb: null
      tokens_per_sec: null
      ttft_ms: null
      max_context_at_quant: null
      notes: ""
    macbook_m4_pro_64gb:
      fits: null
      best_quant: ""
      ram_usage_gb: null
      tokens_per_sec: null
      ttft_ms: null
      max_context_at_quant: null
      inference_engine: ""                     # llama.cpp | MLX | ollama | Core ML
      notes: ""
    macbook_air_m4_24gb:
      fits: null
      best_quant: ""
      ram_usage_gb: null
      tokens_per_sec: null
      ttft_ms: null
      max_context_at_quant: null
      inference_engine: ""
      notes: ""
    # Extensible: add more hardware profiles as needed
    custom_hardware: []                        # list of {name, vram_gb, fits, quant, tps, notes}

  # --- Runtime support ---
  runtimes:
    gguf: false
    ollama: false
    ollama_tag: ""                             # exact tag name in ollama library
    lm_studio: false
    vllm: false
    trt_llm: false
    mlx: false
    llama_cpp: false
    sglang: false
    transformers: false
    exllamav2: false
    core_ml: false
    onnx: false
    openvino: false
    triton: false
    nim: false                                 # NVIDIA Inference Microservice

# ═══════════════════════════════════════════════════════════════════════
# SECTION 11: INFERENCE PERFORMANCE
# How fast and efficient is it in practice.
# ═══════════════════════════════════════════════════════════════════════
inference_performance:
  # API performance (cloud-hosted)
  api_latency_p50_ms: null
  api_latency_p99_ms: null
  api_ttft_ms: null
  api_tps_output: null
  api_tps_input: null                          # prompt processing speed

  # Local performance (see also hardware_profiles above for per-device)
  context_speed_degradation: ""                # e.g. "~30% slower at 128K vs 4K"
  prefill_speed: ""                            # tokens/sec for prompt processing
  batch_throughput_notes: ""

  # Generation-specific (image/video/audio)
  generation_time_sec: null                    # time to generate one output
  generation_steps: null
  
  # Efficiency
  quality_per_dollar: null                     # composite quality / API cost
  quality_per_watt: null                       # for local inference

# ═══════════════════════════════════════════════════════════════════════
# SECTION 12: RISK & GOVERNANCE
# NIST AI RMF aligned. Critical for institutional downselect.
# ═══════════════════════════════════════════════════════════════════════
risk_governance:
  # NIST AI RMF trustworthiness characteristics
  valid_and_reliable: ""                       # high | medium | low | untested
  safe: ""
  secure_and_resilient: ""
  accountable_and_transparent: ""
  explainable_and_interpretable: ""
  privacy_enhanced: ""
  fair_with_bias_managed: ""

  explainability:
    method: ""                                 # chain-of-thought | attention-viz | SHAP | none
    reasoning_visible: false                   # can you see the reasoning trace?
    
  bias_evaluation:
    conducted: false
    methodology: ""
    results_summary: ""
    known_biases: []
    
  adversarial_robustness:
    tested: false
    methodology: ""
    resistance_level: ""                       # resistant | moderate | vulnerable | untested
    known_vulnerabilities: []
    
  privacy:
    data_retention_policy: ""                  # none | session | 30-days | indefinite | configurable
    pii_handling: ""                           # redacted | logged | passed-through | not-applicable
    training_data_pii_scrubbed: null
    data_processing_location: []
    gdpr_compliant: null
    hipaa_eligible: null
    ccpa_compliant: null
    
  supply_chain:
    training_data_transparency: ""             # full | partial | opaque
    model_provenance_documented: false
    third_party_dependencies: []
    ai_bom_available: false                    # AI Bill of Materials
    reproducible: false                        # can training be reproduced?
    
  incident_history:
    safety_incidents: []
    cve_ids: []
    known_failure_modes: []
    
  regulatory_alignment:
    eu_ai_act_risk_level: ""                   # unacceptable | high | limited | minimal | n/a
    nist_rmf_profile: ""
    iso_42001_certified: null
    soc2_type2: null
    fedramp_level: ""                          # high | moderate | low | none

# ═══════════════════════════════════════════════════════════════════════
# SECTION 13: COMMUNITY & ADOPTION
# How widely used and trusted this model is.
# ═══════════════════════════════════════════════════════════════════════
adoption:
  huggingface_downloads: null                  # total downloads
  huggingface_likes: null
  ollama_pulls: null
  community_forks: null                        # number of fine-tunes/derivatives
  is_common_distillation_teacher: false
  is_common_finetune_base: false
  openrouter_ranking: null
  open_webui_ranking: null
  atom_project_rank: null                      # The ATOM Project download ranking
  notable_users: []                            # organizations publicly using this model

# ═══════════════════════════════════════════════════════════════════════
# SECTION 14: PRIVATE DOWNSELECT
# Institution-specific evaluation. This is YOUR data, not public.
# ═══════════════════════════════════════════════════════════════════════
downselect:
  compliance_tags: []                          # fedramp-high | fedramp-moderate | hipaa | sox | itar | cmmc
  clearance_tags: []                           # approved-cui | approved-fouo | unclass-only
  defense_tags: []                             # approved-dod | approved-ic | five-eyes-ok
  sovereignty_tags: []                         # us-only-hosting | eu-data-ok | no-cn-origin
  use_case_tags: []                            # rag-pipeline | code-assistant | customer-facing | internal-only
  
  eval_status: ""                              # eval-complete | eval-pending | eval-failed | not-started
  risk_tier: ""                                # low | medium | high | critical
  cost_tier: ""                                # budget-approved | budget-review | rejected
  
  custom_score: null                           # 0-100, composite from your eval pipeline
  custom_notes: ""
  reviewed_by: ""
  review_date: ""
  approval_authority: ""
  next_review_date: ""

# ═══════════════════════════════════════════════════════════════════════
# SECTION 15: METADATA & SOURCING
# Where this card's data came from. Provenance for the card itself.
# ═══════════════════════════════════════════════════════════════════════
sources:
  models_dev_url: ""
  provider_docs_url: ""
  huggingface_url: ""
  arxiv_url: ""
  paper_url: ""
  github_url: ""
  ollama_url: ""
  lm_studio_url: ""
  artificial_analysis_url: ""
  arena_url: ""
  helm_url: ""
  
  # Source freshness tracking (for backend researcher)
  last_scraped_models_dev: ""
  last_scraped_huggingface: ""
  last_scraped_benchmarks: ""
  last_scraped_pricing: ""
  last_scraped_performance: ""

card_schema_version: "3.0"
card_author: ""
card_created: ""
card_updated: ""
card_completeness: null                        # 0-100, auto-calculated: % of relevant fields filled
card_fields_total: null                        # total applicable fields for this model_type
card_fields_filled: null                       # how many are non-null
---

# {Model Display Name}

## Overview
<!-- 2-3 sentences: what is it, what architecture, what it's best at -->

## Architecture Notes
<!-- Technical details: MoE routing, attention innovations, training approach -->

## Strengths
<!-- What it does better than alternatives in its category -->

## Weaknesses & Limitations
<!-- Honest assessment: failure modes, gaps, known issues -->

## Recommended Use Cases
<!-- Specific scenarios mapped to hardware where this model excels -->

## Hardware Deployment Guide
<!-- Practical: which quant on which device, expected performance, gotchas -->

## Risk & Compliance Notes
<!-- Export control, bias concerns, regulatory alignment, data sovereignty -->

## Competitive Landscape
<!-- How this compares to direct alternatives in its weight/price class -->

## Changelog
| Date | Change | Author |
|------|--------|--------|
