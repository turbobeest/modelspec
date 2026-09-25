# MODEL-143 round-2 source audit

Read on 2026-09-25. All sources are first-party lab documentation, announcements,
commercial terms, licence texts, or lab-controlled weight repositories.

## Before and after by facet

| Facet | Before | After |
|---|---:|---:|
| `feature.batch` | 16 | 16 |
| `feature.effort_controls` | 12 | 7 |
| `feature.streaming` | 24 | 8 |
| `feature.structured_output` | 19 | 7 |
| `feature.tool_calling` | 19 | 7 |
| `licence.commercial_use` | 32 | 4 |
| `licence.fine_tuning` | 32 | 5 |
| `licence.output_training` | 32 | 5 |
| `licence.user_cap` | 32 | 5 |
| `model.context_window` | 18 | 0 |
| `model.input_modalities` | 32 | 0 |
| `model.max_output_tokens` | 22 | 13 |
| `model.output_modalities` | 32 | 0 |
| `model.release_date` | 32 | 1 |
| `model.weights_openness` | 20 | 0 |
| `origin.base_lineage` | 32 | 27 |
| `origin.lab_jurisdiction` | 32 | 12 |
| `origin.weights_hosting` | 32 | 32 |

Total: 470 before, 149 after.

## Remaining `not_disclosed` facts

### `anthropic/claude-fable-5`

- `origin.base_lineage`: checked `model-143-anthropic-claude-fable-5`, `model-143-anthropic-models-overview`, `model-143-anthropic-structured-outputs`, `model-143-anthropic-streaming`, `model-143-anthropic-commercial-terms`
- `origin.weights_hosting`: checked `model-143-anthropic-claude-fable-5`, `model-143-anthropic-models-overview`, `model-143-anthropic-structured-outputs`, `model-143-anthropic-streaming`, `model-143-anthropic-commercial-terms`

### `anthropic/claude-fable-5-1`

- `origin.base_lineage`: checked `model-143-anthropic-claude-fable-5-1`, `model-143-anthropic-models-overview`, `model-143-anthropic-structured-outputs`, `model-143-anthropic-streaming`, `model-143-anthropic-commercial-terms`
- `origin.weights_hosting`: checked `model-143-anthropic-claude-fable-5-1`, `model-143-anthropic-models-overview`, `model-143-anthropic-structured-outputs`, `model-143-anthropic-streaming`, `model-143-anthropic-commercial-terms`

### `anthropic/claude-opus-4-6`

- `origin.base_lineage`: checked `model-143-anthropic-claude-opus-4-6`, `model-143-anthropic-models-overview`, `model-143-anthropic-structured-outputs`, `model-143-anthropic-streaming`, `model-143-anthropic-commercial-terms`
- `origin.weights_hosting`: checked `model-143-anthropic-claude-opus-4-6`, `model-143-anthropic-models-overview`, `model-143-anthropic-structured-outputs`, `model-143-anthropic-streaming`, `model-143-anthropic-commercial-terms`

### `anthropic/claude-opus-4-7`

- `origin.base_lineage`: checked `model-143-anthropic-claude-opus-4-7`, `model-143-anthropic-models-overview`, `model-143-anthropic-structured-outputs`, `model-143-anthropic-streaming`, `model-143-anthropic-commercial-terms`
- `origin.weights_hosting`: checked `model-143-anthropic-claude-opus-4-7`, `model-143-anthropic-models-overview`, `model-143-anthropic-structured-outputs`, `model-143-anthropic-streaming`, `model-143-anthropic-commercial-terms`

### `anthropic/claude-opus-5`

- `origin.base_lineage`: checked `model-143-anthropic-claude-opus-5`, `model-143-anthropic-models-overview`, `model-143-anthropic-structured-outputs`, `model-143-anthropic-streaming`, `model-143-anthropic-commercial-terms`
- `origin.weights_hosting`: checked `model-143-anthropic-claude-opus-5`, `model-143-anthropic-models-overview`, `model-143-anthropic-structured-outputs`, `model-143-anthropic-streaming`, `model-143-anthropic-commercial-terms`

### `anthropic/claude-opus-5-5`

