---
model_id: openai/gpt-6-astra
display_name: GPT-6 Astra
provider: openai
provider_display: OpenAI
family: gpt-astra
version: gpt-6-astra
release_date: '2026-09-04'
last_updated: '2026-09-11'
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
  license_type: proprietary
  license_url: https://openai.com/policies
  tos_url: https://openai.com/policies/terms-of-use
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
    max_input_tokens: 922000
    max_output_tokens: 128000
    context_window: 1050000
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
    computer_use: true
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
    web_browsing: true
    file_system_access: false
    code_execution: false
    long_running_tasks: false
    memory_management: false
    self_delegation: false
cost:
  input: 10.0
  output: 50.0
  reasoning: null
  cache_read: 1.0
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
  note: OpenAI Standard API pricing on the 2026-09-03 launch page. Fast mode is 2x
    Standard price for up to 2x speed. Competitor price columns were not taken.
availability:
  primary_provider:
    name: OpenAI API
    platform_url: https://platform.openai.com/
    api_endpoint: https://api.openai.com/v1
    npm_package: ''
    env_vars:
    - OPENAI_API_KEY
    model_id_on_platform: gpt-6-astra
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
    available: true
    model_id: ''
    url: https://aws.amazon.com/bedrock/
    fine_tuning: false
    gated: false
    regions: []
    notes: Named on the 2026-09-03 launch page. Platform model id not published there.
  azure_ai_foundry:
    available: true
    model_id: ''
    url: https://ai.azure.com/
    fine_tuning: false
    gated: false
    regions: []
    notes: Named on the 2026-09-03 launch page. Platform model id not published there.
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
    available: true
    model_id: gpt-6-astra
    url: https://chat.openai.com/
    fine_tuning: false
    gated: false
    regions: []
    notes: Plus, Pro, Business, Enterprise per the launch page. Enterprise off by
      default. Pro/Business/Enterprise also get GPT-6 Astra Pro.
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
  - benchmark_id: aa_briefcase
    model_id_as_evaluated: GPT-6 Astra (max)
    score: 53.0
    unit: normalized Elo percent
    source_url: https://artificialanalysis.ai/articles/artificial-analysis-intelligence-index-v4-2
    source_kind: independent_evaluator
    evidence_date: '2026-09-04'
    date_type: published
    verified_at: '2026-09-08'
    benchmark_version: AA-Briefcase / AA v4.2
    configuration: AA v4.2 published comparison; both models labelled max; model-dependent
      reasoning is not compute-matched. Values read from fixed release chart, not
      live tables. Undisclosed code/prompt pins are not inferred.
    limitations: ''
  - benchmark_id: aa_lcr
    model_id_as_evaluated: GPT-6 Astra (max)
    score: 81.0
    unit: percent
    source_url: https://artificialanalysis.ai/articles/artificial-analysis-intelligence-index-v4-2
    source_kind: independent_evaluator
    evidence_date: '2026-09-04'
    date_type: published
    verified_at: '2026-09-08'
    benchmark_version: AA-LCR v1.1 / AA v4.2
    configuration: AA v4.2 published comparison; both models labelled max; model-dependent
      reasoning is not compute-matched. Values read from fixed release chart, not
      live tables. Undisclosed code/prompt pins are not inferred.
    limitations: ''
  - benchmark_id: automationbench_aa
    model_id_as_evaluated: GPT-6 Astra (max)
    score: 68.5
    unit: percent
    source_url: https://artificialanalysis.ai/articles/artificial-analysis-intelligence-index-v4-3
    source_kind: independent_evaluator
    evidence_date: '2026-09-07'
    date_type: published
    verified_at: '2026-09-08'
    benchmark_version: AutomationBench 1.0.6 / AA held-out split
    configuration: 'AA v4.3: private 657-task split; single run; 50-turn cap; objective-credit
      score with guardrail-zeroing; both models at max reasoning (not equal compute).'
    limitations: ''
  - benchmark_id: critpt
    model_id_as_evaluated: GPT-6 Astra (max)
    score: 32.0
    unit: percent
    source_url: https://artificialanalysis.ai/articles/artificial-analysis-intelligence-index-v4-2
    source_kind: independent_evaluator
    evidence_date: '2026-09-04'
    date_type: published
    verified_at: '2026-09-08'
    benchmark_version: CritPt / AA v4.2 implementation
    configuration: AA v4.2 published comparison; both models labelled max; model-dependent
      reasoning is not compute-matched. Values read from fixed release chart, not
      live tables. Undisclosed code/prompt pins are not inferred.
    limitations: ''
  - benchmark_id: gdp_pdf_aa
    model_id_as_evaluated: GPT-6 Astra (max)
    score: 33.0
    unit: percent
    source_url: https://artificialanalysis.ai/articles/artificial-analysis-intelligence-index-v4-2
    source_kind: independent_evaluator
    evidence_date: '2026-09-04'
    date_type: published
    verified_at: '2026-09-08'
    benchmark_version: GDP.pdf / AA v4.2 implementation
    configuration: AA v4.2 published comparison; both models labelled max; model-dependent
      reasoning is not compute-matched. Values read from fixed release chart, not
      live tables. Undisclosed code/prompt pins are not inferred.
    limitations: ''
  - benchmark_id: gdpval_aa
    model_id_as_evaluated: GPT-6 Astra (max)
    score: 54.0
    unit: normalized Elo percent
    source_url: https://artificialanalysis.ai/articles/artificial-analysis-intelligence-index-v4-2
    source_kind: independent_evaluator
    evidence_date: '2026-09-04'
    date_type: published
    verified_at: '2026-09-08'
    benchmark_version: GDPval-AA v2 / AA v4.2
    configuration: AA v4.2 published comparison; both models labelled max; model-dependent
      reasoning is not compute-matched. Values read from fixed release chart, not
      live tables. Undisclosed code/prompt pins are not inferred.
    limitations: ''
  - benchmark_id: scicode
    model_id_as_evaluated: GPT-6 Astra (max)
    score: 56.0
    unit: percent
    source_url: https://artificialanalysis.ai/articles/artificial-analysis-intelligence-index-v4-2
    source_kind: independent_evaluator
    evidence_date: '2026-09-04'
    date_type: published
    verified_at: '2026-09-08'
    benchmark_version: SciCode / AA v4.2 implementation
    configuration: AA v4.2 published comparison; both models labelled max; model-dependent
      reasoning is not compute-matched. Values read from fixed release chart, not
      live tables. Undisclosed code/prompt pins are not inferred.
    limitations: ''
  - benchmark_id: gpqa_diamond
    model_id_as_evaluated: GPT-6 Astra (max)
    score: 96.0
    unit: percent
    source_url: https://openai.com/index/gpt-6-astra/
    source_kind: provider_self_report
    evidence_date: '2026-09-03'
    date_type: published
    verified_at: '2026-09-09'
    benchmark_version: GPQA Diamond
    configuration: 'Launch page: evaluation scores are the maximum at any effort.
      Competitor columns were not taken. Publication date is OpenAI''s own dating
      of this article (Research, Sep 3, 2026) on openai.com/index/gpt-5-6/.'
    limitations: ''
  - benchmark_id: terminal_bench_v4_0
    model_id_as_evaluated: GPT-6 Astra
    score: 57.9
    unit: percent
    source_url: https://openai.com/index/gpt-6-astra/
    source_kind: provider_self_report
    evidence_date: '2026-09-03'
    date_type: published
    verified_at: '2026-09-11'
    benchmark_version: Terminal-Bench 4.0
    configuration: Launch-page Coding table, Astra column only. Not attached to
      terminal_bench (v1.0, superseded). Competitor columns were not taken.
    limitations: OpenAI's 57.9% is not Artificial Analysis's 59.1% on the same
      version label; different protocol.
  - benchmark_id: terminal_bench_science
    model_id_as_evaluated: GPT-6 Astra
    score: 64.6
    unit: percent
    source_url: https://openai.com/index/gpt-6-astra/
    source_kind: provider_self_report
    evidence_date: '2026-09-03'
    date_type: published
    verified_at: '2026-09-11'
    benchmark_version: Terminal-Bench Science 0.1
    configuration: Launch-page Academic table, Astra column only. Competitor
      columns were not taken.
    limitations: ''
  - benchmark_id: browsecomp
    model_id_as_evaluated: GPT-6 Astra
    score: 91.5
    unit: percent
    source_url: https://openai.com/index/gpt-6-astra/
    source_kind: provider_self_report
    evidence_date: '2026-09-03'
    date_type: published
    verified_at: '2026-09-11'
    benchmark_version: BrowseComp
    configuration: Launch-page Professional table, Astra column only. Competitor
      columns were not taken.
    limitations: ''
  - benchmark_id: hle_tools
    model_id_as_evaluated: GPT-6 Astra
    score: 57.2
    unit: percent
    source_url: https://openai.com/index/gpt-6-astra/
    source_kind: provider_self_report
    evidence_date: '2026-09-03'
    date_type: published
    verified_at: '2026-09-11'
    benchmark_version: Humanity's Last Exam (w/ tools)
    configuration: Launch-page Academic table. Attached to hle_tools, not hle.
      Competitor columns were not taken.
    limitations: ''
  - benchmark_id: arc_agi_2
    model_id_as_evaluated: GPT-6 Astra
    score: 95.0
    unit: percent
    source_url: https://openai.com/index/gpt-6-astra/
    source_kind: provider_self_report
    evidence_date: '2026-09-03'
    date_type: published
    verified_at: '2026-09-11'
    benchmark_version: ARC-AGI-2
    configuration: Launch-page Abstract reasoning table, Astra column only. ARC-AGI-3
      99.9% is not attached; we have no arc_agi_3 page.
    limitations: ''
  - benchmark_id: automationbench
    model_id_as_evaluated: GPT-6 Astra
    score: 41.4
    unit: percent
    source_url: https://openai.com/index/gpt-6-astra/
    source_kind: provider_self_report
    evidence_date: '2026-09-03'
    date_type: published
    verified_at: '2026-09-11'
    benchmark_version: AutomationBench
    configuration: Launch-page Professional table, Astra column only. Distinct from
      automationbench_aa (AA held-out split, 68.5). Competitor columns were not taken.
    limitations: ''
  - benchmark_id: arena_elo_overall
    model_id_as_evaluated: gpt-6-astra-max
    score: 1443.72
    unit: elo
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: Text Arena overall, raw (not style-controlled)
    configuration: LMArena's official leaderboard dataset, split latest, subset `text`
      (raw, non-style-controlled), category overall; leaderboard_publish_date 2026-09-13
      is the stated date. Rating 1443.72 (95% CI 1432.08-1455.37), 2693 votes. The live
      arena.ai board read 2026-09-24 still shows this snapshot (same vote counts).
    limitations: Normalization in api/ranking/engine.py bounds Arena Elo at 1400; values
      above clip.
  - benchmark_id: arena_elo_coding
    model_id_as_evaluated: gpt-6-astra-max
    score: 1488.58
    unit: elo
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: Text Arena coding category, raw (not style-controlled)
    configuration: LMArena's official leaderboard dataset, split latest, subset `text`
      (raw, non-style-controlled), category coding. Raw to match arena_elo_overall;
      the arena.ai page defaults to style control; leaderboard_publish_date 2026-09-13
      is the stated date. Rating 1488.58 (95% CI 1464.98-1512.19), 645 votes. The live
      arena.ai board read 2026-09-24 still shows this snapshot (same vote counts).
    limitations: Normalization in api/ranking/engine.py bounds Arena Elo at 1400; values
      above clip.
  - benchmark_id: arena_elo_style_control
    model_id_as_evaluated: gpt-6-astra-max
    score: 1479.77
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / overall, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category overall,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1479.77 [1468.12, 1491.42], 2693 votes,
      rank 24.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_coding
    model_id_as_evaluated: gpt-6-astra-max
    score: 1542.88
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / coding, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category coding,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1542.88 [1519.42, 1566.34], 645 votes,
      rank 6.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_hard_prompts
    model_id_as_evaluated: gpt-6-astra-max
    score: 1497.05
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / hard_prompts, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category hard_prompts,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1497.05 [1482.38, 1511.71], 1678 votes,
      rank 31.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_creative_writing
    model_id_as_evaluated: gpt-6-astra-max
    score: 1460.72
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / creative_writing, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category creative_writing,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1460.72 [1434.76, 1486.67], 572 votes,
      rank 25.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_instruction_following
    model_id_as_evaluated: gpt-6-astra-max
    score: 1460.95
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / instruction_following, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category instruction_following,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1460.95 [1440.56, 1481.35], 846 votes,
      rank 43.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_multi_turn
    model_id_as_evaluated: gpt-6-astra-max
    score: 1499.35
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / multi_turn, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category multi_turn,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1499.35 [1468.96, 1529.74], 373 votes,
      rank 8.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_expert
    model_id_as_evaluated: gpt-6-astra-max
    score: 1472.21
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / expert, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category expert,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1472.21 [1433.58, 1510.85], 247 votes,
      rank 76.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_longer_query
    model_id_as_evaluated: gpt-6-astra-max
    score: 1481.11
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / longer_query, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category longer_query,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1481.11 [1463.17, 1499.06], 1177 votes,
      rank 38.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_non_english
    model_id_as_evaluated: gpt-6-astra-max
    score: 1460.02
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: text_style_control / non_english, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset text_style_control, category non_english,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1460.02 [1444.69, 1475.35], 1554 votes,
      rank 36.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_medicine
    model_id_as_evaluated: gpt-6-astra-max
    score: 1496.16
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
      (effort: max; MODEL-123 max-effort rule). Rating 1496.16 [1456.30, 1536.02], 199 votes,
      rank 21.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_legal
    model_id_as_evaluated: gpt-6-astra-max
    score: 1510.23
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
      (effort: max; MODEL-123 max-effort rule). Rating 1510.23 [1470.43, 1550.03], 213 votes,
      rank 5.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_business
    model_id_as_evaluated: gpt-6-astra-max
    score: 1478.56
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
      (effort: max; MODEL-123 max-effort rule). Rating 1478.56 [1451.70, 1505.42], 502 votes,
      rank 24.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_science
    model_id_as_evaluated: gpt-6-astra-max
    score: 1497.62
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
      (effort: max; MODEL-123 max-effort rule). Rating 1497.62 [1469.60, 1525.63], 427 votes,
      rank 22.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_writing
    model_id_as_evaluated: gpt-6-astra-max
    score: 1478.06
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
      (effort: max; MODEL-123 max-effort rule). Rating 1478.06 [1455.19, 1500.94], 714 votes,
      rank 14.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_sc_vision
    model_id_as_evaluated: gpt-6-astra-max
    score: 1284.0
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-13'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: vision_style_control / overall, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset vision_style_control, category overall,
      leaderboard_publish_date 2026-09-13; style control. Highest-effort row for the product
      (effort: max; MODEL-123 max-effort rule). Rating 1284.00 [1266.98, 1301.03], 1367 votes,
      rank 16.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: arena_webdev
    model_id_as_evaluated: gpt-6-astra-max
    score: 1792.18
    unit: Arena score (Elo scale)
    source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset
    source_kind: independent_evaluator
    evidence_date: '2026-09-23'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: webdev / overall, latest split, revision 1880dbebff5b
    configuration: 'LMArena leaderboard dataset, subset webdev, category overall, leaderboard_publish_date
      2026-09-23; no style-controlled variant. Highest-effort row for the product (effort: max;
      MODEL-123 max-effort rule). Rating 1792.18 [1780.14, 1804.22], 4325 votes, rank 2.'
    limitations: Crowd preference votes, not a checked answer. Data (c) LMArena, CC BY 4.0;
      attribution on the benchmark page.
  - benchmark_id: gpqa_diamond
    model_id_as_evaluated: gpt-6-astra_max
    score: 95.77
    unit: percent
    source_url: https://epoch.ai/benchmarks/gpqa-diamond
    source_kind: independent_evaluator
    evidence_date: '2026-08-30'
    date_type: evaluated
    verified_at: '2026-09-24'
    benchmark_version: GPQA Diamond (Epoch AI run)
    configuration: Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (gpqa_diamond.csv),
      read 2026-09-24. Run started 2026-08-30T14:57:43.000Z; effort max; highest-effort run
      for the model (MODEL-123 max-effort rule), newest on a tie. Standard error 1.37 points.
    limitations: Epoch AI data, CC BY 4.0.
  - benchmark_id: frontiermath_tiers_1_3_v2
    model_id_as_evaluated: gpt-6-astra_max
    score: 93.68
    unit: percent
    source_url: https://epoch.ai/frontiermath
    source_kind: independent_evaluator
    evidence_date: '2026-08-30'
    date_type: evaluated
    verified_at: '2026-09-24'
    benchmark_version: FrontierMath-Tiers-1-3-v2-Private (Epoch AI run)
    configuration: Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (frontiermath_tiers_1_3_v2.csv),
      read 2026-09-24. Run started 2026-08-30T14:57:43.000Z; effort max; highest-effort run
      for the model (MODEL-123 max-effort rule), newest on a tie. Standard error 1.44 points.
    limitations: Epoch AI data, CC BY 4.0.
  - benchmark_id: simpleqa_verified
    model_id_as_evaluated: gpt-6-astra_max
    score: 75.6
    unit: percent
    source_url: https://epoch.ai/benchmarks/simpleqa-verified
    source_kind: independent_evaluator
    evidence_date: '2026-08-30'
    date_type: evaluated
    verified_at: '2026-09-24'
    benchmark_version: SimpleQA Verified, proportion correct, Epoch AI protocol with anti-abstention
      prompt
    configuration: Epoch AI's own run, from https://epoch.ai/data/benchmark_data.zip (simpleqa_verified.csv),
      read 2026-09-24. Run started 2026-08-30T14:57:43.000Z; effort max; highest-effort run
      for the model (MODEL-123 max-effort rule), newest on a tie. Standard error 1.36 points.
    limitations: Epoch AI data, CC BY 4.0.
  - benchmark_id: frontiercode_v1_1
    model_id_as_evaluated: GPT-6 Astra
    score: 53.26
    unit: percent
    source_url: https://cognition.com/frontiercode
    source_kind: benchmark_author
    evidence_date: '2026-09-24'
    date_type: evaluated
    verified_at: '2026-09-24'
    benchmark_version: FrontierCode 1.1, main score (Mean@5)
    configuration: Board row as copied in Epoch AI's benchmark data (frontiercode_external.csv,
      https://epoch.ai/data/benchmark_data.zip), read 2026-09-24. Effort max; the highest-effort
      row for the model (MODEL-123 max-effort rule). Harness codex.
    limitations: A live board's standing, dated by the day ModelSpec read Epoch AI's copy; the
      copy carries no per-row date. Epoch AI data, CC BY 4.0.
  - benchmark_id: vending_bench_2
    model_id_as_evaluated: GPT-6 Astra
    score: 15514.7
    unit: USD
    source_url: https://andonlabs.com/evals/vending-bench-2
    source_kind: benchmark_author
    evidence_date: '2026-09-24'
    date_type: evaluated
    verified_at: '2026-09-24'
    benchmark_version: Vending-Bench 2, mean final balance over 5 runs
    configuration: Board row as copied in Epoch AI's benchmark data (vending_bench_2_external.csv,
      https://epoch.ai/data/benchmark_data.zip), read 2026-09-24. Effort unknown; the highest-effort
      row for the model (MODEL-123 max-effort rule).
    limitations: A live board's standing, dated by the day ModelSpec read Epoch AI's copy; the
      copy carries no per-row date. Epoch AI data, CC BY 4.0.
  - benchmark_id: deepswe_v1_1
    model_id_as_evaluated: gpt-6-astra (max)
    score: 73.23
    unit: percent
    source_url: https://deepswe.datacurve.ai/
    source_kind: benchmark_author
    evidence_date: '2026-09-24'
    date_type: evaluated
    verified_at: '2026-09-24'
    benchmark_version: DeepSWE v1.1, pass@1, mini-swe-agent
    configuration: Board row as copied in Epoch AI's benchmark data (deepswe_external.csv, https://epoch.ai/data/benchmark_data.zip),
      read 2026-09-24. Effort max; the highest-effort row for the model (MODEL-123 max-effort
      rule). Harness mini-swe-agent.
    limitations: A live board's standing, dated by the day ModelSpec read Epoch AI's copy; the
      copy carries no per-row date. Epoch AI data, CC BY 4.0.
  - benchmark_id: terminal_bench_v4_0
    model_id_as_evaluated: GPT-6 Astra (max) with Codex
    score: 58.18
    unit: percent
    source_url: https://www.tbench.ai/leaderboard/terminal-bench/4.0
    source_kind: benchmark_author
    evidence_date: '2026-09-03'
    date_type: published
    verified_at: '2026-09-24'
    benchmark_version: Terminal-Bench 4.0
    configuration: 'tbench.ai leaderboard row read 2026-09-24: agent Codex (OpenAI), reasoning
      effort max, 330 trials, accuracy 58.18 ± 2.79 (95% CI). The board''s row date is the evidence
      date. Highest-effort row for the model, best agent on a tie.'
    limitations: The agent harness differs between rows; compare rows with the same agent.
  - benchmark_id: hle
    model_id_as_evaluated: GPT 6 Astra
    score: 54.8
    unit: percent
    source_url: https://labs.scale.com/leaderboard/humanitys_last_exam
    source_kind: independent_evaluator
    evidence_date: '2026-09-09'
    date_type: evaluated
    verified_at: '2026-09-24'
    benchmark_version: Humanity's Last Exam, Scale Labs leaderboard
    configuration: Scale Labs leaderboard entry read 2026-09-24; entry created 2026-09-09T18:59:21.000Z;
      effort default; ±1.94 (95% CI).
    limitations: 'Potential contamination warning: This model was evaluated after the public
      release of HLE, allowing model builder access to the prompts and solutions.'
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
  models_dev_url: https://models.dev/openai
  provider_docs_url: https://openai.com/index/gpt-6-astra/
  huggingface_url: ''
  arxiv_url: ''
  paper_url: https://openai.com/index/gpt-6-astra/
  github_url: ''
  ollama_url: ''
  artificial_analysis_url: https://artificialanalysis.ai/articles/artificial-analysis-intelligence-index-v4-2
  arena_url: ''
  last_scraped_models_dev: ''
  last_scraped_huggingface: ''
  last_scraped_benchmarks: '2026-09-11'
  last_scraped_pricing: '2026-09-11'
