# Two-key verification

`decision/verify.py` (MODEL-140; design §5, "Two keys"). The agent that
collects a value never verifies it.

## Flow

1. A collector files a **claim** with `Queue.file`: the target (`fact` or
   `evidence` ID), the subject and the names it is published under, the value,
   unit and conditions (effort, harness, date), the source snapshots it read
   and who collected it (agent, model family, method).
2. Source change detection (`decision/sources.py`) re-queues the claims citing a
   changed region with `Queue.requeue(report)`. The re-check pins each source
   to its new retained copy. `RecheckReport.requeue` refs are `fact:<id>` or
   `evidence:<id>`.
3. `modelspec verify [--changed-only] [--llm-reader claude|mistral]` (or `verify.run`) re-reads each pending
   claim from the cited regions of its retained copies. It appends one
   `Verification` per value to `verification/log.jsonl` and prints a summary.
   `--changed-only` skips new values and runs only the re-queued ones.

## Extractors

The verifier re-extracts the value. It never reads the collector's value
first. Deterministic extractors always run first:

- `TableExtractor`: tables as `decision.normalise` renders them. It needs a
  model column. The value column is the one whose header is the claim's label,
  or else the only score-like column. A unit in the header, such as
  `Score (%)`, applies to the column.
- `KeyValueExtractor`: `Key: value` lists. The region must name the subject
  under a `Model` or `Name` key.
