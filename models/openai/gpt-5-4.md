---
model_id: openai/gpt-5-4
display_name: GPT-5.4
provider: openai
provider_display: OpenAI
family: gpt
version: gpt-5.4
release_date: '2026-03-05'
last_updated: '2026-03-05'
status: active
model_type: llm-reasoning
model_subtypes:
- llm-code
tags:
- openai-compatible
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
  license_type: proprietary
  license_url: https://openai.com/policies/business-terms/
  tos_url: https://openai.com/policies/business-terms/
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
    max_input_tokens: 922000
    max_output_tokens: 128000
    context_window: 1050000
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
    overall: tier-1
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
    overall: tier-1
    mathematical: true
    logical: false
    scientific: false
    planning: false
    multi_step: true
    chain_of_thought: true
    self_correction: false
    spatial: false
    temporal: false
    causal: false
    think_budget_control: false
  tool_use:
    overall: tier-1
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
  input: 2.5
  output: 15.0
  reasoning: null
  cache_read: 0.25
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
    arena_elo_hard_prompts: 1507.2
    arena_elo_style_control: 1483.6
    gpqa_diamond: 92.8
    graphwalks_bfs_256k_1m: 21.4
    hle: 39.8
    hle_tools: 52.1
    osworld: 75.0
    swe_bench_pro: 57.7
    terminal_bench_2: 75.1
    usamo_2026: 95.2
  benchmark_source: lmarena.ai, provider-reports, anthropic-system-card-mythos, domain-evals
  benchmark_as_of: 2026-04
  evidence:
  - benchmark_id: metr_time_horizon_50
    model_id_as_evaluated: gpt_5_4
    score: 341.735276
    unit: minutes
    source_url: https://metr.org/assets/benchmark_results_1_1.yaml
    source_kind: benchmark_author
    evidence_date: '2026-04-10'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: METR-Horizon-v1.1
    configuration: Time Horizon 1.1 YAML field p50_horizon_length.estimate, minutes, Inspect-era 1.1 protocol. Public chart shows hours. Not Time Horizon 1.0.
    limitations: YAML CI [186.581591, 768.779526] minutes. METR states measurements above 16 hours are unreliable on this suite.
    id: openai/gpt-5-4#metr_time_horizon_50#8b1d93d1b4c0
    measured_by: benchmark_author
    effort: null
    harness: null
    sources:
    - source_id: model-160-metr-time-horizon-1-1
      snapshot_ref: sha256:1d8fdb5423293355d5411f065038e25f4c9ad805d547ba87354d95cc29724369
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: metr_time_horizon_80
    model_id_as_evaluated: gpt_5_4
    score: 53.877851
    unit: minutes
    source_url: https://metr.org/assets/benchmark_results_1_1.yaml
    source_kind: benchmark_author
    evidence_date: '2026-04-10'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: METR-Horizon-v1.1
    configuration: Time Horizon 1.1 YAML field p80_horizon_length.estimate, minutes, Inspect-era 1.1 protocol. Public chart shows hours. Not Time Horizon 1.0.
    limitations: YAML CI [23.957027, 108.679232] minutes. METR states measurements above 16 hours are unreliable on this suite.
    id: openai/gpt-5-4#metr_time_horizon_80#7c024d112d86
    measured_by: benchmark_author
    effort: null
    harness: null
    sources:
    - source_id: model-160-metr-time-horizon-1-1
      snapshot_ref: sha256:1d8fdb5423293355d5411f065038e25f4c9ad805d547ba87354d95cc29724369
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: arena_elo_overall
    model_id_as_evaluated: gpt-5.4-high
    score: 1469.63
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: Text Arena overall, raw (not style-controlled)
    configuration: 'LMArena''s official leaderboard dataset, split latest, subset `text`
      (raw, non-style-controlled), category overall; leaderboard_publish_date 2026-09-13
      is the stated date. Row gpt-5.4-high: rating 1469.63 (95% CI 1465.79-1473.48), 60537
      votes. Highest-effort row for the model (MODEL-123 max-effort rule), matching this
      card''s style-controlled rows. MODEL-127 audit correction: MODEL-109 had taken the
      default-effort row gpt-5.4 (1452.64); dataset re-read 2026-09-24.'
    limitations: Normalization in api/ranking/engine.py bounds Arena Elo at 1400; values
      above clip.
    id: openai/gpt-5-4#arena_elo_overall#9009e51bb407
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text
      snapshot_ref: sha256:5499198274b1cf531f2446dd915dd0629a365172dec9759fc21a57a225867972
      cited_regions:
      - rows
    interval:
    - 1465.79
    - 1473.48
    n: 60537
    observed_at: '2026-09-28'
  - benchmark_id: arena_elo_coding
    model_id_as_evaluated: gpt-5.4-high
    score: 1495.51
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: Text Arena coding category, raw (not style-controlled)
    configuration: "LMArena's official leaderboard dataset, split latest, subset `text` (raw, non-style-controlled), category coding; leaderboard_publish_date 2026-09-13 is the stated date. Row gpt-5.4-high: rating 1495.51 (95% CI 1489.58-1501.45), 16395 votes. Highest-effort row for the model (MODEL-123 max-effort rule), matching this card's style-controlled rows. MODEL-127 audit correction: MODEL-109 had taken the default-effort row gpt-5.4 (1480.04); dataset re-read 2026-09-24."
    limitations: Normalization in api/ranking/engine.py bounds Arena Elo at 1400; values
      above clip.
    id: openai/gpt-5-4#arena_elo_coding#6804fdc94455
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text
      snapshot_ref: sha256:507db5c8f302dffbcb9c859c57e2f3368d9dead75f9849daa4f0aebf03aca17e
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: arena_elo_style_control
    model_id_as_evaluated: gpt-5.4-high
    score: 1476.39
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / overall, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category overall,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: high; MODEL-123 max-effort rule). Rating 1476.39 [1472.51, 1480.26], 60537 votes,
      rank 26.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: openai/gpt-5-4#arena_elo_style_control#debe0a60cc18
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
    model_id_as_evaluated: gpt-5.4-high
    score: 1520.08
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / coding, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category coding,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: high; MODEL-123 max-effort rule). Rating 1520.08 [1514.09, 1526.06], 16395 votes,
      rank 29.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: openai/gpt-5-4#arena_sc_coding#809d13c65778
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
    model_id_as_evaluated: gpt-5.4-high
    score: 1497.91
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / hard_prompts, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category hard_prompts,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: high; MODEL-123 max-effort rule). Rating 1497.91 [1493.29, 1502.53], 39229 votes,
      rank 29.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: openai/gpt-5-4#arena_sc_hard_prompts#bcdafb57843a
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
    model_id_as_evaluated: gpt-5.4-high
    score: 1494.13
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / math, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category math, leaderboard_publish_date
      2026-09-13; style control. Highest-effort row for the product (effort: high; MODEL-123
      max-effort rule). Rating 1494.13 [1483.18, 1505.08], 3179 votes, rank 17.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: openai/gpt-5-4#arena_sc_math#8fe3a746c37e
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
    model_id_as_evaluated: gpt-5.4-high
    score: 1444.19
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / creative_writing, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category creative_writing,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: high; MODEL-123 max-effort rule). Rating 1444.19 [1437.02, 1451.36], 10081 votes,
      rank 47.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: openai/gpt-5-4#arena_sc_creative_writing#842e5e7add9f
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
    model_id_as_evaluated: gpt-5.4-high
    score: 1472.44
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / instruction_following, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category instruction_following,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: high; MODEL-123 max-effort rule). Rating 1472.44 [1466.85, 1478.02], 20257 votes,
      rank 27.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: openai/gpt-5-4#arena_sc_instruction_following#f43453cc7ecf
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
    model_id_as_evaluated: gpt-5.4-high
    score: 1493.77
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / multi_turn, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category multi_turn,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: high; MODEL-123 max-effort rule). Rating 1493.77 [1486.99, 1500.55], 11259 votes,
      rank 17.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: openai/gpt-5-4#arena_sc_multi_turn#24982f421bc0
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
    model_id_as_evaluated: gpt-5.4-high
    score: 1515.72
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / expert, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category expert,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: high; MODEL-123 max-effort rule). Rating 1515.72 [1506.99, 1524.44], 5741 votes,
      rank 15.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: openai/gpt-5-4#arena_sc_expert#5e8329235781
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
    model_id_as_evaluated: gpt-5.4-high
    score: 1483.16
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / longer_query, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category longer_query,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: high; MODEL-123 max-effort rule). Rating 1483.16 [1477.74, 1488.58], 25968 votes,
      rank 32.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: openai/gpt-5-4#arena_sc_longer_query#3cdb673cf09f
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
    model_id_as_evaluated: gpt-5.4-high
    score: 1468.48
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / non_english, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category non_english,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: high; MODEL-123 max-effort rule). Rating 1468.48 [1463.74, 1473.22], 33029 votes,
      rank 25.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: openai/gpt-5-4#arena_sc_non_english#80a3f148f08c
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
    model_id_as_evaluated: gpt-5.4-high
    score: 1475.97
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
      (effort: high; MODEL-123 max-effort rule). Rating 1475.97 [1466.08, 1485.87], 4457 votes,
      rank 58.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: openai/gpt-5-4#arena_sc_medicine#c9468f68e8eb
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
    model_id_as_evaluated: gpt-5.4-high
    score: 1490.58
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
      (effort: high; MODEL-123 max-effort rule). Rating 1490.58 [1481.17, 1499.99], 4885 votes,
      rank 22.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: openai/gpt-5-4#arena_sc_legal#78cb2f954616
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
    model_id_as_evaluated: gpt-5.4-high
    score: 1483.87
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
      (effort: high; MODEL-123 max-effort rule). Rating 1483.87 [1477.23, 1490.51], 12327 votes,
      rank 21.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: openai/gpt-5-4#arena_sc_business#55e9dbb6787a
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
    model_id_as_evaluated: gpt-5.4-high
    score: 1487.64
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
      (effort: high; MODEL-123 max-effort rule). Rating 1487.64 [1480.62, 1494.65], 9869 votes,
      rank 38.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: openai/gpt-5-4#arena_sc_science#41f8f1cf2d09
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
    model_id_as_evaluated: gpt-5.4-high
    score: 1465.32
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
      (effort: high; MODEL-123 max-effort rule). Rating 1465.32 [1459.19, 1471.44], 15014 votes,
      rank 28.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: openai/gpt-5-4#arena_sc_writing#8fe25152473b
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
    model_id_as_evaluated: gpt-5.4-high
    score: 1284.79
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: vision_style_control / overall, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset vision_style_control, category overall,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: high; MODEL-123 max-effort rule). Rating 1284.79 [1278.53, 1291.04], 25357 votes,
      rank 15.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: openai/gpt-5-4#arena_sc_vision#8bc06fd270a9
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-vision-style-control
      snapshot_ref: sha256:693bb5beed49b4a7d42c9a96f9478ac70d74903bc6be5b38767e2f6b0d69fe7f
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: arena_webdev
    model_id_as_evaluated: gpt-5.4
    score: 1392.0
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-23'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: webdev / overall, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset webdev, category overall, leaderboard_publish_date
      2026-09-23; no style-controlled variant. Highest-effort row for the product (effort: default;
      MODEL-123 max-effort rule). Rating 1392.00 [1380.47, 1403.52], 3196 votes, rank 83.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: openai/gpt-5-4#arena_webdev#380e2b10fed1
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
    model_id_as_evaluated: gpt-5.4-2026-03-05_xhigh
    score: 93.3
    unit: percent
    source_url: https://epoch.ai/benchmarks/gpqa-diamond
    source_kind: independent_evaluator
    evidence_date: '2026-03-06'
    date_type: evaluated
    verified_at: '2026-09-28'
    benchmark_version: GPQA Diamond (Epoch AI run)
    configuration: Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (gpqa_diamond.csv),
      read 2026-09-24. Run started 2026-03-06T02:57:02.864Z; effort xhigh; highest-effort run
      for the model (MODEL-123 max-effort rule), newest on a tie. Standard error 1.80 points.
    limitations: Epoch AI data, CC BY 4.0.
    id: openai/gpt-5-4#gpqa_diamond#f50f22079a50
    measured_by: independent_evaluator
    effort: xhigh
    harness: null
    sources:
    - source_id: model-143-evidence-epoch-gpqa-diamond-csv
      snapshot_ref: sha256:a25a72a0e190ea7f53b8711a3793afd00492581a29c19c2a89c0e7fa19183f12
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: frontiermath_tiers_1_3_v2
    model_id_as_evaluated: gpt-5.4-2026-03-05_xhigh
    score: 78.6
    unit: percent
    source_url: https://epoch.ai/frontiermath
    source_kind: independent_evaluator
    evidence_date: '2026-06-11'
    date_type: evaluated
    verified_at: '2026-09-28'
    benchmark_version: FrontierMath-Tiers-1-3-v2-Private (Epoch AI run)
    configuration: Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (frontiermath_tiers_1_3_v2.csv),
      read 2026-09-24. Run started 2026-06-11T17:55:45.000Z; effort xhigh; highest-effort run
      for the model (MODEL-123 max-effort rule), newest on a tie. Standard error 2.43 points.
    limitations: Epoch AI data, CC BY 4.0.
    id: openai/gpt-5-4#frontiermath_tiers_1_3_v2#0c2423a94755
    measured_by: independent_evaluator
    effort: xhigh
    harness: null
    sources:
    - source_id: model-143-evidence-epoch-frontiermath-tiers-1-3-v2-csv
      snapshot_ref: sha256:a38d3375a77ff7cbb6aa8dbb75394839ac0303ff7cf41a8c80ef294bb06b9c93
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: simpleqa_verified
    model_id_as_evaluated: gpt-5.4-2026-03-05_xhigh
    score: 45.1
    unit: percent
    source_url: https://epoch.ai/benchmarks/simpleqa-verified
    source_kind: independent_evaluator
    evidence_date: '2026-08-27'
    date_type: evaluated
    verified_at: '2026-09-28'
    benchmark_version: SimpleQA Verified, proportion correct, Epoch AI protocol with anti-abstention
      prompt
    configuration: Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (simpleqa_verified.csv),
      read 2026-09-24. Run started 2026-08-27T19:28:16.000Z; effort xhigh; highest-effort run
      for the model (MODEL-123 max-effort rule), newest on a tie. Standard error 1.57 points.
    limitations: Epoch AI data, CC BY 4.0.
    id: openai/gpt-5-4#simpleqa_verified#8fecd470b37a
    measured_by: independent_evaluator
    effort: xhigh
    harness: null
    sources:
    - source_id: model-160-epoch-simpleqa-verified-csv
      snapshot_ref: sha256:1f18c84606f93b761f4bffcfe1f688b4f4bd7d0d26ef1bcfa2486126c4fb123e
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: swe_bench_verified
    model_id_as_evaluated: gpt-5.4-2026-03-05_high
    score: 76.86
    unit: percent
    source_url: https://epoch.ai/benchmarks/swe-bench-verified
    source_kind: independent_evaluator
    evidence_date: '2026-03-06'
    date_type: evaluated
    verified_at: '2026-09-28'
    benchmark_version: SWE-bench Verified (Epoch AI run)
    configuration: Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (swe_bench_verified.csv),
      read 2026-09-24. Run started 2026-03-06T11:07:43.396Z; effort high; highest-effort run
      for the model (MODEL-123 max-effort rule), newest on a tie. Standard error 1.92 points.
    limitations: Epoch AI data, CC BY 4.0.
    id: openai/gpt-5-4#swe_bench_verified#92fc8342b3c4
    measured_by: independent_evaluator
    effort: high
    harness: null
    sources:
    - source_id: model-160-epoch-swe-bench-verified-csv
      snapshot_ref: sha256:e0247c7d3ab619909d4ad5f823318c22a312ee996c1e620c38dcf888494ec4ca
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: vending_bench_2
    model_id_as_evaluated: GPT-5.4
    score: 6144.18
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
    id: openai/gpt-5-4#vending_bench_2#a6fa5b14fb50
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
    model_id_as_evaluated: gpt-5-4 (xhigh)
    score: 51.77
    unit: percent
    source_url: https://deepswe.datacurve.ai/
    source_kind: benchmark_author
    evidence_date: '2026-09-25'
    date_type: evaluated
    verified_at: '2026-09-28'
    benchmark_version: DeepSWE v1.1, pass@1, mini-swe-agent
    configuration: Board row as copied in Epoch AI's benchmark data (deepswe_external.csv, https://epoch.ai/data/benchmark_data.zip),
      read 2026-09-24. Effort xhigh; the highest-effort row for the model (MODEL-123 max-effort
      rule). Harness mini-swe-agent.
    limitations: A live board's standing, dated by the day ModelSpec read Epoch AI's copy; the
      copy carries no per-row date. Epoch AI data, CC BY 4.0.
    id: openai/gpt-5-4#deepswe_v1_1#a69faea231d2
    measured_by: benchmark_author
    effort: xhigh
    harness: unregistered
    sources:
    - source_id: model-160-deepswe-v1-1
      snapshot_ref: sha256:64010fde30846107b5210ba17347a269780973bf71eb8ce9c1d316a353733156
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: hle
    model_id_as_evaluated: gpt-5.4-2026-03-05 (xhigh thinking)
    score: 36.24
    unit: percent
    source_url: https://labs.scale.com/leaderboard/humanitys_last_exam
    source_kind: independent_evaluator
    evidence_date: '2026-09-24'
    date_type: evaluated
    verified_at: '2026-09-28'
    benchmark_version: Humanity's Last Exam, Scale Labs leaderboard
    configuration: Scale Labs leaderboard entry read 2026-09-24; entry created 2026-03-10T21:09:26.000Z;
      effort xhigh; ±1.88 (95% CI).
    limitations: 'Potential contamination warning: This model was evaluated after the public
      release of HLE, allowing model builder access to the prompts and solutions.'
    id: openai/gpt-5-4#hle#7ff3c64eaebc
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
    model_id_as_evaluated: gpt-5.4 (xHigh)*
    score: 59.1
    unit: percent
    source_url: https://labs.scale.com/leaderboard/swe_bench_pro_public
    source_kind: independent_evaluator
    evidence_date: '2026-04-08'
    date_type: evaluated
    verified_at: '2026-09-28'
    benchmark_version: SWE-Bench Pro, public dataset, Scale Labs leaderboard
    configuration: 'Scale Labs leaderboard entry read 2026-09-24; entry created 2026-04-08T17:04:48.000Z;
      effort xhigh; ±3.56 (95% CI). Harness: mini-swe-agent (the board marks mini-swe-agent
      runs with an asterisk).'
    limitations: ''
    id: openai/gpt-5-4#swe_bench_pro#eadfdacd55d8
    measured_by: independent_evaluator
    effort: xhigh
    harness: unregistered
    sources:
    - source_id: model-160-scale-swe-bench-pro-public
      snapshot_ref: sha256:27682f9d9581ddcc087df28d6400780b64742f9eb9eb0596542418b345387bf1
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: aime_2026
    model_id_as_evaluated: GPT-5.4 (xhigh)
    score: 99.17
    unit: percent
    source_url: https://matharena.ai/competition_tables/aime--aime_2026
    source_kind: independent_evaluator
    evidence_date: '2026-09-26'
    date_type: evaluated
    verified_at: '2026-09-28'
    benchmark_version: AIME 2026, MathArena final-answer table
    configuration: MathArena competition table read 2026-09-26; the table states no run
      date, so the reading is dated by the observation. Effort xhigh; highest-effort row
      for the model. MathArena lists final-answer competitions as deprecated.
    limitations: 'MathArena marks this row: model was released after competition release, so
      contamination is possible.'
    id: openai/gpt-5-4#aime_2026#2177361b157c
    measured_by: independent_evaluator
    effort: xhigh
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
    model_id_as_evaluated: GPT-5.4 (xhigh)
    score: 39.43
    unit: percent
    source_url: https://sierra-tau-bench-public.s3.us-west-2.amazonaws.com/submissions/gpt-5-4_sierra_2026-03-25/submission.json
    source_kind: benchmark_author
    evidence_date: '2026-05-06'
    date_type: evaluated
    verified_at: '2026-09-28'
    benchmark_version: τ-Knowledge τ-Banking (banking_knowledge), pass^1
    configuration: τ-bench leaderboard submission gpt-5-4_sierra_2026-03-25, submitted by Sierra;
      retrieval config alltools; reasoning effort xhigh; user simulator gpt-5.2; tau2-bench
      1.0.1. pass^4 21.65.
    limitations: 'Evaluated with reasoning_effort ''xhigh'' (the highest effort level this model
      supports). Retrieval: AllTools (BM25 + dense OpenAI text-embedding-3-large + sandboxed
      shell). User simulator: gpt-5.2 with reasoning_effort: low. 4 trials. Seed: 300. Banking_knowledge
      domain only — other domains intention'
    id: openai/gpt-5-4#tau3_banking#9abcb4f58352
    measured_by: benchmark_author
    effort: xhigh
    harness: null
    sources:
    - source_id: model-160-tau-bench-gpt-5-4-sierra-2026-03-25
      snapshot_ref: sha256:b9a97a08aae3f0923b816c709ea9f24464de328bc577b7e4af8225aea90643ba
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: arena_sc_english
    model_id_as_evaluated: gpt-5.4-high
    score: 1477.88
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / english, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1477.88 [1472.84,
      1482.91], 27508 votes, rank 37. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:c10623c0b42bc927b984d3933d31aa31c3cd1c21841797328e80981e6d334892
      cited_regions:
      - rows
    id: openai/gpt-5-4#arena_sc_english#34c6dcdbea1c
  - benchmark_id: arena_sc_chinese
    model_id_as_evaluated: gpt-5.4-high
    score: 1504.78
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / chinese, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1504.78 [1493.87,
      1515.69], 3462 votes, rank 45. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:1e2f3fa3120aa6532923deddea1fcb48e14b14f7e2f3396e16e17304594752bd
      cited_regions:
      - rows
    id: openai/gpt-5-4#arena_sc_chinese#e140693446c5
  - benchmark_id: arena_sc_japanese
    model_id_as_evaluated: gpt-5.4-high
    score: 1481.79
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / japanese, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1481.79 [1456.28,
      1507.30], 643 votes, rank 14. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:c9ec43cc46cde9a9a084781e014b590ecb91e24ff239d072e5e3e1fbe299075a
      cited_regions:
      - rows
    id: openai/gpt-5-4#arena_sc_japanese#ecf13596cd00
  - benchmark_id: arena_sc_korean
    model_id_as_evaluated: gpt-5.4-high
    score: 1437.3
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / korean, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1437.30 [1417.20,
      1457.41], 1076 votes, rank 27. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:da67028715236f4510ef6cd2b29aa4a819e6b581fd48575bbee287a0a72545fa
      cited_regions:
      - rows
    id: openai/gpt-5-4#arena_sc_korean#7062f5b0090a
  - benchmark_id: arena_sc_russian
    model_id_as_evaluated: gpt-5.4-high
    score: 1489.95
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / russian, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1489.95 [1481.73,
      1498.17], 6509 votes, rank 20. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:3d6ede20ed72833ccae1f56c86762a83c811d6fcb89f7960178d516bbb50aa8d
      cited_regions:
      - rows
    id: openai/gpt-5-4#arena_sc_russian#396dbaf15b9f
  - benchmark_id: arena_sc_spanish
    model_id_as_evaluated: gpt-5.4-high
    score: 1457.52
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / spanish, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1457.52 [1442.96,
      1472.08], 2020 votes, rank 48. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:626c233148bb4156f80113d49c8163082ed947cbfb64e20739771d4fe07b33f1
      cited_regions:
      - rows
    id: openai/gpt-5-4#arena_sc_spanish#03bc7489c400
  - benchmark_id: arena_sc_german
    model_id_as_evaluated: gpt-5.4-high
    score: 1472.53
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / german, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1472.53 [1453.15,
      1491.92], 1050 votes, rank 34. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:6074611b99cf8732f4dee1ad2a5718683b7a9ca7fdff6588d35ba1863ea5f8ac
      cited_regions:
      - rows
    id: openai/gpt-5-4#arena_sc_german#62179d7a112a
  - benchmark_id: arena_sc_french
    model_id_as_evaluated: gpt-5.4-high
    score: 1501.75
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / french, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1501.75 [1487.05,
      1516.45], 2286 votes, rank 22. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:26b468ee0d48430ff995f4feb0483b5c391cb383a59ea1755a4e91eeb0f6a8f2
      cited_regions:
      - rows
    id: openai/gpt-5-4#arena_sc_french#b5f1a8f47368
  - benchmark_id: arena_sc_polish
    model_id_as_evaluated: gpt-5.4-high
    score: 1481.37
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / polish, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1481.37 [1464.28,
      1498.45], 1295 votes, rank 23. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:1d2df11d9abaf322e77c330fab6d5e5ef26979c835443f67601b6c89b8f3f299
      cited_regions:
      - rows
    id: openai/gpt-5-4#arena_sc_polish#935d50af9f44
  - benchmark_id: arena_sc_vision_ocr
    model_id_as_evaluated: gpt-5.4-high
    score: 1299.64
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: vision_style_control / ocr, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1299.64 [1293.33,
      1305.95], 18040 votes, rank 15. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-vision-style-control
      snapshot_ref: sha256:99489a369ef55faf7aa620e6883cd433e47186123b5bf44b8343073a0f22fadf
      cited_regions:
      - rows
    id: openai/gpt-5-4#arena_sc_vision_ocr#10531aeddc1a
  - benchmark_id: arena_sc_vision_diagram
    model_id_as_evaluated: gpt-5.4-high
    score: 1319.27
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: vision_style_control / diagram, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1319.27 [1310.29,
      1328.26], 6803 votes, rank 10. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-vision-style-control
      snapshot_ref: sha256:9bc8dfd6db75a6a49f2764592a2a096290158c27a7288ac98c8fdee2efa80bd2
      cited_regions:
      - rows
    id: openai/gpt-5-4#arena_sc_vision_diagram#aa15ee032f1a
  - benchmark_id: arena_sc_vision_homework
    model_id_as_evaluated: gpt-5.4-high
    score: 1331.84
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: vision_style_control / homework, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1331.84 [1320.32,
      1343.35], 3264 votes, rank 7. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-vision-style-control
      snapshot_ref: sha256:d55d1f7ffb986be7b796464f4c9b446aa3f66769bd4027b6e5a8394fe2ef1db0
      cited_regions:
      - rows
    id: openai/gpt-5-4#arena_sc_vision_homework#a98504bbc7e3
  - benchmark_id: arena_sc_document
    model_id_as_evaluated: gpt-5.4
    score: 1471.0
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: document / overall, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1471.00 [1464.97,
      1477.04], 33331 votes, rank 14. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-document
      snapshot_ref: sha256:40f0c4aa079cc5d1dd633a2286b1bf63a24f2ee612d86330310020711b047a70
      cited_regions:
      - rows
    id: openai/gpt-5-4#arena_sc_document#ad3720d6948a
  - benchmark_id: arena_sc_industry_software_it_services
    model_id_as_evaluated: gpt-5.4-high
    score: 1506.5
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / industry_software_and_it_services, latest split, revision
      1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1506.50 [1501.21,
      1511.79], 23772 votes, rank 34. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:4538dd5bcb06397043fc55c64535410a284e7da8668e8c13cc2950c6f1baa37c
      cited_regions:
      - rows
    id: openai/gpt-5-4#arena_sc_industry_software_it_services#98c9912126e9
  - benchmark_id: arena_sc_industry_entertainment_sports_media
    model_id_as_evaluated: gpt-5.4-high
    score: 1442.56
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / industry_entertainment_and_sports_and_media, latest
      split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1442.56 [1435.97,
      1449.16], 12916 votes, rank 41. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:89233e13dec450388587fa44e3af9cfb82da53034e616b951c1cbe809b0c4cef
      cited_regions:
      - rows
    id: openai/gpt-5-4#arena_sc_industry_entertainment_sports_media#37c825ab5ac3
  - benchmark_id: arena_sc_industry_mathematical
    model_id_as_evaluated: gpt-5.4-high
    score: 1499.48
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / industry_mathematical, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1499.48 [1488.32,
      1510.64], 3236 votes, rank 19. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:514a2f81b6bce9bc34481c6e0d7af71184302842a4f5b8284657dc5024965f25
      cited_regions:
      - rows
    id: openai/gpt-5-4#arena_sc_industry_mathematical#3c2d596335b9
  - benchmark_id: arena_sc_factuality
    model_id_as_evaluated: gpt-5.4-high
    score: 1485.01
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_factuality / overall, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1485.01 [1482.01,
      1488.00], 60435 votes, rank 9. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-factuality
      snapshot_ref: sha256:359d85539a6e849ffbfe46427efdefadb4be9c907f9fbea9f799ce7bbf6c52c2
      cited_regions:
      - rows
    id: openai/gpt-5-4#arena_sc_factuality#76bcb29c51a0
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
  models_dev_url: https://models.dev/openai
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
  - source_id: model-143-openai-gpt-5-4
    snapshot_ref: sha256:56c7e709958cf5eab6e96673a1c0f85e250345ff31d6165bbcb48609f38ac581
    cited_regions:
    - model-spec
  - source_id: model-143-openai-models-overview
    snapshot_ref: sha256:bdc3168feccafca027197f5ec142f4ec4ff7c61466085d47931e9093525e6de4
    cited_regions:
    - audit
  - source_id: model-143-openai-changelog
    snapshot_ref: sha256:b2081a8984a0212a31945f67d1e9e8983ed396b736bb4767901472a5d86b9f06
    cited_regions:
    - audit
  - source_id: model-143-openai-reasoning
    snapshot_ref: sha256:d10bae47e0233ce7428779d30bc1edf6f69784f267140c277cb58fe01ebe4a77
    cited_regions:
    - audit
  - source_id: model-143-openai-services-agreement
    snapshot_ref: sha256:281462a94d8676b839c6c41a484a3e0390d988621bd868610c201ab884360f94
    cited_regions:
    - audit
