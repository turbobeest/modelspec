---
model_id: google/gemini-3-7-flash
display_name: Gemini 3.7 Flash
provider: google
provider_display: Google DeepMind
family: gemini-flash
version: gemini-3.7-flash
release_date: '2026-08-13'
last_updated: '2026-08-13'
status: active
model_type: llm-reasoning
model_subtypes: []
tags: []
pipeline_tag: ''
architecture:
  type: null
  total_parameters: null
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
  origin_org_type: null
modalities:
  input:
  - text
  - image
  - video
  - audio
  - pdf
  output:
  - text
  text:
    max_input_tokens: null
    max_output_tokens: 65536
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
    input_supported: true
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
  input: 0.75
  output: 3.75
  reasoning: null
  cache_read: 0.075
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
  scores: {}
  evidence:
  - benchmark_id: arena_elo_style_control
    model_id_as_evaluated: gemini-3.7-flash-high
    score: 1489.82
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / overall, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category overall,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: high; MODEL-123 max-effort rule). Rating 1489.82 [1481.62, 1498.02], 5640 votes,
      rank 12.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: google/gemini-3-7-flash#arena_elo_style_control#98b2af289dc5
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
    model_id_as_evaluated: gemini-3.7-flash-high
    score: 1520.59
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / coding, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category coding,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: high; MODEL-123 max-effort rule). Rating 1520.59 [1505.81, 1535.37], 1730 votes,
      rank 26.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: google/gemini-3-7-flash#arena_sc_coding#160eff398cbf
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
    model_id_as_evaluated: gemini-3.7-flash-high
    score: 1506.7
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / hard_prompts, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category hard_prompts,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: high; MODEL-123 max-effort rule). Rating 1506.70 [1496.59, 1516.81], 3793 votes,
      rank 18.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: google/gemini-3-7-flash#arena_sc_hard_prompts#aba74016b974
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
    model_id_as_evaluated: gemini-3.7-flash-high
    score: 1521.51
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / math, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category math, leaderboard_publish_date
      2026-09-13; style control. Highest-effort row for the product (effort: high; MODEL-123
      max-effort rule). Rating 1521.51 [1488.25, 1554.77], 310 votes, rank 5.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: google/gemini-3-7-flash#arena_sc_math#a26416f8d42f
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
    model_id_as_evaluated: gemini-3.7-flash-high
    score: 1494.76
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / creative_writing, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category creative_writing,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: high; MODEL-123 max-effort rule). Rating 1494.76 [1476.54, 1512.98], 1185 votes,
      rank 4.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: google/gemini-3-7-flash#arena_sc_creative_writing#ab21c2a35622
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
    model_id_as_evaluated: gemini-3.7-flash-high
    score: 1484.41
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / instruction_following, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category instruction_following,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: high; MODEL-123 max-effort rule). Rating 1484.41 [1470.76, 1498.07], 2035 votes,
      rank 12.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: google/gemini-3-7-flash#arena_sc_instruction_following#eadce7ffa0b9
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
    model_id_as_evaluated: gemini-3.7-flash-high
    score: 1498.23
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / multi_turn, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category multi_turn,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: high; MODEL-123 max-effort rule). Rating 1498.23 [1477.43, 1519.04], 883 votes,
      rank 9.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: google/gemini-3-7-flash#arena_sc_multi_turn#41927684804f
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
    model_id_as_evaluated: gemini-3.7-flash-high
    score: 1515.38
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / expert, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category expert,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: high; MODEL-123 max-effort rule). Rating 1515.38 [1492.31, 1538.45], 649 votes,
      rank 16.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: google/gemini-3-7-flash#arena_sc_expert#65814a1d1bb1
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
    model_id_as_evaluated: gemini-3.7-flash-high
    score: 1498.07
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / longer_query, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category longer_query,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: high; MODEL-123 max-effort rule). Rating 1498.07 [1485.82, 1510.32], 2680 votes,
      rank 16.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: google/gemini-3-7-flash#arena_sc_longer_query#9d9fe1f1bb89
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
    model_id_as_evaluated: gemini-3.7-flash-high
    score: 1483.76
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / non_english, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category non_english,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: high; MODEL-123 max-effort rule). Rating 1483.76 [1473.02, 1494.51], 3275 votes,
      rank 10.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: google/gemini-3-7-flash#arena_sc_non_english#b3fdeb416bc3
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
    model_id_as_evaluated: gemini-3.7-flash-high
    score: 1493.05
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
      (effort: high; MODEL-123 max-effort rule). Rating 1493.05 [1461.27, 1524.83], 381 votes,
      rank 24.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: google/gemini-3-7-flash#arena_sc_medicine#8e5ce276d9c5
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
    model_id_as_evaluated: gemini-3.7-flash-high
    score: 1496.89
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
      (effort: high; MODEL-123 max-effort rule). Rating 1496.89 [1468.23, 1525.56], 436 votes,
      rank 16.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: google/gemini-3-7-flash#arena_sc_legal#11eed42e4c89
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
    model_id_as_evaluated: gemini-3.7-flash-high
    score: 1474.41
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
      (effort: high; MODEL-123 max-effort rule). Rating 1474.41 [1455.01, 1493.82], 989 votes,
      rank 31.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: google/gemini-3-7-flash#arena_sc_business#0098ef32727a
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
    model_id_as_evaluated: gemini-3.7-flash-high
    score: 1510.95
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
      (effort: high; MODEL-123 max-effort rule). Rating 1510.95 [1491.67, 1530.24], 948 votes,
      rank 14.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: google/gemini-3-7-flash#arena_sc_science#61fbad21e4d0
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
    model_id_as_evaluated: gemini-3.7-flash-high
    score: 1488.65
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
      (effort: high; MODEL-123 max-effort rule). Rating 1488.65 [1472.58, 1504.72], 1480 votes,
      rank 7.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: google/gemini-3-7-flash#arena_sc_writing#b9671dcb5fce
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:451771d6d03dfcdc902ebbb505ce47bfc614e33bde751b42f3be31d89d416086
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_webdev
    model_id_as_evaluated: gemini-3.7-flash-high
    score: 1594.56
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-23'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: webdev / overall, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset webdev, category overall, leaderboard_publish_date
      2026-09-23; no style-controlled variant. Highest-effort row for the product (effort: high;
      MODEL-123 max-effort rule). Rating 1594.56 [1586.31, 1602.82], 7162 votes, rank 22.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: google/gemini-3-7-flash#arena_webdev#3494032d4822
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
    model_id_as_evaluated: gemini-3.7-flash_high
    score: 94.82
    unit: percent
    source_url: https://epoch.ai/benchmarks/gpqa-diamond
    source_kind: independent_evaluator
    evidence_date: '2026-08-14'
    date_type: evaluated
    verified_at: '2026-09-29'
    benchmark_version: GPQA Diamond (Epoch AI run)
    configuration: Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (gpqa_diamond.csv),
      read 2026-09-24. Run started 2026-08-14T18:29:12.000Z; effort high; highest-effort run
      for the model (MODEL-123 max-effort rule), newest on a tie. Standard error 1.35 points.
    limitations: Epoch AI data, CC BY 4.0.
    id: google/gemini-3-7-flash#gpqa_diamond#fe74472c076a
    measured_by: independent_evaluator
    effort: high
    harness: null
    sources:
    - source_id: model-143-evidence-epoch-gpqa-diamond-csv
      snapshot_ref: sha256:946618a3befb5210ccf841c8f3c6b257584d10d5314a7e03408fb73aa13a38a9
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: frontiermath_tiers_1_3_v2
    model_id_as_evaluated: gemini-3.7-flash_high
    score: 71.58
    unit: percent
    source_url: https://epoch.ai/frontiermath
    source_kind: independent_evaluator
    evidence_date: '2026-08-14'
    date_type: evaluated
    verified_at: '2026-09-29'
    benchmark_version: FrontierMath-Tiers-1-3-v2-Private (Epoch AI run)
    configuration: Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (frontiermath_tiers_1_3_v2.csv),
      read 2026-09-24. Run started 2026-08-14T19:59:58.000Z; effort high; highest-effort run
      for the model (MODEL-123 max-effort rule), newest on a tie. Standard error 2.68 points.
    limitations: Epoch AI data, CC BY 4.0.
    id: google/gemini-3-7-flash#frontiermath_tiers_1_3_v2#053531728168
    measured_by: independent_evaluator
    effort: high
    harness: null
    sources:
    - source_id: model-143-evidence-epoch-frontiermath-tiers-1-3-v2-csv
      snapshot_ref: sha256:ff8b653f9ba2c936d6278eeecc42b3a3dee1079e409c8806616f80fb41e23c11
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: simpleqa_verified
    model_id_as_evaluated: gemini-3.7-flash_high
    score: 69.2
    unit: percent
    source_url: https://epoch.ai/benchmarks/simpleqa-verified
    source_kind: independent_evaluator
    evidence_date: '2026-08-27'
    date_type: evaluated
    verified_at: '2026-09-29'
    benchmark_version: SimpleQA Verified, proportion correct, Epoch AI protocol with anti-abstention
      prompt
    configuration: Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (simpleqa_verified.csv),
      read 2026-09-24. Run started 2026-08-27T19:30:25.000Z; effort high; highest-effort run
      for the model (MODEL-123 max-effort rule), newest on a tie. Standard error 1.46 points.
    limitations: Epoch AI data, CC BY 4.0.
    id: google/gemini-3-7-flash#simpleqa_verified#1e9f1c381872
    measured_by: independent_evaluator
    effort: high
    harness: null
    sources:
    - source_id: model-160-epoch-simpleqa-verified-csv
      snapshot_ref: sha256:f4e88f5154755ef9c355b28d6900467dce89bcbe0ea54329d1f96215c21239fa
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: frontiercode_v1_1
    model_id_as_evaluated: Gemini 3.7 Flash
    score: 43.6
    unit: percent
    source_url: https://cognition.com/frontiercode
    source_kind: benchmark_author
    evidence_date: '2026-09-29'
    date_type: evaluated
    verified_at: '2026-09-29'
    benchmark_version: FrontierCode 1.1, main score (Mean@5)
    configuration: Board row as copied in Epoch AI's benchmark data (frontiercode_external.csv,
      https://epoch.ai/data/benchmark_data.zip), read 2026-09-24. Effort medium; the highest-effort
      row for the model (MODEL-123 max-effort rule). Harness chisel.
    limitations: A live board's standing, dated by the day ModelSpec read Epoch AI's copy; the
      copy carries no per-row date. Epoch AI data, CC BY 4.0.
    id: google/gemini-3-7-flash#frontiercode_v1_1#8751a571f44e
    measured_by: benchmark_author
    effort: medium
    harness: unregistered
    sources:
    - source_id: model-160-frontiercode
      snapshot_ref: sha256:946a90057bea730dbfa5a27ab38168e01b5269492c1b41f46cf4ec29dd0d3cf3
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: deepswe_v1_1
    model_id_as_evaluated: gemini-3-7-flash (high)
    score: 65.27
    unit: percent
    source_url: https://deepswe.datacurve.ai/
    source_kind: benchmark_author
    evidence_date: '2026-09-29'
    date_type: evaluated
    verified_at: '2026-09-29'
    benchmark_version: DeepSWE v1.1, pass@1, mini-swe-agent
    configuration: Board row as copied in Epoch AI's benchmark data (deepswe_external.csv, https://epoch.ai/data/benchmark_data.zip),
      read 2026-09-24. Effort high; the highest-effort row for the model (MODEL-123 max-effort
      rule). Harness mini-swe-agent.
    limitations: A live board's standing, dated by the day ModelSpec read Epoch AI's copy; the
      copy carries no per-row date. Epoch AI data, CC BY 4.0.
    id: google/gemini-3-7-flash#deepswe_v1_1#0d63a8811e24
    measured_by: benchmark_author
    effort: high
    harness: unregistered
    sources:
    - source_id: model-160-deepswe-v1-1
      snapshot_ref: sha256:33c505b573a474e601643fe1e1295b91b10e3ef62dfeab167a3851226358c972
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: terminal_bench_v4_0
    model_id_as_evaluated: Gemini 3.7 Flash
    score: 11.21
    unit: percent
    source_url: https://www.tbench.ai/leaderboard/terminal-bench/4.0
    source_kind: benchmark_author
    evidence_date: '2026-08-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: Terminal-Bench 4.0
    configuration: 'tbench.ai leaderboard row read 2026-09-24: agent mini-SWE-agent (SWE-agent),
      reasoning effort high, 330 trials, accuracy 11.21 ± 2.45 (95% CI). The board''s row date
      is the evidence date. Highest-effort row for the model, best agent on a tie.'
    limitations: The agent harness differs between rows; compare rows with the same agent.
    id: google/gemini-3-7-flash#terminal_bench_v4_0#60947f594915
    measured_by: benchmark_author
    effort: high
    harness: unregistered
    sources:
    - source_id: model-143-evidence-terminal-bench-4-0-json
      snapshot_ref: sha256:ea8d2644137b35340e437581fd626baeb200138b503f17f66f91fdf8eaf7f701
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_english
    model_id_as_evaluated: gemini-3.7-flash-high
    score: 1487.54
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / english, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1487.54 [1475.22,
      1499.86], 2365 votes, rank 20. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:cee57baa7239c5aa2091dcb5db0b4c2ac22cec732b235d66c0cda2ee55bdcb44
      cited_regions:
      - rows
    id: google/gemini-3-7-flash#arena_sc_english#e864e9475fcd
  - benchmark_id: arena_sc_chinese
    model_id_as_evaluated: gemini-3.7-flash-high
    score: 1555.76
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / chinese, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1555.76 [1525.33,
      1586.20], 386 votes, rank 4. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:9bf00fc37e8a997735f423949aba6ffc5551990b6f835297d3fed2b364abe02b
      cited_regions:
      - rows
    id: google/gemini-3-7-flash#arena_sc_chinese#8537bf4ec06d
  - benchmark_id: arena_sc_russian
    model_id_as_evaluated: gemini-3.7-flash-high
    score: 1513.63
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / russian, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1513.63 [1489.21,
      1538.06], 611 votes, rank 3. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:eb77af068077fa90a9514ad454b6a65f061a176f0d68897132e1526f3be743dd
      cited_regions:
      - rows
    id: google/gemini-3-7-flash#arena_sc_russian#7ad581fbac05
  - benchmark_id: arena_sc_french
    model_id_as_evaluated: gemini-3.7-flash-high
    score: 1509.07
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / french, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1509.07 [1465.80,
      1552.34], 209 votes, rank 11. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:c6c9f83eb7147bedac479a445a3803aad09d613643414d3cd5035dbde46d6f2f
      cited_regions:
      - rows
    id: google/gemini-3-7-flash#arena_sc_french#cf45f937a987
  - benchmark_id: arena_sc_industry_software_it_services
    model_id_as_evaluated: gemini-3.7-flash-high
    score: 1511.67
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / industry_software_and_it_services, latest split, revision
      1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1511.67 [1499.07,
      1524.26], 2327 votes, rank 25. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:4eaa9890dce0719aa263af890c9f2a7bb1a3198e291d84dbf8c1371d4f150c52
      cited_regions:
      - rows
    id: google/gemini-3-7-flash#arena_sc_industry_software_it_services#f2975011649c
  - benchmark_id: arena_sc_industry_entertainment_sports_media
    model_id_as_evaluated: gemini-3.7-flash-high
    score: 1476.55
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / industry_entertainment_and_sports_and_media, latest
      split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1476.55 [1460.63,
      1492.47], 1570 votes, rank 6. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:df0d5e7c4d4ce1f683618242c0786eafd164d98b3b49dbaa6e699476bec94ccf
      cited_regions:
      - rows
    id: google/gemini-3-7-flash#arena_sc_industry_entertainment_sports_media#d04ccdf9188b
  - benchmark_id: arena_sc_industry_mathematical
    model_id_as_evaluated: gemini-3.7-flash-high
    score: 1510.79
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / industry_mathematical, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1510.79 [1479.65,
      1541.92], 353 votes, rank 10. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:b0f3ee924239a7a9a1e60676935d0c83091f29517b8acb95e07868e370822e82
      cited_regions:
      - rows
    id: google/gemini-3-7-flash#arena_sc_industry_mathematical#ebb198ae5de9
  - benchmark_id: arena_sc_factuality
    model_id_as_evaluated: gemini-3.7-flash-high
    score: 1485.68
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_factuality / overall, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1485.68 [1478.80,
      1492.56], 5640 votes, rank 8. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-factuality
      snapshot_ref: sha256:ece0fd0afe2b42a38bce698a6be5329044b5503f5edb7f43473c19394b38fc28
      cited_regions:
      - rows
    id: google/gemini-3-7-flash#arena_sc_factuality#23d180d9d348
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
  models_dev_url: https://models.dev/google
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
  - source_id: model-143-google-gemini-3-7-flash
    snapshot_ref: sha256:78f5cafa60ca51ba2e861fc4a1059287c17d304b220fc73f8e2950121bd0287e
    cited_regions:
    - model-spec
  - source_id: model-143-google-deprecations
    snapshot_ref: sha256:ba167204b2fcda0540af24c209b447e7f7c93e07a93a5325914fd4921e00a8dd
    cited_regions:
    - audit
  - source_id: model-143-google-streaming
    snapshot_ref: sha256:891afedb041a982cd2cda18e69e62801dca2cb3a7f9d61eccb7ae5fd214aa5cc
    cited_regions:
    - audit
  - source_id: model-143-google-terms
    snapshot_ref: sha256:698c8ccbb493d4806c4424549eb84baa69ffcad3fd0e37769d89c41c74a28501
    cited_regions:
    - audit
  - source_id: model-143-google-company
    snapshot_ref: sha256:330037a17276cde421aaa59c82be2e81253a115eeb13dcad397e96f61bd8df5c
    cited_regions:
    - audit
  - source_id: model-143-google-sec
    snapshot_ref: sha256:9624fe558574d3c33ca6a6a0f9451a2fdba6e11e465de1d5a822d2e3d70042bc
    cited_regions:
    - audit
