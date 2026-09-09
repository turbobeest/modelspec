#!/usr/bin/env python3
"""Opt-in, bounded Grok runner for benchmark pages admitted by the eligibility gate."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import signal
import subprocess
import sys
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CENSUS = ROOT / "benchmarks" / "_census"
GLOBAL_LOCK_PATH = CENSUS / "cache" / "eligible-run.lock"
sys.path.insert(0, str(ROOT))
from schema.benchmark_eligibility import EligibilityReport  # noqa: E402
from scripts.benchmarks.downselect import build_report  # noqa: E402

STOP = threading.Event()
STATUS_LOCK = threading.RLock()


def now() -> str:
    return datetime.now(UTC).isoformat()


def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def write_status(run_dir: Path, status: dict[str, object]) -> None:
    with STATUS_LOCK:
        status["updated_at"] = now()
        atomic_json(run_dir / "status.json", status)


def run_logged(command: list[str], log_dir: Path, stem: str, cwd: Path) -> int:
    out = log_dir / f"{stem}.stdout.jsonl"
    err = log_dir / f"{stem}.stderr.log"
    with out.open("w", encoding="utf-8") as stdout, err.open("w", encoding="utf-8") as stderr:
        proc = subprocess.Popen(command, cwd=cwd, stdout=stdout, stderr=stderr)
        started = now()
        atomic_json(log_dir / f"{stem}.process.json", {"pid": proc.pid, "started": started})
        returncode = proc.wait()
    atomic_json(
        log_dir / f"{stem}.process.json",
        {"pid": proc.pid, "started": started, "returncode": returncode, "finished": now()},
    )
    return returncode


def prompt_file(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def valid_review(path: Path, candidate_id: str) -> tuple[bool, str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return False, f"review.json is not valid JSON: {exc}"
    if not isinstance(data, dict) or set(data) != {"id", "reason", "verdict"}:
        return False, "review.json must contain only id, reason, verdict"
    if data["id"] != candidate_id or data["verdict"] not in {"approved", "rejected"}:
        return False, "review identity or verdict is invalid"
    if not isinstance(data["reason"], str) or not data["reason"].strip():
        return False, "review reason is empty"
    return data["verdict"] == "approved", str(data["reason"])


def page_for(candidate_id: str) -> Path:
    path = Path(candidate_id)
    if path.name != candidate_id or candidate_id in {"", ".", ".."}:
        raise ValueError(f"unsafe benchmark id: {candidate_id!r}")
    return ROOT / "benchmarks" / f"{candidate_id}.md"


def page_hash(path: Path) -> str | None:
    if path.is_symlink():
        raise ValueError(f"benchmark page is a symlink: {path}")
    if not path.exists():
        return None
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"benchmark page is not a regular file: {path}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pause_marker() -> Path | None:
    markers = sorted(CENSUS.glob("cache/*/QUALITY_AUDIT_PAUSE.json"))
    return markers[-1] if markers else None


def job(
    candidate_id: str,
    run_dir: Path,
    evidence: Path,
    reference: Path,
    grok: str,
    status: dict[str, object],
) -> tuple[str, bool, str]:
    job_dir = run_dir / "jobs" / candidate_id
    job_dir.mkdir(parents=True)
    (job_dir / "logs").mkdir()
    page = page_for(candidate_id)
    validator = ROOT / "scripts" / "benchmarks" / "validate.py"

    def gate() -> bool:
        if pause_marker() is None:
            return False
        report = build_report(evidence, reference, date.today())
        return candidate_id in report.active_ids

    def phase(value: str) -> None:
        with STATUS_LOCK:
            status.setdefault("jobs", {})[candidate_id] = {"phase": value, "ok": None}
            write_status(run_dir, status)

    try:
        if STOP.is_set():
            return candidate_id, False, "stop requested before dispatch"
        if not gate():
            return candidate_id, False, "eligibility expired or candidate is no longer active"
        phase("write-running")
        atomic_json(job_dir / "page-before.json", {"sha256": page_hash(page)})
        if page.exists():
            (job_dir / "before.md").write_bytes(page.read_bytes())
        prompt = job_dir / "writer-prompt.md"
        prompt_file(
            prompt,
            f"""You are writing exactly one benchmark page for {candidate_id} in {page}.
