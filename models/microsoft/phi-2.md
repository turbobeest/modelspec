---
model_id: microsoft/phi-2
display_name: phi 2
provider: microsoft
provider_display: Microsoft
family: phi
version: ''
release_date: '2023-12-13'
last_updated: ''
status: active
model_type: llm-code
model_subtypes: []
tags:
- text-generation
pipeline_tag: text-generation
architecture:
  type: null
  total_parameters: 2779683840
  active_parameters: null
  num_experts: null
  experts_per_token: null
  num_layers: 32
  hidden_size: 2560
  intermediate_size: 10240
  attention_type: null
  num_attention_heads: 32
  num_kv_heads: 32
  positional_encoding: null
  rope_theta: null
  vocab_size: 51200
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
  license_type: mit
  license_url: https://huggingface.co/microsoft/phi-2/raw/main/LICENSE
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
    context_window: 2048
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
    model_id: microsoft/phi-2
    url: https://huggingface.co/microsoft/phi-2
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
    model_id_as_evaluated: microsoft/phi-2
    score: 61.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#arc_challenge#75fd273b536d
  - benchmark_id: bbh
    model_id_as_evaluated: microsoft/phi-2
    score: 48.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/microsoft/phi-2/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-17'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-9111785434bf
      snapshot_ref: sha256:aa2ee9567298b96595c08d559288b5d02eff34671741f2aec611d59a9f3fc882
      cited_regions:
      - rows
    id: microsoft/phi-2#bbh#13001dbbb423
  - benchmark_id: gpqa_pooled
    model_id_as_evaluated: microsoft/phi-2
    score: 27.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/microsoft/phi-2/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-17'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-9111785434bf
      snapshot_ref: sha256:aa2ee9567298b96595c08d559288b5d02eff34671741f2aec611d59a9f3fc882
      cited_regions:
      - rows
    id: microsoft/phi-2#gpqa_pooled#3ed41bc6a772
  - benchmark_id: gsm8k
    model_id_as_evaluated: microsoft/phi-2
    score: 55.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#gsm8k#1aaf9b0a9591
  - benchmark_id: hellaswag
    model_id_as_evaluated: microsoft/phi-2
    score: 74.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#hellaswag#50d621d70198
  - benchmark_id: ifeval
    model_id_as_evaluated: microsoft/phi-2
    score: 27.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/microsoft/phi-2/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-17'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-9111785434bf
      snapshot_ref: sha256:aa2ee9567298b96595c08d559288b5d02eff34671741f2aec611d59a9f3fc882
      cited_regions:
      - rows
    id: microsoft/phi-2#ifeval#cef9fc120774
  - benchmark_id: math_lvl5
    model_id_as_evaluated: microsoft/phi-2
    score: 2.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/microsoft/phi-2/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-17'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-9111785434bf
      snapshot_ref: sha256:aa2ee9567298b96595c08d559288b5d02eff34671741f2aec611d59a9f3fc882
      cited_regions:
      - rows
    id: microsoft/phi-2#math_lvl5#190bcb79a836
  - benchmark_id: mmlu_abstract_algebra
    model_id_as_evaluated: microsoft/phi-2
    score: 29.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_abstract_algebra#bdc5ec81529c
  - benchmark_id: mmlu_anatomy
    model_id_as_evaluated: microsoft/phi-2
    score: 44.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_anatomy#40fb6f887f46
  - benchmark_id: mmlu_astronomy
    model_id_as_evaluated: microsoft/phi-2
    score: 58.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_astronomy#339a9c2234dd
  - benchmark_id: mmlu_business_ethics
    model_id_as_evaluated: microsoft/phi-2
    score: 56.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_business_ethics#42798b4737c4
  - benchmark_id: mmlu_clinical_knowledge
    model_id_as_evaluated: microsoft/phi-2
    score: 60.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_clinical_knowledge#7ef956502313
  - benchmark_id: mmlu_college_biology
    model_id_as_evaluated: microsoft/phi-2
    score: 66.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_college_biology#13c84401e8ac
  - benchmark_id: mmlu_college_chemistry
    model_id_as_evaluated: microsoft/phi-2
    score: 40.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_college_chemistry#5e54eb828f42
  - benchmark_id: mmlu_college_computer_science
    model_id_as_evaluated: microsoft/phi-2
    score: 41.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_college_computer_science#96e8ffbad996
  - benchmark_id: mmlu_college_mathematics
    model_id_as_evaluated: microsoft/phi-2
    score: 38.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_college_mathematics#098c3b413b82
  - benchmark_id: mmlu_college_medicine
    model_id_as_evaluated: microsoft/phi-2
    score: 59.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_college_medicine#b03469b73aec
  - benchmark_id: mmlu_college_physics
    model_id_as_evaluated: microsoft/phi-2
    score: 37.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_college_physics#c30142a06b34
  - benchmark_id: mmlu_computer_security
    model_id_as_evaluated: microsoft/phi-2
    score: 74.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_computer_security#03bd4b5ab8ef
  - benchmark_id: mmlu_conceptual_physics
    model_id_as_evaluated: microsoft/phi-2
    score: 52.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_conceptual_physics#2622ed8decc7
  - benchmark_id: mmlu_econometrics
    model_id_as_evaluated: microsoft/phi-2
    score: 38.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_econometrics#763a18b0f135
  - benchmark_id: mmlu_electrical_engineering
    model_id_as_evaluated: microsoft/phi-2
    score: 55.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_electrical_engineering#bcd63b7845b3
  - benchmark_id: mmlu_elementary_mathematics
    model_id_as_evaluated: microsoft/phi-2
    score: 46.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_elementary_mathematics#0a94f41d9f67
  - benchmark_id: mmlu_formal_logic
    model_id_as_evaluated: microsoft/phi-2
    score: 35.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_formal_logic#bc1f1337064c
  - benchmark_id: mmlu_global_facts
    model_id_as_evaluated: microsoft/phi-2
    score: 38.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_global_facts#f4b098717f9c
  - benchmark_id: mmlu_high_school_biology
    model_id_as_evaluated: microsoft/phi-2
    score: 67.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_high_school_biology#32df13576a3b
  - benchmark_id: mmlu_high_school_chemistry
    model_id_as_evaluated: microsoft/phi-2
    score: 47.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_high_school_chemistry#0491ba0c28b4
  - benchmark_id: mmlu_high_school_computer_science
    model_id_as_evaluated: microsoft/phi-2
    score: 64.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_high_school_computer_science#a4f339793588
  - benchmark_id: mmlu_high_school_european_history
    model_id_as_evaluated: microsoft/phi-2
    score: 64.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_high_school_european_history#41a03e3efc19
  - benchmark_id: mmlu_high_school_geography
    model_id_as_evaluated: microsoft/phi-2
    score: 75.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_high_school_geography#f254f352d04f
  - benchmark_id: mmlu_high_school_government_and_politics
    model_id_as_evaluated: microsoft/phi-2
    score: 80.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_high_school_government_and_politics#09cd542db2ba
  - benchmark_id: mmlu_high_school_macroeconomics
    model_id_as_evaluated: microsoft/phi-2
    score: 58.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_high_school_macroeconomics#f23842c9c2a3
  - benchmark_id: mmlu_high_school_mathematics
    model_id_as_evaluated: microsoft/phi-2
    score: 33.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_high_school_mathematics#8b2d6ae15ea9
  - benchmark_id: mmlu_high_school_microeconomics
    model_id_as_evaluated: microsoft/phi-2
    score: 62.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_high_school_microeconomics#f71a16e804fa
  - benchmark_id: mmlu_high_school_physics
    model_id_as_evaluated: microsoft/phi-2
    score: 38.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_high_school_physics#431b9e239118
  - benchmark_id: mmlu_high_school_psychology
    model_id_as_evaluated: microsoft/phi-2
    score: 79.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_high_school_psychology#8d2ad70be466
  - benchmark_id: mmlu_high_school_statistics
    model_id_as_evaluated: microsoft/phi-2
    score: 47.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_high_school_statistics#5999283d389a
  - benchmark_id: mmlu_high_school_us_history
    model_id_as_evaluated: microsoft/phi-2
    score: 66.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_high_school_us_history#d062596a6a8f
  - benchmark_id: mmlu_high_school_world_history
    model_id_as_evaluated: microsoft/phi-2
    score: 74.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_high_school_world_history#8e12bb7cdae2
  - benchmark_id: mmlu_human_aging
    model_id_as_evaluated: microsoft/phi-2
    score: 65.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_human_aging#26c9284a60f3
  - benchmark_id: mmlu_human_sexuality
    model_id_as_evaluated: microsoft/phi-2
    score: 70.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_human_sexuality#b35cbec9eff5
  - benchmark_id: mmlu_international_law
    model_id_as_evaluated: microsoft/phi-2
    score: 72.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_international_law#5d70a5d58e4b
  - benchmark_id: mmlu_jurisprudence
    model_id_as_evaluated: microsoft/phi-2
    score: 73.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_jurisprudence#cc14c93a5a10
  - benchmark_id: mmlu_logical_fallacies
    model_id_as_evaluated: microsoft/phi-2
    score: 73.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_logical_fallacies#7a69026b6c62
  - benchmark_id: mmlu_machine_learning
    model_id_as_evaluated: microsoft/phi-2
    score: 48.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_machine_learning#229d6c689eea
  - benchmark_id: mmlu_management
    model_id_as_evaluated: microsoft/phi-2
    score: 70.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_management#20468af7df03
  - benchmark_id: mmlu_marketing
    model_id_as_evaluated: microsoft/phi-2
    score: 82.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_marketing#75c7755012fd
  - benchmark_id: mmlu_medical_genetics
    model_id_as_evaluated: microsoft/phi-2
    score: 64.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_medical_genetics#6d8c2b6a3b2c
  - benchmark_id: mmlu_miscellaneous
    model_id_as_evaluated: microsoft/phi-2
    score: 69.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_miscellaneous#ef63a6d8eb35
  - benchmark_id: mmlu_moral_disputes
    model_id_as_evaluated: microsoft/phi-2
    score: 66.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_moral_disputes#339c55d7f6a9
  - benchmark_id: mmlu_moral_scenarios
    model_id_as_evaluated: microsoft/phi-2
    score: 29.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_moral_scenarios#f349ac1c61de
  - benchmark_id: mmlu_nutrition
    model_id_as_evaluated: microsoft/phi-2
    score: 62.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_nutrition#b4ce490195e3
  - benchmark_id: mmlu_philosophy
    model_id_as_evaluated: microsoft/phi-2
    score: 62.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_philosophy#6f0e6c8f9aa0
  - benchmark_id: mmlu_prehistory
    model_id_as_evaluated: microsoft/phi-2
    score: 62.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_prehistory#a800e013bbab
  - benchmark_id: mmlu_pro
    model_id_as_evaluated: microsoft/phi-2
    score: 26.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/microsoft/phi-2/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-17'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-9111785434bf
      snapshot_ref: sha256:aa2ee9567298b96595c08d559288b5d02eff34671741f2aec611d59a9f3fc882
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_pro#7c19c7a926e3
  - benchmark_id: mmlu_professional_accounting
    model_id_as_evaluated: microsoft/phi-2
    score: 44.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_professional_accounting#1f3d95fed6ce
  - benchmark_id: mmlu_professional_law
    model_id_as_evaluated: microsoft/phi-2
    score: 43.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_professional_law#7e0d5feac5f5
  - benchmark_id: mmlu_professional_medicine
    model_id_as_evaluated: microsoft/phi-2
    score: 48.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_professional_medicine#e02e8817dbb7
  - benchmark_id: mmlu_professional_psychology
    model_id_as_evaluated: microsoft/phi-2
    score: 56.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_professional_psychology#7bda93eb0de0
  - benchmark_id: mmlu_public_relations
    model_id_as_evaluated: microsoft/phi-2
    score: 62.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_public_relations#4baa047aa99d
  - benchmark_id: mmlu_security_studies
    model_id_as_evaluated: microsoft/phi-2
    score: 71.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_security_studies#e2bde27de0cb
  - benchmark_id: mmlu_sociology
    model_id_as_evaluated: microsoft/phi-2
    score: 80.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_sociology#8cc45b0fd513
  - benchmark_id: mmlu_us_foreign_policy
    model_id_as_evaluated: microsoft/phi-2
    score: 77.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_us_foreign_policy#4b83bbb9ac9f
  - benchmark_id: mmlu_virology
    model_id_as_evaluated: microsoft/phi-2
    score: 47.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_virology#14e1b03a5eda
  - benchmark_id: mmlu_world_religions
    model_id_as_evaluated: microsoft/phi-2
    score: 69.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#mmlu_world_religions#7a2be64cd2fe
  - benchmark_id: musr
    model_id_as_evaluated: microsoft/phi-2
    score: 41.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/microsoft/phi-2/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-17'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-9111785434bf
      snapshot_ref: sha256:aa2ee9567298b96595c08d559288b5d02eff34671741f2aec611d59a9f3fc882
      cited_regions:
      - rows
    id: microsoft/phi-2#musr#c7b05f5c1864
  - benchmark_id: truthfulqa
    model_id_as_evaluated: microsoft/phi-2
    score: 44.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#truthfulqa#2d35932ef508
  - benchmark_id: winogrande
    model_id_as_evaluated: microsoft/phi-2
    score: 73.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/phi-2/results_2024-04-15T16-12-26.100927.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-15'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-4c6c85818b06
      snapshot_ref: sha256:f64b6234cbace292aa5d9d0c9c267f3e00f702645615241cce8ea80d9073e53b
      cited_regions:
      - rows
    id: microsoft/phi-2#winogrande#46dcc10e49b0
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
  huggingface_downloads: 1527071
  huggingface_likes: 3441
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
  huggingface_url: https://huggingface.co/microsoft/phi-2
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

# phi 2

Auto-generated from HuggingFace Hub metadata for [microsoft/phi-2](https://huggingface.co/microsoft/phi-2).

Licence: mit. Creator LICENSE file https://huggingface.co/microsoft/phi-2/raw/main/LICENSE (MIT License) and Hub cardData.license mit, read 2026-09-18.
