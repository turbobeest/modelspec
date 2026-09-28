---
model_id: zhipu/glm-5-2
display_name: GLM-5.2
provider: zhipu
provider_display: Z.ai (Zhipu AI)
family: glm
version: '5.2'
release_date: '2026-06-13'
last_updated: '2026-09-10'
status: active
model_type: llm-reasoning
model_subtypes: []
tags: []
pipeline_tag: ''
architecture:
  type: null
  total_parameters: 753329940480
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
  library_name: ''
licensing:
  open_weights: true
  license_type: mit
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
  origin_country: CN
  origin_org_type: null
modalities:
  input:
  - text
  output:
  - text
  text:
    max_input_tokens: null
    max_output_tokens: 131072
    context_window: 1000000
    streaming: null
    fill_in_middle: null
    json_mode: true
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
    overall: null
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
  input: 1.4
  output: 4.4
  reasoning: null
  cache_read: 0.28
  cache_write: 0.0
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
  note: Z.ai first-party API $1.40/$4.40 per 1M (docs.z.ai/guides/llm/glm-5.2,
    2026-09-10). Together serverless matches those prices and
    lists context 1048575 (docs.together.ai/docs/serverless-models, 2026-09-10); the
    provider figure is 1M tokens.
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
    model_id: zai-org/GLM-5.2
    url: https://huggingface.co/zai-org/GLM-5.2
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
  - benchmark_id: arena_elo_style_control
    model_id_as_evaluated: glm-5.2-max
    score: 1472.1
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / overall, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category overall,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1472.10 [1467.48, 1476.71], 36798 votes,
      rank 38.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: zhipu/glm-5-2#arena_elo_style_control#8cf8d809a569
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:4c99fd5665f6e5745aaaaff66731f8fc8b37659626ce55ed7dad2cc12c71d900
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: arena_sc_coding
    model_id_as_evaluated: glm-5.2-max
    score: 1509.81
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / coding, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category coding,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1509.81 [1502.93, 1516.69], 10311 votes,
      rank 48.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: zhipu/glm-5-2#arena_sc_coding#8325776505c6
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:323b53f5f53c709fd4e181dd59a928d7d275b38e6281c307648b293925fdc03b
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: arena_sc_hard_prompts
    model_id_as_evaluated: glm-5.2-max
    score: 1493.08
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / hard_prompts, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category hard_prompts,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1493.08 [1487.78, 1498.37], 24262 votes,
      rank 37.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: zhipu/glm-5-2#arena_sc_hard_prompts#f792f99acc1e
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:51050cf234ba130a5786cf4e32d6f650a87b263b8fff51209a9d1b820c22623a
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: arena_sc_math
    model_id_as_evaluated: glm-5.2-max
    score: 1479.48
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / math, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category math, leaderboard_publish_date
      2026-09-13; style control. Highest-effort row for the product (effort: max; MODEL-123
      max-effort rule). Rating 1479.48 [1464.96, 1494.00], 1662 votes, rank 26.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: zhipu/glm-5-2#arena_sc_math#cb0756c6bb35
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:2eeb7c07a7bcabaff9ebc1f2f7ff4fe5f607018c9883b3260799cdd1999b5f44
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: arena_sc_creative_writing
    model_id_as_evaluated: glm-5.2-max
    score: 1450.95
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / creative_writing, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category creative_writing,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1450.95 [1442.88, 1459.02], 7046 votes,
      rank 35.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: zhipu/glm-5-2#arena_sc_creative_writing#f80ee924fdb6
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:97f2b8d590973faf49c61a72be606d026673c083c685710b64aefa9325d4ecf0
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: arena_sc_instruction_following
    model_id_as_evaluated: glm-5.2-max
    score: 1466.16
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / instruction_following, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category instruction_following,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1466.16 [1459.83, 1472.49], 12822 votes,
      rank 32.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: zhipu/glm-5-2#arena_sc_instruction_following#2d1c993e1af3
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:6eef3af9530f366da3d86f112c6ea9733c41ce956c31a47daf8e109a192979df
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: arena_sc_multi_turn
    model_id_as_evaluated: glm-5.2-max
    score: 1468.92
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / multi_turn, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category multi_turn,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1468.92 [1460.57, 1477.27], 6003 votes,
      rank 57.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: zhipu/glm-5-2#arena_sc_multi_turn#721a1e490afa
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:526ccc1218e07be8833373ce5cf7fc27975914b534b86ac08acf9671b628f010
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: arena_sc_expert
    model_id_as_evaluated: glm-5.2-max
    score: 1493.72
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / expert, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category expert,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1493.72 [1483.68, 1503.77], 3869 votes,
      rank 40.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: zhipu/glm-5-2#arena_sc_expert#c3feb9651207
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:699bca36a93bdf000da6c88fac3568822be06e294e5946cf96bfce5490501dd1
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: arena_sc_longer_query
    model_id_as_evaluated: glm-5.2-max
    score: 1483.27
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / longer_query, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category longer_query,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1483.27 [1477.28, 1489.25], 16836 votes,
      rank 31.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: zhipu/glm-5-2#arena_sc_longer_query#24a6cb842544
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:2c60aa8ba40ed9a9480e56483d39f39162a294fc9ac295c92a6e760e8487ad7f
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: arena_sc_non_english
    model_id_as_evaluated: glm-5.2-max
    score: 1458.33
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / non_english, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category non_english,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1458.33 [1452.98, 1463.69], 21161 votes,
      rank 38.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: zhipu/glm-5-2#arena_sc_non_english#071e200e0eb3
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:27a96087822f82d920862b1d4b34ef12a91c320aa07746766c2b5f5869811103
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: arena_sc_medicine
    model_id_as_evaluated: glm-5.2-max
    score: 1485.29
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / industry_medicine_and_healthcare, latest split,
      revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category industry_medicine_and_healthcare,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1485.29 [1473.06, 1497.52], 2652 votes,
      rank 41.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: zhipu/glm-5-2#arena_sc_medicine#4b180596d350
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:6764aac77322dc9383d4e194b9f28c571379b15d56349b7ce67e47bb38c8c20f
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: arena_sc_legal
    model_id_as_evaluated: glm-5.2-max
    score: 1479.37
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / industry_legal_and_government, latest split, revision
      1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category industry_legal_and_government,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1479.37 [1467.96, 1490.78], 2995 votes,
      rank 36.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: zhipu/glm-5-2#arena_sc_legal#f46cdac9caa0
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:49caeb2b4586b0222e12201bcc4dca0818f116d657be63f6dbd6542848aa3911
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: arena_sc_business
    model_id_as_evaluated: glm-5.2-max
    score: 1459.75
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / industry_business_and_management_and_financial_operations,
      latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category industry_business_and_management_and_financial_operations,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1459.75 [1452.01, 1467.49], 7174 votes,
      rank 53.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: zhipu/glm-5-2#arena_sc_business#f56b54cbedb7
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:d9d4cce87afea54ca87c4146e654198a2eae110bf7495444ae555d3752ff68b6
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: arena_sc_science
    model_id_as_evaluated: glm-5.2-max
    score: 1490.66
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / industry_life_and_physical_and_social_science, latest
      split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category industry_life_and_physical_and_social_science,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1490.66 [1482.48, 1498.85], 5983 votes,
      rank 30.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: zhipu/glm-5-2#arena_sc_science#901aff243e65
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:1bf06c413f0788c8679963f12858593c3785e34e8243794d3ebc85142e509727
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: arena_sc_writing
    model_id_as_evaluated: glm-5.2-max
    score: 1455.16
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: text_style_control / industry_writing_and_literature_and_language, latest
      split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category industry_writing_and_literature_and_language,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1455.16 [1448.13, 1462.19], 9635 votes,
      rank 38.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: zhipu/glm-5-2#arena_sc_writing#aee7cdcc0522
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:3593556c5bea46cf0f93c6d98c401c3f98aa3221eda056f983eed4428a7f7186
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: arena_webdev
    model_id_as_evaluated: glm-5.2-max
    score: 1599.52
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-23'
    date_type: published
    verified_at: '2026-09-28'
    benchmark_version: webdev / overall, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset webdev, category overall, leaderboard_publish_date
      2026-09-23; no style-controlled variant. Highest-effort row for the product (effort: max;
      MODEL-123 max-effort rule). Rating 1599.52 [1592.73, 1606.30], 12440 votes, rank 21.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: zhipu/glm-5-2#arena_webdev#16d59f403e03
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-143-evidence-arena-webdev-json
      snapshot_ref: sha256:da76d3a70760439afe51f8ac9c2d7ff514a0b4147c7b898213209c1765a36c23
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: gpqa_diamond
    model_id_as_evaluated: glm-5.2_max
    score: 91.86
    unit: percent
    source_url: https://epoch.ai/benchmarks/gpqa-diamond
    source_kind: independent_evaluator
    evidence_date: '2026-06-24'
    date_type: evaluated
    verified_at: '2026-09-28'
    benchmark_version: GPQA Diamond (Epoch AI run)
    configuration: Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (gpqa_diamond.csv),
      read 2026-09-24. Run started 2026-06-24T20:55:39.000Z; effort max; highest-effort run
      for the model (MODEL-123 max-effort rule), newest on a tie. Standard error 1.61 points.
    limitations: Epoch AI data, CC BY 4.0.
    id: zhipu/glm-5-2#gpqa_diamond#000153c44f32
    measured_by: independent_evaluator
    effort: max
    harness: null
    sources:
    - source_id: model-143-evidence-epoch-gpqa-diamond-csv
      snapshot_ref: sha256:fd51bd49f0388b2be106166a662fc4f65e0d4158b4f230d615d4647e4b95fe59
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: frontiermath_tiers_1_3_v2
    model_id_as_evaluated: glm-5.2_max
    score: 59.21
    unit: percent
    source_url: https://epoch.ai/frontiermath
    source_kind: independent_evaluator
    evidence_date: '2026-06-19'
    date_type: evaluated
    verified_at: '2026-09-28'
    benchmark_version: FrontierMath-Tiers-1-3-v2-Private (Epoch AI run)
    configuration: Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (frontiermath_tiers_1_3_v2.csv),
      read 2026-09-24. Run started 2026-06-19T16:13:05.000Z; effort max; highest-effort run
      for the model (MODEL-123 max-effort rule), newest on a tie. Standard error 2.96 points.
    limitations: Epoch AI data, CC BY 4.0.
    id: zhipu/glm-5-2#frontiermath_tiers_1_3_v2#bb084b2f9a80
    measured_by: independent_evaluator
    effort: max
    harness: null
    sources:
    - source_id: model-143-evidence-epoch-frontiermath-tiers-1-3-v2-csv
      snapshot_ref: sha256:d19dfd3736a2e103a7b1a6e3ca14ea4907d9756ddcaa92e36e0cfaf1eb7a448d
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: simpleqa_verified
    model_id_as_evaluated: glm-5.2_max
    score: 34.2
    unit: percent
    source_url: https://epoch.ai/benchmarks/simpleqa-verified
    source_kind: independent_evaluator
    evidence_date: '2026-08-27'
    date_type: evaluated
    verified_at: '2026-09-28'
    benchmark_version: SimpleQA Verified, proportion correct, Epoch AI protocol with anti-abstention
      prompt
    configuration: Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (simpleqa_verified.csv),
      read 2026-09-24. Run started 2026-08-27T19:36:05.000Z; effort max; highest-effort run
      for the model (MODEL-123 max-effort rule), newest on a tie. Standard error 1.50 points.
    limitations: Epoch AI data, CC BY 4.0.
    id: zhipu/glm-5-2#simpleqa_verified#bdec63d119ba
    measured_by: independent_evaluator
    effort: max
    harness: null
    sources:
    - source_id: model-160-epoch-simpleqa-verified-csv
      snapshot_ref: sha256:fadcdfcce8f8b9704c469aa69d5bfec2780cecd8211de5093faa390af730e7dc
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: swe_bench_verified
    model_id_as_evaluated: glm-5.2_max
    score: 78.7
    unit: percent
    source_url: https://epoch.ai/benchmarks/swe-bench-verified
    source_kind: independent_evaluator
    evidence_date: '2026-06-25'
    date_type: evaluated
    verified_at: '2026-09-28'
    benchmark_version: SWE-bench Verified (Epoch AI run)
    configuration: Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (swe_bench_verified.csv),
      read 2026-09-24. Run started 2026-06-25T13:13:06.902Z; effort max; highest-effort run
      for the model (MODEL-123 max-effort rule), newest on a tie. Standard error 1.87 points.
    limitations: Epoch AI data, CC BY 4.0.
    id: zhipu/glm-5-2#swe_bench_verified#805917b3a0af
    measured_by: independent_evaluator
    effort: max
    harness: null
    sources:
    - source_id: model-160-epoch-swe-bench-verified-csv
      snapshot_ref: sha256:2fedfaff66b1d7adc7b1eb0557fae2827812844f5f5e580e5e2c738205f83a9b
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: frontiercode_v1_1
    model_id_as_evaluated: GLM 5.2
    score: 24.5
    unit: percent
    source_url: https://cognition.com/frontiercode
    source_kind: benchmark_author
    evidence_date: '2026-09-25'
    date_type: evaluated
    verified_at: '2026-09-28'
    benchmark_version: FrontierCode 1.1, main score (Mean@5)
    configuration: Board row as copied in Epoch AI's benchmark data (frontiercode_external.csv,
      https://epoch.ai/data/benchmark_data.zip), read 2026-09-24. Effort none; the highest-effort
      row for the model (MODEL-123 max-effort rule). Harness mini-swe-agent.
    limitations: A live board's standing, dated by the day ModelSpec read Epoch AI's copy; the
      copy carries no per-row date. Epoch AI data, CC BY 4.0.
    id: zhipu/glm-5-2#frontiercode_v1_1#5b1e2ccd9352
    measured_by: benchmark_author
    effort: null
    harness: null
    sources:
    - source_id: model-160-frontiercode
      snapshot_ref: sha256:62a9280a8be3ac6583e6b83dc7b916217bfc32be4ff00d12fae255fe2babf689
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: vending_bench_2
    model_id_as_evaluated: GLM-5.2
    score: 8313.78
    unit: USD
    source_url: https://andonlabs.com/evals/vending-bench-2
    source_kind: benchmark_author
    evidence_date: '2026-09-25'
    date_type: evaluated
    verified_at: '2026-09-28'
    benchmark_version: Vending-Bench 2, mean final balance over 5 runs
    configuration: Board row as copied in Epoch AI's benchmark data (vending_bench_2_external.csv,
      https://epoch.ai/data/benchmark_data.zip), read 2026-09-24. Effort unknown; the highest-effort
      row for the model (MODEL-123 max-effort rule).
    limitations: A live board's standing, dated by the day ModelSpec read Epoch AI's copy; the
      copy carries no per-row date. Epoch AI data, CC BY 4.0.
    id: zhipu/glm-5-2#vending_bench_2#2a3b3ffac8fb
    measured_by: benchmark_author
    effort: null
    harness: null
    sources:
    - source_id: model-160-vending-bench-2
      snapshot_ref: sha256:8724ee26281bff37eb4fe6af19bda2406b8d5fccdd4d54fdbfc44248b32ef12b
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: deepswe_v1_1
    model_id_as_evaluated: glm-5-2 (max)
    score: 43.78
    unit: percent
    source_url: https://deepswe.datacurve.ai/
    source_kind: benchmark_author
    evidence_date: '2026-09-25'
    date_type: evaluated
    verified_at: '2026-09-28'
    benchmark_version: DeepSWE v1.1, pass@1, mini-swe-agent
    configuration: Board row as copied in Epoch AI's benchmark data (deepswe_external.csv, https://epoch.ai/data/benchmark_data.zip),
      read 2026-09-24. Effort max; the highest-effort row for the model (MODEL-123 max-effort
      rule). Harness mini-swe-agent.
    limitations: A live board's standing, dated by the day ModelSpec read Epoch AI's copy; the
      copy carries no per-row date. Epoch AI data, CC BY 4.0.
    id: zhipu/glm-5-2#deepswe_v1_1#a13ec1b7e360
    measured_by: benchmark_author
    effort: max
    harness: unregistered
    sources:
    - source_id: model-160-deepswe-v1-1
      snapshot_ref: sha256:64010fde30846107b5210ba17347a269780973bf71eb8ce9c1d316a353733156
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: aime_2026
    model_id_as_evaluated: GLM 5.2
    score: 90.0
    unit: percent
    source_url: https://matharena.ai/competition_tables/aime--aime_2026
    source_kind: independent_evaluator
    evidence_date: '2026-09-25'
    date_type: evaluated
    verified_at: '2026-09-28'
    benchmark_version: AIME 2026, MathArena final-answer table
    configuration: MathArena competition table read 2026-09-24; the table states no run date,
      so the reading is dated by the observation. Effort default; highest-effort row for the
      model. MathArena lists final-answer competitions as deprecated.
    limitations: 'MathArena marks this row: model was released after competition release, so
      contamination is possible.'
    id: zhipu/glm-5-2#aime_2026#be95f0de2f89
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-matharena-aime-2026
      snapshot_ref: sha256:af6ab2f2d086514b45f4a2a12858238247ddb81633a0992c73da928ac806f1c8
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  - benchmark_id: tau3_banking
    model_id_as_evaluated: GLM-5.2 (xhigh)
    score: 37.11
    unit: percent
    source_url: https://sierra-tau-bench-public.s3.us-west-2.amazonaws.com/submissions/glm-5-2_sierra_2026-08-04/submission.json
    source_kind: benchmark_author
    evidence_date: '2026-07-24'
    date_type: evaluated
    verified_at: '2026-09-28'
    benchmark_version: τ-Knowledge τ-Banking (banking_knowledge), pass^1
    configuration: τ-bench leaderboard submission glm-5-2_sierra_2026-08-04, submitted by Sierra;
      retrieval config alltools; reasoning effort xhigh; user simulator gpt-5.2; tau2-bench
      1.0.1. pass^4 13.402061855670103.
    limitations: Banking_knowledge evaluation with AllTools retrieval, GPT-5.2 low-reasoning
      user simulation, four trials, and seed 300.
    id: zhipu/glm-5-2#tau3_banking#a1fd7b3fddb7
    measured_by: benchmark_author
    effort: xhigh
    harness: null
    sources:
    - source_id: model-160-tau-bench-glm-5-2-sierra-2026-08-04
      snapshot_ref: sha256:c7d229b4c7d6a3a10f60fa940a56377f0465841574266bcc0994a640a404bf53
      cited_regions:
      - rows
    observed_at: '2026-09-28'
  benchmark_source: ''
  benchmark_as_of: ''
  benchmark_notes: ''