- facet: model.input_modalities
  value:
  - text
  - image
  - video
  - audio
  - document
  state: known
  sources:
  - source_id: model-143-google-gemini-3-7-flash
    snapshot_ref: sha256:78f5cafa60ca51ba2e861fc4a1059287c17d304b220fc73f8e2950121bd0287e
    cited_regions:
    - model-spec
  - source_id: model-143-google-deprecations
    snapshot_ref: sha256:ba167204b2fcda0540af24c209b447e7f7c93e07a93a5325914fd4921e00a8dd
    cited_regions:
    - audit
  - source_id: model-143-google-streaming
    snapshot_ref: sha256:891afedb041a982cd2cda18e69e62801dca2cb3a7f9d61eccb7ae5fd214aa5cc
    cited_regions:
    - audit
  - source_id: model-143-google-terms
    snapshot_ref: sha256:698c8ccbb493d4806c4424549eb84baa69ffcad3fd0e37769d89c41c74a28501
    cited_regions:
    - audit
  - source_id: model-143-google-company
    snapshot_ref: sha256:330037a17276cde421aaa59c82be2e81253a115eeb13dcad397e96f61bd8df5c
    cited_regions:
    - audit
  - source_id: model-143-google-sec
    snapshot_ref: sha256:9624fe558574d3c33ca6a6a0f9451a2fdba6e11e465de1d5a822d2e3d70042bc
    cited_regions:
    - audit