- `origin.base_lineage`: checked `model-143-anthropic-claude-opus-5-5`, `model-143-anthropic-models-overview`, `model-143-anthropic-structured-outputs`, `model-143-anthropic-streaming`, `model-143-anthropic-commercial-terms`
- `origin.weights_hosting`: checked `model-143-anthropic-claude-opus-5-5`, `model-143-anthropic-models-overview`, `model-143-anthropic-structured-outputs`, `model-143-anthropic-streaming`, `model-143-anthropic-commercial-terms`

### `deepseek/deepseek-v4-pro`

- `model.max_output_tokens`: checked `model-143-deepseek-deepseek-v4-pro`, `model-143-deepseek-function-calling`, `model-143-deepseek-json-output`, `model-143-deepseek-streaming`, `model-143-deepseek-v4-license`, `model-143-hf-metadata-deepseek-deepseek-v4-pro`
- `origin.lab_jurisdiction`: checked `model-143-deepseek-deepseek-v4-pro`, `model-143-deepseek-function-calling`, `model-143-deepseek-json-output`, `model-143-deepseek-streaming`, `model-143-deepseek-v4-license`, `model-143-hf-metadata-deepseek-deepseek-v4-pro`
- `origin.base_lineage`: checked `model-143-deepseek-deepseek-v4-pro`, `model-143-deepseek-function-calling`, `model-143-deepseek-json-output`, `model-143-deepseek-streaming`, `model-143-deepseek-v4-license`, `model-143-hf-metadata-deepseek-deepseek-v4-pro`
- `origin.weights_hosting`: checked `model-143-deepseek-deepseek-v4-pro`, `model-143-deepseek-function-calling`, `model-143-deepseek-json-output`, `model-143-deepseek-streaming`, `model-143-deepseek-v4-license`, `model-143-hf-metadata-deepseek-deepseek-v4-pro`
- `feature.batch`: checked `model-143-deepseek-deepseek-v4-pro`, `model-143-deepseek-function-calling`, `model-143-deepseek-json-output`, `model-143-deepseek-streaming`, `model-143-deepseek-v4-license`, `model-143-hf-metadata-deepseek-deepseek-v4-pro`

### `google/gemini-3-1-pro-preview`

- `origin.base_lineage`: checked `model-143-google-gemini-3-1-pro-preview`, `model-143-google-deprecations`, `model-143-google-streaming`, `model-143-google-terms`, `model-143-google-company`, `model-143-google-sec`
- `origin.weights_hosting`: checked `model-143-google-gemini-3-1-pro-preview`, `model-143-google-deprecations`, `model-143-google-streaming`, `model-143-google-terms`, `model-143-google-company`, `model-143-google-sec`

### `google/gemini-3-5-flash`

- `origin.base_lineage`: checked `model-143-google-gemini-3-5-flash`, `model-143-google-deprecations`, `model-143-google-streaming`, `model-143-google-terms`, `model-143-google-company`, `model-143-google-sec`
- `origin.weights_hosting`: checked `model-143-google-gemini-3-5-flash`, `model-143-google-deprecations`, `model-143-google-streaming`, `model-143-google-terms`, `model-143-google-company`, `model-143-google-sec`

### `google/gemini-3-7-flash`

- `origin.base_lineage`: checked `model-143-google-gemini-3-7-flash`, `model-143-google-deprecations`, `model-143-google-streaming`, `model-143-google-terms`, `model-143-google-company`, `model-143-google-sec`
- `origin.weights_hosting`: checked `model-143-google-gemini-3-7-flash`, `model-143-google-deprecations`, `model-143-google-streaming`, `model-143-google-terms`, `model-143-google-company`, `model-143-google-sec`

### `google/gemini-3-8-flash`

- `origin.base_lineage`: checked `model-143-google-gemini-3-8-flash`, `model-143-google-deprecations`, `model-143-google-streaming`, `model-143-google-terms`, `model-143-google-company`, `model-143-google-sec`
- `origin.weights_hosting`: checked `model-143-google-gemini-3-8-flash`, `model-143-google-deprecations`, `model-143-google-streaming`, `model-143-google-terms`, `model-143-google-company`, `model-143-google-sec`

### `jcorners/ingot-8b-r3`