deployment:
  api_only: false
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
  models_dev_url: https://models.dev/zhipu
  provider_docs_url: https://docs.z.ai/guides/llm/glm-5.2
  huggingface_url: https://huggingface.co/zai-org/GLM-5.2
  arxiv_url: ''
  paper_url: ''
  github_url: ''
  ollama_url: ''
  artificial_analysis_url: ''
  arena_url: ''
  last_scraped_models_dev: ''
  last_scraped_huggingface: ''
  last_scraped_benchmarks: ''
  last_scraped_pricing: '2026-09-10'
facts:
- facet: model.class
  value: text-generator
  state: known
  sources:
  - source_id: model-143-zhipu-glm-5-2
    snapshot_ref: sha256:7ba22185651d8f69fbf6227ee718eb680fd834ec8e79ba78df6fa54896614b3d
    cited_regions:
    - model-spec
  - source_id: model-143-zai-glm-5-2-guide
    snapshot_ref: sha256:18952b9061a41540d9800a5c9522ae762403538fdbb366d24591c416db6c481c
    cited_regions:
    - audit
  - source_id: model-143-zai-glm-5-3-guide
    snapshot_ref: sha256:3bb6cb24fec34e806be0fbc2201399aaae38550431612d96d359284e08d1d8c5
    cited_regions:
    - audit
