---
model_id: meta/muse-spark-1-3
display_name: Muse Spark 1.3
provider: meta
provider_display: Meta
family: muse
version: muse-spark-1.3
release_date: '2026-09-02'
last_updated: '2026-09-02'
status: active
model_type: llm-reasoning
model_subtypes:
- vlm
tags:
- text-generation
pipeline_tag: text-generation
architecture:
  type: null
  total_parameters: null
  total_parameters_source: ''
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
  library_name: ''
licensing:
  open_weights: false
  license_type: proprietary
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
  - video
  - audio
  - pdf
  output:
  - text
  text:
    max_input_tokens: null
    max_output_tokens: 131072
    context_window: 1048576
    streaming: true
    fill_in_middle: null
    json_mode: true
    system_prompt: null
  vision:
    supported: true
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
    input_supported: true
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
    input_supported: true
    output_supported: false
    max_input_duration_sec: null
    max_output_duration_sec: null
    max_resolution: ''
    max_fps: null
    audio_sync: false
    temporal_reasoning: false
  document:
    pdf_native: true
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
    think_budget_control: true
  tool_use:
    overall: null
    function_calling: true
    mcp_compatible: false
    parallel_tool_calls: true
    tool_selection_accuracy: null
    multi_turn_tool_use: false
    tool_error_recovery: false
    computer_use: true
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
  input: 1.25
  output: 4.25
  reasoning: null
  cache_read: 0.15
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
  note: USD per 1M tokens, Standard tier model id muse-spark-1.3. Read 2026-09-24
    from https://ai.developer.meta.com/docs/pricing-rate-limits.md. Contributor model
    ids, where Meta publishes them, are a different offering and are not these prices.
