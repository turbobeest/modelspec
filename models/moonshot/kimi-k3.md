---
model_id: moonshot/kimi-k3
display_name: Kimi K3
provider: moonshot
provider_display: Moonshot AI
family: kimi-k3
version: kimi-k3
release_date: '2026-07-16'
last_updated: '2026-07-16'
status: active
model_type: llm-reasoning
model_subtypes: []
tags: []
pipeline_tag: ''
architecture:
  type: null
  total_parameters: 2779931837184
  active_parameters: 104000000000
  num_experts: 896
  experts_per_token: null
  num_layers: 93
  hidden_size: 7168
  intermediate_size: 33792
  attention_type: null
  num_attention_heads: 96
  num_kv_heads: 96
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
    max_output_tokens: 131072
    context_window: 1048576
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
  input: 3.0
  output: 15.0
  reasoning: null
  cache_read: 0.3
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
    model_id: moonshotai/Kimi-K3
    url: https://huggingface.co/moonshotai/Kimi-K3
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
    model_id_as_evaluated: kimi-k3-max
    score: 1484.77
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / overall, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category overall,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1484.77 [1479.54, 1489.99], 20987 votes,
      rank 17.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: moonshot/kimi-k3#arena_elo_style_control#626b086a22fe
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:4d4c1c595c9a3713571168e832cea0f8e21a49fd8f94477e3abb7b8baacb7f15
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: arena_sc_coding
    model_id_as_evaluated: kimi-k3-max
    score: 1538.42
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / coding, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category coding,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1538.42 [1529.87, 1546.98], 5507 votes,
      rank 7.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: moonshot/kimi-k3#arena_sc_coding#306e8dc75662
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:caf9b5703109661b42968133e550f65fdb9ca50ab6e59ecdfc73c7e4de5c3c45
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: arena_sc_hard_prompts
    model_id_as_evaluated: kimi-k3-max
    score: 1514.14
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / hard_prompts, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category hard_prompts,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1514.14 [1508.05, 1520.22], 13581 votes,
      rank 10.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: moonshot/kimi-k3#arena_sc_hard_prompts#f1abfe13b40d
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:b60cf4b309d5fe3eea22cc125b7c98541ca2682e49fe92446a183fdfdd359e1a
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: arena_sc_math
    model_id_as_evaluated: kimi-k3-max
    score: 1500.64
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / math, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category math, leaderboard_publish_date
      2026-09-13; style control. Highest-effort row for the product (effort: max; MODEL-123
      max-effort rule). Rating 1500.64 [1480.75, 1520.53], 884 votes, rank 12.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: moonshot/kimi-k3#arena_sc_math#e187c3e088ce
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:76ca012bdf32035c92e141476e8bd45598be37d1dc3cf0cd193a0d0d7bf39bc7
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: arena_sc_creative_writing
    model_id_as_evaluated: kimi-k3-max
    score: 1458.44
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / creative_writing, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category creative_writing,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1458.44 [1448.44, 1468.45], 4133 votes,
      rank 27.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: moonshot/kimi-k3#arena_sc_creative_writing#a7ce6365092e
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:27802dee78bd4363dd42d3de0709a8cf4a45960f80ff269f6836775d716d4f0d
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: arena_sc_instruction_following
    model_id_as_evaluated: kimi-k3-max
    score: 1483.73
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / instruction_following, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category instruction_following,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1483.73 [1475.99, 1491.46], 6985 votes,
      rank 13.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: moonshot/kimi-k3#arena_sc_instruction_following#7b194e0492e1
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:eca177df4c1a744108f181021aae3ee8d548db755cc2dc8891596b4d2d15a0bc
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: arena_sc_multi_turn
    model_id_as_evaluated: kimi-k3-max
    score: 1496.04
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / multi_turn, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category multi_turn,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1496.04 [1485.22, 1506.86], 3311 votes,
      rank 13.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: moonshot/kimi-k3#arena_sc_multi_turn#4be8dc4891c9
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:31eb4f266a0d465ac673b6c33be1c98d795615cd1960e6163ce9472551776753
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: arena_sc_expert
    model_id_as_evaluated: kimi-k3-max
    score: 1526.92
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / expert, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category expert,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1526.92 [1512.88, 1540.97], 1863 votes,
      rank 10.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: moonshot/kimi-k3#arena_sc_expert#947736537901
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:d497c617fc2671535d33a52174292877141c74068860d2fe84c591c29ba94abd
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: arena_sc_longer_query
    model_id_as_evaluated: kimi-k3-max
    score: 1500.43
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / longer_query, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category longer_query,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1500.43 [1493.18, 1507.68], 9244 votes,
      rank 12.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: moonshot/kimi-k3#arena_sc_longer_query#f032a65ed6bd
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:71b1528ba70059de51741aaa3a3ec90376bcb6bc022d50bb258a83a8e21f44fe
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: arena_sc_non_english
    model_id_as_evaluated: kimi-k3-max
    score: 1472.23
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / non_english, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category non_english,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1472.23 [1466.06, 1478.40], 12798 votes,
      rank 19.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: moonshot/kimi-k3#arena_sc_non_english#d9c7bf733912
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:ea6db786e7b1ae0c912da2c758b6b58b1a6b78db9fd514304a9815b2935bd273
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: arena_sc_medicine
    model_id_as_evaluated: kimi-k3-max
    score: 1506.37
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / industry_medicine_and_healthcare, latest split,
      revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category industry_medicine_and_healthcare,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1506.37 [1490.13, 1522.61], 1415 votes,
      rank 9.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: moonshot/kimi-k3#arena_sc_medicine#30502cc52421
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:83f0847e4fad478a6144928aa94f30b93113108e6dcedc354f8432ed6a24e4d3
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: arena_sc_legal
    model_id_as_evaluated: kimi-k3-max
    score: 1507.83
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / industry_legal_and_government, latest split, revision
      1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category industry_legal_and_government,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1507.83 [1492.75, 1522.90], 1682 votes,
      rank 7.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: moonshot/kimi-k3#arena_sc_legal#178335086307
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:2d62891fc7f2899c9042be725561d35beb09d558df6b897ce100816712845463
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: arena_sc_business
    model_id_as_evaluated: kimi-k3-max
    score: 1486.36
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / industry_business_and_management_and_financial_operations,
      latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category industry_business_and_management_and_financial_operations,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1486.36 [1476.66, 1496.05], 4119 votes,
      rank 16.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: moonshot/kimi-k3#arena_sc_business#e573ae0000af
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:634bebae98b7eba8bc18d48c958512d1207fe6d9266228500e0431f43e5681f5
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: arena_sc_science
    model_id_as_evaluated: kimi-k3-max
    score: 1516.51
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / industry_life_and_physical_and_social_science, latest
      split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category industry_life_and_physical_and_social_science,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1516.51 [1505.82, 1527.20], 3255 votes,
      rank 7.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: moonshot/kimi-k3#arena_sc_science#647032bb63f0
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:e9cee91c44d7e948f729fdd89f6120fe9f03a7d1d53c2adbec436b11baf5cc52
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: arena_sc_writing
    model_id_as_evaluated: kimi-k3-max
    score: 1470.74
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / industry_writing_and_literature_and_language, latest
      split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category industry_writing_and_literature_and_language,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1470.74 [1462.04, 1479.43], 5445 votes,
      rank 22.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: moonshot/kimi-k3#arena_sc_writing#648b68c738ae
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:72c46a9fbaa925b94151093fc623120a948fb8d214b75210767c35041aab8d7d
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: arena_webdev
    model_id_as_evaluated: kimi-k3-max
    score: 1659.57
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-23'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: webdev / overall, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset webdev, category overall, leaderboard_publish_date
      2026-09-23; no style-controlled variant. Highest-effort row for the product (effort: max;
      MODEL-123 max-effort rule). Rating 1659.57 [1652.73, 1666.41], 13252 votes, rank 9.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: moonshot/kimi-k3#arena_webdev#d698922b83c5
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-143-evidence-arena-webdev-json
      snapshot_ref: sha256:087c77f0270a031a23a14024c7245d440783c2258f99f9b5cd756c9f30e54d27
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: gpqa_diamond
    model_id_as_evaluated: kimi-k3_max
    score: 93.12
    unit: percent
    source_url: https://epoch.ai/benchmarks/gpqa-diamond
    source_kind: independent_evaluator
    evidence_date: '2026-07-16'
    date_type: evaluated
    verified_at: '2026-09-28'
    benchmark_version: GPQA Diamond (Epoch AI run)
    configuration: Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (gpqa_diamond.csv),
      read 2026-09-24. Run started 2026-07-16T21:59:40.000Z; effort max; highest-effort run
      for the model (MODEL-123 max-effort rule), newest on a tie. Standard error 1.49 points.
    limitations: Epoch AI data, CC BY 4.0.
    id: moonshot/kimi-k3#gpqa_diamond#f91dd4efa0b8
    measured_by: independent_evaluator
    effort: max
    harness: null
    sources:
    - source_id: model-143-evidence-epoch-gpqa-diamond-csv
      snapshot_ref: sha256:a25a72a0e190ea7f53b8711a3793afd00492581a29c19c2a89c0e7fa19183f12
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: frontiermath_tiers_1_3_v2
    model_id_as_evaluated: kimi-k3_max
    score: 72.18
    unit: percent
    source_url: https://epoch.ai/frontiermath
    source_kind: independent_evaluator
    evidence_date: '2026-07-17'
    date_type: evaluated
    verified_at: '2026-09-28'
    benchmark_version: FrontierMath-Tiers-1-3-v2-Private (Epoch AI run)
    configuration: Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (frontiermath_tiers_1_3_v2.csv),
      read 2026-09-24. Run started 2026-07-17T01:48:42.000Z; effort max; highest-effort run
      for the model (MODEL-123 max-effort rule), newest on a tie. Standard error 2.66 points.
    limitations: Epoch AI data, CC BY 4.0.
    id: moonshot/kimi-k3#frontiermath_tiers_1_3_v2#68507244572b
    measured_by: independent_evaluator
    effort: max
    harness: null
    sources:
    - source_id: model-143-evidence-epoch-frontiermath-tiers-1-3-v2-csv
      snapshot_ref: sha256:a38d3375a77ff7cbb6aa8dbb75394839ac0303ff7cf41a8c80ef294bb06b9c93
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: simpleqa_verified
    model_id_as_evaluated: kimi-k3_max
    score: 50.6
    unit: percent
    source_url: https://epoch.ai/benchmarks/simpleqa-verified
    source_kind: independent_evaluator
    evidence_date: '2026-08-27'
    date_type: evaluated
    verified_at: '2026-09-28'
    benchmark_version: SimpleQA Verified, proportion correct, Epoch AI protocol with anti-abstention
      prompt
    configuration: Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (simpleqa_verified.csv),
      read 2026-09-24. Run started 2026-08-27T19:36:12.000Z; effort max; highest-effort run
      for the model (MODEL-123 max-effort rule), newest on a tie. Standard error 1.58 points.
    limitations: Epoch AI data, CC BY 4.0.
    id: moonshot/kimi-k3#simpleqa_verified#a38e8a324525
    measured_by: independent_evaluator
    effort: max
    harness: null
    sources:
    - source_id: model-160-epoch-simpleqa-verified-csv
      snapshot_ref: sha256:1f18c84606f93b761f4bffcfe1f688b4f4bd7d0d26ef1bcfa2486126c4fb123e
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: frontiercode_v1_1
    model_id_as_evaluated: Kimi K3
    score: 44.2
    unit: percent
    source_url: https://cognition.com/frontiercode
    source_kind: benchmark_author
    evidence_date: '2026-09-25'
    date_type: evaluated
    verified_at: '2026-09-28'
    benchmark_version: FrontierCode 1.1, main score (Mean@5)
    configuration: Board row as copied in Epoch AI's benchmark data (frontiercode_external.csv,
      https://epoch.ai/data/benchmark_data.zip), read 2026-09-24. Effort none; the highest-effort
      row for the model (MODEL-123 max-effort rule). Harness mini-swe-agent.
    limitations: A live board's standing, dated by the day ModelSpec read Epoch AI's copy; the
      copy carries no per-row date. Epoch AI data, CC BY 4.0.
    id: moonshot/kimi-k3#frontiercode_v1_1#f63b6831f269
    measured_by: benchmark_author
    effort: null
    harness: null
    sources:
    - source_id: model-160-frontiercode
      snapshot_ref: sha256:e79cf2ff877616fcfc04b43354775a89f8285b017f38151f4cfad91d165146f3
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: vending_bench_2
    model_id_as_evaluated: Kimi K3 (Moonshot)
    score: 5165.04
    unit: USD
    source_url: https://andonlabs.com/evals/vending-bench-2
    source_kind: benchmark_author
    evidence_date: '2026-09-25'
    date_type: evaluated
    verified_at: '2026-09-28'
    benchmark_version: Vending-Bench 2, mean final balance over 5 runs
    configuration: Board row as copied in Epoch AI's benchmark data (vending_bench_2_external.csv,
      https://epoch.ai/data/benchmark_data.zip), read 2026-09-24. Effort unknown; the highest-effort
      row for the model (MODEL-123 max-effort rule).
    limitations: A live board's standing, dated by the day ModelSpec read Epoch AI's copy; the
      copy carries no per-row date. Epoch AI data, CC BY 4.0.
    id: moonshot/kimi-k3#vending_bench_2#d0a01806a09d
    measured_by: benchmark_author
    effort: null
    harness: null
    sources:
    - source_id: model-160-vending-bench-2
      snapshot_ref: sha256:8724ee26281bff37eb4fe6af19bda2406b8d5fccdd4d54fdbfc44248b32ef12b
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: deepswe_v1_1
    model_id_as_evaluated: kimi-k3 (max)
    score: 68.51
    unit: percent
    source_url: https://deepswe.datacurve.ai/
    source_kind: benchmark_author
    evidence_date: '2026-09-25'
    date_type: evaluated
    verified_at: '2026-09-28'
    benchmark_version: DeepSWE v1.1, pass@1, mini-swe-agent
    configuration: Board row as copied in Epoch AI's benchmark data (deepswe_external.csv, https://epoch.ai/data/benchmark_data.zip),
      read 2026-09-24. Effort max; the highest-effort row for the model (MODEL-123 max-effort
      rule). Harness mini-swe-agent.
    limitations: A live board's standing, dated by the day ModelSpec read Epoch AI's copy; the
      copy carries no per-row date. Epoch AI data, CC BY 4.0.
    id: moonshot/kimi-k3#deepswe_v1_1#2a2bf0c4b1e5
    measured_by: benchmark_author
    effort: max
    harness: unregistered
    sources:
    - source_id: model-160-deepswe-v1-1
      snapshot_ref: sha256:64010fde30846107b5210ba17347a269780973bf71eb8ce9c1d316a353733156
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: aime_2026
    model_id_as_evaluated: Kimi K3 (Think)
    score: 96.67
    unit: percent
    source_url: https://matharena.ai/competition_tables/aime--aime_2026
    source_kind: independent_evaluator
    evidence_date: '2026-09-26'
    date_type: evaluated
    verified_at: '2026-09-28'
    benchmark_version: AIME 2026, MathArena final-answer table
    configuration: MathArena competition table read 2026-09-26; the table states no run
      date, so the reading is dated by the observation. Effort thinking; highest-effort
      row for the model. MathArena lists final-answer competitions as deprecated.
    limitations: 'MathArena marks this row: model was released after competition release, so
      contamination is possible.'
    id: moonshot/kimi-k3#aime_2026#653197fd9de9
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-matharena-aime-2026
      snapshot_ref: sha256:af6ab2f2d086514b45f4a2a12858238247ddb81633a0992c73da928ac806f1c8
      cited_regions:
      - rows
    quality_flags:
    - deprecated
    - contamination_warning
    observed_at: '2026-09-28'
  - benchmark_id: tau3_banking
    model_id_as_evaluated: Kimi K3 (max)
    score: 37.11
    unit: percent
    source_url: https://sierra-tau-bench-public.s3.us-west-2.amazonaws.com/submissions/kimi-k3_sierra_2026-08-04/submission.json
    source_kind: benchmark_author
    evidence_date: '2026-07-24'
    date_type: evaluated
    verified_at: '2026-09-28'
    benchmark_version: τ-Knowledge τ-Banking (banking_knowledge), pass^1
    configuration: τ-bench leaderboard submission kimi-k3_sierra_2026-08-04, submitted by Sierra;
      retrieval config alltools; reasoning effort max; user simulator gpt-5.2; tau2-bench 1.0.1.
      pass^4 17.525773195876287.
    limitations: Banking_knowledge evaluation with AllTools retrieval, GPT-5.2 low-reasoning
      user simulation, four trials, and seed 300.
    id: moonshot/kimi-k3#tau3_banking#f6ca45252a49
    measured_by: benchmark_author
    effort: max
    harness: null
    sources:
    - source_id: model-160-tau-bench-kimi-k3-sierra-2026-08-04
      snapshot_ref: sha256:953240d6d6d641a76c2379a26afd455180d7fd8dbe9d506cf952255eef1b14d7
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: arena_sc_english
    model_id_as_evaluated: kimi-k3-max
    score: 1493.42
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / english, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1493.42 [1486.26,
      1500.58], 8182 votes, rank 12. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:c10623c0b42bc927b984d3933d31aa31c3cd1c21841797328e80981e6d334892
      cited_regions:
      - rows
    id: moonshot/kimi-k3#arena_sc_english#705d451eec3c
  - benchmark_id: arena_sc_chinese
    model_id_as_evaluated: kimi-k3-max
    score: 1534.52
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / chinese, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1534.52 [1518.15,
      1550.89], 1386 votes, rank 14. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:1e2f3fa3120aa6532923deddea1fcb48e14b14f7e2f3396e16e17304594752bd
      cited_regions:
      - rows
    id: moonshot/kimi-k3#arena_sc_chinese#4c54e41c259c
  - benchmark_id: arena_sc_japanese
    model_id_as_evaluated: kimi-k3-max
    score: 1510.67
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / japanese, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1510.67 [1478.33,
      1543.02], 373 votes, rank 2. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:c9ec43cc46cde9a9a084781e014b590ecb91e24ff239d072e5e3e1fbe299075a
      cited_regions:
      - rows
    id: moonshot/kimi-k3#arena_sc_japanese#22da9db1954f
  - benchmark_id: arena_sc_korean
    model_id_as_evaluated: kimi-k3-max
    score: 1480.27
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / korean, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1480.27 [1453.56,
      1506.99], 483 votes, rank 5. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:da67028715236f4510ef6cd2b29aa4a819e6b581fd48575bbee287a0a72545fa
      cited_regions:
      - rows
    id: moonshot/kimi-k3#arena_sc_korean#402497564763
  - benchmark_id: arena_sc_russian
    model_id_as_evaluated: kimi-k3-max
    score: 1487.07
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / russian, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1487.07 [1474.47,
      1499.66], 2341 votes, rank 23. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:3d6ede20ed72833ccae1f56c86762a83c811d6fcb89f7960178d516bbb50aa8d
      cited_regions:
      - rows
    id: moonshot/kimi-k3#arena_sc_russian#974fa1d5cb10
  - benchmark_id: arena_sc_spanish
    model_id_as_evaluated: kimi-k3-max
    score: 1486.3
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / spanish, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1486.30 [1462.87,
      1509.73], 633 votes, rank 9. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:626c233148bb4156f80113d49c8163082ed947cbfb64e20739771d4fe07b33f1
      cited_regions:
      - rows
    id: moonshot/kimi-k3#arena_sc_spanish#34ee0d3d39a7
  - benchmark_id: arena_sc_german
    model_id_as_evaluated: kimi-k3-max
    score: 1476.33
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / german, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1476.33 [1446.68,
      1505.98], 413 votes, rank 26. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:6074611b99cf8732f4dee1ad2a5718683b7a9ca7fdff6588d35ba1863ea5f8ac
      cited_regions:
      - rows
    id: moonshot/kimi-k3#arena_sc_german#a487fc2a5ca1
  - benchmark_id: arena_sc_french
    model_id_as_evaluated: kimi-k3-max
    score: 1504.93
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / french, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1504.93 [1482.65,
      1527.21], 765 votes, rank 17. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:26b468ee0d48430ff995f4feb0483b5c391cb383a59ea1755a4e91eeb0f6a8f2
      cited_regions:
      - rows
    id: moonshot/kimi-k3#arena_sc_french#5362c5998ab6
  - benchmark_id: arena_sc_polish
    model_id_as_evaluated: kimi-k3-max
    score: 1497.99
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / polish, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1497.99 [1467.73,
      1528.24], 343 votes, rank 10. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:1d2df11d9abaf322e77c330fab6d5e5ef26979c835443f67601b6c89b8f3f299
      cited_regions:
      - rows
    id: moonshot/kimi-k3#arena_sc_polish#cd6782ed274a
  - benchmark_id: arena_sc_industry_software_it_services
    model_id_as_evaluated: kimi-k3-max
    score: 1525.13
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / industry_software_and_it_services, latest split, revision
      1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1525.13 [1517.92,
      1532.34], 8252 votes, rank 9. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:4538dd5bcb06397043fc55c64535410a284e7da8668e8c13cc2950c6f1baa37c
      cited_regions:
      - rows
    id: moonshot/kimi-k3#arena_sc_industry_software_it_services#19244e0abde6
  - benchmark_id: arena_sc_industry_entertainment_sports_media
    model_id_as_evaluated: kimi-k3-max
    score: 1452.51
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / industry_entertainment_and_sports_and_media, latest
      split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1452.51 [1443.43,
      1461.59], 5076 votes, rank 29. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:89233e13dec450388587fa44e3af9cfb82da53034e616b951c1cbe809b0c4cef
      cited_regions:
      - rows
    id: moonshot/kimi-k3#arena_sc_industry_entertainment_sports_media#ae61f76047f7
  - benchmark_id: arena_sc_industry_mathematical
    model_id_as_evaluated: kimi-k3-max
    score: 1504.54
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / industry_mathematical, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1504.54 [1485.99,
      1523.09], 1054 votes, rank 15. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:514a2f81b6bce9bc34481c6e0d7af71184302842a4f5b8284657dc5024965f25
      cited_regions:
      - rows
    id: moonshot/kimi-k3#arena_sc_industry_mathematical#74e502d7acfd
  - benchmark_id: arena_sc_factuality
    model_id_as_evaluated: kimi-k3-max
    score: 1470.4
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_factuality / overall, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1470.40 [1466.24,
      1474.56], 20843 votes, rank 24. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-factuality
      snapshot_ref: sha256:359d85539a6e849ffbfe46427efdefadb4be9c907f9fbea9f799ce7bbf6c52c2
      cited_regions:
      - rows
    id: moonshot/kimi-k3#arena_sc_factuality#d49835a7c80d
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
  - source_id: model-143-moonshot-kimi-k3
    snapshot_ref: sha256:57de265b5842dfa465c6e73b368b0e15a89b8793b5450528dad577da202cc6fe
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
  - source_id: model-143-moonshot-kimi-k3
    snapshot_ref: sha256:57de265b5842dfa465c6e73b368b0e15a89b8793b5450528dad577da202cc6fe
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
  - source_id: model-143-moonshot-kimi-k3
    snapshot_ref: sha256:57de265b5842dfa465c6e73b368b0e15a89b8793b5450528dad577da202cc6fe
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
  value: 1048576
  state: known
  sources:
  - source_id: model-143-moonshot-kimi-k3
    snapshot_ref: sha256:57de265b5842dfa465c6e73b368b0e15a89b8793b5450528dad577da202cc6fe
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
  value: 131072
  state: known
  sources:
  - source_id: model-143-moonshot-kimi-k3
    snapshot_ref: sha256:57de265b5842dfa465c6e73b368b0e15a89b8793b5450528dad577da202cc6fe
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
  - source_id: model-143-moonshot-kimi-k3
    snapshot_ref: sha256:57de265b5842dfa465c6e73b368b0e15a89b8793b5450528dad577da202cc6fe
    cited_regions:
    - model-spec
  - source_id: model-143-hf-metadata-moonshot-kimi-k3
    snapshot_ref: sha256:ef531848d7ea9fef27f5adafff654378067b97e7d8753230deb054058c8e6449
    cited_regions:
    - audit
  - source_id: model-143-kimi-k3-license
    snapshot_ref: sha256:20c797ce19af0c17de52c6afb144644768a591c521655f5ebf5712c9850f2887
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
  - source_id: model-143-moonshot-kimi-k3
    snapshot_ref: sha256:57de265b5842dfa465c6e73b368b0e15a89b8793b5450528dad577da202cc6fe
    cited_regions:
    - model-spec
  - source_id: model-143-kimi-k3-license
    snapshot_ref: sha256:20c797ce19af0c17de52c6afb144644768a591c521655f5ebf5712c9850f2887
    cited_regions:
    - audit
