---
model_id: deepseek/deepseek-v4-pro
display_name: DeepSeek V4 Pro
provider: deepseek
provider_display: DeepSeek
family: deepseek-thinking
version: deepseek-v4-pro
release_date: '2026-08-12'
last_updated: '2026-08-22'
status: active
model_type: llm-reasoning
model_subtypes: []
tags: []
pipeline_tag: ''
architecture:
  type: null
  total_parameters: 1598839674782
  active_parameters: 49000000000
  num_experts: 384
  experts_per_token: 6
  num_layers: 61
  hidden_size: 7168
  intermediate_size: null
  attention_type: null
  num_attention_heads: 128
  num_kv_heads: 1
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
  origin_country: CN
  origin_org_type: null
modalities:
  input:
  - text
  output:
  - text
  text:
    max_input_tokens: null
    max_output_tokens: 384000
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
  input: 0.435
  output: 0.87
  reasoning: null
  cache_read: 0.003625
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
    model_id: deepseek-ai/DeepSeek-V4-Pro
    url: https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro
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
  - benchmark_id: gpqa_diamond
    model_id_as_evaluated: DeepSeek-V4-Pro (max)
    score: 90.1
    unit: percent
    source_url: https://arxiv.org/abs/2606.19348
    source_kind: provider_self_report
    evidence_date: '2026-04-26'
    date_type: published
    verified_at: '2026-09-09'
    benchmark_version: GPQA Diamond (Pass@1)
    configuration: Maximum reasoning-effort mode; temperature 1.0. SWE-Verified was
      run in DeepSeek's internal bash + file-edit harness (500-step cap, 512K context),
      not a third-party agent scaffold. LiveCodeBench is reported as v6 on this page
      and was not attached to live_code_bench.
    limitations: ''
    measured_by: provider_self_report
  - benchmark_id: mmlu_pro
    model_id_as_evaluated: DeepSeek-V4-Pro (max)
    score: 87.5
    unit: percent
    source_url: https://arxiv.org/abs/2606.19348
    source_kind: provider_self_report
    evidence_date: '2026-04-26'
    date_type: published
    verified_at: '2026-09-09'
    benchmark_version: MMLU-Pro (EM)
    configuration: Maximum reasoning-effort mode; temperature 1.0. SWE-Verified was
      run in DeepSeek's internal bash + file-edit harness (500-step cap, 512K context),
      not a third-party agent scaffold. LiveCodeBench is reported as v6 on this page
      and was not attached to live_code_bench.
    limitations: ''
    id: deepseek/deepseek-v4-pro#mmlu_pro#ae826abe812d
    measured_by: provider_self_report
    effort: max
    harness: null
    sources:
    - source_id: model-191-deepseek-v4-pro-paper
      snapshot_ref: sha256:1b80985eddbf33a5f1002d045354b2cace7160186c7d3c05e6e7edb3c0778115
      cited_regions:
      - evidence
  - benchmark_id: swe_bench_verified
    model_id_as_evaluated: DeepSeek-V4-Pro (max)
    score: 80.6
    unit: percent
    source_url: https://arxiv.org/abs/2606.19348
    source_kind: provider_self_report
    evidence_date: '2026-04-26'
    date_type: published
    verified_at: '2026-09-09'
    benchmark_version: SWE-bench Verified (Resolved)
    configuration: Maximum reasoning-effort mode; temperature 1.0. SWE-Verified was
      run in DeepSeek's internal bash + file-edit harness (500-step cap, 512K context),
      not a third-party agent scaffold. LiveCodeBench is reported as v6 on this page
      and was not attached to live_code_bench.
    limitations: ''
    measured_by: provider_self_report
  - benchmark_id: arena_elo_style_control
    model_id_as_evaluated: deepseek-v4-pro
    score: 1457.34
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / overall, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category overall,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1457.34 [1453.34, 1461.34], 54130
      votes, rank 57.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: deepseek/deepseek-v4-pro#arena_elo_style_control#ac8b24532794
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
    model_id_as_evaluated: deepseek-v4-pro
    score: 1501.5
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / coding, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category coding,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1501.50 [1495.44, 1507.56], 16143
      votes, rank 65.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: deepseek/deepseek-v4-pro#arena_sc_coding#7bb6a22dd938
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
    model_id_as_evaluated: deepseek-v4-pro
    score: 1479.8
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / hard_prompts, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category hard_prompts,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1479.80 [1475.12, 1484.48], 36039
      votes, rank 56.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: deepseek/deepseek-v4-pro#arena_sc_hard_prompts#1721a1bb9d73
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
    model_id_as_evaluated: deepseek-v4-pro
    score: 1444.63
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / math, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category math, leaderboard_publish_date
      2026-09-13; style control. Highest-effort row for the product (effort: default; MODEL-123
      max-effort rule). Rating 1444.63 [1433.13, 1456.14], 2868 votes, rank 70.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: deepseek/deepseek-v4-pro#arena_sc_math#dac2caeac8b4
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
    model_id_as_evaluated: deepseek-v4-pro
    score: 1443.95
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / creative_writing, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category creative_writing,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1443.95 [1436.47, 1451.44], 8998
      votes, rank 48.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: deepseek/deepseek-v4-pro#arena_sc_creative_writing#30e657b83531
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
    model_id_as_evaluated: deepseek-v4-pro
    score: 1452.55
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / instruction_following, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category instruction_following,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1452.55 [1446.83, 1458.27], 18649
      votes, rank 54.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: deepseek/deepseek-v4-pro#arena_sc_instruction_following#e747acf81c15
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
    model_id_as_evaluated: deepseek-v4-pro
    score: 1475.19
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / multi_turn, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category multi_turn,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1475.19 [1468.01, 1482.38], 9800
      votes, rank 45.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: deepseek/deepseek-v4-pro#arena_sc_multi_turn#cbebd3a79af9
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
    model_id_as_evaluated: deepseek-v4-pro
    score: 1481.35
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / expert, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category expert,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1481.35 [1472.57, 1490.12], 5440
      votes, rank 61.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: deepseek/deepseek-v4-pro#arena_sc_expert#a0b0b1c4a88e
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
    model_id_as_evaluated: deepseek-v4-pro
    score: 1471.54
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / longer_query, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category longer_query,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1471.54 [1466.05, 1477.03], 23898
      votes, rank 52.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: deepseek/deepseek-v4-pro#arena_sc_longer_query#bffd2050cd41
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
    model_id_as_evaluated: deepseek-v4-pro
    score: 1444.72
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / non_english, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category non_english,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1444.72 [1439.90, 1449.54], 30240
      votes, rank 58.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: deepseek/deepseek-v4-pro#arena_sc_non_english#2c74e3a5d154
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
    model_id_as_evaluated: deepseek-v4-pro
    score: 1476.7
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
      (effort: default; MODEL-123 max-effort rule). Rating 1476.70 [1466.20, 1487.21], 3766
      votes, rank 57.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: deepseek/deepseek-v4-pro#arena_sc_medicine#cc8bcc37ece4
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
    model_id_as_evaluated: deepseek-v4-pro
    score: 1473.18
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
      (effort: default; MODEL-123 max-effort rule). Rating 1473.18 [1463.34, 1483.01], 4229
      votes, rank 47.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: deepseek/deepseek-v4-pro#arena_sc_legal#5e2494fe4a5e
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
    model_id_as_evaluated: deepseek-v4-pro
    score: 1460.69
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
      (effort: default; MODEL-123 max-effort rule). Rating 1460.69 [1453.80, 1467.58], 10721
      votes, rank 51.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: deepseek/deepseek-v4-pro#arena_sc_business#5c7b704a0a15
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
    model_id_as_evaluated: deepseek-v4-pro
    score: 1480.7
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
      (effort: default; MODEL-123 max-effort rule). Rating 1480.70 [1473.37, 1488.02], 8597
      votes, rank 50.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: deepseek/deepseek-v4-pro#arena_sc_science#b885a31fd483
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
    model_id_as_evaluated: deepseek-v4-pro
    score: 1450.89
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
      (effort: default; MODEL-123 max-effort rule). Rating 1450.89 [1444.40, 1457.37], 13127
      votes, rank 47.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: deepseek/deepseek-v4-pro#arena_sc_writing#6e7ee8f3ed7a
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
    model_id_as_evaluated: deepseek-v4-pro
    score: 1445.47
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-23'
    date_type: published
    verified_at: '2026-09-29'
    benchmark_version: webdev / overall, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset webdev, category overall, leaderboard_publish_date
      2026-09-23; no style-controlled variant. Highest-effort row for the product (effort: default;
      MODEL-123 max-effort rule). Rating 1445.47 [1438.97, 1451.96], 13179 votes, rank 62.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: deepseek/deepseek-v4-pro#arena_webdev#a813b293dcd0
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
    model_id_as_evaluated: deepseek-v4-pro_max
    score: 89.65
    unit: percent
    source_url: https://epoch.ai/benchmarks/gpqa-diamond
    source_kind: independent_evaluator
    evidence_date: '2026-06-16'
    date_type: evaluated
    verified_at: '2026-09-29'
    benchmark_version: GPQA Diamond (Epoch AI run)
    configuration: Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (gpqa_diamond.csv),
      read 2026-09-24. Run started 2026-06-16T20:16:55.000Z; effort max; highest-effort run
      for the model (MODEL-123 max-effort rule), newest on a tie. Standard error 1.75 points.
    limitations: Epoch AI data, CC BY 4.0.
    id: deepseek/deepseek-v4-pro#gpqa_diamond#d19463c1378a
    measured_by: independent_evaluator
    effort: max
    harness: null
    sources:
    - source_id: model-143-evidence-epoch-gpqa-diamond-csv
      snapshot_ref: sha256:2170dd89d5d68d21790626cdefaa361e5f7e9d7f2c543b74c46f75886451e3af
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: frontiermath_tiers_1_3_v2
    model_id_as_evaluated: deepseek-v4-pro_max
    score: 45.26
    unit: percent
    source_url: https://epoch.ai/frontiermath
    source_kind: independent_evaluator
    evidence_date: '2026-06-17'
    date_type: evaluated
    verified_at: '2026-09-29'
    benchmark_version: FrontierMath-Tiers-1-3-v2-Private (Epoch AI run)
    configuration: Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (frontiermath_tiers_1_3_v2.csv),
      read 2026-09-24. Run started 2026-06-17T02:30:14.000Z; effort max; highest-effort run
      for the model (MODEL-123 max-effort rule), newest on a tie. Standard error 2.95 points.
    limitations: Epoch AI data, CC BY 4.0.
    id: deepseek/deepseek-v4-pro#frontiermath_tiers_1_3_v2#dd93eea5663f
    measured_by: independent_evaluator
    effort: max
    harness: null
    sources:
    - source_id: model-143-evidence-epoch-frontiermath-tiers-1-3-v2-csv
      snapshot_ref: sha256:290afed31fc291e207d29c71b15aea9b6ad5e6bd50795136d1a6781e259aabcd
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: simpleqa_verified
    model_id_as_evaluated: deepseek-v4-pro_max
    score: 46.99
    unit: percent
    source_url: https://epoch.ai/benchmarks/simpleqa-verified
    source_kind: independent_evaluator
    evidence_date: '2026-08-27'
    date_type: evaluated
    verified_at: '2026-09-29'
    benchmark_version: SimpleQA Verified, proportion correct, Epoch AI protocol with anti-abstention
      prompt
    configuration: Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (simpleqa_verified.csv),
      read 2026-09-24. Run started 2026-08-27T19:30:29.000Z; effort max; highest-effort run
      for the model (MODEL-123 max-effort rule), newest on a tie. Standard error 1.58 points.
    limitations: Epoch AI data, CC BY 4.0.
    id: deepseek/deepseek-v4-pro#simpleqa_verified#49345e002b7f
    measured_by: independent_evaluator
    effort: max
    harness: null
    sources:
    - source_id: model-160-epoch-simpleqa-verified-csv
      snapshot_ref: sha256:563eeb084e21ec07a8843924df2451b3e802138eac826f0956d19c4bf37fa4fb
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: swe_bench_verified
    model_id_as_evaluated: deepseek-v4-pro_max
    score: 77.64
    unit: percent
    source_url: https://epoch.ai/benchmarks/swe-bench-verified
    source_kind: independent_evaluator
    evidence_date: '2026-06-18'
    date_type: evaluated
    verified_at: '2026-09-29'
    benchmark_version: SWE-bench Verified (Epoch AI run)
    configuration: Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (swe_bench_verified.csv),
      read 2026-09-24. Run started 2026-06-18T17:43:54.039Z; effort max; highest-effort run
      for the model (MODEL-123 max-effort rule), newest on a tie. Standard error 1.90 points.
    limitations: Epoch AI data, CC BY 4.0.
    id: deepseek/deepseek-v4-pro#swe_bench_verified#653a9e640833
    measured_by: independent_evaluator
    effort: max
    harness: null
    sources:
    - source_id: model-160-epoch-swe-bench-verified-csv
      snapshot_ref: sha256:bb5c01fbbf380f785f217de1bbda9a0a0716044a1add83c6dcc64cbe50931ac3
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: frontiercode_v1_1
    model_id_as_evaluated: DeepSeek V4 Pro
    score: 17.6
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
    id: deepseek/deepseek-v4-pro#frontiercode_v1_1#889510703080
    measured_by: benchmark_author
    effort: null
    harness: unregistered
    sources:
    - source_id: model-160-frontiercode
      snapshot_ref: sha256:946a90057bea730dbfa5a27ab38168e01b5269492c1b41f46cf4ec29dd0d3cf3
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: vending_bench_2
    model_id_as_evaluated: Deepseek V4 Pro
    score: 3284.52
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
    id: deepseek/deepseek-v4-pro#vending_bench_2#494cf422cb5e
    measured_by: benchmark_author
    effort: null
    harness: null
    sources:
    - source_id: model-160-vending-bench-2
      snapshot_ref: sha256:94074584ec83e973b31884f48956a6bc43e36a33d47dc3feaa7c52adf23a9c12
      cited_regions:
      - rows
    observed_at: '2026-09-29'
  - benchmark_id: aime_2026
    model_id_as_evaluated: DeepSeek-v4-Pro (Max)
    score: 96.67
    unit: percent
    source_url: https://matharena.ai/competition_tables/aime--aime_2026
    source_kind: independent_evaluator
    evidence_date: '2026-09-29'
    date_type: evaluated
    verified_at: '2026-09-29'
    benchmark_version: AIME 2026, MathArena final-answer table
    configuration: MathArena competition table read 2026-09-26; the table states no run
      date, so the reading is dated by the observation. Effort max; highest-effort row
      for the model. MathArena lists final-answer competitions as deprecated.
    limitations: 'MathArena marks this row: model was released after competition release, so
      contamination is possible.'
    id: deepseek/deepseek-v4-pro#aime_2026#4ac540f4e251
    measured_by: independent_evaluator
    effort: max
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
  - benchmark_id: arena_sc_english
    model_id_as_evaluated: deepseek-v4-pro
    score: 1466.79
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / english, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1466.79 [1461.57,
      1472.01], 23890 votes, rank 57. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:cee57baa7239c5aa2091dcb5db0b4c2ac22cec732b235d66c0cda2ee55bdcb44
      cited_regions:
      - rows
    id: deepseek/deepseek-v4-pro#arena_sc_english#dbcc2cd8efd9
  - benchmark_id: arena_sc_chinese
    model_id_as_evaluated: deepseek-v4-pro
    score: 1493.3
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / chinese, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1493.30 [1481.45,
      1505.14], 2859 votes, rank 67. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:9bf00fc37e8a997735f423949aba6ffc5551990b6f835297d3fed2b364abe02b
      cited_regions:
      - rows
    id: deepseek/deepseek-v4-pro#arena_sc_chinese#0d83a1bcfc4b
  - benchmark_id: arena_sc_japanese
    model_id_as_evaluated: deepseek-v4-pro
    score: 1462.21
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / japanese, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1462.21 [1437.94,
      1486.48], 691 votes, rank 22. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:13b68c219a1ec549a9336846ddacaf97471f6323c09e4f45a73eab7a0857a9ca
      cited_regions:
      - rows
    id: deepseek/deepseek-v4-pro#arena_sc_japanese#79705f0e7843
  - benchmark_id: arena_sc_korean
    model_id_as_evaluated: deepseek-v4-pro
    score: 1418.01
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / korean, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1418.01 [1398.63,
      1437.38], 1069 votes, rank 49. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:96706e685de18541b6ad515db22607a7840bad8bc902a30a8a38f949cd409c08
      cited_regions:
      - rows
    id: deepseek/deepseek-v4-pro#arena_sc_korean#718f818d82a0
  - benchmark_id: arena_sc_russian
    model_id_as_evaluated: deepseek-v4-pro
    score: 1457.01
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / russian, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1457.01 [1448.43,
      1465.60], 5695 votes, rank 56. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:eb77af068077fa90a9514ad454b6a65f061a176f0d68897132e1526f3be743dd
      cited_regions:
      - rows
    id: deepseek/deepseek-v4-pro#arena_sc_russian#b9bb34d6dd9f
  - benchmark_id: arena_sc_spanish
    model_id_as_evaluated: deepseek-v4-pro
    score: 1454.23
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / spanish, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1454.23 [1438.59,
      1469.88], 1690 votes, rank 53. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:e56e27431afb859f3376e3d5609785906e24647b4c0c65a324b7995944b9573b
      cited_regions:
      - rows
    id: deepseek/deepseek-v4-pro#arena_sc_spanish#43fbb5a4191f
  - benchmark_id: arena_sc_german
    model_id_as_evaluated: deepseek-v4-pro
    score: 1467.7
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / german, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1467.70 [1447.73,
      1487.68], 955 votes, rank 42. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:098d6730e0b426da68eee86ddfd97bb03c3b1048e178378de1ec3924fa209c6d
      cited_regions:
      - rows
    id: deepseek/deepseek-v4-pro#arena_sc_german#a71904394306
  - benchmark_id: arena_sc_french
    model_id_as_evaluated: deepseek-v4-pro
    score: 1484.3
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / french, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1484.30 [1469.29,
      1499.31], 2118 votes, rank 45. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:c6c9f83eb7147bedac479a445a3803aad09d613643414d3cd5035dbde46d6f2f
      cited_regions:
      - rows
    id: deepseek/deepseek-v4-pro#arena_sc_french#cdf321bfff92
  - benchmark_id: arena_sc_polish
    model_id_as_evaluated: deepseek-v4-pro
    score: 1467.43
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / polish, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1467.43 [1449.05,
      1485.82], 1084 votes, rank 41. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:a99daf2dc2fbf9b06de90a127cc1408c7a19e4fa45a1a4d538b668211c4b5892
      cited_regions:
      - rows
    id: deepseek/deepseek-v4-pro#arena_sc_polish#30a19ee53063
  - benchmark_id: arena_sc_industry_software_it_services
    model_id_as_evaluated: deepseek-v4-pro
    score: 1491.76
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / industry_software_and_it_services, latest split, revision
      1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1491.76 [1486.38,
      1497.14], 22255 votes, rank 59. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:4eaa9890dce0719aa263af890c9f2a7bb1a3198e291d84dbf8c1371d4f150c52
      cited_regions:
      - rows
    id: deepseek/deepseek-v4-pro#arena_sc_industry_software_it_services#bcc3ebdb7b45
  - benchmark_id: arena_sc_industry_entertainment_sports_media
    model_id_as_evaluated: deepseek-v4-pro
    score: 1433.68
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / industry_entertainment_and_sports_and_media, latest
      split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1433.68 [1426.88,
      1440.47], 11822 votes, rank 56. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:df0d5e7c4d4ce1f683618242c0786eafd164d98b3b49dbaa6e699476bec94ccf
      cited_regions:
      - rows
    id: deepseek/deepseek-v4-pro#arena_sc_industry_entertainment_sports_media#283ad52c7508
  - benchmark_id: arena_sc_industry_mathematical
    model_id_as_evaluated: deepseek-v4-pro
    score: 1460.32
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_style_control / industry_mathematical, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1460.32 [1448.83,
      1471.81], 2997 votes, rank 59. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:b0f3ee924239a7a9a1e60676935d0c83091f29517b8acb95e07868e370822e82
      cited_regions:
      - rows
    id: deepseek/deepseek-v4-pro#arena_sc_industry_mathematical#b926d6825a42
  - benchmark_id: arena_sc_factuality
    model_id_as_evaluated: deepseek-v4-pro
    score: 1454.79
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: text_factuality / overall, latest split, revision 1880dbebff5b
    configuration: Pinned LMArena dataset; publication date 2026-09-13; rating 1454.79 [1451.60,
      1457.97], 54066 votes, rank 50. Observed 2026-09-27.
    limitations: 'Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.'
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-factuality
      snapshot_ref: sha256:ece0fd0afe2b42a38bce698a6be5329044b5503f5edb7f43473c19394b38fc28
      cited_regions:
      - rows
    id: deepseek/deepseek-v4-pro#arena_sc_factuality#ef8c5406fdb9
  - benchmark_id: finance_benchmark_v2
    model_id_as_evaluated: deepseek/deepseek-v4-pro
    score: 89.0411
    unit: percent
    source_url: https://finbenchmark.ai/
    source_kind: independent_evaluator
    evidence_date: '2026-07-13'
    date_type: evaluated
    observed_at: '2026-09-29'
    verified_at: '2026-09-29'
    benchmark_version: Finance Benchmark v2, harness 0.2.0
    configuration: 73 v2 tasks; three attempts per task; temperature zero.
    limitations: Passes at least once, so this value does not measure repeated-run consistency.
    measured_by: independent_evaluator
    effort: null
    harness: unregistered
    sources:
    - source_id: model-192-finance-benchmark-v2
      snapshot_ref: sha256:9e10ecf98bc44ca664396e7a752fd46c9a08466f368aa35c8ff6456b0f1c4540
      cited_regions:
      - rows
    id: deepseek/deepseek-v4-pro#finance_benchmark_v2#88593fd013f7
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
  models_dev_url: https://models.dev/deepseek
  provider_docs_url: ''
  huggingface_url: ''
  arxiv_url: ''
  paper_url: ''
  github_url: ''
  ollama_url: ''
  artificial_analysis_url: ''
  arena_url: ''
  last_scraped_models_dev: ''
  last_scraped_huggingface: ''
  last_scraped_benchmarks: ''
  last_scraped_pricing: ''
