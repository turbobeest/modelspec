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

# Lexical scopes the Worker does not execute. The path includes every enclosing
# class and function, so a nested function does not inherit a builder's exclusion.
NON_WORKER_SCOPES = {
    ("decision.snapshot", ("_Compiler",)),
    ("decision.snapshot", ("collect_repo",)),
    ("decision.snapshot", ("build_from_repo",)),
    ("decision.snapshot", ("_load_ed25519_private_key",)),
    ("decision.snapshot", ("env_ed25519_signer",)),
    ("decision.snapshot", ("verify_vocabulary",)),
    ("decision.normalise", ("normalise_document",)),
    ("pipeline.ranking", ("main",)),
}

# Imported only when load_snapshot_bytes is given a nonempty Ed25519 public-key
# set. Preload passes public_keys={} and a request load passes an HMAC key.
HMAC_ONLY_IMPORTS = {
    "cryptography.exceptions",
    "cryptography.hazmat.primitives.asymmetric.ed25519",
}


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

    def visit(statements: list[ast.stmt], scope: tuple[str, ...] = ()) -> None:
        for node in statements:
            if isinstance(node, ast.Import):
                found.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                base = _absolute_from_import(module, path, node)
                if (
                    module == "decision.snapshot"
                    and scope == ("load_snapshot_bytes",)
                    and base in HMAC_ONLY_IMPORTS
                ):
                    continue
                if base:
                    found.add(base)
                for alias in node.names:
                    candidate = f"{base}.{alias.name}" if base else alias.name
                    if candidate in known:
                        found.add(candidate)
            elif isinstance(node, ast.If):
                # An annotation-only import is not executed at module load.
                if isinstance(node.test, ast.Name) and node.test.id == "TYPE_CHECKING":
                    visit(node.orelse, scope)
                else:
                    visit(node.body, scope)
                    visit(node.orelse, scope)
            elif isinstance(node, (ast.Try, ast.TryStar)):
                visit(node.body, scope)
                visit(node.orelse, scope)
                visit(node.finalbody, scope)
                for handler in node.handlers:
                    visit(handler.body, scope)
            elif isinstance(node, (ast.With, ast.AsyncWith)):
                visit(node.body, scope)
            elif isinstance(node, (ast.For, ast.AsyncFor, ast.While)):
                visit(node.body, scope)
                visit(node.orelse, scope)
            elif isinstance(node, ast.Match):
                for case in node.cases:
                    visit(case.body, scope)
            elif isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                nested = (*scope, node.name)
                if (module, nested) not in NON_WORKER_SCOPES:
                    visit(node.body, nested)

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
            if imported_path is None and imported == "bundled_data":
                # This generated module exists only in private builds. --require-data
                # enforces its presence when checking that deployment artifact.
                continue
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
    parser.add_argument("--require-data", action="store_true", help="Require the private bundled catalogue.")
    args = parser.parse_args()
    missing, visited = missing_imports(args.bundle)
    missing_files = missing_vendored_files(args.bundle)
    if args.require_data and not (args.bundle / "bundled_data.py").is_file():
        missing_files.append(Path("bundled_data.py"))
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
