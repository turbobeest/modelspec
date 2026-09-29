---
model_id: moonshot/kimi-k2-6
display_name: Kimi K2.6
provider: moonshot
provider_display: Moonshot AI
family: kimi-k2
version: kimi-k2.6
release_date: '2026-04-21'
last_updated: '2026-04-21'
status: active
model_type: llm-reasoning
model_subtypes: []
tags: []
pipeline_tag: ''
architecture:
  type: null
  total_parameters: 1026879376368
  active_parameters: 32000000000
  num_experts: 384
  experts_per_token: 8
  num_layers: 61
  hidden_size: 7168
  intermediate_size: 18432
  attention_type: null
  num_attention_heads: 64
  num_kv_heads: 64
  positional_encoding: null
  rope_theta: null
  vocab_size: 163840
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
  library_name: ''
licensing:
  open_weights: true
  license_type: null
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
  origin_country: CN
  origin_org_type: null
modalities:
  input:
  - text
  - image
  - video
  output:
  - text
  text:
    max_input_tokens: null
    max_output_tokens: 262144
    context_window: 262144
    streaming: null
    fill_in_middle: null
    json_mode: true
    system_prompt: null
  vision:
    supported: true
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
    overall: null
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
  input: 0.95
  output: 4.0
  reasoning: null
  cache_read: 0.16
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
    model_id: moonshotai/Kimi-K2.6
    url: https://huggingface.co/moonshotai/Kimi-K2.6
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
    model_id_as_evaluated: kimi-k2.6
    score: 1460.44
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / overall, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category overall,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1460.44 [1455.91, 1464.98], 37502
      votes, rank 52.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: moonshot/kimi-k2-6#arena_elo_style_control#0457d27fd6c3
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:bea7ea9d7344aeccaed159b64f2f3aa97e84231d3723b02f9d4a5672b6b889b8
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_coding
    model_id_as_evaluated: kimi-k2.6
    score: 1513.99
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / coding, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category coding,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1513.99 [1506.95, 1521.03], 10398
      votes, rank 39.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: moonshot/kimi-k2-6#arena_sc_coding#de84c5062b96
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:da249e40e0397ffcd8dd5f738c4c91f9a389869f8ae9e26c425a1187f04c7118
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_hard_prompts
    model_id_as_evaluated: kimi-k2.6
    score: 1484.73
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / hard_prompts, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category hard_prompts,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1484.73 [1479.44, 1490.01], 24291
      votes, rank 50.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: moonshot/kimi-k2-6#arena_sc_hard_prompts#ba47fa15092f
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:5a69c3a3a5f23cf6bfd2b0ecae495ec9731f62df889f4147793616588a2d4f8b
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_math
    model_id_as_evaluated: kimi-k2.6
    score: 1478.07
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / math, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category math, leaderboard_publish_date
      2026-09-13; style control. Highest-effort row for the product (effort: default; MODEL-123
      max-effort rule). Rating 1478.07 [1464.57, 1491.57], 1931 votes, rank 27.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: moonshot/kimi-k2-6#arena_sc_math#e6c53599f64c
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:41e622d3837a9ab1577d975e3c57ae92db367c09f45606ed1870a32a4591335a
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_creative_writing
    model_id_as_evaluated: kimi-k2.6
    score: 1430.7
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / creative_writing, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category creative_writing,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1430.70 [1422.22, 1439.18], 5821
      votes, rank 65.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: moonshot/kimi-k2-6#arena_sc_creative_writing#614f6bb2965a
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:4ca49a5b7efede8e577057d10266b363a837e56331ac79f7540f7da349a3eee5
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_instruction_following
    model_id_as_evaluated: kimi-k2.6
    score: 1453.72
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / instruction_following, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category instruction_following,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1453.72 [1447.25, 1460.19], 12215
      votes, rank 51.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: moonshot/kimi-k2-6#arena_sc_instruction_following#1150e4ca057b
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:6bcc35b68ac189cda1a204de4fab84c84fcd9d853dc2c3265e68366133d9093b
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_multi_turn
    model_id_as_evaluated: kimi-k2.6
    score: 1459.44
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / multi_turn, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category multi_turn,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1459.44 [1451.27, 1467.60], 6553
      votes, rank 69.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: moonshot/kimi-k2-6#arena_sc_multi_turn#f75aa44e457d
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:76f93ba07e2611ee096faf4210eb6b965b5b113b375cb5edec5f224be61fc346
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_expert
    model_id_as_evaluated: kimi-k2.6
    score: 1501.57
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / expert, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category expert,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1501.57 [1491.23, 1511.91], 3505
      votes, rank 32.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: moonshot/kimi-k2-6#arena_sc_expert#c6e295d4bd3c
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:ebf8116274f3815b353511b1829bd763a0817e2a0c5d3669072ebd5571271745
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_longer_query
    model_id_as_evaluated: kimi-k2.6
    score: 1475.74
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / longer_query, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category longer_query,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1475.74 [1469.51, 1481.96], 15529
      votes, rank 45.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: moonshot/kimi-k2-6#arena_sc_longer_query#267f68d7a70f
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:3c7de94587c842e12c134292a7df52a9faafb46f877d184d8f235d5c1d466737
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_non_english
    model_id_as_evaluated: kimi-k2.6
    score: 1448.97
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / non_english, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category non_english,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1448.97 [1443.54, 1454.41], 20342
      votes, rank 51.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: moonshot/kimi-k2-6#arena_sc_non_english#fbdeeb0f8eb4
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:47f41bf8222f55644ca4a36db5ad4178546c5d3e2982bcda2dc08798f9776a65
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_medicine
    model_id_as_evaluated: kimi-k2.6
    score: 1470.9
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / industry_medicine_and_healthcare, latest split,
      revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category industry_medicine_and_healthcare,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1470.90 [1458.97, 1482.83], 2702
      votes, rank 69.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: moonshot/kimi-k2-6#arena_sc_medicine#edd6755dc698
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:31163709a3917ed23ec956a2589a6a5ad30924817977652909218ecbbf9a8d0e
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_legal
    model_id_as_evaluated: kimi-k2.6
    score: 1461.67
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / industry_legal_and_government, latest split, revision
      1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category industry_legal_and_government,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1461.67 [1450.24, 1473.09], 2844
      votes, rank 69.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: moonshot/kimi-k2-6#arena_sc_legal#dcc8fcdb37ba
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:6aec9d4dd9fc82958ffeceea56c977de5d8204f6c62ad5113657b828f9bc55da
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_business
    model_id_as_evaluated: kimi-k2.6
    score: 1455.48
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / industry_business_and_management_and_financial_operations,
      latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category industry_business_and_management_and_financial_operations,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1455.48 [1447.77, 1463.19], 7473
      votes, rank 61.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: moonshot/kimi-k2-6#arena_sc_business#ad9530a2bcd5
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:ba565a81fbb65e9d13c80776fda09aabedc819d64793b355a5a5fe836212472e
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_science
    model_id_as_evaluated: kimi-k2.6
    score: 1477.44
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / industry_life_and_physical_and_social_science, latest
      split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category industry_life_and_physical_and_social_science,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1477.44 [1469.32, 1485.55], 6226
      votes, rank 61.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: moonshot/kimi-k2-6#arena_sc_science#4d184c5f164a
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:dff891db693196c263ad841fcb75cf135a4529936b386a76fc324e6b66bb2d2e
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_writing
    model_id_as_evaluated: kimi-k2.6
    score: 1438.36
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / industry_writing_and_literature_and_language, latest
      split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category industry_writing_and_literature_and_language,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1438.36 [1431.12, 1445.59], 8851
      votes, rank 65.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: moonshot/kimi-k2-6#arena_sc_writing#734d4b819b1c
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:451771d6d03dfcdc902ebbb505ce47bfc614e33bde751b42f3be31d89d416086
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_vision
    model_id_as_evaluated: kimi-k2.6
    score: 1262.37
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: vision_style_control / overall, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset vision_style_control, category overall,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1262.37 [1255.30, 1269.44], 15347
      votes, rank 37.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: moonshot/kimi-k2-6#arena_sc_vision#86df970cfee2
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-vision-style-control
      snapshot_ref: sha256:9da6b0bec36701b281c5b1b1e49bed1a536c78908b3d186f41a551360cb584c4
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_webdev
    model_id_as_evaluated: kimi-k2.6
    score: 1508.6
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-23'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: webdev / overall, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset webdev, category overall, leaderboard_publish_date
      2026-09-23; no style-controlled variant. Highest-effort row for the product (effort: default;
      MODEL-123 max-effort rule). Rating 1508.60 [1501.20, 1516.00], 9587 votes, rank 45.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: moonshot/kimi-k2-6#arena_webdev#0f3c176169e6
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-143-evidence-arena-webdev-json
      snapshot_ref: sha256:1342f43f483667f8e4313a1fb517522e1f18aa1b09d4812f8d3163c4ff30b9bc
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: gpqa_diamond
    model_id_as_evaluated: kimi-k2.6
    score: 90.78
    unit: percent
    source_url: https://epoch.ai/benchmarks/gpqa-diamond
    source_kind: independent_evaluator
    evidence_date: '2026-05-01'
    date_type: evaluated
    verified_at: '2026-09-29'
    benchmark_version: GPQA Diamond (Epoch AI run)
    configuration: Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (gpqa_diamond.csv),
      read 2026-09-24. Run started 2026-05-01T17:25:36.000Z; effort default; highest-effort
      run for the model (MODEL-123 max-effort rule), newest on a tie. Standard error 1.72 points.
    limitations: Epoch AI data, CC BY 4.0.
    id: moonshot/kimi-k2-6#gpqa_diamond#4b86fab1a201
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-143-evidence-epoch-gpqa-diamond-csv
      snapshot_ref: sha256:946618a3befb5210ccf841c8f3c6b257584d10d5314a7e03408fb73aa13a38a9
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: frontiermath_tiers_1_3_v2
    model_id_as_evaluated: kimi-k2.6
    score: 57.19
    unit: percent
    source_url: https://epoch.ai/frontiermath
    source_kind: independent_evaluator
    evidence_date: '2026-06-10'
    date_type: evaluated
    verified_at: '2026-09-29'
    benchmark_version: FrontierMath-Tiers-1-3-v2-Private (Epoch AI run)
    configuration: Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (frontiermath_tiers_1_3_v2.csv),
      read 2026-09-24. Run started 2026-06-10T19:47:36.000Z; effort default; highest-effort
      run for the model (MODEL-123 max-effort rule), newest on a tie. Standard error 2.94 points.
    limitations: Epoch AI data, CC BY 4.0.
    id: moonshot/kimi-k2-6#frontiermath_tiers_1_3_v2#debe969d7468
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-143-evidence-epoch-frontiermath-tiers-1-3-v2-csv
      snapshot_ref: sha256:ff8b653f9ba2c936d6278eeecc42b3a3dee1079e409c8806616f80fb41e23c11
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: simpleqa_verified
    model_id_as_evaluated: kimi-k2.6
    score: 34.9
    unit: percent
    source_url: https://epoch.ai/benchmarks/simpleqa-verified
    source_kind: independent_evaluator
    evidence_date: '2026-08-10'
    date_type: evaluated
    verified_at: '2026-09-29'
    benchmark_version: SimpleQA Verified, proportion correct, Epoch AI protocol with anti-abstention
      prompt
    configuration: Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (simpleqa_verified.csv),
      read 2026-09-24. Run started 2026-08-10T21:35:30.000Z; effort default; highest-effort
      run for the model (MODEL-123 max-effort rule), newest on a tie. Standard error 1.51 points.
    limitations: Epoch AI data, CC BY 4.0.
    id: moonshot/kimi-k2-6#simpleqa_verified#0ec5d94f82ca
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-epoch-simpleqa-verified-csv
      snapshot_ref: sha256:f4e88f5154755ef9c355b28d6900467dce89bcbe0ea54329d1f96215c21239fa
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: swe_bench_verified
    model_id_as_evaluated: kimi-k2.6
    score: 76.65
    unit: percent
    source_url: https://epoch.ai/benchmarks/swe-bench-verified
    source_kind: independent_evaluator
    evidence_date: '2026-05-08'
    date_type: evaluated
    verified_at: '2026-09-29'
    benchmark_version: SWE-bench Verified (Epoch AI run)
    configuration: Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (swe_bench_verified.csv),
      read 2026-09-24. Run started 2026-05-08T10:21:24.110Z; effort default; highest-effort
      run for the model (MODEL-123 max-effort rule), newest on a tie. Standard error 1.92 points.
    limitations: Epoch AI data, CC BY 4.0.
    id: moonshot/kimi-k2-6#swe_bench_verified#141378cad40d
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-epoch-swe-bench-verified-csv
      snapshot_ref: sha256:2cd01ace47ba0c0e08f7fee6c4ed24921ff7ce01fe86d73f9e18203dc2adca0f
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: vending_bench_2
    model_id_as_evaluated: Kimi K2.6
    score: 6204.57
    unit: USD
    source_url: https://andonlabs.com/evals/vending-bench-2
    source_kind: benchmark_author
    evidence_date: '2026-09-29'
    date_type: evaluated
    verified_at: '2026-09-29'
    benchmark_version: Vending-Bench 2, mean final balance over 5 runs
    configuration: Board row as copied in Epoch AI's benchmark data (vending_bench_2_external.csv,
      https://epoch.ai/data/benchmark_data.zip), read 2026-09-24. Effort default; the highest-effort
      row for the model (MODEL-123 max-effort rule).
    limitations: A live board's standing, dated by the day ModelSpec read Epoch AI's copy; the
      copy carries no per-row date. Epoch AI data, CC BY 4.0.
    id: moonshot/kimi-k2-6#vending_bench_2#9c61499093a2
    measured_by: benchmark_author
    effort: null
    harness: null
    sources:
    - source_id: model-160-vending-bench-2
      snapshot_ref: sha256:94074584ec83e973b31884f48956a6bc43e36a33d47dc3feaa7c52adf23a9c12
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: aime_2026
    model_id_as_evaluated: Kimi K2.6 (Think)
    score: 95.83
    unit: percent
    source_url: https://matharena.ai/competition_tables/aime--aime_2026
    source_kind: independent_evaluator
    evidence_date: '2026-09-29'
    date_type: evaluated
    verified_at: '2026-09-29'
    benchmark_version: AIME 2026, MathArena final-answer table
    configuration: MathArena competition table read 2026-09-26; the table states no run
      date, so the reading is dated by the observation. Effort thinking; highest-effort
      row for the model. MathArena lists final-answer competitions as deprecated.
    limitations: 'MathArena marks this row: model was released after competition release, so
      contamination is possible.'
    id: moonshot/kimi-k2-6#aime_2026#6284c8028cd6
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-matharena-aime-2026
      snapshot_ref: sha256:82521ecfb14888fcf11b8fe08e9aa67eb588467d241b6778ecd538ae6d382b5e
      cited_regions:
      - rows
    quality_flags:
    - deprecated
    - contamination_warning
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_english
    model_id_as_evaluated: kimi-k2.6
    score: 1467.48
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / english, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1467.48 [1461.75,
      1473.21], 17160 votes, rank 55. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:cee57baa7239c5aa2091dcb5db0b4c2ac22cec732b235d66c0cda2ee55bdcb44
      cited_regions:
      - rows
    id: moonshot/kimi-k2-6#arena_sc_english#1debb5f14c98
  - benchmark_id: arena_sc_chinese
    model_id_as_evaluated: kimi-k2.6
    score: 1525.77
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / chinese, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1525.77 [1511.49,
      1540.04], 1886 votes, rank 21. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:9bf00fc37e8a997735f423949aba6ffc5551990b6f835297d3fed2b364abe02b
      cited_regions:
      - rows
    id: moonshot/kimi-k2-6#arena_sc_chinese#04f321622015
  - benchmark_id: arena_sc_japanese
    model_id_as_evaluated: kimi-k2.6
    score: 1442.95
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / japanese, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1442.95 [1413.93,
      1471.98], 467 votes, rank 36. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:13b68c219a1ec549a9336846ddacaf97471f6323c09e4f45a73eab7a0857a9ca
      cited_regions:
      - rows
    id: moonshot/kimi-k2-6#arena_sc_japanese#4fd91ecd7c9f
  - benchmark_id: arena_sc_korean
    model_id_as_evaluated: kimi-k2.6
    score: 1422.51
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / korean, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1422.51 [1399.49,
      1445.53], 713 votes, rank 45. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:96706e685de18541b6ad515db22607a7840bad8bc902a30a8a38f949cd409c08
      cited_regions:
      - rows
    id: moonshot/kimi-k2-6#arena_sc_korean#dcbee107a5fe
  - benchmark_id: arena_sc_russian
    model_id_as_evaluated: kimi-k2.6
    score: 1452.85
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / russian, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1452.85 [1442.95,
      1462.74], 3814 votes, rank 63. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:eb77af068077fa90a9514ad454b6a65f061a176f0d68897132e1526f3be743dd
      cited_regions:
      - rows
    id: moonshot/kimi-k2-6#arena_sc_russian#f238d0ea6ef6
  - benchmark_id: arena_sc_spanish
    model_id_as_evaluated: kimi-k2.6
    score: 1457.57
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / spanish, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1457.57 [1440.46,
      1474.68], 1320 votes, rank 47. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:e56e27431afb859f3376e3d5609785906e24647b4c0c65a324b7995944b9573b
      cited_regions:
      - rows
    id: moonshot/kimi-k2-6#arena_sc_spanish#8305074e78f9
  - benchmark_id: arena_sc_german
    model_id_as_evaluated: kimi-k2.6
    score: 1456.74
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / german, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1456.74 [1435.08,
      1478.40], 724 votes, rank 53. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:098d6730e0b426da68eee86ddfd97bb03c3b1048e178378de1ec3924fa209c6d
      cited_regions:
      - rows
    id: moonshot/kimi-k2-6#arena_sc_german#ba53a76d053c
  - benchmark_id: arena_sc_french
    model_id_as_evaluated: kimi-k2.6
    score: 1473.05
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / french, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1473.05 [1456.03,
      1490.06], 1501 votes, rank 66. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:c6c9f83eb7147bedac479a445a3803aad09d613643414d3cd5035dbde46d6f2f
      cited_regions:
      - rows
    id: moonshot/kimi-k2-6#arena_sc_french#ee62b93ace91
  - benchmark_id: arena_sc_polish
    model_id_as_evaluated: kimi-k2.6
    score: 1445.22
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / polish, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1445.22 [1423.93,
      1466.51], 740 votes, rank 69. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:a99daf2dc2fbf9b06de90a127cc1408c7a19e4fa45a1a4d538b668211c4b5892
      cited_regions:
      - rows
    id: moonshot/kimi-k2-6#arena_sc_polish#4a3a8c8538a7
  - benchmark_id: arena_sc_vision_ocr
    model_id_as_evaluated: kimi-k2.6
    score: 1277.67
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: vision_style_control / ocr, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1277.67 [1270.32,
      1285.03], 11005 votes, rank 36. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-vision-style-control
      snapshot_ref: sha256:72ff33856df7c05e7611f78bd6f0a13fc422694ad107f25e00c11b10edb14422
      cited_regions:
      - rows
    id: moonshot/kimi-k2-6#arena_sc_vision_ocr#3d1b194798cc
  - benchmark_id: arena_sc_vision_diagram
    model_id_as_evaluated: kimi-k2.6
    score: 1292.45
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: vision_style_control / diagram, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1292.45 [1281.87,
      1303.03], 4017 votes, rank 36. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-vision-style-control
      snapshot_ref: sha256:f70ad4aae81aa8b6cca27735001f45704e13f64af12ad93244cd19ca60d98085
      cited_regions:
      - rows
    id: moonshot/kimi-k2-6#arena_sc_vision_diagram#baf8d0c4d171
  - benchmark_id: arena_sc_vision_homework
    model_id_as_evaluated: kimi-k2.6
    score: 1302.15
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: vision_style_control / homework, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1302.15 [1288.75,
      1315.55], 2136 votes, rank 27. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-vision-style-control
      snapshot_ref: sha256:8015c65e88084d6c6b25f9787fb1528f550abd8e055cf8f3b753e863296d3176
      cited_regions:
      - rows
    id: moonshot/kimi-k2-6#arena_sc_vision_homework#48a9ed1e3233
  - benchmark_id: arena_sc_document
    model_id_as_evaluated: kimi-k2.6
    score: 1450.74
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: document / overall, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1450.74 [1443.10,
      1458.37], 11291 votes, rank 27. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-document
      snapshot_ref: sha256:050705ac3c2e5ba81aacf700b87f5144dd7b0ec9f7f12168be5086b1c11be958
      cited_regions:
      - rows
    id: moonshot/kimi-k2-6#arena_sc_document#f50cf87ee769
  - benchmark_id: arena_sc_industry_software_it_services
    model_id_as_evaluated: kimi-k2.6
    score: 1502.89
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / industry_software_and_it_services, latest split, revision
      1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1502.89 [1496.79,
      1508.99], 15050 votes, rank 38. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:4eaa9890dce0719aa263af890c9f2a7bb1a3198e291d84dbf8c1371d4f150c52
      cited_regions:
      - rows
    id: moonshot/kimi-k2-6#arena_sc_industry_software_it_services#352afa0247dc
  - benchmark_id: arena_sc_industry_entertainment_sports_media
    model_id_as_evaluated: kimi-k2.6
    score: 1427.41
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / industry_entertainment_and_sports_and_media, latest
      split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1427.41 [1419.66,
      1435.16], 7607 votes, rank 66. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:df0d5e7c4d4ce1f683618242c0786eafd164d98b3b49dbaa6e699476bec94ccf
      cited_regions:
      - rows
    id: moonshot/kimi-k2-6#arena_sc_industry_entertainment_sports_media#707e823d5492
  - benchmark_id: arena_sc_industry_mathematical
    model_id_as_evaluated: kimi-k2.6
    score: 1484.07
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / industry_mathematical, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1484.07 [1470.75,
      1497.40], 2046 votes, rank 35. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:b0f3ee924239a7a9a1e60676935d0c83091f29517b8acb95e07868e370822e82
      cited_regions:
      - rows
    id: moonshot/kimi-k2-6#arena_sc_industry_mathematical#6e24a064aab3
  - benchmark_id: arena_sc_factuality
    model_id_as_evaluated: kimi-k2.6
    score: 1455.34
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_factuality / overall, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1455.34 [1451.62,
      1459.06], 37456 votes, rank 48. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-factuality
      snapshot_ref: sha256:ece0fd0afe2b42a38bce698a6be5329044b5503f5edb7f43473c19394b38fc28
      cited_regions:
      - rows
    id: moonshot/kimi-k2-6#arena_sc_factuality#e61adbc1cbb3
  benchmark_source: ''
  benchmark_as_of: ''
  benchmark_notes: ''
