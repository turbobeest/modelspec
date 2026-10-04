"""Every Python module a workflow runs must find its third-party imports installed.

MODEL-312. MODEL-307 moved pydantic out of the package's runtime dependencies,
and the scheduled Coverage report, which installed only ``-e .``, failed the
next morning: ``scripts.slo`` reaches ``decision`` through a function-level
import, and ``decision`` imports pydantic at module level. No pull request
check ran that workflow, so nothing caught it.

This walks the import graph statically from each ``python -m MOD`` and
``python path.py`` a workflow step runs, and compares the third-party packages
it reaches against what that job's ``pip install`` lines install. The rule:

* a local import is followed wherever it is written, inside a function or not;
* a third-party import counts only at module level. One written inside a
  function is that function's own optional dependency (``decision.snapshot``
  imports cryptography only to sign);
* imports under ``try/except ImportError`` or ``if TYPE_CHECKING`` never count.
"""

from __future__ import annotations

import ast
import re
import shlex
import sys
import tomllib
from collections.abc import Iterator, Mapping
from functools import cache
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = REPO_ROOT / ".github" / "workflows"

# A distribution whose import name is not its normalised project name.
IMPORT_NAME = {"pyyaml": "yaml", "beautifulsoup4": "bs4", "pytest-xdist": "xdist",
               "pytest-asyncio": "pytest_asyncio"}

# (importer, imported): a function-level local import no workflow ever executes.
# Each needs the reason; the last test fails when one stops existing.
NOT_RUN_BY_WORKFLOWS = {
    ("tests.corpus.corpus", "cli.modelspec.legacy"):
        "run_cli is called only from tests/test_corpus.py, never by a workflow subcommand",
}

INVOCATION = re.compile(r"(?:^|[\s;(&|])python3? (?:-m ([\w.]+)|([\w./-]+\.py))")
PIP_INSTALL = re.compile(r"(?:^|\s)(?:python3? -m )?pip3? install (.*)")
GUARD_EXCEPTIONS = {"ImportError", "ModuleNotFoundError", "Exception"}


def _find(module: str, roots: list[Path]) -> Path | None:
    for root in roots:
        path = root.joinpath(*module.split("."))
        if (path / "__init__.py").is_file():
            return path / "__init__.py"
        if path.with_suffix(".py").is_file():
            return path.with_suffix(".py")
    return None


def _is_local(top: str, roots: list[Path]) -> bool:
    return any((root / top).is_dir() or (root / f"{top}.py").is_file() for root in roots)


def _guarded_and_lazy(node: ast.AST, parents: Mapping[ast.AST, ast.AST]) -> tuple[bool, bool]:
    child, parent, lazy = node, parents.get(node), False
    while parent is not None:
        if isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            lazy = True
        if isinstance(parent, ast.Try) and child in parent.body:
            for handler in parent.handlers:
                caught = handler.type
                names = ({"Exception"} if caught is None else
                         {getattr(e, "id", "") for e in getattr(caught, "elts", [caught])})
                if names & GUARD_EXCEPTIONS:
                    return True, lazy
        if isinstance(parent, ast.If) and "TYPE_CHECKING" in ast.unparse(parent.test):
            return True, lazy
        child, parent = parent, parents.get(parent)
    return False, lazy


@cache
def _imports(path: Path, module: str) -> tuple[tuple[str, tuple[str, ...], bool], ...]:
    """(imported module, names imported from it, whether it sits in a function)."""
    return tuple(_walk_imports(path, module))


def _walk_imports(path: Path, module: str) -> Iterator[tuple[str, tuple[str, ...], bool]]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    parents = {child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}
    package = module if path.name == "__init__.py" else module.rpartition(".")[0]
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Import, ast.ImportFrom)):
            continue
        guarded, lazy = _guarded_and_lazy(node, parents)
        if guarded:
            continue
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name, (), lazy
            continue
        name = node.module or ""
        if node.level:
            base = package.split(".")[:len(package.split(".")) - node.level + 1]
            name = ".".join(base + ([node.module] if node.module else []))
        yield name, tuple(alias.name for alias in node.names), lazy


def reached_packages(entry: str, roots: list[Path],
                     not_run: Mapping[tuple[str, str], str] = NOT_RUN_BY_WORKFLOWS,
                     used: set[tuple[str, str]] | None = None) -> dict[str, str]:
    """Third-party top-level package -> the local module that imports it."""
    seen: set[str] = set()
    reached: dict[str, str] = {}
    stack = [(entry, "<entry>", False)]
    while stack:
        name, importer, lazy = stack.pop()
        top = name.split(".")[0]
        if top in sys.stdlib_module_names or top == "__future__":
            continue
        if not _is_local(top, roots):
            if not lazy:
                reached.setdefault(top, importer)
            continue
        if lazy and (importer, name) in not_run:
            if used is not None:
                used.add((importer, name))
            continue
        parts = name.split(".")
        for i in range(1, len(parts) + 1):
            module = ".".join(parts[:i])
            path = _find(module, roots)
            if path is None or module in seen:
                continue
            seen.add(module)
            for imported, names, is_lazy in _imports(path, module):
                stack.append((imported, module, is_lazy))
                stack.extend((f"{imported}.{n}", module, is_lazy) for n in names
                             if _find(f"{imported}.{n}", roots))
    return reached


