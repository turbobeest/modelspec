"""Platform drafts for a release breakdown (MODEL-226).

Drafts are views of the MODEL-224 sample breakdown. Nothing is posted.
"""

from __future__ import annotations

import ast
import importlib
import re
import subprocess
from dataclasses import replace
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

import pytest

from decision.excluded import excluded_sources
from pipeline.social_cards import render_card_html
from release_blog import platforms
from release_blog.breakdown import to_bytes
from release_blog.model import Breakdown, Cited
from release_blog.platforms import AUTOMATIC_POSTING, DraftImage, render_drafts
from release_blog.render import _number, charts
from release_blog.tone import refused_words

_URL = re.compile(r"https?://\S+")
_ISO_DATE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
_NUMBER = re.compile(r"(?<![\w.^])[$]?\d[\d,]*(?:\.\d+)?%?")
_TEXT = re.compile(r"<text\b[^>]*>(.*?)</text>", re.DOTALL)
_TITLE = re.compile(r"<title\b[^>]*>(.*?)</title>", re.DOTALL)
_CHART = re.compile(r"<!-- chart -->.*?<!-- /chart -->", re.DOTALL)
_LABEL = re.compile(r'aria-label="([^"]*)"')


@pytest.fixture(scope="module")
def breakdown(tmp_path_factory) -> Breakdown:
    """The MODEL-224 sample: signed snapshots and the real decision engine."""
    from release_blog.gates import load_signed
    from tests import test_release_blog as sample

    root = tmp_path_factory.mktemp("platforms")
    after = load_signed(
        sample._write(root / "after.json.gz", with_new=True), public_keys=sample.PUBLIC
    )
    before = load_signed(
        sample._write(root / "before.json.gz", with_new=False), public_keys=sample.PUBLIC
    )
    return sample._build(after, before)


def _tokens(cited: Cited) -> set[str]:
    found = set()
    for value in (cited.value, abs(cited.value)):
        shown = _number(value, cited.unit)
        found.add(shown)
        if shown.endswith("%"):
            found.add(shown[:-1])
        if shown.startswith("$"):
            found.add(shown[1:])
    return found


def _allowed(breakdown: Breakdown) -> set[str]:
    """Spellings of numbers the breakdown already holds."""
    raw = breakdown.model_dump()
    found: set[str] = set()

    def walk(value) -> None:
        if isinstance(value, dict) and "read_date" in value and "value" in value:
            found.update(_tokens(Cited.model_validate(value)))
            return
        if isinstance(value, dict):
            for item in value.values():
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(raw)
    found.add(str(breakdown.revision))
    for offering in breakdown.cost.offerings:
        for size in (offering.task.input, offering.task.output):
            found.add(str(size))
            found.add(f"{size:,}")
    for row in breakdown.recheck.schedule:
        found.add(str(row["day"]))
    return found


def _dates(breakdown: Breakdown) -> set[str]:
    raw = breakdown.model_dump(mode="json")
    return set(_ISO_DATE.findall(str(raw)))


def _prepare(breakdown: Breakdown, text: str) -> str:
    text = _URL.sub(" ", text)
    text = _ISO_DATE.sub(" ", text)
    for phrase in (breakdown.model.name, *breakdown.names.values()):
        if any(character.isdigit() for character in phrase):
            text = text.replace(phrase, " ")
    return text


def stray_numbers(breakdown: Breakdown, text: str) -> list[str]:
    allowed = _allowed(breakdown)
    return [
        match.group(0)
        for match in _NUMBER.finditer(_prepare(breakdown, text))
        if match.group(0) not in allowed
    ]


def _visible(svg: str, *, keep_chart: bool) -> str:
    body = svg if keep_chart else _CHART.sub(" ", svg)
    parts = _TEXT.findall(body) + _TITLE.findall(body) + _LABEL.findall(body)
    return " ".join(parts)


def copy_text(draft) -> str:
    """Words a person would post or read on a card, not stylesheet geometry."""
    parts = [
        *draft.posts,
        draft.title,
        draft.submission,
        draft.rules,
        draft.note,
        draft.link,
        *(image.alt for image in draft.images),
    ]
    parts.extend(_visible(image.svg, keep_chart=image.role == "claims") for image in draft.images)
    return "\n".join(parts)