- facet: model.output_modalities
  value:
  - text
  state: known
  sources:
  - source_id: model-143-google-gemini-3-7-flash
    snapshot_ref: sha256:78f5cafa60ca51ba2e861fc4a1059287c17d304b220fc73f8e2950121bd0287e
    cited_regions:
    - model-spec
  - source_id: model-143-google-deprecations
    snapshot_ref: sha256:ba167204b2fcda0540af24c209b447e7f7c93e07a93a5325914fd4921e00a8dd
    cited_regions:
    - audit
  - source_id: model-143-google-streaming
    snapshot_ref: sha256:891afedb041a982cd2cda18e69e62801dca2cb3a7f9d61eccb7ae5fd214aa5cc
    cited_regions:
    - audit
  - source_id: model-143-google-terms
    snapshot_ref: sha256:698c8ccbb493d4806c4424549eb84baa69ffcad3fd0e37769d89c41c74a28501
    cited_regions:
    - audit
  - source_id: model-143-google-company
    snapshot_ref: sha256:330037a17276cde421aaa59c82be2e81253a115eeb13dcad397e96f61bd8df5c
    cited_regions:
    - audit
  - source_id: model-143-google-sec
    snapshot_ref: sha256:9624fe558574d3c33ca6a6a0f9451a2fdba6e11e465de1d5a822d2e3d70042bc
    cited_regions:
    - audit
