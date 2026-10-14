# MODEL-378 engine verification

Base SHA: `629f7533068d2ab2b0f793be2eaa5aea3152ddf6`.
Initial implementation SHA: `3dbc2b66e795053cbc16bf596923bff80cd90625`.
Latest verified source SHA: `94c21d8b4b79f89f5c7c67198fc2217d85a6cc47`.
The latest delivery commit updates this evidence report. Its SHA is recorded in the
executor completion line and can be read with `git log -1 --format=%H --
docs/evidence/g2-ios/MODEL-378-fix.md`.

Worktree: `/Users/terbeest/dev/worktrees/model-378`.
Branch: `sparksandsawdust/model-378-engine`.
Private data main in the earlier run: `45cb41c1bfed7112e82402ed52278bfbef6bc3b3`.
Both the local `origin/main` ref and the remote main ref named that data SHA.
The data checkout was behind main, so verification used a `git archive` of
`origin/main` extracted inside this worktree, without changing another checkout.

## Authorized lab-subject follow-up

The user expanded scope to `catalogue.py`, `invariants.py`, and their synthetic
regression tests. Calibration now puts the compiler's registered labs in
`Catalogue.labs`, keyed by exact `lab:<id>` subjects. The invariant resolves
subjects against models, offerings, and labs. It preserves original fact IDs
and subjects, rejects unknown labs, and leaves candidate tables and counts intact.

Follow-up base: `9f3f4440fb148bd7cd587c18d544dec2c2daa573`.
Merged main: `d5569420b07ab8c7dd8efa2117789afb36505197`, producing
`c2457307faffc7a2973ded666a86ca06e0ba203b`. The final tests were replayed against
that merge before the fix. Private-data main was first archived at
`e5a0cf1f085c1b4d621de538d08378962eb3d78c`. It advanced during the full run,
so the final audit used a fresh archive of
`20c154d89c5bc8ace0601d95ab2785b6fa6592d1`.

| Follow-up check | Exit code | Observed result |
| --- | --- | --- |
| Shared-lab regression and three unknown-subject cases against the pre-fix merge | 1 | `4 failed in 2.46s`; the valid shared fact failed `subject_resolves`, and negative cases had two errors instead of one |
| Focused suites | 0 | `171 passed, 3 skipped in 16.84s` |
| Initial offline audit at the source SHA above | 0 | 5,559 served records, 0 errors, 2,803 warnings; model and offering counts unchanged |
| Final audit against refreshed private main, as of October 14 | 0 | Summary below; served record and candidate counts unchanged |
| Initial full suite in local time | 1 | `1 failed, 10452 passed, 8 skipped, 11 warnings in 1526.38s (0:25:26)` |
| Freshness test with UTC | 0 | `1 passed in 421.05s (0:07:01)` |
| Full suite with UTC at the source SHA above | 0 | `10453 passed, 8 skipped, 11 warnings in 1930.64s (0:32:10)` |

```text
Served facts: 5559; errors: 0; warnings: 2859; models: 1384; offerings: 92
```

The shared-lab test checks the original ID and raw subject, one shared fact,
two models, one offering, and six facts. The negative cases pass unknown
subjects through compilation and recalibration before asserting the one error.
Both read-only reviews found no defects. No public contract or frozen data changed.

The first full run crossed UTC midnight. `test_built_tree_passes_surface_lint`
found sitemap dates of October 13 against an October 14 UTC build manifest.
The builder uses local `date.today()` while the manifest uses UTC. The
isolated test and full-suite rerun use process-local `TZ=UTC` to align both
clocks; no product source or assertion changed for this setup issue.

Commands used the same tool versions listed below and Node `v22.22.3`:

```bash
# Red replay cwd: .scratch/model-378-followup/pre-fix-engine
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_data_trust.py::test_calibration_resolves_shared_lab_facts_without_adding_candidates tests/test_data_trust.py::test_unknown_lab_subject_still_errors
# The remaining commands ran from the engine worktree.
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_data_trust.py tests/test_slice1_offerings.py tests/test_lab_jurisdiction.py tests/test_architecture_facts.py tests/test_decision_router_config.py
MODELSPEC_ENGINE=$PWD PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m scripts.data_trust data --data-dir .scratch/model-378-followup/data-main --summary-only --date 2026-10-13
MODELSPEC_ENGINE=$PWD PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m scripts.data_trust data --data-dir .scratch/model-378-final-audit/data-main --summary-only --date 2026-10-14
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
TZ=UTC PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_agent_ready.py::test_built_tree_passes_surface_lint
TZ=UTC PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
```

