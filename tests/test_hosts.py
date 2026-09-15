"""Host profiles (MODEL-26 phase A): shape, unified invariants, and sourcing.

Every non-null number must cite a page that was actually read; a null beats a guess.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

HOSTS = Path(__file__).resolve().parent.parent / "hosts"
SECTIONS = {
    "cpu": {"model", "cores", "threads"},
    "system_memory": {"type", "channels", "max_speed_mt_s", "capacity_max_gb",
                      "capacity_options_gb", "bandwidth_gb_s", "bandwidth_derivation"},
    "pcie": {"cpu_gen", "cpu_lanes_usable", "accelerator_link_gen", "accelerator_link_width"},
    "storage": {"class", "capacity_options_gb"},
}
TOP = {"id", "display_name", "kind", "unified", "hardware_ref", *SECTIONS,
       "field_sources", "figures_are", "notes"}
PROFILES = sorted(p for p in HOSTS.glob("*.yaml") if not p.name.startswith("_"))


def _numeric(v):
    if isinstance(v, bool):
        return False
    if isinstance(v, (int, float)):
        return True
    return isinstance(v, list) and bool(v) and all(_numeric(x) for x in v)


def test_schema_and_profiles_exist():
    assert (HOSTS / "_schema.yaml").exists()
    assert 1 <= len(PROFILES) <= 3


@pytest.mark.parametrize("path", PROFILES, ids=lambda p: p.stem)
def test_profile_validates(path):
    raw = yaml.safe_load(path.read_text())
    assert set(raw) == TOP, set(raw) ^ TOP
    assert raw["id"] == path.stem
    assert raw["kind"] in {"platform", "system"}
    assert isinstance(raw["unified"], bool)
    assert raw["figures_are"] in {"vendor-specification", "independent-measurement", "mixed"}
    for section, keys in SECTIONS.items():
        assert set(raw[section]) == keys, (section, set(raw[section]) ^ keys)
        for k, v in raw[section].items():
            assert v is None or isinstance(v, (str, int, float, list)), (section, k)
    if raw["unified"]:
        assert raw["system_memory"]["type"] == "unified"
        assert raw["pcie"]["accelerator_link_gen"] is None
    if raw["hardware_ref"]:
        assert (HOSTS.parent / "hardware" / f"{raw['hardware_ref']}.yaml").exists()


@pytest.mark.parametrize("path", PROFILES, ids=lambda p: p.stem)
def test_every_number_is_sourced(path):
    raw = yaml.safe_load(path.read_text())
    sources = raw["field_sources"]
    numeric = {f"{s}.{k}" for s in SECTIONS for k, v in raw[s].items() if _numeric(v)}
    missing = numeric - set(sources)
    assert not missing, f"unsourced numeric fields: {sorted(missing)}"
    for key, src in sources.items():
        section, _, field = key.partition(".")
        assert raw.get(section, {}).get(field) is not None, f"source for null/unknown {key}"
        assert src["url"].startswith("https://")
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", src["read_at"])
        assert src["quote"].strip()
