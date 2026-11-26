"""A different signal for a model with an open card PR attaches to it (MODEL-563).

MODEL-475 moved the re-checks of one signal onto the pull request it opened. A
second signal with a different id can name the same new model while that model's
add-or-identify pull request is still open. Its card is not on main yet, so on
main it resolves `new` again. The workflow acknowledges it onto the open pull
request instead, and its re-checks then run on that pull request's branch.

A pull request is eligible only when its title names the full resolved model id,
it targets main from a writer branch in the same repository, and its changed
files include that model's card. Any failed GitHub read processes the signal
normally.
"""

from __future__ import annotations

import asyncio
import importlib.util
import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest
import yaml

from tests.test_release_signals import _write_card

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "private-writers" / "release-signals.yml"
STEP = "Attach a different signal to the open card PR for its model"
REPO = "turbobeest/modelspec-data"
FIRST_ID = "grok-20260926-123456789"
SECOND_ID = "grok-20260927-987654321"
PR_URL = f"https://github.com/{REPO}/pull/9002"
ISSUE_URL = f"https://github.com/{REPO}/issues/9001"
BRANCH = f"data/release-signal-{FIRST_ID}-initial"
CARD = "models/acme/orbit-2.md"
KEY = "Bearer read-secret"


def _signal(
    signal_id: str = SECOND_ID, model_name: str = "Orbit 2", provider: str = "Acme",
) -> dict[str, object]:
    return {
        "model_name": model_name,
        "provider": provider,
        "first_seen_url": "https://x.com/acme/status/987654321",
        "timestamp": "2026-09-27T08:00:00Z",
        "confidence": 0.9,
        "signal_id": signal_id,
    }


def _open_pr(
    number: int = 9002, *, title: str = "data: add or identify acme/orbit-2 (MODEL-113)",
    base: str = "main", head: str = BRANCH, repo: str | None = REPO, url: str | None = None,
) -> dict[str, object]:
    """One open pull request as the REST `pulls` list returns it."""
    return {
        "number": number,
        "html_url": url or f"https://github.com/{REPO}/pull/{number}",
        "title": title,
        "base": {"ref": base},
        "head": {"ref": head, "repo": {"full_name": repo} if repo else None},
    }


def _steps() -> list[dict]:
    workflow = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    return workflow["jobs"]["process"]["steps"]


def _step(name: str) -> dict:
    return next(step for step in _steps() if step.get("name") == name)


def _engine_root(tmp_path: Path) -> None:
    """main: Orbit 1 of two labs. Orbit 2 is drafted on the open PR's branch, not here."""
    _write_card(tmp_path / "engine", "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    _write_card(
        tmp_path / "engine", "another-org", "orbit-1", display="Orbit 1", version="orbit-1",
    )


