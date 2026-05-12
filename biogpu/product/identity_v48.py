"""BioGPU-Core v4.8 product identity map.

This module is intentionally non-operational: it gives the project a durable
commercial/technical vocabulary without changing benchmark behaviour.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List


@dataclass(frozen=True)
class ProductName:
    name: str
    role: str
    keep: bool
    public_use: str
    warning: str = ""


@dataclass(frozen=True)
class RoadmapStage:
    stage: str
    label: str
    purpose: str
    readiness: str
    deliverables: List[str]


PRODUCT_NAMES: List[ProductName] = [
    ProductName(
        name="BioGPU-Core",
        role="technical kernel / project codename",
        keep=True,
        public_use=(
            "Use as the repository/core engine name. It preserves the history of the project, "
            "but must not be marketed as a direct GPU/CUDA replacement."
        ),
        warning="Avoid standalone GPU-replacement claims.",
    ),
    ProductName(
        name="BioCompute Runtime",
        role="primary external product name",
        keep=True,
        public_use="Use as the main product description for the runtime that executes manifests, benchmarks, adapters and result bundles.",
    ),
    ProductName(
        name="BioSDK / Living Compute SDK",
        role="developer-facing SDK layer",
        keep=True,
        public_use="Use for client libraries, examples, adapter development and integration with enterprise/lab workflows.",
        warning="BioSDK is a generic term used elsewhere; do trademark/domain checks before legal branding.",
    ),
    ProductName(
        name="NSI-1.0 / Neural Substrate Interface",
        role="interface standard draft",
        keep=True,
        public_use="Use for the vendor-neutral schema/contract: traces, manifests, readouts, bundles, safety profiles and adapter conformance.",
    ),
    ProductName(
        name="BioCompute Control Plane",
        role="hosted/on-prem server layer",
        keep=True,
        public_use="Use for the future server, job queue, permissions, storage, audit, teams and dashboards.",
    ),
    ProductName(
        name="BioCompute OS",
        role="long-term OS-like goal",
        keep=True,
        public_use="Use as the long-term roadmap target after runtime, control plane, real adapters and lab-approved live workflows exist.",
        warning="Do not claim OS status until persistent services, scheduling, devices, permissions and live safety supervisor exist.",
    ),
]


ROADMAP: List[RoadmapStage] = [
    RoadmapStage(
        stage="R0",
        label="Evidence-preserving research archive",
        purpose="Keep v12-v47 real-data results, matrices and reports reproducible.",
        readiness="done in v4.7 evidence pack",
        deliverables=["pulse_feature_matrix", "v12/v15/v32/v33/v36 outputs", "PC runner scripts"],
    ),
    RoadmapStage(
        stage="R1",
        label="BioSDK / Living Compute SDK",
        purpose="Developer-facing package for replay, read-only imports, result bundles and adapter writing.",
        readiness="partial / ready for power-PC validation",
        deliverables=["CLI", "schemas", "sample manifests", "data asset registry", "adapter conformance tests"],
    ),
    RoadmapStage(
        stage="R2",
        label="BioCompute Runtime",
        purpose="Manifest-driven execution engine for datasets, readouts, benchmarks, safety and bundles.",
        readiness="architectural prototype exists",
        deliverables=["runtime manifest", "job runner", "benchmark registry", "bundle generator", "audit logs"],
    ),
    RoadmapStage(
        stage="R3",
        label="NSI-1.0 standard draft",
        purpose="Vendor-neutral interface profile over NWB/HDF5/vendor exports/API streams.",
        readiness="draft in v4.8",
        deliverables=["Trace schema", "TaskManifest schema", "ResultBundle schema", "SafetyProfile", "AdapterContract"],
    ),
    RoadmapStage(
        stage="R4",
        label="BioCompute Control Plane",
        purpose="Hosted/on-prem service for users, jobs, datasets, quotas, storage and dashboards.",
        readiness="server scaffold exists; production missing",
        deliverables=["auth", "DB", "job queue", "object storage", "API keys", "team workspaces", "admin dashboard"],
    ),
    RoadmapStage(
        stage="R5",
        label="BioCompute OS",
        purpose="OS-like layer for device/session management, scheduler, permissions, telemetry and lab-approved live workflows.",
        readiness="long-term goal",
        deliverables=["daemon", "device manager", "plugin system", "safety supervisor", "operator approvals", "live telemetry"],
    ),
]


def product_identity() -> Dict[str, object]:
    return {
        "version": "4.8",
        "keep_repository_name": "BioGPU-Core",
        "primary_external_name": "BioCompute Runtime",
        "sdk_name": "BioSDK / Living Compute SDK",
        "interface_standard": "NSI-1.0 / Neural Substrate Interface",
        "long_term_goal": "BioCompute OS",
        "gpu_claim_policy": "BioGPU-Core is not marketed as a GPU/CUDA/LLM accelerator replacement until live evidence proves narrow task advantage.",
        "names": [asdict(x) for x in PRODUCT_NAMES],
        "roadmap": [asdict(x) for x in ROADMAP],
    }


def assert_identity_consistent() -> None:
    data = product_identity()
    assert data["keep_repository_name"] == "BioGPU-Core"
    assert data["primary_external_name"] == "BioCompute Runtime"
    assert any(n.name == "BioCompute OS" for n in PRODUCT_NAMES)
    assert any(stage.stage == "R3" and "NSI" in stage.label for stage in ROADMAP)
