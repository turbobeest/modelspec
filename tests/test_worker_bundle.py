"""The built rank Worker carries the complete local import graph."""

from __future__ import annotations

import ast
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

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


@pytest.mark.parametrize(
    ("source", "invoke"),
    [
        (
            "def answer():\n"
            "    from missing_runtime_package import answer\n"
            "    return answer()\n",
            "entry.service.answer()",
        ),
        (
            "async def answer():\n"
            "    from missing_runtime_package import answer\n"
            "    return answer()\n",
            "import asyncio; asyncio.run(entry.service.answer())",
        ),
        (
            "def answer():\n"
            "    def nested():\n"
            "        from missing_runtime_package import answer\n"
            "        return answer()\n"
            "    return nested()\n",
            "entry.service.answer()",
        ),
        (
            "def answer():\n"
            "    for _unused in (None,):\n"
            "        from missing_runtime_package import answer\n"
            "        return answer()\n",
            "entry.service.answer()",
        ),
        (
            "class Service:\n"
            "    def answer(self):\n"
            "        from missing_runtime_package import answer\n"
            "        return answer()\n",
            "entry.service.Service().answer()",
        ),
    ],
    ids=["ordinary", "async", "nested", "loop", "method"],
)
def test_import_graph_reports_a_function_local_missing_import(
    tmp_path: Path, source: str, invoke: str,
) -> None:
    checker = _load_checker()
    (tmp_path / "entry.py").write_text("import service\n", encoding="utf-8")
    (tmp_path / "service.py").write_text(source, encoding="utf-8")
    actual = subprocess.run(
        [sys.executable, "-I", "-c",
         f"import sys; sys.path.insert(0, {str(tmp_path)!r}); import entry; {invoke}"],
        capture_output=True, text=True,
    )
    assert actual.returncode == 1
    assert "No module named 'missing_runtime_package'" in actual.stderr

    missing, _visited = checker.missing_imports(tmp_path)

    assert [(item.module, item.imported_by) for item in missing] == [
        ("missing_runtime_package", "service")
    ]


@pytest.mark.parametrize(
    "source",
    [
        "def answer(value):\n"
        "    match value:\n"
        "        case 1:\n"
        "            from missing_runtime_package import answer\n"
        "            return answer()\n",
        "def answer():\n"
        "    for _unused in (None,):\n"
        "        _unused = None\n"
        "    else:\n"
        "        from missing_runtime_package import answer\n"
        "        return answer()\n",
        "def answer():\n"
        "    with contextlib.nullcontext():\n"
        "        from missing_runtime_package import answer\n"
        "        return answer()\n",
        "def answer():\n"
        "    def middle():\n"
        "        def inner():\n"
        "            from missing_runtime_package import answer\n"
        "            return answer()\n"
        "        return inner()\n"
        "    return middle()\n",
        "def answer():\n"
        "    from .missing_runtime_package import answer\n"
        "    return answer()\n",
        "def answer():\n"
        "    try:\n"
        "        from missing_runtime_package import answer\n"
        "        return answer()\n"
        "    except ImportError:\n"
        "        return None\n",
        "def answer():\n"
        "    try:\n"
        "        value = 1\n"
        "    except Exception:\n"
        "        from missing_runtime_package import answer\n"
        "        return answer()\n",
        "def answer():\n"
        "    try:\n"
        "        value = 1\n"
        "    except Exception:\n"
        "        return None\n"
        "    else:\n"
        "        from missing_runtime_package import answer\n"
        "        return answer()\n",
        "def answer():\n"
        "    try:\n"
        "        value = 1\n"
        "    finally:\n"
        "        from missing_runtime_package import answer\n"
        "        return answer()\n",
        "def answer():\n"
        "    while True:\n"
        "        from missing_runtime_package import answer\n"
        "        return answer()\n",
        "async def answer():\n"
        "    async with contextlib.nullcontext():\n"
        "        from missing_runtime_package import answer\n"
        "        return answer()\n",
        "def answer():\n"
        "    try:\n"
        "        value = 1\n"
        "    except* Exception:\n"
        "        from missing_runtime_package import answer\n"
        "        return answer()\n",
    ],
    ids=[
        "match", "loop-else", "with-body", "three-levels", "relative", "try-except-import",
        "except-handler", "try-else", "try-finally", "while", "async-with", "except-star",
    ],
)
def test_import_graph_reports_a_function_local_import_in_each_block(
    tmp_path: Path, source: str,
) -> None:
    checker = _load_checker()
    (tmp_path / "entry.py").write_text("import service\n", encoding="utf-8")
    (tmp_path / "service.py").write_text(source, encoding="utf-8")

    missing, _visited = checker.missing_imports(tmp_path)

    assert [(item.module, item.imported_by) for item in missing] == [
        ("missing_runtime_package", "service")
    ]


