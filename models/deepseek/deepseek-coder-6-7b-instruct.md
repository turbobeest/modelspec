---
model_id: deepseek/deepseek-coder-6-7b-instruct
display_name: deepseek coder 6.7B instruct
provider: deepseek
provider_display: DeepSeek
family: deepseek
version: ''
release_date: '2023-10-29'
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
  license_url: https://huggingface.co/deepseek-ai/deepseek-coder-6.7b-instruct/raw/main/LICENSE
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
    model_id: deepseek-ai/deepseek-coder-6.7b-instruct
    url: https://huggingface.co/deepseek-ai/deepseek-coder-6.7b-instruct
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
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 38.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#arc_challenge#c1181eaad287
  - benchmark_id: gsm8k
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 26.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#gsm8k#198dc2974450
  - benchmark_id: hellaswag
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 55.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#hellaswag#fd7c486ffb5f
  - benchmark_id: mmlu_abstract_algebra
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 33.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_abstract_algebra#4b70d2630bc2
  - benchmark_id: mmlu_anatomy
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 34.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_anatomy#3316998e34ab
  - benchmark_id: mmlu_astronomy
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 33.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_astronomy#38803262f495
  - benchmark_id: mmlu_business_ethics
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 42.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_business_ethics#29c702b1bd86
  - benchmark_id: mmlu_clinical_knowledge
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 41.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_clinical_knowledge#7e0f10976fd9
  - benchmark_id: mmlu_college_biology
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 33.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_college_biology#478dd71e23f2
  - benchmark_id: mmlu_college_chemistry
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 36.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_college_chemistry#434d8fb523a6
  - benchmark_id: mmlu_college_computer_science
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 43.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_college_computer_science#7110f48bfb38
  - benchmark_id: mmlu_college_mathematics
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 34.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_college_mathematics#11c5557e6828
  - benchmark_id: mmlu_college_medicine
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 33.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_college_medicine#4d62bbb2a096
  - benchmark_id: mmlu_college_physics
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 23.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_college_physics#65d991e1f691
  - benchmark_id: mmlu_computer_security
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 61.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_computer_security#8405887678eb
  - benchmark_id: mmlu_conceptual_physics
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 34.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_conceptual_physics#e0d19d426f92
  - benchmark_id: mmlu_econometrics
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 30.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_econometrics#ca6efad720a3
  - benchmark_id: mmlu_electrical_engineering
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 44.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_electrical_engineering#85a188eca8be
  - benchmark_id: mmlu_elementary_mathematics
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 34.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_elementary_mathematics#bb73e69e2744
  - benchmark_id: mmlu_formal_logic
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 36.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_formal_logic#da6c6b84824a
  - benchmark_id: mmlu_global_facts
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 33.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_global_facts#068f943e65ae
  - benchmark_id: mmlu_high_school_biology
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 41.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_high_school_biology#1e1a0165c291
  - benchmark_id: mmlu_high_school_chemistry
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 32.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_high_school_chemistry#519e2eb74e61
  - benchmark_id: mmlu_high_school_computer_science
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 56.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_high_school_computer_science#4821fb434f1a
  - benchmark_id: mmlu_high_school_european_history
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 37.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_high_school_european_history#a834b6efa902
  - benchmark_id: mmlu_high_school_geography
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 42.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_high_school_geography#a49208d944bd
  - benchmark_id: mmlu_high_school_government_and_politics
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 43.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_high_school_government_and_politics#91a69d531dc8
  - benchmark_id: mmlu_high_school_macroeconomics
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 35.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_high_school_macroeconomics#0f3541b63e19
  - benchmark_id: mmlu_high_school_mathematics
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 27.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_high_school_mathematics#dc6827bda4c4
  - benchmark_id: mmlu_high_school_microeconomics
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 41.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_high_school_microeconomics#370e4ba6a870
  - benchmark_id: mmlu_high_school_physics
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 33.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_high_school_physics#bc646ddcf698
  - benchmark_id: mmlu_high_school_psychology
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 41.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_high_school_psychology#c6bf1733229a
  - benchmark_id: mmlu_high_school_statistics
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 36.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_high_school_statistics#fde574a3f854
  - benchmark_id: mmlu_high_school_us_history
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 39.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_high_school_us_history#4a13e3c2f072
  - benchmark_id: mmlu_high_school_world_history
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 37.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_high_school_world_history#2bfa8d849be4
  - benchmark_id: mmlu_human_aging
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 39.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_human_aging#2a216a372ed6
  - benchmark_id: mmlu_human_sexuality
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 42.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_human_sexuality#35fd301553c7
  - benchmark_id: mmlu_international_law
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 45.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_international_law#3e54b7fb10d9
  - benchmark_id: mmlu_jurisprudence
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 37.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_jurisprudence#d31d2f33b36c
  - benchmark_id: mmlu_logical_fallacies
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 46.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_logical_fallacies#a770b9e53f93
  - benchmark_id: mmlu_machine_learning
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 33.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_machine_learning#69e901e7deed
  - benchmark_id: mmlu_management
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 38.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_management#91ccce4c8278
  - benchmark_id: mmlu_marketing
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 65.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_marketing#feafabf40a8a
  - benchmark_id: mmlu_medical_genetics
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 41.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_medical_genetics#1dd77c95125f
  - benchmark_id: mmlu_miscellaneous
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 43.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_miscellaneous#2940e68d6cb8
  - benchmark_id: mmlu_moral_disputes
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 41.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_moral_disputes#db93902683cb
  - benchmark_id: mmlu_moral_scenarios
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 25.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_moral_scenarios#20a81d9dadfd
  - benchmark_id: mmlu_nutrition
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 39.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_nutrition#afab0e1f707b
  - benchmark_id: mmlu_philosophy
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 42.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_philosophy#554bb66edf8a
  - benchmark_id: mmlu_prehistory
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 36.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_prehistory#e5ec2b5dfdac
  - benchmark_id: mmlu_professional_accounting
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 31.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_professional_accounting#2771e20c3243
  - benchmark_id: mmlu_professional_law
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 28.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_professional_law#70ffe71f0199
  - benchmark_id: mmlu_professional_medicine
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 34.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_professional_medicine#f6c0099ffa63
  - benchmark_id: mmlu_professional_psychology
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 35.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_professional_psychology#1163f6ef4384
  - benchmark_id: mmlu_public_relations
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 52.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_public_relations#6c3a5a39f208
  - benchmark_id: mmlu_security_studies
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 45.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_security_studies#cfa438eb5f1e
  - benchmark_id: mmlu_sociology
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 42.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_sociology#47391494e27f
  - benchmark_id: mmlu_us_foreign_policy
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 54.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_us_foreign_policy#791b508dec8a
  - benchmark_id: mmlu_virology
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 37.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_virology#b8f4710469be
  - benchmark_id: mmlu_world_religions
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 35.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#mmlu_world_religions#d7daed85ba0d
  - benchmark_id: truthfulqa
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 45.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#truthfulqa#b2daa25f9083
  - benchmark_id: winogrande
    model_id_as_evaluated: deepseek-ai/deepseek-coder-6.7b-instruct
    score: 56.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-instruct/results_2024-01-05T09-40-26.509293.json
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
    - source_id: oll-v1-650475dc3cda
      snapshot_ref: sha256:3fa0beeb1198647b463a0e1aa8c69a6666da6f5475ec2a7e6e7ace28211ea125
      cited_regions:
      - rows
    id: deepseek/deepseek-coder-6-7b-instruct#winogrande#13ebd2b4b0e4
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
  huggingface_downloads: 76001
  huggingface_likes: 486
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
  huggingface_url: https://huggingface.co/deepseek-ai/deepseek-coder-6.7b-instruct
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

# deepseek coder 6.7B instruct

Auto-generated from HuggingFace Hub metadata for [deepseek-ai/deepseek-coder-6.7b-instruct](https://huggingface.co/deepseek-ai/deepseek-coder-6.7b-instruct).

Licence: deepseek. Creator LICENSE file https://huggingface.co/deepseek-ai/deepseek-coder-6.7b-instruct/raw/main/LICENSE (DeepSeek License Agreement) and Hub cardData.license other and license_name deepseek, read 2026-09-18.
