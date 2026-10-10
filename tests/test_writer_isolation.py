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

from pipeline.data_source import is_data_path

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
    r"\$\{\{\s*(?:steps\.|matrix\.|needs\.|github\.event\.|github\.head_ref|inputs\.)"
)
# Writer `run:` text is an allowlist. `cd` is rejected: jobs set
# `working-directory` or call `git -C`, and `cd` would hide where a later
# relative path writes. `break` and `continue` stay because the link loop and
# the price-reread restore loop use them. `find -exec` / `-execdir` / `-ok` /
# `-okdir` / `-delete` are rejected outside the link step. `git -c` is
# rejected because it can point `core.hooksPath` at the data checkout;
# `git config` may set only `user.name`, `user.email`, and the push
# extraheader. `python -I -c` may not call exec, eval, importlib, runpy, or
# subprocess. `python -I -m` may only load `scripts.*`, `cli.*`,
# `release_signals.*`, `pipeline.*`, or `pip`. A script path must be
# `engine/...` with no `..` and must not be a data path the link step mounts
# (`models/`, `benchmarks/`, ...). After the link step, a redirection,
# `cp`/`mv`/`ln` destination, `tar -C`, `unzip -d`, or
# `gh run download --dir`/`-D` whose path is under `data/` is a restore.
# Git is exempt. A relative path that does not start with `data/` is the
# writer's own file inside `working-directory: data`.
_ASSIGN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*\+?=")
_ARRAY = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=\(")
_CASE_ARM = re.compile(
    r"^(?:\"(?:[^\"\\]|\\.)*\"|'(?:[^'\\]|\\.)*'|\S)+\)\s*(?:;;)?\s*$"
)
_COMPOUND_OPEN = frozenset({
    "if", "elif", "then", "else", "while", "until", "do", "{",
})
_COMPOUND_CLOSE = frozenset({"fi", "done", "esac", "}", ";;"})
_COMPOUND_SKIP = frozenset({"for", "case", "select"})
_BUILTINS = frozenset({
    "exit", "set", "local", "export", "read", "shift", "return",
    "break", "continue", "true", "false",
})
_COMMANDS = frozenset({
    "git", "gh", "jq", "curl", "echo", "printf", "test", "[", "[[",
    "mkdir", "cat", "cp", "rm", "ln", "date", "base64", "grep", "head",
    "tee", "find", "realpath", "openssl", "sed", "awk", "wc", "sort",
    "tr", "cut", "basename", "dirname", "npm",
})
_FIND_RUN = frozenset({"-exec", "-execdir", "-ok", "-okdir", "-delete"})
_GIT_SUBS = frozenset({
    "clone", "cat-file", "merge-base", "rev-parse", "config", "switch",
    "add", "commit", "push", "show", "fetch", "status", "diff",
})
_GIT_CONFIG_KEYS = frozenset({
    "user.name",
    "user.email",
    "http.https://github.com/.extraheader",
})
_DANGEROUS_PY = re.compile(
    r"\b(?:exec|eval|compile|__import__|importlib|runpy|subprocess|"
    r"breakpoint|pickle|marshal)\b|os\.system|os\.popen"
)
_MODULE_OK = re.compile(
    r"^(?:pip|(?:scripts|cli|release_signals|pipeline)(?:\.[A-Za-z_][\w.]*)?)$"
)
_PIP_BIN = re.compile(r"^pip\d*(?:\.\d+)*$")
_WS_PREFIXES = (
    "${{ github.workspace }}/",
    "${{github.workspace}}/",
    "$GITHUB_WORKSPACE/",
)
_WORKSPACE_ROOTS = frozenset({
    "", ".", "${{ github.workspace }}", "${{github.workspace}}", "$GITHUB_WORKSPACE",
})
_MODULE = re.compile(r"^[A-Za-z_][\w.]*$")
_ENGINE_PIP = re.compile(
    r"^\$GITHUB_WORKSPACE/engine(?:\[[A-Za-z0-9_,.-]+\])?(?:/\S+)?$"
)
_SPEC = re.compile(
    r"^[A-Za-z0-9][\w.-]*(?:\[[A-Za-z0-9_,.-]+\])?"
    r"(?:(?:==|>=|<=|!=|~=|>|<)[A-Za-z0-9.*+!,<>=_-]+)?$"
)
_NPM_PIN = re.compile(r"^(?:@[A-Za-z0-9_.-]+/)?[A-Za-z0-9_.-]+@\d+\.\d+\.\d+$")
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


def _extract_backticks(text: str) -> tuple[str, list[str]]:
    """Pull `...` command text out. Backticks inside single quotes stay literal."""
    out: list[str] = []
    found: list[str] = []
    index = 0
    quote: str | None = None
    while index < len(text):
        char = text[index]
        if quote == "'":
            out.append(char)
            if char == "'":
                quote = None
            index += 1
            continue
        if quote == '"':
            if char == "\\" and index + 1 < len(text):
                out.append(text[index:index + 2])
                index += 2
                continue
            if char == "`":
                end = text.find("`", index + 1)
                if end == -1:
                    found.append(text[index + 1:])
                    return "".join(out), found
                found.append(text[index + 1:end])
                index = end + 1
                continue
            out.append(char)
            if char == '"':
                quote = None
            index += 1
            continue
        if char in {"'", '"'}:
            quote = char
            out.append(char)
            index += 1
            continue
        if char == "`":
            end = text.find("`", index + 1)
            if end == -1:
                found.append(text[index + 1:])
                return "".join(out), found
            found.append(text[index + 1:end])
            index = end + 1
            continue
        out.append(char)
        index += 1
    return "".join(out), found


def _commands(text: str) -> list[list[str] | None]:
    text = text.replace("\\\n", " ")
    text = _strip_heredocs(text)
    lines = [line for line in text.splitlines() if not line.lstrip().startswith("#")]
    text, substitutions = _extract_substitutions("\n".join(lines))
    text, backticks = _extract_backticks(text)
    found: list[list[str] | None] = []
    for inner in (*substitutions, *backticks):
        found.extend(_commands(inner))
    for segment in _split_segments(text):
        if _ARRAY.match(segment) or _CASE_ARM.match(segment) or segment in {";;", "in"}:
            continue
        try:
            found.append(shlex.split(segment, posix=True))
        except ValueError:
            found.append(None)
    return found


def _strip_redir(tokens: list[str]) -> list[str]:
    kept: list[str] = []
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token in {">", ">>", ">|", "<", "<>", "<<<"}:
            index += 2
            continue
        if token.startswith("<<<") or token.startswith("<<"):
            index += 1
            continue
        if re.fullmatch(r"\d*>&-|\d*<&-|\d*>&?\d+|\d*<&\d+", token):
            index += 1
            continue
        if re.fullmatch(r"\d*>>?[^\d&].*|\d*<[^\d&].*", token):
            index += 1
            continue
        kept.append(token)
        index += 1
    return kept


def _pip_token_ok(token: str) -> bool:
    if ".." in token.split("/"):
        return False
    return _SPEC.fullmatch(token) is not None or _ENGINE_PIP.fullmatch(token) is not None


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
            if not _pip_token_ok(nxt) or _ENGINE_PIP.fullmatch(nxt) is None:
                problems.append(f"{job_name}: pip install argument is not allowed ({token})")
            index += 2
            continue
        if token.startswith("-") or not _pip_token_ok(token):
            problems.append(f"{job_name}: pip install argument is not allowed ({token})")
        index += 1
    return problems


def _script_problem(script: str) -> str | None:
    text = script
    prefix = "$GITHUB_WORKSPACE/"
    if text.startswith(prefix):
        text = text[len(prefix):]
    parts = text.split("/")
    if text.startswith("/") or ".." in parts or text.startswith("$"):
        return "not an allowed isolated form"
    norm = os.path.normpath(text)
    if ".." in norm.split("/") or not norm.startswith("engine/"):
        return "not an allowed isolated form"
    relative = norm[len("engine/"):]
    if not relative or is_data_path(relative):
        return "not an allowed isolated form"
    return None


def _python_problems(job_name: str, args: list[str]) -> list[str]:
    if len(args) < 2 or args[1] != "-I":
        return [f"{job_name}: a python command is missing -I"]
    rest = args[2:]
    if not rest:
        return [f"{job_name}: python invocation is not an allowed isolated form"]
    if rest[0] == "-m":
        if len(rest) < 2 or _MODULE.fullmatch(rest[1]) is None:
            return [f"{job_name}: python invocation is not an allowed isolated form"]
        if _MODULE_OK.fullmatch(rest[1]) is None:
            return [f"{job_name}: rejected module {rest[1]}"]
        if rest[1] == "pip":
            return _pip_problems(job_name, rest[2:])
        return []
    if rest[0] == "-c":
        if len(rest) < 2 or _DANGEROUS_PY.search(rest[1]):
            return [f"{job_name}: rejected python -c"]
        return []
    if rest[0] == "-":
        return []
    problem = _script_problem(rest[0])
    if problem:
        return [f"{job_name}: python invocation is {problem}"]
    return []


def _looks_like_other_python(command: str) -> bool:
    base = command.rsplit("/", 1)[-1]
    if base == "py" or re.fullmatch(r"python\d+(?:\.\d+)?", base):
        return True
    if "/" in command and "python" in base:
        return True
    return command.startswith("$") and "python" in command


def _git_config_key(args: list[str]) -> str:
    index = args.index("config") + 1
    while index < len(args):
        arg = args[index]
        if arg in {"-f", "--file"}:
            index += 2
            continue
        if arg.startswith("-"):
            index += 1
            continue
        return arg
    return ""


def _git_problems(job_name: str, args: list[str]) -> list[str]:
    index = 1
    sub = ""
    while index < len(args):
        arg = args[index]
        if arg == "-C":
            index += 2
            continue
        if (
            arg == "-c"
            or arg.startswith("--config-env")
            or (arg.startswith("-c") and not arg.startswith("-C"))
        ):
            return [f"{job_name}: rejected git -c"]
        if arg.startswith("-"):
            index += 1
            continue
        sub = arg
        break
    if any("hookspath" in arg.lower() for arg in args):
        return [f"{job_name}: rejected git -c"]
    if sub not in _GIT_SUBS:
        return [f"{job_name}: rejected git {sub or 'git'}"]
    if sub == "config" and _git_config_key(args) not in _GIT_CONFIG_KEYS:
        return [f"{job_name}: rejected git config"]
    return []


def _npm_problems(job_name: str, args: list[str], workdir: str) -> list[str]:
    rest = args[1:]
    pinned = len(rest) == 3 and rest[:2] == ["install", "-g"] and _NPM_PIN.fullmatch(rest[2])
    if pinned and workdir == _RUNNER_TEMP:
        return []
    return [f"{job_name}: rejected command npm"]


def _classify(
    job_name: str, tokens: list[str], workdir: str, in_link: bool
) -> list[str]:
    stripped = _strip_redir(tokens)
    index = 0
    while index < len(stripped) and _ASSIGN.match(stripped[index]):
        index += 1
    if index >= len(stripped):
        return []
    token = stripped[index]
    if token in _COMPOUND_SKIP or token in _COMPOUND_CLOSE or token == "in":
        return []
    if token in _COMPOUND_OPEN or token == "!":
        return _classify(job_name, stripped[index + 1:], workdir, in_link)
    if token == "(":
        if ")" not in stripped[index + 1:]:
            return [f"{job_name}: unparseable shell"]
        end = len(stripped) - 1 - stripped[::-1].index(")")
        return _classify(job_name, stripped[index + 1:end], workdir, in_link)
    if token in _BUILTINS:
        return []
    args = stripped[index:]
    command = args[0]
    base = command.rsplit("/", 1)[-1]
    if _PIP_BIN.fullmatch(base):
        return [f"{job_name}: pip install is not python -I -m pip"]
    if command in {"python", "python3"}:
        return _python_problems(job_name, args)
    if _looks_like_other_python(command):
        return [f"{job_name}: python invocation is not allowed ({command})"]
    if command not in _COMMANDS:
        return [f"{job_name}: rejected command {command}"]
    if command == "git":
        return _git_problems(job_name, args)
    if command == "find":
        if in_link:
            return []
        for arg in args:
            if arg in _FIND_RUN:
                return [f"{job_name}: rejected find {arg}"]
        return []
    if command == "npm":
        return _npm_problems(job_name, args, workdir)
    return []


def _command_problems(
    job_name: str, tokens: list[str], workdir: str, in_link: bool
) -> list[str]:
    if not tokens:
        return []
    return _classify(job_name, tokens, workdir, in_link)


def _path_writes_data(raw: str, *, root_counts: bool = False) -> bool:
    text = str(raw).strip().strip("'\"")
    if root_counts and text in _WORKSPACE_ROOTS:
        return True
    for prefix in _WS_PREFIXES:
        if text.startswith(prefix):
            text = text[len(prefix):]
            break
    while text.startswith("./"):
        text = text[2:]
    if root_counts and text in {"", "."}:
        return True
    return text == "data" or text.startswith("data/")


def _action_writes_data(step: dict) -> bool:
    uses = str(step.get("uses") or "")
    if "upload-artifact" in uses:
        return False
    cache = "actions/cache" in uses or "/restore" in uses
    download = "download-artifact" in uses
    if not cache and not download:
        return False
    raw = (step.get("with") or {}).get("path")
    if download and (raw is None or str(raw).strip() == ""):
        return True
    items = raw if isinstance(raw, list) else str(raw or "").splitlines()
    return any(_path_writes_data(item, root_counts=True) for item in items)


def _redir_targets(tokens: list[str]) -> list[str]:
    targets: list[str] = []
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token in {">", ">>", ">|"}:
            if index + 1 < len(tokens):
                targets.append(tokens[index + 1])
            index += 2
            continue
        matched = re.fullmatch(r"(\d*>>?)(.+)", token)
        if matched and "&" not in token and not token.startswith("<"):
            targets.append(matched.group(2))
        index += 1
    return targets


def _destinations(args: list[str]) -> list[str]:
    dests: list[str] = []
    operands: list[str] = []
    index = 1
    while index < len(args):
        arg = args[index]
        if arg == "--":
            operands.extend(args[index + 1:])
            break
        if arg in {"-t", "--target-directory"}:
            if index + 1 < len(args):
                dests.append(args[index + 1])
            index += 2
            continue
        if arg.startswith("--target-directory="):
            dests.append(arg.split("=", 1)[1])
            index += 1
            continue
        if arg.startswith("-"):
            index += 1
            continue
        operands.append(arg)
        index += 1
    return dests or operands[-1:]


def _paired(args: list[str], names: set[str], glued: str) -> list[str]:
    found: list[str] = []
    index = 1
    while index < len(args):
        arg = args[index]
        if arg in names:
            if index + 1 < len(args):
                found.append(args[index + 1])
            index += 2
            continue
        for name in names:
            if name.startswith("--") and arg.startswith(name + "="):
                found.append(arg.split("=", 1)[1])
        if (
            glued
            and not arg.startswith("--")
            and arg.startswith(glued)
            and len(arg) > len(glued)
        ):
            found.append(arg[len(glued):])
        index += 1
    return found


def _command_word(tokens: list[str]) -> str | None:
    stripped = _strip_redir(tokens)
    index = 0
    while index < len(stripped) and _ASSIGN.match(stripped[index]):
        index += 1
    while index < len(stripped) and (
        stripped[index] in _COMPOUND_OPEN or stripped[index] == "!"
    ):
        index += 1
    if index >= len(stripped):
        return None
    token = stripped[index]
    if token in _COMPOUND_CLOSE or token in _COMPOUND_SKIP or token == "in":
        return None
    return token


def _segment_writes(tokens: list[str]) -> bool:
    word = _command_word(tokens)
    if word == "git":
        return False
    if any(_path_writes_data(item) for item in _redir_targets(tokens)):
        return True
    stripped = _strip_redir(tokens)
    if word == "(":
        if ")" not in stripped:
            return True
        end = len(stripped) - 1 - stripped[::-1].index(")")
        start = stripped.index("(")
        return _segment_writes(stripped[start + 1:end])
    if word in {"cp", "mv", "ln"} and any(
        _path_writes_data(item) for item in _destinations(stripped)
    ):
        return True
    if word == "tar" and any(
        _path_writes_data(item) for item in _paired(stripped, {"-C", "--directory"}, "-C")
    ):
        return True
    if word == "unzip" and any(
        _path_writes_data(item) for item in _paired(stripped, {"-d"}, "-d")
    ):
        return True
    if word == "gh" and stripped[:3] == ["gh", "run", "download"] and any(
        _path_writes_data(item) for item in _paired(stripped, {"--dir", "-D"}, "-D")
    ):
        return True
    return False


def _run_writes_data(run: str) -> bool:
    for tokens in _commands(run):
        if tokens and _segment_writes(tokens):
            return True
    return False

def _workdir(job: dict, step: dict) -> str:
    if "working-directory" in step:
        return str(step["working-directory"])
    defaults = (job.get("defaults") or {}).get("run") or {}
    return str(defaults.get("working-directory") or "")


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
        shell = step.get("shell")
        if shell is not None and str(shell).split()[:1] != ["bash"]:
            problems.append(f"{job_name}: shell is not bash")
        uses = str(step.get("uses") or "")
        if uses.startswith("./") or uses.startswith("../"):
            problems.append(f"{job_name}: local action {uses}")
        in_link = step.get("name") == LINK_NAME
        workdir = _workdir(job, step)
        for tokens in _commands(run):
            if tokens is None:
                problems.append(f"{job_name}: unparseable shell")
                continue
            problems.extend(_command_problems(job_name, tokens, workdir, in_link))
        with_ = step.get("with") or {}
        if with_.get("repository") == ENGINE_REPOSITORY and with_.get("ref") != PIN_REF:
            problems.append(f"{job_name}: engine checkout ref is not the verified pin")
    links = [step for step in steps if step.get("name") == LINK_NAME]
    if len(links) == 1:
        link_at = steps.index(links[0])
        wrote = any(
            _action_writes_data(step) or _run_writes_data(step.get("run") or "")
            for step in steps[link_at + 1:]
        )
        if wrote:
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
        ("python -I -m pytest", "rejected module pytest"),
        ("python -I -m tox", "rejected module tox"),
        ("python -I -m nox", "rejected module nox"),
        (
            "npm install -g @anthropic-ai/claude-code@2.1.267",
            "rejected command npm",
        ),
        ("npm install -g @anthropic-ai/claude-code@latest", "rejected command npm"),
        ("env python scripts/x.py", "rejected command env"),
        ("exec python scripts/x.py", "rejected command exec"),
        ("timeout 60 python scripts/x.py", "rejected command timeout"),
        ("( python scripts/x.py )", "missing -I"),
        ("`python scripts/x.py`", "missing -I"),
        ("eval 'python scripts/x.py'", "rejected command eval"),
        ("bash -c 'python scripts/x.py'", "rejected command bash"),
        ("bash -e scripts/x.sh", "rejected command bash"),
        ("cat x | bash -s", "rejected command bash"),
        ("sh -c ./x", "rejected command sh"),
        ("node -e 'require(\"./scripts/x.js\")'", "rejected command node"),
        ("python -I -m pdb scripts/x.py", "rejected module pdb"),
        ("python -I -m runpy scripts.x", "rejected module runpy"),
        ("python -I -m unittest discover -s scripts", "rejected module unittest"),
        ("python -I -m cProfile scripts/x.py", "rejected module cProfile"),
        ("python -I -m trace --run scripts/x.py", "rejected module trace"),
        ("python -I engine/../data/scripts/x.py", "not an allowed isolated form"),
        ("python -I engine/models/evil.yaml", "not an allowed isolated form"),
        (
            'python -I -m pip install "$GITHUB_WORKSPACE/engine/../data"',
            "not allowed",
        ),
        (
            "python -I -c 'exec(open(\"scripts/x.py\").read())'",
            "rejected python -c",
        ),
        ("find . -name x.py -exec python {} ';'", "rejected find -exec"),
        ("xargs python < list", "rejected command xargs"),
        ("sudo python scripts/x.py", "rejected command sudo"),
        ("nohup python scripts/x.py", "rejected command nohup"),
        ("command python scripts/x.py", "rejected command command"),
        ("builtin source scripts/x.sh", "rejected command builtin"),
        ("perl scripts/x.pl", "rejected command perl"),
        ("ruby scripts/x.rb", "rejected command ruby"),
        ("deno run x.ts", "rejected command deno"),
        ("bun x.ts", "rejected command bun"),
        ("pip3.11 install -r r.txt", "pip install is not python -I -m pip"),
        ("/bin/bash scripts/x.sh", "rejected command /bin/bash"),
        ("zsh scripts/x.sh", "rejected command zsh"),
        ("git -c core.hooksPath=hooks commit -m x", "rejected git -c"),
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


@pytest.mark.parametrize(
    ("step", "fragment"),
    [
        (
            "\n      - uses: ./data/.github/actions/x\n",
            "local action ./data/.github/actions/x",
        ),
        (
            "\n      - name: s\n        shell: python {0}\n        run: import scripts.x\n",
            "shell is not bash",
        ),
        (
            "\n      - uses: actions/cache@v4\n        with:\n"
            "          path: ./data/models\n          key: k\n",
            "restore writes under data/ after the link step",
        ),
        (
            "\n      - uses: actions/cache@v4\n        with:\n"
            "          path: ${{ github.workspace }}/data/models\n          key: k\n",
            "restore writes under data/ after the link step",
        ),
        (
            "\n      - uses: actions/download-artifact@v4\n        with:\n          name: x\n",
            "restore writes under data/ after the link step",
        ),
        (
            "\n      - uses: actions/download-artifact@v4\n        with:\n"
            "          name: x\n          path: .\n",
            "restore writes under data/ after the link step",
        ),
        (
            "\n      - name: Fetch copies\n        run: gh run download 1 --dir data/models\n",
            "restore writes under data/ after the link step",
        ),
        (
            "\n      - name: s\n        run: echo ${{ github.head_ref }}\n",
            "untrusted expression in run script",
        ),
    ],
)
def test_a_step_level_bypass_is_rejected(step: str, fragment: str) -> None:
    text = _text("daily-research")
    needle = "\n      - name: Install dependencies\n"
    assert text.count(needle) == 1
    problems = isolation_problems(text.replace(needle, step + needle, 1))
    assert any(fragment in problem for problem in problems), problems


def test_price_reread_restore_filters_events_from_the_environment() -> None:
    step = next(
        item
        for item in _document(_text("price-reread"))["jobs"]["reread"]["steps"]
        if item.get("name") == "Restore last week's retained copies"
    )
    assert step["env"]["EVENT_SCHEDULE"] == "schedule"
    assert step["env"]["EVENT_DISPATCH"] == "workflow_dispatch"
    assert "env.EVENT_SCHEDULE" in step["run"]
    assert "env.EVENT_DISPATCH" in step["run"]
    assert "${{" not in step["run"]


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
