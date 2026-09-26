---
model_id: 01-ai/yi-1-5-34b-chat
display_name: Yi 1.5 34B Chat
provider: 01-ai
provider_display: 01.AI
family: yi
version: ''
release_date: '2024-05-10'
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
  license_url: https://huggingface.co/01-ai/Yi-1.5-34B-Chat/raw/main/README.md
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
  input: 0.6
  output: 0.6
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
    model_id: 01-ai/Yi-1.5-34B-Chat
    url: https://huggingface.co/01-ai/Yi-1.5-34B-Chat
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
    model_id_as_evaluated: yi-1.5-34b-chat
    score: 1212.65
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / overall, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category overall,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1212.65 [1207.61, 1217.69], 24146
      votes, rank 328.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_coding
    model_id_as_evaluated: yi-1.5-34b-chat
    score: 1248.51
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / coding, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category coding,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1248.51 [1238.03, 1258.98], 3841
      votes, rank 331.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_hard_prompts
    model_id_as_evaluated: yi-1.5-34b-chat
    score: 1225.32
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / hard_prompts, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category hard_prompts,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1225.32 [1216.99, 1233.66], 6679
      votes, rank 327.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_math
    model_id_as_evaluated: yi-1.5-34b-chat
    score: 1212.5
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / math, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category math, leaderboard_publish_date
      2026-09-13; style control. Highest-effort row for the product (effort: default; MODEL-123
      max-effort rule). Rating 1212.50 [1201.41, 1223.60], 2985 votes, rank 300.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_creative_writing
    model_id_as_evaluated: yi-1.5-34b-chat
    score: 1158.64
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / creative_writing, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category creative_writing,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1158.64 [1147.44, 1169.84], 3602
      votes, rank 335.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_instruction_following
    model_id_as_evaluated: yi-1.5-34b-chat
    score: 1187.84
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / instruction_following, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category instruction_following,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1187.84 [1180.12, 1195.56], 8996
      votes, rank 331.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_multi_turn
    model_id_as_evaluated: yi-1.5-34b-chat
    score: 1189.65
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / multi_turn, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category multi_turn,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1189.65 [1178.36, 1200.94], 3391
      votes, rank 325.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_expert
    model_id_as_evaluated: yi-1.5-34b-chat
    score: 1220.39
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / expert, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category expert,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1220.39 [1201.81, 1238.98], 1049
      votes, rank 307.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_longer_query
    model_id_as_evaluated: yi-1.5-34b-chat
    score: 1204.66
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / longer_query, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category longer_query,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1204.66 [1191.29, 1218.04], 2098
      votes, rank 329.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_non_english
    model_id_as_evaluated: yi-1.5-34b-chat
    score: 1166.01
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / non_english, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category non_english,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1166.01 [1158.87, 1173.15], 11643
      votes, rank 331.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_medicine
    model_id_as_evaluated: yi-1.5-34b-chat
    score: 1225.18
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
      (effort: default; MODEL-123 max-effort rule). Rating 1225.18 [1207.58, 1242.78], 1330
      votes, rank 316.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_legal
    model_id_as_evaluated: yi-1.5-34b-chat
    score: 1251.16
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
      (effort: default; MODEL-123 max-effort rule). Rating 1251.16 [1234.62, 1267.71], 1510
      votes, rank 313.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_business
    model_id_as_evaluated: yi-1.5-34b-chat
    score: 1195.11
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
      (effort: default; MODEL-123 max-effort rule). Rating 1195.11 [1182.85, 1207.37], 2763
      votes, rank 328.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_science
    model_id_as_evaluated: yi-1.5-34b-chat
    score: 1229.47
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
      (effort: default; MODEL-123 max-effort rule). Rating 1229.47 [1218.68, 1240.26], 4292
      votes, rank 326.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_writing
    model_id_as_evaluated: yi-1.5-34b-chat
    score: 1174.63
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
      (effort: default; MODEL-123 max-effort rule). Rating 1174.63 [1165.71, 1183.56], 6540
      votes, rank 334.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: gpqa_diamond
    model_id_as_evaluated: Yi-1.5-34B-Chat
    score: 31.98
    unit: percent
    source_url: https://epoch.ai/benchmarks/gpqa-diamond
    source_kind: independent_evaluator
    evidence_date: '2025-01-27'
    date_type: evaluated
    verified_at: '2026-09-24'
    benchmark_version: GPQA Diamond (Epoch AI run)
    configuration: Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (gpqa_diamond.csv),
      read 2026-09-24. Run started 2025-01-27T00:00:00.000Z; effort default; highest-effort
      run for the model (MODEL-123 max-effort rule), newest on a tie. Standard error 2.00 points.
    limitations: Epoch AI data, CC BY 4.0.
  - benchmark_id: arc_challenge
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 70.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#arc_challenge#c95d9027e8d6
  - benchmark_id: bbh
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 60.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/01-ai/Yi-1.5-34B-Chat/results_2025-02-13T18-27-04.338360.json
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
    - source_id: oll-v2-9c7075604dc5
      snapshot_ref: sha256:c5fd4a01fb21360b0f462d210c2d4bb941f8435063f6ba22b5b767fda9b01dfd
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#bbh#c70aba9e07bb
  - benchmark_id: gsm8k
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 71.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#gsm8k#f361260dd792
  - benchmark_id: hellaswag
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 86.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#hellaswag#f8e514fdb607
  - benchmark_id: ifeval
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 60.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/01-ai/Yi-1.5-34B-Chat/results_2025-02-13T18-27-04.338360.json
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
    - source_id: oll-v2-9c7075604dc5
      snapshot_ref: sha256:c5fd4a01fb21360b0f462d210c2d4bb941f8435063f6ba22b5b767fda9b01dfd
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#ifeval#9aa8e7f07e19
  - benchmark_id: mmlu_abstract_algebra
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 58.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_abstract_algebra#3f40bebaf4a3
  - benchmark_id: mmlu_anatomy
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 80.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_anatomy#694a047b42ff
  - benchmark_id: mmlu_astronomy
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 87.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_astronomy#c751d1a54545
  - benchmark_id: mmlu_business_ethics
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 81.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_business_ethics#1b70350b34f5
  - benchmark_id: mmlu_clinical_knowledge
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 77.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_clinical_knowledge#612b1c9ac9fc
  - benchmark_id: mmlu_college_biology
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 82.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_college_biology#22f753ee4683
  - benchmark_id: mmlu_college_chemistry
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 56.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_college_chemistry#cbb9739b4d46
  - benchmark_id: mmlu_college_computer_science
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 69.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_college_computer_science#c7ac12ab6019
  - benchmark_id: mmlu_college_mathematics
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 51.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_college_mathematics#bc8048aeeb86
  - benchmark_id: mmlu_college_medicine
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 75.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_college_medicine#a6b307bf95df
  - benchmark_id: mmlu_college_physics
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 52.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_college_physics#b16775b17487
  - benchmark_id: mmlu_computer_security
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 82.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_computer_security#7a6dc7bd14ea
  - benchmark_id: mmlu_conceptual_physics
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 81.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_conceptual_physics#33e048eaddad
  - benchmark_id: mmlu_econometrics
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 57.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_econometrics#f854779c75aa
  - benchmark_id: mmlu_electrical_engineering
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 74.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_electrical_engineering#6735f9102fe7
  - benchmark_id: mmlu_elementary_mathematics
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 75.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_elementary_mathematics#0feba18fc482
  - benchmark_id: mmlu_formal_logic
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 66.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_formal_logic#f07bc1702d7d
  - benchmark_id: mmlu_global_facts
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 51.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_global_facts#d2151f2ccc08
  - benchmark_id: mmlu_high_school_biology
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 88.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_high_school_biology#9642b03d718a
  - benchmark_id: mmlu_high_school_chemistry
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 66.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_high_school_chemistry#0c1d8ee9212f
  - benchmark_id: mmlu_high_school_computer_science
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 90.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_high_school_computer_science#6235227f33e9
  - benchmark_id: mmlu_high_school_european_history
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 86.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_high_school_european_history#29ba21dfbf9c
  - benchmark_id: mmlu_high_school_geography
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 88.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_high_school_geography#3f5c0c0c0034
  - benchmark_id: mmlu_high_school_government_and_politics
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 95.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_high_school_government_and_politics#775190e49d30
  - benchmark_id: mmlu_high_school_macroeconomics
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 83.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_high_school_macroeconomics#7c384c3de493
  - benchmark_id: mmlu_high_school_mathematics
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 55.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_high_school_mathematics#e9bcd384a62a
  - benchmark_id: mmlu_high_school_microeconomics
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 87.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_high_school_microeconomics#1ae39eb74a4f
  - benchmark_id: mmlu_high_school_physics
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 60.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_high_school_physics#0fe37513d29b
  - benchmark_id: mmlu_high_school_psychology
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 89.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_high_school_psychology#4825bede2ca5
  - benchmark_id: mmlu_high_school_statistics
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 68.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_high_school_statistics#a1f28ca42bc9
  - benchmark_id: mmlu_high_school_us_history
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 90.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_high_school_us_history#2ebd0ffd4e04
  - benchmark_id: mmlu_high_school_world_history
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 88.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_high_school_world_history#ae2ca1cb4e1b
  - benchmark_id: mmlu_human_aging
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 80.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_human_aging#6d0483cebeff
  - benchmark_id: mmlu_human_sexuality
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 87.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_human_sexuality#160d54697bd7
  - benchmark_id: mmlu_international_law
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 87.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_international_law#89586071ea51
  - benchmark_id: mmlu_jurisprudence
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 83.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_jurisprudence#ac84dee10d00
  - benchmark_id: mmlu_logical_fallacies
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 85.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_logical_fallacies#c352d0de77a4
  - benchmark_id: mmlu_machine_learning
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 63.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_machine_learning#93ffae8c49dc
  - benchmark_id: mmlu_management
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 88.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_management#2c9ff8951ec2
  - benchmark_id: mmlu_marketing
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 92.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_marketing#ac6c3a2d5ea3
  - benchmark_id: mmlu_medical_genetics
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 84.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_medical_genetics#fc1dbfc005aa
  - benchmark_id: mmlu_miscellaneous
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 89.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_miscellaneous#a66f34f2a04b
  - benchmark_id: mmlu_moral_disputes
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 81.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_moral_disputes#ced126517d56
  - benchmark_id: mmlu_moral_scenarios
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 68.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_moral_scenarios#a48f9a63edf5
  - benchmark_id: mmlu_nutrition
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 82.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_nutrition#f2937e864512
  - benchmark_id: mmlu_philosophy
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 77.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_philosophy#116582d8ad57
  - benchmark_id: mmlu_prehistory
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 85.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_prehistory#4fdbd6fb4d34
  - benchmark_id: mmlu_pro
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 45.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/01-ai/Yi-1.5-34B-Chat/results_2025-02-13T18-27-04.338360.json
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
    - source_id: oll-v2-9c7075604dc5
      snapshot_ref: sha256:c5fd4a01fb21360b0f462d210c2d4bb941f8435063f6ba22b5b767fda9b01dfd
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_pro#9bd3495df14f
  - benchmark_id: mmlu_professional_accounting
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 63.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_professional_accounting#fe2512aeeeaf
  - benchmark_id: mmlu_professional_law
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 57.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_professional_law#e1298f6dfeae
  - benchmark_id: mmlu_professional_medicine
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 81.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_professional_medicine#6f10dc0c0590
  - benchmark_id: mmlu_professional_psychology
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 78.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_professional_psychology#e1fc1666796a
  - benchmark_id: mmlu_public_relations
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 72.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_public_relations#33e3e6084bdd
  - benchmark_id: mmlu_security_studies
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 82.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_security_studies#c850a3b7f71d
  - benchmark_id: mmlu_sociology
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 88.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_sociology#3d1d0fbe6b31
  - benchmark_id: mmlu_us_foreign_policy
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 86.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_us_foreign_policy#49a78f832192
  - benchmark_id: mmlu_virology
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 62.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_virology#b64c9ef8cf1c
  - benchmark_id: mmlu_world_religions
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 86.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#mmlu_world_religions#9eef2d64e943
  - benchmark_id: musr
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 42.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/01-ai/Yi-1.5-34B-Chat/results_2025-02-13T18-27-04.338360.json
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
    - source_id: oll-v2-9c7075604dc5
      snapshot_ref: sha256:c5fd4a01fb21360b0f462d210c2d4bb941f8435063f6ba22b5b767fda9b01dfd
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#musr#5abf6129c9c2
  - benchmark_id: truthfulqa
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 62.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#truthfulqa#7741c7027cfe
  - benchmark_id: winogrande
    model_id_as_evaluated: 01-ai/Yi-1.5-34B-Chat
    score: 81.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-Chat/results_2024-05-15T03-44-20.662749.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-7c5ceaa7fe1f
      snapshot_ref: sha256:b0be7a22b44a408e321782290d05d8a5756a9171f606f21617879985111a6c52
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-34b-chat#winogrande#f09af83cdd63
  benchmark_source: open-llm-leaderboard-v2, open-llm-leaderboard-v1
  benchmark_as_of: 2026-04
  benchmark_notes: 'MODEL-116, 2026-09-24: removed math_500 58.5 and gpqa_diamond 36.5. They came from a hand-typed
    table in scripts/enrich_open_llm.py labelled Open LLM Leaderboard v2, and do not match that leaderboard (its row
    for 01-ai/Yi-1.5-34B-Chat has MATH Lvl 5 Raw 27.7 and GPQA Raw 36.5). MODEL-154, read 2026-09-24: Rechecked ifeval,
    bbh, musr and mmlu_pro against this model''s own OLL v2 run (01-ai/Yi-1.5-34B-Chat, torch.bfloat16, model revision
    f3128b2d02d82989daae566c0a7eadc621ca3254). IFEval is the mean of strict prompt and instruction accuracy; BBH and
    MuSR are unweighted subtask means; MMLU-Pro is raw accuracy. Values are percentages rounded to one decimal, not
    normalized leaderboard scores. Source: https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/01-ai/Yi-1.5-34B-Chat/results_2025-02-13T18-27-04.338360.json.'
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
  huggingface_downloads: 13105
  huggingface_likes: 276
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
  huggingface_url: https://huggingface.co/01-ai/Yi-1.5-34B-Chat
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


# Yi 1.5 34B Chat

Auto-generated from HuggingFace Hub metadata for [01-ai/Yi-1.5-34B-Chat](https://huggingface.co/01-ai/Yi-1.5-34B-Chat).

Licence: apache-2.0. Creator distribution https://huggingface.co/01-ai/Yi-1.5-34B-Chat/raw/main/README.md (apache-2.0) and Hub cardData.license apache-2.0, read 2026-09-18.
