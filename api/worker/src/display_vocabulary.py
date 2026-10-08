"""Names and definitions for drawing /decide, without catalogue statistics."""
from __future__ import annotations

import json
import re
from collections import Counter
from copy import deepcopy

try:
    from agent_guide import MINIMAL_SPEC, VOCAB_NEXT
except ImportError:
    from .agent_guide import MINIMAL_SPEC, VOCAB_NEXT

SECTIONS = ("starter", "facets", "benchmarks", "domains", "providers", "models",
            "task_types", "coverage", "templates", "refinements", "estate", "vendors",
            "template_categories", "template_tiers")
PAGE_SIZE = 20
SEARCH_SECTIONS = ("facets", "domains", "refinements", "benchmarks", "templates", "task_types",
                   "estate", "providers", "vendors", "models", "template_categories", "template_tiers")

FACET_FIELDS = ("id", "label", "definition", "subject", "value_type", "unit", "unit_definition",
                "operators", "objective", "preference", "better", "risk", "computed_by", "literals")
BENCHMARK_FIELDS = ("id", "name", "unit", "higher_is_better", "domains")
DOMAIN_FIELDS = ("id", "name", "proxy_only", "default_basis", "default_benchmark", "benchmarks")
TEMPLATE_FIELDS = ("id", "category", "tier", "tradeoff", "canvas", "name", "purpose", "where",
                   "weights", "task_tokens", "needs", "teaches", "spec", "available")


def pick(row, fields):
    return {key: row[key] for key in fields if key in row}


def trim(vocabulary, *, model_ids, facet_values):
    """Project explicit display fields. Only approved aggregates cross this boundary."""
    result = pick(vocabulary, ("vocabulary_version", "contract_version", "snapshot", "default_task_tokens",
                               "task_types", "providers", "vendors", "template_categories", "template_tiers"))
    result["facets"] = [pick(row, FACET_FIELDS) for row in vocabulary.get("facets", [])]
    for row, source in zip(result["facets"], vocabulary.get("facets", [])):
        row["has_data"] = source.get("known", 0) > 0
        observed = {item["value"]: item for item in source.get("values", [])}
        values = facet_values.get(row["id"], list(observed)) if source.get("value_type") in {"enum", "boolean", "set", "string"} else []
        if values:
            row["values"] = [dict(pick(observed.get(value, {"value": value}), ("value", "label")),
                                  has_data=observed.get(value, {}).get("count", 0) > 0)
                             for value in values]
    result["benchmarks"] = [pick(row, BENCHMARK_FIELDS + (("range",) if row.get("models", 0) >= 3 else ()))
                            for row in vocabulary.get("benchmarks", [])]
    result["refinements"] = [dict(pick(row, ("id", "name", "parent_domain", "kind", "definition", "benchmarks", "weight_key")),
                                  thin=row.get("evidence_state") == "thin")
                             for row in vocabulary.get("refinements", [])]
    result["domains"] = [pick(row, DOMAIN_FIELDS) for row in vocabulary.get("domains", [])]
    result["models"] = {mid: {"display_name": row.get("display_name")} for mid, row in
                        vocabulary.get("models", {}).items() if mid in model_ids}
    estate = vocabulary.get("estate", {})
    result["estate"] = {"providers": estate.get("providers", []), "devices": estate.get("devices", []),
                        "plans": [pick(row, ("id", "provider", "name")) for row in estate.get("plans", [])]}
    result["templates"] = [pick(row, TEMPLATE_FIELDS) for row in vocabulary.get("templates", [])]
    return result


MAX_IDS = 100
MAX_TERM = 128
# The suggestion pass is reachable without a key, so its work has a hard ceiling:
# two needles of at most 32 characters, and at most this many Levenshtein cells.
SUGGESTION_NEEDLES = 2
SUGGESTION_NEEDLE_CHARS = 32
SUGGESTION_CELLS = 300_000


def vocabulary_response(selected, section):
    result = {section: selected, "next": VOCAB_NEXT["starter" if section == "starter" else "lookup"]}
    if section == "starter":
        result["spec"] = deepcopy(MINIMAL_SPEC)
    return result


def starter_ids(vocabulary):
    """Count each registered facet once per template spec; break ties by ID."""
    counts = Counter()
    for template in vocabulary.get("templates", []):
        spec = json.dumps(template.get("spec") or {})
        counts.update(row["id"] for row in vocabulary.get("facets", [])
                      if re.search(r"(?<![\w.])" + re.escape(row["id"]) + r"(?![\w.])", spec))
    return sorted(counts, key=lambda fid: (-counts[fid], fid))[:15]


