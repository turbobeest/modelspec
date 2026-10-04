"""Start a subscription job with a clean environment plus the ModelSpec key.

Run it under 1Password, which injects MODELSPEC_API_KEY into this process only:

    op run --env-file=qa/subscription.env.op -- \
      /Users/terbeest/dev/modelspec/.venv/bin/python -m qa.run_with_modelspec_key \
      scenarios --cli claude --cli codex --cli grok

The key is read from this process's environment and passed to the job by execve,
never in argv. Everything else is dropped, including op's own variables and any
vendor key the shell exports. A sandbox (test_) key is refused: its synthetic
results are not a measurement.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

KEY = "MODELSPEC_API_KEY"
PASSED = ("HOME", "PATH", "TERM", "LANG")


def job_environment(incoming: dict) -> dict:
    key = incoming.get(KEY, "")
    if not key or key.startswith("op://"):
        raise ValueError(f"{KEY} is not set; run this under op run --env-file=…")
    if key.startswith("test_"):
        raise ValueError(f"Refusing a test_ sandbox {KEY}: its results are synthetic")
    env = {name: incoming[name] for name in PASSED if incoming.get(name)}
    env.setdefault("LANG", "en_US.UTF-8")
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1])
    env[KEY] = key
    return env


def main(argv: list[str]) -> None:
    try:
        env = job_environment(dict(os.environ))
    except ValueError as exc:
        print(exc, file=sys.stderr)
        raise SystemExit(2) from None
    os.execve(sys.executable, [sys.executable, "-m", "qa.subscription_jobs", *argv], env)


if __name__ == "__main__":
    main(sys.argv[1:])