facts:
- facet: model.class
  value: text-generator
  state: known
  sources:
  - source_id: model-143-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:c4d714818a4d3333542edc7d38ea065825a0cf7aa8fea3605bbd1d1c18e4a610
    cited_regions:
    - model-spec
  - source_id: model-143-deepseek-function-calling
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
  - source_id: model-143-deepseek-json-output
    snapshot_ref: sha256:f728a4dad99c2328c9c982b08c113f400abcc1a7eba238f08738f51a951d1b30
    cited_regions:
    - audit
  - source_id: model-143-deepseek-streaming
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
- facet: model.input_modalities
  value:
  - text
  state: known
  sources:
  - source_id: model-143-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:c4d714818a4d3333542edc7d38ea065825a0cf7aa8fea3605bbd1d1c18e4a610
    cited_regions:
    - model-spec
  - source_id: model-143-deepseek-function-calling
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
  - source_id: model-143-deepseek-json-output
    snapshot_ref: sha256:f728a4dad99c2328c9c982b08c113f400abcc1a7eba238f08738f51a951d1b30
    cited_regions:
    - audit
  - source_id: model-143-deepseek-streaming
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
- facet: model.output_modalities
  value:
  - text
  state: known
  sources:
  - source_id: model-143-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:c4d714818a4d3333542edc7d38ea065825a0cf7aa8fea3605bbd1d1c18e4a610
    cited_regions:
    - model-spec
  - source_id: model-143-deepseek-function-calling
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
  - source_id: model-143-deepseek-json-output
    snapshot_ref: sha256:f728a4dad99c2328c9c982b08c113f400abcc1a7eba238f08738f51a951d1b30
    cited_regions:
    - audit
  - source_id: model-143-deepseek-streaming
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
- facet: model.context_window
  value: 1000000
  state: known
  sources:
  - source_id: model-143-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:c4d714818a4d3333542edc7d38ea065825a0cf7aa8fea3605bbd1d1c18e4a610
    cited_regions:
    - model-spec
  - source_id: model-143-deepseek-function-calling
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
  - source_id: model-143-deepseek-json-output
    snapshot_ref: sha256:f728a4dad99c2328c9c982b08c113f400abcc1a7eba238f08738f51a951d1b30
    cited_regions:
    - audit
  - source_id: model-143-deepseek-streaming
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
- facet: model.max_output_tokens
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:c4d714818a4d3333542edc7d38ea065825a0cf7aa8fea3605bbd1d1c18e4a610
    cited_regions:
    - model-spec
  - source_id: model-143-deepseek-function-calling
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
  - source_id: model-143-deepseek-json-output
    snapshot_ref: sha256:f728a4dad99c2328c9c982b08c113f400abcc1a7eba238f08738f51a951d1b30
    cited_regions:
    - audit
  - source_id: model-143-deepseek-streaming
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
  - source_id: model-143-deepseek-v4-license
    snapshot_ref: sha256:f2c6c602815669d292889e5be8c802f2ed950653b77999b1584e8e6aed25d040
    cited_regions:
    - audit
  - source_id: model-143-hf-metadata-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:4d07285dd7292c42d15980fc6296f9956bf8a655529284a97be5b1b9eacea13f
    cited_regions:
    - audit
  checked_sources:
  - model-143-deepseek-deepseek-v4-pro
  - model-143-deepseek-function-calling
  - model-143-deepseek-json-output
  - model-143-deepseek-streaming
  - model-143-deepseek-v4-license
  - model-143-hf-metadata-deepseek-deepseek-v4-pro
