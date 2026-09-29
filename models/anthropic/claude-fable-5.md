---
model_id: anthropic/claude-fable-5
display_name: Claude Fable 5
provider: anthropic
provider_display: Anthropic
family: claude-fable
version: claude-fable-5
release_date: '2026-06-07'
last_updated: '2026-06-09'
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
  - pdf
  output:
  - text
  text:
    max_input_tokens: null
    max_output_tokens: 128000
    context_window: 1000000
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
  input: 10.0
  output: 50.0
  reasoning: null
  cache_read: 1.0
  cache_write: 12.5
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
    model_id_as_evaluated: claude-fable-5
    score: 1505.68
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / overall, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category overall,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1505.68 [1500.92, 1510.45], 30057
      votes, rank 1.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: anthropic/claude-fable-5#arena_elo_style_control#c0987d80ba01
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
    model_id_as_evaluated: claude-fable-5
    score: 1552.39
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / coding, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category coding,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1552.39 [1544.95, 1559.84], 8040
      votes, rank 1.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: anthropic/claude-fable-5#arena_sc_coding#e1119f5239dd
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
    model_id_as_evaluated: claude-fable-5
    score: 1532.14
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / hard_prompts, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category hard_prompts,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1532.14 [1526.64, 1537.64], 19784
      votes, rank 2.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: anthropic/claude-fable-5#arena_sc_hard_prompts#4f73ec29df58
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
    model_id_as_evaluated: claude-fable-5
    score: 1526.28
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / math, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category math, leaderboard_publish_date
      2026-09-13; style control. Highest-effort row for the product (effort: default; MODEL-123
      max-effort rule). Rating 1526.28 [1510.73, 1541.84], 1467 votes, rank 1.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: anthropic/claude-fable-5#arena_sc_math#b8f05e428fa3
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
    model_id_as_evaluated: claude-fable-5
    score: 1504.13
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / creative_writing, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category creative_writing,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1504.13 [1495.53, 1512.74], 6073
      votes, rank 1.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: anthropic/claude-fable-5#arena_sc_creative_writing#9812345d64ed
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
    model_id_as_evaluated: claude-fable-5
    score: 1511.3
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / instruction_following, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category instruction_following,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1511.30 [1504.54, 1518.05], 10641
      votes, rank 2.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: anthropic/claude-fable-5#arena_sc_instruction_following#1f18b76a33b3
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
    model_id_as_evaluated: claude-fable-5
    score: 1517.56
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / multi_turn, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category multi_turn,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1517.56 [1508.49, 1526.62], 5048
      votes, rank 2.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: anthropic/claude-fable-5#arena_sc_multi_turn#e1ddeb68e213
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
    model_id_as_evaluated: claude-fable-5
    score: 1548.48
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / expert, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category expert,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1548.48 [1537.58, 1559.38], 3257
      votes, rank 1.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: anthropic/claude-fable-5#arena_sc_expert#a8739177720d
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
    model_id_as_evaluated: claude-fable-5
    score: 1521.41
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / longer_query, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category longer_query,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1521.41 [1515.07, 1527.74], 13819
      votes, rank 2.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: anthropic/claude-fable-5#arena_sc_longer_query#17784fed28db
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
    model_id_as_evaluated: claude-fable-5
    score: 1495.98
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / non_english, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category non_english,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1495.98 [1490.31, 1501.64], 16958
      votes, rank 1.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: anthropic/claude-fable-5#arena_sc_non_english#50b8aef00bfc
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
    model_id_as_evaluated: claude-fable-5
    score: 1505.28
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
      (effort: default; MODEL-123 max-effort rule). Rating 1505.28 [1491.65, 1518.90], 2125
      votes, rank 10.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: anthropic/claude-fable-5#arena_sc_medicine#020db3a3fd8a
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
    model_id_as_evaluated: claude-fable-5
    score: 1512.36
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
      (effort: default; MODEL-123 max-effort rule). Rating 1512.36 [1499.80, 1524.91], 2509
      votes, rank 2.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: anthropic/claude-fable-5#arena_sc_legal#0266d8239bfe
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
    model_id_as_evaluated: claude-fable-5
    score: 1501.64
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
      (effort: default; MODEL-123 max-effort rule). Rating 1501.64 [1493.40, 1509.88], 6169
      votes, rank 3.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: anthropic/claude-fable-5#arena_sc_business#408ac5d2cfbf
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
    model_id_as_evaluated: claude-fable-5
    score: 1528.15
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
      (effort: default; MODEL-123 max-effort rule). Rating 1528.15 [1519.08, 1537.23], 4806
      votes, rank 1.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: anthropic/claude-fable-5#arena_sc_science#f7d8442ac8e6
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
    model_id_as_evaluated: claude-fable-5
    score: 1511.45
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
      (effort: default; MODEL-123 max-effort rule). Rating 1511.45 [1503.93, 1518.97], 8123
      votes, rank 1.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: anthropic/claude-fable-5#arena_sc_writing#c84145aff92c
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
    model_id_as_evaluated: claude-fable-5
    score: 1309.5
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: vision_style_control / overall, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset vision_style_control, category overall,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1309.50 [1301.57, 1317.44], 11304
      votes, rank 1.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: anthropic/claude-fable-5#arena_sc_vision#67b18972954e
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
    model_id_as_evaluated: claude-fable-5-high
    score: 1626.83
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-23'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: webdev / overall, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset webdev, category overall, leaderboard_publish_date
      2026-09-23; no style-controlled variant. Highest-effort row for the product (effort: high;
      MODEL-123 max-effort rule). Rating 1626.83 [1619.88, 1633.78], 11933 votes, rank 14.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: anthropic/claude-fable-5#arena_webdev#efbde51ffe75
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
    model_id_as_evaluated: claude-fable-5_max
    score: 85.86
    unit: percent
    source_url: https://epoch.ai/benchmarks/gpqa-diamond
    source_kind: independent_evaluator
    evidence_date: '2026-08-06'
    date_type: evaluated
    verified_at: '2026-09-29'
    benchmark_version: GPQA Diamond (Epoch AI run)
    configuration: Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (gpqa_diamond.csv),
      read 2026-09-24. Run started 2026-08-06T22:17:56.000Z; effort max; highest-effort run
      for the model (MODEL-123 max-effort rule), newest on a tie. Standard error 2.48 points.
    limitations: Epoch AI data, CC BY 4.0.
    id: anthropic/claude-fable-5#gpqa_diamond#5b91135baa58
    measured_by: independent_evaluator
    effort: max
    harness: null
    sources:
    - source_id: model-143-evidence-epoch-gpqa-diamond-csv
      snapshot_ref: sha256:946618a3befb5210ccf841c8f3c6b257584d10d5314a7e03408fb73aa13a38a9
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: frontiermath_tiers_1_3_v2
    model_id_as_evaluated: claude-fable-5_max
    score: 87.02
    unit: percent
    source_url: https://epoch.ai/frontiermath
    source_kind: independent_evaluator
    evidence_date: '2026-06-09'
    date_type: evaluated
    verified_at: '2026-09-29'
    benchmark_version: FrontierMath-Tiers-1-3-v2-Private (Epoch AI run)
    configuration: Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (frontiermath_tiers_1_3_v2.csv),
      read 2026-09-24. Run started 2026-06-09T18:12:35.000Z; effort max; highest-effort run
      for the model (MODEL-123 max-effort rule), newest on a tie. Standard error 1.99 points.
    limitations: Epoch AI data, CC BY 4.0.
    id: anthropic/claude-fable-5#frontiermath_tiers_1_3_v2#3d8e81975798
    measured_by: independent_evaluator
    effort: max
    harness: null
    sources:
    - source_id: model-143-evidence-epoch-frontiermath-tiers-1-3-v2-csv
      snapshot_ref: sha256:ff8b653f9ba2c936d6278eeecc42b3a3dee1079e409c8806616f80fb41e23c11
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: simpleqa_verified
    model_id_as_evaluated: claude-fable-5_xhigh
    score: 70.7
    unit: percent
    source_url: https://epoch.ai/benchmarks/simpleqa-verified
    source_kind: independent_evaluator
    evidence_date: '2026-08-10'
    date_type: evaluated
    verified_at: '2026-09-29'
    benchmark_version: SimpleQA Verified, proportion correct, Epoch AI protocol with anti-abstention
      prompt
    configuration: Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (simpleqa_verified.csv),
      read 2026-09-24. Run started 2026-08-10T23:44:03.000Z; effort xhigh; highest-effort run
      for the model (MODEL-123 max-effort rule), newest on a tie. Standard error 1.44 points.
    limitations: Epoch AI data, CC BY 4.0.
    id: anthropic/claude-fable-5#simpleqa_verified#54f34fcf1fe3
    measured_by: independent_evaluator
    effort: xhigh
    harness: null
    sources:
    - source_id: model-160-epoch-simpleqa-verified-csv
      snapshot_ref: sha256:f4e88f5154755ef9c355b28d6900467dce89bcbe0ea54329d1f96215c21239fa
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: frontiercode_v1_1
    model_id_as_evaluated: Fable 5
    score: 53.5
    unit: percent
    source_url: https://cognition.com/frontiercode
    source_kind: benchmark_author
    evidence_date: '2026-09-29'
    date_type: evaluated
    verified_at: '2026-09-29'
    benchmark_version: FrontierCode 1.1, main score (Mean@5)
    configuration: Board row as copied in Epoch AI's benchmark data (frontiercode_external.csv,
      https://epoch.ai/data/benchmark_data.zip), read 2026-09-24. Effort xhigh; the highest-effort
      row for the model (MODEL-123 max-effort rule). Harness claude-code.
    limitations: A live board's standing, dated by the day ModelSpec read Epoch AI's copy; the
      copy carries no per-row date. Epoch AI data, CC BY 4.0.
    id: anthropic/claude-fable-5#frontiercode_v1_1#9040ccbe31ae
    measured_by: benchmark_author
    effort: xhigh
    harness: unregistered
    sources:
    - source_id: model-160-frontiercode
      snapshot_ref: sha256:946a90057bea730dbfa5a27ab38168e01b5269492c1b41f46cf4ec29dd0d3cf3
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: vending_bench_2
    model_id_as_evaluated: Claude Fable 5 - Max
    score: 4966.64
    unit: USD
    source_url: https://andonlabs.com/evals/vending-bench-2
    source_kind: benchmark_author
    evidence_date: '2026-09-29'
    date_type: evaluated
    verified_at: '2026-09-29'
    benchmark_version: Vending-Bench 2, mean final balance over 5 runs
    configuration: Board row as copied in Epoch AI's benchmark data (vending_bench_2_external.csv,
      https://epoch.ai/data/benchmark_data.zip), read 2026-09-24. Effort max; the highest-effort
      row for the model (MODEL-123 max-effort rule).
    limitations: A live board's standing, dated by the day ModelSpec read Epoch AI's copy; the
      copy carries no per-row date. Epoch AI data, CC BY 4.0.
    id: anthropic/claude-fable-5#vending_bench_2#dfe0ba043ba0
    measured_by: benchmark_author
    effort: max
    harness: null
    sources:
    - source_id: model-160-vending-bench-2
      snapshot_ref: sha256:94074584ec83e973b31884f48956a6bc43e36a33d47dc3feaa7c52adf23a9c12
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: deepswe_v1_1
    model_id_as_evaluated: claude-fable-5 (max)
    score: 69.72
    unit: percent
    source_url: https://deepswe.datacurve.ai/
    source_kind: benchmark_author
    evidence_date: '2026-09-29'
    date_type: evaluated
    verified_at: '2026-09-29'
    benchmark_version: DeepSWE v1.1, pass@1, mini-swe-agent
    configuration: Board row as copied in Epoch AI's benchmark data (deepswe_external.csv, https://epoch.ai/data/benchmark_data.zip),
      read 2026-09-24. Effort max; the highest-effort row for the model (MODEL-123 max-effort
      rule). Harness mini-swe-agent.
    limitations: A live board's standing, dated by the day ModelSpec read Epoch AI's copy; the
      copy carries no per-row date. Epoch AI data, CC BY 4.0.
    id: anthropic/claude-fable-5#deepswe_v1_1#7baad782fe25
    measured_by: benchmark_author
    effort: max
    harness: unregistered
    sources:
    - source_id: model-160-deepswe-v1-1
      snapshot_ref: sha256:33c505b573a474e601643fe1e1295b91b10e3ef62dfeab167a3851226358c972
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: terminal_bench_v4_0
    model_id_as_evaluated: Fable 5
    score: 44.55
    unit: percent
    source_url: https://www.tbench.ai/leaderboard/terminal-bench/4.0
    source_kind: benchmark_author
    evidence_date: '2026-06-09'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: Terminal-Bench 4.0
    configuration: 'tbench.ai leaderboard row read 2026-09-24: agent Claude Code (Anthropic),
      reasoning effort max, 330 trials, accuracy 44.55 ± 3.85 (95% CI). The board''s row date
      is the evidence date. Highest-effort row for the model, best agent on a tie.'
    limitations: The agent harness differs between rows; compare rows with the same agent.
    id: anthropic/claude-fable-5#terminal_bench_v4_0#6d3dc7a08de0
    measured_by: benchmark_author
    effort: max
    harness: unregistered
    sources:
    - source_id: model-143-evidence-terminal-bench-4-0-json
      snapshot_ref: sha256:ea8d2644137b35340e437581fd626baeb200138b503f17f66f91fdf8eaf7f701
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: tau3_banking
    model_id_as_evaluated: Claude Fable 5 (max)
    score: 39.69
    unit: percent
    source_url: https://sierra-tau-bench-public.s3.us-west-2.amazonaws.com/submissions/claude-fable-5_sierra_2026-08-04/submission.json
    source_kind: benchmark_author
    evidence_date: '2026-07-23'
    date_type: evaluated
    verified_at: '2026-09-29'
    benchmark_version: τ-Knowledge τ-Banking (banking_knowledge), pass^1
    configuration: τ-bench leaderboard submission claude-fable-5_sierra_2026-08-04, submitted
      by Sierra; retrieval config alltools; reasoning effort max; user simulator gpt-5.2; tau2-bench
      1.0.1. pass^4 28.865979381443296.
    limitations: Banking_knowledge evaluation with AllTools retrieval, GPT-5.2 low-reasoning
      user simulation, four trials, and seed 300.
    id: anthropic/claude-fable-5#tau3_banking#5c6b6916124d
    measured_by: benchmark_author
    effort: max
    harness: null
    sources:
    - source_id: model-160-tau-bench-claude-fable-5-sierra-2026-08-04
      snapshot_ref: sha256:7302aa2a55915f2c6d1245acffc7a4cf0839485777f8e76b4a20f481cbe4355c
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_english
    model_id_as_evaluated: claude-fable-5
    score: 1513.18
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / english, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1513.18 [1507.05,
      1519.31], 13092 votes, rank 2. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:cee57baa7239c5aa2091dcb5db0b4c2ac22cec732b235d66c0cda2ee55bdcb44
      cited_regions:
      - rows
    id: anthropic/claude-fable-5#arena_sc_english#816a59bf4aae
  - benchmark_id: arena_sc_chinese
    model_id_as_evaluated: claude-fable-5
    score: 1553.41
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / chinese, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1553.41 [1538.95,
      1567.87], 1873 votes, rank 5. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:9bf00fc37e8a997735f423949aba6ffc5551990b6f835297d3fed2b364abe02b
      cited_regions:
      - rows
    id: anthropic/claude-fable-5#arena_sc_chinese#6f452f53023f
  - benchmark_id: arena_sc_japanese
    model_id_as_evaluated: claude-fable-5
    score: 1523.48
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / japanese, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1523.48 [1493.19,
      1553.76], 423 votes, rank 1. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:13b68c219a1ec549a9336846ddacaf97471f6323c09e4f45a73eab7a0857a9ca
      cited_regions:
      - rows
    id: anthropic/claude-fable-5#arena_sc_japanese#1a5a34613d61
  - benchmark_id: arena_sc_korean
    model_id_as_evaluated: claude-fable-5
    score: 1500.04
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / korean, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1500.04 [1474.41,
      1525.67], 600 votes, rank 2. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:96706e685de18541b6ad515db22607a7840bad8bc902a30a8a38f949cd409c08
      cited_regions:
      - rows
    id: anthropic/claude-fable-5#arena_sc_korean#e8dedf6e4984
  - benchmark_id: arena_sc_russian
    model_id_as_evaluated: claude-fable-5
    score: 1518.83
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / russian, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1518.83 [1507.60,
      1530.06], 3055 votes, rank 1. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:eb77af068077fa90a9514ad454b6a65f061a176f0d68897132e1526f3be743dd
      cited_regions:
      - rows
    id: anthropic/claude-fable-5#arena_sc_russian#1a072d6e0e8e
  - benchmark_id: arena_sc_spanish
    model_id_as_evaluated: claude-fable-5
    score: 1514.49
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / spanish, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1514.49 [1494.61,
      1534.37], 981 votes, rank 1. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:e56e27431afb859f3376e3d5609785906e24647b4c0c65a324b7995944b9573b
      cited_regions:
      - rows
    id: anthropic/claude-fable-5#arena_sc_spanish#c99f419bbbd2
  - benchmark_id: arena_sc_german
    model_id_as_evaluated: claude-fable-5
    score: 1497.46
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / german, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1497.46 [1470.31,
      1524.60], 490 votes, rank 10. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:098d6730e0b426da68eee86ddfd97bb03c3b1048e178378de1ec3924fa209c6d
      cited_regions:
      - rows
    id: anthropic/claude-fable-5#arena_sc_german#1bd05e86bfd1
  - benchmark_id: arena_sc_french
    model_id_as_evaluated: claude-fable-5
    score: 1523.06
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / french, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1523.06 [1503.48,
      1542.64], 1083 votes, rank 3. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:c6c9f83eb7147bedac479a445a3803aad09d613643414d3cd5035dbde46d6f2f
      cited_regions:
      - rows
    id: anthropic/claude-fable-5#arena_sc_french#4231c1167250
  - benchmark_id: arena_sc_polish
    model_id_as_evaluated: claude-fable-5
    score: 1504.81
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / polish, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1504.81 [1478.72,
      1530.89], 481 votes, rank 3. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:a99daf2dc2fbf9b06de90a127cc1408c7a19e4fa45a1a4d538b668211c4b5892
      cited_regions:
      - rows
    id: anthropic/claude-fable-5#arena_sc_polish#0027824c7290
  - benchmark_id: arena_sc_vision_ocr
    model_id_as_evaluated: claude-fable-5
    score: 1325.36
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: vision_style_control / ocr, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1325.36 [1317.09,
      1333.63], 8040 votes, rank 1. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-vision-style-control
      snapshot_ref: sha256:72ff33856df7c05e7611f78bd6f0a13fc422694ad107f25e00c11b10edb14422
      cited_regions:
      - rows
    id: anthropic/claude-fable-5#arena_sc_vision_ocr#c41b585ef1b7
  - benchmark_id: arena_sc_vision_diagram
    model_id_as_evaluated: claude-fable-5
    score: 1355.26
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: vision_style_control / diagram, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1355.26 [1343.57,
      1366.95], 3051 votes, rank 1. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-vision-style-control
      snapshot_ref: sha256:f70ad4aae81aa8b6cca27735001f45704e13f64af12ad93244cd19ca60d98085
      cited_regions:
      - rows
    id: anthropic/claude-fable-5#arena_sc_vision_diagram#a1eaaf9637fb
  - benchmark_id: arena_sc_vision_homework
    model_id_as_evaluated: claude-fable-5
    score: 1343.28
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: vision_style_control / homework, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1343.28 [1326.31,
      1360.26], 1318 votes, rank 2. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-vision-style-control
      snapshot_ref: sha256:8015c65e88084d6c6b25f9787fb1528f550abd8e055cf8f3b753e863296d3176
      cited_regions:
      - rows
    id: anthropic/claude-fable-5#arena_sc_vision_homework#5071ab40219d
  - benchmark_id: arena_sc_document
    model_id_as_evaluated: claude-fable-5
    score: 1496.08
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: document / overall, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1496.08 [1488.22,
      1503.94], 8497 votes, rank 5. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-document
      snapshot_ref: sha256:050705ac3c2e5ba81aacf700b87f5144dd7b0ec9f7f12168be5086b1c11be958
      cited_regions:
      - rows
    id: anthropic/claude-fable-5#arena_sc_document#14e64ff8651a
  - benchmark_id: arena_sc_industry_software_it_services
    model_id_as_evaluated: claude-fable-5
    score: 1539.64
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / industry_software_and_it_services, latest split, revision
      1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1539.64 [1533.17,
      1546.11], 11470 votes, rank 3. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:4eaa9890dce0719aa263af890c9f2a7bb1a3198e291d84dbf8c1371d4f150c52
      cited_regions:
      - rows
    id: anthropic/claude-fable-5#arena_sc_industry_software_it_services#159935694d97
  - benchmark_id: arena_sc_industry_entertainment_sports_media
    model_id_as_evaluated: claude-fable-5
    score: 1495.88
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / industry_entertainment_and_sports_and_media, latest
      split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1495.88 [1488.10,
      1503.67], 7578 votes, rank 1. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:df0d5e7c4d4ce1f683618242c0786eafd164d98b3b49dbaa6e699476bec94ccf
      cited_regions:
      - rows
    id: anthropic/claude-fable-5#arena_sc_industry_entertainment_sports_media#1e158e54dff3
  - benchmark_id: arena_sc_industry_mathematical
    model_id_as_evaluated: claude-fable-5
    score: 1516.32
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / industry_mathematical, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1516.32 [1501.28,
      1531.36], 1651 votes, rank 4. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:b0f3ee924239a7a9a1e60676935d0c83091f29517b8acb95e07868e370822e82
      cited_regions:
      - rows
    id: anthropic/claude-fable-5#arena_sc_industry_mathematical#dbabc2681bb8
  - benchmark_id: arena_sc_factuality
    model_id_as_evaluated: claude-fable-5
    score: 1484.03
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_factuality / overall, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1484.03 [1480.27,
      1487.79], 29855 votes, rank 10. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-factuality
      snapshot_ref: sha256:ece0fd0afe2b42a38bce698a6be5329044b5503f5edb7f43473c19394b38fc28
      cited_regions:
      - rows
    id: anthropic/claude-fable-5#arena_sc_factuality#437401b5195c
  - benchmark_id: finance_benchmark_v2
    model_id_as_evaluated: anthropic/claude-fable-5
    score: 90.411
    unit: percent
    source_url: https://finbenchmark.ai/
    source_kind: independent_evaluator
    evidence_date: '2026-07-06'
    date_type: evaluated
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: Finance Benchmark v2, harness 0.2.0
    configuration: 73 v2 tasks; three attempts per task; temperature zero.
    limitations: Passes at least once, so this value does not measure repeated-run consistency.
    measured_by: independent_evaluator
    effort: null
    harness: unregistered
    sources:
    - source_id: model-192-finance-benchmark-v2
      snapshot_ref: sha256:9e10ecf98bc44ca664396e7a752fd46c9a08466f368aa35c8ff6456b0f1c4540
      cited_regions:
      - rows
    id: anthropic/claude-fable-5#finance_benchmark_v2#928d1896fdc0
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
  models_dev_url: https://models.dev/anthropic
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
  - source_id: model-143-anthropic-claude-fable-5
    snapshot_ref: sha256:1ea0e92587855d9cc6695e742a294b76f7a8209a492b3f2cdf8aa6f4f36dca13
    cited_regions:
    - model-spec
  - source_id: model-143-anthropic-models-overview
    snapshot_ref: sha256:081fd4411b01088963ae62e43b378ba3c708843c5f553c277371f014a02bc65f
    cited_regions:
    - audit
  - source_id: model-143-anthropic-structured-outputs
    snapshot_ref: sha256:b93fe8ddc691cd8f9a022aacc8c3adabf38c9e8ed215ae955d61939ee64abaf9
    cited_regions:
    - audit
  - source_id: model-143-anthropic-streaming
    snapshot_ref: sha256:cdc7449de7d6829e2f611641ce1fcec68564814fd54ab3398c559189073b6f69
    cited_regions:
    - audit
  - source_id: model-143-anthropic-commercial-terms
    snapshot_ref: sha256:cfb59d90c8b31ffb9c1e3a0b95bff416c7b3d19218eb3c15e8d0169ea36caeca
    cited_regions:
    - audit
