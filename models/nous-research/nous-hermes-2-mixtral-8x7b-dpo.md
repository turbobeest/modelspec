---
model_id: nous-research/nous-hermes-2-mixtral-8x7b-dpo
display_name: Nous Hermes 2 Mixtral 8x7B DPO
provider: nous-research
provider_display: Nous Research
family: hermes
version: ''
release_date: '2024-01-11'
last_updated: ''
status: active
model_type: llm-chat
model_subtypes: []
tags:
- text-generation
- openai-compatible
pipeline_tag: text-generation
architecture:
  type: null
  total_parameters: 46702809088
  active_parameters: 12879675392
  num_experts: 8
  experts_per_token: 2
  num_layers: 32
  hidden_size: 4096
  intermediate_size: 14336
  attention_type: null
  num_attention_heads: 32
  num_kv_heads: 8
  positional_encoding: null
  rope_theta: null
  vocab_size: 32002
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
  base_model: mistralai/Mixtral-8x7B-v0.1
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
  license_url: https://huggingface.co/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/raw/main/README.md
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
  origin_country: FR
  origin_org_type: open-collective
modalities:
  input:
  - text
  output:
  - text
  text:
    max_input_tokens: null
    max_output_tokens: null
    context_window: 32768
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
  input: 0.24
  output: 0.24
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
    available: true
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
    available: true
    model_id: ''
    url: https://ollama.com/
    fine_tuning: false
    gated: false
    regions: []
    notes: ''
  lm_studio:
    available: true
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
    model_id: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    url: https://huggingface.co/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
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
    model_id_as_evaluated: nous-hermes-2-mixtral-8x7b-dpo
    score: 1164.16
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / overall, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category overall,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1164.16 [1152.26, 1176.06], 3777
      votes, rank 356.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_coding
    model_id_as_evaluated: nous-hermes-2-mixtral-8x7b-dpo
    score: 1175.77
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / coding, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category coding,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1175.77 [1152.31, 1199.22], 575 votes,
      rank 362.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_hard_prompts
    model_id_as_evaluated: nous-hermes-2-mixtral-8x7b-dpo
    score: 1129.28
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / hard_prompts, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category hard_prompts,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1129.28 [1111.69, 1146.88], 1066
      votes, rank 376.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_math
    model_id_as_evaluated: nous-hermes-2-mixtral-8x7b-dpo
    score: 1092.77
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / math, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category math, leaderboard_publish_date
      2026-09-13; style control. Highest-effort row for the product (effort: default; MODEL-123
      max-effort rule). Rating 1092.77 [1071.31, 1114.23], 628 votes, rank 360.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_creative_writing
    model_id_as_evaluated: nous-hermes-2-mixtral-8x7b-dpo
    score: 1134.32
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / creative_writing, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category creative_writing,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1134.32 [1111.03, 1157.61], 616 votes,
      rank 355.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_instruction_following
    model_id_as_evaluated: nous-hermes-2-mixtral-8x7b-dpo
    score: 1107.62
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / instruction_following, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category instruction_following,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1107.62 [1091.29, 1123.94], 1421
      votes, rank 372.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_multi_turn
    model_id_as_evaluated: nous-hermes-2-mixtral-8x7b-dpo
    score: 1128.52
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / multi_turn, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category multi_turn,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1128.52 [1102.57, 1154.46], 467 votes,
      rank 354.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_longer_query
    model_id_as_evaluated: nous-hermes-2-mixtral-8x7b-dpo
    score: 1116.32
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / longer_query, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category longer_query,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1116.32 [1081.32, 1151.33], 230 votes,
      rank 366.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_non_english
    model_id_as_evaluated: nous-hermes-2-mixtral-8x7b-dpo
    score: 1096.51
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / non_english, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category non_english,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1096.51 [1075.63, 1117.38], 744 votes,
      rank 362.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_medicine
    model_id_as_evaluated: nous-hermes-2-mixtral-8x7b-dpo
    score: 1149.08
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / industry_medicine_and_healthcare, latest split,
      revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category industry_medicine_and_healthcare,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1149.08 [1116.99, 1181.18], 266 votes,
      rank 349.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_business
    model_id_as_evaluated: nous-hermes-2-mixtral-8x7b-dpo
    score: 1150.84
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / industry_business_and_management_and_financial_operations,
      latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category industry_business_and_management_and_financial_operations,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1150.84 [1116.18, 1185.50], 282 votes,
      rank 349.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_science
    model_id_as_evaluated: nous-hermes-2-mixtral-8x7b-dpo
    score: 1186.68
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / industry_life_and_physical_and_social_science, latest
      split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category industry_life_and_physical_and_social_science,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1186.68 [1163.89, 1209.48], 651 votes,
      rank 350.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_writing
    model_id_as_evaluated: nous-hermes-2-mixtral-8x7b-dpo
    score: 1140.07
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / industry_writing_and_literature_and_language, latest
      split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category industry_writing_and_literature_and_language,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1140.07 [1120.13, 1160.02], 858 votes,
      rank 354.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arc_challenge
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 71.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#arc_challenge#95080fb2ca9d
  - benchmark_id: bbh
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 55.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2025-02-13T18-27-04.338360.json
    source_kind: benchmark_author
    evidence_date: '2024-07-30'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v2-881add5abb33
      snapshot_ref: sha256:405f7aa815da9b069d9ca1d6d83f8f8f6d5568de6929d3d2bc65a3c99bce7b50
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#bbh#9db2c64a00a3
  - benchmark_id: gpqa_pooled
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 32.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2025-02-13T18-27-04.338360.json
    source_kind: benchmark_author
    evidence_date: '2024-07-30'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v2-881add5abb33
      snapshot_ref: sha256:405f7aa815da9b069d9ca1d6d83f8f8f6d5568de6929d3d2bc65a3c99bce7b50
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#gpqa_pooled#727c8a19e08c
  - benchmark_id: gsm8k
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 71.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#gsm8k#89730c269126
  - benchmark_id: hellaswag
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 87.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#hellaswag#fb7f7a0d7527
  - benchmark_id: ifeval
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 59.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2025-02-13T18-27-04.338360.json
    source_kind: benchmark_author
    evidence_date: '2024-07-30'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v2-881add5abb33
      snapshot_ref: sha256:405f7aa815da9b069d9ca1d6d83f8f8f6d5568de6929d3d2bc65a3c99bce7b50
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#ifeval#e66365b67cb8
  - benchmark_id: math_lvl5
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 12.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2025-02-13T18-27-04.338360.json
    source_kind: benchmark_author
    evidence_date: '2024-07-30'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v2-881add5abb33
      snapshot_ref: sha256:405f7aa815da9b069d9ca1d6d83f8f8f6d5568de6929d3d2bc65a3c99bce7b50
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#math_lvl5#16440d6245ce
  - benchmark_id: mmlu_abstract_algebra
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 43.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_abstract_algebra#4d05fc90d6b5
  - benchmark_id: mmlu_anatomy
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 68.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_anatomy#0efa2ece7003
  - benchmark_id: mmlu_astronomy
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 80.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_astronomy#e32b881e08f3
  - benchmark_id: mmlu_business_ethics
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 73.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_business_ethics#676dbfdd2703
  - benchmark_id: mmlu_clinical_knowledge
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 79.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_clinical_knowledge#9ed696b56e83
  - benchmark_id: mmlu_college_biology
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 83.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_college_biology#6de4e4de274d
  - benchmark_id: mmlu_college_chemistry
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 55.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_college_chemistry#9075815aa1f2
  - benchmark_id: mmlu_college_computer_science
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 66.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_college_computer_science#38a57185cea8
  - benchmark_id: mmlu_college_mathematics
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 43.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_college_mathematics#d44ecb4ce061
  - benchmark_id: mmlu_college_medicine
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 69.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_college_medicine#93aa7f2dfe51
  - benchmark_id: mmlu_college_physics
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 49.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_college_physics#7b24d668111f
  - benchmark_id: mmlu_computer_security
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 81.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_computer_security#1cf6bf44c4a3
  - benchmark_id: mmlu_conceptual_physics
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 69.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_conceptual_physics#644cd99ef0d0
  - benchmark_id: mmlu_econometrics
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 64.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_econometrics#8c01ab05a1b3
  - benchmark_id: mmlu_electrical_engineering
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 69.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_electrical_engineering#e0d6dec96af2
  - benchmark_id: mmlu_elementary_mathematics
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 50.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_elementary_mathematics#400630925180
  - benchmark_id: mmlu_formal_logic
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 57.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_formal_logic#42a4b68d0fdb
  - benchmark_id: mmlu_global_facts
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 45.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_global_facts#973f07c749f2
  - benchmark_id: mmlu_high_school_biology
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 85.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_high_school_biology#05394e24cdc4
  - benchmark_id: mmlu_high_school_chemistry
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 59.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_high_school_chemistry#9cb82995d382
  - benchmark_id: mmlu_high_school_computer_science
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 75.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_high_school_computer_science#b2013c0d4586
  - benchmark_id: mmlu_high_school_european_history
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 78.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_high_school_european_history#f5f9b37a3abe
  - benchmark_id: mmlu_high_school_geography
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 85.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_high_school_geography#155de5d627fc
  - benchmark_id: mmlu_high_school_government_and_politics
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 93.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_high_school_government_and_politics#617a476bbc82
  - benchmark_id: mmlu_high_school_macroeconomics
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 69.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_high_school_macroeconomics#41a96c930c5c
  - benchmark_id: mmlu_high_school_mathematics
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 34.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_high_school_mathematics#59087d786547
  - benchmark_id: mmlu_high_school_microeconomics
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 79.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_high_school_microeconomics#57a215c2876c
  - benchmark_id: mmlu_high_school_physics
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 45.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_high_school_physics#909ef43ab3b4
  - benchmark_id: mmlu_high_school_psychology
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 89.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_high_school_psychology#8cfb226bc889
  - benchmark_id: mmlu_high_school_statistics
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 66.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_high_school_statistics#9b55deb915e7
  - benchmark_id: mmlu_high_school_us_history
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 86.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_high_school_us_history#dcce813fd62f
  - benchmark_id: mmlu_high_school_world_history
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 89.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_high_school_world_history#a6c457eb165c
  - benchmark_id: mmlu_human_aging
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 76.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_human_aging#417bf04b6482
  - benchmark_id: mmlu_human_sexuality
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 87.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_human_sexuality#1585fe7e7c64
  - benchmark_id: mmlu_international_law
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 86.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_international_law#d7b8d86a53d1
  - benchmark_id: mmlu_jurisprudence
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 84.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_jurisprudence#fc57855939e9
  - benchmark_id: mmlu_logical_fallacies
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 80.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_logical_fallacies#a15e586a91d8
  - benchmark_id: mmlu_machine_learning
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 54.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_machine_learning#43d1cd371cd2
  - benchmark_id: mmlu_management
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 85.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_management#c71ffa24cbf6
  - benchmark_id: mmlu_marketing
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 90.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_marketing#236fe5682e00
  - benchmark_id: mmlu_medical_genetics
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 80.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_medical_genetics#597676171b4e
  - benchmark_id: mmlu_miscellaneous
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 88.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_miscellaneous#0b19a0409396
  - benchmark_id: mmlu_moral_disputes
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 80.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_moral_disputes#3f7895cda623
  - benchmark_id: mmlu_moral_scenarios
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 57.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_moral_scenarios#71c92840cab2
  - benchmark_id: mmlu_nutrition
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 80.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_nutrition#592def5ec983
  - benchmark_id: mmlu_philosophy
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 79.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_philosophy#6fc9c8e339e7
  - benchmark_id: mmlu_prehistory
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 85.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_prehistory#4952d6e7d0c7
  - benchmark_id: mmlu_pro
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 36.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2025-02-13T18-27-04.338360.json
    source_kind: benchmark_author
    evidence_date: '2024-07-30'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v2-881add5abb33
      snapshot_ref: sha256:405f7aa815da9b069d9ca1d6d83f8f8f6d5568de6929d3d2bc65a3c99bce7b50
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_pro#06e1c55556b8
  - benchmark_id: mmlu_professional_accounting
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 52.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_professional_accounting#20bdcd6b8378
  - benchmark_id: mmlu_professional_law
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 55.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_professional_law#d93cdec92c70
  - benchmark_id: mmlu_professional_medicine
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 78.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_professional_medicine#40551a2e391f
  - benchmark_id: mmlu_professional_psychology
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 78.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_professional_psychology#31ce2cc18963
  - benchmark_id: mmlu_public_relations
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 69.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_public_relations#8a0032b91f1a
  - benchmark_id: mmlu_security_studies
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 81.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_security_studies#530aa24816e4
  - benchmark_id: mmlu_sociology
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 87.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_sociology#4ad4dd48e997
  - benchmark_id: mmlu_us_foreign_policy
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 91.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_us_foreign_policy#ed732b5a8198
  - benchmark_id: mmlu_virology
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 50.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_virology#081382006f98
  - benchmark_id: mmlu_world_religions
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 89.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#mmlu_world_religions#655b7051ebde
  - benchmark_id: musr
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 46.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2025-02-13T18-27-04.338360.json
    source_kind: benchmark_author
    evidence_date: '2024-07-30'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v2-881add5abb33
      snapshot_ref: sha256:405f7aa815da9b069d9ca1d6d83f8f8f6d5568de6929d3d2bc65a3c99bce7b50
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#musr#a7e728cc2ec8
  - benchmark_id: truthfulqa
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 54.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#truthfulqa#b16885dbf955
  - benchmark_id: winogrande
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
    score: 83.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json
    source_kind: benchmark_author
    evidence_date: '2024-01-22'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: benchmark_author
    sources:
    - source_id: oll-v1-e476ebcdb70d
      snapshot_ref: sha256:9c5e3e235c8138bc1b4bd649c82dd8a73aa9301b17ebcfdaa4ab12fdfed272c3
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-mixtral-8x7b-dpo#winogrande#bf058cf35a3b
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
  huggingface_downloads: 8992
  huggingface_likes: 452
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
  huggingface_url: https://huggingface.co/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO
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


# Nous Hermes 2 Mixtral 8x7B DPO

Auto-generated from HuggingFace Hub metadata for [NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO](https://huggingface.co/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO).

Licence: apache-2.0. Creator distribution https://huggingface.co/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/raw/main/README.md (apache-2.0) and Hub cardData.license apache-2.0, read 2026-09-18.
