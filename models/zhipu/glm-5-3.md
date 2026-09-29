---
model_id: zhipu/glm-5-3
display_name: GLM-5.3
provider: zhipu
provider_display: Z.ai (Zhipu AI)
family: glm
version: '5.3'
release_date: '2026-08-14'
last_updated: '2026-09-04'
status: active
model_type: llm-reasoning
model_subtypes:
- llm-code
tags:
- text-generation
- openai-compatible
pipeline_tag: text-generation
architecture:
  type: MoE
  total_parameters: 753329940480
  total_parameters_source: safetensors
  active_parameters: null
  num_experts: 256
  experts_per_token: 8
  num_layers: 78
  hidden_size: 6144
  intermediate_size: 12288
  attention_type: null
  num_attention_heads: 64
  num_kv_heads: 64
  positional_encoding: RoPE
  rope_theta: 8000000.0
  vocab_size: 154880
  tokenizer_type: null
  embedding_dimensions: null
  activation_function: ''
  precision_native: ''
  flash_attention: null
  tie_word_embeddings: false
  sliding_window_size: null
  vision_encoder: ''
  vision_resolution_max: ''
  vision_patch_size: null
  diffusion_scheduler: ''
  diffusion_steps_default: null
  vae_type: ''
lineage:
  base_model: zai-org/GLM-5.2
  base_model_relation: continuation
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
  license_type: other
  license_url: https://huggingface.co/zai-org/GLM-5.3/blob/main/LICENSE
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
  export_control_notes: Custom GLM-5.3 licence (Z.AI, 2026). Commercial use is granted,
    except Model-as-a-Service operators with >USD 10B trailing-12-month affiliate
    revenue, who must pass a Z.AI security review.
  origin_country: CN
  origin_org_type: private