- facet: model.context_window
  value: 1048576
  state: known
  sources:
  - source_id: model-143-google-gemini-3-7-flash
    snapshot_ref: sha256:78f5cafa60ca51ba2e861fc4a1059287c17d304b220fc73f8e2950121bd0287e
    cited_regions:
    - model-spec
  - source_id: model-143-google-deprecations
    snapshot_ref: sha256:ba167204b2fcda0540af24c209b447e7f7c93e07a93a5325914fd4921e00a8dd
    cited_regions:
    - audit
  - source_id: model-143-google-streaming
    snapshot_ref: sha256:891afedb041a982cd2cda18e69e62801dca2cb3a7f9d61eccb7ae5fd214aa5cc
    cited_regions:
    - audit
  - source_id: model-143-google-terms
    snapshot_ref: sha256:698c8ccbb493d4806c4424549eb84baa69ffcad3fd0e37769d89c41c74a28501
    cited_regions:
    - audit
  - source_id: model-143-google-company
    snapshot_ref: sha256:330037a17276cde421aaa59c82be2e81253a115eeb13dcad397e96f61bd8df5c
    cited_regions:
    - audit
  - source_id: model-143-google-sec
    snapshot_ref: sha256:9624fe558574d3c33ca6a6a0f9451a2fdba6e11e465de1d5a822d2e3d70042bc
    cited_regions:
    - audit