def test_annotation_only_import_inside_a_function_is_not_a_bundle_dependency(
    tmp_path: Path,
) -> None:
    checker = _load_checker()
    (tmp_path / "entry.py").write_text(
        "def answer():\n"
        "    from typing import TYPE_CHECKING\n"
        "    if TYPE_CHECKING:\n"
        "        import missing_annotation_package\n"
        "    else:\n"
        "        import missing_runtime_package\n",
        encoding="utf-8",
    )

    missing, _visited = checker.missing_imports(tmp_path)

    assert [(item.module, item.imported_by) for item in missing] == [
        ("missing_runtime_package", "entry")
    ]


def test_builder_exclusion_does_not_hide_a_runtime_import(tmp_path: Path) -> None:
    checker = _load_checker()
    (tmp_path / "entry.py").write_text("import decision.snapshot\n", encoding="utf-8")
    package = tmp_path / "decision"
    package.mkdir()
    (package / "__init__.py").touch()
    (package / "snapshot.py").write_text(
        "def collect_repo():\n"
        "    import pipeline.load\n"
        "class _Compiler:\n"
        "    def compile(self):\n"
        "        import decision.labs\n"
        "def runtime_request():\n"
        "    import missing_runtime_package\n",
        encoding="utf-8",
    )

    missing, _visited = checker.missing_imports(tmp_path)

    assert [(item.module, item.imported_by) for item in missing] == [
        ("missing_runtime_package", "decision.snapshot")
    ]


def test_builder_name_in_a_nested_function_does_not_inherit_the_exclusion(
    tmp_path: Path,
) -> None:
    checker = _load_checker()
    (tmp_path / "entry.py").write_text("import decision.snapshot\n", encoding="utf-8")
    package = tmp_path / "decision"
    package.mkdir()
    (package / "__init__.py").touch()
    (package / "snapshot.py").write_text(
        "def runtime():\n"
        "    def collect_repo():\n"
        "        import missing_runtime_package\n"
        "    return collect_repo()\n",
        encoding="utf-8",
    )

    missing, _visited = checker.missing_imports(tmp_path)

    assert [(item.module, item.imported_by) for item in missing] == [
        ("missing_runtime_package", "decision.snapshot")
    ]


def test_ed25519_imports_stay_excluded_only_inside_load_snapshot_bytes(
    tmp_path: Path,
) -> None:
    checker = _load_checker()
    assert checker.HMAC_ONLY_IMPORTS == {
        "cryptography.exceptions",
        "cryptography.hazmat.primitives.asymmetric.ed25519",
    }
    (tmp_path / "entry.py").write_text("import decision.snapshot\n", encoding="utf-8")
    package = tmp_path / "decision"
    package.mkdir()
    (package / "__init__.py").touch()
    (package / "snapshot.py").write_text(
        "def load_snapshot_bytes():\n"
        "    import missing_runtime_package\n"
        "    from missing_from_package import answer\n"
        "    from cryptography.exceptions import InvalidSignature\n"
        "    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey\n"
        "    from cryptography.hazmat.primitives import serialization\n"
        "def other():\n"
        "    from cryptography.exceptions import InvalidSignature\n",
        encoding="utf-8",
    )

    missing, _visited = checker.missing_imports(tmp_path)

    assert sorted((item.module, item.imported_by) for item in missing) == [
        ("cryptography.exceptions", "decision.snapshot"),
        ("cryptography.hazmat.primitives", "decision.snapshot"),
        ("missing_from_package", "decision.snapshot"),
        ("missing_runtime_package", "decision.snapshot"),
    ]


def test_excluded_function_name_in_another_module_is_reported(tmp_path: Path) -> None:
    checker = _load_checker()
    (tmp_path / "entry.py").write_text(
        "def main():\n"
        "    import missing_runtime_package\n",
        encoding="utf-8",
    )

    missing, _visited = checker.missing_imports(tmp_path)

    assert [(item.module, item.imported_by) for item in missing] == [
        ("missing_runtime_package", "entry")
    ]


