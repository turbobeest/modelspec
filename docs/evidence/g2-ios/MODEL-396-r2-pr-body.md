The source verifier extracts text from a restricted PDF subset using offline pypdf 6.19.0. An object allowlist and finite input, page, decoding, parsing and text budgets reject unsupported or malformed documents. Original bytes and extracted text have separate hashes. Verification requires approved retention and a template bound to the complete source, extraction, subject and facet; PDFs cannot fall through to generic or LLM readers.

The review fixes put pypdf only in the optional `verify` extra and install that extra in the pytest CI jobs. A missing dependency produces installation guidance. Unapproved revisions of previously approved PDFs report regions as CHANGED and trigger requeue and governance alerts without retaining the new bytes. PDF detection is cached per stored copy per run. The regenerated CLI bundle fixes the stale-guidance installation failure. `origin/main` was merged without rebasing.

No production PDF template is approved. Real-world PDFs, including Small 4's technical PDF, are still refused by the structure limits. Small 4's maximum-output fact remains unverified and needs a later engine PR. The data#98 audit does not establish permission to retain Mistral PDFs. No Mistral data or offering is filed.

Validation for this revision:

- Reproduced six regression failures against the pre-fix implementation, plus the stale-bundle test and failed fresh-venv install.
- 795 tests passed serially: 126 PDF/reader/Worker-import tests, 651 source/verification/model/retention/Kimi-reader tests, and 18 guidance/wheel-packaging tests.
- `python -m pipeline.agent_copy check` exited 0.
- `pip install -e .` succeeded in a fresh venv under /tmp. CLI help succeeded with pypdf absent; package metadata restricts pypdf to the verify extra.
- Targeted Ruff and whitespace checks passed.
- The earlier private Worker memory measurements were 108.92 MiB current and 104.60 MiB successor, under the 115 MiB limit. They were not rerun in this round.
- Full local pytest and site builds were not run. CI and independent review remain pending. This PR stays draft.

[Review-fix reproduction commands and red/green evidence](docs/evidence/g2-ios/MODEL-396-r2-fix.md). [Original implementation evidence](docs/evidence/g2-ios/MODEL-396-fix.md). [Accepted PDF structure and limits](docs/design/MODEL-396-readers.md).

Executed by ChatGPT Codex (GPT-6.1 Sol); cross-model review by Claude Opus pending.
