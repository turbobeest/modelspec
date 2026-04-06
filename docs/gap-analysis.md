# Template Gap Analysis — Honest Assessment

## Verdict

The V1 template **exceeds any single existing source** (models.dev, HuggingFace model cards, Datasaur scorecard, Vellum leaderboard) but **does not yet synthesize everything across all of them**. It's roughly 65% of what a truly comprehensive model intelligence card needs.

Here's what's missing, organized by source.

---

## 1. Missing from Models.dev Parity

**Status: ~95% covered.** Only minor gaps:

| Field | In Template? | Notes |
|---|---|---|
| All TOML schema fields | ✅ | Full coverage |
| `cost.input_audio` / `cost.output_audio` | ❌ | Audio-specific pricing not in template |
| Provider `npm` package / `api` endpoint | ❌ | Relevant for SDK integration |
| Provider `env` (auth env vars) | ❌ | Useful for deployment tooling |

---

## 2. Missing from HuggingFace Model Cards

**Status: ~50% covered.** HF cards track model lineage and training details we completely skip:

| Field | In Template? | Why It Matters |
|---|---|---|
| `base_model` | ❌ | What model was this finetuned/quantized from? Critical for lineage |
| `base_model_relation` | ❌ | finetune \| adapter \| quantized \| merge |
| `pipeline_tag` | ❌ | text-generation \| text-to-image \| etc. |
| `library_name` | ❌ | transformers \| diffusers \| vllm \| etc. |
| `datasets` (training data) | ❌ | What data was used — huge for trust/compliance |
| `co2_eq_emissions` | ❌ | Carbon footprint of training |
| `training_hardware` | ❌ | What hardware was used to train |
| `training_time` | ❌ | Duration / compute cost |
| `eval_results` (structured) | ❌ | HF has a structured format for benchmark results |
| `tags` (freeform) | ❌ | Discoverability tags |
| `not-for-all-audiences` | ❌ | Content safety flag |

---

## 3. Missing Architecture & Technical Details

**Status: ~20% covered.** This is the biggest gap. We track *what* a model can do but not *what it is*:

| Field | In Template? | Why It Matters |
|---|---|---|
| `architecture_type` | ❌ | dense \| MoE \| SSM \| hybrid \| diffusion — fundamental |
| `total_parameters` | ❌ | 7B, 70B, 405B — everyone's first question |
| `active_parameters` | ❌ | For MoE models (e.g. 30B total, 3B active) |
| `num_experts` / `experts_active` | ❌ | MoE routing details |
| `attention_type` | ❌ | MHA \| GQA \| MLA \| linear — affects speed |
| `positional_encoding` | ❌ | RoPE \| ALiBi \| NTK-aware — affects context extension |
| `vocab_size` | ❌ | Tokenizer efficiency |
| `tokenizer_type` | ❌ | BPE \| SentencePiece \| tiktoken |
| `embedding_dimensions` | ❌ | For embedding models |
| `num_layers` / `hidden_size` | ❌ | Architecture depth/width |
| `training_compute_flops` | ❌ | Total training cost estimate |
| `training_data_tokens` | ❌ | How much data it saw |
| `training_data_cutoff` | ❌ | Different from knowledge_cutoff (when training data ends vs. what it knows) |

---

## 4. Missing Benchmarks

**Status: ~30% covered.** We have 7 benchmark slots. The current landscape demands 20+:

