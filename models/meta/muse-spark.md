---
model_id: meta/muse-spark
display_name: Muse Spark
provider: meta
provider_display: Meta
family: muse
version: spark
release_date: '2026-04-08'
last_updated: '2026-04-08'
status: active
model_type: llm-reasoning
model_subtypes:
- vlm
tags:
- text-generation
pipeline_tag: text-generation
architecture:
  type: null
  total_parameters: 68976653312
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
  open_weights: false
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
  origin_country: US
  origin_org_type: private
modalities:
  input:
  - text
  - image
  - audio
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
    supported: true
    ocr: true
    chart_reading: true
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
    agentic_coding: true
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
    overall: tier-1
    mathematical: true
    logical: true
    scientific: true
    planning: true
    multi_step: true
    chain_of_thought: true
    self_correction: true
    spatial: false
    temporal: false
    causal: true
    think_budget_control: true
  tool_use:
    overall: tier-1
    function_calling: true
    mcp_compatible: false
    parallel_tool_calls: true
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
    available: false
    model_id: ''
    url: https://huggingface.co/
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
    arc_agi_2: 42.5
    charxiv_reasoning: 86.4
    deepsearchqa: 74.8
    healthbench_hard: 42.8
    ipho_2025_theory: 82.6
    frontierscience_research: 38.3
    medxpertqa_multimodal: 78.4
    terminal_bench_2: 59.0
    zerobench: 33.0
  benchmark_source: meta-blog, officechai
  benchmark_as_of: 2026-04
  evidence:
  - benchmark_id: arena_elo_style_control
    model_id_as_evaluated: muse-spark
    score: 1488.05
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / overall, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category overall,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1488.05 [1482.21, 1493.90], 13565
      votes, rank 13.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: meta/muse-spark#arena_elo_style_control#859002e19068
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
    model_id_as_evaluated: muse-spark
    score: 1525.75
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / coding, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category coding,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1525.75 [1515.63, 1535.87], 3771
      votes, rank 19.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: meta/muse-spark#arena_sc_coding#e5ebb1052b6c
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
    model_id_as_evaluated: muse-spark
    score: 1504.78
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / hard_prompts, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category hard_prompts,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1504.78 [1497.78, 1511.79], 8738
      votes, rank 19.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: meta/muse-spark#arena_sc_hard_prompts#f56b7e8510fc
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
    model_id_as_evaluated: muse-spark
    score: 1460.89
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / math, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category math, leaderboard_publish_date
      2026-09-13; style control. Highest-effort row for the product (effort: default; MODEL-123
      max-effort rule). Rating 1460.89 [1440.98, 1480.81], 857 votes, rank 54.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: meta/muse-spark#arena_sc_math#97766f13c77e
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
    model_id_as_evaluated: muse-spark
    score: 1463.7
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / creative_writing, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category creative_writing,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1463.70 [1449.70, 1477.71], 1948
      votes, rank 20.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: meta/muse-spark#arena_sc_creative_writing#3ea45ace03b5
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
    model_id_as_evaluated: muse-spark
    score: 1463.34
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / instruction_following, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category instruction_following,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1463.34 [1454.11, 1472.56], 4494
      votes, rank 38.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: meta/muse-spark#arena_sc_instruction_following#dc8ae7251c12
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
    model_id_as_evaluated: muse-spark
    score: 1491.31
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / multi_turn, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category multi_turn,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1491.31 [1477.87, 1504.75], 2179
      votes, rank 21.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: meta/muse-spark#arena_sc_multi_turn#900d2292a53b
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
    model_id_as_evaluated: muse-spark
    score: 1489.93
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / expert, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category expert,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1489.93 [1473.26, 1506.59], 1293
      votes, rank 46.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: meta/muse-spark#arena_sc_expert#a81c6018ff5c
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
    model_id_as_evaluated: muse-spark
    score: 1474.17
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / longer_query, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category longer_query,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1474.17 [1465.36, 1482.97], 5308
      votes, rank 47.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: meta/muse-spark#arena_sc_longer_query#e736ae7981c1
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
    model_id_as_evaluated: muse-spark
    score: 1476.71
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / non_english, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category non_english,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1476.71 [1469.15, 1484.27], 7097
      votes, rank 16.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: meta/muse-spark#arena_sc_non_english#a941f93d1146
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
    model_id_as_evaluated: muse-spark
    score: 1503.55
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
      (effort: default; MODEL-123 max-effort rule). Rating 1503.55 [1483.77, 1523.33], 954 votes,
      rank 11.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: meta/muse-spark#arena_sc_medicine#c720d914208c
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
    model_id_as_evaluated: muse-spark
    score: 1503.34
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
      (effort: default; MODEL-123 max-effort rule). Rating 1503.34 [1483.68, 1522.99], 973 votes,
      rank 10.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: meta/muse-spark#arena_sc_legal#12cf6c7d4dc8
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
    model_id_as_evaluated: muse-spark
    score: 1489.64
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
      (effort: default; MODEL-123 max-effort rule). Rating 1489.64 [1477.82, 1501.45], 2743
      votes, rank 12.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: meta/muse-spark#arena_sc_business#285dcb841a13
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
    model_id_as_evaluated: muse-spark
    score: 1497.12
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
      (effort: default; MODEL-123 max-effort rule). Rating 1497.12 [1484.28, 1509.96], 2264
      votes, rank 24.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: meta/muse-spark#arena_sc_science#33b63e334473
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
    model_id_as_evaluated: muse-spark
    score: 1459.84
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
      (effort: default; MODEL-123 max-effort rule). Rating 1459.84 [1448.84, 1470.83], 3130
      votes, rank 33.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: meta/muse-spark#arena_sc_writing#2cdd625f9c45
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:72c46a9fbaa925b94151093fc623120a948fb8d214b75210767c35041aab8d7d
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: arena_sc_vision
    model_id_as_evaluated: muse-spark
    score: 1293.68
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: vision_style_control / overall, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset vision_style_control, category overall,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1293.68 [1284.32, 1303.04], 5572
      votes, rank 7.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: meta/muse-spark#arena_sc_vision#82779fe1e1c1
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-vision-style-control
      snapshot_ref: sha256:693bb5beed49b4a7d42c9a96f9478ac70d74903bc6be5b38767e2f6b0d69fe7f
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: gpqa_diamond
    model_id_as_evaluated: muse-spark
    score: 89.8
    unit: percent
    source_url: https://epoch.ai/benchmarks/gpqa-diamond
    source_kind: independent_evaluator
    evidence_date: '2026-04-08'
    date_type: evaluated
    verified_at: '2026-09-28'
    benchmark_version: GPQA Diamond (Epoch AI run)
    configuration: Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (gpqa_diamond.csv),
      read 2026-09-24. Run started 2026-04-08T16:29:51.099Z; effort default; highest-effort
      run for the model (MODEL-123 max-effort rule), newest on a tie. Standard error 2.20 points.
    limitations: Epoch AI data, CC BY 4.0.
    id: meta/muse-spark#gpqa_diamond#2bc372676afe
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-143-evidence-epoch-gpqa-diamond-csv
      snapshot_ref: sha256:a25a72a0e190ea7f53b8711a3793afd00492581a29c19c2a89c0e7fa19183f12
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: hle
    model_id_as_evaluated: Muse Spark
    score: 40.56
    unit: percent
    source_url: https://labs.scale.com/leaderboard/humanitys_last_exam
    source_kind: independent_evaluator
    evidence_date: '2026-09-24'
    date_type: evaluated
    verified_at: '2026-09-28'
    benchmark_version: Humanity's Last Exam, Scale Labs leaderboard
    configuration: Scale Labs leaderboard entry read 2026-09-24; entry created 2026-04-08T16:57:23.000Z;
      effort default; ±1.92 (95% CI).
    limitations: 'Potential contamination warning: This model was evaluated after the public
      release of HLE, allowing model builder access to the prompts and solutions.'
    id: meta/muse-spark#hle#eb29f8f780ed
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-143-evidence-scale-hle-json
      snapshot_ref: sha256:08116925d8aa9277931ba1b4f0dde85a03de063b590d84b5ca76ce07c3e3e653
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: swe_bench_pro
    model_id_as_evaluated: Muse Spark*
    score: 55.0
    unit: percent
    source_url: https://labs.scale.com/leaderboard/swe_bench_pro_public
    source_kind: independent_evaluator
    evidence_date: '2026-04-08'
    date_type: evaluated
    verified_at: '2026-09-28'
    benchmark_version: SWE-Bench Pro, public dataset, Scale Labs leaderboard
    configuration: 'Scale Labs leaderboard entry read 2026-09-24; entry created 2026-04-08T17:04:49.000Z;
      effort default; ±3.6 (95% CI). Harness: mini-swe-agent (the board marks mini-swe-agent
      runs with an asterisk).'
    limitations: ''
    id: meta/muse-spark#swe_bench_pro#0ea81c2cbb4b
    measured_by: independent_evaluator
    effort: null
    harness: unregistered
    sources:
    - source_id: model-160-scale-swe-bench-pro-public
      snapshot_ref: sha256:27682f9d9581ddcc087df28d6400780b64742f9eb9eb0596542418b345387bf1
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: arena_sc_english
    model_id_as_evaluated: muse-spark
    score: 1495.49
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / english, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1495.49 [1487.71,
      1503.26], 6468 votes, rank 11. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:c10623c0b42bc927b984d3933d31aa31c3cd1c21841797328e80981e6d334892
      cited_regions:
      - rows
    id: meta/muse-spark#arena_sc_english#35d995ec9863
  - benchmark_id: arena_sc_chinese
    model_id_as_evaluated: muse-spark
    score: 1520.52
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / chinese, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1520.52 [1499.17,
      1541.86], 849 votes, rank 25. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:1e2f3fa3120aa6532923deddea1fcb48e14b14f7e2f3396e16e17304594752bd
      cited_regions:
      - rows
    id: meta/muse-spark#arena_sc_chinese#163a66e8d10e
  - benchmark_id: arena_sc_korean
    model_id_as_evaluated: muse-spark
    score: 1473.94
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / korean, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1473.94 [1434.54,
      1513.33], 248 votes, rank 8. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:da67028715236f4510ef6cd2b29aa4a819e6b581fd48575bbee287a0a72545fa
      cited_regions:
      - rows
    id: meta/muse-spark#arena_sc_korean#3a5a65564203
  - benchmark_id: arena_sc_russian
    model_id_as_evaluated: muse-spark
    score: 1481.46
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / russian, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1481.46 [1465.61,
      1497.32], 1468 votes, rank 28. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:3d6ede20ed72833ccae1f56c86762a83c811d6fcb89f7960178d516bbb50aa8d
      cited_regions:
      - rows
    id: meta/muse-spark#arena_sc_russian#89b619898d8f
  - benchmark_id: arena_sc_spanish
    model_id_as_evaluated: muse-spark
    score: 1480.99
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / spanish, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1480.99 [1453.69,
      1508.28], 500 votes, rank 11. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:626c233148bb4156f80113d49c8163082ed947cbfb64e20739771d4fe07b33f1
      cited_regions:
      - rows
    id: meta/muse-spark#arena_sc_spanish#44acbef2acd1
  - benchmark_id: arena_sc_german
    model_id_as_evaluated: muse-spark
    score: 1509.49
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / german, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1509.49 [1469.68,
      1549.29], 235 votes, rank 4. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:6074611b99cf8732f4dee1ad2a5718683b7a9ca7fdff6588d35ba1863ea5f8ac
      cited_regions:
      - rows
    id: meta/muse-spark#arena_sc_german#382c4f178378
  - benchmark_id: arena_sc_french
    model_id_as_evaluated: muse-spark
    score: 1525.65
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / french, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1525.65 [1496.81,
      1554.49], 470 votes, rank 2. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:26b468ee0d48430ff995f4feb0483b5c391cb383a59ea1755a4e91eeb0f6a8f2
      cited_regions:
      - rows
    id: meta/muse-spark#arena_sc_french#b7b549cc6dcc
  - benchmark_id: arena_sc_polish
    model_id_as_evaluated: muse-spark
    score: 1481.97
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / polish, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1481.97 [1448.63,
      1515.30], 310 votes, rank 22. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:1d2df11d9abaf322e77c330fab6d5e5ef26979c835443f67601b6c89b8f3f299
      cited_regions:
      - rows
    id: meta/muse-spark#arena_sc_polish#3304daf60b39
  - benchmark_id: arena_sc_vision_ocr
    model_id_as_evaluated: muse-spark
    score: 1301.8
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: vision_style_control / ocr, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1301.80 [1291.61,
      1311.99], 4009 votes, rank 11. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-vision-style-control
      snapshot_ref: sha256:99489a369ef55faf7aa620e6883cd433e47186123b5bf44b8343073a0f22fadf
      cited_regions:
      - rows
    id: meta/muse-spark#arena_sc_vision_ocr#29e22238bf38
  - benchmark_id: arena_sc_vision_diagram
    model_id_as_evaluated: muse-spark
    score: 1312.46
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: vision_style_control / diagram, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1312.46 [1296.81,
      1328.10], 1519 votes, rank 19. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-vision-style-control
      snapshot_ref: sha256:9bc8dfd6db75a6a49f2764592a2a096290158c27a7288ac98c8fdee2efa80bd2
      cited_regions:
      - rows
    id: meta/muse-spark#arena_sc_vision_diagram#b8b0cb724957
  - benchmark_id: arena_sc_vision_homework
    model_id_as_evaluated: muse-spark
    score: 1299.97
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: vision_style_control / homework, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1299.97 [1280.28,
      1319.66], 913 votes, rank 28. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-vision-style-control
      snapshot_ref: sha256:d55d1f7ffb986be7b796464f4c9b446aa3f66769bd4027b6e5a8394fe2ef1db0
      cited_regions:
      - rows
    id: meta/muse-spark#arena_sc_vision_homework#d7539cad61cb
  - benchmark_id: arena_sc_document
    model_id_as_evaluated: muse-spark
    score: 1444.19
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: document / overall, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1444.19 [1425.90,
      1462.48], 1084 votes, rank 29. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-document
      snapshot_ref: sha256:40f0c4aa079cc5d1dd633a2286b1bf63a24f2ee612d86330310020711b047a70
      cited_regions:
      - rows
    id: meta/muse-spark#arena_sc_document#37947d26e290
  - benchmark_id: arena_sc_industry_software_it_services
    model_id_as_evaluated: muse-spark
    score: 1520.06
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / industry_software_and_it_services, latest split, revision
      1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1520.06 [1511.51,
      1528.61], 5318 votes, rank 13. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:4538dd5bcb06397043fc55c64535410a284e7da8668e8c13cc2950c6f1baa37c
      cited_regions:
      - rows
    id: meta/muse-spark#arena_sc_industry_software_it_services#4a82ec8fe77f
  - benchmark_id: arena_sc_industry_entertainment_sports_media
    model_id_as_evaluated: muse-spark
    score: 1462.19
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / industry_entertainment_and_sports_and_media, latest
      split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1462.19 [1449.89,
      1474.48], 2510 votes, rank 14. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:89233e13dec450388587fa44e3af9cfb82da53034e616b951c1cbe809b0c4cef
      cited_regions:
      - rows
    id: meta/muse-spark#arena_sc_industry_entertainment_sports_media#c2cb9df20e34
  - benchmark_id: arena_sc_industry_mathematical
    model_id_as_evaluated: muse-spark
    score: 1468.67
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / industry_mathematical, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1468.67 [1447.87,
      1489.47], 819 votes, rank 52. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:514a2f81b6bce9bc34481c6e0d7af71184302842a4f5b8284657dc5024965f25
      cited_regions:
      - rows
    id: meta/muse-spark#arena_sc_industry_mathematical#ac70335210e6
  - benchmark_id: arena_sc_factuality
    model_id_as_evaluated: muse-spark
    score: 1466.77
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_factuality / overall, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1466.77 [1461.24,
      1472.30], 13548 votes, rank 30. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-factuality
      snapshot_ref: sha256:359d85539a6e849ffbfe46427efdefadb4be9c907f9fbea9f799ce7bbf6c52c2
      cited_regions:
      - rows
    id: meta/muse-spark#arena_sc_factuality#1afc7de69ce1
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
  huggingface_downloads: 26174
  huggingface_likes: 2205
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
  huggingface_url: https://huggingface.co/meta-llama/Llama-2-70b-chat-hf
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
facts:
- facet: model.class
  value: text-generator
  state: known
  sources:
  - source_id: model-143-meta-muse-spark
    snapshot_ref: sha256:804c2c88e8424231fcf3e8406d4e3707a8166f1622b6ce70805e9f9b6593424a
    cited_regions:
    - model-spec
  - source_id: model-143-meta-release-index
    snapshot_ref: sha256:bcde843202fd01598bfc74c3adeb5b59df1713f0e4c07784728e5c941691895a
    cited_regions:
    - audit
  - source_id: model-143-meta-model-api
    snapshot_ref: sha256:e6306b281f9b3d01d0c83c4c662af0dc8613f1e67138906f112cb24fbea30d2a
    cited_regions:
    - audit
  - source_id: model-143-meta-company
    snapshot_ref: sha256:fcf8283f72c1376dc97cd49a2776df3b6c7608b6f76844ac86c67fa89f497e3f
    cited_regions:
    - audit
  - source_id: model-143-meta-sec
    snapshot_ref: sha256:7627db9dbf44d398db1726ca661ff7222dcbd76bc768ddec13815ab9b9fbd07e
    cited_regions:
    - audit
