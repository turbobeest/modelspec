---
model_id: meta/meta-llama-3-70b-instruct
display_name: Meta Llama 3 70B Instruct
provider: meta
provider_display: Meta
family: llama
version: ''
release_date: '2024-04-17'
last_updated: ''
status: active
model_type: llm-chat
model_subtypes: []
tags:
- text-generation
pipeline_tag: text-generation
architecture:
  type: null
  total_parameters: 70553706496
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
  base_model: meta-llama/Meta-Llama-3-70B
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
  license_type: llama-community
  license_url: https://raw.githubusercontent.com/meta-llama/llama3/main/LICENSE
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
    model_id: meta-llama/Meta-Llama-3-70B-Instruct
    url: https://huggingface.co/meta-llama/Meta-Llama-3-70B-Instruct
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
    mgsm: 91.1
    gsm8k: 95.0
  evidence:
  - benchmark_id: gpqa_diamond
    model_id_as_evaluated: Meta-Llama-3-70B-Instruct
    score: 40.56
    unit: percent
    source_url: https://epoch.ai/benchmarks/gpqa-diamond
    source_kind: independent_evaluator
    evidence_date: '2025-01-27'
    date_type: evaluated
    verified_at: '2026-09-24'
    benchmark_version: GPQA Diamond (Epoch AI run)
    configuration: Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (gpqa_diamond.csv),
      read 2026-09-24. Run started 2025-01-27T00:00:00.000Z; effort default; highest-effort
      run for the model (MODEL-123 max-effort rule), newest on a tie. Standard error 2.62 points.
    limitations: Epoch AI data, CC BY 4.0.
  - benchmark_id: arc_challenge
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 71.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#arc_challenge#1f50498cc3aa
  - benchmark_id: bbh
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 65.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/meta-llama/Meta-Llama-3-70B-Instruct/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-299b7321e950
      snapshot_ref: sha256:f23bfb727a9d38f713ea3326cbcf3e11c5bca79fbec8a20a0d4ce552419d91b7
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#bbh#cecb15fdd71c
  - benchmark_id: gpqa_pooled
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 28.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/meta-llama/Meta-Llama-3-70B-Instruct/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-299b7321e950
      snapshot_ref: sha256:f23bfb727a9d38f713ea3326cbcf3e11c5bca79fbec8a20a0d4ce552419d91b7
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#gpqa_pooled#383c91d3984b
  - benchmark_id: hellaswag
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 85.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#hellaswag#95610991b4d8
  - benchmark_id: ifeval
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 81.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/meta-llama/Meta-Llama-3-70B-Instruct/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-299b7321e950
      snapshot_ref: sha256:f23bfb727a9d38f713ea3326cbcf3e11c5bca79fbec8a20a0d4ce552419d91b7
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#ifeval#49888a10adec
  - benchmark_id: math_lvl5
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 24.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/meta-llama/Meta-Llama-3-70B-Instruct/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-299b7321e950
      snapshot_ref: sha256:f23bfb727a9d38f713ea3326cbcf3e11c5bca79fbec8a20a0d4ce552419d91b7
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#math_lvl5#ceed84f8fe37
  - benchmark_id: mmlu_abstract_algebra
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 51.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_abstract_algebra#66e9987b7448
  - benchmark_id: mmlu_anatomy
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 77.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_anatomy#9de5c9685d84
  - benchmark_id: mmlu_astronomy
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 93.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_astronomy#ed1539f6d540
  - benchmark_id: mmlu_business_ethics
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 86.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_business_ethics#44d30a7830e0
  - benchmark_id: mmlu_clinical_knowledge
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 86.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_clinical_knowledge#59a229755f6e
  - benchmark_id: mmlu_college_biology
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 91.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_college_biology#68c9a002de9a
  - benchmark_id: mmlu_college_chemistry
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 56.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_college_chemistry#5ea3e15ae76d
  - benchmark_id: mmlu_college_computer_science
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 69.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_college_computer_science#9c3b12603c5d
  - benchmark_id: mmlu_college_mathematics
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 58.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_college_mathematics#51ce098407c7
  - benchmark_id: mmlu_college_medicine
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 81.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_college_medicine#f7ba4e7f2ed0
  - benchmark_id: mmlu_college_physics
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 59.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_college_physics#7c0c606ea21c
  - benchmark_id: mmlu_computer_security
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 82.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_computer_security#aa6d04b113fd
  - benchmark_id: mmlu_conceptual_physics
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 81.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_conceptual_physics#50fd10700789
  - benchmark_id: mmlu_econometrics
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 72.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_econometrics#6382a1d64f51
  - benchmark_id: mmlu_electrical_engineering
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 77.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_electrical_engineering#2720ef6c0436
  - benchmark_id: mmlu_elementary_mathematics
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 70.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_elementary_mathematics#2e9e169f076a
  - benchmark_id: mmlu_formal_logic
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 62.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_formal_logic#e7b765dacf33
  - benchmark_id: mmlu_global_facts
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 59.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_global_facts#3fda6396bce7
  - benchmark_id: mmlu_high_school_biology
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 89.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_high_school_biology#8616cefaf868
  - benchmark_id: mmlu_high_school_chemistry
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 69.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_high_school_chemistry#61da446e831c
  - benchmark_id: mmlu_high_school_computer_science
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 92.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_high_school_computer_science#7b6fb360f4ea
  - benchmark_id: mmlu_high_school_european_history
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 86.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_high_school_european_history#e5d2c0296f5a
  - benchmark_id: mmlu_high_school_geography
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 92.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_high_school_geography#92ea525d4212
  - benchmark_id: mmlu_high_school_government_and_politics
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 98.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_high_school_government_and_politics#e1c8ffc5185e
  - benchmark_id: mmlu_high_school_macroeconomics
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 83.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_high_school_macroeconomics#bce5e0b31621
  - benchmark_id: mmlu_high_school_mathematics
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 54.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_high_school_mathematics#a83dd9797acb
  - benchmark_id: mmlu_high_school_microeconomics
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 88.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_high_school_microeconomics#1d93f79a8a89
  - benchmark_id: mmlu_high_school_physics
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 62.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_high_school_physics#73a683a4e60b
  - benchmark_id: mmlu_high_school_psychology
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 94.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_high_school_psychology#56251d8e1496
  - benchmark_id: mmlu_high_school_statistics
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 73.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_high_school_statistics#b23f534f852a
  - benchmark_id: mmlu_high_school_us_history
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 92.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_high_school_us_history#1cab91f93540
  - benchmark_id: mmlu_high_school_world_history
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 92.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_high_school_world_history#8cc97c47b3ff
  - benchmark_id: mmlu_human_aging
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 82.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_human_aging#5a8744278098
  - benchmark_id: mmlu_human_sexuality
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 87.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_human_sexuality#459804f92cb3
  - benchmark_id: mmlu_international_law
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 92.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_international_law#90af19d64ae4
  - benchmark_id: mmlu_jurisprudence
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 88.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_jurisprudence#4a300d47d6c7
  - benchmark_id: mmlu_logical_fallacies
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 85.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_logical_fallacies#1031bb75b598
  - benchmark_id: mmlu_machine_learning
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 70.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_machine_learning#6b8f5137c24f
  - benchmark_id: mmlu_management
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 89.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_management#823af881dfed
  - benchmark_id: mmlu_marketing
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 93.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_marketing#b9638d58cac9
  - benchmark_id: mmlu_medical_genetics
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 92.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_medical_genetics#93594119d946
  - benchmark_id: mmlu_miscellaneous
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 91.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_miscellaneous#73b79460e6b3
  - benchmark_id: mmlu_moral_disputes
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 84.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_moral_disputes#3388f30f280a
  - benchmark_id: mmlu_moral_scenarios
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 70.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_moral_scenarios#f692834edc26
  - benchmark_id: mmlu_nutrition
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 87.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_nutrition#e5d5010dd54c
  - benchmark_id: mmlu_philosophy
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 81.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_philosophy#b1c0f73bb6bd
  - benchmark_id: mmlu_prehistory
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 90.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_prehistory#6510bb8285c8
  - benchmark_id: mmlu_pro
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 52.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/meta-llama/Meta-Llama-3-70B-Instruct/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-299b7321e950
      snapshot_ref: sha256:f23bfb727a9d38f713ea3326cbcf3e11c5bca79fbec8a20a0d4ce552419d91b7
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_pro#61668c27e740
  - benchmark_id: mmlu_professional_accounting
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 63.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_professional_accounting#c30e9617176a
  - benchmark_id: mmlu_professional_law
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 64.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_professional_law#d50081b856f5
  - benchmark_id: mmlu_professional_medicine
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 89.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_professional_medicine#2491aa4be7a1
  - benchmark_id: mmlu_professional_psychology
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 85.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_professional_psychology#bcabac13a552
  - benchmark_id: mmlu_public_relations
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 74.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_public_relations#63e46bc74e28
  - benchmark_id: mmlu_security_studies
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 81.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_security_studies#c3f85ed61818
  - benchmark_id: mmlu_sociology
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 92.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_sociology#50c58cb3c47b
  - benchmark_id: mmlu_us_foreign_policy
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 92.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_us_foreign_policy#de143ee0e21d
  - benchmark_id: mmlu_virology
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 56.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_virology#253cd3dfc736
  - benchmark_id: mmlu_world_religions
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 90.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#mmlu_world_religions#ffc2059c5549
  - benchmark_id: musr
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 41.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/meta-llama/Meta-Llama-3-70B-Instruct/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-18'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-299b7321e950
      snapshot_ref: sha256:f23bfb727a9d38f713ea3326cbcf3e11c5bca79fbec8a20a0d4ce552419d91b7
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#musr#37718fb2660b
  - benchmark_id: truthfulqa
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 61.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#truthfulqa#af24f788bdc6
  - benchmark_id: winogrande
    model_id_as_evaluated: meta-llama/Meta-Llama-3-70B-Instruct
    score: 82.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-70B-Instruct/results_2024-04-21T11-59-48.701689.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-21'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-49d1fef96000
      snapshot_ref: sha256:18210012b447715332eeaf2092c996410cc45f788a4d2527f4cba011db3ebc50
      cited_regions:
      - rows
    id: meta/meta-llama-3-70b-instruct#winogrande#bddae5762a06
  benchmark_source: llm-stats, open-llm-leaderboard-v1, open-llm-leaderboard-v2
  benchmark_as_of: 2026-04
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
  huggingface_downloads: 72691
  huggingface_likes: 1507
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
  huggingface_url: https://huggingface.co/meta-llama/Meta-Llama-3-70B-Instruct
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


# Meta Llama 3 70B Instruct

Auto-generated from HuggingFace Hub metadata for [meta-llama/Meta-Llama-3-70B-Instruct](https://huggingface.co/meta-llama/Meta-Llama-3-70B-Instruct).

Licence: llama-community. Creator distribution https://raw.githubusercontent.com/meta-llama/llama3/main/LICENSE (Meta Llama 3 Community License Agreement) and Hub cardData.license llama3, read 2026-09-18.
