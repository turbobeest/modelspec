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
    verified_at: '2026-09-11'
    benchmark_version: METR-Horizon-v1.1
    configuration: Time Horizon 1.1 YAML field p50_horizon_length.estimate, minutes, Inspect-era 1.1 protocol. Public chart shows hours. Not Time Horizon 1.0.
    limitations: YAML CI [186.581591, 768.779526] minutes. METR states measurements above 16 hours are unreliable on this suite.
    id: openai/gpt-5-4#metr_time_horizon_50#8b1d93d1b4c0
    measured_by: benchmark_author
    effort: null
    harness: null
    sources:
    - source_id: model-160-metr-time-horizon-1-1
      snapshot_ref: sha256:2b9284272537c3bdb7af7691cd0ef2854374b4c7f72a10ececc99aca53c419f4
      cited_regions:
      - rows
  - benchmark_id: metr_time_horizon_80
    model_id_as_evaluated: gpt_5_4
    score: 53.877851
    unit: minutes
    source_url: https://metr.org/assets/benchmark_results_1_1.yaml
    source_kind: benchmark_author
    evidence_date: '2026-04-10'
    date_type: published
    verified_at: '2026-09-11'
    benchmark_version: METR-Horizon-v1.1
    configuration: Time Horizon 1.1 YAML field p80_horizon_length.estimate, minutes, Inspect-era 1.1 protocol. Public chart shows hours. Not Time Horizon 1.0.
    limitations: YAML CI [23.957027, 108.679232] minutes. METR states measurements above 16 hours are unreliable on this suite.
    id: openai/gpt-5-4#metr_time_horizon_80#7c024d112d86
    measured_by: benchmark_author
    effort: null
    harness: null
    sources:
    - source_id: model-160-metr-time-horizon-1-1
      snapshot_ref: sha256:2b9284272537c3bdb7af7691cd0ef2854374b4c7f72a10ececc99aca53c419f4
      cited_regions:
      - rows
  - benchmark_id: arena_elo_overall
    model_id_as_evaluated: gpt-5.4-high
    score: 1469.63
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
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
      snapshot_ref: sha256:b2143e53db27d7506c982ed4a7fe246289fd9ba5d181149507f0ee86bae47c18
      cited_regions:
      - rows
    interval:
    - 1465.79
    - 1473.48
    n: 60537
  - benchmark_id: arena_elo_coding
    model_id_as_evaluated: gpt-5.4-high
    score: 1495.51
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
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
      snapshot_ref: sha256:acfd5444c3981590ac4a3e5589d1f54950660ce053f740f44a755d508540045b
      cited_regions:
      - rows
  - benchmark_id: arena_elo_style_control
    model_id_as_evaluated: gpt-5.4-high
    score: 1476.39
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
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
      snapshot_ref: sha256:4662065250a8ba456c98963d631fa259b3f2c305e33d948af0f8907e71c23550
      cited_regions:
      - rows
  - benchmark_id: arena_sc_coding
    model_id_as_evaluated: gpt-5.4-high
    score: 1520.08
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
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
      snapshot_ref: sha256:861d314ad0c414b03631186d10aa7c7ce22220d9f005f2ff007b64e705982f88
      cited_regions:
      - rows
  - benchmark_id: arena_sc_hard_prompts
    model_id_as_evaluated: gpt-5.4-high
    score: 1497.91
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
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
      snapshot_ref: sha256:c76b4360f6dd0a76db1c93cecd958df7ee2bac63ba20b42d7b97bdc0d4d367c0
      cited_regions:
      - rows
  - benchmark_id: arena_sc_math
    model_id_as_evaluated: gpt-5.4-high
    score: 1494.13
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
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
      snapshot_ref: sha256:3b05392555a93acf4a49b4db0f2c55b1706f39ad4af4fdda135d977a41d913bb
      cited_regions:
      - rows
  - benchmark_id: arena_sc_creative_writing
    model_id_as_evaluated: gpt-5.4-high
    score: 1444.19
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
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
      snapshot_ref: sha256:93f67d3f1afc6c8e089098ff841ea62a788d942bdfed88a5af59c391b50e85ba
      cited_regions:
      - rows
  - benchmark_id: arena_sc_instruction_following
    model_id_as_evaluated: gpt-5.4-high
    score: 1472.44
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
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
      snapshot_ref: sha256:3a5c233b5a355ce846a9593281b3a329824f79715d7a088d43b4e16b4591d64d
      cited_regions:
      - rows
  - benchmark_id: arena_sc_multi_turn
    model_id_as_evaluated: gpt-5.4-high
    score: 1493.77
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
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
      snapshot_ref: sha256:06bb5d8537c4748b32de8eebd54c17aa3f5be95aeb38c431641dfd64bf4fbf28
      cited_regions:
      - rows
  - benchmark_id: arena_sc_expert
    model_id_as_evaluated: gpt-5.4-high
    score: 1515.72
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
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
      snapshot_ref: sha256:e096ca48998dee537b46e71137159b733af46c9e61a3b5d945bd96ccd2ddc70a
      cited_regions:
      - rows
  - benchmark_id: arena_sc_longer_query
    model_id_as_evaluated: gpt-5.4-high
    score: 1483.16
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
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
      snapshot_ref: sha256:154dced7e2bf6cc0d1a39b9edb550ed79ffe348a92bb0251a522e3c9515e0ea6
      cited_regions:
      - rows
  - benchmark_id: arena_sc_non_english
    model_id_as_evaluated: gpt-5.4-high
    score: 1468.48
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
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
      snapshot_ref: sha256:baef93b79236b01c043c3d7d41cb98aace9ab4d718250dc82f863d3b692ddbe5
      cited_regions:
      - rows
  - benchmark_id: arena_sc_medicine
    model_id_as_evaluated: gpt-5.4-high
    score: 1475.97
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
      snapshot_ref: sha256:9ac8343014a6f3fa3a087f7596192bcc37d4be5873044ebb2fbf369eddc040f1
      cited_regions:
      - rows
  - benchmark_id: arena_sc_legal
    model_id_as_evaluated: gpt-5.4-high
    score: 1490.58
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
      snapshot_ref: sha256:73dac5a7b8594e73268d51ccc9991781448045bed3be54cd741b37de4ea10317
      cited_regions:
      - rows
  - benchmark_id: arena_sc_business
    model_id_as_evaluated: gpt-5.4-high
    score: 1483.87
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
      snapshot_ref: sha256:55a6c0caed26dbe460df511bb28bba4ccaa9aab5376e2efa6c7ecbdfca3605f0
      cited_regions:
      - rows
  - benchmark_id: arena_sc_science
    model_id_as_evaluated: gpt-5.4-high
    score: 1487.64
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
      snapshot_ref: sha256:e480b4aa4e4c6687e8e7153b1a1e5fcb4b84cef3f20c7df6895c8f7b5b1fab4c
      cited_regions:
      - rows
  - benchmark_id: arena_sc_writing
    model_id_as_evaluated: gpt-5.4-high
    score: 1465.32
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
      snapshot_ref: sha256:cf0d8c375155a60a2cc2ed34fa27600c376b34ce75cd6d7db33dc51f8c6caade
      cited_regions:
      - rows
  - benchmark_id: arena_sc_vision
    model_id_as_evaluated: gpt-5.4-high
    score: 1284.79
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
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
      snapshot_ref: sha256:efd350d481ea9fcae6cff45c72c1226ed2df2a24aeece0839bfe4e0496368ffd
      cited_regions:
      - rows
  - benchmark_id: arena_webdev
    model_id_as_evaluated: gpt-5.4
    score: 1392.0
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-23'
    date_type: published
    verified_at: '2026-09-24'
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
      snapshot_ref: sha256:8c88f6e665fc8a5667d5b00b1a3ef24d70773f37f9f2fe917623c8c29895c5cf
      cited_regions:
      - rows
  - benchmark_id: gpqa_diamond
    model_id_as_evaluated: gpt-5.4-2026-03-05_xhigh
    score: 93.3
    unit: percent
    source_url: https://epoch.ai/benchmarks/gpqa-diamond
    source_kind: independent_evaluator
    evidence_date: '2026-03-06'
    date_type: evaluated
    verified_at: '2026-09-24'
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
      snapshot_ref: sha256:d5f11aa4a63411b644aa536119ea1a7665c4f56ca47d8e11c97fc4e314449fec
      cited_regions:
      - rows
  - benchmark_id: frontiermath_tiers_1_3_v2
    model_id_as_evaluated: gpt-5.4-2026-03-05_xhigh
    score: 78.6
    unit: percent
    source_url: https://epoch.ai/frontiermath
    source_kind: independent_evaluator
    evidence_date: '2026-06-11'
    date_type: evaluated
    verified_at: '2026-09-24'
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
      snapshot_ref: sha256:5f2d315d4902f61209df86bb3a90b5dee0946624126c126708f64c90af13a93a
      cited_regions:
      - rows
  - benchmark_id: simpleqa_verified
    model_id_as_evaluated: gpt-5.4-2026-03-05_xhigh
    score: 45.1
    unit: percent
    source_url: https://epoch.ai/benchmarks/simpleqa-verified
    source_kind: independent_evaluator
    evidence_date: '2026-08-27'
    date_type: evaluated
    verified_at: '2026-09-24'
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
      snapshot_ref: sha256:cd774c02710b0ebf922eb880c96df454e8c5c4ca53d828a8da2a557a00df5275
      cited_regions:
      - rows
  - benchmark_id: swe_bench_verified
    model_id_as_evaluated: gpt-5.4-2026-03-05_high
    score: 76.86
    unit: percent
    source_url: https://epoch.ai/benchmarks/swe-bench-verified
    source_kind: independent_evaluator
    evidence_date: '2026-03-06'
    date_type: evaluated
    verified_at: '2026-09-24'
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
    - source_id: model-143-evidence-epoch-swe-bench-verified-csv
      snapshot_ref: sha256:1b11e51afaab550c3cd39ceb4c28da4cbdd79208bf381dea2407a758cb8276b3
      cited_regions:
      - rows
  - benchmark_id: vending_bench_2
    model_id_as_evaluated: GPT-5.4
    score: 6144.18
    unit: USD
    source_url: https://andonlabs.com/evals/vending-bench-2
    source_kind: benchmark_author
    evidence_date: '2026-09-25'
    date_type: evaluated
    verified_at: '2026-09-24'
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
      snapshot_ref: sha256:6d8ce9e4ae28f6ef99e0c6059b3cc96abf7fefafc7b90b65954fa6c758516731
      cited_regions:
      - rows
  - benchmark_id: deepswe_v1_1
    model_id_as_evaluated: gpt-5-4 (xhigh)
    score: 51.77
    unit: percent
    source_url: https://deepswe.datacurve.ai/
    source_kind: benchmark_author
    evidence_date: '2026-09-25'
    date_type: evaluated
    verified_at: '2026-09-24'
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
      snapshot_ref: sha256:7fcc641eb55d3cfbc8429ea1ef26448ef44bb66772190ee69f8464958c0a79dc
      cited_regions:
      - rows
  - benchmark_id: hle
    model_id_as_evaluated: gpt-5.4-2026-03-05 (xhigh thinking)
    score: 36.24
    unit: percent
    source_url: https://labs.scale.com/leaderboard/humanitys_last_exam
    source_kind: independent_evaluator
    evidence_date: '2026-09-24'
    date_type: evaluated
    verified_at: '2026-09-24'
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
      snapshot_ref: sha256:c7e558ff927cc7aae1ec9d39ba22de7b5db667674ea408c772002222c11818bd
      cited_regions:
      - rows
  - benchmark_id: swe_bench_pro
    model_id_as_evaluated: gpt-5.4 (xHigh)*
    score: 59.1
    unit: percent
    source_url: https://labs.scale.com/leaderboard/swe_bench_pro_public
    source_kind: independent_evaluator
    evidence_date: '2026-04-08'
    date_type: evaluated
    verified_at: '2026-09-24'
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
      snapshot_ref: sha256:b0df5d5cbc6fd2c3925e740d0379f6570e00d58b98ca576c8141e6af67dc0666
      cited_regions:
      - rows
  - benchmark_id: aime_2026
    model_id_as_evaluated: GPT-5.4 (xhigh)
    score: 99.17
    unit: percent
    source_url: https://matharena.ai/competition_tables/aime--aime_2026
    source_kind: independent_evaluator
    evidence_date: '2026-09-26'
    date_type: evaluated
    verified_at: '2026-09-26'
    benchmark_version: AIME 2026, MathArena final-answer table
    configuration: MathArena competition table read 2026-09-26; the table states no run
      date, so the reading is dated by the observation. Effort xhigh; highest-effort row
      for the model. MathArena lists final-answer competitions as deprecated.
    limitations: 'MathArena marks this row: model was released after competition release, so
      contamination is possible.'
    id: openai/gpt-5-4#aime_2026#cb5c8955d750
    measured_by: independent_evaluator
    effort: xhigh
    harness: null
    sources:
    - source_id: model-161-matharena-aime-2026
      snapshot_ref: sha256:4e2ecda474f16b01f7431017114b165b5f28858663e7c409c944c7a902cbbad4
      cited_regions:
      - rows
    - source_id: model-161-matharena-aime-2026-quality
      snapshot_ref: sha256:42dc4483a15950bd8194ce41b09a56b419751989360e5eaf4c379e8a5f5e552e
      cited_regions:
      - rows
    quality_flags:
    - deprecated
    - contamination_warning
  - benchmark_id: tau3_banking
    model_id_as_evaluated: GPT-5.4 (xhigh)
    score: 39.43
    unit: percent
    source_url: https://sierra-tau-bench-public.s3.us-west-2.amazonaws.com/submissions/gpt-5-4_sierra_2026-03-25/submission.json
    source_kind: benchmark_author
    evidence_date: '2026-05-06'
    date_type: evaluated
    verified_at: '2026-09-24'
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
      snapshot_ref: sha256:f8e1aaa03827b9372ec0fdc105b859c61c09b13125cb91be8714043ed6d0967d
      cited_regions:
      - rows
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