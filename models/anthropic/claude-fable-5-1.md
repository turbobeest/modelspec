---
model_id: anthropic/claude-fable-5-1
display_name: Claude Fable 5.1
provider: anthropic
provider_display: Anthropic
family: claude-fable
version: claude-fable-5-1
release_date: '2026-09-01'
last_updated: '2026-09-01'
status: active
model_type: llm-reasoning
model_subtypes: []
tags: []
pipeline_tag: ''
architecture:
  type: null
  total_parameters: null
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
  open_weights: false
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
  origin_country: US
  origin_org_type: null
modalities:
  input:
  - text
  - image
  - pdf
  output:
  - text
  text:
    max_input_tokens: null
    max_output_tokens: 128000
    context_window: 1000000
    streaming: null
    fill_in_middle: null
    json_mode: true
    system_prompt: null
  vision:
    supported: true
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
  input: 10.0
  output: 50.0
  reasoning: null
  cache_read: 0.25
  cache_write: 12.5
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
    available: false
    model_id: ''
    url: https://huggingface.co/
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
  - benchmark_id: swe_bench_pro
    model_id_as_evaluated: Claude Fable 5.1
    score: 81.2
    unit: percent
    source_url: https://www.anthropic.com/claude-fable-5-1-system-card
    source_kind: provider_self_report
    evidence_date: '2026-09-01'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: SWE-bench Pro
    configuration: Claude Fable 5.1 & Claude Mythos 5.1 System Card (dated September
      1, 2026), section 8. Taken only where the body text attributes the number to Fable
      5.1 by name; the summary table's shared 'Fable 5.1 / Mythos 5.1' column was not
      copied to either card. Adaptive thinking, max effort. Average over five trials.
    limitations: ''
  - benchmark_id: swe_bench_multilingual
    model_id_as_evaluated: Claude Fable 5.1
    score: 89.1
    unit: percent
    source_url: https://www.anthropic.com/claude-fable-5-1-system-card
    source_kind: provider_self_report
    evidence_date: '2026-09-01'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: SWE-bench Multilingual
    configuration: Claude Fable 5.1 & Claude Mythos 5.1 System Card (dated September
      1, 2026), section 8. Taken only where the body text attributes the number to Fable
      5.1 by name; the summary table's shared 'Fable 5.1 / Mythos 5.1' column was not
      copied to either card. Adaptive thinking, max effort. Average over five trials.
    limitations: ''
  - benchmark_id: swe_bench_multimodal
    model_id_as_evaluated: Claude Fable 5.1
    score: 54.7
    unit: percent
    source_url: https://www.anthropic.com/claude-fable-5-1-system-card
    source_kind: provider_self_report
    evidence_date: '2026-09-01'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: SWE-bench Multimodal
    configuration: Claude Fable 5.1 & Claude Mythos 5.1 System Card (dated September
      1, 2026), section 8. Taken only where the body text attributes the number to Fable
      5.1 by name; the summary table's shared 'Fable 5.1 / Mythos 5.1' column was not
      copied to either card. Adaptive thinking, max effort. Average over five trials.
    limitations: ''
  - benchmark_id: terminal_bench_v4_0
    model_id_as_evaluated: Claude Fable 5.1
    score: 55.8
    unit: percent
    source_url: https://www.anthropic.com/claude-fable-5-1-system-card
    source_kind: provider_self_report
    evidence_date: '2026-09-01'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: Terminal-Bench 4.0
    configuration: Claude Fable 5.1 & Claude Mythos 5.1 System Card (dated September
      1, 2026), section 8. Taken only where the body text attributes the number to Fable
      5.1 by name; the summary table's shared 'Fable 5.1 / Mythos 5.1' column was not
      copied to either card. Adaptive thinking, max effort. 15 trials per task, Claude
      Code --bare, max effort; SE ±1.6-2 pts.
    limitations: ''
    id: anthropic/claude-fable-5-1#terminal_bench_v4_0#be4c454ede6e
    measured_by: provider_self_report
    effort: max
    harness: unregistered
    sources:
    - source_id: model-158-anthropic-claude-fable-5-1-system-card
      snapshot_ref: sha256:7aa537ec09dd282f94919a8dd407403be66d1b482b50a36effe46a42213b01b9
      cited_regions:
      - terminal-bench-4-0
  - benchmark_id: terminal_bench_science
    model_id_as_evaluated: Claude Fable 5.1
    score: 52.6
    unit: percent
    source_url: https://www.anthropic.com/claude-fable-5-1-system-card
    source_kind: provider_self_report
    evidence_date: '2026-09-01'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: Terminal-Bench-Science 0.1
    configuration: Claude Fable 5.1 & Claude Mythos 5.1 System Card (dated September
      1, 2026), section 8. Taken only where the body text attributes the number to Fable
      5.1 by name; the summary table's shared 'Fable 5.1 / Mythos 5.1' column was not
      copied to either card. Adaptive thinking, max effort. Averaged over 10 trials
      per task (700 trials).
    limitations: ''
  - benchmark_id: arc_agi_2
    model_id_as_evaluated: Claude Fable 5.1 (max)
    score: 90.0
    unit: percent
    source_url: https://www.anthropic.com/claude-fable-5-1-system-card
    source_kind: provider_self_report
    evidence_date: '2026-09-01'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: ARC-AGI-2
    configuration: Claude Fable 5.1 & Claude Mythos 5.1 System Card (dated September
      1, 2026), section 8. Taken only where the body text attributes the number to Fable
      5.1 by name; the summary table's shared 'Fable 5.1 / Mythos 5.1' column was not
      copied to either card. Adaptive thinking, max effort. Max effort.
    limitations: ''
  - benchmark_id: arena_elo_overall
    model_id_as_evaluated: claude-fable-5.1-max
    score: 1507.58
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: Text Arena overall, raw (not style-controlled)
    configuration: LMArena's official leaderboard dataset, split latest, subset `text`
      (raw, non-style-controlled), category overall; leaderboard_publish_date 2026-09-13
      is the stated date. Rating 1507.58 (95% CI 1499.43-1515.73), 5783 votes. The live
      arena.ai board read 2026-09-24 still shows this snapshot (same vote counts).
    limitations: Normalization in api/ranking/engine.py bounds Arena Elo at 1400; values
      above clip.
    id: anthropic/claude-fable-5-1#arena_elo_overall#9661fc6241b2
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text
      snapshot_ref: sha256:b2143e53db27d7506c982ed4a7fe246289fd9ba5d181149507f0ee86bae47c18
      cited_regions:
      - rows
    interval:
    - 1499.43
    - 1515.73
    n: 5783
  - benchmark_id: arena_elo_coding
    model_id_as_evaluated: claude-fable-5.1-max
    score: 1511.36
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: Text Arena coding category, raw (not style-controlled)
    configuration: LMArena's official leaderboard dataset, split latest, subset `text`
      (raw, non-style-controlled), category coding. Raw to match arena_elo_overall;
      the arena.ai page defaults to style control; leaderboard_publish_date 2026-09-13
      is the stated date. Rating 1511.36 (95% CI 1493.86-1528.85), 1184 votes. The live
      arena.ai board read 2026-09-24 still shows this snapshot (same vote counts).
    limitations: Normalization in api/ranking/engine.py bounds Arena Elo at 1400; values
      above clip.
    id: anthropic/claude-fable-5-1#arena_elo_coding#898943f81012
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text
      snapshot_ref: sha256:acfd5444c3981590ac4a3e5589d1f54950660ce053f740f44a755d508540045b
      cited_regions:
      - rows
  - benchmark_id: arena_elo_style_control
    model_id_as_evaluated: claude-fable-5.1-max
    score: 1498.47
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / overall, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category overall,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1498.47 [1490.31, 1506.64], 5783 votes,
      rank 5.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: anthropic/claude-fable-5-1#arena_elo_style_control#8ac8ce0e6d60
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:4662065250a8ba456c98963d631fa259b3f2c305e33d948af0f8907e71c23550
      cited_regions:
      - rows
  - benchmark_id: arena_sc_coding
    model_id_as_evaluated: claude-fable-5.1-max
    score: 1518.89
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / coding, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category coding,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1518.89 [1501.27, 1536.50], 1184 votes,
      rank 32.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: anthropic/claude-fable-5-1#arena_sc_coding#2d51f6f3d3f3
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:861d314ad0c414b03631186d10aa7c7ce22220d9f005f2ff007b64e705982f88
      cited_regions:
      - rows
  - benchmark_id: arena_sc_hard_prompts
    model_id_as_evaluated: claude-fable-5.1-max
    score: 1516.66
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / hard_prompts, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category hard_prompts,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1516.66 [1506.19, 1527.13], 3437 votes,
      rank 8.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: anthropic/claude-fable-5-1#arena_sc_hard_prompts#5c8af8fd54fd
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:c76b4360f6dd0a76db1c93cecd958df7ee2bac63ba20b42d7b97bdc0d4d367c0
      cited_regions:
      - rows
  - benchmark_id: arena_sc_math
    model_id_as_evaluated: claude-fable-5.1-max
    score: 1522.28
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / math, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category math, leaderboard_publish_date
      2026-09-13; style control. Highest-effort row for the product (effort: max; MODEL-123
      max-effort rule). Rating 1522.28 [1486.11, 1558.46], 243 votes, rank 4.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: anthropic/claude-fable-5-1#arena_sc_math#b39d788bd347
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:3b05392555a93acf4a49b4db0f2c55b1706f39ad4af4fdda135d977a41d913bb
      cited_regions:
      - rows
  - benchmark_id: arena_sc_creative_writing
    model_id_as_evaluated: claude-fable-5.1-max
    score: 1486.33
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / creative_writing, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category creative_writing,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1486.33 [1468.29, 1504.37], 1233 votes,
      rank 6.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: anthropic/claude-fable-5-1#arena_sc_creative_writing#4e66481e8140
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:93f67d3f1afc6c8e089098ff841ea62a788d942bdfed88a5af59c391b50e85ba
      cited_regions:
      - rows
  - benchmark_id: arena_sc_instruction_following
    model_id_as_evaluated: claude-fable-5.1-max
    score: 1495.81
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / instruction_following, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category instruction_following,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1495.81 [1481.06, 1510.57], 1773 votes,
      rank 6.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: anthropic/claude-fable-5-1#arena_sc_instruction_following#ce66f691cf68
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:3a5c233b5a355ce846a9593281b3a329824f79715d7a088d43b4e16b4591d64d
      cited_regions:
      - rows
  - benchmark_id: arena_sc_multi_turn
    model_id_as_evaluated: claude-fable-5.1-max
    score: 1487.94
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / multi_turn, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category multi_turn,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1487.94 [1466.85, 1509.03], 807 votes,
      rank 23.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: anthropic/claude-fable-5-1#arena_sc_multi_turn#b931103cebf3
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:06bb5d8537c4748b32de8eebd54c17aa3f5be95aeb38c431641dfd64bf4fbf28
      cited_regions:
      - rows
  - benchmark_id: arena_sc_expert
    model_id_as_evaluated: claude-fable-5.1-max
    score: 1532.3
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / expert, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category expert,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1532.30 [1504.21, 1560.38], 468 votes,
      rank 8.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: anthropic/claude-fable-5-1#arena_sc_expert#1f01344a4da7
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:e096ca48998dee537b46e71137159b733af46c9e61a3b5d945bd96ccd2ddc70a
      cited_regions:
      - rows
  - benchmark_id: arena_sc_longer_query
    model_id_as_evaluated: claude-fable-5.1-max
    score: 1510.61
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / longer_query, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category longer_query,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1510.61 [1497.74, 1523.49], 2413 votes,
      rank 5.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: anthropic/claude-fable-5-1#arena_sc_longer_query#cdbc6e694f1e
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:154dced7e2bf6cc0d1a39b9edb550ed79ffe348a92bb0251a522e3c9515e0ea6
      cited_regions:
      - rows
  - benchmark_id: arena_sc_non_english
    model_id_as_evaluated: claude-fable-5.1-max
    score: 1492.38
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / non_english, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category non_english,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1492.38 [1481.90, 1502.85], 3374 votes,
      rank 3.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: anthropic/claude-fable-5-1#arena_sc_non_english#3b705ee6bda4
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:baef93b79236b01c043c3d7d41cb98aace9ab4d718250dc82f863d3b692ddbe5
      cited_regions:
      - rows
  - benchmark_id: arena_sc_medicine
    model_id_as_evaluated: claude-fable-5.1-max
    score: 1509.29
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
      (effort: max; MODEL-123 max-effort rule). Rating 1509.29 [1479.91, 1538.68], 435 votes,
      rank 6.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: anthropic/claude-fable-5-1#arena_sc_medicine#688371e6dbf9
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:9ac8343014a6f3fa3a087f7596192bcc37d4be5873044ebb2fbf369eddc040f1
      cited_regions:
      - rows
  - benchmark_id: arena_sc_legal
    model_id_as_evaluated: claude-fable-5.1-max
    score: 1497.12
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
      (effort: max; MODEL-123 max-effort rule). Rating 1497.12 [1468.85, 1525.39], 452 votes,
      rank 15.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: anthropic/claude-fable-5-1#arena_sc_legal#261d8bb99dea
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:73dac5a7b8594e73268d51ccc9991781448045bed3be54cd741b37de4ea10317
      cited_regions:
      - rows
  - benchmark_id: arena_sc_business
    model_id_as_evaluated: claude-fable-5.1-max
    score: 1485.89
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
      (effort: max; MODEL-123 max-effort rule). Rating 1485.89 [1468.05, 1503.73], 1118 votes,
      rank 17.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: anthropic/claude-fable-5-1#arena_sc_business#3d4d21f2afad
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:55a6c0caed26dbe460df511bb28bba4ccaa9aab5376e2efa6c7ecbdfca3605f0
      cited_regions:
      - rows
  - benchmark_id: arena_sc_science
    model_id_as_evaluated: claude-fable-5.1-max
    score: 1513.51
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
      (effort: max; MODEL-123 max-effort rule). Rating 1513.51 [1494.01, 1533.01], 924 votes,
      rank 9.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: anthropic/claude-fable-5-1#arena_sc_science#30e3e5aadc0e
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:e480b4aa4e4c6687e8e7153b1a1e5fcb4b84cef3f20c7df6895c8f7b5b1fab4c
      cited_regions:
      - rows
  - benchmark_id: arena_sc_writing
    model_id_as_evaluated: claude-fable-5.1-max
    score: 1500.64
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
      (effort: max; MODEL-123 max-effort rule). Rating 1500.64 [1484.88, 1516.41], 1574 votes,
      rank 2.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: anthropic/claude-fable-5-1#arena_sc_writing#72f0256d121f
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-text-style-control
      snapshot_ref: sha256:cf0d8c375155a60a2cc2ed34fa27600c376b34ce75cd6d7db33dc51f8c6caade
      cited_regions:
      - rows
  - benchmark_id: arena_sc_vision
    model_id_as_evaluated: claude-fable-5.1-max
    score: 1288.87
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: vision_style_control / overall, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset vision_style_control, category overall,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1288.87 [1276.57, 1301.16], 2701 votes,
      rank 11.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: anthropic/claude-fable-5-1#arena_sc_vision#87d43c380e00
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-160-arena-vision-style-control
      snapshot_ref: sha256:efd350d481ea9fcae6cff45c72c1226ed2df2a24aeece0839bfe4e0496368ffd
      cited_regions:
      - rows
  - benchmark_id: arena_webdev
    model_id_as_evaluated: claude-fable-5.1-max
    score: 1754.67
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-23'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: webdev / overall, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset webdev, category overall, leaderboard_publish_date
      2026-09-23; no style-controlled variant. Highest-effort row for the product (effort: max;
      MODEL-123 max-effort rule). Rating 1754.67 [1743.91, 1765.42], 4916 votes, rank 3.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
    id: anthropic/claude-fable-5-1#arena_webdev#00a93a57404d
    measured_by: independent_evaluator
    effort: null
    harness: null
    sources:
    - source_id: model-143-evidence-arena-webdev-json
      snapshot_ref: sha256:8c88f6e665fc8a5667d5b00b1a3ef24d70773f37f9f2fe917623c8c29895c5cf
      cited_regions:
      - rows
  - benchmark_id: frontiermath_tiers_1_3_v2
    model_id_as_evaluated: claude-fable-5-1_max
    score: 90.18
    unit: percent
    source_url: https://epoch.ai/frontiermath
    source_kind: independent_evaluator
    evidence_date: '2026-09-01'
    date_type: evaluated
    verified_at: '2026-09-24'
    benchmark_version: FrontierMath-Tiers-1-3-v2-Private (Epoch AI run)
    configuration: Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (frontiermath_tiers_1_3_v2.csv),
      read 2026-09-24. Run started 2026-09-01T18:38:24.000Z; effort max; highest-effort run
      for the model (MODEL-123 max-effort rule), newest on a tie. Standard error 1.77 points.
    limitations: Epoch AI data, CC BY 4.0.
    id: anthropic/claude-fable-5-1#frontiermath_tiers_1_3_v2#b8160fa3d3e6
    measured_by: independent_evaluator
    effort: max
    harness: null
    sources:
    - source_id: model-143-evidence-epoch-frontiermath-tiers-1-3-v2-csv
      snapshot_ref: sha256:5f2d315d4902f61209df86bb3a90b5dee0946624126c126708f64c90af13a93a
      cited_regions:
      - rows
  - benchmark_id: simpleqa_verified
    model_id_as_evaluated: claude-fable-5-1_max
    score: 70.8
    unit: percent
    source_url: https://epoch.ai/benchmarks/simpleqa-verified
    source_kind: independent_evaluator
    evidence_date: '2026-09-01'
    date_type: evaluated
    verified_at: '2026-09-24'
    benchmark_version: SimpleQA Verified, proportion correct, Epoch AI protocol with anti-abstention
      prompt
    configuration: Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (simpleqa_verified.csv),
      read 2026-09-24. Run started 2026-09-01T18:31:59.000Z; effort max; highest-effort run
      for the model (MODEL-123 max-effort rule), newest on a tie. Standard error 1.44 points.
    limitations: Epoch AI data, CC BY 4.0.
    id: anthropic/claude-fable-5-1#simpleqa_verified#92aeb614e7c4
    measured_by: independent_evaluator
    effort: max
    harness: null
    sources:
    - source_id: model-160-epoch-simpleqa-verified-csv
      snapshot_ref: sha256:cd774c02710b0ebf922eb880c96df454e8c5c4ca53d828a8da2a557a00df5275
      cited_regions:
      - rows
  - benchmark_id: frontiercode_v1_1
    model_id_as_evaluated: Fable 5.1
    score: 50.9
    unit: percent
    source_url: https://cognition.com/frontiercode
    source_kind: benchmark_author
    evidence_date: '2026-09-25'
    date_type: evaluated
    verified_at: '2026-09-24'
    benchmark_version: FrontierCode 1.1, main score (Mean@5)
    configuration: Board row as copied in Epoch AI's benchmark data (frontiercode_external.csv,
      https://epoch.ai/data/benchmark_data.zip), read 2026-09-24. Effort medium; the highest-effort
      row for the model (MODEL-123 max-effort rule). Harness claude-code.
    limitations: A live board's standing, dated by the day ModelSpec read Epoch AI's copy; the
      copy carries no per-row date. Epoch AI data, CC BY 4.0.
    id: anthropic/claude-fable-5-1#frontiercode_v1_1#2e7f4ee2e909
    measured_by: benchmark_author
    effort: medium
    harness: null
    sources:
    - source_id: model-160-frontiercode
      snapshot_ref: sha256:15fcd95ba12a8dc8c69096acfcef38a31e6834f37d9c4b84df1d7ea4bed87e1f
      cited_regions:
      - rows
  - benchmark_id: vending_bench_2
    model_id_as_evaluated: Claude Fable 5.1
    score: 5421.56
    unit: USD
    source_url: https://andonlabs.com/evals/vending-bench-2
    source_kind: benchmark_author
    evidence_date: '2026-09-25'
    date_type: evaluated
    verified_at: '2026-09-24'
    benchmark_version: Vending-Bench 2, mean final balance over 5 runs
    configuration: Board row as copied in Epoch AI's benchmark data (vending_bench_2_external.csv,
      https://epoch.ai/data/benchmark_data.zip), read 2026-09-24. Effort unknown; the highest-effort
      row for the model (MODEL-123 max-effort rule).
    limitations: A live board's standing, dated by the day ModelSpec read Epoch AI's copy; the
      copy carries no per-row date. Epoch AI data, CC BY 4.0.
    id: anthropic/claude-fable-5-1#vending_bench_2#1dbca369a383
    measured_by: benchmark_author
    effort: null
    harness: null
    sources:
    - source_id: model-160-vending-bench-2
      snapshot_ref: sha256:6d8ce9e4ae28f6ef99e0c6059b3cc96abf7fefafc7b90b65954fa6c758516731
      cited_regions:
      - rows
  - benchmark_id: terminal_bench_v4_0
    model_id_as_evaluated: Fable 5.1
    score: 57.88
    unit: percent
    source_url: https://www.tbench.ai/leaderboard/terminal-bench/4.0
    source_kind: benchmark_author
    evidence_date: '2026-09-01'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: Terminal-Bench 4.0
    configuration: 'tbench.ai leaderboard row read 2026-09-24: agent Claude Code (Anthropic),
      reasoning effort max, 330 trials, accuracy 57.88 ± 3.76 (95% CI). The board''s row date
      is the evidence date. Highest-effort row for the model, best agent on a tie.'
    limitations: The agent harness differs between rows; compare rows with the same agent.
    id: anthropic/claude-fable-5-1#terminal_bench_v4_0#18b78bc593ca
    measured_by: benchmark_author
    effort: max
    harness: unregistered
    sources:
    - source_id: model-143-evidence-terminal-bench-4-0-json
      snapshot_ref: sha256:660c5a0fbc79f54671c60e88cced246abad7b9b9935e1db6d63dc2fe30bb3204
      cited_regions:
      - rows
  - benchmark_id: hle
    model_id_as_evaluated: Fable 5.1 (xhigh)
    score: 46.5
    unit: percent
    source_url: https://labs.scale.com/leaderboard/humanitys_last_exam
    source_kind: independent_evaluator
    evidence_date: '2026-09-24'
    date_type: evaluated
    verified_at: '2026-09-24'
    benchmark_version: Humanity's Last Exam, Scale Labs leaderboard
    configuration: Scale Labs leaderboard entry read 2026-09-24; entry created 2026-09-03T18:22:21.000Z;
      effort xhigh; ±2 (95% CI).
    limitations: 'Potential contamination warning: This model was evaluated after the public
      release of HLE, allowing model builder access to the prompts and solutions.'
    id: anthropic/claude-fable-5-1#hle#e5aeb03e5dac
    measured_by: independent_evaluator
    effort: xhigh
    harness: null
    sources:
    - source_id: model-143-evidence-scale-hle-json
      snapshot_ref: sha256:c7e558ff927cc7aae1ec9d39ba22de7b5db667674ea408c772002222c11818bd
      cited_regions:
      - rows
  - benchmark_id: cursorbench_4
    model_id_as_evaluated: Fable 5.1 (max)
    score: 51.8
    unit: percent
    source_url: https://cursor.com/cursorbench
    source_kind: benchmark_author
    evidence_date: '2026-09-25'
    date_type: evaluated
    verified_at: '2026-09-24'
    benchmark_version: CursorBench 4.0
    configuration: Cursor's CursorBench 4.0 board read 2026-09-24 (tasks updated 2026-09-10
      per its changelog); the board states no row date, so the reading is dated by the observation.
      Highest-effort row (max); $17.28 a task.
    limitations: Runs only in Cursor's production agent harness.
    id: anthropic/claude-fable-5-1#cursorbench_4#d30f1a858bf1
    measured_by: benchmark_author
    effort: max
    harness: null
    sources:
    - source_id: model-160-cursorbench
      snapshot_ref: sha256:8f663ca9611104e24712ac2c6e42e0c7444850db6ce29d3d17a046b1d4bd973b
      cited_regions:
      - rows
  - benchmark_id: healthbench_professional
    model_id_as_evaluated: Claude Fable 5.1
    score: 62.1
    unit: percent
    source_url: https://www.anthropic.com/claude-opus-5-5-system-card
    source_kind: provider_self_report
    evidence_date: '2026-09-22'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: HealthBench Professional, length-adjusted
    configuration: 'Claude Opus 5.5 System Card (published 2026-09-22), Table 8.1.A and section
      8.15.2: length-adjusted HealthBench Professional score (the method in the HealthBench
      Professional paper). Adaptive thinking at max effort, averaged over five trials, Claude
      Opus 4.8 as the grader model, no tools. Anthropic''s own models only; the table''s GPT-6
      Astra column is a competitor''s score and is not attached.'
    limitations: Graded by the provider's own model; not comparable across graders.
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
  models_dev_url: https://models.dev/anthropic
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
  - source_id: model-143-anthropic-claude-fable-5-1
    snapshot_ref: sha256:08acdc753711be9f58e666880119eb8b9e20d9406df3d5b996564db2b0e0a37b
    cited_regions:
    - model-spec
  - source_id: model-143-anthropic-models-overview
    snapshot_ref: sha256:081fd4411b01088963ae62e43b378ba3c708843c5f553c277371f014a02bc65f
    cited_regions:
    - audit
  - source_id: model-143-anthropic-structured-outputs
    snapshot_ref: sha256:b93fe8ddc691cd8f9a022aacc8c3adabf38c9e8ed215ae955d61939ee64abaf9
    cited_regions:
    - audit
  - source_id: model-143-anthropic-streaming
    snapshot_ref: sha256:cdc7449de7d6829e2f611641ce1fcec68564814fd54ab3398c559189073b6f69
    cited_regions:
    - audit
  - source_id: model-143-anthropic-commercial-terms
    snapshot_ref: sha256:cfb59d90c8b31ffb9c1e3a0b95bff416c7b3d19218eb3c15e8d0169ea36caeca
    cited_regions:
    - audit
