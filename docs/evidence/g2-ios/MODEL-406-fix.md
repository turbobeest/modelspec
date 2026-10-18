# MODEL-406 execution evidence

Execution dates: 2026-10-17 and 2026-10-18. Worktree: `/Users/terbeest/dev/worktrees/model-406`.
Branch: `model-406-agent-bundle-merge`. PR:
<https://github.com/turbobeest/modelspec/pull/817>.

- Base SHA: `0cf4080a72d354295c434206257d089d26b50ed6`.
- First commit, design only: `47d3dede60f685e1aaeb27259c6899722c973702`.
- Round-1 implementation SHA: `03a2c32a548bd94c99f7658b1ed197f0b5cde129`.
- Round-2 implementation SHA: `b7e7e421d9ed00883dc3275ca803e65344d8727e`.
- The delivery commit adds only this evidence. Resolve its full SHA with
  `git log -1 --format=%H -- docs/evidence/g2-ios/MODEL-406-fix.md`.
  The final execution marker reports that delivery SHA.

## Change and preserved checks

The shared JSON renderer sorts `source_hashes` and writes each digest below
its source-path key. The unchanged key lines separate independently changed
digests during a Git merge. Both the CLI bundle and MCP capture use that
renderer. Their parsed data is unchanged, except for the CLI generator's
own hash after editing that generator.

The existing SHA-256 inputs, runtime JSON readers and packaging checks remain
in place. Pytest now also invokes the complete agent-copy freshness check.
The MCP capture freshness assertion includes the exact regeneration command.
No workflow, contract, published prose, frozen data, production switch or
packaging allowlist changed.

The parsed-data comparison against the base commit also exited 0:

```bash
/Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY_COMPARE'
import hashlib
import json
import subprocess
from pathlib import Path
for relative in ('cli/modelspec/agent-bundle.json', 'qa/fixtures/mcp-tools.json'):
    before = json.loads(subprocess.check_output(['git', 'show', f'0cf4080a:{relative}']))
    after = json.loads(Path(relative).read_bytes())
    if relative.startswith('cli/'):
        before['source_hashes']['pipeline/agent_copy.py'] = hashlib.sha256(Path('pipeline/agent_copy.py').read_bytes()).hexdigest()
    assert before == after, relative
    print(relative, 'parsed data preserved; only the CLI generator self-pin changed')
PY_COMPARE
```

## Red-first result

Before changing production code, ran:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_generated_pins.py --tb=short
```

Exit 1:

```text
17 failed, 45 passed in 130.04s (0:02:10)
```

The failures were:

| Test | Red result | Green result |
| --- | --- | --- |
| `test_independent_source_changes_merge_cleanly` | 14 neighboring-source pairs conflicted: 8 CLI pairs and 6 MCP pairs. | All 57 pairs pass, covering all pairs of 9 CLI and 7 MCP pins. |
| `test_generated_pin_files_are_byte_stable` | Both artifacts failed the sorted-key assertion; repeated generation was already byte-stable. | Both generators produce identical bytes on two runs, with sorted pins and the same production serialization. |
| `test_capture_freshness_check_rejects_a_stale_pin` | Staleness was rejected, but the assertion lacked the required regeneration command. | Staleness is rejected with `python -m qa.contracts` in the failure. |

Representative merge failures:

```text
test_independent_source_changes_merge_cleanly[cli/modelspec/agent-bundle.json-pipeline/entity.py-pipeline/pricing.py]
E   AssertionError: Auto-merging cli/modelspec/agent-bundle.json
E     CONFLICT (content): Merge conflict in cli/modelspec/agent-bundle.json
E     Automatic merge failed; fix conflicts and then commit the result.
E   assert 1 == 0

test_independent_source_changes_merge_cleanly[qa/fixtures/mcp-tools.json-mcp/src/server.ts-mcp/src/vocabulary.ts]
E   AssertionError: Auto-merging qa/fixtures/mcp-tools.json
E     CONFLICT (content): Merge conflict in qa/fixtures/mcp-tools.json
E   assert 1 == 0
```

The capture diagnostic failed with `Regex pattern did not match` and
`Expected regex: 'python -m qa.contracts'`. The sorted-key assertion failed
with `assert list(hashes) == sorted(hashes)` for each artifact.

An earlier test-development run was terminated after review found fixture
cleanup issues. Those issues were corrected before the completed red run
above. No production implementation changed before that completed run.

## Green verification

Regenerated in dependency order, each command exited 0:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy write
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m api.worker.openapi
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m qa.contracts
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m api.worker.openapi --check
```

