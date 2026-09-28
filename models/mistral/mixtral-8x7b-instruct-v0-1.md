---
model_id: mistral/mixtral-8x7b-instruct-v0-1
display_name: Mixtral 8x7B Instruct v0.1
provider: mistral
provider_display: Mistral AI
family: mistral
version: ''
release_date: '2023-12-10'
last_updated: ''
status: active
model_type: llm-chat
model_subtypes: []
tags:
- openai-compatible
pipeline_tag: ''
architecture:
  type: null
  total_parameters: 46702792704
  active_parameters: 12879659008
  num_experts: 8
  experts_per_token: 2
  num_layers: 32
  hidden_size: 4096
  intermediate_size: 14336
  attention_type: null
  num_attention_heads: 32
  num_kv_heads: 8
  positional_encoding: null
  rope_theta: null
  vocab_size: 32000
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
  base_model: mistralai/Mixtral-8x7B-v0.1
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
  library_name: vllm
licensing:
  open_weights: true
  license_type: apache-2.0
  license_url: https://huggingface.co/mistralai/Mixtral-8x7B-Instruct-v0.1/raw/main/README.md
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
  origin_country: FR
  origin_org_type: private
modalities:
  input:
  - text
  output:
  - text
  text:
    max_input_tokens: null
    max_output_tokens: null
    context_window: 32768
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
    overall: null
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
    lsp_integration: false
    repository_understanding: false
  reasoning:
    overall: null
    mathematical: false
    logical: false
    scientific: false
    planning: false
    multi_step: false
    chain_of_thought: true
    self_correction: false
    spatial: false
    temporal: false
    causal: false
    think_budget_control: false
  tool_use:
    overall: tier-2
    function_calling: true
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
  input: 0.24
  output: 0.24
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
    available: true
    model_id: ''
    url: https://groq.com/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  together_ai:
    available: true
    model_id: ''
    url: https://www.together.ai/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  fireworks_ai:
    available: true
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
    available: true
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
    available: true
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
    available: true
    model_id: ''
    url: https://ollama.com/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  lm_studio:
    available: true
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
    model_id: mistralai/Mixtral-8x7B-Instruct-v0.1
    url: https://huggingface.co/mistralai/Mixtral-8x7B-Instruct-v0.1
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
    model_id_as_evaluated: mixtral-8x7b-instruct-v0.1
    score: 1196.86
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / overall, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category overall,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1196.86 [1192.60, 1201.13], 73503
      votes, rank 335.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_coding
    model_id_as_evaluated: mixtral-8x7b-instruct-v0.1
    score: 1239.71
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / coding, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category coding,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1239.71 [1231.63, 1247.79], 11784
      votes, rank 336.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_hard_prompts
    model_id_as_evaluated: mixtral-8x7b-instruct-v0.1
    score: 1210.85
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / hard_prompts, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category hard_prompts,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1210.85 [1204.14, 1217.56], 19541
      votes, rank 337.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_math
    model_id_as_evaluated: mixtral-8x7b-instruct-v0.1
    score: 1190.85
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / math, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category math, leaderboard_publish_date
      2026-09-13; style control. Highest-effort row for the product (effort: default; MODEL-123
      max-effort rule). Rating 1190.85 [1182.23, 1199.46], 9663 votes, rank 322.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_creative_writing
    model_id_as_evaluated: mixtral-8x7b-instruct-v0.1
    score: 1159.03
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / creative_writing, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category creative_writing,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1159.03 [1150.36, 1167.69], 11172
      votes, rank 334.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_instruction_following
    model_id_as_evaluated: mixtral-8x7b-instruct-v0.1
    score: 1180.46
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / instruction_following, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category instruction_following,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1180.46 [1174.14, 1186.78], 24974
      votes, rank 334.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_multi_turn
    model_id_as_evaluated: mixtral-8x7b-instruct-v0.1
    score: 1167.68
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / multi_turn, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category multi_turn,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1167.68 [1159.04, 1176.32], 10873
      votes, rank 331.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_expert
    model_id_as_evaluated: mixtral-8x7b-instruct-v0.1
    score: 1196.84
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / expert, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category expert,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1196.84 [1183.80, 1209.89], 3240
      votes, rank 320.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_longer_query
    model_id_as_evaluated: mixtral-8x7b-instruct-v0.1
    score: 1183.42
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / longer_query, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category longer_query,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1183.42 [1173.85, 1192.99], 6572
      votes, rank 340.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_non_english
    model_id_as_evaluated: mixtral-8x7b-instruct-v0.1
    score: 1145.83
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / non_english, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category non_english,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1145.83 [1139.70, 1151.97], 27205
      votes, rank 341.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_medicine
    model_id_as_evaluated: mixtral-8x7b-instruct-v0.1
    score: 1207.01
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
      (effort: default; MODEL-123 max-effort rule). Rating 1207.01 [1194.26, 1219.76], 4050
      votes, rank 324.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_legal
    model_id_as_evaluated: mixtral-8x7b-instruct-v0.1
    score: 1224.23
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
      (effort: default; MODEL-123 max-effort rule). Rating 1224.23 [1211.52, 1236.94], 3953
      votes, rank 320.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_business
    model_id_as_evaluated: mixtral-8x7b-instruct-v0.1
    score: 1177.14
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
      (effort: default; MODEL-123 max-effort rule). Rating 1177.14 [1167.25, 1187.03], 7070
      votes, rank 333.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_science
    model_id_as_evaluated: mixtral-8x7b-instruct-v0.1
    score: 1213.27
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
      (effort: default; MODEL-123 max-effort rule). Rating 1213.27 [1204.84, 1221.70], 12824
      votes, rank 334.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_writing
    model_id_as_evaluated: mixtral-8x7b-instruct-v0.1
    score: 1170.22
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
      (effort: default; MODEL-123 max-effort rule). Rating 1170.22 [1162.89, 1177.55], 17942
      votes, rank 338.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: gpqa_diamond
    model_id_as_evaluated: Mixtral-8x7B-Instruct-v0.1
    score: 30.59
    unit: percent
    source_url: https://epoch.ai/benchmarks/gpqa-diamond
    source_kind: independent_evaluator
    evidence_date: '2025-01-27'
    date_type: evaluated
    verified_at: '2026-09-24'
    benchmark_version: GPQA Diamond (Epoch AI run)
    configuration: Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (gpqa_diamond.csv),
      read 2026-09-24. Run started 2025-01-27T00:00:00.000Z; effort default; highest-effort
      run for the model (MODEL-123 max-effort rule), newest on a tie. Standard error 1.94 points.
    limitations: Epoch AI data, CC BY 4.0.
  - benchmark_id: arc_challenge
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 70.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#arc_challenge#b6b3a7a98eec
  - benchmark_id: bbh
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 49.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-09-26'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-4bd4d8c7144a
      snapshot_ref: sha256:70add990f890a23c496f5da3ec5e7b56150bbd8b70681295c56d732077431a40
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#bbh#647bf1d46e8b
  - benchmark_id: gsm8k
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 61.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#gsm8k#462d37c88df3
  - benchmark_id: hellaswag
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 87.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#hellaswag#f847dd6107b0
  - benchmark_id: ifeval
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 56.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-09-26'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-4bd4d8c7144a
      snapshot_ref: sha256:70add990f890a23c496f5da3ec5e7b56150bbd8b70681295c56d732077431a40
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#ifeval#33bc64daed7b
  - benchmark_id: mmlu_abstract_algebra
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 42.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_abstract_algebra#b311cc0f743c
  - benchmark_id: mmlu_anatomy
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 66.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_anatomy#bdcd7c4d42e4
  - benchmark_id: mmlu_astronomy
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 78.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_astronomy#ecbc0483f9db
  - benchmark_id: mmlu_business_ethics
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 73.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_business_ethics#e37948a4773a
  - benchmark_id: mmlu_clinical_knowledge
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 77.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_clinical_knowledge#3f5ed9be8d36
  - benchmark_id: mmlu_college_biology
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 82.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_college_biology#6f18c4096cc2
  - benchmark_id: mmlu_college_chemistry
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 50.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_college_chemistry#36bb5bbb4981
  - benchmark_id: mmlu_college_computer_science
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 66.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_college_computer_science#6fd4bec3c825
  - benchmark_id: mmlu_college_mathematics
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 46.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_college_mathematics#a0f13135c4b6
  - benchmark_id: mmlu_college_medicine
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 75.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_college_medicine#c11ba8e1573d
  - benchmark_id: mmlu_college_physics
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 43.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_college_physics#2e55019ff683
  - benchmark_id: mmlu_computer_security
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 81.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_computer_security#f0c80c3ae74f
  - benchmark_id: mmlu_conceptual_physics
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 66.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_conceptual_physics#a471ffd62004
  - benchmark_id: mmlu_econometrics
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 61.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_econometrics#d04d17c2af85
  - benchmark_id: mmlu_electrical_engineering
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 64.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_electrical_engineering#9efa7927933d
  - benchmark_id: mmlu_elementary_mathematics
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 47.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_elementary_mathematics#742549f05723
  - benchmark_id: mmlu_formal_logic
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 52.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_formal_logic#30b82fedc0c4
  - benchmark_id: mmlu_global_facts
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 42.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_global_facts#5b865f6074f9
  - benchmark_id: mmlu_high_school_biology
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 85.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_high_school_biology#2e69db2fa681
  - benchmark_id: mmlu_high_school_chemistry
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 62.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_high_school_chemistry#939bff6c9441
  - benchmark_id: mmlu_high_school_computer_science
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 78.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_high_school_computer_science#e756305f2575
  - benchmark_id: mmlu_high_school_european_history
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 80.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_high_school_european_history#da34a440d7e0
  - benchmark_id: mmlu_high_school_geography
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 86.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_high_school_geography#5017613b253b
  - benchmark_id: mmlu_high_school_government_and_politics
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 95.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_high_school_government_and_politics#bb0124481989
  - benchmark_id: mmlu_high_school_macroeconomics
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 69.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_high_school_macroeconomics#267172b44b4e
  - benchmark_id: mmlu_high_school_mathematics
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 38.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_high_school_mathematics#08e4de9a01bc
  - benchmark_id: mmlu_high_school_microeconomics
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 80.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_high_school_microeconomics#40a3de2cb415
  - benchmark_id: mmlu_high_school_physics
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 47.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_high_school_physics#15cd7f23adf6
  - benchmark_id: mmlu_high_school_psychology
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 88.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_high_school_psychology#4cf05f06f1ad
  - benchmark_id: mmlu_high_school_statistics
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 59.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_high_school_statistics#403e834493c2
  - benchmark_id: mmlu_high_school_us_history
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 85.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_high_school_us_history#6f19be808a8a
  - benchmark_id: mmlu_high_school_world_history
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 84.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_high_school_world_history#b83ba92e5357
  - benchmark_id: mmlu_human_aging
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 75.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_human_aging#c4a5c2d037ea
  - benchmark_id: mmlu_human_sexuality
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 80.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_human_sexuality#c60d78dc4411
  - benchmark_id: mmlu_international_law
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 87.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_international_law#8dbc39f035f5
  - benchmark_id: mmlu_jurisprudence
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 84.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_jurisprudence#9c9fd43bf421
  - benchmark_id: mmlu_logical_fallacies
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 81.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_logical_fallacies#26ad0c7c9d72
  - benchmark_id: mmlu_machine_learning
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 57.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_machine_learning#c1e24fcb160e
  - benchmark_id: mmlu_management
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 84.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_management#6c6118e8c28b
  - benchmark_id: mmlu_marketing
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 92.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_marketing#a50b3b5061eb
  - benchmark_id: mmlu_medical_genetics
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 77.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_medical_genetics#4005127a0fa7
  - benchmark_id: mmlu_miscellaneous
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 88.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_miscellaneous#3a527792c19f
  - benchmark_id: mmlu_moral_disputes
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 78.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_moral_disputes#c85f27ace2f1
  - benchmark_id: mmlu_moral_scenarios
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 46.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_moral_scenarios#39ecdb5c3afa
  - benchmark_id: mmlu_nutrition
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 82.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_nutrition#8a195c7933a6
  - benchmark_id: mmlu_philosophy
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 79.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_philosophy#0fef09fb55d9
  - benchmark_id: mmlu_prehistory
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 83.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_prehistory#46b7a441f1ca
  - benchmark_id: mmlu_pro
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 36.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-09-26'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-4bd4d8c7144a
      snapshot_ref: sha256:70add990f890a23c496f5da3ec5e7b56150bbd8b70681295c56d732077431a40
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_pro#abdc11ec345c
  - benchmark_id: mmlu_professional_accounting
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 55.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_professional_accounting#8b38872a64e5
  - benchmark_id: mmlu_professional_law
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 54.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_professional_law#966ff48d911f
  - benchmark_id: mmlu_professional_medicine
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 79.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_professional_medicine#9ae755369e4a
  - benchmark_id: mmlu_professional_psychology
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 76.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_professional_psychology#cb87cbf25adf
  - benchmark_id: mmlu_public_relations
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 70.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_public_relations#b4cb6dce0e08
  - benchmark_id: mmlu_security_studies
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 77.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_security_studies#f183774a4445
  - benchmark_id: mmlu_sociology
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 89.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_sociology#8ff829c2459a
  - benchmark_id: mmlu_us_foreign_policy
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 90.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_us_foreign_policy#bd2a083a2dc3
  - benchmark_id: mmlu_virology
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 50.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_virology#038dcefeec86
  - benchmark_id: mmlu_world_religions
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 87.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#mmlu_world_religions#bb054110e596
  - benchmark_id: musr
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 42.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-09-26'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-4bd4d8c7144a
      snapshot_ref: sha256:70add990f890a23c496f5da3ec5e7b56150bbd8b70681295c56d732077431a40
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#musr#dab1b7efd249
  - benchmark_id: truthfulqa
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 65.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#truthfulqa#455bf4d41b6e
  - benchmark_id: winogrande
    model_id_as_evaluated: mistralai/Mixtral-8x7B-Instruct-v0.1
    score: 81.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2024-01-05T04-20-22.140239.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-459dba707d22
      snapshot_ref: sha256:9b15ea9f5d2dd18b1d93fdcc168032d166d659c0b0bbde4a0c8d639fd47fcdb2
      cited_regions:
      - rows
    id: mistral/mixtral-8x7b-instruct-v0-1#winogrande#4faaa3fd9b54
  benchmark_source: open-llm-leaderboard-v2, open-llm-leaderboard-v1
  benchmark_as_of: 2026-04
  benchmark_notes: 'MODEL-116, 2026-09-24: removed math_500 40.1 and gpqa_diamond 27.2. They came from a hand-typed
    table in scripts/enrich_open_llm.py labelled Open LLM Leaderboard v2, and do not match that leaderboard (its row
    for mistralai/Mixtral-8x7B-Instruct-v0.1 has MATH Lvl 5 Raw 9.1 and GPQA Raw 30.3). MODEL-154, read 2026-09-24:
    Rechecked ifeval, bbh, musr and mmlu_pro against this model''s own OLL v2 run (mistralai/Mixtral-8x7B-Instruct-v0.1,
    torch.bfloat16, model revision 41bd4c9e7e4fb318ca40e721131d4933966c2cc1). IFEval is the mean of strict prompt
    and instruction accuracy; BBH and MuSR are unweighted subtask means; MMLU-Pro is raw accuracy. Values are percentages
    rounded to one decimal, not normalized leaderboard scores. Source: https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2025-02-13T18-27-04.338360.json.'
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
    vllm: true
    trt_llm: false
    mlx: false
    llama_cpp: false
    sglang: false
    transformers: false
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
  huggingface_downloads: 433678
  huggingface_likes: 4654
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
  huggingface_url: https://huggingface.co/mistralai/Mixtral-8x7B-Instruct-v0.1
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


# Mixtral 8x7B Instruct v0.1

Auto-generated from HuggingFace Hub metadata for [mistralai/Mixtral-8x7B-Instruct-v0.1](https://huggingface.co/mistralai/Mixtral-8x7B-Instruct-v0.1).

Licence: apache-2.0. Creator distribution https://huggingface.co/mistralai/Mixtral-8x7B-Instruct-v0.1/raw/main/README.md (apache-2.0) and Hub cardData.license apache-2.0, read 2026-09-18.
