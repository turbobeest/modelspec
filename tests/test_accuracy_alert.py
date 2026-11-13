from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from scripts import accuracy_alert

RUN = "https://github.com/turbobeest/modelspec/actions/runs/37426044223"


def _report(status: str, sample: list[dict]) -> dict:
    return {
        "snapshot": "snap_da666e1f901c2821",
        "generated_at": "2026-10-06T06:55:39Z",
        "status": status,
        "layers": [
            {
                "name": "data_fidelity",
                "status": status,
                "gating": True,
                "summary": "Re-read 12 verified values; 1 did not verify.",
                "details": {"sample": sample},
            },
            {
                "name": "frozen_image_engine_recall",
                "status": "pass",
                "gating": False,
                "summary": "All 20 match.",
                "details": [],
            },
        ],
    }


def test_the_alert_publishes_counts_for_values_that_did_not_verify() -> None:
    report = _report(
        "fail",
        [
            {
                "target": "fact:xai/subscription/supergrok#offering.subscription.usage_allowance",
                "outcome": "unreachable",
                "reason": "unreachable:model-173-xai-consumer-pricing#page",
                "source_urls": ["https://x.ai/pricing"],
            },
            {"target": "fact:a#b", "outcome": "verified", "reason": None, "source_urls": []},
            {"target": "fact:c#d", "outcome": "undetermined", "reason": "render_required",
             "source_urls": []},
        ],
    )
    report["layers"][0]["counts"] = {
        "verified": 1, "mismatch": 0, "unreachable": 1, "undetermined": 1,
    }

    text = accuracy_alert.body(report, RUN, output_dir=Path("accuracy-report"))

    assert text == (
        "**Overall: FAIL**\n"
        "\n"
        "| Layer | Status | Gate | Summary |\n"
        "| --- | --- | --- | --- |\n"
        "| data_fidelity | FAIL | yes | failures 1; mismatches 0; unreachable 1; undetermined 1; "
        "over the undetermined limit: no. |\n"
        "| frozen_image_engine_recall | PASS | no | failures 0; mismatches 0; unreachable 0; "
        "undetermined 0; over the undetermined limit: no; "
        "verdicts that differ from the baseline: 0. |\n"
        "\n"
        "The full report is on the machine that ran it, in the output directory "
        "accuracy-report.\n"
        "\n"
        "details are not published; run the nightly profile locally against the private data\n"
        "\n"
        f"Run: {RUN}\n"
    )
    assert "fact:" not in text
    assert "https://x.ai/pricing" not in text


def test_the_public_issue_names_only_the_output_directory(tmp_path: Path) -> None:
    folder = tmp_path / "private-path-sentinel" / "accuracy-report"
    folder.mkdir(parents=True)
    report_path = folder / "accuracy.json"
    report_path.write_text(json.dumps(_report("fail", [])), encoding="utf-8")
    present = tmp_path / "present.md"
    missing = tmp_path / "missing.md"

    assert accuracy_alert.main(
        ["--report", str(report_path), "--run-url", RUN, "--output", str(present)]
    ) == 0
    assert accuracy_alert.main(
        ["--report", str(folder / "missing.json"), "--run-url", RUN, "--output", str(missing)]
    ) == 0

    for text in (present.read_text(encoding="utf-8"), missing.read_text(encoding="utf-8")):
        assert "private-path-sentinel" not in text
        assert str(folder.parent) not in text
        assert (
            "The full report is on the machine that ran it, in the output directory "
            "accuracy-report.\n"
        ) in text
    assert missing.read_text(encoding="utf-8").startswith(
        "the run failed before a report was written\n"
    )


def test_a_run_that_wrote_no_report_still_alerts(tmp_path: Path) -> None:
    out = tmp_path / "body.md"

    assert accuracy_alert.main(
        ["--report", str(tmp_path / "missing.json"), "--run-url", RUN, "--output", str(out)]
    ) == 0
    assert out.read_text() == (
        "the run failed before a report was written\n"
        "\n"
        "The full report is on the machine that ran it, in the output directory "
        f"{tmp_path.name}.\n"
        "\n"
        f"Run: {RUN}\n"
    )


def test_python_is_installed_before_the_private_fetch() -> None:
    workflow = yaml.load(
        Path(".github/workflows/accuracy-nightly.yml").read_text(), Loader=yaml.BaseLoader
    )
    names = [step.get("name") for step in workflow["jobs"]["accuracy"]["steps"]]
    fetch = names.index("Read private verification records")
    assert names.index("Set up Python") < fetch
    assert names.index("Install dependencies") < fetch


def test_the_alert_builder_runs_when_yaml_cannot_be_imported(tmp_path: Path) -> None:
    report = {
        "status": "fail",
        "layers": [{
            "name": "data_fidelity",
            "status": "fail",
            "gating": True,
            "counts": {"mismatch": 1, "unreachable": 0, "undetermined": 0},
            "details": {"sample": [{"target": "fact:yaml-block-sentinel"}]},
        }],
    }
    report_path = tmp_path / "accuracy.json"
    report_path.write_text(json.dumps(report), encoding="utf-8")
    present = tmp_path / "present.md"
    missing = tmp_path / "missing.md"
    driver = tmp_path / "driver.py"
    root = str(Path(__file__).resolve().parents[1])
    driver.write_text(
        "import sys\n"
        "class BlockYaml:\n"
        "    def find_spec(self, fullname, path, target=None):\n"
        "        if fullname == 'yaml' or fullname.startswith('yaml.'):\n"
        "            raise ModuleNotFoundError(fullname)\n"
        "        return None\n"
        "sys.meta_path.insert(0, BlockYaml())\n"
        "try:\n"
        "    import yaml\n"
        "except ModuleNotFoundError:\n"
        "    pass\n"
        "else:\n"
        "    raise SystemExit('yaml imported')\n"
        "from scripts.accuracy_alert import main\n"
        f"present_code = main(['--report', {str(report_path)!r}, '--run-url', {RUN!r},"
        f" '--output', {str(present)!r}])\n"
        f"missing_code = main(['--report', {str(tmp_path / 'no-report.json')!r},"
        f" '--run-url', {RUN!r}, '--output', {str(missing)!r}])\n"
        "if present_code != 0 or missing_code != 0:\n"
        "    raise SystemExit(f'codes {present_code} {missing_code}')\n",
        encoding="utf-8",
    )
    env = os.environ.copy()
    env["PYTHONPATH"] = root
    result = subprocess.run(
        [sys.executable, str(driver)], cwd=root, capture_output=True, text=True, env=env,
    )

    assert result.returncode == 0, result.stderr + result.stdout
    present_text = present.read_text(encoding="utf-8")
    assert "fact:yaml-block-sentinel" not in present_text
    assert "FAIL" in present_text
    assert present_text.endswith(f"Run: {RUN}\n")
    assert missing.read_text(encoding="utf-8") == (
        "the run failed before a report was written\n"
        "\n"
        "The full report is on the machine that ran it, in the output directory "
        f"{tmp_path.name}.\n"
        "\n"
        f"Run: {RUN}\n"
    )