card_schema_version: '3.0'
card_author: models.dev-seeder
card_created: '2026-04-05'
card_updated: '2026-09-11'
authoring_guide:
  applies_to:
    model_id: openai/gpt-6-astra
    version: gpt-6-astra
  as_of: '2026-09-15'
  status: current
  sections:
    prompt_shape:
    - text: More likely to stop and ask clarifying questions; prompt it to infer intent and persist when
        the request implies authorization.
      sources:
      - url: https://platform.openai.com/docs/guides/latest-model
        title: Using GPT-6 Astra
        accessed: '2026-09-15'
        kind: provider-guidance
    - text: Ask it to request approval only after preparing a concrete, reviewable result.
      sources:
      - url: https://platform.openai.com/docs/guides/latest-model
        title: Using GPT-6 Astra
        accessed: '2026-09-15'
        kind: provider-guidance
    system_message:
    - text: Sensitive to instructions in skills and files like AGENTS.md; audit them and state that user
        instructions take precedence.
      sources:
      - url: https://platform.openai.com/docs/guides/latest-model
        title: Using GPT-6 Astra
        accessed: '2026-09-15'
        kind: provider-guidance
    reasoning_and_tools:
    - text: Does not support none reasoning effort; if migrating from none or minimal, start at low.
      sources:
      - url: https://platform.openai.com/docs/guides/latest-model
        title: Using GPT-6 Astra
        accessed: '2026-09-15'
        kind: provider-guidance
    - text: Tool calling requires the Responses API.
      sources:
      - url: https://platform.openai.com/docs/guides/latest-model
        title: Using GPT-6 Astra
        accessed: '2026-09-15'
        kind: provider-guidance
    - text: temperature, top_p and top_logprobs are unsupported and must be removed.
      sources:
      - url: https://platform.openai.com/docs/guides/latest-model
        title: Using GPT-6 Astra
        accessed: '2026-09-15'
        kind: provider-guidance
    - text: To change effort mid-conversation, use configuration_update items so the cached prompt prefix
        is preserved.
      sources:
      - url: https://platform.openai.com/docs/guides/latest-model
        title: Using GPT-6 Astra
        accessed: '2026-09-15'
        kind: provider-guidance
    - text: May delegate to subagents less than wanted; specify when and how much to delegate.
      sources:
      - url: https://platform.openai.com/docs/guides/latest-model
        title: Using GPT-6 Astra
        accessed: '2026-09-15'
        kind: provider-guidance
    formatting:
    - text: Tends toward lists, tables and Markdown; specify prose if the application needs it.
      sources:
      - url: https://platform.openai.com/docs/guides/latest-model
        title: Using GPT-6 Astra
        accessed: '2026-09-15'
        kind: provider-guidance
    - text: May reuse recurring phrases; state the required writing style.
      sources:
      - url: https://platform.openai.com/docs/guides/latest-model
        title: Using GPT-6 Astra
        accessed: '2026-09-15'
        kind: provider-guidance
    - text: Inter-agent messages can contain spacing errors; instruct it to keep them legible.
      sources:
      - url: https://platform.openai.com/docs/guides/latest-model
        title: Using GPT-6 Astra
        accessed: '2026-09-15'
        kind: provider-guidance
    failure_modes:
    - text: Unclear or conflicting guidance in skill files can make it block work early.
      sources:
      - url: https://platform.openai.com/docs/guides/latest-model
        title: Using GPT-6 Astra
        accessed: '2026-09-15'
        kind: provider-guidance
    - text: On small coding tasks it can test more broadly than needed; calibrate how much verification
        a change requires.
      sources:
      - url: https://platform.openai.com/docs/guides/latest-model
        title: Using GPT-6 Astra
        accessed: '2026-09-15'
        kind: provider-guidance
    retry_advice:
    - text: If it keeps pausing for approval, add follow-through guidance rather than re-running the same
        prompt.
      sources:
      - url: https://platform.openai.com/docs/guides/latest-model
        title: Using GPT-6 Astra
        accessed: '2026-09-15'
        kind: provider-guidance
    - text: Ask it to name the skill instruction that caused a pause, to find the conflicting guidance.
      sources:
      - url: https://platform.openai.com/docs/guides/latest-model
        title: Using GPT-6 Astra
        accessed: '2026-09-15'
        kind: provider-guidance