- facet: model.input_modalities
  value:
  - text
  - image
  - document
  state: known
  sources:
  - source_id: model-143-openai-gpt-5-4
    snapshot_ref: sha256:56c7e709958cf5eab6e96673a1c0f85e250345ff31d6165bbcb48609f38ac581
    cited_regions:
    - model-spec
  - source_id: model-143-openai-models-overview
    snapshot_ref: sha256:bdc3168feccafca027197f5ec142f4ec4ff7c61466085d47931e9093525e6de4
    cited_regions:
    - audit
  - source_id: model-143-openai-changelog
    snapshot_ref: sha256:b2081a8984a0212a31945f67d1e9e8983ed396b736bb4767901472a5d86b9f06
    cited_regions:
    - audit
  - source_id: model-143-openai-reasoning
    snapshot_ref: sha256:d10bae47e0233ce7428779d30bc1edf6f69784f267140c277cb58fe01ebe4a77
    cited_regions:
    - audit
  - source_id: model-143-openai-services-agreement
    snapshot_ref: sha256:281462a94d8676b839c6c41a484a3e0390d988621bd868610c201ab884360f94
    cited_regions:
    - audit
- facet: model.output_modalities
  value:
  - text
  state: known
  sources:
  - source_id: model-143-openai-gpt-5-4
    snapshot_ref: sha256:56c7e709958cf5eab6e96673a1c0f85e250345ff31d6165bbcb48609f38ac581
    cited_regions:
    - model-spec
  - source_id: model-143-openai-models-overview
    snapshot_ref: sha256:bdc3168feccafca027197f5ec142f4ec4ff7c61466085d47931e9093525e6de4
    cited_regions:
    - audit
  - source_id: model-143-openai-changelog
    snapshot_ref: sha256:b2081a8984a0212a31945f67d1e9e8983ed396b736bb4767901472a5d86b9f06
    cited_regions:
    - audit
  - source_id: model-143-openai-reasoning
    snapshot_ref: sha256:d10bae47e0233ce7428779d30bc1edf6f69784f267140c277cb58fe01ebe4a77
    cited_regions:
    - audit
  - source_id: model-143-openai-services-agreement
    snapshot_ref: sha256:281462a94d8676b839c6c41a484a3e0390d988621bd868610c201ab884360f94
    cited_regions:
    - audit