- facet: model.input_modalities
  value:
  - text
  - image
  - document
  state: known
  sources:
  - source_id: model-143-anthropic-claude-fable-5
    snapshot_ref: sha256:1ea0e92587855d9cc6695e742a294b76f7a8209a492b3f2cdf8aa6f4f36dca13
    cited_regions:
    - model-spec
  - source_id: model-143-anthropic-models-overview
    snapshot_ref: sha256:081fd4411b01088963ae62e43b378ba3c708843c5f553c277371f014a02bc65f
    cited_regions:
    - audit
  - source_id: model-143-anthropic-structured-outputs
    snapshot_ref: sha256:b93fe8ddc691cd8f9a022aacc8c3adabf38c9e8ed215ae955d61939ee64abaf9
    cited_regions:
    - audit
  - source_id: model-143-anthropic-streaming
    snapshot_ref: sha256:cdc7449de7d6829e2f611641ce1fcec68564814fd54ab3398c559189073b6f69
    cited_regions:
    - audit
  - source_id: model-143-anthropic-commercial-terms
    snapshot_ref: sha256:cfb59d90c8b31ffb9c1e3a0b95bff416c7b3d19218eb3c15e8d0169ea36caeca
    cited_regions:
    - audit
- facet: model.output_modalities
  value:
  - text
  state: known
  sources:
  - source_id: model-143-anthropic-claude-fable-5
    snapshot_ref: sha256:1ea0e92587855d9cc6695e742a294b76f7a8209a492b3f2cdf8aa6f4f36dca13
    cited_regions:
    - model-spec
  - source_id: model-143-anthropic-models-overview
    snapshot_ref: sha256:081fd4411b01088963ae62e43b378ba3c708843c5f553c277371f014a02bc65f
    cited_regions:
    - audit
  - source_id: model-143-anthropic-structured-outputs
    snapshot_ref: sha256:b93fe8ddc691cd8f9a022aacc8c3adabf38c9e8ed215ae955d61939ee64abaf9
    cited_regions:
    - audit
  - source_id: model-143-anthropic-streaming
    snapshot_ref: sha256:cdc7449de7d6829e2f611641ce1fcec68564814fd54ab3398c559189073b6f69
    cited_regions:
    - audit
  - source_id: model-143-anthropic-commercial-terms
    snapshot_ref: sha256:cfb59d90c8b31ffb9c1e3a0b95bff416c7b3d19218eb3c15e8d0169ea36caeca
    cited_regions:
    - audit
