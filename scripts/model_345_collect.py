#!/usr/bin/env python3
"""File licence facts for the open-weights lineup from the licence text (MODEL-345).

Reads each model's licence (its own Hugging Face LICENSE, or the text the README
front matter names when the repo has none), retains the copy, and files the four
``licence.*`` facts. ``modelspec verify`` is the only writer of outcomes.

Values in ``READINGS`` were read on 2026-10-08 from those licence texts. Each
value carries a verbatim clause and the ``LICENCE_READING_RULES`` key it applied.
The script refuses to file a value whose clause is not in the copy it just
retained. A null value is ``not_disclosed`` when that facet's rule says the
licence does not address it.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path

import yaml

from decision.licence_rules import LICENCE_READING_RULES
from decision.model import CitedRegion, Fact, RegionLocator, Source, SourceRef, VerificationActor
from decision.normalise import NORMALISERS, normalise_document
from decision.sources import CopyStore, Fetcher, load_sources, recheck
from decision.verify import Claim, Queue, StoredRegions, licence_is_bound, normalise_name
from scripts.policy.licence_coverage import FACETS, open_weights_lineup

READ_ON = "2026-10-08"
READ_AT = datetime(2026, 10, 8, 18, tzinfo=UTC)
COLLECTOR = VerificationActor(
    agent="grok-model-345",
    model_family="xai",
    method="licence-text-read@1",
)
#: The README region the filed fact cites, and the region the binding check reads.
BINDING_REGION = "model-spec"
LABELS = {
    "licence.commercial_use": "commercial use",
    "licence.user_cap": "monthly active user cap",
    "licence.output_training": "output training",
    "licence.fine_tuning": "licence fine tuning",
}

# Clauses below are copied from the retained licence text, not from a catalogue.
MIT_GRANT = (
    "to use, copy, modify, merge, publish, distribute, sublicense, and/or sell "
    "copies of the Software"
)
MIT_NOTICE = (
    "The above copyright notice and this permission notice shall be included in all "
    "copies or substantial portions of the Software."
)
APACHE_DERIV = "copyright license to reproduce, prepare Derivative Works of"
APACHE_SELL = "use, offer to sell, sell, import"
K2_DISPLAY = (
    "more than 100 million monthly active users, or more than 20 million US dollars "
    "(or equivalent in other currencies) in monthly revenue, you shall prominently "
    'display "Kimi K2.6" on the user interface of such product or service.'
)
K3_AGREEMENT = (
    "the Licensee must enter into a separate agreement with Moonshot AI before using "
    "the Software or its derivative works for any commercial purpose."
)
K3_DISPLAY = (
    "more than 100 million monthly active users, or more than 20 million US dollars "
    '(or equivalent in other currencies) in monthly revenue, "Kimi K3" must be '
    "prominently displayed on the user interface of such product or service."
)
K3_TUNE = "to run, deploy, fine-tune, or otherwise modify the Software and create derivative works"
QWEN_DISPLAY = (
    "more than 100,000,000 monthly active users or US$ 20,000,000 "
    "(or equivalent in other currencies) monthly revenue, respective model name must "
    "be prominently displayed"
)
QWEN_SEPARATE = (
    "the licensee shall obtain a separate license from Qwen before Using the Software "
    "or its derivative works for any commercial purpose."
)
QWEN_TUNE = "fine-tune, and create derivative works"
GLM_REVIEW = (
    "the Licensee must pass Z.AI's security review before using the Software or its "
    "derivative works for any commercial purpose."
)
GLM_REVENUE = (
    "exceeds 10 billion US dollars (or the equivalent in other currencies) in total "
    "over any consecutive 12 months"
)
GLM_TUNE = "to run, deploy, fine-tune, or otherwise modify the Software and create derivative works from it"
KALM_EU = "KaLM-Embedding IS NOT INTENDED FOR USE WITHIN THE EUROPEAN UNION."
KALM_DERIVATIVE = (
    "any other machine learning model which is created by transfer of patterns of the "
    "weights, parameters, operations, or Output of Gemma, to that model in order to "
    "cause that model to perform similarly to Gemma, including distillation methods "
    "that use intermediate data representations or methods based on the generation of "
    "synthetic data Outputs by Gemma for training that model"
)

_LICENCE_BLOCK = re.compile(
    r"(?ms)^- facet: licence\.commercial_use\n.*?(?=^- facet: (?!licence\.)|^---\n)"
)


def _reading(value: object, *quotes: str) -> dict:
    return {"value": value, "quotes": quotes, "read_on": READ_ON}


def _mit() -> dict[str, dict]:
    # Grant includes sell and modify. The only condition is the notice on copies.
    # No monthly-active-user figure. No sentence about training on outputs.
    return {
        "licence.commercial_use": _reading("permitted", MIT_GRANT),
        "licence.user_cap": _reading("unbounded", MIT_NOTICE),
        "licence.output_training": _reading(None, MIT_GRANT),
        "licence.fine_tuning": _reading("permitted", MIT_GRANT),
    }


def _apache() -> dict[str, dict]:
    # Section 2: copyright licence to prepare Derivative Works, patent licence to sell.
    # No monthly-active-user figure. No sentence about training on outputs.
    return {
        "licence.commercial_use": _reading("permitted", APACHE_SELL),
        "licence.user_cap": _reading("unbounded", APACHE_DERIV),
        "licence.output_training": _reading(None, APACHE_DERIV),
        "licence.fine_tuning": _reading("permitted", APACHE_DERIV),
    }


def _licence(model_id: str, url: str, normaliser: str = "text-default") -> dict:
    slug = re.sub(r"[^a-z0-9]+", "-", model_id.casefold()).strip("-")
    return {"id": f"model-345-{slug}", "url": url, "normaliser": normaliser}


APACHE = {
    "id": "model-345-apache-2.0",
    "url": "https://www.apache.org/licenses/LICENSE-2.0.txt",
    "normaliser": "text-default",
}
GEMMA = {
    # README license_link. The retained page is the Apache License 2.0.
    # It does not incorporate Gemma Terms of Use or a Prohibited Use Policy,
    # so commercial_use stays permitted under the commercial_use rule.
    "id": "model-345-gemma-4-license",
    "url": "https://ai.google.dev/gemma/docs/gemma_4_license",
    "normaliser": "html-default",
}
CANONICAL_MIT = {
    # README says license: mit. The repo publishes no LICENSE file.
    "id": "model-345-mit-opensource",
    "url": "https://opensource.org/license/mit",
    "normaliser": "html-default",
}

# licence.* readings. None is not_disclosed. read_on is 2026-10-08 on every row.
READINGS: dict[str, dict] = {
    "deepseek/deepseek-flash": {
        "readme_source": "model-163-deepseek-deepseek-flash",
        "readme_repo": "deepseek-ai/DeepSeek-V4.1-Flash",
        "licence": _licence(
            "deepseek/deepseek-flash",
            "https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/raw/main/LICENSE",
        ),
        "facets": _mit(),  # README license: mit. Own LICENSE is that MIT text.
    },
    "deepseek/deepseek-v3-1": {
        "readme_source": "model-163-deepseek-deepseek-v3-1",
        "readme_repo": "deepseek-ai/DeepSeek-V3.1",
        "licence": _licence(
            "deepseek/deepseek-v3-1",
            "https://huggingface.co/deepseek-ai/DeepSeek-V3.1/raw/main/LICENSE",
        ),
        "facets": _mit(),
    },
    "deepseek/deepseek-v4-pro": {
        "readme_source": "model-143-deepseek-deepseek-v4-pro",
        "readme_repo": "deepseek-ai/DeepSeek-V4-Pro",
        "licence": _licence(
            "deepseek/deepseek-v4-pro",
            "https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/raw/main/LICENSE",
        ),
        "facets": _mit(),
    },
    "microsoft/phi-4": {
        "readme_source": "model-163-microsoft-phi-4",
        "readme_repo": "microsoft/phi-4",
        "licence": _licence(
            "microsoft/phi-4",
            "https://huggingface.co/microsoft/phi-4/raw/main/LICENSE",
        ),
        "facets": _mit(),  # README license: mit and license_link points at this file.
    },
    "zhipu/glm-5-2": {
        "readme_source": "model-143-zhipu-glm-5-2",
        "readme_repo": "zai-org/GLM-5.2",
        "licence": _licence(
            "zhipu/glm-5-2",
            "https://huggingface.co/zai-org/GLM-5.2/raw/main/LICENSE",
        ),
        "facets": _mit(),
    },
    "microsoft/harrier-oss-v1-27b": {
        "readme_source": "model-143-microsoft-harrier-oss-v1-27b",
        "readme_repo": "microsoft/harrier-oss-v1-27b",
        "licence": CANONICAL_MIT,
        "facets": _mit(),
    },
    "qwen/qwen3-embedding-8b": {
        "readme_source": "model-163-qwen-qwen3-embedding-8b",
        "readme_repo": "Qwen/Qwen3-Embedding-8B",
        "licence": _licence(
            "qwen/qwen3-embedding-8b",
            "https://huggingface.co/Qwen/Qwen3-Embedding-8B/raw/main/LICENSE",
        ),
        "facets": _apache(),  # README license: apache-2.0. Own LICENSE is Apache 2.0.
    },
    "kingsoft/qzhou-embedding": {
        "readme_source": "model-143-kingsoft-qzhou-embedding",
        "readme_repo": "Kingsoft-LLM/QZhou-Embedding",
        "licence": APACHE,  # README license: apache-2.0. No licence file in the repo.
        "facets": _apache(),
    },
    "querit/querit": {
        "readme_source": "model-143-querit-querit",
        "readme_repo": "Querit/Querit",
        "licence": APACHE,
        "facets": _apache(),
    },
    "querit/querit-4b": {
        "readme_source": "model-143-querit-querit-4b",
        "readme_repo": "Querit/Querit-4B",
        "licence": APACHE,
        "facets": _apache(),
    },
    "google/gemma-4-26b-a4b-it": {
        "readme_source": "model-163-google-gemma-4-26b-a4b-it",
        "readme_repo": "google/gemma-4-26b-a4b-it",
        "licence": GEMMA,  # README license: apache-2.0 and license_link to this page.
        "facets": _apache(),
    },
    "google/gemma-4-31b-it": {
        "readme_source": "model-163-google-gemma-4-31b-it",
        "readme_repo": "google/gemma-4-31b-it",
        "licence": GEMMA,
        "facets": _apache(),
    },
    "google/gemma-4-e2b-it": {
        "readme_source": "model-163-google-gemma-4-e2b-it",
        "readme_repo": "google/gemma-4-E2B-it",
        "licence": GEMMA,
        "facets": _apache(),
    },
    "google/gemma-4-e4b-it": {
        "readme_source": "model-163-google-gemma-4-e4b-it",
        "readme_repo": "google/gemma-4-E4B-it",
        "licence": GEMMA,
        "facets": _apache(),
    },
    "moonshot/kimi-k2-6": {
        # Modified MIT. The only added term is a display duty above 100M MAU or
        # $20M monthly revenue. That figure is not a separate-agreement cap.
        # No sentence about training on outputs.
        "readme_source": "model-143-moonshot-kimi-k2-6",
        "readme_repo": "moonshotai/Kimi-K2.6",
        "licence": _licence(
            "moonshot/kimi-k2-6",
            "https://huggingface.co/moonshotai/Kimi-K2.6/raw/main/LICENSE",
        ),
        "facets": {
            "licence.commercial_use": _reading("permitted_with_conditions", K2_DISPLAY),
            "licence.user_cap": _reading("unbounded", K2_DISPLAY),
            "licence.output_training": _reading(None, MIT_GRANT),
            "licence.fine_tuning": _reading("permitted_with_conditions", K2_DISPLAY, MIT_GRANT),
        },
    },
    "moonshot/kimi-k3": {
        # Grant names fine-tune. A separate agreement is required for a MaaS
        # business above $20M over 12 months. 100M MAU only requires displaying
        # "Kimi K3". No sentence grants or bans training on outputs.
        "readme_source": "model-143-moonshot-kimi-k3",
        "readme_repo": "moonshotai/Kimi-K3",
        "licence": _licence(
            "moonshot/kimi-k3",
            "https://huggingface.co/moonshotai/Kimi-K3/raw/main/LICENSE",
        ),
        "facets": {
            "licence.commercial_use": _reading("permitted_with_conditions", K3_AGREEMENT),
            "licence.user_cap": _reading("unbounded", K3_DISPLAY),
            "licence.output_training": _reading(None, K3_TUNE),
            "licence.fine_tuning": _reading("permitted_with_conditions", K3_TUNE),
        },
    },
    "qwen/qwen3-8-flash-next": {
        # Qwen Community License 1.0, the file license_link names. 100,000,000 MAU
        # is a display duty. A MaaS or AI Work Assistant business needs a separate
        # licence. No sentence about training on outputs.
        "readme_source": "model-143-qwen-qwen3-8-flash-next",
        "readme_repo": "Qwen/Qwen3.8-Flash-Next",
        "licence": _licence(
            "qwen/qwen3-8-flash-next",
            "https://huggingface.co/Qwen/Qwen3.8-Flash-Next/raw/main/LICENSE",
        ),
        "facets": {
            "licence.commercial_use": _reading("permitted_with_conditions", QWEN_SEPARATE),
            "licence.user_cap": _reading("unbounded", QWEN_DISPLAY),
            "licence.output_training": _reading(None, QWEN_TUNE),
            "licence.fine_tuning": _reading("permitted_with_conditions", QWEN_TUNE),
        },
    },
    "zhipu/glm-5-3": {
        # Grant names fine-tune. A MaaS business above $10B over 12 months must
        # pass a security review. No monthly-active-user figure. No sentence
        # about training on outputs.
        "readme_source": "model-143-zhipu-glm-5-3",
        "readme_repo": "zai-org/GLM-5.3",
        "licence": _licence(
            "zhipu/glm-5-3",
            "https://huggingface.co/zai-org/GLM-5.3/raw/main/LICENSE",
        ),
        "facets": {
            "licence.commercial_use": _reading("permitted_with_conditions", GLM_REVIEW),
            "licence.user_cap": _reading("unbounded", GLM_REVENUE),
            "licence.output_training": _reading(None, GLM_TUNE),
            "licence.fine_tuning": _reading("permitted_with_conditions", GLM_TUNE),
        },
    },
    "tencent/kalm-embedding-gemma3-12b-2511": {
        # KaLM grant is MIT-like and bars EU use. The same file embeds the Gemma
        # Terms of Use. A model trained on Gemma outputs so that it performs like
        # Gemma is a Model Derivative, so output_training is restricted.
        "readme_source": "model-143-tencent-kalm-embedding-gemma3-12b-2511",
        "readme_repo": "tencent/KaLM-Embedding-Gemma3-12B-2511",
        "licence": _licence(
            "tencent/kalm-embedding-gemma3-12b-2511",
            "https://huggingface.co/tencent/KaLM-Embedding-Gemma3-12B-2511/raw/main/LICENSE.txt",
        ),
        "facets": {
            "licence.commercial_use": _reading("permitted_with_conditions", KALM_EU),
            "licence.user_cap": _reading("unbounded", MIT_NOTICE),
            "licence.output_training": _reading("restricted", KALM_DERIVATIVE),
            "licence.fine_tuning": _reading("permitted_with_conditions", MIT_GRANT, KALM_EU),
        },
    },
}

for _row in READINGS.values():
    for _facet, _reading in _row["facets"].items():
        if _facet not in LICENCE_READING_RULES:
            raise SystemExit(f"no licence reading rule for {_facet}")
        # Each value applies licence_reading_rule(_facet): the condition rule and
        # the facet rule. Inheritance is applied when the licence is bound.
        # The filed key is the facet.
        _reading["rule"] = _facet


def _front_matter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise SystemExit(f"{path}: no front matter")
    return yaml.safe_load(text.split("---", 2)[1]) or {}, text


def _published_names(data: dict) -> tuple[str, ...]:
    model_id = data["model_id"]
    raw = (
        data.get("display_name"),
        data.get("family"),
        data.get("version"),
        model_id.split("/", 1)[-1],
    )
    names: list[str] = []
    for name in raw:
        if isinstance(name, str) and name.strip() and name.strip() not in names:
            names.append(name.strip())
    if not names:
        raise SystemExit(f"{model_id}: card has no published name")
    return tuple(names)


def _licence_sources() -> list[dict]:
    seen: dict[str, dict] = {}
    for row in READINGS.values():
        licence = row["licence"]
        previous = seen.get(licence["id"])
        if previous is not None and previous["url"] != licence["url"]:
            raise SystemExit(f"licence source {licence['id']} has two URLs")
        seen[licence["id"]] = licence
    return list(seen.values())


def _as_source(spec: dict) -> Source:
    return Source(
        id=spec["id"],
        url=spec["url"],
        fetch="http",
        normaliser=spec["normaliser"],
        kind="licence_text",
        cited_regions=[CitedRegion(id="page", locator=RegionLocator(kind="page", value=""))],
    )


def _register(path: Path, specs: list[dict]) -> None:
    text = path.read_text(encoding="utf-8")
    fresh = [spec for spec in specs if f"- id: {spec['id']}\n" not in text]
    if not fresh:
        return
    rows = []
    for spec in fresh:
        rows.append({
            "id": spec["id"],
            "url": spec["url"],
            "fetch": "http",
            "normaliser": spec["normaliser"],
            "kind": "licence_text",
            "cited_regions": [{"id": "page", "locator": {"kind": "page", "value": ""}}],
        })
    block = yaml.safe_dump(rows, sort_keys=False, allow_unicode=True)
    if not text.endswith("\n"):
        text += "\n"
    comment = ""
    if "MODEL-345 licence texts" not in text:
        comment = "# MODEL-345 licence texts; read 2026-10-08.\n"
    path.write_text(text + comment + block, encoding="utf-8")


def _span(text: str, path: Path) -> tuple[int, int]:
    match = _LICENCE_BLOCK.search(text)
    if match is None:
        raise SystemExit(f"{path}: licence facts are not a contiguous block")
    found = re.findall(r"(?m)^- facet: (\S+)", match.group(0))
    if found != list(FACETS):
        raise SystemExit(f"{path}: licence block is {found}")
    return match.start(), match.end()


def _fact_block(facts: list[Fact]) -> str:
    rows = []
    for fact in facts:
        row = fact.model_dump(mode="json", exclude={"id", "subject", "verification"})
        for key in ("derivation", "measurement"):
            if row.get(key) is None:
                row.pop(key, None)
        if not row.get("checked_sources"):
            row.pop("checked_sources", None)
        rows.append(row)
    return yaml.safe_dump(rows, sort_keys=False, allow_unicode=True)


def _replace(path: Path, text: str, facts: list[Fact]) -> None:
    start, end = _span(text, path)
    path.write_text(text[:start] + _fact_block(facts) + text[end:], encoding="utf-8")


def _show(value: object) -> str:
    return "not_disclosed" if value is None else str(value)


def _text(store: CopyStore, snapshot_ref: str, normaliser: str) -> str:
    return normalise_document(store.get(snapshot_ref), NORMALISERS[normaliser]).text


def _card_base_model(data: dict) -> str | None:
    """The card's ``lineage.base_model``, or ``None`` when it names no base."""
    lineage = data.get("lineage")
    if not isinstance(lineage, dict):
        return None
    raw = lineage.get("base_model")
    if not isinstance(raw, str):
        return None
    text = raw.strip()
    return text or None


