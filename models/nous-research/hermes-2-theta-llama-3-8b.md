---
model_id: nous-research/hermes-2-theta-llama-3-8b
display_name: Hermes 2 Theta Llama 3 8B
provider: nous-research
provider_display: Nous Research
family: llama
version: ''
release_date: '2024-05-05'
last_updated: ''
status: active
model_type: llm-chat
model_subtypes: []
tags:
- text-generation
pipeline_tag: text-generation
architecture:
  type: null
  total_parameters: 8030261248
  active_parameters: null
  num_experts: null
  experts_per_token: null
  num_layers: 32
  hidden_size: 4096
  intermediate_size: 14336
  attention_type: null
  num_attention_heads: 32
  num_kv_heads: 8
  positional_encoding: null
  rope_theta: null
  vocab_size: 128256
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
  base_model: NousResearch/Hermes-2-Pro-Llama-3-8B
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
  origin_org_type: open-collective
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
    model_id: NousResearch/Hermes-2-Theta-Llama-3-8B
    url: https://huggingface.co/NousResearch/Hermes-2-Theta-Llama-3-8B
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
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 63.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#arc_challenge#14a28085a336
  - benchmark_id: bbh
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 52.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2025-02-13T18-27-04.338360.json
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
    - source_id: oll-v2-64afe26e8540
      snapshot_ref: sha256:e57b911e9ead5396ccdc52491261852e76dc803965bcb9f101e020d695fbfeb5
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#bbh#084e64cd0cdf
  - benchmark_id: gpqa_pooled
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 30.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2025-02-13T18-27-04.338360.json
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
    - source_id: oll-v2-64afe26e8540
      snapshot_ref: sha256:e57b911e9ead5396ccdc52491261852e76dc803965bcb9f101e020d695fbfeb5
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#gpqa_pooled#cdd43416ef53
  - benchmark_id: gsm8k
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 70.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#gsm8k#9d6b66d016fe
  - benchmark_id: hellaswag
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 82.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#hellaswag#2e28ca81e44f
  - benchmark_id: ifeval
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 65.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2025-02-13T18-27-04.338360.json
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
    - source_id: oll-v2-64afe26e8540
      snapshot_ref: sha256:e57b911e9ead5396ccdc52491261852e76dc803965bcb9f101e020d695fbfeb5
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#ifeval#d085f391734e
  - benchmark_id: math_lvl5
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 9.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2025-02-13T18-27-04.338360.json
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
    - source_id: oll-v2-64afe26e8540
      snapshot_ref: sha256:e57b911e9ead5396ccdc52491261852e76dc803965bcb9f101e020d695fbfeb5
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#math_lvl5#af7cf4af9f78
  - benchmark_id: mmlu_abstract_algebra
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 38.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_abstract_algebra#93ecbd18ee75
  - benchmark_id: mmlu_anatomy
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 63.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_anatomy#b0189f0e926f
  - benchmark_id: mmlu_astronomy
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 69.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_astronomy#3a47ca828ebf
  - benchmark_id: mmlu_business_ethics
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 64.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_business_ethics#19315f2cd6fd
  - benchmark_id: mmlu_clinical_knowledge
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 74.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_clinical_knowledge#26ef5f25cacd
  - benchmark_id: mmlu_college_biology
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 74.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_college_biology#d83e3dc0eb15
  - benchmark_id: mmlu_college_chemistry
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 48.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_college_chemistry#63b12e482b5b
  - benchmark_id: mmlu_college_computer_science
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 49.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_college_computer_science#09b0eb7fd753
  - benchmark_id: mmlu_college_mathematics
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 35.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_college_mathematics#bb0bb05b92c2
  - benchmark_id: mmlu_college_medicine
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 66.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_college_medicine#ffefbb2be68d
  - benchmark_id: mmlu_college_physics
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 48.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_college_physics#b20ad6090f99
  - benchmark_id: mmlu_computer_security
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 79.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_computer_security#0fbbc40930d5
  - benchmark_id: mmlu_conceptual_physics
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 55.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_conceptual_physics#f63b60966332
  - benchmark_id: mmlu_econometrics
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 55.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_econometrics#701bd3edfab2
  - benchmark_id: mmlu_electrical_engineering
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 61.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_electrical_engineering#0d88e4e0c828
  - benchmark_id: mmlu_elementary_mathematics
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 45.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_elementary_mathematics#a8dba73ee026
  - benchmark_id: mmlu_formal_logic
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 48.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_formal_logic#b0809976e606
  - benchmark_id: mmlu_global_facts
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 39.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_global_facts#3620f2ec8cf0
  - benchmark_id: mmlu_high_school_biology
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 81.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_high_school_biology#9b7b4b6220d5
  - benchmark_id: mmlu_high_school_chemistry
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 51.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_high_school_chemistry#0b9934e1e4d1
  - benchmark_id: mmlu_high_school_computer_science
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 70.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_high_school_computer_science#729d69de285d
  - benchmark_id: mmlu_high_school_european_history
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 75.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_high_school_european_history#00b7eafce009
  - benchmark_id: mmlu_high_school_geography
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 81.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_high_school_geography#133539984545
  - benchmark_id: mmlu_high_school_government_and_politics
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 88.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_high_school_government_and_politics#d5205eebad3b
  - benchmark_id: mmlu_high_school_macroeconomics
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 65.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_high_school_macroeconomics#48033e6bbe67
  - benchmark_id: mmlu_high_school_mathematics
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 38.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_high_school_mathematics#24a09f07c299
  - benchmark_id: mmlu_high_school_microeconomics
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 75.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_high_school_microeconomics#5b66b46bbb88
  - benchmark_id: mmlu_high_school_physics
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 45.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_high_school_physics#c7684a84bf6e
  - benchmark_id: mmlu_high_school_psychology
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 83.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_high_school_psychology#b3ae1a1c7a5c
  - benchmark_id: mmlu_high_school_statistics
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 50.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_high_school_statistics#b34eeab2b3cb
  - benchmark_id: mmlu_high_school_us_history
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 83.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_high_school_us_history#f2c9af9d38f0
  - benchmark_id: mmlu_high_school_world_history
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 86.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_high_school_world_history#7f0d5876beea
  - benchmark_id: mmlu_human_aging
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 72.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_human_aging#6ea39e489202
  - benchmark_id: mmlu_human_sexuality
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 80.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_human_sexuality#5df66bed1a8d
  - benchmark_id: mmlu_international_law
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 78.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_international_law#9eaebe464f76
  - benchmark_id: mmlu_jurisprudence
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 75.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_jurisprudence#9832ed4a8453
  - benchmark_id: mmlu_logical_fallacies
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 73.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_logical_fallacies#85cfbe457fd8
  - benchmark_id: mmlu_machine_learning
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 55.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_machine_learning#8e300b3a03e0
  - benchmark_id: mmlu_management
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 80.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_management#94e3ec27b653
  - benchmark_id: mmlu_marketing
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 89.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_marketing#98fe6a5d758d
  - benchmark_id: mmlu_medical_genetics
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 79.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_medical_genetics#b0341fdcaa73
  - benchmark_id: mmlu_miscellaneous
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 84.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_miscellaneous#4ff8ca298e7f
  - benchmark_id: mmlu_moral_disputes
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 74.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_moral_disputes#e3b87f481432
  - benchmark_id: mmlu_moral_scenarios
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 43.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_moral_scenarios#7d4beb1d9875
  - benchmark_id: mmlu_nutrition
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 73.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_nutrition#b3b294dadc07
  - benchmark_id: mmlu_philosophy
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 73.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_philosophy#a5676f20fd3d
  - benchmark_id: mmlu_prehistory
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 73.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_prehistory#2c8fa4001622
  - benchmark_id: mmlu_pro
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 33.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2025-02-13T18-27-04.338360.json
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
    - source_id: oll-v2-64afe26e8540
      snapshot_ref: sha256:e57b911e9ead5396ccdc52491261852e76dc803965bcb9f101e020d695fbfeb5
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_pro#5a0eb0c5b901
  - benchmark_id: mmlu_professional_accounting
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 52.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_professional_accounting#c4aaed15f4d4
  - benchmark_id: mmlu_professional_law
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 48.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_professional_law#b5dbd819aa75
  - benchmark_id: mmlu_professional_medicine
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 69.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_professional_medicine#a58b214348ae
  - benchmark_id: mmlu_professional_psychology
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 70.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_professional_psychology#65654be3ecbd
  - benchmark_id: mmlu_public_relations
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 65.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_public_relations#d6a702bd82b3
  - benchmark_id: mmlu_security_studies
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 77.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_security_studies#5c7bf2a57541
  - benchmark_id: mmlu_sociology
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 87.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_sociology#b465456cdb84
  - benchmark_id: mmlu_us_foreign_policy
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 86.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_us_foreign_policy#bd91374a1096
  - benchmark_id: mmlu_virology
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 54.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_virology#8ede00267df5
  - benchmark_id: mmlu_world_religions
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 80.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#mmlu_world_religions#c691d3d0cc5b
  - benchmark_id: musr
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 39.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2025-02-13T18-27-04.338360.json
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
    - source_id: oll-v2-64afe26e8540
      snapshot_ref: sha256:e57b911e9ead5396ccdc52491261852e76dc803965bcb9f101e020d695fbfeb5
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#musr#e1c5339e29de
  - benchmark_id: truthfulqa
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 55.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#truthfulqa#1fa9b386abed
  - benchmark_id: winogrande
    model_id_as_evaluated: NousResearch/Hermes-2-Theta-Llama-3-8B
    score: 76.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json
    source_kind: benchmark_author
    evidence_date: '2024-05-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-62f123b1e8cb
      snapshot_ref: sha256:2cf2b11f40ef8b717807011139890b7cc5b06a0f0314bc84162e418bb10c6d82
      cited_regions:
      - rows
    id: nous-research/hermes-2-theta-llama-3-8b#winogrande#81ce544adf2f
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
  huggingface_downloads: 10350
  huggingface_likes: 204
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
  huggingface_url: https://huggingface.co/NousResearch/Hermes-2-Theta-Llama-3-8B
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


# Hermes 2 Theta Llama 3 8B

Auto-generated from HuggingFace Hub metadata for [NousResearch/Hermes-2-Theta-Llama-3-8B](https://huggingface.co/NousResearch/Hermes-2-Theta-Llama-3-8B).