- `model.max_output_tokens`: checked `model-143-jcorners-ingot-8b-r3`, `model-143-hf-metadata-jcorners-ingot-8b-r3`
- `licence.user_cap`: checked `model-143-jcorners-ingot-8b-r3`, `model-143-hf-metadata-jcorners-ingot-8b-r3`
- `licence.output_training`: checked `model-143-jcorners-ingot-8b-r3`, `model-143-hf-metadata-jcorners-ingot-8b-r3`
- `licence.fine_tuning`: checked `model-143-jcorners-ingot-8b-r3`, `model-143-hf-metadata-jcorners-ingot-8b-r3`
- `origin.weights_hosting`: checked `model-143-jcorners-ingot-8b-r3`, `model-143-hf-metadata-jcorners-ingot-8b-r3`
- `feature.tool_calling`: checked `model-143-jcorners-ingot-8b-r3`, `model-143-hf-metadata-jcorners-ingot-8b-r3`
- `feature.structured_output`: checked `model-143-jcorners-ingot-8b-r3`, `model-143-hf-metadata-jcorners-ingot-8b-r3`
- `feature.effort_controls`: checked `model-143-jcorners-ingot-8b-r3`, `model-143-hf-metadata-jcorners-ingot-8b-r3`
- `feature.batch`: checked `model-143-jcorners-ingot-8b-r3`, `model-143-hf-metadata-jcorners-ingot-8b-r3`
- `feature.streaming`: checked `model-143-jcorners-ingot-8b-r3`, `model-143-hf-metadata-jcorners-ingot-8b-r3`

### `kingsoft/qzhou-embedding`

- `model.max_output_tokens`: checked `model-143-kingsoft-qzhou-embedding`, `model-143-apache-2-license`, `model-143-hf-metadata-kingsoft-qzhou-embedding`
- `origin.lab_jurisdiction`: checked `model-143-kingsoft-qzhou-embedding`, `model-143-apache-2-license`, `model-143-hf-metadata-kingsoft-qzhou-embedding`
- `origin.weights_hosting`: checked `model-143-kingsoft-qzhou-embedding`, `model-143-apache-2-license`, `model-143-hf-metadata-kingsoft-qzhou-embedding`
- `feature.tool_calling`: checked `model-143-kingsoft-qzhou-embedding`, `model-143-apache-2-license`, `model-143-hf-metadata-kingsoft-qzhou-embedding`
- `feature.structured_output`: checked `model-143-kingsoft-qzhou-embedding`, `model-143-apache-2-license`, `model-143-hf-metadata-kingsoft-qzhou-embedding`
- `feature.effort_controls`: checked `model-143-kingsoft-qzhou-embedding`, `model-143-apache-2-license`, `model-143-hf-metadata-kingsoft-qzhou-embedding`
- `feature.batch`: checked `model-143-kingsoft-qzhou-embedding`, `model-143-apache-2-license`, `model-143-hf-metadata-kingsoft-qzhou-embedding`
- `feature.streaming`: checked `model-143-kingsoft-qzhou-embedding`, `model-143-apache-2-license`, `model-143-hf-metadata-kingsoft-qzhou-embedding`

### `meta/muse-spark`

- `model.max_output_tokens`: checked `model-143-meta-muse-spark`, `model-143-meta-release-index`, `model-143-meta-model-api`, `model-143-meta-company`, `model-143-meta-sec`
- `licence.commercial_use`: checked `model-143-meta-muse-spark`, `model-143-meta-release-index`, `model-143-meta-model-api`, `model-143-meta-company`, `model-143-meta-sec`
- `licence.user_cap`: checked `model-143-meta-muse-spark`, `model-143-meta-release-index`, `model-143-meta-model-api`, `model-143-meta-company`, `model-143-meta-sec`
- `licence.output_training`: checked `model-143-meta-muse-spark`, `model-143-meta-release-index`, `model-143-meta-model-api`, `model-143-meta-company`, `model-143-meta-sec`
- `licence.fine_tuning`: checked `model-143-meta-muse-spark`, `model-143-meta-release-index`, `model-143-meta-model-api`, `model-143-meta-company`, `model-143-meta-sec`
- `origin.base_lineage`: checked `model-143-meta-muse-spark`, `model-143-meta-release-index`, `model-143-meta-model-api`, `model-143-meta-company`, `model-143-meta-sec`
- `origin.weights_hosting`: checked `model-143-meta-muse-spark`, `model-143-meta-release-index`, `model-143-meta-model-api`, `model-143-meta-company`, `model-143-meta-sec`
- `feature.batch`: checked `model-143-meta-muse-spark`, `model-143-meta-release-index`, `model-143-meta-model-api`, `model-143-meta-company`, `model-143-meta-sec`

### `meta/muse-spark-1-1`