def test_the_alert_omits_failure_transport_status_source_and_copies() -> None:
    report = _report("fail", [{
        "target": "fact:lab/blocked#context", "outcome": "unreachable",
        "reason": "unreachable:source#table", "source_urls": ["https://example.test/source"],
        "sources": [{
            "source_id": "source", "transport": "http", "declared_fetch": "http",
            "http_status": 403, "error_category": "http_error", "copy_ref": None,
            "cited_copy_ref": "sha256:" + "a" * 64,
        }],
    }])
    report["layers"][0]["counts"] = {
        "verified": 0, "mismatch": 0, "unreachable": 1, "undetermined": 0,
    }

    text = accuracy_alert.body(report, RUN)
    assert "FAIL" in text
    assert "unreachable 1" in text
    assert "fact:lab/blocked#context" not in text
    assert "source `source`" not in text
    assert "sha256:" not in text
    assert "https://example.test/source" not in text


def test_main_reads_the_written_report(tmp_path: Path) -> None:
    path = tmp_path / "accuracy.json"
    path.write_text(json.dumps(_report("pass", [])))
    out = tmp_path / "body.md"

    accuracy_alert.main(["--report", str(path), "--run-url", RUN, "--output", str(out)])

    assert "Values that did not verify" not in out.read_text()
    assert out.read_text().endswith(f"Run: {RUN}\n")


def test_the_nightly_opens_and_closes_the_alert_issue() -> None:
    workflow = yaml.load(
        Path(".github/workflows/accuracy-nightly.yml").read_text(), Loader=yaml.BaseLoader
    )
    job = workflow["jobs"]["accuracy"]
    steps = {step.get("name"): step for step in job["steps"]}

    assert job["permissions"]["issues"] == "write"
    alert = steps["Alert the orchestrator"]
    assert alert["if"] == "failure() && github.ref == 'refs/heads/main'"
    assert "scripts/accuracy_alert.py" in alert["run"]
    assert "--label alert" in alert["run"]
    # An empty list must give no number, not "null" (the first alert would fail).
    assert "--jq '.[0].number // empty'" in alert["run"]
    clear = steps["Close the alert after a green night"]
    assert clear["if"] == "success() && github.ref == 'refs/heads/main'"


@pytest.mark.parametrize("list_status,numbers,close_status,expected_status,closed", [
    (42, "", 0, 42, []),
    (0, "", 0, 0, []),
    (0, "11\n22\n", 0, 0, ["11", "22"]),
    (0, "11\n22\n", 43, 43, ["11"]),
], ids=["list-failure", "empty", "closed", "close-failure"])
def test_nightly_close_alert_propagates_command_results(
    tmp_path, list_status, numbers, close_status, expected_status, closed,
):
    import os
    import subprocess

    workflow = yaml.safe_load(Path(".github/workflows/accuracy-nightly.yml").read_text())
    step = next(s for s in workflow["jobs"]["accuracy"]["steps"]
                if s.get("name") == "Close the alert after a green night")
    stub = '''gh() {
      if [ "$1 $2" = "issue list" ]; then
        printf '%s' "$ISSUES"
        return "$LIST_STATUS"
      fi
      if [ "$1 $2" = "issue close" ]; then
        printf '%s\\n' "$3" >> closed
        return "$CLOSE_STATUS"
      fi
      return 99
    }
'''
    result = subprocess.run(
        ["bash", "-e", "-c", stub + step["run"]], cwd=tmp_path, capture_output=True, text=True,
        env=os.environ | {"ISSUES": numbers, "LIST_STATUS": str(list_status),
                          "CLOSE_STATUS": str(close_status), "RUN_URL": "offline"},
    )
    assert result.returncode == expected_status, result.stdout + result.stderr
    calls = tmp_path / "closed"
    assert (calls.read_text().splitlines() if calls.exists() else []) == closed


def test_the_public_issue_lists_mismatch_and_unreachable_counts_only() -> None:
    report = {
        "snapshot": "snap_da666e1f901c2821",
        "generated_at": "2026-10-06T06:55:39Z",
        "status": "fail",
        "layers": [
            {
                "name": "data_fidelity",
                "status": "fail",
                "gating": True,
                "summary": "Re-read 12 verified values; 1 did not verify.",
                "counts": {"verified": 10, "mismatch": 1, "unreachable": 2, "undetermined": 3},
                "details": {"sample": [
                    {
                        "target": "fact:lab/blocked#context",
                        "outcome": "mismatch",
                        "reason": "value_disagreed",
                        "source_urls": ["https://example.test/source"],
                        "sources": [{
                            "source_id": "source",
                            "transport": "http",
                            "http_status": 403,
                            "error_category": "http_error",
                            "cited_copy_ref": "sha256:" + "a" * 64,
                            "copy_ref": "sha256:" + "b" * 64,
                        }],
                    },
                    {
                        "target": "evidence:lab/model#mmlu#1",
                        "outcome": "unreachable",
                        "reason": "unreachable:source#table",
                        "source_urls": ["https://example.test/other"],
                        "sources": [],
                    },
                ]},
            },
        ],
    }

    text = accuracy_alert.body(report, RUN, output_dir=Path("accuracy-report"))

    assert text == (
        "**Overall: FAIL**\n"
        "\n"
        "| Layer | Status | Gate | Summary |\n"
        "| --- | --- | --- | --- |\n"
        "| data_fidelity | FAIL | yes | failures 3; mismatches 1; unreachable 2; undetermined 3; "
        "over the undetermined limit: no. |\n"
        "\n"
        "The full report is on the machine that ran it, in the output directory "
        "accuracy-report.\n"
        "\n"
        "details are not published; run the nightly profile locally against the private data\n"
        "\n"
        f"Run: {RUN}\n"
    )
    assert "fact:lab/blocked#context" not in text
    assert "evidence:lab/model#mmlu#1" not in text
    assert "sha256:" not in text
    assert "https://example.test/source" not in text
    assert "https://example.test/other" not in text