- facet: model.input_modalities
  value:
  - text
  - image
  - document
  state: known
  sources:
  - source_id: model-143-anthropic-claude-fable-5-1
    snapshot_ref: sha256:08acdc753711be9f58e666880119eb8b9e20d9406df3d5b996564db2b0e0a37b
    cited_regions:
    - model-spec
  - source_id: model-143-anthropic-models-overview
    snapshot_ref: sha256:081fd4411b01088963ae62e43b378ba3c708843c5f553c277371f014a02bc65f
    cited_regions:
    - audit
  - source_id: model-143-anthropic-structured-outputs
    snapshot_ref: sha256:b93fe8ddc691cd8f9a022aacc8c3adabf38c9e8ed215ae955d61939ee64abaf9
    cited_regions:
    - audit
  - source_id: model-143-anthropic-streaming
    snapshot_ref: sha256:cdc7449de7d6829e2f611641ce1fcec68564814fd54ab3398c559189073b6f69
    cited_regions:
    - audit
  - source_id: model-143-anthropic-commercial-terms
    snapshot_ref: sha256:cfb59d90c8b31ffb9c1e3a0b95bff416c7b3d19218eb3c15e8d0169ea36caeca
    cited_regions:
    - audit
- facet: model.output_modalities
  value:
  - text
  state: known
  sources:
  - source_id: model-143-anthropic-claude-fable-5-1
    snapshot_ref: sha256:08acdc753711be9f58e666880119eb8b9e20d9406df3d5b996564db2b0e0a37b
    cited_regions:
    - model-spec
  - source_id: model-143-anthropic-models-overview
    snapshot_ref: sha256:081fd4411b01088963ae62e43b378ba3c708843c5f553c277371f014a02bc65f
    cited_regions:
    - audit
  - source_id: model-143-anthropic-structured-outputs
    snapshot_ref: sha256:b93fe8ddc691cd8f9a022aacc8c3adabf38c9e8ed215ae955d61939ee64abaf9
    cited_regions:
    - audit
  - source_id: model-143-anthropic-streaming
    snapshot_ref: sha256:cdc7449de7d6829e2f611641ce1fcec68564814fd54ab3398c559189073b6f69
    cited_regions:
    - audit
  - source_id: model-143-anthropic-commercial-terms
    snapshot_ref: sha256:cfb59d90c8b31ffb9c1e3a0b95bff416c7b3d19218eb3c15e8d0169ea36caeca
    cited_regions:
    - audit
