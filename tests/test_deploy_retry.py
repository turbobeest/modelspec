"""MODEL-487: the production Worker deploy retries a transient Cloudflare failure.

The deploy job reads the private data repository and everything it prints is
public. These tests pin what the wrapper may print: fixed lines, and the last
attempt's output exactly as the unwrapped step printed it.
"""

from __future__ import annotations

import io
import subprocess
import sys
from pathlib import Path

import pytest

from scripts import deploy_retry
from scripts.deploy_retry import (
    MAX_ATTEMPTS,
    PAUSES,
    classify,
    failure_line,
    retry_line,
    run,
)

ROOT = Path(__file__).resolve().parents[1]

CODE_10013 = (
    "A request to the Cloudflare API (/accounts/ACCOUNT/workers/scripts/rank) failed.\n"
    "Unknown internal error [code: 10013]\n"
)
MALFORMED = "Received a malformed response from the API\n"
REJECTIONS = (
    "Script startup exceeded CPU limit [code: 10021]\n",
    "Worker exceeded the size limit of 10 MiB [code: 10027]\n",
    "Binding KV is invalid [code: 10042]\n",
    "Text var is too large [code: 10054]\n",
    # A transient code beside a rejection code is a rejection.
    CODE_10013 + "Validation failed [code: 10021]\n",
    MALFORMED + "Validation failed [code: 10021]\n",
)
UNKNOWN = (
    "",
    "Traceback (most recent call last):\nModuleNotFoundError: No module named 'x'\n",
    "npm ERR! network timeout\n",
    "Authentication error\n",
    "something about code 10013 without the brackets\n",
)


@pytest.mark.parametrize("output", (CODE_10013, MALFORMED, "x\n" + CODE_10013 + "y\n"))
def test_the_two_transient_messages_are_classified_transient(output: str) -> None:
    assert classify(output) == "transient"


@pytest.mark.parametrize("output", REJECTIONS)
def test_a_rejection_is_never_transient(output: str) -> None:
    assert classify(output) == "rejected"


@pytest.mark.parametrize("output", UNKNOWN)
def test_an_unknown_failure_is_never_transient(output: str) -> None:
    assert classify(output) == "unknown"


class Scripted:
    """A deploy command that answers from a list, one answer per attempt."""

    def __init__(self, *answers: tuple[int, str]) -> None:
        self.answers = list(answers)
        self.calls: list[tuple[str, ...]] = []

    def __call__(self, command):
        self.calls.append(tuple(command))
        return self.answers.pop(0)


def _run(*answers: tuple[int, str]):
    execute = Scripted(*answers)
    pauses: list[float] = []
    out = io.StringIO()
    code = run(["deploy", "--x"], execute=execute, sleep=pauses.append, out=out)
    return code, out.getvalue(), pauses, execute


def test_a_first_attempt_that_passes_prints_the_tool_output_and_nothing_else() -> None:
    code, printed, pauses, execute = _run((0, "Deployed rank\nVersion ID: abc\n"))
    assert (code, printed, pauses) == (0, "Deployed rank\nVersion ID: abc\n", [])
    assert execute.calls == [("deploy", "--x")]


def test_a_transient_failure_retries_and_the_failed_text_is_not_printed() -> None:
    code, printed, pauses, execute = _run((1, CODE_10013), (1, MALFORMED), (0, "Deployed\n"))
    assert code == 0
    assert printed == retry_line(1) + "\n" + retry_line(2) + "\n" + "Deployed\n"
    assert "ACCOUNT" not in printed and "10013" not in printed and "malformed" not in printed
    assert pauses == [20, 60] == list(PAUSES)
    assert len(execute.calls) == 3


def test_the_bound_is_three_attempts_in_all() -> None:
    assert MAX_ATTEMPTS == 3
    code, printed, pauses, execute = _run((1, CODE_10013), (1, CODE_10013), (7, CODE_10013))
    assert code == 7
    assert len(execute.calls) == 3
    assert pauses == [20, 60]
    assert printed.splitlines()[:2] == [retry_line(1), retry_line(2)]
    assert printed.splitlines()[-1] == failure_line("transient-exhausted")


