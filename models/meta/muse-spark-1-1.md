---
model_id: meta/muse-spark-1-1
display_name: Muse Spark 1.1
provider: meta
provider_display: Meta
family: muse
version: muse-spark-1.1
release_date: '2026-07-09'
last_updated: '2026-07-09'
status: active
model_type: llm-reasoning
model_subtypes:
- vlm
tags:
- text-generation
pipeline_tag: text-generation
architecture:
  type: null
  total_parameters: null
  total_parameters_source: ''
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
  - video
  - audio
  - pdf
  output:
  - text
  text:
    max_input_tokens: null
    max_output_tokens: null
    context_window: 1048576
    streaming: true
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
    input_supported: true
    output_supported: false
    max_input_duration_sec: null
    max_output_duration_sec: null
    max_resolution: ''
    max_fps: null
    audio_sync: false
    temporal_reasoning: false
  document:
    pdf_native: true
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
    parallel_tool_calls: true
    tool_selection_accuracy: null
    multi_turn_tool_use: false
    tool_error_recovery: false
    computer_use: true
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
  input: 1.25
  output: 4.25
  reasoning: null
  cache_read: 0.15
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
  note: USD per 1M tokens, Standard tier model id muse-spark-1.1. Read 2026-09-24
    from https://ai.developer.meta.com/docs/pricing-rate-limits.md. Contributor model
    ids, where Meta publishes them, are a different offering and are not these prices.
availability:
  primary_provider:
    name: Meta Model API
    platform_url: https://ai.developer.meta.com/docs/models.md
    api_endpoint: https://api.meta.ai/v1
    npm_package: ''
    env_vars: []
    model_id_on_platform: muse-spark-1.1
    rate_limit_rpm: 3000
    rate_limit_tpm: 4000000
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
  - benchmark_id: arena_elo_overall
    model_id_as_evaluated: muse-spark-1.1
    score: 1480.17
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text/latest, overall
    configuration: LMArena leaderboard dataset, CC BY 4.0, category overall, leaderboard_publish_date
      2026-09-13, read 2026-09-24. Rank 15, 27615 votes, interval [1475.35, 1485.0].
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC
      BY 4.0.
    id: meta/muse-spark-1-1#arena_elo_overall#efdcadcfd60c
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text
      snapshot_ref: sha256:5b1d1f5db8552e7e438f8758c2c0c2c938ba740796f0e4cee157bbde173e780d
      cited_regions:
      - rows
  - benchmark_id: arena_elo_vision
    model_id_as_evaluated: muse-spark-1.1
    score: 1294.16
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: vision/latest, overall
    configuration: LMArena leaderboard dataset, CC BY 4.0, category overall, leaderboard_publish_date
      2026-09-13, read 2026-09-24. Rank 21, 8447 votes, interval [1286.17, 1302.16].
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC
      BY 4.0.
    id: meta/muse-spark-1-1#arena_elo_vision#c2537b6cc314
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-vision
      snapshot_ref: sha256:12075d19b12efd468a1bd4314619e07e2f44409bd500c3c2cb0ca3d2b813fa7b
      cited_regions:
      - rows
  - benchmark_id: arena_webdev
    model_id_as_evaluated: muse-spark-1.1
    score: 1542.36
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-23'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: webdev/latest, overall
    configuration: LMArena leaderboard dataset, CC BY 4.0, category overall, leaderboard_publish_date
      2026-09-23, read 2026-09-24. Rank 32, 7521 votes, interval [1534.53, 1550.19].
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC
      BY 4.0.
    id: meta/muse-spark-1-1#arena_webdev#10ec5db7edcf
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-143-evidence-arena-webdev-json
      snapshot_ref: sha256:8c88f6e665fc8a5667d5b00b1a3ef24d70773f37f9f2fe917623c8c29895c5cf
      cited_regions:
      - rows
  - benchmark_id: swe_bench_pro
    model_id_as_evaluated: Muse Spark 1.1*
    score: 61.5
    unit: percent
    source_url: https://labs.scale.com/leaderboard/swe_bench_pro
    source_kind: independent_evaluator
    evidence_date: '2026-07-09'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: SWE-Bench Pro, public dataset
    configuration: Public-dataset row on the Scale Labs page, read 2026-09-24. Resolve
      rate 61.5, confidence interval upper 3.1, rank 1, createdAt 2026-07-09. The
      asterisk means mini-swe-agent, as the page states.
    limitations: Public split only. The same page lists a private-split row at 51.5,
      which is not this number.
    id: meta/muse-spark-1-1#swe_bench_pro#6857d2ed9fb3
    measured_by: independent_evaluator
    effort: null
    harness: unregistered
    sources:
    - source_id: model-160-scale-swe-bench-pro-public
      snapshot_ref: sha256:b0df5d5cbc6fd2c3925e740d0379f6570e00d58b98ca576c8141e6af67dc0666
      cited_regions:
      - rows
  benchmark_source: ''
  benchmark_as_of: ''
  benchmark_notes: ''
deployment:
  api_only: true
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
    data_retention_policy: 'Standard tier: prompts and completions are not used to
      train Meta models. Read 2026-09-24 from https://ai.developer.meta.com/docs/pricing-rate-limits.md.'
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
  models_dev_url: ''
  provider_docs_url: https://ai.developer.meta.com/docs/models.md
  huggingface_url: ''
  arxiv_url: ''
  paper_url: ''
  github_url: ''
  ollama_url: ''
  artificial_analysis_url: ''
  arena_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  last_scraped_models_dev: ''
  last_scraped_huggingface: ''
  last_scraped_benchmarks: '2026-09-24'
  last_scraped_pricing: '2026-09-24'