def test_signature_exemption_does_not_apply_in_another_module(tmp_path: Path) -> None:
    checker = _load_checker()
    (tmp_path / "entry.py").write_text(
        "def load_snapshot_bytes():\n"
        "    from cryptography.exceptions import InvalidSignature\n"
        "    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey\n",
        encoding="utf-8",
    )

    missing, _visited = checker.missing_imports(tmp_path)

    assert sorted((item.module, item.imported_by) for item in missing) == [
        ("cryptography.exceptions", "entry"),
        ("cryptography.hazmat.primitives.asymmetric.ed25519", "entry"),
    ]


def test_literal_dynamic_import_inside_a_function_stays_reachable(tmp_path: Path) -> None:
    checker = _load_checker()
    (tmp_path / "entry.py").write_text(
        "def answer():\n"
        "    import importlib\n"
        "    importlib.import_module('lazy_service')\n",
        encoding="utf-8",
    )

    missing, _visited = checker.missing_imports(tmp_path)

    assert [(item.module, item.imported_by) for item in missing] == [
        ("lazy_service", "entry")
    ]


def test_checker_cli_names_a_missing_function_import(tmp_path: Path) -> None:
    (tmp_path / "entry.py").write_text(
        "def answer():\n    import missing_runtime_package\n",
        encoding="utf-8",
    )
    rejected = subprocess.run(
        [sys.executable, str(CHECKER), str(tmp_path)],
        capture_output=True, text=True,
    )
    assert rejected.returncode == 1
    assert "missing missing_runtime_package (imported by entry)" in rejected.stderr


def _keyword(call: ast.Call, name: str) -> ast.keyword | None:
    return next((item for item in call.keywords if item.arg == name), None)