def compact(row, section):
    if section in {"facets", "starter"}:
        result = pick(row, ("id", "label", "definition", "value_type", "better", "literals"))
        if isinstance(result.get("definition"), str):
            result["definition"] = re.split(r"\.\s", " ".join(result["definition"].split()))[0].rstrip(".") + "."
        if "allowed_values" in row:
            result["allowed_values"] = row["allowed_values"]
        elif "values" in row:
            result["allowed_values"] = [value["value"] for value in row["values"]]
        return result
    if section == "models":
        return pick(row, ("display_name",))
    if isinstance(row, dict):
        return pick(row, ("id", "name", "label"))
    return row


def normalize(value):
    return re.sub(r"[_\-./\s]+", " ", str(value).lower()).strip()


def section_rows(vocabulary, section):
    source = vocabulary.get(section, {})
    if section == "estate":
        for group in ("providers", "devices", "plans"):
            for row in source.get(group, []):
                yield row["id"] if isinstance(row, dict) else row, row, group
    elif isinstance(source, dict):
        for key, row in source.items():
            yield key, row, None
    else:
        for row in source:
            yield row.get("id", "") if isinstance(row, dict) else row, row, None


def searchable_fields(section, key, row):
    """Ordered match categories; nested benchmark domains are deliberately excluded."""
    fields = [("id", key, None)]
    if section in {"providers", "vendors"}:
        fields.append(("label", row, None))
    if not isinstance(row, dict):
        return fields
    labels = ("label",) if section == "facets" else (("display_name",) if section == "models" else ("name",))
    fields.extend(("label", row[label], None) for label in labels if row.get(label) is not None)
    if section == "estate" and row.get("provider") is not None:
        fields.append(("label", row["provider"], None))
    definitions = ("purpose", "category", "tier") if section == "templates" else (
        ("definition",) if section in {"facets", "refinements"} else ())
    fields.extend(("definition", row[field], None) for field in definitions if row.get(field) is not None)
    if section == "facets":
        for value in row.get("values", []):
            fields.append(("value", value["value"], value["value"]))
            if value.get("label") is not None:
                fields.append(("value", value["label"], value["value"]))
        fields.extend(("value", value, value) for value in row.get("allowed_values", []))
    return fields


def match_fields(fields, needle):
    tokens = needle.split()
    prior = []
    for kind in ("id", "label", "definition", "value"):
        current = [(normalize(text), value) for category, text, value in fields if category == kind]
        for text, value in current:
            if needle in text:
                return kind, value
        combined = prior + [text for text, _ in current]
        if current and all(any(token in text for text in combined) for token in tokens):
            value = next((value for text, value in current if any(token in text for token in tokens)), None)
            return kind, value
        prior = combined
    return None


def similarity(left, right):
    if not left or not right:
        return 0
    previous = list(range(len(right) + 1))
    for i, a in enumerate(left, 1):
        current = [i]
        for j, b in enumerate(right, 1):
            current.append(min(current[-1] + 1, previous[j] + 1, previous[j - 1] + (a != b)))
        previous = current
    return 1 - previous[-1] / max(len(left), len(right))


def suggestions(vocabulary, needles):
    """A value suggestion names its facet id, so retrying with id= cannot dead-end."""
    candidates = {}
    for section in SEARCH_SECTIONS:
        for key, row, _ in section_rows(vocabulary, section):
            fields = searchable_fields(section, key, row)
            candidates[(section, str(key), None)] = (str(key), [text for kind, text, _ in fields if kind == "label"], None)
            for kind, text, value in fields:
                if kind == "value":
                    name = json.dumps(value, ensure_ascii=False) if isinstance(value, bool) else str(value)
                    candidates.setdefault((section, str(key), name), (name, [], value))[1].append(text)
    needles = [normalize(needle)[:SUGGESTION_NEEDLE_CHARS] for needle in needles[:SUGGESTION_NEEDLES]]
    scored, cells = [], 0
    for (section, key, name), (text, labels, value) in candidates.items():
        # Token scores let a typo like "pirce" suggest offering.price.input.
        # An ordered dedupe keeps the budget's stopping point the same on every run.
        haystacks = dict.fromkeys([normalize(text), normalize(re.split(r"[._]", text)[-1]),
                                   *normalize(text).split(), *(normalize(label) for label in labels)])
        score = 0
        for needle in needles:
            for hay in haystacks:
                # Levenshtein similarity is at most min/max length, so skip pairs that cannot reach 0.4.
                if not needle or not hay or min(len(needle), len(hay)) < 0.4 * max(len(needle), len(hay)):
                    continue
                cells += len(needle) * len(hay)
                if cells > SUGGESTION_CELLS:
                    break
                score = max(score, similarity(needle, hay))
        if score >= 0.4:
            scored.append((score, section, key, name, value))
        if cells > SUGGESTION_CELLS:
            break
    scored.sort(key=lambda item: (-item[0], SEARCH_SECTIONS.index(item[1]), item[2], item[3] or ""))
    return [{"section": section, "id": key, **({"value": value} if name is not None else {})}
            for _, section, key, name, value in scored[:5]]


