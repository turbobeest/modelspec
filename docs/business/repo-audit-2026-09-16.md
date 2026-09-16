# The business context, measured against the repository

**2026-09-16.** [`BUSINESS_CONTEXT.md`](BUSINESS_CONTEXT.md) carries a strategy
conversation held in claude.ai. Its own header says the live-site figures are a
snapshot and to *"check the actual codebase before relying on it"*. This file is
that check, run against `origin/main` `8cdde5f`. Every number below was measured
in the working tree on the date above, and the command is named so it can be
re-run.

Standing rule 4 applies to this file as much as to a ticket: **verify by
running**. Where the strategy document and the tree disagree, the tree wins.

## What holds

| Claim | Measured | Verdict |
|---|---|---|
| 1,339 model cards | 1,339 (`ls models/*/*.md`) | exact |
| 73 providers | 73 (`ls -d models/*/`) | exact |
| 1,112 benchmark pages | 1,112 distinct `id:` in `benchmarks/*.md` | exact |
| Rankings, downselect, CLI exist | `pipeline/ranking.py`, `web3d/`, `cli/modelspec/offline.py` | holds |
| Licence is MIT | **partly** — see below | revise |

## What does not hold, and why it matters

### 1. The corpus is not unreleased. It has been public for five months.

The document says *"Nobody has had access yet. The licence is not locked in;
MIT can be changed before launch."* The first sentence is true of **customers**
and false of **the corpus**.

`turbobeest/modelspec` is a public repository (GitHub API, `"private": false`,
created 2026-04-05), and `modelspec.dev` serves the export. The repository is
also not MIT-only: `LICENSE` splits it, and has since 2026-09-08 —

- code: MIT
- data (`models/`, `benchmarks/`): **CC BY-SA 4.0**

CC BY-SA 4.0 is irrevocable by its own terms. Every copy taken in those five
months keeps a perpetual licence to that content. [`CLA.md`](../../CLA.md) §2
lets the project relicense **going forward** — that is precisely what it was
written for — but no instrument reaches a copy already distributed.

**Consequence for strategy:** the section 9 licensing proposal ("graph data free
but delayed") is available for *future* data, not for the corpus as it stands.
Plan on that basis. [`data-policy.md`](data-policy.md) works through what remains
open.

### 2. Benchgraph's "7 active, 1,097 unassessed, 0 models reporting" is stale

Measured today:

- `status: active` on **739** benchmark pages, not 7. (`status: unknown` 295,
  superseded 27, saturated 21, proposed 6.)
- Model cards carry **164 distinct benchmark ids**, and **every one of them
  resolves to a benchmark page**. Zero orphans.
- So pages with at least one model reporting: **164 of 1,112 (15%)**. Pages with
  none: **948**.

The "0 models reporting" symptom is gone. The real shape is different and worth
stating plainly, because it changes what the fix is: this is not a broken join,
it is a **long tail of pages nobody scores against**. Four ids carry a third of
the corpus (`gpqa_diamond` 356 cards, `ifeval` 354, `math_500` 354,
`mmlu_pro` 354).

That is still the top data priority from section 11 — but as coverage and
honest disposition, not as a bug hunt. See `REV-11`.

### 3. The flagship revenue lever is blocked on two empty fields

Section 8 names **enterprise governance** — approved-model registry, licence,
origin and residency checks — as *"now the strongest revenue lever"*, and
section 9 names the *"verified, policy-rich graph"* as a moat. All four fields
exist on every card. Two of them are empty:

| Field | Filled | Of 1,339 |
|---|---|---|
| `origin_country` | 1,286 | **96%** |
| `license_type` | 1,258 | **94%** |
| `commercial_use` | 8 | **1%** |
| `data_residency` | 0 | **0%** |

This is not neglect. It is standing rule 1 working as designed — handoff
README names `commercial_use` as an example of a field deliberately left null
rather than guessed. But it means **the thing the plan says is most sellable
cannot be sold today**, and no payment rail changes that.

It is also more tractable than 1,331 blanks suggests, because `license_type` is
already populated and much of `commercial_use` follows from it as a licence
fact, not a judgement call:

| `license_type` | Cards | What `commercial_use` needs |
|---|---|---|
| `apache-2.0`, `mit` | 683 | the licence text; deterministic |
| `llama-community`, `gemma`, `deepseek` | 169 | **three** family-licence readings, each conditional |
| `proprietary` | 150 | provider terms; ~20 providers cover it |
| `other`, null | 336 | genuine per-card research; leave null until done |
| `cc-by-nc-4.0` | 1 | no |

Roughly **75% of the corpus is reachable from about two dozen careful
determinations plus a mapping table.** That is `REV-4`, and it is the highest
revenue-per-hour item in this repository.

`data_residency` splits the same way: open-weight models are residency-free by
construction, hosted ones need the provider's published region list. `REV-5`.

### 4. `stale_after_days` is already 30

`cli/modelspec/snapshot.py:49` — `STALE_AFTER_DAYS = 30`. The published contract
says a snapshot older than 30 days is served with a warning, and
`--require-fresh` fails on it.

This is a direct, mechanical constraint on the "delay the free data by a month"
option in section 9. Worked through in [`data-policy.md`](data-policy.md).

### 5. Two of the plan's 30-day items are repo-flagged "do not start"

Section 11 item 2 is *"Ship hosted `recommend`"*. That is **MODEL-3** (Worker)
plus **MODEL-6** (payment rail). `CLAUDE.md`, `AGENTS.md`,
`docs/handoff/current.md` and `docs/handoff/post-mvp-loop.md` all carry a
do-not-start on both, resting on [`../agent-commerce-assessment.md`](../agent-commerce-assessment.md).

That assessment is not a scheduling preference. It set an evidence bar for
charging at all: *"the active benchmark set is meaningfully larger than seven,
card scores carry per-score sources and dates (MODEL-13), and at least some
hardware throughput is measured rather than predicted (MODEL-22)"*.

**This is a live contradiction between two documents the project treats as
current, and it is Jamie's to resolve, not an agent's.** Recorded as the first
open decision in [`revenue-backlog.md`](revenue-backlog.md). Until it is
resolved, MODEL-3 and MODEL-6 stay do-not-start.

### 6. CLA sign-off covers 10 of 50 commits — and it does not matter yet

`git log` shows 50 commits, all from one author
(`117555601+turbobeest@users.noreply.github.com`), 10 carrying `Signed-off-by`.

The owner cannot fail to license work to themself, so IP is clean **today**.
The gap becomes real the moment a second contributor lands a PR, and an acquirer
will diff the sign-off log against the author log during diligence. `REV-12`.

## Sources

All figures: working tree at `origin/main` `8cdde5f`, 2026-09-16. Repository
visibility: GitHub REST `GET /repos/turbobeest/modelspec`, read 2026-09-16.
