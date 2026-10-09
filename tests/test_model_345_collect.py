"""MODEL-345 collector names the reading rule on every licence value."""

from __future__ import annotations

from dataclasses import replace

from decision.licence_rules import LICENCE_READING_RULES
from decision.model import CitedRegion, Source
from decision.normalise import NORMALISERS, normalise_document
from decision.sources import CopyStore
from decision.verify import StoredRegions, licence_is_bound
from scripts.model_345_collect import BINDING_REGION, FACETS, READINGS, readme_binds_licence


def test_every_collector_value_names_the_rule_it_applied() -> None:
    assert set(LICENCE_READING_RULES) == set(FACETS)
    for model_id, row in READINGS.items():
        for facet in FACETS:
            reading = row["facets"][facet]
            assert reading["rule"] == facet, (model_id, facet)
            assert reading["rule"] in LICENCE_READING_RULES


def _readme(source_id: str = "gemma-readme") -> Source:
    return Source(
        id=source_id,
        url="https://huggingface.co/google/gemma-4-e2b-it",
        normaliser="html-default",
        kind="weights_repository",
        cited_regions=[
            CitedRegion(id=BINDING_REGION,
                        locator={"kind": "heading", "value": BINDING_REGION}),
        ],
    )


def test_the_collector_binds_on_the_cited_region_the_verifier_reads(tmp_path) -> None:
    apache = "https://www.apache.org/licenses/LICENSE-2.0"
    names = ("gemma 4 E2B it", "Gemma", "gemma-4-e2b-it")
    subject = "google/gemma-4-e2b-it"
    outside = """<html><body>
<p>gemma 4 E2B it</p>
<p>license: apache-2.0</p>
<h2 id="model-spec">Model spec</h2>
<p>Architecture notes for a sibling page.</p>
</body></html>
"""
    store = CopyStore(tmp_path)
    readme = _readme()
    ref = store.put(outside.encode())
    rules = replace(NORMALISERS["html-default"], strip_volatile=False)
    page = normalise_document(outside.encode(), rules).text
    region = StoredRegions(store, {readme.id: readme}).text(readme.id, ref, BINDING_REGION)
    assert region
    assert "license:" not in region.casefold()
    assert licence_is_bound(names, [page], apache, subject=subject)
    assert not licence_is_bound(names, [region], apache, subject=subject)
    assert not readme_binds_licence(readme, store, ref, names, apache, subject)

    inside = """<html><body>
<p>Some other model</p>
<h2 id="model-spec">Model spec</h2>
<p>gemma 4 E2B it</p>
<p>license_link: https://www.apache.org/licenses/LICENSE-2.0.txt</p>
</body></html>
"""
    ref = store.put(inside.encode())
    region = StoredRegions(store, {readme.id: readme}).text(readme.id, ref, BINDING_REGION)
    assert licence_is_bound(names, [region], apache, subject=subject)
    assert readme_binds_licence(readme, store, ref, names, apache, subject)
