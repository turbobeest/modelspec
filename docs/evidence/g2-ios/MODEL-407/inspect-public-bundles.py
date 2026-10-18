from pathlib import Path
import gzip
import hashlib
import json
import runpy
import shutil
import subprocess

ROOT = Path.cwd()
SCRATCH = ROOT / "tmp/model-407/memory_probe"
tracked = subprocess.check_output(["git", "ls-files", "api/worker/src"], text=True).splitlines()
results = []
for label, source, bundle in (
    ("candidate", ROOT, SCRATCH / "public-bundle-calibrated"),
    ("b4a7074f", SCRATCH / ".engine-b4a7074f", SCRATCH / "public-bundle-b4a7074f"),
):
    for name in tracked:
        path = source / name
        if path.suffix == ".py" and path.exists():
            shutil.copyfile(path, bundle / path.name)
    module = runpy.run_path(str(bundle / "bundled_data.py"))
    row = {"label": label, "bundle_sha256": hashlib.sha256((bundle / "bundled_data.py").read_bytes()).hexdigest(), "snapshots": []}
    for path in ("/api/decision/snapshot.json.gz", "/api/decision/snapshot-successor.json.gz"):
        encoded = module["read"](path)
        assert encoded is not None, path
        raw = gzip.decompress(encoded)
        content = json.loads(raw)["content"]
        ids = content.get("hardware_fit_record_ids", [r["id"] for r in content.get("hardware_fit_records", [])])
        synthetic = [rid for rid in ids if rid.startswith("hardware-fit:memory-fixture-")]
        assert len(synthetic) == 15, (label, path, len(synthetic))
        table = content.get("record_table", {})
        hardware = content.get("hardware_fit_record_table", {})
        row["snapshots"].append({
            "path": path, "compressed_bytes": len(encoded), "json_bytes": len(raw),
            "synthetic_hardware_rows": len(synthetic),
            "synthetic_sources": sum(sid.startswith("memory-fixture-") for sid in content["sources"]),
            "total_sources": len(content["sources"]),
            "valid_until": content.get("valid_until"), "valid_from": content.get("valid_from"),
            "provenance_fields": len(table.get("fields", [])), "provenance_rows": len(table.get("rows", {})),
            "provenance_slots": sum(len(r) for r in table.get("rows", {}).values()),
            "hardware_provenance_fields": len(hardware.get("fields", [])), "hardware_provenance_rows": len(hardware.get("rows", {})),
        })
    results.append(row)
(SCRATCH / "bundle-metadata.json").write_text(json.dumps(results, indent=2) + "\n")
print(json.dumps(results, indent=2))
