---
model_id: google/gemma-2b-it
display_name: gemma 2B it
provider: google
provider_display: Google DeepMind
family: gemma
version: ''
release_date: '2024-02-08'
last_updated: ''
status: active
model_type: llm-chat
model_subtypes: []
tags:
- text-generation
pipeline_tag: text-generation
architecture:
  type: null
  total_parameters: 2506172416
  active_parameters: null
  num_experts: null
  experts_per_token: null
  num_layers: null
  hidden_size: null
  intermediate_size: null
  attention_type: null
  num_attention_heads: null
  num_kv_heads: null
  positional_encoding: null
  rope_theta: null
  vocab_size: null
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
  license_type: gemma
  license_url: ''
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
    context_window: 8192
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
  input: null
  output: null
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
  note: ''
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
    model_id: google/gemma-2b-it
    url: https://huggingface.co/google/gemma-2b-it
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
    model_id_as_evaluated: gemma-2b-it
    score: 1093.27
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / overall, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category overall,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1093.27 [1081.80, 1104.73], 4780
      votes, rank 387.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_coding
    model_id_as_evaluated: gemma-2b-it
    score: 1136.34
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / coding, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category coding,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1136.34 [1114.44, 1158.24], 742 votes,
      rank 379.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_hard_prompts
    model_id_as_evaluated: gemma-2b-it
    score: 1111.54
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / hard_prompts, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category hard_prompts,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1111.54 [1094.04, 1129.03], 1191
      votes, rank 383.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_math
    model_id_as_evaluated: gemma-2b-it
    score: 1072.57
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / math, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category math, leaderboard_publish_date
      2026-09-13; style control. Highest-effort row for the product (effort: default; MODEL-123
      max-effort rule). Rating 1072.57 [1050.59, 1094.56], 597 votes, rank 368.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_creative_writing
    model_id_as_evaluated: gemma-2b-it
    score: 1078.2
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / creative_writing, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category creative_writing,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1078.20 [1054.91, 1101.50], 696 votes,
      rank 384.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_instruction_following
    model_id_as_evaluated: gemma-2b-it
    score: 1070.17
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / instruction_following, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category instruction_following,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1070.17 [1054.07, 1086.27], 1522
      votes, rank 385.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_multi_turn
    model_id_as_evaluated: gemma-2b-it
    score: 1035.06
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / multi_turn, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category multi_turn,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1035.06 [1011.79, 1058.32], 768 votes,
      rank 388.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_longer_query
    model_id_as_evaluated: gemma-2b-it
    score: 1084.95
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / longer_query, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category longer_query,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1084.95 [1054.03, 1115.87], 377 votes,
      rank 374.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_non_english
    model_id_as_evaluated: gemma-2b-it
    score: 1052.73
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / non_english, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category non_english,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1052.73 [1037.07, 1068.40], 1752
      votes, rank 383.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_medicine
    model_id_as_evaluated: gemma-2b-it
    score: 1089.13
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
      (effort: default; MODEL-123 max-effort rule). Rating 1089.13 [1050.90, 1127.37], 292 votes,
      rank 366.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_legal
    model_id_as_evaluated: gemma-2b-it
    score: 1138.88
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
      (effort: default; MODEL-123 max-effort rule). Rating 1138.88 [1100.94, 1176.82], 273 votes,
      rank 362.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_business
    model_id_as_evaluated: gemma-2b-it
    score: 1101.05
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
      (effort: default; MODEL-123 max-effort rule). Rating 1101.05 [1073.03, 1129.08], 447 votes,
      rank 372.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_science
    model_id_as_evaluated: gemma-2b-it
    score: 1075.37
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
      (effort: default; MODEL-123 max-effort rule). Rating 1075.37 [1052.46, 1098.28], 879 votes,
      rank 388.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_writing
    model_id_as_evaluated: gemma-2b-it
    score: 1057.3
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
      (effort: default; MODEL-123 max-effort rule). Rating 1057.30 [1038.56, 1076.04], 1152
      votes, rank 388.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arc_challenge
    model_id_as_evaluated: google/gemma-2b-it
    score: 43.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#arc_challenge#1e13c1e3c0f5
  - benchmark_id: bbh
    model_id_as_evaluated: google/gemma-2b-it
    score: 31.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/google/gemma-2b-it/results_2025-02-13T18-27-04.338360.json
    source_kind: benchmark_author
    evidence_date: '2024-06-17'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v2-10ac5516f60b
      snapshot_ref: sha256:0a51512e84e680e50294e8bc32f8a212f65e8db55f30583b25e8b572e29864f3
      cited_regions:
      - rows
    id: google/gemma-2b-it#bbh#cdfe7b201745
  - benchmark_id: gpqa_pooled
    model_id_as_evaluated: google/gemma-2b-it
    score: 27.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/google/gemma-2b-it/results_2025-02-13T18-27-04.338360.json
    source_kind: benchmark_author
    evidence_date: '2024-06-17'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v2-10ac5516f60b
      snapshot_ref: sha256:0a51512e84e680e50294e8bc32f8a212f65e8db55f30583b25e8b572e29864f3
      cited_regions:
      - rows
    id: google/gemma-2b-it#gpqa_pooled#ace65ea41fd7
  - benchmark_id: gsm8k
    model_id_as_evaluated: google/gemma-2b-it
    score: 5.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#gsm8k#86e5f30fcb32
  - benchmark_id: hellaswag
    model_id_as_evaluated: google/gemma-2b-it
    score: 62.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#hellaswag#de5cd521a129
  - benchmark_id: ifeval
    model_id_as_evaluated: google/gemma-2b-it
    score: 26.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/google/gemma-2b-it/results_2025-02-13T18-27-04.338360.json
    source_kind: benchmark_author
    evidence_date: '2024-06-17'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v2-10ac5516f60b
      snapshot_ref: sha256:0a51512e84e680e50294e8bc32f8a212f65e8db55f30583b25e8b572e29864f3
      cited_regions:
      - rows
    id: google/gemma-2b-it#ifeval#85df9579dc83
  - benchmark_id: math_lvl5
    model_id_as_evaluated: google/gemma-2b-it
    score: 2.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/google/gemma-2b-it/results_2025-02-13T18-27-04.338360.json
    source_kind: benchmark_author
    evidence_date: '2024-06-17'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v2-10ac5516f60b
      snapshot_ref: sha256:0a51512e84e680e50294e8bc32f8a212f65e8db55f30583b25e8b572e29864f3
      cited_regions:
      - rows
    id: google/gemma-2b-it#math_lvl5#64bb1e37f6b2
  - benchmark_id: mmlu_abstract_algebra
    model_id_as_evaluated: google/gemma-2b-it
    score: 28.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_abstract_algebra#140c13cf0c2e
  - benchmark_id: mmlu_anatomy
    model_id_as_evaluated: google/gemma-2b-it
    score: 38.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_anatomy#8ebbbd9e4097
  - benchmark_id: mmlu_astronomy
    model_id_as_evaluated: google/gemma-2b-it
    score: 33.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_astronomy#ecf078e8dd25
  - benchmark_id: mmlu_business_ethics
    model_id_as_evaluated: google/gemma-2b-it
    score: 48.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_business_ethics#1c1d625bf66c
  - benchmark_id: mmlu_clinical_knowledge
    model_id_as_evaluated: google/gemma-2b-it
    score: 42.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_clinical_knowledge#4589996fc961
  - benchmark_id: mmlu_college_biology
    model_id_as_evaluated: google/gemma-2b-it
    score: 34.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_college_biology#a0257cd6f381
  - benchmark_id: mmlu_college_chemistry
    model_id_as_evaluated: google/gemma-2b-it
    score: 26.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_college_chemistry#00e91a6bd4fe
  - benchmark_id: mmlu_college_computer_science
    model_id_as_evaluated: google/gemma-2b-it
    score: 31.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_college_computer_science#66d6991f05ec
  - benchmark_id: mmlu_college_mathematics
    model_id_as_evaluated: google/gemma-2b-it
    score: 26.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_college_mathematics#4ec305283b58
  - benchmark_id: mmlu_college_medicine
    model_id_as_evaluated: google/gemma-2b-it
    score: 35.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_college_medicine#f7eb185a540b
  - benchmark_id: mmlu_college_physics
    model_id_as_evaluated: google/gemma-2b-it
    score: 18.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_college_physics#3336dc6d1c31
  - benchmark_id: mmlu_computer_security
    model_id_as_evaluated: google/gemma-2b-it
    score: 45.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_computer_security#57211866b657
  - benchmark_id: mmlu_conceptual_physics
    model_id_as_evaluated: google/gemma-2b-it
    score: 35.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_conceptual_physics#df2d1d5349b7
  - benchmark_id: mmlu_econometrics
    model_id_as_evaluated: google/gemma-2b-it
    score: 28.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_econometrics#23a684b74f10
  - benchmark_id: mmlu_electrical_engineering
    model_id_as_evaluated: google/gemma-2b-it
    score: 46.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_electrical_engineering#e2fff75e88f3
  - benchmark_id: mmlu_elementary_mathematics
    model_id_as_evaluated: google/gemma-2b-it
    score: 24.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_elementary_mathematics#e5135e2a466f
  - benchmark_id: mmlu_formal_logic
    model_id_as_evaluated: google/gemma-2b-it
    score: 25.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_formal_logic#f8fb247db7d5
  - benchmark_id: mmlu_global_facts
    model_id_as_evaluated: google/gemma-2b-it
    score: 30.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_global_facts#735d89d78339
  - benchmark_id: mmlu_high_school_biology
    model_id_as_evaluated: google/gemma-2b-it
    score: 31.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_high_school_biology#7806ab242168
  - benchmark_id: mmlu_high_school_chemistry
    model_id_as_evaluated: google/gemma-2b-it
    score: 29.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_high_school_chemistry#d24f39b8ac52
  - benchmark_id: mmlu_high_school_computer_science
    model_id_as_evaluated: google/gemma-2b-it
    score: 37.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_high_school_computer_science#faed3de6cf90
  - benchmark_id: mmlu_high_school_european_history
    model_id_as_evaluated: google/gemma-2b-it
    score: 46.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_high_school_european_history#3722eec9f110
  - benchmark_id: mmlu_high_school_geography
    model_id_as_evaluated: google/gemma-2b-it
    score: 46.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_high_school_geography#7ca97cbc7667
  - benchmark_id: mmlu_high_school_government_and_politics
    model_id_as_evaluated: google/gemma-2b-it
    score: 47.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_high_school_government_and_politics#1c830e154f23
  - benchmark_id: mmlu_high_school_macroeconomics
    model_id_as_evaluated: google/gemma-2b-it
    score: 32.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_high_school_macroeconomics#069dbf2c779c
  - benchmark_id: mmlu_high_school_mathematics
    model_id_as_evaluated: google/gemma-2b-it
    score: 20.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_high_school_mathematics#dcac81e55cf8
  - benchmark_id: mmlu_high_school_microeconomics
    model_id_as_evaluated: google/gemma-2b-it
    score: 34.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_high_school_microeconomics#9f0339781f57
  - benchmark_id: mmlu_high_school_physics
    model_id_as_evaluated: google/gemma-2b-it
    score: 25.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_high_school_physics#84b13835ac6a
  - benchmark_id: mmlu_high_school_psychology
    model_id_as_evaluated: google/gemma-2b-it
    score: 51.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_high_school_psychology#34c3de8e0341
  - benchmark_id: mmlu_high_school_statistics
    model_id_as_evaluated: google/gemma-2b-it
    score: 20.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_high_school_statistics#a751b9db8cdd
  - benchmark_id: mmlu_high_school_us_history
    model_id_as_evaluated: google/gemma-2b-it
    score: 42.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_high_school_us_history#ab47a415c8df
  - benchmark_id: mmlu_high_school_world_history
    model_id_as_evaluated: google/gemma-2b-it
    score: 51.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_high_school_world_history#a4a6320530ac
  - benchmark_id: mmlu_human_aging
    model_id_as_evaluated: google/gemma-2b-it
    score: 39.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_human_aging#8fd730f5867a
  - benchmark_id: mmlu_human_sexuality
    model_id_as_evaluated: google/gemma-2b-it
    score: 42.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_human_sexuality#9cc0c4d06119
  - benchmark_id: mmlu_international_law
    model_id_as_evaluated: google/gemma-2b-it
    score: 52.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_international_law#976994dc3877
  - benchmark_id: mmlu_jurisprudence
    model_id_as_evaluated: google/gemma-2b-it
    score: 46.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_jurisprudence#e40a83fc98b2
  - benchmark_id: mmlu_logical_fallacies
    model_id_as_evaluated: google/gemma-2b-it
    score: 36.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_logical_fallacies#f18b91bb3ce6
  - benchmark_id: mmlu_machine_learning
    model_id_as_evaluated: google/gemma-2b-it
    score: 33.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_machine_learning#32c5d306b93e
  - benchmark_id: mmlu_management
    model_id_as_evaluated: google/gemma-2b-it
    score: 44.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_management#289c720b4e87
  - benchmark_id: mmlu_marketing
    model_id_as_evaluated: google/gemma-2b-it
    score: 59.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_marketing#e3a5295d1314
  - benchmark_id: mmlu_medical_genetics
    model_id_as_evaluated: google/gemma-2b-it
    score: 39.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_medical_genetics#08704f2d02c6
  - benchmark_id: mmlu_miscellaneous
    model_id_as_evaluated: google/gemma-2b-it
    score: 46.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_miscellaneous#421feed32ef0
  - benchmark_id: mmlu_moral_disputes
    model_id_as_evaluated: google/gemma-2b-it
    score: 40.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_moral_disputes#fbf5f2c3abbe
  - benchmark_id: mmlu_moral_scenarios
    model_id_as_evaluated: google/gemma-2b-it
    score: 25.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_moral_scenarios#fa3f70de9797
  - benchmark_id: mmlu_nutrition
    model_id_as_evaluated: google/gemma-2b-it
    score: 45.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_nutrition#4ceb1960e602
  - benchmark_id: mmlu_philosophy
    model_id_as_evaluated: google/gemma-2b-it
    score: 40.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_philosophy#81cc39d2e74b
  - benchmark_id: mmlu_prehistory
    model_id_as_evaluated: google/gemma-2b-it
    score: 40.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_prehistory#c1d41e4d89e9
  - benchmark_id: mmlu_pro
    model_id_as_evaluated: google/gemma-2b-it
    score: 13.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/google/gemma-2b-it/results_2025-02-13T18-27-04.338360.json
    source_kind: benchmark_author
    evidence_date: '2024-06-17'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v2-10ac5516f60b
      snapshot_ref: sha256:0a51512e84e680e50294e8bc32f8a212f65e8db55f30583b25e8b572e29864f3
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_pro#146c332989c9
  - benchmark_id: mmlu_professional_accounting
    model_id_as_evaluated: google/gemma-2b-it
    score: 30.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_professional_accounting#3c0352484faa
  - benchmark_id: mmlu_professional_law
    model_id_as_evaluated: google/gemma-2b-it
    score: 31.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_professional_law#2175f8809e41
  - benchmark_id: mmlu_professional_medicine
    model_id_as_evaluated: google/gemma-2b-it
    score: 20.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_professional_medicine#daf1bec66822
  - benchmark_id: mmlu_professional_psychology
    model_id_as_evaluated: google/gemma-2b-it
    score: 38.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_professional_psychology#d7a0f3328fb8
  - benchmark_id: mmlu_public_relations
    model_id_as_evaluated: google/gemma-2b-it
    score: 41.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_public_relations#ef7a06bda256
  - benchmark_id: mmlu_security_studies
    model_id_as_evaluated: google/gemma-2b-it
    score: 47.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_security_studies#f3dd05cafc4c
  - benchmark_id: mmlu_sociology
    model_id_as_evaluated: google/gemma-2b-it
    score: 43.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_sociology#9b838f515959
  - benchmark_id: mmlu_us_foreign_policy
    model_id_as_evaluated: google/gemma-2b-it
    score: 64.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_us_foreign_policy#9b983c90a895
  - benchmark_id: mmlu_virology
    model_id_as_evaluated: google/gemma-2b-it
    score: 41.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_virology#a8601b8638df
  - benchmark_id: mmlu_world_religions
    model_id_as_evaluated: google/gemma-2b-it
    score: 43.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#mmlu_world_religions#60bf29368390
  - benchmark_id: musr
    model_id_as_evaluated: google/gemma-2b-it
    score: 33.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/google/gemma-2b-it/results_2025-02-13T18-27-04.338360.json
    source_kind: benchmark_author
    evidence_date: '2024-06-17'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v2-10ac5516f60b
      snapshot_ref: sha256:0a51512e84e680e50294e8bc32f8a212f65e8db55f30583b25e8b572e29864f3
      cited_regions:
      - rows
    id: google/gemma-2b-it#musr#54d5e4498730
  - benchmark_id: truthfulqa
    model_id_as_evaluated: google/gemma-2b-it
    score: 45.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#truthfulqa#62942de84bb9
  - benchmark_id: winogrande
    model_id_as_evaluated: google/gemma-2b-it
    score: 60.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-86126911893f
      snapshot_ref: sha256:110a5a03dfd99b5a9cda6688f45e5dc50f6e5d8b44024219a3dcb1cd8328289b
      cited_regions:
      - rows
    id: google/gemma-2b-it#winogrande#2ccef17fb42b
  benchmark_source: open-llm-leaderboard-v1, open-llm-leaderboard-v2
  benchmark_as_of: 2024-07
  benchmark_notes: ''
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
    gguf: true
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
  huggingface_downloads: 56607
  huggingface_likes: 863
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
  huggingface_url: https://huggingface.co/google/gemma-2b-it
  arxiv_url: ''
  paper_url: ''
  github_url: ''
  ollama_url: ''
  artificial_analysis_url: ''
  arena_url: ''
  last_scraped_models_dev: ''
  last_scraped_huggingface: '2026-04-05'
  last_scraped_benchmarks: ''
  last_scraped_pricing: ''
card_schema_version: '3.0'
card_author: huggingface-seeder
card_created: '2026-04-05'
card_updated: '2026-04-05'
---


# gemma 2B it

Auto-generated from HuggingFace Hub metadata for [google/gemma-2b-it](https://huggingface.co/google/gemma-2b-it).