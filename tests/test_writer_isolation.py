"""Writers run the verified engine only. The data checkout is never on sys.path."""

from __future__ import annotations

import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
WRITERS = ROOT / ".github" / "private-writers"
NAMES = (
    "curation-benchmarks",
    "daily-research",
    "data-trust-audit",
    "leaderboard-refresh",
    "price-reread",
    "release-signals",
    "speed-probe",
)
LINK_NAME = (
    "Link the data paths into the verified engine and put only the engine on the import path"
)
PIN_REF = "${{ steps.engine_pin.outputs.sha }}"
ENGINE_REPOSITORY = "turbobeest/modelspec"
PY_CMD = re.compile(r"(?<![\w./-])python3?(?=\s)")
EDITABLE_DATA = re.compile(r"""-e\s+(?:\.|'\.\[|"\.\[)""")
UNTRUSTED = re.compile(
    r"\$\{\{\s*(?:steps\.|matrix\.|needs\.|github\.event\.|inputs\.)"
)
_KEYWORDS = frozenset({
    "if", "then", "else", "elif", "fi", "while", "until", "do", "done",
    "for", "in", "case", "esac", "!", "{", "}", "time", "coproc", "select",
    "function", "continue", "break", "return", "exit",
})
_ASSIGN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*\+?=")
_REDIR = re.compile(r"^(?:\d*>>?|\d*<|\d*>&\d*|\d*>&-|\d*<&\d*|<<.*|>&|>\|)$")
_MODULE = re.compile(r"^[A-Za-z_][\w.]*$")
_ENGINE_PIP = re.compile(
    r"^\$GITHUB_WORKSPACE/engine(?:\[[A-Za-z0-9_,.-]+\])?(?:/\S+)?$"
)
_SPEC = re.compile(
    r"^[A-Za-z0-9][\w.-]*(?:\[[A-Za-z0-9_,.-]+\])?"
    r"(?:(?:==|>=|<=|!=|~=|>|<)[A-Za-z0-9.*+!,<>=_-]+)?$"
)
_NPM_PIN = re.compile(r"^(?:@[A-Za-z0-9_.-]+/)?[A-Za-z0-9_.-]+@\d+\.\d+\.\d+$")
_DATA_WRITE = re.compile(r"(?:^|[\s'\"=])data/")
_RUNNER_TEMP = "${{ runner.temp }}"
REALPATH_SHIM = """#!/bin/sh
if [ "$1" = "-e" ]; then
  shift
  if [ -x /opt/homebrew/bin/grealpath ]; then
    exec /opt/homebrew/bin/grealpath -e "$@"
  elif [ -x /usr/local/bin/grealpath ]; then
    exec /usr/local/bin/grealpath -e "$@"
  else
    exec /usr/bin/realpath -e "$@"
  fi
fi
exec /bin/realpath "$@"
"""


def _text(name: str) -> str:
    return (WRITERS / f"{name}.yml").read_text(encoding="utf-8")


def _document(text: str) -> dict:
    loaded = yaml.safe_load(text)
    if not isinstance(loaded, dict):
        raise AssertionError("workflow did not parse to a mapping")
    return loaded


def _canonical_link() -> dict:
    for job in _document(_text("daily-research"))["jobs"].values():
        for step in job.get("steps") or []:
            if step.get("name") == LINK_NAME:
                return step
    raise AssertionError("daily-research has no link step")


def isolation_problems(text: str) -> list[str]:
    """Reasons a writer workflow breaks isolation. An empty list means it holds."""
    problems: list[str] = []
    if "PYTHONPATH" in text:
        problems.append("PYTHONPATH is set")
    if "prepare_data_writer" in text:
        problems.append("prepare_data_writer still runs")
    if EDITABLE_DATA.search(text):
        problems.append("editable install targets the data checkout")
    try:
        document = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        return problems + [f"YAML did not parse: {exc}"]
    if not isinstance(document, dict) or "jobs" not in document:
        return problems + ["workflow has no jobs"]
    permissions = document.get("permissions")
    if permissions != {"contents": "read"}:
        problems.append(f"workflow permissions are {permissions!r}")
    canonical = _canonical_link()
    for job_name, job in document["jobs"].items():
        problems.extend(_job_problems(str(job_name), job, canonical))
    return problems