- facet: model.context_window
  value: 1050000
  state: known
  sources:
  - source_id: model-143-openai-gpt-5-4
    snapshot_ref: sha256:56c7e709958cf5eab6e96673a1c0f85e250345ff31d6165bbcb48609f38ac581
    cited_regions:
    - model-spec
  - source_id: model-143-openai-models-overview
    snapshot_ref: sha256:bdc3168feccafca027197f5ec142f4ec4ff7c61466085d47931e9093525e6de4
    cited_regions:
    - audit
  - source_id: model-143-openai-changelog
    snapshot_ref: sha256:b2081a8984a0212a31945f67d1e9e8983ed396b736bb4767901472a5d86b9f06
    cited_regions:
    - audit
  - source_id: model-143-openai-reasoning
    snapshot_ref: sha256:d10bae47e0233ce7428779d30bc1edf6f69784f267140c277cb58fe01ebe4a77
    cited_regions:
    - audit
  - source_id: model-143-openai-services-agreement
    snapshot_ref: sha256:281462a94d8676b839c6c41a484a3e0390d988621bd868610c201ab884360f94
    cited_regions:
    - audit
- facet: model.max_output_tokens
  value: 128000
  state: known
  sources:
  - source_id: model-143-openai-gpt-5-4
    snapshot_ref: sha256:56c7e709958cf5eab6e96673a1c0f85e250345ff31d6165bbcb48609f38ac581
    cited_regions:
    - model-spec
  - source_id: model-143-openai-models-overview
    snapshot_ref: sha256:bdc3168feccafca027197f5ec142f4ec4ff7c61466085d47931e9093525e6de4
    cited_regions:
    - audit
  - source_id: model-143-openai-changelog
    snapshot_ref: sha256:b2081a8984a0212a31945f67d1e9e8983ed396b736bb4767901472a5d86b9f06
    cited_regions:
    - audit
  - source_id: model-143-openai-reasoning
    snapshot_ref: sha256:d10bae47e0233ce7428779d30bc1edf6f69784f267140c277cb58fe01ebe4a77
    cited_regions:
    - audit
  - source_id: model-143-openai-services-agreement
    snapshot_ref: sha256:281462a94d8676b839c6c41a484a3e0390d988621bd868610c201ab884360f94
    cited_regions:
    - audit