- facet: model.weights_openness
  value: open_weights
  state: known
  sources:
  - source_id: model-143-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:c4d714818a4d3333542edc7d38ea065825a0cf7aa8fea3605bbd1d1c18e4a610
    cited_regions:
    - model-spec
  - source_id: model-143-hf-metadata-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:4d07285dd7292c42d15980fc6296f9956bf8a655529284a97be5b1b9eacea13f
    cited_regions:
    - audit
  - source_id: model-143-deepseek-v4-license
    snapshot_ref: sha256:f2c6c602815669d292889e5be8c802f2ed950653b77999b1584e8e6aed25d040
    cited_regions:
    - audit
  - source_id: model-143-deepseek-function-calling
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
  - source_id: model-143-deepseek-json-output
    snapshot_ref: sha256:f728a4dad99c2328c9c982b08c113f400abcc1a7eba238f08738f51a951d1b30
    cited_regions:
    - audit
  - source_id: model-143-deepseek-streaming
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
- facet: licence.commercial_use
  value: permitted
  state: known
  sources:
  - source_id: model-143-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:c4d714818a4d3333542edc7d38ea065825a0cf7aa8fea3605bbd1d1c18e4a610
    cited_regions:
    - model-spec
  - source_id: model-143-deepseek-v4-license
    snapshot_ref: sha256:f2c6c602815669d292889e5be8c802f2ed950653b77999b1584e8e6aed25d040
    cited_regions:
    - audit