- facet: licence.user_cap
  value: unbounded
  state: known
  sources:
  - source_id: model-143-moonshot-kimi-k3
    snapshot_ref: sha256:57de265b5842dfa465c6e73b368b0e15a89b8793b5450528dad577da202cc6fe
    cited_regions:
    - model-spec
  - source_id: model-143-kimi-k3-license
    snapshot_ref: sha256:20c797ce19af0c17de52c6afb144644768a591c521655f5ebf5712c9850f2887
    cited_regions:
    - audit
- facet: licence.output_training
  value: permitted
  state: known
  sources:
  - source_id: model-143-moonshot-kimi-k3
    snapshot_ref: sha256:57de265b5842dfa465c6e73b368b0e15a89b8793b5450528dad577da202cc6fe
    cited_regions:
    - model-spec
  - source_id: model-143-kimi-k3-license
    snapshot_ref: sha256:20c797ce19af0c17de52c6afb144644768a591c521655f5ebf5712c9850f2887
    cited_regions:
    - audit
- facet: licence.fine_tuning
  value: permitted_with_conditions
  state: known
  sources:
  - source_id: model-143-moonshot-kimi-k3
    snapshot_ref: sha256:57de265b5842dfa465c6e73b368b0e15a89b8793b5450528dad577da202cc6fe
    cited_regions:
    - model-spec
  - source_id: model-143-kimi-k3-license
    snapshot_ref: sha256:20c797ce19af0c17de52c6afb144644768a591c521655f5ebf5712c9850f2887
    cited_regions:
    - audit
