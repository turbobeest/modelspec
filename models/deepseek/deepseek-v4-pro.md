---
model_id: deepseek/deepseek-v4-pro
display_name: DeepSeek V4 Pro
provider: deepseek
provider_display: DeepSeek
family: deepseek-thinking
version: deepseek-v4-pro
release_date: '2026-08-12'
last_updated: '2026-08-22'
status: active
model_type: llm-reasoning
model_subtypes: []
tags: []
pipeline_tag: ''
architecture:
  type: null
  total_parameters: 1598839674782
  active_parameters: 49000000000
  num_experts: 384
  experts_per_token: 6
  num_layers: 61
  hidden_size: 7168
  intermediate_size: null
  attention_type: null
  num_attention_heads: 128
  num_kv_heads: 1
  positional_encoding: null
  rope_theta: null
  vocab_size: 129280
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
  output:
  - text
  text:
    max_input_tokens: null
    max_output_tokens: 384000
    context_window: 1000000
    streaming: null
    fill_in_middle: null
    json_mode: true
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
  input: 0.435
  output: 0.87
  reasoning: null
  cache_read: 0.003625
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
    model_id: deepseek-ai/DeepSeek-V4-Pro
    url: https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro
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
  - benchmark_id: gpqa_diamond
    model_id_as_evaluated: DeepSeek-V4-Pro (max)
    score: 90.1
    unit: percent
    source_url: https://arxiv.org/abs/2606.19348
    source_kind: provider_self_report
    evidence_date: '2026-04-26'
    date_type: published
    verified_at: '2026-09-09'
    benchmark_version: GPQA Diamond (Pass@1)
    configuration: Maximum reasoning-effort mode; temperature 1.0. SWE-Verified was
      run in DeepSeek's internal bash + file-edit harness (500-step cap, 512K context),
      not a third-party agent scaffold. LiveCodeBench is reported as v6 on this page
      and was not attached to live_code_bench.
    limitations: ''
  - benchmark_id: mmlu_pro
    model_id_as_evaluated: DeepSeek-V4-Pro (max)
    score: 87.5
    unit: percent
    source_url: https://arxiv.org/abs/2606.19348
    source_kind: provider_self_report
    evidence_date: '2026-04-26'
    date_type: published
    verified_at: '2026-09-09'
    benchmark_version: MMLU-Pro (EM)
    configuration: Maximum reasoning-effort mode; temperature 1.0. SWE-Verified was
      run in DeepSeek's internal bash + file-edit harness (500-step cap, 512K context),
      not a third-party agent scaffold. LiveCodeBench is reported as v6 on this page
      and was not attached to live_code_bench.
    limitations: ''
    id: deepseek/deepseek-v4-pro#mmlu_pro#ae826abe812d
    measured_by: provider_self_report
    effort: max
    harness: null
    sources:
    - source_id: model-191-deepseek-v4-pro-paper
      snapshot_ref: sha256:1b80985eddbf33a5f1002d045354b2cace7160186c7d3c05e6e7edb3c0778115
      cited_regions:
      - evidence
  - benchmark_id: swe_bench_verified
    model_id_as_evaluated: DeepSeek-V4-Pro (max)
    score: 80.6
    unit: percent
    source_url: https://arxiv.org/abs/2606.19348
    source_kind: provider_self_report
    evidence_date: '2026-04-26'
    date_type: published
    verified_at: '2026-09-09'
    benchmark_version: SWE-bench Verified (Resolved)
    configuration: Maximum reasoning-effort mode; temperature 1.0. SWE-Verified was
      run in DeepSeek's internal bash + file-edit harness (500-step cap, 512K context),
      not a third-party agent scaffold. LiveCodeBench is reported as v6 on this page
      and was not attached to live_code_bench.
    limitations: ''
  - benchmark_id: arena_elo_style_control
    model_id_as_evaluated: deepseek-v4-pro
    score: 1457.34
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / overall, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category overall,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1457.34 [1453.34, 1461.34], 54130
      votes, rank 57.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: deepseek/deepseek-v4-pro#arena_elo_style_control#ac8b24532794
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
    model_id_as_evaluated: deepseek-v4-pro
    score: 1501.5
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / coding, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category coding,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1501.50 [1495.44, 1507.56], 16143
      votes, rank 65.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: deepseek/deepseek-v4-pro#arena_sc_coding#7bb6a22dd938
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
    model_id_as_evaluated: deepseek-v4-pro
    score: 1479.8
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / hard_prompts, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category hard_prompts,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1479.80 [1475.12, 1484.48], 36039
      votes, rank 56.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: deepseek/deepseek-v4-pro#arena_sc_hard_prompts#1721a1bb9d73
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
    model_id_as_evaluated: deepseek-v4-pro
    score: 1444.63
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / math, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category math, leaderboard_publish_date
      2026-09-13; style control. Highest-effort row for the product (effort: default; MODEL-123
      max-effort rule). Rating 1444.63 [1433.13, 1456.14], 2868 votes, rank 70.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: deepseek/deepseek-v4-pro#arena_sc_math#dac2caeac8b4
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
    model_id_as_evaluated: deepseek-v4-pro
    score: 1443.95
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / creative_writing, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category creative_writing,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1443.95 [1436.47, 1451.44], 8998
      votes, rank 48.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: deepseek/deepseek-v4-pro#arena_sc_creative_writing#30e657b83531
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
    model_id_as_evaluated: deepseek-v4-pro
    score: 1452.55
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / instruction_following, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category instruction_following,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1452.55 [1446.83, 1458.27], 18649
      votes, rank 54.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: deepseek/deepseek-v4-pro#arena_sc_instruction_following#e747acf81c15
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
    model_id_as_evaluated: deepseek-v4-pro
    score: 1475.19
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / multi_turn, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category multi_turn,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1475.19 [1468.01, 1482.38], 9800
      votes, rank 45.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: deepseek/deepseek-v4-pro#arena_sc_multi_turn#cbebd3a79af9
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
    model_id_as_evaluated: deepseek-v4-pro
    score: 1481.35
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / expert, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category expert,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1481.35 [1472.57, 1490.12], 5440
      votes, rank 61.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: deepseek/deepseek-v4-pro#arena_sc_expert#a0b0b1c4a88e
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
    model_id_as_evaluated: deepseek-v4-pro
    score: 1471.54
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / longer_query, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category longer_query,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1471.54 [1466.05, 1477.03], 23898
      votes, rank 52.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: deepseek/deepseek-v4-pro#arena_sc_longer_query#bffd2050cd41
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
    model_id_as_evaluated: deepseek-v4-pro
    score: 1444.72
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / non_english, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category non_english,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1444.72 [1439.90, 1449.54], 30240
      votes, rank 58.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: deepseek/deepseek-v4-pro#arena_sc_non_english#2c74e3a5d154
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
    model_id_as_evaluated: deepseek-v4-pro
    score: 1476.7
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
      (effort: default; MODEL-123 max-effort rule). Rating 1476.70 [1466.20, 1487.21], 3766
      votes, rank 57.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: deepseek/deepseek-v4-pro#arena_sc_medicine#cc8bcc37ece4
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
    model_id_as_evaluated: deepseek-v4-pro
    score: 1473.18
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
      (effort: default; MODEL-123 max-effort rule). Rating 1473.18 [1463.34, 1483.01], 4229
      votes, rank 47.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: deepseek/deepseek-v4-pro#arena_sc_legal#5e2494fe4a5e
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
    model_id_as_evaluated: deepseek-v4-pro
    score: 1460.69
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
      (effort: default; MODEL-123 max-effort rule). Rating 1460.69 [1453.80, 1467.58], 10721
      votes, rank 51.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: deepseek/deepseek-v4-pro#arena_sc_business#5c7b704a0a15
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
    model_id_as_evaluated: deepseek-v4-pro
    score: 1480.7
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
      (effort: default; MODEL-123 max-effort rule). Rating 1480.70 [1473.37, 1488.02], 8597
      votes, rank 50.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: deepseek/deepseek-v4-pro#arena_sc_science#b885a31fd483
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
    model_id_as_evaluated: deepseek-v4-pro
    score: 1450.89
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
      (effort: default; MODEL-123 max-effort rule). Rating 1450.89 [1444.40, 1457.37], 13127
      votes, rank 47.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: deepseek/deepseek-v4-pro#arena_sc_writing#6e7ee8f3ed7a
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
    model_id_as_evaluated: deepseek-v4-pro
    score: 1445.47
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-23'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: webdev / overall, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset webdev, category overall, leaderboard_publish_date
      2026-09-23; no style-controlled variant. Highest-effort row for the product (effort: default;
      MODEL-123 max-effort rule). Rating 1445.47 [1438.97, 1451.96], 13179 votes, rank 62.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: deepseek/deepseek-v4-pro#arena_webdev#a813b293dcd0
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
    model_id_as_evaluated: deepseek-v4-pro_max
    score: 89.65
    unit: percent
    source_url: https://epoch.ai/benchmarks/gpqa-diamond
    source_kind: independent_evaluator
    evidence_date: '2026-06-16'
    date_type: evaluated
    verified_at: '2026-09-28'
    benchmark_version: GPQA Diamond (Epoch AI run)
    configuration: Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (gpqa_diamond.csv),
      read 2026-09-24. Run started 2026-06-16T20:16:55.000Z; effort max; highest-effort run
      for the model (MODEL-123 max-effort rule), newest on a tie. Standard error 1.75 points.
    limitations: Epoch AI data, CC BY 4.0.
    id: deepseek/deepseek-v4-pro#gpqa_diamond#d19463c1378a
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
    model_id_as_evaluated: deepseek-v4-pro_max
    score: 45.26
    unit: percent
    source_url: https://epoch.ai/frontiermath
    source_kind: independent_evaluator
    evidence_date: '2026-06-17'
    date_type: evaluated
    verified_at: '2026-09-28'
    benchmark_version: FrontierMath-Tiers-1-3-v2-Private (Epoch AI run)
    configuration: Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (frontiermath_tiers_1_3_v2.csv),
      read 2026-09-24. Run started 2026-06-17T02:30:14.000Z; effort max; highest-effort run
      for the model (MODEL-123 max-effort rule), newest on a tie. Standard error 2.95 points.
    limitations: Epoch AI data, CC BY 4.0.
    id: deepseek/deepseek-v4-pro#frontiermath_tiers_1_3_v2#dd93eea5663f
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
    model_id_as_evaluated: deepseek-v4-pro_max
    score: 46.99
    unit: percent
    source_url: https://epoch.ai/benchmarks/simpleqa-verified
    source_kind: independent_evaluator
    evidence_date: '2026-08-27'
    date_type: evaluated
    verified_at: '2026-09-28'
    benchmark_version: SimpleQA Verified, proportion correct, Epoch AI protocol with anti-abstention
      prompt
    configuration: Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (simpleqa_verified.csv),
      read 2026-09-24. Run started 2026-08-27T19:30:29.000Z; effort max; highest-effort run
      for the model (MODEL-123 max-effort rule), newest on a tie. Standard error 1.58 points.
    limitations: Epoch AI data, CC BY 4.0.
    id: deepseek/deepseek-v4-pro#simpleqa_verified#49345e002b7f
    measured_by: independent_evaluator
    effort: max
    harness: null
    sources:
    - source_id: model-160-epoch-simpleqa-verified-csv
      snapshot_ref: sha256:1f18c84606f93b761f4bffcfe1f688b4f4bd7d0d26ef1bcfa2486126c4fb123e
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: swe_bench_verified
    model_id_as_evaluated: deepseek-v4-pro_max
    score: 77.64
    unit: percent
    source_url: https://epoch.ai/benchmarks/swe-bench-verified
    source_kind: independent_evaluator
    evidence_date: '2026-06-18'
    date_type: evaluated
    verified_at: '2026-09-28'
    benchmark_version: SWE-bench Verified (Epoch AI run)
    configuration: Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (swe_bench_verified.csv),
      read 2026-09-24. Run started 2026-06-18T17:43:54.039Z; effort max; highest-effort run
      for the model (MODEL-123 max-effort rule), newest on a tie. Standard error 1.90 points.
    limitations: Epoch AI data, CC BY 4.0.
    id: deepseek/deepseek-v4-pro#swe_bench_verified#653a9e640833
    measured_by: independent_evaluator
    effort: max
    harness: null
    sources:
    - source_id: model-160-epoch-swe-bench-verified-csv
      snapshot_ref: sha256:e0247c7d3ab619909d4ad5f823318c22a312ee996c1e620c38dcf888494ec4ca
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: frontiercode_v1_1
    model_id_as_evaluated: DeepSeek V4 Pro
    score: 17.6
    unit: percent
    source_url: https://cognition.com/frontiercode
    source_kind: benchmark_author
    evidence_date: '2026-09-26'
    date_type: evaluated
    verified_at: '2026-09-28'
    benchmark_version: FrontierCode 1.1, main score (Mean@5)
    configuration: Board row as copied in Epoch AI's benchmark data (frontiercode_external.csv,
      https://epoch.ai/data/benchmark_data.zip), read 2026-09-24. Effort none; the highest-effort
      row for the model (MODEL-123 max-effort rule). Harness mini-swe-agent.
    limitations: A live board's standing, dated by the day ModelSpec read Epoch AI's copy; the
      copy carries no per-row date. Epoch AI data, CC BY 4.0.
    id: deepseek/deepseek-v4-pro#frontiercode_v1_1#ca962e1a36fe
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
    model_id_as_evaluated: Deepseek V4 Pro
    score: 3284.52
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
    id: deepseek/deepseek-v4-pro#vending_bench_2#d0ccc210af57
    measured_by: benchmark_author
    effort: null
    harness: null
    sources:
    - source_id: model-160-vending-bench-2
      snapshot_ref: sha256:8724ee26281bff37eb4fe6af19bda2406b8d5fccdd4d54fdbfc44248b32ef12b
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: aime_2026
    model_id_as_evaluated: DeepSeek-v4-Pro (Max)
    score: 96.67
    unit: percent
    source_url: https://matharena.ai/competition_tables/aime--aime_2026
    source_kind: independent_evaluator
    evidence_date: '2026-09-25'
    date_type: evaluated
    verified_at: '2026-09-28'
    benchmark_version: AIME 2026, MathArena final-answer table
    configuration: MathArena competition table read 2026-09-26; the table states no run
      date, so the reading is dated by the observation. Effort max; highest-effort row
      for the model. MathArena lists final-answer competitions as deprecated.
    limitations: 'MathArena marks this row: model was released after competition release, so
      contamination is possible.'
    id: deepseek/deepseek-v4-pro#aime_2026#762af5769a5d
    measured_by: independent_evaluator
    effort: max
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
  - benchmark_id: arena_sc_english
    model_id_as_evaluated: deepseek-v4-pro
    score: 1466.79
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / english, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1466.79 [1461.57,
      1472.01], 23890 votes, rank 57. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:c10623c0b42bc927b984d3933d31aa31c3cd1c21841797328e80981e6d334892
      cited_regions:
      - rows
    id: deepseek/deepseek-v4-pro#arena_sc_english#dbcc2cd8efd9
  - benchmark_id: arena_sc_chinese
    model_id_as_evaluated: deepseek-v4-pro
    score: 1493.3
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / chinese, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1493.30 [1481.45,
      1505.14], 2859 votes, rank 67. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:1e2f3fa3120aa6532923deddea1fcb48e14b14f7e2f3396e16e17304594752bd
      cited_regions:
      - rows
    id: deepseek/deepseek-v4-pro#arena_sc_chinese#0d83a1bcfc4b
  - benchmark_id: arena_sc_japanese
    model_id_as_evaluated: deepseek-v4-pro
    score: 1462.21
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / japanese, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1462.21 [1437.94,
      1486.48], 691 votes, rank 22. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:c9ec43cc46cde9a9a084781e014b590ecb91e24ff239d072e5e3e1fbe299075a
      cited_regions:
      - rows
    id: deepseek/deepseek-v4-pro#arena_sc_japanese#79705f0e7843
  - benchmark_id: arena_sc_korean
    model_id_as_evaluated: deepseek-v4-pro
    score: 1418.01
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / korean, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1418.01 [1398.63,
      1437.38], 1069 votes, rank 49. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:da67028715236f4510ef6cd2b29aa4a819e6b581fd48575bbee287a0a72545fa
      cited_regions:
      - rows
    id: deepseek/deepseek-v4-pro#arena_sc_korean#718f818d82a0
  - benchmark_id: arena_sc_russian
    model_id_as_evaluated: deepseek-v4-pro
    score: 1457.01
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / russian, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1457.01 [1448.43,
      1465.60], 5695 votes, rank 56. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:3d6ede20ed72833ccae1f56c86762a83c811d6fcb89f7960178d516bbb50aa8d
      cited_regions:
      - rows
    id: deepseek/deepseek-v4-pro#arena_sc_russian#b9bb34d6dd9f
  - benchmark_id: arena_sc_spanish
    model_id_as_evaluated: deepseek-v4-pro
    score: 1454.23
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / spanish, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1454.23 [1438.59,
      1469.88], 1690 votes, rank 53. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:626c233148bb4156f80113d49c8163082ed947cbfb64e20739771d4fe07b33f1
      cited_regions:
      - rows
    id: deepseek/deepseek-v4-pro#arena_sc_spanish#43fbb5a4191f
  - benchmark_id: arena_sc_german
    model_id_as_evaluated: deepseek-v4-pro
    score: 1467.7
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / german, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1467.70 [1447.73,
      1487.68], 955 votes, rank 42. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:6074611b99cf8732f4dee1ad2a5718683b7a9ca7fdff6588d35ba1863ea5f8ac
      cited_regions:
      - rows
    id: deepseek/deepseek-v4-pro#arena_sc_german#a71904394306
  - benchmark_id: arena_sc_french
    model_id_as_evaluated: deepseek-v4-pro
    score: 1484.3
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / french, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1484.30 [1469.29,
      1499.31], 2118 votes, rank 45. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:26b468ee0d48430ff995f4feb0483b5c391cb383a59ea1755a4e91eeb0f6a8f2
      cited_regions:
      - rows
    id: deepseek/deepseek-v4-pro#arena_sc_french#cdf321bfff92
  - benchmark_id: arena_sc_polish
    model_id_as_evaluated: deepseek-v4-pro
    score: 1467.43
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / polish, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1467.43 [1449.05,
      1485.82], 1084 votes, rank 41. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:1d2df11d9abaf322e77c330fab6d5e5ef26979c835443f67601b6c89b8f3f299
      cited_regions:
      - rows
    id: deepseek/deepseek-v4-pro#arena_sc_polish#30a19ee53063
  - benchmark_id: arena_sc_industry_software_it_services
    model_id_as_evaluated: deepseek-v4-pro
    score: 1491.76
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / industry_software_and_it_services, latest split, revision
      1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1491.76 [1486.38,
      1497.14], 22255 votes, rank 59. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:4538dd5bcb06397043fc55c64535410a284e7da8668e8c13cc2950c6f1baa37c
      cited_regions:
      - rows
    id: deepseek/deepseek-v4-pro#arena_sc_industry_software_it_services#bcc3ebdb7b45
  - benchmark_id: arena_sc_industry_entertainment_sports_media
    model_id_as_evaluated: deepseek-v4-pro
    score: 1433.68
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / industry_entertainment_and_sports_and_media, latest
      split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1433.68 [1426.88,
      1440.47], 11822 votes, rank 56. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:89233e13dec450388587fa44e3af9cfb82da53034e616b951c1cbe809b0c4cef
      cited_regions:
      - rows
    id: deepseek/deepseek-v4-pro#arena_sc_industry_entertainment_sports_media#283ad52c7508
  - benchmark_id: arena_sc_industry_mathematical
    model_id_as_evaluated: deepseek-v4-pro
    score: 1460.32
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / industry_mathematical, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1460.32 [1448.83,
      1471.81], 2997 votes, rank 59. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:514a2f81b6bce9bc34481c6e0d7af71184302842a4f5b8284657dc5024965f25
      cited_regions:
      - rows
    id: deepseek/deepseek-v4-pro#arena_sc_industry_mathematical#b926d6825a42
  - benchmark_id: arena_sc_factuality
    model_id_as_evaluated: deepseek-v4-pro
    score: 1454.79
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-28'
    verified_at: '2026-09-28'
    benchmark_version: text_factuality / overall, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1454.79 [1451.60,
      1457.97], 54066 votes, rank 50. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-factuality
      snapshot_ref: sha256:359d85539a6e849ffbfe46427efdefadb4be9c907f9fbea9f799ce7bbf6c52c2
      cited_regions:
      - rows
    id: deepseek/deepseek-v4-pro#arena_sc_factuality#ef8c5406fdb9
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
  models_dev_url: https://models.dev/deepseek
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
  - source_id: model-143-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:c4d714818a4d3333542edc7d38ea065825a0cf7aa8fea3605bbd1d1c18e4a610
    cited_regions:
    - model-spec
  - source_id: model-143-deepseek-function-calling
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
  - source_id: model-143-deepseek-json-output
    snapshot_ref: sha256:f728a4dad99c2328c9c982b08c113f400abcc1a7eba238f08738f51a951d1b30
    cited_regions:
    - audit
  - source_id: model-143-deepseek-streaming
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
- facet: model.input_modalities
  value:
  - text
  state: known
  sources:
  - source_id: model-143-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:c4d714818a4d3333542edc7d38ea065825a0cf7aa8fea3605bbd1d1c18e4a610
    cited_regions:
    - model-spec
  - source_id: model-143-deepseek-function-calling
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
  - source_id: model-143-deepseek-json-output
    snapshot_ref: sha256:f728a4dad99c2328c9c982b08c113f400abcc1a7eba238f08738f51a951d1b30
    cited_regions:
    - audit
  - source_id: model-143-deepseek-streaming
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
- facet: model.output_modalities
  value:
  - text
  state: known
  sources:
  - source_id: model-143-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:c4d714818a4d3333542edc7d38ea065825a0cf7aa8fea3605bbd1d1c18e4a610
    cited_regions:
    - model-spec
  - source_id: model-143-deepseek-function-calling
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
  - source_id: model-143-deepseek-json-output
    snapshot_ref: sha256:f728a4dad99c2328c9c982b08c113f400abcc1a7eba238f08738f51a951d1b30
    cited_regions:
    - audit
  - source_id: model-143-deepseek-streaming
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
- facet: model.context_window
  value: 1000000
  state: known
  sources:
  - source_id: model-143-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:c4d714818a4d3333542edc7d38ea065825a0cf7aa8fea3605bbd1d1c18e4a610
    cited_regions:
    - model-spec
  - source_id: model-143-deepseek-function-calling
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
  - source_id: model-143-deepseek-json-output
    snapshot_ref: sha256:f728a4dad99c2328c9c982b08c113f400abcc1a7eba238f08738f51a951d1b30
    cited_regions:
    - audit
  - source_id: model-143-deepseek-streaming
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
- facet: model.max_output_tokens
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:c4d714818a4d3333542edc7d38ea065825a0cf7aa8fea3605bbd1d1c18e4a610
    cited_regions:
    - model-spec
  - source_id: model-143-deepseek-function-calling
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
  - source_id: model-143-deepseek-json-output
    snapshot_ref: sha256:f728a4dad99c2328c9c982b08c113f400abcc1a7eba238f08738f51a951d1b30
    cited_regions:
    - audit
  - source_id: model-143-deepseek-streaming
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
  - source_id: model-143-deepseek-v4-license
    snapshot_ref: sha256:f2c6c602815669d292889e5be8c802f2ed950653b77999b1584e8e6aed25d040
    cited_regions:
    - audit
  - source_id: model-143-hf-metadata-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:4d07285dd7292c42d15980fc6296f9956bf8a655529284a97be5b1b9eacea13f
    cited_regions:
    - audit
  checked_sources:
  - model-143-deepseek-deepseek-v4-pro
  - model-143-deepseek-function-calling
  - model-143-deepseek-json-output
  - model-143-deepseek-streaming
  - model-143-deepseek-v4-license
  - model-143-hf-metadata-deepseek-deepseek-v4-pro
