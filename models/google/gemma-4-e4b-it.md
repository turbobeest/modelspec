---
model_id: google/gemma-4-e4b-it
display_name: gemma 4 E4B it
provider: google
provider_display: Google DeepMind
family: gemma
version: ''
release_date: '2026-03-02'
last_updated: ''
status: active
model_type: llm-chat
model_subtypes: []
tags:
- any-to-any
pipeline_tag: any-to-any
architecture:
  type: null
  total_parameters: 7996156490
  active_parameters: null
  num_experts: null
  experts_per_token: null
  num_layers: 42
  hidden_size: 2560
  intermediate_size: 10240
  attention_type: null
  num_attention_heads: 8
  num_kv_heads: 2
  positional_encoding: null
  rope_theta: null
  vocab_size: 262144
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
  open_weights: true
  license_type: gemma
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
  output:
  - text
  text:
    max_input_tokens: null
    max_output_tokens: null
    context_window: 131072
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
    overall: tier-2
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
  input: 0.05
  output: 0.05
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
  note: Estimated inference cost on popular platforms ($/M tokens)
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
    model_id: google/gemma-4-E4B-it
    url: https://huggingface.co/google/gemma-4-E4B-it
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
  - benchmark_id: mmlu_pro
    model_id_as_evaluated: Gemma 4 E4B
    score: 69.4
    unit: percent
    source_url: https://ai.google.dev/gemma/docs/core/model_card_4
    source_kind: provider_self_report
    evidence_date: '2026-07-30'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: MMLU-Pro
    configuration: Google's Gemma 4 model card (last updated 2026-07-30), Benchmark Results table;
      the page states the results are for the instruction-tuned models.
    limitations: ''
    measured_by: provider_self_report
    effort: null
    harness: null
    sources:
    - source_id: model-233-google-gemma-4-model-card
      snapshot_ref: sha256:5793665e8eea120093150c2c6f87362e152c6e0db0fa26130beb59ccd2c07992
      cited_regions:
      - benchmark-results
    id: google/gemma-4-e4b-it#mmlu_pro#bfcaaa63af0b
  - benchmark_id: aime_2026
    model_id_as_evaluated: Gemma 4 E4B
    score: 42.5
    unit: percent
    source_url: https://ai.google.dev/gemma/docs/core/model_card_4
    source_kind: provider_self_report
    evidence_date: '2026-07-30'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: AIME 2026, no tools
    configuration: Google's Gemma 4 model card (last updated 2026-07-30), Benchmark Results table;
      the page states the results are for the instruction-tuned models.
    limitations: ''
    measured_by: provider_self_report
    effort: null
    harness: null
    sources:
    - source_id: model-233-google-gemma-4-model-card
      snapshot_ref: sha256:5793665e8eea120093150c2c6f87362e152c6e0db0fa26130beb59ccd2c07992
      cited_regions:
      - benchmark-results
    id: google/gemma-4-e4b-it#aime_2026#63c497d6b5ad
  - benchmark_id: gpqa_diamond
    model_id_as_evaluated: Gemma 4 E4B
    score: 58.6
    unit: percent
    source_url: https://ai.google.dev/gemma/docs/core/model_card_4
    source_kind: provider_self_report
    evidence_date: '2026-07-30'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: GPQA Diamond
    configuration: Google's Gemma 4 model card (last updated 2026-07-30), Benchmark Results table;
      the page states the results are for the instruction-tuned models.
    limitations: ''
    measured_by: provider_self_report
    effort: null
    harness: null
    sources:
    - source_id: model-233-google-gemma-4-model-card
      snapshot_ref: sha256:5793665e8eea120093150c2c6f87362e152c6e0db0fa26130beb59ccd2c07992
      cited_regions:
      - benchmark-results
    id: google/gemma-4-e4b-it#gpqa_diamond#c9d0357972df
  - benchmark_id: bbeh
    model_id_as_evaluated: Gemma 4 E4B
    score: 33.1
    unit: percent
    source_url: https://ai.google.dev/gemma/docs/core/model_card_4
    source_kind: provider_self_report
    evidence_date: '2026-07-30'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: BIG-Bench Extra Hard
    configuration: Google's Gemma 4 model card (last updated 2026-07-30), Benchmark Results table;
      the page states the results are for the instruction-tuned models.
    limitations: ''
    measured_by: provider_self_report
    effort: null
    harness: null
    sources:
    - source_id: model-233-google-gemma-4-model-card
      snapshot_ref: sha256:5793665e8eea120093150c2c6f87362e152c6e0db0fa26130beb59ccd2c07992
      cited_regions:
      - benchmark-results
    id: google/gemma-4-e4b-it#bbeh#b838953b703d
  - benchmark_id: mmmlu
    model_id_as_evaluated: Gemma 4 E4B
    score: 76.6
    unit: percent
    source_url: https://ai.google.dev/gemma/docs/core/model_card_4
    source_kind: provider_self_report
    evidence_date: '2026-07-30'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: MMMLU
    configuration: Google's Gemma 4 model card (last updated 2026-07-30), Benchmark Results table;
      the page states the results are for the instruction-tuned models.
    limitations: ''
    measured_by: provider_self_report
    effort: null
    harness: null
    sources:
    - source_id: model-233-google-gemma-4-model-card
      snapshot_ref: sha256:5793665e8eea120093150c2c6f87362e152c6e0db0fa26130beb59ccd2c07992
      cited_regions:
      - benchmark-results
    id: google/gemma-4-e4b-it#mmmlu#667509c9fea0
  - benchmark_id: deepmind_mrcr_v2
    model_id_as_evaluated: Gemma 4 E4B
    score: 25.4
    unit: percent
    source_url: https://ai.google.dev/gemma/docs/core/model_card_4
    source_kind: provider_self_report
    evidence_date: '2026-07-30'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: MRCR v2, 8 needles, up to 128K tokens, average
    configuration: Google's Gemma 4 model card (last updated 2026-07-30), Benchmark Results table;
      the page states the results are for the instruction-tuned models.
    limitations: ''
    measured_by: provider_self_report
    effort: null
    harness: null
    sources:
    - source_id: model-233-google-gemma-4-model-card
      snapshot_ref: sha256:5793665e8eea120093150c2c6f87362e152c6e0db0fa26130beb59ccd2c07992
      cited_regions:
      - benchmark-results
    id: google/gemma-4-e4b-it#deepmind_mrcr_v2#9ddc534979c9
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
  huggingface_downloads: 197704
  huggingface_likes: 329
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
  huggingface_url: https://huggingface.co/google/gemma-4-E4B-it
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
- id: google/gemma-4-e4b-it#model.fits_hardware
  subject:
    kind: model
    id: google/gemma-4-e4b-it
  facet: model.fits_hardware
  value:
  - amd_instinct_mi210
  - amd_instinct_mi250x
  - amd_instinct_mi300x
  - amd_instinct_mi325x
  - amd_instinct_mi355x
  - amd_rx_7900_xt
  - amd_rx_7900_xtx
  - amd_rx_9070_xt
  - amd_ryzen_ai_max_plus_395
  - apple_m1_max
  - apple_m2_max
  - apple_m2_ultra
  - apple_m3_max
  - apple_m3_ultra
  - apple_m4
  - apple_m4_max
  - apple_m4_pro
  - apple_m5_max
  - google_tpu7x
  - google_tpu_v4
  - google_tpu_v5e
  - google_tpu_v5p
  - google_tpu_v6e
  - intel_arc_a770_16gb
  - intel_gaudi_2
  - intel_gaudi_3
  - nvidia_a100_40gb_sxm
  - nvidia_a100_80gb_sxm
  - nvidia_b200
  - nvidia_b300
  - nvidia_dgx_spark
  - nvidia_gb200_superchip
  - nvidia_h100_nvl
  - nvidia_h100_pcie
  - nvidia_h100_sxm
  - nvidia_h200_sxm
  - nvidia_jetson_agx_orin_32gb
  - nvidia_jetson_agx_orin_64gb
  - nvidia_jetson_orin_nano_8gb
  - nvidia_jetson_orin_nx_16gb
  - nvidia_jetson_orin_nx_8gb
  - nvidia_jetson_t4000
  - nvidia_jetson_t5000
  - nvidia_l4
  - nvidia_l40s
  - nvidia_rtx_3060_12gb
  - nvidia_rtx_3090
  - nvidia_rtx_4000_sff_ada
  - nvidia_rtx_4060_ti_16gb
  - nvidia_rtx_4070_ti_super
  - nvidia_rtx_4080_super
  - nvidia_rtx_4090
  - nvidia_rtx_4500_ada
  - nvidia_rtx_5000_ada
  - nvidia_rtx_5080
  - nvidia_rtx_5090
  - nvidia_rtx_6000_ada
  - nvidia_rtx_a6000
  - nvidia_rubin_gpu
  - nvidia_tesla_p40
  - qualcomm_snapdragon_x_elite
  state: known
  derivation:
    method: decision.hardware.compute_fit@1
    formula: parameters_total * bytes_per_parameter <= memory_capacity_gb * (1 - working_allowance) *
      1e9
    inputs:
      weights_openness: open_weights
      parameters_total: 7996156490
      working_allowance: 0.25
      quant_bytes: '{''bf16'': 2.0, ''fp16'': 2.0, ''fp8'': 1.0, ''int4'': 0.5, ''int8'': 1.0, ''q4'':
        0.5, ''q5'': 0.625, ''q6'': 0.75}'
      has_device_unknowns: 'true'
      model_snapshot_ref: sha256:63cc0c23e2829a09b47cfa25113988cc71368497923c50165b276f7e9f35da96
      hardware_registry_sha256: sha256:10baf5e1ce9e5a1e5b970f4fdc25d9f67db8c562c8c109157ae9722bf6357bff
      hardware_device_count: 64
  sources:
  - source_id: model-174-google-gemma-4-e4b-it-hardware-input
    snapshot_ref: sha256:63cc0c23e2829a09b47cfa25113988cc71368497923c50165b276f7e9f35da96
    cited_regions:
    - rows
