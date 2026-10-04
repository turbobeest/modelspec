# Repository-only offline CLI contract

Historical contract for `python -m cli.modelspec.legacy`. This source is not
distributed in `modelspec-dev` 0.3.0. Agents use the [keyed CLI](../cli-contract.md).
The following contract describes the retired offline implementation only.


The decision commands are the primary interface for agents. Start with
`modelspec snapshot fetch`, inspect valid spec values with `modelspec vocab`,
then run `modelspec decide --template ID` or pass a spec file. DPF's ticket
author calls this CLI.

The offline v1 commands remain a legacy contract for existing callers. Their
stdout, JSON envelopes, and exit codes stay unchanged unless the contract's
major version changes.

## The interface

```
modelspec snapshot fetch [--origin URL] [--api-key KEY] [--json]
                                          download the rank snapshot and, when available,
                                          the decision snapshot and vocabulary
                                          (networked, like feedback)
modelspec snapshot status [--json]        what is cached, how old, which build or decision
modelspec vocab [SECTION] [--json]        inspect the cached decision vocabulary
modelspec decide SPEC.yaml --check        validate a spec without running a decision
modelspec feedback [DECISION_ID] --rating RATING [--note TEXT] [--dry-run] [--json]
                                          rate an answer; sends one request, no key (MODEL-221)
modelspec outcome enable|disable|record|show|export
                                          opt-in, local outcome records (MODEL-211)
```

Legacy v1 commands:

```
modelspec offline rank <use-case> [...]   rank models for a use case
modelspec offline fit [<hardware-id>]     what a given machine can run, or list the machines
modelspec offline class-fit [<task>]      which *class* of model a problem needs (MODEL-100)
```

`modelspec decide [SPEC.yaml] [--template ID] [--check] [--explain …] [--why-not MODEL_ID] [--emit-router-config FORMAT [--out PATH] [--include-rest] [--include-thin]] [--json]`
is the decision engine's command (MODEL-135). It speaks the **decision
contract**, which is versioned on its own (`contract_version`) and documented in
[`decision-contract.md`](../decision-contract.md). With neither `--snapshot-file`
nor `MODELSPEC_DECISION_SNAPSHOT`, it reads the decision snapshot cached by
`modelspec snapshot fetch`. It makes no network request itself.

`modelspec vocab` reads only the vocabulary selected by `decision/current`.
With no section it prints the snapshot ID, section counts, and the next command
to run. The sections are `facets`, `benchmarks`, `domains`, `providers`,
`task-types`, `coverage`, and `templates`. Human output uses compact tables. In the JSON
envelope, `result` contains the selected section or the complete vocabulary
when no section is given. `--search TEXT` matches IDs and labels or names. `--domain DOMAIN`
limits benchmarks to a domain. `--class CLASS` limits benchmarks to domains
where that class has verified coverage. The vocabulary does not declare facet
applicability by class, so `--class` does not remove facets. A missing cache
exits 3 and tells the caller to run `modelspec snapshot fetch`.

Vocabulary domain rows may include `estimate_benchmarks`, the benchmark IDs
that drive stored capability estimates. This list can differ from the domain's
`benchmarks` drill-down. Vocabulary model rows may include `class`, the model's
class from the snapshot; older cached vocabularies can omit both fields.
Facet rows may also include `allowed_values`, the complete finite vocabulary
from the facet registry, even when the snapshot has not observed every value
(MODEL-280). This is a new optional field. Existing `values` rows and their
counts retain their shape and meaning; the vocabulary and CLI envelope
versions do not change.

Number facet rows also carry `better`: `higher`, `lower`, or `neither` (no
inherent direction, such as a parameter count), read from the facet registry
(MODEL-297). The same field is kept in the Worker's `GET /v1/vocabulary`
display bundle and in the compact facet rows that the Worker lookup and MCP
`vocab` return. To prefer less of a `lower` facet, weight its ID with a leading
`-`, as in `-offering.price.input`. This is a new optional field on number rows
only. Older cached vocabularies, and a Worker deployed before this change, omit
it; no existing field's range widens, so the vocabulary and CLI envelope
versions do not change.

`modelspec decide SPEC.yaml --check` loads the cached decision snapshot, parses
the spec with decide's registry, and runs decide's resolve stage. It stops before
filtering and optimisation. Vocabulary coverage is advisory: accepted facets,
benchmarks, domains, providers, or task types that have no published vocabulary
row produce a warning and do not change the exit code. Resolve failures use the
same `decision_failed` code as a real decision. Success exits 0 and reports the
Must count, Prefer count, and snapshot pin. If a spec pins another snapshot, the
command warns but still succeeds. `--json` applies to both success and failure.

`--template ID` reads the template from that cached vocabulary and expands its
`spec` fragment on the client. With an optional spec file, top-level file fields
win and the template's `where` conditions come before the file's `where`
conditions. `--check` validates the expanded spec without running a decision.
`modelspec vocab templates` lists the cached rows. An unknown ID exits 1 and
lists every valid ID. Templates add no decision-spec field and do not change
either the decision contract version or the CLI JSON envelope version.

`modelspec decide SPEC.yaml --compare-to SNAPSHOT_ID` reruns the same spec on
the current cached decision snapshot and a retained generation, then reports
the model-grained difference. `previous` selects the retained non-current
generation; a path to a local snapshot `.gz` is also accepted. A missing ID
exits 1 and lists the cached IDs. The command never downloads history because
the origin does not publish old snapshots. Comparison ignores the spec's own
`snapshot` pin and says so in human output.

Human output starts with entered and left counts (and a changed top model when
applicable), followed by one line per changed model. `--json` uses the common
`schema_version`, `command`, `freshness`, `result` envelope. The result includes
`changed`, old and new snapshot IDs and `as_of` dates, the old and new status,
counts, and model rows for entries, departures and their Must reason, rank and
`may_qualify` changes, and changed price, capability, or Must values with record
IDs where the decision exposes them. `spec_snapshot_ignored` records whether
the input spec contained a non-`latest` pin. No change is a successful result with
`changed: false`; both changed and unchanged comparisons exit 0.

