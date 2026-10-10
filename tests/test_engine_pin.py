"""Private writers verify .engine-pin before any engine code runs."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import NamedTuple

import pytest
import yaml

if shutil.which("bash") is None or shutil.which("git") is None:
    pytest.skip("bash or git is missing", allow_module_level=True)

ROOT = Path(__file__).resolve().parents[1]
WRITERS = ROOT / ".github" / "private-writers"
NAMES = (
    "recall-private",
    "release-signals",
    "price-reread",
    "leaderboard-refresh",
    "daily-research",
    "curation-benchmarks",
    "speed-probe",
    "data-trust-audit",
)
ENGINE_JOBS = {
    "recall-private": 1,
    "release-signals": 1,
    "price-reread": 1,
    "leaderboard-refresh": 1,
    "daily-research": 1,
    "curation-benchmarks": 4,
    "speed-probe": 1,
    "data-trust-audit": 1,
}
ENGINE_REPOSITORY = "turbobeest/modelspec"
PIN_REF = "${{ steps.engine_pin.outputs.sha }}"
HEX40 = re.compile(r"^[0-9a-fA-F]{40}$")
CONFIRM = "Confirm the engine checkout is the verified pin"
DOWNGRADE = "Refuse an engine pin older than the base branch pin"
DESCEND = "Refuse an engine pin that does not descend from the default branch pin"


class LocalEngine(NamedTuple):
    url: str
    ancestor: str
    tip: str
    side: str


def _document(name: str) -> dict:
    return yaml.safe_load((WRITERS / f"{name}.yml").read_text(encoding="utf-8"))


def _engine_jobs(document: dict) -> list[dict]:
    matched = [
        job
        for job in document["jobs"].values()
        if any(
            (step.get("with") or {}).get("repository") == ENGINE_REPOSITORY
            for step in job.get("steps") or []
        )
    ]
    assert matched
    return matched


def _engine_job(document: dict) -> dict:
    matched = _engine_jobs(document)
    assert len(matched) == 1
    return matched[0]


def _all_steps(document: dict) -> list[dict]:
    steps: list[dict] = []
    for job in document["jobs"].values():
        steps.extend(job.get("steps") or [])
    return steps


def _index(steps: list[dict], predicate) -> int:
    found = [index for index, step in enumerate(steps) if predicate(step)]
    assert len(found) == 1
    return found[0]


def _pin_step(name: str = NAMES[0]) -> dict:
    steps = _engine_job(_document(name))["steps"]
    return steps[_index(steps, lambda step: step.get("id") == "engine_pin")]


def _git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


@pytest.fixture(scope="module")
def local_engine(tmp_path_factory: pytest.TempPathFactory) -> LocalEngine:
    root = tmp_path_factory.mktemp("engine-pin")
    repo = root / "modelspec"
    repo.mkdir()
    subprocess.run(
        ["git", "-c", "init.defaultBranch=main", "init", str(repo)],
        check=True,
        capture_output=True,
        text=True,
    )
    hooks = root / "hooks"
    hooks.mkdir()
    _git(repo, "config", "user.email", "engine-pin-test@example.com")
    _git(repo, "config", "user.name", "Engine Pin Test")
    _git(repo, "config", "commit.gpgsign", "false")
    _git(repo, "config", "uploadpack.allowFilter", "true")
    _git(repo, "config", "core.hooksPath", str(hooks))
    for message in ("one", "two", "three"):
        _git(repo, "commit", "--allow-empty", "-m", message)
    assert _git(repo, "rev-parse", "--abbrev-ref", "HEAD") == "main"
    ancestor = _git(repo, "rev-parse", "HEAD~2")
    tip = _git(repo, "rev-parse", "HEAD")
    _git(repo, "checkout", "-b", "side")
    _git(repo, "commit", "--allow-empty", "-m", "side")
    side = _git(repo, "rev-parse", "HEAD")
    _git(repo, "checkout", "main")
    return LocalEngine(repo.resolve().as_uri(), ancestor, tip, side)


def _run_pin(
    script: str,
    work: Path,
    engine_repo: str,
    pin: str | None,
    lazy_fetch: bool = False,
):
    data = work / "data"
    data.mkdir()
    if pin is not None:
        (data / ".engine-pin").write_text(pin, encoding="utf-8")
    output = work / "github_output"
    output.write_text("", encoding="utf-8")
    env = os.environ.copy()
    env.update(
        {
            "ENGINE_REPO": engine_repo,
            "RUNNER_TEMP": str(work / "runner"),
            "GITHUB_OUTPUT": str(output),
            "GIT_NO_LAZY_FETCH": "0" if lazy_fetch else "1",
            "GIT_TERMINAL_PROMPT": "0",
        }
    )
    (work / "runner").mkdir()
    completed = subprocess.run(
        ["bash", "-c", script],
        cwd=work,
        env=env,
        capture_output=True,
        text=True,
    )
    return completed, output.read_text(encoding="utf-8")


def _engine_checkout_and_confirm(job: dict) -> tuple[dict, dict]:
    steps = job["steps"]
    engine = _index(
        steps,
        lambda step: (step.get("with") or {}).get("repository") == ENGINE_REPOSITORY,
    )
    return steps[engine], steps[engine + 1]


def test_the_engine_pin_step_is_identical_in_every_writer() -> None:
    steps = [
        step
        for name in NAMES
        for job in _engine_jobs(_document(name))
        for step in job["steps"]
        if step.get("id") == "engine_pin"
    ]
    assert steps
    assert all(step == steps[0] for step in steps)
    assert steps[0]["name"] == "Verify the engine pin is on modelspec main"
    assert steps[0]["working-directory"] == "."
    assert steps[0]["env"] == {
        "ENGINE_REPO": "https://github.com/turbobeest/modelspec.git",
        "GIT_NO_LAZY_FETCH": "1",
    }
    blocks = [
        _engine_checkout_and_confirm(job)
        for name in NAMES
        for job in _engine_jobs(_document(name))
    ]
    assert all(block == blocks[0] for block in blocks)


@pytest.mark.parametrize("name", NAMES)
def test_the_pin_is_verified_before_the_engine_checkout(name: str) -> None:
    document = _document(name)
    jobs = _engine_jobs(document)
    assert len(jobs) == ENGINE_JOBS[name]
    for job in jobs:
        steps = job["steps"]
        data = _index(
            steps,
            lambda step: (
                str(step.get("uses", "")).startswith("actions/checkout")
                and (step.get("with") or {}).get("path") == "data"
            ),
        )
        pin = _index(steps, lambda step: step.get("id") == "engine_pin")
        engine = _index(
            steps,
            lambda step: (step.get("with") or {}).get("repository") == ENGINE_REPOSITORY,
        )
        assert steps[data + 1] is steps[pin]
        between = [step.get("name") for step in steps[pin + 1 : engine]]
        assert between == ([DOWNGRADE] if name == "recall-private" else [])
        assert steps[engine]["with"]["ref"] == PIN_REF
        assert steps[engine]["with"]["path"] == "engine"
        confirm = steps[engine + 1]
        assert confirm["name"] == CONFIRM
        assert confirm["env"]["PIN"] == PIN_REF
        assert confirm["run"] == 'test "$(git -C ../engine rev-parse HEAD)" = "$PIN"'
        assert "working-directory" not in confirm
        assert job["defaults"]["run"]["working-directory"] == "data"
    for step in _all_steps(document):
        ref = (step.get("with") or {}).get("ref")
        repository = (step.get("with") or {}).get("repository")
        if repository == ENGINE_REPOSITORY:
            assert ref == PIN_REF
            assert HEX40.fullmatch(str(ref)) is None


@pytest.mark.parametrize(
    "case",
    [
        "ancestor",
        "tip",
        "side",
        "unknown",
        "short",
        "uppercase",
        "branch",
        "two-lines",
        "empty",
        "missing",
        "leading-space",
        "trailing-space",
        "unreachable",
    ],
)
def test_the_pin_script_accepts_only_a_commit_on_main(
    case: str, tmp_path: Path, local_engine: LocalEngine
) -> None:
    script = _pin_step()["run"]
    ancestor = local_engine.ancestor
    tip = local_engine.tip
    url = local_engine.url
    pin: str | None
    expect_sha: str | None
    if case == "ancestor":
        pin, expect_sha = ancestor + "\n", ancestor
    elif case == "tip":
        pin, expect_sha = tip + "\n", tip
    elif case == "side":
        pin, expect_sha = local_engine.side + "\n", None
    elif case == "unknown":
        pin, expect_sha = "ab" * 20 + "\n", None
    elif case == "short":
        pin, expect_sha = ancestor[:12] + "\n", None
    elif case == "uppercase":
        pin, expect_sha = ancestor.upper() + "\n", None
    elif case == "branch":
        pin, expect_sha = "main\n", None
    elif case == "two-lines":
        pin, expect_sha = ancestor + "\n" + tip + "\n", None
    elif case == "empty":
        pin, expect_sha = "", None
    elif case == "missing":
        pin, expect_sha = None, None
    elif case == "leading-space":
        pin, expect_sha = " " + ancestor + "\n", None
    elif case == "trailing-space":
        pin, expect_sha = ancestor + " \n", None
    elif case == "unreachable":
        pin, expect_sha = ancestor + "\n", None
        url = (tmp_path / "missing-engine").resolve().as_uri()
    else:
        raise AssertionError(case)

    completed, output = _run_pin(script, tmp_path, url, pin)
    detail = f"{case}: exit {completed.returncode}\n{completed.stderr}"
    if expect_sha is None:
        assert completed.returncode != 0, detail
        assert output == "", detail
    else:
        assert completed.returncode == 0, detail
        assert output == f"sha={expect_sha}\n"


def test_a_fetchable_commit_off_main_is_refused_by_ancestry(
    tmp_path: Path, local_engine: LocalEngine
) -> None:
    # GitHub serves any commit in the fork network by SHA. Model that with
    # lazy fetch on, so the side commit reaches the clone and only
    # `merge-base --is-ancestor` can refuse it.
    source = Path(local_engine.url.removeprefix("file://"))
    _git(source, "config", "uploadpack.allowAnySHA1InWant", "true")
    try:
        completed, output = _run_pin(
            _pin_step()["run"], tmp_path, local_engine.url, local_engine.side + "\n", True
        )
        clone = tmp_path / "runner" / "engine-pin-check"
        fetched = subprocess.run(
            ["git", "-C", str(clone), "cat-file", "-e", local_engine.side + "^{commit}"],
            env={**os.environ, "GIT_NO_LAZY_FETCH": "1"},
        )
    finally:
        _git(source, "config", "--unset", "uploadpack.allowAnySHA1InWant")
    assert fetched.returncode == 0, "the side commit never reached the clone"
    assert completed.returncode != 0
    assert "not a commit on modelspec main" in completed.stdout
    assert output == ""


def _downgrade_step() -> dict:
    steps = _engine_job(_document("recall-private"))["steps"]
    return steps[_index(steps, lambda step: step.get("name") == DOWNGRADE)]


def test_the_downgrade_check_runs_only_on_pull_requests() -> None:
    step = _downgrade_step()
    assert step["if"] == "github.event_name == 'pull_request'"
    assert step["env"]["BASE_SHA"] == "${{ github.event.pull_request.base.sha }}"
    assert step["env"]["PIN"] == PIN_REF


@pytest.mark.parametrize(
    "case,base_pin,head_pin,passes",
    [
        ("bump", "ancestor", "tip", True),
        ("same", "tip", "tip", True),
        ("downgrade", "tip", "ancestor", False),
        ("first-pin", None, "tip", True),
        ("bad-base-pin", "main", "tip", False),
    ],
)
def test_a_pull_request_cannot_move_the_pin_backwards(
    case: str,
    base_pin: str | None,
    head_pin: str,
    passes: bool,
    tmp_path: Path,
    local_engine: LocalEngine,
) -> None:
    shas = {"ancestor": local_engine.ancestor, "tip": local_engine.tip, "main": "main"}
    data = tmp_path / "data"
    data.mkdir()
    subprocess.run(["git", "init", "-q", str(data)], check=True)
    _git(data, "config", "user.email", "engine-pin-test@example.com")
    _git(data, "config", "user.name", "Engine Pin Test")
    _git(data, "config", "commit.gpgsign", "false")
    if base_pin is not None:
        (data / ".engine-pin").write_text(shas[base_pin] + "\n", encoding="utf-8")
        _git(data, "add", ".engine-pin")
    _git(data, "commit", "-q", "--allow-empty", "-m", "base")
    base_sha = _git(data, "rev-parse", "HEAD")
    (data / ".engine-pin").write_text(shas[head_pin] + "\n", encoding="utf-8")
    runner = tmp_path / "runner"
    runner.mkdir()
    output = tmp_path / "github_output"
    output.write_text("", encoding="utf-8")
    env = {
        **os.environ,
        "ENGINE_REPO": local_engine.url,
        "RUNNER_TEMP": str(runner),
        "GITHUB_OUTPUT": str(output),
        "GIT_NO_LAZY_FETCH": "1",
        "GIT_TERMINAL_PROMPT": "0",
    }
    verified = subprocess.run(
        ["bash", "-c", _pin_step("recall-private")["run"]],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
    )
    assert verified.returncode == 0, verified.stderr
    completed = subprocess.run(
        ["bash", "-c", _downgrade_step()["run"]],
        cwd=tmp_path,
        env={**env, "BASE_SHA": base_sha, "PIN": shas[head_pin]},
        capture_output=True,
        text=True,
    )
    assert (completed.returncode == 0) is passes, f"{case}: {completed.stdout}{completed.stderr}"


def _descend_step() -> dict:
    steps = _engine_job(_document("release-signals"))["steps"]
    return steps[_index(steps, lambda step: step.get("name") == DESCEND)]


def test_the_descent_check_runs_only_on_the_release_signals_process_job() -> None:
    for name in NAMES:
        for job_name, job in _document(name)["jobs"].items():
            matched = [
                index
                for index, step in enumerate(job.get("steps") or [])
                if step.get("name") == DESCEND
            ]
            if name == "release-signals" and job_name == "process":
                assert matched == [
                    _index(job["steps"], lambda step: step.get("name") == CONFIRM) + 1
                ]
                step = job["steps"][matched[0]]
                assert str(job["steps"][matched[0] + 1].get("uses") or "").startswith(
                    "actions/setup-python"
                )
                assert step["working-directory"] == "."
                assert "origin/main:.engine-pin" in step["run"]
                assert 'merge-base --is-ancestor "$base" "$pin"' in step["run"]
                assert 'echo "$GH_TOKEN"' not in step["run"]
                assert "echo $GH_TOKEN" not in step["run"]
            else:
                assert matched == []


def test_release_signals_process_pushes_without_persisted_credentials() -> None:
    job = _engine_job(_document("release-signals"))
    checkout = next(
        step
        for step in job["steps"]
        if str(step.get("uses") or "").startswith("actions/checkout")
        and (step.get("with") or {}).get("path") == "data"
    )
    assert checkout["with"]["persist-credentials"] is False
    push = next(step for step in job["steps"] if "git push" in (step.get("run") or ""))
    assert "http.https://github.com/.extraheader" in push["run"]
    assert "--unset-all http.https://github.com/.extraheader" in push["run"]
    assert 'echo "$GH_TOKEN"' not in push["run"]
    assert "echo $GH_TOKEN" not in push["run"]
    assert push["env"]["GH_TOKEN"] == "${{ secrets.GITHUB_TOKEN }}"


def _data_checkout(tmp_path: Path, main_pin: str, head_pin: str) -> Path:
    work = tmp_path / "work"
    bare = tmp_path / "origin.git"
    data = work / "data"
    work.mkdir()
    subprocess.run(["git", "init", "--bare", "-q", str(bare)], check=True)
    subprocess.run(
        ["git", "-c", "init.defaultBranch=main", "init", "-q", str(data)],
        check=True,
    )
    _git(data, "config", "user.email", "engine-pin-test@example.com")
    _git(data, "config", "user.name", "Engine Pin Test")
    _git(data, "config", "commit.gpgsign", "false")
    (data / ".engine-pin").write_text(main_pin + "\n", encoding="utf-8")
    _git(data, "add", ".engine-pin")
    _git(data, "commit", "-q", "-m", "pin")
    _git(data, "remote", "add", "origin", str(bare))
    _git(data, "push", "-q", "origin", "HEAD:main")
    _git(data, "fetch", "-q", "origin", "main")
    if head_pin != main_pin:
        (data / ".engine-pin").write_text(head_pin + "\n", encoding="utf-8")
    return work


@pytest.mark.parametrize(
    ("case", "main_pin", "head_pin", "passes"),
    [
        ("equal", "ancestor", "ancestor", True),
        ("descendant", "ancestor", "tip", True),
        ("downgrade", "tip", "ancestor", False),
        ("side", "tip", "side", False),
    ],
)
def test_a_branch_pin_must_descend_from_the_default_branch_pin(
    case: str,
    main_pin: str,
    head_pin: str,
    passes: bool,
    tmp_path: Path,
    local_engine: LocalEngine,
) -> None:
    shas = {
        "ancestor": local_engine.ancestor,
        "tip": local_engine.tip,
        "side": local_engine.side,
    }
    work = _data_checkout(tmp_path, shas[main_pin], shas[head_pin])
    runner = tmp_path / "runner"
    runner.mkdir()
    env = {
        **os.environ,
        "ENGINE_REPO": local_engine.url,
        "RUNNER_TEMP": str(runner),
        "GH_TOKEN": "not-used",
        "GIT_NO_LAZY_FETCH": "1",
        "GIT_TERMINAL_PROMPT": "0",
    }
    completed = subprocess.run(
        ["bash", "-c", _descend_step()["run"]],
        cwd=work,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    detail = f"{case}: exit {completed.returncode}\n{completed.stdout}{completed.stderr}"
    assert (completed.returncode == 0) is passes, detail
    if not passes:
        assert "does not descend from the default branch pin" in completed.stdout, detail
