# Agentic latency benchmark: what a measured one needs (MODEL-57)

No surveyed source publishes per-model wall-clock time for a tool-calling task
([survey](agentic-latency-survey.md)). So there is no benchmark page. This is the
spec a measured benchmark would need before it can enter under the eligibility
contract ([host layer, deferred section](host-layer.md)).

## Definition

Wall-clock per task = time from the harness sending the task to the agent until
the agent returns its final answer or the harness stops it.
It decomposes as `Σ(prefill + decode + network) + Σ(tool execution + I/O + waits)`.
Only the first sum is model-attributable. A result must report both sums separately.

## Harness

- One named, versioned harness with a pinned commit (for example an existing open
  harness such as mini-SWE-agent, tau2-bench or HAL, extended with timing).
- Fixed scaffold, prompt, tool set, step limit, token limit and timeout across models.
- Per-step trace timestamps: request sent, first token, last token, tool start, tool end.
- Tools deterministic where possible (mocked APIs, local containers, no live web).

## Task set

- A named, versioned task set with a fixed task count, drawn from a public benchmark
  with a known licence.
- Mix of short loops and long loops. Report the step count distribution with times.
- Timeouts and failures are reported, not dropped. Time is reported for successful
  and for all tasks separately.

## Hardware and host

- Every result carries MODEL-26 keys: `host_id` and `hardware_id` for the tool
  execution environment. Self-hosted models also carry them for the inference server.
- API-served models: record provider, endpoint, region and client location. The
  provider's hardware stays null unless published.
- Runtime and version (for example vLLM, llama.cpp) and quantization for self-hosted runs.
- Concurrency during the run is stated.

## Repetitions and variance

- At least 3 full repetitions per model, run at different times of day for API models.
- Report median and P90 per task and across tasks, plus the interquartile range.
- Report the date range of the runs. Evidence dating uses the observation date.

## Attribution

- Attributable to the model and serving: model-side time, tokens per step, and
  steps to completion. A model that needs fewer steps is genuinely faster.
- Not attributable: tool runtime, container start, network to tools, and harness
  overhead. These are reported but must not rank models across different hosts.
- Totals from different `host_id`s or harnesses are not comparable. The ranking
  engine should compare only within one harness + task set + host.

## Cost

- Token spend per task and dollars at the stated price date.
- Compute cost of the tool environment per hour.
- Running it is not free: every model x task x repetition is a paid rollout. The HAL
  paper reports about $40,000 for 21,730 rollouts (arXiv 2510.11977, read 2026-09-15).
  That is quoted as scale context, not as an estimate for this benchmark.

## Decisions for Jamie

1. **Build or wait?** Recommendation: wait. Do not build a runner now. Revisit
   when a third-party leaderboard publishes per-task wall-clock with a harness version.
2. **Interim proxy.** Recommendation: allow `steps to completion` (SWE-bench already
   publishes step-limit and step-distribution views) and a published API
   end-to-end response time as two separate, clearly named benchmarks. Never sum
   them into a "loop latency".
3. **If building later.** Recommendation: extend one existing open harness with
   timestamps rather than writing a new one. Report model-side time and tool time
   separately. Keep it outside the default ranking floors until at least 3 repetitions exist.
4. **Comparability scope.** Confirm that latency results rank only within one
   `host_id` + harness + task set.
