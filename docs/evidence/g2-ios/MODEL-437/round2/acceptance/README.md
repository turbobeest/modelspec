# MODEL-437 round-2 private acceptance

Measured implementation `6b9695fc75748bf31d8f07955bbf8fea89fc57f0` against main `a03c4d077acc03c2bc5dba526ff635fb708ccb94` with main host policy. Baseline a and candidate d use original data `9d9de96f062ac031336ee483ae97c3b436bd3845`. Candidate c uses #866 policy `82ebcf4627d255d7641303caff2d149e879cf359` and data#118 `f722d3fcb673b28bdff9fa1b5cac06c22cc61c38`.

| State | Period | Cases | First result | Tie set | Answer kind | Kind/member set | Gaps | Scores/cited | Warned templates | Steady MiB | Peak MiB |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| d | current | 302 | 0 | 0 | 0 | 0 | 0 | 944/0 | 1/40 | 109.0079 | 109.7911 |
| d | successor | 302 | 0 | 0 | 0 | 0 | 0 | 944/0 | 1/40 | 104.6112 | 107.7897 |
| c | current | 302 | 1 | 1 | 0 | 1 | 0 | 945/12 | 18/40 | 104.6295 | 105.4141 |
| c | successor | 302 | 1 | 1 | 0 | 1 | 0 | 945/12 | 16/40 | 103.7415 | 105.7109 |

All a/c/d states evaluated 319 corpus cases per period, including the 302 repository cases, with zero expectation failures, 286 contract-validated HTTP-200 responses and 269 repository HTTP-200 responses. Baseline a has 944 benchmark records, no cited benchmark records and one warned template out of 40 in both periods. All four candidate memory probes pass the 115 MiB steady limit. The local probe uses the deploy vendoring path and Pyodide 0.28.3; it is not a production Cloudflare memory observation.

The raw comparator correctly exits 1. The only changed case, `facet-must-model.fits_hardware`, changes in both periods. Its request has `where: [{known: model.fits_hardware}]`, maximizes `software_engineering`, requests summary explanations and has limit 5. It does not ask that a model fit a specific device.

The identical ten hardware-fit facts are admitted under main policy and rejected as `quarantined (mixed citation)` under #866. The facts have tier `best_effort`, so the MODEL-439 guaranteed-fact repair leaves them unchanged. Their inherited offering facts bring the total to 32 subjects that change from known to unknown. The candidate retains all 944 baseline benchmark readings unchanged, admits one additional reading, and changes zero software-engineering capability estimates. In-memory diagnostic replays that replace only the hardware-fact columns and indexes restore the exact baseline first result, answer kind and member set in both periods. Replacing the capability fit or snapshot seed does not. These diagnostic replays write no snapshot and disable no production gate.

The repair was applied directly from data#118, whose sole parent is the pinned baseline. All 13 changed files match branch bytes. Unchanged leaf files link to baseline through real directories. The #891 script was then actually executed in dry-run mode using an explicit empty CopyStore and date 2026-10-21; it reports zero remaining changes. No repair --write run was performed here. No source page bytes were opened or fetched.

The first c attempt failed before corpus evaluation because a scratch view used nested directory symlinks that recursive discovery skipped. The corrected view uses real directories and unchanged leaf-file links. Failed-attempt provenance is retained; the engine and private data were not changed to resolve it.

Run setup_acceptance.py in a fresh scratch directory after placing the other helpers there. It retrieves pinned input revisions. Run run_acceptance.sh baseline, then candidate-d and candidate-c, compare, gates-d/gates-c and memory-d/memory-c. The candidate phases require the measured implementation checkout. setup-commands.public.json records the actual initial retrieval commands; commands.public.jsonl records measured subprocess argv, timestamps and direct exit codes. The setup script is a saved reproduction of construction originally executed inline. Calendar-dependent exports used the actual UTC date 2026-10-21; replaying on another day requires that date to be fixed in the environment.

Helpers remove ambient HMAC/Ed25519 signing keys before setting their throwaway HMAC key. The root executor also confirmed the relevant ambient keys were absent for the initial runs. All private export and memory subprocesses have exited. The root executor reports public re-vendoring completed with 129 files and clean imports. Private scratch removal waits for confirmation that these public artifacts have been copied. cleanup_acceptance.py deletes only the named acceptance scratch tree and does not follow the links into private inputs.