facts:
- facet: model.class
  value: text-generator
  state: known
  sources:
  - source_id: model-143-meta-muse-spark-1-1
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
  - video
  - audio
  - document
  state: known
  sources:
  - source_id: model-143-meta-muse-spark-1-1
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
  - source_id: model-143-meta-muse-spark-1-1
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
  value: 1048576
  state: known
  sources:
  - source_id: model-143-meta-muse-spark-1-1
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
  - source_id: model-143-meta-muse-spark-1-1
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
  - model-143-meta-muse-spark-1-1
  - model-143-meta-release-index
  - model-143-meta-model-api
  - model-143-meta-company
  - model-143-meta-sec
- facet: model.weights_openness
  value: closed_weights
  state: known
  sources:
  - source_id: model-143-meta-muse-spark-1-1
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
  - source_id: model-143-meta-muse-spark-1-1
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
  - model-143-meta-muse-spark-1-1
  - model-143-meta-release-index
  - model-143-meta-model-api
  - model-143-meta-company
  - model-143-meta-sec
- facet: licence.user_cap
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-meta-muse-spark-1-1
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
  - model-143-meta-muse-spark-1-1
  - model-143-meta-release-index
  - model-143-meta-model-api
  - model-143-meta-company
  - model-143-meta-sec
- facet: licence.output_training
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-meta-muse-spark-1-1
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
  - model-143-meta-muse-spark-1-1
  - model-143-meta-release-index
  - model-143-meta-model-api
  - model-143-meta-company
  - model-143-meta-sec
- facet: licence.fine_tuning
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-meta-muse-spark-1-1
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
  - model-143-meta-muse-spark-1-1
  - model-143-meta-release-index
  - model-143-meta-model-api
  - model-143-meta-company
  - model-143-meta-sec
- facet: origin.lab_jurisdiction
  value:
  - US
  state: known
  sources:
  - source_id: model-143-meta-muse-spark-1-1
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
  - source_id: model-143-meta-muse-spark-1-1
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
  - model-143-meta-muse-spark-1-1
  - model-143-meta-release-index
  - model-143-meta-model-api
  - model-143-meta-company
  - model-143-meta-sec
- facet: origin.weights_hosting
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-meta-muse-spark-1-1
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
  - model-143-meta-muse-spark-1-1
  - model-143-meta-release-index
  - model-143-meta-model-api
  - model-143-meta-company
  - model-143-meta-sec
- facet: model.release_date
  value: '2026-07-09'
  state: known
  sources:
  - source_id: model-143-meta-muse-spark-1-1
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
  - source_id: model-143-meta-muse-spark-1-1
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
  - source_id: model-143-meta-muse-spark-1-1
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
  - source_id: model-143-meta-muse-spark-1-1
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
  - source_id: model-143-meta-muse-spark-1-1
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
  - source_id: model-143-meta-muse-spark-1-1
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
  - model-143-meta-muse-spark-1-1
  - model-143-meta-release-index
  - model-143-meta-model-api
  - model-143-meta-company
  - model-143-meta-sec
- facet: feature.streaming
  value: true
  state: known
  sources:
  - source_id: model-143-meta-muse-spark-1-1
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
card_author: Grok 4.7
card_created: '2026-09-24'
card_updated: '2026-09-24'
---

# Muse Spark 1.1

Muse Spark 1.1 is a multimodal reasoning model from Meta Superintelligence Labs, served as `muse-spark-1.1` on Meta Model API.
The models page, read 2026-09-24 at https://ai.developer.meta.com/docs/models.md, lists text, image, video, audio and PDF input, text output, and a context window of 1,048,576 tokens.
Meta's announcement of this version is dated 9 July 2026: https://research.meta.ai/blog/introducing-muse-spark-meta-model-api.
That post calls it an upgrade of Muse Spark for tool use, computer use, coding and multimodal understanding, and says the model can manage a context window of 1 million tokens.

`meta/muse-spark` remains the April 2026 model.
The Arena text parquet (publish date 2026-09-13) lists that model's row, `muse-spark`, and this version's row, `muse-spark-1.1`.
The SWE-bench Pro public table likewise lists "Muse Spark" and "Muse Spark 1.1" as two rows.

Standard-tier price, read 2026-09-24 from https://ai.developer.meta.com/docs/pricing-rate-limits.md: $1.25 per million input tokens, $0.15 cached input, $4.25 output.
The same page says prompts and completions on the Standard tier are not used to train Meta models, and lists 3,000 requests per minute and 4,000,000 tokens per minute.
Meta does not publish a contributor model id for 1.1.
The pages read for this version do not state a parameter count, a maximum output length, or a downloadable-weights licence.
Those fields stay empty.

The overview at https://ai.developer.meta.com/docs/overview.md, read the same day, says Muse Spark on this API supports parallel tool calls and streamed tool-call arguments.
Base URL on that page: https://api.meta.ai/v1.

## Evidence

Arena scores are the overall rows of https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset (CC BY 4.0), read 2026-09-24.
The SWE-bench Pro public resolve rate is from https://labs.scale.com/leaderboard/swe_bench_pro, read the same day.
The row name ends in an asterisk. The page says an asterisk means the run used mini-swe-agent.
The public entry's createdAt is 2026-07-09. The page does not give a separate run date.