- `model.max_output_tokens`: checked `model-143-meta-muse-spark-1-1`, `model-143-meta-release-index`, `model-143-meta-model-api`, `model-143-meta-company`, `model-143-meta-sec`
- `licence.commercial_use`: checked `model-143-meta-muse-spark-1-1`, `model-143-meta-release-index`, `model-143-meta-model-api`, `model-143-meta-company`, `model-143-meta-sec`
- `licence.user_cap`: checked `model-143-meta-muse-spark-1-1`, `model-143-meta-release-index`, `model-143-meta-model-api`, `model-143-meta-company`, `model-143-meta-sec`
- `licence.output_training`: checked `model-143-meta-muse-spark-1-1`, `model-143-meta-release-index`, `model-143-meta-model-api`, `model-143-meta-company`, `model-143-meta-sec`
- `licence.fine_tuning`: checked `model-143-meta-muse-spark-1-1`, `model-143-meta-release-index`, `model-143-meta-model-api`, `model-143-meta-company`, `model-143-meta-sec`
- `origin.base_lineage`: checked `model-143-meta-muse-spark-1-1`, `model-143-meta-release-index`, `model-143-meta-model-api`, `model-143-meta-company`, `model-143-meta-sec`
- `origin.weights_hosting`: checked `model-143-meta-muse-spark-1-1`, `model-143-meta-release-index`, `model-143-meta-model-api`, `model-143-meta-company`, `model-143-meta-sec`
- `feature.batch`: checked `model-143-meta-muse-spark-1-1`, `model-143-meta-release-index`, `model-143-meta-model-api`, `model-143-meta-company`, `model-143-meta-sec`

### `meta/muse-spark-1-3`

- `model.max_output_tokens`: checked `model-143-meta-muse-spark-1-3`, `model-143-meta-release-index`, `model-143-meta-model-api`, `model-143-meta-company`, `model-143-meta-sec`
- `licence.commercial_use`: checked `model-143-meta-muse-spark-1-3`, `model-143-meta-release-index`, `model-143-meta-model-api`, `model-143-meta-company`, `model-143-meta-sec`
- `licence.user_cap`: checked `model-143-meta-muse-spark-1-3`, `model-143-meta-release-index`, `model-143-meta-model-api`, `model-143-meta-company`, `model-143-meta-sec`
- `licence.output_training`: checked `model-143-meta-muse-spark-1-3`, `model-143-meta-release-index`, `model-143-meta-model-api`, `model-143-meta-company`, `model-143-meta-sec`
- `licence.fine_tuning`: checked `model-143-meta-muse-spark-1-3`, `model-143-meta-release-index`, `model-143-meta-model-api`, `model-143-meta-company`, `model-143-meta-sec`
- `origin.base_lineage`: checked `model-143-meta-muse-spark-1-3`, `model-143-meta-release-index`, `model-143-meta-model-api`, `model-143-meta-company`, `model-143-meta-sec`
- `origin.weights_hosting`: checked `model-143-meta-muse-spark-1-3`, `model-143-meta-release-index`, `model-143-meta-model-api`, `model-143-meta-company`, `model-143-meta-sec`
- `feature.batch`: checked `model-143-meta-muse-spark-1-3`, `model-143-meta-release-index`, `model-143-meta-model-api`, `model-143-meta-company`, `model-143-meta-sec`

### `microsoft/harrier-oss-v1-27b`

- `model.max_output_tokens`: checked `model-143-microsoft-harrier-oss-v1-27b`, `model-143-mit-license`, `model-143-hf-metadata-microsoft-harrier-oss-v1-27b`
- `origin.lab_jurisdiction`: checked `model-143-microsoft-harrier-oss-v1-27b`, `model-143-mit-license`, `model-143-hf-metadata-microsoft-harrier-oss-v1-27b`
- `origin.base_lineage`: checked `model-143-microsoft-harrier-oss-v1-27b`, `model-143-mit-license`, `model-143-hf-metadata-microsoft-harrier-oss-v1-27b`
- `origin.weights_hosting`: checked `model-143-microsoft-harrier-oss-v1-27b`, `model-143-mit-license`, `model-143-hf-metadata-microsoft-harrier-oss-v1-27b`
- `feature.tool_calling`: checked `model-143-microsoft-harrier-oss-v1-27b`, `model-143-mit-license`, `model-143-hf-metadata-microsoft-harrier-oss-v1-27b`
- `feature.structured_output`: checked `model-143-microsoft-harrier-oss-v1-27b`, `model-143-mit-license`, `model-143-hf-metadata-microsoft-harrier-oss-v1-27b`
- `feature.effort_controls`: checked `model-143-microsoft-harrier-oss-v1-27b`, `model-143-mit-license`, `model-143-hf-metadata-microsoft-harrier-oss-v1-27b`
- `feature.batch`: checked `model-143-microsoft-harrier-oss-v1-27b`, `model-143-mit-license`, `model-143-hf-metadata-microsoft-harrier-oss-v1-27b`
- `feature.streaming`: checked `model-143-microsoft-harrier-oss-v1-27b`, `model-143-mit-license`, `model-143-hf-metadata-microsoft-harrier-oss-v1-27b`

