"""Social profile assets and handles (MODEL-115). The JSON-LD wiring is tested in
tests/test_structured_data.py."""

from __future__ import annotations

import json
import struct
from pathlib import Path

import pytest

from pipeline import social_profiles

ROOT = Path(__file__).resolve().parents[1]


def _png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    return struct.unpack(">II", data[16:24])


@pytest.mark.parametrize("platform,handle", [
    ("x", "modelspec.ai"),
    ("instagram", "model spec"),
    ("tiktok", "@modelspec"),
    ("linkedin", "https://linkedin.com/company/modelspec"),
])
def test_invalid_handles_fail_instead_of_publishing_bad_urls(
    tmp_path: Path, platform: str, handle: str
) -> None:
    config = tmp_path / "profiles.json"
    values = {name: "" for name in social_profiles.PLATFORMS}
    values[platform] = handle
    config.write_text(json.dumps(values), encoding="utf-8")

    with pytest.raises(ValueError, match=platform):
        social_profiles.profile_urls(config)


def test_profile_kit_has_the_documented_pixel_sizes() -> None:
    expected = {
        "x-avatar.png": (400, 400),
        "x-banner.png": (1500, 500),
        "instagram-avatar.png": (320, 320),
        "tiktok-avatar.png": (200, 200),
        "linkedin-logo.png": (400, 400),
        "linkedin-cover.png": (1512, 256),
    }
    root = ROOT / "brand" / "social"

    assert {path.name for path in root.glob("*.png")} == set(expected)
    assert {path.name for path in root.glob("*.svg")} == {
        name.removesuffix(".png") + ".svg" for name in expected
    }
    for name, size in expected.items():
        assert _png_size(root / name) == size
    for name in ("x-banner.svg", "linkedin-cover.svg"):
        assert "<text" not in (root / name).read_text(encoding="utf-8")
