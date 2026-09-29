---
model_id: meta/muse-spark
display_name: Muse Spark
provider: meta
provider_display: Meta
family: muse
version: spark
release_date: '2026-04-08'
last_updated: '2026-04-08'
status: active
model_type: llm-reasoning
model_subtypes:
- vlm
tags:
- text-generation
pipeline_tag: text-generation
architecture:
  type: null
  total_parameters: 68976653312
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
  open_weights: false
  license_type: null
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
  - image
  - audio
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
    supported: true
    ocr: true
    chart_reading: true
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
    agentic_coding: true
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
    overall: tier-1
    mathematical: true
    logical: true
    scientific: true
    planning: true
    multi_step: true
    chain_of_thought: true
    self_correction: true
    spatial: false
    temporal: false
    causal: true
    think_budget_control: true
  tool_use:
    overall: tier-1
    function_calling: true
    mcp_compatible: false
    parallel_tool_calls: true
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
    available: false
    model_id: ''
    url: https://huggingface.co/
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
    arc_agi_2: 42.5
    charxiv_reasoning: 86.4
    deepsearchqa: 74.8
    healthbench_hard: 42.8
    ipho_2025_theory: 82.6
    frontierscience_research: 38.3
    medxpertqa_multimodal: 78.4
    terminal_bench_2: 59.0
    zerobench: 33.0
  benchmark_source: meta-blog, officechai
  benchmark_as_of: 2026-04
  evidence:
  - benchmark_id: arena_elo_style_control
    model_id_as_evaluated: muse-spark
    score: 1488.05
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / overall, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category overall,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1488.05 [1482.21, 1493.90], 13565
      votes, rank 13.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: meta/muse-spark#arena_elo_style_control#859002e19068
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:bea7ea9d7344aeccaed159b64f2f3aa97e84231d3723b02f9d4a5672b6b889b8
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_coding
    model_id_as_evaluated: muse-spark
    score: 1525.75
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / coding, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category coding,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1525.75 [1515.63, 1535.87], 3771
      votes, rank 19.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: meta/muse-spark#arena_sc_coding#e5ebb1052b6c
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:da249e40e0397ffcd8dd5f738c4c91f9a389869f8ae9e26c425a1187f04c7118
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_hard_prompts
    model_id_as_evaluated: muse-spark
    score: 1504.78
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / hard_prompts, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category hard_prompts,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1504.78 [1497.78, 1511.79], 8738
      votes, rank 19.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: meta/muse-spark#arena_sc_hard_prompts#f56b7e8510fc
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:5a69c3a3a5f23cf6bfd2b0ecae495ec9731f62df889f4147793616588a2d4f8b
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_math
    model_id_as_evaluated: muse-spark
    score: 1460.89
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / math, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category math, leaderboard_publish_date
      2026-09-13; style control. Highest-effort row for the product (effort: default; MODEL-123
      max-effort rule). Rating 1460.89 [1440.98, 1480.81], 857 votes, rank 54.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: meta/muse-spark#arena_sc_math#97766f13c77e
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:41e622d3837a9ab1577d975e3c57ae92db367c09f45606ed1870a32a4591335a
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_creative_writing
    model_id_as_evaluated: muse-spark
    score: 1463.7
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / creative_writing, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category creative_writing,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1463.70 [1449.70, 1477.71], 1948
      votes, rank 20.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: meta/muse-spark#arena_sc_creative_writing#3ea45ace03b5
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:4ca49a5b7efede8e577057d10266b363a837e56331ac79f7540f7da349a3eee5
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_instruction_following
    model_id_as_evaluated: muse-spark
    score: 1463.34
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / instruction_following, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category instruction_following,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1463.34 [1454.11, 1472.56], 4494
      votes, rank 38.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: meta/muse-spark#arena_sc_instruction_following#dc8ae7251c12
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:6bcc35b68ac189cda1a204de4fab84c84fcd9d853dc2c3265e68366133d9093b
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_multi_turn
    model_id_as_evaluated: muse-spark
    score: 1491.31
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / multi_turn, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category multi_turn,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1491.31 [1477.87, 1504.75], 2179
      votes, rank 21.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: meta/muse-spark#arena_sc_multi_turn#900d2292a53b
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:76f93ba07e2611ee096faf4210eb6b965b5b113b375cb5edec5f224be61fc346
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_expert
    model_id_as_evaluated: muse-spark
    score: 1489.93
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / expert, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category expert,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1489.93 [1473.26, 1506.59], 1293
      votes, rank 46.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: meta/muse-spark#arena_sc_expert#a81c6018ff5c
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:ebf8116274f3815b353511b1829bd763a0817e2a0c5d3669072ebd5571271745
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_longer_query
    model_id_as_evaluated: muse-spark
    score: 1474.17
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / longer_query, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category longer_query,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1474.17 [1465.36, 1482.97], 5308
      votes, rank 47.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: meta/muse-spark#arena_sc_longer_query#e736ae7981c1
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:3c7de94587c842e12c134292a7df52a9faafb46f877d184d8f235d5c1d466737
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_non_english
    model_id_as_evaluated: muse-spark
    score: 1476.71
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / non_english, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category non_english,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1476.71 [1469.15, 1484.27], 7097
      votes, rank 16.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: meta/muse-spark#arena_sc_non_english#a941f93d1146
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:47f41bf8222f55644ca4a36db5ad4178546c5d3e2982bcda2dc08798f9776a65
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_medicine
    model_id_as_evaluated: muse-spark
    score: 1503.55
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / industry_medicine_and_healthcare, latest split,
      revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category industry_medicine_and_healthcare,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1503.55 [1483.77, 1523.33], 954 votes,
      rank 11.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: meta/muse-spark#arena_sc_medicine#c720d914208c
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:31163709a3917ed23ec956a2589a6a5ad30924817977652909218ecbbf9a8d0e
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_legal
    model_id_as_evaluated: muse-spark
    score: 1503.34
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / industry_legal_and_government, latest split, revision
      1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category industry_legal_and_government,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1503.34 [1483.68, 1522.99], 973 votes,
      rank 10.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: meta/muse-spark#arena_sc_legal#12cf6c7d4dc8
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:6aec9d4dd9fc82958ffeceea56c977de5d8204f6c62ad5113657b828f9bc55da
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_business
    model_id_as_evaluated: muse-spark
    score: 1489.64
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / industry_business_and_management_and_financial_operations,
      latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category industry_business_and_management_and_financial_operations,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1489.64 [1477.82, 1501.45], 2743
      votes, rank 12.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: meta/muse-spark#arena_sc_business#285dcb841a13
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:ba565a81fbb65e9d13c80776fda09aabedc819d64793b355a5a5fe836212472e
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_science
    model_id_as_evaluated: muse-spark
    score: 1497.12
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / industry_life_and_physical_and_social_science, latest
      split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category industry_life_and_physical_and_social_science,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1497.12 [1484.28, 1509.96], 2264
      votes, rank 24.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: meta/muse-spark#arena_sc_science#33b63e334473
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:dff891db693196c263ad841fcb75cf135a4529936b386a76fc324e6b66bb2d2e
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_writing
    model_id_as_evaluated: muse-spark
    score: 1459.84
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / industry_writing_and_literature_and_language, latest
      split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category industry_writing_and_literature_and_language,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1459.84 [1448.84, 1470.83], 3130
      votes, rank 33.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: meta/muse-spark#arena_sc_writing#2cdd625f9c45
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:451771d6d03dfcdc902ebbb505ce47bfc614e33bde751b42f3be31d89d416086
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_vision
    model_id_as_evaluated: muse-spark
    score: 1293.68
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: vision_style_control / overall, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset vision_style_control, category overall,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1293.68 [1284.32, 1303.04], 5572
      votes, rank 7.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: meta/muse-spark#arena_sc_vision#82779fe1e1c1
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-vision-style-control
      snapshot_ref: sha256:9da6b0bec36701b281c5b1b1e49bed1a536c78908b3d186f41a551360cb584c4
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: gpqa_diamond
    model_id_as_evaluated: muse-spark
    score: 89.8
    unit: percent
    source_url: https://epoch.ai/benchmarks/gpqa-diamond
    source_kind: independent_evaluator
    evidence_date: '2026-04-08'
    date_type: evaluated
    verified_at: '2026-09-29'
    benchmark_version: GPQA Diamond (Epoch AI run)
    configuration: Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (gpqa_diamond.csv),
      read 2026-09-24. Run started 2026-04-08T16:29:51.099Z; effort default; highest-effort
      run for the model (MODEL-123 max-effort rule), newest on a tie. Standard error 2.20 points.
    limitations: Epoch AI data, CC BY 4.0.
    id: meta/muse-spark#gpqa_diamond#2bc372676afe
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-143-evidence-epoch-gpqa-diamond-csv
      snapshot_ref: sha256:39583bb153c2d06652ef7e4886b645abb7ea53fe3b7bb6c8aaeccef4055705cb
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: hle
    model_id_as_evaluated: Muse Spark
    score: 40.56
    unit: percent
    source_url: https://labs.scale.com/leaderboard/humanitys_last_exam
    source_kind: independent_evaluator
    evidence_date: '2026-09-29'
    date_type: evaluated
    verified_at: '2026-09-29'
    benchmark_version: Humanity's Last Exam, Scale Labs leaderboard
    configuration: Scale Labs leaderboard entry read 2026-09-24; entry created 2026-04-08T16:57:23.000Z;
      effort default; ±1.92 (95% CI).
    limitations: 'Potential contamination warning: This model was evaluated after the public
      release of HLE, allowing model builder access to the prompts and solutions.'
    id: meta/muse-spark#hle#df4eed74027c
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-143-evidence-scale-hle-json
      snapshot_ref: sha256:ed69749324d707d71cd52ecfd30482b055235387a614e3d1003638c23d35e300
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: swe_bench_pro
    model_id_as_evaluated: Muse Spark*
    score: 55.0
    unit: percent
    source_url: https://labs.scale.com/leaderboard/swe_bench_pro_public
    source_kind: independent_evaluator
    evidence_date: '2026-04-08'
    date_type: evaluated
    verified_at: '2026-09-29'
    benchmark_version: SWE-Bench Pro, public dataset, Scale Labs leaderboard
    configuration: 'Scale Labs leaderboard entry read 2026-09-24; entry created 2026-04-08T17:04:49.000Z;
      effort default; ±3.6 (95% CI). Harness: mini-swe-agent (the board marks mini-swe-agent
      runs with an asterisk).'
    limitations: ''
    id: meta/muse-spark#swe_bench_pro#0ea81c2cbb4b
    measured_by: independent_evaluator
    effort: null
    harness: unregistered
    sources:
    - source_id: model-160-scale-swe-bench-pro-public
      snapshot_ref: sha256:c05db8e5781b1f9db1bf944dd4c94cee212f6827a10a5d8c39db0b29a3bb0338
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_english
    model_id_as_evaluated: muse-spark
    score: 1495.49
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / english, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1495.49 [1487.71,
      1503.26], 6468 votes, rank 11. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:cee57baa7239c5aa2091dcb5db0b4c2ac22cec732b235d66c0cda2ee55bdcb44
      cited_regions:
      - rows
    id: meta/muse-spark#arena_sc_english#35d995ec9863
  - benchmark_id: arena_sc_chinese
    model_id_as_evaluated: muse-spark
    score: 1520.52
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / chinese, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1520.52 [1499.17,
      1541.86], 849 votes, rank 25. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:9bf00fc37e8a997735f423949aba6ffc5551990b6f835297d3fed2b364abe02b
      cited_regions:
      - rows
    id: meta/muse-spark#arena_sc_chinese#163a66e8d10e
  - benchmark_id: arena_sc_korean
    model_id_as_evaluated: muse-spark
    score: 1473.94
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / korean, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1473.94 [1434.54,
      1513.33], 248 votes, rank 8. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:96706e685de18541b6ad515db22607a7840bad8bc902a30a8a38f949cd409c08
      cited_regions:
      - rows
    id: meta/muse-spark#arena_sc_korean#3a5a65564203
  - benchmark_id: arena_sc_russian
    model_id_as_evaluated: muse-spark
    score: 1481.46
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / russian, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1481.46 [1465.61,
      1497.32], 1468 votes, rank 28. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:eb77af068077fa90a9514ad454b6a65f061a176f0d68897132e1526f3be743dd
      cited_regions:
      - rows
    id: meta/muse-spark#arena_sc_russian#89b619898d8f
  - benchmark_id: arena_sc_spanish
    model_id_as_evaluated: muse-spark
    score: 1480.99
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / spanish, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1480.99 [1453.69,
      1508.28], 500 votes, rank 11. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:e56e27431afb859f3376e3d5609785906e24647b4c0c65a324b7995944b9573b
      cited_regions:
      - rows
    id: meta/muse-spark#arena_sc_spanish#44acbef2acd1
  - benchmark_id: arena_sc_german
    model_id_as_evaluated: muse-spark
    score: 1509.49
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / german, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1509.49 [1469.68,
      1549.29], 235 votes, rank 4. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:098d6730e0b426da68eee86ddfd97bb03c3b1048e178378de1ec3924fa209c6d
      cited_regions:
      - rows
    id: meta/muse-spark#arena_sc_german#382c4f178378
  - benchmark_id: arena_sc_french
    model_id_as_evaluated: muse-spark
    score: 1525.65
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / french, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1525.65 [1496.81,
      1554.49], 470 votes, rank 2. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:c6c9f83eb7147bedac479a445a3803aad09d613643414d3cd5035dbde46d6f2f
      cited_regions:
      - rows
    id: meta/muse-spark#arena_sc_french#b7b549cc6dcc
  - benchmark_id: arena_sc_polish
    model_id_as_evaluated: muse-spark
    score: 1481.97
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / polish, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1481.97 [1448.63,
      1515.30], 310 votes, rank 22. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:a99daf2dc2fbf9b06de90a127cc1408c7a19e4fa45a1a4d538b668211c4b5892
      cited_regions:
      - rows
    id: meta/muse-spark#arena_sc_polish#3304daf60b39
  - benchmark_id: arena_sc_vision_ocr
    model_id_as_evaluated: muse-spark
    score: 1301.8
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: vision_style_control / ocr, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1301.80 [1291.61,
      1311.99], 4009 votes, rank 11. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-vision-style-control
      snapshot_ref: sha256:72ff33856df7c05e7611f78bd6f0a13fc422694ad107f25e00c11b10edb14422
      cited_regions:
      - rows
    id: meta/muse-spark#arena_sc_vision_ocr#29e22238bf38
  - benchmark_id: arena_sc_vision_diagram
    model_id_as_evaluated: muse-spark
    score: 1312.46
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: vision_style_control / diagram, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1312.46 [1296.81,
      1328.10], 1519 votes, rank 19. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-vision-style-control
      snapshot_ref: sha256:f70ad4aae81aa8b6cca27735001f45704e13f64af12ad93244cd19ca60d98085
      cited_regions:
      - rows
    id: meta/muse-spark#arena_sc_vision_diagram#b8b0cb724957
  - benchmark_id: arena_sc_vision_homework
    model_id_as_evaluated: muse-spark
    score: 1299.97
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: vision_style_control / homework, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1299.97 [1280.28,
      1319.66], 913 votes, rank 28. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-vision-style-control
      snapshot_ref: sha256:8015c65e88084d6c6b25f9787fb1528f550abd8e055cf8f3b753e863296d3176
      cited_regions:
      - rows
    id: meta/muse-spark#arena_sc_vision_homework#d7539cad61cb
  - benchmark_id: arena_sc_document
    model_id_as_evaluated: muse-spark
    score: 1444.19
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: document / overall, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1444.19 [1425.90,
      1462.48], 1084 votes, rank 29. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-document
      snapshot_ref: sha256:050705ac3c2e5ba81aacf700b87f5144dd7b0ec9f7f12168be5086b1c11be958
      cited_regions:
      - rows
    id: meta/muse-spark#arena_sc_document#37947d26e290
  - benchmark_id: arena_sc_industry_software_it_services
    model_id_as_evaluated: muse-spark
    score: 1520.06
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / industry_software_and_it_services, latest split, revision
      1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1520.06 [1511.51,
      1528.61], 5318 votes, rank 13. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:4eaa9890dce0719aa263af890c9f2a7bb1a3198e291d84dbf8c1371d4f150c52
      cited_regions:
      - rows
    id: meta/muse-spark#arena_sc_industry_software_it_services#4a82ec8fe77f
  - benchmark_id: arena_sc_industry_entertainment_sports_media
    model_id_as_evaluated: muse-spark
    score: 1462.19
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / industry_entertainment_and_sports_and_media, latest
      split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1462.19 [1449.89,
      1474.48], 2510 votes, rank 14. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:df0d5e7c4d4ce1f683618242c0786eafd164d98b3b49dbaa6e699476bec94ccf
      cited_regions:
      - rows
    id: meta/muse-spark#arena_sc_industry_entertainment_sports_media#c2cb9df20e34
  - benchmark_id: arena_sc_industry_mathematical
    model_id_as_evaluated: muse-spark
    score: 1468.67
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / industry_mathematical, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1468.67 [1447.87,
      1489.47], 819 votes, rank 52. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:b0f3ee924239a7a9a1e60676935d0c83091f29517b8acb95e07868e370822e82
      cited_regions:
      - rows
    id: meta/muse-spark#arena_sc_industry_mathematical#ac70335210e6
  - benchmark_id: arena_sc_factuality
    model_id_as_evaluated: muse-spark
    score: 1466.77
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_factuality / overall, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1466.77 [1461.24,
      1472.30], 13548 votes, rank 30. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-factuality
      snapshot_ref: sha256:ece0fd0afe2b42a38bce698a6be5329044b5503f5edb7f43473c19394b38fc28
      cited_regions:
      - rows
    id: meta/muse-spark#arena_sc_factuality#1afc7de69ce1
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
  huggingface_downloads: 26174
  huggingface_likes: 2205
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
  huggingface_url: https://huggingface.co/meta-llama/Llama-2-70b-chat-hf
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
facts:
- facet: model.class
  value: text-generator
  state: known
  sources:
  - source_id: model-143-meta-muse-spark
    snapshot_ref: sha256:804c2c88e8424231fcf3e8406d4e3707a8166f1622b6ce70805e9f9b6593424a
    cited_regions:
    - model-spec
  - source_id: model-143-meta-release-index
    snapshot_ref: sha256:bcde843202fd01598bfc74c3adeb5b59df1713f0e4c07784728e5c941691895a
    cited_regions:
    - audit
  - source_id: model-143-meta-model-api
    snapshot_ref: sha256:e6306b281f9b3d01d0c83c4c662af0dc8613f1e67138906f112cb24fbea30d2a
    cited_regions:
    - audit
  - source_id: model-143-meta-company
    snapshot_ref: sha256:fcf8283f72c1376dc97cd49a2776df3b6c7608b6f76844ac86c67fa89f497e3f
    cited_regions:
    - audit
  - source_id: model-143-meta-sec
    snapshot_ref: sha256:7627db9dbf44d398db1726ca661ff7222dcbd76bc768ddec13815ab9b9fbd07e
    cited_regions:
    - audit
