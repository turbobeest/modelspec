"""MODEL-476: a writer that opens a pull request starts its own recall check.

The writer sources under .github/private-writers/ run only in the private data
repository. A pull request opened there with the repository token never starts
a `pull_request` workflow, so the "Approved answers on private data" check does
not run by itself. Each writer that opens or updates a pull request therefore
gets one separate job that alone holds `actions: write` and dispatches the
recall workflow on the pull request branch.
"""

from __future__ import annotations

import os
import re
import stat
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
WRITERS = ROOT / ".github" / "private-writers"
JOB = "recall-dispatch"
RECALL_FILE = "recall-private.yml"
STEP_NAME = "Dispatch the recall workflow on the pull request branch"
FALLBACK_TEXT = (
    'The "Approved answers on private data" check could not be started automatically. '
    'Run it by dispatching "Private production-data recall" on this branch (or close and '
    "reopen the pull request) and merge only when it passes."
)
STARTED_TEXT = (
    'The "Approved answers on private data" check was started on this branch by the '
    "workflow run that opened this pull request. Merge only when it passes."
)

# Every job's permissions as they were before MODEL-476. The new job is the only addition.
BEFORE = {
    "admission-drafter": {"draft": {"contents": "write", "pull-requests": "write"}},
    "curation-benchmarks": {
        "gate": {"contents": "read"},
        "watch": {"contents": "read", "actions": "read"},
        "draft": {"contents": "write", "pull-requests": "write"},
        "issues": {"contents": "read", "issues": "write"},
    },
    "daily-research": {
        "research": {"contents": "write", "pull-requests": "write"},
        "sync": {"contents": "write", "pull-requests": "write"},
    },
    "data-trust-audit": {"audit": {"contents": "write", "pull-requests": "write"}},
    "leaderboard-refresh": {"refresh": {"contents": "write", "pull-requests": "write"}},
    "lineup-proposer": {"propose": {"contents": "write", "pull-requests": "write"}},
    "model-week": {"draft": {"contents": "write", "pull-requests": "write"}},
    "price-reread": {
        "render": {"contents": "read"},
        "fallback": {"contents": "read", "actions": "read"},
        "reread": {
            "contents": "write", "pull-requests": "write", "issues": "write", "actions": "read",
        },
    },
    "release-signals": {
        "pending": {},
        "process": {"contents": "write", "pull-requests": "write"},
        "review": {"contents": "read", "issues": "write"},
    },
    "rendered-reread": {
        "reread": {
            "contents": "write", "pull-requests": "write", "issues": "write", "actions": "read",
        },
    },
    "speed-probe": {"probe": {"contents": "write", "pull-requests": "write"}},
}