- facet: model.input_modalities
  value:
  - text
  - image
  - audio
  state: known
  sources:
  - source_id: model-143-meta-muse-spark
    snapshot_ref: sha256:804c2c88e8424231fcf3e8406d4e3707a8166f1622b6ce70805e9f9b6593424a
    cited_regions:
    - model-spec
  - source_id: model-143-meta-release-index
    snapshot_ref: sha256:bcde843202fd01598bfc74c3adeb5b59df1713f0e4c07784728e5c941691895a
    cited_regions:
    - audit
  - source_id: model-143-meta-model-api
    snapshot_ref: sha256:e6306b281f9b3d01d0c83c4c662af0dc8613f1e67138906f112cb24fbea30d2a
    cited_regions:
    - audit
  - source_id: model-143-meta-company
    snapshot_ref: sha256:fcf8283f72c1376dc97cd49a2776df3b6c7608b6f76844ac86c67fa89f497e3f
    cited_regions:
    - audit
  - source_id: model-143-meta-sec
    snapshot_ref: sha256:7627db9dbf44d398db1726ca661ff7222dcbd76bc768ddec13815ab9b9fbd07e
    cited_regions:
    - audit
- facet: model.output_modalities
  value:
  - text
  state: known
  sources:
  - source_id: model-143-meta-muse-spark
    snapshot_ref: sha256:804c2c88e8424231fcf3e8406d4e3707a8166f1622b6ce70805e9f9b6593424a
    cited_regions:
    - model-spec
  - source_id: model-143-meta-release-index
    snapshot_ref: sha256:bcde843202fd01598bfc74c3adeb5b59df1713f0e4c07784728e5c941691895a
    cited_regions:
    - audit
  - source_id: model-143-meta-model-api
    snapshot_ref: sha256:e6306b281f9b3d01d0c83c4c662af0dc8613f1e67138906f112cb24fbea30d2a
    cited_regions:
    - audit
  - source_id: model-143-meta-company
    snapshot_ref: sha256:fcf8283f72c1376dc97cd49a2776df3b6c7608b6f76844ac86c67fa89f497e3f
    cited_regions:
    - audit
  - source_id: model-143-meta-sec
    snapshot_ref: sha256:7627db9dbf44d398db1726ca661ff7222dcbd76bc768ddec13815ab9b9fbd07e
    cited_regions:
    - audit