deployment:
  api_only: false
  local_inference: false
  self_hostable: false
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
  huggingface_downloads: null
  huggingface_likes: null
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
  models_dev_url: https://models.dev/moonshotai
  provider_docs_url: ''
  huggingface_url: ''
  arxiv_url: ''
  paper_url: ''
  github_url: ''
  ollama_url: ''
  artificial_analysis_url: ''
  arena_url: ''
  last_scraped_models_dev: ''
  last_scraped_huggingface: ''
  last_scraped_benchmarks: ''
  last_scraped_pricing: ''
facts:
- facet: model.class
  value: text-generator
  state: known
  sources:
  - source_id: model-143-moonshot-kimi-k2-6
    snapshot_ref: sha256:95db3be1d0473e482c7aa901f237ad7af8bb7929625a777b27428081bb8ea9f7
    cited_regions:
    - model-spec
  - source_id: model-143-kimi-k2-6-guide
    snapshot_ref: sha256:3d5a698cf776fcbe743fc02d2335e23f45dbb9a2c5fbba66195a4b1c861bc275
    cited_regions:
    - audit
  - source_id: model-143-kimi-k3-guide
    snapshot_ref: sha256:2d5f971cdba4f6e36d021746ff9511f9323e4a66c27e30ac3c3ea6a10b36d96f
    cited_regions:
    - audit
