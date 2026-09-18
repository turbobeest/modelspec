"""What each licence actually says about commercial use, read from the licence.

Every entry in `READINGS` was produced by fetching the document at its `url` on
its `read_on` date and reading the clause quoted in `source.quote`. None of it
was recalled. That is standing rule 2, and it is not a style preference: the
corpus has already published 1,589 wrong "it fits" answers that came from
exactly the kind of plausible inference a model is good at.

**A licence that is not in this table produces no value.** `reading_for`
returns `None` rather than a default, and there is deliberately no
`allowed`-shaped fallback for "looks permissive". An unread licence is an
unanswered question, and `UsePermission.UNSPECIFIED` is the honest way to say
so.

**Adding an entry means reading a document.** Fetch it, quote the operative
clause, set `read_on` to the day you fetched it, and add a case to
`tests/test_policy_commercial_use.py`. The date is as load-bearing as the URL:
licence terms are rewritten without notice, and an undated reading cannot be
rechecked later.

Keys are the identifiers the distribution point uses, so that a determination
can be traced to a licence *document* rather than to a family name. That
matters most for `llama-community`, which is not one licence: Llama 2, 3, 3.1,
3.2, 3.3 and 4 are six separate agreements. They happen to agree on the
commercial threshold, but they are still six documents and each is cited as
itself.
"""

from __future__ import annotations

import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from schema.card import PolicySource  # noqa: E402
from schema.enums import UsePermission  # noqa: E402

#: The day every document in this table was fetched and read. One date because
#: the readings were done in one pass; a later edit carries its own date rather
#: than inheriting this one.
READ_ON = "2026-09-16"


@dataclass(frozen=True)
class LicenceReading:
    """One licence, read once, with the clause the answer came from.

    `conditions` is required exactly when `permission` is `RESTRICTED` — the
    same rule `schema.card.Licensing` and `schema.enrichment.EnrichmentRecord`
    enforce, checked here too so a bad entry fails at import rather than at the
    end of a corpus run.
    """

    permission: UsePermission
    source: PolicySource
    conditions: str = ""

    def __post_init__(self) -> None:
        if self.permission is UsePermission.RESTRICTED and not self.conditions.strip():
            raise ValueError(
                f"{self.source.url} is recorded as 'restricted' with no conditions. "
                "'Restricted' without the restriction tells a buyer nothing they "
                "can act on."
            )
        if self.permission is not UsePermission.RESTRICTED and self.conditions.strip():
            raise ValueError(
                f"{self.source.url} carries conditions but is "
                f"{self.permission.value!r}; conditions belong to a restricted grant."
            )
        if self.permission not in (
            UsePermission.ALLOWED,
            UsePermission.RESTRICTED,
            UsePermission.PROHIBITED,
        ):
            raise ValueError(
                f"{self.permission.value!r} is not a determination. This table "
                "records what a licence says; a licence that was not read simply "
                "has no entry."
            )


def _licence(url: str, quote: str, read_on: str = READ_ON) -> PolicySource:
    return PolicySource(kind="license", url=url, read_on=read_on, quote=quote)


def _terms(url: str, quote: str, read_on: str = READ_ON) -> PolicySource:
    return PolicySource(kind="terms_of_service", url=url, read_on=read_on, quote=quote)


# ── The Llama community licences ────────────────────────────────────────────
# Six documents, one threshold. Each is read and cited as itself: citing Llama
# 3.1's URL for a Llama 2 model would be manufacturing evidence, even though
# the clause is the same sentence with a different version name in it.
_LLAMA_CONDITION = (
    "Commercial use is granted, but a licensee whose products or services had "
    "more than 700 million monthly active users in the calendar month before "
    "the model's release date must request a separate licence from Meta, which "
    "Meta may grant at its sole discretion. Use is also subject to Meta's "
    "Acceptable Use Policy, and outputs may not be used to improve any other "
    "large language model."
)

