---
model_id: microsoft/phi-3-mini-4k-instruct
display_name: Phi 3 mini 4K instruct
provider: microsoft
provider_display: Microsoft
family: phi
version: ''
release_date: '2024-04-22'
last_updated: ''
status: active
model_type: llm-code
model_subtypes: []
tags:
- text-generation
pipeline_tag: text-generation
architecture:
  type: null
  total_parameters: 3821079552
  active_parameters: null
  num_experts: null
  experts_per_token: null
  num_layers: 32
  hidden_size: 3072
  intermediate_size: 8192
  attention_type: null
  num_attention_heads: 32
  num_kv_heads: 32
  positional_encoding: null
  rope_theta: null
  vocab_size: 32064
  tokenizer_type: null
  embedding_dimensions: null
  activation_function: ''
  precision_native: ''
  flash_attention: null
  tie_word_embeddings: null
  sliding_window_size: null
  vision_encoder: ''
  vision_resolution_max: ''
  vision_patch_size: null
  diffusion_scheduler: ''
  diffusion_steps_default: null
  vae_type: ''
  total_parameters_source: safetensors
lineage:
  base_model: ''
  base_model_relation: null
  merge_models: []
  adapter_type: ''
  adapter_rank: null
  training_datasets: []
  training_data_tokens: null
  training_data_cutoff: ''
  training_compute_flops: null
  training_hardware: ''
  training_time: ''
  training_cost_estimate: ''
  training_method: null
  co2_emissions_kg: null
  co2_source: ''
  energy_kwh: null
  library_name: transformers
licensing:
  open_weights: true
  license_type: mit
  license_url: https://huggingface.co/microsoft/Phi-3-mini-4k-instruct/raw/main/LICENSE
  tos_url: ''
  acceptable_use_policy_url: ''
  not_for_all_audiences: false
  commercial_use: unspecified
  commercial_use_source: null
  commercial_use_conditions: ''
  defense_use: unspecified
  government_use: unspecified
  medical_use: unspecified
  academic_use: unspecified
  geographic_restrictions: []
  export_control_notes: ''
  origin_country: US
  origin_org_type: private
modalities:
  input:
  - text
  output:
  - text
  text:
    max_input_tokens: null
    max_output_tokens: null
    context_window: 4096
    streaming: null
    fill_in_middle: null
    json_mode: null
    system_prompt: null
  vision:
    supported: false
    ocr: false
    chart_reading: false
    spatial_reasoning: false
    handwriting: false
    object_detection: false
    object_counting: false
    visual_grounding: false
    max_image_resolution: ''
    max_images_per_request: null
    video_frames: false
  audio:
    input_supported: false
    output_supported: false
    realtime_streaming: false
    asr_languages: []
    tts_languages: []
    tts_voices: null
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
    max_resolution: ''
    max_fps: null
    audio_sync: false
    temporal_reasoning: false
  document:
    pdf_native: false
    table_extraction: false
    form_understanding: false
    max_pages: null
    layout_analysis: false
  image_generation:
    supported: false
    max_resolution: ''
    aspect_ratios: []
    inpainting: false
    outpainting: false
    img2img: false
    text_rendering_quality: ''
    style_control: false
    controlnet_support: false
    lora_support: false
  embeddings:
    supported: false
    dimensions: null
    dimensions_configurable: false
    dimension_options: []
    max_input_tokens: null
    similarity_metric: ''
    normalized: null
    batch_size_max: null
    instruction_aware: false
  reranking:
    supported: false
    max_input_pairs: null
    max_input_length: null
    cross_encoder: null