Archives came from `git archive` at the recorded engine and data SHAs and were
extracted with Python `tarfile` under `.scratch/model-378-followup` and
`.scratch/model-378-final-audit`, outside `docs`. The old `docs/evidence/g2-ios/.model-378-exec` scratch was deleted and
never committed. The temporary archives and replay directories were also removed.
The historical results and commands below describe the earlier finish run.
Their old scratch paths no longer exist. The audit sampled zero claims and does
not establish sampled accuracy. PR #734 remains draft; its body was not changed.

## Changes and contract

The governance invariant now permits Moonshot documents on `kimi.ai` and its
subdomains, including the `platform.kimi.ai` URLs in the private offering data.
A provider missing from `GOVERNANCE_DOMAINS` fails an assertion that names the
provider and the map to update.

The audit calibration explicitly skips compiler records with `kind: hardware`.
The snapshot continues to retain their device, memory, date, and registered
source references. These records are vendor specifications, not independently
verified facts or benchmark evidence. Adding only a `subject` would turn the
crash into invalid fact or benchmark findings. The public decision and snapshot
shapes remain unchanged, and the contract version stays 2.17. The contract's
hardware specification distinction appears under "Architecture and hardware
estimates (MODEL-348)" in `docs/decision-contract.md`.
A read-only reviewer checked this choice against the contract's hardware
specification distinction.

## Red before green

All seven new regression cases ran against the unchanged implementation before
either fix. The final red run exited 1 with `7 failed in 0.72s`.

| Test | Red observation | Green observation |
| --- | --- | --- |
| `test_moonshot_governance_accepts_kimi_documents[kimi.ai]` | `KeyError: 'moonshot'` | Passed in the focused suite. |
| `test_moonshot_governance_accepts_kimi_documents[platform.kimi.ai]` | `KeyError: 'moonshot'` | Passed in the focused suite. |
| `test_moonshot_governance_rejects_other_domains` with three hosts | `KeyError: 'moonshot'` instead of the expected assertion | All three cases passed; misleading prefix and suffix hosts and an unrelated provider remain rejected. |
| `test_unknown_governance_provider_has_a_clear_failure` | `KeyError: 'sambanova'` | Passed; the failure names `sambanova` and `GOVERNANCE_DOMAINS`. |
| `test_calibration_keeps_vendor_hardware_out_of_verified_facts` | `KeyError: 'subject'` at the actual calibration consumer | Passed; the snapshot retains the hardware record, the audit retains exactly two model facts, and invariant errors are zero. |

The private-data governance invariant also failed before the fix, exiting 1
with `KeyError: 'moonshot'` and `1 failed in 0.70s`.
The unchanged offline audit exited 1 and reported:

```text
Served facts: 0; errors: 1; warnings: 1324; models: 1384; offerings: 92
Legacy provenance coverage: 2880/2880 (100.0000%)
```

The focused green run exited 0:

```text
127 passed, 2 skipped in 11.03s
```

The offering and router suites on the private-data overlay exited 0:

```text
31 passed, 2 skipped in 3.58s
```

The private data repo's MODEL-209 identifier admission and retained-byte
verification tests also exited 0:

```text
19 passed in 54.11s
```

Their first run rejected the verification overlay's symlinked retained-copy
directory. That run exited 1 with `1 failed, 10 passed, 8 errors in 50.28s`.
The isolated overlay was corrected to contain physical copies of `research/`,
and the unchanged tests passed on rerun. No reader guard was changed.

The two skipped router checks require optional LiteLLM imports that are absent
from this Python environment. The vendored router schema checks passed.

## Historical audit gate before the authorized follow-up

Before the authorized follow-up, patched calibration reached the served
records but exited 1:

```text
Served facts: 5559; errors: 8; warnings: 2803; models: 1384; offerings: 92
Legacy provenance coverage: 3689/473855 (0.7785%)
```

A second run with `--json` confirmed that all eight errors are
`subject_resolves` on `origin.lab_jurisdiction` records.

The private record listing is omitted; only the aggregate findings are recorded.