### `moonshot/kimi-k2-6`

- `origin.lab_jurisdiction`: checked `model-143-moonshot-kimi-k2-6`, `model-143-kimi-k2-6-guide`, `model-143-kimi-k3-guide`, `model-143-kimi-k2-6-license`, `model-143-hf-metadata-moonshot-kimi-k2-6`
- `origin.base_lineage`: checked `model-143-moonshot-kimi-k2-6`, `model-143-kimi-k2-6-guide`, `model-143-kimi-k3-guide`, `model-143-kimi-k2-6-license`, `model-143-hf-metadata-moonshot-kimi-k2-6`
- `origin.weights_hosting`: checked `model-143-moonshot-kimi-k2-6`, `model-143-kimi-k2-6-guide`, `model-143-kimi-k3-guide`, `model-143-kimi-k2-6-license`, `model-143-hf-metadata-moonshot-kimi-k2-6`
- `feature.batch`: checked `model-143-moonshot-kimi-k2-6`, `model-143-kimi-k2-6-guide`, `model-143-kimi-k3-guide`, `model-143-kimi-k2-6-license`, `model-143-hf-metadata-moonshot-kimi-k2-6`

### `moonshot/kimi-k3`

- `origin.lab_jurisdiction`: checked `model-143-moonshot-kimi-k3`, `model-143-kimi-k2-6-guide`, `model-143-kimi-k3-guide`, `model-143-kimi-k3-license`, `model-143-hf-metadata-moonshot-kimi-k3`
- `origin.base_lineage`: checked `model-143-moonshot-kimi-k3`, `model-143-kimi-k2-6-guide`, `model-143-kimi-k3-guide`, `model-143-kimi-k3-license`, `model-143-hf-metadata-moonshot-kimi-k3`
- `origin.weights_hosting`: checked `model-143-moonshot-kimi-k3`, `model-143-kimi-k2-6-guide`, `model-143-kimi-k3-guide`, `model-143-kimi-k3-license`, `model-143-hf-metadata-moonshot-kimi-k3`
- `feature.batch`: checked `model-143-moonshot-kimi-k3`, `model-143-kimi-k2-6-guide`, `model-143-kimi-k3-guide`, `model-143-kimi-k3-license`, `model-143-hf-metadata-moonshot-kimi-k3`

### `openai/gpt-5-4`

- `origin.base_lineage`: checked `model-143-openai-gpt-5-4`, `model-143-openai-models-overview`, `model-143-openai-changelog`, `model-143-openai-reasoning`, `model-143-openai-services-agreement`
- `origin.weights_hosting`: checked `model-143-openai-gpt-5-4`, `model-143-openai-models-overview`, `model-143-openai-changelog`, `model-143-openai-reasoning`, `model-143-openai-services-agreement`

### `openai/gpt-5-6-sol`

- `origin.base_lineage`: checked `model-143-openai-gpt-5-6-sol`, `model-143-openai-models-overview`, `model-143-openai-changelog`, `model-143-openai-reasoning`, `model-143-openai-services-agreement`
- `origin.weights_hosting`: checked `model-143-openai-gpt-5-6-sol`, `model-143-openai-models-overview`, `model-143-openai-changelog`, `model-143-openai-reasoning`, `model-143-openai-services-agreement`

### `openai/gpt-6-astra`

- `origin.base_lineage`: checked `model-143-openai-gpt-6-astra`, `model-143-openai-models-overview`, `model-143-openai-changelog`, `model-143-openai-reasoning`, `model-143-openai-services-agreement`
- `origin.weights_hosting`: checked `model-143-openai-gpt-6-astra`, `model-143-openai-models-overview`, `model-143-openai-changelog`, `model-143-openai-reasoning`, `model-143-openai-services-agreement`

