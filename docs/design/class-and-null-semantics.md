# Class and null semantics (MODEL-97, MODEL-98)

*Design, written before the code. Decided 2026-09-20.*

Two tickets, one worktree, one bump. MODEL-97 asks the catalogue to stop
publishing "nobody looked" and "there is nothing to look for" as the same empty
value. MODEL-98 adds `decision-model` to `ModelType`, which widens a published
enum and costs a major version under the MODEL-59 rule. Jamie's call
(2026-09-20) is that consumers absorb **one** break rather than two, so they
ship together.

This document answers the five questions the ticket asks in order, and records
what was deliberately *not* done and why.

---

## 1. How "inapplicable" is recorded

### The candidates

**(a) A sentinel value in the field.** `architecture.num_layers: "n/a"`,
`modalities.text.max_output_tokens: "inapplicable"`.

* *Drift:* low — the marker is where the value would be.
* *Round-trip:* it survives YAML, but only by changing the field's Python type
  from `int | None` to `int | str | None` on every field that can carry it.
  Pydantic would accept a string where a count belongs, which is exactly the
  validation this schema exists to provide.
* *Consumer:* catastrophic. `/api/models/<id>.json` publishes the card
  frontmatter verbatim (`pipeline/export.py`), so every typed numeric field in
  the tree becomes `number | string | null`. That is a widening of **hundreds**
  of fields at once, and every consumer arithmetic path (`if layers > 0`)
  breaks on a string.
* **Loses.** It buys one distinction by corrupting the type of the whole tree.

**(b) A per-card `not_applicable: [dotted.field.paths]` list.**

* *Drift:* this is the failure mode. The list is hand-written prose about the
  schema, maintained separately from both the schema and the card. A path can
  be misspelled, can name a field that was renamed, can be copied between cards
  by a seeder, and — worst — can go stale in the one direction that lies: a
  field marked inapplicable and later filled in by research now asserts two
  contradictory things at once. Validation catches the first three; nothing
  catches an author who marks a field inapplicable because it was *hard to
  find*. `data_residency: []` on 1,339 cards (MODEL-77) is what that failure
  looks like at corpus scale.
* *Round-trip:* it needs work. `ModelCard.from_yaml_string` maps known
  top-level keys and **silently drops** the rest, while `pipeline/load.py`
  publishes the raw frontmatter. A new top-level key would therefore survive
  into the export but vanish from any card that a tool round-tripped through
  `ModelCard.to_yaml()` — a silent data loss that no test currently covers.
* *Consumer:* good. Additive new key, existing fields unchanged.
* **Loses**, as the primary mechanism. Kept in reserve: see "The escape hatch
  we did not build".

**(c) Applicability derived from `model_type` via a table.**

* *Drift:* cannot drift *per card*, because there is nothing per card to
  maintain. One table, one class, one answer; change a card's `model_type` and
  its applicability follows in the same commit. The table itself can be wrong,
  but it is wrong **visibly and in one place**, reviewed once rather than 1,339
  times.
* *Round-trip:* nothing to round-trip. The card gains no key, so
  `to_yaml()`/`from_yaml_file()` are untouched and cannot lose it.
* *Consumer:* the derivation must be *published*, or a consumer cannot see it.
  That is an additive block in the export, not a change to any existing field.
* **Wins.**

This is not a new idea in this repository: `schema/card.py` already carries
`__applicable_model_types__` on the nested modality and capability sections,
and `applicable_field_coverage` already refuses to count a subtree that the
card's class cannot have. MODEL-97 is that mechanism finished — extended from
whole sections to named fields, and published instead of kept internal.

### The decision

**Applicability is derived from `model_type` (plus `model_subtypes`), never
authored on a card.** One table in a new `schema/applicability.py`, evaluated
by a pure function, published as a derived block beside the card.

Two constraints on the table, both enforced by tests:

1. **Every path must resolve to a real `ModelCard` field.** A typo is a test
   failure, not a silent no-op. This is the anti-drift device that option (b)
   cannot have.
