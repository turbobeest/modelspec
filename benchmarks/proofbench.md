---
id: proofbench
name: "ProofBench"
aliases:
  - "FormalProofBench"
  - "Proof Bench"
  - "ProofBench v1.1"
page_kind: benchmark
category: math
subcategory: "Lean 4 graduate-level formal theorem proving"
status: active
summary: >
  Private 100-problem Lean 4 suite: given a natural-language statement and a
  formal theorem, the model must write a proof the checker accepts.
measures: >
  ProofBench (Vals AI; paper title FormalProofBench) tests whether a model can
  turn graduate-level math into a machine-checked Lean 4 proof. Each item pairs
  an English problem with a vetted Lean statement. The model may search Mathlib
  and run Lean, then must submit one proof. The checker either accepts it or
  not. There is no partial credit for a plausible write-up. Problems come from
  qualifying exams and textbooks across analysis, algebra, probability, number
  theory, and logic, not from contest short-answer keys.
task_format: >
  Agentic loop with lean_loogle, lean_run_code, and a single submit_proof.
  Up to 40 turns (Epoch and Vals write-ups). Natural-language statement plus
  Lean 4 theorem in; compiled proof out.
metric:
  name: "proof success rate"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Binary per problem. Vals ProofBench v1.1 (updated 4 Sep 2026): AlephProver
    100%, Claude Opus 5 99%, Claude Fable 5 95%, Kimi K3 87%, Harmonic
    Aristotle 86%, GPT-5.6 Sol 83% on the 100-problem private split. The March
    2026 FormalProofBench paper reported 33.5% for the best foundation model
    then tested.
dataset:
  size: 100
  size_note: >
    Leaderboard split is 100 private problems. The GitHub repo ships only
    sample Lean files; remaining statements are held out. Epoch describes the
    same 100-problem private split. Textbook/qualifying-exam sources; domains
    include analysis, algebra, probability, number theory, and logic.
  url: "https://vals.ai/benchmarks/proof_bench"
  license: ""
  languages:
    - en
  modalities:
    - text
    - code
  splits: "private 100-problem leaderboard split; sample problems in the repo"
  public_test_set: false
publisher:
  org: "Vals AI"
  authors:
    - "Nikil Ravi"
    - "Kexing Ying"
    - "Vasilii Nesterov"
    - "Rayan Krishnan"
    - "Elif Uskuplu"
    - "Bingyu Xia"
    - "Janitha Aswedige"
    - "Langston Nashold"
  url: "https://vals.ai/benchmarks/proof_bench"
paper:
  title: "FormalProofBench: Can Models Write Graduate Level Math Proofs That Are Formally Verified?"
  arxiv: "2603.26996"
  url: "https://arxiv.org/abs/2603.26996"
  year: 2026
leaderboard_url: "https://vals.ai/benchmarks/proof_bench"
repo_url: "https://github.com/vals-ai/proof-bench"
released: "2026-03"
last_updated: "2026-09"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: saturated
  top_score: 100
  as_of: "2026-09"
  note: >
    Vals v1.1 board dated 4 Sep 2026 lists AlephProver at 100% and Claude Opus 5
    at 99%. Vals itself warns that one problem in 100 is not a real gap and that
    a perfect score is a ceiling. The March 2026 workshop paper's 33.5% figure
    is a different snapshot, not a live number.
contamination:
  risk: low
  note: >
    The scored split is private. Sample Lean files in the public repo are not
    the board. Lean 4 checking blocks memorised natural-language write-ups.
    Textbook-origin statements could still overlap public formalisations.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    github.com/vals-ai/proof-bench: python main.py --dataset exported --model ... --k 3
    Tools: lean_run_code, lean_loogle, submit_proof. Epoch: up to 40 turns,
    Mathlib search plus code execution. Aristotle uses a separate harness.
tags:
  - math
  - lean
  - formal-verification
  - agentic
  - private-test