- facet: model.class
  value: text-generator
  state: known
  sources:
  - source_id: model-163-google-gemma-4-e4b-it
    snapshot_ref: sha256:b21e4f69614ccd77baa2f3797d05311040dee07b989cb9f0d25111aa4b605b2c
    cited_regions:
    - model-spec
  checked_sources: []
- facet: model.input_modalities
  value: null
  state: not_disclosed
  sources:
  - source_id: model-163-google-gemma-4-e4b-it
    snapshot_ref: sha256:b21e4f69614ccd77baa2f3797d05311040dee07b989cb9f0d25111aa4b605b2c
    cited_regions:
    - model-spec
  checked_sources:
  - model-163-google-gemma-4-e4b-it
- facet: model.output_modalities
  value: null
  state: not_disclosed
  sources:
  - source_id: model-163-google-gemma-4-e4b-it
    snapshot_ref: sha256:b21e4f69614ccd77baa2f3797d05311040dee07b989cb9f0d25111aa4b605b2c
    cited_regions:
    - model-spec
  checked_sources:
  - model-163-google-gemma-4-e4b-it
- facet: model.context_window
  value: null
  state: not_disclosed
  sources:
  - source_id: model-163-google-gemma-4-e4b-it
    snapshot_ref: sha256:b21e4f69614ccd77baa2f3797d05311040dee07b989cb9f0d25111aa4b605b2c
    cited_regions:
    - model-spec
  checked_sources:
  - model-163-google-gemma-4-e4b-it