- facet: model.input_modalities
  value:
  - text
  - image
  - audio
  state: known
  sources:
  - source_id: model-143-meta-muse-spark
    snapshot_ref: sha256:804c2c88e8424231fcf3e8406d4e3707a8166f1622b6ce70805e9f9b6593424a
    cited_regions:
    - model-spec
  - source_id: model-143-meta-release-index
    snapshot_ref: sha256:bcde843202fd01598bfc74c3adeb5b59df1713f0e4c07784728e5c941691895a
    cited_regions:
    - audit
  - source_id: model-143-meta-model-api
    snapshot_ref: sha256:e6306b281f9b3d01d0c83c4c662af0dc8613f1e67138906f112cb24fbea30d2a
    cited_regions:
    - audit
  - source_id: model-143-meta-company
    snapshot_ref: sha256:fcf8283f72c1376dc97cd49a2776df3b6c7608b6f76844ac86c67fa89f497e3f
    cited_regions:
    - audit
  - source_id: model-143-meta-sec
    snapshot_ref: sha256:7627db9dbf44d398db1726ca661ff7222dcbd76bc768ddec13815ab9b9fbd07e
    cited_regions:
    - audit
- facet: model.output_modalities
  value:
  - text
  state: known
  sources:
  - source_id: model-143-meta-muse-spark
    snapshot_ref: sha256:804c2c88e8424231fcf3e8406d4e3707a8166f1622b6ce70805e9f9b6593424a
    cited_regions:
    - model-spec
  - source_id: model-143-meta-release-index
    snapshot_ref: sha256:bcde843202fd01598bfc74c3adeb5b59df1713f0e4c07784728e5c941691895a
    cited_regions:
    - audit
  - source_id: model-143-meta-model-api
    snapshot_ref: sha256:e6306b281f9b3d01d0c83c4c662af0dc8613f1e67138906f112cb24fbea30d2a
    cited_regions:
    - audit
  - source_id: model-143-meta-company
    snapshot_ref: sha256:fcf8283f72c1376dc97cd49a2776df3b6c7608b6f76844ac86c67fa89f497e3f
    cited_regions:
    - audit
  - source_id: model-143-meta-sec
    snapshot_ref: sha256:7627db9dbf44d398db1726ca661ff7222dcbd76bc768ddec13815ab9b9fbd07e
    cited_regions:
    - audit
