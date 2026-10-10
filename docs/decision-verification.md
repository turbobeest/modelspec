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

- `HFConfigExtractor`, `hf-config@1`: retained Hugging Face configs, including
  nested `text_config` and the public API's `config` field. It reads
  `model.architecture`, `model.experts_total`, and `model.experts_per_token`.
- `ModelCardParamsExtractor`, `model-card-params@1`: explicit active-parameter
  or effective-parameter statements and labelled model-card table cells.
  A parameter-count field's `4.92B-A0.43B` notation supplies the active count
  only when its total agrees with the retained API census. Model-name suffixes
  such as `A4B` never supply a count.
- `HFParametersExtractor`, `hf-safetensors@1`: the API's safetensors census.
  It sums per-dtype counts when present because some sharded repositories
  report an index-entry count in `safetensors.total`.
- `DenseActiveEqualsTotalExtractor`, `dense-active-equals-total@1`: a dense
  config plus a retained API census from the same repository. It recomputes
  active parameters as total parameters. Both copies must be cited.

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
case-insensitive. Fenced YAML counts. So do the leading `key: value` lines
of a normalised page, whose fences the text normaliser has already dropped,
including a list written as `base_model:` and then `- id`. A heading, a
blank line, or any other line ends that block. A prose mention of the base
does not count. The returned rule is `base-model`. MIT
and Apache-2.0 do not say that, so they do not bind by this path.

The derivative-terms check is one sentence. Its subject is the derivatives,
and it says they are or remain subject to, or must or shall be distributed
under, these or this terms, licence, or agreement. `derivatives` opens the
sentence or follows whitespace. `Non-derivatives` does not count. `not`,
`no`, `none`, and `need not` anywhere in the match reject the sentence. A
definition of "Model Derivatives", and a later
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
`offering.subscription.*` fact whose current value was verified, fetches each
cited page once more over plain HTTP or an opted-in local browser, pins
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
- `not_reread`: a rendered fetch was not enabled, the value is still quarantined,
  or the deterministic readers cannot read an LLM-verified value. The readers
  reconfirm an LLM-verified value only when they confirm the same value. A
  different numeric value goes to `needs_review`, never `changed`. Facts that
  are overdue also alert when they cannot be re-read.

`--rendered` fetches HTML with local Chromium. `--render-to <directory>` captures
eligible rendered pages without verifying or writing facts. `--rendered-from
<directory>` validates and replays that artifact without a browser. Source
preparations are code in `decision.sources.RENDERED_PREPARATIONS`, keyed by source
ID. They add no registry field or locator kind. The AWS Bedrock preparation opens
the Anthropic tab, scrolls the global pricing component into view and waits for
its header and numeric price cells within one timeout budget. A preparation
failure retains the HTML and records the error in the artifact's existing
`error` field. Both direct and replay runs report it as `unreadable`, including
for LLM-verified values.

CSS cited-region locators support tags, IDs, classes, existence and equality
attributes, prefix `^=`, substring `*=` and suffix `$=` attributes, and descendant
or child `>` combinators. Quoted values preserve spaces and `>` characters.
Escapes, other attribute operators, selector lists and pseudo-classes are
rejected at registration.

Both keys on a new value are code in this repository: the readers that found it
and the verifier that confirmed it. The pull request's reviewer is the check that
the readers still read the page as intended.

The retained copies live in the `price-reread-copies` artifact between runs;
only the report's text diff needs them. On 2026-09-29 a run fetched 33 pages
(16 MB), and 14 more need a rendered fetch. It took about a minute on one Linux
runner, with no model and no paid scraper.

## HF architecture collection

`scripts/model_348_architecture.py --root <modelspec-data> [--dry-run]
[--report PATH]` collects hardware facts for the open-weights premier lineup.
It resolves the repository from the card's HF fields or its existing
total-parameter API citation. Conflicting repositories remain unresolved.
The source registry admits commit URLs, so config and README URLs use the
API's 40-character commit SHA. When no SHA is available they use `main`.
The API itself retains its existing URL and source ID.

The architecture rules inspect every config level, including the top level,
`text_config`, other nested objects and lists. They run in this order:

1. Any routed-expert count greater than one means `MoE`. Recognised count
   keys are `n_routed_experts`, `num_local_experts`, `num_experts`, and
   `moe_num_experts`. This includes DBRX's nested `ffn_config`.
