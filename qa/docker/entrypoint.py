"""A fixed Linux environment. No credential files are handled here."""

from __future__ import annotations

import os
import re
import sys

PASSED_ENV = frozenset(("TERM", "LANG", "MODELSPEC_MCP_URL"))
VENDOR_ENV = re.compile(
    r"(?:API[_-]?KEY|(?:ANTHROPIC|OPENAI|GEMINI|GOOGLE|XAI|GROK|CLAUDE|CODEX|AZURE|"
    r"AWS|BEDROCK|VERTEX).*(?:TOKEN|KEY|CREDENTIAL|IDENTITY)|GOOGLE_APPLICATION_CREDENTIALS)",
    re.I,
)
CLAUDE_ENV = {
    "CLAUDE_CODE_DISABLE_CLAUDE_MDS": "1",
    "CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1",
    "CLAUDE_CODE_SKIP_PROMPT_HISTORY": "1",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
    "ENABLE_CLAUDEAI_MCP_SERVERS": "false",
    "ENABLE_TOOL_SEARCH": "false",
}


def refuse_vendor_auth(env: dict) -> None:
    if any(VENDOR_ENV.search(name) for name in env if not name.startswith("MODELSPEC_")):
        raise ValueError("Subscription-only harness refuses vendor API-key or token environment")


def runtime_environment(cli: str, mode: str, incoming: dict) -> dict:
    refuse_vendor_auth(incoming)
    env = {
        name: value
        for name, value in incoming.items()
        if name in PASSED_ENV or re.fullmatch(r"MODELSPEC_[A-Z0-9_]+", name)
    }
    env.update(
        HOME="/home/agent",
        PATH="/usr/local/bin:/usr/bin:/bin",
        USER="agent",
        LOGNAME="agent",
        SHELL="/bin/bash",
        TMPDIR="/tmp",
        XDG_CONFIG_HOME="/home/agent/.config",
        XDG_DATA_HOME="/home/agent/.local/share",
        XDG_CACHE_HOME="/home/agent/.cache",
        DISABLE_AUTOUPDATER="1",
        GROK_DISABLE_AUTOUPDATER="1",
    )
    if cli == "claude" and mode == "isolated":
        env.update(CLAUDE_ENV)
    if cli == "gemini":
        env.update(
            NO_BROWSER="true",
            GEMINI_CLI_SYSTEM_SETTINGS_PATH=(
                "/opt/modelspec-harness/gemini-isolated.json"
                if mode == "isolated"
                else "/opt/modelspec-harness/gemini-positive.json"
            ),
            GEMINI_CLI_SYSTEM_DEFAULTS_PATH="/work/gemini-system-unset.json",
        )
    if cli == "grok" and mode != "login":
        # Relax discovery for the positive control without persisting a folder
        # grant into the authentication volume. Isolated runs retain the native
        # trust gate, and inventory rejects any already-trusted customizations.
        env["GROK_FOLDER_TRUST"] = "1" if mode == "isolated" else "0"
        if mode == "isolated":
            env["GROK_MEMORY"] = "0"
            for family in ("CLAUDE", "CURSOR"):
                for kind in ("SKILLS", "RULES", "AGENTS", "MCPS", "HOOKS"):
                    env[f"GROK_{family}_{kind}_ENABLED"] = "0"
    return env


def main() -> None:
    cli, mode, *command = sys.argv[1:]
    if (
        cli not in ("claude", "codex", "gemini", "grok")
        or mode not in ("isolated", "positive", "login")
        or not command
    ):
        raise ValueError("Invalid container invocation")
    os.execvpe(command[0], command, runtime_environment(cli, mode, dict(os.environ)))


if __name__ == "__main__":
    try:
        main()
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(78)