---

# GPT-6 Astra

Closed-weight reasoning model from OpenAI, launched 3 September 2026. API id
`gpt-6-astra`. Parameter count is unpublished. Standard API price is $10 / $50
per million input / output tokens; Fast mode is 2× that price.

Rolling out to ChatGPT Plus, Pro, Business, and Enterprise, and on the OpenAI
API, Azure, and Bedrock. Enterprise access is off by default. Pro, Business,
and Enterprise also get GPT-6 Astra Pro.

## What OpenAI published (Astra column only)

Scores below are from [the launch page](https://openai.com/index/gpt-6-astra/),
dated 3 September 2026. Competitor columns were not taken. Independent
Artificial Analysis numbers stay on their own evidence rows.

- GPQA Diamond 96.0%
- Terminal-Bench 4.0 57.9%
- Terminal-Bench Science 0.1 64.6%
- BrowseComp 91.5%
- Humanity's Last Exam (with tools) 57.2%
- ARC-AGI-2 95.0%
- AutomationBench 41.4% (not AA's held-out 68.5%)

SWE-bench Verified, HumanEval, LiveCodeBench, Aider Polyglot, LM Arena, AIME,
and MMLU-Pro are not on that page. OSWorld 2.0 (72.6%) and ARC-AGI-3 (99.9%)
are not attached: our `osworld` page is not the 2.0 variant, and we have no
`arc_agi_3` page.

## Key features (launch page)

- Computer use and browsing
- Function calling
- Structured JSON output
- Image and file input
- Chain-of-thought / effort settings
