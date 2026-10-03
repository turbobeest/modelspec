# Agent scenarios, 2026-10-01

Scripted agent and judge replay with recorded LOCAL engine responses. Rates and latencies verify plumbing, not vendor quality or live SLOs.

Mode: dry-run. Runs: 222/222. Estimated spend: $0.0000; cap: $25.00.

Success requires a completed answer, a passing rubric judgement, and an acceptable top model or tied subset when recall evidence exists. Recall acceptable lists are unordered sets, not exact tied rankings. Abstentions match only explicit recall rules. The judge assesses evidence separation and required uncertainty flags.

Missing judgements and capped or failed runs count as failures. Expected-match rates exclude cases without approved expectations or a parsed judgement.

## Success and tool use

| Group | Runs | Success | Expected match | Mean tools | API p50 ms | API p95 ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| F1 | 93 | 0.0% | 92.3% | 2.03 | 3.91 | 47.46 |
| F2 | 15 | 0.0% | n/a | 2.00 | 0.00 | 3.93 |
| F3 | 48 | 0.0% | 80.0% | 2.00 | 0.00 | 34.19 |
| F4 | 66 | 0.0% | 0.0% | 2.00 | 0.00 | 42.42 |
| claude | 74 | 0.0% | 80.0% | 2.01 | 3.24 | 42.42 |
| openai | 74 | 0.0% | 80.0% | 2.01 | 0.00 | 42.42 |
| gemini | 74 | 0.0% | 80.0% | 2.01 | 3.24 | 42.42 |

The JSON includes each family × agent intersection and every ordered tool call, API round-trip latency, retry, validation issue, token count, final answer and judge result. Tool results are deduplicated by response_ref.

## Misuse patterns

- wrong_facet_ids: model.context_tokens (2)
- schema_confusion_by_tool: decide (18)
- missing_capabilities: A fits_hardware membership alone cannot prove fit for a machine topology, runtime, quantization and KV-cache workload. (15), The decide contract rejects free-text task and cannot evaluate or route this exact prompt. (15), the registry has no model-level self-hosting facet; open weights does not prove deployability. (9), "adequate hardware" names no registered hardware SKU to constrain. (6), no registered domain distinguishes defect review from patch generation. (3), no registered domain represents general assistance across domains. (3), grounded generation over retrieved documents has no registered domain; (3), summary faithfulness has no distinct registered domain or facet; (3), high-volume throughput is not constrained because the question gives no rate. (3), customer-support quality has no distinct registered domain. (3), chart and technical-screenshot interpretation has no distinct registered domain. (3), multilingual does not name which languages must be supported. (3), one-device count and unspecified quantization cannot be expressed by model.fits_hardware. (3), "base Apple M4" does not identify a product, RAM amount, or registered hardware SKU. (3), the registry has no model-level local-hosting facet; open weights does not prove deployability. (3), scientific research workflow quality has no distinct registered domain. (3), no transcription domain is registered, and language, streaming, and audio length are unspecified. (3)

## Gap list

These are catalogue annotations tied to contracts and recall specs. They identify requirements that cannot be expressed completely; they are not inferred from transport errors. A partial proxy is recorded as a gap in the remaining requirement.

