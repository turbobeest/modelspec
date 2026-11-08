"""Archived replay helpers require a supplied revision and still resolve it.

Git revision checks use a real repository. Historical replay work stops at the
first subsequent operation, before retained sources or remote services are used.
MODELSPEC_EVIDENCE_REPLAY_DATA can select an existing read-only scratch clone.
"""

import os
from pathlib import Path
import runpy
import subprocess
import sys
import tarfile

import pytest


ROOT = Path(__file__).resolve().parents[1]
ENV = "MODELSPEC_EXPECTED_DATA_SHA"
SCRIPTS = {
    "sentences": "MODEL-390-engine-sentence-seeds.py",
    "repair-audit": "MODEL-437/round2/acceptance/audit_repaired_view.py",
    "acceptance": "MODEL-437/round2/acceptance/setup_acceptance.py",
    "stage": "MODEL-444/probes/stage_data.py",
    "baseline": "MODEL-439/r2/prepare_baseline.py",
}


class ReachedPostCheck(Exception):
    pass


@pytest.fixture(scope="module")
def replay_repo(tmp_path_factory):
    supplied = os.environ.get("MODELSPEC_EVIDENCE_REPLAY_DATA")
    if supplied:
        return Path(supplied)
    repo = tmp_path_factory.mktemp("replay-revisions")
    subprocess.run(["git", "init", "--quiet", str(repo)], check=True)
    (repo / ".engine-pin").write_text("# Synthetic replay fixture\n")
    subprocess.run(["git", "-C", str(repo), "add", ".engine-pin"], check=True)
    subprocess.run([
        "git", "-C", str(repo), "-c", "user.name=Fixture",
        "-c", "user.email=fixture@example.invalid", "commit", "--quiet",
        "-m", "Synthetic replay input",
    ], check=True)
    return repo


def run_until_post_check(name, repo, scratch, monkeypatch, expected):
    real_run = subprocess.run
    head = real_run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                    check=True, capture_output=True, text=True).stdout.strip()
    if expected is None:
        monkeypatch.delenv(ENV, raising=False)
    else:
        monkeypatch.setenv(ENV, expected)
    monkeypatch.setenv("GIT_NO_LAZY_FETCH", "1")
    path = ROOT / "docs/evidence/g2-ios" / SCRIPTS[name]
    argv = [str(path)]
    if name == "baseline":
        argv += ["--repo", str(repo), "--data-dir", str(repo),
                 "--output", str(scratch / "baseline"),
                 "--main-ref", head, "--policy-ref", head]
        if expected is not None:
            argv += ["--data-ref", expected]
    monkeypatch.setattr(sys, "argv", argv)
    fetches = 0

    def checked_run(command, **kwargs):
        nonlocal fetches
        command = list(command)
        if command[:2] == ["git", "clone"]:
            Path(command[-1]).symlink_to(repo, target_is_directory=True)
            return subprocess.CompletedProcess(command, 0, b"")
        assert command[0] == "git", "Replay attempted a non-Git external command"
        options = command[3:] if command[1] == "-C" else command[1:]
        if options[0] in {"fetch", "checkout"}:
            if options[0] == "fetch":
                fetches += 1
                if fetches == 2:
                    raise ReachedPostCheck("baseline checkout completed")
            real_run(["git", "-C", str(repo), "cat-file", "-e",
                      options[-1] + "^{commit}"], check=True, capture_output=True)
            return subprocess.CompletedProcess(command, 0, b"")
        if options[0] == "diff":
            # The unrelated historical repair target is a fixture input. Resolve
            # the supplied baseline with real Git, then reach the parent check.
            return real_run(["git", "-C", str(repo), "diff", "--name-only", "-z",
                             options[-2], head], **kwargs)
        if options[0] == "cat-file":
            raise ReachedPostCheck("repair baseline resolved")
        if options[0] == "archive":
            # Archive only the harmless fixture/config file, never retained pages.
            return real_run(["git", "-C", str(repo), "archive", "--worktree-attributes", "--format=tar",
                             options[-1], ".engine-pin"], **{
                                 key: value for key, value in kwargs.items() if key != "cwd"
                             })
        assert options[0] in {"rev-parse", "status"}, "Unexpected Git operation"
        return real_run(["git", "-C", str(repo), *options], **kwargs)

    def post_check(*_args, **_kwargs):
        raise ReachedPostCheck("next replay operation reached")

    real_mkdir = Path.mkdir

    def isolated_mkdir(path, *args, **kwargs):
        if str(path).startswith("/tmp/model-444-scratch/probes"):
            return None
        return real_mkdir(path, *args, **kwargs)

    monkeypatch.setattr(subprocess, "run", checked_run)
    monkeypatch.setattr(tarfile, "open", post_check)
    monkeypatch.setattr(Path, "mkdir", isolated_mkdir)
    # The seeder installs a process-wide hook. Its offline policy is outside
    # this revision-input test; all subprocess I/O is bounded above.
    monkeypatch.setattr(sys, "addaudithook", lambda _hook: None)
    namespace = runpy.run_path(str(path))
    if name == "sentences":
        derive = namespace["derive"]
        derive.__globals__["load_sources"] = post_check
        derive(repo)
    elif name in {"acceptance", "baseline"}:
        main = namespace["main"]
        if name == "acceptance":
            main.__globals__["ROOT"] = scratch / "acceptance"
        main()


@pytest.mark.parametrize("name", SCRIPTS)
def test_supplied_revision_reaches_post_check(name, replay_repo, tmp_path, monkeypatch):
    head = subprocess.run(["git", "-C", str(replay_repo), "rev-parse", "HEAD"],
                          check=True, capture_output=True, text=True).stdout.strip()
    with pytest.raises(ReachedPostCheck):
        run_until_post_check(name, replay_repo, tmp_path, monkeypatch, head)


@pytest.mark.parametrize("name", SCRIPTS)
def test_missing_revision_is_required(name, replay_repo, tmp_path, monkeypatch):
    if name == "baseline":
        with pytest.raises(SystemExit) as failure:
            run_until_post_check(name, replay_repo, tmp_path, monkeypatch, None)
        assert failure.value.code == 2
    else:
        with pytest.raises(KeyError, match=ENV):
            run_until_post_check(name, replay_repo, tmp_path, monkeypatch, None)


@pytest.mark.parametrize("name", SCRIPTS)
def test_wrong_revision_is_rejected(name, replay_repo, tmp_path, monkeypatch):
    error = ValueError if name == "sentences" else subprocess.CalledProcessError
    with pytest.raises(error) as failure:
        run_until_post_check(name, replay_repo, tmp_path, monkeypatch, "f" * 40)
    assert "f" * 40 not in str(failure.value)