availability:
  primary_provider:
    name: Meta Model API
    platform_url: https://ai.developer.meta.com/docs/models.md
    api_endpoint: https://api.meta.ai/v1
    npm_package: ''
    env_vars: []
    model_id_on_platform: muse-spark-1.3
    rate_limit_rpm: 3000
    rate_limit_tpm: 4000000
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
  scores: {}
  evidence:
  - benchmark_id: arena_elo_overall
    model_id_as_evaluated: muse-spark-1.3-max
    score: 1489.74
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-30'
    benchmark_version: text/latest, overall
    configuration: LMArena leaderboard dataset, CC BY 4.0, category overall, leaderboard_publish_date
      2026-09-13, read 2026-09-24. Rank 10, 4723 votes, interval [1480.91, 1498.57].
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC
      BY 4.0.
    id: meta/muse-spark-1-3#arena_elo_overall#823c259bcf5b
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text
      snapshot_ref: sha256:c75f97c00af5cdce1b735cd74bc058988e6afb9d411c400e70b3420557519012
      cited_regions:
      - rows
    interval:
    - 1480.91
    - 1498.57
    n: 4723
    observed_at: '2026-09-30'
  - benchmark_id: arena_elo_vision
    model_id_as_evaluated: muse-spark-1.3-max
    score: 1314.56
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-30'
    benchmark_version: vision/latest, overall
    configuration: LMArena leaderboard dataset, CC BY 4.0, category overall, leaderboard_publish_date
      2026-09-13, read 2026-09-24. Rank 8, 1804 votes, interval [1299.74, 1329.38].
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC
      BY 4.0.
    id: meta/muse-spark-1-3#arena_elo_vision#673d2dfdef97
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-vision
      snapshot_ref: sha256:529f825984ddc66837a82102819fab3e444034339aed09edf82560297ddf57d2
      cited_regions:
      - rows
    observed_at: '2026-09-30'
  - benchmark_id: arena_webdev
    model_id_as_evaluated: muse-spark-1.3-max
    score: 1658.22
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-23'
    date_type: published
    verified_at: '2026-09-30'
    benchmark_version: webdev/latest, overall
    configuration: LMArena leaderboard dataset, CC BY 4.0, category overall, leaderboard_publish_date
      2026-09-23, read 2026-09-24. Rank 10, 5342 votes, interval [1648.65, 1667.78].
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC
      BY 4.0.
    id: meta/muse-spark-1-3#arena_webdev#3f3d7fdf0fbe
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-143-evidence-arena-webdev-json
      snapshot_ref: sha256:31b3d323e3968c31c3238ed5782c805c2ae4be8758520c2e6837e2f3cb7633cb
      cited_regions:
      - rows
    observed_at: '2026-09-30'
  - benchmark_id: arena_webdev
    model_id_as_evaluated: muse-spark-1.3 (xHigh)
    score: 1626.2
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-23'
    date_type: published
    verified_at: '2026-09-30'
    benchmark_version: webdev/latest, overall
    configuration: LMArena leaderboard dataset, CC BY 4.0, category overall, leaderboard_publish_date
      2026-09-23, read 2026-09-24. Rank 15, 4391 votes, interval [1616.13, 1636.27].
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC
      BY 4.0.
    id: meta/muse-spark-1-3#arena_webdev#b375a0e5e4d2
    measured_by: independent_evaluator
    effort: xhigh
    harness: null
    sources:
    - source_id: model-143-evidence-arena-webdev-json
      snapshot_ref: sha256:31b3d323e3968c31c3238ed5782c805c2ae4be8758520c2e6837e2f3cb7633cb
      cited_regions:
      - rows
    observed_at: '2026-09-30'
  - benchmark_id: cursorbench_4
    model_id_as_evaluated: Muse Spark 1.3
    score: 41.6
    unit: percent
    source_url: https://cursor.com/cursorbench
    source_kind: benchmark_author
    evidence_date: '2026-09-30'
    date_type: evaluated
    verified_at: '2026-09-30'
    benchmark_version: CursorBench 4.0
    configuration: Cursor's CursorBench 4.0 board read 2026-09-25; the board states no row date,
      so the reading is dated by the observation. Highest-effort row (max); $2.64 a task.
    limitations: Runs only in Cursor's production agent harness.
    effort: max
    harness: null
    measured_by: benchmark_author
    sources:
    - source_id: model-160-cursorbench
      snapshot_ref: sha256:b4348223b746be823e859c53f5f915636067e44aa6e798994655b8400a148bc2
      cited_regions:
      - rows
    id: meta/muse-spark-1-3#cursorbench_4#5db52bb38afe
    observed_at: '2026-09-30'
  - benchmark_id: arena_sc_english
    model_id_as_evaluated: muse-spark-1.3-max
    score: 1489.42
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-30'
    verified_at: '2026-09-30'
    benchmark_version: text_style_control / english, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1489.42 [1475.96,
      1502.88], 1907 votes, rank 16. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:1e2fcc24a5c8cdcd90c665aaa64b557f473180d9ce1725066717e04bfd10e5f1
      cited_regions:
      - rows
    id: meta/muse-spark-1-3#arena_sc_english#e365a8f9c0b8
  - benchmark_id: arena_sc_chinese
    model_id_as_evaluated: muse-spark-1.3-max
    score: 1541.22
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-30'
    verified_at: '2026-09-30'
    benchmark_version: text_style_control / chinese, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1541.22 [1507.02,
      1575.42], 299 votes, rank 9. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:449b90746065449e59f0dd2bbdfcb8ef55aa5fe42c1b6beb8c930eb79a68224d
      cited_regions:
      - rows
    id: meta/muse-spark-1-3#arena_sc_chinese#d6331f3dfe98
  - benchmark_id: arena_sc_russian
    model_id_as_evaluated: muse-spark-1.3-max
    score: 1505.98
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-30'
    verified_at: '2026-09-30'
    benchmark_version: text_style_control / russian, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1505.98 [1481.13,
      1530.83], 558 votes, rank 7. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:5364bedcc9fe8a9598db9c20aabead5411e9c132021ef8e55da2be02c0a36c67
      cited_regions:
      - rows
    id: meta/muse-spark-1-3#arena_sc_russian#910d7a3307c2
  - benchmark_id: arena_sc_vision_ocr
    model_id_as_evaluated: muse-spark-1.3-max
    score: 1309.84
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-30'
    verified_at: '2026-09-30'
    benchmark_version: vision_style_control / ocr, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1309.84 [1292.30,
      1327.38], 1237 votes, rank 7. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-vision-style-control
      snapshot_ref: sha256:2dce15e32ba82760a14eb6d794d7a44e23c6445c5521dcc4b9663521e402f9d6
      cited_regions:
      - rows
    id: meta/muse-spark-1-3#arena_sc_vision_ocr#2e733a631ebf
  - benchmark_id: arena_sc_vision_diagram
    model_id_as_evaluated: muse-spark-1.3-max
    score: 1314.03
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-30'
    verified_at: '2026-09-30'
    benchmark_version: vision_style_control / diagram, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1314.03 [1285.51,
      1342.55], 451 votes, rank 17. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-vision-style-control
      snapshot_ref: sha256:b3b3df0cdc8c9065197b822d9005d334197cf72b9da69ab35a05b6bb1401d9bd
      cited_regions:
      - rows
    id: meta/muse-spark-1-3#arena_sc_vision_diagram#509cd37bdd15
  - benchmark_id: arena_sc_vision_homework
    model_id_as_evaluated: muse-spark-1.3-max
    score: 1280.78
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-30'
    verified_at: '2026-09-30'
    benchmark_version: vision_style_control / homework, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1280.78 [1238.78,
      1322.77], 196 votes, rank 44. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-vision-style-control
      snapshot_ref: sha256:c6cc8aff02e174d0d07d3b1062861395df1b9dcd3ea53fb5c3f7dfffc0de039f
      cited_regions:
      - rows
    id: meta/muse-spark-1-3#arena_sc_vision_homework#937ea632f78a
  - benchmark_id: arena_sc_document
    model_id_as_evaluated: muse-spark-1.3-max
    score: 1470.66
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-30'
    verified_at: '2026-09-30'
    benchmark_version: document / overall, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1470.66 [1452.37,
      1488.95], 1006 votes, rank 15. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-document
      snapshot_ref: sha256:5647d463e779905a42ab0cc56675629608fc252462f6535402778fc965f013f5
      cited_regions:
      - rows
    id: meta/muse-spark-1-3#arena_sc_document#055622d2df76
  - benchmark_id: arena_sc_industry_software_it_services
    model_id_as_evaluated: muse-spark-1.3-max
    score: 1534.09
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-30'
    verified_at: '2026-09-30'
    benchmark_version: text_style_control / industry_software_and_it_services, latest split, revision
      1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1534.09 [1520.46,
      1547.71], 1943 votes, rank 5. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:eea47e91c8bc87fe0b61f2a3c0e4eba132c33a7b65597a78092fce12744d989a
      cited_regions:
      - rows
    id: meta/muse-spark-1-3#arena_sc_industry_software_it_services#31ecd78bb436
  - benchmark_id: arena_sc_industry_entertainment_sports_media
    model_id_as_evaluated: muse-spark-1.3-max
    score: 1461.27
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-30'
    verified_at: '2026-09-30'
    benchmark_version: text_style_control / industry_entertainment_and_sports_and_media, latest
      split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1461.27 [1442.39,
      1480.16], 1071 votes, rank 16. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:dd31fbcb0b964ee4faa128a3bcac1f1ad740ec5fa6755b63a7cdd8654950bf11
      cited_regions:
      - rows
    id: meta/muse-spark-1-3#arena_sc_industry_entertainment_sports_media#f11710cbfe7d
  - benchmark_id: arena_sc_industry_mathematical
    model_id_as_evaluated: muse-spark-1.3-max
    score: 1498.74
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-30'
    verified_at: '2026-09-30'
    benchmark_version: text_style_control / industry_mathematical, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1498.74 [1462.29,
      1535.19], 257 votes, rank 21. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:6061abfc8f62e0094fea0e87ea00b13d5f43d12e35990052572243771c51f1db
      cited_regions:
      - rows
    id: meta/muse-spark-1-3#arena_sc_industry_mathematical#db9a5fa79d37
  - benchmark_id: arena_sc_factuality
    model_id_as_evaluated: muse-spark-1.3-max
    score: 1482.83
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-30'
    verified_at: '2026-09-30'
    benchmark_version: text_factuality / overall, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1482.83 [1475.02,
      1490.64], 4593 votes, rank 11. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-factuality
      snapshot_ref: sha256:6cd314acaa71574c46eb9bfadb9a78b786a28b13499126a045487d4aba292032
      cited_regions:
      - rows
    id: meta/muse-spark-1-3#arena_sc_factuality#b8648d964001
  - benchmark_id: brokenarxiv
    model_id_as_evaluated: Muse Spark 1.3
    score: 36.66
    unit: percent
    source_url: https://matharena.ai/competition_tables/overall--brokenarxiv
    source_kind: benchmark_author
    evidence_date: '2026-09-30'
    date_type: evaluated
    verified_at: '2026-09-30'
    benchmark_version: BrokenArXiv, MathArena Overall table
    configuration: MathArena competition table read 2026-09-29; the table states no run date,
      so the reading is dated by the observation. Accuracy averaged over four runs per problem.
      Effort not stated, as the model cell names it.
    limitations: Overall pools MathArena's monthly editions, so it moves when an edition is added.
      MathArena warns the model was released after the problems were.
    measured_by: benchmark_author
    effort: null
    harness: null
    sources:
    - source_id: model-233-matharena-brokenarxiv
      snapshot_ref: sha256:6d37ddbf9d94259ac1372ebffce5792c896cf14d81297a7af9b2d846d538254b
      cited_regions:
      - rows
    quality_flags:
    - contamination_warning
    observed_at: '2026-09-30'
    id: meta/muse-spark-1-3#brokenarxiv#10e6aea49ecb
  - benchmark_id: arxivmath
    model_id_as_evaluated: Muse Spark 1.3
    score: 65.23
    unit: percent
    source_url: https://matharena.ai/competition_tables/overall--arxivmath
    source_kind: benchmark_author
    evidence_date: '2026-09-30'
    date_type: evaluated
    verified_at: '2026-09-30'
    benchmark_version: ArXivMath, MathArena Overall table
    configuration: MathArena competition table read 2026-09-29; the table states no run date,
      so the reading is dated by the observation. Accuracy averaged over four runs per problem.
      Effort not stated, as the model cell names it.
    limitations: Overall pools MathArena's monthly editions, so it moves when an edition is added.
      MathArena warns the model was released after the problems were.
    measured_by: benchmark_author
    effort: null
    harness: null
    sources:
    - source_id: model-233-matharena-arxivmath
      snapshot_ref: sha256:8a7a53d402a60a08b27d509895c3ffadb2737db7a41e78b074f9783b0c6333a9
      cited_regions:
      - rows
    quality_flags:
    - contamination_warning
    observed_at: '2026-09-30'
    id: meta/muse-spark-1-3#arxivmath#3bc6bd711e69
  benchmark_source: ''
  benchmark_as_of: ''
  benchmark_notes: ''
