---
model_id: nous-research/nous-hermes-2-solar-10-7b
display_name: Nous Hermes 2 SOLAR 10.7B
provider: nous-research
provider_display: Nous Research
family: hermes
version: ''
release_date: '2024-01-01'
last_updated: ''
status: active
model_type: llm-chat
model_subtypes: []
tags:
- text-generation
pipeline_tag: text-generation
architecture:
  type: null
  total_parameters: 10731540480
  active_parameters: null
  num_experts: null
  experts_per_token: null
  num_layers: 48
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
  base_model: upstage/SOLAR-10.7B-v1.0
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
  license_url: https://huggingface.co/NousResearch/Nous-Hermes-2-SOLAR-10.7B/raw/main/README.md
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
    context_window: 4096
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
    model_id: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    url: https://huggingface.co/NousResearch/Nous-Hermes-2-SOLAR-10.7B
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
  - benchmark_id: arc_challenge
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 66.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#arc_challenge#05edccc43b20
  - benchmark_id: bbh
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 54.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-10d6931f1023
      snapshot_ref: sha256:0074a8b47ba6d048915aa8bd3ed4c2c05f6fd74d0bdbb3c8c45ea81d17296532
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#bbh#04b6040a8eb1
  - benchmark_id: gpqa_pooled
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 29.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-10d6931f1023
      snapshot_ref: sha256:0074a8b47ba6d048915aa8bd3ed4c2c05f6fd74d0bdbb3c8c45ea81d17296532
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#gpqa_pooled#c9f66511284a
  - benchmark_id: gsm8k
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 69.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#gsm8k#f415fe17a9e7
  - benchmark_id: hellaswag
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 84.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#hellaswag#e1bdecf74938
  - benchmark_id: ifeval
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 52.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-10d6931f1023
      snapshot_ref: sha256:0074a8b47ba6d048915aa8bd3ed4c2c05f6fd74d0bdbb3c8c45ea81d17296532
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#ifeval#37fa63dc2aaa
  - benchmark_id: math_lvl5
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 5.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-10d6931f1023
      snapshot_ref: sha256:0074a8b47ba6d048915aa8bd3ed4c2c05f6fd74d0bdbb3c8c45ea81d17296532
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#math_lvl5#334620b36e33
  - benchmark_id: mmlu_abstract_algebra
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 35.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_abstract_algebra#9fcdfba154e8
  - benchmark_id: mmlu_anatomy
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 56.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_anatomy#0580ab65a100
  - benchmark_id: mmlu_astronomy
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 76.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_astronomy#2ee57ee2a504
  - benchmark_id: mmlu_business_ethics
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 74.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_business_ethics#ab075446e529
  - benchmark_id: mmlu_clinical_knowledge
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 69.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_clinical_knowledge#d96aa8dd96b0
  - benchmark_id: mmlu_college_biology
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 72.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_college_biology#fcf893a04a4c
  - benchmark_id: mmlu_college_chemistry
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 47.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_college_chemistry#0b329dedd27a
  - benchmark_id: mmlu_college_computer_science
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 42.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_college_computer_science#4638c802a7b3
  - benchmark_id: mmlu_college_mathematics
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 37.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_college_mathematics#e76392ab0d5a
  - benchmark_id: mmlu_college_medicine
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 64.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_college_medicine#6c496631c4a3
  - benchmark_id: mmlu_college_physics
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 41.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_college_physics#be877aa6f636
  - benchmark_id: mmlu_computer_security
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 73.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_computer_security#1d560514efea
  - benchmark_id: mmlu_conceptual_physics
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 59.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_conceptual_physics#9014bfbb327d
  - benchmark_id: mmlu_econometrics
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 54.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_econometrics#7a4d960990dc
  - benchmark_id: mmlu_electrical_engineering
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 57.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_electrical_engineering#2c57d51b81cc
  - benchmark_id: mmlu_elementary_mathematics
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 48.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_elementary_mathematics#4ab30f0d8c2b
  - benchmark_id: mmlu_formal_logic
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 45.2
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_formal_logic#b49dd7bb9e7c
  - benchmark_id: mmlu_global_facts
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 32.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_global_facts#7ab15f869948
  - benchmark_id: mmlu_high_school_biology
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 80.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_high_school_biology#cad4d10a98c3
  - benchmark_id: mmlu_high_school_chemistry
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 51.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_high_school_chemistry#89bd35564df6
  - benchmark_id: mmlu_high_school_computer_science
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 71.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_high_school_computer_science#4cf8b38451b4
  - benchmark_id: mmlu_high_school_european_history
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 83.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_high_school_european_history#0b7696347efa
  - benchmark_id: mmlu_high_school_geography
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 87.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_high_school_geography#fed2ce1b780c
  - benchmark_id: mmlu_high_school_government_and_politics
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 89.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_high_school_government_and_politics#dfa7e49949f2
  - benchmark_id: mmlu_high_school_macroeconomics
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 67.4
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_high_school_macroeconomics#94161e42496a
  - benchmark_id: mmlu_high_school_mathematics
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 36.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_high_school_mathematics#7e322533d452
  - benchmark_id: mmlu_high_school_microeconomics
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 69.3
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_high_school_microeconomics#6a7fbc04c396
  - benchmark_id: mmlu_high_school_physics
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 37.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_high_school_physics#42bd87202261
  - benchmark_id: mmlu_high_school_psychology
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 85.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_high_school_psychology#3cf070cc57ae
  - benchmark_id: mmlu_high_school_statistics
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 52.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_high_school_statistics#ccf761474512
  - benchmark_id: mmlu_high_school_us_history
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 83.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_high_school_us_history#97ae233df595
  - benchmark_id: mmlu_high_school_world_history
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 87.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_high_school_world_history#df63faddef3d
  - benchmark_id: mmlu_human_aging
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 74.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_human_aging#9f70963fd801
  - benchmark_id: mmlu_human_sexuality
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 77.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_human_sexuality#071afbbf5d02
  - benchmark_id: mmlu_international_law
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 81.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_international_law#3e18b54cbccd
  - benchmark_id: mmlu_jurisprudence
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 78.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_jurisprudence#39e8b59e9a0f
  - benchmark_id: mmlu_logical_fallacies
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 74.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_logical_fallacies#c48d8ca475c8
  - benchmark_id: mmlu_machine_learning
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 50.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_machine_learning#01017e4a0c73
  - benchmark_id: mmlu_management
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 80.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_management#eca84271b08f
  - benchmark_id: mmlu_marketing
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 88.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_marketing#813fc281a119
  - benchmark_id: mmlu_medical_genetics
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 74.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_medical_genetics#2e6c3f8b4495
  - benchmark_id: mmlu_miscellaneous
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 82.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_miscellaneous#402dc340140e
  - benchmark_id: mmlu_moral_disputes
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 74.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_moral_disputes#9dc897d00784
  - benchmark_id: mmlu_moral_scenarios
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 34.9
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_moral_scenarios#fc6fda8ffe21
  - benchmark_id: mmlu_nutrition
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 77.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_nutrition#c7e726eceed1
  - benchmark_id: mmlu_philosophy
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 72.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_philosophy#367f7e11f733
  - benchmark_id: mmlu_prehistory
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 77.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_prehistory#899d457bb32a
  - benchmark_id: mmlu_pro
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 34.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-10d6931f1023
      snapshot_ref: sha256:0074a8b47ba6d048915aa8bd3ed4c2c05f6fd74d0bdbb3c8c45ea81d17296532
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_pro#7a208cf75c6e
  - benchmark_id: mmlu_professional_accounting
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 51.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_professional_accounting#64720b69b22a
  - benchmark_id: mmlu_professional_law
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 50.1
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_professional_law#83b4c0fe4513
  - benchmark_id: mmlu_professional_medicine
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 75.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_professional_medicine#2a90a0971142
  - benchmark_id: mmlu_professional_psychology
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 68.5
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_professional_psychology#7964f12e3236
  - benchmark_id: mmlu_public_relations
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 70.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_public_relations#19ff9c84ef0e
  - benchmark_id: mmlu_security_studies
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 78.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_security_studies#5d6aa22e0a36
  - benchmark_id: mmlu_sociology
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 82.6
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_sociology#ffab1c2780b9
  - benchmark_id: mmlu_us_foreign_policy
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 91.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_us_foreign_policy#312b8d214977
  - benchmark_id: mmlu_virology
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 56.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_virology#7c6f4788babe
  - benchmark_id: mmlu_world_religions
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 83.0
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#mmlu_world_religions#e878c6c0c8c1
  - benchmark_id: musr
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 43.7
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2025-02-13T18-27-04.338360.json
    source_kind: independent_evaluator
    evidence_date: '2024-06-16'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v2
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v2-10d6931f1023
      snapshot_ref: sha256:0074a8b47ba6d048915aa8bd3ed4c2c05f6fd74d0bdbb3c8c45ea81d17296532
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#musr#272d5be79875
  - benchmark_id: truthfulqa
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 55.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#truthfulqa#643c131d441b
  - benchmark_id: winogrande
    model_id_as_evaluated: NousResearch/Nous-Hermes-2-SOLAR-10.7B
    score: 82.8
    unit: percent
    source_url: https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json
    source_kind: independent_evaluator
    evidence_date: '2024-01-04'
    date_type: evaluated
    verified_at: '2026-09-25'
    benchmark_version: Open LLM Leaderboard v1
    configuration: Published per-model result; leaderboard metric converted from fraction to percent.
    limitations: Static leaderboard result. The source file identifies the evaluated repository and run
      date.
    measured_by: independent_evaluator
    sources:
    - source_id: oll-v1-d4b04a77b077
      snapshot_ref: sha256:405a88a3dec90a5066e444ee60a07029689380f2a98087553b17f20ac628aa30
      cited_regions:
      - rows
    id: nous-research/nous-hermes-2-solar-10-7b#winogrande#38ac8ae8d44b
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
  huggingface_downloads: 9179
  huggingface_likes: 208
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
  huggingface_url: https://huggingface.co/NousResearch/Nous-Hermes-2-SOLAR-10.7B
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


# Nous Hermes 2 SOLAR 10.7B

Auto-generated from HuggingFace Hub metadata for [NousResearch/Nous-Hermes-2-SOLAR-10.7B](https://huggingface.co/NousResearch/Nous-Hermes-2-SOLAR-10.7B).

Licence: apache-2.0. Creator distribution https://huggingface.co/NousResearch/Nous-Hermes-2-SOLAR-10.7B/raw/main/README.md (apache-2.0) and Hub cardData.license apache-2.0, read 2026-09-18.
