Adds `/orchestrators/` with a system-prompt block, a registry-backed worked Spec, bounded-answer guidance, keyed MCP setup, and config-export commands. Registers the page in the live build, sitemap, JSON-LD, agent guide, and `llms.txt`.

The CI follow-up regenerates OpenAPI and refreshes the deliberate flag-off byte baseline, dependent QA captures, and preview-page fixture. The audit compares against `0afd269c` with `DECISION_LINK_ENABLED=false`. The guide diff is:

```diff
--- base/docs/agents.md
+++ current/docs/agents.md
@@ -3 +3 @@
-Guide version: 1-31f80fb67e121e42.
+Guide version: 1-79cf5b6e5f3bf838.
@@ -17,0 +18 @@
+Orchestrator system prompt and worked Spec: https://modelspec.dev/orchestrators/.
```

The pointer is the only added prose. MCP JSON embeds the same pointer in `context_guide` and propagates the derived version through `guide_version` and `instructions`. Undoing that pointer and derived version changes restores the complete old guide and MCP bytes. Every other MCP field is unchanged, and CLI text is byte-identical. The fixed MCP hash changes from `408bf5a9...` to `2d036788...`; the guide hash changes from `b6b32730...` to `86de2926...`. No assertion was removed or weakened, and all disabled-response hashes remain unchanged.

Validation: the full Python suite passed with **11,227 passed, nine skipped, exit 0**. All 15 actual landing and social-card Chromium cases ran and passed. The 277 focused tests passed with two live-API tests skipped. OpenAPI freshness, vendor isolation, the Wrangler 4.139.0 dry run, and the built Worker's 74-module import graph passed.

[Round-two evidence and complete byte hashes](https://github.com/turbobeest/modelspec/blob/model-orchestrator-recipe/docs/evidence/g2-ios/MODEL-orchestrator-recipe-r2-fix.md).

Executed by ChatGPT Codex (GPT-6.1 Sol); cross-model review by Claude Opus pending.
