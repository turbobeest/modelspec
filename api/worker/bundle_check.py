"""Check the import graph Wrangler wrote into a Worker bundle."""

from __future__ import annotations

import argparse
import ast
import runpy
import sys
from collections import deque
from dataclasses import dataclass
from pathlib import Path

RUNTIME_MODULES = {"_pyodide", "js", "pyodide"}


@dataclass(frozen=True)
class MissingImport:
    module: str
    imported_by: str


def _module_name(root: Path, path: Path) -> str:
    relative = path.relative_to(root)
    parts = list(relative.with_suffix("").parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def _module_index(bundle: Path) -> dict[str, Path]:
    modules: dict[str, Path] = {}
    vendor = bundle / "python_modules"
    for root in (bundle, vendor):
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*.py")):
            if root == bundle and vendor in path.parents:
                continue
            name = _module_name(root, path)
            if name:
                modules.setdefault(name, path)
    return modules


def _absolute_from_import(module: str, path: Path, node: ast.ImportFrom) -> str:
    if node.level == 0:
        return node.module or ""
    package = module.split(".")
    if path.name != "__init__.py":
        package.pop()
    trim = node.level - 1
    if trim:
        package = package[:-trim]
    if node.module:
        package.extend(node.module.split("."))
    return ".".join(package)


def _imports(path: Path, module: str, known: set[str]) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: set[str] = set()
    def visit(statements: list[ast.stmt]) -> None:
        for node in statements:
            if isinstance(node, ast.Import):
                found.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                base = _absolute_from_import(module, path, node)
                if base:
                    found.add(base)
                for alias in node.names:
                    candidate = f"{base}.{alias.name}" if base else alias.name
                    if candidate in known:
                        found.add(candidate)
            elif isinstance(node, ast.If):
                # An annotation-only import is not executed at module load.
                if isinstance(node.test, ast.Name) and node.test.id == "TYPE_CHECKING":
                    visit(node.orelse)
                else:
                    visit(node.body)
                    visit(node.orelse)
            elif isinstance(node, (ast.Try, ast.TryStar)):
                visit(node.body)
                visit(node.orelse)
                visit(node.finalbody)
                for handler in node.handlers:
                    visit(handler.body)
            elif isinstance(node, (ast.With, ast.AsyncWith)):
                visit(node.body)
            elif isinstance(node, ast.ClassDef):
                visit(node.body)

    visit(tree.body)

    # Literal lazy imports are part of the Worker's graph even when the call is
    # inside a route-specific function, as decide_service is in entry.py.
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and node.args
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, str)
        ):
            function = node.func
            is_import_module = (
                isinstance(function, ast.Name) and function.id == "import_module"
            ) or (
                isinstance(function, ast.Attribute)
                and isinstance(function.value, ast.Name)
                and function.value.id == "importlib"
                and function.attr == "import_module"
            )
            if is_import_module:
                found.add(node.args[0].value)
    return found


def missing_imports(bundle: Path) -> tuple[list[MissingImport], set[str]]:
    """Return unresolved imports reachable from the built ``entry.py``."""
    bundle = bundle.resolve()
    modules = _module_index(bundle)
    entry = bundle / "entry.py"
    if not entry.is_file():
        return [MissingImport("entry", "<bundle>")], set()

    stdlib = set(sys.stdlib_module_names) | {"__future__"}
    queue = deque([("entry", entry)])
    visited: set[str] = set()
    missing: set[MissingImport] = set()

    while queue:
        module, path = queue.popleft()
        if module in visited:
            continue
        visited.add(module)
        for imported in _imports(path, module, set(modules)):
            top_level = imported.split(".", 1)[0]
            if top_level in stdlib or top_level in RUNTIME_MODULES:
                continue
            imported_path = modules.get(imported)
            if imported_path is None:
                missing.add(MissingImport(imported, module))
                continue
            # Third-party packages are present once their top-level module
            # resolves. Walking their optional and platform-specific imports
            # would test the dependency itself instead of this Worker bundle.
            if "python_modules" in imported_path.parts and top_level not in {
                "api", "decision", "pipeline", "schema"
            }:
                continue
            resolved_name = _module_name(
                bundle / "python_modules"
                if bundle / "python_modules" in imported_path.parents
                else bundle,
                imported_path,
            )
            parts = resolved_name.split(".")
            for index in range(1, len(parts)):
                parent = ".".join(parts[:index])
                if parent_path := modules.get(parent):
                    queue.append((parent, parent_path))
            queue.append((resolved_name, imported_path))

    return sorted(missing, key=lambda item: (item.module, item.imported_by)), visited


def missing_vendored_files(bundle: Path) -> list[Path]:
    """Return source-manifest paths absent from Wrangler's built output."""
    vendor = runpy.run_path(str(Path(__file__).with_name("vendor.py")))
    targets = vendor["SOURCES"].values()
    return sorted(
        target
        for target in targets
        if not (bundle / target).is_file()
        and not (bundle / "python_modules" / target).is_file()
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path, help="Wrangler --outdir directory")
    args = parser.parse_args()
    missing, visited = missing_imports(args.bundle)
    missing_files = missing_vendored_files(args.bundle)
    if missing:
        for item in missing:
            print(f"missing {item.module} (imported by {item.imported_by})", file=sys.stderr)
    if missing_files:
        for path in missing_files:
            print(f"missing vendored file {path}", file=sys.stderr)
    if missing or missing_files:
        return 1
    print(f"bundle import graph complete: {len(visited)} local modules reachable from entry.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