def _heredoc_delimiter(line: str) -> str | None:
    quote: str | None = None
    index = 0
    while index < len(line):
        char = line[index]
        if quote is not None:
            if char == quote:
                quote = None
            index += 1
            continue
        if char in {"'", '"'}:
            quote = char
            index += 1
            continue
        if line.startswith("<<", index):
            start = index + 2
            if start < len(line) and line[start] == "-":
                start += 1
            if start < len(line) and line[start] in {"'", '"'}:
                end = line.find(line[start], start + 1)
                if end == -1:
                    return None
                return line[start + 1:end]
            word = re.match(r"[A-Za-z0-9_]+", line[start:])
            return None if word is None else word.group(0)
        index += 1
    return None


def _strip_heredocs(text: str) -> str:
    lines = text.splitlines()
    kept: list[str] = []
    index = 0
    while index < len(lines):
        kept.append(lines[index])
        delimiter = _heredoc_delimiter(lines[index])
        index += 1
        if delimiter is None:
            continue
        while index < len(lines) and lines[index].strip() != delimiter:
            index += 1
        if index < len(lines):
            index += 1
    return "\n".join(kept)


def _matching_paren(text: str, open_at: int) -> int:
    depth = 0
    index = open_at
    quote: str | None = None
    while index < len(text):
        char = text[index]
        if quote is not None:
            if char == "\\" and quote == '"' and index + 1 < len(text):
                index += 2
                continue
            if char == quote:
                quote = None
            index += 1
            continue
        if char in {"'", '"'}:
            quote = char
            index += 1
            continue
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return index
        index += 1
    return len(text) - 1


def _extract_substitutions(text: str) -> tuple[str, list[str]]:
    """Pull $(...) command text out. $(< file) is a read, not a command."""
    out: list[str] = []
    found: list[str] = []
    index = 0
    while index < len(text):
        if text[index] == "'":
            end = text.find("'", index + 1)
            if end == -1:
                out.append(text[index:])
                break
            out.append(text[index:end + 1])
            index = end + 1
            continue
        if text.startswith("$(<", index):
            end = _matching_paren(text, index + 1)
            out.append(text[index:end + 1])
            index = end + 1
            continue
        if text.startswith("$(", index):
            end = _matching_paren(text, index + 1)
            found.append(text[index + 2:end])
            index = end + 1
            continue
        out.append(text[index])
        index += 1
    return "".join(out), found


def _split_segments(text: str) -> list[str]:
    parts: list[str] = []
    buf: list[str] = []
    index = 0
    quote: str | None = None
    while index < len(text):
        char = text[index]
        if quote is not None:
            buf.append(char)
            if char == "\\" and quote == '"' and index + 1 < len(text):
                buf.append(text[index + 1])
                index += 2
                continue
            if char == quote:
                quote = None
            index += 1
            continue
        if char in {"'", '"'}:
            quote = char
            buf.append(char)
            index += 1
            continue
        if char in {"\n", ";"} or text.startswith("&&", index) or text.startswith("||", index):
            parts.append("".join(buf))
            buf = []
            index += 2 if text.startswith(("&&", "||"), index) else 1
            continue
        if char == "|":
            parts.append("".join(buf))
            buf = []
            index += 1
            continue
        buf.append(char)
        index += 1
    parts.append("".join(buf))
    return [part.strip() for part in parts if part.strip()]


def _commands(text: str) -> list[list[str]]:
    text = text.replace("\\\n", " ")
    text = _strip_heredocs(text)
    lines = [line for line in text.splitlines() if not line.lstrip().startswith("#")]
    text, substitutions = _extract_substitutions("\n".join(lines))
    found: list[list[str]] = []
    for substitution in substitutions:
        found.extend(_commands(substitution))
    for segment in _split_segments(text):
        try:
            found.append(shlex.split(segment, posix=True))
        except ValueError:
            found.append(segment.split())
    return found


