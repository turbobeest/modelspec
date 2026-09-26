---
model_id: deepseek/deepseek-coder-6-7b-base
display_name: deepseek coder 6.7B base
provider: deepseek
provider_display: DeepSeek
family: deepseek
version: ''
release_date: '2023-10-23'
last_updated: ''
status: active
model_type: llm-code
model_subtypes: []
tags:
- text-generation
pipeline_tag: text-generation
architecture:
  type: null
  total_parameters: 6740512768
  active_parameters: null
  num_experts: null
  experts_per_token: null
  num_layers: 32
  hidden_size: 4096
  intermediate_size: 11008
  attention_type: null
  num_attention_heads: 32
  num_kv_heads: 32
  positional_encoding: null
  rope_theta: null
  vocab_size: 32256
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
  license_type: deepseek
  license_url: https://huggingface.co/deepseek-ai/deepseek-coder-6.7b-base/raw/main/LICENSE
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
  origin_org_type: private
modalities:
  input:
  - text
  output:
  - text
  text:
    max_input_tokens: null
    max_output_tokens: null
    context_window: 16384
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
    overall: tier-2
    languages: []
    agentic_coding: false
    code_review: false
    refactoring: false
    debugging: true
    test_generation: false
    documentation: false
    code_completion: true
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
  input: 0.14
  output: 0.28
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
    model_id: deepseek-ai/deepseek-coder-6.7b-base
    url: https://huggingface.co/deepseek-ai/deepseek-coder-6.7b-base
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
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 37.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#arc_challenge#b642a008b852
  - benchmark_id: gsm8k
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 18.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#gsm8k#6b6fc424e0d2
  - benchmark_id: hellaswag
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 53.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#hellaswag#3c0b3955b9dd
  - benchmark_id: mmlu_abstract_algebra
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 33.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_abstract_algebra#347d078ea139
  - benchmark_id: mmlu_anatomy
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 40.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_anatomy#ebce317717d9
  - benchmark_id: mmlu_astronomy
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 35.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_astronomy#030b4fb8c039
  - benchmark_id: mmlu_business_ethics
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 40.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_business_ethics#e6dcda18dd6c
  - benchmark_id: mmlu_clinical_knowledge
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 41.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_clinical_knowledge#4ee00078a4f4
  - benchmark_id: mmlu_college_biology
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 30.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_college_biology#16532f246700
  - benchmark_id: mmlu_college_chemistry
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 39.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_college_chemistry#f493b3692efc
  - benchmark_id: mmlu_college_computer_science
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 43.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_college_computer_science#85251b721cea
  - benchmark_id: mmlu_college_mathematics
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 32.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_college_mathematics#b3ff0dda0a9d
  - benchmark_id: mmlu_college_medicine
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 34.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_college_medicine#ed9e50c26600
  - benchmark_id: mmlu_college_physics
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 25.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_college_physics#e3acc0dbd330
  - benchmark_id: mmlu_computer_security
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 62.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_computer_security#f601ea00d8e2
  - benchmark_id: mmlu_conceptual_physics
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 35.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_conceptual_physics#6b38a3a3fe22
  - benchmark_id: mmlu_econometrics
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 29.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_econometrics#aa9823070a7f
  - benchmark_id: mmlu_electrical_engineering
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 45.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_electrical_engineering#c362101dd4cf
  - benchmark_id: mmlu_elementary_mathematics
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 31.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_elementary_mathematics#89f972269412
  - benchmark_id: mmlu_formal_logic
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 29.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_formal_logic#797c84c87317
  - benchmark_id: mmlu_global_facts
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 28.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_global_facts#6fff2506c929
  - benchmark_id: mmlu_high_school_biology
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 36.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_high_school_biology#ec0ce99a2278
  - benchmark_id: mmlu_high_school_chemistry
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 29.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_high_school_chemistry#b8302e6312e4
  - benchmark_id: mmlu_high_school_computer_science
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 52.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_high_school_computer_science#afcb7595dcb5
  - benchmark_id: mmlu_high_school_european_history
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 37.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_high_school_european_history#b80f0bc4331a
  - benchmark_id: mmlu_high_school_geography
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 40.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_high_school_geography#a6d6a79141d7
  - benchmark_id: mmlu_high_school_government_and_politics
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 42.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_high_school_government_and_politics#5f6180214478
  - benchmark_id: mmlu_high_school_macroeconomics
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 34.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_high_school_macroeconomics#7d70cc5bc95c
  - benchmark_id: mmlu_high_school_mathematics
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 28.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_high_school_mathematics#376fc6c9238e
  - benchmark_id: mmlu_high_school_microeconomics
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 36.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_high_school_microeconomics#a5a22ba6a10e
  - benchmark_id: mmlu_high_school_physics
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 27.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_high_school_physics#3363a911adac
  - benchmark_id: mmlu_high_school_psychology
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 38.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_high_school_psychology#d28a538eb57e
  - benchmark_id: mmlu_high_school_statistics
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 37.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_high_school_statistics#8cb840da53dd
  - benchmark_id: mmlu_high_school_us_history
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 34.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_high_school_us_history#f19094aa23ec
  - benchmark_id: mmlu_high_school_world_history
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 32.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_high_school_world_history#9b57ee283890
  - benchmark_id: mmlu_human_aging
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 38.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_human_aging#eb1e8c5b92e0
  - benchmark_id: mmlu_human_sexuality
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 46.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_human_sexuality#c3a362ec3d91
  - benchmark_id: mmlu_international_law
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 52.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_international_law#d7361ab1f75a
  - benchmark_id: mmlu_jurisprudence
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 34.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_jurisprudence#2756150929ad
  - benchmark_id: mmlu_logical_fallacies
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 42.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_logical_fallacies#871c3da1553b
  - benchmark_id: mmlu_machine_learning
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 27.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_machine_learning#53700415c8df
  - benchmark_id: mmlu_management
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 42.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_management#558df888553d
  - benchmark_id: mmlu_marketing
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 63.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_marketing#155f8fb73be9
  - benchmark_id: mmlu_medical_genetics
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 47.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_medical_genetics#48af49402a86
  - benchmark_id: mmlu_miscellaneous
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 40.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_miscellaneous#66c06410b031
  - benchmark_id: mmlu_moral_disputes
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 40.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_moral_disputes#8138a9339463
  - benchmark_id: mmlu_moral_scenarios
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 28.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_moral_scenarios#6157f3d268e2
  - benchmark_id: mmlu_nutrition
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 40.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_nutrition#769e5a778ff2
  - benchmark_id: mmlu_philosophy
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 44.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_philosophy#13cab8929f0c
  - benchmark_id: mmlu_prehistory
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 28.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_prehistory#2f6fe47180e6
  - benchmark_id: mmlu_professional_accounting
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 34.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_professional_accounting#a04664fa7fbc
  - benchmark_id: mmlu_professional_law
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 28.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_professional_law#5910120b96ea
  - benchmark_id: mmlu_professional_medicine
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 44.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_professional_medicine#9c63e29ea5d8
  - benchmark_id: mmlu_professional_psychology
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 31.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_professional_psychology#039f3aa1eb1d
  - benchmark_id: mmlu_public_relations
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 50.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_public_relations#fbd42225b26e
  - benchmark_id: mmlu_security_studies
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 42.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_security_studies#bd2c9806dad0
  - benchmark_id: mmlu_sociology
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 45.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_sociology#ec58c3831d8e
  - benchmark_id: mmlu_us_foreign_policy
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 49.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_us_foreign_policy#47b11c31d4c6
  - benchmark_id: mmlu_virology
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 41.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_virology#94c9ec70ae27
  - benchmark_id: mmlu_world_religions
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 38.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#mmlu_world_religions#c72d1920d8b1
  - benchmark_id: truthfulqa
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 40.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#truthfulqa#e518d499b3bc
  - benchmark_id: winogrande
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-base
    score: 58.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-02'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-b411691a236c
      snapshot_ref: sha256:7d618dec145bc3d2f6ea2906a9f71121bbb9d88f85bc937f810d5d8e8e443292
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-base#winogrande#0e5ffee404bf
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
  huggingface_downloads: 55682
  huggingface_likes: 122
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
  huggingface_url: https://huggingface.co/deepseek-ai/deepseek-coder-6.7b-base
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

# deepseek coder 6.7B base

Auto-generated from HuggingFace Hub metadata for [deepseek-ai/deepseek-coder-6.7b-base](https://huggingface.co/deepseek-ai/deepseek-coder-6.7b-base).

Licence: deepseek. Creator LICENSE file https://huggingface.co/deepseek-ai/deepseek-coder-6.7b-base/raw/main/LICENSE (DeepSeek License Agreement) and Hub cardData.license other and license_name deepseek-license, read 2026-09-18.
