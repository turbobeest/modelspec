---
model_id: deepseek/deepseek-v3-1
display_name: DeepSeek V3.1
provider: deepseek
provider_display: DeepSeek
family: deepseek
version: ''
release_date: '2025-08-21'
last_updated: ''
status: active
model_type: llm-code
model_subtypes:
- llm-reasoning
tags:
- text-generation
- openai-compatible
pipeline_tag: text-generation
architecture:
  type: null
  total_parameters: 684531386000
  active_parameters: 37000000000
  num_experts: 256
  experts_per_token: 8
  num_layers: 61
  hidden_size: 7168
  intermediate_size: 18432
  attention_type: null
  num_attention_heads: 128
  num_kv_heads: 128
  positional_encoding: null
  rope_theta: null
  vocab_size: 129280
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
  base_model: deepseek-ai/DeepSeek-V3.1-Base
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
  license_url: https://huggingface.co/deepseek-ai/DeepSeek-V3.1/raw/main/LICENSE
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
    context_window: 131072
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
    overall: tier-1
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
    available: true
    model_id: ''
    url: https://www.together.ai/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  fireworks_ai:
    available: true
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
    available: true
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
    available: true
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
    available: true
    model_id: deepseek-chat
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
    model_id: deepseek-ai/DeepSeek-V3.1
    url: https://huggingface.co/deepseek-ai/DeepSeek-V3.1
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
    arena_elo_coding: 1340.0
    arena_elo_hard_prompts: 1433.3
    arena_elo_math: 1320.0
    arena_elo_overall: 1330.0
    arena_elo_style_control: 1417.9
    gpqa_diamond: 62.3
    humaneval: 87.5
    ifeval: 85.5
    live_code_bench: 57.7
    math_500: 91.0
    mmlu_pro: 77.2
    multipl_e_csharp: 79.8
    multipl_e_julia: 60.2
    multipl_e_kotlin: 71.5
    multipl_e_lua: 54.5
    multipl_e_perl: 49.5
    multipl_e_php: 77.2
    multipl_e_r: 56.5
    multipl_e_ruby: 64.5
    multipl_e_scala: 59.8
    multipl_e_swift: 64.8
    terminal_bench: 31.3
  benchmark_source: lmarena.ai, provider-reports, safety-evals, preference-evals,
    open-llm-leaderboard-v2, llm-stats
  benchmark_as_of: 2026-04
  benchmark_notes: ''
  evidence:
  - benchmark_id: arena_elo_style_control
    model_id_as_evaluated: deepseek-v3.1-thinking
    score: 1415.98
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-30'
    benchmark_version: text_style_control / overall, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category overall,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: thinking; MODEL-123 max-effort rule). Rating 1415.98 [1409.31, 1422.66], 11460
      votes, rank 125.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    measured_by: independent_evaluator
    observed_at: '2026-09-30'
    id: deepseek/deepseek-v3-1#arena_elo_style_control#3b78cb8124fc
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:1bc41471fa63c00d5e990f8ff6c7ae8d343321a704311ca8585bda974efd153d
      cited_regions:
      - rows
  - benchmark_id: arena_sc_coding
    model_id_as_evaluated: deepseek-v3.1-thinking
    score: 1455.79
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-30'
    benchmark_version: text_style_control / coding, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category coding,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: thinking; MODEL-123 max-effort rule). Rating 1455.79 [1442.32, 1469.27], 1875
      votes, rank 136.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    measured_by: independent_evaluator
    observed_at: '2026-09-30'
    id: deepseek/deepseek-v3-1#arena_sc_coding#f4d574508e37
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:089deb374ac3c4b394209968c2abcb3cf655a1b9a30a4131b30ac8c829a701b0
      cited_regions:
      - rows
  - benchmark_id: arena_sc_hard_prompts
    model_id_as_evaluated: deepseek-v3.1-thinking
    score: 1436.26
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-30'
    benchmark_version: text_style_control / hard_prompts, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category hard_prompts,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: thinking; MODEL-123 max-effort rule). Rating 1436.26 [1427.63, 1444.90], 5094
      votes, rank 124.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    measured_by: independent_evaluator
    observed_at: '2026-09-30'
    id: deepseek/deepseek-v3-1#arena_sc_hard_prompts#33f39ee8c80c
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:1b7b4656ca832e762e7f13e33eaaf32c7340cd045337d7ac1f054ef70c4bf1bf
      cited_regions:
      - rows
  - benchmark_id: arena_sc_math
    model_id_as_evaluated: deepseek-v3.1-thinking
    score: 1415.75
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-30'
    benchmark_version: text_style_control / math, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category math, leaderboard_publish_date
      2026-09-13; style control. Highest-effort row for the product (effort: thinking; MODEL-123
      max-effort rule). Rating 1415.75 [1393.66, 1437.85], 658 votes, rank 119.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    measured_by: independent_evaluator
    observed_at: '2026-09-30'
    id: deepseek/deepseek-v3-1#arena_sc_math#944adebb5d90
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:1874a1ccff7caa3c0046e181bbaeb0b8343bce7adb4066b951bc9c44d194ec6d
      cited_regions:
      - rows
  - benchmark_id: arena_sc_creative_writing
    model_id_as_evaluated: deepseek-v3.1-thinking
    score: 1401.92
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-30'
    benchmark_version: text_style_control / creative_writing, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category creative_writing,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: thinking; MODEL-123 max-effort rule). Rating 1401.92 [1387.04, 1416.80], 1616
      votes, rank 96.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    measured_by: independent_evaluator
    observed_at: '2026-09-30'
    id: deepseek/deepseek-v3-1#arena_sc_creative_writing#a864b6225c16
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:fc5f6716f31834193f7b2136ea74bde411ae5ba90fc4ac118d482310e61b38d2
      cited_regions:
      - rows
  - benchmark_id: arena_sc_instruction_following
    model_id_as_evaluated: deepseek-v3.1-thinking
    score: 1416.41
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-30'
    benchmark_version: text_style_control / instruction_following, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category instruction_following,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: thinking; MODEL-123 max-effort rule). Rating 1416.41 [1405.34, 1427.48], 2832
      votes, rank 103.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    measured_by: independent_evaluator
    observed_at: '2026-09-30'
    id: deepseek/deepseek-v3-1#arena_sc_instruction_following#086ff094caff
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:8dcf9ad77990db5c111c78a9d921ba5a078255a7268d36cda182d9e2e8baed14
      cited_regions:
      - rows
  - benchmark_id: arena_sc_multi_turn
    model_id_as_evaluated: deepseek-v3.1-thinking
    score: 1415.29
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-30'
    benchmark_version: text_style_control / multi_turn, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category multi_turn,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: thinking; MODEL-123 max-effort rule). Rating 1415.29 [1401.39, 1429.20], 1824
      votes, rank 129.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    measured_by: independent_evaluator
    observed_at: '2026-09-30'
    id: deepseek/deepseek-v3-1#arena_sc_multi_turn#94a53d4328a1
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:669cce652634672175a1aa830b1e106cc211f20e4f5a8190f41be169b0e8780e
      cited_regions:
      - rows
  - benchmark_id: arena_sc_expert
    model_id_as_evaluated: deepseek-v3.1-thinking
    score: 1431.03
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-30'
    benchmark_version: text_style_control / expert, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category expert,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: thinking; MODEL-123 max-effort rule). Rating 1431.03 [1406.43, 1455.63], 535
      votes, rank 130.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    measured_by: independent_evaluator
    observed_at: '2026-09-30'
    id: deepseek/deepseek-v3-1#arena_sc_expert#fabc3700150f
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:db8d6995a9ec2ba53e4d4d240df0cce213a4b54b2143ae674970e3afa1dfe764
      cited_regions:
      - rows
  - benchmark_id: arena_sc_longer_query
    model_id_as_evaluated: deepseek-v3.1-thinking
    score: 1446.13
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-30'
    benchmark_version: text_style_control / longer_query, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category longer_query,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: thinking; MODEL-123 max-effort rule). Rating 1446.13 [1434.20, 1458.05], 2383
      votes, rank 89.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    measured_by: independent_evaluator
    observed_at: '2026-09-30'
    id: deepseek/deepseek-v3-1#arena_sc_longer_query#11b956ec3a7c
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:f27585ee7eee36757893f733b338f207eabe2f9fb0349b6b539f7cb5c60fd4ab
      cited_regions:
      - rows
  - benchmark_id: arena_sc_non_english
    model_id_as_evaluated: deepseek-v3.1-thinking
    score: 1400.91
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-30'
    benchmark_version: text_style_control / non_english, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category non_english,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: thinking; MODEL-123 max-effort rule). Rating 1400.91 [1393.04, 1408.79], 6799
      votes, rank 125.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    measured_by: independent_evaluator
    observed_at: '2026-09-30'
    id: deepseek/deepseek-v3-1#arena_sc_non_english#ab53500cabd5
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:52e386a612514d210b1d77719363e4ca268905f06901681ab924fac1d9520304
      cited_regions:
      - rows
  - benchmark_id: arena_sc_medicine
    model_id_as_evaluated: deepseek-v3.1-thinking
    score: 1446.69
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-30'
    benchmark_version: text_style_control / industry_medicine_and_healthcare, latest split,
      revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category industry_medicine_and_healthcare,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: thinking; MODEL-123 max-effort rule). Rating 1446.69 [1424.20, 1469.17], 695
      votes, rank 103.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    measured_by: independent_evaluator
    observed_at: '2026-09-30'
    id: deepseek/deepseek-v3-1#arena_sc_medicine#8022ae85cca7
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:544b6524228d2e78462111b28f6dc4d5ae76d82f8ba52fd6040b0639e1f4856c
      cited_regions:
      - rows
  - benchmark_id: arena_sc_legal
    model_id_as_evaluated: deepseek-v3.1-thinking
    score: 1422.48
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-30'
    benchmark_version: text_style_control / industry_legal_and_government, latest split, revision
      1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category industry_legal_and_government,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: thinking; MODEL-123 max-effort rule). Rating 1422.48 [1401.70, 1443.26], 772
      votes, rank 129.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    measured_by: independent_evaluator
    observed_at: '2026-09-30'
    id: deepseek/deepseek-v3-1#arena_sc_legal#d8188d4fb977
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:07e3a236f9ee5e0cecac83995952d8e94413e872035c5ccae1efa23137a236ed
      cited_regions:
      - rows
  - benchmark_id: arena_sc_business
    model_id_as_evaluated: deepseek-v3.1-thinking
    score: 1417.6
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-30'
    benchmark_version: text_style_control / industry_business_and_management_and_financial_operations,
      latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category industry_business_and_management_and_financial_operations,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: thinking; MODEL-123 max-effort rule). Rating 1417.60 [1404.26, 1430.94], 1934
      votes, rank 117.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    measured_by: independent_evaluator
    observed_at: '2026-09-30'
    id: deepseek/deepseek-v3-1#arena_sc_business#b52897d5a124
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:d1da5448d5afc01a34ae83fe1a795ef9a79a434bfe906fe2426ce82a67b36755
      cited_regions:
      - rows
  - benchmark_id: arena_sc_science
    model_id_as_evaluated: deepseek-v3.1-thinking
    score: 1426.71
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-30'
    benchmark_version: text_style_control / industry_life_and_physical_and_social_science, latest
      split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category industry_life_and_physical_and_social_science,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: thinking; MODEL-123 max-effort rule). Rating 1426.71 [1413.05, 1440.37], 1834
      votes, rank 136.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    measured_by: independent_evaluator
    observed_at: '2026-09-30'
    id: deepseek/deepseek-v3-1#arena_sc_science#967982fe8560
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:1017485e0b9dcfcf7d1a4dfeeed89d314f2f74f8131a3f8e05d6b833360bea76
      cited_regions:
      - rows
  - benchmark_id: arena_sc_writing
    model_id_as_evaluated: deepseek-v3.1-thinking
    score: 1407.36
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-30'
    benchmark_version: text_style_control / industry_writing_and_literature_and_language, latest
      split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category industry_writing_and_literature_and_language,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: thinking; MODEL-123 max-effort rule). Rating 1407.36 [1395.90, 1418.83], 2720
      votes, rank 100.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    measured_by: independent_evaluator
    observed_at: '2026-09-30'
    id: deepseek/deepseek-v3-1#arena_sc_writing#27104d722efa
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:60b89142370aecd9137ff982bd144e8628dc8abadd10f41b90d334d34878bae0
      cited_regions:
      - rows
  - benchmark_id: aime_2025
    model_id_as_evaluated: DeepSeek-v3.1 (Think)
    score: 90.83
    unit: percent
    source_url: https://matharena.ai/competition_tables/aime--aime_2025
    source_kind: independent_evaluator
    evidence_date: '2026-09-24'
    date_type: evaluated
    verified_at: '2026-09-24'
    benchmark_version: AIME 2025, MathArena final-answer table
    configuration: MathArena competition table read 2026-09-24; the table states no run date,
      so the reading is dated by the observation. Effort thinking; highest-effort row for the
      model. MathArena lists final-answer competitions as deprecated.
    limitations: 'MathArena marks this row: model was released after competition release, so
      contamination is possible.'
    measured_by: independent_evaluator
  - benchmark_id: arena_sc_english
    model_id_as_evaluated: deepseek-v3.1
    score: 1425.9057257594832
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: evaluated
    observed_at: '2026-09-30'
    verified_at: '2026-09-30'
    benchmark_version: ''
    configuration: ''
    limitations: ''
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:1e2fcc24a5c8cdcd90c665aaa64b557f473180d9ce1725066717e04bfd10e5f1
      cited_regions:
      - rows
    id: deepseek/deepseek-v3-1#arena_sc_english#f2740e50ab87
  - benchmark_id: arena_sc_chinese
    model_id_as_evaluated: deepseek-v3.1
    score: 1455.4592987888652
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: evaluated
    observed_at: '2026-09-30'
    verified_at: '2026-09-30'
    benchmark_version: ''
    configuration: ''
    limitations: ''
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:449b90746065449e59f0dd2bbdfcb8ef55aa5fe42c1b6beb8c930eb79a68224d
      cited_regions:
      - rows
    id: deepseek/deepseek-v3-1#arena_sc_chinese#e35025d70f6e
  - benchmark_id: arena_sc_japanese
    model_id_as_evaluated: deepseek-v3.1
    score: 1380.4177059756025
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: evaluated
    observed_at: '2026-09-30'
    verified_at: '2026-09-30'
    benchmark_version: ''
    configuration: ''
    limitations: ''
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:7839399ba846da94c65849c08837839d515c8b37ae6314453bedf1c962846be2
      cited_regions:
      - rows
    id: deepseek/deepseek-v3-1#arena_sc_japanese#ceba83c789fd
  - benchmark_id: arena_sc_korean
    model_id_as_evaluated: deepseek-v3.1
    score: 1341.4837594873711
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: evaluated
    observed_at: '2026-09-30'
    verified_at: '2026-09-30'
    benchmark_version: ''
    configuration: ''
    limitations: ''
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:8a792645624d2854a8bb09bcb4bbfee6219a8e973f03fb84a4e42716cb635ae8
      cited_regions:
      - rows
    id: deepseek/deepseek-v3-1#arena_sc_korean#b0f20edb1149
  - benchmark_id: arena_sc_russian
    model_id_as_evaluated: deepseek-v3.1
    score: 1405.249229165275
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: evaluated
    observed_at: '2026-09-30'
    verified_at: '2026-09-30'
    benchmark_version: ''
    configuration: ''
    limitations: ''
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:5364bedcc9fe8a9598db9c20aabead5411e9c132021ef8e55da2be02c0a36c67
      cited_regions:
      - rows
    id: deepseek/deepseek-v3-1#arena_sc_russian#47b4d7c0b90c
  - benchmark_id: arena_sc_spanish
    model_id_as_evaluated: deepseek-v3.1
    score: 1422.032359118477
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: evaluated
    observed_at: '2026-09-30'
    verified_at: '2026-09-30'
    benchmark_version: ''
    configuration: ''
    limitations: ''
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:8d2651582e59832130a278d4b2efb6e4c03ae6e796506ad9930aec870da2547b
      cited_regions:
      - rows
    id: deepseek/deepseek-v3-1#arena_sc_spanish#6ae9d5750caf
  - benchmark_id: arena_sc_german
    model_id_as_evaluated: deepseek-v3.1
    score: 1406.607862125182
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: evaluated
    observed_at: '2026-09-30'
    verified_at: '2026-09-30'
    benchmark_version: ''
    configuration: ''
    limitations: ''
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:5b6244cf0e66d4e7a6c2239bd4aedb255de731f67f134c7be235df3f2266be4b
      cited_regions:
      - rows
    id: deepseek/deepseek-v3-1#arena_sc_german#d8e81037f4a7
  - benchmark_id: arena_sc_french
    model_id_as_evaluated: deepseek-v3.1
    score: 1447.1739118433268
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: evaluated
    observed_at: '2026-09-30'
    verified_at: '2026-09-30'
    benchmark_version: ''
    configuration: ''
    limitations: ''
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:4425fd6448ec82f9820e7f3c151d3e136d0ec46a97a44a53afbe50c9c35efb7a
      cited_regions:
      - rows
    id: deepseek/deepseek-v3-1#arena_sc_french#c169d67eca40
  - benchmark_id: arena_sc_polish
    model_id_as_evaluated: deepseek-v3.1
    score: 1400.4928686803462
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: evaluated
    observed_at: '2026-09-30'
    verified_at: '2026-09-30'
    benchmark_version: ''
    configuration: ''
    limitations: ''
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:97e2e1ee9652b13516342dcba0cf4472957d6b7e4a17134aafdf774b2d57516d
      cited_regions:
      - rows
    id: deepseek/deepseek-v3-1#arena_sc_polish#f2b4ee283a5c
  - benchmark_id: arena_sc_industry_software_it_services
    model_id_as_evaluated: deepseek-v3.1
    score: 1444.0107344817718
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: evaluated
    observed_at: '2026-09-30'
    verified_at: '2026-09-30'
    benchmark_version: ''
    configuration: ''
    limitations: ''
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:eea47e91c8bc87fe0b61f2a3c0e4eba132c33a7b65597a78092fce12744d989a
      cited_regions:
      - rows
    id: deepseek/deepseek-v3-1#arena_sc_industry_software_it_services#d079a7bd053e
  - benchmark_id: arena_sc_industry_entertainment_sports_media
    model_id_as_evaluated: deepseek-v3.1
    score: 1377.0604549081636
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: evaluated
    observed_at: '2026-09-30'
    verified_at: '2026-09-30'
    benchmark_version: ''
    configuration: ''
    limitations: ''
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:dd31fbcb0b964ee4faa128a3bcac1f1ad740ec5fa6755b63a7cdd8654950bf11
      cited_regions:
      - rows
    id: deepseek/deepseek-v3-1#arena_sc_industry_entertainment_sports_media#e39cb917fb85
  - benchmark_id: arena_sc_industry_mathematical
    model_id_as_evaluated: deepseek-v3.1
    score: 1412.065051775985
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: evaluated
    observed_at: '2026-09-30'
    verified_at: '2026-09-30'
    benchmark_version: ''
    configuration: ''
    limitations: ''
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:6061abfc8f62e0094fea0e87ea00b13d5f43d12e35990052572243771c51f1db
      cited_regions:
      - rows
    id: deepseek/deepseek-v3-1#arena_sc_industry_mathematical#09005e9159ee
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
  api_tps_input: null
  context_speed_degradation: ''
  generation_time_sec: null
  quality_per_dollar: null
  quality_per_watt: null