_DATE = r"[0-9]{4}-[0-9]{2}-[0-9]{2}"
# Per writer: the jobs the dispatch waits for, the exact branch pattern, the exact
# BRANCHES expression, and sample names the pattern must accept and refuse.
SPEC = {
    "admission-drafter": {
        "needs": ["draft"],
        "pattern": r"^admission/[a-z0-9][a-z0-9.-]*/[a-z0-9][a-z0-9.-]*$",
        "branches": "${{ needs.draft.outputs.pr_branch }}",
        "valid": ["admission/anthropic/claude-haiku-5-5", "admission/acme/orbit-1.2"],
        "invalid": ["admission/Acme/orbit", "admission/acme", "admission/a/b/c", "-admission/a/b",
                    "data/model-week", "admission/../x", "admission/a/b;id"],
    },
    "curation-benchmarks": {
        "needs": ["draft"],
        "pattern": rf"^curation/benchmarks/[A-Za-z0-9][A-Za-z0-9._-]*-{_DATE}$",
        "branches": "${{ needs.draft.outputs.pr_branches }}",
        "valid": ["curation/benchmarks/aime_2025-2026-11-13", "curation/benchmarks/census-leads-2026-11-13"],
        "invalid": ["curation/benchmarks/x", "curation/benchmarks/-x-2026-11-13",
                    "curation/benchmarks/x y-2026-11-13", "curation/other/x-2026-11-13",
                    "curation/benchmarks/x$(id)-2026-11-13", "data/lineup-proposal"],
    },
    "daily-research": {
        "needs": ["sync"],
        "pattern": r"^research/daily-models$",
        "branches": "${{ needs.sync.outputs.pr_branch }}",
        "valid": ["research/daily-models"],
        "invalid": ["research/daily-models2", "research/daily-models/x", "data/model-week",
                    "research/daily-models;id", "--ref"],
    },
    "data-trust-audit": {
        "needs": ["audit"],
        "pattern": rf"^data/data-trust-{_DATE}$",
        "branches": "${{ needs.audit.outputs.pr_branch }}",
        "valid": ["data/data-trust-2026-11-13"],
        "invalid": ["data/data-trust-", "data/data-trust-2026-11-13x", "data/data-trust-2026-11-1",
                    "data/model-week"],
    },
    "leaderboard-refresh": {
        "needs": ["refresh"],
        "pattern": r"^data/weekly-leaderboard-refresh$",
        "branches": "${{ needs.refresh.outputs.pr_branch }}",
        "valid": ["data/weekly-leaderboard-refresh"],
        "invalid": ["data/weekly-leaderboard-refresh-2", "data/model-week", "main"],
    },
    "lineup-proposer": {
        "needs": ["propose"],
        "pattern": r"^data/lineup-proposal$",
        "branches": "${{ needs.propose.outputs.pr_branch }}",
        "valid": ["data/lineup-proposal"],
        "invalid": ["data/lineup-proposals", "data/lineup-proposal/x", "main", "refs/heads/data/lineup-proposal"],
    },
    "model-week": {
        "needs": ["draft"],
        "pattern": r"^data/model-week$",
        "branches": "${{ needs.draft.outputs.pr_branch }}",
        "valid": ["data/model-week"],
        "invalid": ["data/model-week-1", "data/model-week/x", "main"],
    },
    "price-reread": {
        "needs": ["reread"],
        "pattern": r"^data/weekly-price-(reread|reconfirm)$",
        "branches": "${{ needs.reread.outputs.pr_branch }} ${{ needs.reread.outputs.pr_branch_reconfirm }}",
        "valid": ["data/weekly-price-reread", "data/weekly-price-reconfirm"],
        "invalid": ["data/weekly-price-other", "data/weekly-price-reread2", "main"],
    },
    "release-signals": {
        "needs": ["process"],
        "pattern": r"^data/release-signal-[A-Za-z0-9._-]{1,150}-[0-9]{1,3}$",
        "branches": " ".join(f"${{{{ needs.process.outputs.branch_{i} }}}}" for i in range(10)),
        "valid": ["data/release-signal-anthropic.claude-5-0", "data/release-signal-a_b-7"],
        "invalid": ["data/release-signal-a-b", "data/release-signal-a/b-0",
                    "data/release-signal-a;id-0", "main", "data/release-signal-a-0x"],
    },
    "rendered-reread": {
        "needs": ["reread"],
        "pattern": r"^data/weekly-rendered-reread$",
        "branches": "${{ needs.reread.outputs.pr_branch }}",
        "valid": ["data/weekly-rendered-reread"],
        "invalid": ["data/weekly-rendered-reread-2", "main", "data/weekly-rendered-reread/x"],
    },
    "speed-probe": {
        "needs": ["probe"],
        "pattern": r"^data/speed-pilot-[0-9]{1,20}$",
        "branches": "${{ needs.probe.outputs.pr_branch }}",
        "valid": ["data/speed-pilot-123456789"],
        "invalid": ["data/speed-pilot-", "data/speed-pilot-12a", "data/speed-pilot-1/2", "main"],
    },
}
NAMES = tuple(SPEC)