def _tools(
    tmp_path: Path, pages: list[list[dict]], files: dict[int, list[list[str]]],
) -> Path:
    """An offline `gh api --paginate` that applies `--jq` to every page, like gh."""
    stub = tmp_path / "bin"
    stub.mkdir(exist_ok=True)
    fixtures = tmp_path / "gh-fixtures"
    fixtures.mkdir(exist_ok=True)
    for index, page in enumerate(pages):
        (fixtures / f"pulls-{index:02d}.json").write_text(json.dumps(page), encoding="utf-8")
    for number, file_pages in files.items():
        for index, page in enumerate(file_pages):
            (fixtures / f"files-{number}-{index:02d}.json").write_text(
                json.dumps([{"filename": name} for name in page]), encoding="utf-8",
            )
    (stub / "gh").write_text(
        "#!/bin/bash\n"
        "printf '%s\\n' \"$*\" >> \"$RUNNER_TEMP/gh-calls\"\n"
        "fixtures=\"$RUNNER_TEMP/gh-fixtures\"\n"
        "case \"$1 $2\" in\n"
        "  'pr comment') [ -z \"${GH_COMMENT_FAILS:-}\" ]; exit ;;\n"
        "  'api --paginate') ;;\n"
        "  *) exit 3 ;;\n"
        "esac\n"
        "path=\"$3\"; filter=\"$5\"\n"
        "[ \"$4\" = --jq ] || exit 4\n"
        "if [[ \"$path\" == \"repos/$GH_REPO/pulls?\"* ]]; then\n"
        "  [ -z \"${GH_LIST_FAILS:-}\" ] || exit 1\n"
        "  pattern=\"pulls-*.json\"\n"
        "elif [[ \"$path\" =~ ^repos/$GH_REPO/pulls/([0-9]+)/files\\? ]]; then\n"
        "  [ -z \"${GH_FILES_FAILS:-}\" ] || exit 1\n"
        "  pattern=\"files-${BASH_REMATCH[1]}-*.json\"\n"
        "else\n"
        "  exit 5\n"
        "fi\n"
        "for page in $(ls \"$fixtures\" | grep -x \"${pattern//\\*/.*}\" | sort); do\n"
        "  jq -c \"$filter\" \"$fixtures/$page\" | jq -r 'if type == \"string\" then . else tojson end'\n"
        "done\n",
        encoding="utf-8",
    )
    (stub / "curl").write_text(
        "#!/bin/bash\n"
        "while [ $# -gt 0 ]; do\n"
        "  if [ \"$1\" = --data-binary ]; then cp \"${2#@}\" \"$RUNNER_TEMP/posted.json\"; fi\n"
        "  shift\n"
        "done\n",
        encoding="utf-8",
    )
    # The runner's python sees the engine; `-I` would hide PYTHONPATH here.
    (stub / "python").write_text(
        "#!/bin/sh\n"
        "[ \"$1\" = -I ] && shift\n"
        f"PYTHONPATH={ROOT} exec {sys.executable} \"$@\"\n",
        encoding="utf-8",
    )
    for name in ("gh", "curl", "python"):
        (stub / name).chmod(0o755)
    return stub


def _run(
    step: dict, tmp_path: Path, env: dict[str, str], *,
    pages: list[list[dict]] | None = None, files: dict[int, list[list[str]]] | None = None,
) -> tuple[subprocess.CompletedProcess[str], dict[str, str]]:
    output = tmp_path / "github-output"
    output.write_text("", encoding="utf-8")
    done = subprocess.run(
        ["bash", "-e", "-o", "pipefail", "-c", step["run"]],
        cwd=tmp_path, capture_output=True, text=True, check=False,
        env=os.environ | {
            "RUNNER_TEMP": str(tmp_path),
            "GITHUB_WORKSPACE": str(tmp_path),
            "GITHUB_OUTPUT": str(output),
            "GITHUB_STEP_SUMMARY": str(tmp_path / "summary.md"),
            "GH_TOKEN": "offline-fixture",
            "GH_REPO": REPO,
            "PATH": os.pathsep.join(
                (str(_tools(tmp_path, pages or [], files or {})), os.environ["PATH"])
            ),
        } | env,
    )
    outputs = dict(
        line.split("=", 1) for line in output.read_text(encoding="utf-8").splitlines() if line
    )
    return done, outputs


def _pending(tmp_path: Path, payload: dict) -> None:
    (tmp_path / "pending.json").write_text(json.dumps(payload), encoding="utf-8")


def _attach(
    tmp_path: Path, *, pages: list[list[dict]], files: dict[int, list[list[str]]] | None = None,
    recheck_day: int = 0, signal_id: str = SECOND_ID, env: dict[str, str] | None = None,
) -> tuple[subprocess.CompletedProcess[str], dict[str, str]]:
    return _run(_step(STEP), tmp_path, {
        "SIGNAL_ID": signal_id, "RECHECK_DAY": str(recheck_day),
    } | (env or {}), pages=pages, files=files if files is not None else {9002: [[CARD]]})


def _calls(tmp_path: Path) -> list[str]:
    path = tmp_path / "gh-calls"
    return path.read_text(encoding="utf-8").splitlines() if path.exists() else []


def _assert_not_attached(tmp_path: Path, done, outputs) -> None:
    assert done.returncode == 0, done.stderr
    assert outputs == {}
    assert not (tmp_path / "result.json").exists()
    assert not [call for call in _calls(tmp_path) if call.startswith("pr comment")]