adoption:
  huggingface_downloads: 141505
  huggingface_likes: 819
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
  huggingface_url: https://huggingface.co/deepseek-ai/DeepSeek-V3.1
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
facts:
- facet: model.class
  value: text-generator
  state: known
  sources:
  - source_id: model-163-deepseek-deepseek-v3-1
    snapshot_ref: sha256:dcb317340f6f0ae5146c99b0f0062c1c9781d330997901254ff0c18a5b35a918
    cited_regions:
    - model-spec
  checked_sources: []
- facet: model.input_modalities
  value: null
  state: not_disclosed
  sources:
  - source_id: model-163-deepseek-deepseek-v3-1
    snapshot_ref: sha256:dcb317340f6f0ae5146c99b0f0062c1c9781d330997901254ff0c18a5b35a918
    cited_regions:
    - model-spec
  checked_sources:
  - model-163-deepseek-deepseek-v3-1
- facet: model.output_modalities
  value: null
  state: not_disclosed
  sources:
  - source_id: model-163-deepseek-deepseek-v3-1
    snapshot_ref: sha256:dcb317340f6f0ae5146c99b0f0062c1c9781d330997901254ff0c18a5b35a918
    cited_regions:
    - model-spec
  checked_sources:
  - model-163-deepseek-deepseek-v3-1