def test_nightly_fetch_does_not_print_the_private_commit_or_the_report(tmp_path: Path) -> None:
    workflow = yaml.load(
        Path(".github/workflows/accuracy-nightly.yml").read_text(), Loader=yaml.BaseLoader
    )
    steps = workflow["jobs"]["accuracy"]["steps"]
    assert not any(
        (step.get("with") or {}).get("repository") == "turbobeest/modelspec-data"
        for step in steps
    )
    fetch = next(step for step in steps if step.get("name") == "Read private verification records")
    run = fetch["run"]
    assert fetch["if"] == "vars.DATA_SPLIT_ENABLED == 'true'"
    assert fetch["env"]["DATA_TOKEN"] == "${{ secrets.MODELSPEC_DATA_TOKEN }}"
    assert "http.extraheader" in run
    assert "echo" not in run
    assert "set -x" not in run and "xtrace" not in run
    git_lines = [line.strip() for line in run.splitlines() if re.search(r"\bgit\b", line)]
    assert git_lines
    for line in git_lines:
        assert ">/dev/null" in line and "2>&1" in line
        assert re.search(r"\b(log|rev-parse)\b", line) is None
    assert "--depth=1" in run or "--depth 1" in run
    assert "refs/heads/main" in run
    for step in steps:
        uses = step.get("uses") or ""
        assert "upload-artifact" not in uses
        assert "upload-pages-artifact" not in uses
        script = step.get("run") or ""
        assert "set -x" not in script and "xtrace" not in script
        assert "GITHUB_STEP_SUMMARY" not in script
        for line in script.splitlines():
            prints = re.search(r"\b(cat|jq|echo|printf)\b", line)
            names_report = re.search(r"accuracy\.(json|md)", line)
            if prints and names_report:
                pytest.fail(line)

    bindir = tmp_path / "bin"
    bindir.mkdir()
    recorded = tmp_path / "git-args"
    git = bindir / "git"
    git.write_text(
        "#!/bin/sh\n"
        f"printf '%s\\n' \"$*\" >> {recorded}\n"
        "cmd=$1\n"
        "if [ \"$cmd\" = \"-C\" ]; then shift 2; cmd=$1; fi\n"
        "while [ \"$cmd\" = \"-c\" ]; do shift 2; cmd=$1; done\n"
        "if [ \"$cmd\" = fetch ]; then exit \"${FETCH_STATUS:-0}\"; fi\n"
        "exit 0\n"
    )
    git.chmod(0o755)
    token = "secret-token-sentinel"
    result = subprocess.run(
        ["bash", "-c", run], cwd=tmp_path, capture_output=True, text=True,
        env=os.environ | {
            "PATH": f"{bindir}:{os.environ.get('PATH', '')}",
            "DATA_TOKEN": token,
            "FETCH_STATUS": "0",
            "GIT_TERMINAL_PROMPT": "0",
        },
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == ""
    assert result.stderr == ""
    assert token not in result.stdout + result.stderr
    log = recorded.read_text()
    assert token not in log
    assert "\nfetch " in f"\n{log}" or log.startswith("fetch ") or " fetch " in log
    assert re.search(r"(^|\s)(log|rev-parse)(\s|$)", log) is None

    failed = subprocess.run(
        ["bash", "-c", run], cwd=tmp_path, capture_output=True, text=True,
        env=os.environ | {
            "PATH": f"{bindir}:{os.environ.get('PATH', '')}",
            "DATA_TOKEN": token,
            "FETCH_STATUS": "7",
            "GIT_TERMINAL_PROMPT": "0",
        },
    )
    assert failed.returncode == 7
    assert failed.stdout == ""
    assert token not in failed.stderr


_NIGHTLY_REVIEW = (
    "this workflow runs in a public repository against private data; "
    "a reviewer must check every output of a changed step"
)

_FETCH_RUN = """\
set -euo pipefail
dest=.accuracy-private
rm -rf "$dest"
mkdir -p "$dest"
git -C "$dest" init -q >/dev/null 2>&1
git -C "$dest" remote add origin "https://github.com/turbobeest/modelspec-data.git" >/dev/null 2>&1
header=$(printf 'x-access-token:%s' "$DATA_TOKEN" | base64 | tr -d '\\n')
""" + (
    'git -C "$dest" -c "http.extraheader=AUTHORIZATION: basic ${header}" '
    "fetch --depth=1 origin '+refs/heads/main:refs/remotes/origin/main' "
    ">/dev/null 2>&1\n"
    'git -C "$dest" checkout --detach --quiet origin/main >/dev/null 2>&1\n'
)

_LAYERS_RUN = """\
stage=()
if [ "$STAGE_FAILURE" = "true" ]; then stage=(--stage-failure); fi
corrections=()
if [ "$DATA_SPLIT_ENABLED" = "true" ]; then
  corrections=(--private-data-root .accuracy-private)
fi
python scripts/accuracy.py --profile nightly --output-dir accuracy-report "${stage[@]}" "${corrections[@]}"
"""

_ALERT_RUN = """\
python scripts/accuracy_alert.py --report accuracy-report/accuracy.json \\
  --run-url "$RUN_URL" --output alert.md
gh label create alert --color B60205 \\
  --description "Read by the orchestrator heartbeat" --force
number=$(gh issue list --label alert --state open \\
  --search 'in:title "Accuracy nightly failed"' --json number --jq '.[0].number // empty')
if [ -n "$number" ]; then
  gh issue comment "$number" --body-file alert.md
else
  gh issue create --title "Accuracy nightly failed" --label alert --body-file alert.md
fi
"""

_CLOSE_RUN = """\
set -o pipefail
gh issue list --label alert --state open \\
  --search 'in:title "Accuracy nightly failed"' --json number --jq '.[].number' |
while read -r number; do
  gh issue close "$number" --comment "Green again: $RUN_URL"
done
"""

# Every step the nightly job may run, and the exact command text of each run block.
_NIGHTLY_STEPS = (
    {
        "name": "Checkout",
        "uses": "actions/checkout@11d5960a326750d5838078e36cf38b85af677262",
    },
    {
        "name": "Set up Python",
        "uses": "actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065",
    },
    {"name": "Install dependencies", "run": "python -m pip install -e '.[dev]'"},
    {"name": "Require the private checkout credential", "run": 'test -n "$DATA_TOKEN"'},
    {"name": "Read private verification records", "run": _FETCH_RUN},
    {"name": "Run network accuracy layers", "run": _LAYERS_RUN},
    {"name": "Alert the orchestrator", "run": _ALERT_RUN},
    {"name": "Close the alert after a green night", "run": _CLOSE_RUN},
)

_UNLISTED_COMMANDS = (
    "git -C .accuracy-private log -1",
    "git -C .accuracy-private rev-parse HEAD",
    "cat .accuracy-private/.git/HEAD",
    "cat accuracy-report/*",
    "head accuracy-report/accuracy.md",
    "gh issue create --body-file accuracy-report/accuracy.md",
    'python -c "print(open(\'accuracy-report/accuracy.md\'))"',
)


def _normalise_run(script: str) -> str:
    return "\n".join(line.rstrip() for line in script.strip("\n").splitlines())


def nightly_allowance_problems(steps) -> list[str]:
    """Allow-list for accuracy-nightly. Any other step or command is a review."""
    pinned = list(_NIGHTLY_STEPS)
    if len(steps) != len(pinned) or [step.get("name") for step in steps] != [
        row["name"] for row in pinned
    ]:
        return [_NIGHTLY_REVIEW]
    problems = []
    for step, row in zip(steps, pinned):
        if step.get("uses") != row.get("uses"):
            problems.append(_NIGHTLY_REVIEW)
        expected = row.get("run")
        actual = step.get("run")
        if expected is None:
            if actual not in (None, ""):
                problems.append(_NIGHTLY_REVIEW)
        elif _normalise_run(actual or "") != _normalise_run(expected):
            problems.append(_NIGHTLY_REVIEW)
    return problems


class _WorkflowLoader(yaml.SafeLoader):
    """Anchors and `<<` merge keys resolve. Scalars stay strings, so `on` is not True.

    BaseLoader already kept `on` as a string and the composer already resolved
    aliases. It left merge keys as a literal `<<` entry. The merge resolver is
    the one SafeLoader rule this loader keeps.
    """


_WorkflowLoader.yaml_implicit_resolvers = {
    "<": list(yaml.SafeLoader.yaml_implicit_resolvers["<"]),
}


def _load_workflow(filename: str) -> dict:
    return yaml.load(
        Path(f".github/workflows/{filename}").read_text(), Loader=_WorkflowLoader
    )


def _nightly_steps() -> list[dict]:
    return _load_workflow("accuracy-nightly.yml")["jobs"]["accuracy"]["steps"]


def test_accuracy_nightly_steps_match_the_allow_list() -> None:
    workflow = _load_workflow("accuracy-nightly.yml")
    assert context_guard_problems("accuracy-nightly.yml", "accuracy", workflow) == []


@pytest.mark.parametrize("command", _UNLISTED_COMMANDS)
def test_an_unlisted_command_fails_the_nightly_allow_list(command: str) -> None:
    steps = deepcopy(_nightly_steps())
    fetch = next(step for step in steps if step["name"] == "Read private verification records")
    fetch["run"] = fetch["run"] + command + "\n"

    problems = nightly_allowance_problems(steps)

    assert problems, _NIGHTLY_REVIEW
    assert problems == [_NIGHTLY_REVIEW]


def test_a_new_nightly_step_fails_the_allow_list() -> None:
    steps = deepcopy(_nightly_steps())
    steps.append({"name": "Show the private commit", "run": "git -C .accuracy-private log -1"})

    assert nightly_allowance_problems(steps) == [_NIGHTLY_REVIEW], _NIGHTLY_REVIEW


def test_a_new_nightly_action_fails_the_allow_list() -> None:
    steps = deepcopy(_nightly_steps())
    steps.append({"name": "Upload the report", "uses": "actions/upload-artifact@v4"})

    assert nightly_allowance_problems(steps) == [_NIGHTLY_REVIEW], _NIGHTLY_REVIEW


# data-lag.yml and rank-api.yml fetch the private repository the same way the
# nightly does. There is no composite action in this repository, so each job
# repeats the snippet. From that fetch to the end of the job, every step is
# pinned: name, uses, id, working-directory, and a hash of run, if, env, and with.
# context_guard_problems also pins the workflow and job fields around those
# steps, and every step of the guarded job, including the ones before the fetch.
_RANK_FETCH_RUN = """\
set -euo pipefail
dest=modelspec-data
rm -rf "$dest"
mkdir -p "$dest"
git -C "$dest" init -q >/dev/null 2>&1
git -C "$dest" remote add origin "https://github.com/turbobeest/modelspec-data.git" >/dev/null 2>&1
header=$(printf 'x-access-token:%s' "$DATA_TOKEN" | base64 | tr -d '\\n')
""" + (
    'git -C "$dest" -c "http.extraheader=AUTHORIZATION: basic ${header}" '
    "fetch --depth=1 origin '+refs/heads/main:refs/remotes/origin/main' "
    ">/dev/null 2>&1\n"
    'git -C "$dest" checkout --detach --quiet origin/main >/dev/null 2>&1\n'
)

_LAG_FETCH_RUN = """\
set -euo pipefail
dest=modelspec-data
rm -rf "$dest"
mkdir -p "$dest"
git -C "$dest" init -q >/dev/null 2>&1
git -C "$dest" remote add origin "https://github.com/turbobeest/modelspec-data.git" >/dev/null 2>&1
header=$(printf 'x-access-token:%s' "$DATA_TOKEN" | base64 | tr -d '\\n')
""" + (
    'git -C "$dest" -c "http.extraheader=AUTHORIZATION: basic ${header}" '
    "fetch origin '+refs/heads/*:refs/remotes/origin/*' "
    ">/dev/null 2>&1\n"
    'git -C "$dest" checkout --detach --quiet origin/main >/dev/null 2>&1\n'
)

_PRIVATE_FETCHES = (
    ("data-lag.yml", "lag", "Read the private data with its history", _LAG_FETCH_RUN, None),
    ("rank-api.yml", "deploy-staging", "Read the private data", _RANK_FETCH_RUN,
     "vars.DATA_SPLIT_ENABLED == 'true' && github.ref == 'refs/heads/main' && "
     "(github.event_name == 'push' || github.event_name == 'workflow_dispatch' || "
     "github.event_name == 'schedule')"),
    ("rank-api.yml", "deploy", "Read the private data", _RANK_FETCH_RUN,
     "vars.DATA_SPLIT_ENABLED == 'true' && github.ref == 'refs/heads/main' && "
     "(github.event_name == 'push' || github.event_name == 'workflow_dispatch' || "
     "github.event_name == 'schedule')"),
)

_PRIVATE_DIR_COMMANDS = (
    "git -C modelspec-data log -1",
    "git -C modelspec-data rev-parse HEAD",
    "cat modelspec-data/models/a.md",
    "head modelspec-data/models/a.md",
    "jq . modelspec-data/x.json",
)

def _workflow_steps(filename: str, job: str) -> list[dict]:
    return _load_workflow(filename)["jobs"][job]["steps"]


_HASHED_STEP_KEYS = {"run", "if", "env", "with"}
_FETCH_NAMES = {
    "data-lag.yml": "Read the private data with its history",
    "rank-api.yml": "Read the private data",
}


def _freeze(value):
    if isinstance(value, dict):
        return tuple((key, _freeze(value[key])) for key in sorted(value))
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


def _step_pin(step: dict) -> tuple:
    """Name, uses, id, and working-directory, plus a hash of run, if, env, and with."""
    pinned = []
    for key in sorted(step):
        if key in _HASHED_STEP_KEYS:
            text = _normalise_run(step[key]) if key == "run" else repr(_freeze(step[key]))
            digest = hashlib.sha256(text.encode()).hexdigest()
            pinned.append((f"{key}_sha256", digest))
        else:
            pinned.append((key, step[key]))
    return tuple(pinned)


def _private_tail(filename: str, steps: list[dict]) -> list[dict] | None:
    name = _FETCH_NAMES.get(filename)
    if name is None:
        return None
    indexes = [index for index, step in enumerate(steps) if step.get("name") == name]
    if len(indexes) != 1:
        return None
    return steps[indexes[0]:]


_PRIVATE_JOB_TAILS = {
    ('data-lag.yml', 'lag'): (
        (
            ('env_sha256', '8976983088cce184bbb41ffd3cadb8edcf7da41809ac8ac6eb9f1368558779a0'),
            ('name', 'Read the private data with its history'),
            ('run_sha256', '1cf5aeb51a4dadaec2275d7367b81b3f1cf12d4ee4cf0d1cf304acfaac28256b'),
        ),
        (
            ('uses', 'actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065'),
            ('with_sha256', 'bea4bc3e67d4faae28bbb7424225e23369fa71676b9fbcd26d984e7ce6a960bd'),
        ),
        (
            ('id', 'lag'),
            ('name', 'Publish the image as of today minus nine months'),
            ('run_sha256', '7502418de50c4f54c20d91ef7a66b22edfce05de5c4ca8eec8a039a421a32681'),
        ),
        (
            ('if_sha256', 'e06dbccd0ce1f95e8cadda83388b9acdf1d1761362cda48a8fe8dda9f570bd75'),
            ('name', 'Open the pull request'),
            ('uses', 'peter-evans/create-pull-request@22a9089034f40e5a961c8808d113e2c98fb63676'),
            ('with_sha256', '13dcfb9261eeae0f8b37e44c6bb211a5fba753b1a2de2e6aacf1039944ba00df'),
        ),
    ),
    ('rank-api.yml', 'deploy-staging'): (
        (
            ('env_sha256', '8976983088cce184bbb41ffd3cadb8edcf7da41809ac8ac6eb9f1368558779a0'),
            ('if_sha256', 'a36c564c97d8e5767258ee1d2d62c2d1870cf789e3b747a8fdc21c211c1548da'),
            ('name', 'Read the private data'),
            ('run_sha256', 'eeb9d387bdf89a7bcaedb2ea273dc18dba85579b9f6628d17a66fba3ba5f6140'),
        ),
        (
            ('uses', 'actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065'),
            ('with_sha256', '0533878eac284b0d887f17074801067043bac0da5e1fd30caab7b3a83217571d'),
        ),
        (
            ('uses', 'astral-sh/setup-uv@d0cc045d04ccac9d8b7881df0226f9e82c39688e'),
            ('with_sha256', '152c8de28c3c497da56a854b15f412a7c116edb16274e5408735aed83891a7aa'),
        ),
        (
            ('uses', 'actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020'),
            ('with_sha256', '6fb296a6aa140e73597d106493abb9b1e5dc166a9b067dd6efe7befcf9ba4491'),
        ),
        (
            ('env_sha256', 'cfdfaeb14593c650faf5aa2420a3dc6e532224f16d091318f46fe46d2d3796e7'),
            ('name', 'Vendor the scorer into the Worker bundle'),
            ('run_sha256', 'b86373d58a9f257ca39a6e99ec1468983325e9a276c75c80c413e1ee2df8920b'),
        ),
        (
            ('env_sha256', '4cc70b1dfc3fcff19a2c015882793e684f1b2c3e1165fcd90c61e22ff574a77e'),
            ('if_sha256', 'c520997cd2844ab801f22bc05e1b1e3f90cc0fd2f314c0798bcd465f0572dc6c'),
            ('name', 'Check private steady bundle memory against 120 MiB'),
            ('run_sha256', '7b0431e32a788c7ff15df75ec931020af30ca14c6c492c5e6430cab497f377d1'),
        ),
        (
            ('name', "Resolve the Worker's Python dependencies"),
            ('run_sha256', 'c01a3e8693bed4bcc29050ac5d7ef1512f99a510850360144d18f1b496b1ae40'),
        ),
        (
            ('name', 'Deploy staging'),
            ('run_sha256', '5961bd0ed7cb08956d495b111f0aa199b6992622a1dabb207100cd36f131c78c'),
            ('working-directory', 'api/worker'),
        ),
        (
            ('name', 'Sync the staging decision snapshot verification key'),
            ('run_sha256', 'dcab67333c1d72e23674af0b63f0e765459e632976c8854f40689b675a2a0322'),
            ('working-directory', 'api/worker'),
        ),
    ),
    ('rank-api.yml', 'deploy'): (
        (
            ('env_sha256', '8976983088cce184bbb41ffd3cadb8edcf7da41809ac8ac6eb9f1368558779a0'),
            ('if_sha256', 'a36c564c97d8e5767258ee1d2d62c2d1870cf789e3b747a8fdc21c211c1548da'),
            ('name', 'Read the private data'),
            ('run_sha256', 'eeb9d387bdf89a7bcaedb2ea273dc18dba85579b9f6628d17a66fba3ba5f6140'),
        ),
        (
            ('uses', 'actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065'),
            ('with_sha256', '0533878eac284b0d887f17074801067043bac0da5e1fd30caab7b3a83217571d'),
        ),
        (
            ('uses', 'astral-sh/setup-uv@d0cc045d04ccac9d8b7881df0226f9e82c39688e'),
            ('with_sha256', '152c8de28c3c497da56a854b15f412a7c116edb16274e5408735aed83891a7aa'),
        ),
        (
            ('uses', 'actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020'),
            ('with_sha256', '6fb296a6aa140e73597d106493abb9b1e5dc166a9b067dd6efe7befcf9ba4491'),
        ),
        (
            ('env_sha256', 'cfdfaeb14593c650faf5aa2420a3dc6e532224f16d091318f46fe46d2d3796e7'),
            ('name', 'Vendor the scorer into the Worker bundle'),
            ('run_sha256', 'b86373d58a9f257ca39a6e99ec1468983325e9a276c75c80c413e1ee2df8920b'),
        ),
        (
            ('env_sha256', '4cc70b1dfc3fcff19a2c015882793e684f1b2c3e1165fcd90c61e22ff574a77e'),
            ('if_sha256', 'c520997cd2844ab801f22bc05e1b1e3f90cc0fd2f314c0798bcd465f0572dc6c'),
            ('name', 'Check private steady bundle memory against 120 MiB'),
            ('run_sha256', '7b0431e32a788c7ff15df75ec931020af30ca14c6c492c5e6430cab497f377d1'),
        ),
        (
            ('name', "Resolve the Worker's Python dependencies"),
            ('run_sha256', 'c01a3e8693bed4bcc29050ac5d7ef1512f99a510850360144d18f1b496b1ae40'),
        ),
        (
            ('name', 'Dependencies for the post-deploy spec probe'),
            ('run_sha256', '6d2ebf8eb8552c869dec8b1fb2b8bca3a4f427f1d5ed3cf40714465a484fcf99'),
        ),
        (
            ('name', 'Deploy'),
            ('run_sha256', '65400d86de8051fa07d870529fbafee01ee5d4f727fb9c2898e3b0d347e7d95c'),
            ('working-directory', 'api/worker'),
        ),
        (
            ('name', 'Sync the decision snapshot verification key'),
            ('run_sha256', 'e36e1488e7278733eab79649ffc94b0c17760c1f9f16f5efa87f0ce27caf578a'),
            ('working-directory', 'api/worker'),
        ),
        (
            ('env_sha256', '973f661e5b10b052db946ba89c40d9e1601a9a08b85c7bf03339d8b5efc4e76b'),
            ('name', 'Smoke-test api.modelspec.dev'),
            ('run_sha256', 'c5c855a7647f13a4a8ee408b01567c1b1cb4c16bbb520a6aa117d33a8ac16da7'),
        ),
        (
            ('name', 'Decision latency smoke (warning only)'),
            ('run_sha256', '231d3e95dc3751abc7c36f7fbf0e90ab1cf906b710fd7aca5388a1404d8ea1fa'),
        ),
    ),
}


def private_fetch_problems(filename: str, job: str, steps: list[dict]) -> list[str]:
    """Allow-list every step from the private fetch through the end of the job."""
    expected = _PRIVATE_JOB_TAILS.get((filename, job))
    tail = _private_tail(filename, steps)
    if expected is None or tail is None or tuple(_step_pin(step) for step in tail) != expected:
        return [_JOB_REVIEW]
    if any(
        (step.get("with") or {}).get("repository") == "turbobeest/modelspec-data"
        for step in steps
    ):
        return [_JOB_REVIEW]
    return []


def test_data_lag_and_rank_private_fetches_match_the_allow_list() -> None:
    problems = [
        f"{filename}:{job}"
        for filename, job, _, _, _ in _PRIVATE_FETCHES
        if context_guard_problems(filename, job, _load_workflow(filename))
    ]
    assert problems == [], _JOB_REVIEW


@pytest.mark.parametrize("command", _PRIVATE_DIR_COMMANDS)
def test_an_unlisted_command_fails_the_private_fetch_allow_list(command: str) -> None:
    filename, job, name, _, _ = _PRIVATE_FETCHES[0]
    steps = deepcopy(_workflow_steps(filename, job))
    fetch = next(step for step in steps if step.get("name") == name)
    fetch["run"] = fetch["run"] + command + "\n"

    problems = private_fetch_problems(filename, job, steps)

    assert problems, _NIGHTLY_REVIEW
    assert problems == [_JOB_REVIEW]


@pytest.mark.parametrize("command", _PRIVATE_DIR_COMMANDS)
def test_a_new_step_that_reads_the_private_directory_fails(command: str) -> None:
    filename, job, _, _, _ = _PRIVATE_FETCHES[0]
    steps = deepcopy(_workflow_steps(filename, job))
    steps.append({"name": "Show private data", "run": command + "\n"})

    problems = private_fetch_problems(filename, job, steps)

    assert problems, _NIGHTLY_REVIEW
    assert problems == [_JOB_REVIEW]


def test_a_new_upload_of_the_private_checkout_fails() -> None:
    filename, job, _, _, _ = _PRIVATE_FETCHES[2]
    steps = deepcopy(_workflow_steps(filename, job))
    steps.append({"name": "Upload the private checkout", "uses": "actions/upload-artifact@v4"})

    problems = private_fetch_problems(filename, job, steps)

    assert problems, _NIGHTLY_REVIEW
    assert problems == [_JOB_REVIEW]


def test_private_fetches_fail_closed_before_publish_or_deploy() -> None:
    lag = _workflow_steps("data-lag.yml", "lag")
    fetch = next(step for step in lag if step.get("name") == "Read the private data with its history")
    publish = next(step for step in lag if step.get("name") == "Publish the image as of today minus nine months")
    assert lag.index(fetch) < lag.index(publish)
    assert not fetch.get("continue-on-error")
    assert "set -euo pipefail" in fetch["run"]
    assert "|| true" not in fetch["run"]
    assert "--depth" not in fetch["run"]
    assert fetch["env"]["DATA_TOKEN"] == "${{ secrets.MODELSPEC_DATA_TOKEN }}"
    assert fetch["env"]["GIT_TERMINAL_PROMPT"] == "0"

    for job_name, deploy_name in (
        ("deploy-staging", "Deploy staging"),
        ("deploy", "Deploy"),
    ):
        steps = _workflow_steps("rank-api.yml", job_name)
        fetch = next(step for step in steps if step.get("name") == "Read the private data")
        vendor = next(step for step in steps if step.get("name") == "Vendor the scorer into the Worker bundle")
        deploy = next(step for step in steps if step.get("name") == deploy_name)
        assert steps.index(fetch) < steps.index(vendor) < steps.index(deploy)
        assert not fetch.get("continue-on-error") and not deploy.get("continue-on-error")
        assert "set -euo pipefail" in fetch["run"]
        assert "|| true" not in fetch["run"]
        assert "--depth=1" in fetch["run"]
        assert "if" not in deploy
        assert fetch["env"]["DATA_TOKEN"] == "${{ secrets.MODELSPEC_DATA_TOKEN }}"


@pytest.mark.parametrize(
    "filename,job,name",
    [(item[0], item[1], item[2]) for item in _PRIVATE_FETCHES],
)
def test_private_fetch_discards_output_and_fails_when_git_fetch_fails(
    filename: str, job: str, name: str, tmp_path: Path,
) -> None:
    fetch = next(step for step in _workflow_steps(filename, job) if step.get("name") == name)
    run = fetch["run"]
    assert "echo" not in run
    assert "set -x" not in run and "xtrace" not in run
    git_lines = [line.strip() for line in run.splitlines() if re.search(r"\bgit\b", line)]
    assert git_lines
    for line in git_lines:
        assert ">/dev/null" in line and "2>&1" in line
        assert re.search(r"\b(log|rev-parse)\b", line) is None

    bindir = tmp_path / "bin"
    bindir.mkdir()
    recorded = tmp_path / "git-args"
    git = bindir / "git"
    git.write_text(
        "#!/bin/sh\n"
        f"printf '%s\\n' \"$*\" >> {recorded}\n"
        "cmd=$1\n"
        "if [ \"$cmd\" = \"-C\" ]; then shift 2; cmd=$1; fi\n"
        "while [ \"$cmd\" = \"-c\" ]; do shift 2; cmd=$1; done\n"
        "if [ \"$cmd\" = fetch ]; then exit \"${FETCH_STATUS:-0}\"; fi\n"
        "exit 0\n"
    )
    git.chmod(0o755)
    token = "secret-token-sentinel"
    result = subprocess.run(
        ["bash", "-c", run], cwd=tmp_path, capture_output=True, text=True,
        env=os.environ | {
            "PATH": f"{bindir}:{os.environ.get('PATH', '')}",
            "DATA_TOKEN": token,
            "FETCH_STATUS": "0",
            "GIT_TERMINAL_PROMPT": "0",
        },
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == ""
    assert result.stderr == ""
    assert token not in result.stdout + result.stderr
    log = recorded.read_text()
    assert token not in log
    assert " fetch " in f" {log}" or "\nfetch " in f"\n{log}"
    assert re.search(r"(^|\s)(log|rev-parse)(\s|$)", log) is None

    failed = subprocess.run(
        ["bash", "-c", run], cwd=tmp_path, capture_output=True, text=True,
        env=os.environ | {
            "PATH": f"{bindir}:{os.environ.get('PATH', '')}",
            "DATA_TOKEN": token,
            "FETCH_STATUS": "7",
            "GIT_TERMINAL_PROMPT": "0",
        },
    )
    assert failed.returncode == 7
    assert failed.stdout == ""
    assert token not in failed.stderr


# From the private fetch to the end of the job, every step is pinned. A deny
# pattern on a few commands misses a dropped redirect, a working-directory, and
# git show / tail / grep.
_JOB_REVIEW = (
    "this job runs in a public repository against private data; "
    "a reviewer must check every output of a changed step"
)


def _run_step(steps: list[dict], filename: str) -> dict:
    """A step after the fetch, so a command edit is not the fetch pin itself."""
    if filename == "data-lag.yml":
        return next(
            step for step in steps
            if (step.get("name") or "").startswith("Publish the image")
        )
    return next(
        step for step in steps
        if step.get("name") == "Vendor the scorer into the Worker bundle"
    )


def _changed_private_steps(case: str, filename: str, steps: list[dict]) -> None:
    if case == "dropped-redirect":
        step = _run_step(steps, filename)
        assert '> "$RUNNER_TEMP/lag-status.json"' in step["run"]
        step["run"] = step["run"].replace('> "$RUNNER_TEMP/lag-status.json"', "", 1)
        return
    if case == "working-directory-git-log":
        steps.append({
            "name": "Inspect the private checkout",
            "working-directory": "modelspec-data",
            "run": "git log\n",
        })
        return
    if case == "git-show":
        step = _run_step(steps, filename)
        step["run"] = step["run"] + "git -C modelspec-data show HEAD\n"
        return
    if case == "tail":
        step = _run_step(steps, filename)
        step["run"] = step["run"] + "tail modelspec-data/data-image.json\n"
        return
    if case == "grep":
        step = _run_step(steps, filename)
        step["run"] = step["run"] + "grep -R . modelspec-data\n"
        return
    if case == "upload":
        steps.append({
            "name": "Upload the private checkout",
            "uses": "actions/upload-artifact@v4",
        })
        return
    raise AssertionError(case)


_PRIVATE_JOB_CHANGES = [
    ("data-lag.yml", "lag", "dropped-redirect"),
    *[
        (filename, job, case)
        for filename, job, _, _, _ in _PRIVATE_FETCHES
        for case in ("working-directory-git-log", "git-show", "tail", "grep", "upload")
    ],
]


@pytest.mark.parametrize("filename,job,case", _PRIVATE_JOB_CHANGES)
def test_a_changed_private_job_step_needs_a_review(filename: str, job: str, case: str) -> None:
    steps = deepcopy(_workflow_steps(filename, job))
    _changed_private_steps(case, filename, steps)

    problems = private_fetch_problems(filename, job, steps)

    assert problems == [_JOB_REVIEW]


# What surrounds a pinned step can change what that step prints while the step
# text stays byte-identical. The same review message as the step allow-list.
_GUARDED_JOBS = (
    ("accuracy-nightly.yml", "accuracy"),
    ("data-lag.yml", "lag"),
    ("rank-api.yml", "deploy-staging"),
    ("rank-api.yml", "deploy"),
)

_SURROUNDING_EDITS = (
    "workflow-shell",
    "job-shell",
    "workflow-workdir",
    "job-workdir",
    "job-git-trace",
    "job-bash-env",
    "workflow-env-git-trace",
    "actions-step-debug",
    "actions-runner-debug",
    "container",
    "services",
    "strategy",
    "runs-on",
    "workflow-permissions",
    "job-permissions",
    "environment",
    "step-shell",
    "step-env",
    "step-if",
    "step-continue-on-error",
    "step-working-directory",
    "checkout-with",
    "uses-tag",
    "job-uses-branch",
    "insert-github-env",
    "insert-bash-env",
    "insert-hooks-path",
    "insert-git-alias",
    "download-artifact",
)


def _review(filename: str) -> str:
    if filename == "accuracy-nightly.yml":
        return _NIGHTLY_REVIEW
    return _JOB_REVIEW


def _private_checkout(filename: str) -> str:
    if filename == "accuracy-nightly.yml":
        return ".accuracy-private"
    return "modelspec-data"


def _fetch_index(filename: str, steps: list[dict]) -> int:
    if filename == "accuracy-nightly.yml":
        name = "Read private verification records"
    elif filename == "data-lag.yml":
        name = "Read the private data with its history"
    else:
        name = "Read the private data"
    return next(index for index, step in enumerate(steps) if step.get("name") == name)


def _checkout_step(steps: list[dict]) -> dict:
    return next(
        step for step in steps
        if str(step.get("uses") or "").startswith("actions/checkout@")
    )


def _apply_surrounding_edit(workflow: dict, filename: str, job: str, edit: str) -> None:
    """Mutate one surrounding field. The pinned step `run` text stays put."""
    body = workflow["jobs"][job]
    steps = body["steps"]
    fetch = steps[_fetch_index(filename, steps)]
    if edit == "workflow-shell":
        workflow.setdefault("defaults", {}).setdefault("run", {})["shell"] = "bash -x {0}"
    elif edit == "job-shell":
        body.setdefault("defaults", {}).setdefault("run", {})["shell"] = "bash -x {0}"
    elif edit == "workflow-workdir":
        workflow.setdefault("defaults", {}).setdefault("run", {})["working-directory"] = (
            _private_checkout(filename)
        )
    elif edit == "job-workdir":
        body.setdefault("defaults", {}).setdefault("run", {})["working-directory"] = (
            _private_checkout(filename)
        )
    elif edit == "job-git-trace":
        body.setdefault("env", {})["GIT_TRACE"] = "1"
    elif edit == "job-bash-env":
        body.setdefault("env", {})["BASH_ENV"] = "/tmp/trace.sh"
    elif edit == "workflow-env-git-trace":
        workflow.setdefault("env", {})["GIT_TRACE"] = "1"
    elif edit == "actions-step-debug":
        workflow.setdefault("env", {})["ACTIONS_STEP_DEBUG"] = "true"
    elif edit == "actions-runner-debug":
        workflow.setdefault("env", {})["ACTIONS_RUNNER_DEBUG"] = "true"
    elif edit == "container":
        body["container"] = "ubuntu:22.04"
    elif edit == "services":
        body["services"] = {"redis": {"image": "redis"}}
    elif edit == "strategy":
        body["strategy"] = {"fail-fast": "true"}
    elif edit == "runs-on":
        body["runs-on"] = "self-hosted"
    elif edit == "workflow-permissions":
        workflow.setdefault("permissions", {})["actions"] = "write"
    elif edit == "job-permissions":
        body.setdefault("permissions", {})["actions"] = "write"
    elif edit == "environment":
        body["environment"] = "staging"
    elif edit == "step-shell":
        fetch["shell"] = "bash -x {0}"
    elif edit == "step-env":
        fetch.setdefault("env", {})["GIT_TRACE"] = "1"
    elif edit == "step-if":
        fetch["if"] = "false"
    elif edit == "step-continue-on-error":
        fetch["continue-on-error"] = "true"
    elif edit == "step-working-directory":
        fetch["working-directory"] = _private_checkout(filename)
    elif edit == "checkout-with":
        _checkout_step(steps).setdefault("with", {})["persist-credentials"] = "true"
    elif edit == "uses-tag":
        _checkout_step(steps)["uses"] = "actions/checkout@v4"
    elif edit == "job-uses-branch":
        # Steps stay byte-identical. A job-level `uses` is not part of the step pin.
        body["uses"] = "turbobeest/modelspec/.github/workflows/build.yml@main"
    elif edit == "insert-github-env":
        steps.insert(_fetch_index(filename, steps), {
            "name": "Export trace",
            "run": 'echo GIT_TRACE=1 >> "$GITHUB_ENV"\n',
        })
    elif edit == "insert-bash-env":
        steps.insert(_fetch_index(filename, steps), {
            "name": "Export bash env",
            "run": 'echo BASH_ENV=/tmp/trace.sh >> "$GITHUB_ENV"\n',
        })
    elif edit == "insert-hooks-path":
        steps.insert(_fetch_index(filename, steps), {
            "name": "Point git hooks at a trace script",
            "run": "git config --global core.hooksPath /tmp/hooks\n",
        })
    elif edit == "insert-git-alias":
        steps.insert(_fetch_index(filename, steps), {
            "name": "Alias git checkout",
            "run": "git config --global alias.checkout 'log -1'\n",
        })
    elif edit == "download-artifact":
        workflow["jobs"]["republish"] = {
            "needs": [job],
            "runs-on": "ubuntu-latest",
            "steps": [{"name": "Download", "uses": "actions/download-artifact@v4"}],
        }
    else:
        raise AssertionError(edit)


_MISSING = "<absent>"
_WORKFLOW_CONTEXT_KEYS = ("env", "defaults", "permissions")
_JOB_CONTEXT_KEYS = (
    "env",
    "defaults",
    "container",
    "services",
    "strategy",
    "runs-on",
    "permissions",
    "environment",
)
# Taken from the unmodified workflow files. A change of env, defaults, shell,
# permissions, or any step of the guarded job moves one of these digests.
_SURROUNDING_PINS = {
    ("accuracy-nightly.yml", "accuracy"):
        "9b57a2fb13509cb6104e832a38cf5f56220d80a0aa96bc0cf333a77e7b2919cb",
    ("data-lag.yml", "lag"):
        "5c852829612beaaf4778fdc64644820a525c16105c8cc36d9720f54a3f7bc9d3",
    ("rank-api.yml", "deploy-staging"):
        "580d64e310d5ea9391fb1d3c9bb99d157919dbc308b26eca4e411cbe675a2817",
    ("rank-api.yml", "deploy"):
        "9c8496dfd092d04a636994767dff6b842d120cf8a03ed9dc908e4d23a695ce6e",
}
_STEP_PINS = {
    ("accuracy-nightly.yml", "accuracy"):
        "8d375eeb7a57b0011c2dd19bf505ea4dcd9b75dc98e2fd63d21aa81ff0bb43e3",
    ("data-lag.yml", "lag"):
        "4073d896920e594663d02fadb66fe4e029259f3436f32ab9f2d95602e1c9f835",
    ("rank-api.yml", "deploy-staging"):
        "3f56082ba0e87ec558d3012580e64873e84bb79422c9cbbb2ab4122df1486f00",
    ("rank-api.yml", "deploy"):
        "06d88e49c7cee954429559d6b242671eb1e1fa7843dd9e2aab00aaf036465e35",
}
_FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
_DOCKER_PIN = re.compile(r"^docker://[^@\s]+@sha256:[0-9a-f]{64}$")


def _picked(mapping: dict, keys: tuple[str, ...]) -> tuple:
    picked = []
    for key in keys:
        if key in mapping:
            picked.append((key, _freeze(mapping[key])))
        else:
            picked.append((key, _MISSING))
    return tuple(picked)


def _surrounding_digest(workflow: dict, job: str) -> str:
    payload = (
        _picked(workflow, _WORKFLOW_CONTEXT_KEYS),
        _picked(workflow["jobs"][job], _JOB_CONTEXT_KEYS),
    )
    return hashlib.sha256(repr(payload).encode()).hexdigest()


def _guarded_steps_digest(steps: list[dict]) -> str:
    payload = tuple(_step_pin(step) for step in steps)
    return hashlib.sha256(repr(payload).encode()).hexdigest()


def _uses_ref_is_pinned(uses: str) -> bool:
    """Full commit SHA. A local `./` action has no ref and moves with this commit."""
    if uses.startswith("./"):
        return True
    if uses.startswith("docker://"):
        return _DOCKER_PIN.fullmatch(uses) is not None
    if "@" not in uses:
        return False
    return _FULL_SHA.fullmatch(uses.rsplit("@", 1)[1]) is not None


def _unpinned_uses(workflow: dict, job: str) -> list[str]:
    body = workflow["jobs"][job]
    found = []
    job_uses = body.get("uses")
    if isinstance(job_uses, str) and not _uses_ref_is_pinned(job_uses):
        found.append(job_uses)
    for step in body.get("steps") or []:
        uses = step.get("uses")
        if isinstance(uses, str) and not _uses_ref_is_pinned(uses):
            found.append(uses)
    return found


def _needs_job(needs, job: str) -> bool:
    if isinstance(needs, str):
        return needs == job
    if isinstance(needs, list):
        return job in needs
    return False


def _step_downloads_artifact(step: dict) -> bool:
    uses = step.get("uses") or ""
    run = step.get("run") or ""
    return (
        "download-artifact" in uses
        or "download-artifact" in run
        or "gh run download" in run
    )


def _later_job_downloads_guarded_artifact(workflow: dict, job: str) -> bool:
    for name, body in workflow.get("jobs", {}).items():
        if name == job or not isinstance(body, dict):
            continue
        if not _needs_job(body.get("needs"), job):
            continue
        for step in body.get("steps") or []:
            if isinstance(step, dict) and _step_downloads_artifact(step):
                return True
    return False


def context_guard_problems(filename: str, job: str, workflow: dict) -> list[str]:
    """Allow-list for one guarded job, including what surrounds its steps."""
    message = _review(filename)
    body = workflow["jobs"][job]
    steps = body.get("steps")
    if not isinstance(steps, list):
        return [message]
    if filename == "accuracy-nightly.yml":
        problems = nightly_allowance_problems(steps)
    else:
        problems = private_fetch_problems(filename, job, steps)
    if problems:
        return problems
    if _surrounding_digest(workflow, job) != _SURROUNDING_PINS[(filename, job)]:
        return [message]
    if _guarded_steps_digest(steps) != _STEP_PINS[(filename, job)]:
        return [message]
    if _unpinned_uses(workflow, job):
        return [message]
    if _later_job_downloads_guarded_artifact(workflow, job):
        return [message]
    return []


def _with_merged_debug_shell(filename: str, job: str) -> dict:
    text = Path(f".github/workflows/{filename}").read_text()
    needle = f"  {job}:\n"
    assert text.count(needle) == 1
    insertion = (
        f"  {job}:\n"
        "    defaults:\n"
        "      run:\n"
        "        <<: *debug-shell\n"
    )
    document = (
        'x-debug: &debug-shell\n  shell: "bash -x {0}"\n'
        + text.replace(needle, insertion, 1)
    )
    return yaml.load(document, Loader=_WorkflowLoader)


@pytest.mark.parametrize("filename", ("accuracy-nightly.yml", "data-lag.yml", "rank-api.yml"))
def test_the_workflow_key_on_stays_a_string(filename: str) -> None:
    workflow = _load_workflow(filename)
    assert "on" in workflow
    assert True not in workflow


@pytest.mark.parametrize("filename,job", _GUARDED_JOBS)
def test_a_merged_debug_shell_is_visible_to_the_guard(filename: str, job: str) -> None:
    workflow = _with_merged_debug_shell(filename, job)
    assert "on" in workflow and True not in workflow
    assert workflow["jobs"][job]["defaults"]["run"]["shell"] == "bash -x {0}"
    assert context_guard_problems(filename, job, workflow) == [_review(filename)]


@pytest.mark.parametrize("filename,job", _GUARDED_JOBS)
@pytest.mark.parametrize("edit", _SURROUNDING_EDITS)
def test_a_private_job_surrounding_edit_needs_a_review(
    filename: str, job: str, edit: str,
) -> None:
    workflow = _load_workflow(filename)
    _apply_surrounding_edit(workflow, filename, job, edit)
    assert context_guard_problems(filename, job, workflow) == [_review(filename)]


@pytest.mark.parametrize("filename,job", _GUARDED_JOBS)
def test_concurrency_and_timeout_minutes_stay_free(filename: str, job: str) -> None:
    workflow = _load_workflow(filename)
    workflow["concurrency"]["group"] = workflow["concurrency"]["group"] + "-edited"
    workflow["jobs"][job]["timeout-minutes"] = "45"
    workflow["jobs"][job]["concurrency"] = {"group": "edited", "cancel-in-progress": "false"}
    assert context_guard_problems(filename, job, workflow) == []


@pytest.mark.parametrize("filename", ("accuracy-nightly.yml", "data-lag.yml", "rank-api.yml"))
def test_a_job_that_does_not_read_the_private_repository_may_change_env(filename: str) -> None:
    workflow = _load_workflow(filename)
    if filename == "rank-api.yml":
        # `bundle` and `memory` never check the private repository out.
        workflow["jobs"]["bundle"].setdefault("env", {})["GIT_TRACE"] = "1"
    else:
        # Those two workflows have no second job. A job added beside the guarded
        # one, with no private fetch, is free to set env.
        workflow["jobs"]["public-report"] = {
            "runs-on": "ubuntu-latest",
            "env": {"GIT_TRACE": "1"},
            "steps": [{"name": "Note", "run": "echo ok\n"}],
        }
    for guarded in (name for workflow_name, name in _GUARDED_JOBS if workflow_name == filename):
        assert context_guard_problems(filename, guarded, workflow) == []


@pytest.mark.parametrize("filename,job", _GUARDED_JOBS)
def test_a_later_job_that_only_needs_the_guarded_job_stays_free(
    filename: str, job: str,
) -> None:
    workflow = _load_workflow(filename)
    workflow["jobs"]["after"] = {
        "needs": [job],
        "runs-on": "ubuntu-latest",
        "steps": [{"name": "Note", "run": "echo done\n"}],
    }
    assert context_guard_problems(filename, job, workflow) == []


@pytest.mark.parametrize(
    "uses,pinned",
    (
        ("actions/checkout@11d5960a326750d5838078e36cf38b85af677262", True),
        ("actions/checkout@v4", False),
        ("actions/checkout@main", False),
        ("actions/checkout@11d5960", False),
        ("actions/checkout", False),
        ("./.github/actions/fetch", True),
        ("docker://alpine:3.20", False),
        ("docker://alpine@sha256:" + ("a" * 64), True),
        ("turbobeest/modelspec/.github/workflows/build.yml@main", False),
        ("turbobeest/modelspec/.github/workflows/build.yml@" + ("ab" * 20), True),
    ),
)
def test_a_uses_ref_needs_a_full_commit_sha(uses: str, pinned: bool) -> None:
    assert _uses_ref_is_pinned(uses) is pinned