- facet: model.input_modalities
  value:
  - text
  - image
  - video
  state: known
  sources:
  - source_id: model-143-moonshot-kimi-k2-6
    snapshot_ref: sha256:95db3be1d0473e482c7aa901f237ad7af8bb7929625a777b27428081bb8ea9f7
    cited_regions:
    - model-spec
  - source_id: model-143-kimi-k2-6-guide
    snapshot_ref: sha256:3d5a698cf776fcbe743fc02d2335e23f45dbb9a2c5fbba66195a4b1c861bc275
    cited_regions:
    - audit
  - source_id: model-143-kimi-k3-guide
    snapshot_ref: sha256:2d5f971cdba4f6e36d021746ff9511f9323e4a66c27e30ac3c3ea6a10b36d96f
    cited_regions:
    - audit
- facet: model.output_modalities
  value:
  - text
  state: known
  sources:
  - source_id: model-143-moonshot-kimi-k2-6
    snapshot_ref: sha256:95db3be1d0473e482c7aa901f237ad7af8bb7929625a777b27428081bb8ea9f7
    cited_regions:
    - model-spec
  - source_id: model-143-kimi-k2-6-guide
    snapshot_ref: sha256:3d5a698cf776fcbe743fc02d2335e23f45dbb9a2c5fbba66195a4b1c861bc275
    cited_regions:
    - audit
  - source_id: model-143-kimi-k3-guide
    snapshot_ref: sha256:2d5f971cdba4f6e36d021746ff9511f9323e4a66c27e30ac3c3ea6a10b36d96f
    cited_regions:
    - audit
