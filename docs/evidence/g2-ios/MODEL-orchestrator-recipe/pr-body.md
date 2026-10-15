Adds `/orchestrators/` with a system-prompt block, a Spec generated from `coding-balanced`, bounded-answer handling, keyed MCP setup, and router-config exports. Registers the page in the live build, sitemap, and breadcrumb JSON-LD, with pointers from `agents.md` and `llms.txt`.

Validation: all six recipe tests pass, including parsing every displayed CLI command with the actual parser and validating the Spec against bundled `DecideRequest`. Both site builds pass. The web suite passes 843 tests; the browser corpus passes 27 with eight existing flag-dependent skips. Chromium checks pass at desktop and phone widths with JavaScript disabled.

The required full Python suite reports 11,161 passed, 66 failed, and nine skipped. Validation is blocked on dependent guide-version metadata, byte-hash pins, and a stand-in page fixture across five files outside the spec's named paths. Scope approval was requested under CODEX-EXEC.md; those files remain unchanged. A concrete, unapplied refresh patch and the complete results are in the [execution evidence](https://github.com/turbobeest/modelspec/blob/model-orchestrator-recipe/docs/evidence/g2-ios/MODEL-orchestrator-recipe-fix.md). This draft is not ready for merge.

Executed by ChatGPT Codex (GPT-6.1 Sol); cross-model review by Claude Opus pending.
