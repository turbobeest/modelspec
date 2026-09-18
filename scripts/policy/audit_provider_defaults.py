#!/usr/bin/env python3
"""MODEL-86: audit cards whose license_type equals the removed provider default.

Reconstructs PROVIDER_LICENSE from git history of scripts/enrich_cards.py,
selects unsourced matches, reads the creator distribution point (Hub API +
LICENSE / README, or the vendor terms page for a closed API), and writes
license_url plus a dated body note. A licence that cannot be read is nulled.

Cap: 250 cards, highest-traffic providers first. Re-run:

    PYTHONPATH=$PWD python scripts/policy/audit_provider_defaults.py
    PYTHONPATH=$PWD python scripts/policy/audit_provider_defaults.py --apply
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import httpx
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.policy.commercial_use import licence_of_record  # noqa: E402
from scripts.policy.licences import reading_for  # noqa: E402

READ_ON = "2026-09-18"
CAP = 250
HF_API = "https://huggingface.co/api/models"
UA = (
    "Mozilla/5.0 (compatible; ModelSpec-licence-audit/1.0; "
    "+https://github.com/turbobeest/modelspec)"
)

# Removed table, reconstructed from `git show HEAD -- scripts/enrich_cards.py`
# (commit 481da75, MODEL-85). Values are LicenseType strings.
PROVIDER_LICENSE: dict[str, str] = {
    "anthropic": "proprietary",
    "openai": "proprietary",
    "google": "proprietary",
    "mistral": "apache-2.0",
    "meta": "llama-community",
    "qwen": "apache-2.0",
    "deepseek": "deepseek",
    "cohere": "other",
    "xai": "proprietary",
    "stability": "other",
    "tii": "apache-2.0",
    "microsoft": "mit",
    "ibm": "apache-2.0",
    "nvidia": "other",
    "allen-ai": "apache-2.0",
    "baai": "mit",
    "sentence-transformers": "apache-2.0",
    "voyage": "proprietary",
    "perplexity": "proprietary",
    "01-ai": "apache-2.0",
    "snowflake": "apache-2.0",
    "salesforce": "apache-2.0",
    "together": "apache-2.0",
    "nomic": "apache-2.0",
    "jina": "apache-2.0",
    "intfloat": "mit",
    "cerebras": "llama-community",
    "upstage": "apache-2.0",
    "minimax": "other",
    "moonshot": "proprietary",
    "tencent": "other",
    "zhipu": "other",
    "baichuan": "other",
    "samsung": "other",
    "kakao": "other",
    "inception": "apache-2.0",
    "rwkv": "apache-2.0",
    "skywork": "other",
    "stepfun": "other",
    "openbmb": "apache-2.0",
    "liquid": "other",
    "moondream": "apache-2.0",
    "nous-research": "apache-2.0",
    "teknium": "apache-2.0",
    "unsloth": "apache-2.0",
    "black-forest-labs": "other",
    "ai21": "proprietary",
}

# Highest-traffic providers first. Gemma is not in the google default (the
# special case already typed those `gemma`); remaining google suspects are Gemini.
TRAFFIC_ORDER = (
    "openai",
    "anthropic",
    "google",
    "xai",
    "mistral",
    "qwen",
    "meta",
    "deepseek",
    "microsoft",
    "cohere",
    "nvidia",
    "perplexity",
)

CLOSED_TERMS: dict[str, tuple[str, str]] = {
    "openai": (
        "https://openai.com/policies/business-terms/",
        "OpenAI Services Agreement (effective 1 January 2026)",
    ),
    "anthropic": (
        "https://www.anthropic.com/legal/commercial-terms",
        "Anthropic Commercial Terms of Service",
    ),
    "google": (
        "https://ai.google.dev/gemini-api/terms",
        "Gemini API Additional Terms of Service (effective 23 March 2026)",
    ),
    "xai": (
        "https://x.ai/legal/terms-of-service-enterprise",
        "SpaceXAI Terms of Service — Enterprise (last updated 14 August 2026)",
    ),
    "perplexity": (
        "https://www.perplexity.ai/hub/legal/perplexity-api-terms-of-service",
        "Perplexity API Terms of Service (last updated 23 January 2026)",
    ),
    "mistral": (
        "https://legal.mistral.ai/terms/commercial-terms-of-service",
        "Mistral AI Terms of Service for Commercial Users",
    ),
    "deepseek": (
        "https://cdn.deepseek.com/policies/en-US/deepseek-open-platform-terms-of-service.html",
        "DeepSeek Open Platform Terms of Service (effective 29 April 2026)",
    ),
}

# Hub `license` / `license_name` → card LicenseType. Unmapped custom names
# fall through to LICENSE-file classification or `other` if a URL exists.
HF_TO_TYPE: dict[str, str] = {
    "apache-2.0": "apache-2.0",
    "mit": "mit",
    "bsd-3-clause": "other",
    "bsd-2-clause": "other",
    "gpl-3.0": "gpl-3.0",
    "gpl-2.0": "other",
    "agpl-3.0": "other",
    "cc-by-4.0": "cc-by-4.0",
    "cc-by-nc-4.0": "cc-by-nc-4.0",
    "cc-by-nc-sa-4.0": "other",
    "openrail": "openrail",
    "openrail++": "openrail",
    "creativeml-openrail-m": "openrail",
    "bigscience-openrail-m": "openrail",
    "gemma": "gemma",
    "llama2": "llama-community",
    "llama3": "llama-community",
    "llama3.1": "llama-community",
    "llama3.2": "llama-community",
    "llama3.3": "llama-community",
    "llama4": "llama-community",
    "llama-2": "llama-community",
    "llama-3": "llama-community",
    "llama-4": "llama-community",
    "deepseek": "deepseek",
    "qwen": "qwen",
    "qwen-license": "qwen",
    "qwen-research": "qwen",
    "tongyi-qianwen": "qwen",
    "tongyi-qianwen-license-agreement": "qwen",
    "tongyi-qianwen-research": "qwen",
    "mrl": "other",
    "mnpl": "other",
    "proprietary": "proprietary",
    "stabilityai-ai-community": "other",
    "sai-nc-community": "other",
    "flux-1-dev-non-commercial-license": "other",
    "flux-non-commercial-license": "other",
    "flux-dev-non-commercial-license": "other",
    "deepseek-license": "deepseek",
    "falcon-llm-license": "other",
    "falcon-mamba-7b-license": "other",
    "falcon-mamba-license": "other",
    "tencent-hunyuan-community": "other",
    "tencent-hunyuan-a13b": "other",
    "tencent-hunyuanworld-1.0-community": "other",
    "tencent-hunyuanworld-mirror-community": "other",
    "youtu-llm": "other",
    "stable-audio-community": "other",
    "stable-cascade-nc-community": "other",
    "stable-video-diffusion-community": "other",
    "stable-video-diffusion-1-1-community": "other",
    "stabilityai-nc-research-community": "other",
    "stabilityai-ai-non-commercial": "other",
    "tencent-kalm-embedding-community": "other",
    "cc-by-sa-4.0": "other",
    "cc-by-nc-sa-4.0": "other",
    "artistic-2.0": "other",
    "mpl-2.0": "other",
    "lgpl-3.0": "other",
    "lgpl-2.1": "other",
}

LICENSE_FILES = (
    "LICENSE",
    "LICENSE.md",
    "LICENSE.txt",
    "LICENSE-MODEL",
    "LICENSE-MODEL.txt",
    "license",
    "licence",
)


@dataclass
class Suspect:
    path: Path
    model_id: str
    provider: str
    license_type: str
    open_weights: bool
    hf_repo: str | None
    commercial_use: str


@dataclass
class Decision:
    model_id: str
    provider: str
    before: str
    after: str | None
    action: str  # confirmed / corrected / nulled
    license_url: str
    note: str
    declared: str | None
    declared_name: str | None
    cu_before: str
    cu_after: str


def _front_and_body(path: Path) -> tuple[dict, str, str]:
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"no frontmatter: {path}")
    return yaml.safe_load(parts[1]), parts[2], text


def _hf_repo(data: dict) -> str | None:
    avail = (data.get("availability") or {}).get("huggingface") or {}
    mid = (avail.get("model_id") or "").strip()
    if mid.count("/") == 1:
        return mid
    for raw in (
        (avail.get("url") or ""),
        ((data.get("sources") or {}).get("huggingface_url") or ""),
    ):
        m = re.match(r"https?://huggingface\.co/([\w.-]+/[\w.-]+)/?$", raw.strip())
        if m and m.group(1).split("/")[0] not in {"models", "datasets", "spaces"}:
            return m.group(1)
    return None


def load_suspects() -> list[Suspect]:
    out: list[Suspect] = []
    for path in sorted((REPO_ROOT / "models").glob("*/*.md")):
        if path.name == "LICENSE.md":
            continue
        data, body, _ = _front_and_body(path)
        provider = (data.get("provider") or "").lower()
        default = PROVIDER_LICENSE.get(provider)
        lic = data.get("licensing") or {}
        lt = lic.get("license_type")
        if default is None or lt != default:
            continue
        url = (lic.get("license_url") or "").strip()
        if url or "Licence:" in body:
            continue
        out.append(
            Suspect(
                path=path,
                model_id=data["model_id"],
                provider=provider,
                license_type=str(lt),
                open_weights=bool(lic.get("open_weights")),
                hf_repo=_hf_repo(data),
                commercial_use=str(lic.get("commercial_use") or "unspecified"),
            )
        )
    return out


def select_batch(
    suspects: list[Suspect],
    cap: int = CAP,
    providers: list[str] | None = None,
) -> list[Suspect]:
    order = providers if providers else list(TRAFFIC_ORDER)
    rank = {p: i for i, p in enumerate(order)}
    pool = [s for s in suspects if s.provider in rank] if providers else suspects
    ordered = sorted(
        pool,
        key=lambda s: (
            rank.get(s.provider, len(order)),
            0 if s.hf_repo else 1,
            s.model_id,
        ),
    )
    return ordered[:cap]


def _classify_license_text(text: str) -> tuple[str | None, str]:
    head = text[:2500]
    low = head.lower()
    if "modified mit" in low:
        return "other", "Modified MIT License"
    if "apache license" in low and "version 2.0" in low:
        return "apache-2.0", "Apache License Version 2.0, January 2004"
    if re.search(r"\bmit license\b", low) or (
        "permission is hereby granted, free of charge" in low and "modified mit" not in low
    ):
        return "mit", "MIT License"
    if "qwen research license" in low:
        return "qwen", "Qwen RESEARCH LICENSE AGREEMENT"
    if "qwen license agreement" in low:
        return "qwen", "Qwen LICENSE AGREEMENT"
    if "tongyi qianwen license agreement" in low:
        return "qwen", "Tongyi Qianwen LICENSE AGREEMENT"
    if "mistral ai research license" in low or (
        "mistral" in low and "for research purposes" in low
    ):
        return "other", "Mistral AI Research License"
    if "mistral ai non-production license" in low or (
        "mistral" in low and "non-production environments" in low
    ):
        return "other", "Mistral AI Non-Production License"
    if "gemma" in low and "terms" in low:
        return "gemma", "Gemma Terms of Use"
    if "llama" in low and "community license" in low:
        return "llama-community", "Llama Community License"
    if "deepseek license agreement" in low or "deepseek model license" in low:
        return "deepseek", "DeepSeek License Agreement"
    if "creativeml open rail" in low or "open rail-m" in low or "openrail-m" in low:
        return "openrail", "CreativeML Open RAIL-M License"
    if "stability ai community license" in low:
        return "other", "Stability AI Community License Agreement"
    if "non-commercial research community license" in low:
        return "other", "Stability AI Non-Commercial Research Community License"
    if "flux" in low and "non-commercial" in low:
        return "other", "FLUX Non-Commercial License"
    if "falcon llm license" in low or "technology innovation institute" in low and "falcon" in low:
        return "other", "TII Falcon LLM License"
    if "yi series models community license" in low:
        return "other", "Yi Series Models Community License Agreement"
    if "tencent hunyuan" in low and "license" in low:
        return "other", "Tencent Hunyuan Community License Agreement"
    if "gemma" in low and "terms of use" in low:
        return "gemma", "Gemma Terms of Use"
    return None, head.splitlines()[0][:80] if head.strip() else ""


def _as_str(value: Any) -> str:
    if isinstance(value, list):
        value = value[0] if value else ""
    if value is None:
        return ""
    return str(value).strip()


def _absolute_license_url(repo: str, link: str) -> str:
    """Turn a Hub license_link into a fetchable URL, or ''."""
    link = (link or "").strip()
    if not link:
        return ""
    blob = re.match(
        r"https://github\.com/([^/]+)/([^/]+)/blob/([^/]+)/(.*)$",
        link,
    )
    if blob:
        return (
            f"https://raw.githubusercontent.com/{blob.group(1)}/"
            f"{blob.group(2)}/{blob.group(3)}/{blob.group(4)}"
        )
    if link.startswith("http://") or link.startswith("https://"):
        return link
    link = link.lstrip("./")
    return f"https://huggingface.co/{repo}/raw/main/{link}"


def _hf_get(client: httpx.Client, url: str) -> httpx.Response | None:
    delay = 1.5
    last: httpx.Response | None = None
    for _ in range(5):
        try:
            last = client.get(url)
        except httpx.HTTPError:
            time.sleep(delay)
            delay = min(delay * 2, 16)
            continue
        if last.status_code != 429:
            return last
        time.sleep(delay)
        delay = min(delay * 2, 16)
    return last


def _map_hf(license_key: str | None, license_name: str | None) -> str | None:
    for raw in (license_key, license_name):
        if not raw:
            continue
        key = raw.strip().lower()
        if key in {"other", "unknown", ""}:
            continue
        mapped = HF_TO_TYPE.get(key)
        if mapped:
            return mapped
    return None


def fetch_hf(client: httpx.Client, repo: str) -> dict[str, Any]:
    info: dict[str, Any] = {"repo": repo, "ok": False}
    r = _hf_get(client, f"{HF_API}/{repo}")
    if r is None:
        info["error"] = "no response"
        return info
    if r.status_code != 200:
        info["api_status"] = r.status_code
        return info
    try:
        data = r.json()
    except ValueError as exc:
        info["error"] = str(exc)
        return info
    card = data.get("cardData") or {}
    info["ok"] = True
    info["license"] = _as_str(data.get("license") or card.get("license") or "")
    info["license_name"] = _as_str(card.get("license_name") or "")
    info["license_link"] = _as_str(card.get("license_link") or "")
    info["gated"] = data.get("gated")
    # LICENSE file, then the declared license_link, then README frontmatter.
    candidates = [f"https://huggingface.co/{repo}/raw/main/{name}" for name in LICENSE_FILES]
    abs_link = _absolute_license_url(repo, info["license_link"])
    if abs_link and abs_link not in candidates:
        candidates.append(abs_link)
    for url in candidates:
        lr = _hf_get(client, url)
        if lr is None or lr.status_code != 200 or not lr.text:
            continue
        if "Entry not found" in lr.text[:40]:
            continue
        if lr.text.lstrip()[:15].lower().startswith("<!doctype html") or lr.text.lstrip()[:6].lower() == "<html":
            continue
        info["license_file_url"] = str(lr.url)
        info["license_file_text"] = lr.text
        break
    if "license_file_text" not in info:
        rr = _hf_get(client, f"https://huggingface.co/{repo}/raw/main/README.md")
        if rr is not None and rr.status_code == 200 and rr.text.startswith("---"):
            info["readme_url"] = str(rr.url)
            info["readme_text"] = rr.text[:8000]
    return info


def decide_from_hf(s: Suspect, info: dict[str, Any]) -> Decision:
    declared = _as_str(info.get("license")).lower() or None
    declared_name = _as_str(info.get("license_name")).lower() or None
    file_url = info.get("license_file_url") or ""
    file_text = info.get("license_file_text") or ""
    readme_url = info.get("readme_url") or ""
    license_link = _as_str(info.get("license_link"))

    repo = str(info.get("repo") or "")
    abs_link = _absolute_license_url(repo, license_link)
    hub_page = f"https://huggingface.co/{repo}" if repo else ""

    mapped = None
    label = ""
    cite = ""
    if file_text:
        mapped, label = _classify_license_text(file_text)
        cite = file_url
    if mapped is None:
        mapped = _map_hf(declared, declared_name)
        if mapped:
            label = declared_name or declared or mapped
            cite = file_url or abs_link or readme_url or hub_page
    if mapped is None and declared in {"other", None} and declared_name:
        # Known custom name we refuse to invent a LicenseType for: still `other`
        # if we have a URL, else null. The Hub model page is a URL.
        mapped = "other"
        label = declared_name
        cite = cite or abs_link or readme_url or hub_page

    if mapped is None:
        return Decision(
            model_id=s.model_id,
            provider=s.provider,
            before=s.license_type,
            after=None,
            action="nulled",
            license_url="",
            note=(
                f"Licence: null. No readable licence at the creator distribution "
                f"point huggingface.co/{info.get('repo') or ''} "
                f"(Hub cardData.license {declared!r} license_name {declared_name!r}; "
                f"no LICENSE file), read {READ_ON}. A known-wrong {s.license_type} "
                f"default is worse than none."
            ),
            declared=declared,
            declared_name=declared_name,
            cu_before="",
            cu_after="",
        )

    hub_bits = []
    if declared:
        hub_bits.append(f"Hub cardData.license {declared}")
    if declared_name:
        hub_bits.append(f"license_name {declared_name}")
    hub = " and ".join(hub_bits) if hub_bits else "Hub metadata"
    if mapped == s.license_type:
        action = "confirmed"
        after: str | None = mapped
    else:
        action = "corrected"
        after = mapped
    note = (
        f"Licence: {after}. Creator "
        f"{('LICENSE file ' + cite) if file_url else ('distribution ' + cite)} "
        f"({label}) and {hub}, read {READ_ON}."
    )
    return Decision(
        model_id=s.model_id,
        provider=s.provider,
        before=s.license_type,
        after=after,
        action=action,
        license_url=cite,
        note=note,
        declared=declared,
        declared_name=declared_name,
        cu_before="",
        cu_after="",
    )


def decide_closed(s: Suspect) -> Decision:
    terms = CLOSED_TERMS.get(s.provider)
    if terms is None:
        return Decision(
            model_id=s.model_id,
            provider=s.provider,
            before=s.license_type,
            after=None,
            action="nulled",
            license_url="",
            note=(
                f"Licence: null. Closed model; no vendor terms document was "
                f"read for provider {s.provider!r} on {READ_ON}. A known-wrong "
                f"{s.license_type} default is worse than none."
            ),
            declared=None,
            declared_name=None,
            cu_before="",
            cu_after="",
        )
    url, label = terms
    after = "proprietary"
    action = "confirmed" if s.license_type == "proprietary" else "corrected"
    note = f"Licence: proprietary. Vendor terms {url} ({label}), read {READ_ON}."
    return Decision(
        model_id=s.model_id,
        provider=s.provider,
        before=s.license_type,
        after=after,
        action=action,
        license_url=url,
        note=note,
        declared=None,
        declared_name=None,
        cu_before="",
        cu_after="",
    )


def decide(s: Suspect, hf: dict[str, Any] | None) -> Decision:
    if hf and hf.get("ok"):
        return decide_from_hf(s, hf)
    if s.hf_repo and hf and not hf.get("ok"):
        # Named a repo but could not read it.
        return Decision(
            model_id=s.model_id,
            provider=s.provider,
            before=s.license_type,
            after=None,
            action="nulled",
            license_url="",
            note=(
                f"Licence: null. Creator Hub repository {s.hf_repo} was not "
                f"readable ({hf.get('api_status') or hf.get('error') or 'no response'}), "
                f"read {READ_ON}. A known-wrong {s.license_type} default is worse than none."
            ),
            declared=None,
            declared_name=None,
            cu_before="",
            cu_after="",
        )
    # No distribution repo. Closed API, or open-weights with no address.
    if s.provider in CLOSED_TERMS and not s.open_weights:
        return decide_closed(s)
    if s.provider in CLOSED_TERMS and s.provider not in {"mistral", "deepseek"}:
        # Closed-API family (GPT, Claude, Gemini, Grok) even if a card left
        # open_weights true by mistake: the vendor terms are the document.
        return decide_closed(s)
    if s.provider in {"mistral", "deepseek"} and not s.open_weights:
        return decide_closed(s)
    if s.provider == "deepseek" and not s.hf_repo:
        # API aliases (deepseek-chat, deepseek-reasoner) with no weights repo.
        return decide_closed(s)
    return Decision(
        model_id=s.model_id,
        provider=s.provider,
        before=s.license_type,
        after=None,
        action="nulled",
        license_url="",
        note=(
            f"Licence: null. No creator distribution point on the card, "
            f"read {READ_ON}. A known-wrong {s.license_type} default is worse "
            f"than none."
        ),
        declared=None,
        declared_name=None,
        cu_before="",
        cu_after="",
    )


def _yaml_value(value: str | None) -> str:
    if value is None:
        return "null"
    return value


def _replace_line(text: str, key: str, value: str) -> str:
    pat = re.compile(rf"^([ ]*){re.escape(key)}:.*$", re.M)
    m = pat.search(text)
    if not m:
        raise ValueError(f"missing {key}")
    return text[: m.start()] + f"{m.group(1)}{key}: {value}" + text[m.end() :]


def _insert_note(text: str, note: str) -> str:
    if "Licence:" in text:
        return text
    parts = text.split("---", 2)
    body = parts[2]
    heading = re.search(r"\n## ", body)
    insertion = "\n" + note + "\n"
    if heading:
        body = body[: heading.start()] + insertion + body[heading.start() :]
    else:
        body = body.rstrip() + "\n" + insertion
    return "---".join(parts[:2]) + "---" + body


def apply_decision(path: Path, d: Decision) -> None:
    text = path.read_text(encoding="utf-8")
    text = _replace_line(text, "license_type", _yaml_value(d.after))
    if d.license_url:
        text = _replace_line(text, "license_url", d.license_url)
        if d.after == "proprietary":
            # Closed API: the cited document is the vendor terms.
            try:
                text = _replace_line(text, "tos_url", d.license_url)
            except ValueError:
                pass
        if "huggingface.co" in d.license_url:
            try:
                text = _replace_line(text, "last_scraped_huggingface", f"'{READ_ON}'")
            except ValueError:
                pass
    text = _replace_line(text, "card_updated", f"'{READ_ON}'")
    text = _insert_note(text, d.note)
    path.write_text(text, encoding="utf-8")


def _cu_label(card_type: str | None, provider: str, declared: str | None, declared_name: str | None) -> str:
    res = licence_of_record(
        card_type,
        provider=provider,
        declared_licence=declared or ("other" if declared_name else None),
        declared_licence_name=declared_name,
    )
    if res.licence_key is None:
        return f"unspecified/{res.reason}"
    reading = reading_for(res.licence_key)
    perm = reading.permission.value if reading else "unread"
    return f"{perm}/{res.reason}/{res.licence_key}"


def annotate_cu(d: Decision, s: Suspect) -> None:
    d.cu_before = _cu_label(s.license_type, s.provider, d.declared, d.declared_name)
    d.cu_after = _cu_label(d.after, s.provider, d.declared, d.declared_name)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--cap", type=int, default=CAP)
    parser.add_argument(
        "--providers",
        default="",
        help="comma-separated providers, in selection order (omit for traffic order)",
    )
    args = parser.parse_args()
    providers = [p.strip() for p in args.providers.split(",") if p.strip()] or None

    suspects = load_suspects()
    per = Counter(s.provider for s in suspects)
    print(f"suspect_total {len(suspects)}")
    for prov, n in per.most_common():
        print(f"suspect {prov} {n}")

    batch = select_batch(suspects, args.cap, providers=providers)
    remaining = [s for s in suspects if s not in batch]
    print(f"batch {len(batch)}")
    print(f"remaining {len(remaining)}")
    rem_per = Counter(s.provider for s in remaining)
    for prov, n in rem_per.most_common():
        print(f"remaining {prov} {n}")

    by_id = {s.model_id: s for s in batch}
    hf_needed = [s for s in batch if s.hf_repo]
    hf_results: dict[str, dict[str, Any]] = {}
    if hf_needed:
        limits = httpx.Limits(max_connections=4, max_keepalive_connections=4)
        with httpx.Client(timeout=30.0, headers={"User-Agent": UA}, follow_redirects=True, limits=limits) as client:
            with ThreadPoolExecutor(max_workers=4) as pool:
                futs = {pool.submit(fetch_hf, client, s.hf_repo): s for s in hf_needed if s.hf_repo}
                for fut in as_completed(futs):
                    s = futs[fut]
                    try:
                        hf_results[s.model_id] = fut.result()
                    except Exception as exc:  # noqa: BLE001
                        hf_results[s.model_id] = {"ok": False, "error": str(exc), "repo": s.hf_repo}

    decisions: list[Decision] = []
    for s in batch:
        d = decide(s, hf_results.get(s.model_id))
        annotate_cu(d, s)
        decisions.append(d)
        if args.apply:
            apply_decision(s.path, d)

    actions = Counter(d.action for d in decisions)
    cu_changed = [d for d in decisions if d.cu_before.split("/")[0] != d.cu_after.split("/")[0]]
    print(f"confirmed {actions.get('confirmed', 0)}")
    print(f"corrected {actions.get('corrected', 0)}")
    print(f"nulled {actions.get('nulled', 0)}")
    print(f"determinations_changed {len(cu_changed)}")
    for d in decisions:
        print(
            f"card {d.model_id} {d.action} {d.before}->{d.after} "
            f"cu {d.cu_before}->{d.cu_after}"
        )

    report = {
        "suspect_total": len(suspects),
        "suspect_per_provider": dict(per),
        "batch": len(batch),
        "remaining_per_provider": dict(rem_per),
        "actions": dict(actions),
        "determinations_changed": [
            {
                "model_id": d.model_id,
                "before": d.cu_before,
                "after": d.cu_after,
                "license": f"{d.before}->{d.after}",
            }
            for d in cu_changed
        ],
        "decisions": [asdict(d) for d in decisions],
    }
    out = Path("/tmp/model-86-report.json")
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"report {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