class _VisibleHTML(HTMLParser):
    """Text a person can read. Stylesheet geometry stays out."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"style", "script", "metadata"}:
            self._skip += 1
        if self._skip:
            return
        for key, value in attrs:
            if key in {"alt", "aria-label", "title"} and value:
                self.parts.append(value)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"style", "script", "metadata"} and self._skip:
            self._skip -= 1

    def handle_data(self, data: str) -> None:
        if not self._skip and data.strip():
            self.parts.append(data.strip())


def _html_bits(document: str) -> list[str]:
    parser = _VisibleHTML()
    parser.feed(document)
    return parser.parts


def _chart_bits(svg: str) -> list[str]:
    return [*_TEXT.findall(svg), *_TITLE.findall(svg), *_LABEL.findall(svg)]


def _authorized(breakdown: Breakdown) -> list[str]:
    """Sentences and chart labels the draft helpers actually render."""
    parts = [
        platforms._hook(breakdown),
        breakdown.headline.text,
        *[platforms._standing_line(breakdown, row) for row in breakdown.standing],
        platforms._cost_line(breakdown) or "",
        *platforms._comparisons(breakdown),
        platforms._unread(breakdown) or "",
        platforms._held(breakdown),
        *platforms._unreported(breakdown),
        platforms._speed(breakdown) or "",
        platforms._domains(breakdown) or "",
        *platforms._plans(breakdown),
        platforms._facets(breakdown) or "",
        platforms._inapplicable(breakdown) or "",
        breakdown.disclosures.neutrality,
        *platforms._hook_sources(breakdown),
    ]
    for svg in charts(breakdown).values():
        parts.extend(_chart_bits(svg))
    return [unescape(part).strip() for part in parts if part and part.strip()]


_SENTENCE_BREAK = re.compile(r"(?<=[.!?])\s+")


def _units(text: str) -> list[str]:
    found: list[str] = []
    for block in unescape(text).split("\n"):
        block = block.strip()
        if not block:
            continue
        sentences = [part.strip() for part in _SENTENCE_BREAK.split(block) if part.strip()]
        found.extend(sentences or [block])
    return found


def _draft_segments(draft) -> list[str]:
    segments: list[str] = []
    for text in (*draft.posts, draft.title, draft.submission, draft.rules, draft.note, draft.link):
        segments.extend(_units(text))
    for image in draft.images:
        segments.extend(_units(image.alt))
        segments.extend(unescape(bit).strip() for bit in _chart_bits(image.svg) if bit.strip())
        if image.card is not None:
            segments.extend(_units(image.card.headline))
            segments.extend(_units(image.card.alt))
            for bit in _html_bits(image.card.content):
                segments.extend(_units(bit))
        if image.html:
            for bit in _html_bits(image.html):
                segments.extend(_units(bit))
    return [segment for segment in segments if segment]


def untraced_segments(breakdown: Breakdown, draft) -> list[str]:
    """Numeric copy that is not a substring of the fact it was rendered from.

    A bare spelling such as ``70%`` does not authorize a different sentence.
    The posted segment itself has to sit inside an authorized fact.
    """
    authorized = _authorized(breakdown)
    found: list[str] = []
    for segment in _draft_segments(draft):
        if not _NUMBER.search(_prepare(breakdown, segment)):
            continue
        if any(segment in entry for entry in authorized):
            continue
        if segment not in found:
            found.append(segment)
    return found


def _hook_from_model_225():
    source = subprocess.check_output(
        ["git", "show", "model-225-release-pipeline:release_blog/pipeline.py"],
        cwd=Path(__file__).resolve().parents[1],
        text=True,
    )
    hook = next(
        node
        for node in ast.parse(source).body
        if isinstance(node, ast.FunctionDef) and node.name == "_platforms"
    )
    namespace: dict[str, object] = {"Path": Path, "importlib": importlib}
    executable = compile(ast.Module(body=[hook], type_ignores=[]), "<807 hook>", "exec")
    exec(executable, namespace)
    return namespace["_platforms"]


def _with_repeated_readings(breakdown: Breakdown, benchmark: str, repeats: int) -> Breakdown:
    rows = breakdown.claims_vs_evidence.claims
    original = next(row for row in rows if row.benchmark == benchmark)
    longer = original.model_copy(update={"readings": original.readings * repeats})
    claims = breakdown.claims_vs_evidence.model_copy(
        update={"claims": [longer if row.benchmark == benchmark else row for row in rows]}
    )
    return breakdown.model_copy(update={"claims_vs_evidence": claims})


def _svg(width: int, height: int, payload: int) -> str:
    return f'<svg width="{width}" height="{height}">{"x" * payload}</svg>'


def test_a_number_absent_from_the_breakdown_is_rejected(breakdown) -> None:
    assert stray_numbers(breakdown, "The held-back score is 99%.") == ["99%"]


def test_sample_drafts_exist_for_every_platform(breakdown) -> None:
    drafts = render_drafts(breakdown)
    assert set(drafts) == {
        "x",
        "linkedin",
        "facebook",
        "instagram",
        "reddit",
        "hackernews",
    }
    assert AUTOMATIC_POSTING is False
    assert all(draft.posted is False and draft.platform == name for name, draft in drafts.items())
    again = render_drafts(breakdown)
    assert [draft.posts for draft in again.values()] == [draft.posts for draft in drafts.values()]


def test_sample_drafts_use_only_breakdown_numbers(breakdown) -> None:
    for name, draft in render_drafts(breakdown).items():
        assert stray_numbers(breakdown, copy_text(draft)) == [], name
        dates = set(_ISO_DATE.findall(copy_text(draft)))
        assert dates <= _dates(breakdown)


def test_drafts_stay_neutral_and_never_name_an_excluded_source(breakdown) -> None:
    drafts = render_drafts(breakdown)
    blob = "\n".join(copy_text(draft) for draft in drafts.values())
    blob += "\n".join(image.svg for draft in drafts.values() for image in draft.images)
    assert refused_words(blob) == []
    assert excluded_sources().text.search(blob) is None
    assert "router" not in blob.lower()


def test_x_thread_fits_and_opens_on_the_claims_gap(breakdown) -> None:
    draft = render_drafts(breakdown)["x"]
    chart = charts(breakdown)["claims.svg"]
    assert 5 <= len(draft.posts) <= 7
    too_long = [(index, len(post)) for index, post in enumerate(draft.posts) if len(post) > 280]
    assert too_long == []
    hook = draft.posts[0]
    assert "swe_bench_pro" in hook
    assert "2.1" in hook and "lower" in hook
    assert "70%" in hook and "67.9%" in hook
    assert draft.link in draft.text
    assert len(draft.images) == 1
    image = draft.images[0]
    assert image.role == "claims" and image.svg == chart
    assert 1 <= image.width <= 4096 and 1 <= image.height <= 4096
    assert len(image.svg.encode()) <= 5_000_000


def test_linkedin_is_an_analysis_of_alternatives_with_the_chart(breakdown) -> None:
    draft = render_drafts(breakdown)["linkedin"]
    assert "analysis of alternatives" in draft.text
    assert len(draft.text) <= 3000
    assert draft.link in draft.text
    assert len(draft.images) == 1
    assert draft.images[0].svg == charts(breakdown)["claims.svg"]
    assert draft.images[0].width <= 8192 and draft.images[0].height <= 8192
    assert "text generator" in draft.text


def test_facebook_post_is_short_and_carries_the_chart_and_link(breakdown) -> None:
    draft = render_drafts(breakdown)["facebook"]
    assert len(draft.text) <= 500
    assert draft.link in draft.text
    assert len(draft.images) == 1
    assert draft.images[0].svg == charts(breakdown)["claims.svg"]


def test_instagram_carousel_is_square_cards_from_the_social_renderer(breakdown) -> None:
    draft = render_drafts(breakdown)["instagram"]
    made = charts(breakdown)
    assert 3 <= len(draft.images) <= 5
    assert [image.role for image in draft.images] == ["headline", "standing", "cost", "gaps"]
    assert draft.link in draft.text
    assert len(draft.text) <= 2200
    assert "caption" in draft.text.lower()
    for image in draft.images:
        assert (image.width, image.height) == (1080, 1080)
        assert image.svg.startswith("<svg ")
        assert 'width="1080"' in image.svg and 'height="1080"' in image.svg
        assert image.card is not None
        assert image.html == render_card_html(image.card)
        assert len(image.svg.encode()) <= 8_000_000
    assert breakdown.headline.text in draft.images[0].alt
    assert made["standing.svg"] in draft.images[1].svg
    assert made["cost.svg"] in draft.images[2].svg
    assert "cursorbench" in draft.images[3].alt


def test_reddit_draft_names_one_subreddit_and_does_not_cross_post(breakdown) -> None:
    draft = render_drafts(breakdown)["reddit"]
    assert draft.images == ()
    assert draft.subreddit == "r/LocalLLaMA"
    assert len(draft.title) <= 300
    assert len(draft.text) <= 40_000
    assert draft.title == breakdown.headline.text
    assert "ModelSpec" in draft.text
    assert "Do not cross-post." in draft.text
    assert draft.cross_post is False
    assert set(re.findall(r"r/[A-Za-z0-9_]+", draft.text)) == {"r/LocalLLaMA"}
    assert "self-promotion" in draft.rules.lower()
    assert "disclos" in draft.rules.lower()
    assert draft.link in draft.text


def test_hacker_news_is_a_title_and_url_jamie_decides(breakdown) -> None:
    draft = render_drafts(breakdown)["hackernews"]
    assert draft.posts == ()
    assert draft.images == ()
    assert len(draft.title) <= 80
    assert breakdown.headline.text.startswith(draft.title)
    assert draft.submission == f"{draft.title}\n{draft.link}"
    assert draft.note == "Jamie decides whether to submit"
    assert draft.jamie_decides is True


def test_caller_can_supply_the_breakdown_url(breakdown) -> None:
    url = "https://modelspec.dev/blog/lab-alpha-r1/"
    draft = render_drafts(breakdown, post_url=url)["x"]
    assert draft.link == url
    assert url in draft.text


def test_platform_module_has_no_posting_client() -> None:
    source = Path("release_blog/platforms.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)
    banned = ("requests", "httpx", "urllib", "tweepy", "praw", "socket", "http", "subprocess")
    for name in modules:
        assert not any(name == item or name.startswith(item + ".") for item in banned)


def test_model_225_hook_writes_the_six_drafts(breakdown, tmp_path) -> None:
    """PR #807 calls this signature. The hook's return value is the contract."""
    folder = tmp_path / "release"
    folder.mkdir()
    breakdown_path = tmp_path / "breakdown.json"
    breakdown_path.write_bytes(to_bytes(breakdown))
    message = _hook_from_model_225()(breakdown_path, folder, "lab-alpha")
    assert message == "Platform drafts generated for manual review and posting."
    social = folder / "social"
    for name in ("x.txt", "linkedin.txt", "facebook.txt", "instagram.txt", "reddit.md", "hn.txt"):
        assert (social / name).is_file(), name
    linkedin = (social / "linkedin.txt").read_text(encoding="utf-8")
    assert "https://modelspec.dev/blog/lab-alpha/" in linkedin
    assert breakdown.disclosures.neutrality in linkedin