- facet: model.weights_openness
  value: open_weights
  state: known
  sources:
  - source_id: model-143-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:c4d714818a4d3333542edc7d38ea065825a0cf7aa8fea3605bbd1d1c18e4a610
    cited_regions:
    - model-spec
  - source_id: model-143-hf-metadata-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:4d07285dd7292c42d15980fc6296f9956bf8a655529284a97be5b1b9eacea13f
    cited_regions:
    - audit
  - source_id: model-143-deepseek-v4-license
    snapshot_ref: sha256:f2c6c602815669d292889e5be8c802f2ed950653b77999b1584e8e6aed25d040
    cited_regions:
    - audit
  - source_id: model-143-deepseek-function-calling
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
  - source_id: model-143-deepseek-json-output
    snapshot_ref: sha256:f728a4dad99c2328c9c982b08c113f400abcc1a7eba238f08738f51a951d1b30
    cited_regions:
    - audit
  - source_id: model-143-deepseek-streaming
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
- facet: licence.commercial_use
  value: permitted
  state: known
  sources:
  - source_id: model-143-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:c4d714818a4d3333542edc7d38ea065825a0cf7aa8fea3605bbd1d1c18e4a610
    cited_regions:
    - model-spec
  - source_id: model-143-deepseek-v4-license
    snapshot_ref: sha256:f2c6c602815669d292889e5be8c802f2ed950653b77999b1584e8e6aed25d040
    cited_regions:
    - audit
