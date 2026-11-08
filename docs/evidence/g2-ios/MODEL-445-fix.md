# MODEL-445 executor evidence

Status: **blocked on the acceptance target**. The requested noise rules reduce
the reconstructed October 21–November 4 UTC input to **49 discoveries**, not
10. Remaining candidates include GPT-6.1 Terra, Kimi K3.1 Pro, MiniMax M3.1
Flash, LFM3 models, Hy4 and Granite Speech 5. Their presence in issues does
not establish their facts, but the specified noise rules do not justify
hiding them. There is no arbitrary count cap or extra lab denylist.

Base SHA: `6815544116839f991c10904772e7357f12d5b566`.
Final implementation SHA: `faeefd371fd6c3bc4f3a0d0e92b7a5e58c115bd3`.
The evidence-only commit follows it. The final branch SHA is recorded in
the executor completion line and the untracked `.pr-commit.txt` hand-off.

## Measured results

- [Public issue export](MODEL-445-issues.json): 264 open issues, retrieved in
  one `gh issue list` invocation. This is below its 300-issue limit.
- [Reconstructed input](MODEL-445-watch-inputs.json): 68 issues and 69
  observations in `[2026-10-21, 2026-11-05)` UTC. One issue carries two
  source references. Missing creation dates stay null.
- [Replay and every rejection](MODEL-445-replay.md): 49 discoveries,
  19 rejected observations, and one accepted cross-source duplicate grouped.
  Rejection counts: 6 already carded, 6 packaging variants, 4 dated
  checkpoints, 2 reupload organizations and 1 embedding-only organization.
  Public checkout cards and private main cards produce the same counts.
- The same date selection in `America/New_York` contains 67 issues and
  68 observations, yielding 46 discoveries and 21 rejected observations.
  It includes the image variants filed just after midnight UTC on November 5.
  Neither timezone interpretation meets the target.
- [Complete dry-run triage](MODEL-445-triage.md): 13 duplicates, 12 already
  carded, 32 noise and 207 possible releases. The plan would close 57 issues
  as `not planned` and add `release-review` to 207. No issue was changed.
- [Card-addition audit](MODEL-445-card-additions.json): **none added** in the
  requested UTC window on private main at
  `c26a2d7b67039dd0ed2490cd740766680c9e454d`. The clone was not shallow.
  The latest card addition was October 15 UTC. A control audit for October
  1–20 found 13 additions. Historical recall has no denominator here;
  it is null, not 100%.

## Red first and verification

[Test output excerpts](MODEL-445-test-results.txt) name every failed test
and retain its assertion/error output. The unchanged implementation failed
17 new filter cases and 7 triage cases before implementation. Frontier
preservation cases already passed. Additional red-first review cases caught
numeric-version collisions, canonicalized mirror providers, resume starvation,
changed duplicate anchors, output overwrites and wrong-repository apply.

The filter tests cover every new organization and pattern rule, existing-card
matching, per-reason summary counts, and retention of Mistral Large 4, Grok
Imagine Video Lite and GPT-6.1 Sol style IDs. The triage tests use a fake GitHub
process boundary and clock. They verify reason comments, `not planned`,
relabeling, read/write call caps, spacing of at least one second, partial-failure
resume, changed issues and closed issues. No test calls live GitHub.

The older precision fixture now labels the three denied organizations as
all-negative; its denominator is explicitly undefined for those sources.
The historical MODEL-432 test still checks its four frontier releases and
accounts for every input, with an exact list of the newly rejected observations.
The old source-inspection assertion forbidding catalogue loading was replaced
with a behavior check that detection retains carded observations for reporting.

Final focused run: **253 passed, 1 skipped in 120.07s**, exit 0.
The skip requires a built site through MODELSPEC_DIST; this task changes no site.

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_watch_filter.py tests/test_release_watch_precision.py tests/test_release_watch.py tests/test_release_watch_triage.py tests/test_removed_sources.py
```

[Exact commands, tool versions, red/green counts and reproduction steps](MODEL-445-commands.md) include the explicit acceptance check that exited 1:
`AssertionError: MODEL-445 acceptance target unmet: 49 discoveries > 10`.

## Limits

No live source extraction, complete run-artifact recall, true facts about the
remaining candidates, or post-merge fortnight rate was observed. No live
`--apply`, full local pytest suite, deployment, paid-provider call, source-page
retention, Worker export change, production switch, Linear write or merge ran.
The full CI suite and cross-model review remain pending. The temporary private
clone and its audit scratch were deleted before hand-off. The target needs reviewed scope decisions or
verified identities for the remaining candidates; dropping them just to reach
10 would not establish that no real release was lost.
