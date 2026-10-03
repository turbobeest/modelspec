---
model_id: deepseek/deepseek-flash
display_name: DeepSeek V4.1 Flash
provider: deepseek
provider_display: DeepSeek
family: deepseek-flash
version: deepseek-flash
release_date: '2026-09-10'
last_updated: '2026-09-10'
status: active
model_type: llm-reasoning
model_subtypes: []
tags: []
pipeline_tag: ''
architecture:
  type: null
  total_parameters: 763205315794
  total_parameters_source: safetensors
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
  - image
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
  input: 0.15
  output: 0.6
  reasoning: null
  cache_read: 0.003
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
    model_id: deepseek-ai/DeepSeek-V4.1-Flash
    url: https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash
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
    model_id_as_evaluated: DeepSeek-V4.1-Flash
    score: 90.9
    unit: percent
    source_url: https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/raw/main/README.md
    source_kind: provider_self_report
    evidence_date: '2026-09-10'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: GPQA Diamond (Pass@1)
    configuration: DeepSeek-V4.1-Flash model card on Hugging Face (repo created and
      README committed 2026-09-10), 'Comparison with frontier models' table, DS-V4.1-Flash
      column only. Instruct model at reasoning_effort=100, temperature 1.0, top_p 0.95.
      The Base-model table was not used (different model).
    limitations: ''
    id: deepseek/deepseek-flash#gpqa_diamond#0828547084a5
    measured_by: provider_self_report
    effort: null
    harness: null
    sources:
    - source_id: model-163-deepseek-deepseek-flash
      snapshot_ref: sha256:4377c9307d7e1cc46355c3eeb5cfa9e9ab98e37afdc509916555c0bfa221a6ed
      cited_regions:
      - model-spec
  - benchmark_id: hle
    model_id_as_evaluated: DS-V4.1-Flash
    score: 36.8
    unit: percent
    source_url: https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash
    source_kind: provider_self_report
    evidence_date: '2026-09-10'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: HLE (Pass@1)
    configuration: DeepSeek-V4.1-Flash model card on Hugging Face, 'Comparison with frontier models
      (Max reasoning effort)' table, DS-V4.1-Flash column only. The card evaluates agentic coding
      with the Minimal mode of DeepSeek Harness and a 1M-token context window. Full set; the card
      gives 39.1 on the text-only subset, not taken.
    limitations: ''
    measured_by: provider_self_report
    effort: max
    harness: null
    sources:
    - source_id: model-233-deepseek-v4-1-flash-model-card
      snapshot_ref: sha256:942f4ddcbce8049aab488572216911adc7eae5fe5d3823ce7fa4e81ba49a4f53
      cited_regions:
      - comparison-with-frontier-models
    id: deepseek/deepseek-flash#hle#5aa976480984
  - benchmark_id: hle_tools
    model_id_as_evaluated: DS-V4.1-Flash
    score: 63.9
    unit: percent
    source_url: https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash
    source_kind: provider_self_report
    evidence_date: '2026-09-10'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: HLE w/ tools (Pass@1)
    configuration: DeepSeek-V4.1-Flash model card on Hugging Face, 'Comparison with frontier models
      (Max reasoning effort)' table, DS-V4.1-Flash column only. The card evaluates agentic coding
      with the Minimal mode of DeepSeek Harness and a 1M-token context window.
    limitations: ''
    measured_by: provider_self_report
    effort: max
    harness: null
    sources:
    - source_id: model-233-deepseek-v4-1-flash-model-card
      snapshot_ref: sha256:942f4ddcbce8049aab488572216911adc7eae5fe5d3823ce7fa4e81ba49a4f53
      cited_regions:
      - comparison-with-frontier-models
    id: deepseek/deepseek-flash#hle_tools#619ab50681a4
  - benchmark_id: terminal_bench_v2_1
    model_id_as_evaluated: DS-V4.1-Flash
    score: 90.6
    unit: percent
    source_url: https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash
    source_kind: provider_self_report
    evidence_date: '2026-09-10'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: Terminal-Bench 2.1 (Pass@1)
    configuration: DeepSeek-V4.1-Flash model card on Hugging Face, 'Comparison with frontier models
      (Max reasoning effort)' table, DS-V4.1-Flash column only. The card evaluates agentic coding
      with the Minimal mode of DeepSeek Harness and a 1M-token context window.
    limitations: ''
    measured_by: provider_self_report
    effort: max
    harness: null
    sources:
    - source_id: model-233-deepseek-v4-1-flash-model-card
      snapshot_ref: sha256:942f4ddcbce8049aab488572216911adc7eae5fe5d3823ce7fa4e81ba49a4f53
      cited_regions:
      - comparison-with-frontier-models
    id: deepseek/deepseek-flash#terminal_bench_v2_1#428207633f83
  - benchmark_id: terminal_bench_3_0
    model_id_as_evaluated: DS-V4.1-Flash
    score: 30.0
    unit: percent
    source_url: https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash
    source_kind: provider_self_report
    evidence_date: '2026-09-10'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: Terminal-Bench 3.0 (Pass@1)
    configuration: DeepSeek-V4.1-Flash model card on Hugging Face, 'Comparison with frontier models
      (Max reasoning effort)' table, DS-V4.1-Flash column only. The card evaluates agentic coding
      with the Minimal mode of DeepSeek Harness and a 1M-token context window.
    limitations: ''
    measured_by: provider_self_report
    effort: max
    harness: null
    sources:
    - source_id: model-233-deepseek-v4-1-flash-model-card
      snapshot_ref: sha256:942f4ddcbce8049aab488572216911adc7eae5fe5d3823ce7fa4e81ba49a4f53
      cited_regions:
      - comparison-with-frontier-models
    id: deepseek/deepseek-flash#terminal_bench_3_0#d51f155e47cc
  - benchmark_id: terminal_bench_v4_0
    model_id_as_evaluated: DS-V4.1-Flash
    score: 31.2
    unit: percent
    source_url: https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash
    source_kind: provider_self_report
    evidence_date: '2026-09-10'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: Terminal-Bench 4.0 (Pass@1)
    configuration: DeepSeek-V4.1-Flash model card on Hugging Face, 'Comparison with frontier models
      (Max reasoning effort)' table, DS-V4.1-Flash column only. The card evaluates agentic coding
      with the Minimal mode of DeepSeek Harness and a 1M-token context window.
    limitations: ''
    measured_by: provider_self_report
    effort: max
    harness: null
    sources:
    - source_id: model-233-deepseek-v4-1-flash-model-card
      snapshot_ref: sha256:942f4ddcbce8049aab488572216911adc7eae5fe5d3823ce7fa4e81ba49a4f53
      cited_regions:
      - comparison-with-frontier-models
    id: deepseek/deepseek-flash#terminal_bench_v4_0#8686f38d6b8d
  - benchmark_id: cybergym
    model_id_as_evaluated: DS-V4.1-Flash
    score: 88.1
    unit: percent
    source_url: https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash
    source_kind: provider_self_report
    evidence_date: '2026-09-10'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: CyberGym (Pass@1)
    configuration: DeepSeek-V4.1-Flash model card on Hugging Face, 'Comparison with frontier models
      (Max reasoning effort)' table, DS-V4.1-Flash column only. The card evaluates agentic coding
      with the Minimal mode of DeepSeek Harness and a 1M-token context window.
    limitations: ''
    measured_by: provider_self_report
    effort: max
    harness: null
    sources:
    - source_id: model-233-deepseek-v4-1-flash-model-card
      snapshot_ref: sha256:942f4ddcbce8049aab488572216911adc7eae5fe5d3823ce7fa4e81ba49a4f53
      cited_regions:
      - comparison-with-frontier-models
    id: deepseek/deepseek-flash#cybergym#dbc33b8e6302
  - benchmark_id: deepswe_v1_1
    model_id_as_evaluated: DS-V4.1-Flash
    score: 74.2
    unit: percent
    source_url: https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash
    source_kind: provider_self_report
    evidence_date: '2026-09-10'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: DeepSWE v1.1 (Resolved)
    configuration: DeepSeek-V4.1-Flash model card on Hugging Face, 'Comparison with frontier models
      (Max reasoning effort)' table, DS-V4.1-Flash column only. The card evaluates agentic coding
      with the Minimal mode of DeepSeek Harness and a 1M-token context window.
    limitations: ''
    measured_by: provider_self_report
    effort: max
    harness: null
    sources:
    - source_id: model-233-deepseek-v4-1-flash-model-card
      snapshot_ref: sha256:942f4ddcbce8049aab488572216911adc7eae5fe5d3823ce7fa4e81ba49a4f53
      cited_regions:
      - comparison-with-frontier-models
    id: deepseek/deepseek-flash#deepswe_v1_1#239e2cd499c6
  - benchmark_id: brokenarxiv
    model_id_as_evaluated: DeepSeek-V4.1-Flash (Max)
    score: 40.87
    unit: percent
    source_url: https://matharena.ai/competition_tables/overall--brokenarxiv
    source_kind: benchmark_author
    evidence_date: '2026-09-30'
    date_type: evaluated
    verified_at: '2026-09-30'
    benchmark_version: BrokenArXiv, MathArena Overall table
    configuration: MathArena competition table read 2026-09-29; the table states no run date,
      so the reading is dated by the observation. Accuracy averaged over four runs per problem.
      Effort max, as the model cell names it.
    limitations: Overall pools MathArena's monthly editions, so it moves when an edition is added.
      MathArena warns the model was released after the problems were.
    measured_by: benchmark_author
    effort: max
    harness: null
    sources:
    - source_id: model-233-matharena-brokenarxiv
      snapshot_ref: sha256:6d37ddbf9d94259ac1372ebffce5792c896cf14d81297a7af9b2d846d538254b
      cited_regions:
      - rows
    quality_flags:
    - contamination_warning
    observed_at: '2026-09-30'
    id: deepseek/deepseek-flash#brokenarxiv#f7c201ee77cd
  - benchmark_id: arxivmath
    model_id_as_evaluated: DeepSeek-V4.1-Flash (Max)
    score: 53.28
    unit: percent
    source_url: https://matharena.ai/competition_tables/overall--arxivmath
    source_kind: benchmark_author
    evidence_date: '2026-09-30'
    date_type: evaluated
    verified_at: '2026-09-30'
    benchmark_version: ArXivMath, MathArena Overall table
    configuration: MathArena competition table read 2026-09-29; the table states no run date,
      so the reading is dated by the observation. Accuracy averaged over four runs per problem.
      Effort max, as the model cell names it.
    limitations: Overall pools MathArena's monthly editions, so it moves when an edition is added.
      MathArena warns the model was released after the problems were.
    measured_by: benchmark_author
    effort: max
    harness: null
    sources:
    - source_id: model-233-matharena-arxivmath
      snapshot_ref: sha256:8a7a53d402a60a08b27d509895c3ffadb2737db7a41e78b074f9783b0c6333a9
      cited_regions:
      - rows
    quality_flags:
    - contamination_warning
    observed_at: '2026-09-30'
    id: deepseek/deepseek-flash#arxivmath#7764dbcf7819
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
  huggingface_url: https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash
  arxiv_url: ''
  paper_url: ''
  github_url: ''
  ollama_url: ''
  artificial_analysis_url: ''
  arena_url: ''
  last_scraped_models_dev: ''
  last_scraped_huggingface: '2026-09-12'
  last_scraped_benchmarks: ''
  last_scraped_pricing: ''