- facet: model.max_output_tokens
  value: 65536
  state: known
  sources:
  - source_id: model-143-google-gemini-3-7-flash
    snapshot_ref: sha256:78f5cafa60ca51ba2e861fc4a1059287c17d304b220fc73f8e2950121bd0287e
    cited_regions:
    - model-spec
  - source_id: model-143-google-deprecations
    snapshot_ref: sha256:ba167204b2fcda0540af24c209b447e7f7c93e07a93a5325914fd4921e00a8dd
    cited_regions:
    - audit
  - source_id: model-143-google-streaming
    snapshot_ref: sha256:891afedb041a982cd2cda18e69e62801dca2cb3a7f9d61eccb7ae5fd214aa5cc
    cited_regions:
    - audit
  - source_id: model-143-google-terms
    snapshot_ref: sha256:698c8ccbb493d4806c4424549eb84baa69ffcad3fd0e37769d89c41c74a28501
    cited_regions:
    - audit
  - source_id: model-143-google-company
    snapshot_ref: sha256:330037a17276cde421aaa59c82be2e81253a115eeb13dcad397e96f61bd8df5c
    cited_regions:
    - audit
  - source_id: model-143-google-sec
    snapshot_ref: sha256:9624fe558574d3c33ca6a6a0f9451a2fdba6e11e465de1d5a822d2e3d70042bc
    cited_regions:
    - audit
- facet: model.weights_openness
  value: closed_weights
  state: known
  sources:
  - source_id: model-143-google-gemini-3-7-flash
    snapshot_ref: sha256:78f5cafa60ca51ba2e861fc4a1059287c17d304b220fc73f8e2950121bd0287e
    cited_regions:
    - model-spec
  - source_id: model-143-google-deprecations
    snapshot_ref: sha256:ba167204b2fcda0540af24c209b447e7f7c93e07a93a5325914fd4921e00a8dd
    cited_regions:
    - audit
  - source_id: model-143-google-streaming
    snapshot_ref: sha256:891afedb041a982cd2cda18e69e62801dca2cb3a7f9d61eccb7ae5fd214aa5cc
    cited_regions:
    - audit
  - source_id: model-143-google-terms
    snapshot_ref: sha256:698c8ccbb493d4806c4424549eb84baa69ffcad3fd0e37769d89c41c74a28501
    cited_regions:
    - audit
  - source_id: model-143-google-company
    snapshot_ref: sha256:330037a17276cde421aaa59c82be2e81253a115eeb13dcad397e96f61bd8df5c
    cited_regions:
    - audit
  - source_id: model-143-google-sec
    snapshot_ref: sha256:9624fe558574d3c33ca6a6a0f9451a2fdba6e11e465de1d5a822d2e3d70042bc
    cited_regions:
    - audit
- facet: licence.commercial_use
  value: permitted_with_conditions
  state: known
  sources:
  - source_id: model-143-google-gemini-3-7-flash
    snapshot_ref: sha256:78f5cafa60ca51ba2e861fc4a1059287c17d304b220fc73f8e2950121bd0287e
    cited_regions:
    - model-spec
  - source_id: model-143-google-terms
    snapshot_ref: sha256:698c8ccbb493d4806c4424549eb84baa69ffcad3fd0e37769d89c41c74a28501
    cited_regions:
    - audit
- facet: licence.user_cap
  value: unbounded
  state: known
  sources:
  - source_id: model-143-google-gemini-3-7-flash
    snapshot_ref: sha256:78f5cafa60ca51ba2e861fc4a1059287c17d304b220fc73f8e2950121bd0287e
    cited_regions:
    - model-spec
  - source_id: model-143-google-terms
    snapshot_ref: sha256:698c8ccbb493d4806c4424549eb84baa69ffcad3fd0e37769d89c41c74a28501
    cited_regions:
    - audit
- facet: licence.output_training
  value: restricted
  state: known
  sources:
  - source_id: model-143-google-gemini-3-7-flash
    snapshot_ref: sha256:78f5cafa60ca51ba2e861fc4a1059287c17d304b220fc73f8e2950121bd0287e
    cited_regions:
    - model-spec
  - source_id: model-143-google-terms
    snapshot_ref: sha256:698c8ccbb493d4806c4424549eb84baa69ffcad3fd0e37769d89c41c74a28501
    cited_regions:
    - audit
- facet: licence.fine_tuning
  value: prohibited
  state: known
  sources:
  - source_id: model-143-google-gemini-3-7-flash
    snapshot_ref: sha256:78f5cafa60ca51ba2e861fc4a1059287c17d304b220fc73f8e2950121bd0287e
    cited_regions:
    - model-spec
  - source_id: model-143-google-terms
    snapshot_ref: sha256:698c8ccbb493d4806c4424549eb84baa69ffcad3fd0e37769d89c41c74a28501
    cited_regions:
    - audit