- facet: model.context_window
  value: 1000000
  state: known
  sources:
  - source_id: model-143-anthropic-claude-fable-5-1
    snapshot_ref: sha256:08acdc753711be9f58e666880119eb8b9e20d9406df3d5b996564db2b0e0a37b
    cited_regions:
    - model-spec
  - source_id: model-143-anthropic-models-overview
    snapshot_ref: sha256:081fd4411b01088963ae62e43b378ba3c708843c5f553c277371f014a02bc65f
    cited_regions:
    - audit
  - source_id: model-143-anthropic-structured-outputs
    snapshot_ref: sha256:b93fe8ddc691cd8f9a022aacc8c3adabf38c9e8ed215ae955d61939ee64abaf9
    cited_regions:
    - audit
  - source_id: model-143-anthropic-streaming
    snapshot_ref: sha256:cdc7449de7d6829e2f611641ce1fcec68564814fd54ab3398c559189073b6f69
    cited_regions:
    - audit
  - source_id: model-143-anthropic-commercial-terms
    snapshot_ref: sha256:cfb59d90c8b31ffb9c1e3a0b95bff416c7b3d19218eb3c15e8d0169ea36caeca
    cited_regions:
    - audit
- facet: model.max_output_tokens
  value: 128000
  state: known
  sources:
  - source_id: model-143-anthropic-claude-fable-5-1
    snapshot_ref: sha256:08acdc753711be9f58e666880119eb8b9e20d9406df3d5b996564db2b0e0a37b
    cited_regions:
    - model-spec
  - source_id: model-143-anthropic-models-overview
    snapshot_ref: sha256:081fd4411b01088963ae62e43b378ba3c708843c5f553c277371f014a02bc65f
    cited_regions:
    - audit
  - source_id: model-143-anthropic-structured-outputs
    snapshot_ref: sha256:b93fe8ddc691cd8f9a022aacc8c3adabf38c9e8ed215ae955d61939ee64abaf9
    cited_regions:
    - audit
  - source_id: model-143-anthropic-streaming
    snapshot_ref: sha256:cdc7449de7d6829e2f611641ce1fcec68564814fd54ab3398c559189073b6f69
    cited_regions:
    - audit
  - source_id: model-143-anthropic-commercial-terms
    snapshot_ref: sha256:cfb59d90c8b31ffb9c1e3a0b95bff416c7b3d19218eb3c15e8d0169ea36caeca
    cited_regions:
    - audit
