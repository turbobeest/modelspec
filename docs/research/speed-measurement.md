# Speed measurement for premier offerings

Read on 2026-09-28. This note covers `offering.speed.time_to_first_token` and
`offering.speed.throughput`. It does not report a ModelSpec measurement. ADR
0004 requires Jamie to approve active probes before any paid request is sent.

## Published-source review

The review found no reusable public reading that meets the facet definitions
for any of the 38 slice-1 offerings. Each offering therefore records two
`unknown` facts and names the registered provider and model pages checked.
These facts are not verified values and the snapshot does not treat them as
measurements.

| Source class | What it measures | How a reading is dated | Reuse result | Lineup result |
|---|---|---|---|---|
| Provider model, pricing, and performance documentation | Model availability, price, limits, and sometimes the definitions of time to first token and output tokens per second | Page publication or update date when present; otherwise the retrieval date | ModelSpec may cite individual facts and retain a source snapshot. It does not reproduce a provider's page or table. AWS documentation has an explicit CC BY-SA 4.0 licence. Google developer documentation is generally CC BY 4.0 when the page carries the standard notice. Other reviewed provider terms do not grant a broad republication licence. | No page publishes a median for a matching model, provider, region, and tier with the required prompt length, output length, effort, client region, sample size, and measurement date. |
| Provider status pages | Service availability, incidents, and sometimes service-wide response time | Incident timestamps and rolling status windows | Public facts may be cited. Status-page charts are not copied. | The metrics are service-wide and do not separate model, region, tier, prompt length, or generation throughput. |
| OpenRouter provider pages | Live time to first token, throughput, and uptime by model and provider, with selectable percentile and a rolling time window | The page states the rolling window. A retained reading would also need its retrieval date. | Not reusable. The [OpenRouter Terms of Service](https://openrouter.ai/terms/) prohibit scripts, robots, or other automated means that scrape or copy information from the service. The pages also omit the prompt and output lengths, client region, and sample size required by the ModelSpec facets. | Excluded from the registry and offering facts. |
| Lab model cards and system cards | Model architecture, capability evidence, and occasionally self-hosted inference results for a named hardware and software setup | Publication date, repository revision, or commit date | Each card's own licence controls reuse. The review uses only cards and repositories already registered for the premier set. | A self-hosted number does not describe a managed provider offering. None of the reviewed cards gives a matching provider reading with the complete method. |

All pages in the next table were read on 2026-09-28. The offering facts use
the source IDs in the last column, so the URLs remain in the single source
registry rather than being copied into every offering file.

| Offering provider | Primary pages checked | Published speed measurement | Registered source IDs |
|---|---|---|---|
| Alibaba Model Studio | [Qwen 3.8 Max model page](https://help.aliyun.com/en/model-studio/qwen3-8-max), [pricing](https://www.alibabacloud.com/help/en/model-studio/model-pricing) | No. TPM is an account capacity limit, not single-request output speed. | `model-143-qwen-qwen3-8-max-0902`, `alibaba-model-studio-pricing` |
| Anthropic | [model overview](https://platform.claude.com/docs/en/models/overview), [pricing](https://platform.claude.com/docs/en/about-claude/pricing) | No per-model median or complete method. | One `model-143-anthropic-*` source per model, `anthropic-pricing` |
| Amazon Bedrock | [pricing](https://aws.amazon.com/bedrock/pricing/), [latency-optimized inference](https://docs.aws.amazon.com/bedrock/latest/userguide/latency-optimized-inference.html) | No matching lineup value. The separate 2025 study below measures older models. | `aws-pricing` plus the matching lab model page |
| Azure AI Foundry | [pricing](https://azure.microsoft.com/en-us/pricing/details/azure-openai/), [latency metrics](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/latency) | No public value. Azure tells customers how to read their own monitor data. | `azure-pricing` plus the matching OpenAI model page |
| DeepSeek | [V4 Pro model card](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/resolve/main/README.md), [API pricing](https://api-docs.deepseek.com/quick_start/pricing/) | No per-offering median or complete method. | `model-143-deepseek-deepseek-v4-pro`, `deepseek-v4-pricing` |
| Google Gemini API | [model pages](https://ai.google.dev/gemini-api/docs/models), [pricing](https://ai.google.dev/gemini-api/docs/pricing) | No per-model median or complete method. | One `model-143-google-*` source per model, `gemini-pricing` |
| Google Vertex AI | [generative AI pricing](https://cloud.google.com/vertex-ai/generative-ai/pricing) and the matching lab model page | No per-model median or complete method. | `vertex-pricing` plus the matching Google or Anthropic model page |
| Meta Model API | [model documentation](https://ai.developer.meta.com/docs/models.md), [pricing and limits](https://ai.developer.meta.com/docs/pricing-rate-limits.md) | No per-model median or complete method. | One `model-143-meta-*` source per model, `meta-model-api-pricing` |
| OpenAI | [model catalogue](https://developers.openai.com/api/docs/models/all) and each model page | Model pages use qualitative speed labels, not a measurement. | One `model-143-openai-*` source per model, `openai-data` |
| TypeSafe | [model documentation](https://docs.typesafe.ai/models.md) | No per-offering median or complete method. | `model-143-typesafe-jev-1-13`, `typesafe-models` |
| xAI | [Grok 4.7 model page](https://docs.x.ai/developers/models/grok-4.7) | The page describes a separate fast product but gives no standard-offering measurement. | `model-143-xai-grok-4-7`, `xai-grok-4-7` |
| Z.ai | [GLM 5.2 guide](https://docs.z.ai/guides/llm/glm-5.2), [GLM 5.3 guide](https://docs.z.ai/guides/llm/glm-5.3), [pricing](https://docs.z.ai/guides/overview/pricing.md) | No per-offering median or complete method. | One `model-143-zai-*` source per model, `zai-pricing` |

The [OpenAI](https://status.openai.com/),
[Anthropic](https://status.anthropic.com/), [AWS](https://health.aws.amazon.com/health/status),
[Azure](https://azure.status.microsoft/en-us/status), and
[Google Cloud](https://status.cloud.google.com/) status pages were also read
on 2026-09-28. They date incidents and rolling availability, not speed
readings for a model, region, and tier. They are not registered as evidence
for either speed facet.

The strongest numerical provider publication was AWS's [latency-optimized
inference study](https://aws.amazon.com/blogs/machine-learning/optimizing-ai-responsiveness-a-practical-guide-to-amazon-bedrock-latency-optimized-inference/),
published 2025-01-28. It reports about 1,600 calls, prompt lengths from 100 to
100,000 tokens, outputs from 100 to 1,000 tokens, a client in `us-west-2`, and
models in `us-east-2`. Its table contains median time to first token and output
tokens per second. The measured Claude 3.5 Haiku and Llama 3.1 70B offerings
are not in `premier/slice-1.yaml`, so none of those values transfers to this
lineup. AWS licenses documentation on `docs.aws.amazon.com` under CC BY-SA 4.0,
as stated in the [AWS Site Terms](https://aws.amazon.com/terms/). The blog page
itself remains subject to the general site terms, so ModelSpec cites its facts
instead of copying its table.

Microsoft's [Azure OpenAI latency documentation](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/latency)
defines the customer metrics `AzureOpenAITimeToResponse` and
`AzureOpenAINormalizedTBTInMS`. It publishes no per-offering value. The
[Microsoft Learn terms](https://learn.microsoft.com/en-us/legal/termsofuse)
do not grant general commercial republication rights, so a future collector
should retain the minimum cited region and publish only the sourced fact.

Google's [developer site policy](https://developers.google.com/terms/site-policies)
permits reuse of pages carrying the standard CC BY 4.0 notice with attribution.
The Gemini and Vertex pages reviewed describe models, prices, quotas, and
operational metrics, but not reusable per-offering speed readings. The
[Gemini API terms](https://ai.google.dev/gemini-api/terms) govern use of the
API, not a licence to infer a speed number without measuring it.

The other checked provider and model pages are the registered sources listed
in each unknown fact. Qualitative claims such as "fast", throughput capacity
such as tokens per minute, concurrency limits, and a separate premium speed
tier are not median single-request throughput. They stay null.

## Proposed ModelSpec measurement

Jamie can approve a pilot first. The measurement runner should be a small,
versioned command in this repository. It should write raw request timing and
token counts to content-addressed files outside git, then emit facts only after
the two-key verification flow has checked the aggregate and method.

For each offering, the runner should:

1. Pin the provider model identifier, region, account tier, streaming mode,
   default reasoning effort, SDK version, runner commit, and client region.
2. Use three fixed public prompts of about 1,000, 8,000, and 32,000 provider
   tokens. Ask for 256 output tokens with temperature zero where supported.
   Store the exact provider-reported input and output token counts.
3. Make three unrecorded warm-up calls per prompt size, then 30 measured calls.
   Randomize offerings in round-robin order so time of day does not favour one
   provider. Do not retry a successful request. Record failures and throttles
   separately.
4. Measure time to first token from immediately before the HTTP request until
   the first content token arrives. Measure throughput from the first content
   token through the last content token, divided by provider-reported output
   tokens after the first token. Exclude cached responses and tool calls.
5. Publish the median, sample size, run window in UTC, prompt and output token
   distributions, effort, client and provider regions, and software versions.
   Also retain p10 and p90 for audit, without turning them into new facets.
6. Register the resulting source as `volatility: live`. Re-run weekly through
   the MODEL-124 refresh. A source change replaces the reading only after a
   second agent verifies the new aggregate and method.

The first pilot can use only the 8,000-token prompt, 10 measured calls, and
three warm-ups per offering. Its purpose is to validate authentication,
stream parsing, token accounting, and the retained source format. It should
not enter a decision snapshot.

The full baseline should use one fixed client region for globally named
offerings. Region-specific offerings need a runner in the named region and a
method label that prevents direct comparison with another client region.
A later approved dual-region run can measure geographic sensitivity.

## Cost

The 38 current offering files have a combined list price of $144.662 per one
million input tokens and $715.26 per one million output tokens. Those figures
were read from the verified offering facts on 2026-09-28.

The full single-region baseline uses 90 measured calls per offering. For each
offering it sends 1.23 million input tokens and requests 23,040 output tokens.
At current list prices, the measured calls cost about $194.41. Three warm-up
calls per prompt size add about 10 percent, for $213.85 total. A $270 approval
cap leaves roughly 25 percent for reasoning tokens, tokenization differences,
and bounded retries after transport failures.

The 8,000-input, 256-output pilot costs about $13.40 for ten measured calls
per offering. Three warm-ups raise that to about $17.42. A $25 approval cap is
enough for the pilot. A dual-region full run approximately doubles provider
charges, so its separate approval cap should be $540. Small cloud-runner and
log-storage charges should remain under $5 per region, but the implementation
must estimate them again when Jamie approves the run.

No API calls should run until Jamie approves the exact offering set, method,
client regions, paid keys, and spending cap.