- facet: model.context_window
  value: 262144
  state: known
  sources:
  - source_id: model-143-moonshot-kimi-k2-6
    snapshot_ref: sha256:95db3be1d0473e482c7aa901f237ad7af8bb7929625a777b27428081bb8ea9f7
    cited_regions:
    - model-spec
  - source_id: model-143-kimi-k2-6-guide
    snapshot_ref: sha256:3d5a698cf776fcbe743fc02d2335e23f45dbb9a2c5fbba66195a4b1c861bc275
    cited_regions:
    - audit
  - source_id: model-143-kimi-k3-guide
    snapshot_ref: sha256:2d5f971cdba4f6e36d021746ff9511f9323e4a66c27e30ac3c3ea6a10b36d96f
    cited_regions:
    - audit
- facet: model.max_output_tokens
  value: 262144
  state: known
  sources:
  - source_id: model-143-moonshot-kimi-k2-6
    snapshot_ref: sha256:95db3be1d0473e482c7aa901f237ad7af8bb7929625a777b27428081bb8ea9f7
    cited_regions:
    - model-spec
  - source_id: model-143-kimi-k2-6-guide
    snapshot_ref: sha256:3d5a698cf776fcbe743fc02d2335e23f45dbb9a2c5fbba66195a4b1c861bc275
    cited_regions:
    - audit
  - source_id: model-143-kimi-k3-guide
    snapshot_ref: sha256:2d5f971cdba4f6e36d021746ff9511f9323e4a66c27e30ac3c3ea6a10b36d96f
    cited_regions:
    - audit