- facet: model.input_modalities
  value:
  - text
  state: known
  sources:
  - source_id: model-143-zhipu-glm-5-2
    snapshot_ref: sha256:7ba22185651d8f69fbf6227ee718eb680fd834ec8e79ba78df6fa54896614b3d
    cited_regions:
    - model-spec
  - source_id: model-143-zai-glm-5-2-guide
    snapshot_ref: sha256:18952b9061a41540d9800a5c9522ae762403538fdbb366d24591c416db6c481c
    cited_regions:
    - audit
  - source_id: model-143-zai-glm-5-3-guide
    snapshot_ref: sha256:3bb6cb24fec34e806be0fbc2201399aaae38550431612d96d359284e08d1d8c5
    cited_regions:
    - audit
- facet: model.output_modalities
  value:
  - text
  state: known
  sources:
  - source_id: model-143-zhipu-glm-5-2
    snapshot_ref: sha256:7ba22185651d8f69fbf6227ee718eb680fd834ec8e79ba78df6fa54896614b3d
    cited_regions:
    - model-spec
  - source_id: model-143-zai-glm-5-2-guide
    snapshot_ref: sha256:18952b9061a41540d9800a5c9522ae762403538fdbb366d24591c416db6c481c
    cited_regions:
    - audit
  - source_id: model-143-zai-glm-5-3-guide
    snapshot_ref: sha256:3bb6cb24fec34e806be0fbc2201399aaae38550431612d96d359284e08d1d8c5
    cited_regions:
    - audit