- facet: licence.user_cap
  value: unbounded
  state: known
  sources:
  - source_id: model-143-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:c4d714818a4d3333542edc7d38ea065825a0cf7aa8fea3605bbd1d1c18e4a610
    cited_regions:
    - model-spec
  - source_id: model-143-deepseek-v4-license
    snapshot_ref: sha256:f2c6c602815669d292889e5be8c802f2ed950653b77999b1584e8e6aed25d040
    cited_regions:
    - audit
- facet: licence.output_training
  value: permitted
  state: known
  sources:
  - source_id: model-143-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:c4d714818a4d3333542edc7d38ea065825a0cf7aa8fea3605bbd1d1c18e4a610
    cited_regions:
    - model-spec
  - source_id: model-143-deepseek-v4-license
    snapshot_ref: sha256:f2c6c602815669d292889e5be8c802f2ed950653b77999b1584e8e6aed25d040
    cited_regions:
    - audit
- facet: licence.fine_tuning
  value: permitted
  state: known
  sources:
  - source_id: model-143-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:c4d714818a4d3333542edc7d38ea065825a0cf7aa8fea3605bbd1d1c18e4a610
    cited_regions:
    - model-spec
  - source_id: model-143-deepseek-v4-license
    snapshot_ref: sha256:f2c6c602815669d292889e5be8c802f2ed950653b77999b1584e8e6aed25d040
    cited_regions:
    - audit