- facet: origin.lab_jurisdiction
  value:
  - US
  state: known
  sources:
  - source_id: model-143-google-gemini-3-7-flash
    snapshot_ref: sha256:78f5cafa60ca51ba2e861fc4a1059287c17d304b220fc73f8e2950121bd0287e
    cited_regions:
    - model-spec
  - source_id: model-143-google-deprecations
    snapshot_ref: sha256:ba167204b2fcda0540af24c209b447e7f7c93e07a93a5325914fd4921e00a8dd
    cited_regions:
    - audit
  - source_id: model-143-google-streaming
    snapshot_ref: sha256:891afedb041a982cd2cda18e69e62801dca2cb3a7f9d61eccb7ae5fd214aa5cc
    cited_regions:
    - audit
  - source_id: model-143-google-terms
    snapshot_ref: sha256:698c8ccbb493d4806c4424549eb84baa69ffcad3fd0e37769d89c41c74a28501
    cited_regions:
    - audit
  - source_id: model-143-google-company
    snapshot_ref: sha256:330037a17276cde421aaa59c82be2e81253a115eeb13dcad397e96f61bd8df5c
    cited_regions:
    - audit
  - source_id: model-143-google-sec
    snapshot_ref: sha256:9624fe558574d3c33ca6a6a0f9451a2fdba6e11e465de1d5a822d2e3d70042bc
    cited_regions:
    - audit
- facet: origin.base_lineage
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-google-gemini-3-7-flash
    snapshot_ref: sha256:78f5cafa60ca51ba2e861fc4a1059287c17d304b220fc73f8e2950121bd0287e
    cited_regions:
    - model-spec
  - source_id: model-143-google-deprecations
    snapshot_ref: sha256:ba167204b2fcda0540af24c209b447e7f7c93e07a93a5325914fd4921e00a8dd
    cited_regions:
    - audit
  - source_id: model-143-google-streaming
    snapshot_ref: sha256:891afedb041a982cd2cda18e69e62801dca2cb3a7f9d61eccb7ae5fd214aa5cc
    cited_regions:
    - audit
  - source_id: model-143-google-terms
    snapshot_ref: sha256:698c8ccbb493d4806c4424549eb84baa69ffcad3fd0e37769d89c41c74a28501
    cited_regions:
    - audit
  - source_id: model-143-google-company
    snapshot_ref: sha256:330037a17276cde421aaa59c82be2e81253a115eeb13dcad397e96f61bd8df5c
    cited_regions:
    - audit
  - source_id: model-143-google-sec
    snapshot_ref: sha256:9624fe558574d3c33ca6a6a0f9451a2fdba6e11e465de1d5a822d2e3d70042bc
    cited_regions:
    - audit
  checked_sources:
  - model-143-google-gemini-3-7-flash
  - model-143-google-deprecations
  - model-143-google-streaming
  - model-143-google-terms
  - model-143-google-company
  - model-143-google-sec
- facet: origin.weights_hosting
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-google-gemini-3-7-flash
    snapshot_ref: sha256:78f5cafa60ca51ba2e861fc4a1059287c17d304b220fc73f8e2950121bd0287e
    cited_regions:
    - model-spec
  - source_id: model-143-google-deprecations
    snapshot_ref: sha256:ba167204b2fcda0540af24c209b447e7f7c93e07a93a5325914fd4921e00a8dd
    cited_regions:
    - audit
  - source_id: model-143-google-streaming
    snapshot_ref: sha256:891afedb041a982cd2cda18e69e62801dca2cb3a7f9d61eccb7ae5fd214aa5cc
    cited_regions:
    - audit
  - source_id: model-143-google-terms
    snapshot_ref: sha256:698c8ccbb493d4806c4424549eb84baa69ffcad3fd0e37769d89c41c74a28501
    cited_regions:
    - audit
  - source_id: model-143-google-company
    snapshot_ref: sha256:330037a17276cde421aaa59c82be2e81253a115eeb13dcad397e96f61bd8df5c
    cited_regions:
    - audit
  - source_id: model-143-google-sec
    snapshot_ref: sha256:9624fe558574d3c33ca6a6a0f9451a2fdba6e11e465de1d5a822d2e3d70042bc
    cited_regions:
    - audit
  checked_sources:
  - model-143-google-gemini-3-7-flash
  - model-143-google-deprecations
  - model-143-google-streaming
  - model-143-google-terms
  - model-143-google-company
  - model-143-google-sec
- facet: model.release_date
  value: '2026-08-13'
  state: known
  sources:
  - source_id: model-143-google-gemini-3-7-flash
    snapshot_ref: sha256:78f5cafa60ca51ba2e861fc4a1059287c17d304b220fc73f8e2950121bd0287e
    cited_regions:
    - model-spec
  - source_id: model-143-google-deprecations
    snapshot_ref: sha256:ba167204b2fcda0540af24c209b447e7f7c93e07a93a5325914fd4921e00a8dd
    cited_regions:
    - audit
  - source_id: model-143-google-streaming
    snapshot_ref: sha256:891afedb041a982cd2cda18e69e62801dca2cb3a7f9d61eccb7ae5fd214aa5cc
    cited_regions:
    - audit
  - source_id: model-143-google-terms
    snapshot_ref: sha256:698c8ccbb493d4806c4424549eb84baa69ffcad3fd0e37769d89c41c74a28501
    cited_regions:
    - audit
  - source_id: model-143-google-company
    snapshot_ref: sha256:330037a17276cde421aaa59c82be2e81253a115eeb13dcad397e96f61bd8df5c
    cited_regions:
    - audit
  - source_id: model-143-google-sec
    snapshot_ref: sha256:9624fe558574d3c33ca6a6a0f9451a2fdba6e11e465de1d5a822d2e3d70042bc
    cited_regions:
    - audit
