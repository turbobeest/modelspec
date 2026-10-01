"""Profile real Worker requests offline. Use a public vendor --data-dir . bundle.

CPython: python scripts/profile_decide.py api/worker/src
Pyodide: see api/worker/profile_decide.cjs for the Node invocation.
Both produce JSON with initialization timings and exclusive request phases,
five warmups and 50 samples per explain level, and the first full request. No timers or
instrumentation are installed in production. --out retains response hashes
for comparison between revisions; --runs changes the warm sample count.
--spec selects an exact JSON Spec; the Pyodide driver takes it as argument five.
"""

from __future__ import annotations

import argparse
import asyncio
import functools
import hashlib
import json
import math
import os
import statistics
import sys
import time
import types
from pathlib import Path

PHASES = (
    "parse_validation",
    "filtering",
    "capability_ranking",
    "tie_bands",
    "explanation",
    "json_serialisation",
)
SPEC = {
    "spec_version": 1,
    "snapshot": "latest",
    "where": ["model.class = text-generator", "model.lifecycle = active"],
    "optimize": {"weights": {"software_engineering": 1}},
    "limit": 500,
}


def install_worker(bundle, snapshot_path=None, startup=None):
    sys.path.insert(0, str(bundle))

    async def no_network(*args, **kwargs):
        raise AssertionError("profile attempted network access")

    class Response:
        def __init__(self, body, status=200, headers=None):
            self.body, self.status, self.headers = body, status, headers or {}

    class Request:
        method, url = "POST", "https://api.modelspec.dev/v1/decide"
        headers = {"origin": "https://modelspec.dev"}

        def __init__(self, payload):
            self.payload = json.dumps(payload)

        async def text(self):
            return self.payload

    sys.modules["js"] = types.SimpleNamespace(fetch=no_network)
    sys.modules["workers"] = types.SimpleNamespace(
        Response=Response, WorkerEntrypoint=type("WorkerEntrypoint", (), {})
    )
    if snapshot_path is not None:
        try:
            import bundled_data
        except ModuleNotFoundError as exc:
            if exc.name != "bundled_data":
                raise
            bundled_data = types.ModuleType("bundled_data")
            bundled_data.read = lambda path: None
            sys.modules["bundled_data"] = bundled_data
        original_read = bundled_data.read
        snapshot_bytes = Path(snapshot_path).read_bytes()
        bundled_data.read = lambda path: (
            snapshot_bytes if path == "/api/decision/snapshot.json.gz" else original_read(path)
        )
    import decide_service

    if startup is not None:
        from decision import registry
        from decision import snapshot as snapshot_module

        originals = []

        def measure_startup(module, name, phase):
            original = getattr(module, name)
            originals.append((module, name, original))

            @functools.wraps(original)
            def timed(*args, **kwargs):
                started = time.perf_counter()
                try:
                    return original(*args, **kwargs)
                finally:
                    startup[phase] += (time.perf_counter() - started) * 1000

            setattr(module, name, timed)

        startup.update(
            dict.fromkeys(
                ("bundled_read", "snapshot_parse_verify", "snapshot_index", "registry"), 0.0
            )
        )
        measure_startup(decide_service, "load_snapshot_bytes", "snapshot_parse_verify")
        measure_startup(snapshot_module.LoadedSnapshot, "__init__", "snapshot_index")
        measure_startup(registry, "default", "registry")
        try:
            import bundled_data
        except ModuleNotFoundError as exc:
            if exc.name != "bundled_data":
                raise
        else:
            measure_startup(bundled_data, "read", "bundled_read")
    import entry

    if startup is not None:
        for module, name, original in originals:
            setattr(module, name, original)
        startup["snapshot_parse_verify"] -= startup["snapshot_index"]

    from decision import engine, explain

    worker = entry.Default()
    worker.env = types.SimpleNamespace(
        MODELSPEC_SNAPSHOT_KEY=os.environ.get(
            "MODELSPEC_SNAPSHOT_KEY", "model247-memory-fixture-key"
        ),
        BUILD_COMMIT="local-profile",
    )
    return entry, decide_service, engine, explain, worker, Request


