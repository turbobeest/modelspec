"""Audit source-copy policy from bounded manifests and file existence."""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

from decision.retention import canonical_host, cite_only_origin_restrictive
from scripts.data_trust.catalogue import Finding

MAX_FILES = 50_000
MAX_MANIFEST_BYTES = 2 * 1024 * 1024
MAX_MANIFEST_NODES = 100_000
MAX_MANIFEST_DEPTH = 20
PATH_FIELDS = ("path", "file", "copy", "copy_path", "raw_path", "artifact")
# Extracted or derived page text kept beside a copy (MODEL-515). It is page content
# under the same retention rule as a copy, so it gets the same origin test.
EXTRACT_FIELDS = ("visible_copy", "visible_path", "text_copy", "text_path",
                  "extract", "extract_path", "normalized_path")
ORIGIN_FIELDS = ("url", "requested_url", "source_url", "sourceURL", "final_url")
BODY_SUFFIXES = {".gz", ".html", ".htm", ".pdf"}
# MODEL-517: a manifest record can name its page (`name`, `page_id`, `page`) instead of
# giving a path, and the page's files sit beside the manifest as `<name>.*` or
# `<name>-*`. These suffixes are the page-derived files such a link can reach.
NAME_FIELDS = ("name", "page_id", "page")
LINKED_SUFFIXES = BODY_SUFFIXES | {".txt", ".png", ".json"}
DERIVATIVE_TAGS = {"regions", "text", "visible", "extract", "raw", "screenshot", "preview",
                   "normalized", "body", "copy", "html"}
# A non-2xx response is a block or error page, with nothing to retain, when it is small
# (block pages run about 5 KB; 8 KiB leaves headroom) or its title is a known block marker.
# A larger error response may be a paywall teaser holding page text, so it is judged.
BLOCK_PAGE_BYTES = 8192
BLOCK_MARKERS = re.compile(r"attention required|cloudflare|access denied|just a moment|captcha",
                           re.IGNORECASE)
# Record fields that carry page text; other long strings (errors, URL lists) are not text.
TEXT_KEYS = ("preview", "excerpt", "text", "content", "body", "snippet", "quote", "extract",
             "visible")
SHA_IN_NAME = re.compile(r"(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])")
# Page text kept inline in a record. A short quote is a sentence or two; 280 characters
# (the length of one post) is the longest string still read as a quote, not a page body.
MAX_INLINE_TEXT = 280


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
            if (any(key in value for key in (*PATH_FIELDS, *EXTRACT_FIELDS, *NAME_FIELDS))
                    and any(key in value for key in (*ORIGIN_FIELDS, "resolved_urls",
                                                     "sha256", "bytes", "snapshot_ref"))):
                yield value
            pending.extend((child, depth + 1) for child in value.values()
                           if isinstance(child, (dict, list)))
        elif isinstance(value, list):
            pending.extend((child, depth + 1) for child in value
                           if isinstance(child, (dict, list)))


def _all_records(document):
    """Every dict that carries its own origin, bounded like `_records`."""
    pending = [(document, 0)]
    visited = 0
    while pending:
        value, depth = pending.pop()
        visited += 1
        if visited > MAX_MANIFEST_NODES or depth > MAX_MANIFEST_DEPTH:
            raise ValueError("manifest structure limit")
        if isinstance(value, dict):
            if any(key in value for key in (*ORIGIN_FIELDS, "resolved_urls")):
                yield value
            pending.extend((child, depth + 1) for child in value.values()
                           if isinstance(child, (dict, list)))
        elif isinstance(value, list):
            pending.extend((child, depth + 1) for child in value
                           if isinstance(child, (dict, list)))


