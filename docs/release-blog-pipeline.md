# Prepare release breakdown review PRs

MODEL-225 implements the public release-bundle executor. **Fresh production
release triggering is blocked.** The current private data split and the older
blog design disagree about public snapshot retention. This change does not
publish private snapshots, configure credentials, or dispatch a workflow.

## Design and the blocked handoff

New cards arrive through human-merged PRs in `turbobeest/modelspec-data`.
The older [release blog design](design/release-blog.md#5-ticket-4-the-same-day-pipeline)
assumed those cards and full signed snapshots were public. The current
[data split](design/data-split.md#public-ci-must-not-leak-the-private-data)
prohibits publishing fresh full snapshots and prohibits public PR creation
from a public job with private-data access.

The blog renderer retains every cited snapshot under `blog/snapshots/` and
copies it into site output even when the post is a draft. A keyed download
would still disclose the full fresh catalogue once the snapshot was committed.
Filtering that signed snapshot would invalidate its signature, content hash,
and reproducible decisions. A smaller independently signed snapshot would
change the comparison population and needs an explicit editorial scope.

Two designs were considered. Scheduled private polling can reuse
`MODELSPEC_DATA_TOKEN`, but crosses the prohibited public publishing boundary.
A private merge event can send metadata through an authenticated dispatch,
but that solves authentication only. Both still need an approved public
editorial export. The implemented executor therefore accepts only bundles
already committed in the public repository. It has no private download path.
Independent design review reached the same conclusion.

To complete the production handoff:

1. Define and approve a public signed editorial snapshot that reproduces the
   article's findings without exporting the fresh private catalogue. The current
   full-snapshot contract cannot provide that guarantee.
2. Produce that snapshot and its exact `pr` accuracy report after a private
   card PR merges. An upstream approval must make those inputs public before
   this executor reads them.
3. For private-to-public `workflow_dispatch`, Jamie configures a private-repo
   secret named `MODELSPEC_RELEASE_DISPATCH_TOKEN`, scoped to
   `turbobeest/modelspec`, with Actions read/write access. No such secret is
   created by this change. Stop at this repository-settings step until Jamie
   configures it. The existing `MODELSPEC_DATA_DISPATCH_TOKEN` points in the
   opposite direction.
4. Wire the approved exporter to the public bundle path and dispatch. Replaying
   the private merge itself and measuring live latency remain unobserved.

No repository setting, publication switch, Worker route, legal term, ranking
floor, or private writer is changed here.

## Public bundle format

An approved bundle consists of signed files already present under
`blog/snapshots/`, an accuracy report, and this manifest:

```yaml
# blog/releases/example-release.yaml
signal_id: example-release
model: lab/model
announced_at: '2026-09-26T12:00:00Z'
after: blog/snapshots/snap_<signed-id>.json.gz
before: blog/snapshots/snap_<previous-signed-id>.json.gz
accuracy: blog/releases/example-accuracy.json
```

`before` may be null for a backfill. The draft states the missing template
comparison. An optional `vocabulary` path names the matching public decision
vocabulary. All paths must remain inside `blog/`; symlinks and parent traversal
are refused. The command compares each input with its committed `HEAD` bytes.
Its workflow runs only on this repository's `main`, never on a PR or fork.

```bash
python -m release_blog.pipeline \
	--signal blog/releases/example-release.yaml \
	--out /tmp/release-review.json
```

The command validates pinned Ed25519 signatures, the actual `pr` accuracy
layers, snapshot/model eligibility, complete lab claims, stated missing
independent readings, numeric provenance, excluded sources, tone, and exact
reproducible Markdown. It runs the corpus and blog suites and renders the page
preview before writing the PR manifest. A failed check exits 2 and leaves no
success manifest. Local generated files can remain for inspection after failure.

The workflow also builds and tests the web page, including the corpus in
Chromium, before running the executor. Only then does it stage the explicit
post directory, push its deterministic branch and run `gh pr create --draft`.
The existing `RESEARCH_PR_TOKEN` is available only to that final transport step.
The workflow never merges or posts to a social platform. It checks all PR
states for its branch and leaves an existing or closed PR alone.

The schedule checks committed bundles hourly, at minute 23. A main push that
changes a public bundle starts the same path immediately. With no bundles the
workflow is a no-op. This cadence makes a same-day draft possible after an
approved public bundle arrives; it makes no claim about the blocked private
handoff. The PR records the announcement and preparation times, elapsed hours,
and whether they fall within the 24-hour target.

## Rechecks and publication

Rechecks are due at +1, +7 and +30 days from the first revision's actual
publication date. When several dates are overdue, the executor processes the
latest due milestone. It requires a signed snapshot dated at or after that
milestone. The first revision's `before` snapshot stays fixed. An unapproved
post or pending revision gets no further revision.

A material change is any changed finding in claims and evidence, standing,
template changes, cost, hardware, or stated measurement gaps. The comparison
ignores snapshot IDs, decision IDs, record IDs, verification dates and revision
bookkeeping. Numeric tolerance is zero, including P(best), consistent with the
editorial rule that a changed finding gets a revision. Sampling changes caused
by a different snapshot seed can therefore cause an update. An identical
finding produces no revision or PR; no-change checks may repeat hourly because
they do not create a state-only public PR.

Each update writes a new `rN/` directory with a dated update section. Old
revision files stay byte-identical. A published post keeps its status and old
approvals; the new revision has null `published`, `approved_by`, and `approval`
fields. Normal site rendering skips that revision. Jamie approves publication
separately, and the existing automerge exclusion for `blog/` remains in force.

## Optional platform drafts

If MODEL-226 supplies `release_blog.platforms`, the adapter calls:

```python
generate_from_breakdown(
	breakdown_path=revision / "breakdown.json",
	post_url="https://modelspec.dev/blog/<slug>/",
	output_dir=revision / "social",
)
```

If the module is absent, the PR states that platform drafts are pending. A
dependency or runtime failure inside an installed module fails the run.
MODEL-225 does not create or edit `release_blog/platforms.py`.

## Verification

`tests/test_release_pipeline.py` replays both the launch and +7-day update
through signed synthetic fixtures and a recording draft transport. It also
checks gate refusal, schedule boundaries, duplicate suppression, path bounds,
and immutable previous revisions. This proves local generation and gated draft
requests. It does not prove a real private merge, live export, or opened blog PR.
The executor PR's commands, red output, green output and limitations are in
`docs/evidence/g2-ios/MODEL-225-fix.md`.
