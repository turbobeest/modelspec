---
model_id: google/gemma-2b
display_name: gemma 2B
provider: google
provider_display: Google DeepMind
family: gemma
version: ''
release_date: '2024-02-08'
last_updated: ''
status: active
model_type: llm-chat
model_subtypes: []
tags:
- text-generation
pipeline_tag: text-generation
architecture:
  type: null
  total_parameters: 2506172416
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
    context_window: 8192
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
    model_id: google/gemma-2b
    url: https://huggingface.co/google/gemma-2b
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
    model_id_as_evaluated: google/gemma-2b
    score: 48.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#arc_challenge#cc91fa48fbcc
  - benchmark_id: bbh
    model_id_as_evaluated: google/gemma-2b
    score: 33.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/google/gemma-2b/results_2025-02-13T18-27-04.338360.json
    source_kind: benchmark_author
    evidence_date: '2024-06-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v2-5a02359c436a
      snapshot_ref: sha256:4c39df32cd31e3e112ab8e9311e9de6db0428b8183de76c0ae600c6ca5217def
      cited_regions:
      - rows
    id: google/gemma-2b#bbh#dab7697e5419
  - benchmark_id: gpqa_pooled
    model_id_as_evaluated: google/gemma-2b
    score: 25.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/google/gemma-2b/results_2024-10-24T00-00-00.000000.json
    source_kind: benchmark_author
    evidence_date: '2024-06-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v2-5eb856752837
      snapshot_ref: sha256:d31d6dfd0ffc88d90f12e55878abb22f162f8018390391134f3677835ffe48c6
      cited_regions:
      - rows
    id: google/gemma-2b#gpqa_pooled#ec8d1e74f53a
  - benchmark_id: gsm8k
    model_id_as_evaluated: google/gemma-2b
    score: 16.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#gsm8k#7991cf8acd16
  - benchmark_id: hellaswag
    model_id_as_evaluated: google/gemma-2b
    score: 71.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#hellaswag#8d2fd413a777
  - benchmark_id: ifeval
    model_id_as_evaluated: google/gemma-2b
    score: 20.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/google/gemma-2b/results_2024-10-24T00-00-00.000000.json
    source_kind: benchmark_author
    evidence_date: '2024-06-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v2-5eb856752837
      snapshot_ref: sha256:d31d6dfd0ffc88d90f12e55878abb22f162f8018390391134f3677835ffe48c6
      cited_regions:
      - rows
    id: google/gemma-2b#ifeval#2fadc947e95b
  - benchmark_id: math_lvl5
    model_id_as_evaluated: google/gemma-2b
    score: 3.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/google/gemma-2b/results_2025-02-13T18-27-04.338360.json
    source_kind: benchmark_author
    evidence_date: '2024-06-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v2-5a02359c436a
      snapshot_ref: sha256:4c39df32cd31e3e112ab8e9311e9de6db0428b8183de76c0ae600c6ca5217def
      cited_regions:
      - rows
    id: google/gemma-2b#math_lvl5#24ec4deb180c
  - benchmark_id: mmlu_abstract_algebra
    model_id_as_evaluated: google/gemma-2b
    score: 26.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_abstract_algebra#27599cc71ac0
  - benchmark_id: mmlu_anatomy
    model_id_as_evaluated: google/gemma-2b
    score: 48.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_anatomy#936832b51e97
  - benchmark_id: mmlu_astronomy
    model_id_as_evaluated: google/gemma-2b
    score: 42.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_astronomy#261f97fd8c24
  - benchmark_id: mmlu_business_ethics
    model_id_as_evaluated: google/gemma-2b
    score: 44.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_business_ethics#b8b0de6d2d04
  - benchmark_id: mmlu_clinical_knowledge
    model_id_as_evaluated: google/gemma-2b
    score: 46.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_clinical_knowledge#f962d3e3cd87
  - benchmark_id: mmlu_college_biology
    model_id_as_evaluated: google/gemma-2b
    score: 45.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_college_biology#d0208351e83b
  - benchmark_id: mmlu_college_chemistry
    model_id_as_evaluated: google/gemma-2b
    score: 37.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_college_chemistry#147ea2cd35a3
  - benchmark_id: mmlu_college_computer_science
    model_id_as_evaluated: google/gemma-2b
    score: 38.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_college_computer_science#3b18fec23e9f
  - benchmark_id: mmlu_college_mathematics
    model_id_as_evaluated: google/gemma-2b
    score: 30.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_college_mathematics#66b559704d25
  - benchmark_id: mmlu_college_medicine
    model_id_as_evaluated: google/gemma-2b
    score: 42.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_college_medicine#524d979d1ac3
  - benchmark_id: mmlu_college_physics
    model_id_as_evaluated: google/gemma-2b
    score: 14.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_college_physics#bd969bb0391a
  - benchmark_id: mmlu_computer_security
    model_id_as_evaluated: google/gemma-2b
    score: 53.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_computer_security#b35c83c0e6c9
  - benchmark_id: mmlu_conceptual_physics
    model_id_as_evaluated: google/gemma-2b
    score: 41.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_conceptual_physics#f50e025ac1a4
  - benchmark_id: mmlu_econometrics
    model_id_as_evaluated: google/gemma-2b
    score: 31.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_econometrics#cdd161046d8c
  - benchmark_id: mmlu_electrical_engineering
    model_id_as_evaluated: google/gemma-2b
    score: 40.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_electrical_engineering#d1e66c85b05d
  - benchmark_id: mmlu_elementary_mathematics
    model_id_as_evaluated: google/gemma-2b
    score: 26.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_elementary_mathematics#1a67475c8e41
  - benchmark_id: mmlu_formal_logic
    model_id_as_evaluated: google/gemma-2b
    score: 27.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_formal_logic#655b0cd155f5
  - benchmark_id: mmlu_global_facts
    model_id_as_evaluated: google/gemma-2b
    score: 31.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_global_facts#e520f8da71db
  - benchmark_id: mmlu_high_school_biology
    model_id_as_evaluated: google/gemma-2b
    score: 48.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_high_school_biology#d7b3598881ce
  - benchmark_id: mmlu_high_school_chemistry
    model_id_as_evaluated: google/gemma-2b
    score: 40.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_high_school_chemistry#deda7e0d8a82
  - benchmark_id: mmlu_high_school_computer_science
    model_id_as_evaluated: google/gemma-2b
    score: 42.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_high_school_computer_science#f1962f566bb4
  - benchmark_id: mmlu_high_school_european_history
    model_id_as_evaluated: google/gemma-2b
    score: 41.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_high_school_european_history#21d7d76408da
  - benchmark_id: mmlu_high_school_geography
    model_id_as_evaluated: google/gemma-2b
    score: 50.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_high_school_geography#c5b775abf4d2
  - benchmark_id: mmlu_high_school_government_and_politics
    model_id_as_evaluated: google/gemma-2b
    score: 59.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_high_school_government_and_politics#f7ae75afe886
  - benchmark_id: mmlu_high_school_macroeconomics
    model_id_as_evaluated: google/gemma-2b
    score: 41.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_high_school_macroeconomics#6a7cb518b258
  - benchmark_id: mmlu_high_school_mathematics
    model_id_as_evaluated: google/gemma-2b
    score: 25.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_high_school_mathematics#01e2e1cca70b
  - benchmark_id: mmlu_high_school_microeconomics
    model_id_as_evaluated: google/gemma-2b
    score: 38.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_high_school_microeconomics#98bcc04b0f65
  - benchmark_id: mmlu_high_school_physics
    model_id_as_evaluated: google/gemma-2b
    score: 25.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_high_school_physics#297ab031e6f4
  - benchmark_id: mmlu_high_school_psychology
    model_id_as_evaluated: google/gemma-2b
    score: 57.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_high_school_psychology#9f4642e04609
  - benchmark_id: mmlu_high_school_statistics
    model_id_as_evaluated: google/gemma-2b
    score: 35.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_high_school_statistics#f9d0ea411bc0
  - benchmark_id: mmlu_high_school_us_history
    model_id_as_evaluated: google/gemma-2b
    score: 44.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_high_school_us_history#13a4ee329884
  - benchmark_id: mmlu_high_school_world_history
    model_id_as_evaluated: google/gemma-2b
    score: 39.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_high_school_world_history#702fca7e018c
  - benchmark_id: mmlu_human_aging
    model_id_as_evaluated: google/gemma-2b
    score: 44.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_human_aging#17d5d397806a
  - benchmark_id: mmlu_human_sexuality
    model_id_as_evaluated: google/gemma-2b
    score: 45.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_human_sexuality#fe8569eab22d
  - benchmark_id: mmlu_international_law
    model_id_as_evaluated: google/gemma-2b
    score: 61.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_international_law#be17f8b79d39
  - benchmark_id: mmlu_jurisprudence
    model_id_as_evaluated: google/gemma-2b
    score: 41.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_jurisprudence#1e1c91e5a8ff
  - benchmark_id: mmlu_logical_fallacies
    model_id_as_evaluated: google/gemma-2b
    score: 41.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_logical_fallacies#ab37a9e97106
  - benchmark_id: mmlu_machine_learning
    model_id_as_evaluated: google/gemma-2b
    score: 39.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_machine_learning#c310b95d7696
  - benchmark_id: mmlu_management
    model_id_as_evaluated: google/gemma-2b
    score: 56.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_management#14fb500cdf2f
  - benchmark_id: mmlu_marketing
    model_id_as_evaluated: google/gemma-2b
    score: 60.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_marketing#53db472c3c54
  - benchmark_id: mmlu_medical_genetics
    model_id_as_evaluated: google/gemma-2b
    score: 43.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_medical_genetics#c00663b8c18e
  - benchmark_id: mmlu_miscellaneous
    model_id_as_evaluated: google/gemma-2b
    score: 54.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_miscellaneous#0b0b51a1aeb4
  - benchmark_id: mmlu_moral_disputes
    model_id_as_evaluated: google/gemma-2b
    score: 43.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_moral_disputes#3dae82b142f1
  - benchmark_id: mmlu_moral_scenarios
    model_id_as_evaluated: google/gemma-2b
    score: 23.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_moral_scenarios#855c2201d9d8
  - benchmark_id: mmlu_nutrition
    model_id_as_evaluated: google/gemma-2b
    score: 46.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_nutrition#aeb7fba90536
  - benchmark_id: mmlu_philosophy
    model_id_as_evaluated: google/gemma-2b
    score: 41.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_philosophy#940d01b71ff2
  - benchmark_id: mmlu_prehistory
    model_id_as_evaluated: google/gemma-2b
    score: 46.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_prehistory#46288a9493ab
  - benchmark_id: mmlu_pro
    model_id_as_evaluated: google/gemma-2b
    score: 13.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/google/gemma-2b/results_2024-10-24T00-00-00.000000.json
    source_kind: benchmark_author
    evidence_date: '2024-06-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v2-5eb856752837
      snapshot_ref: sha256:d31d6dfd0ffc88d90f12e55878abb22f162f8018390391134f3677835ffe48c6
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_pro#653b61dd03fa
  - benchmark_id: mmlu_professional_accounting
    model_id_as_evaluated: google/gemma-2b
    score: 34.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_professional_accounting#f2d57d713cb1
  - benchmark_id: mmlu_professional_law
    model_id_as_evaluated: google/gemma-2b
    score: 34.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_professional_law#b2796be26450
  - benchmark_id: mmlu_professional_medicine
    model_id_as_evaluated: google/gemma-2b
    score: 35.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_professional_medicine#9bf4f0d75752
  - benchmark_id: mmlu_professional_psychology
    model_id_as_evaluated: google/gemma-2b
    score: 37.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_professional_psychology#b24641eeb7f1
  - benchmark_id: mmlu_public_relations
    model_id_as_evaluated: google/gemma-2b
    score: 47.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_public_relations#a3de438a3550
  - benchmark_id: mmlu_security_studies
    model_id_as_evaluated: google/gemma-2b
    score: 46.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_security_studies#ade38e82bf1d
  - benchmark_id: mmlu_sociology
    model_id_as_evaluated: google/gemma-2b
    score: 42.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_sociology#cff98ae12a0c
  - benchmark_id: mmlu_us_foreign_policy
    model_id_as_evaluated: google/gemma-2b
    score: 57.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_us_foreign_policy#6a4b7eec8b71
  - benchmark_id: mmlu_virology
    model_id_as_evaluated: google/gemma-2b
    score: 44.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_virology#e8a7f2e12a35
  - benchmark_id: mmlu_world_religions
    model_id_as_evaluated: google/gemma-2b
    score: 54.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#mmlu_world_religions#61b5adbbc330
  - benchmark_id: musr
    model_id_as_evaluated: google/gemma-2b
    score: 39.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/google/gemma-2b/results_2024-10-24T00-00-00.000000.json
    source_kind: benchmark_author
    evidence_date: '2024-06-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v2-5eb856752837
      snapshot_ref: sha256:d31d6dfd0ffc88d90f12e55878abb22f162f8018390391134f3677835ffe48c6
      cited_regions:
      - rows
    id: google/gemma-2b#musr#736528dd81a8
  - benchmark_id: truthfulqa
    model_id_as_evaluated: google/gemma-2b
    score: 33.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#truthfulqa#b4748af428e9
  - benchmark_id: winogrande
    model_id_as_evaluated: google/gemma-2b
    score: 66.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b/results_2024-02-22T14-01-00.018926.json
    source_kind: benchmark_author
    evidence_date: '2024-02-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-2b8faa8a1145
      snapshot_ref: sha256:3e0dbf64b434fbb449720cb33e11932cd2142ba445624b57edc91db985e4e2d9
      cited_regions:
      - rows
    id: google/gemma-2b#winogrande#c293b8b0fcb7
  benchmark_source: open-llm-leaderboard-v1, open-llm-leaderboard-v2
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
    gguf: true
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
  huggingface_downloads: 163231
  huggingface_likes: 1155
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
  huggingface_url: https://huggingface.co/google/gemma-2b
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
card_schema_version: '3.0'
card_author: huggingface-seeder
card_created: '2026-04-05'
card_updated: '2026-04-05'
---


# gemma 2B

Auto-generated from HuggingFace Hub metadata for [google/gemma-2b](https://huggingface.co/google/gemma-2b).