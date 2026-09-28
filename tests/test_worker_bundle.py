"""The built rank Worker carries the complete local import graph."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKER_ROOT = REPO_ROOT / "api" / "worker"
CHECKER = WORKER_ROOT / "bundle_check.py"
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "rank-api.yml"


def _load_checker():
    spec = importlib.util.spec_from_file_location("worker_bundle_check", CHECKER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_import_graph_reports_a_missing_transitive_package(tmp_path: Path) -> None:
    checker = _load_checker()
    (tmp_path / "entry.py").write_text("import service\n", encoding="utf-8")
    (tmp_path / "service.py").write_text("from repo.engine import run\n", encoding="utf-8")
    (tmp_path / "repo").mkdir()
    (tmp_path / "repo" / "__init__.py").touch()

    missing, visited = checker.missing_imports(tmp_path)

    assert [(item.module, item.imported_by) for item in missing] == [
        ("repo.engine", "service")
    ]
    assert visited == {"entry", "service"}


def test_import_graph_walks_relative_imports_from_package_initializers(
    tmp_path: Path,
) -> None:
    checker = _load_checker()
    (tmp_path / "entry.py").write_text("import repo\n", encoding="utf-8")
    (tmp_path / "repo").mkdir()
    (tmp_path / "repo" / "__init__.py").write_text(
        "from . import engine\n", encoding="utf-8"
    )
    (tmp_path / "repo" / "engine.py").write_text("VALUE = 1\n", encoding="utf-8")

    missing, visited = checker.missing_imports(tmp_path)

    assert missing == []
    assert visited == {"entry", "repo", "repo.engine"}


def test_import_graph_follows_literal_dynamic_imports(tmp_path: Path) -> None:
    checker = _load_checker()
    (tmp_path / "entry.py").write_text(
        'import importlib\nimportlib.import_module("lazy_service")\n',
        encoding="utf-8",
    )

    missing, _visited = checker.missing_imports(tmp_path)

    assert [(item.module, item.imported_by) for item in missing] == [
        ("lazy_service", "entry")
    ]


def test_checker_requires_every_file_in_the_vendor_manifest(tmp_path: Path) -> None:
    checker = _load_checker()
    vendor = __import__("runpy").run_path(str(WORKER_ROOT / "vendor.py"))
    targets = set(vendor["SOURCES"].values())
    for target in targets:
        path = tmp_path / target
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
    missing = next(iter(targets))
    (tmp_path / missing).unlink()

    assert checker.missing_vendored_files(tmp_path) == [missing]


def test_ci_checks_the_actual_pywrangler_output() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    build = workflow.index("pywrangler deploy --dry-run")
    check = workflow.index("bundle_check.py ../../dist/rank-worker")
    assert build < check