- facet: origin.lab_jurisdiction
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:c4d714818a4d3333542edc7d38ea065825a0cf7aa8fea3605bbd1d1c18e4a610
    cited_regions:
    - model-spec
  - source_id: model-143-deepseek-function-calling
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
  - source_id: model-143-deepseek-json-output
    snapshot_ref: sha256:f728a4dad99c2328c9c982b08c113f400abcc1a7eba238f08738f51a951d1b30
    cited_regions:
    - audit
  - source_id: model-143-deepseek-streaming
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
  - source_id: model-143-deepseek-v4-license
    snapshot_ref: sha256:f2c6c602815669d292889e5be8c802f2ed950653b77999b1584e8e6aed25d040
    cited_regions:
    - audit
  - source_id: model-143-hf-metadata-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:4d07285dd7292c42d15980fc6296f9956bf8a655529284a97be5b1b9eacea13f
    cited_regions:
    - audit
  checked_sources:
  - model-143-deepseek-deepseek-v4-pro
  - model-143-deepseek-function-calling
  - model-143-deepseek-json-output
  - model-143-deepseek-streaming
  - model-143-deepseek-v4-license
  - model-143-hf-metadata-deepseek-deepseek-v4-pro
- facet: origin.base_lineage
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:c4d714818a4d3333542edc7d38ea065825a0cf7aa8fea3605bbd1d1c18e4a610
    cited_regions:
    - model-spec
  - source_id: model-143-deepseek-function-calling
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
  - source_id: model-143-deepseek-json-output
    snapshot_ref: sha256:f728a4dad99c2328c9c982b08c113f400abcc1a7eba238f08738f51a951d1b30
    cited_regions:
    - audit
  - source_id: model-143-deepseek-streaming
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
  - source_id: model-143-deepseek-v4-license
    snapshot_ref: sha256:f2c6c602815669d292889e5be8c802f2ed950653b77999b1584e8e6aed25d040
    cited_regions:
    - audit
  - source_id: model-143-hf-metadata-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:4d07285dd7292c42d15980fc6296f9956bf8a655529284a97be5b1b9eacea13f
    cited_regions:
    - audit
  checked_sources:
  - model-143-deepseek-deepseek-v4-pro
  - model-143-deepseek-function-calling
  - model-143-deepseek-json-output
  - model-143-deepseek-streaming
  - model-143-deepseek-v4-license
  - model-143-hf-metadata-deepseek-deepseek-v4-pro