2. Populated expert or MoE settings block a dense classification. Null
   placeholders do not. Recognised counts of 0, false or 1 do not establish
   MoE or block dense on their own. An explicit false `enable_moe_block`,
   `enable_moe`, `use_moe`, or `moe_enabled` flag permits dense when all other
   expert settings are null or absent. A populated setting conflicts with
   that disable flag and blocks dense; an enabled flag with null counts also
   blocks dense. Rule 1 still takes priority for a routed count above one.
   Unfamiliar populated expert keys block dense even with a value of 0 or 1.
3. A recurrent or SSM config with no attention heads or attention layer types
   means `SSM`, regardless of its `model_type`. This includes `falcon_mamba`.
   Mamba's `num_heads` counts SSM heads and does not establish attention. Configs with recurrent and attention
   layers mean `hybrid-SSM-transformer` only with positive attention evidence.
   A hybrid marker alone without recurrent or attention evidence gives no reading.
   Other explicit `ssm`, `hybrid`,
   or recurrent settings and `linear_attention` / `linear-attention` layer
   types also prevent dense classification. Nemotron-H's
   `hybrid_override_pattern` and Falcon-H1's `mamba_d_ssm` cannot be dense.
4. Without those settings, `*ForMaskedLM` or a listed BERT-family
   `model_type` on the text backbone means `encoder-only`. A nested vision
   encoder cannot give that classification to a decoder. A decoder needs a positive attention
   head count and a `model_type` in this allowlist to mean `dense-transformer`:
   `llama`, `mistral`, `qwen2`, `qwen3`, `gemma`, `gemma2`, `gemma3`,
   `gemma3_text`, `gemma4`, `gemma4_text`, `phi`, `phi3`, `phi4`, `gpt2`,
   `gpt_neox`, `gptj`, `opt`, `bloom`, `falcon`, `mpt`, `olmo`, `olmo2`,
   `stablelm`, and `starcoder2`. For multimodal configs, the decoder type and
   heads come from `text_config`; exclusion rules still inspect every level.
   An embedding task does not change the backbone classification.
5. Otherwise there is no architecture reading.

`model.experts_total` counts routed experts per layer, excluding shared
experts such as `n_shared_experts`. `model.experts_per_token` reads
`num_experts_per_tok`, `num_experts_per_token`, `moe_topk`, `moe_top_k`, `top_k_experts`, or
`router_top_k` in a
config classified as MoE. Zero entries describe layers without routed
experts and do not change a uniform positive count. Conflicting or varying
positive counts give no single count. Both facets use the `experts` unit, `better: neither`, and
capability risk. They are best effort facts, never ranking signals.

The active facet counts parameters used to process one token. An explicit
effective count for the exact variant is therefore an active reading. For
example, Gemma 4 E2B's `2.3B effective (5.1B with embeddings)` reads as
2,300,000,000 active parameters. The embedding-inclusive total is not the
active count. The E4B column's 4.5B effective count belongs only to E4B.