capabilities:
  coding:
    overall: tier-2
    languages: []
    agentic_coding: false
    code_review: false
    refactoring: false
    debugging: true
    test_generation: false
    documentation: false
    code_completion: true
    multi_file_editing: false
    fill_in_middle: false
    lsp_integration: false
    repository_understanding: false
  reasoning:
    overall: null
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
    think_budget_control: false
  tool_use:
    overall: null
    function_calling: false
    mcp_compatible: false
    parallel_tool_calls: false
    tool_selection_accuracy: null
    multi_turn_tool_use: false
    tool_error_recovery: false
    computer_use: false
  language:
    multilingual: false
    num_languages: null
    strong_languages: []
    translation_quality: null
    long_context_retrieval: null
  creative:
    writing: null
    summarization: null
    instruction_following: null
    storytelling: null
    technical_writing: null
  safety_alignment:
    alignment_approach: ''
    refusal_rate: null
    jailbreak_resistance: null
    content_safety_tier: null
    guardrail_builtin: false
  domain_specific:
    medical_knowledge: null
    legal_knowledge: null
    financial_knowledge: null
    scientific_knowledge: null
  agent_capabilities:
    autonomous_execution: false
    web_browsing: false
    file_system_access: false
    code_execution: false
    long_running_tasks: false
    memory_management: false
    self_delegation: false
cost:
  input: 0.1
  output: 0.1
  reasoning: null
  cache_read: null
  cache_write: null
  input_audio: null
  output_audio: null
  input_image: null
  output_image: null
  output_video_per_sec: null
  batch_input: null
  batch_output: null
  embedding_per_million: null
  reranking_per_million: null
  finetune_per_million_tokens: null
  finetune_hosting_per_hour: null
  free_tier: false
  free_tier_limits: ''
  note: Estimated inference cost on popular platforms ($/M tokens)