modalities:
  input:
  - text
  output:
  - text
  text:
    max_input_tokens: null
    max_output_tokens: 131072
    context_window: 1048576
    streaming: true
    fill_in_middle: null
    json_mode: true
    system_prompt: true
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
    think_budget_control: true
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
  cache_read: 0.26
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
  note: USD per 1M tokens on the Z.ai API (https://docs.z.ai/guides/overview/pricing).
    Cached input storage is listed as limited-time free; cache_write left null.
availability:
  primary_provider:
    name: Z.ai
    platform_url: https://z.ai
    api_endpoint: https://api.z.ai/api/paas/v4
    npm_package: '@ai-sdk/openai-compatible'
    env_vars:
    - ZHIPU_API_KEY
    model_id_on_platform: glm-5.3
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
    model_id: zai-org/GLM-5.3
    url: https://www.together.ai/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  fireworks_ai:
    available: true
    model_id: accounts/fireworks/models/glm-5p3
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
    available: true
    model_id: z-ai/glm-5.3
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
    available: true
    model_id: zai-glm-5-3
    url: https://console.mistral.ai/
    fine_tuning: false
    gated: false
    regions: []
    notes: Listed on models.dev provider 'mistral'. Availability, not authorship (MODEL-82).
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
    available: true
    model_id: glm-5.3
    url: https://docs.z.ai/guides/llm/glm-5.3
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
    available: true
    model_id: glm-5.3
    url: https://ollama.com/library/glm-5.3
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
    model_id: zai-org/GLM-5.3
    url: https://huggingface.co/zai-org/GLM-5.3
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
    model_id_as_evaluated: glm-5.3-max
    score: 1483.02
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / overall, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category overall,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1483.02 [1476.58, 1489.46], 10960 votes,
      rank 19.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: zhipu/glm-5-3#arena_elo_style_control#d5d3e543a11f
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
    model_id_as_evaluated: glm-5.3-max
    score: 1524.01
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / coding, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category coding,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1524.01 [1512.42, 1535.61], 2846 votes,
      rank 22.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: zhipu/glm-5-3#arena_sc_coding#8351122c6a8d
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
    model_id_as_evaluated: glm-5.3-max
    score: 1506.93
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / hard_prompts, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category hard_prompts,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1506.93 [1499.25, 1514.61], 7161 votes,
      rank 17.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: zhipu/glm-5-3#arena_sc_hard_prompts#c42d0eb2337d
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
    model_id_as_evaluated: glm-5.3-max
    score: 1504.05
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / math, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category math, leaderboard_publish_date
      2026-09-13; style control. Highest-effort row for the product (effort: max; MODEL-123
      max-effort rule). Rating 1504.05 [1477.04, 1531.06], 430 votes, rank 10.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: zhipu/glm-5-3#arena_sc_math#125925b24320
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
    model_id_as_evaluated: glm-5.3-max
    score: 1462.38
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / creative_writing, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category creative_writing,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1462.38 [1449.45, 1475.32], 2436 votes,
      rank 22.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: zhipu/glm-5-3#arena_sc_creative_writing#bd6913acd311
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
    model_id_as_evaluated: glm-5.3-max
    score: 1480.37
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / instruction_following, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category instruction_following,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1480.37 [1470.26, 1490.48], 3825 votes,
      rank 17.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: zhipu/glm-5-3#arena_sc_instruction_following#2e4c404ae0cc
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
    model_id_as_evaluated: glm-5.3-max
    score: 1492.7
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / multi_turn, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category multi_turn,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1492.70 [1477.63, 1507.78], 1684 votes,
      rank 20.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: zhipu/glm-5-3#arena_sc_multi_turn#16b103baeb60
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
    model_id_as_evaluated: glm-5.3-max
    score: 1522.15
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / expert, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category expert,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1522.15 [1504.33, 1539.96], 1151 votes,
      rank 12.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: zhipu/glm-5-3#arena_sc_expert#d22a7e4d6406
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
    model_id_as_evaluated: glm-5.3-max
    score: 1491.88
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / longer_query, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category longer_query,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1491.88 [1482.95, 1500.82], 5257 votes,
      rank 22.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: zhipu/glm-5-3#arena_sc_longer_query#30aa4369919d
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
    model_id_as_evaluated: glm-5.3-max
    score: 1466.14
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / non_english, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category non_english,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1466.14 [1458.28, 1474.01], 6475 votes,
      rank 27.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: zhipu/glm-5-3#arena_sc_non_english#e22d345cac7b
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
    model_id_as_evaluated: glm-5.3-max
    score: 1499.1
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
      (effort: max; MODEL-123 max-effort rule). Rating 1499.10 [1477.27, 1520.92], 784 votes,
      rank 17.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: zhipu/glm-5-3#arena_sc_medicine#601e02fade9b
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
    model_id_as_evaluated: glm-5.3-max
    score: 1487.79
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
      (effort: max; MODEL-123 max-effort rule). Rating 1487.79 [1468.42, 1507.16], 984 votes,
      rank 23.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: zhipu/glm-5-3#arena_sc_legal#6484844e3158
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
    model_id_as_evaluated: glm-5.3-max
    score: 1470.31
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
      (effort: max; MODEL-123 max-effort rule). Rating 1470.31 [1456.92, 1483.70], 2089 votes,
      rank 34.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: zhipu/glm-5-3#arena_sc_business#db1615d59e1a
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
    model_id_as_evaluated: glm-5.3-max
    score: 1513.27
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
      (effort: max; MODEL-123 max-effort rule). Rating 1513.27 [1499.29, 1527.26], 1826 votes,
      rank 10.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: zhipu/glm-5-3#arena_sc_science#54b0a7740484
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
    model_id_as_evaluated: glm-5.3-max
    score: 1474.14
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
      (effort: max; MODEL-123 max-effort rule). Rating 1474.14 [1462.84, 1485.44], 3095 votes,
      rank 19.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: zhipu/glm-5-3#arena_sc_writing#4959437ff597
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
    model_id_as_evaluated: glm-5.3-max
    score: 1621.84
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-23'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: webdev / overall, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset webdev, category overall, leaderboard_publish_date
      2026-09-23; no style-controlled variant. Highest-effort row for the product (effort: max;
      MODEL-123 max-effort rule). Rating 1621.84 [1612.73, 1630.96], 5801 votes, rank 17.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: zhipu/glm-5-3#arena_webdev#d1d902f3e76b
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
    model_id_as_evaluated: glm-5.3_max
    score: 90.91
    unit: percent
    source_url: https://epoch.ai/benchmarks/gpqa-diamond
    source_kind: independent_evaluator
    evidence_date: '2026-08-24'
    date_type: evaluated
    verified_at: '2026-09-29'
    benchmark_version: GPQA Diamond (Epoch AI run)
    configuration: Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (gpqa_diamond.csv),
      read 2026-09-24. Run started 2026-08-24T19:44:18.000Z; effort max; highest-effort run
      for the model (MODEL-123 max-effort rule), newest on a tie. Standard error 1.59 points.
    limitations: Epoch AI data, CC BY 4.0.
    id: zhipu/glm-5-3#gpqa_diamond#f4493a16269f
    measured_by: independent_evaluator
    effort: max
    harness: null
    sources:
    - source_id: model-143-evidence-epoch-gpqa-diamond-csv
      snapshot_ref: sha256:946618a3befb5210ccf841c8f3c6b257584d10d5314a7e03408fb73aa13a38a9
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: frontiermath_tiers_1_3_v2
    model_id_as_evaluated: glm-5.3_max
    score: 68.77
    unit: percent
    source_url: https://epoch.ai/frontiermath
    source_kind: independent_evaluator
    evidence_date: '2026-08-25'
    date_type: evaluated
    verified_at: '2026-09-29'
    benchmark_version: FrontierMath-Tiers-1-3-v2-Private (Epoch AI run)
    configuration: Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (frontiermath_tiers_1_3_v2.csv),
      read 2026-09-24. Run started 2026-08-25T14:20:20.000Z; effort max; highest-effort run
      for the model (MODEL-123 max-effort rule), newest on a tie. Standard error 2.75 points.
    limitations: Epoch AI data, CC BY 4.0.
    id: zhipu/glm-5-3#frontiermath_tiers_1_3_v2#6580c4de9d2f
    measured_by: independent_evaluator
    effort: max
    harness: null
    sources:
    - source_id: model-143-evidence-epoch-frontiermath-tiers-1-3-v2-csv
      snapshot_ref: sha256:ff8b653f9ba2c936d6278eeecc42b3a3dee1079e409c8806616f80fb41e23c11
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: simpleqa_verified
    model_id_as_evaluated: glm-5.3_max
    score: 41.0
    unit: percent
    source_url: https://epoch.ai/benchmarks/simpleqa-verified
    source_kind: independent_evaluator
    evidence_date: '2026-08-28'
    date_type: evaluated
    verified_at: '2026-09-29'
    benchmark_version: SimpleQA Verified, proportion correct, Epoch AI protocol with anti-abstention
      prompt
    configuration: Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (simpleqa_verified.csv),
      read 2026-09-24. Run started 2026-08-28T17:00:06.000Z; effort max; highest-effort run
      for the model (MODEL-123 max-effort rule), newest on a tie. Standard error 1.56 points.
    limitations: Epoch AI data, CC BY 4.0.
    id: zhipu/glm-5-3#simpleqa_verified#c7d64319b553
    measured_by: independent_evaluator
    effort: max
    harness: null
    sources:
    - source_id: model-160-epoch-simpleqa-verified-csv
      snapshot_ref: sha256:f4e88f5154755ef9c355b28d6900467dce89bcbe0ea54329d1f96215c21239fa
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: frontiercode_v1_1
    model_id_as_evaluated: GLM 5.3
    score: 40.1
    unit: percent
    source_url: https://cognition.com/frontiercode
    source_kind: benchmark_author
    evidence_date: '2026-09-29'
    date_type: evaluated
    verified_at: '2026-09-29'
    benchmark_version: FrontierCode 1.1, main score (Mean@5)
    configuration: Board row as copied in Epoch AI's benchmark data (frontiercode_external.csv,
      https://epoch.ai/data/benchmark_data.zip), read 2026-09-24. Effort max; the highest-effort
      row for the model (MODEL-123 max-effort rule). Harness chisel.
    limitations: A live board's standing, dated by the day ModelSpec read Epoch AI's copy; the
      copy carries no per-row date. Epoch AI data, CC BY 4.0.
    id: zhipu/glm-5-3#frontiercode_v1_1#f5c9c1c1ae58
    measured_by: benchmark_author
    effort: max
    harness: unregistered
    sources:
    - source_id: model-160-frontiercode
      snapshot_ref: sha256:946a90057bea730dbfa5a27ab38168e01b5269492c1b41f46cf4ec29dd0d3cf3
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: vending_bench_2
    model_id_as_evaluated: GLM-5.3
    score: 8163.61
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
    id: zhipu/glm-5-3#vending_bench_2#5fb660647e9a
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
    model_id_as_evaluated: glm-5-3 (max)
    score: 68.96
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
    id: zhipu/glm-5-3#deepswe_v1_1#aaac79fdbd7e
    measured_by: benchmark_author
    effort: max
    harness: unregistered
    sources:
    - source_id: model-160-deepswe-v1-1
      snapshot_ref: sha256:33c505b573a474e601643fe1e1295b91b10e3ef62dfeab167a3851226358c972
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: terminal_bench_v4_0
    model_id_as_evaluated: GLM-5.3
    score: 41.82
    unit: percent
    source_url: https://www.tbench.ai/leaderboard/terminal-bench/4.0
    source_kind: benchmark_author
    evidence_date: '2026-08-14'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: Terminal-Bench 4.0
    configuration: 'tbench.ai leaderboard row read 2026-09-24: agent Claude Code (Anthropic),
      reasoning effort max, 330 trials, accuracy 41.82 ± 3.23 (95% CI). The board''s row date
      is the evidence date. Highest-effort row for the model, best agent on a tie.'
    limitations: The agent harness differs between rows; compare rows with the same agent.
    id: zhipu/glm-5-3#terminal_bench_v4_0#0721891a6173
    measured_by: benchmark_author
    effort: max
    harness: unregistered
    sources:
    - source_id: model-143-evidence-terminal-bench-4-0-json
      snapshot_ref: sha256:ea8d2644137b35340e437581fd626baeb200138b503f17f66f91fdf8eaf7f701
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: arena_sc_english
    model_id_as_evaluated: glm-5.3-max
    score: 1498.27
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / english, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1498.27 [1489.06,
      1507.48], 4481 votes, rank 9. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:cee57baa7239c5aa2091dcb5db0b4c2ac22cec732b235d66c0cda2ee55bdcb44
      cited_regions:
      - rows
    id: zhipu/glm-5-3#arena_sc_english#4de3cf3ce978
  - benchmark_id: arena_sc_chinese
    model_id_as_evaluated: glm-5.3-max
    score: 1524.9
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / chinese, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1524.90 [1502.43,
      1547.37], 750 votes, rank 23. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:9bf00fc37e8a997735f423949aba6ffc5551990b6f835297d3fed2b364abe02b
      cited_regions:
      - rows
    id: zhipu/glm-5-3#arena_sc_chinese#d1c1d415559d
  - benchmark_id: arena_sc_japanese
    model_id_as_evaluated: glm-5.3-max
    score: 1443.46
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / japanese, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1443.46 [1401.71,
      1485.21], 209 votes, rank 35. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:13b68c219a1ec549a9336846ddacaf97471f6323c09e4f45a73eab7a0857a9ca
      cited_regions:
      - rows
    id: zhipu/glm-5-3#arena_sc_japanese#716d62e5e843
  - benchmark_id: arena_sc_korean
    model_id_as_evaluated: glm-5.3-max
    score: 1484.83
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / korean, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1484.83 [1442.21,
      1527.46], 183 votes, rank 4. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:96706e685de18541b6ad515db22607a7840bad8bc902a30a8a38f949cd409c08
      cited_regions:
      - rows
    id: zhipu/glm-5-3#arena_sc_korean#0f7c906cb8a3
  - benchmark_id: arena_sc_russian
    model_id_as_evaluated: glm-5.3-max
    score: 1475.38
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / russian, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1475.38 [1458.64,
      1492.12], 1295 votes, rank 34. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:eb77af068077fa90a9514ad454b6a65f061a176f0d68897132e1526f3be743dd
      cited_regions:
      - rows
    id: zhipu/glm-5-3#arena_sc_russian#9be251957a35
  - benchmark_id: arena_sc_spanish
    model_id_as_evaluated: glm-5.3-max
    score: 1445.46
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / spanish, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1445.46 [1412.78,
      1478.15], 295 votes, rank 65. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:e56e27431afb859f3376e3d5609785906e24647b4c0c65a324b7995944b9573b
      cited_regions:
      - rows
    id: zhipu/glm-5-3#arena_sc_spanish#2b244499d7c5
  - benchmark_id: arena_sc_german
    model_id_as_evaluated: glm-5.3-max
    score: 1543.7
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / german, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1543.70 [1497.36,
      1590.04], 155 votes, rank 1. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:098d6730e0b426da68eee86ddfd97bb03c3b1048e178378de1ec3924fa209c6d
      cited_regions:
      - rows
    id: zhipu/glm-5-3#arena_sc_german#66cd7d08ad77
  - benchmark_id: arena_sc_french
    model_id_as_evaluated: glm-5.3-max
    score: 1518.87
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / french, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1518.87 [1486.21,
      1551.52], 339 votes, rank 4. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:c6c9f83eb7147bedac479a445a3803aad09d613643414d3cd5035dbde46d6f2f
      cited_regions:
      - rows
    id: zhipu/glm-5-3#arena_sc_french#bf89d008a896
  - benchmark_id: arena_sc_polish
    model_id_as_evaluated: glm-5.3-max
    score: 1481.04
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / polish, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1481.04 [1435.77,
      1526.31], 158 votes, rank 24. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:a99daf2dc2fbf9b06de90a127cc1408c7a19e4fa45a1a4d538b668211c4b5892
      cited_regions:
      - rows
    id: zhipu/glm-5-3#arena_sc_polish#933029e43ebb
  - benchmark_id: arena_sc_industry_software_it_services
    model_id_as_evaluated: glm-5.3-max
    score: 1518.07
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / industry_software_and_it_services, latest split, revision
      1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1518.07 [1508.51,
      1527.63], 4225 votes, rank 16. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:4eaa9890dce0719aa263af890c9f2a7bb1a3198e291d84dbf8c1371d4f150c52
      cited_regions:
      - rows
    id: zhipu/glm-5-3#arena_sc_industry_software_it_services#7f2ec04aafc7
  - benchmark_id: arena_sc_industry_entertainment_sports_media
    model_id_as_evaluated: glm-5.3-max
    score: 1455.46
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / industry_entertainment_and_sports_and_media, latest
      split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1455.46 [1443.69,
      1467.22], 2923 votes, rank 22. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:df0d5e7c4d4ce1f683618242c0786eafd164d98b3b49dbaa6e699476bec94ccf
      cited_regions:
      - rows
    id: zhipu/glm-5-3#arena_sc_industry_entertainment_sports_media#993151909653
  - benchmark_id: arena_sc_industry_mathematical
    model_id_as_evaluated: glm-5.3-max
    score: 1511.83
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / industry_mathematical, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1511.83 [1487.65,
      1536.00], 583 votes, rank 9. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:b0f3ee924239a7a9a1e60676935d0c83091f29517b8acb95e07868e370822e82
      cited_regions:
      - rows
    id: zhipu/glm-5-3#arena_sc_industry_mathematical#9f4360f342b3
  - benchmark_id: arena_sc_factuality
    model_id_as_evaluated: glm-5.3-max
    score: 1469.8
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_factuality / overall, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1469.80 [1464.24,
      1475.35], 10813 votes, rank 26. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-factuality
      snapshot_ref: sha256:ece0fd0afe2b42a38bce698a6be5329044b5503f5edb7f43473c19394b38fc28
      cited_regions:
      - rows
    id: zhipu/glm-5-3#arena_sc_factuality#2ccee3c90558
  benchmark_source: ''
  benchmark_as_of: ''
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
    ollama: true
    ollama_tag: glm-5.3
    lm_studio: false
    vllm: true
    trt_llm: false
    mlx: false
    llama_cpp: false
    sglang: true
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
  huggingface_downloads: 552019
  huggingface_likes: 1796
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
  models_dev_url: https://models.dev
  provider_docs_url: https://docs.z.ai/guides/llm/glm-5.3
  huggingface_url: https://huggingface.co/zai-org/GLM-5.3
  arxiv_url: https://arxiv.org/abs/2602.15763
  paper_url: ''
  github_url: https://github.com/zai-org/GLM-5
  ollama_url: https://ollama.com/library/glm-5.3
  artificial_analysis_url: ''
  arena_url: ''
  last_scraped_models_dev: '2026-09-10'
  last_scraped_huggingface: '2026-09-10'
  last_scraped_benchmarks: ''
  last_scraped_pricing: '2026-09-10'
facts:
- facet: model.class
  value: text-generator
  state: known
  sources:
  - source_id: model-143-zhipu-glm-5-3
    snapshot_ref: sha256:ed1c0a4563c437a32f8953d637a1db9bd831de1b24bd3062a5ace9e04340b1cf
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
  - source_id: model-143-zhipu-glm-5-3
    snapshot_ref: sha256:ed1c0a4563c437a32f8953d637a1db9bd831de1b24bd3062a5ace9e04340b1cf
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
  - source_id: model-143-zhipu-glm-5-3
    snapshot_ref: sha256:ed1c0a4563c437a32f8953d637a1db9bd831de1b24bd3062a5ace9e04340b1cf
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
  value: 1048576
  state: known
  sources:
  - source_id: model-143-zhipu-glm-5-3
    snapshot_ref: sha256:ed1c0a4563c437a32f8953d637a1db9bd831de1b24bd3062a5ace9e04340b1cf
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
  - source_id: model-143-zhipu-glm-5-3
    snapshot_ref: sha256:ed1c0a4563c437a32f8953d637a1db9bd831de1b24bd3062a5ace9e04340b1cf
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
  - source_id: model-143-zhipu-glm-5-3
    snapshot_ref: sha256:ed1c0a4563c437a32f8953d637a1db9bd831de1b24bd3062a5ace9e04340b1cf
    cited_regions:
    - model-spec
  - source_id: model-143-hf-metadata-zhipu-glm-5-3
    snapshot_ref: sha256:b198e08d17f97f7c5b01363713fa4548d106cb326069ee235b90e5bd6369fa5b
    cited_regions:
    - audit
  - source_id: model-143-glm-5-3-license
    snapshot_ref: sha256:96e1622099fc9d6b70c9760f007d99e66d7497eec636b63c60fe208401e9170c
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
  value: permitted_with_conditions
  state: known
  sources:
  - source_id: model-143-zhipu-glm-5-3
    snapshot_ref: sha256:ed1c0a4563c437a32f8953d637a1db9bd831de1b24bd3062a5ace9e04340b1cf
    cited_regions:
    - model-spec
  - source_id: model-143-glm-5-3-license
    snapshot_ref: sha256:96e1622099fc9d6b70c9760f007d99e66d7497eec636b63c60fe208401e9170c
    cited_regions:
    - audit
- facet: licence.user_cap
  value: unbounded
  state: known
  sources:
  - source_id: model-143-zhipu-glm-5-3
    snapshot_ref: sha256:ed1c0a4563c437a32f8953d637a1db9bd831de1b24bd3062a5ace9e04340b1cf
    cited_regions:
    - model-spec
  - source_id: model-143-glm-5-3-license
    snapshot_ref: sha256:96e1622099fc9d6b70c9760f007d99e66d7497eec636b63c60fe208401e9170c
    cited_regions:
    - audit
- facet: licence.output_training
  value: permitted
  state: known
  sources:
  - source_id: model-143-zhipu-glm-5-3
    snapshot_ref: sha256:ed1c0a4563c437a32f8953d637a1db9bd831de1b24bd3062a5ace9e04340b1cf
    cited_regions:
    - model-spec
  - source_id: model-143-glm-5-3-license
    snapshot_ref: sha256:96e1622099fc9d6b70c9760f007d99e66d7497eec636b63c60fe208401e9170c
    cited_regions:
    - audit
- facet: licence.fine_tuning
  value: permitted_with_conditions
  state: known
  sources:
  - source_id: model-143-zhipu-glm-5-3
    snapshot_ref: sha256:ed1c0a4563c437a32f8953d637a1db9bd831de1b24bd3062a5ace9e04340b1cf
    cited_regions:
    - model-spec
  - source_id: model-143-glm-5-3-license
    snapshot_ref: sha256:96e1622099fc9d6b70c9760f007d99e66d7497eec636b63c60fe208401e9170c
    cited_regions:
    - audit
- facet: origin.lab_jurisdiction
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-zhipu-glm-5-3
    snapshot_ref: sha256:ed1c0a4563c437a32f8953d637a1db9bd831de1b24bd3062a5ace9e04340b1cf
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
  - source_id: model-143-glm-5-3-license
    snapshot_ref: sha256:96e1622099fc9d6b70c9760f007d99e66d7497eec636b63c60fe208401e9170c
    cited_regions:
    - audit
  - source_id: model-143-hf-metadata-zhipu-glm-5-3
    snapshot_ref: sha256:b198e08d17f97f7c5b01363713fa4548d106cb326069ee235b90e5bd6369fa5b
    cited_regions:
    - audit
  checked_sources:
  - model-143-zhipu-glm-5-3
  - model-143-zai-glm-5-2-guide
  - model-143-zai-glm-5-3-guide
  - model-143-glm-5-3-license
  - model-143-hf-metadata-zhipu-glm-5-3
- facet: origin.base_lineage
  value:
  - CN
  state: known
  sources:
  - source_id: model-143-zhipu-glm-5-3
    snapshot_ref: sha256:ed1c0a4563c437a32f8953d637a1db9bd831de1b24bd3062a5ace9e04340b1cf
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
  - source_id: model-143-glm-5-3-license
    snapshot_ref: sha256:96e1622099fc9d6b70c9760f007d99e66d7497eec636b63c60fe208401e9170c
    cited_regions:
    - audit
- facet: origin.weights_hosting
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-zhipu-glm-5-3
    snapshot_ref: sha256:ed1c0a4563c437a32f8953d637a1db9bd831de1b24bd3062a5ace9e04340b1cf
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
  - source_id: model-143-glm-5-3-license
    snapshot_ref: sha256:96e1622099fc9d6b70c9760f007d99e66d7497eec636b63c60fe208401e9170c
    cited_regions:
    - audit
  - source_id: model-143-hf-metadata-zhipu-glm-5-3
    snapshot_ref: sha256:b198e08d17f97f7c5b01363713fa4548d106cb326069ee235b90e5bd6369fa5b
    cited_regions:
    - audit
  checked_sources:
  - model-143-zhipu-glm-5-3
  - model-143-zai-glm-5-2-guide
  - model-143-zai-glm-5-3-guide
  - model-143-glm-5-3-license
  - model-143-hf-metadata-zhipu-glm-5-3
- facet: model.release_date
  value: '2026-08-14'
  state: known
  sources:
  - source_id: model-143-zhipu-glm-5-3
    snapshot_ref: sha256:ed1c0a4563c437a32f8953d637a1db9bd831de1b24bd3062a5ace9e04340b1cf
    cited_regions:
    - model-spec
  - source_id: model-143-hf-metadata-zhipu-glm-5-3
    snapshot_ref: sha256:b198e08d17f97f7c5b01363713fa4548d106cb326069ee235b90e5bd6369fa5b
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
  - source_id: model-143-zhipu-glm-5-3
    snapshot_ref: sha256:ed1c0a4563c437a32f8953d637a1db9bd831de1b24bd3062a5ace9e04340b1cf
    cited_regions:
    - model-spec
  - source_id: model-143-hf-metadata-zhipu-glm-5-3
    snapshot_ref: sha256:b198e08d17f97f7c5b01363713fa4548d106cb326069ee235b90e5bd6369fa5b
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
  - source_id: model-143-zhipu-glm-5-3
    snapshot_ref: sha256:ed1c0a4563c437a32f8953d637a1db9bd831de1b24bd3062a5ace9e04340b1cf
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
  - source_id: model-143-zhipu-glm-5-3
    snapshot_ref: sha256:ed1c0a4563c437a32f8953d637a1db9bd831de1b24bd3062a5ace9e04340b1cf
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
  - source_id: model-143-zhipu-glm-5-3
    snapshot_ref: sha256:ed1c0a4563c437a32f8953d637a1db9bd831de1b24bd3062a5ace9e04340b1cf
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
  - source_id: model-143-zhipu-glm-5-3
    snapshot_ref: sha256:ed1c0a4563c437a32f8953d637a1db9bd831de1b24bd3062a5ace9e04340b1cf
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
  - source_id: model-143-glm-5-3-license
    snapshot_ref: sha256:96e1622099fc9d6b70c9760f007d99e66d7497eec636b63c60fe208401e9170c
    cited_regions:
    - audit
  - source_id: model-143-hf-metadata-zhipu-glm-5-3
    snapshot_ref: sha256:b198e08d17f97f7c5b01363713fa4548d106cb326069ee235b90e5bd6369fa5b
    cited_regions:
    - audit
  checked_sources:
  - model-143-zhipu-glm-5-3
  - model-143-zai-glm-5-2-guide
  - model-143-zai-glm-5-3-guide
  - model-143-glm-5-3-license
  - model-143-hf-metadata-zhipu-glm-5-3
- facet: feature.streaming
  value: true
  state: known
  sources:
  - source_id: model-143-zhipu-glm-5-3
    snapshot_ref: sha256:ed1c0a4563c437a32f8953d637a1db9bd831de1b24bd3062a5ace9e04340b1cf
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
- id: zhipu/glm-5-3#model.fits_hardware
  subject:
    kind: model
    id: zhipu/glm-5-3
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
      model_snapshot_ref: sha256:ac0063709e3c1557cb20ab655246af5b46c3e8166f4bd803f46331fd82651a27
      hardware_registry_sha256: sha256:10baf5e1ce9e5a1e5b970f4fdc25d9f67db8c562c8c109157ae9722bf6357bff
      hardware_device_count: 64
  sources:
  - source_id: model-174-zhipu-glm-5-3-hardware-input
    snapshot_ref: sha256:ac0063709e3c1557cb20ab655246af5b46c3e8166f4bd803f46331fd82651a27
    cited_regions:
    - rows
- id: zhipu/glm-5-3#model.parameters_total
  subject:
    kind: model
    id: zhipu/glm-5-3
  facet: model.parameters_total
  value: 753329940480
  state: known
  sources:
  - source_id: model-174-zhipu-glm-5-3-hardware-input
    snapshot_ref: sha256:ac0063709e3c1557cb20ab655246af5b46c3e8166f4bd803f46331fd82651a27
    cited_regions:
    - rows
- id: zhipu/glm-5-3#model.hardware_fit_indeterminate
  subject:
    kind: model
    id: zhipu/glm-5-3
  facet: model.hardware_fit_indeterminate
  value:
  - cerebras_wse3
  - nvidia_vera_rubin_superchip
  state: known
  sources:
  - source_id: model-174-zhipu-glm-5-3-hardware-input
    snapshot_ref: sha256:ac0063709e3c1557cb20ab655246af5b46c3e8166f4bd803f46331fd82651a27
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
      model_snapshot_ref: sha256:ac0063709e3c1557cb20ab655246af5b46c3e8166f4bd803f46331fd82651a27
      hardware_registry_sha256: sha256:10baf5e1ce9e5a1e5b970f4fdc25d9f67db8c562c8c109157ae9722bf6357bff
      hardware_device_count: 64
card_schema_version: '3.0'
card_author: modelspec
card_created: '2026-09-10'
card_updated: '2026-09-28'
---

# GLM-5.3

Z.ai (Zhipu) flagship open-weight MoE. The [provider blog](https://z.ai/blog/glm-5.3) (2026-08-14) and [docs](https://docs.z.ai/guides/llm/glm-5.3) state it uses the same base as GLM-5.2, with gains from post-training; text-only; 1M-token context; 128K max output; reasoning always on (`reasoning_effort`: low / high / max, default max). Weights: [zai-org/GLM-5.3](https://huggingface.co/zai-org/GLM-5.3) (Hub safetensors total 753,329,940,480). Licence is the custom GLM-5.3 licence, not MIT. Dated AA Index v4.2/v4.3 eligibility scores (reasoning_effort=max) and 2026-09-10 live-board standings are attached as verified evidence.