def _command_tokens(tokens: list[str]) -> list[str]:
    if not tokens or tokens[0] in {"for", "case"}:
        return []
    index = 0
    while index < len(tokens) and (
        tokens[index] in _KEYWORDS or _ASSIGN.match(tokens[index])
    ):
        index += 1
    kept: list[str] = []
    while index < len(tokens):
        token = tokens[index]
        if token in _KEYWORDS:
            index += 1
            continue
        if token == "<<<":
            index += 2
            continue
        if token.startswith("<<<"):
            index += 1
            continue
        if _REDIR.fullmatch(token):
            glued = token.startswith("<<") or bool(
                re.fullmatch(r"\d*>&-?|\d*<&\d+|\d*>&\d+", token)
            )
            index += 1 if glued else 2
            continue
        kept.append(token)
        index += 1
    return kept


def _pip_problems(job_name: str, args: list[str]) -> list[str]:
    if not args or args[0] != "install":
        bad = args[0] if args else "pip"
        return [f"{job_name}: pip install argument is not allowed ({bad})"]
    problems: list[str] = []
    index = 1
    while index < len(args):
        token = args[index]
        if token in {"-e", "--editable"}:
            nxt = args[index + 1] if index + 1 < len(args) else ""
            if _ENGINE_PIP.fullmatch(nxt) is None:
                problems.append(f"{job_name}: pip install argument is not allowed ({token})")
            index += 2
            continue
        allowed = _SPEC.fullmatch(token) is not None or _ENGINE_PIP.fullmatch(token) is not None
        if token.startswith("-") or not allowed:
            problems.append(f"{job_name}: pip install argument is not allowed ({token})")
        index += 1
    return problems


def _python_problems(job_name: str, args: list[str]) -> list[str]:
    if len(args) < 2 or args[1] != "-I":
        return [f"{job_name}: a python command is missing -I"]
    rest = args[2:]
    if not rest:
        return [f"{job_name}: python invocation is not an allowed isolated form"]
    if rest[0] == "-m":
        if len(rest) < 2 or _MODULE.fullmatch(rest[1]) is None:
            return [f"{job_name}: python invocation is not an allowed isolated form"]
        if rest[1] in {"pytest", "tox", "nox"}:
            return [f"{job_name}: rejected command {rest[1]}"]
        if rest[1] == "pip":
            return _pip_problems(job_name, rest[2:])
        return []
    if rest[0] == "-c":
        if len(rest) < 2:
            return [f"{job_name}: python invocation is not an allowed isolated form"]
        return []
    if rest[0] == "-":
        return []
    script = rest[0]
    if script.startswith("$GITHUB_WORKSPACE/engine/") or script.startswith("engine/"):
        return []
    return [f"{job_name}: python invocation is not an allowed isolated form"]


def _looks_like_other_python(command: str) -> bool:
    base = command.rsplit("/", 1)[-1]
    if base == "py" or re.fullmatch(r"python\d+(?:\.\d+)?", base):
        return True
    if "/" in command and "python" in base:
        return True
    return command.startswith("$") and "python" in command


def _shell_problems(job_name: str, args: list[str], workdir: str) -> list[str]:
    command = args[0]
    rest = args[1:]
    if command in {"bash", "sh", "node"}:
        if not rest or not rest[0].startswith("-"):
            return [f"{job_name}: rejected command {command}"]
        return []
    if command == "source":
        return [f"{job_name}: rejected command source"]
    if command == "." and rest and not rest[0].startswith("-"):
        return [f"{job_name}: rejected command ."]
    if command.startswith("./"):
        return [f"{job_name}: rejected command {command}"]
    if command == "npx":
        return [f"{job_name}: rejected command npx"]
    if command == "npm":
        pinned = (
            rest == ["install", "-g", rest[2]]
            if len(rest) == 3
            else False
        )
        if pinned and _NPM_PIN.fullmatch(rest[2]) and workdir == _RUNNER_TEMP:
            return []
        return [f"{job_name}: rejected command npm"]
    if command == "make":
        return [f"{job_name}: rejected command make"]
    if command == "uv" and rest[:1] == ["run"]:
        return [f"{job_name}: rejected command uv"]
    if command == "pipx" and rest[:1] == ["run"]:
        return [f"{job_name}: rejected command pipx"]
    if command in {"pytest", "tox", "nox"}:
        return [f"{job_name}: rejected command {command}"]
    return []