- facet: model.max_output_tokens
  value: null
  state: not_disclosed
  sources:
  - source_id: model-163-google-gemma-4-e4b-it
    snapshot_ref: sha256:b21e4f69614ccd77baa2f3797d05311040dee07b989cb9f0d25111aa4b605b2c
    cited_regions:
    - model-spec
  checked_sources:
  - model-163-google-gemma-4-e4b-it
- facet: model.weights_openness
  value: open_weights
  state: known
  sources:
  - source_id: model-163-google-gemma-4-e4b-it
    snapshot_ref: sha256:b21e4f69614ccd77baa2f3797d05311040dee07b989cb9f0d25111aa4b605b2c
    cited_regions:
    - model-spec
  checked_sources: []
- facet: licence.commercial_use
  value: null
  state: not_disclosed
  sources:
  - source_id: model-163-google-gemma-4-e4b-it
    snapshot_ref: sha256:b21e4f69614ccd77baa2f3797d05311040dee07b989cb9f0d25111aa4b605b2c
    cited_regions:
    - model-spec
  checked_sources:
  - model-163-google-gemma-4-e4b-it
- facet: licence.user_cap
  value: null
  state: not_disclosed
  sources:
  - source_id: model-163-google-gemma-4-e4b-it
    snapshot_ref: sha256:b21e4f69614ccd77baa2f3797d05311040dee07b989cb9f0d25111aa4b605b2c
    cited_regions:
    - model-spec
  checked_sources:
  - model-163-google-gemma-4-e4b-it
