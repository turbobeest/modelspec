"""Social profile assets and opt-in structured-data wiring (MODEL-115)."""

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


def test_empty_profile_config_emits_no_same_as() -> None:
    html = (ROOT / "site" / "holding" / "index.html").read_text(encoding="utf-8")

    result = social_profiles.add_same_as(html, ROOT / "brand" / "social" / "profiles.json")

    assert '"sameAs"' not in result
    assert result == html


def test_filled_profile_config_adds_canonical_urls(tmp_path: Path) -> None:
    config = tmp_path / "profiles.json"
    config.write_text(json.dumps({
        "x": "modelspecdev",
        "instagram": "modelspec.dev",
        "tiktok": "modelspec_dev",
        "linkedin": "modelspec-dev",
    }), encoding="utf-8")
    html = (ROOT / "site" / "holding" / "index.html").read_text(encoding="utf-8")

    result = social_profiles.add_same_as(html, config)

    assert '"sameAs"' in result
    assert "https://x.com/modelspecdev" in result
    assert "https://www.instagram.com/modelspec.dev/" in result
    assert "https://www.tiktok.com/@modelspec_dev" in result
    assert "https://www.linkedin.com/company/modelspec-dev/" in result


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
        "linkedin-cover.png": (1128, 191),
    }
    root = ROOT / "brand" / "social"

    assert {path.name for path in root.glob("*.png")} == set(expected)
    assert {path.name for path in root.glob("*.svg")} == {
        name.removesuffix(".png") + ".svg" for name in expected
    }
    for name, size in expected.items():
        assert _png_size(root / name) == size
