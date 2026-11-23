# Standing rules for evidence and card work

Read this before writing a card, a benchmark page, or evidence. Entry:
[`AGENTS.md`](../../AGENTS.md). Worktrees: [`worktrees.md`](worktrees.md).
Architecture map: [`architecture-map.md`](architecture-map.md).

## The rules

Learned expensively during 2026-09-09/10.

1. **Absence is data.** A null is honest; a plausible value is a lie that
   survives review. Cards left `active_parameters`, `commercial_use` and
   `attention_type` null with stated reasons rather than guessing, and that is
   the bar.
2. **A wrong answer is worse than no answer.** `total_parameters` parsed from
   filenames produced **1,589 published "it fits" answers for hardware that
   cannot hold the weights**. A null is skipped by the fit layer; a wrong number
   is served. Hub `safetensors.total` only; never filenames.
3. *Moved to [`AGENTS.md`](../../AGENTS.md):* put limits in code. A Firecrawl
   budget given in two prompts was burned 920 of 1,000; the guard now lives in
   `scripts/benchmarks/fetch.py`.
4. *Moved to `AGENTS.md`:* verify by running, not by reading a ticket.
5. *Moved to `AGENTS.md`:* check exit codes directly, not through a pipe.
6. **Record the exact variant.** Terminal-Bench 2.1 is not `terminal_bench`.
   SWE-bench Pro is not `swe_bench_verified`. MMLU-Pro is not MMLU.
7. **A provider's table of a competitor's score is not primary evidence** for
   that competitor. Claude Mythos 5 has no benchmark evidence for this reason,
   and that is correct.
8. **Evidence dating.** A static result needs a stated day; a retrieval time is
   not a publication date. A *live leaderboard* row is dated by the observation
   (`date_type: evaluated`) — see `BENCHMARK_WRITE_RULE` in
   `scripts/build_manifest.py`.
9. **Inapplicable is not unknown** (MODEL-97). Which fields a class cannot
   answer is derived from `model_type` in `schema/applicability.py` and
   published as an `applicability` block; it is never written on a card.
   Architecture fields are never inapplicable: undisclosed is unknown.
10. **Excluded sources stay excluded.** `decision/excluded.py` lists them and
    the data-trust checks refuse them; never cite one, even second-hand.

11. **Provider-wide SOC 2 statements** (MODEL-341, Jamie 2026-10-08). A
    provider-wide SOC 2 Type 2 statement, such as Microsoft's for Azure, counts
    for an offering only when the cited page names the provider's platform
    that serves the offering (for Azure AI Foundry models: "Azure") and states
    Type 2 (or Type II). The page need not name the specific service; the YAML
    scope comment carries that. Record
    `offering.attestation.soc2` as `value: type_2`, `state: known` for each
    such offering of that provider, for example azure-ai-foundry `gpt-6-astra`
    and `gpt-5-4`. There is no `provider_wide` enum value and no contract bump.
    Where the provider gates the statement by a per-service scope list, add a
    YAML comment on the record that names the list and its URL, so a reader
    can check that the service is in scope. If the page does not cover the
    platform, leave the fact `not_disclosed`; if the scope list excludes the
    service, record `none`/`known`. The audit reader (`decision/verify.py`,
    `GovernanceProseExtractor`) matches the phrase "SOC 2 Type 2" (or "Type
    II") and does not check service scope, so it agrees with the `type_2`
    record; `test_governance_prose_reader_handles_provider_wide_statements`
    covers the reader and `test_soc2_type_2_phrase_matches_registered_enum` the
    comparison. The scope comment is the human check.

12. **Weights openness of a hosted-only model** (MODEL-490, decided by the
    owner, 2026-11-14). `model.weights_openness` is `closed_weights` as a
    lab-level fact when the lab's terms license only a hosted service and no
    registered page of the model offers weights. Required evidence: the section
    of the lab's terms that licenses a hosted service, and each of the model's
    registered pages, read and found to offer no weights. Cite those pages. It
    does not allow a guess for a lab whose terms were not read. It applies only
    to a lab whose terms license only a hosted service: for a lab that publishes
    weights for any model, this rule does not apply, and such a model needs its
    own evidence under the existing reading rule. A page not read is not an
    absence: leave the fact as it is.
13. **User cap when a provider's terms state none** (MODEL-490, decided by the
    owner, 2026-11-14). `licence.user_cap` is `unbounded`, as the facet
    definition says, when the provider's commercial terms were read in full and
    set no user, seat or monthly-active-user threshold. Cite the terms page.
    "Read in full" covers the provider's commercial terms themselves; documents
    the terms incorporate are read too when they are registered sources. When
    they are not registered, the fact is filed on the commercial terms alone and
    its citation says so. It does not allow `unbounded` when the terms mention a
    cap, a tier limit or "contact sales above N", or when the commercial terms
    were not read in full.