- facet: model.context_window
  value: null
  state: not_disclosed
  sources:
  - source_id: model-163-deepseek-deepseek-v3-1
    snapshot_ref: sha256:dcb317340f6f0ae5146c99b0f0062c1c9781d330997901254ff0c18a5b35a918
    cited_regions:
    - model-spec
  checked_sources:
  - model-163-deepseek-deepseek-v3-1
- facet: model.max_output_tokens
  value: null
  state: not_disclosed
  sources:
  - source_id: model-163-deepseek-deepseek-v3-1
    snapshot_ref: sha256:dcb317340f6f0ae5146c99b0f0062c1c9781d330997901254ff0c18a5b35a918
    cited_regions:
    - model-spec
  checked_sources:
  - model-163-deepseek-deepseek-v3-1
- facet: model.weights_openness
  value: open_weights
  state: known
  sources:
  - source_id: model-163-deepseek-deepseek-v3-1
    snapshot_ref: sha256:dcb317340f6f0ae5146c99b0f0062c1c9781d330997901254ff0c18a5b35a918
    cited_regions:
    - model-spec
  checked_sources: []
- facet: licence.commercial_use
  value: null
  state: not_disclosed
  sources:
  - source_id: model-163-deepseek-deepseek-v3-1
    snapshot_ref: sha256:dcb317340f6f0ae5146c99b0f0062c1c9781d330997901254ff0c18a5b35a918
    cited_regions:
    - model-spec
  checked_sources:
  - model-163-deepseek-deepseek-v3-1