The compiler correctly inherits these verified lab facts while retaining their
shared lab subjects and record IDs. `scripts/data_trust/invariants.py:130`
then resolved subjects only against models and offerings. The authorized
follow-up adds the separate lab collection and lab resolution, preserving
the original subjects while rejecting unknown labs.
Dropping these facts or adding labs to the model or offering tables would
misrepresent provenance or candidate counts.

`CODEX-EXEC.md` states, "Stay inside the paths the spec names. If you need a
file outside them, stop and report it." The MODEL-378 spec does not name
`scripts/data_trust/invariants.py`, so that additional change was stopped and
reported. That criterion was unmet at the time; the authorized follow-up
above now records the required audit exit code of 0.

## Earlier finish run on 2026-10-13

The finish run started at `3dbc2b66e795053cbc16bf596923bff80cd90625`
on the same worktree and branch. It fetched and merged `origin/main` twice
without conflicts. Both read-only reviews found no implementation defects.

| Revision | SHA |
| --- | --- |
| Original engine base | `629f7533068d2ab2b0f793be2eaa5aea3152ddf6` |
| Starting implementation | `3dbc2b66e795053cbc16bf596923bff80cd90625` |
| First fetched engine `origin/main` | `df8940c64fb321d258015b7742d249c1aa0174e8` |
| First local merge | `b2d89997543365e72fe966c4b7e9d9731aca1e5f` |
| Latest fetched engine `origin/main` | `b5ec02b18d8edffdd8504b0ea7d108367e5903fd` |
| Latest local merge and verification target | `b4e2a964b89438f64691540a95b2139ea1c8a113` |
| Confirmed private-data main | `45cb41c1bfed7112e82402ed52278bfbef6bc3b3` |

`git ls-remote` confirmed the private-data main revision. A fresh archive of
that revision was extracted into
`docs/evidence/g2-ios/.model-378-exec/finish/data-main`.
The finish overlay repeated the earlier preparation with physical copies of
`tests`, `.github`, and `research`. The real private checkout remained unchanged.

The regression replay archived the original engine base into
`finish/pre-fix-engine` and copied the current regression test files into it.
It removed the Moonshot map entry and the provider assertion from the copied
`test_slice1_offerings.py`, so the seven new cases exercised the original code.
The replay reproduced the same `moonshot`, `sambanova`, and `subject` KeyErrors
as the first run.

| Finish check | Exit code | Observed result |
| --- | --- | --- |
| Seven regressions against the original engine | 1 | `7 failed in 0.85s` |
| Focused engine suites | 0 | `127 passed, 2 skipped in 14.25s` |
| Private-data offering and router suites | 0 | `31 passed, 2 skipped in 4.35s` |
| Offline audit summary | 1 | 5,559 served facts, 8 errors, 2,803 warnings, 1,384 models, 92 offerings |
| Offline audit JSON | 1 | Exactly the same eight `subject_resolves` lab-jurisdiction findings described above |
| Full engine suite, `pytest -q -n 4` | 1 | `2 failed, 10417 passed, 23 skipped, 11 warnings in 1845.18s (0:30:45)` |
| Locked web dependency install | 0 | `npm ci` completed under Node `v22.22.3` |
| `@playwright/test` import after install | 0 | Package `1.63.0` imports successfully |
| Social-card and landing suites after dependency setup | 1 | `47 passed, 12 errors in 859.12s (0:14:19)` |
| Web build after dependency setup | 0 | Generated `web/dist/decide.html`, with no tracked file changes |
| Landing browser parametrizations after the web build | 0 | `12 passed in 8.78s` |
| Latest focused engine suites | 0 | `141 passed, 2 skipped in 15.54s` |
| Latest private-data offering and router suites | 0 | `31 passed, 2 skipped in 5.96s` |
| Latest offline audit summary | 1 | 5,559 served facts, 8 errors, 2,803 warnings, 1,384 models, 92 offerings |
| Latest offline audit JSON | 1 | The same eight `subject_resolves` findings on `origin.lab_jurisdiction` described above |
| Full engine suite after setup and latest merge | 0 | `10448 passed, 8 skipped, 11 warnings in 2167.67s (0:36:07)` |

The first finish JSON audit records engine commit
`b2d89997543365e72fe966c4b7e9d9731aca1e5f`. Its raw JSON was stored in local
scratch, later deleted, and was never included in this public report.
Hardware no longer crashed calibration, but the lab-subject defect still
prevented audit exit code 0 during that earlier run.