- facet: model.weights_openness
  value: closed_weights
  state: known
  sources:
  - source_id: model-143-openai-gpt-5-4
    snapshot_ref: sha256:56c7e709958cf5eab6e96673a1c0f85e250345ff31d6165bbcb48609f38ac581
    cited_regions:
    - model-spec
  - source_id: model-143-openai-models-overview
    snapshot_ref: sha256:bdc3168feccafca027197f5ec142f4ec4ff7c61466085d47931e9093525e6de4
    cited_regions:
    - audit
  - source_id: model-143-openai-changelog
    snapshot_ref: sha256:b2081a8984a0212a31945f67d1e9e8983ed396b736bb4767901472a5d86b9f06
    cited_regions:
    - audit
  - source_id: model-143-openai-reasoning
    snapshot_ref: sha256:d10bae47e0233ce7428779d30bc1edf6f69784f267140c277cb58fe01ebe4a77
    cited_regions:
    - audit
  - source_id: model-143-openai-services-agreement
    snapshot_ref: sha256:281462a94d8676b839c6c41a484a3e0390d988621bd868610c201ab884360f94
    cited_regions:
    - audit
- facet: licence.commercial_use
  value: permitted_with_conditions
  state: known
  sources:
  - source_id: model-143-openai-gpt-5-4
    snapshot_ref: sha256:56c7e709958cf5eab6e96673a1c0f85e250345ff31d6165bbcb48609f38ac581
    cited_regions:
    - model-spec
  - source_id: model-143-openai-services-agreement
    snapshot_ref: sha256:281462a94d8676b839c6c41a484a3e0390d988621bd868610c201ab884360f94
    cited_regions:
    - audit