- facet: licence.user_cap
  value: null
  state: not_disclosed
  sources:
  - source_id: model-163-deepseek-deepseek-v3-1
    snapshot_ref: sha256:dcb317340f6f0ae5146c99b0f0062c1c9781d330997901254ff0c18a5b35a918
    cited_regions:
    - model-spec
  checked_sources:
  - model-163-deepseek-deepseek-v3-1
- facet: licence.output_training
  value: null
  state: not_disclosed
  sources:
  - source_id: model-163-deepseek-deepseek-v3-1
    snapshot_ref: sha256:dcb317340f6f0ae5146c99b0f0062c1c9781d330997901254ff0c18a5b35a918
    cited_regions:
    - model-spec
  checked_sources:
  - model-163-deepseek-deepseek-v3-1
- facet: licence.fine_tuning
  value: null
  state: not_disclosed
  sources:
  - source_id: model-163-deepseek-deepseek-v3-1
    snapshot_ref: sha256:dcb317340f6f0ae5146c99b0f0062c1c9781d330997901254ff0c18a5b35a918
    cited_regions:
    - model-spec
  checked_sources:
  - model-163-deepseek-deepseek-v3-1
- facet: origin.lab_jurisdiction
  value: null
  state: not_disclosed
  sources:
  - source_id: model-163-deepseek-deepseek-v3-1
    snapshot_ref: sha256:dcb317340f6f0ae5146c99b0f0062c1c9781d330997901254ff0c18a5b35a918
    cited_regions:
    - model-spec
  checked_sources:
  - model-163-deepseek-deepseek-v3-1