- facet: model.context_window
  value: 1000000
  state: known
  sources:
  - source_id: model-143-anthropic-claude-fable-5
    snapshot_ref: sha256:1ea0e92587855d9cc6695e742a294b76f7a8209a492b3f2cdf8aa6f4f36dca13
    cited_regions:
    - model-spec
  - source_id: model-143-anthropic-models-overview
    snapshot_ref: sha256:081fd4411b01088963ae62e43b378ba3c708843c5f553c277371f014a02bc65f
    cited_regions:
    - audit
  - source_id: model-143-anthropic-structured-outputs
    snapshot_ref: sha256:b93fe8ddc691cd8f9a022aacc8c3adabf38c9e8ed215ae955d61939ee64abaf9
    cited_regions:
    - audit
  - source_id: model-143-anthropic-streaming
    snapshot_ref: sha256:cdc7449de7d6829e2f611641ce1fcec68564814fd54ab3398c559189073b6f69
    cited_regions:
    - audit
  - source_id: model-143-anthropic-commercial-terms
    snapshot_ref: sha256:cfb59d90c8b31ffb9c1e3a0b95bff416c7b3d19218eb3c15e8d0169ea36caeca
    cited_regions:
    - audit
- facet: model.max_output_tokens
  value: 128000
  state: known
  sources:
  - source_id: model-143-anthropic-claude-fable-5
    snapshot_ref: sha256:1ea0e92587855d9cc6695e742a294b76f7a8209a492b3f2cdf8aa6f4f36dca13
    cited_regions:
    - model-spec
  - source_id: model-143-anthropic-models-overview
    snapshot_ref: sha256:081fd4411b01088963ae62e43b378ba3c708843c5f553c277371f014a02bc65f
    cited_regions:
    - audit
  - source_id: model-143-anthropic-structured-outputs
    snapshot_ref: sha256:b93fe8ddc691cd8f9a022aacc8c3adabf38c9e8ed215ae955d61939ee64abaf9
    cited_regions:
    - audit
  - source_id: model-143-anthropic-streaming
    snapshot_ref: sha256:cdc7449de7d6829e2f611641ce1fcec68564814fd54ab3398c559189073b6f69
    cited_regions:
    - audit
  - source_id: model-143-anthropic-commercial-terms
    snapshot_ref: sha256:cfb59d90c8b31ffb9c1e3a0b95bff416c7b3d19218eb3c15e8d0169ea36caeca
    cited_regions:
    - audit
