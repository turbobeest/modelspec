"""Run the four offline decide browser variants without changing web/dist.

Run after web/npm ci and the shared prerequisite build. Generated corpus,
variant builds, configuration, and browser traces remain in this worker's
scratch directory. The existing repository tests run without source edits.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import socket
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
WEB = ROOT / "web"
SCRATCH = ROOT / "tests/.scratch-model402-service/browser-resumed"
NODE_DIR = Path("/Users/terbeest/.nvm/versions/node/v22.22.3/bin")
PYTHON = "/Users/terbeest/dev/modelspec/.venv/bin/python"
PORT = 4179


def dist_hashes() -> dict[str, str]:
    return {
        str(path.relative_to(WEB / "dist")): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted((WEB / "dist").rglob("*"))
        if path.is_file()
    }


def main() -> int:
    SCRATCH.mkdir(parents=True, exist_ok=True)
    (SCRATCH.parent / ".gitignore").write_text("*\n", encoding="utf-8")
    modules = SCRATCH / "node_modules"
    if not modules.exists():
        modules.symlink_to(WEB / "node_modules", target_is_directory=True)
    env = dict(os.environ)
    for key in (
        "MODELSPEC_DECIDE_URL", "MODELSPEC_PRICING_URL", "MODELSPEC_API_KEY",
        "ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY",
    ):
        env.pop(key, None)
    env.update(
        PATH=str(NODE_DIR) + ":" + str(Path(PYTHON).parent) + ":" + env.get("PATH", ""),
        PYTHONPATH=str(ROOT), CI="true", MODELSPEC_CORPUS_REQUIRED="1",
        MODELSPEC_TEST_PYTHON=PYTHON, MODELSPEC_PYTHON=PYTHON,
        MODELSPEC_CORPUS_DIR=str(SCRATCH / "corpus"),
        VITE_TURNSTILE_SITE_KEY="public-browser-test-key",
    )
    commands: list[dict] = []

    def run(name: str, command: list[str], cwd: Path, context: dict | None = None) -> int:
        print("Running " + name, flush=True)
        with (HERE / (name + ".txt")).open("w", encoding="utf-8") as log:
            log.write("CWD: " + str(cwd) + "\nCOMMAND: " + shlex.join(command) + "\n")
            log.write("CONTEXT: " + json.dumps(context or {}, sort_keys=True) + "\n")
            log.flush()
            result = subprocess.run(command, cwd=cwd, env=env, stdout=log,
                                    stderr=subprocess.STDOUT)
            log.write("\nEXIT_CODE=" + str(result.returncode) + "\n")
        commands.append({"name": name, "command": command, "cwd": str(cwd),
                         "context": context or {}, "exit_code": result.returncode})
        (HERE / "commands.json").write_text(json.dumps(commands, indent=2) + "\n")
        print(name + ": exit " + str(result.returncode), flush=True)
        return result.returncode

    before = dist_hashes()
    assert "decide.html" in before, "root must complete the shared prerequisite build first"
    config = SCRATCH / "playwright.isolated.config.ts"
    config.write_text(
        'import base from ' + json.dumps(str(WEB / "playwright.corpus.config.ts")) + ';\n'
        'import { defineConfig } from "@playwright/test";\n'
        'const command = process.env.MODELSPEC_BROWSER_PREVIEW_COMMAND ?? "";\n'
        'export default defineConfig({\n'
        '  ...base, testDir: ' + json.dumps(str(WEB / "browser-tests")) + ',\n'
        '  use: { ...base.use, baseURL: "http://127.0.0.1:' + str(PORT) + '/decide.html" },\n'
        '  webServer: { command, cwd: ' + json.dumps(str(WEB)) + ',\n'
        '    url: "http://127.0.0.1:' + str(PORT) + '/decide.html", reuseExistingServer: false },\n'
        '});\n',
        encoding="utf-8",
    )
    if run("corpus", [PYTHON, "-m", "tests.corpus", "decisions", "--out",
                      str(SCRATCH / "corpus"), "--cache", str(SCRATCH / "corpus-cache")], ROOT):
        return 1
    failures = []
    for human, visit in (("false", "false"), ("false", "true"),
                         ("true", "false"), ("true", "true")):
        name = "human-" + human + "-visit-" + visit
        output = SCRATCH / name
        env.update(VITE_HUMAN_GATE_ENABLED=human, VITE_VISIT_GATE_ENABLED=visit,
                   MODELSPEC_BROWSER_DIST=str(output / "dist"),
                   MODELSPEC_BROWSER_OUTPUT=str(output / "test-results"),
                   MODELSPEC_BROWSER_PREVIEW_COMMAND=shlex.join([
                       str(NODE_DIR / "node"), str(WEB / "node_modules/vite/bin/vite.js"),
                       "preview", "--host", "127.0.0.1", "--port", str(PORT), "--strictPort",
                       "--outDir", str(output / "dist"),
                   ]))
        context = {key: env[key] for key in (
            "VITE_HUMAN_GATE_ENABLED", "VITE_VISIT_GATE_ENABLED", "VITE_TURNSTILE_SITE_KEY",
            "MODELSPEC_CORPUS_DIR", "MODELSPEC_CORPUS_REQUIRED", "MODELSPEC_BROWSER_DIST",
            "MODELSPEC_BROWSER_OUTPUT", "MODELSPEC_TEST_PYTHON", "CI",
        )}
        built = run(name + "-build", [str(NODE_DIR / "node"),
                    str(WEB / "node_modules/vite/bin/vite.js"), "build", "--outDir",
                    str(output / "dist")], WEB, context)
        if built:
            failures.append(name + "-build")
            continue
        for stage, command in (
            ("vitest", [str(NODE_DIR / "node"), str(WEB / "node_modules/vitest/vitest.mjs"), "run"]),
            ("playwright", [str(NODE_DIR / "node"), str(WEB / "node_modules/@playwright/test/cli.js"),
                            "test", "--config=" + str(config), "--workers=2", "--reporter=list"]),
        ):
            if run(name + "-" + stage, command, WEB, context):
                failures.append(name + "-" + stage)
    after = dist_hashes()
    rows = []
    for human, visit in (("false", "false"), ("false", "true"),
                         ("true", "false"), ("true", "true")):
        variant = "human-" + human + "-visit-" + visit
        vitest_path = HERE / (variant + "-vitest.txt")
        browser_path = HERE / (variant + "-playwright.txt")
        if not vitest_path.exists() or not browser_path.exists():
            continue
        vitest, browser = vitest_path.read_text(), browser_path.read_text()
        test_counts = re.findall(r"Tests\s+([^\n]+)", vitest)
        file_counts = re.findall(r"Test Files\s+([^\n]+)", vitest)
        passed = re.findall(r"(\d+) passed \(", browser)
        skipped = re.findall(r"(\d+) skipped", browser)
        rows.append({"human_gate": human, "visit_gate": visit,
                     "vitest_tests": test_counts[-1].strip() if test_counts else None,
                     "vitest_files": file_counts[-1].strip() if file_counts else None,
                     "playwright_passed": int(passed[-1]) if passed else None,
                     "playwright_skipped": int(skipped[-1]) if skipped else 0})
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", PORT))
    summary = {"failures": failures, "shared_web_dist_unchanged": before == after,
               "shared_web_dist_files": len(before), "commands": commands,
               "results": rows, "preview_port_4179_released": True}
    (HERE / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({key: value for key, value in summary.items() if key != "commands"}, indent=2))
    return int(bool(failures) or before != after)


if __name__ == "__main__":
    raise SystemExit(main())
