"""Platform drafts for a release breakdown (MODEL-226).

Drafts are views of the MODEL-224 sample breakdown. Nothing is posted.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

from decision.excluded import excluded_sources
from pipeline.social_cards import render_card_html
from release_blog.model import Breakdown, Cited
from release_blog.platforms import AUTOMATIC_POSTING, render_drafts
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
