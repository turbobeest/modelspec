"""Publish the class-fit rule as static data (MODEL-100).

`/api/rank/class-fit.json`, beside `profiles.json`, on Cloudflare Pages: no
key, no account, no request to us. It carries the whole rule — the axis, the
derivation, every class with its facets and its terms, the refusal codes, what
the matcher cannot do, and the neutrality commitment — so a caller can run the
same match locally against a static asset.

That is a stronger form of publication than an endpoint that documents its
behaviour, and it is why `POST /v1/class-fit` is deferred rather than built:
the answer costs a few thousand string comparisons over a 15 KB file, so
paying Worker CPU for it (MODEL-3: 121 ms measured, 288.78 ms median, with the
included CPU exhausted long before the included requests) would buy only the
HTTP verb.

**This module is where the taxonomy meets the catalogue, and it is deliberately
not `pipeline/ranking.py`.** The scorer must not import `api.classes` or
`api.class_fit` in either direction — cost-to-correct (MODEL-99) is fitness
evidence for a task, `rank_score` is a within-class quality composite, and a
test enforces the separation by walking the import statements of both files.

Additive: a new file, no field widened, so `build.export_schema_version` stays
`3.0` under the MODEL-59 rule.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from api import class_fit, classes as cls

#: Example model ids published per class. Sorted and capped, so no ordering in
#: the file can be read as a recommendation.
MAX_EXAMPLES = class_fit.MAX_EXAMPLES


def _fold(by_model_type: Mapping[str, Any], reduce_lists: bool = False) -> dict[str, Any]:
    """Re-key a `model_type` map onto class ids, including the non-classes."""
    folded: dict[str, Any] = {}
    for value, payload in by_model_type.items():
        key = cls.MODEL_TYPE_PLACEMENT.get(value)
        if key is None:
            continue
        if reduce_lists:
            folded.setdefault(key, []).extend(payload or ())
        else:
            folded[key] = folded.get(key, 0) + int(payload or 0)
    return folded


def class_fit_export(build_json: dict[str, Any], *,
                     model_type_counts: Mapping[str, int],
                     examples_by_model_type: Mapping[str, Sequence[str]] | None = None,
                     ) -> dict[str, Any]:
    """The published rule, with the catalogue's own counts folded onto it.

    A class absent from `model_type_counts` reports `card_count: 0` and
    `evidence_state: "empty"`, because at build time the catalogue is fully
    known: nobody has to go and look, so `unknown` would be the wrong word.
    That is the opposite call from `class_fit()`'s, where evidence genuinely
    may not have been supplied, and the two are different for the reason
    MODEL-97 spent a commit on.
    """
    counts = _fold(model_type_counts)
    examples = _fold(examples_by_model_type or {}, reduce_lists=True)

    rows: list[dict[str, Any]] = []
    for model_class in cls.CLASSES:
        count = counts.get(model_class.id, 0)
        rows.append({
            "id": model_class.id,
            "is_class": True,
            "consumes": list(model_class.consumes),
            "emits": model_class.emits,
            "decides": model_class.decides,
            "abstains": model_class.abstains,
            "because": model_class.because,
            "terms": list(model_class.terms),
            "model_types": list(model_class.model_types),
            "domains": dict(model_class.domains),
            "rank_profiles": cls.rank_profiles_for(model_class.id),
            "catalogue": {
                "card_count": count,
                "example_model_ids": sorted(examples.get(model_class.id, ()))[:MAX_EXAMPLES],
                "evidence_state": "populated" if count else "empty",
            },
        })

    for non_class, values in cls.NON_CLASSES.items():
        count = counts.get(non_class, 0)
        rows.append({
            "id": non_class,
            "is_class": False,
            "because": cls.NON_CLASS_RESOLUTION[non_class],
            "model_types": list(values),
            "catalogue": {
                "card_count": count,
                "example_model_ids": sorted(examples.get(non_class, ()))[:MAX_EXAMPLES],
                "evidence_state": "populated" if count else "empty",
            },
        })

    rows.sort(key=lambda row: row["id"])
    return {
        "build": build_json,
        "policy": cls.class_fit_policy(),
        "vocabulary": cls.vocabulary(),
        "classes": rows,
        "distinguishing_questions": [
            question.to_json() for question in cls.DISTINGUISHING_QUESTIONS
        ],
    }


def counts_from_cards(cards: Sequence[Any]) -> tuple[dict[str, int], dict[str, list[str]]]:
    """`model_type` counts and a few example ids, read off the cards."""
    counts: dict[str, int] = {}
    examples: dict[str, list[str]] = {}
    for card in cards:
        identity = getattr(card, "identity", None)
        model_type = getattr(identity, "model_type", None) if identity is not None else None
        value = getattr(model_type, "value", model_type)
        if not value:
            continue
        counts[value] = counts.get(value, 0) + 1
        model_id = getattr(identity, "model_id", None)
        if model_id and len(examples.setdefault(value, [])) < MAX_EXAMPLES * 4:
            examples[value].append(str(model_id))
    return counts, examples


def counts_from_snapshot_candidates(
    candidates: Sequence[Mapping[str, Any]],
) -> tuple[dict[str, int], dict[str, list[str]]]:
    """Class-keyed counts and examples from a snapshot's `candidates.json`.

    Every class is seeded at zero on purpose. Offline, the whole catalogue is
    in hand, so a class with no cards is `empty` — somebody has looked and
    there is nothing there — rather than `unknown`. Seeding is what makes that
    distinction true rather than accidental.
    """
    counts: dict[str, int] = {model_class.id: 0 for model_class in cls.CLASSES}
    counts.update({non_class: 0 for non_class in cls.NON_CLASSES})
    examples: dict[str, list[str]] = {}
    for row in candidates:
        key = cls.MODEL_TYPE_PLACEMENT.get(row.get("model_type") or "")
        if key is None:
            continue
        counts[key] = counts.get(key, 0) + 1
        model_id = row.get("model_id")
        if model_id and len(examples.setdefault(key, [])) < MAX_EXAMPLES * 4:
            examples[key].append(str(model_id))
    return counts, examples


def write_export(out_dir: Any, cards: Sequence[Any],
                 build_json: dict[str, Any]) -> dict[str, Any]:
    """Write `class-fit.json` beside `profiles.json`. Returns a small summary."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    counts, examples = counts_from_cards(cards)
    payload = class_fit_export(build_json, model_type_counts=counts,
                               examples_by_model_type=examples)
    (out / "class-fit.json").write_text(
        json.dumps(payload, sort_keys=True, default=str), encoding="utf-8")
    return {
        "classes": len(cls.CLASSES),
        "non_classes": len(cls.NON_CLASSES),
        "placed_model_types": len(cls.MODEL_TYPE_PLACEMENT),
    }