- facet: model.context_window
  value: 1000000
  state: known
  sources:
  - source_id: model-143-zhipu-glm-5-2
    snapshot_ref: sha256:7ba22185651d8f69fbf6227ee718eb680fd834ec8e79ba78df6fa54896614b3d
    cited_regions:
    - model-spec
  - source_id: model-143-zai-glm-5-2-guide
    snapshot_ref: sha256:18952b9061a41540d9800a5c9522ae762403538fdbb366d24591c416db6c481c
    cited_regions:
    - audit
  - source_id: model-143-zai-glm-5-3-guide
    snapshot_ref: sha256:3bb6cb24fec34e806be0fbc2201399aaae38550431612d96d359284e08d1d8c5
    cited_regions:
    - audit
- facet: model.max_output_tokens
  value: 131072
  state: known
  sources:
  - source_id: model-143-zhipu-glm-5-2
    snapshot_ref: sha256:7ba22185651d8f69fbf6227ee718eb680fd834ec8e79ba78df6fa54896614b3d
    cited_regions:
    - model-spec
  - source_id: model-143-zai-glm-5-2-guide
    snapshot_ref: sha256:18952b9061a41540d9800a5c9522ae762403538fdbb366d24591c416db6c481c
    cited_regions:
    - audit
  - source_id: model-143-zai-glm-5-3-guide
    snapshot_ref: sha256:3bb6cb24fec34e806be0fbc2201399aaae38550431612d96d359284e08d1d8c5
    cited_regions:
    - audit