- facet: model.context_window
  value: 8192
  state: known
  sources:
  - source_id: model-143-meta-muse-spark
    snapshot_ref: sha256:804c2c88e8424231fcf3e8406d4e3707a8166f1622b6ce70805e9f9b6593424a
    cited_regions:
    - model-spec
  - source_id: model-143-meta-release-index
    snapshot_ref: sha256:bcde843202fd01598bfc74c3adeb5b59df1713f0e4c07784728e5c941691895a
    cited_regions:
    - audit
  - source_id: model-143-meta-model-api
    snapshot_ref: sha256:e6306b281f9b3d01d0c83c4c662af0dc8613f1e67138906f112cb24fbea30d2a
    cited_regions:
    - audit
  - source_id: model-143-meta-company
    snapshot_ref: sha256:fcf8283f72c1376dc97cd49a2776df3b6c7608b6f76844ac86c67fa89f497e3f
    cited_regions:
    - audit
  - source_id: model-143-meta-sec
    snapshot_ref: sha256:7627db9dbf44d398db1726ca661ff7222dcbd76bc768ddec13815ab9b9fbd07e
    cited_regions:
    - audit
- facet: model.max_output_tokens
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-meta-muse-spark
    snapshot_ref: sha256:804c2c88e8424231fcf3e8406d4e3707a8166f1622b6ce70805e9f9b6593424a
    cited_regions:
    - model-spec
  - source_id: model-143-meta-release-index
    snapshot_ref: sha256:bcde843202fd01598bfc74c3adeb5b59df1713f0e4c07784728e5c941691895a
    cited_regions:
    - audit
  - source_id: model-143-meta-model-api
    snapshot_ref: sha256:e6306b281f9b3d01d0c83c4c662af0dc8613f1e67138906f112cb24fbea30d2a
    cited_regions:
    - audit
  - source_id: model-143-meta-company
    snapshot_ref: sha256:fcf8283f72c1376dc97cd49a2776df3b6c7608b6f76844ac86c67fa89f497e3f
    cited_regions:
    - audit
  - source_id: model-143-meta-sec
    snapshot_ref: sha256:7627db9dbf44d398db1726ca661ff7222dcbd76bc768ddec13815ab9b9fbd07e
    cited_regions:
    - audit
  checked_sources:
  - model-143-meta-muse-spark
  - model-143-meta-release-index
  - model-143-meta-model-api
  - model-143-meta-company
  - model-143-meta-sec