facts:
- facet: model.class
  value: text-generator
  state: known
  sources:
  - source_id: model-163-deepseek-deepseek-flash
    snapshot_ref: sha256:347c9db4e5506acb531cbc3b724407ab88e9af8781679152f0823d7bac16d251
    cited_regions:
    - model-spec
  checked_sources: []
- facet: model.input_modalities
  value: null
  state: not_disclosed
  sources:
  - source_id: model-163-deepseek-deepseek-flash
    snapshot_ref: sha256:347c9db4e5506acb531cbc3b724407ab88e9af8781679152f0823d7bac16d251
    cited_regions:
    - model-spec
  checked_sources:
  - model-163-deepseek-deepseek-flash
- facet: model.output_modalities
  value: null
  state: not_disclosed
  sources:
  - source_id: model-163-deepseek-deepseek-flash
    snapshot_ref: sha256:347c9db4e5506acb531cbc3b724407ab88e9af8781679152f0823d7bac16d251
    cited_regions:
    - model-spec
  checked_sources:
  - model-163-deepseek-deepseek-flash
- facet: model.context_window
  value: null
  state: not_disclosed
  sources:
  - source_id: model-163-deepseek-deepseek-flash
    snapshot_ref: sha256:347c9db4e5506acb531cbc3b724407ab88e9af8781679152f0823d7bac16d251
    cited_regions:
    - model-spec
  checked_sources:
  - model-163-deepseek-deepseek-flash
