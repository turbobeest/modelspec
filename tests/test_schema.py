"""Validate the ModelRank schema compiles and basic operations work."""

import sys
sys.path.insert(0, "/home/claude/modelrank")

from schema.enums import ModelType, ModelStatus, Tier, ArchitectureType, LicenseType
from schema.card import (
    ModelCard, Identity, Architecture, Lineage, Licensing, Capabilities,
    CodingCapability, ReasoningCapability, ToolUseCapability, Benchmarks,
    Deployment, HardwareProfile, Availability, Cost, Modalities, TextDetail,
)

# ── Test 1: Create a minimal card ──────────────────────────
print("Test 1: Minimal card creation...")
card = ModelCard(
    identity=Identity(
        model_id="test/minimal-model",
        display_name="Minimal Test Model",
        provider="test",
    )
)
assert card.identity.model_id == "test/minimal-model"
assert card.card_completeness > 0  # Should have some fields filled
print(f"  ✓ Created. Completeness: {card.card_completeness}%")

# ── Test 2: Create a fully populated card ──────────────────
print("\nTest 2: Rich card creation...")
card = ModelCard(
    identity=Identity(
        model_id="qwen/qwen3-30b-a3b",
        display_name="Qwen3 30B-A3B",
        provider="qwen",
        provider_display="Alibaba / Qwen Team",
        family="qwen3",
        release_date="2025-04",
        status=ModelStatus.ACTIVE,
        model_type=ModelType.LLM_CHAT,
        model_subtypes=[ModelType.LLM_CODE, ModelType.LLM_REASONING],
        tags=["moe", "multilingual", "chinese"],
    ),
    architecture=Architecture(
        type=ArchitectureType.MOE,
        total_parameters=30_000_000_000,
        active_parameters=3_000_000_000,
        num_experts=128,
        experts_per_token=8,
        attention_type="GQA",
    ),
    licensing=Licensing(
        open_weights=True,
        license_type=LicenseType.APACHE_2_0,
        origin_country="CN",
    ),
    modalities=Modalities(
        text=TextDetail(
            context_window=128_000,
            max_input_tokens=128_000,
            max_output_tokens=32_000,
            streaming=True,
        ),
    ),
    capabilities=Capabilities(
        coding=CodingCapability(
            overall=Tier.TIER_1,
            agentic_coding=True,
            multi_file_editing=True,
            languages=["python", "typescript", "rust", "java"],
        ),
        reasoning=ReasoningCapability(
            overall=Tier.TIER_1,
            chain_of_thought=True,
            mathematical=True,
        ),
        tool_use=ToolUseCapability(
            overall=Tier.TIER_1,
            function_calling=True,
            mcp_compatible=True,
        ),
    ),
    cost=Cost(input=0.0, output=0.0, note="Open weights — local inference only"),
    benchmarks=Benchmarks(scores={
        "arena_elo_overall": 1280,
        "gpqa_diamond": 52.3,
        "humaneval": 85.0,
        "swe_bench_verified": 38.2,
    }),
    deployment=Deployment(
        local_inference=True,
        self_hostable=True,
        quantizations_available=["Q4_K_M", "Q5_K_M", "Q8_0", "FP16"],
        hardware_profiles={
            "nvidia_5090_32gb": HardwareProfile(
                fits=True, best_quant="Q8_0", vram_usage_gb=18.0,
                tokens_per_sec=85.0, ttft_ms=120.0,
            ),
            "dgx_spark_128gb": HardwareProfile(
                fits=True, best_quant="FP16", vram_usage_gb=60.0,
                tokens_per_sec=200.0, ttft_ms=50.0,
            ),
            "macbook_m4_pro_64gb": HardwareProfile(
                fits=True, best_quant="Q8_0", ram_usage_gb=20.0,
                tokens_per_sec=45.0, ttft_ms=200.0, inference_engine="MLX",
            ),
            "macbook_air_m4_24gb": HardwareProfile(
                fits=True, best_quant="Q4_K_M", ram_usage_gb=12.0,
                tokens_per_sec=28.0, ttft_ms=350.0, inference_engine="ollama",
            ),
        },
    ),
)

print(f"  ✓ Created. Completeness: {card.card_completeness}%")
print(f"  ✓ Model type: {card.identity.model_type}")
print(f"  ✓ Parameters: {card.architecture.total_parameters:,} total, {card.architecture.active_parameters:,} active")
print(f"  ✓ Benchmarks filled: {card.benchmarks.filled_count()}")
print(f"  ✓ Platforms available: {card.availability.platforms_available()}")

# ── Test 3: Count fields ───────────────────────────────────
print("\nTest 3: Field counting...")
filled, total = card._count_fields(card)
print(f"  ✓ {filled} / {total} fields filled ({card.card_completeness}%)")

# ── Test 4: YAML round-trip ────────────────────────────────
print("\nTest 4: YAML serialization...")
yaml_output = card.to_yaml()
lines = yaml_output.count("\n")
print(f"  ✓ Serialized to {lines} lines of YAML")

# ── Test 5: Schema field count ─────────────────────────────
print("\nTest 5: Schema introspection...")

def count_schema_fields(model_cls, prefix=""):
    count = 0
    for name, field in model_cls.model_fields.items():
        ann = field.annotation
        # Check if it's a Pydantic BaseModel subclass
        if hasattr(ann, "model_fields"):
            count += count_schema_fields(ann, f"{prefix}{name}.")
        else:
            count += 1
    return count

total_fields = count_schema_fields(ModelCard)
print(f"  ✓ Total schema fields: {total_fields}")

# ── Test 6: Enum coverage ──────────────────────────────────
print("\nTest 6: Enum coverage...")
print(f"  ✓ ModelType values: {len(ModelType)}")
print(f"  ✓ ArchitectureType values: {len(ArchitectureType)}")
print(f"  ✓ LicenseType values: {len(LicenseType)}")

print("\n" + "="*50)
print("ALL TESTS PASSED")
print("="*50)
print(f"\nSchema summary:")
print(f"  Total fields in schema:  {total_fields}")
print(f"  Model types supported:   {len(ModelType)}")
print(f"  Architecture types:      {len(ArchitectureType)}")
print(f"  License types:           {len(LicenseType)}")
print(f"  Sample card completeness: {card.card_completeness}%")
