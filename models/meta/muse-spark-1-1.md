---
model_id: meta/muse-spark-1-1
display_name: Muse Spark 1.1
provider: meta
provider_display: Meta
family: muse
version: muse-spark-1.1
release_date: '2026-07-09'
last_updated: '2026-07-09'
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
    max_output_tokens: null
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
    think_budget_control: false
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
  note: USD per 1M tokens, Standard tier model id muse-spark-1.1. Read 2026-09-24
    from https://ai.developer.meta.com/docs/pricing-rate-limits.md. Contributor model
    ids, where Meta publishes them, are a different offering and are not these prices.
availability:
  primary_provider:
    name: Meta Model API
    platform_url: https://ai.developer.meta.com/docs/models.md
    api_endpoint: https://api.meta.ai/v1
    npm_package: ''
    env_vars: []
    model_id_on_platform: muse-spark-1.1
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
    model_id_as_evaluated: muse-spark-1.1
    score: 1480.17
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text/latest, overall
    configuration: LMArena leaderboard dataset, CC BY 4.0, category overall, leaderboard_publish_date
      2026-09-13, read 2026-09-24. Rank 15, 27615 votes, interval [1475.35, 1485.0].
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC
      BY 4.0.
    id: meta/muse-spark-1-1#arena_elo_overall#efdcadcfd60c
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text
      snapshot_ref: sha256:6edcebedc5883fade268c96cf827cebf7e4d850529a482825a5afa1264bb1628
      cited_regions:
      - rows
    interval:
    - 1475.35
    - 1485.0
    n: 27615
    observed_at: '2026-09-29'
  - benchmark_id: arena_elo_vision
    model_id_as_evaluated: muse-spark-1.1
    score: 1294.16
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: vision/latest, overall
    configuration: LMArena leaderboard dataset, CC BY 4.0, category overall, leaderboard_publish_date
      2026-09-13, read 2026-09-24. Rank 21, 8447 votes, interval [1286.17, 1302.16].
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC
      BY 4.0.
    id: meta/muse-spark-1-1#arena_elo_vision#c2537b6cc314
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-vision
      snapshot_ref: sha256:756812129fdf26cd49d126a785b01e1ede317aa6f2cb5d47cbd6893d883bedae
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_webdev
    model_id_as_evaluated: muse-spark-1.1
    score: 1542.36
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-23'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: webdev/latest, overall
    configuration: LMArena leaderboard dataset, CC BY 4.0, category overall, leaderboard_publish_date
      2026-09-23, read 2026-09-24. Rank 32, 7521 votes, interval [1534.53, 1550.19].
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC
      BY 4.0.
    id: meta/muse-spark-1-1#arena_webdev#10ec5db7edcf
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-143-evidence-arena-webdev-json
      snapshot_ref: sha256:1342f43f483667f8e4313a1fb517522e1f18aa1b09d4812f8d3163c4ff30b9bc
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: swe_bench_pro
    model_id_as_evaluated: Muse Spark 1.1*
    score: 61.5
    unit: percent
    source_url: https://labs.scale.com/leaderboard/swe_bench_pro
    source_kind: independent_evaluator
    evidence_date: '2026-07-09'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: SWE-Bench Pro, public dataset
    configuration: Public-dataset row on the Scale Labs page, read 2026-09-24. Resolve
      rate 61.5, confidence interval upper 3.1, rank 1, createdAt 2026-07-09. The
      asterisk means mini-swe-agent, as the page states.
    limitations: Public split only. The same page lists a private-split row at 51.5,
      which is not this number.
    id: meta/muse-spark-1-1#swe_bench_pro#6857d2ed9fb3
    measured_by: independent_evaluator
    effort: null
    harness: unregistered
    sources:
    - source_id: model-160-scale-swe-bench-pro-public
      snapshot_ref: sha256:cad114ecfd6412379b8d97ad250aab1c9c10ab2281b356be45b36b3d459f5457
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_english
    model_id_as_evaluated: muse-spark-1.1
    score: 1492.12
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / english, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1492.12 [1485.78,
      1498.47], 11415 votes, rank 14. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:cee57baa7239c5aa2091dcb5db0b4c2ac22cec732b235d66c0cda2ee55bdcb44
      cited_regions:
      - rows
    id: meta/muse-spark-1-1#arena_sc_english#31e729e27142
  - benchmark_id: arena_sc_chinese
    model_id_as_evaluated: muse-spark-1.1
    score: 1532.52
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / chinese, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1532.52 [1518.01,
      1547.04], 1911 votes, rank 15. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:9bf00fc37e8a997735f423949aba6ffc5551990b6f835297d3fed2b364abe02b
      cited_regions:
      - rows
    id: meta/muse-spark-1-1#arena_sc_chinese#c98cdbfee5d7
  - benchmark_id: arena_sc_japanese
    model_id_as_evaluated: muse-spark-1.1
    score: 1447.15
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / japanese, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1447.15 [1418.41,
      1475.88], 466 votes, rank 32. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:13b68c219a1ec549a9336846ddacaf97471f6323c09e4f45a73eab7a0857a9ca
      cited_regions:
      - rows
    id: meta/muse-spark-1-1#arena_sc_japanese#20f3f6eca474
  - benchmark_id: arena_sc_korean
    model_id_as_evaluated: muse-spark-1.1
    score: 1474.72
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / korean, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1474.72 [1449.13,
      1500.31], 563 votes, rank 7. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:96706e685de18541b6ad515db22607a7840bad8bc902a30a8a38f949cd409c08
      cited_regions:
      - rows
    id: meta/muse-spark-1-1#arena_sc_korean#8c762093cefb
  - benchmark_id: arena_sc_russian
    model_id_as_evaluated: muse-spark-1.1
    score: 1496.38
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / russian, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1496.38 [1485.03,
      1507.73], 2917 votes, rank 13. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:eb77af068077fa90a9514ad454b6a65f061a176f0d68897132e1526f3be743dd
      cited_regions:
      - rows
    id: meta/muse-spark-1-1#arena_sc_russian#d896a4ce5b9a
  - benchmark_id: arena_sc_spanish
    model_id_as_evaluated: muse-spark-1.1
    score: 1488.34
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / spanish, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1488.34 [1466.70,
      1509.98], 812 votes, rank 6. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:e56e27431afb859f3376e3d5609785906e24647b4c0c65a324b7995944b9573b
      cited_regions:
      - rows
    id: meta/muse-spark-1-1#arena_sc_spanish#b9739318f5c4
  - benchmark_id: arena_sc_german
    model_id_as_evaluated: muse-spark-1.1
    score: 1470.96
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / german, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1470.96 [1443.96,
      1497.96], 510 votes, rank 36. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:098d6730e0b426da68eee86ddfd97bb03c3b1048e178378de1ec3924fa209c6d
      cited_regions:
      - rows
    id: meta/muse-spark-1-1#arena_sc_german#a6a8198358b8
  - benchmark_id: arena_sc_french
    model_id_as_evaluated: muse-spark-1.1
    score: 1518.44
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / french, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1518.44 [1497.63,
      1539.24], 956 votes, rank 6. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:c6c9f83eb7147bedac479a445a3803aad09d613643414d3cd5035dbde46d6f2f
      cited_regions:
      - rows
    id: meta/muse-spark-1-1#arena_sc_french#84661faa7c84
  - benchmark_id: arena_sc_polish
    model_id_as_evaluated: muse-spark-1.1
    score: 1499.98
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / polish, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1499.98 [1472.87,
      1527.09], 473 votes, rank 7. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:a99daf2dc2fbf9b06de90a127cc1408c7a19e4fa45a1a4d538b668211c4b5892
      cited_regions:
      - rows
    id: meta/muse-spark-1-1#arena_sc_polish#07d5589b0283
  - benchmark_id: arena_sc_vision_ocr
    model_id_as_evaluated: muse-spark-1.1
    score: 1293.63
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: vision_style_control / ocr, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1293.63 [1284.89,
      1302.37], 5713 votes, rank 22. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-vision-style-control
      snapshot_ref: sha256:72ff33856df7c05e7611f78bd6f0a13fc422694ad107f25e00c11b10edb14422
      cited_regions:
      - rows
    id: meta/muse-spark-1-1#arena_sc_vision_ocr#9a7907ee3a1f
  - benchmark_id: arena_sc_vision_diagram
    model_id_as_evaluated: muse-spark-1.1
    score: 1307.84
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: vision_style_control / diagram, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1307.84 [1294.68,
      1321.01], 2229 votes, rank 24. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-vision-style-control
      snapshot_ref: sha256:f70ad4aae81aa8b6cca27735001f45704e13f64af12ad93244cd19ca60d98085
      cited_regions:
      - rows
    id: meta/muse-spark-1-1#arena_sc_vision_diagram#0a4eddad4f9e
  - benchmark_id: arena_sc_vision_homework
    model_id_as_evaluated: muse-spark-1.1
    score: 1281.19
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: vision_style_control / homework, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1281.19 [1259.81,
      1302.56], 788 votes, rank 42. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-vision-style-control
      snapshot_ref: sha256:8015c65e88084d6c6b25f9787fb1528f550abd8e055cf8f3b753e863296d3176
      cited_regions:
      - rows
    id: meta/muse-spark-1-1#arena_sc_vision_homework#39e4e6c5a74f
  - benchmark_id: arena_sc_document
    model_id_as_evaluated: muse-spark-1.1
    score: 1464.7
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: document / overall, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1464.70 [1455.86,
      1473.54], 4885 votes, rank 18. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-document
      snapshot_ref: sha256:050705ac3c2e5ba81aacf700b87f5144dd7b0ec9f7f12168be5086b1c11be958
      cited_regions:
      - rows
    id: meta/muse-spark-1-1#arena_sc_document#40d74c3db5c6
  - benchmark_id: arena_sc_industry_software_it_services
    model_id_as_evaluated: muse-spark-1.1
    score: 1525.0
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / industry_software_and_it_services, latest split, revision
      1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1525.00 [1518.44,
      1531.56], 11002 votes, rank 10. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:4eaa9890dce0719aa263af890c9f2a7bb1a3198e291d84dbf8c1371d4f150c52
      cited_regions:
      - rows
    id: meta/muse-spark-1-1#arena_sc_industry_software_it_services#67f62c43978c
  - benchmark_id: arena_sc_industry_entertainment_sports_media
    model_id_as_evaluated: muse-spark-1.1
    score: 1454.04
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / industry_entertainment_and_sports_and_media, latest
      split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1454.04 [1446.02,
      1462.07], 6857 votes, rank 25. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:df0d5e7c4d4ce1f683618242c0786eafd164d98b3b49dbaa6e699476bec94ccf
      cited_regions:
      - rows
    id: meta/muse-spark-1-1#arena_sc_industry_entertainment_sports_media#035d3598cbb0
  - benchmark_id: arena_sc_industry_mathematical
    model_id_as_evaluated: muse-spark-1.1
    score: 1504.07
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / industry_mathematical, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1504.07 [1488.39,
      1519.75], 1482 votes, rank 16. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:b0f3ee924239a7a9a1e60676935d0c83091f29517b8acb95e07868e370822e82
      cited_regions:
      - rows
    id: meta/muse-spark-1-1#arena_sc_industry_mathematical#ec4523d028f7
  - benchmark_id: arena_sc_factuality
    model_id_as_evaluated: muse-spark-1.1
    score: 1464.86
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_factuality / overall, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1464.86 [1460.77,
      1468.95], 27418 votes, rank 35. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-factuality
      snapshot_ref: sha256:ece0fd0afe2b42a38bce698a6be5329044b5503f5edb7f43473c19394b38fc28
      cited_regions:
      - rows
    id: meta/muse-spark-1-1#arena_sc_factuality#97d6c161b741
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
  - source_id: model-143-meta-muse-spark-1-1
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
  - source_id: model-143-meta-muse-spark-1-1
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
  - source_id: model-143-meta-muse-spark-1-1
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
  - source_id: model-143-meta-muse-spark-1-1
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
  - source_id: model-143-meta-muse-spark-1-1
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
  - model-143-meta-muse-spark-1-1
  - model-143-meta-release-index
  - model-143-meta-model-api
  - model-143-meta-company
  - model-143-meta-sec
