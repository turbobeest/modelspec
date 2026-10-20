"""Historical xAI capture commands must refuse before browser or disk access."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_xai_capture_helper_is_retired_before_browser_or_output(tmp_path):
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node is required to check the historical capture helper")

    marker = tmp_path / "browser-attempted.txt"
    browser = tmp_path / "synthetic-browser.mjs"
    browser.write_text(
        "import { writeFileSync } from 'node:fs';\n"
        f"const marker = {json.dumps(str(marker))};\n"
        "writeFileSync(marker, 'imported');\n"
        "export const chromium = { launch: async () => {\n"
        "  writeFileSync(marker, 'launch attempted');\n"
        "  throw new Error('Synthetic browser refuses all navigation');\n"
        "}};\n"
    )
    loader = tmp_path / "offline-loader.mjs"
    loader.write_text(
        "export async function resolve(specifier, context, nextResolve) {\n"
        "  if (specifier.endsWith('/playwright/index.mjs')) {\n"
        f"    return {{url: {json.dumps(browser.as_uri())}, shortCircuit: true}};\n"
        "  }\n"
        "  if (!context.parentURL || ['node:fs', 'node:fs/promises',\n"
        "      'node:zlib', 'node:crypto'].includes(specifier)) {\n"
        "    return nextResolve(specifier, context);\n"
        "  }\n"
        "  throw new Error('Offline test rejected an unexpected import');\n"
        "}\n"
    )
    output = tmp_path / "capture"
    result = subprocess.run(
        [node, "--experimental-loader", str(loader),
         str(ROOT / "docs/evidence/g2-ios/MODEL-367/capture.mjs"),
         str(output), "pricing=https://x.ai/pricing"],
        cwd=ROOT, capture_output=True, text=True, timeout=15,
    )

    assert not marker.exists(), f"Browser stub was reached: {marker.read_text()}"
    assert not output.exists()
    assert result.returncode == 1
    assert "retired" in result.stderr.lower()
    assert "cite-only" in result.stderr.lower()