- facet: licence.user_cap
  value: unbounded
  state: known
  sources:
  - source_id: model-143-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:c4d714818a4d3333542edc7d38ea065825a0cf7aa8fea3605bbd1d1c18e4a610
    cited_regions:
    - model-spec
  - source_id: model-143-deepseek-v4-license
    snapshot_ref: sha256:f2c6c602815669d292889e5be8c802f2ed950653b77999b1584e8e6aed25d040
    cited_regions:
    - audit
- facet: licence.output_training
  value: permitted
  state: known
  sources:
  - source_id: model-143-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:c4d714818a4d3333542edc7d38ea065825a0cf7aa8fea3605bbd1d1c18e4a610
    cited_regions:
    - model-spec
  - source_id: model-143-deepseek-v4-license
    snapshot_ref: sha256:f2c6c602815669d292889e5be8c802f2ed950653b77999b1584e8e6aed25d040
    cited_regions:
    - audit
- facet: licence.fine_tuning
  value: permitted
  state: known
  sources:
  - source_id: model-143-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:c4d714818a4d3333542edc7d38ea065825a0cf7aa8fea3605bbd1d1c18e4a610
    cited_regions:
    - model-spec
  - source_id: model-143-deepseek-v4-license
    snapshot_ref: sha256:f2c6c602815669d292889e5be8c802f2ed950653b77999b1584e8e6aed25d040
    cited_regions:
    - audit