def _command_problems(job_name: str, tokens: list[str], workdir: str) -> list[str]:
    args = _command_tokens(tokens)
    if not args:
        return []
    command = args[0]
    base = command.rsplit("/", 1)[-1]
    if base in {"pip", "pip3"}:
        return [f"{job_name}: pip install is not python -I -m pip"]
    if command in {"python", "python3"}:
        return _python_problems(job_name, args)
    if _looks_like_other_python(command):
        return [f"{job_name}: python invocation is not allowed ({command})"]
    return _shell_problems(job_name, args, workdir)


def _workdir(job: dict, step: dict) -> str:
    if "working-directory" in step:
        return str(step["working-directory"])
    defaults = (job.get("defaults") or {}).get("run") or {}
    return str(defaults.get("working-directory") or "")


def _writes_under_data(step: dict) -> bool:
    path = (step.get("with") or {}).get("path") or ""
    paths = path if isinstance(path, list) else str(path).splitlines()
    if any(item.strip() == "data" or item.strip().startswith("data/") for item in paths):
        return True
    return _DATA_WRITE.search(step.get("run") or "") is not None


def _is_restore(step: dict) -> bool:
    uses = str(step.get("uses") or "")
    if "upload-artifact" in uses:
        return False
    name = str(step.get("name") or "")
    return (
        "actions/cache" in uses
        or "download-artifact" in uses
        or "/restore" in uses
        or re.search(r"\b(?:restore|download)\b", name, re.IGNORECASE) is not None
    )


def _job_problems(job_name: str, job: dict, canonical: dict) -> list[str]:
    problems: list[str] = []
    steps = job.get("steps") or []
    runs_python = False
    for step in steps:
        run = step.get("run") or ""
        if PY_CMD.search(run):
            runs_python = True
        if UNTRUSTED.search(run):
            problems.append(f"{job_name}: untrusted expression in run script")
        workdir = _workdir(job, step)
        for tokens in _commands(run):
            problems.extend(_command_problems(job_name, tokens, workdir))
        with_ = step.get("with") or {}
        if with_.get("repository") == ENGINE_REPOSITORY and with_.get("ref") != PIN_REF:
            problems.append(f"{job_name}: engine checkout ref is not the verified pin")
    links = [step for step in steps if step.get("name") == LINK_NAME]
    if len(links) == 1:
        link_at = steps.index(links[0])
        if any(_is_restore(step) and _writes_under_data(step) for step in steps[link_at + 1:]):
            problems.append(f"{job_name}: restore writes under data/ after the link step")
        if links[0] != canonical:
            problems.append(f"{job_name}: link step does not match the canonical link step")
    if not runs_python:
        return problems
    if len(links) != 1:
        return problems + [f"{job_name}: runs python without the link step"]
    setup_at = next(
        (index for index, step in enumerate(steps)
         if str(step.get("uses") or "").startswith("actions/setup-python")),
        None,
    )
    link_at = steps.index(links[0])
    script_at = next(
        (index for index, step in enumerate(steps)
         if "python -I -m scripts" in (step.get("run") or "")
         or "python3 -I -m scripts" in (step.get("run") or "")),
        None,
    )
    if setup_at is None or script_at is None or not (setup_at < link_at < script_at):
        problems.append(
            f"{job_name}: link step is not between setup-python and the first engine script"
        )
    return problems