2. **A path may only be derived from the class.** Not from another card field.
   The tempting rule — "`deployment.hardware_profiles` is inapplicable when
   `licensing.open_weights` is false" — is **refused**, because
   `open_weights` is `bool = False` with no null state: a card nobody has
   researched is indistinguishable from a card that is genuinely closed.
   Deriving inapplicability from it would manufacture "there is nothing to
   know" on every unresearched card in the catalogue. That is the MODEL-77
   `data_residency: []` mistake with a new coat of paint.

### What we refuse to call inapplicable

The MODEL-97 description lists `architecture.num_layers` as inapplicable for a
Jev card, on the grounds that the architecture is undisclosed. **We disagree,
and the distinction matters.** A decision model has layers; TypeSafe has not
published them. That is *unknown and possibly unobtainable* — much nearer
`withheld` than "not applicable". Marking it inapplicable would assert that
there is nothing to know, which is false, and would quietly excuse the
catalogue from ever asking. Architecture fields stay `null`, i.e. not yet
researched, for every class.

"Inapplicable" is reserved for fields that are **meaningless given the class**:
a maximum output-token count for a model that emits no tokens; an output
tok/s for a model with no output stream. Those have no answer, not a missing
answer.

---

## 2. Does this change the published shape?

**MODEL-97 on its own: no, and therefore it needs no bump.**

Established by reading, not assumed:

* `pipeline/export.py::write` publishes `{"build", "card": model.front,
  "body"}` per model. `card` is the frontmatter verbatim. Because applicability
  is derived and stored nowhere on the card, **no field in that tree changes
  type, name, meaning or range.**
* `model_summary()` (`index.json`) publishes a fixed key set; none of it
  changes.
* `candidates.json` / `profiles.json` / the graph views: untouched by MODEL-97.
* The CLI `--json` envelope never carried any of this.

The derivation is published as a **new sibling key** in
`/api/models/<id>.json`:

```json
{
  "build": { … },
  "card":  { … },                     // unchanged, verbatim
  "body":  "…",
  "applicability": {
    "basis": "model_type",
    "model_type": "decision-model",
    "not_applicable": [
      "inference_performance.api_tps_output",
      "modalities.text.fill_in_middle",
      "modalities.text.max_output_tokens",
      "modalities.text.streaming"
    ]
  }
}
```

`docs/cli-contract.md` — "New fields may be **added** to any object. Parse
permissively." — makes that additive, not widening. A consumer that ignores
`applicability` sees precisely the tree it saw yesterday; a `null` it reads
means what it always meant, "no value here", and the new key is where it can
now learn *why*. MODEL-97 is a **no-bump** change, deliberately, and the
reasoning is that the distinction is expressed by adding information rather
than by widening a field's range.

