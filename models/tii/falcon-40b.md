---
model_id: tii/falcon-40b
display_name: falcon 40B
provider: tii
provider_display: TII
family: falcon
version: ''
release_date: '2023-05-24'
last_updated: ''
status: active
model_type: llm-code
model_subtypes: []
tags:
- text-generation
pipeline_tag: text-generation
architecture:
  type: null
  total_parameters: 41835970560
  active_parameters: null
  num_experts: null
  experts_per_token: null
  num_layers: 60
  hidden_size: 8192
  intermediate_size: null
  attention_type: null
  num_attention_heads: 128
  num_kv_heads: 8
  positional_encoding: null
  rope_theta: null
  vocab_size: 65024
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
  license_url: https://huggingface.co/tiiuae/falcon-40b/raw/main/README.md
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
  origin_country: AE
  origin_org_type: private
modalities:
  input:
  - text
  output:
  - text
  text:
    max_input_tokens: null
    max_output_tokens: null
    context_window: 2048
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
  input: 0.6
  output: 0.6
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
    model_id: tiiuae/falcon-40b
    url: https://huggingface.co/tiiuae/falcon-40b
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
    truthfulqa: 41.7
    mmlu_abstract_algebra: 34.0
    mmlu_astronomy: 57.2
    mmlu_business_ethics: 54.0
    mmlu_clinical_knowledge: 60.8
    mmlu_college_biology: 66.7
    mmlu_college_chemistry: 45.0
    mmlu_college_computer_science: 50.0
    mmlu_college_mathematics: 39.0
    mmlu_college_physics: 27.5
    mmlu_electrical_engineering: 53.1
    mmlu_formal_logic: 30.2
    mmlu_high_school_chemistry: 44.3
    mmlu_high_school_computer_science: 62.0
    mmlu_high_school_european_history: 69.7
    mmlu_high_school_macroeconomics: 55.4
    mmlu_high_school_mathematics: 31.5
    mmlu_high_school_microeconomics: 55.5
    mmlu_high_school_physics: 31.8
    mmlu_high_school_psychology: 77.6
    mmlu_high_school_world_history: 71.3
    mmlu_human_sexuality: 72.5
    mmlu_medical_genetics: 66.0
    mmlu_miscellaneous: 75.9
    mmlu_moral_disputes: 62.7
    mmlu_moral_scenarios: 27.0
    mmlu_nutrition: 67.3
    mmlu_philosophy: 66.9
    mmlu_prehistory: 63.3
    mmlu_professional_accounting: 43.6
    mmlu_professional_law: 43.2
    mmlu_security_studies: 66.1
    mmlu_sociology: 79.6
    mmlu_us_foreign_policy: 81.0
    mmlu_virology: 47.6
    mmlu_world_religions: 80.7
  evidence:
  - benchmark_id: arc_challenge
    model_id_as_evaluated: tiiuae/falcon-40b
    score: 61.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/tiiuae/falcon-40b/results_2023-11-27T10-24-56.579363.json
    source_kind: independent_evaluator
    evidence_date: '2023-11-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-412600e523b7
      snapshot_ref: sha256:05cb7cdd0234f9f41324ac3cdc33241da47ce7e74e5b4be5a11b6b26c0cff6e8
      cited_regions:
      - rows
    id: tii/falcon-40b#arc_challenge#eb059aac9b4d
  - benchmark_id: bbh
    model_id_as_evaluated: tiiuae/falcon-40b
    score: 40.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/tiiuae/falcon-40b/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-19'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-18606e317e6f
      snapshot_ref: sha256:ac06bf3a8c1413bf8e6685beea4fb2927dbbe301b8ef1fccf25eaf5ab126fa37
      cited_regions:
      - rows
    id: tii/falcon-40b#bbh#daed8d9ce321
  - benchmark_id: gpqa_pooled
    model_id_as_evaluated: tiiuae/falcon-40b
    score: 27.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/tiiuae/falcon-40b/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-19'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-18606e317e6f
      snapshot_ref: sha256:ac06bf3a8c1413bf8e6685beea4fb2927dbbe301b8ef1fccf25eaf5ab126fa37
      cited_regions:
      - rows
    id: tii/falcon-40b#gpqa_pooled#dd140f2617f3
  - benchmark_id: hellaswag
    model_id_as_evaluated: tiiuae/falcon-40b
    score: 85.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/tiiuae/falcon-40b/results_2023-11-27T10-24-56.579363.json
    source_kind: independent_evaluator
    evidence_date: '2023-11-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-412600e523b7
      snapshot_ref: sha256:05cb7cdd0234f9f41324ac3cdc33241da47ce7e74e5b4be5a11b6b26c0cff6e8
      cited_regions:
      - rows
    id: tii/falcon-40b#hellaswag#753ecabb6e32
  - benchmark_id: ifeval
    model_id_as_evaluated: tiiuae/falcon-40b
    score: 25.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/tiiuae/falcon-40b/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-19'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-18606e317e6f
      snapshot_ref: sha256:ac06bf3a8c1413bf8e6685beea4fb2927dbbe301b8ef1fccf25eaf5ab126fa37
      cited_regions:
      - rows
    id: tii/falcon-40b#ifeval#b9f2e52cf627
  - benchmark_id: math_lvl5
    model_id_as_evaluated: tiiuae/falcon-40b
    score: 1.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/tiiuae/falcon-40b/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-19'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-18606e317e6f
      snapshot_ref: sha256:ac06bf3a8c1413bf8e6685beea4fb2927dbbe301b8ef1fccf25eaf5ab126fa37
      cited_regions:
      - rows
    id: tii/falcon-40b#math_lvl5#66f43f2fb4e3
  - benchmark_id: mmlu_anatomy
    model_id_as_evaluated: tiiuae/falcon-40b
    score: 53.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/tiiuae/falcon-40b/results_2023-11-27T10-24-56.579363.json
    source_kind: independent_evaluator
    evidence_date: '2023-11-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-412600e523b7
      snapshot_ref: sha256:05cb7cdd0234f9f41324ac3cdc33241da47ce7e74e5b4be5a11b6b26c0cff6e8
      cited_regions:
      - rows
    id: tii/falcon-40b#mmlu_anatomy#2b3e9d1c1995
  - benchmark_id: mmlu_college_medicine
    model_id_as_evaluated: tiiuae/falcon-40b
    score: 52.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/tiiuae/falcon-40b/results_2023-11-27T10-24-56.579363.json
    source_kind: independent_evaluator
    evidence_date: '2023-11-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-412600e523b7
      snapshot_ref: sha256:05cb7cdd0234f9f41324ac3cdc33241da47ce7e74e5b4be5a11b6b26c0cff6e8
      cited_regions:
      - rows
    id: tii/falcon-40b#mmlu_college_medicine#343bbe4b2b72
  - benchmark_id: mmlu_computer_security
    model_id_as_evaluated: tiiuae/falcon-40b
    score: 63.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/tiiuae/falcon-40b/results_2023-11-27T10-24-56.579363.json
    source_kind: independent_evaluator
    evidence_date: '2023-11-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-412600e523b7
      snapshot_ref: sha256:05cb7cdd0234f9f41324ac3cdc33241da47ce7e74e5b4be5a11b6b26c0cff6e8
      cited_regions:
      - rows
    id: tii/falcon-40b#mmlu_computer_security#c0a482be5c2f
  - benchmark_id: mmlu_conceptual_physics
    model_id_as_evaluated: tiiuae/falcon-40b
    score: 41.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/tiiuae/falcon-40b/results_2023-11-27T10-24-56.579363.json
    source_kind: independent_evaluator
    evidence_date: '2023-11-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-412600e523b7
      snapshot_ref: sha256:05cb7cdd0234f9f41324ac3cdc33241da47ce7e74e5b4be5a11b6b26c0cff6e8
      cited_regions:
      - rows
    id: tii/falcon-40b#mmlu_conceptual_physics#66ff60e2b99b
  - benchmark_id: mmlu_econometrics
    model_id_as_evaluated: tiiuae/falcon-40b
    score: 33.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/tiiuae/falcon-40b/results_2023-11-27T10-24-56.579363.json
    source_kind: independent_evaluator
    evidence_date: '2023-11-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-412600e523b7
      snapshot_ref: sha256:05cb7cdd0234f9f41324ac3cdc33241da47ce7e74e5b4be5a11b6b26c0cff6e8
      cited_regions:
      - rows
    id: tii/falcon-40b#mmlu_econometrics#cb42bae33204
  - benchmark_id: mmlu_elementary_mathematics
    model_id_as_evaluated: tiiuae/falcon-40b
    score: 33.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/tiiuae/falcon-40b/results_2023-11-27T10-24-56.579363.json
    source_kind: independent_evaluator
    evidence_date: '2023-11-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-412600e523b7
      snapshot_ref: sha256:05cb7cdd0234f9f41324ac3cdc33241da47ce7e74e5b4be5a11b6b26c0cff6e8
      cited_regions:
      - rows
    id: tii/falcon-40b#mmlu_elementary_mathematics#2781d8101e8c
  - benchmark_id: mmlu_global_facts
    model_id_as_evaluated: tiiuae/falcon-40b
    score: 32.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/tiiuae/falcon-40b/results_2023-11-27T10-24-56.579363.json
    source_kind: independent_evaluator
    evidence_date: '2023-11-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-412600e523b7
      snapshot_ref: sha256:05cb7cdd0234f9f41324ac3cdc33241da47ce7e74e5b4be5a11b6b26c0cff6e8
      cited_regions:
      - rows
    id: tii/falcon-40b#mmlu_global_facts#ebce6b5372ef
  - benchmark_id: mmlu_high_school_biology
    model_id_as_evaluated: tiiuae/falcon-40b
    score: 67.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/tiiuae/falcon-40b/results_2023-11-27T10-24-56.579363.json
    source_kind: independent_evaluator
    evidence_date: '2023-11-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-412600e523b7
      snapshot_ref: sha256:05cb7cdd0234f9f41324ac3cdc33241da47ce7e74e5b4be5a11b6b26c0cff6e8
      cited_regions:
      - rows
    id: tii/falcon-40b#mmlu_high_school_biology#1d1968856623
  - benchmark_id: mmlu_high_school_geography
    model_id_as_evaluated: tiiuae/falcon-40b
    score: 74.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/tiiuae/falcon-40b/results_2023-11-27T10-24-56.579363.json
    source_kind: independent_evaluator
    evidence_date: '2023-11-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-412600e523b7
      snapshot_ref: sha256:05cb7cdd0234f9f41324ac3cdc33241da47ce7e74e5b4be5a11b6b26c0cff6e8
      cited_regions:
      - rows
    id: tii/falcon-40b#mmlu_high_school_geography#09e77cb0039b
  - benchmark_id: mmlu_high_school_government_and_politics
    model_id_as_evaluated: tiiuae/falcon-40b
    score: 77.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/tiiuae/falcon-40b/results_2023-11-27T10-24-56.579363.json
    source_kind: independent_evaluator
    evidence_date: '2023-11-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-412600e523b7
      snapshot_ref: sha256:05cb7cdd0234f9f41324ac3cdc33241da47ce7e74e5b4be5a11b6b26c0cff6e8
      cited_regions:
      - rows
    id: tii/falcon-40b#mmlu_high_school_government_and_politics#b3dc3bdf6b06
  - benchmark_id: mmlu_high_school_statistics
    model_id_as_evaluated: tiiuae/falcon-40b
    score: 47.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/tiiuae/falcon-40b/results_2023-11-27T10-24-56.579363.json
    source_kind: independent_evaluator
    evidence_date: '2023-11-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-412600e523b7
      snapshot_ref: sha256:05cb7cdd0234f9f41324ac3cdc33241da47ce7e74e5b4be5a11b6b26c0cff6e8
      cited_regions:
      - rows
    id: tii/falcon-40b#mmlu_high_school_statistics#a9ea7c117a53
  - benchmark_id: mmlu_high_school_us_history
    model_id_as_evaluated: tiiuae/falcon-40b
    score: 71.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/tiiuae/falcon-40b/results_2023-11-27T10-24-56.579363.json
    source_kind: independent_evaluator
    evidence_date: '2023-11-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-412600e523b7
      snapshot_ref: sha256:05cb7cdd0234f9f41324ac3cdc33241da47ce7e74e5b4be5a11b6b26c0cff6e8
      cited_regions:
      - rows
    id: tii/falcon-40b#mmlu_high_school_us_history#703373f9600c
  - benchmark_id: mmlu_human_aging
    model_id_as_evaluated: tiiuae/falcon-40b
    score: 73.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/tiiuae/falcon-40b/results_2023-11-27T10-24-56.579363.json
    source_kind: independent_evaluator
    evidence_date: '2023-11-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-412600e523b7
      snapshot_ref: sha256:05cb7cdd0234f9f41324ac3cdc33241da47ce7e74e5b4be5a11b6b26c0cff6e8
      cited_regions:
      - rows
    id: tii/falcon-40b#mmlu_human_aging#9bbb863675ae
  - benchmark_id: mmlu_international_law
    model_id_as_evaluated: tiiuae/falcon-40b
    score: 65.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/tiiuae/falcon-40b/results_2023-11-27T10-24-56.579363.json
    source_kind: independent_evaluator
    evidence_date: '2023-11-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-412600e523b7
      snapshot_ref: sha256:05cb7cdd0234f9f41324ac3cdc33241da47ce7e74e5b4be5a11b6b26c0cff6e8
      cited_regions:
      - rows
    id: tii/falcon-40b#mmlu_international_law#b35ccfe418a2
  - benchmark_id: mmlu_jurisprudence
    model_id_as_evaluated: tiiuae/falcon-40b
    score: 69.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/tiiuae/falcon-40b/results_2023-11-27T10-24-56.579363.json
    source_kind: independent_evaluator
    evidence_date: '2023-11-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-412600e523b7
      snapshot_ref: sha256:05cb7cdd0234f9f41324ac3cdc33241da47ce7e74e5b4be5a11b6b26c0cff6e8
      cited_regions:
      - rows
    id: tii/falcon-40b#mmlu_jurisprudence#d8f6c77899c0
  - benchmark_id: mmlu_logical_fallacies
    model_id_as_evaluated: tiiuae/falcon-40b
    score: 65.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/tiiuae/falcon-40b/results_2023-11-27T10-24-56.579363.json
    source_kind: independent_evaluator
    evidence_date: '2023-11-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-412600e523b7
      snapshot_ref: sha256:05cb7cdd0234f9f41324ac3cdc33241da47ce7e74e5b4be5a11b6b26c0cff6e8
      cited_regions:
      - rows
    id: tii/falcon-40b#mmlu_logical_fallacies#b25e0b744b0f
  - benchmark_id: mmlu_machine_learning
    model_id_as_evaluated: tiiuae/falcon-40b
    score: 29.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/tiiuae/falcon-40b/results_2023-11-27T10-24-56.579363.json
    source_kind: independent_evaluator
    evidence_date: '2023-11-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-412600e523b7
      snapshot_ref: sha256:05cb7cdd0234f9f41324ac3cdc33241da47ce7e74e5b4be5a11b6b26c0cff6e8
      cited_regions:
      - rows
    id: tii/falcon-40b#mmlu_machine_learning#c45fa44c5293
  - benchmark_id: mmlu_management
    model_id_as_evaluated: tiiuae/falcon-40b
    score: 78.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/tiiuae/falcon-40b/results_2023-11-27T10-24-56.579363.json
    source_kind: independent_evaluator
    evidence_date: '2023-11-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-412600e523b7
      snapshot_ref: sha256:05cb7cdd0234f9f41324ac3cdc33241da47ce7e74e5b4be5a11b6b26c0cff6e8
      cited_regions:
      - rows
    id: tii/falcon-40b#mmlu_management#788e89dc40da
  - benchmark_id: mmlu_marketing
    model_id_as_evaluated: tiiuae/falcon-40b
    score: 79.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/tiiuae/falcon-40b/results_2023-11-27T10-24-56.579363.json
    source_kind: independent_evaluator
    evidence_date: '2023-11-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-412600e523b7
      snapshot_ref: sha256:05cb7cdd0234f9f41324ac3cdc33241da47ce7e74e5b4be5a11b6b26c0cff6e8
      cited_regions:
      - rows
    id: tii/falcon-40b#mmlu_marketing#b0c936658525
  - benchmark_id: mmlu_pro
    model_id_as_evaluated: tiiuae/falcon-40b
    score: 25.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/tiiuae/falcon-40b/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-19'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-18606e317e6f
      snapshot_ref: sha256:ac06bf3a8c1413bf8e6685beea4fb2927dbbe301b8ef1fccf25eaf5ab126fa37
      cited_regions:
      - rows
    id: tii/falcon-40b#mmlu_pro#532115fc0023
  - benchmark_id: mmlu_professional_medicine
    model_id_as_evaluated: tiiuae/falcon-40b
    score: 61.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/tiiuae/falcon-40b/results_2023-11-27T10-24-56.579363.json
    source_kind: independent_evaluator
    evidence_date: '2023-11-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-412600e523b7
      snapshot_ref: sha256:05cb7cdd0234f9f41324ac3cdc33241da47ce7e74e5b4be5a11b6b26c0cff6e8
      cited_regions:
      - rows
    id: tii/falcon-40b#mmlu_professional_medicine#ff24f783c2fd
  - benchmark_id: mmlu_professional_psychology
    model_id_as_evaluated: tiiuae/falcon-40b
    score: 56.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/tiiuae/falcon-40b/results_2023-11-27T10-24-56.579363.json
    source_kind: independent_evaluator
    evidence_date: '2023-11-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-412600e523b7
      snapshot_ref: sha256:05cb7cdd0234f9f41324ac3cdc33241da47ce7e74e5b4be5a11b6b26c0cff6e8
      cited_regions:
      - rows
    id: tii/falcon-40b#mmlu_professional_psychology#b82cb1b5ad17
  - benchmark_id: mmlu_public_relations
    model_id_as_evaluated: tiiuae/falcon-40b
    score: 62.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/tiiuae/falcon-40b/results_2023-11-27T10-24-56.579363.json
    source_kind: independent_evaluator
    evidence_date: '2023-11-27'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-412600e523b7
      snapshot_ref: sha256:05cb7cdd0234f9f41324ac3cdc33241da47ce7e74e5b4be5a11b6b26c0cff6e8
      cited_regions:
      - rows
    id: tii/falcon-40b#mmlu_public_relations#96729d14006a
  - benchmark_id: musr
    model_id_as_evaluated: tiiuae/falcon-40b
    score: 36.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/tiiuae/falcon-40b/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-19'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-18606e317e6f
      snapshot_ref: sha256:ac06bf3a8c1413bf8e6685beea4fb2927dbbe301b8ef1fccf25eaf5ab126fa37
      cited_regions:
      - rows
    id: tii/falcon-40b#musr#9c76ef2e5547
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
  huggingface_downloads: 21631
  huggingface_likes: 2434
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
  huggingface_url: https://huggingface.co/tiiuae/falcon-40b
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

# falcon 40B

Auto-generated from HuggingFace Hub metadata for [tiiuae/falcon-40b](https://huggingface.co/tiiuae/falcon-40b).

Licence: apache-2.0. Creator distribution https://huggingface.co/tiiuae/falcon-40b/raw/main/README.md (apache-2.0) and Hub cardData.license apache-2.0, read 2026-09-18.