availability:
  primary_provider:
    name: ''
    platform_url: ''
    api_endpoint: ''
    npm_package: ''
    env_vars: []
    model_id_on_platform: ''
    rate_limit_rpm: null
    rate_limit_tpm: null
    sla_uptime: ''
    regions: []
    data_residency: null
    data_residency_disclosure: unresearched
    data_residency_source: null
    hipaa_eligible: false
    fedramp_authorized: false
    soc2_compliant: false
    free_tier: false
    free_tier_details: ''
  aws_bedrock:
    available: false
    model_id: ''
    url: https://aws.amazon.com/bedrock/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  azure_ai_foundry:
    available: false
    model_id: ''
    url: https://ai.azure.com/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  google_vertex_ai:
    available: false
    model_id: ''
    url: https://cloud.google.com/vertex-ai
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  nvidia_nim:
    available: false
    model_id: ''
    url: https://build.nvidia.com/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  ibm_watsonx:
    available: false
    model_id: ''
    url: https://www.ibm.com/watsonx
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  snowflake_cortex:
    available: false
    model_id: ''
    url: https://www.snowflake.com/en/data-cloud/cortex/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  groq:
    available: false
    model_id: ''
    url: https://groq.com/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  together_ai:
    available: false
    model_id: ''
    url: https://www.together.ai/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  fireworks_ai:
    available: false
    model_id: ''
    url: https://fireworks.ai/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  replicate:
    available: false
    model_id: ''
    url: https://replicate.com/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  deepinfra:
    available: false
    model_id: ''
    url: https://deepinfra.com/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  cerebras:
    available: false
    model_id: ''
    url: https://www.cerebras.ai/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  sambanova:
    available: false
    model_id: ''
    url: https://sambanova.ai/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  openrouter:
    available: false
    model_id: ''
    url: https://openrouter.ai/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  cursor:
    available: false
    model_id: ''
    url: https://cursor.com/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  github_copilot:
    available: false
    model_id: ''
    url: https://github.com/features/copilot
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  perplexity:
    available: false
    model_id: ''
    url: https://www.perplexity.ai/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  raycast:
    available: false
    model_id: ''
    url: https://www.raycast.com/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  poe:
    available: false
    model_id: ''
    url: https://poe.com/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  chatgpt:
    available: false
    model_id: ''
    url: https://chat.openai.com/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  claude_ai:
    available: false
    model_id: ''
    url: https://claude.ai/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  gemini_app:
    available: false
    model_id: ''
    url: https://gemini.google.com/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  grok_xai:
    available: false
    model_id: ''
    url: https://x.ai/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  meta_ai:
    available: false
    model_id: ''
    url: https://www.meta.ai/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  copilot_microsoft:
    available: false
    model_id: ''
    url: https://copilot.microsoft.com/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  mistral_plateforme:
    available: false
    model_id: ''
    url: https://console.mistral.ai/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  cohere:
    available: false
    model_id: ''
    url: https://cohere.com/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  ai21_labs:
    available: false
    model_id: ''
    url: https://www.ai21.com/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  stability_ai:
    available: false
    model_id: ''
    url: https://stability.ai/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  deepseek:
    available: false
    model_id: ''
    url: https://platform.deepseek.com/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  qwen_alibaba:
    available: false
    model_id: ''
    url: https://www.alibabacloud.com/en/solutions/generative-ai/qwen
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  baidu_ernie:
    available: false
    model_id: ''
    url: https://cloud.baidu.com/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  bytedance_doubao:
    available: false
    model_id: ''
    url: https://www.volcengine.com/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  tencent_hunyuan:
    available: false
    model_id: ''
    url: https://cloud.tencent.com/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  zhipu_glm:
    available: false
    model_id: ''
    url: https://www.zhipuai.cn/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  moonshot_kimi:
    available: false
    model_id: ''
    url: https://www.moonshot.cn/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  minimax:
    available: false
    model_id: ''
    url: https://www.minimax.chat/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  zero_one_ai:
    available: false
    model_id: ''
    url: https://www.01.ai/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  tii_falcon:
    available: false
    model_id: ''
    url: https://falconllm.tii.ae/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  samsung_gauss:
    available: false
    model_id: ''
    url: https://www.samsung.com/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  upstage_solar:
    available: false
    model_id: ''
    url: https://www.upstage.ai/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  ollama:
    available: false
    model_id: ''
    url: https://ollama.com/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  lm_studio:
    available: false
    model_id: ''
    url: https://lmstudio.ai/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  gpt4all:
    available: false
    model_id: ''
    url: https://gpt4all.io/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  jan_ai:
    available: false
    model_id: ''
    url: https://jan.ai/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  mlx_community:
    available: false
    model_id: ''
    url: https://huggingface.co/mlx-community
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  open_webui:
    available: false
    model_id: ''
    url: https://openwebui.com/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  huggingface:
    available: true
    model_id: microsoft/Phi-3-mini-4k-instruct
    url: https://huggingface.co/microsoft/Phi-3-mini-4k-instruct
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  modelscope:
    available: false
    model_id: ''
    url: https://modelscope.cn/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  kaggle_models:
    available: false
    model_id: ''
    url: https://www.kaggle.com/models
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  other_platforms: []
benchmarks:
  scores: {}
  evidence:
  - benchmark_id: arena_elo_style_control
    model_id_as_evaluated: phi-3-mini-4k-instruct
    score: 1127.86
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / overall, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category overall,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1127.86 [1121.46, 1134.25], 20118
      votes, rank 376.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_coding
    model_id_as_evaluated: phi-3-mini-4k-instruct
    score: 1187.61
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / coding, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category coding,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1187.61 [1175.89, 1199.34], 3449
      votes, rank 356.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_hard_prompts
    model_id_as_evaluated: phi-3-mini-4k-instruct
    score: 1152.94
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / hard_prompts, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category hard_prompts,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1152.94 [1143.35, 1162.53], 5872
      votes, rank 365.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_math
    model_id_as_evaluated: phi-3-mini-4k-instruct
    score: 1149.64
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / math, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category math, leaderboard_publish_date
      2026-09-13; style control. Highest-effort row for the product (effort: default; MODEL-123
      max-effort rule). Rating 1149.64 [1137.37, 1161.91], 2564 votes, rank 340.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_creative_writing
    model_id_as_evaluated: phi-3-mini-4k-instruct
    score: 1072.98
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / creative_writing, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category creative_writing,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1072.98 [1060.03, 1085.92], 2812
      votes, rank 385.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_instruction_following
    model_id_as_evaluated: phi-3-mini-4k-instruct
    score: 1113.25
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / instruction_following, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category instruction_following,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1113.25 [1104.36, 1122.13], 7636
      votes, rank 370.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_multi_turn
    model_id_as_evaluated: phi-3-mini-4k-instruct
    score: 1065.09
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / multi_turn, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category multi_turn,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1065.09 [1051.56, 1078.62], 2939
      votes, rank 379.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_expert
    model_id_as_evaluated: phi-3-mini-4k-instruct
    score: 1140.31
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / expert, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category expert,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1140.31 [1120.73, 1159.89], 936 votes,
      rank 339.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_longer_query
    model_id_as_evaluated: phi-3-mini-4k-instruct
    score: 1108.63
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / longer_query, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category longer_query,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1108.63 [1093.30, 1123.96], 1706
      votes, rank 368.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_non_english
    model_id_as_evaluated: phi-3-mini-4k-instruct
    score: 1074.25
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / non_english, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category non_english,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1074.25 [1065.87, 1082.63], 9796
      votes, rank 374.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_medicine
    model_id_as_evaluated: phi-3-mini-4k-instruct
    score: 1129.47
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / industry_medicine_and_healthcare, latest split,
      revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category industry_medicine_and_healthcare,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1129.47 [1108.85, 1150.09], 1078
      votes, rank 358.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_legal
    model_id_as_evaluated: phi-3-mini-4k-instruct
    score: 1154.08
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / industry_legal_and_government, latest split, revision
      1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category industry_legal_and_government,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1154.08 [1134.70, 1173.45], 1126
      votes, rank 357.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_business
    model_id_as_evaluated: phi-3-mini-4k-instruct
    score: 1111.37
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / industry_business_and_management_and_financial_operations,
      latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category industry_business_and_management_and_financial_operations,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1111.37 [1097.69, 1125.06], 2483
      votes, rank 367.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_science
    model_id_as_evaluated: phi-3-mini-4k-instruct
    score: 1145.14
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / industry_life_and_physical_and_social_science, latest
      split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category industry_life_and_physical_and_social_science,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1145.14 [1132.44, 1157.84], 3517
      votes, rank 374.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_writing
    model_id_as_evaluated: phi-3-mini-4k-instruct
    score: 1092.44
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / industry_writing_and_literature_and_language, latest
      split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category industry_writing_and_literature_and_language,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1092.44 [1081.90, 1102.98], 5207
      votes, rank 379.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arc_challenge
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 63.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#arc_challenge#69ef044b359c
  - benchmark_id: bbh
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 56.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/microsoft/Phi-3-mini-4k-instruct/results_2024-06-17T11-04-33.850464.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-17'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-878fe1d5dc11
      snapshot_ref: sha256:67cdf0020fad30be8f0aaa90921f2db262efbcbab6377d7c53a4192c63755cf8
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#bbh#a94c3f879d4e
  - benchmark_id: gsm8k
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 74.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#gsm8k#f15cd2a38164
  - benchmark_id: hellaswag
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 80.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#hellaswag#a946628d1cd0
  - benchmark_id: ifeval
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 56.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/microsoft/Phi-3-mini-4k-instruct/results_2024-06-17T11-04-33.850464.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-17'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-878fe1d5dc11
      snapshot_ref: sha256:67cdf0020fad30be8f0aaa90921f2db262efbcbab6377d7c53a4192c63755cf8
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#ifeval#ea7ee3f71b37
  - benchmark_id: mmlu_abstract_algebra
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 36.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_abstract_algebra#a37693152e35
  - benchmark_id: mmlu_anatomy
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 66.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_anatomy#3c5c536ca256
  - benchmark_id: mmlu_astronomy
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 77.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_astronomy#4b38d1a7afc2
  - benchmark_id: mmlu_business_ethics
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 68.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_business_ethics#3ae2ca0aebeb
  - benchmark_id: mmlu_clinical_knowledge
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 74.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_clinical_knowledge#7974b1e0485b
  - benchmark_id: mmlu_college_biology
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 82.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_college_biology#74a517cf7c1c
  - benchmark_id: mmlu_college_chemistry
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 47.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_college_chemistry#ac30ccd1cd5b
  - benchmark_id: mmlu_college_computer_science
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 55.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_college_computer_science#4832d1f8d944
  - benchmark_id: mmlu_college_mathematics
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 35.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_college_mathematics#937f843d9f1c
  - benchmark_id: mmlu_college_medicine
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 68.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_college_medicine#251a6fa4fdb2
  - benchmark_id: mmlu_college_physics
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 36.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_college_physics#5be825a1e6e4
  - benchmark_id: mmlu_computer_security
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 78.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_computer_security#55499c20da6e
  - benchmark_id: mmlu_conceptual_physics
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 70.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_conceptual_physics#0727f45c1af4
  - benchmark_id: mmlu_econometrics
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 45.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_econometrics#0ac654b93250
  - benchmark_id: mmlu_electrical_engineering
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 57.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_electrical_engineering#1601ee648b5b
  - benchmark_id: mmlu_elementary_mathematics
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 52.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_elementary_mathematics#1cf19cee8229
  - benchmark_id: mmlu_formal_logic
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 58.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_formal_logic#3cd6cb04d9d5
  - benchmark_id: mmlu_global_facts
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 40.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_global_facts#b4ffb3fc9539
  - benchmark_id: mmlu_high_school_biology
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 83.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_high_school_biology#b161ce7e8e94
  - benchmark_id: mmlu_high_school_chemistry
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 60.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_high_school_chemistry#429bdae9704f
  - benchmark_id: mmlu_high_school_computer_science
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 73.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_high_school_computer_science#bc53dd0efdfa
  - benchmark_id: mmlu_high_school_european_history
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 80.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_high_school_european_history#687b0e978128
  - benchmark_id: mmlu_high_school_geography
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 86.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_high_school_geography#deb26198f1b8
  - benchmark_id: mmlu_high_school_government_and_politics
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 90.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_high_school_government_and_politics#71c050efd374
  - benchmark_id: mmlu_high_school_macroeconomics
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 75.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_high_school_macroeconomics#b15b46bf0d6d
  - benchmark_id: mmlu_high_school_mathematics
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 39.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_high_school_mathematics#34764df0c42d
  - benchmark_id: mmlu_high_school_microeconomics
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 83.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_high_school_microeconomics#685436202191
  - benchmark_id: mmlu_high_school_physics
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 44.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_high_school_physics#4be77cc7c385
  - benchmark_id: mmlu_high_school_psychology
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 88.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_high_school_psychology#a88ed881a1ac
  - benchmark_id: mmlu_high_school_statistics
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 61.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_high_school_statistics#50a813703de4
  - benchmark_id: mmlu_high_school_us_history
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 79.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_high_school_us_history#e46898e1cbc4
  - benchmark_id: mmlu_high_school_world_history
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 79.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_high_school_world_history#2f926207ab70
  - benchmark_id: mmlu_human_aging
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 69.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_human_aging#1e70000038bb
  - benchmark_id: mmlu_human_sexuality
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 76.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_human_sexuality#b26cf12eba2c
  - benchmark_id: mmlu_international_law
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 85.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_international_law#d522cbf0f64e
  - benchmark_id: mmlu_jurisprudence
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 79.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_jurisprudence#2387fe1c8112
  - benchmark_id: mmlu_logical_fallacies
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 80.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_logical_fallacies#b81fe8f9ce6e
  - benchmark_id: mmlu_machine_learning
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 55.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_machine_learning#003a52c88430
  - benchmark_id: mmlu_management
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 80.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_management#f081a69e5d63
  - benchmark_id: mmlu_marketing
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 90.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_marketing#65f763641ae7
  - benchmark_id: mmlu_medical_genetics
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 81.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_medical_genetics#f22e569300b5
  - benchmark_id: mmlu_miscellaneous
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 82.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_miscellaneous#405ea66bafad
  - benchmark_id: mmlu_moral_disputes
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 75.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_moral_disputes#0c951a27ab56
  - benchmark_id: mmlu_moral_scenarios
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 58.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_moral_scenarios#fbc4e3040119
  - benchmark_id: mmlu_nutrition
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 75.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_nutrition#010bc241541c
  - benchmark_id: mmlu_philosophy
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 76.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_philosophy#3baf7241a95d
  - benchmark_id: mmlu_prehistory
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 78.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_prehistory#828ecea1e83c
  - benchmark_id: mmlu_pro
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 38.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/microsoft/Phi-3-mini-4k-instruct/results_2024-06-17T11-04-33.850464.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-17'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-878fe1d5dc11
      snapshot_ref: sha256:67cdf0020fad30be8f0aaa90921f2db262efbcbab6377d7c53a4192c63755cf8
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_pro#9eac3e79de0b
  - benchmark_id: mmlu_professional_accounting
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 58.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_professional_accounting#381025174121
  - benchmark_id: mmlu_professional_law
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 51.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_professional_law#2cc1eb98ac6b
  - benchmark_id: mmlu_professional_medicine
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 76.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_professional_medicine#84bfa38e40fd
  - benchmark_id: mmlu_professional_psychology
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 75.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_professional_psychology#295d00413e18
  - benchmark_id: mmlu_public_relations
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 73.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_public_relations#f1bd89584e2c
  - benchmark_id: mmlu_security_studies
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 76.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_security_studies#e6ebdf80820b
  - benchmark_id: mmlu_sociology
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 86.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_sociology#eafcae886560
  - benchmark_id: mmlu_us_foreign_policy
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 85.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_us_foreign_policy#81faf3d19245
  - benchmark_id: mmlu_virology
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 49.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_virology#b58f5a6047e9
  - benchmark_id: mmlu_world_religions
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 83.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#mmlu_world_religions#2f5fc5550ca2
  - benchmark_id: musr
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 39.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/microsoft/Phi-3-mini-4k-instruct/results_2024-06-17T11-04-33.850464.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-17'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-878fe1d5dc11
      snapshot_ref: sha256:67cdf0020fad30be8f0aaa90921f2db262efbcbab6377d7c53a4192c63755cf8
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#musr#b5b2e544c0fd
  - benchmark_id: truthfulqa
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 59.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#truthfulqa#f15ff5c1f0a6
  - benchmark_id: winogrande
    model_id_as_evaluated: microsoft/Phi-3-mini-4k-instruct
    score: 72.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-4k-instruct/results_2024-04-25T13-30-16.480959.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-e8b8eee41571
      snapshot_ref: sha256:d087b4ba299b5ea35b232fcca5280c5f25c4d269ca3072955916d393765ad0a1
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-4k-instruct#winogrande#06dded23113b
  benchmark_source: open-llm-leaderboard-v1, open-llm-leaderboard-v2
  benchmark_as_of: 2024-07
  benchmark_notes: 'MODEL-116, 2026-09-24: removed math_500 16.4 and gpqa_diamond 32.3. They were the Open LLM Leaderboard
    v2 MATH Lvl 5 and GPQA values for unsloth/Phi-3-mini-4k-instruct, a different repository from this card''s (microsoft/Phi-3-mini-4k-instruct).
    MODEL-154, read 2026-09-24: Rechecked ifeval, bbh, musr and mmlu_pro against this model''s own OLL v2 run (microsoft/Phi-3-mini-4k-instruct,
    torch.bfloat16, model revision ff07dc01615f8113924aed013115ab2abd32115b). IFEval is the mean of strict prompt
    and instruction accuracy; BBH and MuSR are unweighted subtask means; MMLU-Pro is raw accuracy. Values are percentages
    rounded to one decimal, not normalized leaderboard scores. Source: https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/microsoft/Phi-3-mini-4k-instruct/results_2024-06-17T11-04-33.850464.json.'
