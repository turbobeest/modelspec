---
model_id: nous-research/nous-hermes-2-yi-34b
display_name: Nous Hermes 2 Yi 34B
provider: nous-research
provider_display: Nous Research
family: yi
version: ''
release_date: '2023-12-23'
last_updated: ''
status: active
model_type: llm-chat
model_subtypes: []
tags:
- text-generation
pipeline_tag: text-generation
architecture:
  type: null
  total_parameters: 34388917248
  active_parameters: null
  num_experts: null
  experts_per_token: null
  num_layers: 60
  hidden_size: 7168
  intermediate_size: 20480
  attention_type: null
  num_attention_heads: 56
  num_kv_heads: 8
  positional_encoding: null
  rope_theta: null
  vocab_size: 64000
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
  base_model: 01-ai/Yi-34B
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
  license_type: apache-2.0
  license_url: https://huggingface.co/NousResearch/Nous-Hermes-2-Yi-34B/raw/main/README.md
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
  origin_org_type: open-collective
modalities:
  input:
  - text
  output:
  - text
  text:
    max_input_tokens: null
    max_output_tokens: null
    context_window: 4096
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
    model_id: NousResearch/Nous-Hermes-2-Yi-34B
    url: https://huggingface.co/NousResearch/Nous-Hermes-2-Yi-34B
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
  - benchmark_id: arc_challenge
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 66.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#arc_challenge#58e96f968952
  - benchmark_id: gsm8k
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 70.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#gsm8k#3fe7f54b4dc1
  - benchmark_id: hellaswag
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 85.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#hellaswag#9502035fc51a
  - benchmark_id: mmlu_abstract_algebra
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 49.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_abstract_algebra#641b22eb9613
  - benchmark_id: mmlu_anatomy
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 71.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_anatomy#a1a48043201f
  - benchmark_id: mmlu_astronomy
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 89.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_astronomy#dc7c886dbfdb
  - benchmark_id: mmlu_business_ethics
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 78.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_business_ethics#a3f4ce25264b
  - benchmark_id: mmlu_clinical_knowledge
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 80.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_clinical_knowledge#35d8fba5ab14
  - benchmark_id: mmlu_college_biology
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 90.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_college_biology#3cd61b93f57b
  - benchmark_id: mmlu_college_chemistry
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 51.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_college_chemistry#989fabb35a23
  - benchmark_id: mmlu_college_computer_science
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 65.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_college_computer_science#24b1871ea35d
  - benchmark_id: mmlu_college_mathematics
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 49.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_college_mathematics#da25d09181b1
  - benchmark_id: mmlu_college_medicine
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 69.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_college_medicine#51d8a292cf00
  - benchmark_id: mmlu_college_physics
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 52.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_college_physics#9d4f4e6584a0
  - benchmark_id: mmlu_computer_security
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 83.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_computer_security#507bf99500c7
  - benchmark_id: mmlu_conceptual_physics
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 79.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_conceptual_physics#179097c3b82f
  - benchmark_id: mmlu_econometrics
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 57.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_econometrics#c7ea4557cf7b
  - benchmark_id: mmlu_electrical_engineering
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 77.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_electrical_engineering#f519ea02f51c
  - benchmark_id: mmlu_elementary_mathematics
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 69.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_elementary_mathematics#b6752d376ad8
  - benchmark_id: mmlu_formal_logic
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 57.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_formal_logic#190ed2739080
  - benchmark_id: mmlu_global_facts
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 51.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_global_facts#fb646876f19a
  - benchmark_id: mmlu_high_school_biology
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 89.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_high_school_biology#70d778e4aa4f
  - benchmark_id: mmlu_high_school_chemistry
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 62.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_high_school_chemistry#8be90e346f46
  - benchmark_id: mmlu_high_school_computer_science
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 84.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_high_school_computer_science#222e9c692b5b
  - benchmark_id: mmlu_high_school_european_history
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 87.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_high_school_european_history#c0eb3bf6ca67
  - benchmark_id: mmlu_high_school_geography
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 89.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_high_school_geography#3df80005e62e
  - benchmark_id: mmlu_high_school_government_and_politics
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 97.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_high_school_government_and_politics#ca183be0a91d
  - benchmark_id: mmlu_high_school_macroeconomics
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 82.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_high_school_macroeconomics#2fbeb2b0c422
  - benchmark_id: mmlu_high_school_mathematics
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 41.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_high_school_mathematics#1fce477984b8
  - benchmark_id: mmlu_high_school_microeconomics
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 85.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_high_school_microeconomics#e01388f120b3
  - benchmark_id: mmlu_high_school_physics
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 50.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_high_school_physics#ef6dab5c19b8
  - benchmark_id: mmlu_high_school_psychology
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 92.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_high_school_psychology#9010a0fe5479
  - benchmark_id: mmlu_high_school_statistics
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 66.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_high_school_statistics#f657080003ae
  - benchmark_id: mmlu_high_school_us_history
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 91.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_high_school_us_history#2cd3bd0aeb1f
  - benchmark_id: mmlu_high_school_world_history
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 90.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_high_school_world_history#376968a124bb
  - benchmark_id: mmlu_human_aging
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 79.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_human_aging#bf187a25d1ee
  - benchmark_id: mmlu_human_sexuality
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 89.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_human_sexuality#72b699be262b
  - benchmark_id: mmlu_international_law
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 90.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_international_law#b57ae17f8b9a
  - benchmark_id: mmlu_jurisprudence
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 89.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_jurisprudence#0ae8621f1c93
  - benchmark_id: mmlu_logical_fallacies
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 87.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_logical_fallacies#fd16e4a4910f
  - benchmark_id: mmlu_machine_learning
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 60.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_machine_learning#f791e6cbbaf4
  - benchmark_id: mmlu_management
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 92.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_management#5d17dcd2423a
  - benchmark_id: mmlu_marketing
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 91.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_marketing#9e4c36428882
  - benchmark_id: mmlu_medical_genetics
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 86.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_medical_genetics#66a2eb2d91b4
  - benchmark_id: mmlu_miscellaneous
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 91.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_miscellaneous#a50471aebc41
  - benchmark_id: mmlu_moral_disputes
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 83.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_moral_disputes#a18042f2c687
  - benchmark_id: mmlu_moral_scenarios
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 71.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_moral_scenarios#ace2d27a299a
  - benchmark_id: mmlu_nutrition
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 84.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_nutrition#ee308a1346c9
  - benchmark_id: mmlu_philosophy
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 81.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_philosophy#73ebeef53623
  - benchmark_id: mmlu_prehistory
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 88.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_prehistory#c7d38e02e002
  - benchmark_id: mmlu_professional_accounting
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 64.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_professional_accounting#158ac5cf7f19
  - benchmark_id: mmlu_professional_law
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 61.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_professional_law#4aa3c86e2380
  - benchmark_id: mmlu_professional_medicine
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 83.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_professional_medicine#3a3ea1d082e6
  - benchmark_id: mmlu_professional_psychology
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 82.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_professional_psychology#9b6965a9c40c
  - benchmark_id: mmlu_public_relations
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 71.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_public_relations#35aa8642dbca
  - benchmark_id: mmlu_security_studies
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 84.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_security_studies#0375c3fe492b
  - benchmark_id: mmlu_sociology
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 87.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_sociology#2c9b5e07abfc
  - benchmark_id: mmlu_us_foreign_policy
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 92.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_us_foreign_policy#1f39ec14d202
  - benchmark_id: mmlu_virology
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 57.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_virology#a2ca090411df
  - benchmark_id: mmlu_world_religions
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 87.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#mmlu_world_religions#8dac5a78cd20
  - benchmark_id: truthfulqa
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 60.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#truthfulqa#5379ff6b54a1
  - benchmark_id: winogrande
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Yi-34B
    score: 83.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Yi-34B/results_2023-12-29T16-55-23.292289.json
    source_kind: benchmark_author
    evidence_date: '2023-12-29'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e21c0e7ff1d6
      snapshot_ref: sha256:0facdd02bf2db1a62703421936a62b7411800c9463f3ac5c5f1da5c5c020ef62
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-yi-34b#winogrande#7e8ee3f2ce4e
  benchmark_source: open-llm-leaderboard-v1
  benchmark_as_of: 2024-07
  benchmark_notes: ''
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
  huggingface_downloads: 8213
  huggingface_likes: 256
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
  huggingface_url: https://huggingface.co/NousResearch/Nous-Hermes-2-Yi-34B
  arxiv_url: ''
  paper_url: ''
  github_url: ''
  ollama_url: ''
  artificial_analysis_url: ''
  arena_url: ''
  last_scraped_models_dev: ''
  last_scraped_huggingface: '2026-09-18'
  last_scraped_benchmarks: ''
  last_scraped_pricing: ''
card_schema_version: '3.0'
card_author: huggingface-seeder
card_created: '2026-04-05'
card_updated: '2026-09-18'
---


# Nous Hermes 2 Yi 34B

Auto-generated from HuggingFace Hub metadata for [NousResearch/Nous-Hermes-2-Yi-34B](https://huggingface.co/NousResearch/Nous-Hermes-2-Yi-34B).

Licence: apache-2.0. Creator distribution https://huggingface.co/NousResearch/Nous-Hermes-2-Yi-34B/raw/main/README.md (apache-2.0) and Hub cardData.license apache-2.0, read 2026-09-18.
