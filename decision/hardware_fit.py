"""Sourced hardware assessments for one exact topology and workload (MODEL-287)."""

from __future__ import annotations

import math
from datetime import date
from typing import Annotated, Any, Literal

from pydantic import (
    BaseModel, ConfigDict, Field, RootModel, TypeAdapter, ValidationError, model_validator,
)

from decision.model import Verification

VERSION = "2.0"
ENDPOINT = "hardware-fit"
FORMULA = (
    "For each device: kv_cache_bytes = kv_bytes_per_token * batch * context; "
    "required_bytes = weights_bytes + kv_cache_bytes + runtime_headroom_bytes; "
    "margin_bytes = capacity_bytes - required_bytes. "
    "estimated_fit = likely if every margin_bytes >= 0, otherwise unlikely."
)
LOWER_BOUND_FORMULA = (
    "For each device: kv_cache_bytes = kv_bytes_per_token * batch * context; "
    "lower_bound_bytes = weights_bytes + kv_cache_bytes; "
    "margin_bytes = capacity_bytes - lower_bound_bytes. "
    "estimated_fit = unlikely if any margin_bytes < 0; otherwise undetermined without runtime headroom."
)

Text = Annotated[str, Field(strict=True, min_length=1, max_length=512, pattern=r"\S")]
DeviceCount = Annotated[int, Field(strict=True, ge=1, le=1024)]
Batch = Annotated[int, Field(strict=True, ge=1, le=1_000_000)]
Context = Annotated[int, Field(strict=True, ge=1, le=1_000_000_000)]
MemoryGB = Annotated[float, Field(strict=True, gt=0, le=1_000_000, allow_inf_nan=False)]
PositiveBytes = Annotated[int, Field(strict=True, gt=0)]
Number = (Annotated[int, Field(strict=True, ge=0)]
          | Annotated[float, Field(strict=True, ge=0, allow_inf_nan=False)])


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid")


class HardwareFitRequest(Record):
    model: Text | None = None
    sku: Text | None = None
    device_count: DeviceCount | None = None
    memory: MemoryGB | None = None
    runtime: Text | None = None
    quantisation: Text | None = None
    batch: Batch | None = None
    context: Context | None = None


class SourcedNumber(Record):
    value: Number
    record_id: Text
    source_ids: list[Text] = Field(min_length=1)


class DeviceInputs(Record):
    weights_bytes: SourcedNumber
    kv_bytes_per_token: SourcedNumber
    runtime_headroom_bytes: SourcedNumber | None = None

    @model_validator(mode="after")
    def resident_weights(self):
        if self.weights_bytes.value <= 0:
            raise ValueError("resident weights must be positive")
        return self


class WorkloadRecord(Record):
    id: Text
    model: Text
    sku: Text
    device_count: DeviceCount
    runtime: Text
    quantisation: Text
    batch: Batch
    context: Context
    memory_bytes_per_device: PositiveBytes
    observed_at: date
    source_ids: list[Text] = Field(min_length=1)
    verification: Verification | None = None


class MeasuredRecord(WorkloadRecord):
    status: Literal["measured"]
    measured_fit: Annotated[bool, Field(strict=True)]
    measured_memory_bytes: list[SourcedNumber] = Field(min_length=1, max_length=1024)

    @model_validator(mode="after")
    def device_observations(self):
        if len(self.measured_memory_bytes) != self.device_count:
            raise ValueError("measurement needs one memory observation per device")
        if self.measured_fit and any(
            value.value > self.memory_bytes_per_device for value in self.measured_memory_bytes
        ):
            raise ValueError("successful measurement exceeds the recorded capacity")
        return self


class EstimatedRecord(WorkloadRecord):
    status: Literal["estimated"]
    per_device: list[DeviceInputs] = Field(min_length=1, max_length=1024)

    @model_validator(mode="after")
    def device_allocations(self):
        if len(self.per_device) != self.device_count:
            raise ValueError("estimate needs one allocation per device")
        return self


HardwareFitRecord = Annotated[MeasuredRecord | EstimatedRecord, Field(discriminator="status")]
RECORD_ADAPTER = TypeAdapter(HardwareFitRecord)