- facet: origin.lab_jurisdiction
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:c4d714818a4d3333542edc7d38ea065825a0cf7aa8fea3605bbd1d1c18e4a610
    cited_regions:
    - model-spec
  - source_id: model-143-deepseek-function-calling
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
  - source_id: model-143-deepseek-json-output
    snapshot_ref: sha256:f728a4dad99c2328c9c982b08c113f400abcc1a7eba238f08738f51a951d1b30
    cited_regions:
    - audit
  - source_id: model-143-deepseek-streaming
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
  - source_id: model-143-deepseek-v4-license
    snapshot_ref: sha256:f2c6c602815669d292889e5be8c802f2ed950653b77999b1584e8e6aed25d040
    cited_regions:
    - audit
  - source_id: model-143-hf-metadata-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:4d07285dd7292c42d15980fc6296f9956bf8a655529284a97be5b1b9eacea13f
    cited_regions:
    - audit
  checked_sources:
  - model-143-deepseek-deepseek-v4-pro
  - model-143-deepseek-function-calling
  - model-143-deepseek-json-output
  - model-143-deepseek-streaming
  - model-143-deepseek-v4-license
  - model-143-hf-metadata-deepseek-deepseek-v4-pro
- facet: origin.base_lineage
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:c4d714818a4d3333542edc7d38ea065825a0cf7aa8fea3605bbd1d1c18e4a610
    cited_regions:
    - model-spec
  - source_id: model-143-deepseek-function-calling
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
  - source_id: model-143-deepseek-json-output
    snapshot_ref: sha256:f728a4dad99c2328c9c982b08c113f400abcc1a7eba238f08738f51a951d1b30
    cited_regions:
    - audit
  - source_id: model-143-deepseek-streaming
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
  - source_id: model-143-deepseek-v4-license
    snapshot_ref: sha256:f2c6c602815669d292889e5be8c802f2ed950653b77999b1584e8e6aed25d040
    cited_regions:
    - audit
  - source_id: model-143-hf-metadata-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:4d07285dd7292c42d15980fc6296f9956bf8a655529284a97be5b1b9eacea13f
    cited_regions:
    - audit
  checked_sources:
  - model-143-deepseek-deepseek-v4-pro
  - model-143-deepseek-function-calling
  - model-143-deepseek-json-output
  - model-143-deepseek-streaming
  - model-143-deepseek-v4-license
  - model-143-hf-metadata-deepseek-deepseek-v4-pro
