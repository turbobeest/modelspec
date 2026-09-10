# Post-MVP loop

An autonomous loop for Grok Build, to run when nobody is watching. Everything
here is **off the dpf critical path** — that is the definition of post-MVP. If
something in this file starts blocking dpf, it stops being a loop item and gets
raised.

## How to run one iteration

```bash
grok --always-approve -p "$(cat docs/handoff/post-mvp-loop.md)" < /dev/null
```

`< /dev/null` is not optional. A Codex worker launched without it hangs on stdin
forever; this cost 26 wasted minutes once.

**Pick ONE item per iteration.** Do not attempt the whole file. Choose by the
order below unless something is blocked, and say at the top of your report which
item you picked and why.

## Rules for every iteration

* **Read `docs/handoff/README.md` first.** Its eight standing rules apply to
  everything here, especially: absence is data, a wrong answer is worse than no
  answer, and verify by running rather than by reading a ticket comment.
* **Own your work end to end**: branch from `origin/main`, run
  `.venv/bin/python -m pytest -q` and require it green, commit, push, open a PR
  with `gh pr create --base main --fill`. `Run pytest` is a required check on
  `main`, so a red branch cannot merge.
* **One branch per iteration.** Never run two agents in this working tree at
  once — they fight over `HEAD`. If a worktree is dirty or on someone else's
  branch, stop and report rather than checking out over it.
* **Firecrawl is metered**: 5,000 credits/month, resets the 10th. Check the
  balance before any crawl. Plain markdown scrape is 1 credit/page; JSON,
  Question and Highlight formats add 4 more. The guard in
  `scripts/benchmarks/fetch.py` enforces a budget — do not bypass it.
* **Report in under 20 lines.** The orchestrator reading you is token-limited.
  PR URL, what changed, what you refused and why. No long tables.

## The queue, in order

1. **MODEL-9 — benchmarks as graph nodes.** BenchGraph's own graph. Jamie has
   put BenchGraph on the back burner, so this is real but unhurried.
2. **MODEL-26 — the host layer.** CPU, system memory, and why agentic
   wall-clock is not inference speed. Jamie's framing: tool calling probably
   matters as much as inference now. Design before building; bring the model to
   a PR comment first.
3. **MODEL-25 wave 3 — edge and long tail.** Jetson Orin and Thor, DGX Spark,
   Strix Halo, Ryzen AI, Intel Arc and Gaudi, Snapdragon X, plus the older parts
   still in wide use. Same rules as wave 2: **every figure from a vendor
   specification page with the URL recorded**, one file per distinct SKU, and a
   missing device beats a fabricated one. Groq and Cerebras WSE-2 remain absent
   because neither publishes a real per-chip datasheet — do not "fix" that.
4. **MODEL-8 — per-model authoring guides.** Only worth doing once the card
   shape has stopped moving.
5. **MODEL-10 — the curation loop.** A Firecrawl research agent plus a Grok
   agent keeping pages current. Depends on MODEL-5 proving itself over seven
   days first.
6. **MODEL-1 — repository restructure.** Cosmetic relative to everything else.
   Do it last, or never.
7. **MODEL-3 and MODEL-6 — the Worker and the payment rail.** **Do not start
   these.** MODEL-3 is off the critical path because the CLI reads a static
   export, and `docs/agent-commerce-assessment.md` recommends against metering
   for now. They are listed here so nobody "helpfully" picks them up.

## Standing background work, safe to pick when the queue is blocked

* **Reduce the 129 open-weight cards with no sourced `total_parameters`** —
  gated repos, pytorch-only, no published figure. The 246 closed-weight ones are
  a floor and are not work.
* **Chase the ~75 unrankable cards that *are* present on Artificial Analysis or
  LM Arena.** These are reachable by better matching. The ~388 that are on no
  board are not, and recrawling will not find them.
* **431,992 pytest warnings per run**, almost all Pydantic deprecations at
  `schema/card.py:804` (`obj.model_fields` on an instance). The output is
  unreadable, so a real warning would be invisible. Worth its own small PR.
* **`claude-mythos-preview`** still needs a relation or status pass now that
  `claude-mythos-5` and `-5-1` exist.