- facet: origin.weights_hosting
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:c4d714818a4d3333542edc7d38ea065825a0cf7aa8fea3605bbd1d1c18e4a610
    cited_regions:
    - model-spec
  - source_id: model-143-deepseek-function-calling
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
  - source_id: model-143-deepseek-json-output
    snapshot_ref: sha256:f728a4dad99c2328c9c982b08c113f400abcc1a7eba238f08738f51a951d1b30
    cited_regions:
    - audit
  - source_id: model-143-deepseek-streaming
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
  - source_id: model-143-deepseek-v4-license
    snapshot_ref: sha256:f2c6c602815669d292889e5be8c802f2ed950653b77999b1584e8e6aed25d040
    cited_regions:
    - audit
  - source_id: model-143-hf-metadata-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:4d07285dd7292c42d15980fc6296f9956bf8a655529284a97be5b1b9eacea13f
    cited_regions:
    - audit
  checked_sources:
  - model-143-deepseek-deepseek-v4-pro
  - model-143-deepseek-function-calling
  - model-143-deepseek-json-output
  - model-143-deepseek-streaming
  - model-143-deepseek-v4-license
  - model-143-hf-metadata-deepseek-deepseek-v4-pro
- facet: model.release_date
  value: '2026-08-12'
  state: known
  sources:
  - source_id: model-143-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:c4d714818a4d3333542edc7d38ea065825a0cf7aa8fea3605bbd1d1c18e4a610
    cited_regions:
    - model-spec
  - source_id: model-143-hf-metadata-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:4d07285dd7292c42d15980fc6296f9956bf8a655529284a97be5b1b9eacea13f
    cited_regions:
    - audit
  - source_id: model-143-deepseek-function-calling
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
  - source_id: model-143-deepseek-json-output
    snapshot_ref: sha256:f728a4dad99c2328c9c982b08c113f400abcc1a7eba238f08738f51a951d1b30
    cited_regions:
    - audit
  - source_id: model-143-deepseek-streaming
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
- facet: model.lifecycle
  value: active
  state: known
  sources:
  - source_id: model-143-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:c4d714818a4d3333542edc7d38ea065825a0cf7aa8fea3605bbd1d1c18e4a610
    cited_regions:
    - model-spec
  - source_id: model-143-hf-metadata-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:4d07285dd7292c42d15980fc6296f9956bf8a655529284a97be5b1b9eacea13f
    cited_regions:
    - audit
  - source_id: model-143-deepseek-function-calling
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
  - source_id: model-143-deepseek-json-output
    snapshot_ref: sha256:f728a4dad99c2328c9c982b08c113f400abcc1a7eba238f08738f51a951d1b30
    cited_regions:
    - audit
  - source_id: model-143-deepseek-streaming
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
- facet: feature.tool_calling
  value: true
  state: known
  sources:
  - source_id: model-143-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:c4d714818a4d3333542edc7d38ea065825a0cf7aa8fea3605bbd1d1c18e4a610
    cited_regions:
    - model-spec
  - source_id: model-143-deepseek-function-calling
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
  - source_id: model-143-deepseek-json-output
    snapshot_ref: sha256:f728a4dad99c2328c9c982b08c113f400abcc1a7eba238f08738f51a951d1b30
    cited_regions:
    - audit
  - source_id: model-143-deepseek-streaming
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
- facet: feature.structured_output
  value: true
  state: known
  sources:
  - source_id: model-143-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:c4d714818a4d3333542edc7d38ea065825a0cf7aa8fea3605bbd1d1c18e4a610
    cited_regions:
    - model-spec
  - source_id: model-143-deepseek-function-calling
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
  - source_id: model-143-deepseek-json-output
    snapshot_ref: sha256:f728a4dad99c2328c9c982b08c113f400abcc1a7eba238f08738f51a951d1b30
    cited_regions:
    - audit
  - source_id: model-143-deepseek-streaming
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
- facet: feature.effort_controls
  value: true
  state: known
  sources:
  - source_id: model-143-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:c4d714818a4d3333542edc7d38ea065825a0cf7aa8fea3605bbd1d1c18e4a610
    cited_regions:
    - model-spec
  - source_id: model-143-deepseek-function-calling
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
  - source_id: model-143-deepseek-json-output
    snapshot_ref: sha256:f728a4dad99c2328c9c982b08c113f400abcc1a7eba238f08738f51a951d1b30
    cited_regions:
    - audit
  - source_id: model-143-deepseek-streaming
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
- facet: feature.batch
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:c4d714818a4d3333542edc7d38ea065825a0cf7aa8fea3605bbd1d1c18e4a610
    cited_regions:
    - model-spec
  - source_id: model-143-deepseek-function-calling
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
  - source_id: model-143-deepseek-json-output
    snapshot_ref: sha256:f728a4dad99c2328c9c982b08c113f400abcc1a7eba238f08738f51a951d1b30
    cited_regions:
    - audit
  - source_id: model-143-deepseek-streaming
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
  - source_id: model-143-deepseek-v4-license
    snapshot_ref: sha256:f2c6c602815669d292889e5be8c802f2ed950653b77999b1584e8e6aed25d040
    cited_regions:
    - audit
  - source_id: model-143-hf-metadata-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:4d07285dd7292c42d15980fc6296f9956bf8a655529284a97be5b1b9eacea13f
    cited_regions:
    - audit
  checked_sources:
  - model-143-deepseek-deepseek-v4-pro
  - model-143-deepseek-function-calling
  - model-143-deepseek-json-output
  - model-143-deepseek-streaming
  - model-143-deepseek-v4-license
  - model-143-hf-metadata-deepseek-deepseek-v4-pro