- facet: origin.weights_hosting
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:c4d714818a4d3333542edc7d38ea065825a0cf7aa8fea3605bbd1d1c18e4a610
    cited_regions:
    - model-spec
  - source_id: model-143-deepseek-function-calling
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
  - source_id: model-143-deepseek-json-output
    snapshot_ref: sha256:f728a4dad99c2328c9c982b08c113f400abcc1a7eba238f08738f51a951d1b30
    cited_regions:
    - audit
  - source_id: model-143-deepseek-streaming
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
  - source_id: model-143-deepseek-v4-license
    snapshot_ref: sha256:f2c6c602815669d292889e5be8c802f2ed950653b77999b1584e8e6aed25d040
    cited_regions:
    - audit
  - source_id: model-143-hf-metadata-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:4d07285dd7292c42d15980fc6296f9956bf8a655529284a97be5b1b9eacea13f
    cited_regions:
    - audit
  checked_sources:
  - model-143-deepseek-deepseek-v4-pro
  - model-143-deepseek-function-calling
  - model-143-deepseek-json-output
  - model-143-deepseek-streaming
  - model-143-deepseek-v4-license
  - model-143-hf-metadata-deepseek-deepseek-v4-pro
- facet: model.release_date
  value: '2026-08-12'
  state: known
  sources:
  - source_id: model-143-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:c4d714818a4d3333542edc7d38ea065825a0cf7aa8fea3605bbd1d1c18e4a610
    cited_regions:
    - model-spec
  - source_id: model-143-hf-metadata-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:4d07285dd7292c42d15980fc6296f9956bf8a655529284a97be5b1b9eacea13f
    cited_regions:
    - audit
  - source_id: model-143-deepseek-function-calling
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
  - source_id: model-143-deepseek-json-output
    snapshot_ref: sha256:f728a4dad99c2328c9c982b08c113f400abcc1a7eba238f08738f51a951d1b30
    cited_regions:
    - audit
  - source_id: model-143-deepseek-streaming
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
- facet: model.lifecycle
  value: active
  state: known
  sources:
  - source_id: model-143-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:c4d714818a4d3333542edc7d38ea065825a0cf7aa8fea3605bbd1d1c18e4a610
    cited_regions:
    - model-spec
  - source_id: model-143-hf-metadata-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:4d07285dd7292c42d15980fc6296f9956bf8a655529284a97be5b1b9eacea13f
    cited_regions:
    - audit
  - source_id: model-143-deepseek-function-calling
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
  - source_id: model-143-deepseek-json-output
    snapshot_ref: sha256:f728a4dad99c2328c9c982b08c113f400abcc1a7eba238f08738f51a951d1b30
    cited_regions:
    - audit
  - source_id: model-143-deepseek-streaming
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
- facet: feature.tool_calling
  value: true
  state: known
  sources:
  - source_id: model-143-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:c4d714818a4d3333542edc7d38ea065825a0cf7aa8fea3605bbd1d1c18e4a610
    cited_regions:
    - model-spec
  - source_id: model-143-deepseek-function-calling
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
  - source_id: model-143-deepseek-json-output
    snapshot_ref: sha256:f728a4dad99c2328c9c982b08c113f400abcc1a7eba238f08738f51a951d1b30
    cited_regions:
    - audit
  - source_id: model-143-deepseek-streaming
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
- facet: feature.structured_output
  value: true
  state: known
  sources:
  - source_id: model-143-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:c4d714818a4d3333542edc7d38ea065825a0cf7aa8fea3605bbd1d1c18e4a610
    cited_regions:
    - model-spec
  - source_id: model-143-deepseek-function-calling
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
  - source_id: model-143-deepseek-json-output
    snapshot_ref: sha256:f728a4dad99c2328c9c982b08c113f400abcc1a7eba238f08738f51a951d1b30
    cited_regions:
    - audit
  - source_id: model-143-deepseek-streaming
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
- facet: feature.effort_controls
  value: true
  state: known
  sources:
  - source_id: model-143-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:c4d714818a4d3333542edc7d38ea065825a0cf7aa8fea3605bbd1d1c18e4a610
    cited_regions:
    - model-spec
  - source_id: model-143-deepseek-function-calling
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
  - source_id: model-143-deepseek-json-output
    snapshot_ref: sha256:f728a4dad99c2328c9c982b08c113f400abcc1a7eba238f08738f51a951d1b30
    cited_regions:
    - audit
  - source_id: model-143-deepseek-streaming
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
- facet: feature.batch
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:c4d714818a4d3333542edc7d38ea065825a0cf7aa8fea3605bbd1d1c18e4a610
    cited_regions:
    - model-spec
  - source_id: model-143-deepseek-function-calling
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
  - source_id: model-143-deepseek-json-output
    snapshot_ref: sha256:f728a4dad99c2328c9c982b08c113f400abcc1a7eba238f08738f51a951d1b30
    cited_regions:
    - audit
  - source_id: model-143-deepseek-streaming
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
  - source_id: model-143-deepseek-v4-license
    snapshot_ref: sha256:f2c6c602815669d292889e5be8c802f2ed950653b77999b1584e8e6aed25d040
    cited_regions:
    - audit
  - source_id: model-143-hf-metadata-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:4d07285dd7292c42d15980fc6296f9956bf8a655529284a97be5b1b9eacea13f
    cited_regions:
    - audit
  checked_sources:
  - model-143-deepseek-deepseek-v4-pro
  - model-143-deepseek-function-calling
  - model-143-deepseek-json-output
  - model-143-deepseek-streaming
  - model-143-deepseek-v4-license
  - model-143-hf-metadata-deepseek-deepseek-v4-pro
