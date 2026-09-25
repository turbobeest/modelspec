---
model_id: jcorners/ingot-8b-r3
display_name: Ingot 8B R3
provider: jcorners
provider_display: Voxell
family: ingot
version: ingot-8b-r3
release_date: '2026-05-23'
last_updated: ''
status: active
model_type: embedding-text
model_subtypes: []
tags:
- mteb
- text-embedding
pipeline_tag: feature-extraction
architecture:
  type: MoE
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
  embedding_dimensions: 4096
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
  base_model: Qwen/Qwen3-Embedding-8B
  base_model_relation: finetune
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
  license_url: https://voxell.ai/forge
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
  origin_country: ''
  origin_org_type: null
modalities:
  input:
  - text
  output:
  - embeddings
  text:
    max_input_tokens: null
    max_output_tokens: null
    context_window: null
    streaming: null
    fill_in_middle: null
    json_mode: null
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
    supported: true
    dimensions: 4096
    dimensions_configurable: false
    dimension_options: []
    max_input_tokens: null
    similarity_metric: ''
    normalized: null
    batch_size_max: null
    instruction_aware: true
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
    chain_of_thought: false
    self_correction: false
    spatial: false
    temporal: false
    causal: false
    think_budget_control: false
  tool_use:
    overall: null
    function_calling: false
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
    name: Voxell
    platform_url: https://voxell.ai/engineering/ingot_poured/
    api_endpoint: https://api-mteb.voxell.ai
    npm_package: ''
    env_vars: []
    model_id_on_platform: ''
    rate_limit_rpm: 200
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
    model_id: JCorners/Ingot-8B-R3
    url: https://huggingface.co/JCorners/Ingot-8B-R3
    fine_tuning: false
    gated: true
    regions: []
    notes: 'Hub API read 2026-09-24: gated auto, and the file list has no weight files.'
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
  - benchmark_id: mteb_eng_v2
    model_id_as_evaluated: jcorners/ingot-8b-r3
    score: 75.98
    unit: percent
    source_url: https://mteb-leaderboard-backend.hf.space/v1/benchmarks/MTEB(eng,%20v2)/scores
    source_kind: benchmark_author
    evidence_date: '2026-09-24'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: MTEB(eng, v2), mean over tasks
    configuration: MTEB leaderboard backend JSON, benchmarkName MTEB(eng, v2), read
      2026-09-24. Score is meanTask times 100. The JSON has no per-row run date, so
      this date is the day the board was read.
    limitations: Mean over the benchmark's tasks. Not a single-task score.
    id: jcorners/ingot-8b-r3#mteb_eng_v2#4bebfdf26d62
    measured_by: benchmark_author
    effort: null
    harness: null
    sources:
    - source_id: model-143-evidence-mteb-eng-v2-json
      snapshot_ref: sha256:ac7d438631091bcea50b96c0f2e3e83741ad7903e14a2e051bae8d7e7260c583
      cited_regions:
      - rows
  - benchmark_id: mteb_v2_retrieval
    model_id_as_evaluated: jcorners/ingot-8b-r3
    score: 70.0
    unit: percent
    source_url: https://mteb-leaderboard-backend.hf.space/v1/benchmarks/MTEB(eng,%20v2)/scores
    source_kind: benchmark_author
    evidence_date: '2026-09-24'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: MTEB(eng, v2), Retrieval task type
    configuration: Same JSON read, field scoresByTaskType.Retrieval times 100. Dated
      by the day the board was read.
    limitations: ''
    id: jcorners/ingot-8b-r3#mteb_v2_retrieval#5e3354975702
    measured_by: benchmark_author
    effort: null
    harness: null
    sources:
    - source_id: model-143-evidence-mteb-eng-v2-json
      snapshot_ref: sha256:ac7d438631091bcea50b96c0f2e3e83741ad7903e14a2e051bae8d7e7260c583
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
  models_dev_url: ''
  provider_docs_url: https://voxell.ai/engineering/ingot_poured/
  huggingface_url: https://huggingface.co/JCorners/Ingot-8B-R3
  arxiv_url: ''
  paper_url: ''
  github_url: ''
  ollama_url: ''
  artificial_analysis_url: ''
  arena_url: ''
  last_scraped_models_dev: ''
  last_scraped_huggingface: '2026-09-24'
  last_scraped_benchmarks: '2026-09-24'
  last_scraped_pricing: ''