- facet: model.weights_openness
  value: closed_weights
  state: known
  sources:
  - source_id: model-143-meta-muse-spark
    snapshot_ref: sha256:804c2c88e8424231fcf3e8406d4e3707a8166f1622b6ce70805e9f9b6593424a
    cited_regions:
    - model-spec
  - source_id: model-143-meta-release-index
    snapshot_ref: sha256:bcde843202fd01598bfc74c3adeb5b59df1713f0e4c07784728e5c941691895a
    cited_regions:
    - audit
  - source_id: model-143-meta-model-api
    snapshot_ref: sha256:e6306b281f9b3d01d0c83c4c662af0dc8613f1e67138906f112cb24fbea30d2a
    cited_regions:
    - audit
  - source_id: model-143-meta-company
    snapshot_ref: sha256:fcf8283f72c1376dc97cd49a2776df3b6c7608b6f76844ac86c67fa89f497e3f
    cited_regions:
    - audit
  - source_id: model-143-meta-sec
    snapshot_ref: sha256:7627db9dbf44d398db1726ca661ff7222dcbd76bc768ddec13815ab9b9fbd07e
    cited_regions:
    - audit
- facet: licence.commercial_use
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-meta-muse-spark
    snapshot_ref: sha256:804c2c88e8424231fcf3e8406d4e3707a8166f1622b6ce70805e9f9b6593424a
    cited_regions:
    - model-spec
  - source_id: model-143-meta-release-index
    snapshot_ref: sha256:bcde843202fd01598bfc74c3adeb5b59df1713f0e4c07784728e5c941691895a
    cited_regions:
    - audit
  - source_id: model-143-meta-model-api
    snapshot_ref: sha256:e6306b281f9b3d01d0c83c4c662af0dc8613f1e67138906f112cb24fbea30d2a
    cited_regions:
    - audit
  - source_id: model-143-meta-company
    snapshot_ref: sha256:fcf8283f72c1376dc97cd49a2776df3b6c7608b6f76844ac86c67fa89f497e3f
    cited_regions:
    - audit
  - source_id: model-143-meta-sec
    snapshot_ref: sha256:7627db9dbf44d398db1726ca661ff7222dcbd76bc768ddec13815ab9b9fbd07e
    cited_regions:
    - audit
  checked_sources:
  - model-143-meta-muse-spark
  - model-143-meta-release-index
  - model-143-meta-model-api
  - model-143-meta-company
  - model-143-meta-sec
