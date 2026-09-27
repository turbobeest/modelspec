"""Refresh test-file duration weights from one or more pytest JUnit XML files."""

from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

try:
    from scripts.pytest_shards import DEFAULT_DURATIONS_PATH, test_files
except ModuleNotFoundError:
    from pytest_shards import DEFAULT_DURATIONS_PATH, test_files


def _test_file(classname: str, modules: dict[str, str]) -> str | None:
    matches = [
        path
        for module, path in modules.items()
        if classname == module or classname.startswith(f"{module}.")
    ]
    return max(matches, key=len) if matches else None


def durations_from_junit(xml_files: list[Path], root: Path) -> dict[str, float]:
    """Sum testcase time attributes by repository-relative test file."""
    modules = {
        path.relative_to(root).with_suffix("").as_posix().replace("/", "."): path.relative_to(
            root
        ).as_posix()
        for path in test_files(root)
    }
    durations: defaultdict[str, float] = defaultdict(float)
    for xml_file in xml_files:
        for testcase in ET.parse(xml_file).iter("testcase"):
            path = _test_file(testcase.attrib.get("classname", ""), modules)
            if path is not None:
                durations[path] += float(testcase.attrib.get("time", "0"))
    return {path: round(seconds, 6) for path, seconds in sorted(durations.items())}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("junit_directory", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    xml_files = sorted(args.junit_directory.rglob("*.xml"))
    if not xml_files:
        parser.error(f"no XML files found under {args.junit_directory}")
    durations = durations_from_junit(xml_files, root)
    output = root / DEFAULT_DURATIONS_PATH
    output.write_text(json.dumps(durations, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(durations)} test-file durations from {len(xml_files)} XML files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
