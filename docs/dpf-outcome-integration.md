# DPF: recording outcomes after a task

*MODEL-211. ADR 0004 step 1: passive outcome records from agents acting on
decisions, starting with DPF, at no added cost.*

DPF's ticket author already calls `modelspec decide` to choose a model. After
DPF runs the task, it can make one more call to say which model it used and how
the task went. The record stays on the machine that runs DPF. What a record
holds, and what it can never hold, is in
[`outcome-privacy.md`](outcome-privacy.md). The command reference is in
[`cli-contract.md`](cli-contract.md#outcome-records-model-211).

## One-time setup, by a person

A person turns recording on after reading what it records. DPF must not do this
itself, because consent has to come from the person who runs it.

```bash
modelspec outcome enable
```

On a machine with no terminal, such as a CI runner, the person who owns the
runner reads the text and runs:

```bash
modelspec outcome enable --yes
```

## The loop DPF runs

1. Decide, and keep the decision ID:

   ```bash
   modelspec decide spec.yaml --json > decision.json
   ```

   While recording is on, `decide` prints a reminder to stderr and keeps a
   small stub of the decision. stdout is unchanged.

2. Run the task with the model DPF chose. It can be the leader, another model
   in the best band, or something else.

3. Record the outcome:

   ```bash
   modelspec outcome record "$(jq -r .decision_id decision.json)" \
     --adopted anthropic/claude-fable-5/anthropic \
     --result success \
     --task-kind bug_fix \
     --latency-ms 48200 \
     --cost-usd 0.31 \
     --json
   ```

`--adopted` is `lab/model`, optionally followed by `/provider`. Use the model ID
and provider slug exactly as the decision printed them. If DPF used a model
that ModelSpec does not list, such as a private fine-tune, pass
`--adopted other`. `record` refuses a model or provider that is not in the
cached catalogue rather than store its name.

`--result` is DPF's own verdict on the task:

| DPF outcome | `--result` |
| --- | --- |
| the ticket's checks passed and the change merged | `success` |
| it merged after a person fixed part of it, or only some acceptance criteria passed | `partial` |
| it was abandoned, reverted, or failed its checks | `failure` |

`--task-kind` is optional. It takes one of the task types that
`modelspec vocab task-types` lists, such as `new_feature`, `bug_fix`,
`refactor` or `test_writing`. Do not pass the ticket title, the ticket ID or
any text from the ticket. No flag accepts them.

`--latency-ms` and `--cost-usd` are optional. Pass them only if DPF measured
them for this task. `record` rounds both to 3 significant figures.

## When DPF got the decision from the API

If DPF called `POST /v1/decide` on the Worker instead of running
`modelspec decide`, there is no local stub. Save the response body and pass it
with `--decision`, so that `record` can still tell whether DPF adopted the
leader:

```bash
curl -s https://api.modelspec.dev/v1/decide \
  -H 'content-type: application/json' -d @spec.json > decision.json
modelspec outcome record "$(jq -r .decision_id decision.json)" \
  --decision decision.json --adopted openai/gpt-5-4 --result failure
```

`record` reads six fields from the file (decision ID, spec hash, snapshot,
contract version, leader and best band) and ignores the rest of it. If the
decision ID in the file differs from the one you pass, `record` refuses.

If `record` has neither a stub nor a file, it still writes the record, with
`was_leader`, `in_best_band`, `spec_hash`, `snapshot` and `contract_version`
set to null.

## What DPF should expect back

| situation | exit | stdout with `--json` |
| --- | --- | --- |
| recorded | 0 | `{"command": "outcome record", "recorded": true, "record": {…}}` |
| recording is off | 0 | `{"command": "outcome record", "recorded": false, "reason": "disabled"}` |
| a flag failed the schema, or the model or provider is not catalogued | 1 | nothing; the error is on stderr |

When recording is off, `record` exits 0, so DPF can call it after every task
and never branch on whether the person opted in. When `record` exits 1, DPF
should log the error and carry on. A failed record must never fail the task.

## Reading it back

```bash
modelspec outcome show              # on or off, where the file is, the latest 20
modelspec outcome show --json -n 0  # counts only
modelspec outcome export > outcomes.jsonl
```

`export` prints the records as JSON Lines, and checks every line against the
schema again first. Nothing is uploaded. Sharing the file with ModelSpec is a
separate decision for the person, and there is no built path for it yet (see
[`design/outcome-upload.md`](design/outcome-upload.md)).