### `openai/gpt-6-sol`

- `origin.base_lineage`: checked `model-143-openai-gpt-6-sol`, `model-143-openai-models-overview`, `model-143-openai-changelog`, `model-143-openai-reasoning`, `model-143-openai-services-agreement`
- `origin.weights_hosting`: checked `model-143-openai-gpt-6-sol`, `model-143-openai-models-overview`, `model-143-openai-changelog`, `model-143-openai-reasoning`, `model-143-openai-services-agreement`

### `querit/querit`

- `model.max_output_tokens`: checked `model-143-querit-querit`, `model-143-apache-2-license`, `model-143-hf-metadata-querit-querit`
- `origin.lab_jurisdiction`: checked `model-143-querit-querit`, `model-143-apache-2-license`, `model-143-hf-metadata-querit-querit`
- `origin.base_lineage`: checked `model-143-querit-querit`, `model-143-apache-2-license`, `model-143-hf-metadata-querit-querit`
- `origin.weights_hosting`: checked `model-143-querit-querit`, `model-143-apache-2-license`, `model-143-hf-metadata-querit-querit`
- `feature.tool_calling`: checked `model-143-querit-querit`, `model-143-apache-2-license`, `model-143-hf-metadata-querit-querit`
- `feature.structured_output`: checked `model-143-querit-querit`, `model-143-apache-2-license`, `model-143-hf-metadata-querit-querit`
- `feature.effort_controls`: checked `model-143-querit-querit`, `model-143-apache-2-license`, `model-143-hf-metadata-querit-querit`
- `feature.batch`: checked `model-143-querit-querit`, `model-143-apache-2-license`, `model-143-hf-metadata-querit-querit`
- `feature.streaming`: checked `model-143-querit-querit`, `model-143-apache-2-license`, `model-143-hf-metadata-querit-querit`

### `querit/querit-4b`

- `model.max_output_tokens`: checked `model-143-querit-querit-4b`, `model-143-apache-2-license`, `model-143-hf-metadata-querit-querit-4b`
- `origin.lab_jurisdiction`: checked `model-143-querit-querit-4b`, `model-143-apache-2-license`, `model-143-hf-metadata-querit-querit-4b`
- `origin.weights_hosting`: checked `model-143-querit-querit-4b`, `model-143-apache-2-license`, `model-143-hf-metadata-querit-querit-4b`
- `feature.tool_calling`: checked `model-143-querit-querit-4b`, `model-143-apache-2-license`, `model-143-hf-metadata-querit-querit-4b`
- `feature.structured_output`: checked `model-143-querit-querit-4b`, `model-143-apache-2-license`, `model-143-hf-metadata-querit-querit-4b`
- `feature.effort_controls`: checked `model-143-querit-querit-4b`, `model-143-apache-2-license`, `model-143-hf-metadata-querit-querit-4b`
- `feature.batch`: checked `model-143-querit-querit-4b`, `model-143-apache-2-license`, `model-143-hf-metadata-querit-querit-4b`
- `feature.streaming`: checked `model-143-querit-querit-4b`, `model-143-apache-2-license`, `model-143-hf-metadata-querit-querit-4b`

### `qwen/qwen3-8-flash-next`

- `model.max_output_tokens`: checked `model-143-qwen-qwen3-8-flash-next`, `model-143-alibaba-modelstudio-terms`, `model-143-qwen3-8-flash-next-license`, `model-143-hf-metadata-qwen-qwen3-8-flash-next`
- `origin.lab_jurisdiction`: checked `model-143-qwen-qwen3-8-flash-next`, `model-143-alibaba-modelstudio-terms`, `model-143-qwen3-8-flash-next-license`, `model-143-hf-metadata-qwen-qwen3-8-flash-next`
- `origin.base_lineage`: checked `model-143-qwen-qwen3-8-flash-next`, `model-143-alibaba-modelstudio-terms`, `model-143-qwen3-8-flash-next-license`, `model-143-hf-metadata-qwen-qwen3-8-flash-next`
- `origin.weights_hosting`: checked `model-143-qwen-qwen3-8-flash-next`, `model-143-alibaba-modelstudio-terms`, `model-143-qwen3-8-flash-next-license`, `model-143-hf-metadata-qwen-qwen3-8-flash-next`
- `feature.structured_output`: checked `model-143-qwen-qwen3-8-flash-next`, `model-143-alibaba-modelstudio-terms`, `model-143-qwen3-8-flash-next-license`, `model-143-hf-metadata-qwen-qwen3-8-flash-next`
- `feature.batch`: checked `model-143-qwen-qwen3-8-flash-next`, `model-143-alibaba-modelstudio-terms`, `model-143-qwen3-8-flash-next-license`, `model-143-hf-metadata-qwen-qwen3-8-flash-next`
- `feature.streaming`: checked `model-143-qwen-qwen3-8-flash-next`, `model-143-alibaba-modelstudio-terms`, `model-143-qwen3-8-flash-next-license`, `model-143-hf-metadata-qwen-qwen3-8-flash-next`

