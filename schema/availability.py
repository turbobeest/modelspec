"""Availability and policy-source definitions shared by cards and the decision registry."""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, model_validator

from .enums import DisclosureState


#: Source kinds a policy determination may cite. `legacy-import` is the one
#: kind that is *not* evidence: see `PolicySource` below.
PolicySourceKind = Literal[
    "license",
    "terms_of_service",
    "acceptable_use_policy",
    "provider_documentation",
    "provider_statement",
    "legacy-import",
]


class PolicySource(BaseModel):
    """The document a policy determination was read from, and the day it was read.

    A policy answer is only worth anything if the reader can go and check it,
    and licences are rewritten without notice — so the date is as load-bearing
    as the URL. This mirrors `BenchmarkEvidence`: everything needed to recheck
    the claim, or it is not a claim.

    `legacy-import` is the single exception and it is deliberately ugly. Eight
    cards carried `commercial_use: true` with no citation from before this
    shape existed. Discarding those values would lose information; dressing
    them up with a plausible licence URL would manufacture evidence that was
    never read. So they keep the value and carry a source that says, in the
    published JSON, that nobody cited anything — the same thing
    `evidence_basis: unverified-legacy` says about benchmark scores. It is
    frozen to those eight by
    `tests/test_policy_shape.py::test_legacy_import_is_frozen_to_the_migrated_eight`;
    a ninth card cannot quietly use it.
    """

    kind: PolicySourceKind
    url: str = ""
    #: The day the document at `url` was read. ISO `YYYY-MM-DD`.
    read_on: str = ""
    #: Optional. The operative clause, verbatim and short, so a reader can see
    #: what the determination was made from without refetching the document.
    quote: str = ""

    @model_validator(mode="after")
    def _evidence_or_an_admission(self) -> PolicySource:
        if self.kind == "legacy-import":
            if self.url or self.read_on or self.quote:
                raise ValueError(
                    "a legacy-import source is the admission that nothing was "
                    "cited; it cannot carry a url, a read date or a quote. "
                    "If a document was actually read, cite it with a real kind."
                )
            return self
        if not self.url.startswith(("http://", "https://")):
            raise ValueError(
                "url must be the document the determination was read from; "
                "a policy answer without one cannot be rechecked"
            )
        try:
            date.fromisoformat(self.read_on)
        except ValueError as exc:
            raise ValueError(
                f"read_on must be the exact ISO date the document was read, "
                f"got {self.read_on!r}. Licence terms change; an undated "
                f"reading cannot be trusted later."
            ) from exc
        return self

    @property
    def is_evidence(self) -> bool:
        """False for `legacy-import`, which is a value with no citation."""
        return self.kind != "legacy-import"


class PlatformEntry(BaseModel):
    """A single platform where a model may be available."""
    available: bool = False
    model_id: str = ""
    url: str = ""
    fine_tuning: bool = False
    gated: bool = False
    regions: list[str] = []
    notes: str = ""


class PrimaryProvider(BaseModel):
    name: str = ""
    platform_url: str = ""
    api_endpoint: str = ""
    npm_package: str = ""
    env_vars: list[str] = []
    model_id_on_platform: str = ""
    rate_limit_rpm: int | None = None
    rate_limit_tpm: int | None = None
    sla_uptime: str = ""
    regions: list[str] = []
    #: Where the provider commits to processing data. `null` until it is a
    #: determination — see `data_residency_disclosure`. Was `list[str] = []`
    #: until MODEL-77, where the default was indistinguishable from an answer
    #: and sat on all 1,339 cards while being researched on none of them.
    data_residency: list[str] | None = None
    data_residency_disclosure: DisclosureState = DisclosureState.UNRESEARCHED
    #: Required when the disclosure is `published`; forbidden otherwise, for
    #: the same reason as `commercial_use_source`.
    data_residency_source: PolicySource | None = None
    hipaa_eligible: bool = False
    fedramp_authorized: bool = False
    soc2_compliant: bool = False
    free_tier: bool = False
    free_tier_details: str = ""

    @model_validator(mode="after")
    def _residency_states_are_not_interchangeable(self) -> PrimaryProvider:
        state = self.data_residency_disclosure
        if state is DisclosureState.PUBLISHED:
            if self.data_residency is None:
                raise ValueError(
                    "data_residency_disclosure is 'published' but data_residency "
                    "is null. An empty list is a legitimate published answer "
                    "('no residency commitment'); null is not an answer at all."
                )
            if self.data_residency_source is None:
                raise ValueError(
                    "data_residency is published with no data_residency_source. "
                    "Standing rule 1: an uncited policy answer is not an answer."
                )
            return self
        if self.data_residency is not None:
            raise ValueError(
                f"data_residency_disclosure is {state.value!r} but data_residency "
                "carries a value. Only a published determination has one; set "
                "the disclosure to 'published' and cite it, or clear the value."
            )
        if self.data_residency_source is not None:
            raise ValueError(
                f"data_residency_disclosure is {state.value!r} but carries a "
                "data_residency_source. Nothing has been published to cite."
            )
        return self