- facet: licence.user_cap
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-meta-muse-spark
    snapshot_ref: sha256:804c2c88e8424231fcf3e8406d4e3707a8166f1622b6ce70805e9f9b6593424a
    cited_regions:
    - model-spec
  - source_id: model-143-meta-release-index
    snapshot_ref: sha256:bcde843202fd01598bfc74c3adeb5b59df1713f0e4c07784728e5c941691895a
    cited_regions:
    - audit
  - source_id: model-143-meta-model-api
    snapshot_ref: sha256:e6306b281f9b3d01d0c83c4c662af0dc8613f1e67138906f112cb24fbea30d2a
    cited_regions:
    - audit
  - source_id: model-143-meta-company
    snapshot_ref: sha256:fcf8283f72c1376dc97cd49a2776df3b6c7608b6f76844ac86c67fa89f497e3f
    cited_regions:
    - audit
  - source_id: model-143-meta-sec
    snapshot_ref: sha256:7627db9dbf44d398db1726ca661ff7222dcbd76bc768ddec13815ab9b9fbd07e
    cited_regions:
    - audit
  checked_sources:
  - model-143-meta-muse-spark
  - model-143-meta-release-index
  - model-143-meta-model-api
  - model-143-meta-company
  - model-143-meta-sec
- facet: licence.output_training
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-meta-muse-spark
    snapshot_ref: sha256:804c2c88e8424231fcf3e8406d4e3707a8166f1622b6ce70805e9f9b6593424a
    cited_regions:
    - model-spec
  - source_id: model-143-meta-release-index
    snapshot_ref: sha256:bcde843202fd01598bfc74c3adeb5b59df1713f0e4c07784728e5c941691895a
    cited_regions:
    - audit
  - source_id: model-143-meta-model-api
    snapshot_ref: sha256:e6306b281f9b3d01d0c83c4c662af0dc8613f1e67138906f112cb24fbea30d2a
    cited_regions:
    - audit
  - source_id: model-143-meta-company
    snapshot_ref: sha256:fcf8283f72c1376dc97cd49a2776df3b6c7608b6f76844ac86c67fa89f497e3f
    cited_regions:
    - audit
  - source_id: model-143-meta-sec
    snapshot_ref: sha256:7627db9dbf44d398db1726ca661ff7222dcbd76bc768ddec13815ab9b9fbd07e
    cited_regions:
    - audit
  checked_sources:
  - model-143-meta-muse-spark
  - model-143-meta-release-index
  - model-143-meta-model-api
  - model-143-meta-company
  - model-143-meta-sec