- facet: model.lifecycle
  value: active
  state: known
  sources:
  - source_id: model-143-google-gemini-3-7-flash
    snapshot_ref: sha256:78f5cafa60ca51ba2e861fc4a1059287c17d304b220fc73f8e2950121bd0287e
    cited_regions:
    - model-spec
  - source_id: model-143-google-deprecations
    snapshot_ref: sha256:ba167204b2fcda0540af24c209b447e7f7c93e07a93a5325914fd4921e00a8dd
    cited_regions:
    - audit
  - source_id: model-143-google-streaming
    snapshot_ref: sha256:891afedb041a982cd2cda18e69e62801dca2cb3a7f9d61eccb7ae5fd214aa5cc
    cited_regions:
    - audit
  - source_id: model-143-google-terms
    snapshot_ref: sha256:698c8ccbb493d4806c4424549eb84baa69ffcad3fd0e37769d89c41c74a28501
    cited_regions:
    - audit
  - source_id: model-143-google-company
    snapshot_ref: sha256:330037a17276cde421aaa59c82be2e81253a115eeb13dcad397e96f61bd8df5c
    cited_regions:
    - audit
  - source_id: model-143-google-sec
    snapshot_ref: sha256:9624fe558574d3c33ca6a6a0f9451a2fdba6e11e465de1d5a822d2e3d70042bc
    cited_regions:
    - audit
- facet: feature.tool_calling
  value: true
  state: known
  sources:
  - source_id: model-143-google-gemini-3-7-flash
    snapshot_ref: sha256:78f5cafa60ca51ba2e861fc4a1059287c17d304b220fc73f8e2950121bd0287e
    cited_regions:
    - model-spec
  - source_id: model-143-google-deprecations
    snapshot_ref: sha256:ba167204b2fcda0540af24c209b447e7f7c93e07a93a5325914fd4921e00a8dd
    cited_regions:
    - audit
  - source_id: model-143-google-streaming
    snapshot_ref: sha256:891afedb041a982cd2cda18e69e62801dca2cb3a7f9d61eccb7ae5fd214aa5cc
    cited_regions:
    - audit
  - source_id: model-143-google-terms
    snapshot_ref: sha256:698c8ccbb493d4806c4424549eb84baa69ffcad3fd0e37769d89c41c74a28501
    cited_regions:
    - audit
  - source_id: model-143-google-company
    snapshot_ref: sha256:330037a17276cde421aaa59c82be2e81253a115eeb13dcad397e96f61bd8df5c
    cited_regions:
    - audit
  - source_id: model-143-google-sec
    snapshot_ref: sha256:9624fe558574d3c33ca6a6a0f9451a2fdba6e11e465de1d5a822d2e3d70042bc
    cited_regions:
    - audit
- facet: feature.structured_output
  value: true
  state: known
  sources:
  - source_id: model-143-google-gemini-3-7-flash
    snapshot_ref: sha256:78f5cafa60ca51ba2e861fc4a1059287c17d304b220fc73f8e2950121bd0287e
    cited_regions:
    - model-spec
  - source_id: model-143-google-deprecations
    snapshot_ref: sha256:ba167204b2fcda0540af24c209b447e7f7c93e07a93a5325914fd4921e00a8dd
    cited_regions:
    - audit
  - source_id: model-143-google-streaming
    snapshot_ref: sha256:891afedb041a982cd2cda18e69e62801dca2cb3a7f9d61eccb7ae5fd214aa5cc
    cited_regions:
    - audit
  - source_id: model-143-google-terms
    snapshot_ref: sha256:698c8ccbb493d4806c4424549eb84baa69ffcad3fd0e37769d89c41c74a28501
    cited_regions:
    - audit
  - source_id: model-143-google-company
    snapshot_ref: sha256:330037a17276cde421aaa59c82be2e81253a115eeb13dcad397e96f61bd8df5c
    cited_regions:
    - audit
  - source_id: model-143-google-sec
    snapshot_ref: sha256:9624fe558574d3c33ca6a6a0f9451a2fdba6e11e465de1d5a822d2e3d70042bc
    cited_regions:
    - audit
- facet: feature.effort_controls
  value: true
  state: known
  sources:
  - source_id: model-143-google-gemini-3-7-flash
    snapshot_ref: sha256:78f5cafa60ca51ba2e861fc4a1059287c17d304b220fc73f8e2950121bd0287e
    cited_regions:
    - model-spec
  - source_id: model-143-google-deprecations
    snapshot_ref: sha256:ba167204b2fcda0540af24c209b447e7f7c93e07a93a5325914fd4921e00a8dd
    cited_regions:
    - audit
  - source_id: model-143-google-streaming
    snapshot_ref: sha256:891afedb041a982cd2cda18e69e62801dca2cb3a7f9d61eccb7ae5fd214aa5cc
    cited_regions:
    - audit
  - source_id: model-143-google-terms
    snapshot_ref: sha256:698c8ccbb493d4806c4424549eb84baa69ffcad3fd0e37769d89c41c74a28501
    cited_regions:
    - audit
  - source_id: model-143-google-company
    snapshot_ref: sha256:330037a17276cde421aaa59c82be2e81253a115eeb13dcad397e96f61bd8df5c
    cited_regions:
    - audit
  - source_id: model-143-google-sec
    snapshot_ref: sha256:9624fe558574d3c33ca6a6a0f9451a2fdba6e11e465de1d5a822d2e3d70042bc
    cited_regions:
    - audit