- facet: feature.streaming
  value: true
  state: known
  sources:
  - source_id: model-143-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:c4d714818a4d3333542edc7d38ea065825a0cf7aa8fea3605bbd1d1c18e4a610
    cited_regions:
    - model-spec
  - source_id: model-143-deepseek-function-calling
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
  - source_id: model-143-deepseek-json-output
    snapshot_ref: sha256:f728a4dad99c2328c9c982b08c113f400abcc1a7eba238f08738f51a951d1b30
    cited_regions:
    - audit
  - source_id: model-143-deepseek-streaming
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
- id: deepseek/deepseek-v4-pro#model.parameters_total
  subject:
    kind: model
    id: deepseek/deepseek-v4-pro
  facet: model.parameters_total
  value: 1598839674782
  state: known
  sources:
  - source_id: model-161-deepseek-v4-pro-rtx-4090-fit
    snapshot_ref: sha256:ede7381cf57ed2b3699b9df7a8a74800a9051d2ac313c90c35b4b0b47a62a96d
    cited_regions:
    - rows
- id: deepseek/deepseek-v4-pro#model.fits_hardware
  subject:
    kind: model
    id: deepseek/deepseek-v4-pro
  facet: model.fits_hardware
  value: []
  state: known
  sources:
  - source_id: model-161-deepseek-v4-pro-rtx-4090-fit
    snapshot_ref: sha256:ede7381cf57ed2b3699b9df7a8a74800a9051d2ac313c90c35b4b0b47a62a96d
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

# DeepSeek V4 Pro

DeepSeek V4 Pro is a Llm Reasoning model from DeepSeek. Part of the deepseek-thinking family.

## Key Features
- Extended reasoning / chain-of-thought
- Function calling / tool use
- Structured output (JSON mode)
- Open weights