- facet: licence.fine_tuning
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-meta-muse-spark
    snapshot_ref: sha256:804c2c88e8424231fcf3e8406d4e3707a8166f1622b6ce70805e9f9b6593424a
    cited_regions:
    - model-spec
  - source_id: model-143-meta-release-index
    snapshot_ref: sha256:bcde843202fd01598bfc74c3adeb5b59df1713f0e4c07784728e5c941691895a
    cited_regions:
    - audit
  - source_id: model-143-meta-model-api
    snapshot_ref: sha256:e6306b281f9b3d01d0c83c4c662af0dc8613f1e67138906f112cb24fbea30d2a
    cited_regions:
    - audit
  - source_id: model-143-meta-company
    snapshot_ref: sha256:fcf8283f72c1376dc97cd49a2776df3b6c7608b6f76844ac86c67fa89f497e3f
    cited_regions:
    - audit
  - source_id: model-143-meta-sec
    snapshot_ref: sha256:7627db9dbf44d398db1726ca661ff7222dcbd76bc768ddec13815ab9b9fbd07e
    cited_regions:
    - audit
  checked_sources:
  - model-143-meta-muse-spark
  - model-143-meta-release-index
  - model-143-meta-model-api
  - model-143-meta-company
  - model-143-meta-sec
- facet: origin.lab_jurisdiction
  value:
  - US
  state: known
  sources:
  - source_id: model-143-meta-muse-spark
    snapshot_ref: sha256:804c2c88e8424231fcf3e8406d4e3707a8166f1622b6ce70805e9f9b6593424a
    cited_regions:
    - model-spec
  - source_id: model-143-meta-release-index
    snapshot_ref: sha256:bcde843202fd01598bfc74c3adeb5b59df1713f0e4c07784728e5c941691895a
    cited_regions:
    - audit
  - source_id: model-143-meta-model-api
    snapshot_ref: sha256:e6306b281f9b3d01d0c83c4c662af0dc8613f1e67138906f112cb24fbea30d2a
    cited_regions:
    - audit
  - source_id: model-143-meta-company
    snapshot_ref: sha256:fcf8283f72c1376dc97cd49a2776df3b6c7608b6f76844ac86c67fa89f497e3f
    cited_regions:
    - audit
  - source_id: model-143-meta-sec
    snapshot_ref: sha256:7627db9dbf44d398db1726ca661ff7222dcbd76bc768ddec13815ab9b9fbd07e
    cited_regions:
    - audit
- facet: origin.base_lineage
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-meta-muse-spark
    snapshot_ref: sha256:804c2c88e8424231fcf3e8406d4e3707a8166f1622b6ce70805e9f9b6593424a
    cited_regions:
    - model-spec
  - source_id: model-143-meta-release-index
    snapshot_ref: sha256:bcde843202fd01598bfc74c3adeb5b59df1713f0e4c07784728e5c941691895a
    cited_regions:
    - audit
  - source_id: model-143-meta-model-api
    snapshot_ref: sha256:e6306b281f9b3d01d0c83c4c662af0dc8613f1e67138906f112cb24fbea30d2a
    cited_regions:
    - audit
  - source_id: model-143-meta-company
    snapshot_ref: sha256:fcf8283f72c1376dc97cd49a2776df3b6c7608b6f76844ac86c67fa89f497e3f
    cited_regions:
    - audit
  - source_id: model-143-meta-sec
    snapshot_ref: sha256:7627db9dbf44d398db1726ca661ff7222dcbd76bc768ddec13815ab9b9fbd07e
    cited_regions:
    - audit
  checked_sources:
  - model-143-meta-muse-spark
  - model-143-meta-release-index
  - model-143-meta-model-api
  - model-143-meta-company
  - model-143-meta-sec
- facet: origin.weights_hosting
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-meta-muse-spark
    snapshot_ref: sha256:804c2c88e8424231fcf3e8406d4e3707a8166f1622b6ce70805e9f9b6593424a
    cited_regions:
    - model-spec
  - source_id: model-143-meta-release-index
    snapshot_ref: sha256:bcde843202fd01598bfc74c3adeb5b59df1713f0e4c07784728e5c941691895a
    cited_regions:
    - audit
  - source_id: model-143-meta-model-api
    snapshot_ref: sha256:e6306b281f9b3d01d0c83c4c662af0dc8613f1e67138906f112cb24fbea30d2a
    cited_regions:
    - audit
  - source_id: model-143-meta-company
    snapshot_ref: sha256:fcf8283f72c1376dc97cd49a2776df3b6c7608b6f76844ac86c67fa89f497e3f
    cited_regions:
    - audit
  - source_id: model-143-meta-sec
    snapshot_ref: sha256:7627db9dbf44d398db1726ca661ff7222dcbd76bc768ddec13815ab9b9fbd07e
    cited_regions:
    - audit
  checked_sources:
  - model-143-meta-muse-spark
  - model-143-meta-release-index
  - model-143-meta-model-api
  - model-143-meta-company
  - model-143-meta-sec
