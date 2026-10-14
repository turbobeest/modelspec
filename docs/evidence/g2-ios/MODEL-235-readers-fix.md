# MODEL-235-readers execution evidence

Two reader defects are fixed. Mistral Pro's exact coding-access sentence now
verifies beside an API-credit feature. MiniMax's Go, Explore, and Build usage
allowances now verify when their FAQ contains the literal `<API Key>` placeholder.
The offline replay changes exactly these four facts from `unreadable` to
`unchanged`. It proposes no price changes.

The ticket remains **BLOCKED**. Unreadable falls from 120 to 116 on the same
saved inputs, above the requested ceiling of 15. Fifty facts cite locators that no longer
match the pages. Other facts cite obsolete tables, absent prices, or facets for
which the deterministic reader still lacks coverage. Data was not changed.

## Revisions and inputs

- Engine base: `e37578f7e162fdec9ef93b21fbfe06e7ffa77598`.
- Run's engine pin: `ee16bf40666a6673d17af9a20b3e3b0ec10e786f`.
- Implementation commit: `1fa662b0b19d30a1dad6f256cc177b78f29bf0e0`.
- Final delivery SHA is the commit containing this report. Resolve it with
  `git log -1 --format=%H -- docs/evidence/g2-ios/MODEL-235-readers-fix.md`.
  The executor's final output also records that SHA.
- Data checkout HEAD: `0cb8eedeb210cf5e31a93d5b9a976485fd628eea`, dated October 6.
  Its 524 facts were an initial diagnostic input, not the final replay input.
- Final data input: the already available local `origin/main` at
  `4d4f709621486e791107830680e7d2293ea450a7`, containing 555 tracked facts.
  `git archive` exported it inside this worktree's ignored `.artifacts` directory.
  The data checkout remained read-only. No remote fetch ran.
- Saved copies and rendered manifest: the two paths supplied in the spec under
  `/private/tmp/claude-501/-Users-terbeest-dev-modelspec/6b307b20-b183-41a5-91e6-14f65d035cbc/scratchpad/rr-38572656013/`.

The engine base and run pin have identical `decision/verify.py` and
`scripts/price_reread.py`, checked with `git diff`. The replay uses a separate
writable copy store inside this worktree. It does not write offerings, claims,
verification records, or the supplied artifacts. Python socket `connect`,
`connect_ex`, and `create_connection` raise during the replay.

The plain-copy artifact has no URL/outcome manifest. The replay tool records its
chosen complete copy digests in `url-map.json`. Canonical HTML URLs identify most
pages. Six explicit assignments identify redirects or text pages. These mappings
are visible in the tool. No saved plain response identifies
`https://chatgpt.com/pricing/`; its four facts are reported as missing offline
responses, not fabricated HTTP 403 responses. The other 39 unreachable facts
come from HTTP 403 entries in the rendered manifest.

## Counts

| Input and engine | unchanged | changed | needs_review | unreadable | unreachable | not_reread |
|---|---:|---:|---:|---:|---:|---:|
| Run 38572656013, as supplied in the spec | 327 | 0 | 21 | 120 | 43 | 44 |
| Saved-input replay, data `4d4f709`, engine pin `ee16bf40` | 335 | 0 | 13 | 120 | 43 | 44 |
| Same replay, final readers | 339 | 0 | 13 | 116 | 43 | 44 |

The supplied run table sums to 555, not 575. The replay reproduces both requested
failure reasons and all 50 missing-region failures. It does not reproduce the
reported unchanged/needs-review split bit-for-bit: eight more facts verify in the
replay. The artifacts do not record the run's exact data revision or a plain HTTP
URL/outcome manifest. The same-input before/after delta is four facts, verified
by comparing every serialized fact result. The initially checked-out October 6
revision produced `272 | 1 | 17 | 89 | 34 | 111`; that was superseded when the
newer locally available data revision was found.

## Repaired engine defects

### Mistral Pro card boundaries

`_card_lines()` stopped at `Faster responses.` because a later feature contained
`$25.5 /mo in API credits.`. The next-card heuristic accepted any nearby dollar
amount as a card price. The exact filed sentence,
`All-day coding in the CLI, IDE, or on web.`, occurs after that premature boundary.

