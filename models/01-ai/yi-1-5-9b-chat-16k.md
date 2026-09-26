---
model_id: 01-ai/yi-1-5-9b-chat-16k
display_name: Yi 1.5 9B Chat 16K
provider: 01-ai
provider_display: 01.AI
family: yi
version: ''
release_date: '2024-05-15'
last_updated: ''
status: active
model_type: llm-chat
model_subtypes: []
tags:
- text-generation
pipeline_tag: text-generation
architecture:
  type: null
  total_parameters: 8829407232
  active_parameters: null
  num_experts: null
  experts_per_token: null
  num_layers: 48
  hidden_size: 4096
  intermediate_size: 11008
  attention_type: null
  num_attention_heads: 32
  num_kv_heads: 4
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
  license_type: apache-2.0
  license_url: https://huggingface.co/01-ai/Yi-1.5-9B-Chat-16K/raw/main/README.md
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
  input: 0.15
  output: 0.15
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
    model_id: 01-ai/Yi-1.5-9B-Chat-16K
    url: https://huggingface.co/01-ai/Yi-1.5-9B-Chat-16K
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
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 64.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#arc_challenge#0510bd0cd7e4
  - benchmark_id: bbh
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 51.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/01-ai/Yi-1.5-9B-Chat-16K/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-a96fec9a4280
      snapshot_ref: sha256:8696e552b50350404b677410b1c4532e02d85ecfc7424c19f202e8bcf699932b
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#bbh#87d7ac60a221
  - benchmark_id: gpqa_pooled
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 30.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/01-ai/Yi-1.5-9B-Chat-16K/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-a96fec9a4280
      snapshot_ref: sha256:8696e552b50350404b677410b1c4532e02d85ecfc7424c19f202e8bcf699932b
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#gpqa_pooled#2f74a972290a
  - benchmark_id: gsm8k
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 59.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#gsm8k#b35513779240
  - benchmark_id: hellaswag
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 80.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#hellaswag#e04410a9f31b
  - benchmark_id: ifeval
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 42.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/01-ai/Yi-1.5-9B-Chat-16K/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-a96fec9a4280
      snapshot_ref: sha256:8696e552b50350404b677410b1c4532e02d85ecfc7424c19f202e8bcf699932b
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#ifeval#1add12a57b31
  - benchmark_id: math_lvl5
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 17.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/01-ai/Yi-1.5-9B-Chat-16K/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-a96fec9a4280
      snapshot_ref: sha256:8696e552b50350404b677410b1c4532e02d85ecfc7424c19f202e8bcf699932b
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#math_lvl5#95fba1447a02
  - benchmark_id: mmlu_abstract_algebra
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 46.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_abstract_algebra#a99c2279cf4b
  - benchmark_id: mmlu_anatomy
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 68.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_anatomy#1c943429b230
  - benchmark_id: mmlu_astronomy
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 74.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_astronomy#f2eb0464d38d
  - benchmark_id: mmlu_business_ethics
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 76.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_business_ethics#3f2eaef0e0f0
  - benchmark_id: mmlu_clinical_knowledge
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 72.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_clinical_knowledge#3e8976318ac5
  - benchmark_id: mmlu_college_biology
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 78.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_college_biology#b2a13fdaafd2
  - benchmark_id: mmlu_college_chemistry
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 54.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_college_chemistry#a2bdbae17947
  - benchmark_id: mmlu_college_computer_science
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 62.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_college_computer_science#c1981de3c964
  - benchmark_id: mmlu_college_mathematics
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 47.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_college_mathematics#5deb2e9a5dc9
  - benchmark_id: mmlu_college_medicine
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 69.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_college_medicine#0e17854c3091
  - benchmark_id: mmlu_college_physics
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 47.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_college_physics#ccb05b09f319
  - benchmark_id: mmlu_computer_security
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 77.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_computer_security#e037aa2b52cf
  - benchmark_id: mmlu_conceptual_physics
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 71.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_conceptual_physics#c84eb0cedb47
  - benchmark_id: mmlu_econometrics
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 59.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_econometrics#1fb79d8e3b02
  - benchmark_id: mmlu_electrical_engineering
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 66.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_electrical_engineering#4e8d35e06bbc
  - benchmark_id: mmlu_elementary_mathematics
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 64.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_elementary_mathematics#f9eafc75c33b
  - benchmark_id: mmlu_formal_logic
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 61.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_formal_logic#2a069cb3ca08
  - benchmark_id: mmlu_global_facts
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 45.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_global_facts#05fe1985c140
  - benchmark_id: mmlu_high_school_biology
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 84.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_high_school_biology#cece1b48d74d
  - benchmark_id: mmlu_high_school_chemistry
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 61.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_high_school_chemistry#bf61532093d3
  - benchmark_id: mmlu_high_school_computer_science
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 87.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_high_school_computer_science#cc81a4b48d85
  - benchmark_id: mmlu_high_school_european_history
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 83.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_high_school_european_history#12bc2e84a13b
  - benchmark_id: mmlu_high_school_geography
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 83.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_high_school_geography#a0422fec7584
  - benchmark_id: mmlu_high_school_government_and_politics
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 89.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_high_school_government_and_politics#601a7ec02861
  - benchmark_id: mmlu_high_school_macroeconomics
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 76.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_high_school_macroeconomics#ef34d663753a
  - benchmark_id: mmlu_high_school_mathematics
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 45.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_high_school_mathematics#3eb1e4da4c98
  - benchmark_id: mmlu_high_school_microeconomics
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 84.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_high_school_microeconomics#8d630ed71b51
  - benchmark_id: mmlu_high_school_physics
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 51.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_high_school_physics#a63f2d679ee9
  - benchmark_id: mmlu_high_school_psychology
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 85.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_high_school_psychology#6377d43a6e84
  - benchmark_id: mmlu_high_school_statistics
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 65.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_high_school_statistics#b3857613f56b
  - benchmark_id: mmlu_high_school_us_history
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 86.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_high_school_us_history#2b3ce90ff4ac
  - benchmark_id: mmlu_high_school_world_history
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 84.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_high_school_world_history#f3b0679c823c
  - benchmark_id: mmlu_human_aging
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 71.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_human_aging#d99b00fe0fce
  - benchmark_id: mmlu_human_sexuality
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 74.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_human_sexuality#922003fa26f3
  - benchmark_id: mmlu_international_law
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 80.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_international_law#7bda927f13e2
  - benchmark_id: mmlu_jurisprudence
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 77.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_jurisprudence#88a494b2738b
  - benchmark_id: mmlu_logical_fallacies
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 82.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_logical_fallacies#b7dcfd2cd58d
  - benchmark_id: mmlu_machine_learning
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 51.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_machine_learning#031a6d5903f0
  - benchmark_id: mmlu_management
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 76.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_management#7af713552c44
  - benchmark_id: mmlu_marketing
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 91.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_marketing#d6870a461f3f
  - benchmark_id: mmlu_medical_genetics
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 80.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_medical_genetics#702d10110a95
  - benchmark_id: mmlu_miscellaneous
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 84.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_miscellaneous#1d0f5eef2eed
  - benchmark_id: mmlu_moral_disputes
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 72.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_moral_disputes#b07045084f28
  - benchmark_id: mmlu_moral_scenarios
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 54.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_moral_scenarios#4bf1d1a8f599
  - benchmark_id: mmlu_nutrition
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 77.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_nutrition#ad6bf612c42b
  - benchmark_id: mmlu_philosophy
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 75.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_philosophy#7b042f4f75cd
  - benchmark_id: mmlu_prehistory
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 74.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_prehistory#a46d55383d0b
  - benchmark_id: mmlu_pro
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 39.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/01-ai/Yi-1.5-9B-Chat-16K/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-a96fec9a4280
      snapshot_ref: sha256:8696e552b50350404b677410b1c4532e02d85ecfc7424c19f202e8bcf699932b
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_pro#36831452dc79
  - benchmark_id: mmlu_professional_accounting
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 57.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_professional_accounting#ebfe36c70e3e
  - benchmark_id: mmlu_professional_law
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 50.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_professional_law#6c5ae81f5ab7
  - benchmark_id: mmlu_professional_medicine
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 68.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_professional_medicine#cb955af86e9b
  - benchmark_id: mmlu_professional_psychology
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 70.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_professional_psychology#199976a16053
  - benchmark_id: mmlu_public_relations
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 72.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_public_relations#a41bc70a450c
  - benchmark_id: mmlu_security_studies
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 77.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_security_studies#49ec825c2b4a
  - benchmark_id: mmlu_sociology
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 81.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_sociology#3bc88e5c7e95
  - benchmark_id: mmlu_us_foreign_policy
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 93.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_us_foreign_policy#51427fed15b9
  - benchmark_id: mmlu_virology
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 57.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_virology#15d6f1e58ca2
  - benchmark_id: mmlu_world_religions
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 84.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#mmlu_world_religions#8eee58120226
  - benchmark_id: musr
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 41.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/01-ai/Yi-1.5-9B-Chat-16K/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-a96fec9a4280
      snapshot_ref: sha256:8696e552b50350404b677410b1c4532e02d85ecfc7424c19f202e8bcf699932b
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#musr#a05b321ef839
  - benchmark_id: truthfulqa
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 51.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#truthfulqa#1cc13a2066d4
  - benchmark_id: winogrande
    model_id_as_evaluated: 01-ai/Yi-1.5-9B-Chat-16K
    score: 75.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-25'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-ae2fdf5972a8
      snapshot_ref: sha256:30569cb9e7b10b3c8acaf7f3c988ae4c17f21d53a609e7562f697491e4aa01d7
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-9b-chat-16k#winogrande#c067468e4a76
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
  huggingface_downloads: 9346
  huggingface_likes: 36
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
  huggingface_url: https://huggingface.co/01-ai/Yi-1.5-9B-Chat-16K
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


# Yi 1.5 9B Chat 16K

Auto-generated from HuggingFace Hub metadata for [01-ai/Yi-1.5-9B-Chat-16K](https://huggingface.co/01-ai/Yi-1.5-9B-Chat-16K).

Licence: apache-2.0. Creator distribution https://huggingface.co/01-ai/Yi-1.5-9B-Chat-16K/raw/main/README.md (apache-2.0) and Hub cardData.license apache-2.0, read 2026-09-18.
