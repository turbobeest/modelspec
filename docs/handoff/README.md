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

    **Operational usage limits are not a user cap** (MODEL-491, decided by the
    owner, 2026-11-25). Limits on use that an order form or the documentation
    sets, such as rate, token, throughput or messaging quotas, are not a
    licence user cap, even where the terms count end-user limits among them and
    forbid circumventing them. `unbounded` stands when the terms set no seat,
    user or monthly-active-user threshold. "A tier limit" above means
    a seat, user or monthly-active-user threshold that a tier sets, not an
    operational quota.
14. **Rules 12 and 13 on a cite-only source.** On a cite-only source the fact is
    filed as a cited fact, with the pages and the date they were read, and
    carries no machine verification: the engine returns `cited` and logs no
    record. Never write a verification record by hand. Lifecycle facts are mostly
    cited from labs' deprecations pages, so the weekly rolling re-read
    (`scripts/evidence_reread.py`, `WATCHED_FACETS`) reads every page a
    `model.lifecycle` fact cites, keeps only the hash of its visible text
    (`reports/evidence-reread/watched-pages.json`), and lists the facts whose page
    changed for a person to re-read (MODEL-527). It changes no value.

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

    **A quarantined reading is refused (MODEL-547).** `cited_reading` refuses with
    `quarantined`, before any read or attempt, a reading with an uncleared mismatch or
    unreachable verdict for any value. It uses the fact gate's predicate (`quarantine_verdicts`,
    the log parsed and ranked as the build does) with target kind `evidence`. A row's id changes
    with its score and date, so the reading owns its stored id and every id logged under
    `<model>#<benchmark>#` (for the subject and the card's `model_id`) that no other current row
    of the benchmark has.

    **Offering facts and `not_disclosed` (MODEL-544).** `cited_change` takes an offering
    fact too: the subject is the offering id (`<provider>/<lab>/<model>/<region>/<tier>` or
    `<provider>/subscription/<plan>`), the fact is looked up in the one offering file the
    loader allows, and first party is the offering's provider. Every other condition is
    unchanged. The readers' facet definition adds one sentence saying the subject is an
    offering (no value). `scripts/cited_offering.py` runs the gate with two subscription CLIs
    and writes the record into the offering file and its claim into the queue from one source
    reference, so the reference and the claim name the same copy (the MODEL-542 check). A
    change to `not_disclosed` needs `accept_not_disclosed` and both readers finding the page
    silent; each reader's finding (`not_stated`) is recorded. It is refused when the readers
    saw only part of the page (`page_truncated`), when the page shows too little text to prove
    silence (`page_too_short`), when the fact cites another page of a permitted kind
    (`other_source_unread`), or when an earlier attempt agreed on a value. Any disagreement
    files nothing. Without `clear_quarantine` the gate and the writer lift no quarantine.

    **A fresh agreement clears a mismatch quarantine (MODEL-552, Jamie 2026-11-25).** With
    `clear_quarantine` (`--clear-quarantine` in `scripts/cited_offering.py` and
    `scripts/cited_reading.py`), `cited_change` and `cited_reading` read a fact or reading with
    exactly one held `mismatch` in that verdict's clearing epoch, `<epoch>:clear:<verdict hash>`
    (`decision.quarantine_clearing`). The agreement clears it only when it is on a later UTC day
    than the verdict and in that later epoch (a log verdict records no page text hash, so the
    later epoch is the branch that can be shown), its two readers are distinct known families,
    and no disagreement is recorded in the clearing epoch or the subject's own epoch. The record
    then carries `clearings`: one line for the append-only
    `verification/quarantine-clearings.jsonl` naming the verdict (`target`, `verdict_sha256`,
    `verdict_date`) and the agreement (`agreement`: the hash of its exact line in
    `cited-attempts.jsonl`, with `subject`, `facet`, `epoch`). The block records
    `previous_epoch` (a rule-15 epoch the build re-derives) and `clearing_epoch`. The writers
    append the line. An agreement on the filed value clears too. The build holds every cited
    fact (with or without a block) and every cited board reading by a verdict on any value of
    its ids, unless its own value is independently `verified`; a sibling row claims an id only
    when it is admitted under it. It admits a held record only through a valid line: it names
    the winning verdict exactly, its agreement is a byte-identical log line that still meets
    every limit, and the fact or row is at its location and carries the block that agreement
    made, with that value, citing the agreement's registered source. An `unreachable` verdict,
    more than one held verdict and a fact that carries an owner's ruling stay blocked. A cleared
    fact is served exactly as a plain cited fact (no `derivation`) and no contract field widens. Card facts have no engine writer; a data PR writes the fact,
    its claim and the line (`quarantine_clearing.append`).

    **A cleared fact is re-read in the epochs after its clearing (MODEL-566).** The cleared
    verdict stays logged, but a valid line releases it: it no longer holds the fact or row in
    the epochs after the clearing epoch, in the gate and in the build alike
    (`quarantine_clearing.fact_released`, `reading_released`, reusing the line checks above).
    The cleared record sits in a re-read epoch named under its clearing epoch
    (`<clearing epoch>:reread:<text hash>`, `fact_epoch`, `reading_epoch`), never one a read
    before the clearing used; a changed page is read there by two readers, and their agreement
    opens the next re-read epoch. The latest valid clearing is followed: a later valid clearing
    of a newer verdict, based in such an epoch, releases the verdicts each earlier line names. The build
    admits a later block only when it is the one an agreement in such an epoch made
    (`later_agreements`: a complete agreed harness attempt by two distinct known families, on
    another page than the agreement that opened its epoch (its text hash, and its cited-region
    hash when both logged one), logged after it, at or after the clearing line's `cleared_at`
    and not after the build's day, in an epoch where no answer, complete or not, disagrees:
    an agreement on silence or absence and a later value do; `link_problem`). Every agreement
    that opens an epoch counts as its opener. The gate decides a re-read with the same
    functions: the chain that releases each verdict (`fact_chain`, `reading_chain`), its openers
    of the epoch (`openers`) and `link_problem` on the read it has just logged.
    Only the latest valid line of each verdict counts (by `cleared_at`, then line order). A
    verdict's epoch is derived only from the record's own agreement: never another setting's,
    and a clearing's only when a line names it. The gate re-reads a released record only on a
    page it fetched itself, and refuses (`quarantined`) a read of the page the record already
    rests on: a clearing is never re-litigated in its own epoch. The reading gate counts
    incomplete answers there too. A verdict newer than the clearing (on
    any value, `mismatch` or `unreachable`) is not the one the line names, so it holds the fact
    again; a forged or byte-mismatched line, a line for another value or subject, and an
    owner-ruled fact release nothing.

    **The owner's ruling past a disagreement (MODEL-551).** A complete `readers_disagree`
    attempt blocks its subject, facet and epoch for good. Only the owner can settle it, with
    one line of the append-only `verification/owner-rulings.jsonl` (`decision.owner_ruling`):
    `subject`, `facet`, `epoch`, `value`, `state`, `ruled_by` (one of `OWNERS`, in code:
    `jamie` alone), `ruled_at`, `ticket`, `source_ids`, `resolves` (the `attempt_id` of each
    disagreeing attempt) and `basis` (one short line, counts and field names only, no page
    text, no URL). `scripts/file_owner_ruling.py` files it, dry-run unless `--write`, and
    refuses unless a complete disagreement is logged for exactly that key in the fact's
    current epoch, the ruler is an owner, a ticket is named, the fact is not quarantined
    (lifting a quarantine is not a ruling), the value fits the facet's type, the stored id
    is the location id and no ruling exists for the key. It appends the line, files the
    matching claim (`collected`, `checked: cited`, latest for the fact) and rewrites the one
    fact from one source reference: the copy the disagreeing readers read (`snapshot_ref`,
    `retrieved_at`) and `derivation.owner_ruling`. Each file is read once and appended only
    if unchanged since. The build admits a fact that carries the block only when exactly
    one valid line for its own location, facet and epoch matches its value, state and
    sources; otherwise it is kept out as `invalid_citation`. A ruled fact is served as any
    cited fact (`verification: null`, the existing `citation`); the block never leaves the
    build, and no contract field widens. A ruling does not reopen its epoch to readers
    (`prior_attempt_disagreed` still holds); a fresh agreement in a later epoch follows the
    rule above.

    **A changed cited region reopens a ruled fact (MODEL-562).** The rolling re-read
    (`ruled_fact_rereads`, `decision.ruling_reread`) reads each page a ruling the build admits
    cites, with the host class read before any request and with the gate's own fetch
    (redirects off, every hop cite-only), so the sweep and the gate hash the same bytes. A
    source whose host now retains copies is counted, not read; an unclassed one is never
    requested. Two hashes are compared, never page text, both against what the disagreement
    the ruling resolves read (its lines in `verification/cited-attempts.jsonl`, nothing else):
    the visible-text hash, and the hash of the regions the source registers (its normaliser and
    locators, volatile text stripped, folded as rule 15 folds text), which the gate now logs
    with each attempt (`region_sha256`). That logged region hash is the only baseline; it is
    never read from the record file. A change outside the cited region (a banner, a date)
    changes nothing; a changed region appends one `reopen` line to
    `reports/evidence-reread/ruled-reopenings.jsonl` (ids and hashes only). A ruling whose
    resolved attempts logged no region hash has no baseline, and nothing reopens
    (`unbaselined`). The gate reads a ruled fact in `<ruled epoch>:reopen:<region
    hash>` only for a page it fetched itself with its own transport, for a ruling the build
    admits, on one of its sources, when the sweep recorded exactly that epoch; otherwise in the
    ruled epoch, where the disagreement still blocks. `reread` compares a ruled page with the
    ruled epoch, never with the block the fact kept. The owner may rule on a disagreement in a
    recorded reopened epoch (`file_owner_ruling`, `owner_ruling.ruled_epoch`). The report
    carries counts only. A fact a quarantine clearing (MODEL-552) made carries its own
    cited-change block and is re-read with the cited-change facts, in the epoch that block's
    text hash names.

    **The owner's ruling on a board reading (MODEL-569).** A board row split between two
    readers has no fact facet, so `file_owner_ruling` also takes `--facet benchmark:<id>` with
    `--reading` (the row's `model_id_as_evaluated`, `effort` and `harness` as JSON) and the
    row's epoch. The line has the same fields and the same limits as a fact's; the value is a
    score (`known`, a number in the board's range). `decision.board_ruling.row_problem` is the
    one test the filer, the gate (`cited_reading`) and the build (`decision.snapshot`,
    `pipeline.load`) apply: the epoch is one of the row's (settings or re-read epoch, a board
    epoch whose region every resolved attempt logged, or a reopened epoch that extends a valid
    ruling with another region); it is current (no later attempt at the reading in another
    epoch, other than a reopened epoch of the ruling's; an agreement there on another score
    supersedes it); nothing holds the row (`reading_held`: a ruling names no verdict and lifts
    none, and a held reading is refused); the score is the ruling's and each ruling source is
    cited at the copy its resolved attempt read. The filer appends the line and rewrites the
    one row (the score, dated by the resolved read, a fresh evidence id,
    `derivation.owner_ruling`); no claim is filed, as the board gate files none. A ruled row's
    old id keeps any verdict it had, so `held_row_missing` still refuses a build that drops it.
    The board owner's page check (`owner_problem`) is part of the shared test. On the re-read
    (MODEL-562's rule for facts) the sweep (`ruled_reading_rereads`) records one `reopen` line
    when the row's board region (`row_region_sha256`, the gate's own fetch) is not the one the
    resolved attempts logged; only then, and only from its own fetch, does the gate read the
    row in `<ruled epoch>:reopen:<region>`. A ruling stops standing only through an agreement
    on another score in such a recorded epoch whose logged region is the one it names; any
    other attempt is ignored, so a forged line cannot withhold the row. A row whose ruling
    stopped standing is read only in that epoch, never from caller bytes; one whose ruling does
    not stand at all is not read.

16. **A confirmed fact no engine reader can read** (MODEL-558, Jamie 2026-11-25, queue 16f).
    Extend the engine's readers first; the two readers come second, and no new verification
    kind or contract field is added. `decision/verify.py` has three deterministic readers for
    structured Hugging Face pages. Each is versioned and abstains whenever the page is in doubt
    (an abstention is no reading, never a mismatch):
    - `hf-config-context@1` reads `model.context_window` from the top-level text model's
      `max_position_embeddings` in a generative model's `config.json` (the config itself or its
      one `text_config`). It abstains on any nested encoder or decoder subconfig that states a
      window, on a window at both levels, on another window field (`n_positions`,
      `max_sequence_length` and the like) that differs, on RoPE scaling at the parent level, on
      a `rope_type` and a `type` that differ, and on any scaling other than a YaRN one that the
      stated window already reflects. The convention (Jamie, 2026-11-25): `model.context_window` stores the
      value the lab states, in prose or a spec table. A config field never overrides a stated
      value and sets the value only when the lab states none. So the reader reads only when the
      fact also cites that repository's README, the README was read, and no cited page states a
      window in any form (`lab_states_context`, a bare integer after a context label included).
    - `hf-readme-spec@1` reads it from README spec tables, bullets and HTML rows, under labels
      that mean context length only. "Max tokens", "max input tokens" and "max sequence length"
      are not read, and only exact token counts are: "256K" and "1M" are not, because decimal
      or binary is the page's own ambiguity.
    - `hf-repo-metadata@1` reads one modality from the declared task (`pipeline_tag` in the API
      JSON; a README's front matter is not read), only when the filed set is exactly that
      modality, no tag, architecture, model type or the task itself names another modality, and
      a structural signal confirms it (`hf_structural_modality`): text input needs text-model
      architectures, a tokenizer file and no processor file for another input; embedding output
      a sentence-transformers pooling module; text output `*ForCausalLM` architectures. A task
      tag alone, singleton included, verifies nothing. It reads `model.weights_openness` as
      `open_weights` only, from the weight files of a public, ungated, non-adapter repository;
      it never reads `closed_weights` (a repository with no weight file may link to weights
      elsewhere; only a gated or absent repository plus an explicit API-only statement can
      support `closed_weights`).

    For the rest, `decision.cited_change.retained_agreement` runs the rule-15 gate on a page
    whose host retains copies. Every rule-15 safeguard holds, and the attempt log and its key
    are shared, so a disagreement on either path blocks both. The epoch is the filed fact's own,
    never the caller's. An answer inside an incomplete attempt counts: one that differs blocks.
    Each subject, facet and epoch gets at most `MAX_ATTEMPTS` (3) attempts, complete or not, so
    a re-run cannot reset the retry budget. In place of the cite-only conditions:
    - the origin's current class is checked before any request, and the host and every redirect
      hop must be classed and retain copies;
    - no deterministic engine reader may find a value for the fact on any retaining source the
      fact cites (`engine_reader_reads`: the verified path wins). Each source is read through
      `StoredRegions` (so a PDF takes its own route), in the context of the fact's full cited set
      (so a reader that needs another source, such as the config reader, sees it); a source that
      cannot be read refuses;
    - it only confirms. An agreed value other than the filed, known one is refused
      (`value_differs`) and the fact is listed for the owner; an agreed absence files nothing
      (`no_value`).

    The record is the `cited_change` block with rule `two-readers-retained-agreement@1`. No
    `Verification` is written, and the build serves the fact as before. A fact that cites a
    cite-only page keeps that citation, so its served basis is not upgraded. The rolling
    re-read re-reads these facts while their origin still retains copies; it reads the origin's
    class first, and one whose origin is now cite-only is listed
    (`retained_agreements_now_cite_only`), not fetched.

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