- facet: model.weights_openness
  value: closed_weights
  state: known
  sources:
  - source_id: model-143-anthropic-claude-fable-5-1
    snapshot_ref: sha256:08acdc753711be9f58e666880119eb8b9e20d9406df3d5b996564db2b0e0a37b
    cited_regions:
    - model-spec
  - source_id: model-143-anthropic-models-overview
    snapshot_ref: sha256:081fd4411b01088963ae62e43b378ba3c708843c5f553c277371f014a02bc65f
    cited_regions:
    - audit
  - source_id: model-143-anthropic-structured-outputs
    snapshot_ref: sha256:b93fe8ddc691cd8f9a022aacc8c3adabf38c9e8ed215ae955d61939ee64abaf9
    cited_regions:
    - audit
  - source_id: model-143-anthropic-streaming
    snapshot_ref: sha256:cdc7449de7d6829e2f611641ce1fcec68564814fd54ab3398c559189073b6f69
    cited_regions:
    - audit
  - source_id: model-143-anthropic-commercial-terms
    snapshot_ref: sha256:cfb59d90c8b31ffb9c1e3a0b95bff416c7b3d19218eb3c15e8d0169ea36caeca
    cited_regions:
    - audit
- facet: licence.commercial_use
  value: permitted_with_conditions
  state: known
  sources:
  - source_id: model-143-anthropic-claude-fable-5-1
    snapshot_ref: sha256:08acdc753711be9f58e666880119eb8b9e20d9406df3d5b996564db2b0e0a37b
    cited_regions:
    - model-spec
  - source_id: model-143-anthropic-commercial-terms
    snapshot_ref: sha256:cfb59d90c8b31ffb9c1e3a0b95bff416c7b3d19218eb3c15e8d0169ea36caeca
    cited_regions:
    - audit
