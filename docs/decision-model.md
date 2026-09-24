# Decision domain records

`decision/model.py` defines the records consumed by source change detection,
verification, and the snapshot builder. These records do not call the v1 ranker.
The design and glossary are on `origin/design/decision-engine` until that draft
PR merges. This implementation follows design sections 4.1, 4.2, and 5, with the
MODEL-134 instruction that verification must differ in agent **or** model family.

## Registry validation

`Fact` resolves `facet(id)`, `Offering` resolves `provider(id)`, and `Evidence`
resolves `harness(id)` unless its value is `unregistered`. Provider subjects also
resolve `provider(id)`. Unknown IDs fail validation. Model and offering subjects
resolve against the eventual snapshot, not the provider registry.

The default registry is `decision.registry`, owned by MODEL-133. It is not yet
present on this branch. Tests supply `context={"registry": RegistryStub()}` to
Pydantic's `model_validate` and `model_validate_json`. `load_offerings` accepts
the same dependency through its `registry` keyword. No production stub ships.
Calling registry-dependent validation without that module or an injected
registry fails rather than skipping validation.

A facet exposes `id`, `value_type`, `tier`, and `risk`. The supported value types
are `integer`, `number`, `boolean`, `string`, `string_set`, and `date`. Numbers
must be finite. Boolean values cannot stand in for integers. Dates are exact
`YYYY-MM-DD` strings. A `string_set` is a JSON list of distinct strings. Unknown
value types fail closed. Tier and risk govern the later filter and completeness
gates; they do not change a fact's value here. Registry integration must confirm
these value-type spellings when MODEL-133 lands.

## Facts and verification

A `Fact` has a stable `id`, a typed `subject`, a registry `facet`, a `state`, a
`value`, source references, and its latest verification. `known` requires a
non-null value and at least one source. All other states require null. An
unknown fact can have no source because no claim has been collected yet.

`Verification` names a fact or evidence ID. Each actor records its agent,
model family, and collection or checking method. A second method alone does
not make the same agent and model family independent. A mismatch requires a
nonempty `diff`; other outcomes carry no diff. A verification attached to a
record must target that record's ID and kind.

`quarantined` is a derived Python property, not writable serialized state.
A missing verification, `mismatch`, or `unreachable` means quarantined. Only
`verified` clears it. This is the verification status, not a completeness gate:
the snapshot builder must also enforce known values, freshness, and source
resolution before admitting records.

## Sources and source snapshots

A `Source` registers an HTTP URL, fetch mode, named normaliser, and uniquely
named cited regions. A region locator is `css`, `xpath`, or `heading_anchor`.
A `SourceSnapshot` records a timezone-aware retrieval time, a normalized-page
fingerprint, per-region fingerprints, and a retained `copy_ref`.

All content references and fingerprints use `sha256:<64 lowercase hex digits>`.
A `SourceRef` names the source, the retained snapshot's content address in
`snapshot_ref`, and the cited region IDs. The reference pins the same retained
content named by `SourceSnapshot.copy_ref`. The normalized-page fingerprint may
differ from this address because normalization changes the bytes.

MODEL-137 owns content storage and hashing. MODEL-138 must resolve source IDs,
check that cited regions exist in both source and snapshot, and bind the
reference to the correct retrieval. These types neither fetch URLs nor write
retained content into git. The registered URL and snapshot retrieval time
provide the source and date of a collected fact.

## Evidence mapping

`Evidence` subclasses `schema.card.BenchmarkEvidence`. Every existing card row
can be passed to `Evidence.model_validate(row.model_dump())`. Use the v2 type
when reading v2 rows directly from card front matter; the existing `ModelCard`
parser remains the v1 reader. It does not preserve the new qualifiers.

| Existing field | V2 meaning |
| --- | --- |
| `benchmark_id` | The benchmark ID, unchanged and open-ended |
| `score`, `unit` | The measured value and unit, unchanged |
| `model_id_as_evaluated` | The source's model label, not a canonical subject ID |
| `source_url` | The existing URL, retained for compatibility |
| `source_kind` | The original three-way provenance label, unchanged |
| `evidence_date`, `date_type` | Existing evidence dating, never replaced by retrieval time |
| `verified_at` | Legacy review date; it does not establish v2 verification |
| `benchmark_version` | Existing optional field, still defaulting to an empty string |
| `configuration`, `limitations` | Existing free-text qualifiers, unchanged |

The added optional fields are `id`, `subject`, `harness`, `effort`, `tools`,
`measured_by`, `subcategory`, `sources`, and `verification`. Absent qualifiers
stay null; absent sources stay an empty list. In particular, missing harness
information does not imply `unregistered`, and missing tools do not imply no
tools. `measured_by` admits the three existing source kinds plus `modelspec` and
`outcome_protocol`. Collection must set it explicitly; loading a legacy row
does not guess it from another field.

Evidence subjects are models or offerings, never providers. Attaching a v2
verification requires an explicit ID, subject, and source references. Legacy
rows remain quarantined until independently verified under this contract.

## Offerings and lifecycle

`load_offerings(path)` reads a YAML list from
`offerings/<provider>/<lab>/<model>.yaml`. Every row must match the path.
An offering's ID is `<provider>/<lab>/<model>/<region>/<tier>`. Region and tier
are path-safe identifiers. Duplicate tuples, duplicate fact IDs or facets, and
facts naming a different subject fail validation.

Offering values are an open list of `Fact` records rather than fixed columns.
Facets describe input, output, cached, and batch prices in USD per 1M tokens;
speed and its measurement method; rate limits and SLA; data handling;
attestations; fine-tuning; private deployment; and harness compatibility.
The registry defines each facet's exact meaning and unit. Unknown facts remain
explicit states or are absent; the loader never fills a price or attestation.

The only offering file in this PR is fake test data under
`tests/fixtures/offerings/`. Its provider, model, sources, and hashes are synthetic.

The v2 `Model` requires an explicit `lifecycle`. `active` and `deprecated` have
`in_lineup=True`; `retired` has `in_live_archive=True`. The eventual decision
filter handles explicit requests for retired models. The v1 card's existing
status enum is unchanged and is not automatically converted. Deprecation and
retirement dates can be sourced facts on the model.

## Legacy score quarantine and compatibility

The new engine never reads `benchmarks.scores`. MODEL-118 re-sources those values
into evidence. A marker beside `Benchmarks.scores` records this rule without
changing the field or v1 behavior.

`tests/test_decision_model.py` round-trips all entities, checks invalid records,
and loads every card and evidence row under `models/`.
`tests/test_decision_compatibility.py` compares both `pipeline.ranking` and the
Worker's `/v1/rank` service to `tests/fixtures/decision/v1-rank.json`. The golden
output was captured from the unchanged v1 code at `76eabc11`, with synthetic
cards covering legacy scores, reviewed evidence, and missing evidence.
