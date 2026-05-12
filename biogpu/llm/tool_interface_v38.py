"""BioGPU v3.8 BioLLM Tool Interface.

This module exposes BioGPU-Core as a structured tool that an LLM/agent can call.
It is intentionally safe-by-default: replay/read-only/API-shadow inputs are allowed,
but live stimulation, electrode actuation, wiring, wet-lab recipes, and environment
control are blocked by the central safety boundary.

The purpose is commercial/enterprise SDK readiness: a customer can integrate the
BioSDK into an agent workflow, validate manifests, read data, obtain a BioGPUTrace,
compute features, run a readout, and return a structured result to the LLM.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Iterable
from datetime import datetime, timezone
import json
import math
import statistics
import uuid

from biogpu.apis.base_external_api_v37 import APIAccessModeV37, BioGPUTraceV37, PermissionDeniedV37
from biogpu.apis.registry_v37 import make_external_api_client_v37, list_external_api_platforms_v37
from biogpu.readout.base_v27 import ReadoutFeatureBatch
from biogpu.readout.registry_v27 import build_readout_registry_v27
from biogpu.safety.boundary_v35 import assert_no_forbidden_payload_v35


class BioLLMModeV38(str, Enum):
    """Allowed operational modes for the LLM-facing tool interface."""

    METADATA_ONLY = "metadata_only"
    API_READ_ONLY = "api_read_only"
    REPLAY = "replay"
    LIVE_SHADOW = "live_shadow"


@dataclass(frozen=True)
class BioLLMTaskV38:
    """User/agent task request passed into the BioGPU tool layer."""

    task_id: str
    user_goal: str
    mode: str = BioLLMModeV38.REPLAY.value
    platform: str = "mcs_mea2100"
    decoder_id: str = "centroid_v27"
    duration_s: float = 1.0
    input_payload: dict[str, Any] = field(default_factory=dict)
    allowed_claim_level: str = "software_replay_or_read_only_api_only"

    def validate(self) -> None:
        if not self.task_id:
            raise ValueError("task_id is required")
        if not self.user_goal:
            raise ValueError("user_goal is required")
        if BioLLMModeV38(self.mode) not in set(BioLLMModeV38):
            raise ValueError(f"unsupported mode: {self.mode}")
        if self.duration_s <= 0:
            raise ValueError("duration_s must be positive")
        assert_no_forbidden_payload_v35(self.to_dict(), context="BioLLMTaskV38")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BioLLMManifestV38:
    """Machine-readable manifest generated from an LLM/agent task."""

    manifest_id: str
    task: dict[str, Any]
    selected_platform: str
    selected_decoder: str
    mode: str
    created_utc: str
    expected_io: dict[str, Any]
    safety: dict[str, Any]
    commercial_tier_hint: str = "Enterprise Read-Only SDK / Live Shadow candidate"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BioLLMFeatureRecordV38:
    """Feature summary extracted from a BioGPUTrace for LLM-readable output."""

    feature_names: tuple[str, ...]
    values: tuple[float, ...]
    source_trace_platform: str
    source_trace_adapter: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BioLLMToolResultV38:
    """Structured result returned back to an LLM/agent."""

    status: str
    manifest_id: str
    task_id: str
    llm_tool_name: str
    structured_result: dict[str, Any]
    claim_level: str
    safety: dict[str, Any]
    trace_summary: dict[str, Any]
    readout_prediction: dict[str, Any] | None
    audit_events: tuple[dict[str, Any], ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BioLLMCommercialTierV38:
    tier: str
    allowed_modes: tuple[str, ...]
    customer_value: str
    restrictions: tuple[str, ...]
    monetization: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def utc_now_v38() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def default_biollm_commercial_tiers_v38() -> list[BioLLMCommercialTierV38]:
    """Commercial packaging ladder for LLM/agent integrations."""

    return [
        BioLLMCommercialTierV38(
            tier="Developer Evaluation",
            allowed_modes=(BioLLMModeV38.METADATA_ONLY.value, BioLLMModeV38.REPLAY.value),
            customer_value="prove SDK integration, run demos, inspect manifests and result bundles",
            restrictions=("no external wetware credentials", "no live stream", "no control"),
            monetization="free/community or low-cost developer license",
        ),
        BioLLMCommercialTierV38(
            tier="Enterprise Read-Only BioSDK",
            allowed_modes=(BioLLMModeV38.METADATA_ONLY.value, BioLLMModeV38.API_READ_ONLY.value, BioLLMModeV38.REPLAY.value),
            customer_value="connect enterprise API/export data to LLM workflows and auditable BioGPUTrace outputs",
            restrictions=("no actuation", "no stimulation", "vendor/lab data policy applies"),
            monetization="annual SDK subscription + connector support",
        ),
        BioLLMCommercialTierV38(
            tier="Enterprise Live Shadow BioSDK",
            allowed_modes=(BioLLMModeV38.LIVE_SHADOW.value, BioLLMModeV38.API_READ_ONLY.value, BioLLMModeV38.REPLAY.value),
            customer_value="LLM/agent sees live biological signal and produces recommendations without controlling the experiment",
            restrictions=("no writes", "human/operator remains in control", "compliance logs required"),
            monetization="premium annual license + deployment fee + support SLA",
        ),
        BioLLMCommercialTierV38(
            tier="Lab-Approved Closed Loop Add-on",
            allowed_modes=(),
            customer_value="future controlled closed-loop enterprise module after vendor/lab approval",
            restrictions=("not included in v3.8", "requires signed SOP", "requires explicit approval"),
            monetization="separate contract, milestones, validation services, possible royalty",
        ),
    ]


def _trace_to_feature_record_v38(trace: BioGPUTraceV37) -> BioLLMFeatureRecordV38:
    spikes = list(trace.spike_events)
    samples = list(trace.trace_samples)
    duration = max(float(trace.duration_s), 1e-9)
    spike_count = float(len(spikes))
    unique_channels = float(len({int(e.get("channel", -1)) for e in spikes}))
    spike_rate_hz = spike_count / duration
    sample_values = [abs(float(s.get("value", 0.0))) for s in samples]
    mean_abs_trace = float(statistics.fmean(sample_values)) if sample_values else 0.0
    trace_energy = float(sum(v * v for v in sample_values) / max(1, len(sample_values)))
    values = (spike_count, unique_channels, spike_rate_hz, mean_abs_trace, trace_energy)
    names = ("spike_count", "unique_channels", "spike_rate_hz", "mean_abs_trace", "trace_energy")
    return BioLLMFeatureRecordV38(
        feature_names=names,
        values=tuple(round(v, 6) for v in values),
        source_trace_platform=trace.platform,
        source_trace_adapter=trace.adapter_name,
    )


def _training_batch_for_tool_v38(feature_names: Iterable[str]) -> ReadoutFeatureBatch:
    names = list(feature_names)
    # Lightweight, deterministic calibration set for SDK/demo/tool integration.
    # It is not a scientific model and is flagged as such in result metadata.
    X = [
        [1.0, 1.0, 1.0, 0.04, 0.002],
        [4.0, 2.0, 4.0, 0.10, 0.010],
        [12.0, 5.0, 12.0, 0.35, 0.120],
        [32.0, 16.0, 32.0, 0.65, 0.420],
    ]
    y = ["low_activity", "low_activity", "activity_detected", "activity_detected"]
    return ReadoutFeatureBatch(feature_names=names, X=X, y=y, metadata={"v38_demo_calibration": True})


def _normalize_platform_v38(platform: str) -> str:
    mapping = {
        "finalspark": "finalspark_remote_wetware",
        "finalspark_remote_wetware": "finalspark_remote_wetware",
        "threebrain": "threebrain_hdmea",
        "3brain": "threebrain_hdmea",
        "threebrain_hdmea": "threebrain_hdmea",
        "axion": "axion_maestro",
        "axion_maestro": "axion_maestro",
        "mcs": "mcs_mea2100",
        "mcs_mea2100": "mcs_mea2100",
        "mea2100": "mcs_mea2100",
    }
    try:
        return mapping[platform.strip().lower()]
    except KeyError as exc:
        known = ", ".join(list_external_api_platforms_v37())
        raise ValueError(f"Unknown v3.8 BioLLM platform {platform!r}; known: {known}") from exc


class BioLLMToolInterfaceV38:
    """LLM-facing tool wrapper around BioGPU-Core.

    The interface is designed for enterprise SDK use: LLM agents can call it as a
    structured tool, but safety and claim boundaries travel with every result.
    """

    tool_name = "biogpu_biollm_tool_v38"

    def build_manifest(self, task: BioLLMTaskV38) -> BioLLMManifestV38:
        task.validate()
        platform = _normalize_platform_v38(task.platform)
        mode = BioLLMModeV38(task.mode)
        expected_io = {
            "input": "BioLLMTaskV38",
            "intermediate": ["BioLLMManifestV38", "BioGPUTraceV37", "BioLLMFeatureRecordV38"],
            "output": "BioLLMToolResultV38",
        }
        safety = {
            "live_output_performed": False,
            "writes_allowed": False,
            "allowed_modes_v38": [m.value for m in BioLLMModeV38],
            "blocked_operations": [
                "send_stimulation_pattern",
                "update_environment",
                "vendor_pinout",
                "wetlab_recipe",
                "unapproved_closed_loop_actuation",
            ],
            "mode_note": f"{mode.value} is safe-by-default and cannot actuate live biology in v3.8",
        }
        manifest = BioLLMManifestV38(
            manifest_id=f"v38-{uuid.uuid4().hex[:12]}",
            task=task.to_dict(),
            selected_platform=platform,
            selected_decoder=task.decoder_id,
            mode=mode.value,
            created_utc=utc_now_v38(),
            expected_io=expected_io,
            safety=safety,
        )
        assert_no_forbidden_payload_v35(manifest.to_dict(), context="BioLLMManifestV38")
        return manifest

    def _api_access_mode_for_llm_mode(self, mode: BioLLMModeV38) -> str:
        if mode == BioLLMModeV38.METADATA_ONLY:
            return APIAccessModeV37.METADATA_ONLY.value
        if mode == BioLLMModeV38.LIVE_SHADOW:
            return APIAccessModeV37.LIVE_SHADOW.value
        return APIAccessModeV37.READ_ONLY.value

    def _make_trace(self, manifest: BioLLMManifestV38) -> BioGPUTraceV37 | None:
        mode = BioLLMModeV38(manifest.mode)
        access_mode = self._api_access_mode_for_llm_mode(mode)
        client = make_external_api_client_v37(manifest.selected_platform, access_mode=access_mode)
        client.connect()
        try:
            if mode == BioLLMModeV38.METADATA_ONLY:
                return None
            # replay and api_read_only both use mock/read-only client export in v3.8.
            return client.export_biogpu_trace(duration_s=float(manifest.task.get("duration_s", 1.0)))
        finally:
            client.close()

    def run(self, task: BioLLMTaskV38) -> BioLLMToolResultV38:
        manifest = self.build_manifest(task)
        audit: list[dict[str, Any]] = [
            {"event": "manifest_created", "timestamp_utc": utc_now_v38(), "manifest_id": manifest.manifest_id},
        ]
        trace = self._make_trace(manifest)
        if trace is None:
            structured = {
                "biogpu_signal": "metadata_only_no_trace",
                "confidence": None,
                "recommendation_to_llm": "Use this result only to confirm SDK/API visibility; no biological data were read.",
                "platform": manifest.selected_platform,
            }
            trace_summary = {"trace_available": False, "platform": manifest.selected_platform}
            prediction = None
            audit.append({"event": "metadata_only_completed", "timestamp_utc": utc_now_v38()})
        else:
            feature = _trace_to_feature_record_v38(trace)
            registry = build_readout_registry_v27()
            if manifest.selected_decoder not in registry:
                raise ValueError(f"Unknown decoder {manifest.selected_decoder!r}; available: {sorted(registry)}")
            decoder = registry[manifest.selected_decoder]
            batch = _training_batch_for_tool_v38(feature.feature_names)
            decoder.fit(batch)
            pred = decoder.predict_one(feature.values, feature_names=list(feature.feature_names))
            prediction = pred.to_dict()
            structured = {
                "biogpu_signal": str(pred.prediction),
                "confidence": pred.confidence,
                "features": feature.to_dict(),
                "recommendation_to_llm": (
                    "Treat as BioSDK integration/readout signal, not as live wetware proof. "
                    "Use claim_level before making scientific or commercial claims."
                ),
                "platform": manifest.selected_platform,
                "mode": manifest.mode,
            }
            trace_summary = {
                "trace_available": True,
                "platform": trace.platform,
                "adapter": trace.adapter_name,
                "spike_events": len(trace.spike_events),
                "trace_samples": len(trace.trace_samples),
                "duration_s": trace.duration_s,
                "source": trace.source,
            }
            audit.append({"event": "trace_exported", "timestamp_utc": utc_now_v38(), "trace_summary": trace_summary})
            audit.append({"event": "readout_completed", "timestamp_utc": utc_now_v38(), "decoder_id": manifest.selected_decoder})

        safety = {
            **manifest.safety,
            "trace_source_live_actuation": False,
            "claim_boundary": task.allowed_claim_level,
            "enterprise_default_access": "read-only first; live control requires separate lab-approved module",
        }
        result = BioLLMToolResultV38(
            status="ok",
            manifest_id=manifest.manifest_id,
            task_id=task.task_id,
            llm_tool_name=self.tool_name,
            structured_result=structured,
            claim_level=task.allowed_claim_level,
            safety=safety,
            trace_summary=trace_summary,
            readout_prediction=prediction,
            audit_events=tuple(audit),
        )
        assert_no_forbidden_payload_v35(result.to_dict(), context="BioLLMToolResultV38")
        return result


def run_biollm_tool_demo_v38(platform: str = "mcs_mea2100", decoder_id: str = "centroid_v27") -> dict[str, Any]:
    task = BioLLMTaskV38(
        task_id="demo_biollm_v38",
        user_goal="Use BioGPU as an LLM-callable read-only biological signal tool",
        mode=BioLLMModeV38.API_READ_ONLY.value,
        platform=platform,
        decoder_id=decoder_id,
        duration_s=1.0,
        input_payload={"prompt_intent": "detect whether biological/replay activity is present"},
    )
    interface = BioLLMToolInterfaceV38()
    result = interface.run(task)
    return result.to_dict()


def save_json_v38(obj: Any, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