14. **Rules 12 and 13 on a cite-only source.** On a cite-only source the fact is
    filed as a cited fact, with the pages and the date they were read, and
    carries no machine verification: the engine returns `cited` and logs no
    record. Never write a verification record by hand.

15. **A cite-only page may change a value when two readers of different families
    agree** (MODEL-531, Jamie 2026-11-22). Rule 14 files a fact as cited and
    leaves its value as it is. A value changes on a cite-only page only through
    `decision.cited_change.cited_change`, and only when every condition holds:
    the host is cite-only (`forbids` or `cite-only` class); the page is
    first-party for the facet (a first-party kind the facet's
    `permitted_source_kinds` allows, with a registry publisher that is the
    subject's lab); two readers of distinct known model lineages (never
    `unknown`, `other`, `unrecorded` or an unlisted name) return the same
    normalised value; each reader's id, family and version are recorded; and no
    source registered for that subject and facet sits on a host that retains
    copies. The gate looks the registered sources up itself in the data
    directory (card, `registry/sources.yaml`, `registry/source-redirects.json`
    for a retaining-host source that now redirects to a cite-only host) and
    refuses when the lookup fails; a caller supplies none of it. Blindness is
    built: `decision.cited_reader` makes one prompt from the URL, the facet
    definition, the subject's name and the page bytes only, records each
    reader's prompt sha256 and an input manifest, and the gate rebuilds the
    prompt from the page bytes and refuses unless both match. The gate takes
    `Reader` objects and runs the harness itself, so no caller supplies answers,
    hashes or manifests. It fetches the page itself, in memory, redirects off,
    and refuses any hop to a retaining host. Every attempt is appended to
    `verification/cited-attempts.jsonl` (no page text), keyed by subject, facet
    and epoch across every page. Any disagreement among the counted attempts
    blocks (`prior_attempt_disagreed`), so a retry cannot shop for agreement; an
    agreement authorises only if made through the harness, and a seeded
    agreement from unproven reads authorises nothing while a seeded
    disagreement still blocks. A
    `registry/source-redirects.json` entry exempts a retaining-host source only
    if its `to` is a registered cite-only source URL and it was checked within 7
    days; the rolling re-read re-probes each entry and drops it unless the
    source still answers 3xx to that URL. The block's `previous_sources` keeps
    the sources the fact cited before, so later re-reads still see them. A failed condition
    is a named refusal and nothing is written. A disagreement leaves the fact as
    filed and flags it. The fact is served as cited, never verified: the record
    keeps the URL, read date, sha256, both readers' answers, prompt hashes and
    manifests under `derivation.cited_change`; no page text, no excerpt, no
    `Verification`. The rolling re-read (`scripts/evidence_reread.py`) flags each
    such fact whose page's visible text changed (`reread_required` hashes the
    normalised text in memory, so byte churn is no change), at most once in 7
    days per fact (`reread_due`, requests logged in
    `verification/cited-reread-requests.jsonl`); two readers then read it again
    (`reread`), and fewer than two flags the fact.

    **Benchmark board readings too (Jamie 2026-11-22).** `decision.cited_change.cited_reading`
    takes a subject, a benchmark id and the reading's settings
    (`model_id_as_evaluated`, `effort`, `harness`; exactly one evidence row must match)
    and applies every condition above unchanged, with one difference: first party is the
    board's own publisher, not the subject's lab. The source is the benchmark's registered
    `benchmark_author` page; its `publisher` must equal the benchmark page's internal
    `owner_id` (both present; a host match alone is not enough), and that registry id's
    URL host must be the source's host. The retaining-host check covers every source the
    reading's rows cite, their `checked_sources`, `derivation.cited_change.previous_sources`
    and the registered sources the benchmark page lists, as the fact gate does. Readers get a prompt built from the URL, the row's
    settings, the subject name and the page bytes, never the filed score; the attempts log
    is keyed by subject, `benchmark:<id>` and a hash of the settings. A changed score is
    served as cited (`state` `known`, `resolution` `cited`); `scripts/cited_reading.py`
    writes it through the refresh writer, with the `derivation.cited_change` block on the
    evidence row (the rolling re-read, `cited_change_rereads`, covers these rows too). A
    prior agreed attempt on another value blocks (`prior_attempt_disagreed`). The clock
    is the gate's own (UTC; `scripts/accuracy.py` now uses the UTC date too); a log entry
    with no time zone is refused (`bad_read_date`). A cost in a row's configuration is not
    read by the gate and keeps its own read day (`cost as of <date>`).

    **No longer published.** When both readers agree the board lists no row (or no score)
    for the reading, one such read only logs an attempt (`absence_pending`). A second
    read at least 24 h after a pending one returns `not_published`, and the writer sets
    `not_published_since` on the row to the day of the first absent read (the field and
    its freshness handling are in `docs/evidence/MODEL-482-not-published-since.md`). A read that finds
    the row ends the pending absences, and a later score clears the field. Readers that split
    on presence are a disagreement and block as above.

