"""Run the writing commands once in CI's serial perf job (MODEL-406)."""

import sys

import pytest

from tests.test_generated_pins import (
    ARTIFACTS,
    generator_repo as generator_repo,
    run,
)


@pytest.mark.perf
def test_real_generators_match_in_process_output(generator_repo, generated_pin_bytes):
    for artifact, args in (
        (ARTIFACTS[0], ("pipeline/agent_copy.py", "write")),
        (ARTIFACTS[1], ("qa/contracts.py",)),
    ):
        target = generator_repo / artifact
        baseline = target.read_bytes()
        try:
            target.unlink()
            result = run(generator_repo, sys.executable, *args, timeout=600)
            assert result.returncode == 0, result.stdout + result.stderr
            assert target.read_bytes() == generated_pin_bytes[artifact]
        finally:
            target.write_bytes(baseline)