OpenAPI reported `api/worker/openapi.yaml matches the implementation`.
Regeneration changed only the two intended pin files.

Focused command, exit 0:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_generated_pins.py tests/test_agent_copy.py tests/test_agent_harness.py tests/test_agent_guide.py tests/test_decision_link.py tests/test_pypi_packaging.py tests/test_cli_wheel.py tests/test_api_docs.py
```

```text
294 passed, 2 skipped in 181.38s (0:03:01)
```

The 62 new cases include 57 real three-way Git merges in temporary
repositories. Each pair changes actual source bytes, computes the changed
digests and serializes them through the production renderer. The merged
digests must match the merged source bytes, and the remaining JSON payload
must stay unchanged. The separate generator checks run the actual writing
commands twice and compare their output with that renderer.

The negative checks first accept a fresh artifact, then reject a stale CLI
pin, stale MCP pin or changed OpenAPI file. The CLI probe replaces only the
digest bytes, so formatting alone cannot cause its failure.

Installed web dependencies and ran the required full command:

```bash
(cd web && PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm ci)
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH /opt/homebrew/bin/flock /tmp/modelspec-fullsuite.lock env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
```

`npm ci` exited 0. The first locked full run exited 1:

```text
11573 passed, 9 skipped, 11 warnings, 12 errors in 1415.18s (0:23:35)
```

All 12 errors were setup failures in
`tests/test_landing.py::test_landing_behaviour_in_browser`. The fixture
copies `web/dist/decide.html`, which had not been built. The shared traceback
was `FileNotFoundError: .../web/dist/decide.html`. No assertion failed.

Built the missing assets, exit 0, with no tracked source changes:

```bash
(cd web && PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm run build)
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_landing.py -k test_landing_behaviour_in_browser
```

Browser retry exited 0: `12 passed, 21 deselected in 18.45s`.
Repeated the same locked full-suite command after building the assets.
Final locked full-suite result, exit 0:

```text
11585 passed, 9 skipped, 11 warnings in 1254.41s (0:20:54)
```

The 11 warnings report unsigned decision vocabulary in the existing CLI
snapshot and keyed-origin tests.
Test output was redirected to scratch logs; exit codes came directly from
the commands, with no pipeline masking them.

## Package smoke and stale-build rejection

From the worktree root, ran these commands with scratch paths beneath
`docs/evidence/g2-ios/model-406-exec`:

```bash
/Users/terbeest/dev/modelspec/.venv/bin/python -m build --outdir docs/evidence/g2-ios/model-406-exec/dist
/Users/terbeest/dev/modelspec/.venv/bin/python -m venv docs/evidence/g2-ios/model-406-exec/venv
docs/evidence/g2-ios/model-406-exec/venv/bin/python -m pip install docs/evidence/g2-ios/model-406-exec/dist/modelspec_dev-1.0.0-py3-none-any.whl
```

All exited 0. The default build built an sdist, then built the wheel from
that sdist, exercising the hook in both distributions:

```text
Successfully built modelspec_dev-1.0.0.tar.gz and modelspec_dev-1.0.0-py3-none-any.whl
```

Then ran the installed CLI away from the checkout root:

```bash
set -e
model406_repo="$PWD"
model406_smoke="$PWD/docs/evidence/g2-ios/model-406-exec"
mkdir -p "$model406_smoke/run"
unset PYTHONPATH
export MODELSPEC_API_KEY=''
export XDG_CONFIG_HOME="$model406_smoke/config"
cd "$model406_smoke/run"
"$model406_smoke/venv/bin/modelspec" --help > ../installed-help.txt
"$model406_smoke/venv/bin/modelspec" decide --help > ../installed-decide-help.txt
"$model406_smoke/venv/bin/modelspec" help agent --json > ../installed-agent.json
"$model406_smoke/venv/bin/modelspec" key --json > ../installed-key.json
"$model406_smoke/venv/bin/python" "$model406_repo/scripts/package_smoke.py"
"$model406_smoke/venv/bin/python" -c 'from pathlib import Path; import cli.modelspec; import sys; path = Path(cli.modelspec.__file__); assert Path(sys.prefix) in path.parents; print("Loaded installed CLI:", path)'
```

Exit 0:

```text
Installed wheel: offline guidance, key gate, bounded default, explicit fields and hosted response verified.
```

The import-path assertion confirmed the CLI came from the fresh virtual
environment's `site-packages`. The smoke script uses mocked HTTP.

For the negative package probe, extracted the sdist and appended a newline
to its `pipeline/entity.py`, leaving the bundled digest unchanged:

```bash
/Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
from pathlib import Path
import tarfile
root = Path('docs/evidence/g2-ios/model-406-exec')
with tarfile.open(root / 'dist/modelspec_dev-1.0.0.tar.gz') as archive:
    archive.extractall(root / 'stale-sdist', filter='data')