- facet: model.weights_openness
  value: closed_weights
  state: known
  sources:
  - source_id: model-143-anthropic-claude-fable-5
    snapshot_ref: sha256:1ea0e92587855d9cc6695e742a294b76f7a8209a492b3f2cdf8aa6f4f36dca13
    cited_regions:
    - model-spec
  - source_id: model-143-anthropic-models-overview
    snapshot_ref: sha256:081fd4411b01088963ae62e43b378ba3c708843c5f553c277371f014a02bc65f
    cited_regions:
    - audit
  - source_id: model-143-anthropic-structured-outputs
    snapshot_ref: sha256:b93fe8ddc691cd8f9a022aacc8c3adabf38c9e8ed215ae955d61939ee64abaf9
    cited_regions:
    - audit
  - source_id: model-143-anthropic-streaming
    snapshot_ref: sha256:cdc7449de7d6829e2f611641ce1fcec68564814fd54ab3398c559189073b6f69
    cited_regions:
    - audit
  - source_id: model-143-anthropic-commercial-terms
    snapshot_ref: sha256:cfb59d90c8b31ffb9c1e3a0b95bff416c7b3d19218eb3c15e8d0169ea36caeca
    cited_regions:
    - audit
- facet: licence.commercial_use
  value: permitted_with_conditions
  state: known
  sources:
  - source_id: model-143-anthropic-claude-fable-5
    snapshot_ref: sha256:1ea0e92587855d9cc6695e742a294b76f7a8209a492b3f2cdf8aa6f4f36dca13
    cited_regions:
    - model-spec
  - source_id: model-143-anthropic-commercial-terms
    snapshot_ref: sha256:cfb59d90c8b31ffb9c1e3a0b95bff416c7b3d19218eb3c15e8d0169ea36caeca
    cited_regions:
    - audit