- facet: model.context_window
  value: 8192
  state: known
  sources:
  - source_id: model-143-meta-muse-spark
    snapshot_ref: sha256:804c2c88e8424231fcf3e8406d4e3707a8166f1622b6ce70805e9f9b6593424a
    cited_regions:
    - model-spec
  - source_id: model-143-meta-release-index
    snapshot_ref: sha256:bcde843202fd01598bfc74c3adeb5b59df1713f0e4c07784728e5c941691895a
    cited_regions:
    - audit
  - source_id: model-143-meta-model-api
    snapshot_ref: sha256:e6306b281f9b3d01d0c83c4c662af0dc8613f1e67138906f112cb24fbea30d2a
    cited_regions:
    - audit
  - source_id: model-143-meta-company
    snapshot_ref: sha256:fcf8283f72c1376dc97cd49a2776df3b6c7608b6f76844ac86c67fa89f497e3f
    cited_regions:
    - audit
  - source_id: model-143-meta-sec
    snapshot_ref: sha256:7627db9dbf44d398db1726ca661ff7222dcbd76bc768ddec13815ab9b9fbd07e
    cited_regions:
    - audit
- facet: model.max_output_tokens
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-meta-muse-spark
    snapshot_ref: sha256:804c2c88e8424231fcf3e8406d4e3707a8166f1622b6ce70805e9f9b6593424a
    cited_regions:
    - model-spec
  - source_id: model-143-meta-release-index
    snapshot_ref: sha256:bcde843202fd01598bfc74c3adeb5b59df1713f0e4c07784728e5c941691895a
    cited_regions:
    - audit
  - source_id: model-143-meta-model-api
    snapshot_ref: sha256:e6306b281f9b3d01d0c83c4c662af0dc8613f1e67138906f112cb24fbea30d2a
    cited_regions:
    - audit
  - source_id: model-143-meta-company
    snapshot_ref: sha256:fcf8283f72c1376dc97cd49a2776df3b6c7608b6f76844ac86c67fa89f497e3f
    cited_regions:
    - audit
  - source_id: model-143-meta-sec
    snapshot_ref: sha256:7627db9dbf44d398db1726ca661ff7222dcbd76bc768ddec13815ab9b9fbd07e
    cited_regions:
    - audit
  checked_sources:
  - model-143-meta-muse-spark
  - model-143-meta-release-index
  - model-143-meta-model-api
  - model-143-meta-company
  - model-143-meta-sec