- facet: licence.user_cap
  value: unbounded
  state: known
  sources:
  - source_id: model-143-anthropic-claude-fable-5-1
    snapshot_ref: sha256:08acdc753711be9f58e666880119eb8b9e20d9406df3d5b996564db2b0e0a37b
    cited_regions:
    - model-spec
  - source_id: model-143-anthropic-commercial-terms
    snapshot_ref: sha256:cfb59d90c8b31ffb9c1e3a0b95bff416c7b3d19218eb3c15e8d0169ea36caeca
    cited_regions:
    - audit
- facet: licence.output_training
  value: restricted
  state: known
  sources:
  - source_id: model-143-anthropic-claude-fable-5-1
    snapshot_ref: sha256:08acdc753711be9f58e666880119eb8b9e20d9406df3d5b996564db2b0e0a37b
    cited_regions:
    - model-spec
  - source_id: model-143-anthropic-commercial-terms
    snapshot_ref: sha256:cfb59d90c8b31ffb9c1e3a0b95bff416c7b3d19218eb3c15e8d0169ea36caeca
    cited_regions:
    - audit
- facet: licence.fine_tuning
  value: prohibited
  state: known
  sources:
  - source_id: model-143-anthropic-claude-fable-5-1
    snapshot_ref: sha256:08acdc753711be9f58e666880119eb8b9e20d9406df3d5b996564db2b0e0a37b
    cited_regions:
    - model-spec
  - source_id: model-143-anthropic-commercial-terms
    snapshot_ref: sha256:cfb59d90c8b31ffb9c1e3a0b95bff416c7b3d19218eb3c15e8d0169ea36caeca
    cited_regions:
    - audit