- facet: licence.user_cap
  value: unbounded
  state: known
  sources:
  - source_id: model-143-openai-gpt-5-4
    snapshot_ref: sha256:56c7e709958cf5eab6e96673a1c0f85e250345ff31d6165bbcb48609f38ac581
    cited_regions:
    - model-spec
  - source_id: model-143-openai-services-agreement
    snapshot_ref: sha256:281462a94d8676b839c6c41a484a3e0390d988621bd868610c201ab884360f94
    cited_regions:
    - audit
- facet: licence.output_training
  value: restricted
  state: known
  sources:
  - source_id: model-143-openai-gpt-5-4
    snapshot_ref: sha256:56c7e709958cf5eab6e96673a1c0f85e250345ff31d6165bbcb48609f38ac581
    cited_regions:
    - model-spec
  - source_id: model-143-openai-services-agreement
    snapshot_ref: sha256:281462a94d8676b839c6c41a484a3e0390d988621bd868610c201ab884360f94
    cited_regions:
    - audit
- facet: licence.fine_tuning
  value: prohibited
  state: known
  sources:
  - source_id: model-143-openai-gpt-5-4
    snapshot_ref: sha256:56c7e709958cf5eab6e96673a1c0f85e250345ff31d6165bbcb48609f38ac581
    cited_regions:
    - model-spec
  - source_id: model-143-openai-services-agreement
    snapshot_ref: sha256:281462a94d8676b839c6c41a484a3e0390d988621bd868610c201ab884360f94
    cited_regions:
    - audit
