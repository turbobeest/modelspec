# MODEL-435: retained source inputs unavailable

MODEL-435 is blocked. No reader fix was made. The permitted private checkout
and the restored private source artifact do not contain the source bytes
needed to reproduce the ten Haiku 5.5 mismatches. Synthetic fixtures based
only on the recorded candidate values would not establish the actual defects.

The engine, facts, source registry, verification history, contracts and Worker
exports remain unchanged. This draft PR records the investigation and an
offline audit that can be repeated when the existing snapshots are available.

- Engine base and last validated implementation SHA:
  `d9ed66aea52395b440bd72a94a109c159d4ea4c2`.
- Worktree: `/Users/terbeest/dev/worktrees/model-435`.
- Branch: `model-435-haiku-readers`.
- Private data branch: `model-430-admit-haiku-5-5`.
- Private data SHA: `c62ce1e1b85dc3468d1e80e0b638e0cc25b3064e`.
- The final documentation commit SHA is recorded in the PR body and executor
  completion line. Recover it from this checkout with `git rev-parse HEAD`.

## Input investigation

The executor brief, ticket spec, repository instructions, evidence handoff
rules, MODEL-430 evidence and research files, and REV-114 were read.
MODEL-430's final commit deliberately removed its nine HTML captures and nine
normalized text files. Its manifest and candidate results remain.

An offline hash scan found no matching bytes for the 91 historical snapshot
references in queued claims for the 27 registered `platform.claude.com` and
`privacy.claude.com` sources. The candidate manifest itself is not a retained
source. The Sonnet derived-copy registry also identifies collector-written
fact projections, which cannot establish the wording of a Haiku source.

The private repository README says raw source copies are Actions artifacts.
The existing `rendered-reread-copies` artifact from run `39213106225` was
restored under the authorized scratch directory. Its 12 bodies did not supply
any of the missing candidate sources. No publisher page was fetched.

The default source cache is outside the ticket's named paths. It was not
searched. The executor brief requires: "Stay inside the paths the spec names.
If you need a file outside them, stop and report it."

To resume, supply an authorized location or an identified existing private
artifact containing the older snapshots, with their source URL mappings.
Do not fetch replacement pages or restore the deliberately removed MODEL-430
captures as a workaround.

## Ten cases

These classifications distinguish observations in the historical report from
causes that cannot be determined without the retained source. No row below
claims that a newly implemented parser fixed the historical mismatch.

| Facet | Historical observation | Classification and unresolved check |
| --- | --- | --- |
| `model.input_modalities` | No value read | Possible format or region defect. The operative model row and complete modality set have not been observed. |
| `model.output_modalities` | No value read | Possible format or region defect. Extra modalities and sibling rows must remain distinguishable. |
| `model.release_date` | No value read | Possible date format, label or region defect. A model release date must be distinguished from a page update date. |
| `feature.structured_output` | No value read; manifest says the captured page did not contain the Haiku name | Binding remains unproved. A generic feature page alone does not establish this model's support. |
| `feature.streaming` | No matching model; manifest says the captured page did not contain the Haiku name | Missing model binding. Keep refused until the source establishes coverage. |
| `offering.data.retention` | No value read | Possible prose or scope defect. The default API period must be distinguished from product and mode exceptions. |
| `offering.data.trains_on_customer_data` | No value read | Possible phrase or scope defect. The relevant API data, default policy and opt-in conditions must be identified. |
| `offering.data.zero_retention` | A `requires_contract` candidate failed | The claim representation drops fact state. A null reading cannot by itself prove a contractual requirement. Source scope remains unobserved. |
| `offering.attestation.soc2` | No value read | Possible phrase or typography defect. Report type, negation and service scope remain unobserved. |
| `offering.attestation.baa` | No value read | Possible phrase or scope defect. A mention is insufficient to establish availability for this offering. |

The historical verifier method identifies the first mismatch, not necessarily
the cause. `verify()` continues through readers and accepts any matching
reading. A future scoped reader must prevent a rejected or ambiguous
statement from succeeding through a later generic reader.

## Data-state comparison

The audit includes every authored Anthropic model fact, every offering fact
whose provider or model is Anthropic, and Anthropic subscription facts.
It reads existing copies in place and never appends verification records.
Detailed results stay in private scratch files; only aggregate results are
published here.

The inventory contains 430 facts: 147 model facts, 221 offering facts and
62 subscription facts. It has 809 source citation instances. Only 35 of those
citation instances have available bytes in the checked locations.

The baseline replay produced 35 verified outcomes, 342 unreachable outcomes
and 53 unknown facts that are not claims. All 25 MODEL-430 candidates lack an
available older copy of the same source URL, including all ten mismatches.
The 35 verified facts are prices for seven Google Vertex offerings of
Anthropic models. They do not exercise the first-party Anthropic readers.

Inherited and computed snapshot facts are outside this authored-fact replay.
The complete private checkout remains unchanged, including their inputs.
No snapshot export was rebuilt.

The before-and-after comparison is recorded in
[the audit summary](MODEL-435/audit-summary.json). Zero fact values, states,
sources or stored outcomes changed. No fact became verified. Identical
unreachable outcomes are not a successful reader regression check.

## Validation and commands

The exact audit commands and their output are recorded in
[commands.md](MODEL-435/commands.md). The helper is
[audit.py](MODEL-435/audit.py). It uses the existing verifier and explicitly
supplied private locations; it does not read the default source cache.

The source-readiness gate is red because the required snapshots are missing.
That is an input failure, not a parser regression test. There is no green
reader-fix result and no synthetic test asserted to reproduce unseen page
structure. No existing test was changed or weakened.

The focused baseline suites ran serially:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python \
  -m pytest -q -p no:cacheprovider \
  tests/test_decision_verify.py tests/test_model_396_readers.py
```

Result: **428 passed in 3.01s**, exit 0. The direct process exit code was
checked. Python was 3.14.4, pytest 9.1.1 and Git 2.50.1.

## Limits and cleanup

This run did not observe the retained source wording for the ten mismatches,
a successful candidate replay, a parser defect turning green, or a complete
Anthropic source replay. It did not admit Haiku, change the data pin, run the
local full suite, spend vendor API credits, run Firecrawl, contact a publisher,
modify Linear or deploy anything.

No Worker-exported code or data changed, so the conditional Worker memory
probe and public re-vendor were not applicable. CI and independent review
were not observed during execution.

Private source bytes and detailed audit results are excluded from this PR.
The private clone and restored artifact are deleted before executor completion.
No task process is left running.