def numeric_inputs(record: MeasuredRecord | EstimatedRecord) -> list[SourcedNumber]:
    if isinstance(record, MeasuredRecord):
        return record.measured_memory_bytes
    return [value for device in record.per_device for value in (
        device.weights_bytes, device.kv_bytes_per_token, device.runtime_headroom_bytes)
            if value is not None]


class Citation(Record):
    id: Text
    url: str


class Provenance(Record):
    value: Number
    record_id: Text | None
    source_ids: list[Text]
    provenance: Literal["sourced", "caller"]
    observed_at: date | None = None


class ExhaustedCredits(Record):
    exhausted: Literal[True]
    available: Annotated[int, Field(strict=True)]
    needed: Annotated[int, Field(strict=True)]
    unit: Literal["credit"]
    message: str
    buy: str


class CommonResponse(Record):
    hardware_fit_version: Literal["2.0"] = VERSION
    endpoint: Literal["hardware-fit"] = ENDPOINT
    snapshot: str
    request: HardwareFitRequest
    sources: list[Citation]
    credits: ExhaustedCredits | None = None


class MissingInput(Record):
    input: Text
    reason: Text


class UndeterminedResponse(CommonResponse):
    status: Literal["undetermined"]
    missing: list[MissingInput] = Field(min_length=1)


class Measurement(Record):
    record_id: Text
    source_ids: list[Text]
    observed_at: date
    memory_bytes_per_device: PositiveBytes
    measured_memory_bytes: list[SourcedNumber]
    verification: Verification


class MeasuredResponse(CommonResponse):
    status: Literal["measured"]
    measured_fit: bool
    measurement: Measurement
    capacity_bytes: Provenance
    model_context_max: Provenance


class DeviceEstimate(DeviceInputs):
    runtime_headroom_bytes: SourcedNumber
    device: Annotated[int, Field(strict=True, ge=0)]
    kv_cache_bytes: Number
    required_bytes: Number
    margin_bytes: int | float


class EstimateBase(CommonResponse):
    status: Literal["estimated"]
    margin_bytes: int | float
    formula: str
    record_id: Text
    observed_at: date
    verification: Verification
    capacity_bytes: Provenance
    model_context_max: Provenance
    assumptions: list[str] = Field(min_length=1)


class FullEstimatedResponse(EstimateBase):
    basis: Literal["full"]
    estimated_fit: Literal["likely", "unlikely"]
    per_device: list[DeviceEstimate]


class HeadroomNotRequired(Record):
    status: Literal["not_required"] = "not_required"
    reason: Text = "Runtime headroom is not required to establish this lower bound."


class LowerBoundDeviceEstimate(Record):
    device: Annotated[int, Field(strict=True, ge=0)]
    weights_bytes: SourcedNumber
    kv_bytes_per_token: SourcedNumber
    runtime_headroom_bytes: SourcedNumber | HeadroomNotRequired
    kv_cache_bytes: Number
    lower_bound_bytes: Number
    margin_bytes: int | float


class LowerBoundEstimatedResponse(EstimateBase):
    basis: Literal["lower_bound"]
    estimated_fit: Literal["unlikely"]
    per_device: list[LowerBoundDeviceEstimate]


class EstimatedResponse(RootModel[
    Annotated[FullEstimatedResponse | LowerBoundEstimatedResponse, Field(discriminator="basis")]
]):
    pass


class HardwareFitResponse(RootModel[
    Annotated[MeasuredResponse | EstimatedResponse | UndeterminedResponse,
              Field(discriminator="status")]
]):
    pass