deployment:
  api_only: false
  local_inference: true
  self_hostable: true
  fine_tuning_supported: false
  fine_tuning_methods: []
  quantizations_available: []
  hardware_profiles:
    nvidia_5090_32gb:
      fits: null
      best_quant: ''
      vram_usage_gb: null
      ram_usage_gb: null
      tokens_per_sec: null
      prompt_tps: null
      ttft_ms: null
      max_context_at_quant: null
      inference_engine: ''
      notes: ''
    dgx_spark_128gb:
      fits: null
      best_quant: ''
      vram_usage_gb: null
      ram_usage_gb: null
      tokens_per_sec: null
      prompt_tps: null
      ttft_ms: null
      max_context_at_quant: null
      inference_engine: ''
      notes: ''
    macbook_m4_pro_64gb:
      fits: null
      best_quant: ''
      vram_usage_gb: null
      ram_usage_gb: null
      tokens_per_sec: null
      prompt_tps: null
      ttft_ms: null
      max_context_at_quant: null
      inference_engine: ''
      notes: ''
    macbook_air_m4_24gb:
      fits: null
      best_quant: ''
      vram_usage_gb: null
      ram_usage_gb: null
      tokens_per_sec: null
      prompt_tps: null
      ttft_ms: null
      max_context_at_quant: null
      inference_engine: ''
      notes: ''
  custom_hardware: []
  runtimes:
    gguf: false
    ollama: false
    ollama_tag: ''
    lm_studio: false
    vllm: false
    trt_llm: false
    mlx: false
    llama_cpp: false
    sglang: false
    transformers: true
    exllamav2: false
    core_ml: false
    onnx: false
    triton: false
    nim: false