- facet: model.weights_openness
  value: open_weights
  state: known
  sources:
  - source_id: model-143-zhipu-glm-5-2
    snapshot_ref: sha256:7ba22185651d8f69fbf6227ee718eb680fd834ec8e79ba78df6fa54896614b3d
    cited_regions:
    - model-spec
  - source_id: model-143-hf-metadata-zhipu-glm-5-2
    snapshot_ref: sha256:b598dfd5e7af7a5d351302ec785bfc7c4354c4d07059b629f375d812b50402f2
    cited_regions:
    - audit
  - source_id: model-143-mit-license
    snapshot_ref: sha256:5d6e376a9522dce46e757b6200e0bab35dac1cf8286aadad4f9195cc841cc43b
    cited_regions:
    - audit
  - source_id: model-143-zai-glm-5-2-guide
    snapshot_ref: sha256:18952b9061a41540d9800a5c9522ae762403538fdbb366d24591c416db6c481c
    cited_regions:
    - audit
  - source_id: model-143-zai-glm-5-3-guide
    snapshot_ref: sha256:3bb6cb24fec34e806be0fbc2201399aaae38550431612d96d359284e08d1d8c5
    cited_regions:
    - audit
- facet: licence.commercial_use
  value: permitted
  state: known
  sources:
  - source_id: model-143-zhipu-glm-5-2
    snapshot_ref: sha256:7ba22185651d8f69fbf6227ee718eb680fd834ec8e79ba78df6fa54896614b3d
    cited_regions:
    - model-spec
  - source_id: model-143-mit-license
    snapshot_ref: sha256:5d6e376a9522dce46e757b6200e0bab35dac1cf8286aadad4f9195cc841cc43b
    cited_regions:
    - audit
