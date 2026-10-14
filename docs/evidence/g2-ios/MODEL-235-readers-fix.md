# MODEL-235-readers execution evidence

The final production change fixes only MiniMax's literal `<API Key>` placeholder
handling. Go, Explore, and Build's exact usage allowances verify. Both reviews
confirmed that fix. All Mistral card-boundary changes have been withdrawn:
`_card_lines` matches `ee16bf40` byte-for-byte.

The offline replay changes three facts from unreadable to unchanged, with no
proposed price changes. It now reports 117 unreadable facts. Mistral Pro's
coding-access fact is intentionally left unreadable for the data side to re-cite
to a scoped region. Any future engine fix must segment actual plan cards in the
parsed DOM, rather than infer their ownership from line windows.

The ≤15 target remains blocked. The complete rollback, safety cases, legacy
limitations, current checks, and final scope are recorded in the
[R3 evidence](MODEL-235-readers-r3-fix.md). The earlier attempts and their withdrawn
results are historical, not claims about the final implementation.

## Revisions and inputs

- Engine base: `e37578f7e162fdec9ef93b21fbfe06e7ffa77598`.
- Run's engine pin: `ee16bf40666a6673d17af9a20b3e3b0ec10e786f`.
- Final implementation commit: `892931a767fc0acf56953d917a8485dad46ebac8`.
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
| Same replay, final MiniMax-only readers | 338 | 0 | 13 | 117 | 43 | 44 |

The supplied run table sums to 555, not 575. The replay reproduces both requested
failure reasons and all 50 missing-region failures. It does not reproduce the
reported unchanged/needs-review split bit-for-bit: eight more facts verify in the
replay. The artifacts do not record the run's exact data revision or a plain HTTP
URL/outcome manifest. The same-input before/after delta is three facts, verified
by comparing every serialized fact result. The initially checked-out October 6
revision produced `272 | 1 | 17 | 89 | 34 | 111`; that was superseded when the
newer locally available data revision was found.

## Repaired engine defects

### Mistral changes withdrawn

Both attempts to recover Mistral Pro's coding-access sentence changed plan
ownership incorrectly. The orchestrator directed restoration of the exact
pinned `_card_lines` implementation. The positive test was removed; the safety
checks that pass on the pin remain. This PR recovers no Mistral fact.

The data side must re-cite the Mistral Pro coding-access fact to a scoped region
and independently verify it. If that requires engine support, the follow-up is
proper plan-card segmentation using the parsed DOM structure, not another
line-window boundary rule.

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
markup to fail verification. The three MiniMax positive cases remain. Current
regression and full-suite results are in the R3 evidence.

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
| Mistral Pro coding access | needs_review | unreadable | unreadable |
| Moonshot Andante CNY price | unreadable | unreadable | unreadable |

#743 added the subscription raw-markup rejection that blocks the MiniMax FAQ.
Its quote handling also changes how the old Mistral failure is reported.
The price-table ownership restriction is retained. #747's licence changes do not
repair or worsen these price/plan outcomes. The older four requested failures
persist before #743, so no broader bisect was necessary.

## Remaining unreadable facts and actions

These groups account for all 117 remaining unreadable facts.

| Count | Group | Evidence and next action |
|---:|---|---|
| 1 | Mistral Pro coding access | Re-cite to a scoped Pro region and independently verify it. The card-boundary change is withdrawn. Any engine follow-up must use parsed DOM card segmentation. |
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

## Current checks and delivery

The [R3 evidence](MODEL-235-readers-r3-fix.md) records the exact pin comparison,
the seven pinned Mistral cases, all retained tests, current focused and full-suite
exit codes, replay commands, and delivery commands. The final PR title and body
refer to the MiniMax-only production change and the 117-unreadable replay.

No live provider page, paid API, Firecrawl, Linear write, workflow dispatch,
production switch, frozen data change, ready transition, or merge ran. The private
data checkout remained read-only. The PR remains a draft.
