"""List, and with ``--apply`` delete, retained page bytes from cite-only sources (MODEL-419).

Since MODEL-411 (#840) the ``CopyStore`` keeps only a citation for a source on a
host in ``registry/source-retention.json``. Copies written before that decision
are still on disk, in ``~/.cache/modelspec/sources`` and in scratch copy stores
under ``/tmp``. This script finds them.

An entry is identified by the source URL recorded for its ``sha256:<hex>`` ref,
never by its bytes:

- the store's own ``<digest>.citation.json`` sidecar (URL and redirect chain);
- data records naming the ref (``snapshot_ref``, ``copy_ref``, ...) with a URL
  of their own (``url``, ``final_url``, ``resolved_urls``, ...) or a
  ``source_id`` whose URL is in a ``sources`` registry. ``--data-dir`` reads a
  checkout's files; ``--data-git`` reads every data file in a repository's
  history, so refs a later commit replaced are still known.

Each recorded URL goes through ``decision.retention.cite_only_origin``, the
#840 matcher (subdomains, case, trailing dot, port, redirect destinations).
A byte file with no recorded URL is counted (``entries`` minus ``identified``)
and left in place: name more data with ``--data-dir`` or ``--data-git``.

    python scripts/purge_cite_only_copies.py --data-dir ../modelspec-data
    python scripts/purge_cite_only_copies.py --discover /tmp --data-git ../modelspec-data
    python scripts/purge_cite_only_copies.py ... --apply

Dry run by default. ``--apply`` deletes only the matched byte files inside the
copy stores and keeps their citation sidecars. It never writes to a data
directory or repository, and it skips a copy store inside one: committed copies
and their git history are MODEL-409's.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import subprocess
import sys
import threading
from collections import defaultdict
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from decision.retention import cite_only_origin, is_cite_only, metadata_origins  # noqa: E402
from decision.sources import CopyStore  # noqa: E402

REF = re.compile(r"^sha256:([0-9a-f]{64})$")
DIGEST = re.compile(r"^[0-9a-f]{64}$")
PREFIX = re.compile(r"^[0-9a-f]{2}$")
#: Keys whose value is the ref of a retained copy (not a normalised fingerprint).
REF_KEYS = ("snapshot_ref", "copy_ref", "cited_copy_ref", "source_snapshot_ref")
DATA_SUFFIXES = (".yaml", ".yml", ".json", ".jsonl", ".md")
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__"}
FRONT_MATTER = re.compile(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", re.DOTALL)
Loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)


# --- recorded source URLs ------------------------------------------------------------------------


@dataclass
class Provenance:
    """Source URLs recorded for copy refs, gathered from data records."""

    #: ref -> URLs recorded beside it.
    urls: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))
    #: ref -> source ids recorded beside it.
    sources: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))
    #: source id -> URLs, from registries and from records naming both.
    source_urls: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))
    warnings: list[str] = field(default_factory=list)

    def origins(self, ref: str) -> tuple[str, ...]:
        found = set(self.urls.get(ref, ()))
        for source_id in self.sources.get(ref, ()):
            found |= self.source_urls.get(source_id, set())
        return tuple(sorted(found))

    def add_document(self, document: object, where: str) -> None:
        if isinstance(document, dict) and isinstance(document.get("sources"), list):
            for row in document["sources"]:
                if isinstance(row, dict) and isinstance(row.get("id"), str) \
                        and isinstance(row.get("url"), str) and row["url"]:
                    self.source_urls[row["id"]].add(row["url"])
        self._walk(document, where)

    def _walk(self, node: object, where: str) -> None:
        if isinstance(node, dict):
            self._record(node, where)
            for value in node.values():
                self._walk(value, where)
        elif isinstance(node, list):
            for value in node:
                self._walk(value, where)

    def _record(self, node: dict, where: str) -> None:
        refs = [node[key] for key in REF_KEYS
                if isinstance(node.get(key), str) and REF.match(node[key])]
        urls = _record_urls(node, where, self.warnings)
        source_id = node.get("source_id")
        if isinstance(source_id, str) and source_id and urls:
            self.source_urls[source_id].update(urls)
        for ref in refs:
            self.urls[ref].update(urls)
            if isinstance(source_id, str) and source_id:
                self.sources[ref].add(source_id)


def _record_urls(node: dict, where: str, warnings: list[str]) -> set[str]:
    try:
        urls = set(metadata_origins(node))
    except ValueError:
        warnings.append(f"{where}: unreadable resolved_urls; using its other URLs")
        urls = set(metadata_origins({k: v for k, v in node.items() if k != "resolved_urls"}))
    if isinstance(node.get("source_url"), str) and node["source_url"]:
        urls.add(node["source_url"])
    return urls


def parse_documents(name: str, text: str) -> list[object]:
    """The structured records in one data file; a card's are in its front matter."""
    if name.endswith(".json"):
        return [json.loads(text)]
    if name.endswith(".jsonl"):
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    if name.endswith((".yaml", ".yml")):
        return list(yaml.load_all(text, Loader=Loader))
    if name.endswith(".md"):
        match = FRONT_MATTER.match(text)
        return [yaml.load(match.group(1), Loader=Loader)] if match else []
    return []


