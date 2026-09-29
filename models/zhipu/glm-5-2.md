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
    verified_at: '2026-09-29'
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
      snapshot_ref: sha256:bea7ea9d7344aeccaed159b64f2f3aa97e84231d3723b02f9d4a5672b6b889b8
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_coding
    model_id_as_evaluated: glm-5.2-max
    score: 1509.81
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
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
      snapshot_ref: sha256:da249e40e0397ffcd8dd5f738c4c91f9a389869f8ae9e26c425a1187f04c7118
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_hard_prompts
    model_id_as_evaluated: glm-5.2-max
    score: 1493.08
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
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
      snapshot_ref: sha256:5a69c3a3a5f23cf6bfd2b0ecae495ec9731f62df889f4147793616588a2d4f8b
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_math
    model_id_as_evaluated: glm-5.2-max
    score: 1479.48
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
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
      snapshot_ref: sha256:41e622d3837a9ab1577d975e3c57ae92db367c09f45606ed1870a32a4591335a
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_creative_writing
    model_id_as_evaluated: glm-5.2-max
    score: 1450.95
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
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
      snapshot_ref: sha256:4ca49a5b7efede8e577057d10266b363a837e56331ac79f7540f7da349a3eee5
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_instruction_following
    model_id_as_evaluated: glm-5.2-max
    score: 1466.16
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
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
      snapshot_ref: sha256:6bcc35b68ac189cda1a204de4fab84c84fcd9d853dc2c3265e68366133d9093b
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_multi_turn
    model_id_as_evaluated: glm-5.2-max
    score: 1468.92
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
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
      snapshot_ref: sha256:76f93ba07e2611ee096faf4210eb6b965b5b113b375cb5edec5f224be61fc346
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_expert
    model_id_as_evaluated: glm-5.2-max
    score: 1493.72
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
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
      snapshot_ref: sha256:ebf8116274f3815b353511b1829bd763a0817e2a0c5d3669072ebd5571271745
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_longer_query
    model_id_as_evaluated: glm-5.2-max
    score: 1483.27
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
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
      snapshot_ref: sha256:3c7de94587c842e12c134292a7df52a9faafb46f877d184d8f235d5c1d466737
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_non_english
    model_id_as_evaluated: glm-5.2-max
    score: 1458.33
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
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
      snapshot_ref: sha256:47f41bf8222f55644ca4a36db5ad4178546c5d3e2982bcda2dc08798f9776a65
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_medicine
    model_id_as_evaluated: glm-5.2-max
    score: 1485.29
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
      snapshot_ref: sha256:31163709a3917ed23ec956a2589a6a5ad30924817977652909218ecbbf9a8d0e
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_legal
    model_id_as_evaluated: glm-5.2-max
    score: 1479.37
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
      snapshot_ref: sha256:6aec9d4dd9fc82958ffeceea56c977de5d8204f6c62ad5113657b828f9bc55da
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_business
    model_id_as_evaluated: glm-5.2-max
    score: 1459.75
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
      snapshot_ref: sha256:ba565a81fbb65e9d13c80776fda09aabedc819d64793b355a5a5fe836212472e
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_science
    model_id_as_evaluated: glm-5.2-max
    score: 1490.66
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
      snapshot_ref: sha256:dff891db693196c263ad841fcb75cf135a4529936b386a76fc324e6b66bb2d2e
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_writing
    model_id_as_evaluated: glm-5.2-max
    score: 1455.16
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
      snapshot_ref: sha256:451771d6d03dfcdc902ebbb505ce47bfc614e33bde751b42f3be31d89d416086
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_webdev
    model_id_as_evaluated: glm-5.2-max
    score: 1599.52
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-23'
    date_type: published
    verified_at: '2026-09-29'
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
      snapshot_ref: sha256:1342f43f483667f8e4313a1fb517522e1f18aa1b09d4812f8d3163c4ff30b9bc
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: gpqa_diamond
    model_id_as_evaluated: glm-5.2_max
    score: 91.86
    unit: percent
    source_url: https://epoch.ai/benchmarks/gpqa-diamond
    source_kind: independent_evaluator
    evidence_date: '2026-06-24'
    date_type: evaluated
    verified_at: '2026-09-29'
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
      snapshot_ref: sha256:39583bb153c2d06652ef7e4886b645abb7ea53fe3b7bb6c8aaeccef4055705cb
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: frontiermath_tiers_1_3_v2
    model_id_as_evaluated: glm-5.2_max
    score: 59.21
    unit: percent
    source_url: https://epoch.ai/frontiermath
    source_kind: independent_evaluator
    evidence_date: '2026-06-19'
    date_type: evaluated
    verified_at: '2026-09-29'
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
      snapshot_ref: sha256:cae4d7f40f600006a0cbd47a4ced7d916a96f50953b9a454830dd46b20aa4c1a
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: simpleqa_verified
    model_id_as_evaluated: glm-5.2_max
    score: 34.2
    unit: percent
    source_url: https://epoch.ai/benchmarks/simpleqa-verified
    source_kind: independent_evaluator
    evidence_date: '2026-08-27'
    date_type: evaluated
    verified_at: '2026-09-29'
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
      snapshot_ref: sha256:33e4a89c307a2e5d6941be7ad13770315c4eff899ed69e92490cd697bdb5a584
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: swe_bench_verified
    model_id_as_evaluated: glm-5.2_max
    score: 78.7
    unit: percent
    source_url: https://epoch.ai/benchmarks/swe-bench-verified
    source_kind: independent_evaluator
    evidence_date: '2026-06-25'
    date_type: evaluated
    verified_at: '2026-09-29'
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
      snapshot_ref: sha256:b6f26a6b1de09762a56e4ae4de985d4b7aa8588bdf6035fdd7a206c164f6bbb4
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: frontiercode_v1_1
    model_id_as_evaluated: GLM 5.2
    score: 24.5
    unit: percent
    source_url: https://cognition.com/frontiercode
    source_kind: benchmark_author
    evidence_date: '2026-09-29'
    date_type: evaluated
    verified_at: '2026-09-29'
    benchmark_version: FrontierCode 1.1, main score (Mean@5)
    configuration: Board row as copied in Epoch AI's benchmark data (frontiercode_external.csv,
      https://epoch.ai/data/benchmark_data.zip), read 2026-09-24. Effort none; the highest-effort
      row for the model (MODEL-123 max-effort rule). Harness mini-swe-agent.
    limitations: A live board's standing, dated by the day ModelSpec read Epoch AI's copy; the
      copy carries no per-row date. Epoch AI data, CC BY 4.0.
    id: zhipu/glm-5-2#frontiercode_v1_1#3ec016aab703
    measured_by: benchmark_author
    effort: null
    harness: unregistered
    sources:
    - source_id: model-160-frontiercode
      snapshot_ref: sha256:cd845eb12dc06498f07c3729c9725cf61ad153cacb7580918f8b955e443b4add
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: vending_bench_2
    model_id_as_evaluated: GLM-5.2
    score: 8313.78
    unit: USD
    source_url: https://andonlabs.com/evals/vending-bench-2
    source_kind: benchmark_author
    evidence_date: '2026-09-29'
    date_type: evaluated
    verified_at: '2026-09-29'
    benchmark_version: Vending-Bench 2, mean final balance over 5 runs
    configuration: Board row as copied in Epoch AI's benchmark data (vending_bench_2_external.csv,
      https://epoch.ai/data/benchmark_data.zip), read 2026-09-24. Effort unknown; the highest-effort
      row for the model (MODEL-123 max-effort rule).
    limitations: A live board's standing, dated by the day ModelSpec read Epoch AI's copy; the
      copy carries no per-row date. Epoch AI data, CC BY 4.0.
    id: zhipu/glm-5-2#vending_bench_2#6152efe4cfec
    measured_by: benchmark_author
    effort: null
    harness: null
    sources:
    - source_id: model-160-vending-bench-2
      snapshot_ref: sha256:94074584ec83e973b31884f48956a6bc43e36a33d47dc3feaa7c52adf23a9c12
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: deepswe_v1_1
    model_id_as_evaluated: glm-5-2 (max)
    score: 43.78
    unit: percent
    source_url: https://deepswe.datacurve.ai/
    source_kind: benchmark_author
    evidence_date: '2026-09-29'
    date_type: evaluated
    verified_at: '2026-09-29'
    benchmark_version: DeepSWE v1.1, pass@1, mini-swe-agent
    configuration: Board row as copied in Epoch AI's benchmark data (deepswe_external.csv, https://epoch.ai/data/benchmark_data.zip),
      read 2026-09-24. Effort max; the highest-effort row for the model (MODEL-123 max-effort
      rule). Harness mini-swe-agent.
    limitations: A live board's standing, dated by the day ModelSpec read Epoch AI's copy; the
      copy carries no per-row date. Epoch AI data, CC BY 4.0.
    id: zhipu/glm-5-2#deepswe_v1_1#9db007df07b9
    measured_by: benchmark_author
    effort: max
    harness: unregistered
    sources:
    - source_id: model-160-deepswe-v1-1
      snapshot_ref: sha256:33c505b573a474e601643fe1e1295b91b10e3ef62dfeab167a3851226358c972
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: aime_2026
    model_id_as_evaluated: GLM 5.2
    score: 90.0
    unit: percent
    source_url: https://matharena.ai/competition_tables/aime--aime_2026
    source_kind: independent_evaluator
    evidence_date: '2026-09-29'
    date_type: evaluated
    verified_at: '2026-09-29'
    benchmark_version: AIME 2026, MathArena final-answer table
    configuration: MathArena competition table read 2026-09-26; the table states no run
      date, so the reading is dated by the observation. Effort default; highest-effort
      row for the model. MathArena lists final-answer competitions as deprecated.
    limitations: 'MathArena marks this row: model was released after competition release, so
      contamination is possible.'
    id: zhipu/glm-5-2#aime_2026#73dede75f448
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-matharena-aime-2026
      snapshot_ref: sha256:82521ecfb14888fcf11b8fe08e9aa67eb588467d241b6778ecd538ae6d382b5e
      cited_regions:
      - rows
    quality_flags:
    - deprecated
    - contamination_warning
    observed_at: '2026-09-29'
  - benchmark_id: tau3_banking
    model_id_as_evaluated: GLM-5.2 (xhigh)
    score: 37.11
    unit: percent
    source_url: https://sierra-tau-bench-public.s3.us-west-2.amazonaws.com/submissions/glm-5-2_sierra_2026-08-04/submission.json
    source_kind: benchmark_author
    evidence_date: '2026-07-24'
    date_type: evaluated
    verified_at: '2026-09-29'
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
      snapshot_ref: sha256:59779e1eb134c7dd4ba8278a9a3a3f03d091673f6067392a15e3a79a1fdef4de
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_english
    model_id_as_evaluated: glm-5.2-max
    score: 1478.78
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / english, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1478.78 [1472.94,
      1484.63], 15630 votes, rank 35. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:cee57baa7239c5aa2091dcb5db0b4c2ac22cec732b235d66c0cda2ee55bdcb44
      cited_regions:
      - rows
    id: zhipu/glm-5-2#arena_sc_english#24cc263a3631
  - benchmark_id: arena_sc_chinese
    model_id_as_evaluated: glm-5.2-max
    score: 1516.63
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / chinese, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1516.63 [1503.78,
      1529.49], 2282 votes, rank 31. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:9bf00fc37e8a997735f423949aba6ffc5551990b6f835297d3fed2b364abe02b
      cited_regions:
      - rows
    id: zhipu/glm-5-2#arena_sc_chinese#eb4b89903b4e
  - benchmark_id: arena_sc_japanese
    model_id_as_evaluated: glm-5.2-max
    score: 1452.48
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / japanese, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1452.48 [1425.80,
      1479.15], 580 votes, rank 28. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:13b68c219a1ec549a9336846ddacaf97471f6323c09e4f45a73eab7a0857a9ca
      cited_regions:
      - rows
    id: zhipu/glm-5-2#arena_sc_japanese#56cb91a7468b
  - benchmark_id: arena_sc_korean
    model_id_as_evaluated: glm-5.2-max
    score: 1440.47
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / korean, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1440.47 [1417.88,
      1463.07], 740 votes, rank 25. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:96706e685de18541b6ad515db22607a7840bad8bc902a30a8a38f949cd409c08
      cited_regions:
      - rows
    id: zhipu/glm-5-2#arena_sc_korean#7cbea5f97298
  - benchmark_id: arena_sc_russian
    model_id_as_evaluated: glm-5.2-max
    score: 1464.61
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / russian, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1464.61 [1454.73,
      1474.48], 3910 votes, rank 47. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:eb77af068077fa90a9514ad454b6a65f061a176f0d68897132e1526f3be743dd
      cited_regions:
      - rows
    id: zhipu/glm-5-2#arena_sc_russian#feaa94f3fc33
  - benchmark_id: arena_sc_spanish
    model_id_as_evaluated: glm-5.2-max
    score: 1476.27
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / spanish, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1476.27 [1457.43,
      1495.11], 1080 votes, rank 16. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:e56e27431afb859f3376e3d5609785906e24647b4c0c65a324b7995944b9573b
      cited_regions:
      - rows
    id: zhipu/glm-5-2#arena_sc_spanish#c8ff59521e07
  - benchmark_id: arena_sc_german
    model_id_as_evaluated: glm-5.2-max
    score: 1473.66
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / german, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1473.66 [1450.50,
      1496.82], 686 votes, rank 31. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:098d6730e0b426da68eee86ddfd97bb03c3b1048e178378de1ec3924fa209c6d
      cited_regions:
      - rows
    id: zhipu/glm-5-2#arena_sc_german#a6647dc9cedf
  - benchmark_id: arena_sc_french
    model_id_as_evaluated: glm-5.2-max
    score: 1491.48
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / french, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1491.48 [1473.55,
      1509.40], 1310 votes, rank 29. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:c6c9f83eb7147bedac479a445a3803aad09d613643414d3cd5035dbde46d6f2f
      cited_regions:
      - rows
    id: zhipu/glm-5-2#arena_sc_french#01055ffa3e21
  - benchmark_id: arena_sc_polish
    model_id_as_evaluated: glm-5.2-max
    score: 1452.03
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / polish, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1452.03 [1428.03,
      1476.02], 616 votes, rank 59. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:a99daf2dc2fbf9b06de90a127cc1408c7a19e4fa45a1a4d538b668211c4b5892
      cited_regions:
      - rows
    id: zhipu/glm-5-2#arena_sc_polish#83f95d0b941a
  - benchmark_id: arena_sc_industry_software_it_services
    model_id_as_evaluated: glm-5.2-max
    score: 1501.85
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / industry_software_and_it_services, latest split, revision
      1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1501.85 [1495.80,
      1507.91], 14686 votes, rank 45. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:4eaa9890dce0719aa263af890c9f2a7bb1a3198e291d84dbf8c1371d4f150c52
      cited_regions:
      - rows
    id: zhipu/glm-5-2#arena_sc_industry_software_it_services#c55b8c1c0dc3
  - benchmark_id: arena_sc_industry_entertainment_sports_media
    model_id_as_evaluated: glm-5.2-max
    score: 1441.94
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / industry_entertainment_and_sports_and_media, latest
      split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1441.94 [1434.59,
      1449.29], 8941 votes, rank 43. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:df0d5e7c4d4ce1f683618242c0786eafd164d98b3b49dbaa6e699476bec94ccf
      cited_regions:
      - rows
    id: zhipu/glm-5-2#arena_sc_industry_entertainment_sports_media#9b352461aead
  - benchmark_id: arena_sc_industry_mathematical
    model_id_as_evaluated: glm-5.2-max
    score: 1488.31
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / industry_mathematical, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1488.31 [1474.64,
      1501.99], 1983 votes, rank 30. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:b0f3ee924239a7a9a1e60676935d0c83091f29517b8acb95e07868e370822e82
      cited_regions:
      - rows
    id: zhipu/glm-5-2#arena_sc_industry_mathematical#b62a265892c1
  - benchmark_id: arena_sc_factuality
    model_id_as_evaluated: glm-5.2-max
    score: 1461.05
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_factuality / overall, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1461.05 [1457.43,
      1464.67], 36648 votes, rank 39. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-factuality
      snapshot_ref: sha256:ece0fd0afe2b42a38bce698a6be5329044b5503f5edb7f43473c19394b38fc28
      cited_regions:
      - rows
    id: zhipu/glm-5-2#arena_sc_factuality#3098fedb40e6
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
- id: zhipu/glm-5-2#model.fits_hardware
  subject:
    kind: model
    id: zhipu/glm-5-2
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
      parameters_total: 753329940480
      working_allowance: 0.25
      quant_bytes: '{''bf16'': 2.0, ''fp16'': 2.0, ''fp8'': 1.0, ''int4'': 0.5, ''int8'': 1.0, ''q4'':
        0.5, ''q5'': 0.625, ''q6'': 0.75}'
      has_device_unknowns: 'true'
      model_snapshot_ref: sha256:d8c63ddcbb44c4600545c9aae22f9300c698637abe911fbfb2ebe32f42f603de
      hardware_registry_sha256: sha256:10baf5e1ce9e5a1e5b970f4fdc25d9f67db8c562c8c109157ae9722bf6357bff
      hardware_device_count: 64
  sources:
  - source_id: model-174-zhipu-glm-5-2-hardware-input
    snapshot_ref: sha256:d8c63ddcbb44c4600545c9aae22f9300c698637abe911fbfb2ebe32f42f603de
    cited_regions:
    - rows