Without `--json`, `modelspec decide` prints a short readable summary: the
status, the answer (a tied group with its tie-breakers, or the single pick,
per the decision's `answer` block), the top five rows with cost per task, the
leading contributions behind the top row, and how many models may qualify.
A `no_feasible` decision prints the `relax` suggestions. `--json` is unchanged
and stays byte-identical to the Worker's `POST /v1/decide` body.

Decision contract 2.12 adds an optional `reading` block (MODEL-284). It is
derived from the engine's answer and the requirements it used, with empty
lists omitted. `tied` names the engine's best-band tie (`answer.members`), including
members beyond the result limit. Present that group as a tie; a tie-breaker
is a conditional choice. A `do_not_claim` line also names a tied
`with_estate.answer`; report that answer as a tie among its own members.
`estimates` names estimated fields, such as
`model.fits_hardware` and `results.estimates`. Hardware membership is a memory
estimate for some supported quantization, not a measured fit for a concrete
quantization, context length, KV cache and runtime workload. `do_not_claim`
contains short reporting prohibitions derived from these facts and the
objective. A cost or mixed-objective rank does not establish a quality rank.

An `invalid_spec` refusal may also carry `reading.not_applied`, the field IDs
or paths rejected by validation. No decision ran for that request. The
existing `error.issues` supplies the reasons. If an agent removes a requirement
and retries, it must still tell the user that requirement was not applied.
The engine cannot recover requirements absent from the retried spec, and the
block never repeats free-text task content.

On a successful response, `not_applied` also names requested capabilities for
which the snapshot has no domain evidence. These labels do not become gates
or proof that the requested capability was evaluated.

The block is absent when there is nothing to report and is limited to 600
UTF-8 bytes of compact JSON. If identifiers exceed that budget, `omitted`
counts the unlisted `tied` or `not_applied` identifiers. The complete tie stays
in `answer.members`, rejected fields in `error.issues`, and requested
capabilities in the spec. Agents must read those complete lists before
reporting. The updated decide page decoder ignores the block. This is an
additive change in decision contract `2.12`; no existing field's range widens.
Published contract `2.11` has no `reading` field. The CLI envelope and export
versions remain unchanged.

`modelspec decide SPEC.yaml --why-not MODEL_ID` answers "why not this model?"
from the finished decision. It runs at `explain: full` internally so an
eliminated model is known. It cannot be combined with `--check` or
`--compare-to`. The verdict is one of:

- `eliminated`: the Must the model failed, with its value and how far it was
  from the threshold, and what relaxing that Must would admit.
- `may_qualify`: the facets that are unknown for it. Unknown is never ranked
  last and never dropped.
- `ranked`: its place among models, and the weight change from `tipping_points`
  that would put it first.
- `not_in_decision`: the ID is not a candidate, or the `limit` cut it.

`--json` prints `{"contract_version", "command", "why_not": {...}}`. The
`why_not` object is CLI output, not part of the decision contract, and carries
`model`, `verdict`, `model_rank`, `ranked_models`, `offerings`, `failed`,
`unknown`, `constraint_costs`, `tipping_points` and a one-line `summary`.

`modelspec decide SPEC.yaml --emit-router-config FORMAT [--out PATH]` turns
the decision into a router or gateway allow-list (MODEL-208). ModelSpec decides
which models belong on the list; the router picks among them per request. The
file is configuration only: ModelSpec never proxies inference, never holds a
prompt, never calls the router, and never writes a credential or a referral
parameter.

The list is the decision's `bands` (contract 2.7). By default it holds the
`best` band. `--include-rest` adds the `rest` band: the other ranked models,
all of which passed every Must. `--include-thin` adds the models with not
enough evidence yet, labelled `thin` in every format. Order is best, then
rest, then thin, each in band order. A listed model carries each of its ranked
offerings as a route, the band's own offering first.

| `FORMAT` | What it writes | Checked against |
| --- | --- | --- |
| `litellm` | A LiteLLM proxy `config.yaml`: one `model_list` deployment per route, `model_name` the ModelSpec model ID, `model_info.id` `modelspec:<offering>`. No `api_key`: LiteLLM reads each provider's own environment variables. | `ConfigYAML` in `litellm.proxy._types` (litellm 1.103.0), and the proxy's own `load_config` |
| `openrouter` | The body of OpenRouter's `POST /api/v1/guardrails`: `allowed_models`, and `allowed_providers` when every route names a provider | `CreateGuardrailRequest` in `https://openrouter.ai/openapi.json` |
| `json` | ModelSpec's own format: per model the band, `p_best`, `p_beats_leader`, score, routes (provider, region, tier, cost) and reasons | [`schemas/router-config-v1.schema.json`](../../schemas/router-config-v1.schema.json) |

Every file carries an audit header: `decision_id`, `spec_hash`, `snapshot`,
`contract_version`, and the command that regenerates it. In LiteLLM the header
is a YAML comment block. In OpenRouter it is the guardrail's `description`. In
`json` it is the `audit` object.

The snapshot does not publish each provider's or router's own model ID. The
file writes a `<...>` placeholder in its place, and `json` writes
`provider_model_id: null`. A router rejects a placeholder, so an unedited file
admits nothing. It never admits a guessed ID. The command warns on stderr.

The config goes to stdout, or to `PATH` with `--out`. With `--out`, stdout is
what `decide` prints without the flag (the readable summary, or with `--json`
the unchanged decision JSON), and a one-line note goes to stderr. `--json` without
`--out` exits 1, because stdout can carry only one document. The flag cannot be
combined with `--check`, `--compare-to` or `--why-not`. `--out`,
`--include-rest` and `--include-thin` need `--emit-router-config`. Errors exit
1 with these codes: `router_config_usage`; `no_qualifying_models`
(`no_feasible`); `no_bands` (a lexicographic or Pareto objective has no
bands); and `empty_allow_list` (the selected bands are empty, for example when
no model has enough evidence to lead; the message names the flag that would
add models).

Options on legacy v1 `offline rank`: `--limit/-n`, `--open-weights`, `--fits <hardware-id>`,
`--max-cost <dollars per million input tokens>`, `--price-sensitivity <0..1>`,
`--json`, `--require-fresh`, `--include-rehosts`.

`fit` also accepts `--limit/-n`, `--json`, `--require-fresh`,
`--include-rehosts`, `--host <id>`, `--host-ram <GB>` and `--include-offload`
(see "Hosts and offload" below). These options
are additive and do not change the meaning of the commands above. `--origin`
is an option on `snapshot fetch`; it defaults to `https://modelspec.dev`.
`--api-key` is an option on `snapshot fetch` too; it has no default and the
supported way to supply one is the `MODELSPEC_API_KEY` environment variable
(see "A keyed origin" below).

The rank export is the required result of `snapshot fetch`. The decision
snapshot and vocabulary are optional. The command tries the requested origin
first. If that origin returns 404 for a decision route or cannot answer that
route, the command tries `https://modelspec.dev` without an API key. If neither
origin supplies a valid matching pair, the command keeps the existing decision
cache and still completes the rank fetch. Human output reports `decision
unavailable`; `--json` reports the same result in
`result.decision_snapshot.available` and `result.decision_snapshot.error`.
The cache stores each matching pair under
`decision/<snapshot_id>/{snapshot.json.gz,vocabulary.json}` and commits a fetch
by atomically replacing the text file `decision/current`. A fetch therefore
leaves readers on either the complete old generation or the complete new one;
after the switch, cleanup keeps the current and previous generations.

`class-fit` accepts a task description as its argument plus `--emits`,
`--consumes` (comma-separated), `--decides`, `--json` and `--require-fresh`.
It is a **new command under the existing envelope**: `schema_version` stays
`"1.0"`, because no field of any existing command's `result` widens.

### `class-fit`: which class, before which model (MODEL-100)

Legacy v1 `offline rank` answers "which model?" once you have decided you want an LLM.
`class-fit` answers the question before that one, and it is the only command
that will tell you the catalogue has nothing for you.

`result.fit_status` is one of:

| value | meaning | exit |
| --- | --- | --- |
| `resolved` | exactly one class survives the caller's constraints | 0 |
| `partial` | **two or more survive, and they are deliberately not ordered.** ModelSpec holds no measurement that ranks one class against another, so it returns every survivor plus the question you must settle | 0 |
| `unavailable` | no class in the published taxonomy emits what was asked for | 2 |
| `refused` | the request cannot be read; `result.refusal.code` says why and what would have worked | 1 |

Two things a caller must not read into the answer. **The candidate list is
sorted by class id and carries no score** — there is no ordering hidden in it,
and `result.policy.orders_classes` is `false` beside every answer. And
`result.candidates[].catalogue.evidence_state` distinguishes `populated`,
`empty` (the catalogue holds no model of that class — a real answer) and
`unknown` (nobody supplied the counts). `empty` is not `unknown` and neither is
a recommendation against the class.

`result.composition` may name a pair of classes as a **sequence** rather than a
choice — "this one, then that one on its abstentions". That is not an
ordering: neither class is placed above the other, and no number is attached.

The whole rule, including the term list the matcher uses, is published keyless
at `https://modelspec.dev/api/rank/class-fit.json`, so a caller can run the
same match locally without calling anything.

## Feedback (MODEL-221)

`modelspec feedback` sends one rating of an answer to
`POST https://api.modelspec.dev/v1/feedback` ([`feedback-api.md`](../feedback-api.md)).
It is the second command that uses the network, and it sends exactly one
request, only when run.

```
modelspec feedback [DECISION_ID] --rating reliable|unreliable|trustworthy|untrustworthy|confusing
                   [--note TEXT] [--trying-to-decide TEXT] [--template ID]
                   [--endpoint URL] [--dry-run] [--json]
```

- **No key.** It never reads `MODELSPEC_API_KEY` and sends no `Authorization`
  header. The body is `{"rating", "client": "cli"}` plus the options given, and
  nothing else: no machine, user or install identifier.
- The body is printed to stderr before it is sent. `--dry-run` prints it to
  stdout as `{"command": "feedback", "dry_run": true, "endpoint", "body"}` and
  sends nothing.
- `--json` prints `{"command": "feedback", "result": <the Worker's answer>}`.
  Check `result.status`: `recorded`, or `not_recorded` while storage is off.
- A refusal exits 1 with `{"command": "feedback", "error": {"code", "message"}}`
  on stderr, the code being the Worker's (`invalid_request`, `rate_limited`, …)
  or `origin_unreachable` / `unexpected_response`.

## Outcome records (MODEL-211)

`modelspec outcome` keeps an opt-in, local log that answers one question: was
this decision adopted, and did the task succeed? It is ADR 0004 step 1 under the
REV-9 rules. What the log holds and what stays local is in
[`outcome-privacy.md`](../outcome-privacy.md). How DPF calls it is in
[`dpf-outcome-integration.md`](../dpf-outcome-integration.md). No `outcome`
command makes a network request.

```
modelspec outcome enable [--yes]          print what is recorded; turn recording on if you agree
modelspec outcome disable [--delete]      turn it off; --delete also deletes every record
modelspec outcome record DECISION_ID --adopted MODEL[/PROVIDER] --result success|partial|failure
                         [--task-kind KIND] [--latency-ms N] [--cost-usd X]
                         [--decision FILE] [--json]
modelspec outcome show [--limit N] [--json]
modelspec outcome export [--out PATH]     JSON Lines, every line re-checked against the schema
```

**Consent.** Recording is off until `enable` is run. `enable` prints every
field below and asks for a yes. With no terminal it exits 1 unless `--yes` is
passed. The consent file is `~/.modelspec/outcomes-consent.json`
(`$MODELSPEC_HOME` overrides the directory) and holds
`{"consent_version": 1}`. A consent with any other version counts as off.

**`record` while off** reads nothing, writes nothing and exits 0. With `--json`,
stdout is `{"command": "outcome record", "recorded": false, "reason": "disabled"}`.

**`record` while on** appends one record to `~/.modelspec/outcomes.jsonl` and
exits 0. With `--json`, stdout is
`{"command": "outcome record", "recorded": true, "record": {…}}`. It exits 1,
with `error.code` on stderr, for:

- `invalid_record`: a value failed the schema. The message names the field and
  the rule, never the value.
- `invalid_adopted`: `--adopted` is not `lab/model`, `lab/model/provider`,
  `other` or `other/provider`.
- `unknown_model` or `unknown_provider`: the model or provider is not in the
  cached decision vocabulary. That vocabulary is the only catalogue, and
  neither a stub nor a `--decision` file can vouch for a model. The check
  keeps private names out of the log. Pass `--adopted other` for a model
  ModelSpec does not list.
- `invalid_decision` or `unreadable`: the `--decision` file is not a decision,
  names a different decision ID, or has a decision ID that is not the hash of
  its spec hash and snapshot.
- `unwritable`: the log cannot be written.

**The record.** These fields, and no others. The schema is `OutcomeRecord` in
`cli/modelspec/outcome.py`. It has `extra="forbid"` and strict types, and
`tests/test_outcome.py` pins the field set.

| field | type |
| --- | --- |
| `record_version` | `1` |
| `decision_id` | `dec_<24 hex>` |
| `spec_hash` | `sha256:<64 hex>` or null |
| `snapshot` | `snap_<16 hex>` or null |
| `contract_version` | the decision contract's `major.minor`, or null |
| `adopted_model` | a catalogued `lab/model`, or `"other"` |
| `adopted_offering` | a catalogued provider slug, or null |
| `was_leader` | bool or null |
| `in_best_band` | bool or null |
| `result` | `success`, `partial` or `failure` |
| `task_kind` | a decision-contract `task_type`, or null |
| `latency_ms` | integer, 0 to 86,400,000, 3 significant figures, or null |
| `cost_usd` | finite number, 0 to 10,000, 3 significant figures, or null |
| `recorded_at` | `YYYY-MM-DDTHH:MMZ`, UTC |
| `cli_version` | the installed CLI's public release (no `+local` segment), or null |

`spec_hash`, `snapshot`, `contract_version`, `was_leader` and `in_best_band`
come from the decision. `record` finds the decision in the `--decision` file
if one is given, and otherwise in the stub that `decide` kept. If it finds
neither, those five fields are null. `was_leader` compares the adopted model
with `bands.leader` (or `answer.leader`). `in_best_band` checks the adopted
model against `bands.best`. For `other`, both are false.

**`decide` while on** keeps a stub in `~/.modelspec/decision-stubs/` holding
the decision ID, spec hash, snapshot, contract version, leader and best-band
model IDs. It keeps at most 500 stubs. It also prints one line to stderr naming
the `outcome record` command to run. stdout, including `--json`, is unchanged,
and `decide` never writes an outcome record. While recording is off, `decide`
does neither.

**`show` and `export`** validate every stored line again. A line that fails,
for example one edited by hand to add a field, is left out and counted on
stderr (`show --json` reports it as `refused_lines`).

**Versioning.** `outcome` is a new command group. It does not change the
envelope or any field of an existing command, so `schema_version` stays
`"1.0"`. A new record field bumps `record_version` and the consent version, so
recording stays off until the person reads the new text and consents again.
Upload is not built; the design is
[`design/outcome-upload.md`](../design/outcome-upload.md).

## The JSON envelope

```json
{
  "schema_version": "1.0",
  "command": "rank",
  "freshness": {
    "fetched_at": "2026-09-09T20:53:00+00:00",
    "age_days": 0.0,
    "stale": false,
    "stale_after_days": 30,
    "origin": "https://modelspec.dev",
    "build_commit": "082e76591c545a0f...",
    "built_at": "2026-09-09T20:47:41+00:00"
  },
  "result": [ ... ],
  "ranking_status": "partial",
  "ranked_count": 122,
  "unranked_count": 1103
}
```

`freshness` is on every answer, and `build_commit` identifies the exact export a
selection was made against. Record it. A recommendation whose basis cannot be
reconstructed later is not evidence, and DPF-22's honest-broker rule requires
that it can be.

The stable envelope fields are `schema_version`, `command`, `freshness`, and
`result`. `freshness` contains `fetched_at`, `age_days`, `stale`,
`stale_after_days`, `origin`, `build_commit`, and `built_at`. `snapshot status
--json` uses the same envelope: its `result` contains `present`, `path`, and
`size_bytes` when a snapshot exists; for an absent snapshot, `freshness` is
`null` and `result` contains `present: false` and `message`.

`snapshot status --json` also adds `result.decision_snapshot`. This additive
object always has `present` and `path`. When present, it also has `snapshot_id`,
`as_of`, `age_days`, `valid`, `signature_verified`, `signature_status`, and
`signature_key_id` when valid. A corrupt
cached file has `present: true`, `valid: false`, and `error`; it does not change
the rank snapshot's status or exit code. `age_days` is the age of the
cached file, not the snapshot's `as_of` date. The CLI verifies Ed25519 offline
against its pinned key set and reports `signature_verified: true`. Before the
first key is provisioned, it reports
`unsigned (ed25519 key not yet provisioned)` and `signature_verified: false`.
The fetch always checks the decision snapshot's `content_hash` and
that its `snapshot_id` derives from that hash before it replaces any cached
file.

`offline rank --json` keeps `result` as the ranked list promised by schema 1.0.
It adds `ranking_status`, `ranked_count`, and `unranked_count` at the envelope
level; the counts are before `--limit`, and `result` is still capped by it.
This is a compatible addition under schema version 1.0: fields are added to the
existing envelope and the type and shape of `result` do not change. The separate
export file `rankings.json` has schema version 2.0 because its profile value
changed from a list to a report; that version is not the CLI envelope version.

`ranking_status` is computed before `--limit` and is one of:

* `complete`: every candidate that passed the filters is rankable;
* `partial`: ranked candidates and insufficient-evidence candidates both exist;
* `unavailable`: candidates passed the filters, but none has enough evidence to
  receive a rank; or
* `empty`: no candidate passed the filters.

The CLI uses the status to avoid treating a partial shortlist as a no-match:
`complete` and `partial` exit 0; `unavailable` and `empty` exit 2. Thus an
empty ranked list with `ranking_status: unavailable` is distinguishable from an
empty catalogue match (`ranking_status: empty`) without changing the meaning of
the result list. `--limit 0` does not change the status or exit code.

### `unranked_candidates`: the models a ranking could not rank (MODEL-110)

`unranked_count` alone lets a stale shortlist look authoritative: a caller
asking for the best coding model never learns that a model released last week
exists and has no scores yet. Every rank answer therefore names them:

```json
"unranked_candidates": {
  "count": 848,
  "cap": 10,
  "models": [
    {"model_id": "anthropic/claude-opus-5-5", "display_name": "Claude Opus 5.5",
     "release_date": "2026-09-22", "reason": "no_scores",
     "missing_benchmarks": ["aider_polyglot", "arena_elo_coding", "…"]}
  ]
}
```

* **Who is named.** A model that passed every filter the request applied
  (`--open-weights`, `--fits`, `--max-cost`, rehosts), whose `model_type` or a
  subtype is one of the profile's `preferred_types`, and that is still
  unranked. The type test is what makes it "a candidate waiting for evidence"
  rather than "the rest of the catalogue": an embedding model with no coding
  scores is not a coding candidate. So `count` ≤ `unranked_count`, which is
  unchanged and still counts every unrankable model in the pool.
* **Order.** Newest `release_date` first; a model with no date, or a date that
  is not `YYYY`, `YYYY-MM` or `YYYY-MM-DD`, sorts last; ties by `model_id`.
* **Bound.** At most `cap` (10) are named. `count` is never capped.
* **`reason`** is one of three, the ones the floors can actually tell apart:
  `no_scores` (no score on any benchmark the profile weighs),
  `below_count_floor` (fewer than `min_benchmark_count`) and
  `below_coverage_floor` (under `min_benchmark_coverage`). A model failing both
  floors is `below_count_floor`. Rehosts, type, hardware and price are
  *filters*, not reasons: a model they remove was never a candidate.
* **`missing_benchmarks`** are the profile's weighted benchmarks the model has
  no score for. `release_date` is the card's, verbatim, or `null`.

The block is always present, `{"count": 0, "cap": 10, "models": []}` when
there is nothing to name, on exit 0 and exit 2 alike. It is disclosure only:
it is computed in `pipeline.ranking.rank_report`, beside the ranking and from
the same scored rows, and nothing in `result` changes. The rank API, the MCP
`rank` tool and `rankings.json` carry the same block from the same function.

Without `--json`, `rank` prints it as one line under the table:

```
848 models are not ranked yet (not enough benchmark evidence), newest first: anthropic/claude-opus-5-5, openai/gpt-6-luna, …, and 838 more.
```

**Versioning.** A new, always-present field on the envelope and on each
`rankings.json` profile report, and a new `release_date` on each
`candidates.json` row. No existing field's range widens, so under MODEL-59
nothing bumps: the envelope stays `"1.0"`, `rankings.json` `"2.0"`,
`build.export_schema_version` `"3.0"`. A snapshot from before this field has no
`release_date`; its candidates are named, all undated, ordered by id.

When `--json` is supplied and a command fails before it can produce an answer,
it writes this machine-readable error object to stderr and writes no answer to
stdout:

```json
{
  "schema_version": "1.0",
  "command": "rank",
  "error": {"message": "..."}
}
```

The same `schema_version` rule applies to successful JSON output and JSON
errors. Without `--json`, failures use a human-readable `error:` line on
stderr. A missing snapshot from `snapshot status --json` is a status response
with exit 3 (and `freshness: null`), not a traceback.

## Exit codes

| code | meaning | what a caller should do |
| --- | --- | --- |
| 0 | an answer | use it |
| 1 | usage or runtime error | fix the call; the message is on stderr |
| 2 | no ranked answer: nothing matched the constraints (`empty`), or no matching candidate had enough evidence (`unavailable`) | inspect `ranking_status`; loosen a constraint or obtain more evidence |
| 3 | no snapshot | run `modelspec snapshot fetch` |
| 4 | stale snapshot and `--require-fresh` was given | fetch, or drop the flag |
| 5 | a keyed origin refused the credential (no key, unknown key, revoked key) | supply or replace the key; retrying the same one will not help |
| 6 | a keyed origin rate-limited the credential | wait for the window named on stderr, then retry |

**2 is not an error.** "Nothing in the catalogue fits your constraints" is a
truthful result, and conflating it with a failure makes a caller retry something
that will never succeed.

**5 and 6 belong to `snapshot fetch` against a keyed origin.** They are the
only codes MODEL-71 added, they are produced by no other command, and no
unkeyed origin produces them: against `https://modelspec.dev`, `snapshot fetch`
still exits 0 or 1 and nothing else. Every other exit code means exactly what
it meant before.

## What we promise

Within a major `schema_version`:

* Existing fields keep their names, types and meaning.
* Exit codes keep their meaning.
* New fields may be **added** to any object. Parse permissively.
* New commands and new options may appear.
* `freshness` is always present on a `--json` answer.

We may change, only with a major version bump:

* Removing or renaming a field, or changing its type or units.
* Changing what an exit code means.
* Changing the shape of `result`.

### Versioning rule (MODEL-59)

Any change that **widens** a contract field's range bumps the **major** version
of that contract. Widening means a client that handled every old value can now
receive one it does not handle. Examples:

* a number becoming nullable;
* a new enum value a client must handle;
* a field that can now be absent.

Snapshot data is versioned by `build.export_schema_version`; the CLI `--json`
envelope by `schema_version`. Purely additive changes (new optional fields, new
flags, new files) do not bump the major. The CLI already refuses a snapshot
whose export major differs from its own, so a widening fails cleanly with an
error instead of crashing a client that assumed the old range.

The MODEL-53 nullable `predicted_decode_tps` below predates this rule and was
shipped without a bump; that is the case the rule exists to prevent.

### The `decision-model` class, and two kinds of null (MODEL-97/98)

`build.export_schema_version` is **3.0**. One bump, two tickets, because
consumers should absorb one break rather than two (Jamie, 2026-09-20).

**What widened.** `model_type` gained `decision-model`:

> evaluates supplied state against caller-defined typed questions, returning
> calibrated choices, scores or probabilities; generates no text.

It is published in `/api/models/<id>.json`, `index.json`,
`/api/rank/candidates.json` and the graph nodes. A new enum value is the
textbook widening under the MODEL-59 rule above, so it bumps the major. (The
earlier non-token classes — `miscellaneous`, `time-series`, `vision-encoder`,
`text-encoder` — shipped without a bump. They predate the rule and are the
omission it exists to prevent; they are not a precedent.)

**What a pre-bump CLI does.** It refuses before reading a row:

```
error: export_schema_version 3.0 is incompatible with this CLI (expects 2.x)
```

Exit 1, or the documented `--json` error object; no traceback, and a cached
snapshot is never clobbered. A 2.x CLI therefore never sees a `decision-model`
row, never scores one and never mis-parses one. **Upgrade the CLI, then
`modelspec snapshot fetch`.** A 3.x CLI refuses a 2.0 snapshot the same way.

**The CLI `--json` envelope does not move.** `schema_version` stays `"1.0"`:
no envelope field carries `model_type`. `rank` and `fit` rows are unchanged,
as are the exit codes. `rankings.json` stays `"2.0"` and the policy export
stays `"1.0"`; they version different documents.

**Inapplicable is not unresearched.** A `null` has always meant "not yet
researched". For some fields on some classes there is nothing to research —
a model that emits no text has no `modalities.text.max_output_tokens` to find.
`/api/models/<id>.json` now carries a derived sibling block:

```json
"applicability": {
  "basis": "model_type",
  "model_type": "decision-model",
  "not_applicable": ["capabilities", "inference_performance.api_tps_output",
                     "modalities.text.max_output_tokens", "…"]
}
```

Each entry is a dotted path from the card root; a path naming a section means
every field beneath it. **This is additive, not a widening**: the `card` tree
is still the frontmatter verbatim, no field in it changes type, name, meaning
or range, and a consumer that ignores `applicability` reads exactly what it
read before. It would not have bumped the major on its own; it rides
`decision-model`'s bump.

| what you see | what it means | what to do |
| --- | --- | --- |
| `null`, path **not** in `not_applicable` | Nobody has researched it. | Treat as unknown. It is a real gap, and it can be closed. |
| `null`, path **in** `not_applicable` | This class of model cannot have it. | Do not render it as a gap, do not count it against the card, and do not ask for it. |

The block is **derived from `model_type`**, never written on a card, so it
cannot contradict the card it describes and cannot be lost in a YAML
round-trip. It says nothing at all for a card whose `model_type` is absent or
unrecognised: an unknown class is unknown, not empty. Architecture fields are
never listed — an undisclosed parameter count is *unknown*, not meaningless.
Reasoning: [`design/class-and-null-semantics.md`](../design/class-and-null-semantics.md).

**Ranking is unchanged and stays safe.** A decision model carries no benchmark
scores, so it comes back `rank_status: "unranked"`, `unranked_reason:
"insufficient_benchmark_evidence"` and `score: null` — never a low score, and
never in `result`. No new `unranked_reason` value was added, deliberately:
that field rides in rows under envelope `schema_version "1.0"`, and widening
it would cost a second bump to say something a caller cannot act on. The
floors are untouched.

### Benchmark coverage gained `verified` rows without a bump

`models_covered` in `/api/benchmarks/<id>.json` used to list only the flat
`benchmarks.scores` dict on each card, so every row's `attribution` was
`unverified-legacy`. It now also lists each reviewed `benchmarks.evidence`
record, with `attribution: "verified"`. A record replaces the card's flat
score for the same benchmark, and a card with several records for one
benchmark gets one row per record. `models_covered` in `catalogue.json` counts
distinct models, not rows.

The new `attribution` value widens that field's range. Under the rule above it
would bump the major. `build.export_schema_version` stays **3.0** on the
MODEL-74 reasoning: the CLI snapshot files (`index`, `candidates`,
`profiles`, `hardware`, `hosts`) carry no coverage rows, and the CLI never
reads `/api/benchmarks/`, so a bump would make every 3.x CLI refuse new
snapshots with no consumer to protect.

Every row carries the same keys. A `verified` row fills `unit`, `date_type`,
`source_kind`, `model_id_as_evaluated`, `benchmark_version`, `configuration`
and `verified_at` from its record, and takes `as_of` and `source` from the
record's `evidence_date` and `source_url`. An `unverified-legacy` row has those
seven keys set to `null`, and its `as_of` and `source` are still the card's
one collection date and source list.

### Policy fields, and the one major bump they cost (MODEL-77)

### Graph Model property removed without a bump (MODEL-74)

Model nodes in `/api/graph/nodes.json` and the graph views no longer carry
`card_completeness` (renamed `applicable_field_coverage`, now an internal
`ModelCard` statistic only). `build.export_schema_version` stays **2.0**:
Jamie decided 2026-09-18 that this removal does not bump the export major.
The CLI snapshot files (`index`, `candidates`, `profiles`, `hardware`) never
carried the key, and the CLI does not read the graph views, so a bump would
have made every 2.x CLI refuse new snapshots with no consumer to protect.

`build.export_schema_version` is **2.0**. `/api/models/<id>.json` publishes a
card's frontmatter verbatim, so reshaping the policy fields reshapes that tree.
Two widenings ship as one bump because they are one decision:

* `licensing.commercial_use` was `true | false | null`. It is now a string:
  `allowed`, `restricted`, `prohibited`, `unspecified` or `withheld` — the same
  `UsePermission` its four siblings (`defense_use`, `government_use`,
  `medical_use`, `academic_use`) already used. A boolean could not say
  "allowed up to 700M monthly active users", which is the actual answer for the
  169 llama-community, gemma and deepseek cards in the catalogue.
* `availability.primary_provider.data_residency` was a list that defaulted to
  `[]` on every card, so "no residency guarantees" and "nobody has looked" were
  the same value. It is now `list | null`, beside
  `data_residency_disclosure` (`unresearched` | `published` | `withheld`).

Both are range-widening under the rule above, so under MODEL-59 each would bump
the major on its own. Doing them in one pass costs one bump instead of two.
A 1.x snapshot is refused by a 2.x CLI with the usual message, and a snapshot
carrying no `export_schema_version` at all is a pre-2.0 tree and is refused the
same way.

**How to treat `withheld` versus `unspecified`/`null`.** They are not
interchangeable and a consumer must not collapse them:

| value | what it means | what a caller should do |
| --- | --- | --- |
| `unspecified` (`commercial_use`), `unresearched` (`data_residency`) | Nobody has determined this. The catalogue is not asserting anything about the licence. | Treat as unknown. Do not infer permission or prohibition. Do not ask again: there is nothing to fetch. |
| `withheld` | The determination exists and is deliberately not published in this tree. | Treat as unknown **for the purposes of the public data**, but as *obtainable* — the answer exists and is not on this card. Never render it as "not researched". |
| `allowed` / `restricted` / `prohibited` | A determination, with its citation. | Use it, and carry the citation. For `restricted`, read `commercial_use_conditions` — the value alone is not actionable. |

#### The two senses of `withheld` (MODEL-79, decided 2026-09-17)

`withheld` means one thing in the contract and always has: **a determination
exists, and this card is not where it is.** It never means nobody looked. What
differs between the two fields is *what kind of thing* was determined, and a
consumer who assumes "withheld = a value is being held back for sale" will
misread most residency cards.

| field | what a `withheld` card is telling you |
| --- | --- |
| `licensing.commercial_use` | **Determined, not published to you.** A licence was identified, read and decided — allowed, restricted or prohibited. The value is held back; ask for it. |
| `availability.primary_provider.data_residency_disclosure` | **Determined — which may be that the provider publishes nothing.** Either a region list was read from the provider's own page, or the provider's documents were read and commit to no region at all. Both are findings, and both are held back; ask for it. |

So for residency, `withheld` answers "has anyone looked?" with *yes*, and
leaves "is there a region list to have?" open. That second question has a real
answer for every withheld platform, and it is sometimes "no — we read their
documents, and they name no processing location". A buyer who needs EU-only
inference is told something useful by that: not "we don't know", but "there is
nothing here to check your requirement against". Under the old shape, this
platform and one nobody had ever looked at were the same card.

**What is *not* withheld.** A platform recorded as unreachable — every
connection refused or timed out from the network the work was done on — stays
`unresearched`, because nobody successfully looked. Two of the fifty platforms
are in that state. `unresearched` is also what a local runtime carries
(`ollama`, `lm_studio`, …): a model on hardware you own has no region-shaped
answer at all, and `withheld` would advertise one that cannot exist.
`scripts/residency/platforms.py` holds that list and the reasoning;
`scripts/residency/report.py disclosure` prints what each of the fifty
publishes.

`withheld` exists because the alternative is a lie at scale. Once
determinations are made and held back, a public `commercial_use: null` would
assert "not yet researched" on roughly 1,300 cards where it is false, in the
one place this catalogue's reputation lives. The marker is carried **in the
value itself**, not in a companion "available elsewhere" flag, so that a
consumer reading only `commercial_use` cannot miss it.

**Sources are not optional.** A determination carries
`commercial_use_source` / `data_residency_source`: the document it was read
from (`kind`, `url`) and the day it was read (`read_on`, ISO), plus an optional
short `quote` of the operative clause. Licence terms are rewritten without
notice, so an undated reading is not evidence. A value without a source fails
card validation; a card that is `unspecified` or `withheld` carries no source
at all, so an empty answer can never look cited.

Eight cards carry `kind: legacy-import` with no URL and no date. Those are the
eight `commercial_use: true` values that existed before this shape, kept rather
than discarded and kept honest rather than dressed up — the same admission
`evidence_basis: unverified-legacy` makes about a benchmark score. A test
freezes that kind to exactly those eight cards.

**Not served yet.** These fields are on the cards and in
`/api/models/<id>.json`. The CLI `--json` envelope does not carry them, so its
`schema_version` stays `"1.0"`; `rank` and `fit` are unchanged. The
`policy-check` endpoint is MODEL-80.

### Two sources' data removed, without a bump (MODEL-117)

On 2026-09-24 every value from two sources whose terms do not permit this
project's use was removed from the catalogue, with the benchmarks they own.
`build.export_schema_version` stays **3.0**, `rankings.json` stays `"2.0"` and
the CLI envelope stays `"1.0"`, because no contract field's range widened:

* **Every removed value lived in a collection that was already variable.**
  Per-card `benchmarks.scores` maps and `benchmarks.evidence` lists,
  `benchmark_scores` and `verified_benchmarks` in `candidates.json`, the
  profile `benchmark_weights` and `benchmark_ranges` maps in `profiles.json`,
  `/api/benchmarks/<id>.json` files, `catalogue.json`'s `active_ids` and its
  `counts` map (keyed by the statuses present; `historical` was already
  absent), and the eligibility report's accepted results. A consumer that
  handled an empty or shorter collection before handles this one.
* **No field that was always present is now absent.** The card slot
  `sources.<name>_url` for the removed source stays, as `""`, the value every
  other card already had. Removing the slot itself would be a removal under the
  promise above and would need a bump; that is Jamie's call.
* **Nothing became nullable that was not.** `inference_performance.api_tps_output`
  (now `null` on the 139 cards whose value came from the removed source) and a
  benchmark page's `saturation.top_score` were already `null` on most cards and
  pages.
* **No enum gained a value.** The catalogue can now hold **zero** active
  benchmarks. `active` is still a disposition, and an empty active set is a
  state the eligibility gate always allowed: it fails closed.

### Deprecated: CLIs older than MODEL-53

CLIs older than #56 (MODEL-53, merge `1d8dd53`) are unsupported. They raise
`TypeError` in `offline fit` against snapshots with a null
`predicted_decode_tps`. Upgrade.

We make no promise about:

* The **ordering or content of results.** The catalogue changes daily — that is
  the point — and the ranking rules will be corrected as defects are found.
  Pin a snapshot if you need reproducibility.
* Human-readable output. Only `--json` is a contract.
* The graph commands (`stats`, `search`, `info`, `compare`, …). Those need a
  local FalkorDB and are for interactive exploration.

## Freshness, and why a stale answer still comes back

A snapshot older than 30 days is served anyway, with a warning on stderr. A
dated answer that says how dated it is beats no answer — the same continuity
rule the dpf library follows. `--require-fresh` inverts this for callers who
would rather fail.

## What the numbers are worth

Rankings are computed from the benchmark scores on the model cards. Each ranked
or unranked row reports `evidence_basis` for the inputs that contributed, not a
certification of the composite or of model quality. `_basis` in
`pipeline/ranking.py` emits one of:

* `none` — no usable weighted measurement contributed
* `unverified-legacy` — every contributing measurement is a legacy card value
* `mixed` — reviewed and legacy measurements both contribute
* `partial-verified` — every present measurement is reviewed, but the profile
  is incomplete
* `verified` — every positively weighted benchmark is present and reviewed

A live catalogue contains more than one of these. `verified` is not a quality
verdict and is not applied to incomplete evidence (see
`tests/test_ranking.py`). Older cards may still be `unverified-legacy`; that
label is no longer universal.

Hardware fit and predicted decode rates are **computed** from memory capacity
and bandwidth, not measured; no one has run these models on these devices.

Treat both as a shortlist to investigate, not a verdict. The interface says so
in every response so that a calling agent can pass the caveat on rather than
laundering it into confidence.

### `predicted_decode_tps` can be `null` (MODEL-53)

A model that fits in memory is not necessarily a model that decodes tokens.
Time-series forecasters, vision encoders (classification, segmentation,
detection), and text encoders (fill-mask, token classification) fit on a
device the same as any other set of weights, but there is no token being
decoded, so a tok/s figure would be invented. As of this change, `offline
fit`'s `predicted_decode_tps` (and the `fastest_predicted_decode_tps` behind
`--fits`) is `null` for these rows instead of an invented number.