source = root / 'stale-sdist/modelspec_dev-1.0.0/pipeline/entity.py'
source.write_bytes(source.read_bytes() + b'\n')
PY
/Users/terbeest/dev/modelspec/.venv/bin/python -m build --wheel --outdir docs/evidence/g2-ios/model-406-exec/rejected-wheel docs/evidence/g2-ios/model-406-exec/stale-sdist/modelspec_dev-1.0.0
```

The build exited 1 as required:

```text
ValueError: CLI guidance is stale. Run python -m pipeline.agent_copy write.
ERROR Backend subprocess exited when trying to invoke build_wheel
```

## Actual generator branch experiments

In addition to the 57 simulated pin cases, two experiments ran the actual
generators on each branch and again after merging both source edits. Both
merges exited 0 and the merged artifact bytes equaled regeneration against
the merged sources. These used source-only whitespace changes in
`pipeline/entity.py` versus `pipeline/pricing.py`, and `mcp/src/server.ts`
versus `mcp/src/vocabulary.ts`.

Exact command, exit 0:

```bash
PYTHONDONTWRITEBYTECODE=1 /Users/terbeest/dev/modelspec/.venv/bin/python docs/evidence/g2-ios/model-406-audit/actual_generator_merge.py
```

```text
PASS cli/modelspec/agent-bundle.json: merge exit=0; regenerated bytes identical; merged sha256=b36295093964ca671d8ff9a28542fd375baacee2197e1af3d52c30ab4b0343b8; sources=pipeline/entity.py,pipeline/pricing.py
PASS qa/fixtures/mcp-tools.json: merge exit=0; regenerated bytes identical; merged sha256=1f13dab326aa3fa3eb96928ead5920103c77ba3e6c9ddcd71aa961f966c07b51; sources=mcp/src/server.ts,mcp/src/vocabulary.ts
RESULT exit=0; 2/2 actual-generator merge cases passed; temporary repositories removed
```

<details>
<summary>Reproduce the generator branch experiments</summary>

Create `docs/evidence/g2-ios/model-406-audit/`, save the following script as
`actual_generator_merge.py` there, and run the command above from the
worktree root. It owns all writable inputs and outputs, uses branch-local
Python imports, records each command and exit, and removes its temporary
repositories on completion.

```python
"""Reproduce real-generator branch merges without changing the source checkout."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import platform
import shlex
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[4]
SCRATCH = Path(__file__).resolve().parent
CASES = (
    ("cli/modelspec/agent-bundle.json", "pipeline/entity.py", "pipeline/pricing.py"),
    ("qa/fixtures/mcp-tools.json", "mcp/src/server.ts", "mcp/src/vocabulary.ts"),
)
LOG = SCRATCH / "actual_generator_merge.log"


def record(message):
    print(message, flush=True)
    with LOG.open("a", encoding="utf-8") as stream:
        stream.write(message + "\n")


def run(root, *command):
    record(f"cwd={root}\nPYTHONPATH={root} PYTHONDONTWRITEBYTECODE=1 {shlex.join(command)}")
    result = subprocess.run(
        command, cwd=root, capture_output=True, text=True, timeout=180,
        env={**os.environ, "PYTHONPATH": str(root), "PYTHONDONTWRITEBYTECODE": "1"},
    )
    record(f"exit={result.returncode}\n{result.stdout}{result.stderr}".rstrip())
    if result.returncode:
        raise RuntimeError(f"Command failed with exit {result.returncode}")
    return result


def git(root, *args):
    return run(
        root, "git", "-c", "user.name=Generated pins audit",
        "-c", "user.email=pins@example.invalid", "-c", "commit.gpgsign=false",
        "-c", "core.hooksPath=/dev/null", *args,
    )


def prepare(root):
    owned = {
        "pipeline/agent_copy.py", "qa/contracts.py", "mcp/src/agent-copy.json",
        "docs/agents.md", "api/worker/src/agent_guide.py", "site/holding/index.html",
        "cli/modelspec/spec.schema.json", "cli/modelspec/feedback.schema.json",
    }
    for artifact, _, _ in CASES:
        owned.add(artifact)
        owned.update(json.loads((ROOT / artifact).read_text())["source_hashes"])
    for relative in owned:
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)

    def link_inputs(source, target):
        for child in source.iterdir():
            if child.name.startswith(".") or child.name == "__pycache__":
                continue
            destination = target / child.name
            if not destination.exists():
                destination.symlink_to(child, target_is_directory=child.is_dir())
            elif child.is_dir():
                link_inputs(child, destination)

    link_inputs(ROOT, root)


def generate(root, artifact):
    if artifact.startswith("cli/"):
        run(root, sys.executable, "-m", "pipeline.agent_copy", "write")
    else:
        run(root, sys.executable, "-m", "qa.contracts")


def case(root, artifact, first, second):
    prepare(root)
    generate(root, artifact)
    target = root / artifact
    baseline = json.loads(target.read_bytes())
    git(root, "init", "-q", "-b", "base")
    git(root, "add", "--", artifact, first, second)
    git(root, "commit", "-qm", "baseline")
    expected = json.loads(target.read_bytes())
    for branch, source in (("first", first), ("second", second)):
        git(root, "switch", "-qc", branch, "base")
        path = root / source
        path.write_bytes(path.read_bytes() + b"\n")
        generate(root, artifact)
        updated = json.loads(target.read_bytes())
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        assert updated["source_hashes"][source] == digest
        expected["source_hashes"][source] = digest
        assert {k: v for k, v in updated.items() if k != "source_hashes"} == {
            k: v for k, v in baseline.items() if k != "source_hashes"
        }
        git(root, "add", "--", artifact, source)
        git(root, "commit", "-qm", branch)
    git(root, "merge", "--no-edit", "first")
    merged = target.read_bytes()
    assert json.loads(merged) == expected
    generate(root, artifact)
    assert target.read_bytes() == merged, "Merged artifact differs from regenerated merged sources"
    for source in (first, second):
        assert json.loads(merged)["source_hashes"][source] == hashlib.sha256(
            (root / source).read_bytes()
        ).hexdigest()
    tracked = git(root, "ls-files").stdout.splitlines()
    assert set(tracked) == {artifact, first, second}
    git(root, "diff", "--exit-code", "--", artifact, first, second)
    record(f"PASS {artifact}: merge exit=0; regenerated bytes identical; merged sha256="
           f"{hashlib.sha256(merged).hexdigest()}; sources={first},{second}")


def main():
    LOG.write_text("", encoding="utf-8")
    record(f"Command: {shlex.join([sys.executable, str(Path(__file__).resolve())])}")
    record(f"Python {platform.python_version()}")
    run(ROOT, "git", "--version")
    for artifact, first, second in CASES:
        with tempfile.TemporaryDirectory(prefix="actual-merge-", dir=SCRATCH) as directory:
            case(Path(directory), artifact, first, second)
        record(f"Cleaned temporary repository {directory}")
    record("RESULT exit=0; 2/2 actual-generator merge cases passed; temporary repositories removed")


if __name__ == "__main__":
    main()
```

</details>

## Tools and limits of observation

Tool versions: Python 3.14.4, pytest 9.1.1, pytest-xdist 3.8.0, Git 2.50.1,
Node v22.22.3, npm 10.9.8, build 1.6.1, hatchling 1.32.4 in the isolated
build environments, flock 0.4.0 and GitHub CLI 2.102.0.

The baseline focused checks passed before the design commit:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_agent_copy.py tests/test_agent_harness.py -k 'committed_copy or cli_bundle or mcp_capture'
```

Exit 0, `5 passed, 97 deselected in 1.60s`. `git diff --check` also exited 0.

I did not observe a production deployment, a real GitHub merge of two PRs,
or the remote CI outcome. The merge proof uses ordinary local Git without a
custom merge driver. No live provider, device or API probe ran. No Linear
write, workflow edit, automatic regeneration push or merge was performed.
The PR remained a draft at the round-1 handoff for the independent review.

Changes to the same source or overlapping generated content can still
conflict. The one-time format migration may conflict with branches using
the old layout. The tests prove independent digest edits after both
branches adopt the new layout; they do not claim arbitrary source changes
can always merge without review.

## Round 2: bound test generation work

Execution date: 2026-10-18. Starting head:
`30abcadf4ee0696864481a55f0575c2510a8cdd3`.
Merged `origin/main` at `6fdc5baef50a1c198a4a0557dbe2299da5f75090`
without conflicts in merge commit `24529e6603ba40a4e6a8412696b2084bb3aa7088`.
The user reported 62 setup errors from one generator timeout on CI shard
2/4 and identified the separate explanation timing failure as out of scope.

The old module fixture ran both writers twice with a 180-second timeout.
One fixture failure therefore failed setup for all 62 cases. The CLI stale
probe also launched two complete generator checks. The local baseline
passed its assertions but failed the requested 60-second file budget:

```text
pytest exit=0; wall=119.45s; under_60s=False
62 passed in 119.15s (0:01:59)
56.49s setup: test_generated_pin_files_are_byte_stable[cli/modelspec/agent-bundle.json]
54.22s call: test_agent_copy_check_rejects_a_stale_pin
```

The timing wrapper exited 1. It ran the unchanged test file before the
round-2 edits. This reproduced the excessive local runtime, not the
180-second CI timeout itself.

The shared session fixture in `tests/conftest.py` now generates each bundle
once with `render(cli_bundle())` and `render(capture_tools())`. The 57 merge
cases reuse those bytes, edit real source files, calculate the edited file's
SHA-256 using the same expression as the generators, render the new pin,
and retain all merge and payload assertions. The CLI negative probe reuses
the fresh bundle while executing the copied module's real `main(["check"])`
comparison, exit status and diagnostic. All negative probes first accept
fresh artifacts and restore changed files afterward.

`tests/test_generated_pins_integration.py` contains one `perf` test. It
removes each copied output, runs each real writer once with a 600-second
timeout, and compares the resulting bytes with the independent in-process
generation. This preserves the generation stability check. The test restores
its outputs even on failure. Subprocesses disable bytecode writes to the
linked read-only inputs.

The existing CI workflow excludes `perf` from all four parallel shards and
runs it once in a serial job. No workflow change was needed. Moving the
end-to-end test into its own module keeps the complete merge test file
within the requested budget. An intermediate version with the end-to-end
test in the same file passed 63 tests but took 69.88 seconds, so it did not
meet the budget.

Final timing, including pytest startup and all 62 tests in
`tests/test_generated_pins.py`, exited 0:

```text
pytest exit=0; wall=36.36s; under_60s=True
62 passed in 36.15s
27.51s setup: test_generated_pin_files_are_byte_stable[cli/modelspec/agent-bundle.json]
0.27s call: test_agent_copy_check_rejects_a_stale_pin
```

Both timings used this command under a Python wrapper with
`time.monotonic()` around `subprocess.run`, direct exit-code inspection,
and an additional nonzero exit when elapsed time reached 60 seconds:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_generated_pins.py --durations=10
```

Fixture and marker checks, all exit 0:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest --setup-plan -q tests/test_generated_pins.py tests/test_generated_pins_integration.py -k 'byte_stable or real_generators'
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest --collect-only -q -m perf tests/test_generated_pins.py tests/test_generated_pins_integration.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest --collect-only -q -m 'not perf' tests/test_generated_pins.py tests/test_generated_pins_integration.py
```

The setup plan showed one `SETUP S generated_pin_bytes` across both modules.
The `perf` selection collected 1 test and deselected 62; `not perf` collected
62 and deselected 1.

Regenerated after the merge, all exit 0:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy write
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m api.worker.openapi
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m qa.contracts
```

The commands took 90.42, 0.62 and 0.23 seconds respectively. Regeneration
left the tracked artifacts unchanged.

Focused verification command:

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_generated_pins.py tests/test_generated_pins_integration.py tests/test_agent_copy.py tests/test_agent_harness.py tests/test_agent_guide.py tests/test_decision_link.py tests/test_pypi_packaging.py tests/test_cli_wheel.py tests/test_api_docs.py
```

Focused result, exit 0: `295 passed, 2 skipped in 122.54s (0:02:02)`.

Full verification command:

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH /opt/homebrew/bin/flock /tmp/modelspec-fullsuite.lock env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
```

Full result, exit 0:

```text
11652 passed, 9 skipped, 11 warnings in 1400.24s (0:23:20)
```

The command waited for the shared lock before starting. The 11 warnings
were the existing unsigned-vocabulary warnings from the CLI snapshot and
keyed-origin tests. The unrelated explanation timing test passed unchanged.

Rechecked tool versions: Python 3.14.4, pytest 9.1.1 and Git 2.50.1.
The round-2 fix changes tests and their documentation only. It leaves
`test_none_latency_is_within_noise_of_bypassed_explanation` unchanged.
The user has already marked PR #817 ready for review; this run does not
change its draft state or merge it. Remote CI performance remains unobserved.