### `qwen/qwen3-8-max-0902`

- `origin.lab_jurisdiction`: checked `model-143-qwen-qwen3-8-max-0902`, `model-143-alibaba-modelstudio-terms`
- `origin.base_lineage`: checked `model-143-qwen-qwen3-8-max-0902`, `model-143-alibaba-modelstudio-terms`
- `origin.weights_hosting`: checked `model-143-qwen-qwen3-8-max-0902`, `model-143-alibaba-modelstudio-terms`

### `tencent/kalm-embedding-gemma3-12b-2511`

- `model.max_output_tokens`: checked `model-143-tencent-kalm-embedding-gemma3-12b-2511`, `model-143-kalm-license`, `model-143-hf-metadata-tencent-kalm-embedding-gemma3-12b-2511`
- `origin.lab_jurisdiction`: checked `model-143-tencent-kalm-embedding-gemma3-12b-2511`, `model-143-kalm-license`, `model-143-hf-metadata-tencent-kalm-embedding-gemma3-12b-2511`
- `origin.weights_hosting`: checked `model-143-tencent-kalm-embedding-gemma3-12b-2511`, `model-143-kalm-license`, `model-143-hf-metadata-tencent-kalm-embedding-gemma3-12b-2511`
- `feature.tool_calling`: checked `model-143-tencent-kalm-embedding-gemma3-12b-2511`, `model-143-kalm-license`, `model-143-hf-metadata-tencent-kalm-embedding-gemma3-12b-2511`
- `feature.structured_output`: checked `model-143-tencent-kalm-embedding-gemma3-12b-2511`, `model-143-kalm-license`, `model-143-hf-metadata-tencent-kalm-embedding-gemma3-12b-2511`
- `feature.effort_controls`: checked `model-143-tencent-kalm-embedding-gemma3-12b-2511`, `model-143-kalm-license`, `model-143-hf-metadata-tencent-kalm-embedding-gemma3-12b-2511`
- `feature.batch`: checked `model-143-tencent-kalm-embedding-gemma3-12b-2511`, `model-143-kalm-license`, `model-143-hf-metadata-tencent-kalm-embedding-gemma3-12b-2511`
- `feature.streaming`: checked `model-143-tencent-kalm-embedding-gemma3-12b-2511`, `model-143-kalm-license`, `model-143-hf-metadata-tencent-kalm-embedding-gemma3-12b-2511`

### `typesafe/jev-1-13`

- `model.max_output_tokens`: checked `model-143-typesafe-jev-1-13`, `model-143-typesafe-models`, `model-143-typesafe-system-one`, `model-143-typesafe-terms`
- `licence.commercial_use`: checked `model-143-typesafe-jev-1-13`, `model-143-typesafe-models`, `model-143-typesafe-system-one`, `model-143-typesafe-terms`
- `licence.user_cap`: checked `model-143-typesafe-jev-1-13`, `model-143-typesafe-models`, `model-143-typesafe-system-one`, `model-143-typesafe-terms`
- `licence.output_training`: checked `model-143-typesafe-jev-1-13`, `model-143-typesafe-models`, `model-143-typesafe-system-one`, `model-143-typesafe-terms`
- `licence.fine_tuning`: checked `model-143-typesafe-jev-1-13`, `model-143-typesafe-models`, `model-143-typesafe-system-one`, `model-143-typesafe-terms`
- `origin.base_lineage`: checked `model-143-typesafe-jev-1-13`, `model-143-typesafe-models`, `model-143-typesafe-system-one`, `model-143-typesafe-terms`
- `origin.weights_hosting`: checked `model-143-typesafe-jev-1-13`, `model-143-typesafe-models`, `model-143-typesafe-system-one`, `model-143-typesafe-terms`
- `model.release_date`: checked `model-143-typesafe-jev-1-13`, `model-143-typesafe-models`, `model-143-typesafe-system-one`, `model-143-typesafe-terms`
- `feature.tool_calling`: checked `model-143-typesafe-jev-1-13`, `model-143-typesafe-models`, `model-143-typesafe-system-one`, `model-143-typesafe-terms`
- `feature.effort_controls`: checked `model-143-typesafe-jev-1-13`, `model-143-typesafe-models`, `model-143-typesafe-system-one`, `model-143-typesafe-terms`
- `feature.batch`: checked `model-143-typesafe-jev-1-13`, `model-143-typesafe-models`, `model-143-typesafe-system-one`, `model-143-typesafe-terms`
- `feature.streaming`: checked `model-143-typesafe-jev-1-13`, `model-143-typesafe-models`, `model-143-typesafe-system-one`, `model-143-typesafe-terms`