- facet: model.weights_openness
  value: open_weights
  state: known
  sources:
  - source_id: model-143-moonshot-kimi-k2-6
    snapshot_ref: sha256:95db3be1d0473e482c7aa901f237ad7af8bb7929625a777b27428081bb8ea9f7
    cited_regions:
    - model-spec
  - source_id: model-143-hf-metadata-moonshot-kimi-k2-6
    snapshot_ref: sha256:617e481660ab7611028cf94fef06f75ec67b5623380f9073eca8b970f607a72a
    cited_regions:
    - audit
  - source_id: model-143-kimi-k2-6-license
    snapshot_ref: sha256:1d4ab2d8404287de44429024a78b58d3aabc4df9d0c490e73fec9ff1fd842529
    cited_regions:
    - audit
  - source_id: model-143-kimi-k2-6-guide
    snapshot_ref: sha256:3d5a698cf776fcbe743fc02d2335e23f45dbb9a2c5fbba66195a4b1c861bc275
    cited_regions:
    - audit
  - source_id: model-143-kimi-k3-guide
    snapshot_ref: sha256:2d5f971cdba4f6e36d021746ff9511f9323e4a66c27e30ac3c3ea6a10b36d96f
    cited_regions:
    - audit
- facet: licence.commercial_use
  value: permitted_with_conditions
  state: known
  sources:
  - source_id: model-143-moonshot-kimi-k2-6
    snapshot_ref: sha256:95db3be1d0473e482c7aa901f237ad7af8bb7929625a777b27428081bb8ea9f7
    cited_regions:
    - model-spec
  - source_id: model-143-kimi-k2-6-license
    snapshot_ref: sha256:1d4ab2d8404287de44429024a78b58d3aabc4df9d0c490e73fec9ff1fd842529
    cited_regions:
    - audit