@pytest.fixture
def service():
    spec = importlib.util.spec_from_file_location(
        "modelspec_attach_signals_service",
        ROOT / "api" / "worker" / "src" / "signals_service.py",
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class KV:
    def __init__(self) -> None:
        self.rows: dict[str, str] = {}

    async def get(self, key: str) -> str | None:
        return self.rows.get(key)

    async def put(self, key: str, value: str, *, expiration_ttl: int | None = None) -> None:
        self.rows[key] = value

    async def delete(self, key: str) -> None:
        self.rows.pop(key, None)

    async def list(self, options: dict | None = None):
        prefix = (options or {}).get("prefix", "")
        return {"keys": [{"name": key} for key in sorted(self.rows) if key.startswith(prefix)]}


def test_the_attach_step_runs_only_for_a_work_item_with_no_open_pull_request() -> None:
    names = [step.get("name") for step in _steps()]
    attach = names.index(STEP)
    assert names.index("Download the pending-work snapshot") < attach
    assert names.index("Install pipeline dependencies") < attach
    assert attach < names.index("Preserve the mechanically checked baseline")
    step = _step(STEP)
    assert step["id"] == "attach"
    assert step["if"] == (
        "steps.recheck.outputs.mode == 'initial' || steps.recheck.outputs.mode == 'unlinked'"
    )
    # An attached signal drafts nothing; its acknowledgement names the open PR.
    assert _step("Process one isolated work item")["if"] == "steps.attach.outputs.pr_url == ''"
    ack = _step("Acknowledge the signal and schedule its 1, 7, and 30 day re-checks")
    assert ack["env"]["RESULT_URL"] == (
        "${{ steps.pr.outputs.url || steps.closed_pr.outputs.url || "
        "steps.attach.outputs.pr_url || matrix.work.pr_url || '' }}"
    )
    # No new permission or secret: the job already writes pull requests.
    assert step["env"]["GH_TOKEN"] == "${{ secrets.GITHUB_TOKEN }}"
    # Every page of the open list, and every page of each candidate's files.
    assert "gh api --paginate" in step["run"]
    assert "base=main" in step["run"]
    assert "/files?per_page=100" in step["run"]
    # Exact filenames: each one is compared as a whole JSON string.
    assert "--jq '.[].filename | tojson'" in step["run"]
    assert 'grep -Fxq -- "$card_json"' in step["run"]


def test_a_second_signal_for_a_model_with_an_open_card_pr_attaches_and_reaches_the_worker(
    service, tmp_path: Path,
) -> None:
    _engine_root(tmp_path)
    kv = KV()
    kv.rows[service.PENDING_PREFIX + SECOND_ID] = json.dumps(_signal(), sort_keys=True)
    pending = asyncio.run(service.pending(
        authorization=KEY, read_key="read-secret", kv=kv, today=date(2026, 9, 27),
    )).body
    _pending(tmp_path, pending)

    done, outputs = _attach(tmp_path, pages=[[
        _open_pr(9100, title="data: add or identify acme/orbit-3 (MODEL-113)"),
        _open_pr(),
    ]], files={9002: [["models/acme/orbit-1.md"], [CARD]]})

    assert done.returncode == 0, done.stderr
    assert outputs == {"pr_url": PR_URL}
    result = json.loads((tmp_path / "result.json").read_text(encoding="utf-8"))
    assert (result["status"], result["signal_id"], result["model_id"], result["pr_url"]) == (
        "attached", SECOND_ID, "acme/orbit-2", PR_URL,
    )
    assert result["recheck_day"] is None
    calls = _calls(tmp_path)
    assert calls[0].startswith(f"api --paginate repos/{REPO}/pulls?state=open&base=main")
    # Only the title-matching PR's files are read, through every page.
    assert calls[1].startswith(f"api --paginate repos/{REPO}/pulls/9002/files?per_page=100")
    assert calls[2].startswith(f"pr comment {PR_URL} --body Release signal {SECOND_ID}")
    assert len(calls) == 3

    _run(
        _step("Acknowledge the signal and schedule its 1, 7, and 30 day re-checks"),
        tmp_path, {"RESULT_URL": outputs["pr_url"], "MODELSPEC_SIGNALS_READ_KEY": "read-secret",
                   "SIGNALS_ORIGIN": "https://signals.invalid"},
    )
    posted = json.loads((tmp_path / "posted.json").read_text(encoding="utf-8"))
    assert posted == {"signal_id": SECOND_ID, "result": "attached", "pr_url": PR_URL}
    acknowledged = asyncio.run(service.acknowledge(
        authorization=KEY, read_key="read-secret", kv=kv, payload=posted,
        today=date(2026, 9, 27),
    ))
    assert acknowledged.body["recheck_days"] == [1, 7, 30]
    due = asyncio.run(service.pending(
        authorization=KEY, read_key="read-secret", kv=kv, today=date(2026, 10, 27),
    )).body
    # Every re-check of the second signal runs on the open card PR's branch.
    assert due["signals"] == []
    assert {(row["day"], row["pr_url"]) for row in due["rechecks"]} == {
        (1, PR_URL), (7, PR_URL), (30, PR_URL),
    }


def test_an_unlinked_recheck_attaches_and_keeps_its_day(tmp_path: Path) -> None:
    _engine_root(tmp_path)
    _pending(tmp_path, {"signals": [], "rechecks": [{
        "signal_id": SECOND_ID, "due": "2026-10-04", "day": 7,
        "pr_url": ISSUE_URL, "signal": _signal(),
    }]})

    done, outputs = _attach(tmp_path, pages=[[_open_pr(
        title="ANSWERS REGRESS: data: add or identify acme/orbit-2 (MODEL-113)",
    )]], recheck_day=7)

    assert done.returncode == 0, done.stderr
    assert outputs == {"pr_url": PR_URL}
    result = json.loads((tmp_path / "result.json").read_text(encoding="utf-8"))
    assert (result["recheck_day"], result["recheck_due"]) == (7, "2026-10-04")


def test_another_labs_model_of_the_same_name_never_attaches(tmp_path: Path) -> None:
    """`another-org/orbit-2` is not `acme/orbit-2`, though both are "Orbit 2"."""
    _engine_root(tmp_path)
    _pending(tmp_path, {"signals": [_signal(provider="Another Org")], "rechecks": []})

    done, outputs = _attach(tmp_path, pages=[[_open_pr()]])

    _assert_not_attached(tmp_path, done, outputs)
    # The acme PR's title never matched, so its files were not even read.
    assert [call.split("?")[0] for call in _calls(tmp_path)] == [
        f"api --paginate repos/{REPO}/pulls",
    ]


def test_the_other_lab_attaches_only_to_its_own_card_pr(tmp_path: Path) -> None:
    _engine_root(tmp_path)
    _pending(tmp_path, {"signals": [_signal(provider="Another Org")], "rechecks": []})
    own = _open_pr(9300, title="data: add or identify another-org/orbit-2 (MODEL-113)")

    done, outputs = _attach(
        tmp_path, pages=[[_open_pr(), own]],
        files={9002: [[CARD]], 9300: [["models/another-org/orbit-2.md"]]},
    )

    assert done.returncode == 0, done.stderr
    assert outputs == {"pr_url": f"https://github.com/{REPO}/pull/9300"}


@pytest.mark.parametrize("files", [
    [[]],
    [["models/acme/orbit-1.md", "registry/sources.yaml"]],
    [["models/another-org/orbit-2.md"]],
    [["models/acme/orbit-2.md.bak", "offerings/acme/orbit-2.yaml"]],
    # Lookalikes: a filename that holds the card path on a line of its own.
    [["notes.txt\nmodels/acme/orbit-2.md"]],
    [["models/acme/orbit-2.md\nREADME"]],
    [["models/acme/orbit-2.md "]],
    [["./models/acme/orbit-2.md"]],
])
def test_a_pr_without_the_models_card_file_never_attaches(
    tmp_path: Path, files: list[list[str]],
) -> None:
    _engine_root(tmp_path)
    _pending(tmp_path, {"signals": [_signal()], "rechecks": []})

    done, outputs = _attach(tmp_path, pages=[[_open_pr()]], files={9002: files})

    _assert_not_attached(tmp_path, done, outputs)


@pytest.mark.parametrize("pr", [
    _open_pr(title="data: add or identify acme/orbit-20 (MODEL-113)"),
    _open_pr(title="data: add or identify orbit-2 (MODEL-113)"),
    _open_pr(title="data: refresh acme/orbit-2 release evidence (MODEL-113)"),
    _open_pr(base="data-lag/image"),
    _open_pr(repo="someone-else/modelspec-data"),
    _open_pr(repo=None),
    _open_pr(head="feature/orbit-2"),
    _open_pr(head="data/release-signal-a..b-initial"),
    _open_pr(url="https://github.com/elsewhere/modelspec-data/pull/9002"),
])
def test_a_title_or_branch_match_alone_never_attaches(tmp_path: Path, pr: dict) -> None:
    _engine_root(tmp_path)
    _pending(tmp_path, {"signals": [_signal()], "rechecks": []})

    # The card file is there; every other condition must hold too.
    done, outputs = _attach(tmp_path, pages=[[pr]])

    _assert_not_attached(tmp_path, done, outputs)


@pytest.mark.parametrize("signal_id, model_name", [
    (SECOND_ID, "Orbit 1"),  # the card is on main: the normal re-check updates it
    ("test-20260927-987654321", "Orbit 2"),  # a test signal is ignored downstream
])
def test_a_model_on_main_or_a_test_signal_never_lists_pull_requests(
    tmp_path: Path, signal_id: str, model_name: str,
) -> None:
    _engine_root(tmp_path)
    _pending(tmp_path, {"signals": [_signal(signal_id, model_name)], "rechecks": []})

    done, outputs = _attach(tmp_path, pages=[[_open_pr()]], signal_id=signal_id)

    _assert_not_attached(tmp_path, done, outputs)
    assert _calls(tmp_path) == []


def test_the_oldest_eligible_pr_is_found_on_a_later_page(tmp_path: Path) -> None:
    _engine_root(tmp_path)
    _pending(tmp_path, {"signals": [_signal()], "rechecks": []})
    filler = [
        _open_pr(1000 + n, title=f"data: add or identify acme/other-{n} (MODEL-113)")
        for n in range(100)
    ]
    newer = _open_pr(9200, head="data/release-signal-watch-x-initial")
    # An older title-matching PR that lacks the card is passed over, not chosen.
    older_without_card = _open_pr(8000)

    done, outputs = _attach(
        tmp_path, pages=[filler, [newer, _open_pr(), older_without_card]],
        files={8000: [["registry/sources.yaml"]], 9002: [[CARD]], 9200: [[CARD]]},
    )

    assert done.returncode == 0, done.stderr
    assert outputs == {"pr_url": PR_URL}
    file_reads = [call for call in _calls(tmp_path) if "/files?" in call]
    assert [call.split("/pulls/")[1].split("/")[0] for call in file_reads] == ["8000", "9002"]


@pytest.mark.parametrize("failure", ["GH_LIST_FAILS", "GH_FILES_FAILS"])
def test_a_failed_github_read_processes_the_signal_normally(
    tmp_path: Path, failure: str,
) -> None:
    _engine_root(tmp_path)
    _pending(tmp_path, {"signals": [_signal()], "rechecks": []})

    done, outputs = _attach(tmp_path, pages=[[_open_pr()]], env={failure: "1"})

    _assert_not_attached(tmp_path, done, outputs)
    assert "so the signal is processed normally" in done.stdout


def test_a_failed_comment_still_attaches_the_signal(tmp_path: Path) -> None:
    _engine_root(tmp_path)
    _pending(tmp_path, {"signals": [_signal()], "rechecks": []})

    done, outputs = _attach(
        tmp_path, pages=[[_open_pr()]], env={"GH_COMMENT_FAILS": "1"},
    )

    assert done.returncode == 0, done.stderr
    assert outputs == {"pr_url": PR_URL}
    assert "::warning::The signal is attached" in done.stdout
