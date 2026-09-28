---
model_id: nous-research/meta-llama-3-8b-instruct
display_name: Meta Llama 3 8B Instruct
provider: nous-research
provider_display: Nous Research
family: llama
version: ''
release_date: '2024-04-18'
last_updated: ''
status: active
model_type: llm-chat
model_subtypes: []
tags:
- text-generation
pipeline_tag: text-generation
architecture:
  type: null
  total_parameters: 8030261248
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
  vocab_size: 128256
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
  base_model: meta/meta-llama-3-8b-instruct
  base_model_relation: repackaged
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
  license_type: llama-community
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
  origin_org_type: open-collective
modalities:
  input:
  - text
  output:
  - text
  text:
    max_input_tokens: null
    max_output_tokens: null
    context_window: 8192
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
  input: null
  output: null
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
    model_id: NousResearch/Meta-Llama-3-8B-Instruct
    url: https://huggingface.co/NousResearch/Meta-Llama-3-8B-Instruct
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
    arc_challenge: 60.8
    gsm8k: 68.7
    truthfulqa: 51.6
    winogrande: 74.5
    mmlu_abstract_algebra: 32.0
    mmlu_anatomy: 65.2
    mmlu_astronomy: 70.4
    mmlu_business_ethics: 69.0
    mmlu_clinical_knowledge: 74.7
    mmlu_college_biology: 79.9
    mmlu_college_computer_science: 59.0
    mmlu_college_mathematics: 39.0
    mmlu_college_medicine: 63.6
    mmlu_college_physics: 50.0
    mmlu_conceptual_physics: 60.4
    mmlu_econometrics: 60.5
    mmlu_electrical_engineering: 62.8
    mmlu_elementary_mathematics: 44.4
    mmlu_formal_logic: 48.4
    mmlu_global_facts: 40.0
    mmlu_high_school_biology: 78.4
    mmlu_high_school_chemistry: 50.7
    mmlu_high_school_european_history: 74.5
    mmlu_high_school_macroeconomics: 65.9
    mmlu_high_school_mathematics: 40.0
    mmlu_high_school_physics: 44.4
    mmlu_high_school_psychology: 83.7
    mmlu_high_school_statistics: 53.7
    mmlu_high_school_world_history: 84.4
    mmlu_human_aging: 72.2
    mmlu_international_law: 81.8
    mmlu_logical_fallacies: 76.7
    mmlu_medical_genetics: 80.0
    mmlu_miscellaneous: 79.8
    mmlu_moral_disputes: 74.9
    mmlu_moral_scenarios: 43.7
    mmlu_nutrition: 74.5
    mmlu_philosophy: 71.4
    mmlu_professional_law: 47.8
    mmlu_professional_medicine: 71.7
    mmlu_professional_psychology: 70.6
    mmlu_virology: 51.2
    mmlu_world_religions: 77.8
  evidence:
  - benchmark_id: hellaswag
    model_id_as_evaluated: NousResearch/Meta-Llama-3-8B-Instruct
    score: 78.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Meta-Llama-3-8B-Instruct/results_2024-04-19T18-40-48.433302.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-19'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-5a1fd131eab1
      snapshot_ref: sha256:2c1671aea87b8c3fcb064326fb3345f1fe11bb4cfd8de27935be55fd22b9311e
      cited_regions:
      - rows
    id: nous-research/meta-llama-3-8b-instruct#hellaswag#0e38705adb12
  - benchmark_id: mmlu_college_chemistry
    model_id_as_evaluated: NousResearch/Meta-Llama-3-8B-Instruct
    score: 47.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Meta-Llama-3-8B-Instruct/results_2024-04-19T18-40-48.433302.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-19'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-5a1fd131eab1
      snapshot_ref: sha256:2c1671aea87b8c3fcb064326fb3345f1fe11bb4cfd8de27935be55fd22b9311e
      cited_regions:
      - rows
    id: nous-research/meta-llama-3-8b-instruct#mmlu_college_chemistry#b8d7aa8e6e6e
  - benchmark_id: mmlu_computer_security
    model_id_as_evaluated: NousResearch/Meta-Llama-3-8B-Instruct
    score: 77.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Meta-Llama-3-8B-Instruct/results_2024-04-19T18-40-48.433302.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-19'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-5a1fd131eab1
      snapshot_ref: sha256:2c1671aea87b8c3fcb064326fb3345f1fe11bb4cfd8de27935be55fd22b9311e
      cited_regions:
      - rows
    id: nous-research/meta-llama-3-8b-instruct#mmlu_computer_security#1f324b08a798
  - benchmark_id: mmlu_high_school_computer_science
    model_id_as_evaluated: NousResearch/Meta-Llama-3-8B-Instruct
    score: 75.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Meta-Llama-3-8B-Instruct/results_2024-04-19T18-40-48.433302.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-19'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-5a1fd131eab1
      snapshot_ref: sha256:2c1671aea87b8c3fcb064326fb3345f1fe11bb4cfd8de27935be55fd22b9311e
      cited_regions:
      - rows
    id: nous-research/meta-llama-3-8b-instruct#mmlu_high_school_computer_science#3db785765071
  - benchmark_id: mmlu_high_school_geography
    model_id_as_evaluated: NousResearch/Meta-Llama-3-8B-Instruct
    score: 84.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Meta-Llama-3-8B-Instruct/results_2024-04-19T18-40-48.433302.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-19'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-5a1fd131eab1
      snapshot_ref: sha256:2c1671aea87b8c3fcb064326fb3345f1fe11bb4cfd8de27935be55fd22b9311e
      cited_regions:
      - rows
    id: nous-research/meta-llama-3-8b-instruct#mmlu_high_school_geography#d1e2073eac90
  - benchmark_id: mmlu_high_school_government_and_politics
    model_id_as_evaluated: NousResearch/Meta-Llama-3-8B-Instruct
    score: 91.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Meta-Llama-3-8B-Instruct/results_2024-04-19T18-40-48.433302.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-19'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-5a1fd131eab1
      snapshot_ref: sha256:2c1671aea87b8c3fcb064326fb3345f1fe11bb4cfd8de27935be55fd22b9311e
      cited_regions:
      - rows
    id: nous-research/meta-llama-3-8b-instruct#mmlu_high_school_government_and_politics#eda06680432a
  - benchmark_id: mmlu_high_school_microeconomics
    model_id_as_evaluated: NousResearch/Meta-Llama-3-8B-Instruct
    score: 76.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Meta-Llama-3-8B-Instruct/results_2024-04-19T18-40-48.433302.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-19'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-5a1fd131eab1
      snapshot_ref: sha256:2c1671aea87b8c3fcb064326fb3345f1fe11bb4cfd8de27935be55fd22b9311e
      cited_regions:
      - rows
    id: nous-research/meta-llama-3-8b-instruct#mmlu_high_school_microeconomics#c84a2252a6c3
  - benchmark_id: mmlu_high_school_us_history
    model_id_as_evaluated: NousResearch/Meta-Llama-3-8B-Instruct
    score: 85.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Meta-Llama-3-8B-Instruct/results_2024-04-19T18-40-48.433302.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-19'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-5a1fd131eab1
      snapshot_ref: sha256:2c1671aea87b8c3fcb064326fb3345f1fe11bb4cfd8de27935be55fd22b9311e
      cited_regions:
      - rows
    id: nous-research/meta-llama-3-8b-instruct#mmlu_high_school_us_history#0b6e36d7037b
  - benchmark_id: mmlu_human_sexuality
    model_id_as_evaluated: NousResearch/Meta-Llama-3-8B-Instruct
    score: 77.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Meta-Llama-3-8B-Instruct/results_2024-04-19T18-40-48.433302.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-19'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-5a1fd131eab1
      snapshot_ref: sha256:2c1671aea87b8c3fcb064326fb3345f1fe11bb4cfd8de27935be55fd22b9311e
      cited_regions:
      - rows
    id: nous-research/meta-llama-3-8b-instruct#mmlu_human_sexuality#369e828c3bc4
  - benchmark_id: mmlu_jurisprudence
    model_id_as_evaluated: NousResearch/Meta-Llama-3-8B-Instruct
    score: 77.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Meta-Llama-3-8B-Instruct/results_2024-04-19T18-40-48.433302.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-19'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-5a1fd131eab1
      snapshot_ref: sha256:2c1671aea87b8c3fcb064326fb3345f1fe11bb4cfd8de27935be55fd22b9311e
      cited_regions:
      - rows
    id: nous-research/meta-llama-3-8b-instruct#mmlu_jurisprudence#9454b90dfefc
  - benchmark_id: mmlu_machine_learning
    model_id_as_evaluated: NousResearch/Meta-Llama-3-8B-Instruct
    score: 54.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Meta-Llama-3-8B-Instruct/results_2024-04-19T18-40-48.433302.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-19'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-5a1fd131eab1
      snapshot_ref: sha256:2c1671aea87b8c3fcb064326fb3345f1fe11bb4cfd8de27935be55fd22b9311e
      cited_regions:
      - rows
    id: nous-research/meta-llama-3-8b-instruct#mmlu_machine_learning#3750e964af3e
  - benchmark_id: mmlu_management
    model_id_as_evaluated: NousResearch/Meta-Llama-3-8B-Instruct
    score: 78.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Meta-Llama-3-8B-Instruct/results_2024-04-19T18-40-48.433302.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-19'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-5a1fd131eab1
      snapshot_ref: sha256:2c1671aea87b8c3fcb064326fb3345f1fe11bb4cfd8de27935be55fd22b9311e
      cited_regions:
      - rows
    id: nous-research/meta-llama-3-8b-instruct#mmlu_management#a8d0711c9088
  - benchmark_id: mmlu_marketing
    model_id_as_evaluated: NousResearch/Meta-Llama-3-8B-Instruct
    score: 90.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Meta-Llama-3-8B-Instruct/results_2024-04-19T18-40-48.433302.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-19'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-5a1fd131eab1
      snapshot_ref: sha256:2c1671aea87b8c3fcb064326fb3345f1fe11bb4cfd8de27935be55fd22b9311e
      cited_regions:
      - rows
    id: nous-research/meta-llama-3-8b-instruct#mmlu_marketing#58ab02a8ce87
  - benchmark_id: mmlu_prehistory
    model_id_as_evaluated: NousResearch/Meta-Llama-3-8B-Instruct
    score: 74.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Meta-Llama-3-8B-Instruct/results_2024-04-19T18-40-48.433302.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-19'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-5a1fd131eab1
      snapshot_ref: sha256:2c1671aea87b8c3fcb064326fb3345f1fe11bb4cfd8de27935be55fd22b9311e
      cited_regions:
      - rows
    id: nous-research/meta-llama-3-8b-instruct#mmlu_prehistory#ae557913b961
  - benchmark_id: mmlu_professional_accounting
    model_id_as_evaluated: NousResearch/Meta-Llama-3-8B-Instruct
    score: 52.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Meta-Llama-3-8B-Instruct/results_2024-04-19T18-40-48.433302.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-19'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-5a1fd131eab1
      snapshot_ref: sha256:2c1671aea87b8c3fcb064326fb3345f1fe11bb4cfd8de27935be55fd22b9311e
      cited_regions:
      - rows
    id: nous-research/meta-llama-3-8b-instruct#mmlu_professional_accounting#0140934e1a9e
  - benchmark_id: mmlu_public_relations
    model_id_as_evaluated: NousResearch/Meta-Llama-3-8B-Instruct
    score: 64.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Meta-Llama-3-8B-Instruct/results_2024-04-19T18-40-48.433302.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-19'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-5a1fd131eab1
      snapshot_ref: sha256:2c1671aea87b8c3fcb064326fb3345f1fe11bb4cfd8de27935be55fd22b9311e
      cited_regions:
      - rows
    id: nous-research/meta-llama-3-8b-instruct#mmlu_public_relations#87117a880123
  - benchmark_id: mmlu_security_studies
    model_id_as_evaluated: NousResearch/Meta-Llama-3-8B-Instruct
    score: 73.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Meta-Llama-3-8B-Instruct/results_2024-04-19T18-40-48.433302.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-19'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-5a1fd131eab1
      snapshot_ref: sha256:2c1671aea87b8c3fcb064326fb3345f1fe11bb4cfd8de27935be55fd22b9311e
      cited_regions:
      - rows
    id: nous-research/meta-llama-3-8b-instruct#mmlu_security_studies#3c75a4bcd3ff
  - benchmark_id: mmlu_sociology
    model_id_as_evaluated: NousResearch/Meta-Llama-3-8B-Instruct
    score: 86.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Meta-Llama-3-8B-Instruct/results_2024-04-19T18-40-48.433302.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-19'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-5a1fd131eab1
      snapshot_ref: sha256:2c1671aea87b8c3fcb064326fb3345f1fe11bb4cfd8de27935be55fd22b9311e
      cited_regions:
      - rows
    id: nous-research/meta-llama-3-8b-instruct#mmlu_sociology#8d224861a1b7
  - benchmark_id: mmlu_us_foreign_policy
    model_id_as_evaluated: NousResearch/Meta-Llama-3-8B-Instruct
    score: 86.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Meta-Llama-3-8B-Instruct/results_2024-04-19T18-40-48.433302.json
    source_kind: independent_evaluator
    evidence_date: '2024-04-19'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-5a1fd131eab1
      snapshot_ref: sha256:2c1671aea87b8c3fcb064326fb3345f1fe11bb4cfd8de27935be55fd22b9311e
      cited_regions:
      - rows
    id: nous-research/meta-llama-3-8b-instruct#mmlu_us_foreign_policy#d9c83382b1c3
  benchmark_source: open-llm-leaderboard-v1, open-llm-leaderboard-v2
  benchmark_as_of: 2024-07
  benchmark_notes: 'MODEL-116, 2026-09-24: removed math_500 9.1 and gpqa_diamond 29.3. They were the Open LLM Leaderboard
    v2 MATH Lvl 5 and GPQA values for meta-llama/Meta-Llama-3-8B-Instruct, a different repository from this card''s
    (NousResearch/Meta-Llama-3-8B-Instruct). MODEL-154, read 2026-09-24: Set ifeval, bbh, musr and mmlu_pro to null.
    No exact repository row in contents and no results directory for this repository. No evidence is transferred from
    a mirror, quantization, base or instruction-tuned variant. Source inventory: https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet.'
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
  huggingface_downloads: 42757
  huggingface_likes: 105
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
  huggingface_url: https://huggingface.co/NousResearch/Meta-Llama-3-8B-Instruct
  arxiv_url: ''
  paper_url: ''
  github_url: ''
  ollama_url: ''
  artificial_analysis_url: ''
  arena_url: ''
  last_scraped_models_dev: ''
  last_scraped_huggingface: '2026-04-05'
  last_scraped_benchmarks: ''
  last_scraped_pricing: ''
card_schema_version: '3.0'
card_author: huggingface-seeder
card_created: '2026-04-05'
card_updated: '2026-04-05'
---


# Meta Llama 3 8B Instruct

Auto-generated from HuggingFace Hub metadata for [NousResearch/Meta-Llama-3-8B-Instruct](https://huggingface.co/NousResearch/Meta-Llama-3-8B-Instruct).