Prose binds each count to the nearest preceding model mention in the same
clause. Alpha's count cannot come from `Unlike Beta (22B active parameters),
Alpha is dense`. A two-column header naming Beta cannot bind to Alpha.
Generic `Property | Value`, `Attribute | Value`, and headerless tables bind
to the repository subject only when the table and nearest preceding heading
do not name another model or variant. Technical fields naming a component,
such as a vision encoder, do not rename the subject. Model rows and columns
must match a subject name exactly after normalization, including hyphenated
variants. `Alpha Lite` does not bind to `Alpha`. Prose that ties a count to
other models, including `models with`, `of <Name>`, `compared with`, `unlike`,
or a model mention after the count in the same clause, supplies no reading.
Own descriptions such as `Alpha is a MoE model with 3B active parameters`
and `Alpha has 3B active parameters out of 30B total` read 3B. A subject's
`language model with 671B total parameters with 37B activated` reads 37B.
More than one distinct own reading for a facet is ambiguous and cannot verify
by selecting whichever agrees. Ranges, qualified bounds and phase-dependent
counts do not become one scalar.

On a line labelled `Number of Total Parameters`, `Number of Parameters`, or
`Total Parameters`, a value `<total>-A<active>` or `<total> A<active>` can
read the active count. The collector checks the existing verified total
against the retained API census. The parameter reader repeats the shorthand
total's agreement with that same-repository census using the written
precision and the standard number tolerance. The README and API must both
be cited. This rule does not read a model-name suffix.

Active equals total only for a dense transformer or encoder-only backbone
whose safetensors census contains exclusively `BF16`, `F16`, and `F32`
counts. FP8 tensors and their scales, packed `I32` / `U8` weights, unknown
dtypes, and a census with only `safetensors.total` cannot use this rule.
A non-null non-text tower, such as `vision_config`, `audio_config`,
`img_processor`, `audio_processor`, `visual`, or an image/audio encoder, prevents equality because the census includes parameters
that a text token never uses. A total stated for the subject in the card must
agree with the census at its written precision. It also requires no blocking
expert or recurrent settings at any config level, no positive PLE dimension
in `hidden_size_per_layer_input`, and no active or effective parameter wording for the subject variant in a retained
model card. A null or zero PLE dimension does not block equality, and
`vocab_size_per_layer_input` alone never blocks it. A zero-width embedding
table holds no parameters. The same table and prose binding rules used for scalar
readings scope that wording; disclosures about other variants do not block it.
A retained README must be cited so the verifier repeats the wording check. The collector requires an existing
verified total and agreement with the fresh retained API census. Hybrid and
unclassified configs do not use equality. The verifier repeats the config
classification and same-repository census comparison without reading the
collector's value as an input.

The retained Gemma 4 31B, E2B and E4B configs explicitly disable MoE and
leave expert settings null, so all three have dense backbones. E2B and E4B
retain their explicit effective counts. In the retained 31B config,
`hidden_size_per_layer_input` is zero but `vocab_size_per_layer_input` is
262144. Its zero-width PLE table does not block equality. Its non-null
vision tower does, and the card's 30.7B total disagrees with the 31,273,088,876 census
beyond its written precision. The card also lists a ~550M vision encoder.
The active count remains a gap. The shared README's effective counts belong
to E2B/E4B and remain their explicit active readings.

All HF hardware claims use only the deterministic readers, even when an LLM
reader is configured. The public API's `config` field is trimmed. It can
supply a positive reading when an explicit rule holds, but it cannot
establish absence of architecture or expert facets. No written rule proves
that a retained config cannot carry these facets, so they have no
`not_disclosed` path. An unlisted model type, varying expert counts, or a
populated expert key without a readable count is a gap. A total-parameter
absence is never verified from a README or config.

An active-parameter absence requires a cited retained config that reads `MoE`,
`hybrid-SSM-transformer`, or `SSM`, a cited retained HF API parameter census,
and a retained README. Unknown architectures and missing configs remain gaps.
Absence also fails when dense equality applies.
The README must have no active, activated, or effective parameter wording at all. If wording is present
but cannot bind to one scalar, the collector reports a gap with the quote
and files no fact. DeepSeek V4.1 Flash's `8B / 16B` prefill/decode counts
remain such a gap. Every no-reading outcome is a gap except an explicitly
verified active-parameter absence. Only supported absences become
`not_disclosed`, with retained-copy citations and `checked_sources` naming every attempted source.
`hf-architecture-absence@1` repeats these checks over all cited copies. A
failed fetch is reported as a failed check and never cited as a reading.

The HF dispatch remains conservative about mixed citations. When a hardware
claim cites both an HF copy and a non-HF document, it is skipped as
`unbound_hf_copy` even if the HF copy alone could supply the value. The
collector files only scoped HF citations; this work does not relax that
dispatch rule.

The collector files facts and claims, updates the legacy `architecture`
block, and prints `DISAGREE` for changed existing values. It refuses to write
facts that fail the retained-copy check. It never writes verification
outcomes. A dry run keeps copies beside the report, outside the data
checkout, and leaves cards, registries, and queues unchanged.

`scripts/policy/architecture_coverage.py --root <modelspec-data>` counts
known and verified facts, sourced and verified `not_disclosed` facts, and
gaps for all five facets. `Fact` has no inapplicable state. Expert facets
therefore need no facts for a model with a verified dense transformer or
encoder-only architecture. The command reports these as `dense_exempt` and
exits nonzero for any gap. It also counts catalogue cards with a non-null
legacy `architecture.active_parameters`, excluding non-card Markdown files.
Vocabulary and snapshot facet columns come from the registry automatically;
`decision/snapshot_keys.json` contains signing keys, not facet IDs.

The `json-default` normalizer preserves JSON arrays and object delimiters
and sorts keys for stable fingerprints. Invalid JSON and recursion failures
while decoding or serializing raise `UnsupportedContentError` with
`invalid_json`. The text normalizer removes lines
containing only punctuation, which makes formatted configs invalid JSON.
README tables can mix HTML and Markdown. The parameter reader normalizes
HTML tables without flattening surrounding Markdown. A table's model row or
column must match the subject; Gemma's variant labels such as `26B A4B` bind
the table without supplying a parameter reading themselves. The sampling
setting `top_k` never supplies an expert count.

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
