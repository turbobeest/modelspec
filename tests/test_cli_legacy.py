"""The root CLI sends agents to the decision engine without changing v1 output."""

from __future__ import annotations

import re

from typer.testing import CliRunner

from cli.modelspec import cli


def _plain(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


def test_root_help_starts_with_decide_and_groups_v1_as_legacy() -> None:
    result = CliRunner().invoke(cli.app, ["--help"])

    assert result.exit_code == 0
    output = _plain(result.stdout)
    flattened = " ".join(output.split())
    assert "Start here: modelspec snapshot fetch, then modelspec vocab, then " in flattened
    assert "modelspec decide --template <id>" in flattened
    assert output.index("Decision commands") < output.index("Legacy (v1)")
    assert output.index("Legacy (v1)") < output.index("Maintainer-only")
    decision = output[output.index("Decision commands"):output.index("Legacy (v1)")]
    legacy = output[output.index("Legacy (v1)"):output.index("Maintainer-only")]
    maintainers = output[output.index("Maintainer-only"):]
    assert [decision.index(command) for command in ("snapshot", "vocab", "decide", "verify")] == sorted(
        decision.index(command) for command in ("snapshot", "vocab", "decide", "verify")
    )
    for command in ("rank", "search", "compare", "hardware", "info", "stats", "gaps", "offline"):
        assert command in legacy
    for command in ("research", "contribute", "validate"):
        assert command in maintainers


def test_graph_rank_warns_on_stderr_and_keeps_stdout(monkeypatch) -> None:
    class Result:
        result_set: list = []

    class Graph:
        def query(self, *args, **kwargs):
            return Result()

    monkeypatch.setattr(cli, "_get_graph", lambda: Graph())

    result = CliRunner().invoke(cli.app, ["rank", "--use-case", "coding"])

    assert result.exit_code == 0
    assert result.stderr == (
        "deprecated: modelspec rank uses the retired fixed-benchmark ranking; "
        "use `modelspec decide --template budget-coding` instead.\n"
    )
    assert result.stdout == "No models found.\n"