- facet: feature.batch
  value: true
  state: known
  sources:
  - source_id: model-143-google-gemini-3-7-flash
    snapshot_ref: sha256:78f5cafa60ca51ba2e861fc4a1059287c17d304b220fc73f8e2950121bd0287e
    cited_regions:
    - model-spec
  - source_id: model-143-google-deprecations
    snapshot_ref: sha256:ba167204b2fcda0540af24c209b447e7f7c93e07a93a5325914fd4921e00a8dd
    cited_regions:
    - audit
  - source_id: model-143-google-streaming
    snapshot_ref: sha256:891afedb041a982cd2cda18e69e62801dca2cb3a7f9d61eccb7ae5fd214aa5cc
    cited_regions:
    - audit
  - source_id: model-143-google-terms
    snapshot_ref: sha256:698c8ccbb493d4806c4424549eb84baa69ffcad3fd0e37769d89c41c74a28501
    cited_regions:
    - audit
  - source_id: model-143-google-company
    snapshot_ref: sha256:330037a17276cde421aaa59c82be2e81253a115eeb13dcad397e96f61bd8df5c
    cited_regions:
    - audit
  - source_id: model-143-google-sec
    snapshot_ref: sha256:9624fe558574d3c33ca6a6a0f9451a2fdba6e11e465de1d5a822d2e3d70042bc
    cited_regions:
    - audit
- facet: feature.streaming
  value: true
  state: known
  sources:
  - source_id: model-143-google-gemini-3-7-flash
    snapshot_ref: sha256:78f5cafa60ca51ba2e861fc4a1059287c17d304b220fc73f8e2950121bd0287e
    cited_regions:
    - model-spec
  - source_id: model-143-google-deprecations
    snapshot_ref: sha256:ba167204b2fcda0540af24c209b447e7f7c93e07a93a5325914fd4921e00a8dd
    cited_regions:
    - audit
  - source_id: model-143-google-streaming
    snapshot_ref: sha256:891afedb041a982cd2cda18e69e62801dca2cb3a7f9d61eccb7ae5fd214aa5cc
    cited_regions:
    - audit
  - source_id: model-143-google-terms
    snapshot_ref: sha256:698c8ccbb493d4806c4424549eb84baa69ffcad3fd0e37769d89c41c74a28501
    cited_regions:
    - audit
  - source_id: model-143-google-company
    snapshot_ref: sha256:330037a17276cde421aaa59c82be2e81253a115eeb13dcad397e96f61bd8df5c
    cited_regions:
    - audit
  - source_id: model-143-google-sec
    snapshot_ref: sha256:9624fe558574d3c33ca6a6a0f9451a2fdba6e11e465de1d5a822d2e3d70042bc
    cited_regions:
    - audit
- id: google/gemini-3-7-flash#model.fits_hardware
  subject:
    kind: model
    id: google/gemini-3-7-flash
  facet: model.fits_hardware
  value: []
  state: known
  derivation:
    method: decision.hardware.compute_fit@1
    formula: parameters_total * bytes_per_parameter <= memory_capacity_gb * (1 - working_allowance) *
      1e9
    inputs:
      weights_openness: closed_weights
      parameters_total: null
      working_allowance: 0.25
      quant_bytes: '{''bf16'': 2.0, ''fp16'': 2.0, ''fp8'': 1.0, ''int4'': 0.5, ''int8'': 1.0, ''q4'':
        0.5, ''q5'': 0.625, ''q6'': 0.75}'
      has_device_unknowns: 'false'
      model_snapshot_ref: sha256:78f5cafa60ca51ba2e861fc4a1059287c17d304b220fc73f8e2950121bd0287e
      hardware_registry_sha256: sha256:10baf5e1ce9e5a1e5b970f4fdc25d9f67db8c562c8c109157ae9722bf6357bff
      hardware_device_count: 64
  sources:
  - source_id: model-143-google-gemini-3-7-flash
    snapshot_ref: sha256:78f5cafa60ca51ba2e861fc4a1059287c17d304b220fc73f8e2950121bd0287e
    cited_regions:
    - model-spec
  - source_id: model-143-google-deprecations
    snapshot_ref: sha256:ba167204b2fcda0540af24c209b447e7f7c93e07a93a5325914fd4921e00a8dd
    cited_regions:
    - audit
  - source_id: model-143-google-streaming
    snapshot_ref: sha256:891afedb041a982cd2cda18e69e62801dca2cb3a7f9d61eccb7ae5fd214aa5cc
    cited_regions:
    - audit
  - source_id: model-143-google-terms
    snapshot_ref: sha256:698c8ccbb493d4806c4424549eb84baa69ffcad3fd0e37769d89c41c74a28501
    cited_regions:
    - audit
  - source_id: model-143-google-company
    snapshot_ref: sha256:330037a17276cde421aaa59c82be2e81253a115eeb13dcad397e96f61bd8df5c
    cited_regions:
    - audit
  - source_id: model-143-google-sec
    snapshot_ref: sha256:9624fe558574d3c33ca6a6a0f9451a2fdba6e11e465de1d5a822d2e3d70042bc
    cited_regions:
    - audit
card_schema_version: '3.0'
card_author: models.dev-seeder
card_created: '2026-04-05'
card_updated: '2026-09-28'
---

# Gemini 3.7 Flash

Gemini 3.7 Flash is a Llm Reasoning model from Google DeepMind. Part of the gemini-flash family. Knowledge cutoff: 2026-03.

## Key Features
- Extended reasoning / chain-of-thought
- Function calling / tool use
- Structured output (JSON mode)
- File/image attachments