Public PR bodies and evidence must not contain private modelspec-data commit SHAs or per-card private values. Private PR numbers, ages and clone URLs are not sensitive.

## Pytest CI shards

The required `Run pytest` check aggregates eight file-level jobs. Private
serving, social cards, agent readiness and landing each run alone and serially.
Four other jobs use stable longest-processing-time packing with the measured
per-file weights in `tests/shard_durations.json`. They keep the longest files
first with xdist's `--no-loadscope-reorder`, preserving each module's fixtures.
The splitter estimates a new file from its byte-size share of the measured
suite. Inspect the predicted balance after adding tests with:

```bash
python scripts/pytest_shards.py --shard-count 8 \
  --isolate tests/test_private_serving.py \
  --isolate tests/test_social_cards.py \
  --isolate tests/test_agent_ready.py \
  --isolate tests/test_landing.py --summary
```

The summary reports summed testcase seconds, not predicted wall time. Each
ordinary shard uses four workers, while isolated shards have one process.
Every shard logs its 25 slowest test phases and has an 80-minute timeout.

The workflow compares the combined shard node IDs with an unsharded
`pytest --collect-only -q -m "not perf"` collection. The required check fails
if a file is missing or duplicated.

Each shard uploads its JUnit timings as `pytest-shard-N-junit`. Refresh the
committed weights from a completed GitHub Actions run with:

```bash
rm -rf /tmp/modelspec-pytest-junit
mkdir -p /tmp/modelspec-pytest-junit
gh run download <run-id> -p 'pytest-shard-*-junit' -D /tmp/modelspec-pytest-junit
python scripts/refresh_shard_durations.py /tmp/modelspec-pytest-junit
```

## Three floors — not backlog (counts as of 2026-09-10)

Of ~604 unrankable cards:

* **~96 can never be ranked** under current profiles — image, video, audio, OCR,
  base models, serving quants. No profile weights a benchmark they could score on.
* **~388 are LLMs not present on the live leaderboards.** More crawling will
  never find them.
* **246 cards have no parameter count because the weights are closed.**

And the trap: **carding a missing model raises the unrankable count** until its
evidence lands. Never optimise that metric — it rewards not carding models.