def test_sample_drafts_trace_every_number_to_its_sentence(breakdown) -> None:
    for name, draft in render_drafts(breakdown).items():
        assert untraced_segments(breakdown, draft) == [], name


def test_instagram_standing_chart_rejects_an_invented_percent(breakdown) -> None:
    draft = render_drafts(breakdown)["instagram"]
    images = []
    for image in draft.images:
        if image.role == "standing":
            assert "<!-- chart -->" in image.svg
            image = replace(
                image,
                svg=image.svg.replace("<!-- chart -->", "<!-- chart --><text>99%</text>", 1),
            )
        images.append(image)
    found = untraced_segments(breakdown, replace(draft, images=tuple(images)))
    assert any("99%" in item for item in found)


def test_instagram_card_html_rejects_an_invented_percent(breakdown) -> None:
    draft = render_drafts(breakdown)["instagram"]
    image = draft.images[0]
    assert image.card is not None
    mutated = replace(image, card=replace(image.card, content="<p>The score is 99%.</p>"))
    assert mutated.html is not None and "99%" in mutated.html
    found = untraced_segments(breakdown, replace(draft, images=(mutated, *draft.images[1:])))
    assert any("99%" in item for item in found)


def test_held_back_score_cannot_be_rewritten_to_an_unrelated_percent(breakdown) -> None:
    draft = render_drafts(breakdown)["x"]
    posts = tuple(
        "The held-back score is 70%." if "second key" in post else post for post in draft.posts
    )
    assert any(post == "The held-back score is 70%." for post in posts)
    found = untraced_segments(breakdown, replace(draft, posts=posts))
    assert any("70%" in item for item in found)