def readme_binds_licence(readme: Source, store: CopyStore, copy_ref: str,
                         names: tuple[str, ...], licence_url: str, subject: str,
                         licence_text: str | None = None,
                         base_model: str | None = None) -> str | None:
    """The rule by which the cited README region binds this licence, or ``None``.

    The text is the cited region ``StoredRegions`` gives the verifier. The
    judgement is :func:`decision.verify.licence_is_bound`. ``licence_text``
    is the retained licence. A ``license:`` SPDX id binds a root file only
    when that text carries the id's signature. ``base_model`` is the card's
    ``lineage.base_model``. A base licence binds the fine-tune when that
    licence requires derivatives to carry its terms.
    """
    text = StoredRegions(store, {readme.id: readme}).text(readme.id, copy_ref, BINDING_REGION)
    if not text:
        return None
    return licence_is_bound(
        names, [text], licence_url, subject=subject, page_urls=(str(readme.url),),
        licence_text=licence_text, base_model=base_model,
    )


def collect(root: Path, *, dry_run: bool, report_path: Path | None) -> dict:
    root = root.resolve()
    lineup = open_weights_lineup(root / "premier" / "slice-1.yaml")
    if set(lineup) != set(READINGS):
        missing = sorted(set(lineup) - set(READINGS))
        extra = sorted(set(READINGS) - set(lineup))
        raise SystemExit(f"lineup and readings differ: missing={missing} extra={extra}")

    registry_path = root / "registry" / "sources.yaml"
    registered = load_sources(registry_path)
    cards = {}
    for model_id, row in READINGS.items():
        path = root / "models" / f"{model_id}.md"
        data, text = _front_matter(path)
        if data.get("model_id") != model_id:
            raise SystemExit(f"{path}: model_id is {data.get('model_id')}")
        _span(text, path)
        readme = registered.get(row["readme_source"])
        if readme is None or row["readme_repo"] not in str(readme.url):
            raise SystemExit(f"{model_id}: readme source {row['readme_source']} is not registered")
        if BINDING_REGION not in {region.id for region in readme.cited_regions}:
            raise SystemExit(f"{row['readme_source']}: no {BINDING_REGION} region")
        cards[model_id] = (path, data, text, readme)

    wanted = []
    seen = set()
    for model_id in lineup:
        readme = cards[model_id][3]
        if readme.id not in seen:
            wanted.append(readme)
            seen.add(readme.id)
    for spec in _licence_sources():
        wanted.append(_as_source(spec))

    store = CopyStore()
    fetched = recheck(
        wanted,
        {},
        [],
        fetcher=Fetcher(timeout=45.0, retries=3, min_host_interval=0.4),
        store=store,
        now=READ_AT,
    )
    failures = [sid for sid, state in fetched.states.items() if state.snapshot is None]
    if failures:
        raise SystemExit(f"unreachable sources: {failures}")

    problems: list[str] = []
    prepared = []
    report_rows = []
    for model_id in lineup:
        path, data, text, readme = cards[model_id]
        row = READINGS[model_id]
        licence = row["licence"]
        licence_snap = fetched.states[licence["id"]].snapshot
        readme_snap = fetched.states[readme.id].snapshot
        assert licence_snap is not None and readme_snap is not None
        licence_text = _text(store, licence_snap.copy_ref, licence["normaliser"])
        names = _published_names(data)
        base_model = _card_base_model(data)
        rule = readme_binds_licence(
            readme, store, readme_snap.copy_ref, names, licence["url"], model_id,
            licence_text, base_model=base_model,
        )
        if not rule:
            problems.append(f"{model_id}: model page does not bind the licence")
        else:
            print(f"{model_id}: {rule}")
        normal = normalise_name(licence_text)
        facet_rows = []
        for facet in FACETS:
            reading = row["facets"][facet]
            if reading.get("rule") != facet:
                problems.append(f"{model_id} {facet}: rule is {reading.get('rule')}")
            for quote in reading["quotes"]:
                if normalise_name(quote) not in normal:
                    problems.append(f"{model_id} {facet}: quote not in retained licence: {quote}")
            facet_rows.append(reading)
        existing = {
            fact["facet"]: fact
            for fact in (data.get("facts") or [])
            if isinstance(fact, dict) and fact.get("facet") in FACETS
        }
        # The licence region is the only reading. The model page is cited so
        # the verifier can bind that licence to this model. It is not a reading.
        refs = [
            SourceRef(source_id=licence["id"], snapshot_ref=licence_snap.copy_ref,
                      cited_regions=["page"]),
            SourceRef(source_id=readme.id, snapshot_ref=readme_snap.copy_ref,
                      cited_regions=[BINDING_REGION]),
        ]
        facts = []
        disagreements = []
        for facet, reading in zip(FACETS, facet_rows, strict=True):
            value = reading["value"]
            old = existing.get(facet)
            old_value = None if old is None else old.get("value")
            old_state = None if old is None else old.get("state")
            if old_state == "known" and old_value != value:
                disagreements.append(
                    f"DISAGREE {model_id} {facet} {_show(old_value)} -> {_show(value)}"
                )
            checked = [readme.id, licence["id"]]
            kwargs = {
                "id": f"{model_id}#{facet}",
                "subject": {"kind": "model", "id": model_id},
                "facet": facet,
                "state": "known" if value is not None else "not_disclosed",
                "sources": refs,
            }
            if value is None:
                kwargs["checked_sources"] = checked
            else:
                kwargs["value"] = value
            facts.append(Fact.model_validate(kwargs))
            report_rows.append({
                "model_id": model_id,
                "facet": facet,
                "value": value,
                "previous_value": old_value,
                "previous_state": old_state,
                "disagreement": old_state == "known" and old_value != value,
                "url": licence["url"],
                "read_on": reading["read_on"],
                "quotes": list(reading["quotes"]),
                "rule": reading["rule"],
                "licence_source": licence["id"],
                "readme_source": readme.id,
                "binding": rule,
            })
        prepared.append((path, text, facts, names, disagreements, base_model))

    if problems:
        for problem in problems:
            print(problem)
        raise SystemExit(f"{len(problems)} licence reading(s) failed the retained-copy check")

    for _path, _card, _facts, _names, disagreements, _base_model in prepared:
        for line in disagreements:
            print(line)
    payload = {"read_on": READ_ON, "rows": report_rows}
    if report_path is not None:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                               encoding="utf-8")
    if dry_run:
        print(f"dry-run: {len(report_rows)} readings, {sum(1 for r in report_rows if r['disagreement'])} disagreements, nothing written")
        return payload

    _register(registry_path, _licence_sources())
    queue = Queue(root / "verification")
    filed = 0
    for path, text, facts, names, _disagreements, base_model in prepared:
        _replace(path, text, facts)
        for fact in facts:
            unit = "monthly_active_users" if fact.facet == "licence.user_cap" else None
            queue.file(
                Claim.from_fact(fact, names=names, collector=COLLECTOR, unit=unit,
                                label=LABELS[fact.facet], base_model=base_model),
                at=READ_AT,
            )
            filed += 1
    print(f"filed {filed} licence facts for {len(prepared)} models")
    return payload


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--root", type=Path, required=True, help="modelspec-data checkout")
    parser.add_argument("--dry-run", action="store_true",
                        help="Fetch and check clauses, then write nothing")
    parser.add_argument("--report", type=Path, default=None,
                        help="Write the reading table as JSON")
    args = parser.parse_args(argv)
    collect(args.root, dry_run=args.dry_run, report_path=args.report)


if __name__ == "__main__":
    main()
