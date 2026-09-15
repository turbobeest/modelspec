"""MODEL-60 runner: one run at a time, resumable, stops a setup on rate limits.

    python -m scripts.latency.runner --checkout <polyglot-benchmark> \
        --sandbox-root <tmp dir> --mode smoke

Records: benchmarks/_latency/runs/<mode>.jsonl. State: benchmarks/_latency/state.json.
Raw timestamped streams go to <sandbox-root>/raw/ and are never committed.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import threading
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from scripts.latency import tasks as T
from scripts.latency.parsers import PARSERS

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "benchmarks" / "_latency"
HOST_ID = "apple_macbook_pro_m5_max"
OLLAMA = "http://100.127.37.30:11434"
RUN_TIMEOUT_S = 570
RATE_LIMIT_RE = re.compile(
    r"rate.?limit|usage.?limit|quota|\b429\b|\b402\b|too many requests|limit reached|balance exhausted|payment required",
    re.I)
# Environment passed to every CLI. Nothing else from the parent survives:
# no SSH_AUTH_SOCK, GH_TOKEN, OP_*, *_API_KEY, ANTHROPIC_BASE_URL.
ENV_ALLOW = ("PATH", "HOME", "USER", "LOGNAME", "LANG", "LC_ALL", "TERM", "SHELL")
FORBIDDEN_ENV = re.compile(r"API_KEY|TOKEN|SECRET|PASSWORD|SSH_AUTH|^OP_|BASE_URL", re.I)

CLAUDE_SETTINGS = {
    "sandbox": {"enabled": True, "autoAllowBashIfSandboxed": True, "allowUnsandboxedCommands": False},
    "permissions": {"deny": [f"{v}(~/{p}/**)" for v in ("Read", "Edit") for p in (
        ".ssh", ".aws", ".config", ".gnupg", ".codex", ".grok", ".gemini", ".claude", "dev", "Library")]},
}

SETUPS: dict[str, dict] = {
    "claude-code/opus-5": {"harness": "claude", "model": "claude-opus-5", "inference_host": "anthropic", "parser": "claude"},
    "codex/gpt-5.6": {"harness": "codex", "model": None, "inference_host": "openai", "parser": None,
                      "blocked": "model id ambiguous: codex lists gpt-5.6-sol, gpt-5.6-terra, gpt-5.6-luna"},
    "grok/grok-4.6": {"harness": "grok", "model": "grok-4.6", "inference_host": "xai", "parser": "unverified"},
    "gemini/gemini-3.8-flash": {"harness": "gemini", "model": None, "inference_host": "google", "parser": None,
                                "blocked": "gemini CLI auth is gemini-api-key (not a subscription login); no gemini-3.8 id found in the CLI"},
}
for _m in ("qwen3:32b", "gemma4:31b", "gemma4:26b", "mistral-large:123b-instruct-2411-q4_K_M",
           "qwen3:30b-a3b-instruct-2507-q4_K_M"):
    SETUPS[f"opencode/{_m}"] = {"harness": "opencode", "model": _m, "inference_host": "nvidia_dgx_spark",
                                "parser": "opencode", "local": True}


def sandbox_env() -> dict:
    env = {k: os.environ[k] for k in ENV_ALLOW if k in os.environ}
    assert not any(FORBIDDEN_ENV.search(k) for k in env), "secret-looking env var leaked"
    return env


def build_command(setup: dict, prompt: str, workdir: Path) -> list[str]:
    h = setup["harness"]
    if h == "claude":
        return ["claude", "-p", prompt, "--model", setup["model"], "--output-format", "stream-json", "--verbose",
                "--dangerously-skip-permissions", "--no-session-persistence", "--strict-mcp-config",
                "--setting-sources", "project", "--settings", json.dumps(CLAUDE_SETTINGS)]
    if h == "grok":
        return ["grok", "-p", prompt, "-m", setup["model"], "--output-format", "streaming-json",
                "--always-approve", "--sandbox", "workspace", "--cwd", str(workdir), "--disable-web-search"]
    if h == "opencode":
        # Run-scoped: HOME is a fresh dir inside the run sandbox, so the user's
        # ~/.config/opencode and any stored provider auth are never loaded.
        # sandbox-exec denies reading /Users (except the opencode binary) and
        # writing anywhere but the run dir. Network stays open for the Spark.
        exe = str(Path(shutil.which("opencode")).resolve())
        return ["sandbox-exec", "-p", opencode_profile(workdir, Path(exe)), exe, "run", prompt,
                "-m", f"spark-ollama/{setup['model']}", "--format", "json", "--auto", "--pure", "--dir", str(workdir)]
    raise NotImplementedError(f"no verified adapter for {h}")


def opencode_config(model: str) -> dict:
    return {
        "$schema": "https://opencode.ai/config.json",
        "autoupdate": False, "share": "disabled",
        "provider": {"spark-ollama": {"npm": "@ai-sdk/openai-compatible", "name": "DGX Spark Ollama",
                                     "options": {"baseURL": f"{OLLAMA}/v1"}, "models": {model: {"name": model}}}},
        "permission": {"external_directory": "deny", "webfetch": "deny"},
    }


def opencode_profile(workdir: Path, exe: Path) -> str:
    run_root = workdir.parent
    return (
        "(version 1)(allow default)"
        '(deny file-read* (subpath "/Users"))'
        f'(allow file-read* (subpath "{exe.parent.parent}"))'
        '(deny file-write* (subpath "/"))'
        f'(allow file-write* (subpath "{run_root}") (subpath "/private/var/folders") (subpath "/private/tmp/opencode") (literal "/dev/null") (literal "/dev/tty"))'
    )


def harness_env(setup: dict, workdir: Path) -> dict:
    env = sandbox_env()
    if setup["harness"] == "opencode":
        home = workdir.parent / (workdir.name + "-home")
        (home / ".config" / "opencode").mkdir(parents=True, exist_ok=True)
        env.update(HOME=str(home), XDG_CONFIG_HOME=str(home / ".config"), XDG_DATA_HOME=str(home / ".local/share"),
                   XDG_CACHE_HOME=str(home / ".cache"), XDG_STATE_HOME=str(home / ".local/state"),
                   OPENCODE_CONFIG_CONTENT=json.dumps(opencode_config(setup["model"])),
                   OPENCODE_DISABLE_AUTOUPDATE="1", OPENCODE_DISABLE_CLAUDE_CODE="1",
                   OPENCODE_DISABLE_PROJECT_CONFIG="1", OPENCODE_DISABLE_MODELS_FETCH="1")
    return env


def cli_version(harness: str) -> str:
    out = subprocess.run([harness, "--version"], capture_output=True, text=True, timeout=30)
    return (out.stdout or out.stderr).strip().splitlines()[0]


def ollama_models() -> set[str]:
    with urllib.request.urlopen(f"{OLLAMA}/api/tags", timeout=10) as r:
        return {m["name"] for m in json.load(r)["models"]}


def run_process(cmd: list[str], cwd: Path, raw_path: Path, env: dict | None = None) -> dict:
    """Timestamp every stdout line on receipt. Returns events and exit status."""
    events, stderr_chunks = [], []
    t0 = time.monotonic()
    proc = subprocess.Popen(cmd, cwd=cwd, env=env or sandbox_env(), stdin=subprocess.DEVNULL,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    err_thread = threading.Thread(target=lambda: stderr_chunks.append(proc.stderr.read()), daemon=True)
    err_thread.start()
    timer = threading.Timer(RUN_TIMEOUT_S, proc.kill)
    timer.start()
    with raw_path.open("w") as raw:
        for line in proc.stdout:
            now = time.monotonic() - t0
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                ev = {"_nonjson": line.rstrip()[:500]}
            events.append((now, ev))
            raw.write(json.dumps({"t": round(now, 4), "event": ev}) + "\n")
    rc = proc.wait()
    timed_out = not timer.is_alive() and rc != 0
    timer.cancel()
    err_thread.join(timeout=5)
    return {"events": events, "end": time.monotonic() - t0, "rc": rc, "timed_out": timed_out,
            "stderr": "".join(stderr_chunks)}


def classify_limit(text: str) -> str | None:
    """The matched rate/usage-limit phrase, or None."""
    m = RATE_LIMIT_RE.search(text)
    return m.group(0) if m else None


def load_state(path: Path) -> dict:
    return json.loads(path.read_text()) if path.exists() else {"done": {}, "stopped_setups": {}}


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkout", type=Path, required=True)
    ap.add_argument("--sandbox-root", type=Path, required=True)
    ap.add_argument("--mode", choices=["smoke", "full"], default="smoke")
    ap.add_argument("--setup", action="append", help="limit to these setup names")
    args = ap.parse_args(argv)

    root = args.sandbox_root.resolve()
    home = Path.home().resolve()
    if root == home or str(root).startswith(str(home) + os.sep) or not str(root).startswith(("/private/tmp", "/tmp")):
        raise SystemExit(f"refusing sandbox root outside /tmp: {root}")
    (root / "raw").mkdir(parents=True, exist_ok=True)

    all_tasks = T.select_tasks(args.checkout)
    set_hash = T.task_set_hash(all_tasks)
    tasks = [t for t in all_tasks if t.task_id == T.SMOKE_TASK] if args.mode == "smoke" else all_tasks
    reps = 1 if args.mode == "smoke" else 3
    state_path = OUT / ("state.json" if args.mode == "full" else "smoke-state.json")
    state = load_state(state_path)
    out = OUT / "runs" / f"{args.mode}.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)

    names = args.setup or list(SETUPS)
    for name in names:
        setup = SETUPS[name]
        for rep in range(1, reps + 1):
            for task in tasks:
                key = f"{name}|{task.task_id}|{rep}"
                if key in state["done"] or name in state["stopped_setups"]:
                    continue
                record = {"setup": name, "harness": setup["harness"], "model_id": setup["model"],
                          "host_id": HOST_ID, "inference_host": setup["inference_host"],
                          "task_set": T.TASK_SET_NAME, "task_set_commit": T.TASK_SET_COMMIT,
                          "task_set_hash": set_hash, "task_id": task.task_id, "repetition": rep}
                skip = setup.get("blocked")
                if not skip and setup.get("local"):
                    try:
                        if setup["model"] not in ollama_models():
                            skip = f"model not present on Spark Ollama ({OLLAMA}/api/tags)"
                    except OSError as exc:
                        skip = f"Ollama unreachable: {exc}"
                if not skip and setup["parser"] is None:
                    skip = "no verified adapter/parser"
                if skip:
                    record.update(status="skipped", error=skip)
                    _write(out, record, state, state_path, key)
                    continue
                record.update(run_record(setup, task, root, key))
                _write(out, record, state, state_path, key)
                if record["status"] == "rate_limited":
                    state["stopped_setups"][name] = record["error"]
                    state_path.write_text(json.dumps(state, indent=2) + "\n")


def run_record(setup: dict, task: T.Task, root: Path, key: str) -> dict:
    run_id = re.sub(r"[^A-Za-z0-9._-]", "_", key) + "-" + str(int(time.time()))
    workdir = root / run_id
    T.prepare_workdir(task, workdir)
    cmd = build_command(setup, T.build_prompt(task), workdir)
    start = datetime.now(timezone.utc)
    proc = run_process(cmd, workdir, root / "raw" / f"{run_id}.jsonl", harness_env(setup, workdir))
    end = datetime.now(timezone.utc)
    timing = PARSERS[setup["parser"]](proc["events"], proc["end"])
    graded = T.grade(task, workdir)
    blob = proc["stderr"] + "".join(json.dumps(e) for _, e in proc["events"][-5:])
    if proc["timed_out"]:
        status, error = "timeout", f"killed after {RUN_TIMEOUT_S}s"
    elif proc["rc"] != 0 and classify_limit(blob):
        status, error = "rate_limited", classify_limit(blob)
    elif proc["rc"] != 0:
        status, error = "error", f"exit {proc['rc']}: {proc['stderr'].strip()[-300:]}"
    else:
        status, error = "ok", None
    return {"harness_version": cli_version(setup["harness"]), "run_id": run_id,
            "start_utc": start.isoformat(), "end_utc": end.isoformat(), "total_s": round(proc["end"], 3),
            **timing.as_dict(), **graded, "status": status, "error": error, "exit_code": proc["rc"],
            "timing_basis": "harness line-receipt timestamps on CLI stdout", "concurrency": 1}


def _write(out: Path, record: dict, state: dict, state_path: Path, key: str) -> None:
    with out.open("a") as fh:
        fh.write(json.dumps(record) + "\n")
    state["done"][key] = record["status"]
    state_path.write_text(json.dumps(state, indent=2) + "\n")
    print(f"{key}: {record['status']} {record.get('total_s', '')} {record.get('error') or ''}", flush=True)


if __name__ == "__main__":
    main()