@pytest.mark.parametrize("name", NAMES)
def test_writer_workflows_keep_the_data_checkout_off_the_import_path(name: str) -> None:
    assert isolation_problems(_text(name)) == []


def test_recall_private_stays_outside_this_guard() -> None:
    assert "recall-private" not in NAMES
    recall = (WRITERS / "recall-private.yml").read_text(encoding="utf-8")
    assert "prepare_data_writer.py" in recall
    assert "PYTHONPATH" in recall


def test_a_pythonpath_assignment_is_rejected() -> None:
    text = _text("daily-research").replace(
        "permissions:\n  contents: read\n",
        "permissions:\n  contents: read\nenv:\n  PYTHONPATH: /tmp/data\n",
        1,
    )
    assert "PYTHONPATH is set" in isolation_problems(text)


def test_a_python_command_without_isolated_mode_is_rejected() -> None:
    text = _text("daily-research").replace(
        "python -I -m scripts.seed_models_dev",
        "python scripts/seed_models_dev.py",
        1,
    )
    assert "research: a python command is missing -I" in isolation_problems(text)


def test_a_bare_pip_install_is_rejected() -> None:
    text = _text("daily-research").replace(
        "python -I -m pip install pydantic pyyaml httpx",
        "pip install pydantic pyyaml httpx",
        1,
    )
    assert "research: pip install is not python -I -m pip" in isolation_problems(text)


@pytest.mark.parametrize("editable", ["-e .", "-e '.[dev]'"])
def test_an_editable_install_of_the_data_tree_is_rejected(editable: str) -> None:
    text = _text("release-signals").replace(
        '-e "$GITHUB_WORKSPACE/engine[dev]"',
        editable,
        1,
    )
    assert "editable install targets the data checkout" in isolation_problems(text)


def test_prepare_data_writer_is_rejected() -> None:
    text = _text("speed-probe").replace(
        "python -I -m scripts.speed preflight",
        "python -I ../engine/scripts/prepare_data_writer.py",
        1,
    )
    assert "prepare_data_writer still runs" in isolation_problems(text)


def test_an_engine_checkout_on_a_branch_is_rejected() -> None:
    text = _text("leaderboard-refresh").replace(
        "ref: ${{ steps.engine_pin.outputs.sha }}",
        "ref: qa/model-267-engine",
        1,
    )
    assert "refresh: engine checkout ref is not the verified pin" in isolation_problems(text)


def test_workflow_write_permission_is_rejected() -> None:
    text = _text("daily-research").replace("contents: read", "contents: write", 1)
    assert "workflow permissions are {'contents': 'write'}" in isolation_problems(text)


def test_a_python_job_without_the_link_step_is_rejected() -> None:
    text = _text("data-trust-audit").replace(LINK_NAME, "Do not link", 1)
    assert "audit: runs python without the link step" in isolation_problems(text)


def test_a_link_step_that_is_not_the_canonical_one_is_rejected() -> None:
    text = _text("price-reread").replace("modelspec-engine.pth", "other-engine.pth", 1)
    assert "reread: link step does not match the canonical link step" in isolation_problems(text)


def test_the_link_step_must_follow_setup_python() -> None:
    text = _text("daily-research")
    start = text.index("      - uses: actions/setup-python@v5\n")
    link_at = text.index(f"      - name: {LINK_NAME}")
    install_at = text.index("\n      - name: Install dependencies\n")
    setup_part = text[start:link_at]
    link_part = text[link_at:install_at]
    swapped = text[:start] + link_part + setup_part + text[install_at:]
    problems = isolation_problems(swapped)
    assert "research: link step is not between setup-python and the first engine script" in problems


def test_a_job_that_runs_no_python_needs_no_link_step() -> None:
    text = """\
name: quiet
permissions:
  contents: read
jobs:
  pending:
    steps:
      - run: curl --fail https://example.invalid
"""
    assert isolation_problems(text) == []


_INSTALL = "        run: python -I -m pip install pydantic pyyaml httpx\n"