- facet: origin.lab_jurisdiction
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-moonshot-kimi-k3
    snapshot_ref: sha256:57de265b5842dfa465c6e73b368b0e15a89b8793b5450528dad577da202cc6fe
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
  - source_id: model-143-kimi-k3-license
    snapshot_ref: sha256:20c797ce19af0c17de52c6afb144644768a591c521655f5ebf5712c9850f2887
    cited_regions:
    - audit
  - source_id: model-143-hf-metadata-moonshot-kimi-k3
    snapshot_ref: sha256:ef531848d7ea9fef27f5adafff654378067b97e7d8753230deb054058c8e6449
    cited_regions:
    - audit
  checked_sources:
  - model-143-moonshot-kimi-k3
  - model-143-kimi-k2-6-guide
  - model-143-kimi-k3-guide
  - model-143-kimi-k3-license
  - model-143-hf-metadata-moonshot-kimi-k3
- facet: origin.base_lineage
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-moonshot-kimi-k3
    snapshot_ref: sha256:57de265b5842dfa465c6e73b368b0e15a89b8793b5450528dad577da202cc6fe
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
  - source_id: model-143-kimi-k3-license
    snapshot_ref: sha256:20c797ce19af0c17de52c6afb144644768a591c521655f5ebf5712c9850f2887
    cited_regions:
    - audit
  - source_id: model-143-hf-metadata-moonshot-kimi-k3
    snapshot_ref: sha256:ef531848d7ea9fef27f5adafff654378067b97e7d8753230deb054058c8e6449
    cited_regions:
    - audit
  checked_sources:
  - model-143-moonshot-kimi-k3
  - model-143-kimi-k2-6-guide
  - model-143-kimi-k3-guide
  - model-143-kimi-k3-license
  - model-143-hf-metadata-moonshot-kimi-k3