- `hardware-5090` (F3): A fits_hardware membership alone cannot prove fit for a machine topology, runtime, quantization and KV-cache workload. Suggested fix: Expose a hardware-fit MCP tool accepting SKU, device count, memory, runtime, quantization, batch and context, and return measured fit or undetermined. Source: `tests/recall/specs/Q17.yaml`.
- `hardware-dual-4090` (F3): A fits_hardware membership alone cannot prove fit for a machine topology, runtime, quantization and KV-cache workload. Suggested fix: Expose a hardware-fit MCP tool accepting SKU, device count, memory, runtime, quantization, batch and context, and return measured fit or undetermined. Source: `tests/recall/specs/Q17.yaml`.
- `hardware-h100` (F3): A fits_hardware membership alone cannot prove fit for a machine topology, runtime, quantization and KV-cache workload. Suggested fix: Expose a hardware-fit MCP tool accepting SKU, device count, memory, runtime, quantization, batch and context, and return measured fit or undetermined. Source: `tests/recall/specs/Q17.yaml`.
- `hardware-m4` (F3): A fits_hardware membership alone cannot prove fit for a machine topology, runtime, quantization and KV-cache workload. Suggested fix: Expose a hardware-fit MCP tool accepting SKU, device count, memory, runtime, quantization, batch and context, and return measured fit or undetermined. Source: `tests/recall/specs/Q17.yaml`.
- `hardware-spark` (F3): A fits_hardware membership alone cannot prove fit for a machine topology, runtime, quantization and KV-cache workload. Suggested fix: Expose a hardware-fit MCP tool accepting SKU, device count, memory, runtime, quantization, batch and context, and return measured fit or undetermined. Source: `tests/recall/specs/Q17.yaml`.
- `prompt-code` (F2): The decide contract rejects free-text task and cannot evaluate or route this exact prompt. Suggested fix: Add an opt-in prompt-to-Spec MCP tool with explicit extracted constraints and user-visible uncertainty; benchmark prompt routing before promising prompt-specific quality. Source: `decision/contract.py:parse_spec`.
- `prompt-document` (F2): The decide contract rejects free-text task and cannot evaluate or route this exact prompt. Suggested fix: Add an opt-in prompt-to-Spec MCP tool with explicit extracted constraints and user-visible uncertainty; benchmark prompt routing before promising prompt-specific quality. Source: `decision/contract.py:parse_spec`.
- `prompt-maths` (F2): The decide contract rejects free-text task and cannot evaluate or route this exact prompt. Suggested fix: Add an opt-in prompt-to-Spec MCP tool with explicit extracted constraints and user-visible uncertainty; benchmark prompt routing before promising prompt-specific quality. Source: `decision/contract.py:parse_spec`.
- `prompt-policy` (F2): The decide contract rejects free-text task and cannot evaluate or route this exact prompt. Suggested fix: Add an opt-in prompt-to-Spec MCP tool with explicit extracted constraints and user-visible uncertainty; benchmark prompt routing before promising prompt-specific quality. Source: `decision/contract.py:parse_spec`.
- `prompt-review` (F2): The decide contract rejects free-text task and cannot evaluate or route this exact prompt. Suggested fix: Add an opt-in prompt-to-Spec MCP tool with explicit extracted constraints and user-visible uncertainty; benchmark prompt routing before promising prompt-specific quality. Source: `decision/contract.py:parse_spec`.
- `recall-q03` (F1): no registered domain distinguishes defect review from patch generation. Suggested fix: Publish a dedicated facet or measured capability, or expose a clarification tool before deciding. Source: `tests/recall/specs/Q03.yaml`.
- `recall-q04` (F1): no registered domain represents general assistance across domains. Suggested fix: Publish a dedicated facet or measured capability, or expose a clarification tool before deciding. Source: `tests/recall/specs/Q04.yaml`.
- `recall-q08` (F1): grounded generation over retrieved documents has no registered domain; Suggested fix: Publish a dedicated facet or measured capability, or expose a clarification tool before deciding. Source: `tests/recall/specs/Q08.yaml`.
- `recall-q09` (F1): summary faithfulness has no distinct registered domain or facet; Suggested fix: Publish a dedicated facet or measured capability, or expose a clarification tool before deciding. Source: `tests/recall/specs/Q09.yaml`.
- `recall-q10` (F4): high-volume throughput is not constrained because the question gives no rate. Suggested fix: Publish a dedicated facet or measured capability, or expose a clarification tool before deciding. Source: `tests/recall/specs/Q10.yaml`.
- `recall-q11` (F4): customer-support quality has no distinct registered domain. Suggested fix: Publish a dedicated facet or measured capability, or expose a clarification tool before deciding. Source: `tests/recall/specs/Q11.yaml`.
- `recall-q12` (F3): the registry has no model-level self-hosting facet; open weights does not prove deployability. Suggested fix: Publish a dedicated facet or measured capability, or expose a clarification tool before deciding. Source: `tests/recall/specs/Q12.yaml`.
- `recall-q12` (F3): "adequate hardware" names no registered hardware SKU to constrain. Suggested fix: Publish a dedicated facet or measured capability, or expose a clarification tool before deciding. Source: `tests/recall/specs/Q12.yaml`.
- `recall-q13` (F3): the registry has no model-level self-hosting facet; open weights does not prove deployability. Suggested fix: Publish a dedicated facet or measured capability, or expose a clarification tool before deciding. Source: `tests/recall/specs/Q13.yaml`.
- `recall-q13` (F3): "adequate hardware" names no registered hardware SKU to constrain. Suggested fix: Publish a dedicated facet or measured capability, or expose a clarification tool before deciding. Source: `tests/recall/specs/Q13.yaml`.
- `recall-q14` (F1): chart and technical-screenshot interpretation has no distinct registered domain. Suggested fix: Publish a dedicated facet or measured capability, or expose a clarification tool before deciding. Source: `tests/recall/specs/Q14.yaml`.
- `recall-q16` (F3): multilingual does not name which languages must be supported. Suggested fix: Publish a dedicated facet or measured capability, or expose a clarification tool before deciding. Source: `tests/recall/specs/Q16.yaml`.
- `recall-q16` (F3): the registry has no model-level self-hosting facet; open weights does not prove deployability. Suggested fix: Publish a dedicated facet or measured capability, or expose a clarification tool before deciding. Source: `tests/recall/specs/Q16.yaml`.
- `recall-q17` (F3): one-device count and unspecified quantization cannot be expressed by model.fits_hardware. Suggested fix: Publish a dedicated facet or measured capability, or expose a clarification tool before deciding. Source: `tests/recall/specs/Q17.yaml`.
- `recall-q18` (F3): "base Apple M4" does not identify a product, RAM amount, or registered hardware SKU. Suggested fix: Publish a dedicated facet or measured capability, or expose a clarification tool before deciding. Source: `tests/recall/specs/Q18.yaml`.
- `recall-q18` (F3): the registry has no model-level local-hosting facet; open weights does not prove deployability. Suggested fix: Publish a dedicated facet or measured capability, or expose a clarification tool before deciding. Source: `tests/recall/specs/Q18.yaml`.
- `recall-q19` (F1): scientific research workflow quality has no distinct registered domain. Suggested fix: Publish a dedicated facet or measured capability, or expose a clarification tool before deciding. Source: `tests/recall/specs/Q19.yaml`.
- `recall-q20` (F1): no transcription domain is registered, and language, streaming, and audio length are unspecified. Suggested fix: Publish a dedicated facet or measured capability, or expose a clarification tool before deciding. Source: `tests/recall/specs/Q20.yaml`.