def _with_command(command: str) -> str:
    block = (
        "        run: |\n"
        "          python -I -m pip install pydantic pyyaml httpx\n"
        f"          {command}\n"
    )
    text = _text("daily-research")
    assert text.count(_INSTALL) == 1
    return text.replace(_INSTALL, block, 1)


@pytest.mark.parametrize(
    ("command", "fragment"),
    [
        ("python -c 'print(1)'", "a python command is missing -I"),
        ("python -I scripts/x.py", "not an allowed isolated form"),
        (
            "$pythonLocation/bin/python -I -c 'print(1)'",
            "python invocation is not allowed ($pythonLocation/bin/python)",
        ),
        ("python3.11 -I -c 'print(1)'", "python invocation is not allowed (python3.11)"),
        (
            "/usr/bin/python3 -I -c 'print(1)'",
            "python invocation is not allowed (/usr/bin/python3)",
        ),
        ("py -I -c 'print(1)'", "python invocation is not allowed (py)"),
        ("python -I -m pip install -r requirements.txt", "not allowed (-r)"),
        (
            "python -I -m pip install --requirement requirements.txt",
            "not allowed (--requirement)",
        ),
        ("python -I -m pip install -e .", "not allowed (-e)"),
        ("python -I -m pip install .", "not allowed (.)"),
        ("python -I -m pip install ./local", "not allowed (./local)"),
        ("python -I -m pip install -c constraints.txt", "not allowed (-c)"),
        (
            "python -I -m pip install --constraint constraints.txt",
            "not allowed (--constraint)",
        ),
        ("python -I -m pip install --editable /tmp/pkg", "not allowed (--editable)"),
        ("python -I -m pip install /tmp/pkg", "not allowed (/tmp/pkg)"),
        ("bash scripts/x.sh", "rejected command bash"),
        ("sh scripts/x.sh", "rejected command sh"),
        ("source scripts/x.sh", "rejected command source"),
        (". ./scripts/x.sh", "rejected command ."),
        ("./scripts/x.sh", "rejected command ./scripts/x.sh"),
        ("npx tsx scripts/x.ts", "rejected command npx"),
        ("npm run build", "rejected command npm"),
        ("npm exec -- something", "rejected command npm"),
        ("make test", "rejected command make"),
        ("node scripts/x.js", "rejected command node"),
        ("uv run tool", "rejected command uv"),
        ("pipx run tool", "rejected command pipx"),
        ("pytest", "rejected command pytest"),
        ("tox", "rejected command tox"),
        ("nox", "rejected command nox"),
        ("python -I -m pytest", "rejected command pytest"),
        ("python -I -m tox", "rejected command tox"),
        ("python -I -m nox", "rejected command nox"),
        (
            "npm install -g @anthropic-ai/claude-code@2.1.267",
            "rejected command npm",
        ),
        ("npm install -g @anthropic-ai/claude-code@latest", "rejected command npm"),
    ],
)
def test_a_writer_command_outside_the_allowlist_is_rejected(
    command: str, fragment: str
) -> None:
    problems = isolation_problems(_with_command(command))
    assert any(f"research: {fragment}" == problem or fragment in problem for problem in problems), (
        problems
    )


def test_an_untrusted_expression_in_a_run_script_is_rejected() -> None:
    text = _text("daily-research").replace(
        'echo "::error::models.dev survey failed; see output above"',
        'echo "${{ steps.survey.outputs.count }}"\n'
        '            echo "::error::models.dev survey failed; see output above"',
        1,
    )
    assert "research: untrusted expression in run script" in isolation_problems(text)


@pytest.mark.parametrize(
    "uses",
    ["actions/cache@v4", "actions/download-artifact@v4", "actions/cache/restore@v4"],
)
def test_a_restore_into_data_after_the_link_step_is_rejected(uses: str) -> None:
    text = _text("daily-research")
    needle = "\n      - name: Install dependencies\n"
    assert text.count(needle) == 1
    step = (
        f"\n      - uses: {uses}\n"
        "        with:\n"
        "          path: data/models\n"
        "          key: planted\n"
    )
    problems = isolation_problems(text.replace(needle, step + needle, 1))
    assert "research: restore writes under data/ after the link step" in problems