The boundary now requires a complete price line, with an optional billing suffix.
The dollar amount inside the API-credit feature cannot end the card. A following
Team card's bare price still ends it. Comparison rules, model matching, and
numeric equality are unchanged.

Red test:
`test_mistral_pro_reads_coding_access_before_api_credit_feature`.

```text
E       assert 'mismatch' == 'verified'
FAILED tests/test_model_235_readers.py::test_mistral_pro_reads_coding_access_before_api_credit_feature
1 failed, 1 passed in 0.28s
```

The sibling-plan check, `test_mistral_pro_does_not_borrow_team_feature`, passed
before and after. The final positive test verifies the exact filed sentence.

### MiniMax FAQ literal credential placeholder

The saved FAQ contains an exact tier table:
`Go | Getting started | 1x (baseline)`, `Explore | Everyday use | 3x`, and
`Build | Intensive use | 7.5x`. `_vendor_layouts()` already extracts the exact
`Usage relative to Go: ...` values. The subscription reader returned no readings
before reaching it because its raw-HTML guard matched `<API Key>` in a normalized
code example elsewhere on the page.

The subscription reader and its quote-candidate path ignore this one exact
literal placeholder when detecting raw markup. The placeholder remains in the
source text. Other markup still rejects the page. No extractor borrows a number,
changes its subject match, or changes comparison tolerances.

Red tests:
`test_minimax_faq_reads_exact_tier_allowance_beside_api_key_placeholder`,
parameterized for Go, Explore, and Build. The finalized trimmed fixture retains
the real Claude Code sentence required by the established layout detector.
It was rerun against the pinned engine with pytest's importlib mode:

```text
E       assert 'mismatch' == 'verified'
3 failed, 6 deselected in 0.32s
```

The green test also wraps the same text in `<div>...</div>` and requires the raw
markup to fail verification. Final regression module: `9 passed in 0.20s`, exit 0.

An earlier fixture trim removed the layout detector's trigger. That trim also
failed after the placeholder fix, so it was corrected using the real FAQ
sentence. A historical pytest attempt without importlib mode imported the current
worktree through pytest's package path and passed; that result was discarded.
The importlib run above exercises the actual pinned reader.

## Historical probes

The replay tool's `--fact` option selects exact IDs and uses the same re-read path.
The historical engine exports stay inside this worktree. No checkout or bisect
changed the assigned branch.

| Fact | Before #743, `7d4f5bd8` | Before #747, `44f56ec6` | Final |
|---|---|---|---|
| Gemini 3.5 Flash input | unreadable | unreadable | unreadable |
| Vertex Sonnet 5.5 input, global partner selector | unreadable, missing region | unreadable, missing region | unreadable, missing region |
| MiniMax Token Plan Plus price | unreadable | unreadable | unreadable |
| MiniMax M Plan Go usage allowance | unchanged | unreadable | unchanged |
| Mistral Pro coding access | needs_review | unreadable | unchanged |
| Moonshot Andante CNY price | unreadable | unreadable | unreadable |

#743 added the subscription raw-markup rejection that blocks the MiniMax FAQ.
Its quote handling also changes how the old Mistral failure is reported.
The price-table ownership restriction is retained. #747's licence changes do not
repair or worsen these price/plan outcomes. The older four requested failures
persist before #743, so no broader bisect was necessary.

## Remaining unreadable facts and actions

These groups account for all 116 remaining unreadable facts.