- facet: licence.user_cap
  value: unbounded
  state: known
  sources:
  - source_id: model-143-moonshot-kimi-k2-6
    snapshot_ref: sha256:95db3be1d0473e482c7aa901f237ad7af8bb7929625a777b27428081bb8ea9f7
    cited_regions:
    - model-spec
  - source_id: model-143-kimi-k2-6-license
    snapshot_ref: sha256:1d4ab2d8404287de44429024a78b58d3aabc4df9d0c490e73fec9ff1fd842529
    cited_regions:
    - audit
- facet: licence.output_training
  value: permitted
  state: known
  sources:
  - source_id: model-143-moonshot-kimi-k2-6
    snapshot_ref: sha256:95db3be1d0473e482c7aa901f237ad7af8bb7929625a777b27428081bb8ea9f7
    cited_regions:
    - model-spec
  - source_id: model-143-kimi-k2-6-license
    snapshot_ref: sha256:1d4ab2d8404287de44429024a78b58d3aabc4df9d0c490e73fec9ff1fd842529
    cited_regions:
    - audit
- facet: licence.fine_tuning
  value: permitted_with_conditions
  state: known
  sources:
  - source_id: model-143-moonshot-kimi-k2-6
    snapshot_ref: sha256:95db3be1d0473e482c7aa901f237ad7af8bb7929625a777b27428081bb8ea9f7
    cited_regions:
    - model-spec
  - source_id: model-143-kimi-k2-6-license
    snapshot_ref: sha256:1d4ab2d8404287de44429024a78b58d3aabc4df9d0c490e73fec9ff1fd842529
    cited_regions:
    - audit
- facet: origin.lab_jurisdiction
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-moonshot-kimi-k2-6
    snapshot_ref: sha256:95db3be1d0473e482c7aa901f237ad7af8bb7929625a777b27428081bb8ea9f7
    cited_regions:
    - model-spec
  - source_id: model-143-kimi-k2-6-guide
    snapshot_ref: sha256:3d5a698cf776fcbe743fc02d2335e23f45dbb9a2c5fbba66195a4b1c861bc275
    cited_regions:
    - audit
  - source_id: model-143-kimi-k3-guide
    snapshot_ref: sha256:2d5f971cdba4f6e36d021746ff9511f9323e4a66c27e30ac3c3ea6a10b36d96f
    cited_regions:
    - audit
  - source_id: model-143-kimi-k2-6-license
    snapshot_ref: sha256:1d4ab2d8404287de44429024a78b58d3aabc4df9d0c490e73fec9ff1fd842529
    cited_regions:
    - audit
  - source_id: model-143-hf-metadata-moonshot-kimi-k2-6
    snapshot_ref: sha256:617e481660ab7611028cf94fef06f75ec67b5623380f9073eca8b970f607a72a
    cited_regions:
    - audit
  checked_sources:
  - model-143-moonshot-kimi-k2-6
  - model-143-kimi-k2-6-guide
  - model-143-kimi-k3-guide
  - model-143-kimi-k2-6-license
  - model-143-hf-metadata-moonshot-kimi-k2-6
- facet: origin.base_lineage
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-moonshot-kimi-k2-6
    snapshot_ref: sha256:95db3be1d0473e482c7aa901f237ad7af8bb7929625a777b27428081bb8ea9f7
    cited_regions:
    - model-spec
  - source_id: model-143-kimi-k2-6-guide
    snapshot_ref: sha256:3d5a698cf776fcbe743fc02d2335e23f45dbb9a2c5fbba66195a4b1c861bc275
    cited_regions:
    - audit
  - source_id: model-143-kimi-k3-guide
    snapshot_ref: sha256:2d5f971cdba4f6e36d021746ff9511f9323e4a66c27e30ac3c3ea6a10b36d96f
    cited_regions:
    - audit
  - source_id: model-143-kimi-k2-6-license
    snapshot_ref: sha256:1d4ab2d8404287de44429024a78b58d3aabc4df9d0c490e73fec9ff1fd842529
    cited_regions:
    - audit
  - source_id: model-143-hf-metadata-moonshot-kimi-k2-6
    snapshot_ref: sha256:617e481660ab7611028cf94fef06f75ec67b5623380f9073eca8b970f607a72a
    cited_regions:
    - audit
  checked_sources:
  - model-143-moonshot-kimi-k2-6
  - model-143-kimi-k2-6-guide
  - model-143-kimi-k3-guide
  - model-143-kimi-k2-6-license
  - model-143-hf-metadata-moonshot-kimi-k2-6