- facet: origin.lab_jurisdiction
  value:
  - US
  state: known
  sources:
  - source_id: model-143-anthropic-claude-fable-5-1
    snapshot_ref: sha256:08acdc753711be9f58e666880119eb8b9e20d9406df3d5b996564db2b0e0a37b
    cited_regions:
    - model-spec
  - source_id: model-143-anthropic-models-overview
    snapshot_ref: sha256:081fd4411b01088963ae62e43b378ba3c708843c5f553c277371f014a02bc65f
    cited_regions:
    - audit
  - source_id: model-143-anthropic-structured-outputs
    snapshot_ref: sha256:b93fe8ddc691cd8f9a022aacc8c3adabf38c9e8ed215ae955d61939ee64abaf9
    cited_regions:
    - audit
  - source_id: model-143-anthropic-streaming
    snapshot_ref: sha256:cdc7449de7d6829e2f611641ce1fcec68564814fd54ab3398c559189073b6f69
    cited_regions:
    - audit
  - source_id: model-143-anthropic-commercial-terms
    snapshot_ref: sha256:cfb59d90c8b31ffb9c1e3a0b95bff416c7b3d19218eb3c15e8d0169ea36caeca
    cited_regions:
    - audit
- facet: origin.base_lineage
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-anthropic-claude-fable-5-1
    snapshot_ref: sha256:08acdc753711be9f58e666880119eb8b9e20d9406df3d5b996564db2b0e0a37b
    cited_regions:
    - model-spec
  - source_id: model-143-anthropic-models-overview
    snapshot_ref: sha256:081fd4411b01088963ae62e43b378ba3c708843c5f553c277371f014a02bc65f
    cited_regions:
    - audit
  - source_id: model-143-anthropic-structured-outputs
    snapshot_ref: sha256:b93fe8ddc691cd8f9a022aacc8c3adabf38c9e8ed215ae955d61939ee64abaf9
    cited_regions:
    - audit
  - source_id: model-143-anthropic-streaming
    snapshot_ref: sha256:cdc7449de7d6829e2f611641ce1fcec68564814fd54ab3398c559189073b6f69
    cited_regions:
    - audit
  - source_id: model-143-anthropic-commercial-terms
    snapshot_ref: sha256:cfb59d90c8b31ffb9c1e3a0b95bff416c7b3d19218eb3c15e8d0169ea36caeca
    cited_regions:
    - audit
  checked_sources:
  - model-143-anthropic-claude-fable-5-1
  - model-143-anthropic-models-overview
  - model-143-anthropic-structured-outputs
  - model-143-anthropic-streaming
  - model-143-anthropic-commercial-terms
- facet: origin.weights_hosting
  value: null
  state: not_disclosed
  sources:
  - source_id: model-143-anthropic-claude-fable-5-1
    snapshot_ref: sha256:08acdc753711be9f58e666880119eb8b9e20d9406df3d5b996564db2b0e0a37b
    cited_regions:
    - model-spec
  - source_id: model-143-anthropic-models-overview
    snapshot_ref: sha256:081fd4411b01088963ae62e43b378ba3c708843c5f553c277371f014a02bc65f
    cited_regions:
    - audit
  - source_id: model-143-anthropic-structured-outputs
    snapshot_ref: sha256:b93fe8ddc691cd8f9a022aacc8c3adabf38c9e8ed215ae955d61939ee64abaf9
    cited_regions:
    - audit
  - source_id: model-143-anthropic-streaming
    snapshot_ref: sha256:cdc7449de7d6829e2f611641ce1fcec68564814fd54ab3398c559189073b6f69
    cited_regions:
    - audit
  - source_id: model-143-anthropic-commercial-terms
    snapshot_ref: sha256:cfb59d90c8b31ffb9c1e3a0b95bff416c7b3d19218eb3c15e8d0169ea36caeca
    cited_regions:
    - audit
  checked_sources:
  - model-143-anthropic-claude-fable-5-1
  - model-143-anthropic-models-overview
  - model-143-anthropic-structured-outputs
  - model-143-anthropic-streaming
  - model-143-anthropic-commercial-terms
- facet: model.release_date
  value: '2026-09-01'
  state: known
  sources:
  - source_id: model-143-anthropic-claude-fable-5-1
    snapshot_ref: sha256:08acdc753711be9f58e666880119eb8b9e20d9406df3d5b996564db2b0e0a37b
    cited_regions:
    - model-spec
  - source_id: model-143-anthropic-models-overview
    snapshot_ref: sha256:081fd4411b01088963ae62e43b378ba3c708843c5f553c277371f014a02bc65f
    cited_regions:
    - audit
  - source_id: model-143-anthropic-structured-outputs
    snapshot_ref: sha256:b93fe8ddc691cd8f9a022aacc8c3adabf38c9e8ed215ae955d61939ee64abaf9
    cited_regions:
    - audit
  - source_id: model-143-anthropic-streaming
    snapshot_ref: sha256:cdc7449de7d6829e2f611641ce1fcec68564814fd54ab3398c559189073b6f69
    cited_regions:
    - audit
  - source_id: model-143-anthropic-commercial-terms
    snapshot_ref: sha256:cfb59d90c8b31ffb9c1e3a0b95bff416c7b3d19218eb3c15e8d0169ea36caeca
    cited_regions:
    - audit