class Availability(BaseModel):
    primary_provider: PrimaryProvider = PrimaryProvider()
    # Cloud platforms
    aws_bedrock: PlatformEntry = PlatformEntry(url="https://aws.amazon.com/bedrock/")
    azure_ai_foundry: PlatformEntry = PlatformEntry(url="https://ai.azure.com/")
    google_vertex_ai: PlatformEntry = PlatformEntry(url="https://cloud.google.com/vertex-ai")
    nvidia_nim: PlatformEntry = PlatformEntry(url="https://build.nvidia.com/")
    ibm_watsonx: PlatformEntry = PlatformEntry(url="https://www.ibm.com/watsonx")
    snowflake_cortex: PlatformEntry = PlatformEntry(url="https://www.snowflake.com/en/data-cloud/cortex/")
    # Inference providers
    groq: PlatformEntry = PlatformEntry(url="https://groq.com/")
    together_ai: PlatformEntry = PlatformEntry(url="https://www.together.ai/")
    fireworks_ai: PlatformEntry = PlatformEntry(url="https://fireworks.ai/")
    replicate: PlatformEntry = PlatformEntry(url="https://replicate.com/")
    deepinfra: PlatformEntry = PlatformEntry(url="https://deepinfra.com/")
    cerebras: PlatformEntry = PlatformEntry(url="https://www.cerebras.ai/")
    sambanova: PlatformEntry = PlatformEntry(url="https://sambanova.ai/")
    # Aggregators
    openrouter: PlatformEntry = PlatformEntry(url="https://openrouter.ai/")
    # AI apps
    cursor: PlatformEntry = PlatformEntry(url="https://cursor.com/")
    github_copilot: PlatformEntry = PlatformEntry(url="https://github.com/features/copilot")
    perplexity: PlatformEntry = PlatformEntry(url="https://www.perplexity.ai/")
    raycast: PlatformEntry = PlatformEntry(url="https://www.raycast.com/")
    poe: PlatformEntry = PlatformEntry(url="https://poe.com/")
    # Consumer chat
    chatgpt: PlatformEntry = PlatformEntry(url="https://chat.openai.com/")
    claude_ai: PlatformEntry = PlatformEntry(url="https://claude.ai/")
    gemini_app: PlatformEntry = PlatformEntry(url="https://gemini.google.com/")
    grok_xai: PlatformEntry = PlatformEntry(url="https://x.ai/")
    meta_ai: PlatformEntry = PlatformEntry(url="https://www.meta.ai/")
    copilot_microsoft: PlatformEntry = PlatformEntry(url="https://copilot.microsoft.com/")
    # Provider platforms
    mistral_plateforme: PlatformEntry = PlatformEntry(url="https://console.mistral.ai/")
    cohere: PlatformEntry = PlatformEntry(url="https://cohere.com/")
    ai21_labs: PlatformEntry = PlatformEntry(url="https://www.ai21.com/")
    stability_ai: PlatformEntry = PlatformEntry(url="https://stability.ai/")
    # Chinese platforms
    deepseek: PlatformEntry = PlatformEntry(url="https://platform.deepseek.com/")
    qwen_alibaba: PlatformEntry = PlatformEntry(url="https://www.alibabacloud.com/en/solutions/generative-ai/qwen")
    baidu_ernie: PlatformEntry = PlatformEntry(url="https://cloud.baidu.com/")
    bytedance_doubao: PlatformEntry = PlatformEntry(url="https://www.volcengine.com/")
    tencent_hunyuan: PlatformEntry = PlatformEntry(url="https://cloud.tencent.com/")
    zhipu_glm: PlatformEntry = PlatformEntry(url="https://www.zhipuai.cn/")
    moonshot_kimi: PlatformEntry = PlatformEntry(url="https://www.moonshot.cn/")
    minimax: PlatformEntry = PlatformEntry(url="https://www.minimax.chat/")
    zero_one_ai: PlatformEntry = PlatformEntry(url="https://www.01.ai/")
    # Regional
    tii_falcon: PlatformEntry = PlatformEntry(url="https://falconllm.tii.ae/")
    samsung_gauss: PlatformEntry = PlatformEntry(url="https://www.samsung.com/")
    upstage_solar: PlatformEntry = PlatformEntry(url="https://www.upstage.ai/")
    # Local
    ollama: PlatformEntry = PlatformEntry(url="https://ollama.com/")
    lm_studio: PlatformEntry = PlatformEntry(url="https://lmstudio.ai/")
    gpt4all: PlatformEntry = PlatformEntry(url="https://gpt4all.io/")
    jan_ai: PlatformEntry = PlatformEntry(url="https://jan.ai/")
    mlx_community: PlatformEntry = PlatformEntry(url="https://huggingface.co/mlx-community")
    open_webui: PlatformEntry = PlatformEntry(url="https://openwebui.com/")
    # Model hubs
    huggingface: PlatformEntry = PlatformEntry(url="https://huggingface.co/")
    modelscope: PlatformEntry = PlatformEntry(url="https://modelscope.cn/")
    kaggle_models: PlatformEntry = PlatformEntry(url="https://www.kaggle.com/models")
    # Overflow
    other_platforms: list[PlatformEntry] = []

    def platforms_available(self) -> list[str]:
        """Return names of all platforms where this model is available."""
        available = []
        for field_name, field_value in self:
            if isinstance(field_value, PlatformEntry) and field_value.available:
                available.append(field_name)
        return available


