"""Run the new registry boundaries against the pre-MODEL-433 implementations.

This leaves the checkout untouched. A nonzero pytest result is expected.
"""

import importlib
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile

import pytest


root = Path(__file__).resolve().parents[4]
base = "3c8042a11aa47e8577559e01f71379119bda2cec"
with tempfile.TemporaryDirectory(prefix="baseline-", dir="/tmp/model-433-scratch") as directory:
    for name in ("decision.model", "decision.sources", "scripts.price_reread"):
        parent, _, attribute = name.rpartition(".")
        package = importlib.import_module(parent)
        relative = name.replace(".", "/") + ".py"
        path = Path(directory) / (attribute + ".py")
        path.write_bytes(subprocess.check_output(
            ["git", "show", f"{base}:{relative}"], cwd=root))
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        setattr(package, attribute, module)
        spec.loader.exec_module(module)
    raise SystemExit(pytest.main([
        "-q", "-p", "no:cacheprovider",
        str(root / "tests/test_rendered_interactions.py")
        + "::test_registry_loads_a_bounded_data_only_recipe",
        str(root / "tests/test_price_reread.py")
        + "::test_render_to_and_live_reread_use_the_registry_recipe_for_a_legacy_source",
    ]))
