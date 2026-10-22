"""Record exact acceptance commands and direct exit codes without private output."""
from datetime import UTC, datetime
import json
import os
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parent
label, *command = sys.argv[1:]
log = root / (label + ".private.log")
env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
env.pop("MODELSPEC_SOURCE_CACHE", None)
env.pop("MODELSPEC_SNAPSHOT_ED25519_KEY", None)
env.pop("MODELSPEC_SNAPSHOT_KEY", None)
start = datetime.now(UTC).isoformat()
with log.open("w") as stream:
    result = subprocess.run(command, cwd=root, env=env, stdout=stream, stderr=stream)
row = {"label": label, "command": command, "cwd": str(root), "source_cache_configured": False,
       "started": start, "finished": datetime.now(UTC).isoformat(), "exit": result.returncode,
       "private_log": str(log)}
(root / ("command-" + label + ".public.json")).write_text(json.dumps(row, indent=2) + "\n")
print(json.dumps({"label": label, "exit": result.returncode, "private_log": str(log)}))
raise SystemExit(result.returncode)
