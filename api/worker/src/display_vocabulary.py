"""Names and definitions for drawing /decide, without catalogue statistics."""
from __future__ import annotations

import json
import re
from collections import Counter
from copy import deepcopy
from functools import cache
from pathlib import Path

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
# the first 8 tokens, each cut to 32 characters, and at most this many Levenshtein cells.
SUGGESTION_TOKENS = 8
SUGGESTION_NEEDLE_CHARS = 32
SUGGESTION_CELLS = 300_000
_KINDS = ("id", "label", "definition", "value")
_STOPWORDS = frozenset({"use", "for", "the", "a", "and", "of", "with", "on", "in", "to"})


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
    if section != "models" and row.get("display_name") is not None:
        fields.append(("label", row["display_name"], None))
    for key in ("aliases", "synonyms"):
        raw = row.get(key)
        items = [raw] if isinstance(raw, str) else raw if isinstance(raw, list) else []
        fields.extend(("label", item, None) for item in items if isinstance(item, str))
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


def _synonym_file():
    here = Path(__file__).resolve().parent
    sibling = here / "pipeline" / "vocab_synonyms.json"
    if sibling.is_file():
        return sibling
    repo = here.parents[2] / "pipeline" / "vocab_synonyms.json"
    if repo.is_file():
        return repo
    raise FileNotFoundError("pipeline/vocab_synonyms.json")


@cache
def _synonym_table():
    data = json.loads(_synonym_file().read_text(encoding="utf-8"))
    spelling = {}
    for canonical, variant in data.get("spelling", []):
        spelling[normalize(variant)] = normalize(canonical)
    phrases = []
    for row in data.get("synonyms", []):
        ids = tuple(row.get("ids", []))
        for phrase in row.get("phrases", []):
            tokens = tuple(normalize(phrase).split())
            if tokens and ids:
                phrases.append((tokens, ids))
    return spelling, tuple(phrases)


def _fold_token(token):
    return _synonym_table()[0].get(token, token)


def _fold(text):
    return " ".join(_fold_token(token) for token in normalize(text).split())


def _fold_fields(fields):
    return [(kind, _fold(text), value) for kind, text, value in fields]


def _match_folded(folded, needle):
    folded_needle = _fold(needle)
    tokens = folded_needle.split()
    if not tokens:
        return None
    prior = []
    for kind in _KINDS:
        current = [(text, value) for category, text, value in folded if category == kind]
        for text, value in current:
            if text and folded_needle in text:
                return kind, value
        combined = prior + [text for text, _ in current]
        if current and all(any(token in text for text in combined) for token in tokens):
            value = next((value for text, value in current if any(token in text for token in tokens)), None)
            return kind, value
        prior = combined
    return None


def _content_tokens(needle):
    raw = tuple(needle.split()) if needle else ()
    content = tuple(token for token in raw if token not in _STOPWORDS and len(token) >= 2)
    return raw, content


def _phrase_cover(raw, content):
    cover, whole = {}, set()
    content = set(content)
    for phrase, ids in _synonym_table()[1]:
        size = len(phrase)
        if not size or size > len(raw):
            continue
        for start in range(len(raw) - size + 1):
            if tuple(raw[start:start + size]) != phrase:
                continue
            hit = [token for token in phrase if token in content]
            for key in ids:
                cover.setdefault(key, set()).update(hit)
            if size == len(raw):
                whole.update(ids)
    return cover, whole


def _token_quality(folded, token, synonym):
    if synonym:
        return 0
    needle = _fold_token(token)
    partial = False
    for _, text, _ in folded:
        if not needle or not text:
            continue
        if needle in text.split():
            return 1
        partial = partial or needle in text
    return 2 if partial else 9


def _best_kind(found):
    kind = min((item[1] for item in found), key=_KINDS.index)
    value = next((item[2] for item in found if item[1] == kind), None) if kind == "value" else None
    return kind, value


