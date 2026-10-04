"""Refuse stale generated guidance before packaging the thin client."""

import hashlib
import json
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    def initialize(self, version, build_data):
        root = Path(self.root)
        bundle = json.loads((root / "cli/modelspec/agent-bundle.json").read_text())
        for relative, expected in bundle["source_hashes"].items():
            if hashlib.sha256((root / relative).read_bytes()).hexdigest() != expected:
                raise ValueError("CLI guidance is stale. Run python -m pipeline.agent_copy write.")