def select_rows(rows, section, full):
    if section == "estate":
        return {group: [row if full else compact(row, section) for _, row, own_group in rows if own_group == group]
                for group in ("providers", "devices", "plans")}
    selected = [(key, row if full else compact(row, section)) for key, row, _ in rows]
    if section in {"providers", "vendors", "models", "coverage"}:
        return dict(selected)
    return [row for _, row in selected]


def search_vocabulary(vocabulary, *, section, search, ids, full, offset, limit):
    cross_section = section == "starter"
    searched = list(SEARCH_SECTIONS) if cross_section else [section]
    needle = normalize(search)
    hits = []
    exact_ids: set[str] = set()
    for name in searched:
        for key, row, group in section_rows(vocabulary, name):
            if ids and key in ids:
                exact_ids.add(key)
            if ids and key not in ids:
                continue
            # A search of only separators normalises to nothing: it matches nothing, not everything.
            match = (match_fields(searchable_fields(name, key, row), needle) if needle
                     else None if search else ("id", None))
            if match is None:
                continue
            kind, value = match
            rank = 0 if key in ids or key == search else ("id", "label", "definition", "value").index(kind) + 1
            label = (row.get("label", row.get("name", row.get("display_name"))) if isinstance(row, dict)
                     else row if name in {"providers", "vendors"} else None)
            entry = {"section": name, "id": key, "matched": kind}
            if label is not None:
                entry["label"] = label
            if kind == "value":
                entry["value"] = value
            hits.append((rank, entry, (key, row, group)))
    # Stable sort preserves source order within each section and match category.
    ranked = sorted(hits, key=lambda hit: (hit[0], searched.index(hit[1]["section"])))
    page = ranked[offset:offset + limit]
    if cross_section:
        result = {name: select_rows([row for _, entry, row in page if entry["section"] == name], name, full)
                  for name in searched}
        starters = set(starter_ids(vocabulary))
        result.update(vocabulary_response([row for row in result["facets"] if row["id"] in starters], "starter"))
    else:
        rows = [row for _, _, row in hits]
        result = vocabulary_response(select_rows(rows if full else rows[offset:offset + limit], section, full), section)
    result.update(matches=[entry for _, entry, _ in page], total=len(hits), searched=searched)
    result["next"] = VOCAB_NEXT["lookup" if hits else "empty"]
    if not hits:
        closest = suggestions(vocabulary, [search] if search else sorted(ids))
        quoted = json.dumps(search if search else ", ".join(sorted(ids)), ensure_ascii=False)
        names = ", ".join(item["id"] + (f" (value {json.dumps(item['value']) if isinstance(item['value'], bool) else item['value']})"
                                        if "value" in item else "")
                          for item in closest) or "none"
        result.update(suggestions=closest, message=f"No vocabulary entry matches {quoted} in the id, label, definition or values of {', '.join(searched)}; closest ids: {names}.")
    if ids:
        missing = sorted(set(ids) - exact_ids)
        if missing:
            result["unknown_ids"] = missing
    return result


def lookup(vocabulary, *, section="starter", search="", ids=(), detail="compact",
           offset=0, limit=PAGE_SIZE):
    """An opt-in lookup. Full detail stays inside the existing display boundary."""
    if section not in SECTIONS:
        raise ValueError("unknown vocabulary section")
    if detail not in {"compact", "full"}:
        raise ValueError("detail must be compact or full")
    if offset < 0 or not 1 <= limit <= PAGE_SIZE:
        raise ValueError("offset must be nonnegative; limit must be between 1 and 20")
    ids = set(ids)
    if len(ids) > MAX_IDS:
        raise ValueError(f"at most {MAX_IDS} ids per lookup")
    if len(search) > MAX_TERM or any(len(item) > MAX_TERM for item in ids):
        raise ValueError(f"search and each id are at most {MAX_TERM} characters")
    if search or ids:
        return search_vocabulary(vocabulary, section=section, search=search, ids=ids,
                                 full=detail == "full" or bool(ids), offset=offset, limit=limit)
    source = vocabulary.get(section, {} if section in {"models", "providers", "vendors", "coverage", "estate"} else [])
    if section == "coverage" and detail == "compact" and not ids:
        return vocabulary_response({}, section)
    if section == "estate" and detail == "compact" and not ids:
        source = {key: vocabulary.get("estate", {}).get(key, []) for key in ("providers", "devices")}
    if section == "starter":
        by_id = {row["id"]: row for row in vocabulary.get("facets", [])}
        source = [by_id[fid] for fid in starter_ids(vocabulary)]
    mapping = isinstance(source, dict)
    if mapping:
        rows = [(key, value) for key, value in source.items()]
    else:
        rows = [(row.get("id", "") if isinstance(row, dict) else row, row) for row in source]

    full = detail == "full" or bool(ids)
    if not full:
        rows = rows[offset:offset + limit]

    selected = [(key, row if full else compact(row, section)) for key, row in rows]
    return vocabulary_response(dict(selected) if mapping else [row for _, row in selected], section)