### `xai/grok-4-7`

- `model.max_output_tokens`: checked `model-143-xai-grok-4-7`, `model-143-xai-function-calling`, `model-143-xai-structured-outputs`, `model-143-xai-enterprise-terms`, `model-143-xai-enterprise-faq`
- `origin.base_lineage`: checked `model-143-xai-grok-4-7`, `model-143-xai-function-calling`, `model-143-xai-structured-outputs`, `model-143-xai-enterprise-terms`, `model-143-xai-enterprise-faq`
- `origin.weights_hosting`: checked `model-143-xai-grok-4-7`, `model-143-xai-function-calling`, `model-143-xai-structured-outputs`, `model-143-xai-enterprise-terms`, `model-143-xai-enterprise-faq`

### `zhipu/glm-5-2`

- `origin.lab_jurisdiction`: checked `model-143-zhipu-glm-5-2`, `model-143-zai-glm-5-2-guide`, `model-143-zai-glm-5-3-guide`, `model-143-mit-license`, `model-143-hf-metadata-zhipu-glm-5-2`
- `origin.base_lineage`: checked `model-143-zhipu-glm-5-2`, `model-143-zai-glm-5-2-guide`, `model-143-zai-glm-5-3-guide`, `model-143-mit-license`, `model-143-hf-metadata-zhipu-glm-5-2`
- `origin.weights_hosting`: checked `model-143-zhipu-glm-5-2`, `model-143-zai-glm-5-2-guide`, `model-143-zai-glm-5-3-guide`, `model-143-mit-license`, `model-143-hf-metadata-zhipu-glm-5-2`
- `feature.batch`: checked `model-143-zhipu-glm-5-2`, `model-143-zai-glm-5-2-guide`, `model-143-zai-glm-5-3-guide`, `model-143-mit-license`, `model-143-hf-metadata-zhipu-glm-5-2`

### `zhipu/glm-5-3`

- `origin.lab_jurisdiction`: checked `model-143-zhipu-glm-5-3`, `model-143-zai-glm-5-2-guide`, `model-143-zai-glm-5-3-guide`, `model-143-glm-5-3-license`, `model-143-hf-metadata-zhipu-glm-5-3`
- `origin.weights_hosting`: checked `model-143-zhipu-glm-5-3`, `model-143-zai-glm-5-2-guide`, `model-143-zai-glm-5-3-guide`, `model-143-glm-5-3-license`, `model-143-hf-metadata-zhipu-glm-5-3`
- `feature.batch`: checked `model-143-zhipu-glm-5-3`, `model-143-zai-glm-5-2-guide`, `model-143-zai-glm-5-3-guide`, `model-143-glm-5-3-license`, `model-143-hf-metadata-zhipu-glm-5-3`

## Verification

- Fresh two-key pass: 640 verified fact values, 0 mismatch, 0 unreachable, and 0 pending.
- Completeness gate: the 1,366-candidate decision snapshot built successfully.
- Full suite: 2,716 passed, 8 skipped, and 1 xpassed.
- Ruff and `git diff --check`: passed.
- Firecrawl: 2 credits in round 2, 3 across the PR; all other reads used plain HTTP.

Round 1 also corrected the retained Arena scores from the CC BY 4.0
`lmarena-ai/leaderboard-dataset` snapshot dated 2026-09-24.

Written by GPT-5 (OpenAI Codex).
