"""MODEL-299: /brand/, the press and brand kit, served from the package unchanged."""

from __future__ import annotations

import html
import re
import zipfile
from datetime import date
from pathlib import Path

import pytest

from pipeline import brand, brand_page, entity, holding, live, structured_data
from pipeline.build import llms_txt
from pipeline.export import Build

ROOT = Path(__file__).resolve().parents[1]
BRAND = ROOT / "brand"
_REF = re.compile(r'(?:href|src)="([^"]+)"')


@pytest.fixture(scope="module")
def tree(tmp_path_factory: pytest.TempPathFactory) -> Path:
    out = tmp_path_factory.mktemp("brand-site")
    brand_page.write(out)
    return out


@pytest.fixture(scope="module")
def page(tree: Path) -> str:
    return (tree / "brand" / "index.html").read_text(encoding="utf-8")


def _visible(text: str) -> str:
    text = re.sub(r"<(script|style)\b.*?</\1>", " ", text, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", text)))


def _expected_sources() -> dict[str, Path]:
    """What the kit must hold, listed from the directories, not from the module."""
    sources = {p.relative_to(BRAND).as_posix(): p
               for p in (BRAND / "2a").rglob("*") if p.is_file()}
    sources["og-card-2a.png"] = BRAND / "og-card-2a.png"
    for p in (BRAND / "social").iterdir():
        if p.suffix in {".png", ".svg"}:
            sources[f"social/{p.name}"] = p
    return sources


def test_the_page_is_generated_with_its_stylesheet_and_canonical(tree: Path, page: str) -> None:
    assert (tree / "brand" / "brand.css").read_bytes() == brand_page.STYLESHEET.read_bytes()
    assert '<link rel="canonical" href="https://modelspec.dev/brand/">' in page
    assert "<title>Brand and press kit · ModelSpec</title>" in page
    assert 'name="robots"' not in page
    assert brand.head_links() in page
    assert page.startswith("<!doctype html>") and page.rstrip().endswith("</html>")


def test_the_page_carries_the_registry_words_verbatim(page: str) -> None:
    text = _visible(page)
    assert entity.ONE_SENTENCE in text
    assert entity.DISAMBIGUATION in text
    assert brand.POSITIONING in text
    assert f'<blockquote class="entity">{html.escape(entity.ONE_SENTENCE, quote=False)}</blockquote>' in page
    for old in entity.SUPERSEDED:
        assert old.lower() not in text.lower()


def test_the_name_and_the_operator_with_its_ampersand(page: str) -> None:
    text = _visible(page)
    assert brand_page.operator() == "Sparks & Sawdust LLC"
    assert "operated by Sparks & Sawdust LLC" in text
    assert "Sparks &amp; Sawdust LLC" in page
    assert "Sparks and Sawdust" not in text
    assert "<b>ModelSpec</b>: one word, with a capital M and a capital S." in page


def test_every_package_file_is_published_byte_for_byte(tree: Path) -> None:
    expected = _expected_sources()
    published = {p.relative_to(tree / "brand" / "assets").as_posix(): p
                 for p in (tree / "brand" / "assets").rglob("*") if p.is_file()}
    assert sorted(published) == sorted(expected)
    for rel, source in expected.items():
        assert published[rel].read_bytes() == source.read_bytes(), rel
    files = {p.relative_to(tree).as_posix() for p in tree.rglob("*") if p.is_file()}
    assert files == brand_page.published()


def test_every_link_on_the_page_into_brand_resolves_to_the_source_bytes(tree: Path, page: str) -> None:
    refs = set(_REF.findall(page))
    linked = sorted(ref for ref in refs if ref.startswith("/brand/"))
    for ref in linked:
        target = tree / ref.lstrip("/")
        assert (target / "index.html" if ref.endswith("/") else target).is_file(), ref
    sources = _expected_sources()
    assets = [ref for ref in linked if ref.startswith("/brand/assets/")]
    # Every image is previewed and downloadable; the README is published in the zip.
    previewed = {ref.removeprefix("/brand/assets/") for ref in assets}
    assert previewed == {rel for rel in sources if not rel.endswith(".md")}
    for ref in assets:
        rel = ref.removeprefix("/brand/assets/")
        assert (tree / ref.lstrip("/")).read_bytes() == sources[rel].read_bytes(), rel
    assert f"/brand/{brand_page.ZIP_NAME}" in refs


def test_each_download_states_format_size_and_file_size(page: str) -> None:
    cards = re.findall(r'<li class="asset">(.*?)</li>', page, re.S)
    assert len(cards) == len(_expected_sources()) - 1  # the README has no preview
    for card in cards:
        name = re.search(r"<code>([^<]+)</code>", card).group(1)
        text = _visible(card)
        if name.endswith(".svg"):
            assert "Format SVG" in text and "Size vector" in text, name
        else:
            assert "Format PNG" in text, name
            assert re.search(r"Size \d+ × \d+ px", text), name
        assert re.search(r"File \d+(\.\d)? (bytes|KB|MB)", text), name
    assert "Size 1200 × 630 px" in _visible(page)
    assert "Size 1024 × 1024 px" in _visible(page)


def test_profile_text_and_handles_are_not_published(tree: Path, page: str) -> None:
    assert not list(tree.rglob("profile-copy.md"))
    assert not list(tree.rglob("profiles.json"))
    assert [p.relative_to(tree).as_posix() for p in tree.rglob("README.md")] == [
        "brand/assets/2a/README.md"]
    copy = (BRAND / "social" / "profile-copy.md").read_text(encoding="utf-8")
    bios = re.findall(r"^> (.+)$", copy, re.M)
    assert bios
    with zipfile.ZipFile(tree / "brand" / brand_page.ZIP_NAME) as archive:
        names = archive.namelist()
    assert not any(name.endswith(("profile-copy.md", "profiles.json", "social/README.md"))
                   for name in names)
    for bio in bios:
        assert bio not in _visible(page)


def test_the_zip_holds_exactly_the_kit(tree: Path) -> None:
    sources = _expected_sources()
    with zipfile.ZipFile(tree / "brand" / brand_page.ZIP_NAME) as archive:
        infos = archive.infolist()
        assert [i.filename for i in infos] == sorted(
            f"{brand_page.ZIP_ROOT}/{rel}" for rel in sources)
        for info in infos:
            rel = info.filename.removeprefix(f"{brand_page.ZIP_ROOT}/")
            assert archive.read(info) == sources[rel].read_bytes(), rel
            assert info.date_time == brand_page.ZIP_TIME
            assert info.compress_type == zipfile.ZIP_STORED
        assert archive.testzip() is None


def test_the_zip_is_reproducible(tmp_path: Path) -> None:
    first, second = tmp_path / "one", tmp_path / "two"
    brand_page.write(first)
    brand_page.write(second)
    zipped = Path("brand") / brand_page.ZIP_NAME
    assert (first / zipped).read_bytes() == (second / zipped).read_bytes()
    assert (first / "brand/index.html").read_bytes() == (second / "brand/index.html").read_bytes()


def test_no_external_font_or_cdn(tree: Path, page: str) -> None:
    css = (tree / "brand" / "brand.css").read_text(encoding="utf-8")
    for text in (page, css):
        assert "fonts.googleapis.com" not in text
        assert "fonts.gstatic.com" not in text
        assert "@import" not in text
    for tag in re.findall(r"<(?:link|script|img)\b[^>]*>", page):
        if 'rel="canonical"' in tag:
            continue
        for ref in _REF.findall(tag):
            assert ref.startswith("/") and not ref.startswith("//"), tag
    assert "url(" not in css


def test_colours_come_from_the_package_readme(page: str) -> None:
    readme = (brand.PACKAGE / "README.md").read_text(encoding="utf-8")
    colours = brand_page.palette()
    assert [c.hex for c in colours] == ["#0B1426", "#F2C94C", "#3FB68B", "#FFFFFF", "#5AA9EC"]
    for colour in colours:
        assert colour.hex in readme
        assert f'style="background:{colour.hex}"' in page
    swatches = set(re.findall(r'style="background:(#[0-9A-Fa-f]{6})"', page))
    assert swatches == {c.hex for c in colours}
    assert {c.token for c in colours} == {"--navy", "--yellow", "--green", "--blue", None}


def test_the_usage_section_renders_the_readme_and_nothing_more(page: str) -> None:
    usage = re.search(r'<section id="usage">(.*?)</section>', page, re.S).group(1)
    text = _visible(usage)
    for line in (brand.PACKAGE / "README.md").read_text(encoding="utf-8").splitlines():
        line = line.removeprefix("# ").removeprefix("- ").replace("`", "").strip()
        if line:
            assert line in text, line
    assert brand_page.avatar_rule() in text
    assert usage.count("<li>") == sum(
        1 for line in brand_page.readme_lines() if line.startswith("- "))


def test_the_typeface_names_only_what_the_package_and_site_define(page: str) -> None:
    section = _visible(re.search(r'<section id="typeface">(.*?)</section>', page, re.S).group(1))
    assert brand_page.wordmark() in section
    assert "Segoe UI" in section
    for family in ("Instrument Sans", "JetBrains Mono"):
        assert family in section
        assert f'font-family: "{family}"' in (
            ROOT / "pipeline" / "landing_assets" / "landing.css").read_text(encoding="utf-8")
    for licence in ("InstrumentSans-OFL.txt", "JetBrainsMono-OFL.txt"):
        assert (ROOT / "site" / "fonts" / licence).is_file()


def test_light_and_dark_themes_follow_the_decide_rule(tree: Path, page: str) -> None:
    css = (tree / "brand" / "brand.css").read_text(encoding="utf-8")
    assert ':root[data-theme="light"]' in css and ':root[data-theme="dark"]' in css
    assert "prefers-color-scheme" not in css
    assert '<html lang="en" data-theme="dark">' in page
    assert "localStorage.getItem('modelspec-theme')" in page
    # Read, never written: the privacy statement names /decide/ as what keeps it.
    assert "setItem" not in page
    assert 'id="theme-toggle"' in page


def test_brand_is_registered_wherever_a_public_page_must_be() -> None:
    assert "/brand/" in live.PAGES
    assert "brand" in live.KEEP_DIRS
    assert structured_data.CRUMBS["/brand/"]
    assert "brand" in holding.KEEP_DIRS["modelspec"]
    build = Build(commit="0" * 40, built_at="2026-10-01T00:00:00+00:00", as_of=date(2026, 10, 1))
    assert "https://modelspec.dev/brand/" in llms_txt(
        site="ModelSpec", base="https://modelspec.dev", build=build)


def test_an_unplaced_file_in_the_package_stops_the_build(monkeypatch, tmp_path: Path) -> None:
    package = tmp_path / "2a"
    (package / "png").mkdir(parents=True)
    for p in brand.PACKAGE.rglob("*"):
        if p.is_file():
            (package / p.relative_to(brand.PACKAGE)).write_bytes(p.read_bytes())
    (package / "modelspec-new.svg").write_text("<svg/>", encoding="utf-8")
    monkeypatch.setattr(brand, "PACKAGE", package)
    with pytest.raises(ValueError, match="does not place"):
        brand_page.kit()