- facet: origin.weights_hosting
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-moonshot-kimi-k2-6
    snapshot_ref: sha256:95db3be1d0473e482c7aa901f237ad7af8bb7929625a777b27428081bb8ea9f7
    cited_regions:
    - model-spec
  - source_id: model-143-kimi-k2-6-guide
    snapshot_ref: sha256:3d5a698cf776fcbe743fc02d2335e23f45dbb9a2c5fbba66195a4b1c861bc275
    cited_regions:
    - audit
  - source_id: model-143-kimi-k3-guide
    snapshot_ref: sha256:2d5f971cdba4f6e36d021746ff9511f9323e4a66c27e30ac3c3ea6a10b36d96f
    cited_regions:
    - audit
  - source_id: model-143-kimi-k2-6-license
    snapshot_ref: sha256:1d4ab2d8404287de44429024a78b58d3aabc4df9d0c490e73fec9ff1fd842529
    cited_regions:
    - audit
  - source_id: model-143-hf-metadata-moonshot-kimi-k2-6
    snapshot_ref: sha256:617e481660ab7611028cf94fef06f75ec67b5623380f9073eca8b970f607a72a
    cited_regions:
    - audit
  checked_sources:
  - model-143-moonshot-kimi-k2-6
  - model-143-kimi-k2-6-guide
  - model-143-kimi-k3-guide
  - model-143-kimi-k2-6-license
  - model-143-hf-metadata-moonshot-kimi-k2-6
- facet: model.release_date
  value: '2026-04-21'
  state: known
  sources:
  - source_id: model-143-moonshot-kimi-k2-6
    snapshot_ref: sha256:95db3be1d0473e482c7aa901f237ad7af8bb7929625a777b27428081bb8ea9f7
    cited_regions:
    - model-spec
  - source_id: model-143-hf-metadata-moonshot-kimi-k2-6
    snapshot_ref: sha256:617e481660ab7611028cf94fef06f75ec67b5623380f9073eca8b970f607a72a
    cited_regions:
    - audit
  - source_id: model-143-kimi-k2-6-guide
    snapshot_ref: sha256:3d5a698cf776fcbe743fc02d2335e23f45dbb9a2c5fbba66195a4b1c861bc275
    cited_regions:
    - audit
  - source_id: model-143-kimi-k3-guide
    snapshot_ref: sha256:2d5f971cdba4f6e36d021746ff9511f9323e4a66c27e30ac3c3ea6a10b36d96f
    cited_regions:
    - audit
- facet: model.lifecycle
  value: active
  state: known
  sources:
  - source_id: model-143-moonshot-kimi-k2-6
    snapshot_ref: sha256:95db3be1d0473e482c7aa901f237ad7af8bb7929625a777b27428081bb8ea9f7
    cited_regions:
    - model-spec
  - source_id: model-143-hf-metadata-moonshot-kimi-k2-6
    snapshot_ref: sha256:617e481660ab7611028cf94fef06f75ec67b5623380f9073eca8b970f607a72a
    cited_regions:
    - audit
  - source_id: model-143-kimi-k2-6-guide
    snapshot_ref: sha256:3d5a698cf776fcbe743fc02d2335e23f45dbb9a2c5fbba66195a4b1c861bc275
    cited_regions:
    - audit
  - source_id: model-143-kimi-k3-guide
    snapshot_ref: sha256:2d5f971cdba4f6e36d021746ff9511f9323e4a66c27e30ac3c3ea6a10b36d96f
    cited_regions:
    - audit
- facet: feature.tool_calling
  value: true
  state: known
  sources:
  - source_id: model-143-moonshot-kimi-k2-6
    snapshot_ref: sha256:95db3be1d0473e482c7aa901f237ad7af8bb7929625a777b27428081bb8ea9f7
    cited_regions:
    - model-spec
  - source_id: model-143-kimi-k2-6-guide
    snapshot_ref: sha256:3d5a698cf776fcbe743fc02d2335e23f45dbb9a2c5fbba66195a4b1c861bc275
    cited_regions:
    - audit
  - source_id: model-143-kimi-k3-guide
    snapshot_ref: sha256:2d5f971cdba4f6e36d021746ff9511f9323e4a66c27e30ac3c3ea6a10b36d96f
    cited_regions:
    - audit
- facet: feature.structured_output
  value: true
  state: known
  sources:
  - source_id: model-143-moonshot-kimi-k2-6
    snapshot_ref: sha256:95db3be1d0473e482c7aa901f237ad7af8bb7929625a777b27428081bb8ea9f7
    cited_regions:
    - model-spec
  - source_id: model-143-kimi-k2-6-guide
    snapshot_ref: sha256:3d5a698cf776fcbe743fc02d2335e23f45dbb9a2c5fbba66195a4b1c861bc275
    cited_regions:
    - audit
  - source_id: model-143-kimi-k3-guide
    snapshot_ref: sha256:2d5f971cdba4f6e36d021746ff9511f9323e4a66c27e30ac3c3ea6a10b36d96f
    cited_regions:
    - audit
- facet: feature.effort_controls
  value: true
  state: known
  sources:
  - source_id: model-143-moonshot-kimi-k2-6
    snapshot_ref: sha256:95db3be1d0473e482c7aa901f237ad7af8bb7929625a777b27428081bb8ea9f7
    cited_regions:
    - model-spec
  - source_id: model-143-kimi-k2-6-guide
    snapshot_ref: sha256:3d5a698cf776fcbe743fc02d2335e23f45dbb9a2c5fbba66195a4b1c861bc275
    cited_regions:
    - audit
  - source_id: model-143-kimi-k3-guide
    snapshot_ref: sha256:2d5f971cdba4f6e36d021746ff9511f9323e4a66c27e30ac3c3ea6a10b36d96f
    cited_regions:
    - audit