- facet: model.max_output_tokens
  value: null
  state: not_disclosed
  sources:
  - source_id: model-163-deepseek-deepseek-flash
    snapshot_ref: sha256:347c9db4e5506acb531cbc3b724407ab88e9af8781679152f0823d7bac16d251
    cited_regions:
    - model-spec
  checked_sources:
  - model-163-deepseek-deepseek-flash
- facet: model.weights_openness
  value: open_weights
  state: known
  sources:
  - source_id: model-163-deepseek-deepseek-flash
    snapshot_ref: sha256:347c9db4e5506acb531cbc3b724407ab88e9af8781679152f0823d7bac16d251
    cited_regions:
    - model-spec
  checked_sources: []
- facet: licence.commercial_use
  value: null
  state: not_disclosed
  sources:
  - source_id: model-163-deepseek-deepseek-flash
    snapshot_ref: sha256:347c9db4e5506acb531cbc3b724407ab88e9af8781679152f0823d7bac16d251
    cited_regions:
    - model-spec
  checked_sources:
  - model-163-deepseek-deepseek-flash
- facet: licence.user_cap
  value: null
  state: not_disclosed
  sources:
  - source_id: model-163-deepseek-deepseek-flash
    snapshot_ref: sha256:347c9db4e5506acb531cbc3b724407ab88e9af8781679152f0823d7bac16d251
    cited_regions:
    - model-spec
  checked_sources:
  - model-163-deepseek-deepseek-flash