deployment:
  api_only: true
  local_inference: false
  self_hostable: false
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
    transformers: false
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
    data_retention_policy: 'Standard tier: prompts and completions are not used to
      train Meta models. Read 2026-09-24 from https://ai.developer.meta.com/docs/pricing-rate-limits.md.'
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
  huggingface_downloads: null
  huggingface_likes: null
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
  provider_docs_url: https://ai.developer.meta.com/docs/models.md
  huggingface_url: ''
  arxiv_url: ''
  paper_url: ''
  github_url: ''
  ollama_url: ''
  artificial_analysis_url: ''
  arena_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
  last_scraped_models_dev: ''
  last_scraped_huggingface: ''
  last_scraped_benchmarks: '2026-09-24'
  last_scraped_pricing: '2026-09-24'
facts:
- facet: model.class
  value: text-generator
  state: known
  sources:
  - source_id: model-143-meta-muse-spark-1-3
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
  - video
  - audio
  - document
  state: known
  sources:
  - source_id: model-143-meta-muse-spark-1-3
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
  - source_id: model-143-meta-muse-spark-1-3
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
  value: 1048576
  state: known
  sources:
  - source_id: model-143-meta-muse-spark-1-3
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
  - source_id: model-143-meta-muse-spark-1-3
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
  - model-143-meta-muse-spark-1-3
  - model-143-meta-release-index
  - model-143-meta-model-api
  - model-143-meta-company
  - model-143-meta-sec