- facet: feature.streaming
  value: true
  state: known
  sources:
  - source_id: model-143-deepseek-deepseek-v4-pro
    snapshot_ref: sha256:c4d714818a4d3333542edc7d38ea065825a0cf7aa8fea3605bbd1d1c18e4a610
    cited_regions:
    - model-spec
  - source_id: model-143-deepseek-function-calling
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
  - source_id: model-143-deepseek-json-output
    snapshot_ref: sha256:f728a4dad99c2328c9c982b08c113f400abcc1a7eba238f08738f51a951d1b30
    cited_regions:
    - audit
  - source_id: model-143-deepseek-streaming
    snapshot_ref: sha256:7ce9db1b1cc7e2efafe7cbfd57b9d46d240c20399f7bd87672c7e3a5250ccdd0
    cited_regions:
    - audit
- id: deepseek/deepseek-v4-pro#model.fits_hardware
  subject:
    kind: model
    id: deepseek/deepseek-v4-pro
  facet: model.fits_hardware
  value: []
  state: known
  derivation:
    method: decision.hardware.compute_fit@1
    formula: parameters_total * bytes_per_parameter <= memory_capacity_gb * (1 - working_allowance) *
      1e9
    inputs:
      weights_openness: open_weights
      parameters_total: 1598839674782
      working_allowance: 0.25
      quant_bytes: '{''bf16'': 2.0, ''fp16'': 2.0, ''fp8'': 1.0, ''int4'': 0.5, ''int8'': 1.0, ''q4'':
        0.5, ''q5'': 0.625, ''q6'': 0.75}'
      has_device_unknowns: 'true'
      model_snapshot_ref: sha256:409b510e4f35de8dbc228bf56ca9ebd72dd3d154b014cd8c23cf9d70edbb6c6b
      hardware_registry_sha256: sha256:10baf5e1ce9e5a1e5b970f4fdc25d9f67db8c562c8c109157ae9722bf6357bff
      hardware_device_count: 64
  sources:
  - source_id: model-174-deepseek-deepseek-v4-pro-hardware-input
    snapshot_ref: sha256:409b510e4f35de8dbc228bf56ca9ebd72dd3d154b014cd8c23cf9d70edbb6c6b
    cited_regions:
    - rows