Read benchmarks/AUTHORING.md, the exact eligibility record and reference report in {job_dir}.
Use accepted results and canonical identity as constraints. Open every cited source before making a
claim; leave unknown claims empty or explicitly not established. Write only {page} and files inside
{job_dir}. Repair an existing page only for source-verified claims and preserve verified previous
facts.
Eligibility approves inclusion, not the factual accuracy of an existing article. Do not pad unknowns
with boilerplate to meet a word minimum; report a blocker instead. Set freshness.researched to
today's date and researched_by to the quoted string "Grok Build eligible run, {candidate_id}". Clear
freshness.reviewed and freshness.reviewed_by when editing. Never mark your own page reviewed.
Do not write other pages, schemas, git state, secrets, subagents, deployments, or external trackers.
""",
        )
        report = build_report(evidence, reference, date.today())
        row = next(row for row in report.rows if row.candidate_id == candidate_id)
        atomic_json(job_dir / "eligibility.json", row.model_dump(mode="json"))
        records = []
        for source in sorted(evidence.glob("*.json")):
            try:
                value = json.loads(source.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if isinstance(value, dict) and value.get("candidate_id") == candidate_id:
                records.append(value)
        if len(records) != 1:
            return candidate_id, False, "exact candidate evidence record is missing or ambiguous"
        atomic_json(job_dir / "candidate-evidence.json", records[0])
        atomic_json(
            job_dir / "reference-models.json", json.loads(reference.read_text(encoding="utf-8"))
        )
        command = [
            grok,
            "--cwd",
            str(ROOT),
            "--prompt-file",
            str(prompt),
            "--no-subagents",
            "--max-turns",
            "60",
            "--permission-mode",
            "auto",
            "--output-format",
            "streaming-json",
        ]
        if STOP.is_set() or not gate():
            return candidate_id, False, "dispatch stopped or eligibility changed before writer"
        if run_logged(command, job_dir / "logs", "writer", ROOT) != 0:
            return candidate_id, False, "writer exited nonzero"
        if STOP.is_set():
            return candidate_id, False, "stopped after writer; review not started"
        if page_hash(page) is None or (
            run_logged(
                [sys.executable, str(validator), str(page)],
                job_dir / "logs",
                "writer-validation",
                ROOT,
            )
            != 0
        ):
            return candidate_id, False, "writer validation failed"
        if STOP.is_set() or not gate():
            return candidate_id, False, "eligibility expired before independent review"
        reviewed_hash = page_hash(page)
        phase("review-running")
        review_prompt = job_dir / "review-prompt.md"
        prompt_file(
            review_prompt,
            f"""Independently review the complete page {page} for {candidate_id}.
