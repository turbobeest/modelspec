"""Platform drafts for a release breakdown (MODEL-226).

Drafts are views of the MODEL-224 sample breakdown. Nothing is posted.
"""

from __future__ import annotations

import ast
import re
from dataclasses import replace
from pathlib import Path

import pytest

from decision.excluded import excluded_sources
from pipeline.social_cards import render_card_html
from release_blog import platforms
from release_blog.breakdown import to_bytes
from release_blog.model import Breakdown
from release_blog.platforms import AUTOMATIC_POSTING, DraftImage, render_drafts
from release_blog.render import charts
from release_blog.tone import refused_words

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
    modules: list[str] = []
    for path in (Path("release_blog/platforms.py"), Path("release_blog/slots.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules.append(node.module)
    banned = ("requests", "httpx", "urllib", "tweepy", "praw", "socket", "http", "subprocess")
    for name in modules:
        assert not any(name == item or name.startswith(item + ".") for item in banned), name


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


# Signed-fixture oracle. These strings are literals: the test does not format
# them through the production helpers. Chart context is the slot's chart, not
# the platform that happens to repeat it.
_SNAPSHOT = "https://modelspec.dev/api/decision/snapshots/snap_ee376ecc9678d46b.json.gz"
_LAB = "https://lab.example.com/alpha-launch"
_BOARD = "https://board.example.org/results"
_PRICE = "https://lab.example.com/pricing"
_READ_LAB = "2026-09-20"
_READ_SNAP = "2026-09-26"
_HEADLINE = (
    "Alpha 2.5 is in the leading band for software engineering; "
    "independent readings sit beside the lab's figures"
)
_EXPECTED = {
    ("model.name", "label", "Alpha 2.5", "", ""),
    ("headline.text", "label", _HEADLINE, "", ""),
    ("post.url", "link", "https://modelspec.dev/blog/lab-alpha/", "", ""),
    ("claims.swe_bench_pro.claim", "hook", "70%", _LAB, _READ_LAB),
    ("claims.swe_bench_pro.readings[0].value", "hook", "67.9%", _BOARD, _READ_LAB),
    ("claims.swe_bench_pro.readings[0].difference", "hook", "2.1", _SNAPSHOT, _READ_SNAP),
    ("standing[0].band_size", "standing", "2", _SNAPSHOT, _READ_SNAP),
    ("standing[1].rank", "standing", "3", _SNAPSHOT, _READ_SNAP),
    ("standing[1].ranked_models", "standing", "3", _SNAPSHOT, _READ_SNAP),
    ("cost.offerings[0].task.input", "cost", "40,000", _PRICE, _READ_SNAP),
    ("cost.offerings[0].task.output", "cost", "4,000", _PRICE, _READ_SNAP),
    ("cost.offerings[0].cost_per_task", "cost", "$0.112", _PRICE, _READ_SNAP),
    ("claims.mmlu_pro.claim", "comparisons", "80%", _LAB, _READ_LAB),
    ("claims.mmlu_pro.readings[0].value", "comparisons", "0.78", _BOARD, _READ_LAB),
    ("claims.terminal_bench.claim", "comparisons", "50%", _LAB, _READ_LAB),
    ("claims.terminal_bench.readings[0].value", "comparisons", "48%", _BOARD, _READ_LAB),
    ("held_back.quarantined", "gaps", "1", _SNAPSHOT, _READ_SNAP),
    ("claims.unreported.livecodebench.reading", "gaps", "72%", _BOARD, _READ_LAB),
    ("claims.cursorbench.claim", "claims", "55%", _LAB, _READ_LAB),
    ("claims.mmlu_pro.claim", "claims", "80%", _LAB, _READ_LAB),
    ("claims.mmlu_pro.readings[0].value", "claims", "0.78", _BOARD, _READ_LAB),
    ("claims.swe_bench_pro.claim", "claims", "70%", _LAB, _READ_LAB),
    ("claims.swe_bench_pro.readings[0].value", "claims", "67.9%", _BOARD, _READ_LAB),
    ("claims.terminal_bench.claim", "claims", "50%", _LAB, _READ_LAB),
    ("claims.terminal_bench.readings[0].value", "claims", "48%", _BOARD, _READ_LAB),
    ("standing[0].estimate.value", "standing.chart", "0.44", _SNAPSHOT, _READ_SNAP),
    ("standing[0].estimate.low", "standing.chart", "0.04", _SNAPSHOT, _READ_SNAP),
    ("standing[0].estimate.high", "standing.chart", "0.84", _SNAPSHOT, _READ_SNAP),
    ("standing[0].leaders[1].estimate.value", "standing.chart", "0.36", _SNAPSHOT, _READ_SNAP),
    ("standing[0].leaders[1].estimate.low", "standing.chart", "-0.30", _SNAPSHOT, _READ_SNAP),
    ("standing[0].leaders[1].estimate.high", "standing.chart", "1.01", _SNAPSHOT, _READ_SNAP),
    ("standing[1].estimate.value", "standing.chart", "-0.31", _SNAPSHOT, _READ_SNAP),
    ("standing[1].estimate.low", "standing.chart", "-1.10", _SNAPSHOT, _READ_SNAP),
    ("standing[1].estimate.high", "standing.chart", "0.47", _SNAPSHOT, _READ_SNAP),
    ("standing[1].leaders[0].estimate.value", "standing.chart", "0.40", _SNAPSHOT, _READ_SNAP),
    ("standing[1].leaders[0].estimate.low", "standing.chart", "-0.66", _SNAPSHOT, _READ_SNAP),
    ("standing[1].leaders[0].estimate.high", "standing.chart", "1.47", _SNAPSHOT, _READ_SNAP),
    ("standing[1].leaders[1].estimate.value", "standing.chart", "0.17", _SNAPSHOT, _READ_SNAP),
    ("standing[1].leaders[1].estimate.low", "standing.chart", "-0.89", _SNAPSHOT, _READ_SNAP),
    ("standing[1].leaders[1].estimate.high", "standing.chart", "1.23", _SNAPSHOT, _READ_SNAP),
    ("standing.scale.-1", "standing.chart", "-1", _SNAPSHOT, _READ_SNAP),
    ("standing.scale.0", "standing.chart", "0", _SNAPSHOT, _READ_SNAP),
    ("standing.scale.1", "standing.chart", "1", _SNAPSHOT, _READ_SNAP),
    ("cost.offerings[0].cost_per_task", "cost.chart", "$0.112", _PRICE, _READ_SNAP),
}
_SUPPLIER = "ModelSpec supplies evaluation services to this lab."
_EARLY = "ModelSpec received early access without editorial conditions."


def _posted(draft) -> str:
    parts = [draft.text, draft.title, draft.submission, draft.note, draft.rules, draft.link]
    for image in draft.images:
        parts.append(image.alt)
        parts.append(image.svg)
        if image.html:
            parts.append(image.html)
    return "\n".join(parts)


def _slot_rows(draft) -> set[tuple[str, str, str, str, str]]:
    return {
        (slot.fact_id, slot.chart, slot.formatted, slot.source_url, slot.read_date)
        for slot in draft.manifest
    }


def test_signed_fixture_numbers_are_literal_fact_slots(breakdown) -> None:
    drafts = render_drafts(breakdown)
    found = set().union(*(_slot_rows(draft) for draft in drafts.values()))
    assert found == _EXPECTED


def test_source_url_and_read_date_are_in_each_platforms_copy(breakdown) -> None:
    drafts = render_drafts(breakdown)
    for name, draft in drafts.items():
        blob = _posted(draft)
        for fact_id, chart, _formatted, url, read in _slot_rows(draft):
            if not url:
                continue
            assert url in blob, (name, fact_id, chart)
            assert read in blob, (name, fact_id, chart)


def test_disclosures_are_in_every_platforms_posted_copy(breakdown) -> None:
    related = breakdown.model_copy(
        update={
            "disclosures": breakdown.disclosures.model_copy(
                update={
                    "supplier": _SUPPLIER,
                    "early_access": _EARLY,
                }
            )
        }
    )
    Breakdown.model_validate(related.model_dump(by_alias=True))
    for name, draft in render_drafts(related).items():
        blob = _posted(draft)
        assert _SUPPLIER in blob, name
        assert _EARLY in blob, name


def test_instagram_standing_svg_rejects_a_claims_percent(breakdown, monkeypatch) -> None:
    original = platforms.charts

    def injected(b):
        made = dict(original(b))
        made["standing.svg"] = made["standing.svg"].replace("</svg>", "<text>70%</text></svg>", 1)
        return made

    monkeypatch.setattr(platforms, "charts", injected)
    with pytest.raises(ValueError):
        render_drafts(breakdown)


def test_instagram_standing_html_rejects_a_claims_percent(breakdown, monkeypatch) -> None:
    original = platforms.render_card_html

    def injected(card):
        html = original(card)
        if card.filename == "instagram-standing.svg":
            html = html.replace("</body>", "<p>70%</p></body>")
        return html

    monkeypatch.setattr(platforms, "render_card_html", injected)
    with pytest.raises(ValueError):
        render_drafts(breakdown)


def test_instagram_standing_alt_rejects_a_claims_percent(breakdown, monkeypatch) -> None:
    original = platforms._square_image

    def injected(*args, **kwargs):
        image = original(*args, **kwargs)
        if image.role == "standing":
            image = replace(image, alt=image.alt + " 70%")
        return image

    monkeypatch.setattr(platforms, "_square_image", injected)
    with pytest.raises(ValueError):
        render_drafts(breakdown)


def test_hook_cannot_replace_the_independent_reading(breakdown, monkeypatch) -> None:
    original = platforms._hook

    def replaced(b):
        return original(b).replace("67.9%", "70%")

    monkeypatch.setattr(platforms, "_hook", replaced)
    with pytest.raises(ValueError):
        render_drafts(breakdown)


def test_template_literal_cannot_add_a_number(breakdown, monkeypatch) -> None:
    original = platforms._hook_sentence

    def extra(b, piece):
        original(b, piece)
        piece.lit(" The extra figure is 70%.")

    monkeypatch.setattr(platforms, "_hook_sentence", extra)
    with pytest.raises(ValueError, match="template literal"):
        render_drafts(breakdown)


def test_cost_chart_rejects_a_number_from_the_claims_chart(breakdown, monkeypatch) -> None:
    original = platforms.charts

    def moved(b):
        made = dict(original(b))
        made["cost.svg"] = made["cost.svg"].replace("</svg>", "<text>67.9%</text></svg>", 1)
        return made

    monkeypatch.setattr(platforms, "charts", moved)
    with pytest.raises(ValueError):
        render_drafts(breakdown)


def test_model_225_hook_uses_the_merged_pipeline(breakdown, tmp_path) -> None:
    """The merged #807 module calls this signature. No local author branch."""
    from release_blog.pipeline import _platforms

    folder = tmp_path / "release"
    folder.mkdir()
    breakdown_path = tmp_path / "breakdown.json"
    breakdown_path.write_bytes(to_bytes(breakdown))
    message = _platforms(breakdown_path, folder, "lab-alpha")
    assert message == "Platform drafts generated for manual review and posting."
    social = folder / "social"
    for name in ("x.txt", "linkedin.txt", "facebook.txt", "instagram.txt", "reddit.md", "hn.txt"):
        assert (social / name).is_file(), name
    linkedin = (social / "linkedin.txt").read_text(encoding="utf-8")
    assert "https://modelspec.dev/blog/lab-alpha/" in linkedin
    assert breakdown.disclosures.neutrality in linkedin


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
