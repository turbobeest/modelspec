# Outcome records: what stays on your machine

*MODEL-211. ADR 0004 step 1, under the REV-9 privacy rules.*

`modelspec outcome` keeps a local log of whether you adopted a decision and
whether the task succeeded. This note says exactly what that log holds, where it
lives and what leaves your machine. The short answer to the last question is
**nothing**.

## It is off until you turn it on

No command records anything until a person runs:

```bash
modelspec outcome enable
```

`enable` prints the full list of recorded fields and asks for a yes. Without a
terminal it refuses unless you pass `--yes`, and it still prints the text first.
The consent is stored as `{"consent_version": 1}`. If a later CLI changes what
is recorded, it bumps that version, and recording stays off until you run
`enable` again and read the new text.

While recording is off, `modelspec outcome record` does nothing. It reads no
cache, validates nothing, writes no file and exits 0 with `not recorded`.

Turning it off is one command:

```bash
modelspec outcome disable            # stop recording; delete the decision stubs
modelspec outcome disable --delete   # also delete every record
```

## What is on disk

Everything lives under `~/.modelspec/`, or under `$MODELSPEC_HOME` if you set
it. The CLI creates a missing directory with mode `0700`, and it leaves an
existing directory's mode alone, because `MODELSPEC_HOME` may point at a
directory the CLI does not own. Every file is written with mode `0600`, and an
existing looser file is tightened. A write never follows a symlink at a file's
path or at the stubs directory. `export --out` also writes its file with mode
`0600`.

| file | when it exists | what it holds |
| --- | --- | --- |
| `outcomes-consent.json` | while recording is on | `{"consent_version": 1}` |
| `outcomes.jsonl` | after the first `record` | one outcome record per line |
| `decision-stubs/dec_….json` | while recording is on, after a `decide` | up to 500 decision stubs |

**An outcome record** holds these fields and nothing else. The schema is
`OutcomeRecord` in `cli/modelspec/outcome.py`. It refuses any field it does not
name, and it does not coerce types:

| field | what it is | what it can hold |
| --- | --- | --- |
| `record_version` | the record format | `1` |
| `decision_id` | the decision you acted on | `dec_` and 24 lowercase hex |
| `spec_hash` | the hash of the decision's spec, not the spec | `sha256:` and 64 hex, or null |
| `snapshot` | the snapshot the decision used | `snap_` and 16 lowercase hex, or null |
| `contract_version` | the decision contract version | `major.minor`, or null |
| `adopted_model` | the model you used | a catalogued `lab/model`, or `other` |
| `adopted_offering` | the provider you used it through | a catalogued provider slug, or null |
| `was_leader` | whether that model led the decision | true, false, or null |
| `in_best_band` | whether it was in the best band | true, false, or null |
| `result` | how the task went | `success`, `partial`, `failure` |
| `task_kind` | the kind of task, optional | one of the 12 fixed task types, or null |
| `latency_ms` | wall time, optional | a whole number from 0 to 86,400,000, rounded to 3 significant figures, or null |
| `cost_usd` | cost, optional | a finite number from 0 to 10,000, rounded to 3 significant figures, or null |
| `recorded_at` | when | UTC, to the minute |
| `cli_version` | this CLI's release | the public release number, never a `+local` segment, or null |

A null in `spec_hash`, `snapshot`, `contract_version`, `was_leader` or
`in_best_band` means the CLI could not find the decision: no stub and no
`--decision` file. It does not guess.

**A decision stub** holds the decision ID, spec hash, snapshot, contract
version, the leader's model ID and the best band's model IDs. `decide` writes
one only while recording is on, so that `record` can work out `was_leader` and
`in_best_band`. `decide` keeps at most 500 stubs and deletes the oldest ones
first. `disable` deletes all of them. The decision ID must equal
`dec_` + the first 24 hex of SHA-256 over the spec hash and snapshot, exactly
as the engine computes it. A stub whose ID does not match is refused.

## What is never recorded

The rule from REV-9: record only what answers "was this recommendation adopted,
and did the task succeed?". Specifically:

- **No prompt or task text.** No field accepts free text. The decision ID,
  spec hash and snapshot are fixed-length hex. `result` and `task_kind` are
  closed lists. The model and provider must be in the catalogue (next point).
  Latency and cost are rounded, so their digits cannot carry text either.
- **No API key values, and not whether you have keys.** No field can hold a
  key. `record` reads no environment variable except `MODELSPEC_HOME` and
  `MODELSPEC_CACHE`, which say where its own files are.
- **No customer, user, machine or repository identifiers.** A model or provider
  must be in the cached ModelSpec catalogue. Otherwise `record` refuses it and
  tells you to pass `--adopted other`, which records the word `other` and never
  the name. This matters because a private fine-tune's name can identify a
  customer. The catalogue is the vocabulary that `snapshot fetch` cached.
  Nothing else can vouch for a model: not a decision stub, and not a
  `--decision` file. `decide --snapshot-file` accepts a private snapshot, and
  a stub made from one could list any name. `cli_version` drops any `+local`
  segment, which can carry a hostname or a git hash.
- **Not the spec.** Only its hash is recorded, and that is the same hash
  `decide` already prints. The hash is unsalted, so someone who can guess
  your whole spec can confirm the guess by hashing it. A spec can name the
  providers and plans you hold. Anyone who holds the same spec and snapshot
  gets the same decision ID. That does not matter while the log stays on your
  machine. The upload design has to deal with it (see below).
- **Not the rest of a decision.** `--decision FILE` reads the six stub fields
  from the file and ignores everything else in it.

If the schema refuses an input, the error names the field and the rule it
broke. It never repeats the value you passed, because that value might be
exactly the text this schema exists to keep out. (Click's own parse error for a
non-number in `--latency-ms` or `--cost-usd` does repeat it, before the schema
sees anything.)

`show` and `export` check every line against the schema again before they print
it. A line that someone edited by hand to add a field is skipped and counted.
It is never passed through.

If a later CLI bumps the consent version, recording stops. The records and
stubs you already have stay on disk. `disable` deletes the stubs, and
`disable --delete` deletes the records too. `disable` deletes only regular files
named like a stub (`dec_<24 hex>.json`). If the stubs directory is a symlink, it
deletes nothing there.

## What leaves your machine

Nothing. No `outcome` command opens a network connection, and `decide` sends
nothing either. Upload to ModelSpec is a separate path with its own consent. It
is designed in [`design/outcome-upload.md`](design/outcome-upload.md) and it is
not built.

The published privacy statement ([`legal/privacy.md`](legal/privacy.md), "Not
yet live") says the **service** does not record outcomes, and that the
statement will be updated before that ships. That is still true: this log is
written by the CLI on your machine, and ModelSpec never receives it. Building
upload requires Jamie's approval and that update to the statement first.