This is a real widening of the field's range, not something the contract
already promised: `predicted_decode_tps` used to always be a number when the
row was present at all. We are making it anyway, without a major version
bump, because the field's **name and meaning stay exactly what they were** —
"the predicted decode speed for this model on this device" — and a
consumer that reads it as "a number, or absent/unknown" (the ordinary way to
treat a nullable numeric field) needs no code change. A consumer that instead
assumed every present row carries a real number will need to add a null
check; this note is that notice.

Rows with a `null` decode rate always sort after every row with a real rate,
never mixed in above a model that actually predicts a speed. The
human-readable form prints `n/a` for these rows, never a blank or a `0.0`.

Filtering `--fits <device>` still returns these models: whether the weights
fit is meaningful on its own. Only the speed is withheld.

## Rehosts (MODEL-54)

A card whose `lineage.base_model_relation` is `repackaged` re-hosts another
catalogue card's weights unchanged (a mirror such as `NousResearch/Llama-2-7b-hf`
of `meta-llama/Llama-2-7b-hf`). `lineage.base_model` names the canonical model
id. `candidates.json` rows carry an additive `rehost_of` field: the canonical id,
or `null`.

`rank` and `fit` leave rehosts out by default, and so do the precomputed
featured rankings in `rankings.json`, so one weight set has one id. Pass
`--include-rehosts` to keep them. A rehost stays reachable by id and on its own
page, and the canonical page lists it under Lineage.