def _add_file(provenance: Provenance, name: str, text: str, where: str) -> None:
    if not any(key in text for key in REF_KEYS) and "sources" not in text:
        return
    try:
        documents = parse_documents(name, text)
    except (ValueError, yaml.YAMLError) as exc:
        provenance.warnings.append(f"{where}: not parsed ({type(exc).__name__})")
        return
    for document in documents:
        provenance.add_document(document, where)


def read_data_dir(provenance: Provenance, root: Path) -> None:
    for directory, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in sorted(files):
            if name.endswith(DATA_SUFFIXES):
                path = Path(directory) / name
                try:
                    text = path.read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError) as exc:
                    provenance.warnings.append(f"{path}: not read ({type(exc).__name__})")
                    continue
                _add_file(provenance, name, text, str(path))


def read_data_git(provenance: Provenance, repo: Path) -> None:
    """Every data blob reachable from any ref in ``repo``; read-only git plumbing."""
    listing = subprocess.run(["git", "-C", str(repo), "rev-list", "--all", "--objects"],
                             check=True, capture_output=True, text=True).stdout
    blobs: dict[str, str] = {}
    for line in listing.splitlines():
        sha, _, path = line.partition(" ")
        if path.endswith(DATA_SUFFIXES):
            blobs.setdefault(sha, path)
    if not blobs:
        return
    # Stream one blob at a time: a whole history can be gigabytes.
    process = subprocess.Popen(["git", "-C", str(repo), "cat-file", "--batch"],
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    writer = threading.Thread(target=_send, args=(process.stdin, blobs), daemon=True)
    writer.start()
    for sha, path in blobs.items():
        header = process.stdout.readline().decode().split()
        if len(header) != 3 or header[1] != "blob":
            provenance.warnings.append(f"{repo}:{sha}: not a blob")
            continue
        body = process.stdout.read(int(header[2]))
        process.stdout.read(1)
        try:
            text = body.decode("utf-8")
        except UnicodeDecodeError:
            continue
        _add_file(provenance, path, text, f"{repo}@{sha[:12]}:{path}")
    writer.join()
    process.stdout.close()
    if process.wait() != 0:
        raise subprocess.CalledProcessError(process.returncode, "git cat-file --batch")


def _send(stdin, blobs: Iterable[str]) -> None:
    with stdin:
        for sha in blobs:
            stdin.write(f"{sha}\n".encode())


# --- copy stores ---------------------------------------------------------------------------------


@dataclass(frozen=True)
class Entry:
    """Retained bytes in a copy store whose recorded source is cite-only."""

    root: Path
    ref: str
    path: Path
    matched: tuple[str, ...]
    #: ``sidecar`` when the store's own citation names the URL, else ``data``.
    evidence: str


def _reason(exc: OSError) -> str:
    return exc.strerror or type(exc).__name__


def _scandir(directory: Path, errors: list[str]) -> list[os.DirEntry] | None:
    """The sorted entries of ``directory``; ``None``, with the reason recorded, if unreadable."""
    try:
        with os.scandir(directory) as listing:
            return sorted(listing, key=lambda entry: entry.name)
    except FileNotFoundError:
        return []
    except OSError as exc:
        errors.append(f"{directory}: skipped, unreadable ({_reason(exc)})")
        return None


def _real_dir(entry: os.DirEntry) -> bool:
    try:
        return entry.is_dir(follow_symlinks=False)
    except OSError:
        return False


def store_entries(root: Path, errors: list[str]) -> Iterator[tuple[str, Path, bool]]:
    """Every digest-named file in a ``CopyStore`` root, as ``(ref, path, is_regular)``.

    Sidecars are excluded, prefix symlinks are not followed, and an unreadable
    directory is recorded in ``errors`` and passed over.
    """
    for prefix in _scandir(root, errors) or ():
        if not (PREFIX.match(prefix.name) and _real_dir(prefix)):
            continue
        for entry in _scandir(Path(prefix.path), errors) or ():
            if DIGEST.match(entry.name) and entry.name.startswith(prefix.name):
                try:
                    regular = entry.is_file(follow_symlinks=False)
                except OSError:
                    regular = False
                yield f"sha256:{entry.name}", Path(entry.path), regular


def is_store_root(path: Path, errors: list[str]) -> bool:
    for prefix in _scandir(path, errors) or ():
        if PREFIX.match(prefix.name) and _real_dir(prefix):
            for entry in _scandir(Path(prefix.path), errors) or ():
                name = entry.name.removesuffix(".citation.json")
                if DIGEST.match(name) and name.startswith(prefix.name):
                    return True
    return False


def discover_roots(base: Path, errors: list[str], notes: list[str]) -> list[Path]:
    """Copy-store roots under ``base``: directories of ``<2 hex>/<64 hex>`` files.

    The walk stays on ``base``'s filesystem and never follows a symlink; a
    symlinked ``base`` is resolved first, and the resolution is noted.
    """
    if base.is_symlink():
        resolved = base.resolve()
        notes.append(f"{base}: a symlink; discovering under {resolved} instead")
        base = resolved
    try:
        device = os.lstat(base).st_dev
    except FileNotFoundError:
        return []
    except OSError as exc:
        errors.append(f"{base}: skipped, unreadable ({_reason(exc)})")
        return []
    roots, pending = [], [base]
    while pending:
        directory = pending.pop()
        entries = _scandir(directory, errors)
        if entries is None:
            continue
        found = any(PREFIX.match(e.name) and _real_dir(e) for e in entries) \
            and is_store_root(directory, errors)
        if found:
            roots.append(directory)
        for entry in reversed(entries):
            if entry.name in SKIP_DIRS or not _real_dir(entry) \
                    or (found and PREFIX.match(entry.name)):
                continue
            try:
                if entry.stat(follow_symlinks=False).st_dev != device:
                    notes.append(f"{entry.path}: another filesystem; not searched")
                    continue
            except OSError as exc:
                errors.append(f"{entry.path}: skipped, unreadable ({_reason(exc)})")
                continue
            pending.append(Path(entry.path))
    return sorted(roots)


def _git_checkouts(path: Path) -> Iterator[Path]:
    """Each directory at or above ``path`` that has a ``.git`` entry (raises if unknowable)."""
    for parent in (path, *path.parents):
        try:
            os.lstat(parent / ".git")
        except FileNotFoundError:
            continue
        except NotADirectoryError:
            continue
        yield parent


def protected(root: Path, data: Iterable[Path]) -> tuple[str, bool] | None:
    """Why ``root`` must be skipped, as ``(reason, is_error)``, or ``None`` to process it.

    A store inside a data directory or a private-repository checkout is never
    purged here. A ``.git`` entry at or above the store that git cannot read
    leaves the checkout unknown, so the store is skipped as an error.
    """
    resolved = root.resolve()
    if any(resolved == d.resolve() or d.resolve() in resolved.parents for d in data):
        return "inside a data directory", False
    try:
        checkouts = list(_git_checkouts(resolved))
    except OSError as exc:
        return f"cannot check for a .git entry ({_reason(exc)})", True
    for checkout in checkouts:
        try:
            result = subprocess.run(["git", "-C", str(checkout), "remote", "-v"],
                                    capture_output=True, text=True)
        except OSError as exc:
            return f"cannot run git for {checkout} ({_reason(exc)})", True
        if result.returncode != 0:
            return f"{checkout}/.git exists but git cannot read it", True
        if "turbobeest/modelspec-data" in result.stdout:
            return "inside a private-repository checkout", False
    return None


@dataclass
class Scan:
    entries: list[Entry] = field(default_factory=list)
    #: Byte files seen, and how many of them have any recorded source URL.
    scanned: int = 0
    identified: int = 0


def find_entries(roots: Iterable[Path], provenance: Provenance, errors: list[str]) -> Scan:
    scan = Scan()
    for root in roots:
        store = CopyStore(root)
        for ref, path, regular in store_entries(root, errors):
            scan.scanned += 1
            try:
                citation = store.citation(ref)
                sidecar = metadata_origins(citation) if citation is not None else ()
            except (ValueError, OSError) as exc:
                provenance.warnings.append(f"{path}: citation sidecar unreadable ({exc})")
                sidecar = ()
            origins = provenance.origins(ref)
            scan.identified += bool(sidecar or origins)
            if sidecar and cite_only_origin(sidecar[0], sidecar[1:]):
                matched, evidence = sidecar, "sidecar"
            elif origins and cite_only_origin(origins[0], origins[1:]):
                matched, evidence = origins, "data"
            else:
                continue
            if not regular:
                errors.append(f"{path}: cite-only name but not a regular file; skipped")
                continue
            scan.entries.append(Entry(root, ref, path,
                                      tuple(u for u in matched if is_cite_only(u)), evidence))
    return scan


def delete(entry: Entry) -> None:
    """Unlink one matched page, only a regular file strictly inside its resolved store."""
    root = entry.root.resolve(strict=True)
    name = entry.path.name
    if not DIGEST.match(name) or entry.ref != f"sha256:{name}":
        raise ValueError(f"refusing to delete a file not named by its ref: {entry.path}")
    parent = entry.path.parent.resolve(strict=True)
    target = parent / name
    if parent.parent != root or parent.name != name[:2] or root not in target.parents:
        raise ValueError(f"refusing to delete outside its copy store: {entry.path}")
    if not stat.S_ISREG(os.lstat(target).st_mode):
        raise ValueError(f"refusing to delete a non-regular file: {entry.path}")
    os.unlink(target)


# --- command line --------------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--root", action="append", type=Path, default=[],
                        help="a CopyStore root (default: CopyStore's own root)")
    parser.add_argument("--discover", action="append", type=Path, default=[],
                        help="find every CopyStore root under this directory")
    parser.add_argument("--data-dir", action="append", type=Path, default=[],
                        help="a data checkout to read refs and source URLs from "
                             "(default: $MODELSPEC_DATA_DIR)")
    parser.add_argument("--data-git", action="append", type=Path, default=[],
                        help="a repository whose whole history is read for refs and URLs")
    parser.add_argument("--apply", action="store_true", help="delete the matched byte files")
    parser.add_argument("--limit", type=int, default=0,
                        help="print at most this many matches (default: all)")
    args = parser.parse_args(argv)

    data_dirs = list(args.data_dir)
    if not data_dirs and not args.data_git and os.environ.get("MODELSPEC_DATA_DIR"):
        data_dirs.append(Path(os.environ["MODELSPEC_DATA_DIR"]))
    if not data_dirs and not args.data_git:
        print("warning: no --data-dir or --data-git; only citation sidecars name sources",
              file=sys.stderr)

    provenance = Provenance()
    for directory in data_dirs:
        read_data_dir(provenance, directory)
    for repo in args.data_git:
        read_data_git(provenance, repo)

    errors: list[str] = []
    notes: list[str] = []
    roots = []
    for root in args.root:
        if root.is_symlink():
            notes.append(f"{root}: a symlink; using {root.resolve()}")
        roots.append(root.resolve())
    for base in args.discover:
        roots.extend(discover_roots(base, errors, notes))
    if not args.root and not args.discover:
        roots.append(CopyStore().root.resolve())
    guarded = [*data_dirs, *args.data_git]
    kept = []
    for root in dict.fromkeys(roots):
        skip = protected(root, guarded)
        if skip is None:
            kept.append(root)
            continue
        reason, is_error = skip
        if is_error:
            errors.append(f"{root}: skipped, {reason}")
        else:
            notes.append(f"{root}: skipped, {reason}")

    scan = find_entries(kept, provenance, errors)
    entries = scan.entries
    shown = entries[:args.limit] if args.limit else entries
    for entry in shown:
        print(f"{entry.evidence}\t{entry.ref}\t{entry.matched[0]}\t{entry.root}")
    if len(shown) < len(entries):
        print(f"... {len(entries) - len(shown)} more")
    for warning in provenance.warnings:
        print(f"warning: {warning}", file=sys.stderr)
    for note in notes:
        print(f"note: {note}", file=sys.stderr)
    print(f"stores={len(kept)} entries={scan.scanned} identified={scan.identified} "
          f"cite_only={len(entries)} mode={'apply' if args.apply else 'dry-run'}")
    if args.apply:
        deleted = 0
        for entry in entries:
            try:
                delete(entry)
                deleted += 1
            except (OSError, ValueError) as exc:
                errors.append(f"{entry.path}: not deleted ({exc})")
        remaining = find_entries(kept, provenance, errors).entries
        print(f"deleted={deleted} remaining_cite_only={len(remaining)}")
    else:
        remaining = []
    errors = list(dict.fromkeys(errors))
    for error in errors:
        print(f"error: {error}", file=sys.stderr)
    print(f"skipped_for_error={len(errors)}")
    return 1 if remaining or errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