- facet: model.weights_openness
  value: closed_weights
  state: known
  sources:
  - source_id: model-143-meta-muse-spark-1-1
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
  - source_id: model-143-meta-muse-spark-1-1
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
  - model-143-meta-muse-spark-1-1
  - model-143-meta-release-index
  - model-143-meta-model-api
  - model-143-meta-company
  - model-143-meta-sec
- facet: licence.user_cap
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-meta-muse-spark-1-1
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
  - model-143-meta-muse-spark-1-1
  - model-143-meta-release-index
  - model-143-meta-model-api
  - model-143-meta-company
  - model-143-meta-sec
- facet: licence.output_training
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-meta-muse-spark-1-1
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
  - model-143-meta-muse-spark-1-1
  - model-143-meta-release-index
  - model-143-meta-model-api
  - model-143-meta-company
  - model-143-meta-sec
- facet: licence.fine_tuning
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-meta-muse-spark-1-1
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
  - model-143-meta-muse-spark-1-1
  - model-143-meta-release-index
  - model-143-meta-model-api
  - model-143-meta-company
  - model-143-meta-sec
- facet: origin.lab_jurisdiction
  value:
  - US
  state: known
  sources:
  - source_id: model-143-meta-muse-spark-1-1
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
  - source_id: model-143-meta-muse-spark-1-1
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
  - model-143-meta-muse-spark-1-1
  - model-143-meta-release-index
  - model-143-meta-model-api
  - model-143-meta-company
  - model-143-meta-sec