During the earlier run, the executor reported the same path restriction in `CODEX-EXEC.md` and asked
the user to expand scope to `scripts/data_trust/invariants.py`. No answer had
arrived when this evidence section was prepared. The subject-resolution
invariant was not weakened, and the contract remains version 2.17 with no
public field widening.

The full engine suite failed in
`tests/test_social_cards.py::test_build_emits_every_template_preview_and_card`
and `tests/test_social_cards.py::test_every_frozen_template_card_has_clean_chromium_layout`.
Both failures reported `ERR_MODULE_NOT_FOUND` because
`web/scripts/render-social-cards.mjs` could not import `@playwright/test`.
The initial run inherited Node `v22.23.1`.

The executor restored the prescribed Node `v22.22.3` and reproduced the missing
dependency with a direct import probe. It started `npm ci` with the locked
dependencies in `web`. The install exited 0, and the same import probe then
exited 0. The restored environment uses npm `10.9.8` and `@playwright/test`
`1.63.0`. No tracked dependency or product source changed.

The rerun covered both complete files, `tests/test_social_cards.py` and
`tests/test_landing.py`. Both original social-card failures passed after the
dependency install. Twelve newly enabled parametrizations of
`tests/test_landing.py::test_landing_behaviour_in_browser` failed in fixture
setup with `FileNotFoundError`. The missing file was
`/Users/terbeest/dev/worktrees/model-378/web/dist/decide.html`.
Those browser checks had been skipped while web dependencies were absent.

The web build exited 0, created `web/dist/decide.html`, and changed no tracked
files. The landing browser parametrizations then exited 0 with 12 passed.
No product code change was needed for either setup failure.

A second `git fetch origin main` advanced engine main to
`b5ec02b18d8edffdd8504b0ea7d108367e5903fd`, which includes MODEL-210 from PR
720. The merge produced `b4e2a964b89438f64691540a95b2139ea1c8a113` without
conflicts. The MODEL-378 implementation diff is unchanged. The executor read
main's decision-contract additions, and its version remains 2.17.
Private-data `ls-remote` still confirmed
`45cb41c1bfed7112e82402ed52278bfbef6bc3b3`.

Focused engine checks and private-data offering and router checks passed at the
earlier merge. That offline summary exited 1 with eight errors.
Its legacy provenance coverage is `3689/473855 (0.7785%)`.
The latest JSON audit also exited 1. It records engine commit
`b4e2a964b89438f64691540a95b2139ea1c8a113` and exactly the same eight
lab-subject `subject_resolves` findings on `origin.lab_jurisdiction` described above.
The final full-suite rerun used the prescribed Node PATH at
`b4e2a964b89438f64691540a95b2139ea1c8a113` and exited 0 with
`10448 passed, 8 skipped, 11 warnings in 2167.67s (0:36:07)`.
The initial full-suite setup failures are preserved above. The offline audit's
eight lab-subject errors were the remaining unmet criterion in that earlier run.
The evidence commit SHA will appear in the executor completion line and is
retrievable with the `git log` command at the top of this report.

## Commands and tools

Commands ran from the named worktree unless a `cd` is shown. Test and audit
output was redirected to local scratch files. Each command's status was
captured immediately with `model378_rc=$?`, the output was read, and the shell
returned `exit "$model378_rc"`. No status was inferred through a pipe.

Tool versions were Python 3.14.4, pytest 9.1.1, pytest-xdist 3.8.0,
Pydantic 2.13.5, PyYAML 6.0.3, HTTPX 0.28.1, Git 2.50.1, and GitHub CLI 2.102.0.
The initial finish full suite inherited Node `v22.23.1`. Dependency diagnosis and
setup then used `/Users/terbeest/.nvm/versions/node/v22.22.3/bin`, npm `10.9.8`,
and `@playwright/test` `1.63.0` after the locked install.

Version commands:

```bash
/Users/terbeest/dev/modelspec/.venv/bin/python --version
/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest --version
git --version
gh --version
/Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
import importlib.metadata
for name in ('pytest-xdist', 'pydantic', 'PyYAML', 'httpx'):
    print(f'{name} {importlib.metadata.version(name)}')
PY
```

Private main identification and isolated overlay preparation, all exit 0:

