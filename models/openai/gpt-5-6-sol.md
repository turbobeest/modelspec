---
model_id: openai/gpt-5-6-sol
display_name: GPT-5.6 Sol
provider: openai
provider_display: OpenAI
family: gpt-sol
version: gpt-5.6-sol
release_date: '2026-07-09'
last_updated: '2026-07-09'
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
  input: 4.0
  output: 20.0
  reasoning: null
  cache_read: 0.4
  cache_write: 5.0
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
  - benchmark_id: gpqa_diamond
    model_id_as_evaluated: GPT-5.6 Sol
    score: 94.6
    unit: percent
    source_url: https://openai.com/index/gpt-5-6/
    source_kind: provider_self_report
    evidence_date: '2026-07-09'
    date_type: published
    verified_at: '2026-09-09'
    benchmark_version: GPQA Diamond
    configuration: GPT-5.6 launch table; the row is labelled by model tier (Sol/Terra/Luna)
      and does not pin a reasoning-effort setting in the cell. Scores are as published
      for that tier, not the Ultra multi-agent configuration.
    limitations: ''
  - benchmark_id: arena_elo_style_control
    model_id_as_evaluated: gpt-5.6-sol-xhigh
    score: 1483.47
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / overall, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category overall,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: xhigh; MODEL-123 max-effort rule). Rating 1483.47 [1478.58, 1488.37], 27069 votes,
      rank 18.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_coding
    model_id_as_evaluated: gpt-5.6-sol-xhigh
    score: 1527.95
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / coding, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category coding,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: xhigh; MODEL-123 max-effort rule). Rating 1527.95 [1520.26, 1535.64], 7547 votes,
      rank 17.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_hard_prompts
    model_id_as_evaluated: gpt-5.6-sol-xhigh
    score: 1508.62
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / hard_prompts, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category hard_prompts,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: xhigh; MODEL-123 max-effort rule). Rating 1508.62 [1502.90, 1514.34], 17808 votes,
      rank 15.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_math
    model_id_as_evaluated: gpt-5.6-sol-xhigh
    score: 1488.05
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / math, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category math, leaderboard_publish_date
      2026-09-13; style control. Highest-effort row for the product (effort: xhigh; MODEL-123
      max-effort rule). Rating 1488.05 [1471.25, 1504.85], 1220 votes, rank 23.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_creative_writing
    model_id_as_evaluated: gpt-5.6-sol-xhigh
    score: 1473.06
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / creative_writing, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category creative_writing,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: xhigh; MODEL-123 max-effort rule). Rating 1473.06 [1463.97, 1482.16], 5344 votes,
      rank 12.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_instruction_following
    model_id_as_evaluated: gpt-5.6-sol-xhigh
    score: 1486.9
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / instruction_following, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category instruction_following,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: xhigh; MODEL-123 max-effort rule). Rating 1486.90 [1479.80, 1494.01], 9363 votes,
      rank 11.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_multi_turn
    model_id_as_evaluated: gpt-5.6-sol-xhigh
    score: 1486.64
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / multi_turn, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category multi_turn,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: xhigh; MODEL-123 max-effort rule). Rating 1486.64 [1477.17, 1496.12], 4537 votes,
      rank 24.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_expert
    model_id_as_evaluated: gpt-5.6-sol-xhigh
    score: 1531.83
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / expert, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category expert,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: xhigh; MODEL-123 max-effort rule). Rating 1531.83 [1520.41, 1543.25], 2954 votes,
      rank 9.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_longer_query
    model_id_as_evaluated: gpt-5.6-sol-xhigh
    score: 1497.87
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / longer_query, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category longer_query,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: xhigh; MODEL-123 max-effort rule). Rating 1497.87 [1491.29, 1504.45], 12438 votes,
      rank 17.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_non_english
    model_id_as_evaluated: gpt-5.6-sol-xhigh
    score: 1474.52
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / non_english, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category non_english,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: xhigh; MODEL-123 max-effort rule). Rating 1474.52 [1468.69, 1480.34], 15900 votes,
      rank 17.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_medicine
    model_id_as_evaluated: gpt-5.6-sol-xhigh
    score: 1482.14
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
      (effort: xhigh; MODEL-123 max-effort rule). Rating 1482.14 [1468.12, 1496.16], 1981 votes,
      rank 47.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_legal
    model_id_as_evaluated: gpt-5.6-sol-xhigh
    score: 1494.13
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
      (effort: xhigh; MODEL-123 max-effort rule). Rating 1494.13 [1481.15, 1507.11], 2270 votes,
      rank 21.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_business
    model_id_as_evaluated: gpt-5.6-sol-xhigh
    score: 1487.62
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
      (effort: xhigh; MODEL-123 max-effort rule). Rating 1487.62 [1478.73, 1496.51], 5232 votes,
      rank 13.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_science
    model_id_as_evaluated: gpt-5.6-sol-xhigh
    score: 1487.41
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
      (effort: xhigh; MODEL-123 max-effort rule). Rating 1487.41 [1477.88, 1496.93], 4331 votes,
      rank 40.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_writing
    model_id_as_evaluated: gpt-5.6-sol-xhigh
    score: 1484.7
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
      (effort: xhigh; MODEL-123 max-effort rule). Rating 1484.70 [1476.70, 1492.69], 7052 votes,
      rank 9.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_vision
    model_id_as_evaluated: gpt-5.6-sol-xhigh
    score: 1285.95
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: vision_style_control / overall, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset vision_style_control, category overall,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: xhigh; MODEL-123 max-effort rule). Rating 1285.95 [1277.57, 1294.32], 7729 votes,
      rank 14.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: gpqa_diamond
    model_id_as_evaluated: gpt-5.6-sol_max
    score: 93.5
    unit: percent
    source_url: https://epoch.ai/benchmarks/gpqa-diamond
    source_kind: independent_evaluator
    evidence_date: '2026-07-09'
    date_type: evaluated
    verified_at: '2026-09-24'
    benchmark_version: GPQA Diamond (Epoch AI run)
    configuration: Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (gpqa_diamond.csv),
      read 2026-09-24. Run started 2026-07-09T02:07:13.000Z; effort max; highest-effort run
      for the model (MODEL-123 max-effort rule), newest on a tie. Standard error 1.57 points.
    limitations: Epoch AI data, CC BY 4.0.
  - benchmark_id: frontiermath_tiers_1_3_v2
    model_id_as_evaluated: gpt-5.6-sol_max
    score: 89.12
    unit: percent
    source_url: https://epoch.ai/frontiermath
    source_kind: independent_evaluator
    evidence_date: '2026-07-09'
    date_type: evaluated
    verified_at: '2026-09-24'
    benchmark_version: FrontierMath-Tiers-1-3-v2-Private (Epoch AI run)
    configuration: Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (frontiermath_tiers_1_3_v2.csv),
      read 2026-09-24. Run started 2026-07-09T02:45:09.000Z; effort max; highest-effort run
      for the model (MODEL-123 max-effort rule), newest on a tie. Standard error 1.85 points.
    limitations: Epoch AI data, CC BY 4.0.
  - benchmark_id: simpleqa_verified
    model_id_as_evaluated: gpt-5.6-sol_max
    score: 69.7
    unit: percent
    source_url: https://epoch.ai/benchmarks/simpleqa-verified
    source_kind: independent_evaluator
    evidence_date: '2026-08-10'
    date_type: evaluated
    verified_at: '2026-09-24'
    benchmark_version: SimpleQA Verified, proportion correct, Epoch AI protocol with anti-abstention
      prompt
    configuration: Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (simpleqa_verified.csv),
      read 2026-09-24. Run started 2026-08-10T23:44:30.000Z; effort max; highest-effort run
      for the model (MODEL-123 max-effort rule), newest on a tie. Standard error 1.45 points.
    limitations: Epoch AI data, CC BY 4.0.
  - benchmark_id: osworld_2
    model_id_as_evaluated: GPT-5.6 Sol (max)
    score: 27.34
    unit: percent
    source_url: https://osworld-v2.xlang.ai/
    source_kind: benchmark_author
    evidence_date: '2026-09-24'
    date_type: evaluated
    verified_at: '2026-09-24'
    benchmark_version: OSWorld 2.0, binary completion, full set
    configuration: Board row as copied in Epoch AI's benchmark data (osworld_2_external.csv,
      https://epoch.ai/data/benchmark_data.zip), read 2026-09-24. Effort max; the highest-effort
      row for the model (MODEL-123 max-effort rule). Step budget 500, tool setting batch tool.
    limitations: A live board's standing, dated by the day ModelSpec read Epoch AI's copy; the
      copy carries no per-row date. Epoch AI data, CC BY 4.0.
  - benchmark_id: frontiercode_v1_1
    model_id_as_evaluated: GPT-5.6 Sol
    score: 47.49
    unit: percent
    source_url: https://cognition.com/frontiercode
    source_kind: benchmark_author
    evidence_date: '2026-09-24'
    date_type: evaluated
    verified_at: '2026-09-24'
    benchmark_version: FrontierCode 1.1, main score (Mean@5)
    configuration: Board row as copied in Epoch AI's benchmark data (frontiercode_external.csv,
      https://epoch.ai/data/benchmark_data.zip), read 2026-09-24. Effort max; the highest-effort
      row for the model (MODEL-123 max-effort rule). Harness codex.
    limitations: A live board's standing, dated by the day ModelSpec read Epoch AI's copy; the
      copy carries no per-row date. Epoch AI data, CC BY 4.0.
  - benchmark_id: vending_bench_2
    model_id_as_evaluated: GPT-5.6 Sol
    score: 9619.37
    unit: USD
    source_url: https://andonlabs.com/evals/vending-bench-2
    source_kind: benchmark_author
    evidence_date: '2026-09-24'
    date_type: evaluated
    verified_at: '2026-09-24'
    benchmark_version: Vending-Bench 2, mean final balance over 5 runs
    configuration: Board row as copied in Epoch AI's benchmark data (vending_bench_2_external.csv,
      https://epoch.ai/data/benchmark_data.zip), read 2026-09-24. Effort unknown; the highest-effort
      row for the model (MODEL-123 max-effort rule).
    limitations: A live board's standing, dated by the day ModelSpec read Epoch AI's copy; the
      copy carries no per-row date. Epoch AI data, CC BY 4.0.
  - benchmark_id: deepswe_v1_1
    model_id_as_evaluated: gpt-5-6-sol (max)
    score: 72.67
    unit: percent
    source_url: https://deepswe.datacurve.ai/
    source_kind: benchmark_author
    evidence_date: '2026-09-24'
    date_type: evaluated
    verified_at: '2026-09-24'
    benchmark_version: DeepSWE v1.1, pass@1, mini-swe-agent
    configuration: Board row as copied in Epoch AI's benchmark data (deepswe_external.csv, https://epoch.ai/data/benchmark_data.zip),
      read 2026-09-24. Effort max; the highest-effort row for the model (MODEL-123 max-effort
      rule). Harness mini-swe-agent.
    limitations: A live board's standing, dated by the day ModelSpec read Epoch AI's copy; the
      copy carries no per-row date. Epoch AI data, CC BY 4.0.
  - benchmark_id: terminal_bench_v4_0
    model_id_as_evaluated: GPT-5.6 Sol (max) with Codex
    score: 37.27
    unit: percent
    source_url: https://www.tbench.ai/leaderboard/terminal-bench/4.0
    source_kind: benchmark_author
    evidence_date: '2026-06-26'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: Terminal-Bench 4.0
    configuration: 'tbench.ai leaderboard row read 2026-09-24: agent Codex (OpenAI), reasoning
      effort max, 330 trials, accuracy 37.27 ± 3.78 (95% CI). The board''s row date is the evidence
      date. Highest-effort row for the model, best agent on a tie.'
    limitations: The agent harness differs between rows; compare rows with the same agent.
  - benchmark_id: tau3_banking
    model_id_as_evaluated: GPT-5.6-sol (xhigh)
    score: 46.91
    unit: percent
    source_url: https://sierra-tau-bench-public.s3.us-west-2.amazonaws.com/submissions/gpt-5-6-sol_sierra_2026-08-04/submission.json
    source_kind: benchmark_author
    evidence_date: '2026-07-22'
    date_type: evaluated
    verified_at: '2026-09-24'
    benchmark_version: τ-Knowledge τ-Banking (banking_knowledge), pass^1
    configuration: τ-bench leaderboard submission gpt-5-6-sol_sierra_2026-08-04, submitted by
      Sierra; retrieval config alltools; reasoning effort xhigh; user simulator gpt-5.2; tau2-bench
      1.0.1. pass^4 27.835051546391753.
    limitations: Banking_knowledge evaluation with AllTools retrieval, GPT-5.2 low-reasoning
      user simulation, four trials, and seed 300.
  - benchmark_id: cursorbench_4
    model_id_as_evaluated: GPT-5.6 Sol (max)
    score: 41.7
    unit: percent
    source_url: https://cursor.com/cursorbench
    source_kind: benchmark_author
    evidence_date: '2026-09-24'
    date_type: evaluated
    verified_at: '2026-09-24'
    benchmark_version: CursorBench 4.0
    configuration: Cursor's CursorBench 4.0 board read 2026-09-24 (tasks updated 2026-09-10
      per its changelog); the board states no row date, so the reading is dated by the observation.
      Highest-effort row (max); $8.23 a task.
    limitations: Runs only in Cursor's production agent harness.
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
card_schema_version: '3.0'
card_author: models.dev-seeder
card_created: '2026-04-05'
card_updated: '2026-04-05'
---

# GPT-5.6 Sol

GPT-5.6 Sol is a Llm Reasoning model from OpenAI. Part of the gpt-sol family. Knowledge cutoff: 2026-02-16.

## Key Features
- Extended reasoning / chain-of-thought
- Function calling / tool use
- Structured output (JSON mode)
- File/image attachments