- facet: model.weights_openness
  value: closed_weights
  state: known
  sources:
  - source_id: model-143-meta-muse-spark-1-3
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
  - source_id: model-143-meta-muse-spark-1-3
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
  - model-143-meta-muse-spark-1-3
  - model-143-meta-release-index
  - model-143-meta-model-api
  - model-143-meta-company
  - model-143-meta-sec
- facet: licence.user_cap
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-meta-muse-spark-1-3
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
  - model-143-meta-muse-spark-1-3
  - model-143-meta-release-index
  - model-143-meta-model-api
  - model-143-meta-company
  - model-143-meta-sec
- facet: licence.output_training
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-meta-muse-spark-1-3
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
  - model-143-meta-muse-spark-1-3
  - model-143-meta-release-index
  - model-143-meta-model-api
  - model-143-meta-company
  - model-143-meta-sec
- facet: licence.fine_tuning
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-meta-muse-spark-1-3
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
  - model-143-meta-muse-spark-1-3
  - model-143-meta-release-index
  - model-143-meta-model-api
  - model-143-meta-company
  - model-143-meta-sec
- facet: origin.lab_jurisdiction
  value:
  - US
  state: known
  sources:
  - source_id: model-143-meta-muse-spark-1-3
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
  - source_id: model-143-meta-muse-spark-1-3
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
  - model-143-meta-muse-spark-1-3
  - model-143-meta-release-index
  - model-143-meta-model-api
  - model-143-meta-company
  - model-143-meta-sec