- facet: licence.output_training
  value: null
  state: not_disclosed
  sources:
  - source_id: model-163-deepseek-deepseek-flash
    snapshot_ref: sha256:347c9db4e5506acb531cbc3b724407ab88e9af8781679152f0823d7bac16d251
    cited_regions:
    - model-spec
  checked_sources:
  - model-163-deepseek-deepseek-flash
- facet: licence.fine_tuning
  value: null
  state: not_disclosed
  sources:
  - source_id: model-163-deepseek-deepseek-flash
    snapshot_ref: sha256:347c9db4e5506acb531cbc3b724407ab88e9af8781679152f0823d7bac16d251
    cited_regions:
    - model-spec
  checked_sources:
  - model-163-deepseek-deepseek-flash
- facet: origin.lab_jurisdiction
  value: null
  state: not_disclosed
  sources:
  - source_id: model-163-deepseek-deepseek-flash
    snapshot_ref: sha256:347c9db4e5506acb531cbc3b724407ab88e9af8781679152f0823d7bac16d251
    cited_regions:
    - model-spec
  checked_sources:
  - model-163-deepseek-deepseek-flash
- facet: origin.base_lineage
  value: null
  state: not_disclosed
  sources:
  - source_id: model-163-deepseek-deepseek-flash
    snapshot_ref: sha256:347c9db4e5506acb531cbc3b724407ab88e9af8781679152f0823d7bac16d251
    cited_regions:
    - model-spec
  checked_sources:
  - model-163-deepseek-deepseek-flash
- facet: origin.weights_hosting
  value: null
  state: not_disclosed
  sources:
  - source_id: model-163-deepseek-deepseek-flash
    snapshot_ref: sha256:347c9db4e5506acb531cbc3b724407ab88e9af8781679152f0823d7bac16d251
    cited_regions:
    - model-spec
  checked_sources:
  - model-163-deepseek-deepseek-flash
- facet: model.release_date
  value: null
  state: not_disclosed
  sources:
  - source_id: model-163-deepseek-deepseek-flash
    snapshot_ref: sha256:347c9db4e5506acb531cbc3b724407ab88e9af8781679152f0823d7bac16d251
    cited_regions:
    - model-spec
  checked_sources:
  - model-163-deepseek-deepseek-flash
- facet: model.lifecycle
  value: active
  state: known
  sources:
  - source_id: model-163-deepseek-deepseek-flash
    snapshot_ref: sha256:347c9db4e5506acb531cbc3b724407ab88e9af8781679152f0823d7bac16d251
    cited_regions:
    - model-spec
  checked_sources: []
- facet: feature.tool_calling
  value: true
  state: known
  sources:
  - source_id: model-163-deepseek-deepseek-flash
    snapshot_ref: sha256:347c9db4e5506acb531cbc3b724407ab88e9af8781679152f0823d7bac16d251
    cited_regions:
    - model-spec
  checked_sources: []
- facet: feature.structured_output
  value: null
  state: not_disclosed
  sources:
  - source_id: model-163-deepseek-deepseek-flash
    snapshot_ref: sha256:347c9db4e5506acb531cbc3b724407ab88e9af8781679152f0823d7bac16d251
    cited_regions:
    - model-spec
  checked_sources:
  - model-163-deepseek-deepseek-flash
- facet: feature.effort_controls
  value: true
  state: known
  sources:
  - source_id: model-163-deepseek-deepseek-flash
    snapshot_ref: sha256:347c9db4e5506acb531cbc3b724407ab88e9af8781679152f0823d7bac16d251
    cited_regions:
    - model-spec
  checked_sources: []