- facet: model.weights_openness
  value: closed_weights
  state: known
  sources:
  - source_id: model-143-meta-muse-spark
    snapshot_ref: sha256:804c2c88e8424231fcf3e8406d4e3707a8166f1622b6ce70805e9f9b6593424a
    cited_regions:
    - model-spec
  - source_id: model-143-meta-release-index
    snapshot_ref: sha256:bcde843202fd01598bfc74c3adeb5b59df1713f0e4c07784728e5c941691895a
    cited_regions:
    - audit
  - source_id: model-143-meta-model-api
    snapshot_ref: sha256:e6306b281f9b3d01d0c83c4c662af0dc8613f1e67138906f112cb24fbea30d2a
    cited_regions:
    - audit
  - source_id: model-143-meta-company
    snapshot_ref: sha256:fcf8283f72c1376dc97cd49a2776df3b6c7608b6f76844ac86c67fa89f497e3f
    cited_regions:
    - audit
  - source_id: model-143-meta-sec
    snapshot_ref: sha256:7627db9dbf44d398db1726ca661ff7222dcbd76bc768ddec13815ab9b9fbd07e
    cited_regions:
    - audit
- facet: licence.commercial_use
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-meta-muse-spark
    snapshot_ref: sha256:804c2c88e8424231fcf3e8406d4e3707a8166f1622b6ce70805e9f9b6593424a
    cited_regions:
    - model-spec
  - source_id: model-143-meta-release-index
    snapshot_ref: sha256:bcde843202fd01598bfc74c3adeb5b59df1713f0e4c07784728e5c941691895a
    cited_regions:
    - audit
  - source_id: model-143-meta-model-api
    snapshot_ref: sha256:e6306b281f9b3d01d0c83c4c662af0dc8613f1e67138906f112cb24fbea30d2a
    cited_regions:
    - audit
  - source_id: model-143-meta-company
    snapshot_ref: sha256:fcf8283f72c1376dc97cd49a2776df3b6c7608b6f76844ac86c67fa89f497e3f
    cited_regions:
    - audit
  - source_id: model-143-meta-sec
    snapshot_ref: sha256:7627db9dbf44d398db1726ca661ff7222dcbd76bc768ddec13815ab9b9fbd07e
    cited_regions:
    - audit
  checked_sources:
  - model-143-meta-muse-spark
  - model-143-meta-release-index
  - model-143-meta-model-api
  - model-143-meta-company
  - model-143-meta-sec