_LLAMA_SOURCES = {
    "llama2": (
        "https://raw.githubusercontent.com/meta-llama/llama/main/LICENSE",
        "If, on the Llama 2 version release date, the monthly active users of "
        "the products or services made available by or for Licensee, or "
        "Licensee's affiliates, is greater than 700 million monthly active "
        "users in the preceding calendar month, you must request a license "
        "from Meta",
    ),
    "llama3": (
        "https://raw.githubusercontent.com/meta-llama/llama3/main/LICENSE",
        "If, on the Meta Llama 3 version release date, the monthly active "
        "users of the products or services made available by or for Licensee, "
        "or Licensee's affiliates, is greater than 700 million monthly active "
        "users in the preceding calendar month, you must request a license "
        "from Meta",
    ),
    "llama3.1": (
        "https://raw.githubusercontent.com/meta-llama/llama-models/main/models/llama3_1/LICENSE",
        "If, on the Llama 3.1 version release date, the monthly active users "
        "of the products or services made available by or for Licensee, or "
        "Licensee's affiliates, is greater than 700 million monthly active "
        "users in the preceding calendar month, you must request a license "
        "from Meta",
    ),
    "llama3.2": (
        "https://raw.githubusercontent.com/meta-llama/llama-models/main/models/llama3_2/LICENSE",
        "If, on the Llama 3.2 version release date, the monthly active users "
        "of the products or services made available by or for Licensee, or "
        "Licensee's affiliates, is greater than 700 million monthly active "
        "users in the preceding calendar month, you must request a license "
        "from Meta",
    ),
    "llama3.3": (
        "https://raw.githubusercontent.com/meta-llama/llama-models/main/models/llama3_3/LICENSE",
        "If, on the Llama 3.3 version release date, the monthly active users "
        "of the products or services made available by or for Licensee, or "
        "Licensee's affiliates, is greater than 700 million monthly active "
        "users in the preceding calendar month, you must request a license "
        "from Meta",
    ),
    "llama4": (
        "https://raw.githubusercontent.com/meta-llama/llama-models/main/models/llama4/LICENSE",
        "If, on the Llama 4 version release date, the monthly active users of "
        "the products or services made available by or for Licensee, or "
        "Licensee's affiliates, is greater than 700 million monthly active "
        "users in the preceding calendar month, you must request a license "
        "from Meta",
    ),
}


