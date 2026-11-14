"""Run the production Worker deploy and retry only a transient Cloudflare failure (MODEL-487).

The deploy job reads the private data repository and everything it prints is
public. This wrapper therefore captures the deploy command's combined output,
classifies it, and prints nothing of it except as follows:

* An attempt that is retried prints one fixed line and no tool text.
* The last attempt, whether it passed or failed, prints the tool's output
  exactly as the unwrapped step did before this wrapper existed.
* A failed deploy ends with one fixed `::error::` line naming the failure
  class. The alert job reads that class from the job's annotations.

A failure is retried only when it is a Cloudflare API error that says nothing
about the Worker itself: code 10013, or a malformed response. Any other
Cloudflare error code (validation, size, binding, ...) is a rejection. A
failure with neither marker is unknown. Neither is retried. At most
MAX_ATTEMPTS attempts are made, with a pause before each retry.

Standard library only: the deploy job runs this before anything else is
installed besides the Worker's own dependencies.
"""

from __future__ import annotations

import re
import subprocess
import sys
import time
from collections.abc import Callable, Sequence
from typing import TextIO

MAX_ATTEMPTS = 3
PAUSES = (20, 60)

TRANSIENT_CODES = frozenset({"10013"})
TRANSIENT_TEXT = ("Received a malformed response from the API",)

CLASS_TRANSIENT_EXHAUSTED = "transient-exhausted"
CLASS_REJECTED = "rejected"
CLASS_UNKNOWN = "unknown"
FAILURE_CLASSES = (CLASS_TRANSIENT_EXHAUSTED, CLASS_REJECTED, CLASS_UNKNOWN)
ANNOTATION_KEY = "deploy-failure-class"

_CODE = re.compile(r"\[code:\s*(\d+)\]")


def classify(output: str) -> str:
    """`transient`, `rejected` or `unknown`; only `transient` is ever retried."""
    codes = set(_CODE.findall(output))
    if codes - TRANSIENT_CODES:
        return "rejected"
    if codes or any(text in output for text in TRANSIENT_TEXT):
        return "transient"
    return "unknown"


def retry_line(attempt: int) -> str:
    return f"deploy attempt {attempt} of {MAX_ATTEMPTS} failed with a transient API error; retrying"


def failure_line(failure_class: str) -> str:
    return f"::error::{ANNOTATION_KEY}={failure_class}"


def _execute(command: Sequence[str]) -> tuple[int, str]:
    done = subprocess.run(
        list(command), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
    )
    return done.returncode, done.stdout.decode("utf-8", errors="replace")


def run(
    command: Sequence[str],
    *,
    execute: Callable[[Sequence[str]], tuple[int, str]] = _execute,
    sleep: Callable[[float], None] = time.sleep,
    out: TextIO | None = None,
) -> int:
    out = out if out is not None else sys.stdout

    def emit(text: str) -> None:
        out.write(text if text.endswith("\n") or not text else text + "\n")
        out.flush()

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            code, output = execute(command)
        except OSError:
            emit("deploy command could not start")
            emit(failure_line(CLASS_UNKNOWN))
            return 127
        if code == 0:
            emit(output)
            return 0
        verdict = classify(output)
        if verdict == "transient" and attempt < MAX_ATTEMPTS:
            emit(retry_line(attempt))
            sleep(PAUSES[attempt - 1])
            continue
        emit(output)
        failure_class = CLASS_TRANSIENT_EXHAUSTED if verdict == "transient" else verdict
        emit(failure_line(failure_class))
        return code
    raise AssertionError("unreachable")  # pragma: no cover


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if args[:1] == ["--"]:
        args = args[1:]
    if not args:
        sys.stderr.write("usage: deploy_retry.py -- <command> [args...]\n")
        return 2
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