- facet: origin.lab_jurisdiction
  value:
  - US
  state: known
  sources:
  - source_id: model-143-openai-gpt-5-4
    snapshot_ref: sha256:56c7e709958cf5eab6e96673a1c0f85e250345ff31d6165bbcb48609f38ac581
    cited_regions:
    - model-spec
  - source_id: model-143-openai-models-overview
    snapshot_ref: sha256:bdc3168feccafca027197f5ec142f4ec4ff7c61466085d47931e9093525e6de4
    cited_regions:
    - audit
  - source_id: model-143-openai-changelog
    snapshot_ref: sha256:b2081a8984a0212a31945f67d1e9e8983ed396b736bb4767901472a5d86b9f06
    cited_regions:
    - audit
  - source_id: model-143-openai-reasoning
    snapshot_ref: sha256:d10bae47e0233ce7428779d30bc1edf6f69784f267140c277cb58fe01ebe4a77
    cited_regions:
    - audit
  - source_id: model-143-openai-services-agreement
    snapshot_ref: sha256:281462a94d8676b839c6c41a484a3e0390d988621bd868610c201ab884360f94
    cited_regions:
    - audit
- facet: origin.base_lineage
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-openai-gpt-5-4
    snapshot_ref: sha256:56c7e709958cf5eab6e96673a1c0f85e250345ff31d6165bbcb48609f38ac581
    cited_regions:
    - model-spec
  - source_id: model-143-openai-models-overview
    snapshot_ref: sha256:bdc3168feccafca027197f5ec142f4ec4ff7c61466085d47931e9093525e6de4
    cited_regions:
    - audit
  - source_id: model-143-openai-changelog
    snapshot_ref: sha256:b2081a8984a0212a31945f67d1e9e8983ed396b736bb4767901472a5d86b9f06
    cited_regions:
    - audit
  - source_id: model-143-openai-reasoning
    snapshot_ref: sha256:d10bae47e0233ce7428779d30bc1edf6f69784f267140c277cb58fe01ebe4a77
    cited_regions:
    - audit
  - source_id: model-143-openai-services-agreement
    snapshot_ref: sha256:281462a94d8676b839c6c41a484a3e0390d988621bd868610c201ab884360f94
    cited_regions:
    - audit
  checked_sources:
  - model-143-openai-gpt-5-4
  - model-143-openai-models-overview
  - model-143-openai-changelog
  - model-143-openai-reasoning
  - model-143-openai-services-agreement