- facet: licence.user_cap
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-meta-muse-spark
    snapshot_ref: sha256:804c2c88e8424231fcf3e8406d4e3707a8166f1622b6ce70805e9f9b6593424a
    cited_regions:
    - model-spec
  - source_id: model-143-meta-release-index
    snapshot_ref: sha256:bcde843202fd01598bfc74c3adeb5b59df1713f0e4c07784728e5c941691895a
    cited_regions:
    - audit
  - source_id: model-143-meta-model-api
    snapshot_ref: sha256:e6306b281f9b3d01d0c83c4c662af0dc8613f1e67138906f112cb24fbea30d2a
    cited_regions:
    - audit
  - source_id: model-143-meta-company
    snapshot_ref: sha256:fcf8283f72c1376dc97cd49a2776df3b6c7608b6f76844ac86c67fa89f497e3f
    cited_regions:
    - audit
  - source_id: model-143-meta-sec
    snapshot_ref: sha256:7627db9dbf44d398db1726ca661ff7222dcbd76bc768ddec13815ab9b9fbd07e
    cited_regions:
    - audit
  checked_sources:
  - model-143-meta-muse-spark
  - model-143-meta-release-index
  - model-143-meta-model-api
  - model-143-meta-company
  - model-143-meta-sec
- facet: licence.output_training
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-meta-muse-spark
    snapshot_ref: sha256:804c2c88e8424231fcf3e8406d4e3707a8166f1622b6ce70805e9f9b6593424a
    cited_regions:
    - model-spec
  - source_id: model-143-meta-release-index
    snapshot_ref: sha256:bcde843202fd01598bfc74c3adeb5b59df1713f0e4c07784728e5c941691895a
    cited_regions:
    - audit
  - source_id: model-143-meta-model-api
    snapshot_ref: sha256:e6306b281f9b3d01d0c83c4c662af0dc8613f1e67138906f112cb24fbea30d2a
    cited_regions:
    - audit
  - source_id: model-143-meta-company
    snapshot_ref: sha256:fcf8283f72c1376dc97cd49a2776df3b6c7608b6f76844ac86c67fa89f497e3f
    cited_regions:
    - audit
  - source_id: model-143-meta-sec
    snapshot_ref: sha256:7627db9dbf44d398db1726ca661ff7222dcbd76bc768ddec13815ab9b9fbd07e
    cited_regions:
    - audit
  checked_sources:
  - model-143-meta-muse-spark
  - model-143-meta-release-index
  - model-143-meta-model-api
  - model-143-meta-company
  - model-143-meta-sec