- facet: origin.weights_hosting
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-moonshot-kimi-k3
    snapshot_ref: sha256:57de265b5842dfa465c6e73b368b0e15a89b8793b5450528dad577da202cc6fe
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
  - source_id: model-143-kimi-k3-license
    snapshot_ref: sha256:20c797ce19af0c17de52c6afb144644768a591c521655f5ebf5712c9850f2887
    cited_regions:
    - audit
  - source_id: model-143-hf-metadata-moonshot-kimi-k3
    snapshot_ref: sha256:ef531848d7ea9fef27f5adafff654378067b97e7d8753230deb054058c8e6449
    cited_regions:
    - audit
  checked_sources:
  - model-143-moonshot-kimi-k3
  - model-143-kimi-k2-6-guide
  - model-143-kimi-k3-guide
  - model-143-kimi-k3-license
  - model-143-hf-metadata-moonshot-kimi-k3
- facet: model.release_date
  value: '2026-07-16'
  state: known
  sources:
  - source_id: model-143-moonshot-kimi-k3
    snapshot_ref: sha256:57de265b5842dfa465c6e73b368b0e15a89b8793b5450528dad577da202cc6fe
    cited_regions:
    - model-spec
  - source_id: model-143-hf-metadata-moonshot-kimi-k3
    snapshot_ref: sha256:ef531848d7ea9fef27f5adafff654378067b97e7d8753230deb054058c8e6449
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
  - source_id: model-143-moonshot-kimi-k3
    snapshot_ref: sha256:57de265b5842dfa465c6e73b368b0e15a89b8793b5450528dad577da202cc6fe
    cited_regions:
    - model-spec
  - source_id: model-143-hf-metadata-moonshot-kimi-k3
    snapshot_ref: sha256:ef531848d7ea9fef27f5adafff654378067b97e7d8753230deb054058c8e6449
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
  - source_id: model-143-moonshot-kimi-k3
    snapshot_ref: sha256:57de265b5842dfa465c6e73b368b0e15a89b8793b5450528dad577da202cc6fe
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
  - source_id: model-143-moonshot-kimi-k3
    snapshot_ref: sha256:57de265b5842dfa465c6e73b368b0e15a89b8793b5450528dad577da202cc6fe
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
  - source_id: model-143-moonshot-kimi-k3
    snapshot_ref: sha256:57de265b5842dfa465c6e73b368b0e15a89b8793b5450528dad577da202cc6fe
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
  - source_id: model-143-moonshot-kimi-k3
    snapshot_ref: sha256:57de265b5842dfa465c6e73b368b0e15a89b8793b5450528dad577da202cc6fe
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
  - source_id: model-143-kimi-k3-license
    snapshot_ref: sha256:20c797ce19af0c17de52c6afb144644768a591c521655f5ebf5712c9850f2887
    cited_regions:
    - audit
  - source_id: model-143-hf-metadata-moonshot-kimi-k3
    snapshot_ref: sha256:ef531848d7ea9fef27f5adafff654378067b97e7d8753230deb054058c8e6449
    cited_regions:
    - audit
  checked_sources:
  - model-143-moonshot-kimi-k3
  - model-143-kimi-k2-6-guide
  - model-143-kimi-k3-guide
  - model-143-kimi-k3-license
  - model-143-hf-metadata-moonshot-kimi-k3
