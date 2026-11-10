"""The serving guide describes the enforced memory gate and public exports."""

import re

import yaml

from pipeline.data_source import REPO_ROOT as ROOT
from pipeline.public_data import KEEP_API, is_retained_snapshot, restrict
from tests.test_worker_memory import assess


def test_data_split_operating_guide_matches_memory_gate_and_retained_exports(tmp_path):
    text = (ROOT / "docs/design/data-split.md").read_text()
    job = yaml.safe_load((ROOT / ".github/workflows/rank-api.yml").read_text())["jobs"]["memory"]
    limits = [int(value) for step in job["steps"]
              for value in re.findall(r"--limit-mib (\d+)", step.get("run", ""))]
    assert limits == [115, 115]
    assert not job.get("continue-on-error", False)
    assert assess(116)["passed"] is False
    assert assess(112, baseline_mib=110)["warnings"]
    documented_limit = re.search(r"(\d+) MiB\s+pull-request gate", text)
    assert documented_limit is not None, "Document the enforced PR memory limit"
    assert int(documented_limit.group(1)) == limits[0]
    gate = text[documented_limit.start():].split("The schedule", 1)[0]
    assert {"current", "successor", "fails", "warning"} <= set(re.findall(r"[A-Za-z]+", gate))
    assert re.search(r"Growth above 1 MiB", gate)
    assert "is warning-only" not in text

    exports = text.split("The output filter keeps", 1)[1].split("Removed routes", 1)[0]
    documented = set(re.findall(r"`([^`]+)`", exports))
    assert KEEP_API <= documented
    pattern = "decision/snapshots/snap_<16 lowercase hex digits>.json.gz"
    assert pattern in documented
    snapshot = pattern.replace("<16 lowercase hex digits>", "0123456789abcdef")
    assert is_retained_snapshot(snapshot)
    retained = KEEP_API | {snapshot}
    for relative in retained | {"unlisted.json"}:
        path = tmp_path / "api" / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("public fixture")
    (tmp_path / "_headers").write_text("")
    restrict(tmp_path)
    actual = {p.relative_to(tmp_path / "api").as_posix()
              for p in (tmp_path / "api").rglob("*")
              if p.is_file() and p.read_bytes() == b"public fixture"}
    assert actual == retained