- facet: licence.fine_tuning
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-meta-muse-spark
    snapshot_ref: sha256:804c2c88e8424231fcf3e8406d4e3707a8166f1622b6ce70805e9f9b6593424a
    cited_regions:
    - model-spec
  - source_id: model-143-meta-release-index
    snapshot_ref: sha256:bcde843202fd01598bfc74c3adeb5b59df1713f0e4c07784728e5c941691895a
    cited_regions:
    - audit
  - source_id: model-143-meta-model-api
    snapshot_ref: sha256:e6306b281f9b3d01d0c83c4c662af0dc8613f1e67138906f112cb24fbea30d2a
    cited_regions:
    - audit
  - source_id: model-143-meta-company
    snapshot_ref: sha256:fcf8283f72c1376dc97cd49a2776df3b6c7608b6f76844ac86c67fa89f497e3f
    cited_regions:
    - audit
  - source_id: model-143-meta-sec
    snapshot_ref: sha256:7627db9dbf44d398db1726ca661ff7222dcbd76bc768ddec13815ab9b9fbd07e
    cited_regions:
    - audit
  checked_sources:
  - model-143-meta-muse-spark
  - model-143-meta-release-index
  - model-143-meta-model-api
  - model-143-meta-company
  - model-143-meta-sec
- facet: origin.lab_jurisdiction
  value:
  - US
  state: known
  sources:
  - source_id: model-143-meta-muse-spark
    snapshot_ref: sha256:804c2c88e8424231fcf3e8406d4e3707a8166f1622b6ce70805e9f9b6593424a
    cited_regions:
    - model-spec
  - source_id: model-143-meta-release-index
    snapshot_ref: sha256:bcde843202fd01598bfc74c3adeb5b59df1713f0e4c07784728e5c941691895a
    cited_regions:
    - audit
  - source_id: model-143-meta-model-api
    snapshot_ref: sha256:e6306b281f9b3d01d0c83c4c662af0dc8613f1e67138906f112cb24fbea30d2a
    cited_regions:
    - audit
  - source_id: model-143-meta-company
    snapshot_ref: sha256:fcf8283f72c1376dc97cd49a2776df3b6c7608b6f76844ac86c67fa89f497e3f
    cited_regions:
    - audit
  - source_id: model-143-meta-sec
    snapshot_ref: sha256:7627db9dbf44d398db1726ca661ff7222dcbd76bc768ddec13815ab9b9fbd07e
    cited_regions:
    - audit
- facet: origin.base_lineage
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-meta-muse-spark
    snapshot_ref: sha256:804c2c88e8424231fcf3e8406d4e3707a8166f1622b6ce70805e9f9b6593424a
    cited_regions:
    - model-spec
  - source_id: model-143-meta-release-index
    snapshot_ref: sha256:bcde843202fd01598bfc74c3adeb5b59df1713f0e4c07784728e5c941691895a
    cited_regions:
    - audit
  - source_id: model-143-meta-model-api
    snapshot_ref: sha256:e6306b281f9b3d01d0c83c4c662af0dc8613f1e67138906f112cb24fbea30d2a
    cited_regions:
    - audit
  - source_id: model-143-meta-company
    snapshot_ref: sha256:fcf8283f72c1376dc97cd49a2776df3b6c7608b6f76844ac86c67fa89f497e3f
    cited_regions:
    - audit
  - source_id: model-143-meta-sec
    snapshot_ref: sha256:7627db9dbf44d398db1726ca661ff7222dcbd76bc768ddec13815ab9b9fbd07e
    cited_regions:
    - audit
  checked_sources:
  - model-143-meta-muse-spark
  - model-143-meta-release-index
  - model-143-meta-model-api
  - model-143-meta-company
  - model-143-meta-sec
