"""Stage pinned MODEL-439 acceptance trees without modifying shared git state."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
import io
import json
import os
from pathlib import Path
import subprocess
import tarfile


def git(repo, *args, env=None):
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, env=env,
    ).stdout


def archive(repo, revision, destination, *, env=None):
    destination.mkdir(parents=True, exist_ok=False)
    data = git(repo, "archive", revision, env=env)
    with tarfile.open(fileobj=io.BytesIO(data)) as handle:
        handle.extractall(destination, filter="data")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--main-ref", required=True)
    parser.add_argument("--policy-ref", required=True)
    parser.add_argument("--combined-ref", required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    revisions = {
        "main": git(args.repo, "rev-parse", args.main_ref).decode().strip(),
        "policy": git(args.repo, "rev-parse", args.policy_ref).decode().strip(),
        "combined": git(args.repo, "rev-parse", args.combined_ref).decode().strip(),
        "baseline_data": git(args.data_dir, "rev-parse", "HEAD").decode().strip(),
    }
    archive(args.data_dir, revisions["baseline_data"], output / "baseline-data")
    archive(args.repo, revisions["main"], output / "main")
    policy = git(args.repo, "show", revisions["policy"] + ":registry/source-retention.json")
    (output / "hosts-866.json").write_bytes(policy)
    common = Path(git(args.repo, "rev-parse", "--git-common-dir").decode().strip())
    if not common.is_absolute():
        common = (args.repo / common).resolve()
    objects = output / "merge-objects"
    objects.mkdir()
    merge_env = dict(os.environ, GIT_OBJECT_DIRECTORY=str(objects),
                     GIT_ALTERNATE_OBJECT_DIRECTORIES=str(common / "objects"))
    result = subprocess.run(
        ["git", "-C", str(args.repo), "merge-tree", "--write-tree",
         revisions["main"], revisions["combined"]],
        capture_output=True, env=merge_env,
    )
    (output / "merge.txt").write_bytes(result.stdout + result.stderr)
    if result.returncode not in (0, 1):
        result.check_returncode()
    metadata = {"revisions": revisions, "combined_merge_clean": result.returncode == 0,
                "prepared_at": datetime.now(UTC).isoformat()}
    if result.returncode == 0:
        tree = result.stdout.decode().splitlines()[0]
        archive(args.repo, tree, output / "combined", env=merge_env)
        metadata["combined_tree"] = tree
    (output / "identities.public.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps(metadata, sort_keys=True))


if __name__ == "__main__":
    main()