def test_exhausted_retries_print_only_the_last_attempt_as_the_old_step_did() -> None:
    last = CODE_10013.replace("ACCOUNT", "LAST")
    _, printed, _, _ = _run((1, CODE_10013), (1, CODE_10013), (1, last))
    assert last in printed
    assert "ACCOUNT" not in printed


@pytest.mark.parametrize("rejection", REJECTIONS)
def test_a_rejection_is_not_retried(rejection: str) -> None:
    code, printed, pauses, execute = _run((3, rejection))
    assert code == 3
    assert len(execute.calls) == 1
    assert pauses == []
    assert retry_line(1) not in printed
    assert printed.splitlines()[-1] == failure_line("rejected")


@pytest.mark.parametrize("output", UNKNOWN)
def test_an_unknown_failure_is_not_retried(output: str) -> None:
    code, printed, pauses, execute = _run((2, output))
    assert code == 2
    assert len(execute.calls) == 1
    assert pauses == []
    assert printed.splitlines()[-1] == failure_line("unknown")


def test_a_transient_failure_then_a_rejection_stops_with_the_rejection() -> None:
    code, printed, pauses, execute = _run((1, CODE_10013), (1, REJECTIONS[0]))
    assert code == 1
    assert len(execute.calls) == 2
    assert pauses == [20]
    assert printed.splitlines()[-1] == failure_line("rejected")


def test_the_printed_lines_are_the_fixed_ones() -> None:
    assert retry_line(1) == "deploy attempt 1 of 3 failed with a transient API error; retrying"
    assert retry_line(2) == "deploy attempt 2 of 3 failed with a transient API error; retrying"
    assert failure_line("transient-exhausted") == "::error::deploy-failure-class=transient-exhausted"
    assert failure_line("rejected") == "::error::deploy-failure-class=rejected"
    assert failure_line("unknown") == "::error::deploy-failure-class=unknown"
    assert deploy_retry.FAILURE_CLASSES == ("transient-exhausted", "rejected", "unknown")


def test_a_command_that_cannot_start_prints_two_fixed_lines() -> None:
    def broken(command):
        raise FileNotFoundError("/home/runner/secret/path/uv")

    out = io.StringIO()
    code = run(["uv"], execute=broken, sleep=lambda _: None, out=out)
    assert code == 127
    assert out.getvalue().splitlines() == [
        "deploy command could not start",
        failure_line("unknown"),
    ]


def test_the_real_wrapper_passes_a_command_through(tmp_path: Path) -> None:
    script = tmp_path / "ok.py"
    script.write_text("import sys\nprint('out')\nprint('err', file=sys.stderr)\n")
    done = subprocess.run(
        [sys.executable, str(ROOT / "scripts/deploy_retry.py"), "--", sys.executable, str(script)],
        capture_output=True, text=True, check=False,
    )
    assert done.returncode == 0
    assert sorted(done.stdout.splitlines()) == ["err", "out"]
    assert done.stderr == ""


def test_the_real_wrapper_reports_a_rejection_with_the_commands_exit_code(tmp_path: Path) -> None:
    script = tmp_path / "bad.py"
    script.write_text("import sys\nprint('Validation [code: 10021]', file=sys.stderr)\nsys.exit(4)\n")
    done = subprocess.run(
        [sys.executable, str(ROOT / "scripts/deploy_retry.py"), "--", sys.executable, str(script)],
        capture_output=True, text=True, check=False,
    )
    assert done.returncode == 4
    assert done.stdout.splitlines() == ["Validation [code: 10021]", failure_line("rejected")]


def test_the_wrapper_without_a_command_is_a_usage_error() -> None:
    done = subprocess.run(
        [sys.executable, str(ROOT / "scripts/deploy_retry.py")],
        capture_output=True, text=True, check=False,
    )
    assert done.returncode == 2
