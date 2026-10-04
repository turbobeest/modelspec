"""The root CLI sends agents to the decision engine without changing v1 output."""

from __future__ import annotations

import re

import pytest
from typer.testing import CliRunner

from cli.modelspec import legacy as cli
from decision.registry import default
from decision.templates import load_templates


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


@pytest.mark.parametrize(
    ("use_case", "guidance_kind", "guidance_target", "guidance"),
    [
        (
            "coding",
            "template",
            "budget-coding",
            "use `modelspec decide --template budget-coding` instead.",
        ),
        (
            "reasoning",
            "domain",
            "reasoning",
            "use `modelspec decide SPEC.yaml` with a `reasoning` objective instead.",
        ),
        (
            "chat",
            "domain",
            "chat_preference",
            "use `modelspec decide SPEC.yaml` with a `chat_preference` objective instead.",
        ),
        (
            "embedding",
            "template",
            "retrieval-embeddings",
            "use `modelspec decide --template retrieval-embeddings` instead.",
        ),
        (
            "agentic",
            "domain",
            "agentic_tool_use",
            "use `modelspec decide SPEC.yaml` with an `agentic_tool_use` objective instead.",
        ),
        (
            "general",
            "selector",
            None,
            "run `modelspec vocab domains`, choose the domain that matches your task, "
            "then use it in a `modelspec decide SPEC.yaml` objective.",
        ),
    ],
)
def test_graph_rank_warns_on_stderr_with_valid_decision_guidance_and_keeps_stdout(
    monkeypatch,
    use_case: str,
    guidance_kind: str,
    guidance_target: str | None,
    guidance: str,
) -> None:
    class Result:
        result_set: list = []

    class Graph:
        def query(self, *args, **kwargs):
            return Result()

    monkeypatch.setattr(cli, "_get_graph", lambda: Graph())

    result = CliRunner().invoke(cli.app, ["rank", "--use-case", use_case])

    assert result.exit_code == 0
    assert result.stderr == (
        "deprecated: modelspec rank uses the retired fixed-benchmark ranking; "
        f"{guidance}\n"
    )
    assert result.stdout == "No models found.\n"

    if guidance_kind == "template":
        assert guidance_target in {template["id"] for template in load_templates()}
    elif guidance_kind == "domain":
        assert guidance_target in {domain.id for domain in default().domains()}
    else:
        assert guidance_kind == "selector"
        assert guidance_target is None


@pytest.mark.parametrize("use_case", ["xyz", "task-specific", "Codingx"])
def test_graph_rank_unknown_use_case_gets_selector_not_invented_domain(
    monkeypatch, use_case: str
) -> None:
    class Graph:
        def query(self, *args, **kwargs):
            raise AssertionError("unknown use case must not query the graph")

    monkeypatch.setattr(cli, "_get_graph", lambda: Graph())

    result = CliRunner().invoke(cli.app, ["rank", "--use-case", use_case])

    assert result.exit_code == 1
    assert result.stderr == (
        "deprecated: modelspec rank uses the retired fixed-benchmark ranking; "
        "run `modelspec vocab domains`, choose the domain that matches your task, "
        "then use it in a `modelspec decide SPEC.yaml` objective.\n"
    )
    assert use_case not in result.stderr
    assert "Unknown use case" in result.stdout