- facet: model.lifecycle
  value: active
  state: known
  sources:
  - source_id: model-143-anthropic-claude-fable-5-1
    snapshot_ref: sha256:08acdc753711be9f58e666880119eb8b9e20d9406df3d5b996564db2b0e0a37b
    cited_regions:
    - model-spec
  - source_id: model-143-anthropic-models-overview
    snapshot_ref: sha256:081fd4411b01088963ae62e43b378ba3c708843c5f553c277371f014a02bc65f
    cited_regions:
    - audit
  - source_id: model-143-anthropic-structured-outputs
    snapshot_ref: sha256:b93fe8ddc691cd8f9a022aacc8c3adabf38c9e8ed215ae955d61939ee64abaf9
    cited_regions:
    - audit
  - source_id: model-143-anthropic-streaming
    snapshot_ref: sha256:cdc7449de7d6829e2f611641ce1fcec68564814fd54ab3398c559189073b6f69
    cited_regions:
    - audit
  - source_id: model-143-anthropic-commercial-terms
    snapshot_ref: sha256:cfb59d90c8b31ffb9c1e3a0b95bff416c7b3d19218eb3c15e8d0169ea36caeca
    cited_regions:
    - audit
- facet: feature.tool_calling
  value: true
  state: known
  sources:
  - source_id: model-143-anthropic-claude-fable-5-1
    snapshot_ref: sha256:08acdc753711be9f58e666880119eb8b9e20d9406df3d5b996564db2b0e0a37b
    cited_regions:
    - model-spec
  - source_id: model-143-anthropic-models-overview
    snapshot_ref: sha256:081fd4411b01088963ae62e43b378ba3c708843c5f553c277371f014a02bc65f
    cited_regions:
    - audit
  - source_id: model-143-anthropic-structured-outputs
    snapshot_ref: sha256:b93fe8ddc691cd8f9a022aacc8c3adabf38c9e8ed215ae955d61939ee64abaf9
    cited_regions:
    - audit
  - source_id: model-143-anthropic-streaming
    snapshot_ref: sha256:cdc7449de7d6829e2f611641ce1fcec68564814fd54ab3398c559189073b6f69
    cited_regions:
    - audit
  - source_id: model-143-anthropic-commercial-terms
    snapshot_ref: sha256:cfb59d90c8b31ffb9c1e3a0b95bff416c7b3d19218eb3c15e8d0169ea36caeca
    cited_regions:
    - audit
- facet: feature.structured_output
  value: true
  state: known
  sources:
  - source_id: model-143-anthropic-claude-fable-5-1
    snapshot_ref: sha256:08acdc753711be9f58e666880119eb8b9e20d9406df3d5b996564db2b0e0a37b
    cited_regions:
    - model-spec
  - source_id: model-143-anthropic-models-overview
    snapshot_ref: sha256:081fd4411b01088963ae62e43b378ba3c708843c5f553c277371f014a02bc65f
    cited_regions:
    - audit
  - source_id: model-143-anthropic-structured-outputs
    snapshot_ref: sha256:b93fe8ddc691cd8f9a022aacc8c3adabf38c9e8ed215ae955d61939ee64abaf9
    cited_regions:
    - audit
  - source_id: model-143-anthropic-streaming
    snapshot_ref: sha256:cdc7449de7d6829e2f611641ce1fcec68564814fd54ab3398c559189073b6f69
    cited_regions:
    - audit
  - source_id: model-143-anthropic-commercial-terms
    snapshot_ref: sha256:cfb59d90c8b31ffb9c1e3a0b95bff416c7b3d19218eb3c15e8d0169ea36caeca
    cited_regions:
    - audit
- facet: feature.effort_controls
  value: true
  state: known
  sources:
  - source_id: model-143-anthropic-claude-fable-5-1
    snapshot_ref: sha256:08acdc753711be9f58e666880119eb8b9e20d9406df3d5b996564db2b0e0a37b
    cited_regions:
    - model-spec
  - source_id: model-143-anthropic-models-overview
    snapshot_ref: sha256:081fd4411b01088963ae62e43b378ba3c708843c5f553c277371f014a02bc65f
    cited_regions:
    - audit
  - source_id: model-143-anthropic-structured-outputs
    snapshot_ref: sha256:b93fe8ddc691cd8f9a022aacc8c3adabf38c9e8ed215ae955d61939ee64abaf9
    cited_regions:
    - audit
  - source_id: model-143-anthropic-streaming
    snapshot_ref: sha256:cdc7449de7d6829e2f611641ce1fcec68564814fd54ab3398c559189073b6f69
    cited_regions:
    - audit
  - source_id: model-143-anthropic-commercial-terms
    snapshot_ref: sha256:cfb59d90c8b31ffb9c1e3a0b95bff416c7b3d19218eb3c15e8d0169ea36caeca
    cited_regions:
    - audit
- facet: feature.batch
  value: true
  state: known
  sources:
  - source_id: model-143-anthropic-claude-fable-5-1
    snapshot_ref: sha256:08acdc753711be9f58e666880119eb8b9e20d9406df3d5b996564db2b0e0a37b
    cited_regions:
    - model-spec
  - source_id: model-143-anthropic-models-overview
    snapshot_ref: sha256:081fd4411b01088963ae62e43b378ba3c708843c5f553c277371f014a02bc65f
    cited_regions:
    - audit
  - source_id: model-143-anthropic-structured-outputs
    snapshot_ref: sha256:b93fe8ddc691cd8f9a022aacc8c3adabf38c9e8ed215ae955d61939ee64abaf9
    cited_regions:
    - audit
  - source_id: model-143-anthropic-streaming
    snapshot_ref: sha256:cdc7449de7d6829e2f611641ce1fcec68564814fd54ab3398c559189073b6f69
    cited_regions:
    - audit
  - source_id: model-143-anthropic-commercial-terms
    snapshot_ref: sha256:cfb59d90c8b31ffb9c1e3a0b95bff416c7b3d19218eb3c15e8d0169ea36caeca
    cited_regions:
    - audit