- facet: licence.user_cap
  value: unbounded
  state: known
  sources:
  - source_id: model-143-anthropic-claude-fable-5
    snapshot_ref: sha256:1ea0e92587855d9cc6695e742a294b76f7a8209a492b3f2cdf8aa6f4f36dca13
    cited_regions:
    - model-spec
  - source_id: model-143-anthropic-commercial-terms
    snapshot_ref: sha256:cfb59d90c8b31ffb9c1e3a0b95bff416c7b3d19218eb3c15e8d0169ea36caeca
    cited_regions:
    - audit
- facet: licence.output_training
  value: restricted
  state: known
  sources:
  - source_id: model-143-anthropic-claude-fable-5
    snapshot_ref: sha256:1ea0e92587855d9cc6695e742a294b76f7a8209a492b3f2cdf8aa6f4f36dca13
    cited_regions:
    - model-spec
  - source_id: model-143-anthropic-commercial-terms
    snapshot_ref: sha256:cfb59d90c8b31ffb9c1e3a0b95bff416c7b3d19218eb3c15e8d0169ea36caeca
    cited_regions:
    - audit
- facet: licence.fine_tuning
  value: prohibited
  state: known
  sources:
  - source_id: model-143-anthropic-claude-fable-5
    snapshot_ref: sha256:1ea0e92587855d9cc6695e742a294b76f7a8209a492b3f2cdf8aa6f4f36dca13
    cited_regions:
    - model-spec
  - source_id: model-143-anthropic-commercial-terms
    snapshot_ref: sha256:cfb59d90c8b31ffb9c1e3a0b95bff416c7b3d19218eb3c15e8d0169ea36caeca
    cited_regions:
    - audit