def test_worker_snapshot_callers_stay_on_the_hmac_path() -> None:
    """Preload passes an empty key set; a request load refuses an empty HMAC key."""
    entry_tree = ast.parse((WORKER_ROOT / "src" / "entry.py").read_text(encoding="utf-8"))
    preload = [
        node for node in ast.walk(entry_tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "load_snapshot_bytes"
    ]
    assert len(preload) == 1
    key = _keyword(preload[0], "key")
    public_keys = _keyword(preload[0], "public_keys")
    assert key is not None and isinstance(key.value, ast.Constant) and key.value.value is None
    assert public_keys is not None and isinstance(public_keys.value, ast.Dict)
    assert public_keys.value.keys == []

    service_tree = ast.parse(
        (WORKER_ROOT / "src" / "decide_service.py").read_text(encoding="utf-8")
    )
    loader = next(
        node for node in service_tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "load_snapshot"
    )
    guard = next(stmt for stmt in loader.body if not isinstance(stmt, ast.Expr))
    assert isinstance(guard, ast.If)
    calls = [
        node for node in ast.walk(loader)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "load_snapshot_bytes"
    ]
    assert len(calls) == 1
    passed_key = _keyword(calls[0], "key")
    assert passed_key is not None and isinstance(passed_key.value, ast.Name)
    assert passed_key.value.id == "key"
    assert _keyword(calls[0], "public_keys") is None

    spec = importlib.util.spec_from_file_location(
        "modelspec_decide_service_bundle", WORKER_ROOT / "src" / "decide_service.py",
    )
    service = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(service)
    for empty in (None, "", b""):
        with pytest.raises(service.SnapshotRefusalError, match="not configured"):
            service.load_snapshot(b"unused", key=empty)


_SNAPSHOT_LOADERS = frozenset({
    "load_snapshot_bytes",
    "load_snapshot",
    "load_built_snapshot",
})


def _snapshot_loader_bindings(tree: ast.AST) -> tuple[dict[str, str], set[str]]:
    bound: dict[str, str] = {}
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                local = alias.asname or alias.name
                if alias.name == "load_snapshot_bytes":
                    bound[local] = alias.name
                elif alias.name == "load_built_snapshot":
                    bound[local] = alias.name
                elif alias.name == "load_snapshot" and node.module == "decision.snapshot":
                    bound[local] = alias.name
                elif node.module == "decision" and alias.name == "snapshot":
                    modules.add(local)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "decision.snapshot" and alias.asname:
                    modules.add(alias.asname)
    return bound, modules


def _called_loader(func: ast.expr) -> str | None:
    if not isinstance(func, ast.Call):
        return None
    callee = func.func
    is_getattr = (isinstance(callee, ast.Name) and callee.id == "getattr") or (
        isinstance(callee, ast.Attribute) and callee.attr == "getattr"
    )
    if not is_getattr or len(func.args) < 2:
        return None
    literal = func.args[1]
    if isinstance(literal, ast.Constant) and literal.value in _SNAPSHOT_LOADERS:
        return literal.value
    return None


def _import_module_call(node: ast.expr) -> bool:
    if not isinstance(node, ast.Call):
        return False
    callee = node.func
    if isinstance(callee, ast.Name) and callee.id == "import_module":
        return True
    return (
        isinstance(callee, ast.Attribute)
        and callee.attr == "import_module"
        and isinstance(callee.value, ast.Name)
        and callee.value.id == "importlib"
    )


def _snapshot_call_kind(
    func: ast.expr, bound: dict[str, str], modules: set[str],
) -> str | None:
    reached = _called_loader(func)
    if reached is not None:
        return reached
    if isinstance(func, ast.Name):
        if func.id in ("load_snapshot_bytes", "load_built_snapshot"):
            return func.id
        return bound.get(func.id)
    if not isinstance(func, ast.Attribute):
        return None
    if func.attr in ("load_snapshot_bytes", "load_built_snapshot"):
        return func.attr
    if func.attr != "load_snapshot":
        return None
    if _import_module_call(func.value):
        return "load_snapshot"
    value = func.value
    if (
        isinstance(value, ast.Attribute)
        and value.attr == "snapshot"
        and isinstance(value.value, ast.Name)
        and value.value.id == "decision"
    ):
        return "load_snapshot"
    if isinstance(value, ast.Name) and value.id in modules:
        return "load_snapshot"
    return None


def _generated_worker_packages() -> set[str]:
    """Directories vendor.py writes beside the entry point. Gitignore omits them, and CI has none."""
    prefix = "api/worker/src/"
    names: set[str] = set()
    for line in (REPO_ROOT / ".gitignore").read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith(prefix) and stripped.endswith("/"):
            names.add(stripped.removeprefix(prefix).split("/", 1)[0])
    return names


def _snapshot_sites_in_tree(tree: ast.AST, rel: str) -> list[tuple[str, str, str]]:
    sites: list[tuple[str, str, str]] = []
    bound, modules = _snapshot_loader_bindings(tree)

    def walk(node: ast.AST, scope: str) -> None:
        if isinstance(node, ast.Call):
            kind = _snapshot_call_kind(node.func, bound, modules)
            if kind is not None:
                sites.append((rel, scope, kind))
        for child in ast.iter_child_nodes(node):
            child_scope = (
                child.name
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
                else scope
            )
            walk(child, child_scope)

    walk(tree, "<module>")
    return sites


def _worker_snapshot_call_sites() -> list[tuple[str, str, str]]:
    sites: list[tuple[str, str, str]] = []
    root = WORKER_ROOT / "src"
    generated = _generated_worker_packages()
    for path in sorted(root.rglob("*.py")):
        if path.relative_to(root).parts[0] in generated:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        sites.extend(_snapshot_sites_in_tree(tree, path.relative_to(root).as_posix()))
    return sites


def test_every_worker_snapshot_call_is_a_site_the_hmac_test_checks() -> None:
    assert sorted(_worker_snapshot_call_sites()) == [
        ("decide_service.py", "load_snapshot", "load_snapshot_bytes"),
        ("entry.py", "<module>", "load_snapshot_bytes"),
    ]


@pytest.mark.parametrize(
    ("source", "kind"),
    [
        (
            "from decision.snapshot import load_snapshot_bytes as x\n"
            "x()\n",
            "load_snapshot_bytes",
        ),
        (
            "from decide_service import load_snapshot_bytes as q\n"
            "q()\n",
            "load_snapshot_bytes",
        ),
        (
            "import decision.snapshot as module\n"
            "getattr(module, 'load_snapshot_bytes')()\n",
            "load_snapshot_bytes",
        ),
        (
            "import importlib\n"
            "importlib.import_module('decision.snapshot').load_snapshot()\n",
            "load_snapshot",
        ),
        (
            "import decision.snapshot\n"
            "decision.snapshot.load_built_snapshot()\n",
            "load_built_snapshot",
        ),
    ],
    ids=["aliased-import", "aliased-import-other-module", "getattr", "importlib", "unsigned-loader"],
)
def test_the_snapshot_census_reports_an_indirect_loader_call(source: str, kind: str) -> None:
    assert _snapshot_sites_in_tree(ast.parse(source), "probe.py") == [
        ("probe.py", "<module>", kind),
    ]


def test_decision_startup_does_not_load_the_full_card_schema() -> None:
    result = subprocess.run(
        [sys.executable, "-c", "import sys; import decision.model; "
         "from decision.registry import default; default(); "
         "assert 'schema.card' not in sys.modules"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