- facet: feature.batch
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-moonshot-kimi-k2-6
    snapshot_ref: sha256:95db3be1d0473e482c7aa901f237ad7af8bb7929625a777b27428081bb8ea9f7
    cited_regions:
    - model-spec
  - source_id: model-143-kimi-k2-6-guide
    snapshot_ref: sha256:3d5a698cf776fcbe743fc02d2335e23f45dbb9a2c5fbba66195a4b1c861bc275
    cited_regions:
    - audit
  - source_id: model-143-kimi-k3-guide
    snapshot_ref: sha256:2d5f971cdba4f6e36d021746ff9511f9323e4a66c27e30ac3c3ea6a10b36d96f
    cited_regions:
    - audit
  - source_id: model-143-kimi-k2-6-license
    snapshot_ref: sha256:1d4ab2d8404287de44429024a78b58d3aabc4df9d0c490e73fec9ff1fd842529
    cited_regions:
    - audit
  - source_id: model-143-hf-metadata-moonshot-kimi-k2-6
    snapshot_ref: sha256:617e481660ab7611028cf94fef06f75ec67b5623380f9073eca8b970f607a72a
    cited_regions:
    - audit
  checked_sources:
  - model-143-moonshot-kimi-k2-6
  - model-143-kimi-k2-6-guide
  - model-143-kimi-k3-guide
  - model-143-kimi-k2-6-license
  - model-143-hf-metadata-moonshot-kimi-k2-6
- facet: feature.streaming
  value: true
  state: known
  sources:
  - source_id: model-143-moonshot-kimi-k2-6
    snapshot_ref: sha256:95db3be1d0473e482c7aa901f237ad7af8bb7929625a777b27428081bb8ea9f7
    cited_regions:
    - model-spec
  - source_id: model-143-kimi-k2-6-guide
    snapshot_ref: sha256:3d5a698cf776fcbe743fc02d2335e23f45dbb9a2c5fbba66195a4b1c861bc275
    cited_regions:
    - audit
  - source_id: model-143-kimi-k3-guide
    snapshot_ref: sha256:2d5f971cdba4f6e36d021746ff9511f9323e4a66c27e30ac3c3ea6a10b36d96f
    cited_regions:
    - audit
- id: moonshot/kimi-k2-6#model.fits_hardware
  subject:
    kind: model
    id: moonshot/kimi-k2-6
  facet: model.fits_hardware
  value: []
  state: known
  derivation:
    method: decision.hardware.compute_fit@1
    formula: parameters_total * bytes_per_parameter <= memory_capacity_gb * (1 - working_allowance) *
      1e9
    inputs:
      weights_openness: open_weights
      parameters_total: 1026879376368
      working_allowance: 0.25
      quant_bytes: '{''bf16'': 2.0, ''fp16'': 2.0, ''fp8'': 1.0, ''int4'': 0.5, ''int8'': 1.0, ''q4'':
        0.5, ''q5'': 0.625, ''q6'': 0.75}'
      has_device_unknowns: 'true'
      model_snapshot_ref: sha256:4907614de6010e874bcd100c0f32d4c120c080941a4dca5294bbfeb976a37654
      hardware_registry_sha256: sha256:10baf5e1ce9e5a1e5b970f4fdc25d9f67db8c562c8c109157ae9722bf6357bff
      hardware_device_count: 64
  sources:
  - source_id: model-174-moonshot-kimi-k2-6-hardware-input
    snapshot_ref: sha256:4907614de6010e874bcd100c0f32d4c120c080941a4dca5294bbfeb976a37654
    cited_regions:
    - rows
- id: moonshot/kimi-k2-6#model.parameters_total
  subject:
    kind: model
    id: moonshot/kimi-k2-6
  facet: model.parameters_total
  value: 1026879376368
  state: known
  sources:
  - source_id: model-174-moonshot-kimi-k2-6-hardware-input
    snapshot_ref: sha256:4907614de6010e874bcd100c0f32d4c120c080941a4dca5294bbfeb976a37654
    cited_regions:
    - rows
- id: moonshot/kimi-k2-6#model.hardware_fit_indeterminate
  subject:
    kind: model
    id: moonshot/kimi-k2-6
  facet: model.hardware_fit_indeterminate
  value:
  - cerebras_wse3
  - nvidia_vera_rubin_superchip
  state: known
  sources:
  - source_id: model-174-moonshot-kimi-k2-6-hardware-input
    snapshot_ref: sha256:4907614de6010e874bcd100c0f32d4c120c080941a4dca5294bbfeb976a37654
    cited_regions:
    - rows
  derivation:
    method: decision.hardware.compute_fit@1
    formula: parameters_total * bytes_per_parameter <= memory_capacity_gb * (1 - working_allowance) *
      1e9
    inputs:
      weights_openness: open_weights
      parameters_total: 1026879376368
      working_allowance: 0.25
      quant_bytes: '{''bf16'': 2.0, ''fp16'': 2.0, ''fp8'': 1.0, ''int4'': 0.5, ''int8'': 1.0, ''q4'':
        0.5, ''q5'': 0.625, ''q6'': 0.75}'
      has_device_unknowns: 'true'
      model_snapshot_ref: sha256:4907614de6010e874bcd100c0f32d4c120c080941a4dca5294bbfeb976a37654
      hardware_registry_sha256: sha256:10baf5e1ce9e5a1e5b970f4fdc25d9f67db8c562c8c109157ae9722bf6357bff
      hardware_device_count: 64
card_schema_version: '3.0'
card_author: models.dev-seeder
card_created: '2026-04-05'
card_updated: '2026-09-28'
---

# Kimi K2.6

Kimi K2.6 is a Llm Reasoning model from Moonshot AI. Part of the kimi-k2 family. Knowledge cutoff: 2025-01.

## Key Features
- Extended reasoning / chain-of-thought
- Function calling / tool use
- Structured output (JSON mode)
- Open weights
- File/image attachments