- facet: origin.weights_hosting
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-openai-gpt-5-4
    snapshot_ref: sha256:56c7e709958cf5eab6e96673a1c0f85e250345ff31d6165bbcb48609f38ac581
    cited_regions:
    - model-spec
  - source_id: model-143-openai-models-overview
    snapshot_ref: sha256:bdc3168feccafca027197f5ec142f4ec4ff7c61466085d47931e9093525e6de4
    cited_regions:
    - audit
  - source_id: model-143-openai-changelog
    snapshot_ref: sha256:b2081a8984a0212a31945f67d1e9e8983ed396b736bb4767901472a5d86b9f06
    cited_regions:
    - audit
  - source_id: model-143-openai-reasoning
    snapshot_ref: sha256:d10bae47e0233ce7428779d30bc1edf6f69784f267140c277cb58fe01ebe4a77
    cited_regions:
    - audit
  - source_id: model-143-openai-services-agreement
    snapshot_ref: sha256:281462a94d8676b839c6c41a484a3e0390d988621bd868610c201ab884360f94
    cited_regions:
    - audit
  checked_sources:
  - model-143-openai-gpt-5-4
  - model-143-openai-models-overview
  - model-143-openai-changelog
  - model-143-openai-reasoning
  - model-143-openai-services-agreement
- facet: model.release_date
  value: '2026-03-05'
  state: known
  sources:
  - source_id: model-143-openai-gpt-5-4
    snapshot_ref: sha256:56c7e709958cf5eab6e96673a1c0f85e250345ff31d6165bbcb48609f38ac581
    cited_regions:
    - model-spec
  - source_id: model-143-openai-models-overview
    snapshot_ref: sha256:bdc3168feccafca027197f5ec142f4ec4ff7c61466085d47931e9093525e6de4
    cited_regions:
    - audit
  - source_id: model-143-openai-changelog
    snapshot_ref: sha256:b2081a8984a0212a31945f67d1e9e8983ed396b736bb4767901472a5d86b9f06
    cited_regions:
    - audit
  - source_id: model-143-openai-reasoning
    snapshot_ref: sha256:d10bae47e0233ce7428779d30bc1edf6f69784f267140c277cb58fe01ebe4a77
    cited_regions:
    - audit
  - source_id: model-143-openai-services-agreement
    snapshot_ref: sha256:281462a94d8676b839c6c41a484a3e0390d988621bd868610c201ab884360f94
    cited_regions:
    - audit
- facet: model.lifecycle
  value: active
  state: known
  sources:
  - source_id: model-143-openai-gpt-5-4
    snapshot_ref: sha256:56c7e709958cf5eab6e96673a1c0f85e250345ff31d6165bbcb48609f38ac581
    cited_regions:
    - model-spec
  - source_id: model-143-openai-models-overview
    snapshot_ref: sha256:bdc3168feccafca027197f5ec142f4ec4ff7c61466085d47931e9093525e6de4
    cited_regions:
    - audit
  - source_id: model-143-openai-changelog
    snapshot_ref: sha256:b2081a8984a0212a31945f67d1e9e8983ed396b736bb4767901472a5d86b9f06
    cited_regions:
    - audit
  - source_id: model-143-openai-reasoning
    snapshot_ref: sha256:d10bae47e0233ce7428779d30bc1edf6f69784f267140c277cb58fe01ebe4a77
    cited_regions:
    - audit
  - source_id: model-143-openai-services-agreement
    snapshot_ref: sha256:281462a94d8676b839c6c41a484a3e0390d988621bd868610c201ab884360f94
    cited_regions:
    - audit
- facet: feature.tool_calling
  value: true
  state: known
  sources:
  - source_id: model-143-openai-gpt-5-4
    snapshot_ref: sha256:56c7e709958cf5eab6e96673a1c0f85e250345ff31d6165bbcb48609f38ac581
    cited_regions:
    - model-spec
  - source_id: model-143-openai-models-overview
    snapshot_ref: sha256:bdc3168feccafca027197f5ec142f4ec4ff7c61466085d47931e9093525e6de4
    cited_regions:
    - audit
  - source_id: model-143-openai-changelog
    snapshot_ref: sha256:b2081a8984a0212a31945f67d1e9e8983ed396b736bb4767901472a5d86b9f06
    cited_regions:
    - audit
  - source_id: model-143-openai-reasoning
    snapshot_ref: sha256:d10bae47e0233ce7428779d30bc1edf6f69784f267140c277cb58fe01ebe4a77
    cited_regions:
    - audit
  - source_id: model-143-openai-services-agreement
    snapshot_ref: sha256:281462a94d8676b839c6c41a484a3e0390d988621bd868610c201ab884360f94
    cited_regions:
    - audit
- facet: feature.structured_output
  value: true
  state: known
  sources:
  - source_id: model-143-openai-gpt-5-4
    snapshot_ref: sha256:56c7e709958cf5eab6e96673a1c0f85e250345ff31d6165bbcb48609f38ac581
    cited_regions:
    - model-spec
  - source_id: model-143-openai-models-overview
    snapshot_ref: sha256:bdc3168feccafca027197f5ec142f4ec4ff7c61466085d47931e9093525e6de4
    cited_regions:
    - audit
  - source_id: model-143-openai-changelog
    snapshot_ref: sha256:b2081a8984a0212a31945f67d1e9e8983ed396b736bb4767901472a5d86b9f06
    cited_regions:
    - audit
  - source_id: model-143-openai-reasoning
    snapshot_ref: sha256:d10bae47e0233ce7428779d30bc1edf6f69784f267140c277cb58fe01ebe4a77
    cited_regions:
    - audit
  - source_id: model-143-openai-services-agreement
    snapshot_ref: sha256:281462a94d8676b839c6c41a484a3e0390d988621bd868610c201ab884360f94
    cited_regions:
    - audit
- facet: feature.effort_controls
  value: true
  state: known
  sources:
  - source_id: model-143-openai-gpt-5-4
    snapshot_ref: sha256:56c7e709958cf5eab6e96673a1c0f85e250345ff31d6165bbcb48609f38ac581
    cited_regions:
    - model-spec
  - source_id: model-143-openai-models-overview
    snapshot_ref: sha256:bdc3168feccafca027197f5ec142f4ec4ff7c61466085d47931e9093525e6de4
    cited_regions:
    - audit
  - source_id: model-143-openai-changelog
    snapshot_ref: sha256:b2081a8984a0212a31945f67d1e9e8983ed396b736bb4767901472a5d86b9f06
    cited_regions:
    - audit
  - source_id: model-143-openai-reasoning
    snapshot_ref: sha256:d10bae47e0233ce7428779d30bc1edf6f69784f267140c277cb58fe01ebe4a77
    cited_regions:
    - audit
  - source_id: model-143-openai-services-agreement
    snapshot_ref: sha256:281462a94d8676b839c6c41a484a3e0390d988621bd868610c201ab884360f94
    cited_regions:
    - audit
