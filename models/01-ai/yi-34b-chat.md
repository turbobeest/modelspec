---
model_id: 01-ai/yi-34b-chat
display_name: Yi 34B Chat
provider: 01-ai
provider_display: 01.AI
family: yi
version: ''
release_date: '2023-11-22'
last_updated: ''
status: active
model_type: llm-chat
model_subtypes: []
tags:
- text-generation
pipeline_tag: text-generation
architecture:
  type: null
  total_parameters: 34388917248
  active_parameters: null
  num_experts: null
  experts_per_token: null
  num_layers: 60
  hidden_size: 7168
  intermediate_size: 20480
  attention_type: null
  num_attention_heads: 56
  num_kv_heads: 8
  positional_encoding: null
  rope_theta: null
  vocab_size: 64000
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
  license_type: apache-2.0
  license_url: https://huggingface.co/01-ai/Yi-34B-Chat/raw/main/LICENSE
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
  origin_country: CN
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
    model_id: 01-ai/Yi-34B-Chat
    url: https://huggingface.co/01-ai/Yi-34B-Chat
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
    model_id_as_evaluated: yi-34b-chat
    score: 1183.47
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / overall, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category overall,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1183.47 [1176.65, 1190.29], 15483
      votes, rank 341.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_coding
    model_id_as_evaluated: yi-34b-chat
    score: 1205.67
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / coding, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category coding,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1205.67 [1192.68, 1218.66], 2345
      votes, rank 348.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_hard_prompts
    model_id_as_evaluated: yi-34b-chat
    score: 1183.74
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / hard_prompts, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category hard_prompts,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1183.74 [1173.18, 1194.31], 3838
      votes, rank 347.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_math
    model_id_as_evaluated: yi-34b-chat
    score: 1150.47
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / math, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category math, leaderboard_publish_date
      2026-09-13; style control. Highest-effort row for the product (effort: default; MODEL-123
      max-effort rule). Rating 1150.47 [1137.21, 1163.74], 2043 votes, rank 339.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_creative_writing
    model_id_as_evaluated: yi-34b-chat
    score: 1153.61
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / creative_writing, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category creative_writing,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1153.61 [1139.85, 1167.37], 2379
      votes, rank 338.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_instruction_following
    model_id_as_evaluated: yi-34b-chat
    score: 1152.05
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / instruction_following, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category instruction_following,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1152.05 [1142.30, 1161.80], 5099
      votes, rank 350.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_multi_turn
    model_id_as_evaluated: yi-34b-chat
    score: 1161.45
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / multi_turn, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category multi_turn,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1161.45 [1146.68, 1176.21], 1947
      votes, rank 336.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_expert
    model_id_as_evaluated: yi-34b-chat
    score: 1155.66
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / expert, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category expert,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1155.66 [1130.61, 1180.71], 559 votes,
      rank 334.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_longer_query
    model_id_as_evaluated: yi-34b-chat
    score: 1172.05
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / longer_query, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category longer_query,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1172.05 [1154.08, 1190.01], 1106
      votes, rank 344.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_non_english
    model_id_as_evaluated: yi-34b-chat
    score: 1139.84
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / non_english, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category non_english,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1139.84 [1129.78, 1149.90], 4911
      votes, rank 344.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_medicine
    model_id_as_evaluated: yi-34b-chat
    score: 1198.64
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
      (effort: default; MODEL-123 max-effort rule). Rating 1198.64 [1176.75, 1220.54], 824 votes,
      rank 331.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_legal
    model_id_as_evaluated: yi-34b-chat
    score: 1220.08
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
      (effort: default; MODEL-123 max-effort rule). Rating 1220.08 [1198.31, 1241.86], 857 votes,
      rank 324.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_business
    model_id_as_evaluated: yi-34b-chat
    score: 1169.1
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
      (effort: default; MODEL-123 max-effort rule). Rating 1169.10 [1152.51, 1185.68], 1433
      votes, rank 341.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_science
    model_id_as_evaluated: yi-34b-chat
    score: 1212.43
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
      (effort: default; MODEL-123 max-effort rule). Rating 1212.43 [1199.22, 1225.63], 2658
      votes, rank 335.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_writing
    model_id_as_evaluated: yi-34b-chat
    score: 1163.73
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
      (effort: default; MODEL-123 max-effort rule). Rating 1163.73 [1152.32, 1175.14], 3702
      votes, rank 343.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: gpqa_diamond
    model_id_as_evaluated: Yi-34B-Chat
    score: 14.74
    unit: percent
    source_url: https://epoch.ai/benchmarks/gpqa-diamond
    source_kind: independent_evaluator
    evidence_date: '2025-01-27'
    date_type: evaluated
    verified_at: '2026-09-24'
    benchmark_version: GPQA Diamond (Epoch AI run)
    configuration: Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (gpqa_diamond.csv),
      read 2026-09-24. Run started 2025-01-27T00:00:00.000Z; effort default; highest-effort
      run for the model (MODEL-123 max-effort rule), newest on a tie. Standard error 1.14 points.
    limitations: Epoch AI data, CC BY 4.0.
  - benchmark_id: arc_challenge
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 65.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#arc_challenge#c2dd483b1de1
  - benchmark_id: bbh
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 55.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/01-ai/Yi-34B-Chat/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-631c76e81143
      snapshot_ref: sha256:671d945e112f7c1f8321215f7011a6df4c365ce008c0c29e7ad4010ea4b1b4a2
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#bbh#3a95240dbe66
  - benchmark_id: gpqa_pooled
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 33.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/01-ai/Yi-34B-Chat/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-631c76e81143
      snapshot_ref: sha256:671d945e112f7c1f8321215f7011a6df4c365ce008c0c29e7ad4010ea4b1b4a2
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#gpqa_pooled#aeb5eacfc4a7
  - benchmark_id: gsm8k
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 31.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#gsm8k#dc9904d284b5
  - benchmark_id: hellaswag
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 84.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#hellaswag#43e8ec6021b0
  - benchmark_id: ifeval
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 47.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/01-ai/Yi-34B-Chat/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-631c76e81143
      snapshot_ref: sha256:671d945e112f7c1f8321215f7011a6df4c365ce008c0c29e7ad4010ea4b1b4a2
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#ifeval#a53d94fe3211
  - benchmark_id: math_lvl5
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 6.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/01-ai/Yi-34B-Chat/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-631c76e81143
      snapshot_ref: sha256:671d945e112f7c1f8321215f7011a6df4c365ce008c0c29e7ad4010ea4b1b4a2
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#math_lvl5#6660374010ce
  - benchmark_id: mmlu_abstract_algebra
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 45.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_abstract_algebra#35f194eac0bb
  - benchmark_id: mmlu_anatomy
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 71.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_anatomy#37f8b627b3c0
  - benchmark_id: mmlu_astronomy
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 85.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_astronomy#866b48bc9829
  - benchmark_id: mmlu_business_ethics
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 79.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_business_ethics#019fb4b477e5
  - benchmark_id: mmlu_clinical_knowledge
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 79.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_clinical_knowledge#64c6dc02b51c
  - benchmark_id: mmlu_college_biology
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 84.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_college_biology#beb67e537788
  - benchmark_id: mmlu_college_chemistry
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 53.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_college_chemistry#2a2e861fed30
  - benchmark_id: mmlu_college_computer_science
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 59.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_college_computer_science#1996e2bd2f8d
  - benchmark_id: mmlu_college_mathematics
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 34.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_college_mathematics#c1eb5d96cd2e
  - benchmark_id: mmlu_college_medicine
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 69.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_college_medicine#8a49d3e6e17c
  - benchmark_id: mmlu_college_physics
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 46.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_college_physics#94a94b81e824
  - benchmark_id: mmlu_computer_security
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 82.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_computer_security#8356811bebb7
  - benchmark_id: mmlu_conceptual_physics
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 76.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_conceptual_physics#d98397d76648
  - benchmark_id: mmlu_econometrics
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 55.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_econometrics#a34d3c37ce9a
  - benchmark_id: mmlu_electrical_engineering
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 80.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_electrical_engineering#de8a2e73dbbc
  - benchmark_id: mmlu_elementary_mathematics
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 63.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_elementary_mathematics#af6c0cd47470
  - benchmark_id: mmlu_formal_logic
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 54.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_formal_logic#77a9fefc9170
  - benchmark_id: mmlu_global_facts
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 56.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_global_facts#a213e67571c2
  - benchmark_id: mmlu_high_school_biology
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 87.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_high_school_biology#80579b909c9f
  - benchmark_id: mmlu_high_school_chemistry
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 62.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_high_school_chemistry#23926996e8f7
  - benchmark_id: mmlu_high_school_computer_science
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 81.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_high_school_computer_science#c3abf14caa1b
  - benchmark_id: mmlu_high_school_european_history
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 85.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_high_school_european_history#d81936123798
  - benchmark_id: mmlu_high_school_geography
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 89.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_high_school_geography#9425ff53e50c
  - benchmark_id: mmlu_high_school_government_and_politics
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 95.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_high_school_government_and_politics#4c8a4ace19e5
  - benchmark_id: mmlu_high_school_macroeconomics
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 78.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_high_school_macroeconomics#52e2695cb080
  - benchmark_id: mmlu_high_school_mathematics
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 35.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_high_school_mathematics#49625253a806
  - benchmark_id: mmlu_high_school_microeconomics
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 83.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_high_school_microeconomics#69391f528524
  - benchmark_id: mmlu_high_school_physics
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 50.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_high_school_physics#1314b94dde93
  - benchmark_id: mmlu_high_school_psychology
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 90.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_high_school_psychology#8c4ccac89d80
  - benchmark_id: mmlu_high_school_statistics
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 63.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_high_school_statistics#46ec49e626e6
  - benchmark_id: mmlu_high_school_us_history
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 90.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_high_school_us_history#56981ca4a536
  - benchmark_id: mmlu_high_school_world_history
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 90.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_high_school_world_history#8dd6f827e45b
  - benchmark_id: mmlu_human_aging
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 81.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_human_aging#1dc1bb4e3f25
  - benchmark_id: mmlu_human_sexuality
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 89.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_human_sexuality#e24d5fbfe1a7
  - benchmark_id: mmlu_international_law
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 89.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_international_law#fd88692a109d
  - benchmark_id: mmlu_jurisprudence
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 88.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_jurisprudence#993b00c3b008
  - benchmark_id: mmlu_logical_fallacies
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 85.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_logical_fallacies#68ca6190eea5
  - benchmark_id: mmlu_machine_learning
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 61.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_machine_learning#4cdcdf7f8969
  - benchmark_id: mmlu_management
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 87.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_management#ef2918699ab1
  - benchmark_id: mmlu_marketing
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 91.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_marketing#67661ce651d3
  - benchmark_id: mmlu_medical_genetics
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 87.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_medical_genetics#4562617cc034
  - benchmark_id: mmlu_miscellaneous
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 89.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_miscellaneous#64a44a1c95bd
  - benchmark_id: mmlu_moral_disputes
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 80.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_moral_disputes#d268ce8c58f2
  - benchmark_id: mmlu_moral_scenarios
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 70.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_moral_scenarios#31ae9eecb720
  - benchmark_id: mmlu_nutrition
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 83.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_nutrition#a0d2a3a0dc00
  - benchmark_id: mmlu_philosophy
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 81.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_philosophy#6ec91da091b6
  - benchmark_id: mmlu_prehistory
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 87.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_prehistory#edb645c07dd7
  - benchmark_id: mmlu_pro
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 40.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/01-ai/Yi-34B-Chat/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-631c76e81143
      snapshot_ref: sha256:671d945e112f7c1f8321215f7011a6df4c365ce008c0c29e7ad4010ea4b1b4a2
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_pro#4e1608381675
  - benchmark_id: mmlu_professional_accounting
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 61.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_professional_accounting#3ac146dcce62
  - benchmark_id: mmlu_professional_law
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 55.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_professional_law#a93653d37a21
  - benchmark_id: mmlu_professional_medicine
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 78.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_professional_medicine#172a2039d30f
  - benchmark_id: mmlu_professional_psychology
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 82.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_professional_psychology#6f636517b4a0
  - benchmark_id: mmlu_public_relations
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 72.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_public_relations#24c57496accd
  - benchmark_id: mmlu_security_studies
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 83.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_security_studies#85bc751d21df
  - benchmark_id: mmlu_sociology
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 88.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_sociology#208df7bc3994
  - benchmark_id: mmlu_us_foreign_policy
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 89.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_us_foreign_policy#dafaaceef047
  - benchmark_id: mmlu_virology
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 58.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_virology#c37b43c09717
  - benchmark_id: mmlu_world_religions
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 87.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#mmlu_world_religions#d4b513ed83c5
  - benchmark_id: musr
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 39.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/01-ai/Yi-34B-Chat/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-631c76e81143
      snapshot_ref: sha256:671d945e112f7c1f8321215f7011a6df4c365ce008c0c29e7ad4010ea4b1b4a2
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#musr#43481b0adc45
  - benchmark_id: truthfulqa
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 55.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#truthfulqa#34734e27d1a1
  - benchmark_id: winogrande
    model_id_as_evaluated: 01-ai/Yi-34B-Chat
    score: 80.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-Chat/results_2023-12-05T03-47-25.491369.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-c788c8cc0fc3
      snapshot_ref: sha256:c88782ce04fecec6dde83cd9ec2aa1123273e48ee0f5bb22a90f9e0346198acb
      cited_regions:
      - rows
    id: 01-ai/yi-34b-chat#winogrande#67be7ffa89d1
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
  huggingface_downloads: 28314
  huggingface_likes: 357
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
  huggingface_url: https://huggingface.co/01-ai/Yi-34B-Chat
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


# Yi 34B Chat

Auto-generated from HuggingFace Hub metadata for [01-ai/Yi-34B-Chat](https://huggingface.co/01-ai/Yi-34B-Chat).

Licence: apache-2.0. Creator LICENSE file https://huggingface.co/01-ai/Yi-34B-Chat/raw/main/LICENSE (Apache License Version 2.0, January 2004) and Hub cardData.license apache-2.0, read 2026-09-18.
