---
model_id: anthropic/claude-mythos-preview
display_name: Claude Mythos Preview
provider: anthropic
provider_display: Anthropic
family: claude-mythos
version: claude-mythos-preview
release_date: '2026-04-07'
last_updated: '2026-04-07'
status: preview
model_type: llm-reasoning
model_subtypes:
- llm-code
- vlm
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
  license_type: proprietary
  license_url: https://www.anthropic.com/legal/commercial-terms
  tos_url: https://www.anthropic.com/legal/commercial-terms
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
    max_output_tokens: 32000
    context_window: 1000000
    streaming: null
    fill_in_middle: null
    json_mode: null
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
    languages:
    - cpp
    - go
    - java
    - javascript
    - python
    - rust
    - typescript
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
    mcp_compatible: true
    parallel_tool_calls: true
    tool_selection_accuracy: null
    multi_turn_tool_use: true
    tool_error_recovery: true
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
  input: 15.0
  output: 75.0
  reasoning: null
  cache_read: 1.5
  cache_write: 18.75
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
    browsecomp: 86.9
    charxiv_reasoning: 86.1
    charxiv_reasoning_tools: 93.2
    gpqa_diamond: 94.55
    graphwalks_bfs_256k_1m: 80.0
    graphwalks_parents_256k_1m: 97.7
    hle: 56.8
    hle_tools: 64.7
    lab_bench_figqa: 79.7
    lab_bench_figqa_tools: 89.0
    mmmlu: 92.67
    osworld: 79.6
    screenspot_pro: 79.5
    screenspot_pro_tools: 92.8
    swe_bench_multilingual: 87.3
    swe_bench_multimodal: 59.0
    swe_bench_pro: 77.8
    swe_bench_verified: 93.9
    terminal_bench_2: 82.0
    usamo_2026: 97.6
  evidence:
  - benchmark_id: metr_time_horizon_50
    model_id_as_evaluated: claude_mythos_preview_early_inspect
    score: 1044.780145
    unit: minutes
    source_url: https://metr.org/assets/benchmark_results_1_1.yaml
    source_kind: benchmark_author
    evidence_date: '2026-05-08'
    date_type: published
    verified_at: '2026-09-11'
    benchmark_version: METR-Horizon-v1.1
    configuration: Time Horizon 1.1 YAML field p50_horizon_length.estimate, minutes, Inspect-era 1.1 protocol. Public chart shows hours. Not Time Horizon 1.0.
    limitations: YAML CI [508.876789, 3304.261235] minutes. Point estimate is above METR's 16-hour (960 minute) reliability note for this suite.
  - benchmark_id: metr_time_horizon_80
    model_id_as_evaluated: claude_mythos_preview_early_inspect
    score: 185.911829
    unit: minutes
    source_url: https://metr.org/assets/benchmark_results_1_1.yaml
    source_kind: benchmark_author
    evidence_date: '2026-05-08'
    date_type: published
    verified_at: '2026-09-11'
    benchmark_version: METR-Horizon-v1.1
    configuration: Time Horizon 1.1 YAML field p80_horizon_length.estimate, minutes, Inspect-era 1.1 protocol. Public chart shows hours. Not Time Horizon 1.0.
    limitations: YAML CI [97.30292, 398.514614] minutes. METR states measurements above 16 hours are unreliable on this suite.
  - benchmark_id: swe_bench_verified
    model_id_as_evaluated: Claude Mythos Preview
    score: 93.9
    unit: percent
    source_url: https://www.anthropic.com/glasswing
    source_kind: provider_self_report
    evidence_date: '2026-04-07'
    date_type: published
    verified_at: '2026-09-23'
    benchmark_version: SWE-bench Verified
    configuration: Project Glasswing evaluation table and system card Table 6.3.A.
    limitations: ''
  - benchmark_id: swe_bench_pro
    model_id_as_evaluated: Claude Mythos Preview
    score: 77.8
    unit: percent
    source_url: https://www.anthropic.com/glasswing
    source_kind: provider_self_report
    evidence_date: '2026-04-07'
    date_type: published
    verified_at: '2026-09-23'
    benchmark_version: SWE-bench Pro
    configuration: Project Glasswing evaluation table and system card Table 6.3.A.
    limitations: ''
  - benchmark_id: swe_bench_multilingual
    model_id_as_evaluated: Claude Mythos Preview
    score: 87.3
    unit: percent
    source_url: https://www.anthropic.com/glasswing
    source_kind: provider_self_report
    evidence_date: '2026-04-07'
    date_type: published
    verified_at: '2026-09-23'
    benchmark_version: SWE-bench Multilingual
    configuration: Project Glasswing evaluation table and system card Table 6.3.A.
    limitations: ''
  - benchmark_id: swe_bench_multimodal
    model_id_as_evaluated: Claude Mythos Preview
    score: 59.0
    unit: percent
    source_url: https://www.anthropic.com/glasswing
    source_kind: provider_self_report
    evidence_date: '2026-04-07'
    date_type: published
    verified_at: '2026-09-23'
    benchmark_version: SWE-bench Multimodal (internal implementation)
    configuration: 'Project Glasswing evaluation table. Anthropic: internal implementation, not comparable to public
      leaderboard scores.'
    limitations: ''
  - benchmark_id: terminal_bench_2
    model_id_as_evaluated: Claude Mythos Preview
    score: 82.0
    unit: percent
    source_url: https://www.anthropic.com/glasswing
    source_kind: provider_self_report
    evidence_date: '2026-04-07'
    date_type: published
    verified_at: '2026-09-23'
    benchmark_version: Terminal-Bench 2.0
    configuration: 'Project Glasswing: Terminus-2 harness, adaptive thinking at maximum effort, 1M-token task budget,
      averaged over five attempts.'
    limitations: ''
  - benchmark_id: gpqa_diamond
    model_id_as_evaluated: Claude Mythos Preview
    score: 94.55
    unit: percent
    source_url: https://www-cdn.anthropic.com/7624816413e9b4d2e3ba620c5a5e091b98b190a5/Claude%20Mythos%20Preview%20System%20Card.pdf
    source_kind: provider_self_report
    evidence_date: '2026-04-07'
    date_type: published
    verified_at: '2026-09-23'
    benchmark_version: GPQA Diamond (198 questions)
    configuration: 'System card section 6.6: 94.55%, averaged over 5 trials.'
    limitations: ''
  - benchmark_id: mmmlu
    model_id_as_evaluated: Claude Mythos Preview
    score: 92.67
    unit: percent
    source_url: https://www-cdn.anthropic.com/7624816413e9b4d2e3ba620c5a5e091b98b190a5/Claude%20Mythos%20Preview%20System%20Card.pdf
    source_kind: provider_self_report
    evidence_date: '2026-04-07'
    date_type: published
    verified_at: '2026-09-23'
    benchmark_version: MMMLU
    configuration: 'System card section 6.7: 92.67% averaged over 5 trials, all non-English pairings.'
    limitations: ''
  - benchmark_id: usamo_2026
    model_id_as_evaluated: Claude Mythos Preview
    score: 97.6
    unit: percent
    source_url: https://www-cdn.anthropic.com/7624816413e9b4d2e3ba620c5a5e091b98b190a5/Claude%20Mythos%20Preview%20System%20Card.pdf
    source_kind: provider_self_report
    evidence_date: '2026-04-07'
    date_type: published
    verified_at: '2026-09-23'
    benchmark_version: USAMO 2026
    configuration: 'System card section 6.8: 97.6%, 10 trials per problem, max effort, no tools.'
    limitations: ''
  - benchmark_id: graphwalks_bfs_256k_1m
    model_id_as_evaluated: Claude Mythos Preview
    score: 80.0
    unit: percent
    source_url: https://www-cdn.anthropic.com/7624816413e9b4d2e3ba620c5a5e091b98b190a5/Claude%20Mythos%20Preview%20System%20Card.pdf
    source_kind: provider_self_report
    evidence_date: '2026-04-07'
    date_type: published
    verified_at: '2026-09-23'
    benchmark_version: GraphWalks BFS 256K-1M
    configuration: System card section 6.9, averaged over 5 trials.
    limitations: ''
  - benchmark_id: graphwalks_parents_256k_1m
    model_id_as_evaluated: Claude Mythos Preview
    score: 97.7
    unit: percent
    source_url: https://www-cdn.anthropic.com/7624816413e9b4d2e3ba620c5a5e091b98b190a5/Claude%20Mythos%20Preview%20System%20Card.pdf
    source_kind: provider_self_report
    evidence_date: '2026-04-07'
    date_type: published
    verified_at: '2026-09-23'
    benchmark_version: GraphWalks parents 256K-1M
    configuration: System card section 6.9, averaged over 5 trials.
    limitations: ''
  - benchmark_id: hle
    model_id_as_evaluated: Claude Mythos Preview
    score: 56.8
    unit: percent
    source_url: https://www.anthropic.com/glasswing
    source_kind: provider_self_report
    evidence_date: '2026-04-07'
    date_type: published
    verified_at: '2026-09-23'
    benchmark_version: Humanity's Last Exam, no tools
    configuration: Project Glasswing table and system card Table 6.3.A.
    limitations: ''
  - benchmark_id: hle_tools
    model_id_as_evaluated: Claude Mythos Preview
    score: 64.7
    unit: percent
    source_url: https://www.anthropic.com/glasswing
    source_kind: provider_self_report
    evidence_date: '2026-04-07'
    date_type: published
    verified_at: '2026-09-23'
    benchmark_version: Humanity's Last Exam, with tools
    configuration: Project Glasswing table and system card Table 6.3.A.
    limitations: ''
  - benchmark_id: browsecomp
    model_id_as_evaluated: Claude Mythos Preview
    score: 86.9
    unit: percent
    source_url: https://www.anthropic.com/glasswing
    source_kind: provider_self_report
    evidence_date: '2026-04-07'
    date_type: published
    verified_at: '2026-09-23'
    benchmark_version: BrowseComp
    configuration: Project Glasswing table and system card Table 6.3.A.
    limitations: ''
  - benchmark_id: osworld
    model_id_as_evaluated: Claude Mythos Preview
    score: 79.6
    unit: percent
    source_url: https://www.anthropic.com/glasswing
    source_kind: provider_self_report
    evidence_date: '2026-04-07'
    date_type: published
    verified_at: '2026-09-23'
    benchmark_version: OSWorld-Verified
    configuration: Project Glasswing table (OSWorld-Verified) and system card Table 6.3.A.
    limitations: ''
  - benchmark_id: lab_bench_figqa
    model_id_as_evaluated: Claude Mythos Preview
    score: 79.7
    unit: percent
    source_url: https://www-cdn.anthropic.com/7624816413e9b4d2e3ba620c5a5e091b98b190a5/Claude%20Mythos%20Preview%20System%20Card.pdf
    source_kind: provider_self_report
    evidence_date: '2026-04-07'
    date_type: published
    verified_at: '2026-09-23'
    benchmark_version: LAB-Bench FigQA, no tools
    configuration: 'System card section 6.11.1: adaptive thinking, max effort, no tools.'
    limitations: ''
  - benchmark_id: lab_bench_figqa_tools
    model_id_as_evaluated: Claude Mythos Preview
    score: 89.0
    unit: percent
    source_url: https://www-cdn.anthropic.com/7624816413e9b4d2e3ba620c5a5e091b98b190a5/Claude%20Mythos%20Preview%20System%20Card.pdf
    source_kind: provider_self_report
    evidence_date: '2026-04-07'
    date_type: published
    verified_at: '2026-09-23'
    benchmark_version: LAB-Bench FigQA, Python tools
    configuration: 'System card section 6.11.1: adaptive thinking, max effort, Python tools.'
    limitations: ''
  - benchmark_id: screenspot_pro
    model_id_as_evaluated: Claude Mythos Preview
    score: 79.5
    unit: percent
    source_url: https://www-cdn.anthropic.com/7624816413e9b4d2e3ba620c5a5e091b98b190a5/Claude%20Mythos%20Preview%20System%20Card.pdf
    source_kind: provider_self_report
    evidence_date: '2026-04-07'
    date_type: published
    verified_at: '2026-09-23'
    benchmark_version: ScreenSpot-Pro, no tools
    configuration: 'System card section 6.11.2: adaptive thinking, max effort, no tools.'
    limitations: ''
  - benchmark_id: screenspot_pro_tools
    model_id_as_evaluated: Claude Mythos Preview
    score: 92.8
    unit: percent
    source_url: https://www-cdn.anthropic.com/7624816413e9b4d2e3ba620c5a5e091b98b190a5/Claude%20Mythos%20Preview%20System%20Card.pdf
    source_kind: provider_self_report
    evidence_date: '2026-04-07'
    date_type: published
    verified_at: '2026-09-23'
    benchmark_version: ScreenSpot-Pro, Python tools
    configuration: 'System card section 6.11.2: adaptive thinking, max effort, Python tools.'
    limitations: ''
  - benchmark_id: charxiv_reasoning
    model_id_as_evaluated: Claude Mythos Preview
    score: 86.1
    unit: percent
    source_url: https://www-cdn.anthropic.com/7624816413e9b4d2e3ba620c5a5e091b98b190a5/Claude%20Mythos%20Preview%20System%20Card.pdf
    source_kind: provider_self_report
    evidence_date: '2026-04-07'
    date_type: published
    verified_at: '2026-09-23'
    benchmark_version: CharXiv Reasoning, no tools
    configuration: 'System card section 6.11.3: 1,000 validation questions, averaged over five runs.'
    limitations: ''
  - benchmark_id: charxiv_reasoning_tools
    model_id_as_evaluated: Claude Mythos Preview
    score: 93.2
    unit: percent
    source_url: https://www-cdn.anthropic.com/7624816413e9b4d2e3ba620c5a5e091b98b190a5/Claude%20Mythos%20Preview%20System%20Card.pdf
    source_kind: provider_self_report
    evidence_date: '2026-04-07'
    date_type: published
    verified_at: '2026-09-23'
    benchmark_version: CharXiv Reasoning, Python tools
    configuration: 'System card section 6.11.3: adaptive thinking, max effort, Python tools.'
    limitations: ''
  benchmark_source: anthropic-system-card
  benchmark_as_of: 2026-04
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
card_schema_version: '3.0'
card_author: models.dev-seeder
card_created: '2026-04-05'
card_updated: '2026-09-23'
authoring_guide:
  applies_to:
    model_id: anthropic/claude-mythos-preview
    version: claude-mythos-preview
  as_of: '2026-09-18'
  status: current
  sections:
    prompt_shape: []
    system_message: []
    reasoning_and_tools:
    - text: Thinking is always on; omitting the thinking parameter still runs adaptive thinking. Disabling
        thinking returns a 400.
      sources:
      - url: https://platform.claude.com/docs/en/build-with-claude/thinking-troubleshooting
        title: Troubleshooting thinking
        accessed: '2026-09-18'
        kind: provider-guidance
      - url: https://platform.claude.com/docs/en/build-with-claude/thinking
        title: Thinking
        accessed: '2026-09-18'
        kind: provider-guidance
    - text: Supports both adaptive thinking and extended thinking with budget_tokens; Anthropic recommends
        adaptive where both are available.
      sources:
      - url: https://platform.claude.com/docs/en/build-with-claude/thinking-troubleshooting
        title: Troubleshooting thinking
        accessed: '2026-09-18'
        kind: provider-guidance
      - url: https://platform.claude.com/docs/en/build-with-claude/extended-thinking
        title: Extended thinking
        accessed: '2026-09-18'
        kind: provider-guidance
    - text: The effort parameter is supported (claude-mythos-preview) and is the recommended control for
        thinking depth under adaptive thinking.
      sources:
      - url: https://platform.claude.com/docs/en/build-with-claude/effort
        title: Effort
        accessed: '2026-09-18'
        kind: provider-guidance
      - url: https://platform.claude.com/docs/en/build-with-claude/thinking
        title: Thinking
        accessed: '2026-09-18'
        kind: provider-guidance
    formatting: []
    failure_modes:
    - text: Prefilling the last assistant turn is not supported on Claude 4.6 models and Claude Mythos
        Preview; migrate off prefilled responses.
      sources:
      - url: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
        title: Prompting best practices
        accessed: '2026-09-18'
        kind: provider-guidance
    retry_advice: []
---


# Claude Opus 4

Claude Opus 4 is a Llm Reasoning model from Anthropic. Part of the claude-opus family. Knowledge cutoff: 2025-03-31.

Licence: proprietary. Vendor terms https://www.anthropic.com/legal/commercial-terms (Anthropic Commercial Terms of Service), read 2026-09-18.

## Key Features
- Extended reasoning / chain-of-thought
- Function calling / tool use
- File/image attachments