facts:
- facet: model.class
  value: vectoriser
  state: known
  sources:
  - source_id: model-143-jcorners-ingot-8b-r3
    snapshot_ref: sha256:f1c44b77bb951ce443758b247295b119a287545dca9e74e20fb155246682f72f
    cited_regions:
    - model-spec
- facet: model.input_modalities
  value:
  - text
  state: known
  sources:
  - source_id: model-143-jcorners-ingot-8b-r3
    snapshot_ref: sha256:f1c44b77bb951ce443758b247295b119a287545dca9e74e20fb155246682f72f
    cited_regions:
    - model-spec
- facet: model.output_modalities
  value:
  - embedding
  state: known
  sources:
  - source_id: model-143-jcorners-ingot-8b-r3
    snapshot_ref: sha256:f1c44b77bb951ce443758b247295b119a287545dca9e74e20fb155246682f72f
    cited_regions:
    - model-spec
- facet: model.context_window
  value: 32768
  state: known
  sources:
  - source_id: model-143-jcorners-ingot-8b-r3
    snapshot_ref: sha256:f1c44b77bb951ce443758b247295b119a287545dca9e74e20fb155246682f72f
    cited_regions:
    - model-spec
- facet: model.max_output_tokens
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-jcorners-ingot-8b-r3
    snapshot_ref: sha256:f1c44b77bb951ce443758b247295b119a287545dca9e74e20fb155246682f72f
    cited_regions:
    - model-spec
  - source_id: model-143-hf-metadata-jcorners-ingot-8b-r3
    snapshot_ref: sha256:4b930b3178b8e921b02d884b90f9a0f7e0d0ec56a55da7a891ab9cce85fde611
    cited_regions:
    - audit
  checked_sources:
  - model-143-jcorners-ingot-8b-r3
  - model-143-hf-metadata-jcorners-ingot-8b-r3
- facet: model.weights_openness
  value: closed_weights
  state: known
  sources:
  - source_id: model-143-jcorners-ingot-8b-r3
    snapshot_ref: sha256:f1c44b77bb951ce443758b247295b119a287545dca9e74e20fb155246682f72f
    cited_regions:
    - model-spec
  - source_id: model-143-hf-metadata-jcorners-ingot-8b-r3
    snapshot_ref: sha256:4b930b3178b8e921b02d884b90f9a0f7e0d0ec56a55da7a891ab9cce85fde611
    cited_regions:
    - audit
- facet: licence.commercial_use
  value: permitted_with_conditions
  state: known
  sources:
  - source_id: model-143-jcorners-ingot-8b-r3
    snapshot_ref: sha256:f1c44b77bb951ce443758b247295b119a287545dca9e74e20fb155246682f72f
    cited_regions:
    - model-spec
- facet: licence.user_cap
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-jcorners-ingot-8b-r3
    snapshot_ref: sha256:f1c44b77bb951ce443758b247295b119a287545dca9e74e20fb155246682f72f
    cited_regions:
    - model-spec
  - source_id: model-143-hf-metadata-jcorners-ingot-8b-r3
    snapshot_ref: sha256:4b930b3178b8e921b02d884b90f9a0f7e0d0ec56a55da7a891ab9cce85fde611
    cited_regions:
    - audit
  checked_sources:
  - model-143-jcorners-ingot-8b-r3
  - model-143-hf-metadata-jcorners-ingot-8b-r3
- facet: licence.output_training
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-jcorners-ingot-8b-r3
    snapshot_ref: sha256:f1c44b77bb951ce443758b247295b119a287545dca9e74e20fb155246682f72f
    cited_regions:
    - model-spec
  - source_id: model-143-hf-metadata-jcorners-ingot-8b-r3
    snapshot_ref: sha256:4b930b3178b8e921b02d884b90f9a0f7e0d0ec56a55da7a891ab9cce85fde611
    cited_regions:
    - audit
  checked_sources:
  - model-143-jcorners-ingot-8b-r3
  - model-143-hf-metadata-jcorners-ingot-8b-r3
