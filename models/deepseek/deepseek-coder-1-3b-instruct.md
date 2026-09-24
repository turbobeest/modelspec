---
model_id: deepseek/deepseek-coder-1-3b-instruct
display_name: deepseek coder 1.3B instruct
provider: deepseek
provider_display: DeepSeek
family: deepseek
version: ''
release_date: '2023-10-29'
last_updated: ''
status: active
model_type: llm-code
model_subtypes: []
tags:
- text-generation
pipeline_tag: text-generation
architecture:
  type: null
  total_parameters: 1346471936
  active_parameters: null
  num_experts: null
  experts_per_token: null
  num_layers: 24
  hidden_size: 2048
  intermediate_size: 5504
  attention_type: null
  num_attention_heads: 16
  num_kv_heads: 16
  positional_encoding: null
  rope_theta: null
  vocab_size: 32256
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
  license_type: deepseek
  license_url: https://huggingface.co/deepseek-ai/deepseek-coder-1.3b-instruct/raw/main/LICENSE
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
    context_window: 16384
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
    overall: null
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
    model_id: deepseek-ai/deepseek-coder-1.3b-instruct
    url: https://huggingface.co/deepseek-ai/deepseek-coder-1.3b-instruct
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
    arc_challenge: 28.6
    gsm8k: 1.1
    hellaswag: 39.9
    truthfulqa: 44.0
    winogrande: 52.4
    mmlu_abstract_algebra: 28.0
    mmlu_anatomy: 29.6
    mmlu_astronomy: 19.7
    mmlu_business_ethics: 29.0
    mmlu_clinical_knowledge: 30.2
    mmlu_college_biology: 25.7
    mmlu_college_chemistry: 25.0
    mmlu_college_computer_science: 29.0
    mmlu_college_mathematics: 23.0
    mmlu_college_medicine: 24.3
    mmlu_college_physics: 25.5
    mmlu_computer_security: 37.0
    mmlu_conceptual_physics: 31.1
    mmlu_econometrics: 24.6
    mmlu_electrical_engineering: 38.6
    mmlu_elementary_mathematics: 25.9
    mmlu_formal_logic: 21.4
    mmlu_global_facts: 27.0
    mmlu_high_school_biology: 28.1
    mmlu_high_school_chemistry: 27.6
    mmlu_high_school_computer_science: 33.0
    mmlu_high_school_european_history: 29.1
    mmlu_high_school_geography: 35.9
    mmlu_high_school_government_and_politics: 32.6
    mmlu_high_school_macroeconomics: 26.9
    mmlu_high_school_mathematics: 24.4
    mmlu_high_school_microeconomics: 26.1
    mmlu_high_school_physics: 30.5
    mmlu_high_school_psychology: 31.7
    mmlu_high_school_statistics: 25.5
    mmlu_high_school_us_history: 25.5
    mmlu_high_school_world_history: 30.8
    mmlu_human_aging: 14.8
    mmlu_human_sexuality: 35.1
    mmlu_international_law: 28.9
    mmlu_jurisprudence: 25.0
    mmlu_logical_fallacies: 28.8
    mmlu_machine_learning: 32.1
    mmlu_management: 37.9
    mmlu_marketing: 33.3
    mmlu_medical_genetics: 21.0
    mmlu_miscellaneous: 29.2
    mmlu_moral_disputes: 28.0
    mmlu_moral_scenarios: 27.3
    mmlu_nutrition: 30.4
    mmlu_philosophy: 29.3
    mmlu_prehistory: 28.7
    mmlu_professional_accounting: 24.5
    mmlu_professional_law: 29.0
    mmlu_professional_medicine: 41.5
    mmlu_professional_psychology: 24.2
    mmlu_public_relations: 33.6
    mmlu_security_studies: 25.3
    mmlu_sociology: 33.8
    mmlu_us_foreign_policy: 32.0
    mmlu_virology: 25.3
    mmlu_world_religions: 21.6
  evidence:
  - benchmark_id: arc_challenge
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 28.58
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task arc:challenge (25-shot, acc_norm), x100.
    limitations: ''
  - benchmark_id: gsm8k
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 1.06
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task gsm8k (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: hellaswag
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 39.87
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hellaswag (10-shot, acc_norm), x100.
    limitations: ''
  - benchmark_id: mmlu_abstract_algebra
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 28.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-abstract_algebra (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_anatomy
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 29.63
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-anatomy (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_astronomy
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 19.74
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-astronomy (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_business_ethics
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 29.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-business_ethics (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_clinical_knowledge
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 30.19
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-clinical_knowledge (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_college_biology
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 25.69
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-college_biology (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_college_chemistry
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 25.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-college_chemistry (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_college_computer_science
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 29.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-college_computer_science (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_college_mathematics
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 23.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-college_mathematics (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_college_medicine
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 24.28
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-college_medicine (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_college_physics
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 25.49
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-college_physics (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_computer_security
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 37.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-computer_security (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_conceptual_physics
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 31.06
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-conceptual_physics (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_econometrics
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 24.56
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-econometrics (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_electrical_engineering
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 38.62
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-electrical_engineering (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_elementary_mathematics
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 25.93
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-elementary_mathematics (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_formal_logic
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 21.43
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-formal_logic (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_global_facts
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 27.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-global_facts (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_high_school_biology
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 28.06
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-high_school_biology (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_high_school_chemistry
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 27.59
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-high_school_chemistry (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_high_school_computer_science
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 33.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-high_school_computer_science (5-shot, acc),
      x100.
    limitations: ''
  - benchmark_id: mmlu_high_school_european_history
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 29.09
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-high_school_european_history (5-shot, acc),
      x100.
    limitations: ''
  - benchmark_id: mmlu_high_school_geography
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 35.86
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-high_school_geography (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_high_school_government_and_politics
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 32.64
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-high_school_government_and_politics (5-shot,
      acc), x100.
    limitations: ''
  - benchmark_id: mmlu_high_school_macroeconomics
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 26.92
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-high_school_macroeconomics (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_high_school_mathematics
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 24.44
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-high_school_mathematics (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_high_school_microeconomics
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 26.05
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-high_school_microeconomics (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_high_school_physics
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 30.46
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-high_school_physics (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_high_school_psychology
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 31.74
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-high_school_psychology (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_high_school_statistics
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 25.46
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-high_school_statistics (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_high_school_us_history
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 25.49
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-high_school_us_history (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_high_school_world_history
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 30.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-high_school_world_history (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_human_aging
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 14.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-human_aging (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_human_sexuality
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 35.11
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-human_sexuality (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_international_law
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 28.93
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-international_law (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_jurisprudence
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 25.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-jurisprudence (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_logical_fallacies
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 28.83
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-logical_fallacies (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_machine_learning
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 32.14
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-machine_learning (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_management
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 37.86
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-management (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_marketing
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 33.33
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-marketing (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_medical_genetics
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 21.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-medical_genetics (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_miscellaneous
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 29.25
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-miscellaneous (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_moral_disputes
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 28.03
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-moral_disputes (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_moral_scenarios
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 27.26
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-moral_scenarios (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_nutrition
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 30.39
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-nutrition (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_philosophy
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 29.26
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-philosophy (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_prehistory
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 28.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-prehistory (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_professional_accounting
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 24.47
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-professional_accounting (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_professional_law
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 29.01
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-professional_law (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_professional_medicine
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 41.54
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-professional_medicine (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_professional_psychology
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 24.18
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-professional_psychology (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_public_relations
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 33.64
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-public_relations (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_security_studies
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 25.31
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-security_studies (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_sociology
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 33.83
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-sociology (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_us_foreign_policy
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 32.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-us_foreign_policy (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_virology
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 25.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-virology (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_world_religions
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 21.64
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-world_religions (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: truthfulqa
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 44.02
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task truthfulqa:mc (0-shot, mc2), x100.
    limitations: ''
  - benchmark_id: winogrande
    model_id_as_evaluated: deepseek-ai/deepseek-coder-1.3b-instruct
    score: 52.41
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/deepseek-ai/deepseek-coder-1.3b-instruct/results_2023-12-04T15-02-34.832979.json
    source_kind: independent_evaluator
    evidence_date: '2023-12-04'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task winogrande (5-shot, acc), x100.
    limitations: ''
  benchmark_source: open-llm-leaderboard-v1
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
  huggingface_downloads: 82045
  huggingface_likes: 159
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
  huggingface_url: https://huggingface.co/deepseek-ai/deepseek-coder-1.3b-instruct
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

# deepseek coder 1.3B instruct

Auto-generated from HuggingFace Hub metadata for [deepseek-ai/deepseek-coder-1.3b-instruct](https://huggingface.co/deepseek-ai/deepseek-coder-1.3b-instruct).

Licence: deepseek. Creator LICENSE file https://huggingface.co/deepseek-ai/deepseek-coder-1.3b-instruct/raw/main/LICENSE (DeepSeek License Agreement) and Hub cardData.license other and license_name deepseek, read 2026-09-18.
