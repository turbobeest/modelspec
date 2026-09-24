---
model_id: mistral/mistral-7b-v0-3
display_name: Mistral 7B v0.3
provider: mistral
provider_display: Mistral AI
family: mistral
version: ''
release_date: '2024-05-22'
last_updated: ''
status: active
model_type: llm-chat
model_subtypes: []
tags:
- openai-compatible
pipeline_tag: ''
architecture:
  type: null
  total_parameters: 7248023552
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
  vocab_size: 32768
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
  library_name: vllm
licensing:
  open_weights: true
  license_type: apache-2.0
  license_url: https://huggingface.co/mistralai/Mistral-7B-v0.3/raw/main/README.md
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
    model_id: mistralai/Mistral-7B-v0.3
    url: https://huggingface.co/mistralai/Mistral-7B-v0.3
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
    arc_challenge: 60.5
    gsm8k: 34.5
    hellaswag: 83.0
    truthfulqa: 41.8
    winogrande: 78.5
    mmlu_abstract_algebra: 30.0
    mmlu_anatomy: 60.7
    mmlu_astronomy: 65.1
    mmlu_business_ethics: 61.0
    mmlu_clinical_knowledge: 68.3
    mmlu_college_biology: 69.4
    mmlu_college_chemistry: 49.0
    mmlu_college_computer_science: 52.0
    mmlu_college_mathematics: 37.0
    mmlu_college_medicine: 63.0
    mmlu_college_physics: 31.4
    mmlu_computer_security: 73.0
    mmlu_conceptual_physics: 58.3
    mmlu_econometrics: 44.7
    mmlu_electrical_engineering: 55.9
    mmlu_elementary_mathematics: 40.2
    mmlu_formal_logic: 39.7
    mmlu_global_facts: 40.0
    mmlu_high_school_biology: 76.1
    mmlu_high_school_chemistry: 54.2
    mmlu_high_school_computer_science: 65.0
    mmlu_high_school_european_history: 76.4
    mmlu_high_school_geography: 77.3
    mmlu_high_school_government_and_politics: 87.6
    mmlu_high_school_macroeconomics: 60.5
    mmlu_high_school_mathematics: 35.9
    mmlu_high_school_microeconomics: 63.9
    mmlu_high_school_physics: 35.8
    mmlu_high_school_psychology: 80.0
    mmlu_high_school_statistics: 51.9
    mmlu_high_school_us_history: 81.4
    mmlu_high_school_world_history: 78.1
    mmlu_human_aging: 70.0
    mmlu_human_sexuality: 77.1
    mmlu_international_law: 81.0
    mmlu_jurisprudence: 74.1
    mmlu_logical_fallacies: 78.5
    mmlu_machine_learning: 53.6
    mmlu_management: 81.6
    mmlu_marketing: 88.0
    mmlu_medical_genetics: 70.0
    mmlu_miscellaneous: 79.8
    mmlu_moral_disputes: 70.2
    mmlu_moral_scenarios: 39.8
    mmlu_nutrition: 74.2
    mmlu_philosophy: 72.7
    mmlu_prehistory: 68.8
    mmlu_professional_accounting: 51.1
    mmlu_professional_law: 46.2
    mmlu_professional_medicine: 68.8
    mmlu_professional_psychology: 66.2
    mmlu_public_relations: 64.5
    mmlu_security_studies: 72.7
    mmlu_sociology: 82.6
    mmlu_us_foreign_policy: 88.0
    mmlu_virology: 53.6
    mmlu_world_religions: 81.9
    ifeval: 22.7
    bbh: 45.2
    math_500: 3.0
    gpqa_diamond: 29.2
    musr: 40.3
    mmlu_pro: 29.5
  evidence:
  - benchmark_id: arc_challenge
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 60.49
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task arc:challenge (25-shot, acc_norm), x100.
    limitations: ''
  - benchmark_id: bbh
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 45.17
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/contents
    source_kind: independent_evaluator
    evidence_date: '2024-06-16'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v2 BBH
    configuration: Open LLM Leaderboard v2 contents row mistralai/Mistral-7B-v0.3, column "BBH Raw" x100 (raw accuracy,
      not the normalised score). Run date from the earliest results_*.json for this repo in open-llm-leaderboard/results.
    limitations: ''
  - benchmark_id: gsm8k
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 34.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task gsm8k (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: hellaswag
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 82.99
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hellaswag (10-shot, acc_norm), x100.
    limitations: ''
  - benchmark_id: ifeval
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 22.66
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/contents
    source_kind: independent_evaluator
    evidence_date: '2024-06-16'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v2 IFEval
    configuration: Open LLM Leaderboard v2 contents row mistralai/Mistral-7B-v0.3, column "IFEval Raw" x100 (raw accuracy,
      not the normalised score). Run date from the earliest results_*.json for this repo in open-llm-leaderboard/results.
    limitations: ''
  - benchmark_id: mmlu_abstract_algebra
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 30.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-abstract_algebra (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_anatomy
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 60.74
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-anatomy (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_astronomy
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 65.13
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-astronomy (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_business_ethics
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 61.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-business_ethics (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_clinical_knowledge
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 68.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-clinical_knowledge (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_college_biology
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 69.44
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-college_biology (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_college_chemistry
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 49.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-college_chemistry (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_college_computer_science
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 52.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-college_computer_science (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_college_mathematics
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 37.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-college_mathematics (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_college_medicine
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 63.01
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-college_medicine (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_college_physics
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 31.37
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-college_physics (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_computer_security
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 73.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-computer_security (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_conceptual_physics
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 58.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-conceptual_physics (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_econometrics
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 44.74
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-econometrics (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_electrical_engineering
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 55.86
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-electrical_engineering (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_elementary_mathematics
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 40.21
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-elementary_mathematics (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_formal_logic
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 39.68
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-formal_logic (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_global_facts
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 40.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-global_facts (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_high_school_biology
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 76.13
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-high_school_biology (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_high_school_chemistry
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 54.19
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-high_school_chemistry (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_high_school_computer_science
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 65.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-high_school_computer_science (5-shot, acc),
      x100.
    limitations: ''
  - benchmark_id: mmlu_high_school_european_history
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 76.36
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-high_school_european_history (5-shot, acc),
      x100.
    limitations: ''
  - benchmark_id: mmlu_high_school_geography
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 77.27
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-high_school_geography (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_high_school_government_and_politics
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 87.56
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-high_school_government_and_politics (5-shot,
      acc), x100.
    limitations: ''
  - benchmark_id: mmlu_high_school_macroeconomics
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 60.51
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-high_school_macroeconomics (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_high_school_mathematics
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 35.93
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-high_school_mathematics (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_high_school_microeconomics
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 63.87
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-high_school_microeconomics (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_high_school_physics
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 35.76
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-high_school_physics (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_high_school_psychology
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 80.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-high_school_psychology (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_high_school_statistics
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 51.85
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-high_school_statistics (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_high_school_us_history
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 81.37
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-high_school_us_history (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_high_school_world_history
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 78.06
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-high_school_world_history (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_human_aging
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 69.96
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-human_aging (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_human_sexuality
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 77.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-human_sexuality (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_international_law
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 80.99
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-international_law (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_jurisprudence
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 74.07
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-jurisprudence (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_logical_fallacies
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 78.53
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-logical_fallacies (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_machine_learning
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 53.57
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-machine_learning (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_management
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 81.55
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-management (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_marketing
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 88.03
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-marketing (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_medical_genetics
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 70.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-medical_genetics (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_miscellaneous
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 79.82
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-miscellaneous (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_moral_disputes
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 70.23
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-moral_disputes (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_moral_scenarios
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 39.78
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-moral_scenarios (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_nutrition
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 74.18
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-nutrition (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_philosophy
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 72.67
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-philosophy (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_prehistory
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 68.83
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-prehistory (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_pro
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 29.53
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/contents
    source_kind: independent_evaluator
    evidence_date: '2024-06-16'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v2 MMLU-Pro
    configuration: Open LLM Leaderboard v2 contents row mistralai/Mistral-7B-v0.3, column "MMLU-PRO Raw" x100 (raw
      accuracy, not the normalised score). Run date from the earliest results_*.json for this repo in open-llm-leaderboard/results.
    limitations: ''
  - benchmark_id: mmlu_professional_accounting
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 51.06
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-professional_accounting (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_professional_law
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 46.15
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-professional_law (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_professional_medicine
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 68.75
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-professional_medicine (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_professional_psychology
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 66.18
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-professional_psychology (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_public_relations
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 64.55
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-public_relations (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_security_studies
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 72.65
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-security_studies (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_sociology
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 82.59
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-sociology (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_us_foreign_policy
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 88.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-us_foreign_policy (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_virology
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 53.61
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-virology (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: mmlu_world_religions
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 81.87
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task hendrycksTest-world_religions (5-shot, acc), x100.
    limitations: ''
  - benchmark_id: musr
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 40.32
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/contents
    source_kind: independent_evaluator
    evidence_date: '2024-06-16'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v2 MuSR
    configuration: Open LLM Leaderboard v2 contents row mistralai/Mistral-7B-v0.3, column "MUSR Raw" x100 (raw accuracy,
      not the normalised score). Run date from the earliest results_*.json for this repo in open-llm-leaderboard/results.
    limitations: ''
  - benchmark_id: truthfulqa
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 41.79
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task truthfulqa:mc (0-shot, mc2), x100.
    limitations: ''
  - benchmark_id: winogrande
    model_id_as_evaluated: mistralai/Mistral-7B-v0.3
    score: 78.45
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/blob/main/mistralai/Mistral-7B-v0.3/results_2024-05-23T11-37-26.409605.json
    source_kind: independent_evaluator
    evidence_date: '2024-05-23'
    date_type: evaluated
    verified_at: '2026-09-23'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Open LLM Leaderboard v1 harness task winogrande (5-shot, acc), x100.
    limitations: ''
  benchmark_source: open-llm-leaderboard-v1, open-llm-leaderboard-v2
  benchmark_as_of: 2024-07
  benchmark_notes: 'MODEL-116 overlap, found in the MODEL-125 clone check on 2026-09-23: gpqa_diamond holds the Open
    LLM Leaderboard v2 "GPQA Raw" value for mistralai/Mistral-7B-v0.3; math_500 holds the Open LLM Leaderboard v2
    "MATH Lvl 5 Raw" value for mistralai/Mistral-7B-v0.3. Each value is confirmed for this exact model but is not
    the benchmark its key names, so it stays in the flat block and is not promoted to evidence.'
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
    vllm: true
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
  huggingface_downloads: 323114
  huggingface_likes: 572
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
  huggingface_url: https://huggingface.co/mistralai/Mistral-7B-v0.3
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


# Mistral 7B v0.3

Auto-generated from HuggingFace Hub metadata for [mistralai/Mistral-7B-v0.3](https://huggingface.co/mistralai/Mistral-7B-v0.3).

Licence: apache-2.0. Creator distribution https://huggingface.co/mistralai/Mistral-7B-v0.3/raw/main/README.md (apache-2.0) and Hub cardData.license apache-2.0, read 2026-09-18.