- facet: origin.lab_jurisdiction
  value:
  - US
  state: known
  sources:
  - source_id: model-143-anthropic-claude-fable-5
    snapshot_ref: sha256:1ea0e92587855d9cc6695e742a294b76f7a8209a492b3f2cdf8aa6f4f36dca13
    cited_regions:
    - model-spec
  - source_id: model-143-anthropic-models-overview
    snapshot_ref: sha256:081fd4411b01088963ae62e43b378ba3c708843c5f553c277371f014a02bc65f
    cited_regions:
    - audit
  - source_id: model-143-anthropic-structured-outputs
    snapshot_ref: sha256:b93fe8ddc691cd8f9a022aacc8c3adabf38c9e8ed215ae955d61939ee64abaf9
    cited_regions:
    - audit
  - source_id: model-143-anthropic-streaming
    snapshot_ref: sha256:cdc7449de7d6829e2f611641ce1fcec68564814fd54ab3398c559189073b6f69
    cited_regions:
    - audit
  - source_id: model-143-anthropic-commercial-terms
    snapshot_ref: sha256:cfb59d90c8b31ffb9c1e3a0b95bff416c7b3d19218eb3c15e8d0169ea36caeca
    cited_regions:
    - audit
- facet: origin.base_lineage
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-anthropic-claude-fable-5
    snapshot_ref: sha256:1ea0e92587855d9cc6695e742a294b76f7a8209a492b3f2cdf8aa6f4f36dca13
    cited_regions:
    - model-spec
  - source_id: model-143-anthropic-models-overview
    snapshot_ref: sha256:081fd4411b01088963ae62e43b378ba3c708843c5f553c277371f014a02bc65f
    cited_regions:
    - audit
  - source_id: model-143-anthropic-structured-outputs
    snapshot_ref: sha256:b93fe8ddc691cd8f9a022aacc8c3adabf38c9e8ed215ae955d61939ee64abaf9
    cited_regions:
    - audit
  - source_id: model-143-anthropic-streaming
    snapshot_ref: sha256:cdc7449de7d6829e2f611641ce1fcec68564814fd54ab3398c559189073b6f69
    cited_regions:
    - audit
  - source_id: model-143-anthropic-commercial-terms
    snapshot_ref: sha256:cfb59d90c8b31ffb9c1e3a0b95bff416c7b3d19218eb3c15e8d0169ea36caeca
    cited_regions:
    - audit
  checked_sources:
  - model-143-anthropic-claude-fable-5
  - model-143-anthropic-models-overview
  - model-143-anthropic-structured-outputs
  - model-143-anthropic-streaming
  - model-143-anthropic-commercial-terms