- facet: origin.weights_hosting
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-meta-muse-spark
    snapshot_ref: sha256:804c2c88e8424231fcf3e8406d4e3707a8166f1622b6ce70805e9f9b6593424a
    cited_regions:
    - model-spec
  - source_id: model-143-meta-release-index
    snapshot_ref: sha256:bcde843202fd01598bfc74c3adeb5b59df1713f0e4c07784728e5c941691895a
    cited_regions:
    - audit
  - source_id: model-143-meta-model-api
    snapshot_ref: sha256:e6306b281f9b3d01d0c83c4c662af0dc8613f1e67138906f112cb24fbea30d2a
    cited_regions:
    - audit
  - source_id: model-143-meta-company
    snapshot_ref: sha256:fcf8283f72c1376dc97cd49a2776df3b6c7608b6f76844ac86c67fa89f497e3f
    cited_regions:
    - audit
  - source_id: model-143-meta-sec
    snapshot_ref: sha256:7627db9dbf44d398db1726ca661ff7222dcbd76bc768ddec13815ab9b9fbd07e
    cited_regions:
    - audit
  checked_sources:
  - model-143-meta-muse-spark
  - model-143-meta-release-index
  - model-143-meta-model-api
  - model-143-meta-company
  - model-143-meta-sec
- facet: model.release_date
  value: '2026-04-08'
  state: known
  sources:
  - source_id: model-143-meta-muse-spark
    snapshot_ref: sha256:804c2c88e8424231fcf3e8406d4e3707a8166f1622b6ce70805e9f9b6593424a
    cited_regions:
    - model-spec
  - source_id: model-143-meta-release-index
    snapshot_ref: sha256:bcde843202fd01598bfc74c3adeb5b59df1713f0e4c07784728e5c941691895a
    cited_regions:
    - audit
  - source_id: model-143-meta-model-api
    snapshot_ref: sha256:e6306b281f9b3d01d0c83c4c662af0dc8613f1e67138906f112cb24fbea30d2a
    cited_regions:
    - audit
  - source_id: model-143-meta-company
    snapshot_ref: sha256:fcf8283f72c1376dc97cd49a2776df3b6c7608b6f76844ac86c67fa89f497e3f
    cited_regions:
    - audit
  - source_id: model-143-meta-sec
    snapshot_ref: sha256:7627db9dbf44d398db1726ca661ff7222dcbd76bc768ddec13815ab9b9fbd07e
    cited_regions:
    - audit
- facet: model.lifecycle
  value: active
  state: known
  sources:
  - source_id: model-143-meta-muse-spark
    snapshot_ref: sha256:804c2c88e8424231fcf3e8406d4e3707a8166f1622b6ce70805e9f9b6593424a
    cited_regions:
    - model-spec
  - source_id: model-143-meta-release-index
    snapshot_ref: sha256:bcde843202fd01598bfc74c3adeb5b59df1713f0e4c07784728e5c941691895a
    cited_regions:
    - audit
  - source_id: model-143-meta-model-api
    snapshot_ref: sha256:e6306b281f9b3d01d0c83c4c662af0dc8613f1e67138906f112cb24fbea30d2a
    cited_regions:
    - audit
  - source_id: model-143-meta-company
    snapshot_ref: sha256:fcf8283f72c1376dc97cd49a2776df3b6c7608b6f76844ac86c67fa89f497e3f
    cited_regions:
    - audit
  - source_id: model-143-meta-sec
    snapshot_ref: sha256:7627db9dbf44d398db1726ca661ff7222dcbd76bc768ddec13815ab9b9fbd07e
    cited_regions:
    - audit
- facet: feature.tool_calling
  value: true
  state: known
  sources:
  - source_id: model-143-meta-muse-spark
    snapshot_ref: sha256:804c2c88e8424231fcf3e8406d4e3707a8166f1622b6ce70805e9f9b6593424a
    cited_regions:
    - model-spec
  - source_id: model-143-meta-release-index
    snapshot_ref: sha256:bcde843202fd01598bfc74c3adeb5b59df1713f0e4c07784728e5c941691895a
    cited_regions:
    - audit
  - source_id: model-143-meta-model-api
    snapshot_ref: sha256:e6306b281f9b3d01d0c83c4c662af0dc8613f1e67138906f112cb24fbea30d2a
    cited_regions:
    - audit
  - source_id: model-143-meta-company
    snapshot_ref: sha256:fcf8283f72c1376dc97cd49a2776df3b6c7608b6f76844ac86c67fa89f497e3f
    cited_regions:
    - audit
  - source_id: model-143-meta-sec
    snapshot_ref: sha256:7627db9dbf44d398db1726ca661ff7222dcbd76bc768ddec13815ab9b9fbd07e
    cited_regions:
    - audit