- facet: origin.weights_hosting
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-meta-muse-spark-1-1
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
  - model-143-meta-muse-spark-1-1
  - model-143-meta-release-index
  - model-143-meta-model-api
  - model-143-meta-company
  - model-143-meta-sec
- facet: model.release_date
  value: '2026-07-09'
  state: known
  sources:
  - source_id: model-143-meta-muse-spark-1-1
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
  - source_id: model-143-meta-muse-spark-1-1
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
  - source_id: model-143-meta-muse-spark-1-1
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
  - source_id: model-143-meta-muse-spark-1-1
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
  - source_id: model-143-meta-muse-spark-1-1
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
  - source_id: model-143-meta-muse-spark-1-1
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
  - model-143-meta-muse-spark-1-1
  - model-143-meta-release-index
  - model-143-meta-model-api
  - model-143-meta-company
  - model-143-meta-sec
- facet: feature.streaming
  value: true
  state: known
  sources:
  - source_id: model-143-meta-muse-spark-1-1
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
- id: meta/muse-spark-1-1#model.fits_hardware
  subject:
    kind: model
    id: meta/muse-spark-1-1
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
  - source_id: model-143-meta-muse-spark-1-1
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

# Muse Spark 1.1

Muse Spark 1.1 is a multimodal reasoning model from Meta Superintelligence Labs, served as `muse-spark-1.1` on Meta Model API.
The models page, read 2026-09-24 at https://ai.developer.meta.com/docs/models.md, lists text, image, video, audio and PDF input, text output, and a context window of 1,048,576 tokens.
Meta's announcement of this version is dated 9 July 2026: https://research.meta.ai/blog/introducing-muse-spark-meta-model-api.
That post calls it an upgrade of Muse Spark for tool use, computer use, coding and multimodal understanding, and says the model can manage a context window of 1 million tokens.