- facet: origin.weights_hosting
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-anthropic-claude-fable-5
    snapshot_ref: sha256:1ea0e92587855d9cc6695e742a294b76f7a8209a492b3f2cdf8aa6f4f36dca13
    cited_regions:
    - model-spec
  - source_id: model-143-anthropic-models-overview
    snapshot_ref: sha256:081fd4411b01088963ae62e43b378ba3c708843c5f553c277371f014a02bc65f
    cited_regions:
    - audit
  - source_id: model-143-anthropic-structured-outputs
    snapshot_ref: sha256:b93fe8ddc691cd8f9a022aacc8c3adabf38c9e8ed215ae955d61939ee64abaf9
    cited_regions:
    - audit
  - source_id: model-143-anthropic-streaming
    snapshot_ref: sha256:cdc7449de7d6829e2f611641ce1fcec68564814fd54ab3398c559189073b6f69
    cited_regions:
    - audit
  - source_id: model-143-anthropic-commercial-terms
    snapshot_ref: sha256:cfb59d90c8b31ffb9c1e3a0b95bff416c7b3d19218eb3c15e8d0169ea36caeca
    cited_regions:
    - audit
  checked_sources:
  - model-143-anthropic-claude-fable-5
  - model-143-anthropic-models-overview
  - model-143-anthropic-structured-outputs
  - model-143-anthropic-streaming
  - model-143-anthropic-commercial-terms
- facet: model.release_date
  value: '2026-06-07'
  state: known
  sources:
  - source_id: model-143-anthropic-claude-fable-5
    snapshot_ref: sha256:1ea0e92587855d9cc6695e742a294b76f7a8209a492b3f2cdf8aa6f4f36dca13
    cited_regions:
    - model-spec
  - source_id: model-143-anthropic-models-overview
    snapshot_ref: sha256:081fd4411b01088963ae62e43b378ba3c708843c5f553c277371f014a02bc65f
    cited_regions:
    - audit
  - source_id: model-143-anthropic-structured-outputs
    snapshot_ref: sha256:b93fe8ddc691cd8f9a022aacc8c3adabf38c9e8ed215ae955d61939ee64abaf9
    cited_regions:
    - audit
  - source_id: model-143-anthropic-streaming
    snapshot_ref: sha256:cdc7449de7d6829e2f611641ce1fcec68564814fd54ab3398c559189073b6f69
    cited_regions:
    - audit
  - source_id: model-143-anthropic-commercial-terms
    snapshot_ref: sha256:cfb59d90c8b31ffb9c1e3a0b95bff416c7b3d19218eb3c15e8d0169ea36caeca
    cited_regions:
    - audit
- facet: model.lifecycle
  value: active
  state: known
  sources:
  - source_id: model-143-anthropic-claude-fable-5
    snapshot_ref: sha256:1ea0e92587855d9cc6695e742a294b76f7a8209a492b3f2cdf8aa6f4f36dca13
    cited_regions:
    - model-spec
  - source_id: model-143-anthropic-models-overview
    snapshot_ref: sha256:081fd4411b01088963ae62e43b378ba3c708843c5f553c277371f014a02bc65f
    cited_regions:
    - audit
  - source_id: model-143-anthropic-structured-outputs
    snapshot_ref: sha256:b93fe8ddc691cd8f9a022aacc8c3adabf38c9e8ed215ae955d61939ee64abaf9
    cited_regions:
    - audit
  - source_id: model-143-anthropic-streaming
    snapshot_ref: sha256:cdc7449de7d6829e2f611641ce1fcec68564814fd54ab3398c559189073b6f69
    cited_regions:
    - audit
  - source_id: model-143-anthropic-commercial-terms
    snapshot_ref: sha256:cfb59d90c8b31ffb9c1e3a0b95bff416c7b3d19218eb3c15e8d0169ea36caeca
    cited_regions:
    - audit
- facet: feature.tool_calling
  value: true
  state: known
  sources:
  - source_id: model-143-anthropic-claude-fable-5
    snapshot_ref: sha256:1ea0e92587855d9cc6695e742a294b76f7a8209a492b3f2cdf8aa6f4f36dca13
    cited_regions:
    - model-spec
  - source_id: model-143-anthropic-models-overview
    snapshot_ref: sha256:081fd4411b01088963ae62e43b378ba3c708843c5f553c277371f014a02bc65f
    cited_regions:
    - audit
  - source_id: model-143-anthropic-structured-outputs
    snapshot_ref: sha256:b93fe8ddc691cd8f9a022aacc8c3adabf38c9e8ed215ae955d61939ee64abaf9
    cited_regions:
    - audit
  - source_id: model-143-anthropic-streaming
    snapshot_ref: sha256:cdc7449de7d6829e2f611641ce1fcec68564814fd54ab3398c559189073b6f69
    cited_regions:
    - audit
  - source_id: model-143-anthropic-commercial-terms
    snapshot_ref: sha256:cfb59d90c8b31ffb9c1e3a0b95bff416c7b3d19218eb3c15e8d0169ea36caeca
    cited_regions:
    - audit
- facet: feature.structured_output
  value: true
  state: known
  sources:
  - source_id: model-143-anthropic-claude-fable-5
    snapshot_ref: sha256:1ea0e92587855d9cc6695e742a294b76f7a8209a492b3f2cdf8aa6f4f36dca13
    cited_regions:
    - model-spec
  - source_id: model-143-anthropic-models-overview
    snapshot_ref: sha256:081fd4411b01088963ae62e43b378ba3c708843c5f553c277371f014a02bc65f
    cited_regions:
    - audit
  - source_id: model-143-anthropic-structured-outputs
    snapshot_ref: sha256:b93fe8ddc691cd8f9a022aacc8c3adabf38c9e8ed215ae955d61939ee64abaf9
    cited_regions:
    - audit
  - source_id: model-143-anthropic-streaming
    snapshot_ref: sha256:cdc7449de7d6829e2f611641ce1fcec68564814fd54ab3398c559189073b6f69
    cited_regions:
    - audit
  - source_id: model-143-anthropic-commercial-terms
    snapshot_ref: sha256:cfb59d90c8b31ffb9c1e3a0b95bff416c7b3d19218eb3c15e8d0169ea36caeca
    cited_regions:
    - audit
