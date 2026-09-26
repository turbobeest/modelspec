---
model_id: deepseek/deepseek-llm-7b-chat
display_name: deepseek llm 7B chat
provider: deepseek
provider_display: DeepSeek
family: deepseek
version: ''
release_date: '2023-11-29'
last_updated: ''
status: active
model_type: llm-chat
model_subtypes: []
tags:
- text-generation
pipeline_tag: text-generation
architecture:
  type: null
  total_parameters: 7000000000
  active_parameters: null
  num_experts: null
  experts_per_token: null
  num_layers: 30
  hidden_size: 4096
  intermediate_size: 11008
  attention_type: null
  num_attention_heads: 32
  num_kv_heads: 32
  positional_encoding: null
  rope_theta: null
  vocab_size: 102400
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
  total_parameters_source: model_card_published:prose_parameters
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
  license_url: https://huggingface.co/deepseek-ai/deepseek-llm-7b-chat/raw/main/LICENSE
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
    model_id: deepseek-ai/deepseek-llm-7b-chat
    url: https://huggingface.co/deepseek-ai/deepseek-llm-7b-chat
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
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 55.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#arc_challenge#b19337043948
  - benchmark_id: bbh
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 36.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/deepseek-ai/deepseek-llm-7b-chat/results_2025-02-13T18-27-04.338360.json
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
    - source_id: oll-v2-4dd33d2a867b
      snapshot_ref: sha256:f6f4b225ea2a32e9c99e2943fbc7eae4cd50deca84dd9a350754496872cdda37
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#bbh#905cfadcd80f
  - benchmark_id: gpqa_pooled
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 26.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/deepseek-ai/deepseek-llm-7b-chat/results_2025-02-13T18-27-04.338360.json
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
    - source_id: oll-v2-4dd33d2a867b
      snapshot_ref: sha256:f6f4b225ea2a32e9c99e2943fbc7eae4cd50deca84dd9a350754496872cdda37
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#gpqa_pooled#97b36a709bad
  - benchmark_id: gsm8k
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 45.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#gsm8k#b16151527621
  - benchmark_id: hellaswag
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 79.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#hellaswag#ce2ecdebe34c
  - benchmark_id: ifeval
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 41.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/deepseek-ai/deepseek-llm-7b-chat/results_2025-02-13T18-27-04.338360.json
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
    - source_id: oll-v2-4dd33d2a867b
      snapshot_ref: sha256:f6f4b225ea2a32e9c99e2943fbc7eae4cd50deca84dd9a350754496872cdda37
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#ifeval#72f1df7b3227
  - benchmark_id: math_lvl5
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 2.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/deepseek-ai/deepseek-llm-7b-chat/results_2025-02-13T18-27-04.338360.json
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
    - source_id: oll-v2-4dd33d2a867b
      snapshot_ref: sha256:f6f4b225ea2a32e9c99e2943fbc7eae4cd50deca84dd9a350754496872cdda37
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#math_lvl5#eb3fe885bbff
  - benchmark_id: mmlu_abstract_algebra
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 25.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_abstract_algebra#8643168cdd54
  - benchmark_id: mmlu_anatomy
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 45.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_anatomy#8e677442b561
  - benchmark_id: mmlu_astronomy
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 52.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_astronomy#9b8cdde9ec29
  - benchmark_id: mmlu_business_ethics
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 55.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_business_ethics#d463d5a86c55
  - benchmark_id: mmlu_clinical_knowledge
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 53.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_clinical_knowledge#bb3532231e3b
  - benchmark_id: mmlu_college_biology
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 50.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_college_biology#c9f4b484636e
  - benchmark_id: mmlu_college_chemistry
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 37.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_college_chemistry#fa9db8b74a38
  - benchmark_id: mmlu_college_computer_science
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 46.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_college_computer_science#c902f6d3fcfe
  - benchmark_id: mmlu_college_mathematics
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 31.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_college_mathematics#386f571f33e8
  - benchmark_id: mmlu_college_medicine
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 49.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_college_medicine#1b0218d4c23b
  - benchmark_id: mmlu_college_physics
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 29.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_college_physics#c83b1de901a7
  - benchmark_id: mmlu_computer_security
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 62.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_computer_security#3a3a6c8a0eaf
  - benchmark_id: mmlu_conceptual_physics
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 43.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_conceptual_physics#efd84729d2a4
  - benchmark_id: mmlu_econometrics
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 27.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_econometrics#de85889481a2
  - benchmark_id: mmlu_electrical_engineering
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 45.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_electrical_engineering#de36cc56d0e9
  - benchmark_id: mmlu_elementary_mathematics
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 31.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_elementary_mathematics#94e8d5f607a1
  - benchmark_id: mmlu_formal_logic
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 33.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_formal_logic#890c1d1a97db
  - benchmark_id: mmlu_global_facts
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 25.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_global_facts#130339222287
  - benchmark_id: mmlu_high_school_biology
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 57.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_high_school_biology#138014e572da
  - benchmark_id: mmlu_high_school_chemistry
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 35.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_high_school_chemistry#b858c7f8e766
  - benchmark_id: mmlu_high_school_computer_science
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 47.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_high_school_computer_science#6d167ce2d36b
  - benchmark_id: mmlu_high_school_european_history
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 67.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_high_school_european_history#3ffc0246b4ca
  - benchmark_id: mmlu_high_school_geography
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 67.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_high_school_geography#588731801867
  - benchmark_id: mmlu_high_school_government_and_politics
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 71.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_high_school_government_and_politics#e36885f45f8c
  - benchmark_id: mmlu_high_school_macroeconomics
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 46.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_high_school_macroeconomics#3908ba65871f
  - benchmark_id: mmlu_high_school_mathematics
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 30.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_high_school_mathematics#454b136f283c
  - benchmark_id: mmlu_high_school_microeconomics
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 47.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_high_school_microeconomics#4b1161abf7e6
  - benchmark_id: mmlu_high_school_physics
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 29.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_high_school_physics#248c8c1e765e
  - benchmark_id: mmlu_high_school_psychology
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 71.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_high_school_psychology#7cf4c9a6d49d
  - benchmark_id: mmlu_high_school_statistics
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 43.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_high_school_statistics#eb0f2964d7ab
  - benchmark_id: mmlu_high_school_us_history
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 71.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_high_school_us_history#d359ac1d7374
  - benchmark_id: mmlu_high_school_world_history
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 72.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_high_school_world_history#92f8cf24624e
  - benchmark_id: mmlu_human_aging
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 57.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_human_aging#e29e38e72e97
  - benchmark_id: mmlu_human_sexuality
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 55.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_human_sexuality#ea07af0d6ee2
  - benchmark_id: mmlu_international_law
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 66.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_international_law#078350e6d0ad
  - benchmark_id: mmlu_jurisprudence
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 63.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_jurisprudence#78f73fcfdda4
  - benchmark_id: mmlu_logical_fallacies
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 60.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_logical_fallacies#efa53435ad9a
  - benchmark_id: mmlu_machine_learning
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 41.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_machine_learning#e9d6861e3034
  - benchmark_id: mmlu_management
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 65.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_management#eef3adc7ae56
  - benchmark_id: mmlu_marketing
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 82.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_marketing#3c70d246cdd2
  - benchmark_id: mmlu_medical_genetics
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 60.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_medical_genetics#dae1e57b84c7
  - benchmark_id: mmlu_miscellaneous
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 73.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_miscellaneous#47729e177369
  - benchmark_id: mmlu_moral_disputes
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 59.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_moral_disputes#e7909cc14cef
  - benchmark_id: mmlu_moral_scenarios
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 30.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_moral_scenarios#843d96a2aebc
  - benchmark_id: mmlu_nutrition
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 52.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_nutrition#fe2716d9f259
  - benchmark_id: mmlu_philosophy
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 55.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_philosophy#f27e7a6b9672
  - benchmark_id: mmlu_prehistory
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 56.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_prehistory#4b5a872dc3f7
  - benchmark_id: mmlu_pro
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 21.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/deepseek-ai/deepseek-llm-7b-chat/results_2025-02-13T18-27-04.338360.json
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
    - source_id: oll-v2-4dd33d2a867b
      snapshot_ref: sha256:f6f4b225ea2a32e9c99e2943fbc7eae4cd50deca84dd9a350754496872cdda37
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_pro#7fb557ae13d6
  - benchmark_id: mmlu_professional_accounting
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 36.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_professional_accounting#261802d945d4
  - benchmark_id: mmlu_professional_law
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 40.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_professional_law#9cb3a27ef7e9
  - benchmark_id: mmlu_professional_medicine
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 46.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_professional_medicine#a774574ba055
  - benchmark_id: mmlu_professional_psychology
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 52.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_professional_psychology#43538a9ddaa9
  - benchmark_id: mmlu_public_relations
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 59.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_public_relations#af11029543e3
  - benchmark_id: mmlu_security_studies
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 62.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_security_studies#3d9989945614
  - benchmark_id: mmlu_sociology
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 70.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_sociology#28672380f320
  - benchmark_id: mmlu_us_foreign_policy
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 82.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_us_foreign_policy#fcd480017c2b
  - benchmark_id: mmlu_virology
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 47.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_virology#593c99ea4cc6
  - benchmark_id: mmlu_world_religions
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 76.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#mmlu_world_religions#6b37422021fe
  - benchmark_id: musr
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 46.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/deepseek-ai/deepseek-llm-7b-chat/results_2025-02-13T18-27-04.338360.json
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
    - source_id: oll-v2-4dd33d2a867b
      snapshot_ref: sha256:f6f4b225ea2a32e9c99e2943fbc7eae4cd50deca84dd9a350754496872cdda37
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#musr#b6f8dede4313
  - benchmark_id: truthfulqa
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 47.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#truthfulqa#4c85a72f1a99
  - benchmark_id: winogrande
    model_id_as_evaluated: deepseek-ai/deepseek-llm-7b-chat
    score: 74.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-llm-7b-chat/results_2024-01-05T10-38-25.592014.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-05'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-63b4ff14f40d
      snapshot_ref: sha256:84991e17cc5d5de10bb83cad0e9c03fb77d88ed3c9ffe713f3d833debf08cdc5
      cited_regions:
      - rows
    id: deepseek/deepseek-llm-7b-chat#winogrande#88dbd95c6dcf
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
  huggingface_downloads: 238376
  huggingface_likes: 218
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
  huggingface_url: https://huggingface.co/deepseek-ai/deepseek-llm-7b-chat
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


# deepseek llm 7B chat

Auto-generated from HuggingFace Hub metadata for [deepseek-ai/deepseek-llm-7b-chat](https://huggingface.co/deepseek-ai/deepseek-llm-7b-chat).

Licence: deepseek. Creator distribution https://huggingface.co/deepseek-ai/deepseek-llm-7b-chat/raw/main/LICENSE (deepseek) and Hub cardData.license other and license_name deepseek, read 2026-09-18.
