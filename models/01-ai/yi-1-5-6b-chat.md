---
model_id: 01-ai/yi-1-5-6b-chat
display_name: Yi 1.5 6B Chat
provider: 01-ai
provider_display: 01.AI
family: yi
version: ''
release_date: '2024-05-11'
last_updated: ''
status: active
model_type: llm-chat
model_subtypes: []
tags:
- text-generation
pipeline_tag: text-generation
architecture:
  type: null
  total_parameters: 6061035520
  active_parameters: null
  num_experts: null
  experts_per_token: null
  num_layers: 32
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
  license_url: https://huggingface.co/01-ai/Yi-1.5-6B-Chat/raw/main/README.md
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
    model_id: 01-ai/Yi-1.5-6B-Chat
    url: https://huggingface.co/01-ai/Yi-1.5-6B-Chat
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
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 60.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#arc_challenge#7efd7770afe6
  - benchmark_id: bbh
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 45.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/01-ai/Yi-1.5-6B-Chat/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-10-28'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-f03663972ad0
      snapshot_ref: sha256:ba395ea181056469a602c797cd9675ce828eac5a4f7453f34246cd8b6a04e576
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#bbh#44f4c3986476
  - benchmark_id: gpqa_pooled
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 30.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/01-ai/Yi-1.5-6B-Chat/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-10-28'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-f03663972ad0
      snapshot_ref: sha256:ba395ea181056469a602c797cd9675ce828eac5a4f7453f34246cd8b6a04e576
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#gpqa_pooled#203acf1c616b
  - benchmark_id: gsm8k
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 67.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#gsm8k#4cf56c499612
  - benchmark_id: hellaswag
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 78.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#hellaswag#4cb435f2001b
  - benchmark_id: ifeval
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 51.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/01-ai/Yi-1.5-6B-Chat/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-10-28'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-f03663972ad0
      snapshot_ref: sha256:ba395ea181056469a602c797cd9675ce828eac5a4f7453f34246cd8b6a04e576
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#ifeval#69f7c5969356
  - benchmark_id: math_lvl5
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 16.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/01-ai/Yi-1.5-6B-Chat/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-10-28'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-f03663972ad0
      snapshot_ref: sha256:ba395ea181056469a602c797cd9675ce828eac5a4f7453f34246cd8b6a04e576
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#math_lvl5#4acceffcc94f
  - benchmark_id: mmlu_abstract_algebra
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 45.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_abstract_algebra#20148eef60e2
  - benchmark_id: mmlu_anatomy
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 51.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_anatomy#a70fa6f18934
  - benchmark_id: mmlu_astronomy
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 67.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_astronomy#f43720b29cf7
  - benchmark_id: mmlu_business_ethics
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 70.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_business_ethics#dae3c5aa610e
  - benchmark_id: mmlu_clinical_knowledge
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 67.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_clinical_knowledge#6e957ef71247
  - benchmark_id: mmlu_college_biology
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 72.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_college_biology#f91a99f85fb0
  - benchmark_id: mmlu_college_chemistry
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 45.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_college_chemistry#b7473e42b61c
  - benchmark_id: mmlu_college_computer_science
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 54.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_college_computer_science#3bc64eb26b32
  - benchmark_id: mmlu_college_mathematics
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 41.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_college_mathematics#5a064dc66058
  - benchmark_id: mmlu_college_medicine
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 60.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_college_medicine#72f78addc965
  - benchmark_id: mmlu_college_physics
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 45.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_college_physics#12793d41e245
  - benchmark_id: mmlu_computer_security
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 71.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_computer_security#7407928a83f1
  - benchmark_id: mmlu_conceptual_physics
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 64.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_conceptual_physics#9dd5a61cecf2
  - benchmark_id: mmlu_econometrics
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 51.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_econometrics#e0f3ae923e01
  - benchmark_id: mmlu_electrical_engineering
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 63.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_electrical_engineering#8b4e5f9f925f
  - benchmark_id: mmlu_elementary_mathematics
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 53.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_elementary_mathematics#cd6217631708
  - benchmark_id: mmlu_formal_logic
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 58.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_formal_logic#34cab9197c1d
  - benchmark_id: mmlu_global_facts
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 42.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_global_facts#4ef1f3fd55d8
  - benchmark_id: mmlu_high_school_biology
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 75.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_high_school_biology#c13dd79eabfa
  - benchmark_id: mmlu_high_school_chemistry
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 53.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_high_school_chemistry#e72348d37994
  - benchmark_id: mmlu_high_school_computer_science
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 75.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_high_school_computer_science#815d4d24a5ee
  - benchmark_id: mmlu_high_school_european_history
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 78.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_high_school_european_history#1e437fc55f9a
  - benchmark_id: mmlu_high_school_geography
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 78.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_high_school_geography#2255e68c1ead
  - benchmark_id: mmlu_high_school_government_and_politics
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 84.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_high_school_government_and_politics#2ad7d8c95f44
  - benchmark_id: mmlu_high_school_macroeconomics
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 66.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_high_school_macroeconomics#6ef6755a6434
  - benchmark_id: mmlu_high_school_mathematics
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 42.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_high_school_mathematics#2f80f4f754b5
  - benchmark_id: mmlu_high_school_microeconomics
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 82.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_high_school_microeconomics#ec52807d91a6
  - benchmark_id: mmlu_high_school_physics
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 39.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_high_school_physics#eb8fbc8a40b5
  - benchmark_id: mmlu_high_school_psychology
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 82.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_high_school_psychology#7d8eea9fa7c8
  - benchmark_id: mmlu_high_school_statistics
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 53.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_high_school_statistics#101aefae0efa
  - benchmark_id: mmlu_high_school_us_history
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 77.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_high_school_us_history#a95a7dfa69cb
  - benchmark_id: mmlu_high_school_world_history
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 78.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_high_school_world_history#603ba86fa3f1
  - benchmark_id: mmlu_human_aging
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 61.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_human_aging#1ea304f757ba
  - benchmark_id: mmlu_human_sexuality
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 65.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_human_sexuality#cd6e655c3d8e
  - benchmark_id: mmlu_international_law
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 76.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_international_law#506eb6a4267f
  - benchmark_id: mmlu_jurisprudence
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 77.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_jurisprudence#7913140fe7da
  - benchmark_id: mmlu_logical_fallacies
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 76.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_logical_fallacies#1b6c404c94a7
  - benchmark_id: mmlu_machine_learning
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 56.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_machine_learning#8de923d8b5de
  - benchmark_id: mmlu_management
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 80.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_management#646f7dd1ecac
  - benchmark_id: mmlu_marketing
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 88.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_marketing#9c45a87858df
  - benchmark_id: mmlu_medical_genetics
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 68.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_medical_genetics#465ed5eff820
  - benchmark_id: mmlu_miscellaneous
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 79.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_miscellaneous#eb4249bb3295
  - benchmark_id: mmlu_moral_disputes
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 69.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_moral_disputes#70126e0cf16a
  - benchmark_id: mmlu_moral_scenarios
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 38.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_moral_scenarios#85de72e01182
  - benchmark_id: mmlu_nutrition
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 68.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_nutrition#7fc27239a66f
  - benchmark_id: mmlu_philosophy
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 64.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_philosophy#50ae0b250da8
  - benchmark_id: mmlu_prehistory
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 63.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_prehistory#86e67d33817b
  - benchmark_id: mmlu_pro
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 31.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/01-ai/Yi-1.5-6B-Chat/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-10-28'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-f03663972ad0
      snapshot_ref: sha256:ba395ea181056469a602c797cd9675ce828eac5a4f7453f34246cd8b6a04e576
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_pro#917af281169b
  - benchmark_id: mmlu_professional_accounting
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 52.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_professional_accounting#885faa1b5979
  - benchmark_id: mmlu_professional_law
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 47.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_professional_law#948b9140ebce
  - benchmark_id: mmlu_professional_medicine
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 53.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_professional_medicine#b8be49326665
  - benchmark_id: mmlu_professional_psychology
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 62.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_professional_psychology#eb84184a887b
  - benchmark_id: mmlu_public_relations
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 64.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_public_relations#748f937dab1d
  - benchmark_id: mmlu_security_studies
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 68.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_security_studies#e0e0cc0250f4
  - benchmark_id: mmlu_sociology
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 81.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_sociology#494a80ec9f7c
  - benchmark_id: mmlu_us_foreign_policy
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 81.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_us_foreign_policy#3d7339a34c78
  - benchmark_id: mmlu_virology
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 50.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_virology#2c6a8fc0b724
  - benchmark_id: mmlu_world_religions
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 74.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#mmlu_world_religions#a85f6bd038ec
  - benchmark_id: musr
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 43.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/01-ai/Yi-1.5-6B-Chat/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-10-28'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-f03663972ad0
      snapshot_ref: sha256:ba395ea181056469a602c797cd9675ce828eac5a4f7453f34246cd8b6a04e576
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#musr#854b5fa1ee86
  - benchmark_id: truthfulqa
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 52.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#truthfulqa#822af389117d
  - benchmark_id: winogrande
    model_id_as_evaluated: 01-ai/Yi-1.5-6B-Chat
    score: 73.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B-Chat/results_2024-05-16T14-12-12.578596.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-f4ce6c6fb60f
      snapshot_ref: sha256:38cf4cb8b297a22a109131a1da88549e9a5e98618502120841ab91186bcede04
      cited_regions:
      - rows
    id: 01-ai/yi-1-5-6b-chat#winogrande#d83c4c1a4cfe
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
  huggingface_downloads: 5918
  huggingface_likes: 41
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
  huggingface_url: https://huggingface.co/01-ai/Yi-1.5-6B-Chat
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


# Yi 1.5 6B Chat

Auto-generated from HuggingFace Hub metadata for [01-ai/Yi-1.5-6B-Chat](https://huggingface.co/01-ai/Yi-1.5-6B-Chat).

Licence: apache-2.0. Creator distribution https://huggingface.co/01-ai/Yi-1.5-6B-Chat/raw/main/README.md (apache-2.0) and Hub cardData.license apache-2.0, read 2026-09-18.