def _inline_text(record: dict):
    """Yield long page-text strings inside a record, without entering a child record that
    has its own origin (that child is judged by its own origin)."""
    pending = [(value, 0, str(key).lower()) for key, value in record.items()
               if key not in ORIGIN_FIELDS and key != "resolved_urls"]
    visited = 0
    while pending:
        value, depth, key = pending.pop()
        visited += 1
        if visited > MAX_MANIFEST_NODES or depth > MAX_MANIFEST_DEPTH:
            raise ValueError("manifest structure limit")
        if isinstance(value, str):
            if len(value) > MAX_INLINE_TEXT and any(word in key for word in TEXT_KEYS):
                yield value
        elif isinstance(value, dict):
            if not any(k in value for k in (*ORIGIN_FIELDS, "resolved_urls")):
                pending.extend((child, depth + 1, str(k).lower()) for k, child in value.items())
        elif isinstance(value, list):
            pending.extend((child, depth + 1, key) for child in value)


def _names(record: dict) -> tuple[str, ...]:
    return tuple(record[key] for key in NAME_FIELDS
                 if isinstance(record.get(key), str) and record[key])


def _linked(name: str, stem: str) -> bool:
    """The page's own stem, or the stem plus a derivative tag, a counter or a digest.
    `pricing-v2` is another page, not `pricing`."""
    if stem == name:
        return True
    if not stem.startswith(name + "-"):
        return False
    tail = stem[len(name) + 1:]
    return tail in DERIVATIVE_TAGS or bool(re.fullmatch(r"\d+|[0-9a-f]{8,64}", tail))


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
    referenced, attributed, restricted, restricted_extracts = set(), set(), set(), set()
    restricted_linked, restricted_inline = set(), set()
    by_directory = {}
    for path in files:
        by_directory.setdefault(path.parent, []).append(path)
    by_digest = {}
    for path in files:
        for digest in SHA_IN_NAME.findall(path.name):
            by_digest.setdefault(digest, []).append(path)

    def check_cite_only_text(manifest, record):
        """Page text kept inline, and files linked by page name or digest (MODEL-517)."""
        try:
            origins = _origins(record)
        except ValueError:
            return
        if not origins or not cite_only_origin_restrictive(origins[0], origins[1:]):
            return
        if any(True for _ in _inline_text(record)):
            restricted_inline.add(manifest)
        status = record.get("status")
        if isinstance(status, int) and not isinstance(status, bool) and not 200 <= status < 300:
            size, title = record.get("bytes"), record.get("title")
            small = isinstance(size, int) and not isinstance(size, bool) and size <= BLOCK_PAGE_BYTES
            if small or (isinstance(title, str) and BLOCK_MARKERS.search(title)):
                return  # a block or error page carries no page content to retain
        for name in _names(record):
            for path in by_directory.get(manifest.parent, ()):
                if (path != manifest and path.suffix in LINKED_SUFFIXES
                        and path.is_relative_to(root / "research")
                        and _linked(name, path.name[:-len(path.suffix)])):
                    restricted_linked.add(path)
        digest = record.get("sha256")
        if isinstance(digest, str):
            for path in by_digest.get(digest.removeprefix("sha256:").lower(), ()):
                if path != manifest and path.suffix in LINKED_SUFFIXES:
                    restricted_linked.add(path)

    def check_record(manifest, record, fields, kept):
        values = [record[key] for key in fields if record.get(key) is not None]
        if not values:
            return
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
            return
        try:
            origins = _origins(record)
        except ValueError:
            add(manifest, "retained_copy_origin", "error")
            return
        if not origins:
            return
        attributed.update(resolved)
        if cite_only_origin_restrictive(origins[0], origins[1:]):
            kept.update(resolved)

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
            check_record(manifest, record, PATH_FIELDS, restricted)
            check_record(manifest, record, EXTRACT_FIELDS, restricted_extracts)
        if manifest.is_relative_to(root / "research"):
            try:
                for record in _all_records(document):
                    check_cite_only_text(manifest, record)
            except ValueError:
                add(manifest, "retained_copy_manifest_limit")
    for path in sorted(restricted):
        add(path, "retained_cite_only_copy", "error")
    for path in sorted(restricted_extracts - restricted):
        add(path, "retained_cite_only_extract", "error")
    for path in sorted(restricted_linked - restricted - restricted_extracts):
        add(path, "retained_cite_only_linked", "error")
    for path in sorted(restricted_inline):
        add(path, "retained_cite_only_inline_text", "error")
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