**MODEL-98 is the bump.** `decision-model` is a value that no consumer
switching on `model_type` has ever seen, and `model_type` is published in
`/api/models/<id>.json`, `index.json`, `candidates.json` and the graph nodes.
That is the textbook widening in the MODEL-59 rule ("a new enum value a client
must handle"). It bumps `build.export_schema_version` **2.0 → 3.0**.

Doing both now means MODEL-97's rendering, coverage and applicability work
rides a bump that MODEL-98 has to pay anyway — one break for consumers, as
decided.

*Historical note, since it is the precedent that could be misread:*
`miscellaneous` (MODEL-58) and `time-series` / `vision-encoder` /
`text-encoder` were added **without** a bump. They predate MODEL-59, and are
the same class of omission as the nullable `predicted_decode_tps` that the
rule exists to prevent. They are not a licence to skip this one.

---

## 3. `decision-model`, and every site that switches on `ModelType`

> **`decision-model`** — evaluates supplied state against caller-defined typed
> questions, returning calibrated choices, scores or probabilities; generates
> no text.

| Site | What it does with a type | Verdict |
| --- | --- | --- |
| `schema/enums.py` | the vocabulary | **must change** — add the member and its docstring |
| `schema/card.py` `_TEXT_TYPES` | gates the `TextDetail` subtree in coverage | **must change** — a decision model *reads* text, so `max_input_tokens` / `context_window` apply. It is deliberately **not** added to `_GENERATIVE_TEXT_TYPES`, so the `Capabilities` block (coding, reasoning, creative, agent) stays out of its denominator |
| `schema/card.py` other `__applicable_model_types__` | vision / audio / video / document / image-gen / embedding / reranking subtrees | **handles it** — membership tests; a new type is simply absent, so those subtrees are already excluded |
| `pipeline/hardware.py` `TOKEN_GENERATING_MODEL_TYPES` | allowlist deciding whether `predicted_decode_tps` is a number or `null` | **handles it correctly by construction** — an allowlist, so an unlisted new type gets `null`, which is the honest answer for a model that decodes nothing. Locked by a test rather than left to luck |
| `pipeline/hosts.py::assess` | calls `is_token_generating` | **handles it** — same allowlist |
| `pipeline/ranking.py::_score` and `api/ranking/engine.py::_score_model` | `preferred_types.index(t)` for a type bonus | **handles it** — a type in no profile's `preferred_types` scores a 0 bonus. It is never *penalised*, and never scored *up* |
| `api/ranking/engine.py` `model_type` constraint filter | equality against a caller-supplied string | **handles it** — a caller can now ask for `decision-model` and get exactly the cards that claim it |
| `pipeline/render.py` | prints `front["model_type"]` into the stat strip and the index row | **handles it** — opaque string. It **must change** for MODEL-97's sake (the applicability section), not for the new value |
| `schema/graph.py` | `model_type` is a string property with an index | **handles it** — no enumeration, no switch |
| `pipeline/competition.py` | groups active models by `model_type` string | **handles it** — a new group with one member, which is correct: a decision model competes with decision models |
| `pipeline/agent_ready.py` | emits the string as `applicationSubCategory` | **handles it** |
| `web3d/downselect.v2.html` (the wizard) | `preferred.indexOf(c.model_type)` | **handles it** — same 0-bonus path as the Python scorer, which is why the two must stay the same code shape |
| `web/src/types/graph.ts` | `model_type?: string` | **handles it** — typed as `string`, not a union |
| `cli/modelspec/cli.py` | `--type` filter, graph queries, `no model_type set` lint | **handles it** — string comparison |
| `cli/modelspec/offline.py`, `api/worker/src/rank_service.py` | read `model_type` out of `candidates.json` into `Candidate` | **handles it** — passed through to the scorer, never enumerated |
| `cli/modelspec/snapshot.py` | refuses a snapshot whose export **major** differs | **must change** — `2.0` → `3.0`; this is the mechanism that makes the bump safe |
| `.github/scripts/check_rank_response.py`, `check_policy_response.py` | assert the live endpoint's `export_schema_version` | **must change** — they pin `"2.0"` literally |

Nothing in the repository enumerates `ModelType` exhaustively at runtime — no
`match` over members, no dict keyed by every value, no exhaustiveness check.
That is why the blast radius is small: the additions are the two version
constants and the intentional semantics, not a long tail of `KeyError`s.

---

## 4. The bump

| Constant | Now | After | Why |
| --- | --- | --- | --- |
| `pipeline/export.py::EXPORT_SCHEMA_VERSION` | `"2.0"` | **`"3.0"`** | `model_type`'s published range widens |
| `cli/modelspec/snapshot.py::EXPORT_SCHEMA_VERSION` | `"2.0"` | **`"3.0"`** | must equal the producer; `tests/test_export.py` holds them equal |
| `.github/scripts/check_*_response.py::EXPORT_SCHEMA_VERSION` | `"2.0"` | **`"3.0"`** | the live smoke checks assert the deployed tree's version |
| `cli.modelspec.offline.SCHEMA_VERSION` (the CLI `--json` envelope) | `"1.0"` | **`"1.0"` — unchanged** | verified by reading: neither `rank`'s result rows (`pipeline/ranking.py::_score`) nor `fit`'s rows carry `model_type`. No envelope field's range widens |
| `rankings.json` `schema_version` | `"2.0"` | **`"2.0"` — unchanged** | the ranking report document is not the card tree |
| `pipeline/policy_export.py::POLICY_EXPORT_SCHEMA_VERSION` | `"1.0"` | **`"1.0"` — unchanged** | the policy tree publishes no `model_type` |

**What a pre-bump CLI does.** It refuses, cleanly, before reading a row.
`cli/modelspec/snapshot.py::_require_compatible_export_schema` compares majors
and raises `SnapshotInvalid`:

> `export_schema_version 3.0 is incompatible with this CLI (expects 2.x)`

`modelspec snapshot fetch` and every `offline` command exit **1** with that
sentence on stderr — or, with `--json`, the documented machine-readable error
object. A 2.x CLI never sees a `decision-model` row, never scores one and never
mis-parses one; it stops at the door. Symmetrically, a 3.x CLI refuses a 2.0
snapshot, so a caller with a stale cache is told to fetch rather than silently
ranking an old tree. Both directions get a test.

**Where consumers are told:** `docs/cli-contract.md` gains a section beside the
MODEL-77 one, naming the bump, the new enum value, the refusal message and the
upgrade instruction; `docs/graph-ontology.md` records the new Model
`model_type` value; `CLAUDE.md` and `AGENTS.md` carry the current version
number. DPF's ticket author is the consumer that matters and it pins the CLI,
so its upgrade is "take the new CLI, then `snapshot fetch`".

---

## 5. Ranking safety

**A decision model must land `unranked`, never scored low.** It already does,
and the guarantee is structural rather than a special case:

`_benchmark_evidence()` (in both `pipeline/ranking.py` and
`api/ranking/engine.py`) computes `rankable = total_weight > 0 and coverage >=
floor and len(present) >= required`. A card with no benchmark scores has
`present = {}`, `coverage = 0.0`, so `rankable` is false, and the row comes
back `rank_status: "unranked"`, `unranked_reason:
"insufficient_benchmark_evidence"`, `score: None` — the `score` key is
literally `None` rather than a small number (`"score": … if
evidence["rank_status"] == "ranked" else None`). It is then partitioned into
`report["unranked"]`, which `rank --json` does not even place in `result`. A
test pins this for a `decision-model` candidate in both scorers.

Note what is *not* changed: the ranking floors (`MIN_BENCHMARK_COVERAGE`,
`MIN_BENCHMARK_COUNT`) are untouched, as instructed.

**An inapplicable field must not read as missing evidence.** Two halves:

* *On the card and the page* — `applicable_field_coverage` excludes derived
  inapplicable paths from its denominator, and the model page moves an
  inapplicable fact out of "Not yet researched" into a separate "Not applicable
  to this class" list. The gap bar's denominator shrinks with it, so a
  time-series card is no longer scored against a context window it cannot have.
* *In the scorer* — **the profile's benchmark denominator is deliberately left
  alone.** It is tempting to drop inapplicable benchmarks from
  `benchmark_weights` per card, and it would be a serious bug: `required =
  min(MIN_BENCHMARK_COUNT, len(weights))`, so shrinking a profile to one
  applicable benchmark would make a single measurement enough to rank a model
  against a coding profile. A model whose benchmarks do not apply to a profile
  is not a better-evidenced candidate; it is a candidate with no evidence, and
  `unranked` is the honest verdict. Nothing about it is scored *low* — that is
  the distinction the rank/unrank split exists to keep.

We also **refuse** to add a new `unranked_reason` value (e.g.
`benchmarks_inapplicable`). `unranked_reason` rides in rows the CLI emits under
envelope `schema_version "1.0"`; a new value would widen the CLI contract and
force a second major bump on DPF, to tell it something it cannot act on today.
Recorded here as a deliberate refusal, not an oversight.

---

## The escape hatch we did not build

A per-card `not_applicable:` list remains the right answer for a fact that is
inapplicable for a reason the *class* cannot know. We have no such case today:
every example in MODEL-97 is either class-derivable (no text out, no output
stream) or is really "unknown" wearing the wrong label (undisclosed
architecture). Building the hatch now would mean maintaining a drift-prone
mechanism for zero call sites, and — because the card gains a new top-level
key — paying for the round-trip hole in `from_yaml_string` described above.
When a real case appears, it arrives with its validation: paths checked against
the schema, and a card that both marks a field inapplicable and gives it a
value is a validation error.

## Scope kept out

* **No Jev card.** That is MODEL-101. The Jev-shaped card in this work is a
  test fixture, and it invents no facts about any real model.
* **No new data on any existing card.** Applicability is derived; a null stays
  a null.
* **No ranking floor, and no `neutrality_commitment()` string, is touched.**