- `LLMExtractor`: prose. It calls an injected `complete(prompt)` function,
  and its actor records the model: `llm-extract:<model>`. The CLI's
  `--llm-reader claude` option calls the authenticated Claude CLI with Sonnet 5
  at low effort. Its verification actor is `claude-cli`, model family
  `anthropic`. `--llm-reader mistral` calls Mistral Large
  (`mistral-large:123b-instruct-2411-q4_K_M`) on the local ollama host
  (`http://100.127.37.30:11434/api/chat`, or `MODELSPEC_OLLAMA_URL`) at
  temperature 0 in JSON mode. Its actor is `ollama`, model family `mistral`: the
  reader for values a Claude collector filed. Both readers get the same prompt.
  It asks for the value, unit, conditions and a source sentence. The verifier
  checks that sentence against the retained cited region. A region can state
  a condition once for a whole table, in a heading ("Comparison with frontier
  models (Max reasoning effort)") or a caption ("all Claude Opus 5.5 results
  use ... max effort"). The prompt asks the reader to give each value the
  conditions the region states for it, and to quote the heading or caption
  sentence as `condition_sentence` (MODEL-233). Which values a caption covers
  ("unless otherwise noted", one model's results only) is the reader's
  reading, and the collector's is the other key. The code refuses the plain
  inventions: a reported effort counts only when the row gives it (the model
  cell's qualifier, a cell that is the level, or an effort phrase), when the
  region's first line names it as an effort and is neither a table row nor
  about another model in the reply, or when a verbatim condition sentence
  names it as an effort and names the row's model, or names the benchmark and
  no other model. So the Opus caption lends max to Claude Opus 5.5 and not to
  Claude Opus 5 or GPT-6 Astra, "default sampling" is no effort, and a
  negated phrase names no level. Otherwise the reply is unparseable and the
  region is not evidence. Not refused: a model the reader leaves out of its
  reply, a cell equal to a level in a column that is not an effort column, and
  a sentence stitched from fragments of the region. Ollama's JSON mode returns one object, not an array, so a system
  turn asks Mistral to wrap the array as `{"values": [...]}`. Without it, Mistral reports only the first
  value in a region.

Reader replies are cached outside the repository under
`~/.cache/modelspec/llm-reader` by the prompt's hash, source-copy hash, cited
region, facet and the subject's published names. A changed prompt asks again.
The licence reader's key also hashes the reading rule, the facet definition
and the allowed values that were filled into the prompt, so a change to any
of those asks the reader again.
The names are in the key because the prompt carries
them: a reader answers mostly for the named subject, so a reply cached for one
plan or model must not answer for a sibling on the same page (MODEL-201).
Mistral's replies are also keyed by its model and request shape, so neither
reader answers for the other. Set `MODELSPEC_LLM_CACHE` to use another
directory. A run stops before its 401st uncached call. Deterministic
extractors still run first. On a `licence.*` claim, `CanonicalLicenceExtractor`
reads a `licence_text` region when the retained text is the canonical MIT
licence or the Apache License 2.0 terms. `LicenceExtractor` reads every other
permitted region, and it is not asked about a text the canonical extractor
accepts. A `model.weights_openness` or `origin.*` claim on a
`licence_text` source still uses the other deterministic extractors.

A `licence.*` claim is read by `LicenceExtractor`
(`licence-extract:<model>`) from a source kind in that facet's
`permitted_source_kinds`, using the same completion function, cache and
call budget as the prose reader. `licence.user_cap` permits only
`licence_text`. The prompt gives the facet's definition, the
reading rule for that facet, and its allowed values, including `unbounded`
for `licence.user_cap`, and asks for the value plus one or more verbatim
clauses. It does not show the collector's value. The reading rule says when
the value is `not_disclosed`. A missing or non-verbatim clause is unparseable,
so the region is not evidence. Any other cited region is a binding page. It
is not a reading, for a known value or an absence. A licence does not name
the model. The binding page names the subject by its display name or its
repository id, as a whole name. `-`, `_`, `.` and spaces separate segments
of that name. A prefix of a longer hyphen-joined name does not count:
Querit is not Querit-4B, and Querit-4B is not Querit-4B-Pro. A family name
does not count. The page names this licence by the first rule that holds.
`license:` and `license_link:` are read from YAML front matter when the page
has it. A `license_link` is exclusive. When the front matter has one, only a
source that matches it binds. A relative link resolves against the README's
repository. On huggingface.co, `raw`, `resolve` and `blob` name the same
file. With no `license_link`, the page names the licence when it contains
the licence URL, or when `license:` is an SPDX id for a shared text:
`apache-2.0` for the apache.org LICENSE-2.0 text, `mit` for
opensource.org/license/mit. A root file in the page's own repository also
binds when its name starts with `LICENSE`, `LICENCE` or `COPYING`, in any
case. `license: other`, and an id that is not in that SPDX table, binds that
file by location. `license: mit` or `license: apache-2.0` binds it only when
the retained text is that licence. MIT text contains "Permission is hereby
granted, free of charge". Apache-2.0 text contains "Apache License" and
"Version 2.0". `README.md`, `config.json` and a file in a subdirectory do
not bind by location. `license: other` does not bind a shared text. A file
in a different repository binds only by `license_link` or by its URL. A
licence cited alone does not verify.

### Canonical MIT and Apache texts

`CanonicalLicenceExtractor` (`canonical-licence@1`) is a deterministic
extractor, so it is an independent second key. `modelspec verify` runs it
with no `--llm-reader`. It accepts a `licence.*` claim whose cited region
is `licence_text` when the retained text is the canonical MIT licence or
the Apache License 2.0 terms. The licence reader is not asked about a text
this extractor accepts. Any other text falls through to that reader.

Recognition is a signature plus an exact residual list. MIT text contains
"Permission is hereby granted, free of charge" and the warranty sentence
`THE SOFTWARE IS PROVIDED "AS IS"`. Curly quotes and the `*AS IS*` spelling
used in some repository files are the same sentence. Apache text contains
"Apache License", "Version 2.0, January 2004", and the section 2 copyright
grant, the sentence that grants a copyright license to prepare Derivative
Works. The text has to contain that licence's canonical body. The text before
and after the body, once whitespace is collapsed and stripped, has to be one
of the pairs in `CANONICAL_LICENCE_RESIDUALS`. Those pairs are the residuals
of the retained copies reviewed for this extractor. For Apache-2.0 the how-to
appendix and the boilerplate notice are removed first, and the copyright line
that was between them is the `after` value, matched exactly. A longer addition
is not this licence. A text that contains "separate agreement", "monthly
active users", "not intended for use", "prohibited use", or "acceptable use"
is not this licence. A new canonical file with a different copyright line is
not read by this extractor until that residual is reviewed and added in code.
That fallback to the licence reader is deliberate. A modified MIT text, an
MIT text with an added agreement, and an MIT text that embeds Gemma terms
are left for the licence reader.

Each facet is mapped to a value with a clause quoted from the text. The
table's rule key is that facet's key in `LICENCE_READING_RULES`.
`LICENCE_CONDITION_RULE` applies. Keeping a copyright, licence, NOTICE or
change notice is not attribution and not a condition. For both licences,
`licence.commercial_use` is `permitted` ("sell copies of the Software" for
MIT, and section 3 "make, have made, use, offer to sell, sell" for
Apache-2.0). `licence.user_cap` is `unbounded`. `licence.output_training` is
`not_disclosed`. `licence.fine_tuning` is `permitted` ("modify ... the
Software" for MIT, and section 2 "prepare Derivative Works" for Apache-2.0).
Jamie decided that reading on 2026-10-09. This extractor applies it.

A reading still has to pass `licence_is_bound`. A canonical text with no
binding page does not verify. A licence bound to the claim's `base_model`
also binds the fine-tune when that licence says derivatives must be
distributed under its terms or remain subject to them. The binding page's
own YAML front matter `base_model` entry, a string or a list of repository
ids, has to list the claimed base. The comparison is the full repository id,
case-insensitive. A prose mention of the base does not count, and neither
does an unfenced `base_model:` line. The returned rule is `base-model`. MIT
and Apache-2.0 do not say that, so they do not bind by this path.

The derivative-terms check is one sentence. Its subject is the derivatives,
and it says they are or remain subject to, or must or shall be distributed
under, these or this terms, licence, or agreement. `not`, `no`, and `need
not` reject the sentence. A definition of "Model Derivatives", and a later
grant preamble ("Subject to the terms and conditions of this License,
Licensor grants ..."), do not match. The retained Gemma terms match because
they say Model Derivatives are subject to the use restrictions and the next
sentence gives recipients a copy of this Agreement. A Llama-style sentence
that only says to provide a copy of this Agreement, and an OpenRAIL sentence
that only carries use restrictions onto derivatives, are not matched yet.
They stay unbound.

### Licence reading rules

`LICENCE_READING_RULES` in `decision/licence_rules.py` is one rule per
`licence.*` facet. Each sentence is derived from that facet's registry
definition. Jamie decided these readings on 2026-10-09. The licence prompt
is `LICENCE_CONDITION_RULE` plus the rule for the claim's facet. The reader
only sees the licence text, so the prompt does not include base-model
inheritance and does not name a model or a licence. Inheritance is applied
when the licence is bound. The collector `scripts/model_345_collect.py`
records the facet id as the rule key on every value, and files the card's
`base_model` on the claim.

On every `licence.*` facet, keeping a copyright, licence, NOTICE or change
notice is not attribution and not a condition. A condition is a display or
naming duty, a separate agreement or licence, a security or other review, a
user, revenue or other threshold, a territorial or field-of-use restriction,
or an incorporated acceptable-use or prohibited-use policy.

- `licence.commercial_use`. `permitted` when commercial use is granted with
  no condition. `permitted_with_conditions` when it is granted subject to a
  condition. The registry definition says that value covers any condition,
  for example a display or naming duty, a user cap or a field-of-use limit.
  Attribution means a display or naming duty. Keeping a copyright, licence
  or NOTICE notice, as MIT and Apache-2.0 require, is not a condition.
  `prohibited` when commercial use is forbidden. `not_disclosed` only when
  the text does not address commercial use or selling at all. MIT and
  Apache-2.0 are `permitted`.
- `licence.user_cap`. A number only when the licence requires a separate
  agreement or licence once a monthly-active-user threshold is exceeded. A
  threshold that only triggers a display, naming or attribution duty is not
  a cap, and neither is a revenue threshold. With no such threshold the
  value is `unbounded`, as the registry definition says. The value is never
  `not_disclosed` when the cited region is the licence text.
- `licence.fine_tuning`. An express grant to modify the model, the Software
  or the Work, or to create derivative works of it, covers fine-tuning.
  `permitted_with_conditions` when using or distributing the result is
  subject to a condition. `permitted` when only notice retention applies.
  `prohibited` when modification is forbidden. MIT and Apache-2.0 are
  `permitted`.
- `licence.output_training`. About using the model's outputs to train or
  improve another model. A grant to fine-tune or modify this model says
  nothing about it. `restricted` or `prohibited` only where the text
  expressly addresses using the model's outputs, or synthetic data or
  distillation from those outputs, to train or improve another model, and
  limits or forbids that use. A generic modification or derivative-works
  clause that never mentions outputs is not that. A licence that defines a
  model trained on its outputs, on synthetic data from them, or by
  distillation from them as a derivative subject to its restrictions is
  `restricted`. `permitted` only when the text expressly allows it.
  `restricted` when the text expressly allows or forbids it only for some
  purposes or models, for example not for a competing model, or makes a
  model trained on outputs a derivative subject to the licence's
  restrictions. `prohibited` when the text expressly forbids it for every
  purpose. `not_disclosed` when the text is silent. The Gemma Terms are that
  case: they define Model Derivatives to include a model trained on
  synthetic data Outputs of Gemma, or by distillation, and they subject
  those models to the Terms' restrictions. MIT, Apache-2.0, and a custom
  licence that only grants modification are `not_disclosed`. Those names
  stay in this document. They are not in the reader prompt.

A fine-tune inherits its base model's licence terms where the base licence
requires it. The card field is `base_model`. Inheritance applies when the
base licence says derivatives must be distributed under its terms or remain
subject to them, and the binding page declares that base in its YAML front
matter. tencent/kalm-embedding-gemma3-12b-2511 has `base_model`
google/gemma-3-12b-pt, and its LICENSE.txt embeds the Gemma terms. The
binding follows that card field only when the page declares it. A licence
bound to the base binds the fine-tune when the text requires derivative
terms. It does not bind an unrelated model, a page that only mentions the
base in prose, or a card that sets no `base_model`.

An absence (a null value, `not_disclosed`) verifies only from a source kind
in the facet's `permitted_source_kinds`. A `licence.*` absence needs that
kind on the source. A README with no kind, or a kind outside the list, is a
mismatch on `source_kind` only when the claim cites no region of a permitted
kind. When the claim also cites a permitted kind, that README is a binding
page and gives no outcome. If every permitted region has no extractor, or
every one raises an extractor error, the claim is skipped: nothing is logged
and it stays queued. Other facets still verify an absence from a source
whose kind is unknown. A known kind outside the facet's list is a mismatch
for every facet.

The first extractor that accepts a region and is independent of the collector
reads it. Two keys means another model family (MODEL-140, enforced by
MODEL-159). A deterministic extractor is always independent. An LLM reader is
independent only when its model family differs from the collector's. So a
Claude-collected value is never sent to the Claude reader. A claim that no
independent extractor can read is `skipped`: nothing is logged, and the claim
stays queued.

The log already holds records from before the family rule, so the rule applies
when records are counted, not when they are parsed. `VerificationLog.latest`
and the snapshot builder skip a same-family `verified` as if it were never
logged. `VerificationLog.requarantined()` lists the values that such a record
vouches for and that no counting record admits.
`scripts/model_159_requeue_dependent.py` prints those values and requeues
them for `--changed-only --llm-reader mistral`.

## Checks

- **Identity.** The row must name the subject, after the name is normalised
  (case and punctuation). An effort qualifier in the model cell, such as
  `(max effort)` or `[high]`, is a condition. Any other qualifier, such as
  `(thinking)`, is a different identity. When the claimed value belongs to
  another row, the diff names that sibling.
- **Value and unit.** Both values are converted to the base unit of their
  dimension (`UNITS`: percent/fraction, tokens/K/M, USD per 1M/1K tokens, and
  so on). Tolerance (`TOLERANCE_RULE`): `|a − b| ≤ 0.5 × max(ulp_a, ulp_b)`.
  Here `ulp` is one unit in the last written decimal place, so a value rounded
  to the other value's precision agrees. When the values disagree and the units
  differ, the diff is `unit`. When the units match, the diff is `value`. A
  source that states no unit does not confirm one.
- **Evidence metadata.** When evidence carries `interval`, `n`, or
  `quality_flags`, the claim value is the canonical composite of `score`,
  `interval`, `n`, and sorted `quality_flags`, and the verification target hash
  covers that entire object. The verifier re-reads every cited region. It
  confirms the score, both interval bounds, and `n` against the model's row,
  and combines quality flags found on the model or benchmark across those
  regions. A missing or different member is a mismatch. Evidence without this
  metadata keeps the scalar score claim.
- **Conditions.** Effort and harness must match. If the source states a
  condition that the claim omits, that is a mismatch: a max-effort score filed
  with no effort is not a default score. A date is checked when the claim
  carries one.

## Outcomes and quarantine

- `verified`
- `mismatch`: `diff` is a JSON list of `{field, expected, found}`. The target
  is listed by `Queue.recrawl_requests()` until it is filed again.
- `unreachable`: the retained copy, the source registration or the cited
  region is missing. The target is also listed for re-crawl.

`is_quarantined(target)` is true unless the target's latest logged outcome is
`verified`. A value that has never been verified is quarantined.
`quarantined_values(targets=None)` lists the quarantined targets in the log,
or among `targets` when that list is given.

## Weekly price and plan re-read

`scripts/price_reread.py`, run by `.github/workflows/price-reread.yml` on
Tuesdays (MODEL-217). It takes every `offering.price.*` and
`offering.subscription.*` fact whose current value was last verified by a
deterministic reader, fetches each cited page once more over plain HTTP, pins
the fact's filed claim to the new copy and verifies it again. Each fact ends as:

- `unchanged`: the recorded value still verifies. The verification is logged
  with the run's date, so the value's age restarts; the offering file is not
  touched. A week with no change opens a log-only pull request on
  `data/weekly-price-reconfirm`. The workflow first proves that only
  `verification/log.jsonl` changed, and only by appends, and then the PR may
  auto-merge. This adds about 160 KB of log a week.
- `changed`: it does not, and exactly one new value for the same subject
  verifies. The job writes that value and the new copy ref into the offering
  file (nothing else in the file changes), files a claim from
  `modelspec-price-reread` and logs the verification. It opens a pull request on
  `data/weekly-price-reread`, with the old and new values and a diff of the cited
  regions' text. `automerge.yml` skips that branch: a person reviews every price
  change.
- `needs_review`, `unreadable`, `unreachable`: the value no longer verifies and
  there is no single replacement; or the page fetched and the readers cannot read
  it; or it did not fetch. These are alerts. The job writes nothing for them,
  opens or updates one issue ("Price and plan re-read needs a person") and fails
  the run. A page is fetched a second time before its facts alert, since some
  servers now and then answer a plain fetch with a script shell or a 403.
- `not_reread`: the page needs a rendered fetch, or an LLM reader verified the
  value, or the value is still quarantined. A deterministic failure would say
  nothing about the page, so these are counted in the report and never alert.

Both keys on a new value are code in this repository: the readers that found it
and the verifier that confirmed it. The pull request's reviewer is the check that
the readers still read the page as intended.

The retained copies live in the `price-reread-copies` artifact between runs;
only the report's text diff needs them. On 2026-09-29 a run fetched 33 pages
(16 MB), and 14 more need a rendered fetch. It took about a minute on one Linux
runner, with no model and no paid scraper.

## Fixture

`tests/fixtures/verification/` seeds these errors: a score copied from a
sibling, a wrong unit (in both directions), a max-effort value filed as default
or with no effort, a stale date, a value absent from the source, a missing copy
and a missing region. Its `reader_claims` are read only by an LLM reader,
replayed from `captioned-results.reader.yaml`: a caption states max effort for
a whole table and names one high-effort exception. A value filed as default,
with no effort, or at max for the exception must end as a mismatch. `tests/test_decision_verify.py` requires every seeded
error to end as a mismatch or quarantined, and every correct value to end as
verified.