async def profile(bundle, runs=50, snapshot_path=None, spec=None):
    startup = {}
    started = time.perf_counter()
    entry, service, engine, explain, worker, request_type = install_worker(
        bundle, snapshot_path, startup
    )
    imports_ms = (time.perf_counter() - started) * 1000
    startup["other_imports"] = imports_ms - sum(startup.values())
    spec = SPEC if spec is None else spec
    totals, stack = {}, []

    def instrument(module, name, phase):
        original = getattr(module, name)

        @functools.wraps(original)
        def timed(*args, **kwargs):
            frame = [time.perf_counter(), 0.0]
            stack.append(frame)
            try:
                return original(*args, **kwargs)
            finally:
                elapsed = time.perf_counter() - frame[0]
                stack.pop()
                totals[phase] += (elapsed - frame[1]) * 1000
                if stack:
                    stack[-1][1] += elapsed

        setattr(module, name, timed)

    from decision import snapshot as snapshot_module

    snapshot_phases = (
        "snapshot_read",
        "snapshot_parse_verify",
        "snapshot_index",
        "snapshot_authenticate",
    )
    instrument(entry, "_bundled_read", "snapshot_read")
    instrument(snapshot_module, "_sign", "snapshot_authenticate")
    instrument(service, "load_snapshot_bytes", "snapshot_parse_verify")
    instrument(snapshot_module.LoadedSnapshot, "__init__", "snapshot_index")
    instrument(service.contract, "parse_spec", "parse_validation")
    instrument(engine, "validate", "parse_validation")
    from decision import filter as filtering

    instrument(filtering, "apply", "filtering")
    engine.apply = filtering.apply
    instrument(engine, "run_optimise", "capability_ranking")
    from decision import capability

    instrument(capability, "deterministic_probabilities", "tie_bands")
    for name in ("band", "blend", "entries"):
        instrument(engine.bands_module, name, "tie_bands")
    instrument(engine, "_answer", "tie_bands")
    instrument(explain, "explain", "explanation")
    instrument(service, "serialise", "json_serialisation")
    # Include Pydantic's JSON conversion in the serialization phase.
    instrument(service.contract.Decision, "model_dump", "json_serialisation")

    async def one(level):
        totals.update(dict.fromkeys((*PHASES, *snapshot_phases), 0.0))
        started = time.perf_counter()
        response = await worker.fetch(request_type({**spec, "explain": level}))
        elapsed = (time.perf_counter() - started) * 1000
        assert response.status == 200, response.body
        raw = response.body.encode() if isinstance(response.body, str) else bytes(response.body)
        return (
            {**totals, "total": elapsed, "other": elapsed - sum(totals.values())},
            hashlib.sha256(raw).hexdigest(),
            len(raw),
        )

    cold, _, _ = await one("full")
    held = entry._decision_holder("https://modelspec.dev").snapshot
    result = {
        "runtime": sys.version.split()[0],
        "snapshot": held.snapshot_id,
        "candidates": len(held.candidates()),
        "corpus_models": len(
            {row["model"] for section in held._corpus_sections for row in section["candidates"]}
        ),
        "out_of_lineup": held.out_of_lineup,
        "runs": runs,
        "imports_ms": imports_ms,
        "initialization_ms": startup,
        "spec": spec,
        "cold_full_ms": cold,
        "levels": {},
    }
    for level in ("none", "summary", "full"):
        rows, hashes = [], set()
        for _ in range(5):
            await one(level)
        for _ in range(runs):
            row, digest, size = await one(level)
            rows.append(row)
            hashes.add(digest)
        assert len(hashes) == 1, "response changed across warm runs"
        result["levels"][level] = {
            "sha256": digest,
            "bytes": size,
            "phases": {
                phase: {
                    "p50": statistics.median(row[phase] for row in rows),
                    "p95": sorted(row[phase] for row in rows)[math.ceil(0.95 * runs) - 1],
                }
                for phase in (*PHASES, *snapshot_phases, "other", "total")
            },
        }
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path, nargs="?")
    parser.add_argument(
        "--snapshot",
        type=Path,
        help="signed public full-catalogue fixture to substitute in the bundle",
    )
    parser.add_argument(
        "--build-public-snapshot",
        type=Path,
        help="build the same public card fixture without the premier restriction",
    )
    parser.add_argument("--spec", type=Path, help="exact JSON Spec to profile")
    parser.add_argument("--runs", type=int, default=50)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.build_public_snapshot:
        from datetime import date

        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from decision.snapshot import build_from_repo

        built = build_from_repo(
            Path(__file__).resolve().parents[1], premier=None, as_of=date.today()
        )
        built.write(args.build_public_snapshot, key="model247-memory-fixture-key")
        print(json.dumps({"snapshot": built.snapshot_id}))
        sys.exit(0)
    if args.bundle is None or args.runs < 1:
        parser.error("bundle and a positive run count are required")
    result = asyncio.run(
        profile(
            args.bundle.resolve(),
            args.runs,
            args.snapshot,
            json.loads(args.spec.read_text()) if args.spec else None,
        )
    )
    output = json.dumps(result, indent=2)
    if args.out:
        args.out.write_text(output + "\n")
    print(output)