def _classify(folded, key, raw, content, cover, whole, exact):
    """Return a hit, or None. total counts subset and synonym hits; only a true miss is zero."""
    text_all = _match_folded(folded, " ".join(raw)) if raw else None
    synonym_tokens = cover.get(key, set())
    text_found = []
    for token in content:
        found = _match_folded(folded, token)
        if found:
            text_found.append((token, found[0], found[1]))
    text_tokens = {token for token, _, _ in text_found}
    matched = tuple(token for token in content if token in text_tokens or token in synonym_tokens)
    synonym_full = bool(content) and set(content) <= synonym_tokens
    whole_query = key in whole

    def via(tokens):
        return "synonym" if any(token not in text_tokens for token in tokens) else None

    if exact:
        if text_all:
            kind, value = text_all
            if kind != "value":
                value = None
        elif text_found:
            kind, value = _best_kind(text_found)
        elif matched or whole_query or synonym_full:
            kind, value = "label", None
        else:
            return None
        return {"tier": 0, "kind": kind, "value": value, "via": None, "matched_tokens": (), "quality": {}}
    if text_all:
        kind, value = text_all
        if kind != "value":
            value = None
        return {"tier": 1, "kind": kind, "value": value, "via": None, "matched_tokens": (), "quality": {}}
    if whole_query or synonym_full:
        kind, value = _best_kind(text_found) if text_found else ("label", None)
        return {"tier": 1, "kind": kind, "value": value, "via": via(content), "matched_tokens": (), "quality": {}}
    if not matched:
        return None
    kind, value = _best_kind(text_found) if text_found else ("label", None)
    quality = {token: _token_quality(folded, token, token in synonym_tokens) for token in matched}
    return {"tier": 2, "kind": kind, "value": value, "via": via(matched),
            "matched_tokens": matched, "quality": quality}


def query_hits(key, fields, search):
    """True when the hosted search would return this id for `search`."""
    needle = normalize(search)
    if not needle:
        return False
    raw, content = _content_tokens(needle)
    cover, whole = _phrase_cover(raw, content)
    return _classify(_fold_fields(fields), str(key), raw, content, cover, whole, False) is not None


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


def _suggestion_tokens(needles):
    tokens = []
    for needle in needles:
        for token in normalize(needle).split():
            if not token:
                continue
            tokens.append(token[:SUGGESTION_NEEDLE_CHARS])
            if len(tokens) >= SUGGESTION_TOKENS:
                return tokens
    return tokens


def _folded_haystacks(text, labels):
    # An ordered dedupe keeps the budget's stopping point the same on every run.
    raw = dict.fromkeys([normalize(text), normalize(re.split(r"[._]", str(text))[-1]),
                         *normalize(text).split(), *(normalize(label) for label in labels)])
    folded, seen = [], set()
    for item in raw:
        hay = _fold(item)
        if hay not in seen:
            seen.add(hay)
            folded.append(hay)
    return folded


def _score_suggestions(candidates, tokens, cover, cells, *, length_filter, ids_only):
    scored, calls, stopped = [], 0, False
    for (section, key, name), (text, labels, value) in candidates.items():
        if stopped:
            break
        if ids_only and name is not None:
            continue
        haystacks = _folded_haystacks(text, labels)
        synonym_tokens = cover.get(str(key), ()) if name is None else ()
        score = 0.0
        for token in tokens:
            if token in synonym_tokens:
                score += 1.0
                continue
            folded_token = _fold(token)
            best = 0.0
            for hay in haystacks:
                # Levenshtein similarity is at most min/max length, so skip pairs that cannot reach 0.4.
                if not folded_token or not hay or (
                        length_filter and min(len(folded_token), len(hay)) < 0.4 * max(len(folded_token), len(hay))):
                    continue
                cost = len(folded_token) * len(hay)
                if cells[0] + cost > SUGGESTION_CELLS:
                    stopped = True
                    break
                cells[0] += cost
                calls += 1
                best = max(best, similarity(folded_token, hay))
            score += best
            if stopped:
                break
        if score > 0:
            scored.append((score, section, key, name, value))
    return scored, calls


def suggestions(vocabulary, needles):
    """A value suggestion names its facet id, so retrying with id= cannot dead-end.

    Scores each of the first 8 tokens. Synonym ids score 1. Keeps scores of at
    least 0.4, or the best score above zero when nothing reaches 0.4. A query
    of only separators has no tokens and suggests nothing.
    """
    tokens = _suggestion_tokens(needles)
    if not tokens:
        return []
    candidates = {}
    for section in SEARCH_SECTIONS:
        for key, row, _ in section_rows(vocabulary, section):
            fields = searchable_fields(section, key, row)
            labels = [text for kind, text, _ in fields if kind == "label"]
            candidates[(section, str(key), None)] = (str(key), labels, None)
            for kind, text, value in fields:
                if kind != "value":
                    continue
                name = json.dumps(value, ensure_ascii=False) if isinstance(value, bool) else str(value)
                candidates.setdefault((section, str(key), name), (name, [], value))[1].append(text)
    cover, _ = _phrase_cover(tuple(tokens), tokens)
    cells = [0]
    scored, calls = _score_suggestions(candidates, tokens, cover, cells, length_filter=True, ids_only=False)
    if not scored and calls == 0 and cells[0] < SUGGESTION_CELLS:
        scored, _ = _score_suggestions(candidates, tokens, cover, cells, length_filter=False, ids_only=True)
    strong = [item for item in scored if item[0] >= 0.4]
    pool = strong if strong else scored
    pool.sort(key=lambda item: (-item[0], SEARCH_SECTIONS.index(item[1]), item[2], item[3] or ""))
    return [{"section": section, "id": key, **({"value": value} if name is not None else {})}
            for _, section, key, name, value in pool[:5]]