### Reasoning & Knowledge
| Benchmark | In Template? | What It Tests |
|---|---|---|
| MMLU-Pro | ❌ | Replaced MMLU — harder, more choices |
| GPQA Diamond | ✅ | PhD-level science (already included) |
| HLE (Humanity's Last Exam) | ❌ | Hardest known benchmark |
| ARC-Challenge | ❌ | Grade-school science reasoning |
| HellaSwag | ❌ | Commonsense reasoning (saturated but baseline) |
| TruthfulQA | ❌ | Resistance to common misconceptions |
| BBH (Big-Bench Hard) | ❌ | 23 challenging compositional tasks |
| IFEval | ❌ | Instruction-following precision |
| MUSR | ❌ | Multi-step soft reasoning |

### Math
| Benchmark | In Template? | What It Tests |
|---|---|---|
| MATH-500 | ✅ | Competition math (already included) |
| AIME 2025 | ❌ | Current frontier math |
| AIME 2026 | ❌ | Newest math benchmark |
| GSM8K | ❌ | Grade-school math (saturated but baseline) |
| MGSM | ❌ | Multilingual math — critical for intl. models |

### Coding
| Benchmark | In Template? | What It Tests |
|---|---|---|
| HumanEval / HumanEval+ | ✅ | Python function generation (already included) |
| SWE-bench Verified | ✅ | Real GitHub issue resolution (already included) |
| LiveCodeBench | ❌ | Live coding problems, contamination-resistant |
| Aider Polyglot | ✅ | Multi-language coding (already included) |
| Terminal Bench | ❌ | Command-line / systems programming |

### Multimodal
| Benchmark | In Template? | What It Tests |
|---|---|---|
| MMMU | ❌ | Multimodal multi-discipline understanding |
| MathVista | ❌ | Visual math reasoning |

### Safety & Bias
| Benchmark | In Template? | What It Tests |
|---|---|---|
| HELM Safety | ❌ | Aggregate safety scoring |
| BBQ | ❌ | Social bias in QA |
| StereoSet | ❌ | Stereotype detection |
| ToxiGen | ❌ | Toxic content generation rates |

### Human Preference
| Benchmark | In Template? | What It Tests |
|---|---|---|
| LMArena (Chatbot Arena) ELO | ✅ | Human preference ranking (already included) |
| MT-Bench | ❌ | Multi-turn conversation quality |
| AlpacaEval | ❌ | Instruction following vs reference |
| WildBench | ❌ | Real user query performance |

### Domain-Specific
| Benchmark | In Template? | What It Tests |
|---|---|---|
| MedQA | ❌ | Medical knowledge |
| LegalBench | ❌ | Legal reasoning |
| FinBench | ❌ | Financial analysis |

---

## 5. Missing NIST AI RMF / Enterprise Risk Dimensions

**Status: ~40% covered.** We have safety basics but miss the governance framework:

| Dimension | In Template? | NIST RMF Mapping |
|---|---|---|
| Explainability | ❌ | MEASURE 2.7 — Can the model explain its reasoning? |
| Bias evaluation results | ❌ | MEASURE 2.11 — Fairness and bias assessment |
| Data provenance / lineage | ❌ | MAP 4 — Where did training data come from? |
| Adversarial robustness | ❌ | MEASURE 2.6 — Resistance to adversarial inputs |
| Privacy posture | ❌ | Data retention, PII handling, data flows |
| Environmental impact | ❌ | Carbon footprint per inference / training |
| Supply chain risk | ❌ | Third-party dependencies, API risks |
| AI-BOM compatibility | ❌ | AI Bill of Materials for audit trails |
| Incident history | ❌ | Known failures, recalls, vulnerability disclosures |
| Human oversight requirements | ❌ | GOVERN 3.2 — Required human-in-the-loop? |

---

## 6. Missing Inference Performance Details

**Status: ~15% covered.** We say "fits on" but don't quantify *how well*:

| Field | In Template? | Why It Matters |
|---|---|---|
| `tokens_per_second` (per hardware, per quant) | ❌ | The single most actionable deployment metric |
| `time_to_first_token` (TTFT) | ❌ | Critical for interactive use |
| `throughput_batch` | ❌ | Batch inference speed |
| `memory_usage_actual` (per quant) | ❌ | Actual vs theoretical VRAM |
| `context_speed_degradation` | ❌ | How much does speed drop at long contexts? |
| `supported_apis` | ❌ | Which cloud providers host this model? |
| `rate_limits` | ❌ | API rate limits per provider |
| `sla` | ❌ | Uptime guarantees |
| `latency_p50` / `latency_p99` | ❌ | API latency distribution |

---

## 7. Missing Multimodal Detail

**Status: ~30% covered.** We list modalities but don't characterize them:

| Field | In Template? | Why It Matters |
|---|---|---|
| Vision detail (OCR, charts, spatial) | ❌ | "Supports images" vs "can read handwriting" is huge |
| Audio detail (ASR, TTS, music) | ❌ | Input vs output, languages |
| Video understanding detail | ❌ | Temporal reasoning, length limits |
| Image generation quality | ❌ | For multimodal output models |
| Document understanding (PDF, table extraction) | ❌ | Enterprise critical |
| Max image resolution | ❌ | Practical limit |
| Max audio duration | ❌ | Practical limit |

---

## 8. Missing from Datasaur / Enterprise Scorecards

| Dimension | In Template? | Notes |
|---|---|---|
| Privacy pillar (self-hostable, data retention) | Partial | We have `local_inference` but not data retention policies |
| Speed pillar (TPS, TTFT, latency) | ❌ | Completely missing |
| Quality pillar composite score | ❌ | Weighted aggregate score |
| Cost-efficiency ratio | ❌ | Quality-per-dollar metric |

---

## Summary Scorecard

| Source | Coverage |
|---|---|
| models.dev TOML schema | 95% |
| HuggingFace model card spec | 50% |
| Benchmark ecosystem (2025-2026) | 30% |
| Architecture / technical details | 20% |
| NIST AI RMF dimensions | 40% |
| Inference performance metrics | 15% |
| Multimodal characterization | 30% |
| Enterprise scorecards (Datasaur, Vellum, HELM) | 40% |

**Overall: ~65% comprehensive**

---

## What Makes It Already Better Than Industry Standard

Despite the gaps, the template already does things *nobody else does in a single card*:

1. **Hardware-model fit matrix** — No existing scorecard maps models to specific consumer hardware
2. **Defense/government use classification** — models.dev, HF, and Datasaur completely ignore this
3. **Origin country tracking** — Critical for export control and supply chain risk; nobody tracks this systematically
4. **Downselect profiles** — The institutional constraint layer doesn't exist anywhere
5. **Unified capability taxonomy with tiers** — Most sources are either benchmarks-only or capabilities-only; we fuse both
6. **MCP compatibility tracking** — Nobody tracks this yet
7. **Quantization-to-hardware mapping** — Exists in scattered forum posts but not in any structured card

---

## Recommended V2 Changes

The V2 template should add these sections (in priority order):

1. **Architecture block** — parameter counts, architecture type, attention mechanism
2. **Expanded benchmarks** — 20+ slots organized by category
3. **Inference performance block** — TPS, TTFT, memory per hardware per quant
4. **Model lineage** — base_model, relation, training data, training compute
5. **Risk & governance block** — NIST RMF aligned fields
6. **Multimodal characterization** — detailed per-modality capabilities
7. **Provider/API block** — which providers serve it, rate limits, SLAs