- facet: feature.effort_controls
  value: true
  state: known
  sources:
  - source_id: model-143-anthropic-claude-fable-5
    snapshot_ref: sha256:1ea0e92587855d9cc6695e742a294b76f7a8209a492b3f2cdf8aa6f4f36dca13
    cited_regions:
    - model-spec
  - source_id: model-143-anthropic-models-overview
    snapshot_ref: sha256:081fd4411b01088963ae62e43b378ba3c708843c5f553c277371f014a02bc65f
    cited_regions:
    - audit
  - source_id: model-143-anthropic-structured-outputs
    snapshot_ref: sha256:b93fe8ddc691cd8f9a022aacc8c3adabf38c9e8ed215ae955d61939ee64abaf9
    cited_regions:
    - audit
  - source_id: model-143-anthropic-streaming
    snapshot_ref: sha256:cdc7449de7d6829e2f611641ce1fcec68564814fd54ab3398c559189073b6f69
    cited_regions:
    - audit
  - source_id: model-143-anthropic-commercial-terms
    snapshot_ref: sha256:cfb59d90c8b31ffb9c1e3a0b95bff416c7b3d19218eb3c15e8d0169ea36caeca
    cited_regions:
    - audit
- facet: feature.batch
  value: true
  state: known
  sources:
  - source_id: model-143-anthropic-claude-fable-5
    snapshot_ref: sha256:1ea0e92587855d9cc6695e742a294b76f7a8209a492b3f2cdf8aa6f4f36dca13
    cited_regions:
    - model-spec
  - source_id: model-143-anthropic-models-overview
    snapshot_ref: sha256:081fd4411b01088963ae62e43b378ba3c708843c5f553c277371f014a02bc65f
    cited_regions:
    - audit
  - source_id: model-143-anthropic-structured-outputs
    snapshot_ref: sha256:b93fe8ddc691cd8f9a022aacc8c3adabf38c9e8ed215ae955d61939ee64abaf9
    cited_regions:
    - audit
  - source_id: model-143-anthropic-streaming
    snapshot_ref: sha256:cdc7449de7d6829e2f611641ce1fcec68564814fd54ab3398c559189073b6f69
    cited_regions:
    - audit
  - source_id: model-143-anthropic-commercial-terms
    snapshot_ref: sha256:cfb59d90c8b31ffb9c1e3a0b95bff416c7b3d19218eb3c15e8d0169ea36caeca
    cited_regions:
    - audit
- facet: feature.streaming
  value: true
  state: known
  sources:
  - source_id: model-143-anthropic-claude-fable-5
    snapshot_ref: sha256:1ea0e92587855d9cc6695e742a294b76f7a8209a492b3f2cdf8aa6f4f36dca13
    cited_regions:
    - model-spec
  - source_id: model-143-anthropic-models-overview
    snapshot_ref: sha256:081fd4411b01088963ae62e43b378ba3c708843c5f553c277371f014a02bc65f
    cited_regions:
    - audit
  - source_id: model-143-anthropic-structured-outputs
    snapshot_ref: sha256:b93fe8ddc691cd8f9a022aacc8c3adabf38c9e8ed215ae955d61939ee64abaf9
    cited_regions:
    - audit
  - source_id: model-143-anthropic-streaming
    snapshot_ref: sha256:cdc7449de7d6829e2f611641ce1fcec68564814fd54ab3398c559189073b6f69
    cited_regions:
    - audit
  - source_id: model-143-anthropic-commercial-terms
    snapshot_ref: sha256:cfb59d90c8b31ffb9c1e3a0b95bff416c7b3d19218eb3c15e8d0169ea36caeca
    cited_regions:
    - audit
- id: anthropic/claude-fable-5#model.fits_hardware
  subject:
    kind: model
    id: anthropic/claude-fable-5
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
      model_snapshot_ref: sha256:1ea0e92587855d9cc6695e742a294b76f7a8209a492b3f2cdf8aa6f4f36dca13
      hardware_registry_sha256: sha256:10baf5e1ce9e5a1e5b970f4fdc25d9f67db8c562c8c109157ae9722bf6357bff
      hardware_device_count: 64
  sources:
  - source_id: model-143-anthropic-claude-fable-5
    snapshot_ref: sha256:1ea0e92587855d9cc6695e742a294b76f7a8209a492b3f2cdf8aa6f4f36dca13
    cited_regions:
    - model-spec
  - source_id: model-143-anthropic-models-overview
    snapshot_ref: sha256:081fd4411b01088963ae62e43b378ba3c708843c5f553c277371f014a02bc65f
    cited_regions:
    - audit
  - source_id: model-143-anthropic-structured-outputs
    snapshot_ref: sha256:b93fe8ddc691cd8f9a022aacc8c3adabf38c9e8ed215ae955d61939ee64abaf9
    cited_regions:
    - audit
  - source_id: model-143-anthropic-streaming
    snapshot_ref: sha256:cdc7449de7d6829e2f611641ce1fcec68564814fd54ab3398c559189073b6f69
    cited_regions:
    - audit
  - source_id: model-143-anthropic-commercial-terms
    snapshot_ref: sha256:cfb59d90c8b31ffb9c1e3a0b95bff416c7b3d19218eb3c15e8d0169ea36caeca
    cited_regions:
    - audit
card_schema_version: '3.0'
card_author: models.dev-seeder
card_created: '2026-04-05'
card_updated: '2026-09-28'
---

# Claude Fable 5

Claude Fable 5 is a Llm Reasoning model from Anthropic. Part of the claude-fable family.

## Key Features
- Extended reasoning / chain-of-thought
- Function calling / tool use
- Structured output (JSON mode)
- File/image attachments