- facet: model.release_date
  value: '2026-04-08'
  state: known
  sources:
  - source_id: model-143-meta-muse-spark
    snapshot_ref: sha256:804c2c88e8424231fcf3e8406d4e3707a8166f1622b6ce70805e9f9b6593424a
    cited_regions:
    - model-spec
  - source_id: model-143-meta-release-index
    snapshot_ref: sha256:bcde843202fd01598bfc74c3adeb5b59df1713f0e4c07784728e5c941691895a
    cited_regions:
    - audit
  - source_id: model-143-meta-model-api
    snapshot_ref: sha256:e6306b281f9b3d01d0c83c4c662af0dc8613f1e67138906f112cb24fbea30d2a
    cited_regions:
    - audit
  - source_id: model-143-meta-company
    snapshot_ref: sha256:fcf8283f72c1376dc97cd49a2776df3b6c7608b6f76844ac86c67fa89f497e3f
    cited_regions:
    - audit
  - source_id: model-143-meta-sec
    snapshot_ref: sha256:7627db9dbf44d398db1726ca661ff7222dcbd76bc768ddec13815ab9b9fbd07e
    cited_regions:
    - audit
- facet: model.lifecycle
  value: active
  state: known
  sources:
  - source_id: model-143-meta-muse-spark
    snapshot_ref: sha256:804c2c88e8424231fcf3e8406d4e3707a8166f1622b6ce70805e9f9b6593424a
    cited_regions:
    - model-spec
  - source_id: model-143-meta-release-index
    snapshot_ref: sha256:bcde843202fd01598bfc74c3adeb5b59df1713f0e4c07784728e5c941691895a
    cited_regions:
    - audit
  - source_id: model-143-meta-model-api
    snapshot_ref: sha256:e6306b281f9b3d01d0c83c4c662af0dc8613f1e67138906f112cb24fbea30d2a
    cited_regions:
    - audit
  - source_id: model-143-meta-company
    snapshot_ref: sha256:fcf8283f72c1376dc97cd49a2776df3b6c7608b6f76844ac86c67fa89f497e3f
    cited_regions:
    - audit
  - source_id: model-143-meta-sec
    snapshot_ref: sha256:7627db9dbf44d398db1726ca661ff7222dcbd76bc768ddec13815ab9b9fbd07e
    cited_regions:
    - audit
- facet: feature.tool_calling
  value: true
  state: known
  sources:
  - source_id: model-143-meta-muse-spark
    snapshot_ref: sha256:804c2c88e8424231fcf3e8406d4e3707a8166f1622b6ce70805e9f9b6593424a
    cited_regions:
    - model-spec
  - source_id: model-143-meta-release-index
    snapshot_ref: sha256:bcde843202fd01598bfc74c3adeb5b59df1713f0e4c07784728e5c941691895a
    cited_regions:
    - audit
  - source_id: model-143-meta-model-api
    snapshot_ref: sha256:e6306b281f9b3d01d0c83c4c662af0dc8613f1e67138906f112cb24fbea30d2a
    cited_regions:
    - audit
  - source_id: model-143-meta-company
    snapshot_ref: sha256:fcf8283f72c1376dc97cd49a2776df3b6c7608b6f76844ac86c67fa89f497e3f
    cited_regions:
    - audit
  - source_id: model-143-meta-sec
    snapshot_ref: sha256:7627db9dbf44d398db1726ca661ff7222dcbd76bc768ddec13815ab9b9fbd07e
    cited_regions:
    - audit
- facet: feature.structured_output
  value: true
  state: known
  sources:
  - source_id: model-143-meta-muse-spark
    snapshot_ref: sha256:804c2c88e8424231fcf3e8406d4e3707a8166f1622b6ce70805e9f9b6593424a
    cited_regions:
    - model-spec
  - source_id: model-143-meta-release-index
    snapshot_ref: sha256:bcde843202fd01598bfc74c3adeb5b59df1713f0e4c07784728e5c941691895a
    cited_regions:
    - audit
  - source_id: model-143-meta-model-api
    snapshot_ref: sha256:e6306b281f9b3d01d0c83c4c662af0dc8613f1e67138906f112cb24fbea30d2a
    cited_regions:
    - audit
  - source_id: model-143-meta-company
    snapshot_ref: sha256:fcf8283f72c1376dc97cd49a2776df3b6c7608b6f76844ac86c67fa89f497e3f
    cited_regions:
    - audit
  - source_id: model-143-meta-sec
    snapshot_ref: sha256:7627db9dbf44d398db1726ca661ff7222dcbd76bc768ddec13815ab9b9fbd07e
    cited_regions:
    - audit
- facet: feature.effort_controls
  value: true
  state: known
  sources:
  - source_id: model-143-meta-muse-spark
    snapshot_ref: sha256:804c2c88e8424231fcf3e8406d4e3707a8166f1622b6ce70805e9f9b6593424a
    cited_regions:
    - model-spec
  - source_id: model-143-meta-release-index
    snapshot_ref: sha256:bcde843202fd01598bfc74c3adeb5b59df1713f0e4c07784728e5c941691895a
    cited_regions:
    - audit
  - source_id: model-143-meta-model-api
    snapshot_ref: sha256:e6306b281f9b3d01d0c83c4c662af0dc8613f1e67138906f112cb24fbea30d2a
    cited_regions:
    - audit
  - source_id: model-143-meta-company
    snapshot_ref: sha256:fcf8283f72c1376dc97cd49a2776df3b6c7608b6f76844ac86c67fa89f497e3f
    cited_regions:
    - audit
  - source_id: model-143-meta-sec
    snapshot_ref: sha256:7627db9dbf44d398db1726ca661ff7222dcbd76bc768ddec13815ab9b9fbd07e
    cited_regions:
    - audit