- id: deepseek/deepseek-v4-pro#model.parameters_total
  subject:
    kind: model
    id: deepseek/deepseek-v4-pro
  facet: model.parameters_total
  value: 1598839674782
  state: known
  sources:
  - source_id: model-174-deepseek-deepseek-v4-pro-hardware-input
    snapshot_ref: sha256:409b510e4f35de8dbc228bf56ca9ebd72dd3d154b014cd8c23cf9d70edbb6c6b
    cited_regions:
    - rows
- id: deepseek/deepseek-v4-pro#model.hardware_fit_indeterminate
  subject:
    kind: model
    id: deepseek/deepseek-v4-pro
  facet: model.hardware_fit_indeterminate
  value:
  - cerebras_wse3
  - nvidia_vera_rubin_superchip
  state: known
  sources:
  - source_id: model-174-deepseek-deepseek-v4-pro-hardware-input
    snapshot_ref: sha256:409b510e4f35de8dbc228bf56ca9ebd72dd3d154b014cd8c23cf9d70edbb6c6b
    cited_regions:
    - rows
  derivation:
    method: decision.hardware.compute_fit@1
    formula: parameters_total * bytes_per_parameter <= memory_capacity_gb * (1 - working_allowance) *
      1e9
    inputs:
      weights_openness: open_weights
      parameters_total: 1598839674782
      working_allowance: 0.25
      quant_bytes: '{''bf16'': 2.0, ''fp16'': 2.0, ''fp8'': 1.0, ''int4'': 0.5, ''int8'': 1.0, ''q4'':
        0.5, ''q5'': 0.625, ''q6'': 0.75}'
      has_device_unknowns: 'true'
      model_snapshot_ref: sha256:409b510e4f35de8dbc228bf56ca9ebd72dd3d154b014cd8c23cf9d70edbb6c6b
      hardware_registry_sha256: sha256:10baf5e1ce9e5a1e5b970f4fdc25d9f67db8c562c8c109157ae9722bf6357bff
      hardware_device_count: 64
card_schema_version: '3.0'
card_author: models.dev-seeder
card_created: '2026-04-05'
card_updated: '2026-09-28'
---

# DeepSeek V4 Pro

DeepSeek V4 Pro is a Llm Reasoning model from DeepSeek. Part of the deepseek-thinking family.

## Key Features
- Extended reasoning / chain-of-thought
- Function calling / tool use
- Structured output (JSON mode)
- Open weights