| Count | Group | Evidence and next action |
|---:|---|---|
| 35 | Vertex partner-Anthropic global locator | The filed CSS selector includes `aria-labelledby="tab-ucj-200-g1-t0"`. That generated ID is absent from the new HTML. Re-collect and register a stable, correctly scoped global-table locator, then independently verify every price. |
| 9 | Z.ai coding-plan locator | Filed `#plan-cards` is absent from the rendered page. Re-register a current plan-card region and verify the three plans' prices, billing periods, and allowances. |
| 6 | MiniMax Token Plan quota locator | Filed `usage-quota` heading is absent after the Token Plan URL redirects to M Plan. Re-cite authoritative legacy-plan quota evidence; the M Plan quota is not evidence for Token Plan. |
| 20 | Vertex Gemini table indexes | Filed `gemini-standard` table 0 now contains Gemini 4 Argon; filed batch table 2 is also obsolete. Re-register the correct standard/batch regions. Current Gemini tables are elsewhere on the page, but the engine does not search outside filed citations. |
| 10 | Gemini direct API prices | The saved page has Flash-Lite but no exact Gemini 3.5 Flash or Gemini 3.7 Flash pricing section. Find current primary evidence for those exact models or record the absence. Flash-Lite's price is not their price. |
| 8 | MiniMax Token Plan values | The redirect destination describes M Plan Go/Explore/Build, not the legacy Token tiers' old prices and other filed values. Re-cite legacy-plan evidence without substituting M Plan values. |
| 16 | Moonshot legacy plans | Current prices belong to Go/Plus/Pro/Max. The legacy section preserves Andante/Moderato/Allegretto/Allegro but does not state their old prices or old usage counts. Re-cite legacy price evidence and re-file changed wording through review. Go's 49 CNY does not verify Andante's 49 CNY. |
| 2 | Cursor Teams wording | The saved page does not state the filed `Cloud agents and automations with shared team context` sentence for Standard/Premium seats. Review and re-file the current exact, scoped wording. |
| 3 | MiniMax wildcard surfaces | The deterministic reader deliberately refuses `coding_tool:*`. These need an independently specified reader for wildcard capability, not a fuzzy model/tool list match. |
| 3 | MiniMax coding-tools quote | The quote is present, but `coding_tools_quote` has no deterministic subscription extraction branch. Add a reader with explicit plan-family scope and exact quote checks. This is a remaining engine coverage gap, not an absent quote. |
| 3 | MiniMax allowance window | The filed value is the verbatim `Duration | 5 hours | 7 days` table row. The existing window reader emits the canonical `five hours` value and needs plan-scoped text. Resolve the field's intended representation and add correctly scoped reading or re-file the fact; do not assert that these strings are equal. |
| 1 | MiniMax Go coding access | The filed statement names an `M Plan API Key`; the current page names a `Subscription Key`. The Go-specific reader finds no verified replacement. Re-file current scoped wording or add a plan-family reader after defining its ownership rule. |

`unreachable:` is generated in `verify()` as a diagnostic prefix before
`source#cited-region`. It is not part of a filed region ID. `StoredRegions.text()`
looks up the exact registered ID and selects its exact locator. There is no prefix
to strip from data or from the resolver. The three missing-locator classes above
are data defects, so that class stops here as the spec directs.

The Gemini, Vertex, MiniMax, and Moonshot fixtures retain these failure cases as
negative safety tests. They passed on the old reader and continue to pass.
It would be incorrect to manufacture positive red/green tests for values absent
from their filed regions. Fixture provenance is recorded in
`tests/fixtures/model_235_readers/README.md`.

## Checks and reproducible commands

Tools: Python 3.14.4, pytest 9.1.1, pytest-xdist 3.8.0, Pydantic 2.13.5,
PyYAML 6.0.3, Ruff 0.16.6, Git 2.50.1, GitHub CLI 2.102.0, Node 22.22.3.
Commands run from the assigned worktree unless noted. Exit codes come from
command completion, without a pipeline.

The local archive exports were made with Python's `tarfile`, using
`subprocess.run(['git', ... 'archive', revision], check=True, capture_output=True)`
and `extractall(worktree_scratch_directory, filter='data')`. Revisions exported
were data `origin/main`, `6e5b9bb6^`, `ee16bf40^`, and `ee16bf40`.