- facet: feature.batch
  value: true
  state: known
  sources:
  - source_id: model-143-openai-gpt-5-4
    snapshot_ref: sha256:56c7e709958cf5eab6e96673a1c0f85e250345ff31d6165bbcb48609f38ac581
    cited_regions:
    - model-spec
  - source_id: model-143-openai-models-overview
    snapshot_ref: sha256:bdc3168feccafca027197f5ec142f4ec4ff7c61466085d47931e9093525e6de4
    cited_regions:
    - audit
  - source_id: model-143-openai-changelog
    snapshot_ref: sha256:b2081a8984a0212a31945f67d1e9e8983ed396b736bb4767901472a5d86b9f06
    cited_regions:
    - audit
  - source_id: model-143-openai-reasoning
    snapshot_ref: sha256:d10bae47e0233ce7428779d30bc1edf6f69784f267140c277cb58fe01ebe4a77
    cited_regions:
    - audit
  - source_id: model-143-openai-services-agreement
    snapshot_ref: sha256:281462a94d8676b839c6c41a484a3e0390d988621bd868610c201ab884360f94
    cited_regions:
    - audit
- facet: feature.streaming
  value: true
  state: known
  sources:
  - source_id: model-143-openai-gpt-5-4
    snapshot_ref: sha256:56c7e709958cf5eab6e96673a1c0f85e250345ff31d6165bbcb48609f38ac581
    cited_regions:
    - model-spec
  - source_id: model-143-openai-models-overview
    snapshot_ref: sha256:bdc3168feccafca027197f5ec142f4ec4ff7c61466085d47931e9093525e6de4
    cited_regions:
    - audit
  - source_id: model-143-openai-changelog
    snapshot_ref: sha256:b2081a8984a0212a31945f67d1e9e8983ed396b736bb4767901472a5d86b9f06
    cited_regions:
    - audit
  - source_id: model-143-openai-reasoning
    snapshot_ref: sha256:d10bae47e0233ce7428779d30bc1edf6f69784f267140c277cb58fe01ebe4a77
    cited_regions:
    - audit
  - source_id: model-143-openai-services-agreement
    snapshot_ref: sha256:281462a94d8676b839c6c41a484a3e0390d988621bd868610c201ab884360f94
    cited_regions:
    - audit
card_schema_version: '3.0'
card_author: models.dev-seeder
card_created: '2026-04-05'
card_updated: '2026-09-26'
authoring_guide:
  applies_to:
    model_id: openai/gpt-5-4
    version: gpt-5.4
  as_of: '2026-09-18'
  status: current
  sections:
    prompt_shape:
    - text: 'Start with the smallest prompt that passes evals. Add blocks only for measured failures:
        tool routing, dependency checks, citations, irreversible actions, or tool-boundary rules.'
      sources:
      - url: https://developers.openai.com/api/docs/guides/latest-model/gpt-5.4
        title: Using GPT-5.4
        accessed: '2026-09-18'
        kind: provider-guidance
    - text: Keep outputs compact with an explicit output contract and verbosity controls; verbosity still
        defaults to medium and is a separate knob from reasoning effort.
      sources:
      - url: https://developers.openai.com/api/docs/guides/latest-model/gpt-5.4
        title: Using GPT-5.4
        accessed: '2026-09-18'
        kind: provider-guidance
    system_message:
    - text: 'State a follow-through policy: proceed on reversible low-risk steps, ask before irreversible
        or external side effects, and make user instructions override style while safety does not yield.'
      sources:
      - url: https://developers.openai.com/api/docs/guides/latest-model/gpt-5.4
        title: Using GPT-5.4
        accessed: '2026-09-18'
        kind: provider-guidance
    - text: For mid-conversation changes, send a scoped task_update that names what changed, what still
        applies, and whether it is this turn only.
      sources:
      - url: https://developers.openai.com/api/docs/guides/latest-model/gpt-5.4
        title: Using GPT-5.4
        accessed: '2026-09-18'
        kind: provider-guidance
    reasoning_and_tools:
    - text: reasoning.effort supports none (default), low, medium, high and xhigh. With none, prompt it
        to outline steps; raise effort only after the prompt already has success criteria and tool rules.
      sources:
      - url: https://developers.openai.com/api/docs/guides/latest-model/gpt-5.4
        title: Using GPT-5.4
        accessed: '2026-09-18'
        kind: provider-guidance
      - url: https://developers.openai.com/api/docs/models/gpt-5.4
        title: GPT-5.4
        accessed: '2026-09-18'
        kind: model-docs
    - text: temperature, top_p and logprobs are only valid at effort none; other efforts error. Prefer
        the Responses API so chain-of-thought can be passed between turns.
      sources:
      - url: https://developers.openai.com/api/docs/guides/latest-model/gpt-5.4
        title: Using GPT-5.4
        accessed: '2026-09-18'
        kind: provider-guidance
    - text: Round-trip assistant phase (commentary vs final_answer) or previous_response_id; dropped phase
        can treat a preamble as the final answer.
      sources:
      - url: https://developers.openai.com/api/docs/guides/latest-model/gpt-5.4
        title: Using GPT-5.4
        accessed: '2026-09-18'
        kind: provider-guidance
    - text: Prompt for persistent tool use, prerequisite checks, and a verification loop before high-impact
        actions. Parallelise only independent lookups.
      sources:
      - url: https://developers.openai.com/api/docs/guides/latest-model/gpt-5.4
        title: Using GPT-5.4
        accessed: '2026-09-18'
        kind: provider-guidance
    formatting:
    - text: For SQL/JSON, emit only the target format. For vision or computer use, set image detail explicitly
        (high or original) instead of auto.
      sources:
      - url: https://developers.openai.com/api/docs/guides/latest-model/gpt-5.4
        title: Using GPT-5.4
        accessed: '2026-09-18'
        kind: provider-guidance
    failure_modes:
    - text: Early in a session, tool routing is less reliable; name the intended tool and required lookups.
        Empty retrievals should trigger fallback queries, not a 'nothing found' close.
      sources:
      - url: https://developers.openai.com/api/docs/guides/latest-model/gpt-5.4
        title: Using GPT-5.4
        accessed: '2026-09-18'
        kind: provider-guidance
    retry_advice: []
---


# GPT-5.4

GPT-5.4 is a Llm Reasoning model from OpenAI. Part of the gpt family. Knowledge cutoff: 2025-08-31.

Licence: proprietary. Vendor terms https://openai.com/policies/business-terms/ (OpenAI Services Agreement (effective 1 January 2026)), read 2026-09-18.

## Key Features
- Extended reasoning / chain-of-thought
- Function calling / tool use
- Structured output (JSON mode)
- File/image attachments