- facet: licence.output_training
  value: null
  state: not_disclosed
  sources:
  - source_id: model-163-google-gemma-4-e4b-it
    snapshot_ref: sha256:b21e4f69614ccd77baa2f3797d05311040dee07b989cb9f0d25111aa4b605b2c
    cited_regions:
    - model-spec
  checked_sources:
  - model-163-google-gemma-4-e4b-it
- facet: licence.fine_tuning
  value: null
  state: not_disclosed
  sources:
  - source_id: model-163-google-gemma-4-e4b-it
    snapshot_ref: sha256:b21e4f69614ccd77baa2f3797d05311040dee07b989cb9f0d25111aa4b605b2c
    cited_regions:
    - model-spec
  checked_sources:
  - model-163-google-gemma-4-e4b-it
- facet: origin.lab_jurisdiction
  value: null
  state: not_disclosed
  sources:
  - source_id: model-163-google-gemma-4-e4b-it
    snapshot_ref: sha256:b21e4f69614ccd77baa2f3797d05311040dee07b989cb9f0d25111aa4b605b2c
    cited_regions:
    - model-spec
  checked_sources:
  - model-163-google-gemma-4-e4b-it
- facet: origin.base_lineage
  value: null
  state: not_disclosed
  sources:
  - source_id: model-163-google-gemma-4-e4b-it
    snapshot_ref: sha256:b21e4f69614ccd77baa2f3797d05311040dee07b989cb9f0d25111aa4b605b2c
    cited_regions:
    - model-spec
  checked_sources:
  - model-163-google-gemma-4-e4b-it
- facet: origin.weights_hosting
  value: null
  state: not_disclosed
  sources:
  - source_id: model-163-google-gemma-4-e4b-it
    snapshot_ref: sha256:b21e4f69614ccd77baa2f3797d05311040dee07b989cb9f0d25111aa4b605b2c
    cited_regions:
    - model-spec
  checked_sources:
  - model-163-google-gemma-4-e4b-it
- facet: model.release_date
  value: null
  state: not_disclosed
  sources:
  - source_id: model-163-google-gemma-4-e4b-it
    snapshot_ref: sha256:b21e4f69614ccd77baa2f3797d05311040dee07b989cb9f0d25111aa4b605b2c
    cited_regions:
    - model-spec
  checked_sources:
  - model-163-google-gemma-4-e4b-it
- facet: model.lifecycle
  value: active
  state: known
  sources:
  - source_id: model-163-google-gemma-4-e4b-it
    snapshot_ref: sha256:b21e4f69614ccd77baa2f3797d05311040dee07b989cb9f0d25111aa4b605b2c
    cited_regions:
    - model-spec
  checked_sources: []