- facet: origin.base_lineage
  value: null
  state: not_disclosed
  sources:
  - source_id: model-163-deepseek-deepseek-v3-1
    snapshot_ref: sha256:dcb317340f6f0ae5146c99b0f0062c1c9781d330997901254ff0c18a5b35a918
    cited_regions:
    - model-spec
  checked_sources:
  - model-163-deepseek-deepseek-v3-1
- facet: origin.weights_hosting
  value: null
  state: not_disclosed
  sources:
  - source_id: model-163-deepseek-deepseek-v3-1
    snapshot_ref: sha256:dcb317340f6f0ae5146c99b0f0062c1c9781d330997901254ff0c18a5b35a918
    cited_regions:
    - model-spec
  checked_sources:
  - model-163-deepseek-deepseek-v3-1
- facet: model.release_date
  value: null
  state: not_disclosed
  sources:
  - source_id: model-163-deepseek-deepseek-v3-1
    snapshot_ref: sha256:dcb317340f6f0ae5146c99b0f0062c1c9781d330997901254ff0c18a5b35a918
    cited_regions:
    - model-spec
  checked_sources:
  - model-163-deepseek-deepseek-v3-1
- facet: model.lifecycle
  value: active
  state: known
  sources:
  - source_id: model-163-deepseek-deepseek-v3-1
    snapshot_ref: sha256:dcb317340f6f0ae5146c99b0f0062c1c9781d330997901254ff0c18a5b35a918
    cited_regions:
    - model-spec
  checked_sources: []
