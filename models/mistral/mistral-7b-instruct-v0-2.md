---
model_id: mistral/mistral-7b-instruct-v0-2
display_name: Mistral 7B Instruct v0.2
provider: mistral
provider_display: Mistral AI
family: mistral
version: ''
release_date: '2023-12-11'
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
  total_parameters: 7241732096
  active_parameters: null
  num_experts: null
  experts_per_token: null
  num_layers: 32
  hidden_size: 4096
  intermediate_size: 14336
  attention_type: null
  num_attention_heads: 32
  num_kv_heads: 8
  positional_encoding: null
  rope_theta: null
  vocab_size: 32000
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
  license_url: https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2/raw/main/README.md
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
  origin_org_type: private
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
  input: 0.1
  output: 0.1
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
    model_id: mistralai/Mistral-7B-Instruct-v0.2
    url: https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2
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
    mmlu_college_biology: 69.4
    mmlu_high_school_computer_science: 65.0
    mmlu_high_school_physics: 35.8
    mmlu_international_law: 81.0
    mmlu_jurisprudence: 74.1
  evidence:
  - benchmark_id: mmlu_college_biology
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 69.44
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-college_biology (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_high_school_computer_science
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 65.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-high_school_computer_science (5-shot, acc),
      x100.
    limitations: ''
  - benchmark_id: mmlu_high_school_physics
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 35.76
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-high_school_physics (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_international_law
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 80.99
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-international_law (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_jurisprudence
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 74.07
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-jurisprudence (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: arena_elo_style_control
    model_id_as_evaluated: mistral-7b-instruct-v0.2
    score: 1149.12
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / overall, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category overall,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1149.12 [1142.47, 1155.76], 19402
      votes, rank 364.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_coding
    model_id_as_evaluated: mistral-7b-instruct-v0.2
    score: 1185.96
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / coding, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category coding,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1185.96 [1174.24, 1197.68], 3114
      votes, rank 358.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_hard_prompts
    model_id_as_evaluated: mistral-7b-instruct-v0.2
    score: 1156.26
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / hard_prompts, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category hard_prompts,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1156.26 [1146.55, 1165.96], 5150
      votes, rank 362.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_math
    model_id_as_evaluated: mistral-7b-instruct-v0.2
    score: 1127.0
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / math, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category math, leaderboard_publish_date
      2026-09-13; style control. Highest-effort row for the product (effort: default; MODEL-123
      max-effort rule). Rating 1127.00 [1114.76, 1139.24], 2605 votes, rank 344.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_creative_writing
    model_id_as_evaluated: mistral-7b-instruct-v0.2
    score: 1103.59
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / creative_writing, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category creative_writing,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1103.59 [1091.02, 1116.17], 2952
      votes, rank 366.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_instruction_following
    model_id_as_evaluated: mistral-7b-instruct-v0.2
    score: 1123.18
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / instruction_following, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category instruction_following,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1123.18 [1114.13, 1132.22], 6659
      votes, rank 365.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_multi_turn
    model_id_as_evaluated: mistral-7b-instruct-v0.2
    score: 1113.44
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / multi_turn, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category multi_turn,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1113.44 [1100.25, 1126.63], 2566
      votes, rank 360.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_expert
    model_id_as_evaluated: mistral-7b-instruct-v0.2
    score: 1140.2
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / expert, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category expert,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1140.20 [1119.52, 1160.89], 798 votes,
      rank 340.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_longer_query
    model_id_as_evaluated: mistral-7b-instruct-v0.2
    score: 1135.22
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / longer_query, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category longer_query,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1135.22 [1119.87, 1150.57], 1592
      votes, rank 361.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_non_english
    model_id_as_evaluated: mistral-7b-instruct-v0.2
    score: 1076.92
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / non_english, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category non_english,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1076.92 [1067.69, 1086.14], 6679
      votes, rank 372.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_medicine
    model_id_as_evaluated: mistral-7b-instruct-v0.2
    score: 1175.69
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
      (effort: default; MODEL-123 max-effort rule). Rating 1175.69 [1156.98, 1194.41], 1091
      votes, rank 340.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_legal
    model_id_as_evaluated: mistral-7b-instruct-v0.2
    score: 1183.99
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / industry_legal_and_government, latest split, revision
      1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category industry_legal_and_government,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: default; MODEL-123 max-effort rule). Rating 1183.99 [1163.48, 1204.49], 976 votes,
      rank 346.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_business
    model_id_as_evaluated: mistral-7b-instruct-v0.2
    score: 1129.31
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
      (effort: default; MODEL-123 max-effort rule). Rating 1129.31 [1113.66, 1144.96], 1743
      votes, rank 360.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_science
    model_id_as_evaluated: mistral-7b-instruct-v0.2
    score: 1171.03
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
      (effort: default; MODEL-123 max-effort rule). Rating 1171.03 [1158.45, 1183.62], 3284
      votes, rank 359.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_writing
    model_id_as_evaluated: mistral-7b-instruct-v0.2
    score: 1113.01
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
      (effort: default; MODEL-123 max-effort rule). Rating 1113.01 [1102.42, 1123.61], 4703
      votes, rank 369.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arc_challenge
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 63.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#arc_challenge#237fd057e3ce
  - benchmark_id: bbh
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 44.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/mistralai/Mistral-7B-Instruct-v0.2/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-17'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-8e4c95a5dc99
      snapshot_ref: sha256:83ed4f2b0344b3d8c680e29779a464a1f01a406e1ad3ad5aef1037ca6f907aa8
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#bbh#6320165072cc
  - benchmark_id: gpqa_pooled
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 27.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/mistralai/Mistral-7B-Instruct-v0.2/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-17'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-8e4c95a5dc99
      snapshot_ref: sha256:83ed4f2b0344b3d8c680e29779a464a1f01a406e1ad3ad5aef1037ca6f907aa8
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#gpqa_pooled#f303387b937a
  - benchmark_id: gsm8k
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 40.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#gsm8k#2fdb9f080c10
  - benchmark_id: hellaswag
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 84.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#hellaswag#f085740e569a
  - benchmark_id: ifeval
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 55.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/mistralai/Mistral-7B-Instruct-v0.2/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-17'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-8e4c95a5dc99
      snapshot_ref: sha256:83ed4f2b0344b3d8c680e29779a464a1f01a406e1ad3ad5aef1037ca6f907aa8
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#ifeval#d4ac11957c60
  - benchmark_id: math_lvl5
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 3.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/mistralai/Mistral-7B-Instruct-v0.2/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-17'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-8e4c95a5dc99
      snapshot_ref: sha256:83ed4f2b0344b3d8c680e29779a464a1f01a406e1ad3ad5aef1037ca6f907aa8
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#math_lvl5#8c52e28858d8
  - benchmark_id: mmlu_abstract_algebra
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 32.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_abstract_algebra#362090393328
  - benchmark_id: mmlu_anatomy
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 57.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_anatomy#a96c5746cdc2
  - benchmark_id: mmlu_astronomy
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 62.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_astronomy#50423ebe0ebc
  - benchmark_id: mmlu_business_ethics
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 60.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_business_ethics#9813eb049230
  - benchmark_id: mmlu_clinical_knowledge
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 67.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_clinical_knowledge#216ee3d39b5a
  - benchmark_id: mmlu_college_chemistry
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 40.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_college_chemistry#2fd8f0240bea
  - benchmark_id: mmlu_college_computer_science
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 53.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_college_computer_science#47869c7a66eb
  - benchmark_id: mmlu_college_mathematics
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 39.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_college_mathematics#afefe36f2111
  - benchmark_id: mmlu_college_medicine
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 59.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_college_medicine#f493dbee518c
  - benchmark_id: mmlu_college_physics
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 42.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_college_physics#431c4ad9f2cb
  - benchmark_id: mmlu_computer_security
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 69.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_computer_security#f7e5b3bbcbf0
  - benchmark_id: mmlu_conceptual_physics
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 53.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_conceptual_physics#4e0b515fb031
  - benchmark_id: mmlu_econometrics
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 40.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_econometrics#673fcb4def2c
  - benchmark_id: mmlu_electrical_engineering
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 61.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_electrical_engineering#ac66c3042adf
  - benchmark_id: mmlu_elementary_mathematics
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 36.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_elementary_mathematics#4434cd8b4e83
  - benchmark_id: mmlu_formal_logic
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 42.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_formal_logic#392e1108442e
  - benchmark_id: mmlu_global_facts
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 35.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_global_facts#57d455dd473d
  - benchmark_id: mmlu_high_school_biology
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 63.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_high_school_biology#f7379638d34a
  - benchmark_id: mmlu_high_school_chemistry
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 51.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_high_school_chemistry#e82b1c9b8aa3
  - benchmark_id: mmlu_high_school_european_history
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 73.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_high_school_european_history#03085d988c2f
  - benchmark_id: mmlu_high_school_geography
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 76.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_high_school_geography#3a6452e81c48
  - benchmark_id: mmlu_high_school_government_and_politics
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 85.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_high_school_government_and_politics#d981c2b4b798
  - benchmark_id: mmlu_high_school_macroeconomics
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 55.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_high_school_macroeconomics#b7a9f2f05106
  - benchmark_id: mmlu_high_school_mathematics
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 30.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_high_school_mathematics#bb113a801cc4
  - benchmark_id: mmlu_high_school_microeconomics
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 65.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_high_school_microeconomics#653099eb033b
  - benchmark_id: mmlu_high_school_psychology
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 79.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_high_school_psychology#db553cf062bd
  - benchmark_id: mmlu_high_school_statistics
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 44.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_high_school_statistics#c8c541705a7e
  - benchmark_id: mmlu_high_school_us_history
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 76.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_high_school_us_history#6e6f9cfb1a37
  - benchmark_id: mmlu_high_school_world_history
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 75.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_high_school_world_history#b718531b5879
  - benchmark_id: mmlu_human_aging
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 61.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_human_aging#1f59ac9dbfa4
  - benchmark_id: mmlu_human_sexuality
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 74.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_human_sexuality#247726d26799
  - benchmark_id: mmlu_logical_fallacies
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 73.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_logical_fallacies#99ca77c90012
  - benchmark_id: mmlu_machine_learning
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 44.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_machine_learning#cdf075ba0c52
  - benchmark_id: mmlu_management
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 75.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_management#ab2f8225a844
  - benchmark_id: mmlu_marketing
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 86.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_marketing#e873ecae948a
  - benchmark_id: mmlu_medical_genetics
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 67.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_medical_genetics#0a57d6d954ce
  - benchmark_id: mmlu_miscellaneous
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 78.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_miscellaneous#112527cdba83
  - benchmark_id: mmlu_moral_disputes
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 69.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_moral_disputes#0c541836e897
  - benchmark_id: mmlu_moral_scenarios
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 31.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_moral_scenarios#283fe52e5be4
  - benchmark_id: mmlu_nutrition
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 68.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_nutrition#cae65e8c81e9
  - benchmark_id: mmlu_philosophy
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 70.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_philosophy#f33f2aefea49
  - benchmark_id: mmlu_prehistory
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 70.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_prehistory#a4041ee2dae1
  - benchmark_id: mmlu_pro
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 27.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/mistralai/Mistral-7B-Instruct-v0.2/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-17'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-8e4c95a5dc99
      snapshot_ref: sha256:83ed4f2b0344b3d8c680e29779a464a1f01a406e1ad3ad5aef1037ca6f907aa8
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_pro#93fe4c85fbff
  - benchmark_id: mmlu_professional_accounting
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 45.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_professional_accounting#cbf6fec70de5
  - benchmark_id: mmlu_professional_law
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 43.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_professional_law#6afce5fd65be
  - benchmark_id: mmlu_professional_medicine
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 61.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_professional_medicine#47cb70a2c466
  - benchmark_id: mmlu_professional_psychology
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 63.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_professional_psychology#aef2830a7efc
  - benchmark_id: mmlu_public_relations
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 70.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_public_relations#bd919d1f5de2
  - benchmark_id: mmlu_security_studies
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 70.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_security_studies#bd414f7f1c80
  - benchmark_id: mmlu_sociology
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 73.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_sociology#650c3ae3706a
  - benchmark_id: mmlu_us_foreign_policy
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 81.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_us_foreign_policy#4694f023d0c8
  - benchmark_id: mmlu_virology
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 49.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_virology#124624cf8f89
  - benchmark_id: mmlu_world_religions
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 83.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#mmlu_world_religions#94e8cf68c793
  - benchmark_id: musr
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 39.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/mistralai/Mistral-7B-Instruct-v0.2/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-17'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-8e4c95a5dc99
      snapshot_ref: sha256:83ed4f2b0344b3d8c680e29779a464a1f01a406e1ad3ad5aef1037ca6f907aa8
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#musr#03197219ea6c
  - benchmark_id: truthfulqa
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 68.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#truthfulqa#c7e9c07f9345
  - benchmark_id: winogrande
    model_id_as_evaluated: mistralai/Mistral-7B-Instruct-v0.2
    score: 77.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-12'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-9f07e96ec376
      snapshot_ref: sha256:80350aaef1506f297e3b7272435335dfdcc2f176735377486623e9ee5d5688df
      cited_regions:
      - rows
    id: mistral/mistral-7b-instruct-v0-2#winogrande#1575baa11c34
  benchmark_source: open-llm-leaderboard-v1, open-llm-leaderboard-v2
  benchmark_as_of: 2024-07
  benchmark_notes: 'MODEL-116, 2026-09-24: the Open LLM Leaderboard v2 "MATH Lvl 5 Raw" and "GPQA Raw" values for
    mistralai/Mistral-7B-Instruct-v0.2 moved from math_500 and gpqa_diamond to math_lvl5 and gpqa_pooled.'
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
  huggingface_downloads: 2473564
  huggingface_likes: 3104
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
  huggingface_url: https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2
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
card_updated: '2026-09-23'
---


# Mistral 7B Instruct v0.2

Auto-generated from HuggingFace Hub metadata for [mistralai/Mistral-7B-Instruct-v0.2](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2).

Licence: apache-2.0. Creator distribution https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2/raw/main/README.md (apache-2.0) and Hub cardData.license apache-2.0, read 2026-09-18.