def select_rows(rows, section, full):
    if section == "estate":
        return {group: [row if full else compact(row, section) for _, row, own_group in rows if own_group == group]
                for group in ("providers", "devices", "plans")}
    selected = [(key, row if full else compact(row, section)) for key, row, _ in rows]
    if section in {"providers", "vendors", "models", "coverage"}:
        return dict(selected)
    return [row for _, row in selected]


def _rank_hits(hits, content, searched):
    exact = [hit for hit in hits if hit["tier"] == 0]
    full = [hit for hit in hits if hit["tier"] == 1]
    subset = [hit for hit in hits if hit["tier"] == 2]
    exact.sort(key=lambda hit: (searched.index(hit["entry"]["section"]), hit["source"]))
    full.sort(key=lambda hit: (_KINDS.index(hit["kind"]), searched.index(hit["entry"]["section"]), hit["source"]))
    buckets = []
    for token in content:
        group = [hit for hit in subset if token in hit["matched_tokens"]]
        group.sort(key=lambda hit: (hit["quality"].get(token, 9), -len(hit["matched_tokens"]),
                                    _KINDS.index(hit["kind"]), searched.index(hit["entry"]["section"]), hit["source"]))
        buckets.append(group)
    interleaved, seen = [], set()
    while True:
        moved = False
        for group in buckets:
            while group and group[0]["source"] in seen:
                del group[0]
            if group:
                hit = group.pop(0)
                seen.add(hit["source"])
                interleaved.append(hit)
                moved = True
        if not moved:
            break
    return exact + full + interleaved


def search_vocabulary(vocabulary, *, section, search, ids, full, offset, limit):
    """Search ids, labels, definitions, values and synonyms.

    Every query token matching is the first tier. Otherwise a content token can
    match; stopwords and one-character tokens count only toward the all-token
    tier. Subset hits interleave so each content token's best hit leads. total
    counts both tiers, including synonym hits, and is zero only when nothing
    matched. A synonym hit keeps matched as label and sets via to "synonym".
    A subset hit adds matched_tokens. Suggestions are returned only on a miss.
    """
    cross_section = section == "starter"
    searched = list(SEARCH_SECTIONS) if cross_section else [section]
    needle = normalize(search)
    raw, content = _content_tokens(needle)
    cover, whole = _phrase_cover(raw, content) if needle else ({}, set())
    hits = []
    exact_ids: set[str] = set()
    for name in searched:
        for key, row, group in section_rows(vocabulary, name):
            if ids and key in ids:
                exact_ids.add(key)
            if ids and key not in ids:
                continue
            # A search of only separators normalises to nothing: it matches nothing, not everything.
            if needle:
                classified = _classify(_fold_fields(searchable_fields(name, key, row)), key, raw, content,
                                       cover, whole, key in ids or key == search)
            elif search:
                classified = None
            else:
                classified = {"tier": 0, "kind": "id", "value": None, "via": None, "matched_tokens": (), "quality": {}}
            if classified is None:
                continue
            kind = classified["kind"]
            label = (row.get("label", row.get("name", row.get("display_name"))) if isinstance(row, dict)
                     else row if name in {"providers", "vendors"} else None)
            entry = {"section": name, "id": key, "matched": kind}
            if label is not None:
                entry["label"] = label
            if kind == "value":
                entry["value"] = classified["value"]
            if classified["via"]:
                entry["via"] = classified["via"]
            if classified["matched_tokens"]:
                entry["matched_tokens"] = list(classified["matched_tokens"])
            hits.append({"entry": entry, "row": (key, row, group), "tier": classified["tier"], "kind": kind,
                         "matched_tokens": classified["matched_tokens"], "quality": classified["quality"],
                         "source": len(hits)})
    ranked = _rank_hits(hits, content, searched)
    page = ranked[offset:offset + limit]
    if cross_section:
        result = {name: select_rows([hit["row"] for hit in page if hit["entry"]["section"] == name], name, full)
                  for name in searched}
        starters = set(starter_ids(vocabulary))
        result.update(vocabulary_response([row for row in result["facets"] if row["id"] in starters], "starter"))
    else:
        rows = [hit["row"] for hit in hits]
        result = vocabulary_response(select_rows(rows if full else rows[offset:offset + limit], section, full), section)
    result.update(matches=[hit["entry"] for hit in page], total=len(hits), searched=searched)
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