- id: zhipu/glm-5-2#model.parameters_total
  subject:
    kind: model
    id: zhipu/glm-5-2
  facet: model.parameters_total
  value: 753329940480
  state: known
  sources:
  - source_id: model-174-zhipu-glm-5-2-hardware-input
    snapshot_ref: sha256:d8c63ddcbb44c4600545c9aae22f9300c698637abe911fbfb2ebe32f42f603de
    cited_regions:
    - rows
- id: zhipu/glm-5-2#model.hardware_fit_indeterminate
  subject:
    kind: model
    id: zhipu/glm-5-2
  facet: model.hardware_fit_indeterminate
  value:
  - cerebras_wse3
  - nvidia_vera_rubin_superchip
  state: known
  sources:
  - source_id: model-174-zhipu-glm-5-2-hardware-input
    snapshot_ref: sha256:d8c63ddcbb44c4600545c9aae22f9300c698637abe911fbfb2ebe32f42f603de
    cited_regions:
    - rows
  derivation:
    method: decision.hardware.compute_fit@1
    formula: parameters_total * bytes_per_parameter <= memory_capacity_gb * (1 - working_allowance) *
      1e9
    inputs:
      weights_openness: open_weights
      parameters_total: 753329940480
      working_allowance: 0.25
      quant_bytes: '{''bf16'': 2.0, ''fp16'': 2.0, ''fp8'': 1.0, ''int4'': 0.5, ''int8'': 1.0, ''q4'':
        0.5, ''q5'': 0.625, ''q6'': 0.75}'
      has_device_unknowns: 'true'
      model_snapshot_ref: sha256:d8c63ddcbb44c4600545c9aae22f9300c698637abe911fbfb2ebe32f42f603de
      hardware_registry_sha256: sha256:10baf5e1ce9e5a1e5b970f4fdc25d9f67db8c562c8c109157ae9722bf6357bff
      hardware_device_count: 64
card_schema_version: '3.0'
card_author: models.dev-seeder
card_created: '2026-04-05'
card_updated: '2026-09-28'
---

# GLM-5.2

GLM-5.2 is Z.ai's flagship open-weight model for long-horizon coding and agent tasks. It is the same size as GLM-5.1 (744B total / 40B active) with a solid 1M-token context. Weights: https://huggingface.co/zai-org/GLM-5.2

## Key Features
- Extended reasoning / chain-of-thought
- Function calling / tool use
- Structured output (JSON mode)
- Open weights (MIT)
