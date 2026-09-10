# Handoff: who owns what after 2026-09-10

ModelSpec's MVP is functionally complete. What remains splits into three piles,
and the split is the point of this document: **most of it is not agent work**,
and treating it as agent work wastes effort and produces confident nonsense.

| Pile | Owner | Where |
|---|---|---|
| Four MVP remainders | Grok Build, as *preparer* — the decisions stay Jamie's | [`mvp-remainder.md`](mvp-remainder.md) |
| Post-MVP backlog | Grok Build, autonomous loop | [`post-mvp-loop.md`](post-mvp-loop.md) |
| Taste and judgement | Claude Code, with Jamie | this file, below |

## The standing rules, which apply to every worker

These were learned expensively during 2026-09-09/10. Do not rediscover them.

1. **Absence is data.** A null is honest; a plausible value is a lie that
   survives review. Cards left `active_parameters`, `commercial_use` and
   `attention_type` null with stated reasons rather than guessing, and that is
   the bar.
2. **A wrong answer is worse than no answer.** `total_parameters` parsed from
   filenames produced **1,589 published "it fits" answers for hardware that
   cannot hold the weights**. A null is skipped by the fit layer; a wrong number
   is served.
3. **Put limits in code, not prose.** Two agents were each given a Firecrawl
   budget in their prompt, acknowledged it, and together burned 920 of 1,000
   credits. The guard now lives in `scripts/benchmarks/fetch.py`.
4. **Verify by running, never by reading a ticket comment.** Six of eight
   "In Review" tickets were optimistically marked. A CI audit twice concluded a
   `|| true` was safe; the second look found it was not.
5. **Check exit codes directly** — `cmd >/dev/null; echo $?`. A pipe reports the
   *last* command's status and has already produced one wrong conclusion here.
6. **Record the exact variant.** Terminal-Bench 2.1 is not `terminal_bench`.
   SWE-bench Pro is not `swe_bench_verified`. MMLU-Pro is not MMLU.
7. **A provider's table of a competitor's score is not primary evidence** for
   that competitor. Claude Mythos 5 has no benchmark evidence for this reason,
   and that is correct.
8. **Evidence dating.** A static result needs a stated day; a retrieval time is
   not a publication date. A *live leaderboard* row is dated by the observation
   (`date_type: evaluated`) — see `BENCHMARK_WRITE_RULE` in
   `scripts/build_manifest.py`.

## Three floors — stop treating these as backlog

Of ~604 unrankable cards:

* **~96 can never be ranked** under current profiles — image, video, audio, OCR,
  base models, serving quants. No profile weights a benchmark they could score on.
* **~388 are LLMs not present on Artificial Analysis or LM Arena.** More crawling
  will never find them.
* **246 cards have no parameter count because the weights are closed.**

And the trap: **carding a missing model raises the unrankable count** until its
evidence lands. Never optimise that metric — it rewards not carding models.

## What stays with Claude Code and Jamie

Anything where the answer depends on taste, product judgement, or what a reader
will feel rather than what a source says:

* **MODEL-24**, the design pass across both sites, once data and pages settle.
* **The 3D graph explorer's look.** Jamie's standing note: "very professional and
  science fiction at the same time", explicitly not cartoonish.
* **What a ranking should mean** when evidence is unequal — the live question in
  MODEL-34.
* **Naming, copy, and how a refusal is explained to a reader.** The catalogue's
  value is that it declines to answer; that has to *read* as rigour, not as a
  gap.
* Any decision where two defensible options exist and the difference is
  editorial. Prepare the options, then bring them to Jamie.
