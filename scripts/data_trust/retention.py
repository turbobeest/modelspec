"""Audit source-copy policy from bounded manifests and file existence."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from decision.retention import canonical_host, cite_only_origin_restrictive
from scripts.data_trust.catalogue import Finding

MAX_FILES = 50_000
MAX_MANIFEST_BYTES = 2 * 1024 * 1024
MAX_MANIFEST_NODES = 100_000
MAX_MANIFEST_DEPTH = 20
PATH_FIELDS = ("path", "file", "copy", "copy_path", "raw_path", "artifact")
ORIGIN_FIELDS = ("url", "requested_url", "source_url", "sourceURL", "final_url")
BODY_SUFFIXES = {".gz", ".html", ".htm", ".pdf"}


def _files(root: Path) -> set[Path]:
    if (root / ".git").exists():
        result = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z"],
            capture_output=True, check=True, timeout=15,
        )
        names = result.stdout.decode("utf-8").split("\0")
        if len(names) > MAX_FILES + 1:
            raise ValueError("file inventory limit")
        return {root / name for name in names if name}
    files = set()
    entries = 0
    for directory, dirs, names in os.walk(root, followlinks=False):
        dirs[:] = [name for name in dirs if name not in {".git", ".venv", "node_modules"}]
        entries += len(dirs) + len(names)
        if entries > MAX_FILES:
            raise ValueError("file inventory limit")
        files.update(Path(directory) / name for name in names)
    return files


def _records(document):
    pending = [(document, 0)]
    visited = 0
    while pending:
        value, depth = pending.pop()
        visited += 1
        if visited > MAX_MANIFEST_NODES or depth > MAX_MANIFEST_DEPTH:
            raise ValueError("manifest structure limit")
        if isinstance(value, dict):
            if (any(key in value for key in PATH_FIELDS)
                    and any(key in value for key in (*ORIGIN_FIELDS, "resolved_urls",
                                                     "sha256", "bytes", "snapshot_ref"))):
                yield value
            pending.extend((child, depth + 1) for child in value.values()
                           if isinstance(child, (dict, list)))
        elif isinstance(value, list):
            pending.extend((child, depth + 1) for child in value
                           if isinstance(child, (dict, list)))


def _origins(record: dict) -> tuple[str, ...]:
    origins = [record[key] for key in ORIGIN_FIELDS if key in record]
    if "resolved_urls" in record:
        redirects = record["resolved_urls"]
        if not isinstance(redirects, list):
            raise ValueError("invalid origin metadata")
        origins.extend(redirects)
    for origin in origins:
        if not isinstance(origin, str) or not origin:
            raise ValueError("invalid origin metadata")
        try:
            if canonical_host(origin) is None:
                raise ValueError("non-HTTP origin")
        except ValueError:
            # The restrictive helper handles malformed HTTP origins below.
            if not origin.lstrip().lower().startswith(("http:", "https:")):
                raise
    return tuple(origins)


def inventory(root: Path) -> list[Finding]:
    root = root.resolve()
    findings = []

    def add(path, rule, severity="warning"):
        findings.append(Finding(str(path.relative_to(root)), "source_copy", rule, severity))

    try:
        files = _files(root)
    except (OSError, ValueError, subprocess.SubprocessError):
        return [Finding("catalogue", "source_copy", "retained_copy_inventory_limit", "warning")]
    referenced, attributed, restricted = set(), set(), set()
    manifests = sorted((path for path in files if path.suffix == ".json"),
                       key=lambda path: (not any(word in path.name.lower()
                                                 for word in ("source", "manifest")), path))
    for manifest in manifests:
        try:
            target = manifest.resolve()
            if target in referenced:
                continue
            if not target.is_relative_to(root):
                add(manifest, "retained_copy_unsafe_path")
                continue
            with manifest.open("rb") as handle:
                raw = handle.read(MAX_MANIFEST_BYTES + 1)
            if len(raw) > MAX_MANIFEST_BYTES:
                add(manifest, "retained_copy_manifest_limit")
                continue
            document = json.loads(raw)
            records = list(_records(document))
        except (OSError, UnicodeError, json.JSONDecodeError, RecursionError):
            add(manifest, "retained_copy_manifest_parse")
            continue
        except (ValueError, RuntimeError):
            add(manifest, "retained_copy_manifest_limit")
            continue
        for record in records:
            values = [record[key] for key in PATH_FIELDS if record.get(key) is not None]
            if not values:
                continue
            resolved = set()
            for value in values:
                if not isinstance(value, str) or not value:
                    add(manifest, "retained_copy_unsafe_path")
                    continue
                path = Path(value)
                if path.is_absolute():
                    add(manifest, "retained_copy_unsafe_path")
                    continue
                candidates = {root / path, manifest.parent / path}
                safe, unsafe = set(), False
                for candidate in candidates:
                    try:
                        target = candidate.resolve(strict=True)
                        if not target.is_relative_to(root):
                            unsafe = True
                        elif Path(os.path.normpath(candidate)) in files and target.is_file():
                            safe.add(target)
                    except FileNotFoundError:
                        continue
                    except (OSError, ValueError, RuntimeError):
                        unsafe = True
                if len(safe) > 1:
                    add(manifest, "retained_copy_ambiguous_path")
                elif safe:
                    resolved.update(safe)
                else:
                    add(manifest, "retained_copy_unsafe_path" if unsafe else "retained_copy_missing")
            referenced.update(resolved)
            if not resolved:
                continue
            try:
                origins = _origins(record)
            except ValueError:
                add(manifest, "retained_copy_origin", "error")
                continue
            if not origins:
                continue
            attributed.update(resolved)
            if cite_only_origin_restrictive(origins[0], origins[1:]):
                restricted.update(resolved)
    for path in sorted(restricted):
        add(path, "retained_cite_only_copy", "error")
    candidates = referenced | {path for path in files
                               if path.is_relative_to(root / "research") and path.suffix in BODY_SUFFIXES}
    for path in sorted(candidates):
        try:
            target = path.resolve(strict=True)
            if target.is_relative_to(root) and target.is_file() and target not in attributed:
                add(path, "retained_copy_unattributed")
        except FileNotFoundError:
            add(path, "retained_copy_missing")
        except (OSError, ValueError, RuntimeError):
            add(path, "retained_copy_unsafe_path")
    return findings