- facet: feature.tool_calling
  value: true
  state: known
  sources:
  - source_id: model-163-google-gemma-4-e4b-it
    snapshot_ref: sha256:b21e4f69614ccd77baa2f3797d05311040dee07b989cb9f0d25111aa4b605b2c
    cited_regions:
    - model-spec
  checked_sources: []
- facet: feature.structured_output
  value: null
  state: not_disclosed
  sources:
  - source_id: model-163-google-gemma-4-e4b-it
    snapshot_ref: sha256:b21e4f69614ccd77baa2f3797d05311040dee07b989cb9f0d25111aa4b605b2c
    cited_regions:
    - model-spec
  checked_sources:
  - model-163-google-gemma-4-e4b-it
- facet: feature.effort_controls
  value: true
  state: known
  sources:
  - source_id: model-163-google-gemma-4-e4b-it
    snapshot_ref: sha256:b21e4f69614ccd77baa2f3797d05311040dee07b989cb9f0d25111aa4b605b2c
    cited_regions:
    - model-spec
  checked_sources: []
- facet: feature.batch
  value: null
  state: not_disclosed
  sources:
  - source_id: model-163-google-gemma-4-e4b-it
    snapshot_ref: sha256:b21e4f69614ccd77baa2f3797d05311040dee07b989cb9f0d25111aa4b605b2c
    cited_regions:
    - model-spec
  checked_sources:
  - model-163-google-gemma-4-e4b-it
- facet: feature.streaming
  value: null
  state: not_disclosed
  sources:
  - source_id: model-163-google-gemma-4-e4b-it
    snapshot_ref: sha256:b21e4f69614ccd77baa2f3797d05311040dee07b989cb9f0d25111aa4b605b2c
    cited_regions:
    - model-spec
  checked_sources:
  - model-163-google-gemma-4-e4b-it
- id: google/gemma-4-e4b-it#model.parameters_total
  subject:
    kind: model
    id: google/gemma-4-e4b-it
  facet: model.parameters_total
  value: 7996156490
  state: known
  sources:
  - source_id: model-174-google-gemma-4-e4b-it-hardware-input
    snapshot_ref: sha256:63cc0c23e2829a09b47cfa25113988cc71368497923c50165b276f7e9f35da96
    cited_regions:
    - rows
- id: google/gemma-4-e4b-it#model.hardware_fit_indeterminate
  subject:
    kind: model
    id: google/gemma-4-e4b-it
  facet: model.hardware_fit_indeterminate
  value:
  - cerebras_wse3
  - nvidia_vera_rubin_superchip
  state: known
  sources:
  - source_id: model-174-google-gemma-4-e4b-it-hardware-input
    snapshot_ref: sha256:63cc0c23e2829a09b47cfa25113988cc71368497923c50165b276f7e9f35da96
    cited_regions:
    - rows
  derivation:
    method: decision.hardware.compute_fit@1
    formula: parameters_total * bytes_per_parameter <= memory_capacity_gb * (1 - working_allowance) *
      1e9
    inputs:
      weights_openness: open_weights
      parameters_total: 7996156490
      working_allowance: 0.25
      quant_bytes: '{''bf16'': 2.0, ''fp16'': 2.0, ''fp8'': 1.0, ''int4'': 0.5, ''int8'': 1.0, ''q4'':
        0.5, ''q5'': 0.625, ''q6'': 0.75}'
      has_device_unknowns: 'true'
      model_snapshot_ref: sha256:63cc0c23e2829a09b47cfa25113988cc71368497923c50165b276f7e9f35da96
      hardware_registry_sha256: sha256:10baf5e1ce9e5a1e5b970f4fdc25d9f67db8c562c8c109157ae9722bf6357bff
      hardware_device_count: 64
card_schema_version: '3.0'
card_author: huggingface-seeder
card_created: '2026-04-05'
card_updated: '2026-09-28'
---


# gemma 4 E4B it

Auto-generated from HuggingFace Hub metadata for [google/gemma-4-E4B-it](https://huggingface.co/google/gemma-4-E4B-it).