- facet: feature.batch
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-meta-muse-spark
    snapshot_ref: sha256:804c2c88e8424231fcf3e8406d4e3707a8166f1622b6ce70805e9f9b6593424a
    cited_regions:
    - model-spec
  - source_id: model-143-meta-release-index
    snapshot_ref: sha256:bcde843202fd01598bfc74c3adeb5b59df1713f0e4c07784728e5c941691895a
    cited_regions:
    - audit
  - source_id: model-143-meta-model-api
    snapshot_ref: sha256:e6306b281f9b3d01d0c83c4c662af0dc8613f1e67138906f112cb24fbea30d2a
    cited_regions:
    - audit
  - source_id: model-143-meta-company
    snapshot_ref: sha256:fcf8283f72c1376dc97cd49a2776df3b6c7608b6f76844ac86c67fa89f497e3f
    cited_regions:
    - audit
  - source_id: model-143-meta-sec
    snapshot_ref: sha256:7627db9dbf44d398db1726ca661ff7222dcbd76bc768ddec13815ab9b9fbd07e
    cited_regions:
    - audit
  checked_sources:
  - model-143-meta-muse-spark
  - model-143-meta-release-index
  - model-143-meta-model-api
  - model-143-meta-company
  - model-143-meta-sec
- facet: feature.streaming
  value: true
  state: known
  sources:
  - source_id: model-143-meta-muse-spark
    snapshot_ref: sha256:804c2c88e8424231fcf3e8406d4e3707a8166f1622b6ce70805e9f9b6593424a
    cited_regions:
    - model-spec
  - source_id: model-143-meta-release-index
    snapshot_ref: sha256:bcde843202fd01598bfc74c3adeb5b59df1713f0e4c07784728e5c941691895a
    cited_regions:
    - audit
  - source_id: model-143-meta-model-api
    snapshot_ref: sha256:e6306b281f9b3d01d0c83c4c662af0dc8613f1e67138906f112cb24fbea30d2a
    cited_regions:
    - audit
  - source_id: model-143-meta-company
    snapshot_ref: sha256:fcf8283f72c1376dc97cd49a2776df3b6c7608b6f76844ac86c67fa89f497e3f
    cited_regions:
    - audit
  - source_id: model-143-meta-sec
    snapshot_ref: sha256:7627db9dbf44d398db1726ca661ff7222dcbd76bc768ddec13815ab9b9fbd07e
    cited_regions:
    - audit
- id: meta/muse-spark#model.fits_hardware
  subject:
    kind: model
    id: meta/muse-spark
  facet: model.fits_hardware
  value: []
  state: known
  derivation:
    method: decision.hardware.compute_fit@1
    formula: parameters_total * bytes_per_parameter <= memory_capacity_gb * (1 - working_allowance) *
      1e9
    inputs:
      weights_openness: closed_weights
      parameters_total: null
      working_allowance: 0.25
      quant_bytes: '{''bf16'': 2.0, ''fp16'': 2.0, ''fp8'': 1.0, ''int4'': 0.5, ''int8'': 1.0, ''q4'':
        0.5, ''q5'': 0.625, ''q6'': 0.75}'
      has_device_unknowns: 'false'
      model_snapshot_ref: sha256:804c2c88e8424231fcf3e8406d4e3707a8166f1622b6ce70805e9f9b6593424a
      hardware_registry_sha256: sha256:10baf5e1ce9e5a1e5b970f4fdc25d9f67db8c562c8c109157ae9722bf6357bff
      hardware_device_count: 64
  sources:
  - source_id: model-143-meta-muse-spark
    snapshot_ref: sha256:804c2c88e8424231fcf3e8406d4e3707a8166f1622b6ce70805e9f9b6593424a
    cited_regions:
    - model-spec
  - source_id: model-143-meta-release-index
    snapshot_ref: sha256:bcde843202fd01598bfc74c3adeb5b59df1713f0e4c07784728e5c941691895a
    cited_regions:
    - audit
  - source_id: model-143-meta-model-api
    snapshot_ref: sha256:e6306b281f9b3d01d0c83c4c662af0dc8613f1e67138906f112cb24fbea30d2a
    cited_regions:
    - audit
  - source_id: model-143-meta-company
    snapshot_ref: sha256:fcf8283f72c1376dc97cd49a2776df3b6c7608b6f76844ac86c67fa89f497e3f
    cited_regions:
    - audit
  - source_id: model-143-meta-sec
    snapshot_ref: sha256:7627db9dbf44d398db1726ca661ff7222dcbd76bc768ddec13815ab9b9fbd07e
    cited_regions:
    - audit
card_schema_version: '3.0'
card_author: manual
card_created: '2026-04-08'
card_updated: '2026-09-28'
---


# Muse Spark

Meta's first model from Meta Superintelligence Labs (MSL), led by Alexandr Wang. Natively multimodal reasoning model with tool-use, visual chain of thought, and multi-agent orchestration. Accepts voice, text, and image input; text-only output. Features Instant, Thinking, and Contemplating modes. Powers Meta AI across 3B+ users. First closed-source model from Meta, departing from the Llama open-weights strategy.

Licence: null. The card's Hugging Face URL is meta-llama/Llama-2-70b-chat-hf, which is not this model, and no Muse Spark licence document was found (read 2026-09-18). A known-wrong llama-community default is worse than none.