Quantised copies (`quantized`) and finetunes have different weights and fit
differently, so they stay in every pool. They are related, not hidden.

## Hosts and offload (MODEL-26 phase B)

`offline fit <device> --host <id>` evaluates the device inside a host profile
(`/api/hosts.json`, from `hosts/*.yaml`; design in `docs/host-layer.md`).

* `--host <id>`: a host profile id. An unknown id, or a snapshot with no host
  profiles (an export from before this change), exits 1.
* `--host-ram <GB>`: the RAM on this machine, before the reserve. Default: the
  profile's `system_memory.capacity_max_gb`. A fixed 8 GB OS reserve is always
  subtracted. Requires `--host`.
* `--include-offload`: append an **offload tier**, which lists models that fit
  only by spilling weights to host RAM. Requires `--host`; without it, exit 1.
  A unified host (`unified: true`, for example Apple silicon) never has an
  offload tier, because its RAM already is the accelerator's memory.

With `--host`, every fit row gains four fields:

| field | values |
| --- | --- |
| `fit_state` | `accelerator` or `offload` (`does_not_fit` rows are never emitted) |
| `offload_fraction` | `0.0` for `accelerator`; `(W + A - C_acc) / W` in (0, 1] for `offload` |
| `host_id` | the `--host` id |
| `predicted_decode_tps_basis` | `accelerator-roofline`, `offload-roofline`, or `null` when `predicted_decode_tps` is null |

