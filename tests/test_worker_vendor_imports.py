"""Every repository module the Worker bundle imports must be in the bundle.

`api/worker/vendor.py` copies an explicit list of files. An import the list
misses only fails at runtime in the Worker, and only on the path that reaches
it: `decision/capability.py` was imported lazily for domain objectives, so
every other request worked and those returned Cloudflare error 1101. This walks
every import in every vendored module, including imports inside functions.
"""

from __future__ import annotations

import ast
import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("modelspec_worker_vendor", ROOT / "api" / "worker" / "vendor.py")
vendor = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vendor)

PACKAGES = {"api", "decision", "pipeline", "release_signals", "schema"}

#: Imports that only build-time code reaches, so the Worker never runs them.
BUILD_TIME = {
    # collect_repo() reads the repository to build a snapshot; the Worker
    # only loads the published one.
    ("decision/snapshot.py", "pipeline.load"),
    ("decision/snapshot.py", "decision.sources"),
    # Lab jurisdiction is applied while the snapshot is built. The Worker
    # loads the published snapshot and never reads registry/labs.yaml.
    ("decision/snapshot.py", "decision.labs"),
    # The v1 graph export and a type annotation; see the comment at the import.
    ("pipeline/ranking.py", "schema.graph"),
    ("pipeline/ranking.py", "schema.card"),
    # Hardware arithmetic is used at runtime; graph is only a type annotation.
    ("pipeline/hardware.py", "schema.graph"),
}


def _module_file(name: str) -> Path | None:
    parts = name.split(".")
    for candidate in (Path(*parts).with_suffix(".py"), Path(*parts) / "__init__.py"):
        if (ROOT / candidate).exists():
            return candidate
    return None


def _imports(path: Path) -> set[str]:
    tree = ast.parse((ROOT / path).read_text(encoding="utf-8"))
    package = ".".join(path.with_suffix("").parts[:-1])
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            base = node.module or ""
            if node.level:
                parent = package.split(".")[: len(package.split(".")) - node.level + 1]
                base = ".".join([*parent, base] if base else parent)
            names.add(base)
            # `from decision import capability` names a module, not an attribute.
            names.update(f"{base}.{alias.name}" for alias in node.names)
    return {n for n in names if n.split(".")[0] in PACKAGES}


def test_every_imported_repository_module_is_vendored():
    vendored = set(vendor.SOURCES)
    missing = set()
    for path in sorted(p for p in vendored if p.suffix == ".py"):
        for name in _imports(path):
            module = _module_file(name)
            if module is not None and module not in vendored and (str(path), name) not in BUILD_TIME:
                missing.add(f"{path} imports {name} ({module})")
    assert not missing, "add to SOURCES in api/worker/vendor.py:\n" + "\n".join(sorted(missing))


def test_worker_bundle_has_no_pdf_extractor_or_pypdf_imports(tmp_path: Path):
    bundle = vendor.build(tmp_path / "bundle")
    forbidden = set()
    for path in bundle.rglob("*.py"):
        relative = path.relative_to(bundle)
        if relative == Path("decision/pdf_text.py"):
            forbidden.add(str(relative))
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            else:
                continue
            for name in names:
                if name == "decision.pdf_text" or name.split(".")[0] == "pypdf":
                    forbidden.add(f"{relative} imports {name}")
    assert not forbidden, "PDF extraction belongs outside the Worker bundle:\n" + "\n".join(
        sorted(forbidden)
    )


def test_worker_pdf_recipe_fails_closed_without_importing_an_offline_reader(tmp_path: Path):
    bundle = vendor.build(tmp_path / "bundle")
    script = """
import pathlib
import sys
sys.path.insert(0, sys.argv[1])
import decision.normalise as normalise
assert pathlib.Path(normalise.__file__).is_relative_to(pathlib.Path(sys.argv[1]))
try:
    normalise.normalise_document(b'%PDF-1.7 malformed', normalise.NORMALISERS['pdf-pypdf-6.19.0-v1'])
except normalise.UnsupportedContentError as error:
    assert error.kind == 'pdf_extractor_unavailable', error.kind
else:
    raise AssertionError('The Worker accepted a PDF without an extractor')
assert 'decision.pdf_text' not in sys.modules
assert 'decision.source_document' not in sys.modules
assert not any(name == 'pypdf' or name.startswith('pypdf.') for name in sys.modules)
"""
    result = subprocess.run(
        [sys.executable, "-I", "-c", script, str(bundle)],
        cwd=bundle,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