```bash
git -C /Users/terbeest/dev/modelspec-data rev-parse origin/main
git -C /Users/terbeest/dev/modelspec-data ls-remote origin refs/heads/main
/Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
from pathlib import Path
import shutil
import subprocess
import tarfile
from pipeline.data_source import overlay

engine = Path.cwd()
scratch = engine / 'docs/evidence/g2-ios/.model-378-exec/root'
data = scratch / 'data-main'
data.mkdir()
archive = scratch / 'data-main.tar'
with archive.open('wb') as out:
    subprocess.run(['git', '-C', '/Users/terbeest/dev/modelspec-data', 'archive', 'origin/main'], stdout=out, check=True)
with tarfile.open(archive) as contents:
    contents.extractall(data, filter='data')
archive.unlink()
root = overlay(engine, data, scratch / 'overlay')
(root / 'tests').unlink()
shutil.copytree(engine / 'tests', root / 'tests', ignore=shutil.ignore_patterns('__pycache__'))
print(root)
PY
```

Final red regression command, exit 1 before the fixes:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_slice1_offerings.py::test_moonshot_governance_accepts_kimi_documents tests/test_slice1_offerings.py::test_moonshot_governance_rejects_other_domains tests/test_slice1_offerings.py::test_unknown_governance_provider_has_a_clear_failure tests/test_data_trust.py::test_calibration_keeps_vendor_hardware_out_of_verified_facts
```

Private-data red governance command, exit 1 before the map fix:

```bash
export MODELSPEC_ENGINE="$PWD"
cd docs/evidence/g2-ios/.model-378-exec/root/overlay
PYTHONPATH="$MODELSPEC_ENGINE:$PWD" /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_slice1_offerings.py::test_governance_facts_only_use_the_serving_providers_own_documents
```

Focused green command, exit 0:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_slice1_offerings.py tests/test_data_trust.py tests/test_architecture_facts.py tests/test_decision_router_config.py
```

Private-data offering and router command, exit 0:

```bash
cp tests/test_slice1_offerings.py docs/evidence/g2-ios/.model-378-exec/root/overlay/tests/test_slice1_offerings.py
export MODELSPEC_ENGINE="$PWD"
cd docs/evidence/g2-ios/.model-378-exec/root/overlay
PYTHONPATH="$MODELSPEC_ENGINE:$PWD" /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_slice1_offerings.py tests/test_decision_router_config.py
```

Offline audit command, exit 1 before and after the hardware fix:

```bash
MODELSPEC_ENGINE="$PWD" PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m scripts.data_trust data --data-dir docs/evidence/g2-ios/.model-378-exec/root/data-main --summary-only --date 2026-10-13
```

Private identifier and retained-byte tests used the same overlay. The first
preparation and run exited 1; the corrected preparation and rerun exited 0:

```bash
/Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
from pathlib import Path
import shutil
scratch = Path('docs/evidence/g2-ios/.model-378-exec/root')
root = scratch / 'overlay'
(root / '.github').unlink()
shutil.copytree(scratch / 'data-main/.github', root / '.github', ignore=shutil.ignore_patterns('__pycache__'))
PY
export MODELSPEC_ENGINE="$PWD"
cd docs/evidence/g2-ios/.model-378-exec/root/overlay
PYTHONPATH="$MODELSPEC_ENGINE:$PWD" /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q .github/scripts/tests/test_model_209_identifiers.py .github/scripts/tests/test_model_209_verification.py
```

The correction ran from the engine worktree before repeating that test command:

```bash
/Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
from pathlib import Path
import shutil
scratch = Path('docs/evidence/g2-ios/.model-378-exec/root')
root = scratch / 'overlay'
(root / 'research').unlink()
shutil.copytree(scratch / 'data-main/research', root / 'research')
if (root / '.cache').is_symlink():
    (root / '.cache').unlink()
PY
```

Detailed offline audit command, exit 1 with the eight lab findings above:

```bash
MODELSPEC_ENGINE="$PWD" PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m scripts.data_trust data --data-dir docs/evidence/g2-ios/.model-378-exec/root/data-main --json --date 2026-10-13
```