- facet: licence.user_cap
  value: unbounded
  state: known
  sources:
  - source_id: model-143-zhipu-glm-5-2
    snapshot_ref: sha256:7ba22185651d8f69fbf6227ee718eb680fd834ec8e79ba78df6fa54896614b3d
    cited_regions:
    - model-spec
  - source_id: model-143-mit-license
    snapshot_ref: sha256:5d6e376a9522dce46e757b6200e0bab35dac1cf8286aadad4f9195cc841cc43b
    cited_regions:
    - audit
- facet: licence.output_training
  value: permitted
  state: known
  sources:
  - source_id: model-143-zhipu-glm-5-2
    snapshot_ref: sha256:7ba22185651d8f69fbf6227ee718eb680fd834ec8e79ba78df6fa54896614b3d
    cited_regions:
    - model-spec
  - source_id: model-143-mit-license
    snapshot_ref: sha256:5d6e376a9522dce46e757b6200e0bab35dac1cf8286aadad4f9195cc841cc43b
    cited_regions:
    - audit
- facet: licence.fine_tuning
  value: permitted
  state: known
  sources:
  - source_id: model-143-zhipu-glm-5-2
    snapshot_ref: sha256:7ba22185651d8f69fbf6227ee718eb680fd834ec8e79ba78df6fa54896614b3d
    cited_regions:
    - model-spec
  - source_id: model-143-mit-license
    snapshot_ref: sha256:5d6e376a9522dce46e757b6200e0bab35dac1cf8286aadad4f9195cc841cc43b
    cited_regions:
    - audit
- facet: origin.lab_jurisdiction
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-zhipu-glm-5-2
    snapshot_ref: sha256:7ba22185651d8f69fbf6227ee718eb680fd834ec8e79ba78df6fa54896614b3d
    cited_regions:
    - model-spec
  - source_id: model-143-zai-glm-5-2-guide
    snapshot_ref: sha256:18952b9061a41540d9800a5c9522ae762403538fdbb366d24591c416db6c481c
    cited_regions:
    - audit
  - source_id: model-143-zai-glm-5-3-guide
    snapshot_ref: sha256:3bb6cb24fec34e806be0fbc2201399aaae38550431612d96d359284e08d1d8c5
    cited_regions:
    - audit
  - source_id: model-143-mit-license
    snapshot_ref: sha256:5d6e376a9522dce46e757b6200e0bab35dac1cf8286aadad4f9195cc841cc43b
    cited_regions:
    - audit
  - source_id: model-143-hf-metadata-zhipu-glm-5-2
    snapshot_ref: sha256:b598dfd5e7af7a5d351302ec785bfc7c4354c4d07059b629f375d812b50402f2
    cited_regions:
    - audit
  checked_sources:
  - model-143-zhipu-glm-5-2
  - model-143-zai-glm-5-2-guide
  - model-143-zai-glm-5-3-guide
  - model-143-mit-license
  - model-143-hf-metadata-zhipu-glm-5-2