def test_a_named_restore_that_writes_under_data_after_the_link_is_rejected() -> None:
    text = _text("daily-research")
    needle = "\n      - name: Install dependencies\n"
    step = (
        "\n      - name: Restore planted files\n"
        "        run: cp /tmp/x.yaml data/models/x.yaml\n"
    )
    problems = isolation_problems(text.replace(needle, step + needle, 1))
    assert "research: restore writes under data/ after the link step" in problems


def test_a_restore_into_data_before_the_link_step_is_allowed() -> None:
    text = _text("daily-research")
    needle = "\n      - uses: actions/setup-python@v5\n"
    assert text.count(needle) == 1
    step = (
        "\n      - uses: actions/cache@v4\n"
        "        with:\n"
        "          path: data/benchmarks/_curation/state\n"
        "          key: planted\n"
    )
    assert isolation_problems(text.replace(needle, step + needle, 1)) == []


@pytest.fixture(scope="module")
def venv_python(tmp_path_factory: pytest.TempPathFactory) -> Path:
    venv = tmp_path_factory.mktemp("writer-isolation-venv") / "venv"
    created = subprocess.run(
        [sys.executable, "-m", "venv", str(venv)],
        capture_output=True,
        text=True,
        check=False,
    )
    python = venv / "bin" / "python"
    if created.returncode != 0 or not python.is_file():
        pytest.skip("python -m venv is unavailable: " + created.stderr[-400:])
    return python


def _workspace(tmp_path: Path) -> Path:
    workspace = tmp_path / "ws"
    data_models = workspace / "data" / "models"
    data_models.mkdir(parents=True)
    (workspace / "data" / "benchmarks").mkdir()
    (data_models / "x.yaml").write_text("id: x\n", encoding="utf-8")
    engine_pipeline = workspace / "engine" / "pipeline"
    engine_pipeline.mkdir(parents=True)
    shutil.copy(ROOT / "pipeline" / "__init__.py", engine_pipeline / "__init__.py")
    shutil.copy(ROOT / "pipeline" / "data_source.py", engine_pipeline / "data_source.py")
    (workspace / "data" / "sitecustomize.py").write_text(
        "import os\nfrom pathlib import Path\nPath(os.environ['MARKER']).write_text('ran')\n",
        encoding="utf-8",
    )
    return workspace


def _realpath_dir(workspace: Path) -> Path:
    bindir = workspace / ".shim"
    bindir.mkdir(exist_ok=True)
    script = bindir / "realpath"
    script.write_text(REALPATH_SHIM, encoding="utf-8")
    script.chmod(0o755)
    return bindir


