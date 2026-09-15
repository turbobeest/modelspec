# Agentic latency: source survey (MODEL-57)

Question: does any published benchmark or leaderboard report **end-to-end wall-clock
time for an agent to complete a tool-calling task**, per model, on a named harness
and task set? Only pages actually opened are listed. Read date for all: 2026-09-15.
No latency numbers are recorded here.

| Source | What it measures | Whole loop? | Host / hardware stated | Per model | Harness, tasks, reps, variance | Usable | Why |
|---|---|---|---|---|---|---|---|
| Artificial Analysis, API performance methodology | TTFT, output speed, and "End-to-End Response Time": time to receive one complete response | No. One API request, no tools | Test client in GCP us-central1-a; provider hardware not stated | Per model x provider | Synthetic prompts; 1k/10k/vision workloads tested 8x per day, P50 over the past 72 hours; weekly 100k-token workload, P50 over 14 days ([methodology v2.2.0, 2 March 2026](https://artificialanalysis.ai/methodology/performance-benchmarking), accessed 2026-09-15) | No | Model-and-endpoint latency, not a tool loop. Useful as the model-side term only. |
| HAL (Holistic Agent Leaderboard), site | Accuracy vs dollar cost per agent across 9 benchmarks | No time axis found on the page | Not stated on the page | Per agent (model + scaffold) | Standard harness; cost-controlled | No | Publishes cost, not wall-clock. |
| HAL harness README | Harness with Weave cost and usage logging | Logs traces; no timing leaderboard | No | n/a | Configurable concurrency | No | README says leaderboard results are no longer updated through this harness. |
| HAL paper, arXiv 2510.11977 | 21,730 rollouts, 9 models x 9 benchmarks, cost analysis; logs shared | Mentions evaluation time for the whole run, not per task | Runs across hundreds of VMs | Per model and scaffold | Abstract gives no per-task time metric | No | Aggregate evaluation throughput, not per-task latency. Released logs might allow a derived measure; not checked. |
| SWE-bench leaderboards | Resolved rate; views for cost, cost limit, step limit, step distribution | No time view listed | Not stated | Per model (mini-SWE-agent for Verified) | 500 Verified, 300 Lite, and other sets | No | Steps and cost are reported, not wall-clock. Steps are a possible proxy but are not time. |
| OSWorld site | Task success on computer-use tasks | No per-task time | AWS support noted as cutting total evaluation time to within 1 hour | Per agent | OSWorld-Verified | No | Time is mentioned only as evaluation infrastructure speed. Site content is CC BY-SA 4.0. |
| tau2-bench repo (Sierra) | Tool-agent-user task success; text and voice modes | No latency metric found in the README | No | Per model | Domains: mock, airline, retail, telecom, banking_knowledge | No | MIT licence; no timing published. |
| Terminal-Bench README | Terminal tasks; Terminal-Bench-Core v0.1.1 for leaderboard | No timing mentioned | No | Per agent | Harness documented elsewhere | No | No time column in what was read. The leaderboard page (tbench.ai/leaderboard) returned a JavaScript shell over plain HTTP and could not be read. |

Correction 2026-09-15 (MODEL-62): the Artificial Analysis row previously said "P50 over 14 days" for all workloads; the methodology page limits the 14-day median to the weekly 100k-token workload.

Not checked (fetch budget): GAIA and BrowseComp leaderboards. No source I opened
calls itself an "agentic latency" or "time-to-complete" leaderboard.

## Sources opened (2026-09-15)

- https://artificialanalysis.ai/methodology/performance-benchmarking
- https://hal.cs.princeton.edu/
- https://raw.githubusercontent.com/princeton-pli/hal-harness/main/README.md
- https://arxiv.org/abs/2510.11977
- https://www.swebench.com/
- https://os-world.github.io/
- https://github.com/sierra-research/tau2-bench
- https://raw.githubusercontent.com/laude-institute/terminal-bench/main/README.md
- https://www.tbench.ai/leaderboard (JS shell only, no readable content)