_READINGS: dict[str, LicenceReading] = {
    # ── Permissive open-source licences ─────────────────────────────────────
    "apache-2.0": LicenceReading(
        permission=UsePermission.ALLOWED,
        source=_licence(
            "https://www.apache.org/licenses/LICENSE-2.0.txt",
            "each Contributor hereby grants to You a perpetual, worldwide, "
            "non-exclusive, no-charge, royalty-free, irrevocable copyright "
            "license to reproduce, prepare Derivative Works of, publicly "
            "display, publicly perform, sublicense, and distribute the Work "
            "and such Derivative Works in Source or Object form.",
        ),
    ),
    "mit": LicenceReading(
        permission=UsePermission.ALLOWED,
        source=_licence(
            "https://opensource.org/license/mit",
            "Permission is hereby granted, free of charge, to any person "
            "obtaining a copy of this software and associated documentation "
            "files (the “Software”), to deal in the Software without "
            "restriction",
        ),
    ),
    "bsd-3-clause": LicenceReading(
        permission=UsePermission.ALLOWED,
        source=_licence(
            "https://opensource.org/license/bsd-3-clause",
            "Redistribution and use in source and binary forms, with or "
            "without modification, are permitted provided that the following "
            "conditions are met:",
        ),
    ),
    # ── Non-commercial licences ─────────────────────────────────────────────
    "cc-by-nc-4.0": LicenceReading(
        permission=UsePermission.PROHIBITED,
        source=_licence(
            "https://creativecommons.org/licenses/by-nc/4.0/legalcode.en",
            "reproduce and Share the Licensed Material, in whole or in part, "
            "for NonCommercial purposes only",
        ),
    ),
    "cc-by-nc-sa-4.0": LicenceReading(
        permission=UsePermission.PROHIBITED,
        source=_licence(
            "https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode.en",
            "reproduce and Share the Licensed Material, in whole or in part, "
            "for NonCommercial purposes only",
        ),
    ),
    # ── Family licences ─────────────────────────────────────────────────────
    "gemma": LicenceReading(
        permission=UsePermission.RESTRICTED,
        source=_terms(
            "https://ai.google.dev/gemma/terms",
            "You must not use any of the Gemma Services: for the restricted "
            "uses set forth in the Gemma Prohibited Use Policy at "
            'ai.google.dev/gemma/prohibited_use_policy (" Prohibited Use '
            'Policy "), which is hereby incorporated by reference into this '
            "Agreement; or in violation of applicable laws and regulations.",
        ),
        conditions=(
            "Commercial use is granted, but use of the model and its outputs is "
            "bound by the Gemma Prohibited Use Policy, which is incorporated "
            "into the terms by reference and may be updated by Google. The "
            "restriction travels with any distributed derivative, and Google "
            "reserves the right to restrict usage it believes violates the terms."
        ),
    ),
    "deepseek": LicenceReading(
        permission=UsePermission.RESTRICTED,
        source=_licence(
            "https://github.com/deepseek-ai/DeepSeek-LLM/raw/HEAD/LICENSE-MODEL",
            "Use-based restrictions. The restrictions set forth in Attachment A "
            "are considered Use-based restrictions. Therefore You cannot use "
            "the Model and the Derivatives of the Model for the specified "
            "restricted uses.",
        ),
        conditions=(
            "Commercial use is granted, including hosting for third-party "
            "remote access, but the Attachment A use-based restrictions apply "
            "and must be passed on as an enforceable provision in any agreement "
            "governing a derivative or redistribution."
        ),
    ),
    **{
        key: LicenceReading(
            permission=UsePermission.RESTRICTED,
            source=_licence(url, quote),
            conditions=_LLAMA_CONDITION,
        )
        for key, (url, quote) in _LLAMA_SOURCES.items()
    },
    # ── Proprietary provider terms ──────────────────────────────────────────
    # Keyed by provider, because a closed model is licensed by the agreement
    # covering the API it is served through, not by a file shipped with weights
    # there are none of.
    "terms:openai": LicenceReading(
        permission=UsePermission.RESTRICTED,
        source=_terms(
            "https://openai.com/policies/business-terms/",
            "OpenAI grants Customer a non-exclusive right to access and use the "
            "Services during the Term. This includes the right to use OpenAI's "
            "API to integrate the Services into Customer Applications and to "
            "make Customer Applications available to End Users.",
        ),
        conditions=(
            "Commercial use is granted under the OpenAI Services Agreement "
            "(effective 1 January 2026) to business and developer customers on "
            "a paid account. Customer owns the Output. Customer may not use "
            "Output to develop competing AI models, resell or transfer API "
            "keys, or use the Services in violation of the OpenAI Policies."
        ),
    ),
    "terms:google": LicenceReading(
        permission=UsePermission.RESTRICTED,
        source=_terms(
            "https://ai.google.dev/gemini-api/terms",
            "You may not use the Services to develop models that compete with "
            "the Services (e.g., Gemini API or Google AI Studio). You also may "
            "not attempt to reverse engineer, extract or replicate any "
            "component of the Services, including the underlying data or models "
            "(e.g., parameter weights).",
        ),
        conditions=(
            "Commercial use is granted under the Gemini API Additional Terms of "
            "Service and Google does not claim ownership of generated content, "
            "but the Services may only be accessed in an available region; "
            "making API clients available to users in the EEA, Switzerland or "
            "the UK requires the Paid Services; and the Services may not be "
            "used to develop competing models or to extract model weights."
        ),
    ),
    "terms:anthropic": LicenceReading(
        permission=UsePermission.RESTRICTED,
        source=_terms(
            "https://www.anthropic.com/legal/commercial-terms",
            "Anthropic agrees that Customer (a) retains all rights to its "
            "Inputs, and (b) owns its Outputs. Anthropic disclaims any rights "
            "it receives to the Customer Content under these Terms.",
        ),
        conditions=(
            "Commercial use is granted under the Anthropic Commercial Terms of "
            "Service (effective 17 June 2025) and the Customer owns its "
            "Outputs, but use is bound by the Usage Policy, the Supported "
            "Regions Policy and the Service Specific Terms, each incorporated "
            "by reference and each revisable by Anthropic."
        ),
    ),
    "terms:xai": LicenceReading(
        permission=UsePermission.RESTRICTED,
        source=_terms(
            "https://x.ai/legal/terms-of-service-enterprise",
            "SpaceXAI grants Customer the limited, non-transferable (except as "
            "expressly permitted herein), non-sublicensable right to (a) access "
            "and use solely for Customer's business purposes the products and "
            "services identified in any Order Form",
        ),
        conditions=(
            "Commercial use is granted under the SpaceXAI Terms of Service — "
            "Enterprise (last updated 14 August 2026) on a subscription "
            "recorded in an Order Form. The grant is limited, non-transferable "
            "and non-sublicensable; end users may only reach the Services as "
            "part of the Customer's bundled service; and use is bound by the "
            "xAI Acceptable Use Policy."
        ),
    ),
    "terms:amazon": LicenceReading(
        permission=UsePermission.RESTRICTED,
        source=_terms(
            "https://aws.amazon.com/service-terms/",
            "The output that you generate using AI Services is Your Content. "
            "Due to the nature of machine learning, output may not be unique "
            "across customers and the Services may generate the same or similar "
            "results across customers.",
        ),
        conditions=(
            "Commercial use is granted under the AWS Service Terms §50 (last "
            "updated 15 September 2026), which cover Amazon Bedrock and the "
            "Amazon Foundation Models (Nova and Titan), and the output is the "
            "customer's content. Use is bound by the AWS Customer Agreement and "
            "the AWS Acceptable Use Policy, and AWS may disable content it "
            "reasonably believes breaches them."
        ),
    ),
    "terms:perplexity": LicenceReading(
        permission=UsePermission.RESTRICTED,
        source=_terms(
            "https://www.perplexity.ai/hub/legal/perplexity-api-terms-of-service",
            "Customer may, on a non-exclusive, non-sublicensable and "
            "non-transferable basis during the term of this Agreement, ... use "
            "the Services and the API Keys solely to submit Input (as defined "
            "in Section 2.3 below) to the Service, receive Output (as defined "
            "in Section 2.3 below) from the Service, and display such Output, "
            "in each case, solely within the Customer Applications in "
            "accordance with the API Documentation",
        ),
        conditions=(
            "Commercial use is granted under the Perplexity API Terms of "
            "Service (last updated 23 January 2026) to API customers only. The "
            "grant is non-exclusive, non-sublicensable and non-transferable, "
            "and Output may only be displayed within the Customer Applications "
            "integrated under the agreement."
        ),
    ),
    # ── MODEL-86: Qwen / Tongyi and Mistral research licences ───────────────
    # Read 2026-09-18. Keys are the Hub `license` / `license_name` strings, not
    # the card family `qwen`. Tongyi Qianwen (2023-08-03) and the Qwen LICENSE
    # AGREEMENT (2024-09-19) are two documents; they share the 100M-MAU
    # threshold and differ on output-to-train-other-models.
    "qwen": LicenceReading(
        permission=UsePermission.RESTRICTED,
        source=_licence(
            "https://huggingface.co/Qwen/Qwen2.5-72B/raw/main/LICENSE",
            "If you are commercially using the Materials, and your product or "
            "service has more than 100 million monthly active users, you shall "
            "request a license from us. You cannot exercise your rights under "
            "this Agreement without our express authorization.",
            read_on="2026-09-18",
        ),
        conditions=(
            "Commercial use is granted, but a licensee whose product or "
            "service has more than 100 million monthly active users must "
            "request a separate licence from Alibaba Cloud. Using the "
            "Materials or their outputs to create a distributed AI model "
            "requires 'Built with Qwen' or 'Improved using Qwen' attribution."
        ),
    ),
    "tongyi-qianwen": LicenceReading(
        permission=UsePermission.RESTRICTED,
        source=_licence(
            "https://huggingface.co/Qwen/Qwen-7B/raw/main/LICENSE",
            "If you are commercially using the Materials, and your product or "
            "service has more than 100 million monthly active users, You shall "
            "request a license from Us. You cannot exercise your rights under "
            "this Agreement without our express authorization.",
            read_on="2026-09-18",
        ),
        conditions=(
            "Commercial use is granted, but a licensee whose product or "
            "service has more than 100 million monthly active users must "
            "request a separate licence from Alibaba Cloud. The Materials and "
            "their outputs may not be used to improve any other large language "
            "model (excluding Tongyi Qianwen or derivative works thereof)."
        ),
    ),
    "qwen-research": LicenceReading(
        permission=UsePermission.PROHIBITED,
        source=_licence(
            "https://huggingface.co/Qwen/Qwen2.5-3B-Instruct/raw/main/LICENSE",
            "make modifications to the Materials FOR NON-COMMERCIAL PURPOSES ONLY.",
            read_on="2026-09-18",
        ),
    ),
    "mrl": LicenceReading(
        permission=UsePermission.PROHIBITED,
        source=_licence(
            "https://mistral.ai/licenses/MRL-0.1.md",
            "You shall only use the Mistral Models, Derivatives (whether or "
            "not created by Mistral AI) and Outputs for Research Purposes.",
            read_on="2026-09-18",
        ),
    ),
    "mnpl": LicenceReading(
        permission=UsePermission.PROHIBITED,
        source=_licence(
            "https://mistral.ai/licenses/MNPL-0.1.md",
            "You shall not supply the Mistral Models or Derivatives in the "
            "course of a commercial activity, whether in return for payment "
            "or free of charge, in any medium or form, including but not "
            "limited to through a hosted or managed service (e.g. SaaS, cloud "
            "instances, etc.), or behind a software layer.",
            read_on="2026-09-18",
        ),
    ),
    "terms:mistral": LicenceReading(
        permission=UsePermission.RESTRICTED,
        source=_terms(
            "https://legal.mistral.ai/terms/commercial-terms-of-service",
            "Subject to Customer's compliance with these Terms, Mistral AI "
            "grants Customer a limited, non-exclusive, non-transferrable "
            "(except as provided in Section 14.2 (Assignment)), "
            "non-sublicensable (except to its End Users) license to access "
            "and use the Mistral AI Products.",
            read_on="2026-09-18",
        ),
        conditions=(
            "Commercial use is granted under the Mistral AI Terms of Service "
            "for Commercial Users as a limited, non-exclusive, "
            "non-transferable, non-sublicensable licence to access the Mistral "
            "AI Products. Use is bound by the Usage Policy and Additional "
            "Terms; image Outputs may not be used to train a competing image "
            "generation product."
        ),
    ),
    # ── MODEL-86 batch 4: long-tail providers ───────────────────────────────
    # Own block so a merge with batch 2 (Qwen / Meta / Microsoft / NVIDIA)
    # stays a clean append. Read 2026-09-18. Keys are Hub license_name or
    # terms:<provider>. MiniMax's "modified-mit" is several documents with
    # different commercial clauses, so it is not keyed here.
    "lfm1.0": LicenceReading(
        permission=UsePermission.RESTRICTED,
        source=_licence(
            "https://huggingface.co/LiquidAI/LFM2-1.2B/raw/main/LICENSE",
            "The rights granted under this License for Commercial Use are "
            "conditioned upon You or Your Legal Entity not exceeding the "
            "Threshold.",
            read_on="2026-09-18",
        ),
        conditions=(
            "Commercial use is granted under the LFM Open License v1.0 only "
            "while the licensee's annual revenue is below USD 10 million. "
            "Commercial use by an entity at or above that threshold is not "
            "licensed; the threshold does not apply to a qualified non-profit "
            "using the work for non-commercial or research purposes."
        ),
    ),
    "ltx-2-community-license-agreement": LicenceReading(
        permission=UsePermission.RESTRICTED,
        source=_licence(
            "https://huggingface.co/unsloth/LTX-2.3-GGUF/raw/main/LICENSE",
            "Entities with annual revenues of at least $10,000,000 (the "
            '"Commercial Entities") are required to obtain a paid commercial '
            "use license in order to use LTX-2 and Derivatives of LTX-2",
            read_on="2026-09-18",
        ),
        conditions=(
            "Commercial use is granted under the LTX-2 Community License "
            "Agreement (5 January 2026) below USD 10 million annual revenue. "
            "Entities at or above that threshold must obtain a separate paid "
            "commercial-use licence from Lightricks. Attachment A use "
            "restrictions apply, including a ban on using the model to train "
            "a competing system."
        ),
    ),
    "terms:inception": LicenceReading(
        permission=UsePermission.RESTRICTED,
        source=_terms(
            "https://www.inceptionlabs.ai/docs/terms-of-use",
            "Subject to these Terms, we grant each user of the Services a "
            "worldwide, non-exclusive, non-sublicensable and non-transferable "
            "license to use (i.e., to download and display locally) Content "
            "solely for purposes of using the Services.",
            read_on="2026-09-18",
        ),
        conditions=(
            "Access is under the Inception Terms of Use (effective 1 September "
            "2025). The grant is non-exclusive, non-sublicensable and "
            "non-transferable. Outputs may be used, modified, reproduced, "
            "distributed and displayed for any purpose not otherwise "
            "restricted; the Terms also say the Services may be used only for "
            "the user's own internal, personal use and not on behalf of a "
            "third party, and Inception may change the Terms."
        ),
    ),
    "terms:upstage": LicenceReading(
        permission=UsePermission.RESTRICTED,
        source=_terms(
            "https://www.upstage.ai/terms-of-service",
            "When a member agrees to these Terms, the Company grants the "
            "member a non-transferable, limited license to use the Service, "
            "and may not be sublicensed. The member may use the Service and "
            "its outputs only within the scope of the Service's intended "
            "purpose, as specified in these Terms.",
            read_on="2026-09-18",
        ),
        conditions=(
            "Commercial use is granted under the Upstage Terms of Service as "
            "a non-transferable, limited, non-sublicensable licence. Outputs "
            "may be used only within the Service's intended purpose. Where "
            "the Company publishes a Korean and an English version, the "
            "Korean text prevails."
        ),
    ),
}

# Hub `license_name` for the 2023 Tongyi Qianwen agreement is sometimes the
# longer spelling. Same document, same reading.
_READINGS["tongyi-qianwen-license-agreement"] = _READINGS["tongyi-qianwen"]

#: The licence readings, by licence identifier. Read-only on purpose: a caller
#: that wants a new licence answered has to add it here, with a document and a
#: date, where the test suite can see it.
READINGS: Mapping[str, LicenceReading] = MappingProxyType(_READINGS)


def reading_for(licence_key: str | None) -> LicenceReading | None:
    """The reading for `licence_key`, or `None` if that licence was not read.

    `None` is the whole point of this function. There is no default and no
    nearest match: an unread licence yields no determination, the card keeps
    `unspecified`, and the gap shows up in the published remaining count
    instead of as a confident wrong answer.
    """
    if not licence_key:
        return None
    return READINGS.get(licence_key.strip().lower())