Full engine command for both runs. The finish command exited 1 with the two
social-card failures recorded above:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4
```

### Finish commands

The finish run used the same interpreter and versions described above. These
commands fetched and merged engine main and confirmed private-data main:

```bash
git fetch origin main
git -C /Users/terbeest/dev/modelspec-data ls-remote origin refs/heads/main
git merge origin/main -m 'Merge origin/main for MODEL-378 delivery' -m 'Co-Authored-By: ChatGPT Codex <noreply@openai.com>'
mkdir -p docs/evidence/g2-ios/.model-378-exec/finish
```

The original engine and current regression tests were prepared for replay:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
from pathlib import Path
import shutil
import subprocess
import tarfile
engine = Path.cwd()
scratch = engine / 'docs/evidence/g2-ios/.model-378-exec/finish'
base = scratch / 'pre-fix-engine'
base.mkdir()
archive = scratch / 'pre-fix-engine.tar'
with archive.open('wb') as out:
    subprocess.run(['git', 'archive', '629f7533068d2ab2b0f793be2eaa5aea3152ddf6'], stdout=out, check=True)
with tarfile.open(archive) as contents:
    contents.extractall(base, filter='data')
archive.unlink()
shutil.copy2(engine / 'tests/test_data_trust.py', base / 'tests/test_data_trust.py')
current = (engine / 'tests/test_slice1_offerings.py').read_text()
current = current.replace('    "moonshot": ("kimi.ai",),\n', '')
guard = '''        assert offering.provider in GOVERNANCE_DOMAINS, (
            f"{offering.provider}: add the provider's own document domains to GOVERNANCE_DOMAINS"
        )
'''
assert guard in current
current = current.replace(guard, '')
(base / 'tests/test_slice1_offerings.py').write_text(current)
print(base)
PY
```

The finish data archive and overlay were prepared with physical copies:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
from pathlib import Path
import shutil
import subprocess
import tarfile
from pipeline.data_source import overlay
engine = Path.cwd()
scratch = engine / 'docs/evidence/g2-ios/.model-378-exec/finish'
data = scratch / 'data-main'
data.mkdir()
archive = scratch / 'data-main.tar'
with archive.open('wb') as out:
    subprocess.run(['git', '-C', '/Users/terbeest/dev/modelspec-data', 'archive', '45cb41c1bfed7112e82402ed52278bfbef6bc3b3'], stdout=out, check=True)
with tarfile.open(archive) as contents:
    contents.extractall(data, filter='data')
archive.unlink()
root = overlay(engine, data, scratch / 'overlay')
(root / 'tests').unlink()
shutil.copytree(engine / 'tests', root / 'tests', ignore=shutil.ignore_patterns('__pycache__'))
(root / '.github').unlink()
shutil.copytree(data / '.github', root / '.github')
(root / 'research').unlink()
shutil.copytree(data / 'research', root / 'research')
if (root / '.cache').is_symlink():
    (root / '.cache').unlink()
print(root)
PY
```

The seven-regression command above ran from `finish/pre-fix-engine`, with
output in `../red-regressions.txt`. The focused green command ran from this
worktree, with output in `finish/green-focused.txt`.
The offering and router command ran from the finish overlay:

```bash
export MODELSPEC_ENGINE="/Users/terbeest/dev/worktrees/model-378"
cd docs/evidence/g2-ios/.model-378-exec/finish/overlay
PYTHONPATH="$MODELSPEC_ENGINE:$PWD" /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_slice1_offerings.py tests/test_decision_router_config.py
```

Its output is in `../green-data-offerings-router.txt`. Both finish audits ran
from the engine worktree:

```bash
MODELSPEC_ENGINE="$PWD" PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m scripts.data_trust data --data-dir docs/evidence/g2-ios/.model-378-exec/finish/data-main --summary-only --date 2026-10-13
MODELSPEC_ENGINE="$PWD" PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m scripts.data_trust data --data-dir docs/evidence/g2-ios/.model-378-exec/finish/data-main --json --date 2026-10-13
```

The summary output is in `finish/data-trust.txt`. JSON output and stderr are
in `finish/data-trust-findings.json` and `finish/data-trust-findings.stderr`.
The full-suite command above writes `finish/full-engine.txt`.
Every finish test and audit command captured `model378_rc=$?` immediately,
printed `EXIT_CODE`, read the output, and returned `exit "$model378_rc"`.

After the full-suite failures, the following import probe ran from `web`
under the prescribed Node version. It exited 1 with the same missing-package
error:

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH node --input-type=module -e 'await import("@playwright/test")'
```

