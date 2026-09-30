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
    evidence_date: '2026-09-30'
    date_type: published
    verified_at: '2026-09-30'
    benchmark_version: METR-Horizon-v1.1
    configuration: Time Horizon 1.1 YAML field p50_horizon_length.estimate, minutes, Inspect-era 1.1 protocol. Public chart shows hours. Not Time Horizon 1.0.
    limitations: YAML CI [186.581591, 768.779526] minutes. METR states measurements above 16 hours are unreliable on this suite.
    id: openai/gpt-5-4#metr_time_horizon_50#6e616a6d1355
    measured_by: benchmark_author
    effort: null
    harness: null
    sources:
    - source_id: model-160-metr-time-horizon-1-1
      snapshot_ref: sha256:fd42a3e290ee11fecfabc5aaac8242be8b5b9525f66f09ff20f9660f7f251641
      cited_regions:
      - rows
    observed_at: '2026-09-30'
  - benchmark_id: metr_time_horizon_80
    model_id_as_evaluated: gpt_5_4
    score: 53.877851
    unit: minutes
    source_url: https://metr.org/assets/benchmark_results_1_1.yaml
    source_kind: benchmark_author
    evidence_date: '2026-09-30'
    date_type: published
    verified_at: '2026-09-30'
    benchmark_version: METR-Horizon-v1.1
    configuration: Time Horizon 1.1 YAML field p80_horizon_length.estimate, minutes, Inspect-era 1.1 protocol. Public chart shows hours. Not Time Horizon 1.0.
    limitations: YAML CI [23.957027, 108.679232] minutes. METR states measurements above 16 hours are unreliable on this suite.
    id: openai/gpt-5-4#metr_time_horizon_80#e4a0158213de
    measured_by: benchmark_author
    effort: null
    harness: null
    sources:
    - source_id: model-160-metr-time-horizon-1-1
      snapshot_ref: sha256:fd42a3e290ee11fecfabc5aaac8242be8b5b9525f66f09ff20f9660f7f251641
      cited_regions:
      - rows
    observed_at: '2026-09-30'
  - benchmark_id: arena_elo_overall
    model_id_as_evaluated: gpt-5.4-high
    score: 1469.63
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-30'
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
      snapshot_ref: sha256:c75f97c00af5cdce1b735cd74bc058988e6afb9d411c400e70b3420557519012
      cited_regions:
      - rows
    interval:
    - 1465.79
    - 1473.48
    n: 60537
    observed_at: '2026-09-30'
  - benchmark_id: arena_elo_coding
    model_id_as_evaluated: gpt-5.4-high
    score: 1495.51
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-30'
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
      snapshot_ref: sha256:58733a4c25231aa976ad6e615cfa3ced1e2bc97fbbcb92d0a0e04878093fc22e
      cited_regions:
      - rows
    observed_at: '2026-09-30'
  - benchmark_id: arena_elo_style_control
    model_id_as_evaluated: gpt-5.4-high
    score: 1476.39
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-30'
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
      snapshot_ref: sha256:1bc41471fa63c00d5e990f8ff6c7ae8d343321a704311ca8585bda974efd153d
      cited_regions:
      - rows
    observed_at: '2026-09-30'
  - benchmark_id: arena_sc_coding
    model_id_as_evaluated: gpt-5.4-high
    score: 1520.08
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-30'
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
      snapshot_ref: sha256:089deb374ac3c4b394209968c2abcb3cf655a1b9a30a4131b30ac8c829a701b0
      cited_regions:
      - rows
    observed_at: '2026-09-30'
  - benchmark_id: arena_sc_hard_prompts
    model_id_as_evaluated: gpt-5.4-high
    score: 1497.91
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-30'
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
      snapshot_ref: sha256:1b7b4656ca832e762e7f13e33eaaf32c7340cd045337d7ac1f054ef70c4bf1bf
      cited_regions:
      - rows
    observed_at: '2026-09-30'
  - benchmark_id: arena_sc_math
    model_id_as_evaluated: gpt-5.4-high
    score: 1494.13
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-30'
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
      snapshot_ref: sha256:1874a1ccff7caa3c0046e181bbaeb0b8343bce7adb4066b951bc9c44d194ec6d
      cited_regions:
      - rows
    observed_at: '2026-09-30'
  - benchmark_id: arena_sc_creative_writing
    model_id_as_evaluated: gpt-5.4-high
    score: 1444.19
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-30'
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
      snapshot_ref: sha256:fc5f6716f31834193f7b2136ea74bde411ae5ba90fc4ac118d482310e61b38d2
      cited_regions:
      - rows
    observed_at: '2026-09-30'
  - benchmark_id: arena_sc_instruction_following
    model_id_as_evaluated: gpt-5.4-high
    score: 1472.44
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-30'
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
      snapshot_ref: sha256:8dcf9ad77990db5c111c78a9d921ba5a078255a7268d36cda182d9e2e8baed14
      cited_regions:
      - rows
    observed_at: '2026-09-30'
  - benchmark_id: arena_sc_multi_turn
    model_id_as_evaluated: gpt-5.4-high
    score: 1493.77
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-30'
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
      snapshot_ref: sha256:669cce652634672175a1aa830b1e106cc211f20e4f5a8190f41be169b0e8780e
      cited_regions:
      - rows
    observed_at: '2026-09-30'
  - benchmark_id: arena_sc_expert
    model_id_as_evaluated: gpt-5.4-high
    score: 1515.72
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-30'
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
      snapshot_ref: sha256:db8d6995a9ec2ba53e4d4d240df0cce213a4b54b2143ae674970e3afa1dfe764
      cited_regions:
      - rows
    observed_at: '2026-09-30'
  - benchmark_id: arena_sc_longer_query
    model_id_as_evaluated: gpt-5.4-high
    score: 1483.16
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-30'
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
      snapshot_ref: sha256:f27585ee7eee36757893f733b338f207eabe2f9fb0349b6b539f7cb5c60fd4ab
      cited_regions:
      - rows
    observed_at: '2026-09-30'
  - benchmark_id: arena_sc_non_english
    model_id_as_evaluated: gpt-5.4-high
    score: 1468.48
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-30'
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
      snapshot_ref: sha256:52e386a612514d210b1d77719363e4ca268905f06901681ab924fac1d9520304
      cited_regions:
      - rows
    observed_at: '2026-09-30'
  - benchmark_id: arena_sc_medicine
    model_id_as_evaluated: gpt-5.4-high
    score: 1475.97
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-30'
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
      snapshot_ref: sha256:544b6524228d2e78462111b28f6dc4d5ae76d82f8ba52fd6040b0639e1f4856c
      cited_regions:
      - rows
    observed_at: '2026-09-30'
  - benchmark_id: arena_sc_legal
    model_id_as_evaluated: gpt-5.4-high
    score: 1490.58
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-30'
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
      snapshot_ref: sha256:07e3a236f9ee5e0cecac83995952d8e94413e872035c5ccae1efa23137a236ed
      cited_regions:
      - rows
    observed_at: '2026-09-30'
  - benchmark_id: arena_sc_business
    model_id_as_evaluated: gpt-5.4-high
    score: 1483.87
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-30'
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
      snapshot_ref: sha256:d1da5448d5afc01a34ae83fe1a795ef9a79a434bfe906fe2426ce82a67b36755
      cited_regions:
      - rows
    observed_at: '2026-09-30'
  - benchmark_id: arena_sc_science
    model_id_as_evaluated: gpt-5.4-high
    score: 1487.64
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-30'
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
      snapshot_ref: sha256:1017485e0b9dcfcf7d1a4dfeeed89d314f2f74f8131a3f8e05d6b833360bea76
      cited_regions:
      - rows
    observed_at: '2026-09-30'
  - benchmark_id: arena_sc_writing
    model_id_as_evaluated: gpt-5.4-high
    score: 1465.32
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-30'
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
      snapshot_ref: sha256:60b89142370aecd9137ff982bd144e8628dc8abadd10f41b90d334d34878bae0
      cited_regions:
      - rows
    observed_at: '2026-09-30'
  - benchmark_id: arena_sc_vision
    model_id_as_evaluated: gpt-5.4-high
    score: 1284.79
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-30'
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
      snapshot_ref: sha256:7cbeea3f83baaecb48aa1caac47e6a310b98842291087f21933928af691e694b
      cited_regions:
      - rows
    observed_at: '2026-09-30'
  - benchmark_id: arena_webdev
    model_id_as_evaluated: gpt-5.4
    score: 1392.0
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-23'
    date_type: published
    verified_at: '2026-09-30'
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
      snapshot_ref: sha256:31b3d323e3968c31c3238ed5782c805c2ae4be8758520c2e6837e2f3cb7633cb
      cited_regions:
      - rows
    observed_at: '2026-09-30'
  - benchmark_id: gpqa_diamond
    model_id_as_evaluated: gpt-5.4-2026-03-05_xhigh
    score: 93.3
    unit: percent
    source_url: https://epoch.ai/benchmarks/gpqa-diamond
    source_kind: independent_evaluator
    evidence_date: '2026-03-06'
    date_type: evaluated
    verified_at: '2026-09-30'
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
      snapshot_ref: sha256:dda8f2d4af6df0de8c7a4490325bf0c217d3dc92c5d55d04d3f62d4d2ab529a2
      cited_regions:
      - rows
    observed_at: '2026-09-30'
  - benchmark_id: frontiermath_tiers_1_3_v2
    model_id_as_evaluated: gpt-5.4-2026-03-05_xhigh
    score: 78.6
    unit: percent
    source_url: https://epoch.ai/frontiermath
    source_kind: independent_evaluator
    evidence_date: '2026-06-11'
    date_type: evaluated
    verified_at: '2026-09-30'
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
      snapshot_ref: sha256:37e80df4aa6aaec8c5ecd855ad6acf066d090004587859f657853c31991b0046
      cited_regions:
      - rows
    observed_at: '2026-09-30'
  - benchmark_id: simpleqa_verified
    model_id_as_evaluated: gpt-5.4-2026-03-05_xhigh
    score: 45.1
    unit: percent
    source_url: https://epoch.ai/benchmarks/simpleqa-verified
    source_kind: independent_evaluator
    evidence_date: '2026-08-27'
    date_type: evaluated
    verified_at: '2026-09-30'
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
      snapshot_ref: sha256:b73919dc0a37684a121e15559fdf4b73ef909848db133faa8ab2ce0cc4ddccae
      cited_regions:
      - rows
    observed_at: '2026-09-30'
  - benchmark_id: swe_bench_verified
    model_id_as_evaluated: gpt-5.4-2026-03-05_high
    score: 76.86
    unit: percent
    source_url: https://epoch.ai/benchmarks/swe-bench-verified
    source_kind: independent_evaluator
    evidence_date: '2026-03-06'
    date_type: evaluated
    verified_at: '2026-09-30'
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
      snapshot_ref: sha256:ed1a16e9654e811735e5fd8ad2d3342b57cff954a552e663f601990b90f9febc
      cited_regions:
      - rows
    observed_at: '2026-09-30'
  - benchmark_id: vending_bench_2
    model_id_as_evaluated: GPT-5.4
    score: 6144.18
    unit: USD
    source_url: https://andonlabs.com/evals/vending-bench-2
    source_kind: benchmark_author
    evidence_date: '2026-09-30'
    date_type: evaluated
    verified_at: '2026-09-30'
    benchmark_version: Vending-Bench 2, mean final balance over 5 runs
    configuration: Board row as copied in Epoch AI's benchmark data (vending_bench_2_external.csv,
      https://epoch.ai/data/benchmark_data.zip), read 2026-09-24. Effort unknown; the highest-effort
      row for the model (MODEL-123 max-effort rule).
    limitations: A live board's standing, dated by the day ModelSpec read Epoch AI's copy; the
      copy carries no per-row date. Epoch AI data, CC BY 4.0.
    id: openai/gpt-5-4#vending_bench_2#a03cdacdd841
    measured_by: benchmark_author
    effort: null
    harness: null
    sources:
    - source_id: model-160-vending-bench-2
      snapshot_ref: sha256:56dc9c006a5dd8343157e3122937b85758f2d208dec87e0c61a3eab1c750efbf
      cited_regions:
      - rows
    observed_at: '2026-09-30'
  - benchmark_id: deepswe_v1_1
    model_id_as_evaluated: gpt-5-4 (xhigh)
    score: 51.77
    unit: percent
    source_url: https://deepswe.datacurve.ai/
    source_kind: benchmark_author
    evidence_date: '2026-09-30'
    date_type: evaluated
    verified_at: '2026-09-30'
    benchmark_version: DeepSWE v1.1, pass@1, mini-swe-agent
    configuration: Board row as copied in Epoch AI's benchmark data (deepswe_external.csv, https://epoch.ai/data/benchmark_data.zip),
      read 2026-09-24. Effort xhigh; the highest-effort row for the model (MODEL-123 max-effort
      rule). Harness mini-swe-agent.
    limitations: A live board's standing, dated by the day ModelSpec read Epoch AI's copy; the
      copy carries no per-row date. Epoch AI data, CC BY 4.0.
    id: openai/gpt-5-4#deepswe_v1_1#ba042cf82206
    measured_by: benchmark_author
    effort: xhigh
    harness: unregistered
    sources:
    - source_id: model-160-deepswe-v1-1
      snapshot_ref: sha256:893865e2bda8e1a02a8e7115c6e02a8f8c843dd0763b8fbb1db3af6c017860f9
      cited_regions:
      - rows
    observed_at: '2026-09-30'
  - benchmark_id: hle
    model_id_as_evaluated: gpt-5.4-2026-03-05 (xhigh thinking)
    score: 36.24
    unit: percent
    source_url: https://labs.scale.com/leaderboard/humanitys_last_exam
    source_kind: independent_evaluator
    evidence_date: '2026-09-30'
    date_type: evaluated
    verified_at: '2026-09-30'
    benchmark_version: Humanity's Last Exam, Scale Labs leaderboard
    configuration: Scale Labs leaderboard entry read 2026-09-24; entry created 2026-03-10T21:09:26.000Z;
      effort xhigh; ±1.88 (95% CI).
    limitations: 'Potential contamination warning: This model was evaluated after the public
      release of HLE, allowing model builder access to the prompts and solutions.'
    id: openai/gpt-5-4#hle#6861aaf569f4
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-143-evidence-scale-hle-json
      snapshot_ref: sha256:635054cdf6208f34897c7f3c9d9e771135fffd781a8b2afa4b1ddb899ddd2bac
      cited_regions:
      - rows
    observed_at: '2026-09-30'
  - benchmark_id: swe_bench_pro
    model_id_as_evaluated: gpt-5.4 (xHigh)*
    score: 59.1
    unit: percent
    source_url: https://labs.scale.com/leaderboard/swe_bench_pro_public
    source_kind: independent_evaluator
    evidence_date: '2026-04-08'
    date_type: evaluated
    verified_at: '2026-09-30'
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
      snapshot_ref: sha256:711c55aa9c54fb56cd3c012095af53a1a1b5daffed5a71ddcd46e5eb090e7b6a
      cited_regions:
      - rows
    observed_at: '2026-09-30'
  - benchmark_id: aime_2026
    model_id_as_evaluated: GPT-5.4 (xhigh)
    score: 99.17
    unit: percent
    source_url: https://matharena.ai/competition_tables/aime--aime_2026
    source_kind: independent_evaluator
    evidence_date: '2026-09-30'
    date_type: evaluated
    verified_at: '2026-09-30'
    benchmark_version: AIME 2026, MathArena final-answer table
    configuration: MathArena competition table read 2026-09-26; the table states no run
      date, so the reading is dated by the observation. Effort xhigh; highest-effort row
      for the model. MathArena lists final-answer competitions as deprecated.
    limitations: 'MathArena marks this row: model was released after competition release, so
      contamination is possible.'
    id: openai/gpt-5-4#aime_2026#693a7d5f91d1
    measured_by: independent_evaluator
    effort: xhigh
    harness: null
    sources:
    - source_id: model-160-matharena-aime-2026
      snapshot_ref: sha256:25c764c1cd0b46c303d73e75eef12617a5aaddae7301955b2d5438a66a53924c
      cited_regions:
      - rows
    quality_flags:
    - deprecated
    - contamination_warning
    observed_at: '2026-09-30'
  - benchmark_id: tau3_banking
    model_id_as_evaluated: GPT-5.4 (xhigh)
    score: 39.43
    unit: percent
    source_url: https://sierra-tau-bench-public.s3.us-west-2.amazonaws.com/submissions/gpt-5-4_sierra_2026-03-25/submission.json
    source_kind: benchmark_author
    evidence_date: '2026-05-06'
    date_type: evaluated
    verified_at: '2026-09-30'
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
      snapshot_ref: sha256:df1fddd827d17e0698c933fdc666cc1cfd146385111fcfe76170e5c9d482be44
      cited_regions:
      - rows
    observed_at: '2026-09-30'
  - benchmark_id: arena_sc_english
    model_id_as_evaluated: gpt-5.4-high
    score: 1477.88
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-30'
    verified_at: '2026-09-30'
    benchmark_version: text_style_control / english, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1477.88 [1472.84,
      1482.91], 27508 votes, rank 37. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:1e2fcc24a5c8cdcd90c665aaa64b557f473180d9ce1725066717e04bfd10e5f1
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
    observed_at: '2026-09-30'
    verified_at: '2026-09-30'
    benchmark_version: text_style_control / chinese, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1504.78 [1493.87,
      1515.69], 3462 votes, rank 45. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:449b90746065449e59f0dd2bbdfcb8ef55aa5fe42c1b6beb8c930eb79a68224d
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
    observed_at: '2026-09-30'
    verified_at: '2026-09-30'
    benchmark_version: text_style_control / japanese, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1481.79 [1456.28,
      1507.30], 643 votes, rank 14. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:7839399ba846da94c65849c08837839d515c8b37ae6314453bedf1c962846be2
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
    observed_at: '2026-09-30'
    verified_at: '2026-09-30'
    benchmark_version: text_style_control / korean, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1437.30 [1417.20,
      1457.41], 1076 votes, rank 27. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:8a792645624d2854a8bb09bcb4bbfee6219a8e973f03fb84a4e42716cb635ae8
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
    observed_at: '2026-09-30'
    verified_at: '2026-09-30'
    benchmark_version: text_style_control / russian, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1489.95 [1481.73,
      1498.17], 6509 votes, rank 20. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:5364bedcc9fe8a9598db9c20aabead5411e9c132021ef8e55da2be02c0a36c67
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
    observed_at: '2026-09-30'
    verified_at: '2026-09-30'
    benchmark_version: text_style_control / spanish, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1457.52 [1442.96,
      1472.08], 2020 votes, rank 48. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:8d2651582e59832130a278d4b2efb6e4c03ae6e796506ad9930aec870da2547b
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
    observed_at: '2026-09-30'
    verified_at: '2026-09-30'
    benchmark_version: text_style_control / german, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1472.53 [1453.15,
      1491.92], 1050 votes, rank 34. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:5b6244cf0e66d4e7a6c2239bd4aedb255de731f67f134c7be235df3f2266be4b
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
    observed_at: '2026-09-30'
    verified_at: '2026-09-30'
    benchmark_version: text_style_control / french, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1501.75 [1487.05,
      1516.45], 2286 votes, rank 22. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:4425fd6448ec82f9820e7f3c151d3e136d0ec46a97a44a53afbe50c9c35efb7a
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
    observed_at: '2026-09-30'
    verified_at: '2026-09-30'
    benchmark_version: text_style_control / polish, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1481.37 [1464.28,
      1498.45], 1295 votes, rank 23. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:97e2e1ee9652b13516342dcba0cf4472957d6b7e4a17134aafdf774b2d57516d
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
    observed_at: '2026-09-30'
    verified_at: '2026-09-30'
    benchmark_version: vision_style_control / ocr, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1299.64 [1293.33,
      1305.95], 18040 votes, rank 15. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-vision-style-control
      snapshot_ref: sha256:2dce15e32ba82760a14eb6d794d7a44e23c6445c5521dcc4b9663521e402f9d6
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
    observed_at: '2026-09-30'
    verified_at: '2026-09-30'
    benchmark_version: vision_style_control / diagram, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1319.27 [1310.29,
      1328.26], 6803 votes, rank 10. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-vision-style-control
      snapshot_ref: sha256:b3b3df0cdc8c9065197b822d9005d334197cf72b9da69ab35a05b6bb1401d9bd
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
    observed_at: '2026-09-30'
    verified_at: '2026-09-30'
    benchmark_version: vision_style_control / homework, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1331.84 [1320.32,
      1343.35], 3264 votes, rank 7. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-vision-style-control
      snapshot_ref: sha256:c6cc8aff02e174d0d07d3b1062861395df1b9dcd3ea53fb5c3f7dfffc0de039f
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
    observed_at: '2026-09-30'
    verified_at: '2026-09-30'
    benchmark_version: document / overall, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1471.00 [1464.97,
      1477.04], 33331 votes, rank 14. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-document
      snapshot_ref: sha256:5647d463e779905a42ab0cc56675629608fc252462f6535402778fc965f013f5
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
    observed_at: '2026-09-30'
    verified_at: '2026-09-30'
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
      snapshot_ref: sha256:eea47e91c8bc87fe0b61f2a3c0e4eba132c33a7b65597a78092fce12744d989a
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
    observed_at: '2026-09-30'
    verified_at: '2026-09-30'
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
      snapshot_ref: sha256:dd31fbcb0b964ee4faa128a3bcac1f1ad740ec5fa6755b63a7cdd8654950bf11
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
    observed_at: '2026-09-30'
    verified_at: '2026-09-30'
    benchmark_version: text_style_control / industry_mathematical, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1499.48 [1488.32,
      1510.64], 3236 votes, rank 19. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:6061abfc8f62e0094fea0e87ea00b13d5f43d12e35990052572243771c51f1db
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
    observed_at: '2026-09-30'
    verified_at: '2026-09-30'
    benchmark_version: text_factuality / overall, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1485.01 [1482.01,
      1488.00], 60435 votes, rank 9. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-factuality
      snapshot_ref: sha256:6cd314acaa71574c46eb9bfadb9a78b786a28b13499126a045487d4aba292032
      cited_regions:
      - rows
    id: openai/gpt-5-4#arena_sc_factuality#76bcb29c51a0
  - benchmark_id: finance_benchmark_v2
    model_id_as_evaluated: openai/gpt-5.4
    score: 63.0137
    unit: percent
    source_url: https://finbenchmark.ai/
    source_kind: independent_evaluator
    evidence_date: '2026-06-15'
    date_type: evaluated
    observed_at: '2026-09-30'
    verified_at: '2026-09-30'
    benchmark_version: Finance Benchmark v2, harness 0.1.0
    configuration: 73 v2 tasks; three attempts per task; temperature zero.
    limitations: Passes at least once, so this value does not measure repeated-run consistency.
    measured_by: independent_evaluator
    effort: null
    harness: unregistered
    sources:
    - source_id: model-192-finance-benchmark-v2
      snapshot_ref: sha256:449a202e4bd36854996cde8fb995fa5af39d5a15aa6022bb8dce718ab7cbde02
      cited_regions:
      - rows
    id: openai/gpt-5-4#finance_benchmark_v2#b8e36b72ddba
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
- id: openai/gpt-5-4#model.fits_hardware
  subject:
    kind: model
    id: openai/gpt-5-4
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
      model_snapshot_ref: sha256:56c7e709958cf5eab6e96673a1c0f85e250345ff31d6165bbcb48609f38ac581
      hardware_registry_sha256: sha256:10baf5e1ce9e5a1e5b970f4fdc25d9f67db8c562c8c109157ae9722bf6357bff
      hardware_device_count: 64
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
card_updated: '2026-09-28'
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