- facet: feature.streaming
  value: true
  state: known
  sources:
  - source_id: model-143-anthropic-claude-fable-5-1
    snapshot_ref: sha256:08acdc753711be9f58e666880119eb8b9e20d9406df3d5b996564db2b0e0a37b
    cited_regions:
    - model-spec
  - source_id: model-143-anthropic-models-overview
    snapshot_ref: sha256:081fd4411b01088963ae62e43b378ba3c708843c5f553c277371f014a02bc65f
    cited_regions:
    - audit
  - source_id: model-143-anthropic-structured-outputs
    snapshot_ref: sha256:b93fe8ddc691cd8f9a022aacc8c3adabf38c9e8ed215ae955d61939ee64abaf9
    cited_regions:
    - audit
  - source_id: model-143-anthropic-streaming
    snapshot_ref: sha256:cdc7449de7d6829e2f611641ce1fcec68564814fd54ab3398c559189073b6f69
    cited_regions:
    - audit
  - source_id: model-143-anthropic-commercial-terms
    snapshot_ref: sha256:cfb59d90c8b31ffb9c1e3a0b95bff416c7b3d19218eb3c15e8d0169ea36caeca
    cited_regions:
    - audit
card_schema_version: '3.0'
card_author: models.dev-seeder
card_created: '2026-04-05'
card_updated: '2026-09-26'
authoring_guide:
  applies_to:
    model_id: anthropic/claude-fable-5-1
    version: claude-fable-5-1
  as_of: '2026-09-15'
  status: current
  sections:
    prompt_shape:
    - text: Prompts written for Claude Fable 5 should work on 5.1 without changes.
      sources:
      - url: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1
        title: Prompting Claude Fable 5.1
        accessed: '2026-09-15'
        kind: provider-guidance
    - text: May add unrequested fixes or extra tests; say explicitly what to leave out of the change.
      sources:
      - url: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1
        title: Prompting Claude Fable 5.1
        accessed: '2026-09-15'
        kind: provider-guidance
    - text: Summaries can reproduce source text unmarked; include one complete example of a correct response.
      sources:
      - url: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1
        title: Prompting Claude Fable 5.1
        accessed: '2026-09-15'
        kind: provider-guidance
    system_message:
    - text: Send per-turn reminders as turn-scoped system messages rather than editing earlier turns.
      sources:
      - url: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1
        title: Prompting Claude Fable 5.1
        accessed: '2026-09-15'
        kind: provider-guidance
    - text: Remove prompt lines that suppress progress narration before adding update instructions.
      sources:
      - url: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1
        title: Prompting Claude Fable 5.1
        accessed: '2026-09-15'
        kind: provider-guidance
    - text: If the product hides tool output from the user, tell the model so it does not run commands
        just to show output.
      sources:
      - url: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1
        title: Prompting Claude Fable 5.1
        accessed: '2026-09-15'
        kind: provider-guidance
    reasoning_and_tools:
    - text: Thinking is always on; effort is the primary cost/latency control. Re-run an effort sweep,
        since level names differ across models.
      sources:
      - url: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1
        title: Prompting Claude Fable 5.1
        accessed: '2026-09-15'
        kind: provider-guidance
      - url: https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices
        title: Prompting best practices
        accessed: '2026-09-15'
        kind: provider-guidance
    - text: At low effort it searches less and answers from memory more; raise effort for those turns
        or add a search nudge.
      sources:
      - url: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1
        title: Prompting Claude Fable 5.1
        accessed: '2026-09-15'
        kind: provider-guidance
    - text: In coding and computer-use loops it may make one tool call per turn; append a batching nudge
        after each round of tool results.
      sources:
      - url: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1
        title: Prompting Claude Fable 5.1
        accessed: '2026-09-15'
        kind: provider-guidance
      - url: https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices
        title: Prompting best practices
        accessed: '2026-09-15'
        kind: provider-guidance
    - text: Keep history append-only and return thinking blocks unchanged; edited earlier turns can make
        requests fail.
      sources:
      - url: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1
        title: Prompting Claude Fable 5.1
        accessed: '2026-09-15'
        kind: provider-guidance
      - url: https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices
        title: Prompting best practices
        accessed: '2026-09-15'
        kind: provider-guidance
    - text: For client-side compaction, state what the summary must preserve.
      sources:
      - url: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1
        title: Prompting Claude Fable 5.1
        accessed: '2026-09-15'
        kind: provider-guidance
    - text: Let the lead agent keep working while subagents run instead of forcing it to wait.
      sources:
      - url: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1
        title: Prompting Claude Fable 5.1
        accessed: '2026-09-15'
        kind: provider-guidance
    formatting:
    - text: Formats less than earlier models; remove anti-formatting rules or replace them with a rule
        for when structure helps.
      sources:
      - url: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1
        title: Prompting Claude Fable 5.1
        accessed: '2026-09-15'
        kind: provider-guidance
      - url: https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices
        title: Prompting best practices
        accessed: '2026-09-15'
        kind: provider-guidance
    - text: Prose can be denser than Fable 5; an instruction defining mannered prose helps.
      sources:
      - url: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1
        title: Prompting Claude Fable 5.1
        accessed: '2026-09-15'
        kind: provider-guidance
    failure_modes:
    - text: May end a turn describing next steps, or ask permission for work already requested; an autonomy
        instruction mitigates this.
      sources:
      - url: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1
        title: Prompting Claude Fable 5.1
        accessed: '2026-09-15'
        kind: provider-guidance
    - text: Safety classifiers can return a refusal on benign coding requests, more often with compile-check
        phrasing, lesser-known languages or base64 tool output.
      sources:
      - url: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1
        title: Prompting Claude Fable 5.1
        accessed: '2026-09-15'
        kind: provider-guidance
    - text: Tends to rewrite whole files for small edits, costing output tokens; ask for targeted edits.
      sources:
      - url: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1
        title: Prompting Claude Fable 5.1
        accessed: '2026-09-15'
        kind: provider-guidance
    - text: At xhigh and max it may draft a long deliverable in thinking then write it again; run at high
        or leave max_tokens headroom.
      sources:
      - url: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1
        title: Prompting Claude Fable 5.1
        accessed: '2026-09-15'
        kind: provider-guidance
    retry_advice:
    - text: For a false-positive refusal, rephrase compile-check questions as a request to find bugs rather
        than resending unchanged.
      sources:
      - url: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1
        title: Prompting Claude Fable 5.1
        accessed: '2026-09-15'
        kind: provider-guidance
    - text: If requests fail as bound to a different conversation, find and remove the harness edits to
        earlier turns.
      sources:
      - url: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1
        title: Prompting Claude Fable 5.1
        accessed: '2026-09-15'
        kind: provider-guidance
---

# Claude Fable 5.1

Claude Fable 5.1 is a Llm Reasoning model from Anthropic. Part of the claude-fable family. Knowledge cutoff: 2026-06.

## Key Features
- Extended reasoning / chain-of-thought
- Function calling / tool use
- Structured output (JSON mode)
- File/image attachments