- facet: origin.weights_hosting
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-meta-muse-spark-1-3
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
  - model-143-meta-muse-spark-1-3
  - model-143-meta-release-index
  - model-143-meta-model-api
  - model-143-meta-company
  - model-143-meta-sec
- facet: model.release_date
  value: '2026-09-02'
  state: known
  sources:
  - source_id: model-143-meta-muse-spark-1-3
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
  - source_id: model-143-meta-muse-spark-1-3
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
  - source_id: model-143-meta-muse-spark-1-3
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
  - source_id: model-143-meta-muse-spark-1-3
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
  - source_id: model-143-meta-muse-spark-1-3
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
  - source_id: model-143-meta-muse-spark-1-3
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
  - model-143-meta-muse-spark-1-3
  - model-143-meta-release-index
  - model-143-meta-model-api
  - model-143-meta-company
  - model-143-meta-sec
- facet: feature.streaming
  value: true
  state: known
  sources:
  - source_id: model-143-meta-muse-spark-1-3
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
- id: meta/muse-spark-1-3#model.fits_hardware
  subject:
    kind: model
    id: meta/muse-spark-1-3
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
  - source_id: model-143-meta-muse-spark-1-3
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
card_author: Grok 4.7
card_created: '2026-09-24'
card_updated: '2026-09-28'
---

# Muse Spark 1.3

Muse Spark 1.3 is Meta's current Muse Spark version on the Model API, id `muse-spark-1.3`.
The models page, read 2026-09-24 at https://ai.developer.meta.com/docs/models.md, describes it as tuned for agentic workflows, including multi-step tool, browser and long-horizon tasks, with improved coding over 1.2.
The same table gives text, image, video, audio and PDF input, text output, and a context window of 1,048,576 tokens.
A note on that page says audio understanding in 1.3 is not fully supported and response quality for audio may be degraded. For audio, the page points to 1.2 or Muse Voice Transcribe.
The page also says 1.3 supports every reasoning-effort level, including "max", on the Standard tier only.
The quickstart, read the same day at https://ai.developer.meta.com/docs/quickstart.md, lists context 1,048,576 and output 131,072 for `muse-spark-1.3`.
Meta's announcement is dated 2 September 2026: https://research.meta.ai/blog/introducing-muse-spark-1-3.

`meta/muse-spark` remains the April 2026 model.
Arena lists its `muse-spark` row along with `muse-spark-1.3-max` and `muse-spark-1.3 (xHigh)`.

Standard-tier price, read 2026-09-24 from https://ai.developer.meta.com/docs/pricing-rate-limits.md: $1.25 input, $0.15 cached input, $4.25 output, per million tokens.
`muse-spark-1.3-contributor` is a separate id on that page, at $0.10 / $0.002 / $0.20, and Meta says it may train on those prompts and completions.
The prices on this card are the Standard id.
No parameter count is stated on the pages read.

## Evidence

Arena overall rows from https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset, CC BY 4.0, read 2026-09-24.
Text and vision publish date 2026-09-13. Webdev publish date 2026-09-23.
Both the max and xHigh webdev rows are recorded. They are effort settings of this version, not a second model.