- facet: feature.tool_calling
  value: true
  state: known
  sources:
  - source_id: model-163-deepseek-deepseek-v3-1
    snapshot_ref: sha256:dcb317340f6f0ae5146c99b0f0062c1c9781d330997901254ff0c18a5b35a918
    cited_regions:
    - model-spec
  checked_sources: []
- facet: feature.structured_output
  value: null
  state: not_disclosed
  sources:
  - source_id: model-163-deepseek-deepseek-v3-1
    snapshot_ref: sha256:dcb317340f6f0ae5146c99b0f0062c1c9781d330997901254ff0c18a5b35a918
    cited_regions:
    - model-spec
  checked_sources:
  - model-163-deepseek-deepseek-v3-1
- facet: feature.effort_controls
  value: true
  state: known
  sources:
  - source_id: model-163-deepseek-deepseek-v3-1
    snapshot_ref: sha256:dcb317340f6f0ae5146c99b0f0062c1c9781d330997901254ff0c18a5b35a918
    cited_regions:
    - model-spec
  checked_sources: []
- facet: feature.batch
  value: null
  state: not_disclosed
  sources:
  - source_id: model-163-deepseek-deepseek-v3-1
    snapshot_ref: sha256:dcb317340f6f0ae5146c99b0f0062c1c9781d330997901254ff0c18a5b35a918
    cited_regions:
    - model-spec
  checked_sources:
  - model-163-deepseek-deepseek-v3-1
