Perplexity Pro facts remain **Cited, not machine-verified**, with all 24 Perplexity fact values and states unchanged. This PR removes the copied FAQ passage and model-list comment introduced by MODEL-368. It preserves source URLs and hashes, plus the recorded retrieval day, and adds the one exact original fetch timestamp found in existing provenance.

**Keep this PR a draft.** It depends on turbobeest/modelspec#840 and turbobeest/modelspec#823 merging first. `.engine-pin` remains `0cf4080a72d354295c434206257d089d26b50ed6`. The orchestrator must later pin a merged engine SHA containing both PRs.

Validation uses the reworked engine in `/Users/terbeest/dev/worktrees/model-368` and a test signing key. Reproducible checks and observation limits are in `docs/evidence/g2-ios/MODEL-368-data.md` and the code PR's `docs/evidence/g2-ios/MODEL-368-cite-fix.md`. The broader private-script suite exposes older originless CopyStore calls that require migration before adopting the new pin; this citation cleanup leaves those unrelated writers unchanged.

Current blocker: the private export preserves five cited facts, but Pro model coverage remains quarantined by its existing October 14 mismatch. The required all-facts-present check fails. Its value and append-only verification history remain unchanged.

Executed by ChatGPT Codex (GPT-6.1 Sol); cross-model review by Claude Opus pending.