```bash
# Source comparison and revisions:
git diff ee16bf40 e37578f7 -- decision/verify.py scripts/price_reread.py
git -C /Users/terbeest/dev/modelspec-data rev-parse HEAD origin/main

# Initial Mistral red, before production changes, exit 1:
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_235_readers.py

# Finalized MiniMax red against the exported pin, exit 1.
# Working directory: .artifacts/model-235-readers/executor/pin
PYTHONPATH=/Users/terbeest/dev/worktrees/model-235-readers/.artifacts/model-235-readers/executor/pin /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest --import-mode=importlib -q /Users/terbeest/dev/worktrees/model-235-readers/tests/test_model_235_readers.py -k minimax_faq

# Green and focused suites, exits 0:
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_235_readers.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_235_readers.py tests/test_price_reread.py tests/test_price_reread_fallback.py tests/test_decision_verify.py tests/test_decision_sources.py tests/test_model380_subscription_quotes.py tests/test_model380_subscription_types.py

# From web/, prepare dependencies and the bundle required by browser tests:
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm ci
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm run build

# From the worktree root, final full check:
TZ=UTC PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile

/Users/terbeest/dev/modelspec/.venv/bin/python -m ruff check tests/test_model_235_readers.py docs/evidence/g2-ios/MODEL-235-readers-replay.py
/Users/terbeest/dev/modelspec/.venv/bin/python scripts/pytest_shards.py --shard-count 4 --summary
git diff --check
```

Focused result: `762 passed in 11.87s`, exit 0. The first full run started before
the MiniMax fix and was interrupted to restart against both fixes. It returned
exit 2 with `9346 passed, 5 skipped, 4 warnings in 611.62s`. Its process tree was
stopped. Two initial focused commands named nonexistent normaliser test files
and returned exit 4; the corrected command above uses `test_decision_sources.py`.
Ruff and whitespace checks pass. The new file appears in the shard summary,
which reports 67, 68, 67, and 67 files with approximately 3521.48 seconds each.
`TZ=UTC` avoids the repository's separately recorded local/UTC site-date mismatch.

Final full-suite result: `11055 passed, 9 skipped, 11 warnings in 1255.98s
(0:20:55)`, exit 0. The warnings are the existing unsigned decision-vocabulary
warnings exercised by CLI tests.

The complete replay invocation is:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python docs/evidence/g2-ios/MODEL-235-readers-replay.py --data-root .artifacts/model-235-readers/executor/data-main --copies /private/tmp/claude-501/-Users-terbeest-dev-modelspec/6b307b20-b183-41a5-91e6-14f65d035cbc/scratchpad/rr-38572656013/price-reread-copies --rendered /private/tmp/claude-501/-Users-terbeest-dev-modelspec/6b307b20-b183-41a5-91e6-14f65d035cbc/scratchpad/rr-38572656013/price-reread-rendered --out .artifacts/model-235-readers/executor/final-after-2
```

The same command with `PYTHONPATH=$PWD/.artifacts/model-235-readers/executor/pin`
and `--out .artifacts/model-235-readers/executor/final-before` produces the pinned
baseline. Historical probes use `PYTHONPATH` pointing to the corresponding
export and repeat `--fact <exact-id>` for the six fact IDs in the historical table.
All completed replay commands returned exit 0.

## Observation limits and delivery

No live provider page, scheduled workflow, production read, vendor API,
Firecrawl, or device was exercised. No source URL was fetched. No Linear write,
workflow dispatch, production switch, frozen data change, merge, or PR ready
transition ran. The data repo was not modified. The full suite exercises local
mock servers and installed browser tooling; the socket block is specific to the
offline replay.

The source commit and evidence commit end with both required author trailers,
with `Co-Authored-By: GPT-6.1 Sol <noreply@openai.com>` last. Delivery uses
`CI_LOCAL_SKIP=1 git push -u origin model-235-readers` after the checks and
`gh pr create --draft --base main --head model-235-readers --title
"price re-read: read MiniMax allowances and Mistral coding access (MODEL-235)"
--body-file .artifacts/model-235-readers/executor/pr-body.md`.
The PR remains a draft for independent review.

## Review correction

The first card-boundary fix failed Grok's neighbouring-plan probes. The follow-up
[R2 evidence](MODEL-235-readers-r2-fix.md) records the structural correction,
red-first A/B regressions, verdict controls, and unchanged replay results.