- facet: feature.structured_output
  value: true
  state: known
  sources:
  - source_id: model-143-meta-muse-spark
    snapshot_ref: sha256:804c2c88e8424231fcf3e8406d4e3707a8166f1622b6ce70805e9f9b6593424a
    cited_regions:
    - model-spec
  - source_id: model-143-meta-release-index
    snapshot_ref: sha256:bcde843202fd01598bfc74c3adeb5b59df1713f0e4c07784728e5c941691895a
    cited_regions:
    - audit
  - source_id: model-143-meta-model-api
    snapshot_ref: sha256:e6306b281f9b3d01d0c83c4c662af0dc8613f1e67138906f112cb24fbea30d2a
    cited_regions:
    - audit
  - source_id: model-143-meta-company
    snapshot_ref: sha256:fcf8283f72c1376dc97cd49a2776df3b6c7608b6f76844ac86c67fa89f497e3f
    cited_regions:
    - audit
  - source_id: model-143-meta-sec
    snapshot_ref: sha256:7627db9dbf44d398db1726ca661ff7222dcbd76bc768ddec13815ab9b9fbd07e
    cited_regions:
    - audit
- facet: feature.effort_controls
  value: true
  state: known
  sources:
  - source_id: model-143-meta-muse-spark
    snapshot_ref: sha256:804c2c88e8424231fcf3e8406d4e3707a8166f1622b6ce70805e9f9b6593424a
    cited_regions:
    - model-spec
  - source_id: model-143-meta-release-index
    snapshot_ref: sha256:bcde843202fd01598bfc74c3adeb5b59df1713f0e4c07784728e5c941691895a
    cited_regions:
    - audit
  - source_id: model-143-meta-model-api
    snapshot_ref: sha256:e6306b281f9b3d01d0c83c4c662af0dc8613f1e67138906f112cb24fbea30d2a
    cited_regions:
    - audit
  - source_id: model-143-meta-company
    snapshot_ref: sha256:fcf8283f72c1376dc97cd49a2776df3b6c7608b6f76844ac86c67fa89f497e3f
    cited_regions:
    - audit
  - source_id: model-143-meta-sec
    snapshot_ref: sha256:7627db9dbf44d398db1726ca661ff7222dcbd76bc768ddec13815ab9b9fbd07e
    cited_regions:
    - audit
- facet: feature.batch
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-meta-muse-spark
    snapshot_ref: sha256:804c2c88e8424231fcf3e8406d4e3707a8166f1622b6ce70805e9f9b6593424a
    cited_regions:
    - model-spec
  - source_id: model-143-meta-release-index
    snapshot_ref: sha256:bcde843202fd01598bfc74c3adeb5b59df1713f0e4c07784728e5c941691895a
    cited_regions:
    - audit
  - source_id: model-143-meta-model-api
    snapshot_ref: sha256:e6306b281f9b3d01d0c83c4c662af0dc8613f1e67138906f112cb24fbea30d2a
    cited_regions:
    - audit
  - source_id: model-143-meta-company
    snapshot_ref: sha256:fcf8283f72c1376dc97cd49a2776df3b6c7608b6f76844ac86c67fa89f497e3f
    cited_regions:
    - audit
  - source_id: model-143-meta-sec
    snapshot_ref: sha256:7627db9dbf44d398db1726ca661ff7222dcbd76bc768ddec13815ab9b9fbd07e
    cited_regions:
    - audit
  checked_sources:
  - model-143-meta-muse-spark
  - model-143-meta-release-index
  - model-143-meta-model-api
  - model-143-meta-company
  - model-143-meta-sec
- facet: feature.streaming
  value: true
  state: known
  sources:
  - source_id: model-143-meta-muse-spark
    snapshot_ref: sha256:804c2c88e8424231fcf3e8406d4e3707a8166f1622b6ce70805e9f9b6593424a
    cited_regions:
    - model-spec
  - source_id: model-143-meta-release-index
    snapshot_ref: sha256:bcde843202fd01598bfc74c3adeb5b59df1713f0e4c07784728e5c941691895a
    cited_regions:
    - audit
  - source_id: model-143-meta-model-api
    snapshot_ref: sha256:e6306b281f9b3d01d0c83c4c662af0dc8613f1e67138906f112cb24fbea30d2a
    cited_regions:
    - audit
  - source_id: model-143-meta-company
    snapshot_ref: sha256:fcf8283f72c1376dc97cd49a2776df3b6c7608b6f76844ac86c67fa89f497e3f
    cited_regions:
    - audit
  - source_id: model-143-meta-sec
    snapshot_ref: sha256:7627db9dbf44d398db1726ca661ff7222dcbd76bc768ddec13815ab9b9fbd07e
    cited_regions:
    - audit
card_schema_version: '3.0'
card_author: manual
card_created: '2026-04-08'
card_updated: '2026-09-18'
---


# Muse Spark

Meta's first model from Meta Superintelligence Labs (MSL), led by Alexandr Wang. Natively multimodal reasoning model with tool-use, visual chain of thought, and multi-agent orchestration. Accepts voice, text, and image input; text-only output. Features Instant, Thinking, and Contemplating modes. Powers Meta AI across 3B+ users. First closed-source model from Meta, departing from the Llama open-weights strategy.

Licence: null. The card's Hugging Face URL is meta-llama/Llama-2-70b-chat-hf, which is not this model, and no Muse Spark licence document was found (read 2026-09-18). A known-wrong llama-community default is worse than none.