def test_held_back_count_cannot_be_replaced_with_a_lab_percent(breakdown) -> None:
    draft = render_drafts(breakdown)["x"]
    posts = tuple(post.replace("quarantined: 1", "quarantined: 70%") for post in draft.posts)
    assert any("quarantined: 70%" in post for post in posts)
    found = untraced_segments(breakdown, replace(draft, posts=posts))
    assert any("quarantined: 70%" in item for item in found)


def test_nine_readings_keep_the_linkedin_url_and_disclosure(breakdown) -> None:
    url = "https://modelspec.dev/blog/example/"
    longer = _with_repeated_readings(breakdown, "terminal_bench", 9)
    draft = render_drafts(longer, post_url=url)["linkedin"]
    assert url in draft.text
    assert breakdown.disclosures.neutrality in draft.text
    assert "analysis of alternatives" in draft.text
    assert len(draft.text) <= 3000


def test_oversized_claims_chart_is_rejected(breakdown, monkeypatch) -> None:
    sample = charts(breakdown)

    def oversized(_breakdown: Breakdown) -> dict[str, str]:
        made = dict(sample)
        made["claims.svg"] = '<svg width="9000" height="9000"></svg>'
        return made

    monkeypatch.setattr(platforms, "charts", oversized)
    with pytest.raises(ValueError):
        render_drafts(breakdown)


