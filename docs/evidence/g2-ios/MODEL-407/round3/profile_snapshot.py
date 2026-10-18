#!/usr/bin/env python3
"""Public MODEL-407 loader timing; exact MODEL-138 best-of-five gate plus separate profiles.

Run from the worktree root. Frozen modules are compiled from git without changing
tracked files. Timed samples use the real thirty-model fixture and file loader,
retain the previous index during the next load, and never run under cProfile.
"""
from __future__ import annotations

import argparse
import cProfile
import gc
import hashlib
import io
import json
import platform
import pstats
from pathlib import Path
import subprocess
import sys
import time
import types

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
BASELINE = "819ba9e1aeb4e5e8a91e305a044224ff061605ed"
HISTORICAL = "4443bb7a3ec8d02d509d60b05eae876354cce92e"
CANDIDATE = "f6dbbcd86845e614a00d3bd7ce8dfa4d55c2f618"


def git_source(ref: str, path: str) -> str:
    if ref == "WORKTREE":
        return (ROOT / path).read_text()
    return subprocess.check_output(["git", "show", f"{ref}:{path}"], cwd=ROOT, text=True)


def module_from_source(name: str, source: str, path: Path, injected=None):
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / "decision/snapshot.py")
    sys.modules[name] = module
    if injected:
        module.__dict__.update(injected)
    path.write_text(source)
    exec(compile(source, str(path), "exec"), module.__dict__)
    return module


def version(label: str, ref: str, out: Path):
    source = git_source(ref, "decision/snapshot.py")
    injected = {}
    marker = "from decision.json_stream import JSONStreamReader\n"
    reader = None
    if marker in source:
        reader = module_from_source(
            f"model407_profile_{label}_reader", git_source(ref, "decision/json_stream.py"),
            out / f"{label}-json_stream.py")
        injected["JSONStreamReader"] = reader.JSONStreamReader
        source = source.replace(marker, "")
    module = module_from_source(
        f"model407_profile_{label}_snapshot", source, out / f"{label}-snapshot.py", injected)
    return module, reader


def fast_arrays(reader_module):
    """Trial only: decode complete buffered arrays in C; stream incomplete ones."""
    reader = reader_module.JSONStreamReader
    original_init, original_array = reader.__init__, reader._array

    def init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        keys = self._keys
        self._decoder = json.JSONDecoder(object_pairs_hook=lambda pairs: {
            keys.setdefault(key, key): value for key, value in pairs
        })

    def array(self):
        try:
            value, end = self._decoder.raw_decode(self._buffer, self._cursor)
        except json.JSONDecodeError:
            pass
        else:
            self._cursor = end
            return value
        return original_array(self)

    reader.__init__, reader._array = init, array


def root_whole_decoder(module, path: Path):
    source = path.read_text()
    namespace = dict(module.__dict__)
    exec(compile(source, str(path), "exec"), namespace)
    module._stream_canonical_envelope = namespace["_stream_canonical_envelope"]


def deep_bytes(value, seen=None):
    if seen is None:
        seen = set()
    if id(value) in seen:
        return 0
    seen.add(id(value))
    size = sys.getsizeof(value)
    if isinstance(value, dict):
        size += sum(deep_bytes(k, seen) + deep_bytes(v, seen) for k, v in value.items())
    elif isinstance(value, (tuple, list, set, frozenset)):
        size += sum(deep_bytes(item, seen) for item in value)
    return size


def measure(module, path: Path):
    def load():
        return module.load_snapshot(path, key=None, public_keys={})

    load()  # Exact test warm-up.
    samples = []
    gc.disable()
    try:
        for _ in range(5):
            start = time.perf_counter()
            index = load()
            samples.append(time.perf_counter() - start)
    finally:
        gc.enable()
    assert len(index.candidates()) == 120
    return {
        "samples_ms": [sample * 1000 for sample in samples],
        "best_ms": min(samples) * 1000,
        "passes_unchanged_100ms_gate": min(samples) < 0.1,
        "index_bytes": deep_bytes(vars(index)),
        "snapshot_id": index.snapshot_id,
    }