- facet: licence.fine_tuning
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-jcorners-ingot-8b-r3
    snapshot_ref: sha256:f1c44b77bb951ce443758b247295b119a287545dca9e74e20fb155246682f72f
    cited_regions:
    - model-spec
  - source_id: model-143-hf-metadata-jcorners-ingot-8b-r3
    snapshot_ref: sha256:4b930b3178b8e921b02d884b90f9a0f7e0d0ec56a55da7a891ab9cce85fde611
    cited_regions:
    - audit
  checked_sources:
  - model-143-jcorners-ingot-8b-r3
  - model-143-hf-metadata-jcorners-ingot-8b-r3
- facet: origin.lab_jurisdiction
  value:
  - US
  state: known
  sources:
  - source_id: model-143-jcorners-ingot-8b-r3
    snapshot_ref: sha256:f1c44b77bb951ce443758b247295b119a287545dca9e74e20fb155246682f72f
    cited_regions:
    - model-spec
- facet: origin.base_lineage
  value:
  - CN
  state: known
  sources:
  - source_id: model-143-jcorners-ingot-8b-r3
    snapshot_ref: sha256:f1c44b77bb951ce443758b247295b119a287545dca9e74e20fb155246682f72f
    cited_regions:
    - model-spec
- facet: origin.weights_hosting
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-jcorners-ingot-8b-r3
    snapshot_ref: sha256:f1c44b77bb951ce443758b247295b119a287545dca9e74e20fb155246682f72f
    cited_regions:
    - model-spec
  - source_id: model-143-hf-metadata-jcorners-ingot-8b-r3
    snapshot_ref: sha256:4b930b3178b8e921b02d884b90f9a0f7e0d0ec56a55da7a891ab9cce85fde611
    cited_regions:
    - audit
  checked_sources:
  - model-143-jcorners-ingot-8b-r3
  - model-143-hf-metadata-jcorners-ingot-8b-r3
- facet: model.release_date
  value: '2026-05-23'
  state: known
  sources:
  - source_id: model-143-jcorners-ingot-8b-r3
    snapshot_ref: sha256:f1c44b77bb951ce443758b247295b119a287545dca9e74e20fb155246682f72f
    cited_regions:
    - model-spec
  - source_id: model-143-hf-metadata-jcorners-ingot-8b-r3
    snapshot_ref: sha256:4b930b3178b8e921b02d884b90f9a0f7e0d0ec56a55da7a891ab9cce85fde611
    cited_regions:
    - audit
- facet: model.lifecycle
  value: active
  state: known
  sources:
  - source_id: model-143-jcorners-ingot-8b-r3
    snapshot_ref: sha256:f1c44b77bb951ce443758b247295b119a287545dca9e74e20fb155246682f72f
    cited_regions:
    - model-spec
  - source_id: model-143-hf-metadata-jcorners-ingot-8b-r3
    snapshot_ref: sha256:4b930b3178b8e921b02d884b90f9a0f7e0d0ec56a55da7a891ab9cce85fde611
    cited_regions:
    - audit
- facet: feature.tool_calling
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-jcorners-ingot-8b-r3
    snapshot_ref: sha256:f1c44b77bb951ce443758b247295b119a287545dca9e74e20fb155246682f72f
    cited_regions:
    - model-spec
  - source_id: model-143-hf-metadata-jcorners-ingot-8b-r3
    snapshot_ref: sha256:4b930b3178b8e921b02d884b90f9a0f7e0d0ec56a55da7a891ab9cce85fde611
    cited_regions:
    - audit
  checked_sources:
  - model-143-jcorners-ingot-8b-r3
  - model-143-hf-metadata-jcorners-ingot-8b-r3