Offload rows also carry `quantization`, the smallest quant that fits, which
spills the least. Their `predicted_decode_tps` is
`0.70 / ((1-f)*P/B_acc + f*P/B_host)` and is `null` for models that do not
decode tokens. Candidates in `candidates.json` gain `total_parameters` and
`active_parameters`, which the CLI needs to size those models.

**Ordering.** Accelerator rows come first, in the existing order. Offload rows
follow as a separate tier, sorted by their own predicted speed. The two tiers
are never interleaved or ranked against each other. `--limit` applies to each
tier separately. The exit code is 2 only when both tiers are empty.

**Without `--host`, the output is byte-identical** to the CLI before this
change (`tests/test_host_offload.py::test_fit_without_host_is_byte_identical`).

**Versioning-rule check.** No existing field's range widens. Every new field
and value appears only when `--host` is given, which is a new flag. `hosts.json`
and the candidate parameter counts are new, optional data. So
`schema_version` stays `"1.0"` and `build.export_schema_version` stays `"1.0"`.
`fit_state` is a new field, not a widening of `fits`. A later change that emits
a new `fit_state` value (for example `cpu_only`) does widen it and needs a major
bump under the rule above.

## A keyed origin (MODEL-71)

The published export on `https://modelspec.dev` is delayed. A snapshot of it is
older than `stale_after_days` the moment it is fetched, so a caller that needs
a current answer would see `"stale": true` on day zero and could never pass
`--require-fresh`. `snapshot fetch` can therefore present a credential to an
origin that serves the current tree to keys entitled to it.

