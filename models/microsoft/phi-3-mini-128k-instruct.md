---
model_id: microsoft/phi-3-mini-128k-instruct
display_name: Phi 3 mini 128K instruct
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
  license_url: https://huggingface.co/microsoft/Phi-3-mini-128k-instruct/raw/main/LICENSE
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
    context_window: 131072
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
    model_id: microsoft/Phi-3-mini-128k-instruct
    url: https://huggingface.co/microsoft/Phi-3-mini-128k-instruct
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
    model_id_as_evaluated: phi-3-mini-128k-instruct
    score: 1129.5
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / overall, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category overall,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1129.50 [1122.08, 1136.92], 20685
      votes, rank 375.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_coding
    model_id_as_evaluated: phi-3-mini-128k-instruct
    score: 1154.71
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / coding, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category coding,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1154.71 [1141.71, 1167.71], 3886
      votes, rank 372.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_hard_prompts
    model_id_as_evaluated: phi-3-mini-128k-instruct
    score: 1130.14
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / hard_prompts, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category hard_prompts,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1130.14 [1119.25, 1141.03], 6167
      votes, rank 375.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_math
    model_id_as_evaluated: phi-3-mini-128k-instruct
    score: 1139.58
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / math, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category math, leaderboard_publish_date
      2026-09-13; style control. Highest-effort row for the product (effort: default; MODEL-123
      max-effort rule). Rating 1139.58 [1126.35, 1152.82], 2813 votes, rank 342.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_creative_writing
    model_id_as_evaluated: phi-3-mini-128k-instruct
    score: 1085.36
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / creative_writing, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category creative_writing,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1085.36 [1070.84, 1099.88], 2949
      votes, rank 380.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_instruction_following
    model_id_as_evaluated: phi-3-mini-128k-instruct
    score: 1099.96
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / instruction_following, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category instruction_following,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1099.96 [1089.63, 1110.29], 7368
      votes, rank 377.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_multi_turn
    model_id_as_evaluated: phi-3-mini-128k-instruct
    score: 1058.47
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / multi_turn, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category multi_turn,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1058.47 [1042.75, 1074.18], 2507
      votes, rank 381.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_expert
    model_id_as_evaluated: phi-3-mini-128k-instruct
    score: 1098.05
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / expert, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category expert,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1098.05 [1077.65, 1118.44], 1095
      votes, rank 350.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_longer_query
    model_id_as_evaluated: phi-3-mini-128k-instruct
    score: 1073.13
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / longer_query, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category longer_query,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1073.13 [1056.97, 1089.28], 2074
      votes, rank 378.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_non_english
    model_id_as_evaluated: phi-3-mini-128k-instruct
    score: 1075.58
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / non_english, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category non_english,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1075.58 [1065.51, 1085.64], 8089
      votes, rank 373.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_medicine
    model_id_as_evaluated: phi-3-mini-128k-instruct
    score: 1127.52
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
      (effort: default; MODEL-123 max-effort rule). Rating 1127.52 [1105.48, 1149.56], 1114
      votes, rank 359.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_legal
    model_id_as_evaluated: phi-3-mini-128k-instruct
    score: 1116.21
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
      (effort: default; MODEL-123 max-effort rule). Rating 1116.21 [1093.66, 1138.77], 1033
      votes, rank 366.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_business
    model_id_as_evaluated: phi-3-mini-128k-instruct
    score: 1097.36
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
      (effort: default; MODEL-123 max-effort rule). Rating 1097.36 [1081.24, 1113.49], 2085
      votes, rank 374.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_science
    model_id_as_evaluated: phi-3-mini-128k-instruct
    score: 1137.24
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
      (effort: default; MODEL-123 max-effort rule). Rating 1137.24 [1123.39, 1151.08], 3426
      votes, rank 377.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_writing
    model_id_as_evaluated: phi-3-mini-128k-instruct
    score: 1098.46
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
      (effort: default; MODEL-123 max-effort rule). Rating 1098.46 [1086.42, 1110.49], 4627
      votes, rank 376.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arc_challenge
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 63.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#arc_challenge#3b93332627ab
  - benchmark_id: bbh
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 55.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/microsoft/Phi-3-mini-128k-instruct/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-24'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-ef5fe1b9dd7f
      snapshot_ref: sha256:e7a9aca8fd49dd97b48e9e450e05d5c7190894c1e8ef8c2fe8bb25aa96d294b5
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#bbh#56b8f9014baa
  - benchmark_id: gpqa_pooled
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 31.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/microsoft/Phi-3-mini-128k-instruct/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-24'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-ef5fe1b9dd7f
      snapshot_ref: sha256:e7a9aca8fd49dd97b48e9e450e05d5c7190894c1e8ef8c2fe8bb25aa96d294b5
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#gpqa_pooled#4ab4a6589b79
  - benchmark_id: gsm8k
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 69.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#gsm8k#d63afca20798
  - benchmark_id: hellaswag
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 80.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#hellaswag#9ec35e28bd4f
  - benchmark_id: ifeval
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 59.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/microsoft/Phi-3-mini-128k-instruct/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-24'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-ef5fe1b9dd7f
      snapshot_ref: sha256:e7a9aca8fd49dd97b48e9e450e05d5c7190894c1e8ef8c2fe8bb25aa96d294b5
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#ifeval#0745c794c398
  - benchmark_id: math_lvl5
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 14.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/microsoft/Phi-3-mini-128k-instruct/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-24'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-ef5fe1b9dd7f
      snapshot_ref: sha256:e7a9aca8fd49dd97b48e9e450e05d5c7190894c1e8ef8c2fe8bb25aa96d294b5
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#math_lvl5#3ddaaae379b3
  - benchmark_id: mmlu_abstract_algebra
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 38.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_abstract_algebra#949e1231f1f6
  - benchmark_id: mmlu_anatomy
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 65.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_anatomy#cc50f93e5d19
  - benchmark_id: mmlu_astronomy
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 78.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_astronomy#e08d3ef88cf5
  - benchmark_id: mmlu_business_ethics
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 68.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_business_ethics#fd90dd5ad3dc
  - benchmark_id: mmlu_clinical_knowledge
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 74.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_clinical_knowledge#aa00da455279
  - benchmark_id: mmlu_college_biology
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 79.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_college_biology#a45f8f53d3ac
  - benchmark_id: mmlu_college_chemistry
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 44.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_college_chemistry#da36f0f2ce0c
  - benchmark_id: mmlu_college_computer_science
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 56.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_college_computer_science#c2fdcc31e057
  - benchmark_id: mmlu_college_mathematics
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 40.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_college_mathematics#63e98c257b53
  - benchmark_id: mmlu_college_medicine
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 68.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_college_medicine#7904c5042235
  - benchmark_id: mmlu_college_physics
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 43.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_college_physics#1517ffceed3c
  - benchmark_id: mmlu_computer_security
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 76.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_computer_security#0ff7c6161e5e
  - benchmark_id: mmlu_conceptual_physics
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 69.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_conceptual_physics#56d32cf0a762
  - benchmark_id: mmlu_econometrics
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 49.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_econometrics#60e16ee4e2ba
  - benchmark_id: mmlu_electrical_engineering
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 62.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_electrical_engineering#8c79ccf6a779
  - benchmark_id: mmlu_elementary_mathematics
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 48.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_elementary_mathematics#7bee7d47a0f5
  - benchmark_id: mmlu_formal_logic
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 57.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_formal_logic#204771cb7d0b
  - benchmark_id: mmlu_global_facts
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 37.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_global_facts#c93c2ece67c8
  - benchmark_id: mmlu_high_school_biology
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 83.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_high_school_biology#468830dd7ad0
  - benchmark_id: mmlu_high_school_chemistry
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 60.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_high_school_chemistry#42ddf88b6b93
  - benchmark_id: mmlu_high_school_computer_science
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 67.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_high_school_computer_science#90f9bb273cb4
  - benchmark_id: mmlu_high_school_european_history
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 81.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_high_school_european_history#bb879f6cf55a
  - benchmark_id: mmlu_high_school_geography
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 84.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_high_school_geography#b39c01d625d3
  - benchmark_id: mmlu_high_school_government_and_politics
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 88.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_high_school_government_and_politics#efedc687a9a4
  - benchmark_id: mmlu_high_school_macroeconomics
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 73.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_high_school_macroeconomics#1026c9648ed3
  - benchmark_id: mmlu_high_school_mathematics
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 40.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_high_school_mathematics#e4377660044f
  - benchmark_id: mmlu_high_school_microeconomics
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 82.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_high_school_microeconomics#6161ad7f9899
  - benchmark_id: mmlu_high_school_physics
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 44.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_high_school_physics#a8758f6d5e30
  - benchmark_id: mmlu_high_school_psychology
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 89.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_high_school_psychology#771be44590db
  - benchmark_id: mmlu_high_school_statistics
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 64.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_high_school_statistics#b9809bb9cbdb
  - benchmark_id: mmlu_high_school_us_history
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 83.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_high_school_us_history#2f9267e5afd7
  - benchmark_id: mmlu_high_school_world_history
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 79.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_high_school_world_history#fc1898cddfb5
  - benchmark_id: mmlu_human_aging
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 70.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_human_aging#93aff51067d2
  - benchmark_id: mmlu_human_sexuality
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 75.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_human_sexuality#d7aee4c6eae0
  - benchmark_id: mmlu_international_law
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 82.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_international_law#071d24251cd4
  - benchmark_id: mmlu_jurisprudence
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 77.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_jurisprudence#f154ab8bf97c
  - benchmark_id: mmlu_logical_fallacies
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 81.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_logical_fallacies#08efcdbf9901
  - benchmark_id: mmlu_machine_learning
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 54.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_machine_learning#8871e2bdebcf
  - benchmark_id: mmlu_management
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 82.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_management#b317849b7b5d
  - benchmark_id: mmlu_marketing
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 88.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_marketing#739ecad65092
  - benchmark_id: mmlu_medical_genetics
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 83.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_medical_genetics#0b65b8063e09
  - benchmark_id: mmlu_miscellaneous
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 81.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_miscellaneous#394a5a715fef
  - benchmark_id: mmlu_moral_disputes
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 74.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_moral_disputes#c06077244a15
  - benchmark_id: mmlu_moral_scenarios
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 58.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_moral_scenarios#e6bb6ad3e8a0
  - benchmark_id: mmlu_nutrition
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 77.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_nutrition#096758f45b7b
  - benchmark_id: mmlu_philosophy
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 73.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_philosophy#4c1311f33fd1
  - benchmark_id: mmlu_prehistory
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 77.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_prehistory#35f030ede535
  - benchmark_id: mmlu_pro
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 37.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/microsoft/Phi-3-mini-128k-instruct/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-24'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-ef5fe1b9dd7f
      snapshot_ref: sha256:e7a9aca8fd49dd97b48e9e450e05d5c7190894c1e8ef8c2fe8bb25aa96d294b5
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_pro#47e27ceafa9d
  - benchmark_id: mmlu_professional_accounting
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 58.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_professional_accounting#2d15c73e4e45
  - benchmark_id: mmlu_professional_law
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 49.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_professional_law#c012230b12f0
  - benchmark_id: mmlu_professional_medicine
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 72.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_professional_medicine#8ab93a565f59
  - benchmark_id: mmlu_professional_psychology
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 75.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_professional_psychology#cdff99067970
  - benchmark_id: mmlu_public_relations
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 67.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_public_relations#48286c019520
  - benchmark_id: mmlu_security_studies
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 74.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_security_studies#d65bbbafa6c5
  - benchmark_id: mmlu_sociology
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 85.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_sociology#1be8ffa9f665
  - benchmark_id: mmlu_us_foreign_policy
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 87.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_us_foreign_policy#603e13d3d776
  - benchmark_id: mmlu_virology
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 47.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_virology#dbd2792d7280
  - benchmark_id: mmlu_world_religions
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 80.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#mmlu_world_religions#01c44334ba81
  - benchmark_id: musr
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 39.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/microsoft/Phi-3-mini-128k-instruct/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-24'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-ef5fe1b9dd7f
      snapshot_ref: sha256:e7a9aca8fd49dd97b48e9e450e05d5c7190894c1e8ef8c2fe8bb25aa96d294b5
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#musr#e5c313a7585a
  - benchmark_id: truthfulqa
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 54.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#truthfulqa#7d8d4d3567d5
  - benchmark_id: winogrande
    model_id_as_evaluated: microsoft/Phi-3-mini-128k-instruct
    score: 72.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json
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
    - source_id: oll-v1-2e0af8c86c8b
      snapshot_ref: sha256:6dce532064a7fa93bdb924f6e118f5588f3307fa1b6fcfdb008b6fa208ddffc7
      cited_regions:
      - rows
    id: microsoft/phi-3-mini-128k-instruct#winogrande#5ae66c70ad1a
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
  huggingface_downloads: 247474
  huggingface_likes: 1696
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
  huggingface_url: https://huggingface.co/microsoft/Phi-3-mini-128k-instruct
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

# Phi 3 mini 128K instruct

Auto-generated from HuggingFace Hub metadata for [microsoft/Phi-3-mini-128k-instruct](https://huggingface.co/microsoft/Phi-3-mini-128k-instruct).

Licence: mit. Creator LICENSE file https://huggingface.co/microsoft/Phi-3-mini-128k-instruct/raw/main/LICENSE (MIT License) and Hub cardData.license mit, read 2026-09-18.