- facet: feature.streaming
  value: true
  state: known
  sources:
  - source_id: model-143-moonshot-kimi-k3
    snapshot_ref: sha256:57de265b5842dfa465c6e73b368b0e15a89b8793b5450528dad577da202cc6fe
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
- id: moonshot/kimi-k3#model.parameters_total
  subject:
    kind: model
    id: moonshot/kimi-k3
  facet: model.parameters_total
  value: 2779931837184
  state: known
  sources:
  - source_id: model-161-kimi-k3-rtx-4090-fit
    snapshot_ref: sha256:9ca75a16dfd64b9af44ca339ba4be8fe66e9eed1466808c9a8e9560fdb859111
    cited_regions:
    - rows
- id: moonshot/kimi-k3#model.fits_hardware
  subject:
    kind: model
    id: moonshot/kimi-k3
  facet: model.fits_hardware
  value: []
  state: known
  sources:
  - source_id: model-161-kimi-k3-rtx-4090-fit
    snapshot_ref: sha256:9ca75a16dfd64b9af44ca339ba4be8fe66e9eed1466808c9a8e9560fdb859111
    cited_regions:
    - rows
  - source_id: model-161-nvidia-rtx-4090-memory
    snapshot_ref: sha256:282762d1ab30d41edb243674a4e9ad07b1b8a5cf9401e34c2ca44c62374361ba
    cited_regions:
    - rows
card_schema_version: '3.0'
card_author: models.dev-seeder
card_created: '2026-04-05'
card_updated: '2026-09-26'
---

# Kimi K3

Kimi K3 is a Llm Reasoning model from Moonshot AI. Part of the kimi-k3 family.

## Key Features
- Extended reasoning / chain-of-thought
- Function calling / tool use
- Structured output (JSON mode)
- Open weights
- File/image attachments
