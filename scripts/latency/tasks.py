"""MODEL-60 task set: 20 Python exercises from Aider's polyglot benchmark.

Pinned to a commit. Graded by the exercise's own unittest file inside a
`python:3.12-slim` container with no network. The agent never sees
`.meta/` (it holds the reference solution) and cannot change the tests that
grade it: tests are copied fresh from the pinned checkout before grading.
"""

from __future__ import annotations

import hashlib
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

TASK_SET_NAME = "aider-polyglot-benchmark/python"
TASK_SET_REPO = "https://github.com/Aider-AI/polyglot-benchmark.git"
TASK_SET_COMMIT = "7e0611e77b54e2dea774cdc0aa00cf9f7ed6144f"
TASK_COUNT = 20
SMOKE_TASK = "affine-cipher"
GRADER_IMAGE = "python:3.12-slim"
PRACTICE = Path("python/exercises/practice")

# Prompt wording follows Aider's benchmark prompt, adapted to an agent that edits files.
PROMPT_TEMPLATE = (
    "{instructions}\n\n"
    "Use the above instructions to modify the supplied files: {solution}\n"
    "Don't change the names of existing functions or classes, as they may be "
    "referenced from other code like unit tests, etc.\n"
    "Only use standard python libraries, don't suggest installing any packages.\n"
    "Do not modify {tests}. Work only in the current directory."
)


@dataclass(frozen=True)
class Task:
    task_id: str
    src: Path

    @property
    def solution(self) -> str:
        return self.task_id.replace("-", "_") + ".py"

    @property
    def tests(self) -> str:
        return self.task_id.replace("-", "_") + "_test.py"


def select_tasks(checkout: Path) -> list[Task]:
    """The first 20 practice exercises by name. Deterministic, no cherry-picking."""
    names = sorted(p.name for p in (checkout / PRACTICE).iterdir() if p.is_dir())
    if len(names) < TASK_COUNT:
        raise ValueError(f"expected >= {TASK_COUNT} exercises, found {len(names)}")
    return [Task(n, checkout / PRACTICE / n) for n in names[:TASK_COUNT]]


def task_set_hash(tasks: list[Task]) -> str:
    """sha256 over (task_id/relpath, file sha256) for every file of the 20 tasks."""
    outer = hashlib.sha256()
    for task in sorted(tasks, key=lambda t: t.task_id):
        for f in sorted(p for p in task.src.rglob("*") if p.is_file()):
            rel = f"{task.task_id}/{f.relative_to(task.src).as_posix()}"
            outer.update(f"{rel}\0{hashlib.sha256(f.read_bytes()).hexdigest()}\n".encode())
    return outer.hexdigest()


def build_prompt(task: Task) -> str:
    docs = task.src / ".docs"
    parts = [(docs / n).read_text() for n in ("instructions.md", "instructions.append.md") if (docs / n).exists()]
    return PROMPT_TEMPLATE.format(instructions="\n\n".join(parts).strip(), solution=task.solution, tests=task.tests)


def prepare_workdir(task: Task, workdir: Path) -> None:
    """Disposable copy: stub + tests + docs only. No .meta (reference solution)."""
    workdir.mkdir(parents=True, exist_ok=False)
    for name in (task.solution, task.tests):
        shutil.copy2(task.src / name, workdir / name)
    shutil.copytree(task.src / ".docs", workdir / ".docs")


def grade(task: Task, workdir: Path, timeout: int = 180) -> dict:
    """Restore pristine tests, then run unittest in a no-network container."""
    grade_dir = workdir.parent / (workdir.name + "-grade")
    shutil.copytree(workdir, grade_dir, ignore=shutil.ignore_patterns("__pycache__", ".docs"))
    shutil.copy2(task.src / task.tests, grade_dir / task.tests)
    cmd = [
        "docker", "run", "--rm", "--network", "none", "--read-only", "--tmpfs", "/tmp",
        "-e", "PYTHONDONTWRITEBYTECODE=1", "-v", f"{grade_dir}:/task:ro", "-w", "/task",
        GRADER_IMAGE, "python", "-m", "unittest", "-q", task.tests[:-3],
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"passed": False, "grader": "timeout", "grader_tail": ""}
    return {"passed": proc.returncode == 0, "grader": f"exit {proc.returncode}", "grader_tail": proc.stderr[-400:]}