The executor completed the locked dependency install from `web` with exit
code 0:

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm ci
```

The same import probe then exited 0. Version checks from `web` reported npm
`10.9.8` and `@playwright/test` `1.63.0`:

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH node --input-type=module -e 'await import("@playwright/test")'
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm --version
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH node -p "require('@playwright/test/package.json').version"
```

The browser suites rerun from the engine worktree exited 1 with 47 passed and
12 fixture errors. Its output is in `finish/green-browser-suites.txt`:

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_social_cards.py tests/test_landing.py
```

The web build ran from `web` and exited 0, with output in
`finish/web-build.txt`:

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH PYTHONPATH=/Users/terbeest/dev/worktrees/model-378 npm run build
```

The landing browser parametrizations ran from the engine worktree and exited
0. Their output is in `finish/green-landing-browser.txt`:

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_landing.py::test_landing_behaviour_in_browser
```

The second main refresh and merge both exited 0:

```bash
git fetch origin main
git -C /Users/terbeest/dev/modelspec-data ls-remote origin refs/heads/main
git merge origin/main -m 'Merge latest origin/main for MODEL-378 verification' -m 'Co-Authored-By: ChatGPT Codex <noreply@openai.com>'
```

The latest focused command adds main's coding-tool regression suite. It exited
0, with output in `finish/green-focused-latest.txt`:

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_slice1_offerings.py tests/test_data_trust.py tests/test_architecture_facts.py tests/test_decision_router_config.py tests/test_decision_coding_tool_open.py
```

The private-data offering and router command above also ran under the
prescribed Node PATH and exited 0. Its output is in
`finish/green-data-offerings-router-latest.txt`. The latest audit repeated the
finish summary command and exited 1, with output in `finish/data-trust-latest.txt`.
These checks use `b4e2a964b89438f64691540a95b2139ea1c8a113`, separate from
the earlier JSON audit at `b2d89997543365e72fe966c4b7e9d9731aca1e5f`.

The latest JSON audit repeats the finish `--json` command at
`b4e2a964b89438f64691540a95b2139ea1c8a113`. It exited 1 and wrote
`finish/data-trust-findings-latest.json` and
`finish/data-trust-findings-latest.stderr`.

The final full-suite rerun ran at the latest merge and exited 0, with output in
`finish/full-engine-repaired.txt`:

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4
```

The open-PR check exited 0 and returned an empty list:

```bash
gh pr list --head sparksandsawdust/model-378-engine --state open --json number,url,isDraft,title
```

Delivery follows the evidence commit. The final push and draft PR outcomes
are recorded in the executor completion output. The prepared PR body explains
the remaining audit gate, notes the data repo's post-merge `.engine-pin` bump,
and ends with
`Executed by ChatGPT Codex (GPT-6.1 Sol ultra); cross-model review pending.`

```bash
git add docs/evidence/g2-ios/MODEL-378-fix.md
git commit -m 'MODEL-378: record finish verification and remaining audit gate' -m 'Co-Authored-By: ChatGPT Codex <noreply@openai.com>'
CI_LOCAL_SKIP=1 git push -u origin sparksandsawdust/model-378-engine
gh pr create --draft --base main --title "MODEL-378: moonshot governance map and hardware record subject" --body-file docs/evidence/g2-ios/.model-378-exec/finish/pr-body.md
```

Additional local checks:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/pytest_shards.py --shard-count 4 --summary
git diff --check
git -C /Users/terbeest/dev/modelspec-data status --short --branch
```

These checks exited 0. The original shard estimates ranged from 3364.562 to
3364.565 seconds. The finish estimates ranged from 3375.126 to 3375.128
seconds. The private checkout remained clean on its existing main commit.

## Limits of observation

No provider API, paid scraper, source refresh, device, or production deployment
ran. The audit used the offline `data` mode and sampled zero claims; it does not
establish sampled accuracy. The finish run exercised `web`'s `npm run build`
and Python site builds through the browser tests. The separate release-chart
check and `web`'s `npm test` were not run. Frozen public data and the private data
checkout were not changed. No production switches, legal text, ranking floors,
or published contract fields changed in the MODEL-378 patch. No WSL gate, SSH,
SCP, or tmux operation ran. All commands started by this executor were awaited
to completion; no separate background process was started.

After the completed engine change merges,
`modelspec-data` needs an `.engine-pin` bump. This executor did not change that
pin or write to Linear. The executor completion output records the delivered
commit SHA and draft PR URL.