- facet: feature.streaming
  value: null
  state: not_disclosed
  sources:
  - source_id: model-163-deepseek-deepseek-v3-1
    snapshot_ref: sha256:dcb317340f6f0ae5146c99b0f0062c1c9781d330997901254ff0c18a5b35a918
    cited_regions:
    - model-spec
  checked_sources:
  - model-163-deepseek-deepseek-v3-1
- id: deepseek/deepseek-v3-1#model.parameters_total
  subject:
    kind: model
    id: deepseek/deepseek-v3-1
  facet: model.parameters_total
  value: 684531386000
  state: known
  sources:
  - source_id: model-174-deepseek-deepseek-v3-1-hardware-input
    snapshot_ref: sha256:810786557e756a6c95d9c0d444ad0ed7cb2b9c7301fcf80649486fcebe223ae1
    cited_regions:
    - rows
- id: deepseek/deepseek-v3-1#model.fits_hardware
  subject:
    kind: model
    id: deepseek/deepseek-v3-1
  facet: model.fits_hardware
  value:
  - apple_m3_ultra
  state: known
  derivation:
    method: decision.hardware.compute_fit@1
    formula: parameters_total * bytes_per_parameter <= memory_capacity_gb * (1 - working_allowance) *
      1e9
    inputs:
      weights_openness: open_weights
      parameters_total: 684531386000
      working_allowance: 0.25
      quant_bytes: '{''bf16'': 2.0, ''fp16'': 2.0, ''fp8'': 1.0, ''int4'': 0.5, ''int8'': 1.0, ''q4'':
        0.5, ''q5'': 0.625, ''q6'': 0.75}'
      has_device_unknowns: 'true'
      model_snapshot_ref: sha256:810786557e756a6c95d9c0d444ad0ed7cb2b9c7301fcf80649486fcebe223ae1
      hardware_registry_sha256: sha256:10baf5e1ce9e5a1e5b970f4fdc25d9f67db8c562c8c109157ae9722bf6357bff
      hardware_device_count: 64
  sources:
  - source_id: model-174-deepseek-deepseek-v3-1-hardware-input
    snapshot_ref: sha256:810786557e756a6c95d9c0d444ad0ed7cb2b9c7301fcf80649486fcebe223ae1
    cited_regions:
    - rows