def _import_name(requirement: str) -> str:
    project = re.split(r"[\[<>=!~ ;]", requirement, maxsplit=1)[0].lower()
    return IMPORT_NAME.get(project, project.replace("-", "_"))


def _pyproject(extras: list[str]) -> list[str]:
    project = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    return [*project["dependencies"],
            *(dep for extra in extras for dep in project["optional-dependencies"][extra])]


def installed_packages(job: Mapping) -> set[str]:
    """Import names a job's ``pip install`` lines provide. ``uv pip`` targets another venv."""
    installed: set[str] = set()
    for step in job.get("steps") or ():
        for line in (step.get("run") or "").replace("\\\n", " ").splitlines():
            match = PIP_INSTALL.search(line)
            if not match or "uv pip" in line:
                continue
            args = iter(shlex.split(match.group(1), comments=True))
            for arg in args:
                assert arg not in ("-r", "-c"), f"teach this test to read {arg} files: {line}"
                if arg == "-e":
                    extras = re.search(r"\[(.*)\]", next(args))
                    installed |= {_import_name(dep) for dep in
                                  _pyproject(extras.group(1).split(",") if extras else [])}
                elif not arg.startswith("-") and "$" not in arg:
                    installed.add(_import_name(arg))
    return installed


def invocations(job: Mapping) -> Iterator[tuple[str, str, list[Path]]]:
    """(as written, entry module, import roots) for each local module a job runs."""
    default = (job.get("defaults") or {}).get("run", {}).get("working-directory", ".")
    for step in job.get("steps") or ():
        cwd = REPO_ROOT / step.get("working-directory", default)
        for match in INVOCATION.finditer(step.get("run") or ""):
            module, script = match.groups()
            if module:
                path = _find(module, [cwd])
                if path is None:
                    continue  # pytest, build, venv: not ours
                main = f"{module}.__main__"
                yield match.group(0).strip(), main if _find(main, [cwd]) else module, [cwd]
            elif (cwd / script).is_file():
                path = (cwd / script).resolve()
                yield match.group(0).strip(), path.stem, [path.parent, REPO_ROOT]


def _jobs() -> Iterator[tuple[str, str, Mapping]]:
    for workflow in sorted(WORKFLOWS.glob("*.yml")):
        for job_id, job in (yaml.safe_load(workflow.read_text(encoding="utf-8"))["jobs"]).items():
            yield workflow.name, job_id, job


@pytest.mark.parametrize(("workflow", "job_id", "job"),
                         [pytest.param(*j, id=f"{j[0]}:{j[1]}") for j in _jobs()])
def test_every_module_a_workflow_runs_has_its_imports_installed(
        workflow: str, job_id: str, job: Mapping) -> None:
    installed = installed_packages(job)
    missing = {}
    for written, entry, roots in invocations(job):
        gaps = {pkg: via for pkg, via in reached_packages(entry, roots).items()
                if pkg not in installed}
        if gaps:
            missing[written] = gaps
    assert not missing, (f"{workflow} job {job_id} installs {sorted(installed)} but runs "
                         f"modules that import more (package: importing module): {missing}")


def test_the_check_catches_the_model_312_regression() -> None:
    """The Coverage report as it was on 2026-10-04: ``-e .`` alone, no pydantic."""
    job = {"steps": [{"run": "python -m pip install -e ."},
                     {"run": 'python -m scripts.slo report --out coverage-report "${stage[@]}"'}]}
    assert "pydantic" not in installed_packages(job)
    (written, entry, roots), = invocations(job)
    assert (written, entry) == ("python -m scripts.slo", "scripts.slo.__main__")
    reached = reached_packages(entry, roots)
    assert "pydantic" in reached
    assert "cryptography" not in reached, "a function-level third-party import counted"


def test_pip_lines_resolve_to_import_names() -> None:
    job = {"steps": [{"run": "python -m pip install \\\n  \"PyYAML==6.0.3\" -q \\\n"
                             "  beautifulsoup4 \"$pins\"\n"
                             "uv pip install -p other -e . falkordb\n"},
                     {"run": "pip install -e '.[dev]'"}]}
    installed = installed_packages(job)
    assert {"yaml", "bs4", "pydantic", "typer", "xdist"} <= installed
    assert "pyyaml" not in installed


def test_every_not_run_exemption_still_exists() -> None:
    used: set[tuple[str, str]] = set()
    for _, _, job in _jobs():
        for _, entry, roots in invocations(job):
            reached_packages(entry, roots, used=used)
    assert used == set(NOT_RUN_BY_WORKFLOWS), \
        f"stale exemptions: {sorted(set(NOT_RUN_BY_WORKFLOWS) - used)}"
