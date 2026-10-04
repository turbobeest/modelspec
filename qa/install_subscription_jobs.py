"""Render/install launchd templates. This script never calls launchctl or loads jobs."""

from __future__ import annotations

import argparse
import plistlib
from pathlib import Path

from qa.tui_harness import ROOT
from qa.subscription_jobs import DEFAULT_STATE

TEMPLATES = Path(__file__).with_name("launchd")


def render(template: Path, repo: Path, state: Path, logs: Path) -> dict:
    text = template.read_text()
    import html
    for marker, value in {"@@REPO@@": repo, "@@STATE@@": state, "@@LOGS@@": logs}.items():
        text = text.replace(marker, html.escape(str(value)))
    return plistlib.loads(text.encode())


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=ROOT, help="Stable public main checkout after merge")
    parser.add_argument("--state-dir", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--destination", type=Path, default=Path.home() / "Library/LaunchAgents")
    parser.add_argument("--logs", type=Path, default=Path.home() / "Library/Logs")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    for template in sorted(TEMPLATES.glob("*.plist")):
        payload = render(template, args.repo.expanduser().resolve(), args.state_dir.expanduser(), args.logs.expanduser())
        target = args.destination.expanduser() / template.name
        if args.dry_run:
            print(plistlib.dumps(payload).decode())
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            args.logs.expanduser().mkdir(parents=True, exist_ok=True)
            if target.is_symlink():
                raise ValueError("LaunchAgent files must not be symlinks")
            target.write_bytes(plistlib.dumps(payload))
        print(f"{'Would install' if args.dry_run else 'Installed, not loaded'} {target}")
    print("Load each job only after its first successful manual run and doctor certification.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