**Nothing else changes.** Same commands, same envelope, same `schema_version`,
same exit codes on every path that already existed. The one difference a keyed
fetch makes is that `freshness.fetched_at` is now and `freshness.stale` is
false. `rank` and `fit` return exactly what they returned before — no new
field, no enrichment, no marker saying a key was used
(`tests/test_cli_keyed_origin.py::test_the_rank_and_fit_envelopes_are_unchanged`).

### Supplying the key

```bash
export MODELSPEC_API_KEY='…'        # supported
modelspec snapshot fetch --origin https://api.modelspec.dev

modelspec snapshot fetch --api-key '…'   # works, and warns
```

**Use the environment variable.** `docs/agent-commerce-assessment.md` §4 is the
reason: a credential in `argv` is visible in process listings to every user on
the machine, is written to shell history, and is captured by anything that logs
a command line — CI transcripts and agent traces included. `--api-key` exists
because some callers cannot set an environment variable, and using it prints a
warning to stderr saying so. The environment is read when `--api-key` is absent;
the flag wins when it is given, because a caller who typed a key meant that key.

The key is sent as `Authorization: Bearer <key>`, which is what
[`api-access.md`](../api-access.md) documents and, not incidentally, the one header
an HTTP client drops when a redirect crosses to another host. **A key is never
put in a URL**, never written into the cached snapshot, and never printed: it
is held in a `Credential` whose `repr` and `str` emit a 12-character `key_id`
(the SHA-256 prefix the origin logs) instead of the secret, and every message
`snapshot fetch` writes is passed through a redaction backstop on the way out.
The public decision fallback uses a separate client with no authorization
header, so the keyed origin's credential cannot reach `modelspec.dev`.
`test_the_key_appears_in_no_output_no_error_and_no_cached_file` drives every
branch of the command with a known key and searches stdout, stderr, the
origin's access log and the cached snapshot for it.