risk_governance:
  valid_and_reliable: ''
  safe: ''
  secure_and_resilient: ''
  accountable_and_transparent: ''
  explainable_and_interpretable: ''
  privacy_enhanced: ''
  fair_with_bias_managed: ''
  bias_evaluation:
    conducted: false
    methodology: ''
    results_summary: ''
    known_biases: []
  adversarial_robustness: untested
  privacy:
    data_retention_policy: ''
    pii_handling: ''
    training_data_pii_scrubbed: null
    data_processing_location: []
    gdpr_compliant: null
    hipaa_eligible: null
    ccpa_compliant: null
  supply_chain:
    training_data_transparency: ''
    model_provenance_documented: false
    third_party_dependencies: []
    ai_bom_available: false
    reproducible: false
  incident_history: []
  known_failure_modes: []
  regulatory:
    eu_ai_act_risk_level: null
    nist_rmf_profile: ''
    iso_42001_certified: null
    soc2_type2: null
    fedramp_level: ''
inference_performance:
  api_latency_p50_ms: null
  api_latency_p99_ms: null
  api_ttft_ms: null
  api_tps_output: null
  api_tps_input: null
  context_speed_degradation: ''
  generation_time_sec: null
  quality_per_dollar: null
  quality_per_watt: null
adoption:
  huggingface_downloads: 678067
  huggingface_likes: 1405
  ollama_pulls: null
  community_forks: null
  is_common_distillation_teacher: false
  is_common_finetune_base: false
  openrouter_ranking: null
  open_webui_ranking: null
  notable_users: []
