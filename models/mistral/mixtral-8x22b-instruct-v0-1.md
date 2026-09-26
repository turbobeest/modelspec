---
model_id: mistral/mixtral-8x22b-instruct-v0-1
display_name: Mixtral 8x22B Instruct v0.1
provider: mistral
provider_display: Mistral AI
family: mistral
version: ''
release_date: '2024-04-16'
last_updated: ''
status: active
model_type: llm-chat
model_subtypes: []
tags:
- openai-compatible
pipeline_tag: ''
architecture:
  type: null
  total_parameters: 140630071296
  active_parameters: 39160774656
  num_experts: 8
  experts_per_token: 2
  num_layers: 56
  hidden_size: 6144
  intermediate_size: 16384
  attention_type: null
  num_attention_heads: 48
  num_kv_heads: 8
  positional_encoding: null
  rope_theta: null
  vocab_size: 32768
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
  base_model: mistralai/Mixtral-8x22B-v0.1
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
  license_url: https://huggingface.co/mistralai/Mixtral-8x22B-Instruct-v0.1/raw/main/README.md
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
    context_window: 65536
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
  input: 0.65
  output: 0.65
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
    model_id: mistralai/Mixtral-8x22B-Instruct-v0.1
    url: https://huggingface.co/mistralai/Mixtral-8x22B-Instruct-v0.1
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
  scores:
    gsm8k: 88.0
  evidence:
  - benchmark_id: arena_elo_style_control
    model_id_as_evaluated: mixtral-8x22b-instruct-v0.1
    score: 1229.28
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / overall, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category overall,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1229.28 [1224.72, 1233.84], 51416
      votes, rank 318.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_coding
    model_id_as_evaluated: mixtral-8x22b-instruct-v0.1
    score: 1277.63
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / coding, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category coding,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1277.63 [1269.00, 1286.26], 8780
      votes, rank 309.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_hard_prompts
    model_id_as_evaluated: mixtral-8x22b-instruct-v0.1
    score: 1243.5
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / hard_prompts, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category hard_prompts,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1243.50 [1236.51, 1250.49], 14707
      votes, rank 314.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_math
    model_id_as_evaluated: mixtral-8x22b-instruct-v0.1
    score: 1228.02
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / math, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category math, leaderboard_publish_date
      2026-09-13; style control. Highest-effort row for the product (effort: default; MODEL-123
      max-effort rule). Rating 1228.02 [1219.01, 1237.02], 6778 votes, rank 291.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_creative_writing
    model_id_as_evaluated: mixtral-8x22b-instruct-v0.1
    score: 1190.12
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / creative_writing, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category creative_writing,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1190.12 [1180.74, 1199.51], 7447
      votes, rank 320.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_instruction_following
    model_id_as_evaluated: mixtral-8x22b-instruct-v0.1
    score: 1215.07
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / instruction_following, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category instruction_following,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1215.07 [1208.51, 1221.63], 18515
      votes, rank 314.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_multi_turn
    model_id_as_evaluated: mixtral-8x22b-instruct-v0.1
    score: 1188.85
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / multi_turn, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category multi_turn,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1188.85 [1179.78, 1197.93], 7764
      votes, rank 326.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_expert
    model_id_as_evaluated: mixtral-8x22b-instruct-v0.1
    score: 1218.04
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / expert, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category expert,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1218.04 [1204.21, 1231.87], 2582
      votes, rank 309.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_longer_query
    model_id_as_evaluated: mixtral-8x22b-instruct-v0.1
    score: 1218.86
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / longer_query, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category longer_query,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1218.86 [1208.98, 1228.74], 5865
      votes, rank 324.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_non_english
    model_id_as_evaluated: mixtral-8x22b-instruct-v0.1
    score: 1196.75
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / non_english, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category non_english,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1196.75 [1190.46, 1203.04], 21524
      votes, rank 321.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_medicine
    model_id_as_evaluated: mixtral-8x22b-instruct-v0.1
    score: 1235.75
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
      (effort: default; MODEL-123 max-effort rule). Rating 1235.75 [1221.89, 1249.62], 2823
      votes, rank 312.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_legal
    model_id_as_evaluated: mixtral-8x22b-instruct-v0.1
    score: 1255.08
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
      (effort: default; MODEL-123 max-effort rule). Rating 1255.08 [1241.45, 1268.72], 2798
      votes, rank 311.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_business
    model_id_as_evaluated: mixtral-8x22b-instruct-v0.1
    score: 1210.6
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
      (effort: default; MODEL-123 max-effort rule). Rating 1210.60 [1200.43, 1220.78], 5554
      votes, rank 322.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_science
    model_id_as_evaluated: mixtral-8x22b-instruct-v0.1
    score: 1248.9
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
      (effort: default; MODEL-123 max-effort rule). Rating 1248.90 [1239.82, 1257.99], 8677
      votes, rank 315.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_writing
    model_id_as_evaluated: mixtral-8x22b-instruct-v0.1
    score: 1209.05
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
      (effort: default; MODEL-123 max-effort rule). Rating 1209.05 [1201.40, 1216.70], 12808
      votes, rank 317.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arc_challenge
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 72.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#arc_challenge#29dd1242f5da
  - benchmark_id: bbh
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 61.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-06-26T15-18-07.434042.json
    source_kind: benchmark_author
    evidence_date: '2024-06-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v2-8fee2c3f372b
      snapshot_ref: sha256:f97330c37d9afa4698c9c2a2d2f121ce2f923a8d9afe59b5014746f539833dd1
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#bbh#d87d849e0279
  - benchmark_id: hellaswag
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 89.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#hellaswag#f7c062f182e1
  - benchmark_id: ifeval
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 71.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-06-26T15-18-07.434042.json
    source_kind: benchmark_author
    evidence_date: '2024-06-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v2-8fee2c3f372b
      snapshot_ref: sha256:f97330c37d9afa4698c9c2a2d2f121ce2f923a8d9afe59b5014746f539833dd1
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#ifeval#16e67442d033
  - benchmark_id: mmlu_abstract_algebra
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 54.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_abstract_algebra#f20da49c2937
  - benchmark_id: mmlu_anatomy
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 74.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_anatomy#a515ef4b09d9
  - benchmark_id: mmlu_astronomy
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 86.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_astronomy#8e16d798dace
  - benchmark_id: mmlu_business_ethics
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 77.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_business_ethics#7658e0c1dfce
  - benchmark_id: mmlu_clinical_knowledge
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 82.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_clinical_knowledge#d38b2a1c75d3
  - benchmark_id: mmlu_college_biology
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 89.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_college_biology#560ec990d8d1
  - benchmark_id: mmlu_college_chemistry
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 56.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_college_chemistry#b9ccffe6cadf
  - benchmark_id: mmlu_college_computer_science
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 70.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_college_computer_science#e88a7d435450
  - benchmark_id: mmlu_college_mathematics
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 49.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_college_mathematics#4548344a665d
  - benchmark_id: mmlu_college_medicine
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 76.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_college_medicine#7a79d7abf1f7
  - benchmark_id: mmlu_college_physics
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 57.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_college_physics#7ba0b1d43a29
  - benchmark_id: mmlu_computer_security
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 81.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_computer_security#e1e570e4ec68
  - benchmark_id: mmlu_conceptual_physics
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 79.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_conceptual_physics#408e21edc922
  - benchmark_id: mmlu_econometrics
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 63.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_econometrics#e7a79c8b12af
  - benchmark_id: mmlu_electrical_engineering
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 75.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_electrical_engineering#e29939415453
  - benchmark_id: mmlu_elementary_mathematics
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 62.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_elementary_mathematics#556b91b33361
  - benchmark_id: mmlu_formal_logic
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 59.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_formal_logic#a0c60438e0a5
  - benchmark_id: mmlu_global_facts
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 54.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_global_facts#5850bcc7dc21
  - benchmark_id: mmlu_high_school_biology
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 90.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_high_school_biology#a8e7d967de94
  - benchmark_id: mmlu_high_school_chemistry
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 69.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_high_school_chemistry#d9a745722d59
  - benchmark_id: mmlu_high_school_computer_science
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 86.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_high_school_computer_science#4d3e7741fd24
  - benchmark_id: mmlu_high_school_european_history
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 85.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_high_school_european_history#3641f2523946
  - benchmark_id: mmlu_high_school_geography
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 89.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_high_school_geography#5acd7477f0dc
  - benchmark_id: mmlu_high_school_government_and_politics
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 96.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_high_school_government_and_politics#251bdcc7f660
  - benchmark_id: mmlu_high_school_macroeconomics
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 81.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_high_school_macroeconomics#555e664b3576
  - benchmark_id: mmlu_high_school_mathematics
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 50.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_high_school_mathematics#5c19ded59f69
  - benchmark_id: mmlu_high_school_microeconomics
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 87.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_high_school_microeconomics#d6c786355dcd
  - benchmark_id: mmlu_high_school_physics
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 50.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_high_school_physics#0e2840fb413b
  - benchmark_id: mmlu_high_school_psychology
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 92.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_high_school_psychology#1a4422ddefd4
  - benchmark_id: mmlu_high_school_statistics
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 69.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_high_school_statistics#ea63ca4cfe75
  - benchmark_id: mmlu_high_school_us_history
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 89.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_high_school_us_history#76dcf55e29ce
  - benchmark_id: mmlu_high_school_world_history
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 91.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_high_school_world_history#4618a95151b3
  - benchmark_id: mmlu_human_aging
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 80.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_human_aging#a5bf594d9b0e
  - benchmark_id: mmlu_human_sexuality
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 88.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_human_sexuality#d98a07e62970
  - benchmark_id: mmlu_international_law
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 90.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_international_law#608b1a92f2fc
  - benchmark_id: mmlu_jurisprudence
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 86.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_jurisprudence#13128623b91b
  - benchmark_id: mmlu_logical_fallacies
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 87.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_logical_fallacies#373c27af8f21
  - benchmark_id: mmlu_machine_learning
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 61.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_machine_learning#3ae1714dd97f
  - benchmark_id: mmlu_management
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 87.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_management#02de32bf5515
  - benchmark_id: mmlu_marketing
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 92.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_marketing#8c7952d3e6cf
  - benchmark_id: mmlu_medical_genetics
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 84.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_medical_genetics#a8fa4f4b06d9
  - benchmark_id: mmlu_miscellaneous
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 89.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_miscellaneous#09813818a0e3
  - benchmark_id: mmlu_moral_disputes
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 84.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_moral_disputes#e88a9c96956a
  - benchmark_id: mmlu_moral_scenarios
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 66.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_moral_scenarios#2809e0f77fe1
  - benchmark_id: mmlu_nutrition
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 87.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_nutrition#7cec9b6c23ce
  - benchmark_id: mmlu_philosophy
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 82.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_philosophy#3086876393ef
  - benchmark_id: mmlu_prehistory
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 87.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_prehistory#6ce2e5ab5fcb
  - benchmark_id: mmlu_pro
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 44.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-06-26T15-18-07.434042.json
    source_kind: benchmark_author
    evidence_date: '2024-06-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v2-8fee2c3f372b
      snapshot_ref: sha256:f97330c37d9afa4698c9c2a2d2f121ce2f923a8d9afe59b5014746f539833dd1
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_pro#5ece498947d7
  - benchmark_id: mmlu_professional_accounting
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 66.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_professional_accounting#f0a588713084
  - benchmark_id: mmlu_professional_law
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 60.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_professional_law#58292b783012
  - benchmark_id: mmlu_professional_medicine
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 88.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_professional_medicine#8cac97337a1c
  - benchmark_id: mmlu_professional_psychology
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 84.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_professional_psychology#56781f1a8571
  - benchmark_id: mmlu_public_relations
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 77.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_public_relations#749229a6f1ea
  - benchmark_id: mmlu_security_studies
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 84.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_security_studies#800d3590a045
  - benchmark_id: mmlu_sociology
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 91.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_sociology#e955e3659cbb
  - benchmark_id: mmlu_us_foreign_policy
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 96.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_us_foreign_policy#2160f8c80cd6
  - benchmark_id: mmlu_virology
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 59.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_virology#e75378097b65
  - benchmark_id: mmlu_world_religions
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 90.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#mmlu_world_religions#71db51b148d2
  - benchmark_id: musr
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 43.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-06-26T15-18-07.434042.json
    source_kind: benchmark_author
    evidence_date: '2024-06-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v2-8fee2c3f372b
      snapshot_ref: sha256:f97330c37d9afa4698c9c2a2d2f121ce2f923a8d9afe59b5014746f539833dd1
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#musr#0f88a1d2a5d6
  - benchmark_id: truthfulqa
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 68.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#truthfulqa#da6be110a62a
  - benchmark_id: winogrande
    model_id_as_evaluated: mistralai/Mixtral-8x22B-Instruct-v0.1
    score: 85.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-04-18T04-27-50.095241.json
    source_kind: benchmark_author
    evidence_date: '2024-04-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-f056592ff29d
      snapshot_ref: sha256:ec95427554c3fded8bb4b0273223b736f03ec66f0104c473844ab83b95beb260
      cited_regions:
      - rows
    id: mistral/mixtral-8x22b-instruct-v0-1#winogrande#a5f4b4059511
  benchmark_source: open-llm-leaderboard-v2, llm-stats, open-llm-leaderboard-v1
  benchmark_as_of: 2026-04
  benchmark_notes: 'MODEL-116, 2026-09-24: removed math_500 56.2 and gpqa_diamond 36.1. They came from a hand-typed
    table in scripts/enrich_open_llm.py labelled Open LLM Leaderboard v2, and do not match that leaderboard (its row
    for mistralai/Mixtral-8x22B-Instruct-v0.1 has MATH Lvl 5 Raw 18.7 and GPQA Raw 37.3). MODEL-154, read 2026-09-24:
    Rechecked ifeval, bbh, musr and mmlu_pro against this model''s own OLL v2 run (mistralai/Mixtral-8x22B-Instruct-v0.1,
    torch.bfloat16, model revision main). IFEval is the mean of strict prompt and instruction accuracy; BBH and MuSR
    are unweighted subtask means; MMLU-Pro is raw accuracy. Values are percentages rounded to one decimal, not normalized
    leaderboard scores. Source: https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-06-26T15-18-07.434042.json.'
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
  huggingface_downloads: 34434
  huggingface_likes: 748
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
  huggingface_url: https://huggingface.co/mistralai/Mixtral-8x22B-Instruct-v0.1
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


# Mixtral 8x22B Instruct v0.1

Auto-generated from HuggingFace Hub metadata for [mistralai/Mixtral-8x22B-Instruct-v0.1](https://huggingface.co/mistralai/Mixtral-8x22B-Instruct-v0.1).

Licence: apache-2.0. Creator distribution https://huggingface.co/mistralai/Mixtral-8x22B-Instruct-v0.1/raw/main/README.md (apache-2.0) and Hub cardData.license apache-2.0, read 2026-09-18.
