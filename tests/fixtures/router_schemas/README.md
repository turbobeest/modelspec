# Router config schemas (MODEL-208)

Each tool's own published schema, vendored so the tests run offline and in CI.
`tests/test_decision_router_config.py` validates `modelspec decide
--emit-router-config` output against them.

| File | Source | Read |
| --- | --- | --- |
| `litellm-config-yaml.schema.json` | `ConfigYAML.model_json_schema()` from `litellm.proxy._types`, litellm 1.103.0 (PyPI). The proxy's Swagger `/#/config.yaml` publishes the same model. | 2026-09-29 |
| `openrouter-create-guardrail-request.schema.json` | `components.schemas.CreateGuardrailRequest` and the schemas it references, from https://openrouter.ai/openapi.json (OpenAPI 3.1). `#/components/schemas/` refs are rewritten to `#/$defs/`. | 2026-09-29 |

To refresh, regenerate from a newer release and rerun the tests. When litellm
is installed, two further tests load the emitted config through LiteLLM's own
`ProxyConfig.load_config` and check every provider prefix against
`litellm.provider_list`.