- facet: origin.base_lineage
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-zhipu-glm-5-2
    snapshot_ref: sha256:7ba22185651d8f69fbf6227ee718eb680fd834ec8e79ba78df6fa54896614b3d
    cited_regions:
    - model-spec
  - source_id: model-143-zai-glm-5-2-guide
    snapshot_ref: sha256:18952b9061a41540d9800a5c9522ae762403538fdbb366d24591c416db6c481c
    cited_regions:
    - audit
  - source_id: model-143-zai-glm-5-3-guide
    snapshot_ref: sha256:3bb6cb24fec34e806be0fbc2201399aaae38550431612d96d359284e08d1d8c5
    cited_regions:
    - audit
  - source_id: model-143-mit-license
    snapshot_ref: sha256:5d6e376a9522dce46e757b6200e0bab35dac1cf8286aadad4f9195cc841cc43b
    cited_regions:
    - audit
  - source_id: model-143-hf-metadata-zhipu-glm-5-2
    snapshot_ref: sha256:b598dfd5e7af7a5d351302ec785bfc7c4354c4d07059b629f375d812b50402f2
    cited_regions:
    - audit
  checked_sources:
  - model-143-zhipu-glm-5-2
  - model-143-zai-glm-5-2-guide
  - model-143-zai-glm-5-3-guide
  - model-143-mit-license
  - model-143-hf-metadata-zhipu-glm-5-2
- facet: origin.weights_hosting
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-zhipu-glm-5-2
    snapshot_ref: sha256:7ba22185651d8f69fbf6227ee718eb680fd834ec8e79ba78df6fa54896614b3d
    cited_regions:
    - model-spec
  - source_id: model-143-zai-glm-5-2-guide
    snapshot_ref: sha256:18952b9061a41540d9800a5c9522ae762403538fdbb366d24591c416db6c481c
    cited_regions:
    - audit
  - source_id: model-143-zai-glm-5-3-guide
    snapshot_ref: sha256:3bb6cb24fec34e806be0fbc2201399aaae38550431612d96d359284e08d1d8c5
    cited_regions:
    - audit
  - source_id: model-143-mit-license
    snapshot_ref: sha256:5d6e376a9522dce46e757b6200e0bab35dac1cf8286aadad4f9195cc841cc43b
    cited_regions:
    - audit
  - source_id: model-143-hf-metadata-zhipu-glm-5-2
    snapshot_ref: sha256:b598dfd5e7af7a5d351302ec785bfc7c4354c4d07059b629f375d812b50402f2
    cited_regions:
    - audit
  checked_sources:
  - model-143-zhipu-glm-5-2
  - model-143-zai-glm-5-2-guide
  - model-143-zai-glm-5-3-guide
  - model-143-mit-license
  - model-143-hf-metadata-zhipu-glm-5-2
- facet: model.release_date
  value: '2026-06-13'
  state: known
  sources:
  - source_id: model-143-zhipu-glm-5-2
    snapshot_ref: sha256:7ba22185651d8f69fbf6227ee718eb680fd834ec8e79ba78df6fa54896614b3d
    cited_regions:
    - model-spec
  - source_id: model-143-hf-metadata-zhipu-glm-5-2
    snapshot_ref: sha256:b598dfd5e7af7a5d351302ec785bfc7c4354c4d07059b629f375d812b50402f2
    cited_regions:
    - audit
  - source_id: model-143-zai-glm-5-2-guide
    snapshot_ref: sha256:18952b9061a41540d9800a5c9522ae762403538fdbb366d24591c416db6c481c
    cited_regions:
    - audit
  - source_id: model-143-zai-glm-5-3-guide
    snapshot_ref: sha256:3bb6cb24fec34e806be0fbc2201399aaae38550431612d96d359284e08d1d8c5
    cited_regions:
    - audit
- facet: model.lifecycle
  value: active
  state: known
  sources:
  - source_id: model-143-zhipu-glm-5-2
    snapshot_ref: sha256:7ba22185651d8f69fbf6227ee718eb680fd834ec8e79ba78df6fa54896614b3d
    cited_regions:
    - model-spec
  - source_id: model-143-hf-metadata-zhipu-glm-5-2
    snapshot_ref: sha256:b598dfd5e7af7a5d351302ec785bfc7c4354c4d07059b629f375d812b50402f2
    cited_regions:
    - audit
  - source_id: model-143-zai-glm-5-2-guide
    snapshot_ref: sha256:18952b9061a41540d9800a5c9522ae762403538fdbb366d24591c416db6c481c
    cited_regions:
    - audit
  - source_id: model-143-zai-glm-5-3-guide
    snapshot_ref: sha256:3bb6cb24fec34e806be0fbc2201399aaae38550431612d96d359284e08d1d8c5
    cited_regions:
    - audit