- id: deepseek/deepseek-v3-1#model.hardware_fit_indeterminate
  subject:
    kind: model
    id: deepseek/deepseek-v3-1
  facet: model.hardware_fit_indeterminate
  value:
  - cerebras_wse3
  - nvidia_vera_rubin_superchip
  state: known
  sources:
  - source_id: model-174-deepseek-deepseek-v3-1-hardware-input
    snapshot_ref: sha256:810786557e756a6c95d9c0d444ad0ed7cb2b9c7301fcf80649486fcebe223ae1
    cited_regions:
    - rows
  derivation:
    method: decision.hardware.compute_fit@1
    formula: parameters_total * bytes_per_parameter <= memory_capacity_gb * (1 - working_allowance) *
      1e9
    inputs:
      weights_openness: open_weights
      parameters_total: 684531386000
      working_allowance: 0.25
      quant_bytes: '{''bf16'': 2.0, ''fp16'': 2.0, ''fp8'': 1.0, ''int4'': 0.5, ''int8'': 1.0, ''q4'':
        0.5, ''q5'': 0.625, ''q6'': 0.75}'
      has_device_unknowns: 'true'
      model_snapshot_ref: sha256:810786557e756a6c95d9c0d444ad0ed7cb2b9c7301fcf80649486fcebe223ae1
      hardware_registry_sha256: sha256:10baf5e1ce9e5a1e5b970f4fdc25d9f67db8c562c8c109157ae9722bf6357bff
      hardware_device_count: 64
card_schema_version: '3.0'
card_author: huggingface-seeder
card_created: '2026-04-05'
card_updated: '2026-09-28'
authoring_guide:
  applies_to:
    model_id: deepseek/deepseek-v3-1
    version: ''
  as_of: '2026-09-18'
  status: current
  sections:
    prompt_shape:
    - text: 'Hybrid thinking: the chat template prefix selects the mode. Non-thinking first turn ends
        the assistant header with </think>; thinking first turn uses <think> instead (R1-like).'
      sources:
      - url: https://huggingface.co/deepseek-ai/DeepSeek-V3.1
        title: DeepSeek-V3.1 model card
        accessed: '2026-09-18'
        kind: model-docs
    system_message: []
    reasoning_and_tools:
    - text: In multi-turn context, drop the previous thinking span but keep </think> on every turn. Tool-calling
        is documented for non-thinking mode, with tool descriptions in the system prompt.
      sources:
      - url: https://huggingface.co/deepseek-ai/DeepSeek-V3.1
        title: DeepSeek-V3.1 model card
        accessed: '2026-09-18'
        kind: model-docs
    formatting:
    - text: Unlike V3, non-thinking mode on V3.1 inserts an extra </think> after the assistant header.
        apply_chat_template takes thinking=True/False.
      sources:
      - url: https://huggingface.co/deepseek-ai/DeepSeek-V3.1
        title: DeepSeek-V3.1 model card
        accessed: '2026-09-18'
        kind: model-docs
    failure_modes: []
    retry_advice: []
---

# DeepSeek V3.1

Auto-generated from HuggingFace Hub metadata for [deepseek-ai/DeepSeek-V3.1](https://huggingface.co/deepseek-ai/DeepSeek-V3.1).

Licence: mit. Creator LICENSE file https://huggingface.co/deepseek-ai/DeepSeek-V3.1/raw/main/LICENSE (MIT License) and Hub cardData.license mit, read 2026-09-18.
