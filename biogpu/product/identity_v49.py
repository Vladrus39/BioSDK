"""BioGPU-Core v4.9 naming correction and product identity.

This module makes the naming strategy explicit after checking that several
obvious OS names are already used in adjacent/non-adjacent markets. It does
not change benchmark behavior.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List


@dataclass(frozen=True)
class NameDecision:
    name: str
    role: str
    decision: str
    rationale: str
    risk: str = ""


@dataclass(frozen=True)
class ClaimBoundary:
    claim: str
    allowed: bool
    wording: str


NAME_DECISIONS: List[NameDecision] = [
    NameDecision(
        name="BioGPU-Core",
        role="repository / technical kernel / project history",
        decision="keep",
        rationale="It preserves project continuity and names the core package, but must be explained as a runtime kernel, not a GPU replacement claim.",
        risk="Do not market as CUDA/RTX/LLM GPU replacement.",
    ),
    NameDecision(
        name="BioSDK / Living Compute SDK",
        role="developer-facing SDK layer",
        decision="keep as descriptive layer",
        rationale="Good concise phrase for clients, adapters and developer examples. Treat as descriptive/generic unless trademark clearance is done.",
        risk="BioSDK appears in biometric/biosignal contexts; legal clearance required for brand use.",
    ),
    NameDecision(
        name="BioCompute Runtime",
        role="near-term external product category",
        decision="keep as category/product descriptor",
        rationale="Accurately describes manifest-driven execution over data, adapters, benchmarks, safety and result bundles.",
        risk="BioCompute is used by other life-sciences AI products; avoid over-reliance as sole distinctive brand.",
    ),
    NameDecision(
        name="NSI-1.0 / Neural Substrate Interface",
        role="vendor-neutral interface standard",
        decision="keep and develop",
        rationale="Most defensible technical asset: schemas, adapter contracts, safety profiles and conformance tests over NWB/HDF5/vendor/API sources.",
    ),
    NameDecision(
        name="SomaOS",
        role="previous OS codename candidate",
        decision="do not use as primary public brand",
        rationale="Already used in hospitality/AI-native OS contexts; keep only as discarded internal naming exploration.",
        risk="High confusion risk.",
    ),
    NameDecision(
        name="BiC OS",
        role="new short OS codename candidate",
        decision="use as working codename only",
        rationale="Short, memorable, derived from BioCompute/Biological Interface Compute, and less misleading than BioGPU OS.",
        risk="Needs trademark/domain/package-index review; BIC is a common acronym and should not be treated as cleared.",
    ),
    NameDecision(
        name="BioCompute OS",
        role="plain long-form OS category name",
        decision="use as generic roadmap phrase",
        rationale="Good explanatory term for documents, but not distinctive enough as a final brand without clearance.",
        risk="BioCompute is used by other organizations.",
    ),
]

CLAIM_BOUNDARIES: List[ClaimBoundary] = [
    ClaimBoundary(
        claim="first biological computer / first wetware OS",
        allowed=False,
        wording="Do not claim this. Existing projects already cover wetware computers, biological APIs, electrophysiology control and neurodata standards.",
    ),
    ClaimBoundary(
        claim="vendor-neutral BioCompute Runtime / NSI layer",
        allowed=True,
        wording="Use this as the main differentiator: a cross-platform runtime/interface layer for replay, API, data, benchmarks, LLM tools, safety and result bundles.",
    ),
    ClaimBoundary(
        claim="GPU replacement for LLM",
        allowed=False,
        wording="Only discuss as original motivation and long-term inspiration; current product is not a CUDA/RTX/LLM accelerator replacement.",
    ),
    ClaimBoundary(
        claim="path toward BioCompute OS / BiC OS",
        allowed=True,
        wording="Allowed as roadmap goal after SDK, runtime, control plane, conformance tests, real adapters and lab-approved live workflows.",
    ),
]


def product_identity_v49() -> Dict[str, object]:
    return {
        "version": "4.9",
        "repository_name": "BioGPU-Core",
        "near_term_product": "BioCompute Runtime",
        "sdk_layer": "BioSDK / Living Compute SDK",
        "standard": "NSI-1.0 / Neural Substrate Interface",
        "control_plane": "BioCompute Control Plane",
        "os_working_codename": "BiC OS",
        "os_long_form": "BioCompute OS",
        "public_brand_status": "not legally cleared; use as working naming only",
        "positioning": "vendor-neutral runtime/interface layer for living neural compute and AI/LLM workflows",
        "name_decisions": [asdict(x) for x in NAME_DECISIONS],
        "claim_boundaries": [asdict(x) for x in CLAIM_BOUNDARIES],
    }


def assert_identity_v49_consistent() -> None:
    data = product_identity_v49()
    assert data["repository_name"] == "BioGPU-Core"
    assert data["os_working_codename"] == "BiC OS"
    assert data["standard"].startswith("NSI-1.0")
    assert any(x.name == "SomaOS" and "do not use" in x.decision for x in NAME_DECISIONS)
    assert any(x.claim == "vendor-neutral BioCompute Runtime / NSI layer" and x.allowed for x in CLAIM_BOUNDARIES)