def _load(name: str) -> dict:
    loaded = yaml.safe_load((WRITERS / f"{name}.yml").read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _dispatch(name: str) -> dict:
    jobs = _load(name)["jobs"]
    assert JOB in jobs, f"{name} has no {JOB} job"
    return jobs[JOB]


def _step(name: str) -> dict:
    steps = _dispatch(name)["steps"]
    assert len(steps) == 1, f"{name}: the dispatch job must have exactly one step"
    return steps[0]


def _walk(value):
    if isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from _walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk(item)
    else:
        yield value


@pytest.mark.parametrize("name", NAMES)
def test_every_pr_writer_has_one_dispatch_job_and_every_other_job_keeps_its_permissions(name: str) -> None:
    jobs = _load(name)["jobs"]
    assert set(jobs) == set(BEFORE[name]) | {JOB}
    for job_name, before in BEFORE[name].items():
        assert jobs[job_name].get("permissions") == before, f"{name}/{job_name}"
    assert _load(name)["permissions"] == {"contents": "read"}


@pytest.mark.parametrize("name", NAMES)
def test_only_the_dispatch_job_holds_actions_write(name: str) -> None:
    document = _load(name)
    holders = [
        job_name for job_name, job in document["jobs"].items()
        if (job.get("permissions") or {}).get("actions") == "write"
    ]
    assert holders == [JOB]
    assert _dispatch(name)["permissions"] == {"actions": "write", "pull-requests": "write"}
    text = (WRITERS / f"{name}.yml").read_text(encoding="utf-8")
    assert text.count("actions: write") == 1
    assert "write-all" not in text


@pytest.mark.parametrize("name", NAMES)
def test_the_dispatch_job_has_no_checkout_and_runs_nothing_from_the_working_tree(name: str) -> None:
    job = _dispatch(name)
    step = _step(name)
    assert step["name"] == STEP_NAME
    assert "uses" not in step
    assert set(job) == {
        "name", "needs", "if", "runs-on", "timeout-minutes", "continue-on-error", "permissions",
        "steps",
    }
    assert set(step) == {"name", "env", "run"}
    assert "working-directory" not in step and "shell" not in step
    run = step["run"]
    assert "checkout" not in run and "python" not in run and "$GITHUB_WORKSPACE" not in run
    assert not re.search(r"(^|[\s;&|(])(\./|bash |sh |source |\. )", run)
    assert not any("checkout" in str(item) for item in _walk(job))


@pytest.mark.parametrize("name", NAMES)
def test_the_branch_name_arrives_through_env_and_never_through_an_expression_in_run(name: str) -> None:
    step = _step(name)
    assert "${{" not in step["run"]
    env = step["env"]
    assert env["BRANCHES"] == SPEC[name]["branches"]
    assert env["BRANCH_PATTERN"] == SPEC[name]["pattern"]
    assert env["GH_TOKEN"] == "${{ github.token }}"
    assert env["GH_REPO"] == "${{ github.repository }}"
    assert env["RECALL_WORKFLOW"] == RECALL_FILE
    assert env["FALLBACK_MESSAGE"] == FALLBACK_TEXT
    # Daily research re-dispatches on every push to main, so it says so once, in the body.
    assert env["STARTED_MESSAGE"] == ("" if name == "daily-research" else STARTED_TEXT)
    assert set(env) == {
        "GH_TOKEN", "GH_REPO", "RECALL_WORKFLOW", "BRANCH_PATTERN", "BRANCHES", "FALLBACK_MESSAGE",
        "STARTED_MESSAGE",
    }
    for key, value in env.items():
        for expression in re.findall(r"\$\{\{(.*?)\}\}", str(value)):
            allowed = (
                expression.strip() in {"github.token", "github.repository"}
                or re.fullmatch(r"\s*needs\.[a-z]+\.outputs\.[a-z_0-9]+\s*", expression)
            )
            assert allowed, f"{name}: {key} reads {expression!r}"
    assert "secrets." not in str(_dispatch(name))


@pytest.mark.parametrize("name", NAMES)
def test_the_dispatch_job_waits_for_the_writer_and_its_failure_never_fails_the_run(name: str) -> None:
    document = _load(name)
    job = _dispatch(name)
    needs = [job["needs"]] if isinstance(job["needs"], str) else job["needs"]
    assert needs == SPEC[name]["needs"]
    assert job["continue-on-error"] is True
    assert str(job["if"]).startswith("${{ !cancelled() && ")
    assert job["timeout-minutes"] <= 5
    for other, body in document["jobs"].items():
        needs = body.get("needs") or []
        needs = [needs] if isinstance(needs, str) else needs
        assert JOB not in needs, f"{name}/{other} waits for the dispatch"
    # The dispatch job is the last link of the chain: nothing consumes its result.
    assert JOB not in str({k: v for k, v in document["jobs"].items() if k != JOB})


@pytest.mark.parametrize("name", NAMES)
def test_the_branch_pattern_accepts_only_this_writers_branches(name: str) -> None:
    pattern = re.compile(SPEC[name]["pattern"])
    assert pattern.pattern.startswith("^") and pattern.pattern.endswith("$")
    for branch in SPEC[name]["valid"]:
        assert pattern.match(branch), branch
    for branch in SPEC[name]["invalid"]:
        assert not pattern.match(branch), branch
    assert not pattern.match("-" + SPEC[name]["valid"][0])


def _run(name: str, tmp_path: Path, branches: str, *, fail_dispatch: bool = False,
         fail_comment: bool = False) -> tuple[subprocess.CompletedProcess[str], list[str]]:
    step = _step(name)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "gh.log"
    log.touch()
    gh = bin_dir / "gh"
    gh.write_text(
        "#!/usr/bin/env bash\n"
        'printf "%s\\n" "$*" >> "$GH_LOG"\n'
        'if [ "$1 $2" = "workflow run" ] && [ -n "${FAIL_DISPATCH:-}" ]; then exit 1; fi\n'
        'if [ "$1 $2" = "pr comment" ] && [ -n "${FAIL_COMMENT:-}" ]; then exit 1; fi\n'
        "exit 0\n",
        encoding="utf-8",
    )
    gh.chmod(gh.stat().st_mode | stat.S_IXUSR)
    env = {
        **os.environ,
        **{k: v for k, v in step["env"].items() if "${{" not in v},
        "BRANCHES": branches,
        "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
        "GH_LOG": str(log),
        "GITHUB_STEP_SUMMARY": str(tmp_path / "summary.md"),
        "GH_TOKEN": "test-token",
        "GH_REPO": "owner/data",
    }
    if fail_dispatch:
        env["FAIL_DISPATCH"] = "1"
    if fail_comment:
        env["FAIL_COMMENT"] = "1"
    result = subprocess.run(
        ["bash", "-c", step["run"]], env=env, cwd=tmp_path, capture_output=True, text=True, check=False,
    )
    return result, log.read_text(encoding="utf-8").splitlines()


@pytest.mark.parametrize("name", NAMES)
def test_a_valid_branch_is_dispatched_once_on_the_recall_workflow_and_announced(name: str, tmp_path: Path) -> None:
    branch = SPEC[name]["valid"][0]
    result, calls = _run(name, tmp_path, branch)
    assert result.returncode == 0, result.stderr
    expected = [f"workflow run {RECALL_FILE} --ref {branch}"]
    if name != "daily-research":
        expected.append(f"pr comment {branch} --body {STARTED_TEXT}")
    assert calls == expected


@pytest.mark.parametrize("name", NAMES)
def test_an_empty_branch_list_does_nothing(name: str, tmp_path: Path) -> None:
    for index, empty in enumerate(("", "   ")):
        case = tmp_path / f"case{index}"
        case.mkdir()
        result, calls = _run(name, case, empty)
        assert result.returncode == 0
        assert calls == []


@pytest.mark.parametrize("name", NAMES)
def test_a_name_outside_the_pattern_is_never_dispatched_and_never_echoed(name: str, tmp_path: Path) -> None:
    for index, bad in enumerate(SPEC[name]["invalid"]):
        case = tmp_path / f"case{index}"
        case.mkdir()
        result, calls = _run(name, case, bad)
        assert result.returncode != 0, bad
        assert calls == [], bad
        assert bad not in result.stdout + result.stderr or bad.isalnum(), bad


@pytest.mark.parametrize("name", NAMES)
def test_a_bad_name_next_to_a_good_one_does_not_stop_the_good_one(name: str, tmp_path: Path) -> None:
    good = SPEC[name]["valid"][0]
    bad = SPEC[name]["invalid"][0]
    result, calls = _run(name, tmp_path, f"{bad} {good}")
    assert result.returncode != 0
    assert calls[0] == f"workflow run {RECALL_FILE} --ref {good}"
    assert not any(call.endswith(f"--ref {bad}") for call in calls)


@pytest.mark.parametrize("name", NAMES)
def test_a_failed_dispatch_posts_the_fallback_and_fails_only_this_job(name: str, tmp_path: Path) -> None:
    branch = SPEC[name]["valid"][0]
    result, calls = _run(name, tmp_path, branch, fail_dispatch=True)
    assert result.returncode != 0
    assert calls == [
        f"workflow run {RECALL_FILE} --ref {branch}",
        f"pr comment {branch} --body {FALLBACK_TEXT}",
    ]
    assert "close and" in FALLBACK_TEXT
    assert _dispatch(name)["continue-on-error"] is True


@pytest.mark.parametrize("name", NAMES)
def test_a_failed_comment_is_a_warning_not_a_lost_pull_request(name: str, tmp_path: Path) -> None:
    branch = SPEC[name]["valid"][0]
    result, calls = _run(name, tmp_path, branch, fail_comment=True)
    assert result.returncode == 0
    assert calls[0] == f"workflow run {RECALL_FILE} --ref {branch}"
    assert ("::warning::" in result.stdout) == (name != "daily-research")


def test_a_pattern_with_option_like_or_shell_text_is_refused_for_every_writer(tmp_path: Path) -> None:
    hostile = ["--help", "-f", "$(id)", "`id`", "a;b", "a|b", "../../x", "a\nb"]
    for name in NAMES:
        for index, bad in enumerate(hostile):
            case = tmp_path / f"{name}-{index}"
            case.mkdir()
            _, calls = _run(name, case, bad)
            assert not any(call.startswith("workflow run") and bad in call for call in calls)


def test_the_release_signal_slots_cover_every_work_item() -> None:
    document = _load("release-signals")
    limit = int(document["env"]["MAX_RELEASE_SIGNAL_WORK_ITEMS"])
    outputs = document["jobs"]["process"]["outputs"]
    assert sorted(outputs) == sorted(f"branch_{i}" for i in range(limit))
    for index in range(limit):
        assert outputs[f"branch_{index}"] == (
            f"${{{{ strategy.job-index == {index} && steps.recall_branch.outputs.branch || '' }}}}"
        )
    assert _dispatch("release-signals")["if"] == (
        "${{ !cancelled() && needs.process.result != 'skipped' }}"
    )


def test_the_release_signal_branch_is_checked_in_the_matrix_job_before_it_becomes_an_output(
    tmp_path: Path,
) -> None:
    steps = _load("release-signals")["jobs"]["process"]["steps"]
    step = next(s for s in steps if s.get("id") == "recall_branch")
    assert step["if"] == "steps.pr.outputs.url != ''"
    assert "actions" not in str(step)
    assert steps.index(step) == steps.index(next(s for s in steps if s.get("id") == "pr")) + 1
    for branch, ok in (
        ("data/release-signal-acme.orbit-1", True),
        ("main", False),
        ("data/release-signal-x;id-1", False),
        ("-data/release-signal-x-1", False),
    ):
        out = tmp_path / f"out-{abs(hash(branch))}"
        out.touch()
        env = {**os.environ, "BRANCH": branch, "GITHUB_OUTPUT": str(out)}
        result = subprocess.run(["bash", "-c", step["run"]], env=env, capture_output=True, text=True,
                                check=False)
        assert result.returncode == 0, result.stderr
        assert out.read_text(encoding="utf-8") == (f"branch={branch}\n" if ok else "")


PR_STEP = {
    "admission-drafter": ("draft", "pr", "pr_branch"),
    "data-trust-audit": ("audit", "pr", "pr_branch"),
    "leaderboard-refresh": ("refresh", "pr", "pr_branch"),
    "lineup-proposer": ("propose", "pr", "pr_branch"),
    "model-week": ("draft", "pr", "pr_branch"),
    "price-reread": ("reread", "pr", "pr_branch"),
    "rendered-reread": ("reread", "pr", "pr_branch"),
    "speed-probe": ("probe", "pr", "pr_branch"),
}


@pytest.mark.parametrize("name", sorted(PR_STEP))
def test_a_create_pull_request_writer_exposes_only_a_created_or_updated_branch(name: str) -> None:
    job_name, step_id, output = PR_STEP[name]
    job = _load(name)["jobs"][job_name]
    step = next(s for s in job["steps"] if s.get("id") == step_id)
    assert str(step["uses"]).startswith("peter-evans/create-pull-request@")
    expected = (
        f"${{{{ (steps.{step_id}.outputs.pull-request-operation == 'created' || "
        f"steps.{step_id}.outputs.pull-request-operation == 'updated') && "
        f"steps.{step_id}.outputs.pull-request-branch || '' }}}}"
    )
    assert job["outputs"][output] == expected
    if name == "price-reread":
        other = next(s for s in job["steps"] if s.get("id") == "pr_reconfirm")
        assert str(other["uses"]).startswith("peter-evans/create-pull-request@")
        assert job["outputs"]["pr_branch_reconfirm"] == expected.replace("steps.pr.", "steps.pr_reconfirm.")
    else:
        assert set(job["outputs"]) == {output}


def test_curation_lists_only_todays_open_curation_draft_branches_for_the_dispatch() -> None:
    job = _load("curation-benchmarks")["jobs"]["draft"]
    step = next(s for s in job["steps"] if s.get("id") == "opened")
    assert job["outputs"] == {"pr_branches": "${{ steps.opened.outputs.branches }}"}
    names = [s.get("name") for s in job["steps"]]
    assert names.index(step["name"]) == names.index("Open draft PRs (one per changed page)") + 1
    assert step["if"] == "${{ !cancelled() }}"
    assert step["continue-on-error"] is True
    assert "actions" not in str(step["env"]).lower()
    assert _dispatch("curation-benchmarks")["if"] == (
        "${{ !cancelled() && needs.draft.outputs.pr_branches != '' }}"
    )


def test_daily_research_dispatches_after_the_sync_and_only_for_an_open_pull_request() -> None:
    document = _load("daily-research")
    sync = document["jobs"]["sync"]
    assert sync["outputs"] == {"pr_branch": "${{ steps.update.outputs.pr_branch }}"}
    assert [s.get("id") for s in sync["steps"]] == ["update"]
    assert "pr_branch=$BRANCH" in sync["steps"][0]["run"]
    assert _dispatch("daily-research")["if"] == (
        "${{ !cancelled() && needs.sync.outputs.pr_branch != '' }}"
    )


@pytest.mark.parametrize("name", [n for n in NAMES if n not in {"curation-benchmarks", "daily-research", "release-signals"}])
def test_the_dispatch_condition_needs_a_branch_from_the_writer(name: str) -> None:
    expression = SPEC[name]["branches"].replace("${{ ", "").replace(" }}", "").split(" ")
    expected = "${{ !cancelled() && (" + " || ".join(f"{e} != ''" for e in expression) + ") }}"
    if len(expression) == 1:
        expected = "${{ !cancelled() && " + f"{expression[0]} != ''" + " }}"
    assert _dispatch(name)["if"] == expected


def test_no_writer_outside_the_pinned_set_gained_a_dispatch_job() -> None:
    for path in sorted(WRITERS.glob("*.yml")):
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        has = JOB in document["jobs"]
        assert has == (path.stem in SPEC), path.name
        if path.stem not in SPEC:
            assert "actions: write" not in path.read_text(encoding="utf-8"), path.name


def test_the_dispatched_recall_workflow_is_the_one_in_the_pull_request_checks() -> None:
    recall = yaml.safe_load((WRITERS / RECALL_FILE).read_text(encoding="utf-8"))
    triggers = recall.get("on") or recall.get(True)
    assert "workflow_dispatch" in triggers
    assert triggers["workflow_dispatch"] is None  # no inputs for the dispatcher to supply
    assert recall["permissions"] == {"contents": "read"}
    assert recall["jobs"]["recall"]["name"] == "Approved answers on private data"
    assert "actions: write" not in (WRITERS / RECALL_FILE).read_text(encoding="utf-8")


def test_the_close_and_reopen_text_survives_only_as_the_dispatch_job_fallback() -> None:
    for path in sorted(WRITERS.glob('*.yml')):
        text = path.read_text(encoding='utf-8')
        if path.stem in SPEC:
            document = yaml.safe_load(text)
            for job_name, job in document['jobs'].items():
                if job_name != JOB:
                    assert 'close and reopen' not in str(job), (path.name, job_name)


def test_daily_research_body_says_the_check_is_started_by_a_follow_up_job() -> None:
    job = _load("daily-research")["jobs"]["research"]
    step = next(s for s in job["steps"] if s.get("uses", "").startswith("peter-evans/create-pull-request@"))
    assert "A follow-up job of this workflow run starts the" in step["with"]["body"]