Read benchmarks/AUTHORING.md, {job_dir / "candidate-evidence.json"}, and
{job_dir / "reference-models.json"}. Open the primary sources for every substantive claim. Do not
trust the writer's report. Eligibility does not approve article facts. Write only JSON to
{job_dir / "review.json"} with exactly {{"id":
"{candidate_id}",
"verdict": "approved" or "rejected", "reason": "specific evidence-based reason"}}. Do not edit
the page or any other file; do not use git, subagents, secrets, or external trackers.
""",
        )
        if STOP.is_set() or not gate():
            return candidate_id, False, "dispatch stopped or eligibility changed before reviewer"
        if page_hash(page) is None or (
            run_logged(
                [
                    grok,
                    "--cwd",
                    str(ROOT),
                    "--prompt-file",
                    str(review_prompt),
                    "--no-subagents",
                    "--max-turns",
                    "50",
                    "--permission-mode",
                    "auto",
                    "--output-format",
                    "streaming-json",
                ],
                job_dir / "logs",
                "reviewer",
                ROOT,
            )
            != 0
        ):
            return candidate_id, False, "reviewer exited nonzero"
        approved, reason = valid_review(job_dir / "review.json", candidate_id)
        if not approved:
            return candidate_id, False, reason
        if (
            run_logged(
                [sys.executable, str(validator), str(page)],
                job_dir / "logs",
                "review-validation",
                ROOT,
            )
            != 0
        ):
            return candidate_id, False, "review validation failed"
        if not gate():
            return candidate_id, False, "eligibility expired after independent review"
        if page_hash(page) != reviewed_hash:
            return candidate_id, False, "page changed during independent review; review is invalid"
        atomic_json(
            job_dir / "approved-page.json",
            {
                "id": candidate_id,
                "sha256": reviewed_hash,
                "reviewed_at": now(),
                "note": "Recheck this hash and current eligibility before coordinator checkpoint.",
            },
        )
        return candidate_id, True, "approved"
    except Exception as exc:  # bounded job failure is recorded, never retried
        return candidate_id, False, f"job error: {exc}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", required=True, type=Path)
    parser.add_argument("--reference-set", required=True, type=Path)
    parser.add_argument("--ids", nargs="+", required=True)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--concurrency", type=int, default=3)
    parser.add_argument("--grok", type=Path, default=Path("~/.local/bin/grok").expanduser())
    args = parser.parse_args(argv)
    STOP.clear()
    if args.concurrency < 1 or len(args.ids) != len(set(args.ids)):
        parser.error("concurrency must be positive and ids must be unique")
    if args.run_dir.exists():
        parser.error("run directory already exists; refusing duplicate run")
    if pause_marker() is None:
        parser.error("QUALITY_AUDIT_PAUSE.json is required while the legacy controller is paused")
    global_lock = None
    try:
        report: EligibilityReport = build_report(args.evidence, args.reference_set, date.today())
        if set(args.ids) - set(report.active_ids):
            parser.error("every requested id must be active in the current eligibility report")
        for candidate_id in args.ids:
            page_for(candidate_id)
        args.run_dir.mkdir(parents=True)
        GLOBAL_LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
        global_lock = GLOBAL_LOCK_PATH.open("a+")
        fcntl.flock(global_lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        lock = (args.run_dir / ".lock").open("w")
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        status: dict[str, object] = {
            "phase": "running",
            "supervisor_pid": os.getpid(),
            "ids": args.ids,
            "jobs": {},
            "started_at": now(),
        }
        write_status(args.run_dir, status)
        previous = signal.signal(signal.SIGINT, lambda *_: STOP.set())
        previous_term = signal.signal(signal.SIGTERM, lambda *_: STOP.set())
        try:
            with ThreadPoolExecutor(max_workers=min(args.concurrency, len(args.ids))) as pool:
                futures = [
                    pool.submit(
                        job,
                        candidate_id,
                        args.run_dir,
                        args.evidence,
                        args.reference_set,
                        str(args.grok),
                        status,
                    )
                    for candidate_id in args.ids
                ]
                for future in as_completed(futures):
                    candidate_id, ok, message = future.result()
                    with STATUS_LOCK:
                        status["jobs"][candidate_id] = {
                            "status": "ready-for-coordinator" if ok else "needsattention",
                            "ok": ok,
                            "error": None if ok else message,
                        }
                        write_status(args.run_dir, status)
        finally:
            signal.signal(signal.SIGINT, previous)
            signal.signal(signal.SIGTERM, previous_term)
        status["phase"] = (
            "ready-for-coordinator"
            if all(v["ok"] for v in status["jobs"].values())
            else ("drained" if STOP.is_set() else "needsattention")
        )
        write_status(args.run_dir, status)
        return 0 if status["phase"] == "ready-for-coordinator" else 2
    except SystemExit:
        raise
    except Exception as exc:
        if global_lock is not None:
            global_lock.close()
        if args.run_dir.exists():
            atomic_json(
                args.run_dir / "status.json",
                {"phase": "needsattention", "error": str(exc), "active_ids": []},
            )
        parser.error(str(exc))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