sources:
  - url: "https://vals.ai/benchmarks/proof_bench"
    title: "Vals AI ProofBench v1.1 leaderboard (updated 4 Sep 2026)"
    accessed: "2026-09-08"
  - url: "https://epoch.ai/benchmarks/proofbench"
    title: "Epoch AI ProofBench methodology (Vals source, 100 private, 40 turns)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2603.26996"
    title: "FormalProofBench arXiv abs (submitted 27 Mar 2026; ICLR 2026 workshop)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/vals-ai/proof-bench/main/README.md"
    title: "vals-ai/proof-bench README (tools and exported dataset flag)"
    accessed: "2026-09-08"
  - url: "https://github.com/vals-ai/proof-bench"
    title: "vals-ai/proof-bench repository"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2510.13888"
    title: "ProofGrader / academic ProofBench (name collision; NL proofs)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-079 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

ProofBench asks for a Lean 4 proof that compiles, not a contest write-up. Each of the 100 scored items gives a natural-language theorem and a vetted Lean statement. The model may search Mathlib and execute Lean, then it must submit one proof. The kernel accepts the proof or the item is wrong.

Problems are pitched at advanced undergraduate and graduate level, from qualifying exams and textbooks, covering analysis, algebra, probability, number theory, and logic. Epoch AI mirrors the Vals board and describes the same private split and tool loop.

## How it is scored

Scoring is binary proof success rate, as a percentage of 100. No partial credit. Vals v1.1 (HTML updated 4 September 2026) lists Logical Intelligence AlephProver at 100%, Claude Opus 5 at 99%, Claude Fable 5 at 95%, Kimi K3 at 87%, Harmonic Aristotle at 86%, and GPT-5.6 Sol at 83%. Vals notes that a one-problem gap is not evidence, and that a perfect score is a ceiling. Models that never call `submit_proof` score near zero even if early Lean steps looked fine (Vals cites DeepSeek V4 submitting 16/100).

The FormalProofBench paper (27 March 2026) reported 33.5% for the best foundation model in that snapshot. That number is not the September 2026 board.

## Dataset and licence

The leaderboard uses 100 held-out problems. `vals-ai/proof-bench` says the `problems/` tree holds samples only. Vals tags the product proprietary; a single SPDX id for the private set was not found. Test answers are not public. English informal statements plus Lean 4 code.

## Who publishes it

Vals AI, with Lean 4 experts. Paper: Nikil Ravi, Kexing Ying, Vasilii Nesterov, Rayan Krishnan, Elif Uskuplu, Bingyu Xia, Janitha Aswedige, Langston Nashold, arXiv 2603.26996, ICLR 2026 workshop VerifAI-2. Live board: `vals.ai/benchmarks/proof_bench`. Epoch AI republishes those scores and does not run a second exam.

## Lineage

This page is the Vals/Epoch Lean 4 ProofBench, including the FormalProofBench paper name and the v1.1 board. It is not the Berkeley ProofBench used to train ProofGrader (arXiv 2510.13888, 145 contest problems, 0–7 expert grades on natural-language proofs). It is not [Putnam-AXIOM](putnam_axiom.md), which scores boxed answers. MiniF2F and PutnamBench have no pages here.

## Saturation and contamination

On the 4 September 2026 v1.1 table the top is at 100% and the next at 99%, so the 100-problem split no longer separates the leaders. Lower ranks still move with tool use and submission rate. The scored set is private, so leakage risk is low relative to public contest archives. Textbook overlap remains possible.

## How to run it

Public samples: `python main.py --dataset exported --model ... --k 3` in `vals-ai/proof-bench` after `SETUP.md`. That run is not the private 100. Live numbers come from Vals, with up to 40 turns and the three-tool bundle. Aristotle uses its own harness (Epoch stores it, does not chart it). No lm-eval task was found. Do not mix a k-sample local run with the hosted board.

## Reading the numbers

100% means every private item compiled, not that the model can formalise arbitrary research math. A 99 vs 100 gap is one problem. Cost and latency on the Vals page vary by more than the accuracy spread (Vals quotes $9.35 per task for AlephProver vs $1.79 for Claude Opus 5). A low score can be a submission-loop failure rather than a math failure. Compare against a natural-language proof set only as a different skill.