downselect:
  compliance_tags: []
  clearance_tags: []
  defense_tags: []
  sovereignty_tags: []
  use_case_tags: []
  eval_status: null
  risk_tier: null
  cost_tier: ''
  custom_score: null
  custom_notes: ''
  reviewed_by: ''
  review_date: ''
  approval_authority: ''
  next_review_date: ''
sources:
  models_dev_url: ''
  provider_docs_url: ''
  huggingface_url: https://huggingface.co/microsoft/Phi-3-mini-4k-instruct
  arxiv_url: ''
  paper_url: ''
  github_url: ''
  ollama_url: ''
  artificial_analysis_url: ''
  arena_url: ''
  last_scraped_models_dev: ''
  last_scraped_huggingface: '2026-09-18'
  last_scraped_benchmarks: ''
  last_scraped_pricing: ''
card_schema_version: '3.0'
card_author: huggingface-seeder
card_created: '2026-04-05'
card_updated: '2026-09-18'
---

# Phi 3 mini 4K instruct

Auto-generated from HuggingFace Hub metadata for [microsoft/Phi-3-mini-4k-instruct](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct).

Licence: mit. Creator LICENSE file https://huggingface.co/microsoft/Phi-3-mini-4k-instruct/raw/main/LICENSE (MIT License) and Hub cardData.license mit, read 2026-09-18.