### The four failures

| What happened | Exit | On stderr |
| --- | --- | --- |
| No key presented, and the origin requires one (`401 missing_api_key`) | 5 | how to set `MODELSPEC_API_KEY`, and the origin's own message |
| The key is unknown or revoked (`401 invalid_api_key`, `403 key_revoked`) | 5 | which source supplied it, its `key_id`, and the origin's message |
| A window is spent (`429 rate_limited`) | 6 | the retry delay, and the origin's message naming the limit and its reset |
| The origin did not answer (DNS, TLS, connection, timeout) | 1 | `error: could not fetch the snapshot: could not reach <origin><route>: …` |

The unreachable case keeps exit 1 and its original sentence on purpose: that
path existed before this change and callers already branch on it. The refusals
relay the origin's own `error.message` rather than paraphrasing it, because the
service already says the useful part — where to get a key, when the window
resets. None of the four prints a traceback, and none of them replaces a
snapshot that is already cached.

### Versioning

Additive under the MODEL-59 rule, so no major bump. One new option, one new
environment variable, and two exit codes that no pre-existing call can receive
— the same reasoning as the MODEL-26 host fields, which are emitted only when
`--host` is given. No existing field's range widens, `schema_version` stays
`"1.0"`, and `build.export_schema_version` is untouched.

