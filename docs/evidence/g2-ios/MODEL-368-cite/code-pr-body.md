Perplexity FAQ facts now remain **Cited, not machine-verified**. The branch includes current main and the cite-only mechanism from #840; **#840 must merge before this PR**. Keep this PR a draft until independent review.

The FAQ reader preserves its exact template and model mapping. It stores the answer-ending fingerprint instead of copied prose. Retention guards reject new Perplexity page copies and replay of historical raw HTML; verification returns `cited` before extraction. Parser tests use runtime synthetic pages, and the optional real-page fixture is removed.

Private data PR turbobeest/modelspec-data#97 removes this ticket's copied quotation and comment, preserves all fact values, and attaches the available original fetch timestamp to its existing source hash. Its `.engine-pin` remains unchanged for the orchestrator to update after both code PRs merge.

Validation commands, red/green results, private export checks, and limitations are recorded in `docs/evidence/g2-ios/MODEL-368-cite-fix.md`. The private script suite exposes older originless CopyStore calls; those require migration before adopting the new engine pin.

Current blocker: the private export preserves five cited facts, but Pro model coverage remains quarantined by its existing October 14 mismatch. The required all-facts-present check fails. Its value and append-only verification history remain unchanged.

Executed by ChatGPT Codex (GPT-6.1 Sol); cross-model review by Claude Opus pending.