`meta/muse-spark` remains the April 2026 model.
The Arena text parquet (publish date 2026-09-13) lists that model's row, `muse-spark`, and this version's row, `muse-spark-1.1`.
The SWE-bench Pro public table likewise lists "Muse Spark" and "Muse Spark 1.1" as two rows.

Standard-tier price, read 2026-09-24 from https://ai.developer.meta.com/docs/pricing-rate-limits.md: $1.25 per million input tokens, $0.15 cached input, $4.25 output.
The same page says prompts and completions on the Standard tier are not used to train Meta models, and lists 3,000 requests per minute and 4,000,000 tokens per minute.
Meta does not publish a contributor model id for 1.1.
The pages read for this version do not state a parameter count, a maximum output length, or a downloadable-weights licence.
Those fields stay empty.

The overview at https://ai.developer.meta.com/docs/overview.md, read the same day, says Muse Spark on this API supports parallel tool calls and streamed tool-call arguments.
Base URL on that page: https://api.meta.ai/v1.

## Evidence

Arena scores are the overall rows of https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset (CC BY 4.0), read 2026-09-24.
The SWE-bench Pro public resolve rate is from https://labs.scale.com/leaderboard/swe_bench_pro, read the same day.
The row name ends in an asterisk. The page says an asterisk means the run used mini-swe-agent.
The public entry's createdAt is 2026-07-09. The page does not give a separate run date.