## The live rank API (MODEL-68)

`POST https://api.modelspec.dev/v1/rank` answers the same question this CLI
answers, from the current export rather than from a local snapshot. Its rows are
**the same rows**: the endpoint runs `pipeline/ranking.py`, vendored into the
Worker verbatim, and `tests/test_rank_worker.py` holds it to bytes identical to
`modelspec offline rank --json` for the same input against the same build.

Nothing in this document changes. The CLI keeps working with no account, no
credential and no network after the first `snapshot fetch`, which is the point of
it. The endpoint is for callers that want today's export without carrying one.

Its status codes map onto the exit codes above:

| Endpoint | CLI |
|---|---|
| `200` a ranking | `0` |
| `400` refused (bad request, unknown use case, unknown device) | `1` |
| `422` no match — carries the eliminating constraint, never a bare empty list | `2` |
| `502` the published export could not be read | — |

Full contract: [`rank-api.md`](../rank-api.md).

## The live policy-check API (MODEL-80)

`POST https://api.modelspec.dev/v1/policy-check` takes a policy document —
required licence terms, permitted origin countries, required processing regions,
a commercial-use requirement — and returns, per model **and per platform**, one
of three verdicts.

There is no CLI surface for it yet (`REV-6`), so nothing in the sections above
changes. It is documented here because its three-state answer is the same
discipline this contract already states for policy fields, and a consumer of one
should be able to find the other.

**`undetermined` is a verdict, not a missing `pass`.** In the response schema it
is structurally distinct: every check carries exactly one of `satisfied`,
`violated` or `undetermined` as a sibling key, and every row exactly one of
`passed`, `failed`, `undetermined`. A consumer written against `satisfied` finds
no `satisfied` key on an undetermined check, so the mistake surfaces in the
caller's code rather than in their deployment. `require_no_undetermined: true`
turns any undetermined row into a documented `422`.

That follows directly from [the policy-field rules above](#policy-fields-and-the-one-major-bump-they-cost-model-77):
`unspecified`, `withheld` and `unresearched` describe a file's contents, not the
world, and none of them is ever read as a permission. Nor is a value whose only
citation is `legacy-import`.

Its status codes map onto the exit codes above:

| Endpoint | CLI |
|---|---|
| `200` verdicts | `0` |
| `400` refused (malformed body, empty policy, unknown model or platform) | `1` |
| `422` the caller demanded no undetermined rows and there are some | `2` |
| `502` the published policy export could not be read | — |
| `503` entitled to the determinations, and they could not be read | — |

The endpoint is free; the determinations it reads are not, and the difference is
labelled on every response (`determinations.included`,
`undetermined_for_lack_of_entitlement`) rather than degraded silently.

Full contract: [`policy-check-api.md`](../policy-check-api.md).