def _run_env(workspace: Path, python: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["PATH"] = (
        str(_realpath_dir(workspace))
        + os.pathsep
        + str(python.parent)
        + os.pathsep
        + env.get("PATH", "")
    )
    # realpath -e returns the canonical path. /var on macOS is /private/var.
    env["GITHUB_WORKSPACE"] = os.path.realpath(workspace)
    env["MARKER"] = str(workspace / "MARKER")
    for key in ("PYTHONPATH", "PYTHONHOME", "PYTHONSTARTUP", "PYTHONSAFEPATH"):
        env.pop(key, None)
    return env


def _run_link(workspace: Path, python: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", "-c", _canonical_link()["run"]],
        cwd=workspace,
        env=_run_env(workspace, python),
        capture_output=True,
        text=True,
        check=False,
    )


def test_the_link_step_imports_the_engine_and_ignores_a_planted_sitecustomize(
    tmp_path: Path, venv_python: Path
) -> None:
    workspace = _workspace(tmp_path)
    linked = _run_link(workspace, venv_python)
    assert linked.returncode == 0, linked.stdout + linked.stderr
    engine = (workspace / "engine").resolve()
    assert (workspace / "engine" / "models").is_symlink()
    assert (workspace / "engine" / "models").resolve() == (workspace / "data" / "models").resolve()
    assert not (workspace / "MARKER").exists()

    env = _run_env(workspace, venv_python)
    env["PYTHONPATH"] = str(workspace / "data")
    imported = subprocess.run(
        [
            str(venv_python), "-I", "-c",
            "import pipeline.data_source; print(pipeline.data_source.REPO_ROOT)",
        ],
        cwd=workspace / "data",
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert imported.returncode == 0, imported.stdout + imported.stderr
    assert Path(imported.stdout.strip()) == engine
    assert not (workspace / "MARKER").exists()


def test_the_link_step_refuses_python_and_symlinks_under_a_data_path(
    tmp_path: Path, venv_python: Path
) -> None:
    workspace = _workspace(tmp_path)
    (workspace / "data" / "models" / "evil.py").write_text("print('no')\n", encoding="utf-8")
    refused = _run_link(workspace, venv_python)
    assert refused.returncode != 0
    assert "::error::refusing" in refused.stdout
    assert not (workspace / "MARKER").exists()

    (workspace / "data" / "models" / "evil.py").unlink()
    alias = workspace / "data" / "models" / "alias.yaml"
    alias.symlink_to("x.yaml")
    refused = _run_link(workspace, venv_python)
    assert refused.returncode != 0
    assert "::error::refusing" in refused.stdout
    assert "alias.yaml" in refused.stdout


def test_the_link_step_refuses_a_symlink_data_directory(
    tmp_path: Path, venv_python: Path
) -> None:
    workspace = _workspace(tmp_path)
    real = tmp_path / "real-data"
    shutil.move(str(workspace / "data"), str(real))
    (workspace / "data").symlink_to(real)
    refused = _run_link(workspace, venv_python)
    assert refused.returncode != 0
    assert "::error::refusing symlink data" in refused.stdout


def test_the_link_step_refuses_a_symlink_in_a_path_component(
    tmp_path: Path, venv_python: Path
) -> None:
    workspace = _workspace(tmp_path)
    outside = tmp_path / "registry"
    outside.mkdir()
    (outside / "sources.yaml").write_text("sources: []\n", encoding="utf-8")
    (workspace / "data" / "registry").symlink_to(outside)
    refused = _run_link(workspace, venv_python)
    assert refused.returncode != 0, refused.stdout + refused.stderr
    assert "::error::refusing symlink data/registry" in refused.stdout


def test_the_link_step_refuses_a_path_that_resolves_outside_the_checkout(
    tmp_path: Path, venv_python: Path
) -> None:
    workspace = _workspace(tmp_path)
    env = _run_env(workspace, venv_python)
    env["GITHUB_WORKSPACE"] = str(tmp_path / "elsewhere")
    refused = subprocess.run(
        ["bash", "-c", _canonical_link()["run"]],
        cwd=workspace,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert refused.returncode != 0, refused.stdout + refused.stderr
    assert "resolves outside the data checkout" in refused.stdout


def test_the_link_step_fails_when_the_path_list_is_empty(
    tmp_path: Path, venv_python: Path
) -> None:
    workspace = _workspace(tmp_path)
    (workspace / "engine" / "pipeline" / "data_source.py").write_text(
        "raise SystemExit(0)\n",
        encoding="utf-8",
    )
    refused = _run_link(workspace, venv_python)
    assert refused.returncode != 0, refused.stdout + refused.stderr
    assert "::error::data paths are empty" in refused.stdout


@pytest.mark.parametrize("missing", ["models", "benchmarks"])
def test_the_link_step_fails_when_a_required_data_directory_is_missing(
    missing: str, tmp_path: Path, venv_python: Path
) -> None:
    workspace = _workspace(tmp_path)
    shutil.rmtree(workspace / "data" / missing)
    refused = _run_link(workspace, venv_python)
    assert refused.returncode != 0, refused.stdout + refused.stderr
    assert f"::error::data/{missing} is missing" in refused.stdout