def profile(module, path: Path, output: Path):
    profiler = cProfile.Profile()
    gc.disable()
    try:
        profiler.runcall(module.load_snapshot, path, key=None, public_keys={})
    finally:
        gc.enable()
    profiler.dump_stats(str(output.with_suffix(".prof")))
    sink = io.StringIO()
    stats = pstats.Stats(profiler, stream=sink)
    stats.sort_stats("cumulative").print_stats(35)
    stats.sort_stats("tottime").print_stats(35)
    output.with_suffix(".txt").write_text(sink.getvalue())
    rows = []
    for (filename, line, function), (primitive, calls, own, cumulative, callers) in stats.stats.items():
        if function in {"_stream_canonical_envelope", "_object", "_array", "_scalar",
                        "_starts", "_whitespace", "read_value", "raw_decode", "content_hash",
                        "decompress", "_hash_consumed", "load_snapshot_bytes"} or (
                            function == "__init__" and "snapshot.py" in filename):
            rows.append({"file": Path(filename).name, "line": line, "function": function,
                         "calls": calls, "self_ms": own * 1000,
                         "cumulative_ms": cumulative * 1000})
    return {"total_calls": stats.total_calls, "profile_total_ms": stats.total_tt * 1000,
            "functions": sorted(rows, key=lambda row: row["cumulative_ms"], reverse=True)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "tmp/model-407/round3/profile-reproduction")
    parser.add_argument("--variants", nargs="+", default=["baseline", "historical", "whole_c", "fast_arrays", "candidate"])
    parser.add_argument("--whole-helper", type=Path, default=Path(__file__).with_name("canonical_c_decoder.py"))
    parser.add_argument("--profile", action="store_true")
    parser.add_argument("--candidate-ref", default=CANDIDATE, help="git ref or WORKTREE for candidate variant")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    versions = {}
    for label in args.variants:
        ref = HISTORICAL if label == "historical" else args.candidate_ref if label == "candidate" else BASELINE
        module, reader = version(label, ref, args.out)
        if label == "fast_arrays":
            fast_arrays(reader)
        elif label == "whole_c":
            root_whole_decoder(module, args.whole_helper)
        elif label not in {"baseline", "historical", "candidate"}:
            raise ValueError(f"unknown variant: {label}")
        versions[label] = module
    from tests.test_decision_snapshot import AS_OF, REGISTRY
    from tests.snapshot_records import thirty_models
    baseline, _ = version("fixture", BASELINE, args.out)
    built = baseline.build_snapshot(thirty_models(), registry=REGISTRY, as_of=AS_OF)
    fixture = args.out / "thirty.json.gz"
    built.write(fixture, key=None, ed25519_signer=None)
    assert fixture.stat().st_size < 3_000_000
    import gzip
    raw = gzip.decompress(fixture.read_bytes())
    result = {"baseline_ref": BASELINE, "historical_ref": HISTORICAL, "candidate_ref": args.candidate_ref,
              "python": sys.version, "platform": platform.platform(),
              "fixture": {"compressed_bytes": fixture.stat().st_size,
                          "json_utf8_bytes": len(raw), "json_sha256": hashlib.sha256(raw).hexdigest()},
              "timing_contract": "one warm load, five file loads, GC disabled, previous index retained; best <100ms",
              "variants": {}}
    for label, module in versions.items():
        timing = measure(module, fixture)
        if args.profile:
            timing["profile"] = profile(module, fixture, args.out / (label + "-profile"))
        result["variants"][label] = timing
        print(json.dumps({"variant": label, **{key: value for key, value in timing.items() if key != "profile"}}), flush=True)
    (args.out / "results.json").write_text(json.dumps(result, indent=2) + "\n")
    return 0 if all(row["passes_unchanged_100ms_gate"] for row in result["variants"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