- facet: feature.structured_output
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-jcorners-ingot-8b-r3
    snapshot_ref: sha256:f1c44b77bb951ce443758b247295b119a287545dca9e74e20fb155246682f72f
    cited_regions:
    - model-spec
  - source_id: model-143-hf-metadata-jcorners-ingot-8b-r3
    snapshot_ref: sha256:4b930b3178b8e921b02d884b90f9a0f7e0d0ec56a55da7a891ab9cce85fde611
    cited_regions:
    - audit
  checked_sources:
  - model-143-jcorners-ingot-8b-r3
  - model-143-hf-metadata-jcorners-ingot-8b-r3
- facet: feature.effort_controls
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-jcorners-ingot-8b-r3
    snapshot_ref: sha256:f1c44b77bb951ce443758b247295b119a287545dca9e74e20fb155246682f72f
    cited_regions:
    - model-spec
  - source_id: model-143-hf-metadata-jcorners-ingot-8b-r3
    snapshot_ref: sha256:4b930b3178b8e921b02d884b90f9a0f7e0d0ec56a55da7a891ab9cce85fde611
    cited_regions:
    - audit
  checked_sources:
  - model-143-jcorners-ingot-8b-r3
  - model-143-hf-metadata-jcorners-ingot-8b-r3
- facet: feature.batch
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-jcorners-ingot-8b-r3
    snapshot_ref: sha256:f1c44b77bb951ce443758b247295b119a287545dca9e74e20fb155246682f72f
    cited_regions:
    - model-spec
  - source_id: model-143-hf-metadata-jcorners-ingot-8b-r3
    snapshot_ref: sha256:4b930b3178b8e921b02d884b90f9a0f7e0d0ec56a55da7a891ab9cce85fde611
    cited_regions:
    - audit
  checked_sources:
  - model-143-jcorners-ingot-8b-r3
  - model-143-hf-metadata-jcorners-ingot-8b-r3
- facet: feature.streaming
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-jcorners-ingot-8b-r3
    snapshot_ref: sha256:f1c44b77bb951ce443758b247295b119a287545dca9e74e20fb155246682f72f
    cited_regions:
    - model-spec
  - source_id: model-143-hf-metadata-jcorners-ingot-8b-r3
    snapshot_ref: sha256:4b930b3178b8e921b02d884b90f9a0f7e0d0ec56a55da7a891ab9cce85fde611
    cited_regions:
    - audit
  checked_sources:
  - model-143-jcorners-ingot-8b-r3
  - model-143-hf-metadata-jcorners-ingot-8b-r3
card_schema_version: '3.0'
card_author: Grok 4.7
card_created: '2026-09-24'
card_updated: '2026-09-24'
---

# Ingot 8B R3

Ingot-8B-R3 is Voxell's text embedding model, submitted to MTEB(eng, v2) as a hosted API.
Jonathan Corners's note, read 2026-09-24 at https://voxell.ai/engineering/ingot_poured/, says it is built on Qwen/Qwen3-Embedding-8B and that the API returns 4096-dimensional float32 vectors.
The same page calls the added layer a routed mixture of experts, with specialists selected from the input.
It also says a task_name field selects the prompt used in the official MTEB run, and that the demo key is limited to 200 requests per minute.
The page is dated May 2026. The MTEB model record's releaseDate is 2026-05-23.

The Hub card at https://huggingface.co/JCorners/Ingot-8B-R3, read the same day through the Hub API, sets license_name proprietary and license_link https://voxell.ai/forge.
That forge page, read the same day, is a product page for a hosted embedding API. It is not a licence grant, so commercial use stays unspecified.
The Hub file list contains no weight files, and the MTEB model record sets openWeights false.
MTEB lists 7.567 billion total parameters and 6.946 billion active. Those are rounded billions, not an exact count, so the parameter fields stay empty.
MTEB also lists maxTokens 32768. The Voxell page does not state a context length, so the card leaves max input empty.

## Evidence

MTEB(eng, v2) mean and retrieval, from https://mteb-leaderboard-backend.hf.space/v1/benchmarks/MTEB(eng,%20v2)/scores, read 2026-09-24.
The Voxell page prints Mean(41) = 75.9795, the same mean the leaderboard returns. The card stores the leaderboard reading.