def check(payload: Any, snapshot: Any, expected_snapshot: str | None = None) -> tuple[int, dict]:
    """Assess the exact request against admitted, signed snapshot records."""
    base = {"hardware_fit_version": VERSION, "endpoint": ENDPOINT, "snapshot": snapshot.snapshot_id}
    if expected_snapshot is not None and expected_snapshot != snapshot.snapshot_id:
        return 409, {**base, "error": {"code": "snapshot_changed",
                                      "message": "The requested snapshot is no longer current."}}
    try:
        request = HardwareFitRequest.model_validate(payload)
    except ValidationError as exc:
        return 400, {**base, "error": {
            "code": "invalid_request", "message": "Invalid hardware-fit request.",
            "issues": [{"path": ".".join(str(part) for part in row["loc"]),
                        "message": row["msg"]} for row in exc.errors()],
        }}
    common = {**base, "request": request.model_dump(exclude_none=True), "sources": []}

    def unknown(*missing):
        return 200, {**common, "status": "undetermined", "missing": [
            {"input": key, "reason": reason} for key, reason in missing]}

    fields = ("model", "sku", "device_count", "runtime", "quantisation", "batch", "context")
    missing = [(field, "required request input is missing") for field in fields
               if getattr(request, field) is None]
    if missing:
        return unknown(*missing)
    if request.model not in snapshot.candidates() or snapshot.kind(request.model) != "model":
        return unknown(("model", "model ID is not in this snapshot"))
    device = snapshot.hardware_device(request.sku)
    if device is None:
        return unknown(("sku", "SKU is not in this snapshot"))
    if not device.get("record_id"):
        return unknown(("sku", device.get("unknown_reason") or device.get("refusal_reason")
                        or "sourced per-device capacity is missing"))
    hardware_record = snapshot.record(device["record_id"])
    memory_options = hardware_record["memory"].get("capacity_options_gb") or [
        hardware_record["memory"]["capacity_gb"]]
    if request.memory is None and len(set(memory_options)) > 1:
        return unknown(("memory", "SKU has several memory configurations; specify GB per device"))
    capacity = request.memory if request.memory is not None else device["memory_capacity_gb"]
    capacity_bytes = int(capacity * 1_000_000_000)
    context_max = snapshot.fact(request.model, "model.context_window")
    if (context_max.state != "known" or type(context_max.value) not in (int, float)
            or not context_max.sources or not context_max.record_id):
        return unknown(("context", "verified model maximum context is missing"))
    if request.context > context_max.value:
        common["sources"] = [{"id": sid, "url": snapshot.source_url(sid)}
                             for sid in sorted(context_max.sources)]
        return unknown(("context", f"requested context exceeds verified model maximum {context_max.value}"))
    openness = snapshot.fact(request.model, "model.weights_openness")
    records = snapshot.hardware_fit_records(request.model, request.sku)
    exact = [row for row in records if all(row[field] == getattr(request, field) for field in fields)
             and row["memory_bytes_per_device"] == capacity_bytes]
    measured = [row for row in exact if row["status"] == "measured"]
    if not measured:
        if not device.get("single_device_fit", True):
            return unknown(("sku", device.get("refusal_reason")
                            or "SKU does not expose one usable memory pool"))
        if openness.state != "known" or openness.value != "open_weights":
            return unknown(("model", "verified self-hostable open weights are missing"))
    if not exact:
        if records and not any(row["quantisation"] == request.quantisation for row in records):
            return unknown(("quantisation", "no sourced record exists for this quantisation"))
        return unknown(
            ("hardware_fit_record", "no verified record binds this exact topology, workload and memory"),
            ("weights_bytes", "verified resident weight bytes for this request are missing"),
            ("kv_bytes_per_token", "verified per-device KV bytes for this request are missing"),
            ("runtime_headroom_bytes", "verified runtime headroom for this request is missing"),
        )
    if measured and len({row["measured_fit"] for row in measured}) > 1:
        return unknown(("measurement", "verified measurements disagree for this exact request"))
    candidates = measured or exact
    if not measured and len({tuple(
        (device["weights_bytes"]["value"], device["kv_bytes_per_token"]["value"],
         device["runtime_headroom_bytes"]["value"] if device.get("runtime_headroom_bytes") is not None
         else None) for device in row["per_device"])
                             for row in candidates}) > 1:
        return unknown(("estimate", "verified estimate inputs disagree for this exact request"))
    row = max(candidates, key=lambda item: (item["observed_at"], item["id"]))
    source_ids = set(row["source_ids"]) | set(context_max.sources)
    if not measured:
        source_ids.update(openness.sources)
    source_ids.update(device["source_ids"])
    source_ids.update(sid for value in numeric_inputs(RECORD_ADAPTER.validate_python(row))
                      for sid in value.source_ids)
    common["sources"] = [{"id": sid, "url": snapshot.source_url(sid)} for sid in sorted(source_ids)]
    capacity_input = {
        "value": capacity_bytes, "provenance": "caller" if request.memory is not None else "sourced",
        "record_id": None if request.memory is not None else device["record_id"],
        "source_ids": [] if request.memory is not None else device["source_ids"],
        "observed_at": None if request.memory is not None else hardware_record["verified_at"],
    }
    context_record = snapshot.record(context_max.record_id)
    context_input = {"value": context_max.value, "record_id": context_max.record_id,
                     "source_ids": list(context_max.sources), "provenance": "sourced",
                     "observed_at": context_record["verification"]["date"]}
    if measured:
        return 200, {**common, "status": "measured", "measured_fit": row["measured_fit"],
                     "capacity_bytes": capacity_input, "model_context_max": context_input,
                     "measurement": {"record_id": row["id"], "source_ids": row["source_ids"],
                                     "observed_at": row["observed_at"],
                                     "memory_bytes_per_device": row["memory_bytes_per_device"],
                                     "measured_memory_bytes": row["measured_memory_bytes"],
                                     "verification": row["verification"]}}
    missing_headroom = [index for index, allocation in enumerate(row["per_device"])
                        if allocation.get("runtime_headroom_bytes") is None]
    basis = "lower_bound" if missing_headroom else "full"
    memory_field = "lower_bound_bytes" if missing_headroom else "required_bytes"
    calculations = []
    for index, allocation in enumerate(row["per_device"]):
        kv_bytes = allocation["kv_bytes_per_token"]["value"] * request.batch * request.context
        if isinstance(kv_bytes, float) and not math.isfinite(kv_bytes):
            return unknown(("kv_cache_bytes", "the cited inputs overflow the KV calculation"))
        required = allocation["weights_bytes"]["value"] + kv_bytes
        if not missing_headroom:
            required += allocation["runtime_headroom_bytes"]["value"]
        if isinstance(required, float) and not math.isfinite(required):
            return unknown((memory_field, "the cited inputs overflow the memory calculation"))
        headroom = allocation.get("runtime_headroom_bytes")
        calculations.append({**allocation, "device": index, "kv_cache_bytes": kv_bytes,
                             "runtime_headroom_bytes": headroom if headroom is not None
                             else HeadroomNotRequired().model_dump(),
                             memory_field: required, "margin_bytes": capacity_bytes - required})
    margin = min(device["margin_bytes"] for device in calculations)
    if missing_headroom and margin >= 0:
        devices = f"devices {missing_headroom}" if len(missing_headroom) <= 8 else f"{len(missing_headroom)} devices"
        return unknown(("runtime_headroom_bytes",
                        f"Verified runtime headroom is missing for {devices}; "
                        "their lower bounds do not establish fit."))
    assumptions = [
        "This is an estimate; runtime execution and successful fit have not been established.",
        "Every device uses the cited allocation for this exact runtime, quantisation, batch and context.",
        "Device memory is evaluated separately and is never pooled.",
        "Batch and context are caller inputs; KV allocation scales as batch times context using the cited per-token value.",
    ]
    if request.memory is not None:
        assumptions.append("Memory capacity is the caller's override in decimal GB per device.")
    if missing_headroom:
        assumptions.append("The lower bound excludes runtime headroom on every device; omitted headroom is not zero.")
    return 200, {**common, "status": "estimated", "estimated_fit": "likely" if margin >= 0 else "unlikely",
                 "basis": basis, "margin_bytes": margin,
                 "formula": LOWER_BOUND_FORMULA if missing_headroom else FORMULA, "record_id": row["id"],
                 "observed_at": row["observed_at"], "verification": row["verification"],
                 "capacity_bytes": capacity_input,
                 "model_context_max": context_input, "per_device": calculations,
                 "assumptions": assumptions}