- facet: feature.batch
  value: null
  state: not_disclosed
  sources:
  - source_id: model-163-deepseek-deepseek-flash
    snapshot_ref: sha256:347c9db4e5506acb531cbc3b724407ab88e9af8781679152f0823d7bac16d251
    cited_regions:
    - model-spec
  checked_sources:
  - model-163-deepseek-deepseek-flash
- facet: feature.streaming
  value: null
  state: not_disclosed
  sources:
  - source_id: model-163-deepseek-deepseek-flash
    snapshot_ref: sha256:347c9db4e5506acb531cbc3b724407ab88e9af8781679152f0823d7bac16d251
    cited_regions:
    - model-spec
  checked_sources:
  - model-163-deepseek-deepseek-flash
- id: deepseek/deepseek-flash#model.parameters_total
  subject:
    kind: model
    id: deepseek/deepseek-flash
  facet: model.parameters_total
  value: 763205315794
  state: known
  sources:
  - source_id: model-174-deepseek-deepseek-flash-hardware-input
    snapshot_ref: sha256:064a0248533339ed7df7625642478c467a36c20fc95426c3faaad6f8f2d579bb
    cited_regions:
    - rows
- id: deepseek/deepseek-flash#model.fits_hardware
  subject:
    kind: model
    id: deepseek/deepseek-flash
  facet: model.fits_hardware
  value:
  - apple_m3_ultra
  state: known
  derivation:
    method: decision.hardware.compute_fit@1
    formula: parameters_total * bytes_per_parameter <= memory_capacity_gb * (1 - working_allowance) *
      1e9
    inputs:
      weights_openness: open_weights
      parameters_total: 763205315794
      working_allowance: 0.25
      quant_bytes: '{''bf16'': 2.0, ''fp16'': 2.0, ''fp8'': 1.0, ''int4'': 0.5, ''int8'': 1.0, ''q4'':
        0.5, ''q5'': 0.625, ''q6'': 0.75}'
      has_device_unknowns: 'true'
      model_snapshot_ref: sha256:064a0248533339ed7df7625642478c467a36c20fc95426c3faaad6f8f2d579bb
      hardware_registry_sha256: sha256:10baf5e1ce9e5a1e5b970f4fdc25d9f67db8c562c8c109157ae9722bf6357bff
      hardware_device_count: 64
  sources:
  - source_id: model-174-deepseek-deepseek-flash-hardware-input
    snapshot_ref: sha256:064a0248533339ed7df7625642478c467a36c20fc95426c3faaad6f8f2d579bb
    cited_regions:
    - rows
- id: deepseek/deepseek-flash#model.hardware_fit_indeterminate
  subject:
    kind: model
    id: deepseek/deepseek-flash
  facet: model.hardware_fit_indeterminate
  value:
  - cerebras_wse3
  - nvidia_vera_rubin_superchip
  state: known
  sources:
  - source_id: model-174-deepseek-deepseek-flash-hardware-input
    snapshot_ref: sha256:064a0248533339ed7df7625642478c467a36c20fc95426c3faaad6f8f2d579bb
    cited_regions:
    - rows
  derivation:
    method: decision.hardware.compute_fit@1
    formula: parameters_total * bytes_per_parameter <= memory_capacity_gb * (1 - working_allowance) *
      1e9
    inputs:
      weights_openness: open_weights
      parameters_total: 763205315794
      working_allowance: 0.25
      quant_bytes: '{''bf16'': 2.0, ''fp16'': 2.0, ''fp8'': 1.0, ''int4'': 0.5, ''int8'': 1.0, ''q4'':
        0.5, ''q5'': 0.625, ''q6'': 0.75}'
      has_device_unknowns: 'true'
      model_snapshot_ref: sha256:064a0248533339ed7df7625642478c467a36c20fc95426c3faaad6f8f2d579bb
      hardware_registry_sha256: sha256:10baf5e1ce9e5a1e5b970f4fdc25d9f67db8c562c8c109157ae9722bf6357bff
      hardware_device_count: 64
card_schema_version: '3.0'
card_author: models.dev-seeder
card_created: '2026-04-05'
card_updated: '2026-09-28'
---

# DeepSeek V4.1 Flash

DeepSeek V4.1 Flash is a Llm Reasoning model from DeepSeek. Part of the deepseek-flash family. Knowledge cutoff: 2025-05.

## Key Features
- Extended reasoning / chain-of-thought
- Function calling / tool use
- Structured output (JSON mode)
- Open weights
- File/image attachments