def test_six_hundred_readings_exceed_the_image_limit(breakdown) -> None:
    longer = _with_repeated_readings(breakdown, "swe_bench_pro", 600)
    with pytest.raises(ValueError):
        render_drafts(longer)


def test_oversized_claims_bytes_are_rejected(breakdown, monkeypatch) -> None:
    sample = charts(breakdown)
    huge = '<svg width="680" height="248">' + ("x" * 5_000_001) + "</svg>"

    def oversized(_breakdown: Breakdown) -> dict[str, str]:
        made = dict(sample)
        made["claims.svg"] = huge
        return made

    monkeypatch.setattr(platforms, "charts", oversized)
    with pytest.raises(ValueError):
        render_drafts(breakdown)


def test_instagram_rejects_a_card_over_eight_megabytes(breakdown, monkeypatch) -> None:
    original = platforms._square

    def huge(title: str, lines: list[str], chart: str | None) -> str:
        svg = original(title, lines, chart)
        return svg.replace("</svg>", "<!-- " + ("x" * 8_000_000) + " --></svg>")

    monkeypatch.setattr(platforms, "_square", huge)
    with pytest.raises(ValueError):
        render_drafts(breakdown)


def test_platform_byte_and_pixel_ceilings_follow_published_caps() -> None:
    enforce = platforms._enforce_image_limits
    six_megabytes = DraftImage("claims", "", _svg(1000, 1000, 6_000_000), 1000, 1000)
    enforce("facebook", six_megabytes)
    with pytest.raises(ValueError):
        enforce("x", six_megabytes)
    with pytest.raises(ValueError):
        enforce("linkedin", six_megabytes)
    over_facebook = DraftImage("claims", "", _svg(1000, 1000, 10_000_001), 1000, 1000)
    with pytest.raises(ValueError):
        enforce("facebook", over_facebook)
    square = DraftImage("claims", "", _svg(9000, 9000, 64), 9000, 9000)
    for platform in ("x", "linkedin", "facebook"):
        with pytest.raises(ValueError):
            enforce(platform, square)
    tall = DraftImage("claims", "", _svg(680, 9832, 64), 680, 9832)
    for platform in ("x", "linkedin", "facebook"):
        with pytest.raises(ValueError):
            enforce(platform, tall)
    instagram = DraftImage("standing", "", _svg(1080, 1080, 8_000_001), 1080, 1080)
    with pytest.raises(ValueError):
        enforce("instagram", instagram)
    enforce("instagram", DraftImage("standing", "", _svg(1080, 1080, 64), 1080, 1080))
    with pytest.raises(ValueError):
        enforce("instagram", DraftImage("standing", "", _svg(2000, 2000, 64), 2000, 2000))
