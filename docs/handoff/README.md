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
    that serves the offering (for Azure AI Foundry models: Azure, including
    Azure OpenAI / AI Foundry) and states Type 2 (or Type II). Record
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

## Pytest CI shards

The required `Run pytest` check aggregates four file-level jobs. The splitter
uses stable longest-processing-time packing with the measured per-file weights
in `tests/shard_durations.json`. It never divides a module because several
modules share process-wide fixtures. The splitter estimates a new file from its
byte-size share of the measured suite. Inspect the predicted balance after
adding tests with:

```bash
python scripts/pytest_shards.py --shard-count 4 --summary
```

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
