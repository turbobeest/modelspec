# Release blog: same-day breakdowns of a new model (MODEL-222)

*Design, written before the code. Decided 2026-09-29. Series 1 of 5.*

When a lab releases a model, its announcement is the only detailed account
anyone reads that day. ModelSpec already holds more than that announcement:
every admitted benchmark reading, a capability estimate per domain with an
interval, verified prices, subscription coverage and hardware fit, all in one
signed snapshot. A **release breakdown** recompiles that snapshot into a full
account of the new model, beside the lab's own numbers, and publishes it as a
post under `/blog/`.

This document is the architecture for the series. It sets the interfaces that
tickets 2 to 5 build to. The editorial standard every post must meet is
[`docs/method/release-breakdown-standard.md`](../method/release-breakdown-standard.md).
Where this document and the standard disagree, the standard wins and this
document is wrong.

| Ticket | Builds | Section |
|---|---|---|
| 1 (MODEL-222) | this design and the editorial standard | — |
| 2 | the `/blog/` site section | [§4](#4-ticket-2-the-blog-site-section) |
| 3 | the breakdown generator | [§3](#3-ticket-3-the-breakdown-generator) |
| 4 | the same-day pipeline | [§5](#5-ticket-4-the-same-day-pipeline) |
| 5 | drafts for X, LinkedIn, Facebook, Instagram, Reddit and Hacker News | [§6](#6-ticket-5-social-drafts) |

Build order: 3, then 2 and 5 in parallel, then 4. Ticket 3 defines
`breakdown.json`, which 2, 4 and 5 all consume, and it moves `_accuracy` and
the domain-default selection out of `scripts/social/generator.py` into
`release_blog/` (§3.1, §3.4), so ticket 5 starts from the moved code. Ticket
4 only automates what 3 and 2 already do by hand.

---

## 1. The one rule the architecture exists to enforce

**A post is a rendering of a signed snapshot. Nothing in it is typed.**

Every number in a post comes from one of two places:

1. the signed decision snapshot the post names, read through
   `decision.snapshot.load_snapshot`, including values the decision engine
   computes from it (`decide()`, cost per task, P(best));
2. that snapshot's verification records, which the snapshot carries in
   `record_table` and `fact_records`.

A value enters a snapshot only through `_Compiler._admit` in
`decision/snapshot.py`. That means it has a `verified` outcome from a verifier
of a different model family, or a deterministic one, than its collector (the
two-key rule, [`docs/decision-verification.md`](../decision-verification.md)),
it has a registered source, and it is not from an excluded source
(`decision/excluded.py`). The breakdown generator therefore inherits every
admission rule by reading nothing else. It does not open `models/`,
`offerings/`, `verification/log.jsonl` or the web.

The consequences are structural, not editorial:

- A number a writer wants but the snapshot does not hold cannot appear. The
  post says it is unknown.
- A post is reproducible. Anyone with the snapshot file and the public key in
  `decision/snapshot_keys.json` can re-run the generator and get the same
  `breakdown.json`, byte for byte.
- A correction is a new snapshot and a new revision, never an edit
  (§4.4).

Human prose is allowed around the numbers, under the placeholder rule in
§4.3.

## 2. Data flow

```
Grok Bot signal ─▶ release-signals.yml ─▶ new-model card PR (a person merges)
                                                  │
                                                  ▼
                               deploy-sites.yml builds and signs snapshot S₁
                                                  │   uploads S₁ as an artifact
                                                  ▼
          release-breakdown.yml (ticket 4): S₀ = the previous deploy's snapshot
                                                  │
              ┌───────────────────────────────────┤
              ▼                                   ▼
   accuracy suite, pr profile, on S₁     release_blog.breakdown (ticket 3)
              │                            reads S₀, S₁ only
              └──────────────┬────────────────────┘
                             ▼
               blog/posts/<slug>/r1/breakdown.json
               blog/posts/<slug>/r1/social/…   (ticket 5)
               blog/snapshots/<S₀>.json.gz, <S₁>.json.gz
                             │
                             ▼
               draft PR, label `release-blog`; Jamie reviews
                             │
                             ▼
               publish PR flips status; Jamie merges by hand
                             │
                             ▼
               pipeline/blog.py (ticket 2) renders /blog/… on the next deploy
```

`S₀` is the snapshot before the model entered. `S₁` is the first one it
appears in. At +1, +7 and +30 days the same path runs again with `S₀` fixed
and a later `S₁`, and it writes revision `r2`, `r3` or `r4`.

## 3. Ticket 3: the breakdown generator

### 3.1 Module and entry point

A new package, `release_blog/`, next to `release_signals/`. It is a library
with a thin CLI, pure in its inputs, and it has no network interface.

```python
# release_blog/breakdown.py
def build_breakdown(
    *,
    model_id: str,
    after: LoadedSnapshot,          # S₁, signature verified
    before: LoadedSnapshot | None,  # S₀, signature verified; None only for a backfill
    accuracy: Mapping[str, Any],    # the pr-profile report for `after`
    revision: int,                  # 1 for launch day, then 2, 3, 4, …
    first_revision: Breakdown | None,  # r1, required when revision > 1
    registry: Registry = default_registry(),
) -> Breakdown: ...

def check_publishable(after: LoadedSnapshot, model_id: str) -> list[str]:
    """Why no breakdown can be written yet; empty when one can."""
```

```bash
python -m release_blog breakdown \
  --model <model_id> \
  --after <S₁.json.gz> --before <S₀.json.gz> \
  --accuracy <report.json> \
  --revision 1 \
  --out blog/posts/<slug>/r1/breakdown.json
```

**Signature.** Both snapshots load through `load_snapshot_bytes(...,
public_keys=load_public_keys("decision/snapshot_keys.json"))`, the Ed25519
path `pipeline/method.py` already uses. The generator refuses a snapshot whose
`signature_verified` is false. It never needs the HMAC secret, so the pipeline
in ticket 4 runs without it.

**Accuracy.** The report must pass the `pr` profile of `scripts/accuracy.py`
for `after.snapshot_id`. Reuse `_accuracy()` from `scripts/social/generator.py`
by moving it to `release_blog/gates.py` and importing it from both.

**Publishable.** `check_publishable` returns a reason, and the CLI writes
nothing, unless the model is a subject in `after` (lineup or archive) and at
least one of these is admitted for it: a `provider_self_report` evidence row,
an independent evidence row, or a capability estimate in any domain. A model
with no admitted evidence has no breakdown. A post that says only "we know
nothing yet" is an announcement, and ModelSpec does not publish those.

### 3.2 `breakdown.json`

Schema: `schemas/release-breakdown-v1.schema.json`, generated from the
pydantic model in `release_blog/model.py`. Canonical JSON (sorted keys, no
insignificant whitespace, the same `canonical_json` the snapshot uses), so two
runs on the same inputs are byte-identical and a test can assert it.

```text
Breakdown
  schema_version        "release-breakdown/1"
  model                 {id, name, provider, class}          # snapshot subject
  revision              int
  generated_from
    after               {snapshot_id, content_hash, as_of, key_id}
    before              {snapshot_id, content_hash, as_of, key_id} | null
    accuracy            {snapshot, profile: "pr", status: "pass"}
    generator           {package: "release_blog", version}
  decisions[]           every decide() call the post relies on
    {purpose, spec, spec_hash, decision_id, snapshot_id}
  claims_vs_evidence    §3.3
  standing              §3.4
  template_changes      §3.5
  cost                  §3.6
  hardware              §3.7 | null
  not_yet_measured      §3.8
  recheck               §3.8
  disclosures
    supplier            schema.suppliers.supplier_for(model.provider) | null
    early_access        post.yaml `early_access` | null   # standard §4.3
    neutrality          neutrality_commitment()["pledge"]
  sources               {source_id: url}     # every URL any section cites
```

Every leaf that carries a number also carries where it came from:

```text
Cited
  value       number
  unit        string | null
  record_id   string | null   # the snapshot record behind it
  source_ids  [string]        # keys into `sources`
  read_date   ISO date        # the record's verification date
  computed    string | null   # e.g. "offering.cost_per_task" when derived
```

A number without `record_id` or `computed` fails schema validation. That is
the machine form of "nothing is typed".

`decisions[].decision_id` is the ID `decision/engine.py` computes,
`dec_` + the first 24 hex of SHA-256(spec hash + snapshot ID). Decisions are
not stored anywhere. Re-running the spec against the retained snapshot
reproduces the ID, and ticket 3 carries a test that does exactly that.

### 3.3 Claims vs evidence

Source: the model's evidence rows in `after`, read as
`decision.snapshot.EvidenceValue`: `benchmark_id, version, subcategory,
value, unit, measured_by, effort, harness, date, source_ids, record_id,
date_type, source_snapshot, interval, n, quality_flags`.

- A **claim** is a row with `measured_by: provider_self_report`. Its source is
  the lab's page. Because it was admitted, a second key re-read that number
  from that page. X and Twitter URLs never qualify: they are signal-only
  ([`docs/grok-bot-signals.md`](../grok-bot-signals.md)).
- An **independent reading** is a row whose `measured_by` is
  `benchmark_author`, `independent_evaluator`, `modelspec` or
  `outcome_protocol`.

For each claim, the generator pairs every independent reading of the same
`benchmark_id`:

```text
ClaimRow
  benchmark      {id, version}
  claim          Cited + {harness, effort, date}
  readings[]     Cited + {measured_by, harness, effort, date,
                          interval, n, quality_flags}
                 + comparability: "same_setup" | "different_setup" | "not_comparable"
                 + differs_in: ["version" | "harness" | "effort" | "unit" | "subcategory"]
                 + difference: Cited | null    # reading − claim, only for same_setup
                 + claim_within_interval: bool | null
  status         "read" | "no_independent_reading_yet"
```

The comparability rules are fixed in code, not chosen per post:

| Condition | `comparability` | `difference` |
|---|---|---|
| Same unit, and version, harness and effort are equal or both unstated | `same_setup` | reading − claim, with `computed: "difference"` |
| Same unit, any of version, harness or effort differs, or one side is unstated | `different_setup` | null. Both numbers are shown, with `differs_in`. |
| Different unit or subcategory | `not_comparable` | null |

The generator never states a cause for a difference. A reading's
`quality_flags`, and the `limitations` of its retained record when it has
them, are shown verbatim beside it. The sentence that states a difference is
generated from one fixed template per `comparability` value, in
`release_blog/wording.py`: size, direction ("higher" or "lower") and unit,
nothing else. Prose cannot restate it (§4.3).

**What the lab didn't report.** Separately, `unreported[]` lists every
benchmark in the default decisions' domains (§3.4) where the model has an
independent reading and no claim. It is a list of readings, not an inference
about the lab's motives.

### 3.4 Where it lands

For each domain in `registry/domains.yaml` where the model has a capability
estimate in `after.capability.estimates`:

```text
DomainStanding
  domain          {id, name}
  estimate        Cited[value, low, high]       # 80% interval, from the snapshot
  decision        ref into decisions[]           # the domain's default spec
  rank            int | null                     # Result.rank in that decision
  band            "best" | "rest" | "thin"       # decision.bands
  band_size       int                            # models in `best`
  p_best          Cited                          # Result.p_best
  top3_stability  Cited
  leaders[]       up to 3 models of the `best` band, each with
                  {model, estimate, p_best}
  drivers[]       the records behind the estimate, from capability.drivers
```

The default spec per domain is the one `scripts/social/generator.py` already
uses in `_standings`. Move that selection to `release_blog/standing.py` and
import it from both, so a social card and the post can never disagree about
which spec a domain means.

P(best) and top-3 stability come from `deterministic_probabilities`, seeded
with `snapshot_id:spec_hash:domain`, so they reproduce exactly.

### 3.5 Which template tiers and bands it changes

For every template in `registry/templates.yaml` (a category row by a tier
column: `best`, `balanced`, `budget`, `fastest`, `private`):

1. `decide(spec, before)` and `decide(spec, after)`, with
   `spec = parse_spec(t.spec, facets=registry)`;
2. `decision.compare.compare(old, new)` for entered, left and rank changes;
3. a new `release_blog.bands.diff_bands(old.bands, new.bands)`, because
   `compare()` does not diff bands.

```text
TemplateChange
  template        {id, category, tier, name}
  decisions       {before: ref, after: ref}
  model_in_best   {before: bool, after: bool}
  top_before      [model]        # the `best` band, ordered by p_best
  top_after       [model]
  displaced       [model]        # in `best` before, not after
  compare_counts  compare()["counts"]
```

Only templates where something changed are listed. The rendered post groups
them by tier. When `before` is null (a backfill, §5.4), this section is empty
and says why.

### 3.6 Cost

**Per task.** For each of the model's offerings in `after`, the computed facet
`offering.cost_per_task` via `decision.computed.with_computed`, at the
contract default task (`DEFAULT_TASK_TOKENS`, 40,000 in and 4,000 out). When a
template the model changed sets its own `task_tokens`, that cost is shown too,
labelled with the task size. Each value is `Cited` with
`computed: "offering.cost_per_task"` and the price records it came from.

**Plans.** `decision.plans.load_plans(after)`, then for every plan:
`covers` is `"unknown"` when `plan.models is None` (coverage not verified),
otherwise `plan.covers(model_id) is not None`. `Plan.covers()` alone returns
`None` both for "not covered" and for "coverage unknown", so calling it
without the `plan.models` check first would print unknown coverage as "not
covered".

```text
PlanCoverage
  plan        {id, provider, name}
  covers      true | false | "unknown"     # "unknown" when models_covered is unknown
  coverage    the PlanCoverage entry and its coverage_quote record, when true
  monthly     Cited | null
  break_even  Cited | null                 # PlanRoute.break_even_tasks_per_month,
                                           # coding_tool access only
```

Plans whose coverage is unknown are listed as unknown, never omitted. Silence
would read as "not covered".

### 3.7 Hardware fit

Only when the snapshot's `model.weights_openness` fact is known and open.
Values are the verified facts `model.fits_hardware` and
`model.hardware_fit_indeterminate` (`registry/facets.yaml`), with their
records. `pipeline/hardware.py` predictions (`predicted_decode_tps`,
`predicted_max_context`) are not snapshot facts, so a post does not show them.

### 3.8 Not measured yet, and the re-check schedule

```text
NotYetMeasured
  unknown_facets    [facet_id]   # guaranteed facets whose state is unknown
  held_back         {reason: count} | null   # content.held_back[<subject>]
                                             # (new, see below): quarantined,
                                             # unsourced, stale_measurement, …
  domains_without_estimate [domain_id]
  claims_without_reading   [benchmark_id]
  speed             "unknown" | Cited  # offering.speed.* under speed-v1
Recheck
  first_published   ISO date     # r1's date
  schedule          [{day: 1|7|30, due: ISO date, revision: int | null}]
```

`held_back` is the count of this model's rows the snapshot refused, by
reason. It lets a post say honestly that readings exist and are waiting for a
second key, without printing numbers that have not passed it.

**Snapshot change this needs (ticket 3).** Today `content.excluded` is one
snapshot-wide `{reason: count}` counter: `_Compiler.content` sums the
per-subject counts it already keeps in `self.excluded`, so a model's own
count cannot be recovered. Ticket 3 adds an additive key,
`content.held_back: {subject_id: {reason: count}}`, for kept subjects only,
built from that same per-subject counter, and `LoadedSnapshot.held_back(cid)`
to read it. It is additive and omitted when empty, as `subscriptions` is
([`docs/decision-snapshot.md`](../decision-snapshot.md)); it widens no
existing field. Until a snapshot carries it, `held_back` is null and the post
says the count is not available, rather than reading the global counter.

For `revision > 1`, the generator also writes `changes_since_r1`: every field
whose value differs from `first_revision`, as old and new `Cited` pairs.

### 3.9 Guards in the generator

The generator refuses to write, rather than warning, when:

- any URL in `sources` matches `excluded_sources().url()`, or any string in
  the output matches `REMOVED_TEXT` (a second check after the snapshot's own);
- any `sources` URL is on `x.com` or `twitter.com`;
- a `Cited` has neither `record_id` nor `computed`;
- the two snapshots were signed by keys not in `decision/snapshot_keys.json`.

### 3.10 Tests (ticket 3)

- Byte-identical output from the same inputs.
- Each comparability row of §3.3, with literal expected values.
- A claim with no reading yields `no_independent_reading_yet`, not a
  difference.
- `decision_id` reproduces by calling `decide()` on the stored spec.
- A fixture snapshot with an unverified row: the row is absent and counted
  in `held_back`.
- An unsigned or wrongly signed snapshot is refused.
- An excluded source injected into a fixture snapshot is refused.

## 4. Ticket 2: the blog site section

### 4.1 Source layout

```
blog/
  snapshots/<snapshot_id>.json.gz     # every snapshot any post cites, signed
  posts/<slug>/
    post.yaml                         # metadata and status (below)
    commentary.md                     # optional human prose (§4.3)
    corrections.yaml                  # append-only (§4.4)
    r1/breakdown.json                 # generator output, never hand-edited
    r1/social/…                       # ticket 5 drafts
    r2/…
```

`slug` is `<YYYY-MM-DD>-<model-slug>`, where the date is r1's publication
date. Each signed snapshot is about 300 KB, so keeping the few that posts
cite in the repository is cheap, and it makes every post verifiable offline.

```yaml
# blog/posts/<slug>/post.yaml
schema_version: 1
model: <model_id>
title: <string>                  # no digits outside the model name (§4.3)
status: draft                    # draft | published
early_access: null               # a plain statement when ModelSpec had
                                 # pre-release access (standard §4.3)
revisions:
  - revision: 1
    published: null              # ISO date, set in the publish PR
    approved_by: null            # GitHub login, set in the publish PR
    approval: null               # URL of the approving review or comment
```

### 4.2 Rendering

`pipeline/blog.py`, called from `pipeline/build.py` like `pipeline/legal.py`
is. Pages are f-strings in the existing `render.shell()` with `MS_NAV`, and
charts are server-side SVG. No new templating or JavaScript dependency.

| Path | Content |
|---|---|
| `/blog/` | published posts, newest first |
| `/blog/<slug>/` | the latest revision, the correction log at the top, the revision history, the re-check schedule |
| `/blog/<slug>/r<N>/` | revision N, frozen as published |
| `/blog/<slug>/r<N>/breakdown.json` | the generator output, as committed |
| `/blog/feed.xml` | Atom feed; a revision or correction is a new entry |
| `/blog/standard/` | the editorial standard, rendered from `docs/method/release-breakdown-standard.md` with `render_markdown_body`, as `pipeline/legal.py` renders `docs/legal/` |
| `/api/decision/snapshots/<id>.json.gz` | every file in `blog/snapshots/`, byte for byte |

The last row is also the retained snapshot history that `POST /v1/compare`
in the Worker already reads (`DECISION_HISTORY_TEMPLATE` in
`api/worker/src/entry.py`), documented as not yet published in
[`docs/decide-api.md`](../decide-api.md).
Publishing it fixes that endpoint's `409` for every snapshot a post cites.
Ticket 2 must add a test that the Worker's expected path and the blog's output
path are the same string.

Every post footer carries: the `after` snapshot ID linked to its retained
file, the content hash and signing key ID, every decision ID with its spec,
the neutrality pledge from `neutrality_commitment()`, and a link to
`/blog/standard/`.

**Only `status: published` posts render.** A draft is never in `dist/`, not
on the internal preview either. Reviewers see a draft with
`python -m pipeline.blog preview <slug> --out <dir>`, and the PR's CI uploads
that preview as a build artifact.

**Holding mode.** `pipeline/holding.py` is an allowlist, so `/blog/` is dark
in holding mode until Jamie names it there. The retained snapshots under
`/api/**` are copied in either mode, as all of `/api/**` is.

### 4.3 Prose and the placeholder rule

`commentary.md` is optional, written by a person, and reviewed in the PR. It
may not contain a digit except inside a placeholder the renderer resolves from
`breakdown.json`:

- `{{n:<json-pointer>}}` renders a `Cited` value with its unit and a footnote
  link to its source and record;
- `{{model:<model_id>}}` renders a model's name from the snapshot, so a name
  like "GPT-6" does not trip the rule.

The renderer fails the build on a bare digit, an unresolved pointer, or a
pointer to a value without provenance. The same check applies to `title`.
The tone rules in the standard (§5 there) are enforced by the same pass: a
word list the renderer refuses, kept in `release_blog/tone.py`.

### 4.4 Revisions and corrections are append-only

- `rN/` directories are immutable once their revision is `published`. A new
  snapshot is a new revision.
- `corrections.yaml` only grows:

```yaml
- id: c1
  date: <ISO date>
  revision: 1                      # the revision that was wrong
  field: /claims_vs_evidence/…     # JSON pointer into that revision
  was: {value, record_id, snapshot_id}
  now: {value, record_id, snapshot_id}   # from the revision that fixes it
  effect: <one sentence, placeholder rule applies>
  fix_pr: <URL>
```

A new check, `tests/test_blog_append_only.py`, compares the PR against
`origin/main`: any change to a published `rN/` file, or to an existing
`corrections.yaml` entry, fails. The rendered post shows every correction at
the top, with old and new values, and links the frozen revision that carried
the error. Nothing is silently replaced.

### 4.5 Publication control

- `automerge.yml` skips any PR that touches `blog/`, exactly as it skips
  `.github/workflows/`. Ticket 2 adds the path and a test that the skip list
  contains it.
- A publish PR changes only `post.yaml` (`status`, `published`,
  `approved_by`, `approval`). Jamie merges it by hand.
- Recommended, and Jamie's call because it changes repository settings: a
  `CODEOWNERS` line `blog/ @<Jamie's login>` with "require review from code
  owners" on `main`.

### 4.6 Tests (ticket 2)

- A draft post produces no file in `dist/`.
- A published post renders every section in §3, with the footer fields.
- A digit in `commentary.md` outside a placeholder fails the build.
- A refused tone word fails the build.
- `test_sitemap.py` covers `/blog/` pages; `feed.xml` validates as Atom.
- Every outbound link on a post is a `sources` URL from its breakdown, a
  modelspec.dev URL or a GitHub URL of this repository. Nothing else, so no
  tracking or affiliate parameter can appear.

## 5. Ticket 4: the same-day pipeline

### 5.1 Where the snapshots come from

`deploy-sites.yml` already builds and signs the snapshot. Ticket 4 adds one
step: upload `dist/modelspec/api/decision/snapshot.json.gz` as an Actions
artifact named `decision-snapshot-<snapshot_id>`, retention 90 days. The
pipeline takes `S₁` from the triggering deploy and `S₀` from the most recent
earlier successful deploy on `main` whose snapshot lacks the model.

### 5.2 Which models get a post

The signal pipeline links a model to its release. For a day-0 item that
resolves to a card, ticket 4 has `scripts/process_release_signals.py` also
write `blog/releases/<signal_id>.yaml` into the working tree, and it extends
the commit step of `release-signals.yml`, which today stages only `models`
and `verification`, to stage `blog/releases` as well. The file therefore
lands in the same card PR and reaches `main` only when a person merges that
PR.

```yaml
signal_id: grok-20260926-1234567890123456789
model: <model_id>          # the resolved card
provider: <provider>
announced_at: 2026-09-26T13:14:15Z   # the signal's timestamp
```

The file holds no PR URL, because the PR does not exist when the script runs.
`first_seen_url` stays out of it too. It is signal-only.

### 5.3 The workflow

`.github/workflows/release-breakdown.yml`:

```yaml
on:
  workflow_run:
    workflows: ["Build and deploy the sites"]   # deploy-sites.yml
    types: [completed]
    branches: [main]
  workflow_dispatch:
    inputs:
      model:    { required: true }
      revision: { required: false }   # default: next revision
```

Steps:

1. Skip unless the deploy succeeded.
2. Download `S₁`; verify its Ed25519 signature.
3. **New posts.** For each `blog/releases/*.yaml` whose model is in `S₁` and
   has no `blog/posts/*/post.yaml`: find `S₀`, run the accuracy `pr` profile
   on `S₁`, run `check_publishable`, and on success run the generator with
   `--revision 1`.
4. **Re-checks.** For each post whose next scheduled day (+1, +7, +30 from
   r1's `published` date) is due and whose latest revision cites an older
   snapshot than `S₁`: generate the next revision. If the new
   `breakdown.json` equals the last one apart from `generated_from`, write
   nothing. An unchanged recap is not a revision.
5. Run ticket 5's social generator on each new revision.
6. Copy `S₀` and `S₁` into `blog/snapshots/`.
7. Open one draft PR per post with `RESEARCH_PR_TOKEN`, label
   `release-blog`, titled `blog: <model name> r<N>`. The body lists every
   decision ID, the `check_publishable` result and the `held_back` counts.
   A post that is not publishable gets no PR. The run summary says why.

Concurrency group `release-breakdown`, one run at a time. Required checks run
on the PR like any other.

The +1/+7/+30 days here are counted from the post's first publication. The
signal pipeline's re-checks (`acknowledge` in
`api/worker/src/signals_service.py`) are counted from the first card PR. They
are usually the same day. When they are not, the post's schedule is the one
readers see, and it is the one in `breakdown.json`.

### 5.4 Backfill

`workflow_dispatch` with a model already in the catalogue writes a post with
`before: null`. It has no template-change section and says so. This is how the
first posts are made before ticket 4's artifact history exists.

### 5.5 What "same-day" means in this pipeline

The critical path is: signal (every 10 minutes) → hourly drain → card PR → a
person merges it → deploy → breakdown PR → Jamie reviews → publish PR →
Jamie merges → deploy. Two of those steps are a person, on purpose. Same-day
is a target the pipeline makes possible, not a promise it can keep alone. The
post states its announcement time (`announced_at`) and its publication time,
so the gap is visible.

## 6. Ticket 5: social drafts

Social drafts are **views of `breakdown.json`**, never a second computation.
Ticket 5 adds to `scripts/social/generator.py`:

```python
def generate_from_breakdown(
    *, breakdown_path: str | Path, post_url: str, output_dir: str | Path,
) -> dict[str, Any]: ...
```

It reuses `_validate_draft`, `_disclosure`, `_svg` and `_png`, and it writes
into `blog/posts/<slug>/r<N>/social/`. Every number in a draft is read from a
`Cited` in the breakdown, so a draft cannot disagree with the post.

| Platform | Output | Constraint the draft respects |
|---|---|---|
| X | `x.txt`, 1200×675 card | 280 characters; the link and snapshot ID in the text |
| LinkedIn | `linkedin.txt`, 1200×627 card | disclosure in the body |
| Facebook | `facebook.txt`, 1200×630 card | disclosure in the body |
| Instagram | `instagram.txt`, 1080×1080 and 1080×1920 cards | links do not click: the card carries sources and read dates, the caption says so |
| Reddit | `reddit.md`: title and self-post body | the draft names no subreddit; a person chooses one and checks its self-promotion rules |
| Hacker News | `hn.txt`: title and URL only | the title is the post's title, not a claim; HN asks for original titles and no editorialising |

Angles are the existing ones (`new_entrant`, `honest_gaps`, `value`, `local`)
plus two: `claims_vs_evidence`, drawn from a `same_setup` row, and
`correction`, drawn from a new `corrections.yaml` entry. A correction draft
states the old value, the new value, the effect and the fix PR, as
[`docs/social/playbook.md`](../social/playbook.md) requires, and is written
for every platform the corrected revision had drafts for. `honest_gaps`
is mandatory for every r1 whose `not_yet_measured` is non-empty, and it goes
out with the first post, not later.

The manifest keeps `"automatic_posting": false`. The module has no posting
interface and no platform SDK. Posting follows
[`docs/social/playbook.md`](../social/playbook.md): a person posts by hand after
Jamie approves each post in writing. No agent holds, reads or enters social
account credentials.

## 7. What is deliberately not built

- **No live posting.** No platform API, no scheduler, no bot account.
- **No editing of published text.** Revisions and corrections only.
- **No numbers from outside the snapshot**, including a model's announcement
  page read live on the day. If the lab's numbers are not admitted yet, the
  post says the claims are pending a second key and shows `held_back`.
- **No predictions.** Hardware speed and context predictions, forecasts of
  where a model "will" land, and extrapolated scores stay out.
- **No comments or reactions on the site.** Corrections come through the
  process in the standard.

## 8. Open questions for Jamie

1. **CODEOWNERS on `blog/`** (§4.5): a repository-settings change, so yours.
2. **`/blog/` in holding mode** (§4.2): whether posts go live before the site
   leaves holding mode. The design keeps them dark until you name the path.
3. **Early access** (standard §4.3): the standard allows pre-release access
   only under disclosure and without conditions on content or timing. Whether
   ModelSpec accepts any is your call.