- facet: feature.tool_calling
  value: true
  state: known
  sources:
  - source_id: model-143-zhipu-glm-5-2
    snapshot_ref: sha256:7ba22185651d8f69fbf6227ee718eb680fd834ec8e79ba78df6fa54896614b3d
    cited_regions:
    - model-spec
  - source_id: model-143-zai-glm-5-2-guide
    snapshot_ref: sha256:18952b9061a41540d9800a5c9522ae762403538fdbb366d24591c416db6c481c
    cited_regions:
    - audit
  - source_id: model-143-zai-glm-5-3-guide
    snapshot_ref: sha256:3bb6cb24fec34e806be0fbc2201399aaae38550431612d96d359284e08d1d8c5
    cited_regions:
    - audit
- facet: feature.structured_output
  value: true
  state: known
  sources:
  - source_id: model-143-zhipu-glm-5-2
    snapshot_ref: sha256:7ba22185651d8f69fbf6227ee718eb680fd834ec8e79ba78df6fa54896614b3d
    cited_regions:
    - model-spec
  - source_id: model-143-zai-glm-5-2-guide
    snapshot_ref: sha256:18952b9061a41540d9800a5c9522ae762403538fdbb366d24591c416db6c481c
    cited_regions:
    - audit
  - source_id: model-143-zai-glm-5-3-guide
    snapshot_ref: sha256:3bb6cb24fec34e806be0fbc2201399aaae38550431612d96d359284e08d1d8c5
    cited_regions:
    - audit
- facet: feature.effort_controls
  value: true
  state: known
  sources:
  - source_id: model-143-zhipu-glm-5-2
    snapshot_ref: sha256:7ba22185651d8f69fbf6227ee718eb680fd834ec8e79ba78df6fa54896614b3d
    cited_regions:
    - model-spec
  - source_id: model-143-zai-glm-5-2-guide
    snapshot_ref: sha256:18952b9061a41540d9800a5c9522ae762403538fdbb366d24591c416db6c481c
    cited_regions:
    - audit
  - source_id: model-143-zai-glm-5-3-guide
    snapshot_ref: sha256:3bb6cb24fec34e806be0fbc2201399aaae38550431612d96d359284e08d1d8c5
    cited_regions:
    - audit
- facet: feature.batch
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-zhipu-glm-5-2
    snapshot_ref: sha256:7ba22185651d8f69fbf6227ee718eb680fd834ec8e79ba78df6fa54896614b3d
    cited_regions:
    - model-spec
  - source_id: model-143-zai-glm-5-2-guide
    snapshot_ref: sha256:18952b9061a41540d9800a5c9522ae762403538fdbb366d24591c416db6c481c
    cited_regions:
    - audit
  - source_id: model-143-zai-glm-5-3-guide
    snapshot_ref: sha256:3bb6cb24fec34e806be0fbc2201399aaae38550431612d96d359284e08d1d8c5
    cited_regions:
    - audit
  - source_id: model-143-mit-license
    snapshot_ref: sha256:5d6e376a9522dce46e757b6200e0bab35dac1cf8286aadad4f9195cc841cc43b
    cited_regions:
    - audit
  - source_id: model-143-hf-metadata-zhipu-glm-5-2
    snapshot_ref: sha256:b598dfd5e7af7a5d351302ec785bfc7c4354c4d07059b629f375d812b50402f2
    cited_regions:
    - audit
  checked_sources:
  - model-143-zhipu-glm-5-2
  - model-143-zai-glm-5-2-guide
  - model-143-zai-glm-5-3-guide
  - model-143-mit-license
  - model-143-hf-metadata-zhipu-glm-5-2
- facet: feature.streaming
  value: true
  state: known
  sources:
  - source_id: model-143-zhipu-glm-5-2
    snapshot_ref: sha256:7ba22185651d8f69fbf6227ee718eb680fd834ec8e79ba78df6fa54896614b3d
    cited_regions:
    - model-spec
  - source_id: model-143-zai-glm-5-2-guide
    snapshot_ref: sha256:18952b9061a41540d9800a5c9522ae762403538fdbb366d24591c416db6c481c
    cited_regions:
    - audit
  - source_id: model-143-zai-glm-5-3-guide
    snapshot_ref: sha256:3bb6cb24fec34e806be0fbc2201399aaae38550431612d96d359284e08d1d8c5
    cited_regions:
    - audit
card_schema_version: '3.0'
card_author: models.dev-seeder
card_created: '2026-04-05'
card_updated: '2026-04-05'
---

# GLM-5.2

GLM-5.2 is Z.ai's flagship open-weight model for long-horizon coding and agent tasks. It is the same size as GLM-5.1 (744B total / 40B active) with a solid 1M-token context. Weights: https://huggingface.co/zai-org/GLM-5.2

## Key Features
- Extended reasoning / chain-of-thought
- Function calling / tool use
- Structured output (JSON mode)
- Open weights (MIT)
