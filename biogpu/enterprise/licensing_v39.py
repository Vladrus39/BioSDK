"""BioGPU-Core v3.9 Enterprise Packaging / Licensing Layer.

This module defines the commercial product structure for BioGPU-Core as a BioSDK
for living neural compute. It is intentionally a packaging/governance layer, not
an uncontrolled live-lab backend.

Commercial intent:
- customers can evaluate replay/mock/metadata modes;
- enterprise customers can license read-only BioSDK connectors and result bundles;
- live-shadow mode can be sold as a higher tier without actuation;
- lab-approved closed-loop modules are future add-ons gated by vendor/lab SOP.

Safety boundary:
- no live stimulation parameters;
- no wet-lab recipes;
- no physical wiring/pinout;
- no claims of GPU advantage without matched measurements.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any

from biogpu.safety.boundary_v35 import assert_no_forbidden_payload_v35, safety_boundary_summary_v35


class BioSDKDeploymentModeV39(str, Enum):
    """Commercial deployment modes supported by v3.9 package planning."""

    LOCAL_REPLAY = "local_replay"
    ENTERPRISE_READ_ONLY = "enterprise_read_only"
    LIVE_SHADOW = "live_shadow"
    LAB_APPROVED_CLOSED_LOOP = "lab_approved_closed_loop"


class BioSDKSupportLevelV39(str, Enum):
    """Support/SLA boundary labels for enterprise packaging."""

    COMMUNITY = "community"
    STANDARD = "standard"
    PREMIUM = "premium"
    LAB_PARTNER = "lab_partner"


@dataclass(frozen=True)
class BioSDKLicenseTierV39:
    """A commercial SKU/tier for BioGPU-Core."""

    tier_id: str
    display_name: str
    intended_customer: str
    allowed_deployment_modes: tuple[str, ...]
    included_components: tuple[str, ...]
    blocked_components: tuple[str, ...]
    monetization_model: str
    support_level: str
    compliance_boundary: str
    suggested_price_band: str
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def validate(self) -> None:
        assert self.tier_id
        assert self.display_name
        assert self.allowed_deployment_modes
        assert_no_forbidden_payload_v35(self.to_dict(), context=f"license_tier:{self.tier_id}")
        # v3.9 must not silently sell closed-loop as already available.
        if BioSDKDeploymentModeV39.LAB_APPROVED_CLOSED_LOOP.value in self.allowed_deployment_modes:
            if "future" not in self.compliance_boundary.lower() and "lab" not in self.compliance_boundary.lower():
                raise ValueError("Closed-loop tier must explicitly remain lab/vendor-gated.")


@dataclass(frozen=True)
class BioSDKDeploymentModeSpecV39:
    """A deployment mode with safety and commercialization requirements."""

    mode: str
    purpose: str
    allowed_actions: tuple[str, ...]
    denied_actions: tuple[str, ...]
    required_artifacts: tuple[str, ...]
    minimum_customer_readiness: str
    commercialization_status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def validate(self) -> None:
        assert self.mode
        assert self.allowed_actions
        assert self.denied_actions
        assert_no_forbidden_payload_v35(self.to_dict(), context=f"deployment_mode:{self.mode}")


@dataclass(frozen=True)
class BioSDKSupportSpecV39:
    """Support and SLA boundary for a commercial tier."""

    level: str
    response_boundary: str
    included_services: tuple[str, ...]
    excluded_services: tuple[str, ...]
    enterprise_artifacts: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def validate(self) -> None:
        assert self.level
        assert_no_forbidden_payload_v35(self.to_dict(), context=f"support_level:{self.level}")


@dataclass(frozen=True)
class BioSDKPartnerOnboardingItemV39:
    """Checklist item for enterprise/lab partner onboarding."""

    phase: str
    item: str
    owner: str
    required_before_paid_use: bool
    evidence: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BioSDKCommercialPackageV39:
    """Complete v3.9 enterprise package manifest."""

    version: str
    product_name: str
    positioning: str
    license_tiers: tuple[BioSDKLicenseTierV39, ...]
    deployment_modes: tuple[BioSDKDeploymentModeSpecV39, ...]
    support_levels: tuple[BioSDKSupportSpecV39, ...]
    onboarding_checklist: tuple[BioSDKPartnerOnboardingItemV39, ...]
    safety_summary: dict[str, Any]
    claim_boundary: tuple[str, ...]
    revenue_logic: tuple[str, ...]
    next_version: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["license_tiers"] = [t.to_dict() for t in self.license_tiers]
        d["deployment_modes"] = [m.to_dict() for m in self.deployment_modes]
        d["support_levels"] = [s.to_dict() for s in self.support_levels]
        d["onboarding_checklist"] = [i.to_dict() for i in self.onboarding_checklist]
        return d

    def validate(self) -> list[str]:
        errors: list[str] = []
        try:
            assert_no_forbidden_payload_v35(self.to_dict(), context="commercial_package_v39")
        except Exception as exc:  # pragma: no cover - defensive aggregation
            errors.append(str(exc))
        for collection in (self.license_tiers, self.deployment_modes, self.support_levels):
            for item in collection:
                try:
                    item.validate()
                except Exception as exc:
                    errors.append(str(exc))
        if not self.license_tiers:
            errors.append("No license tiers defined.")
        if not self.deployment_modes:
            errors.append("No deployment modes defined.")
        return errors


def default_deployment_modes_v39() -> tuple[BioSDKDeploymentModeSpecV39, ...]:
    """Return safe commercial deployment modes."""
    return (
        BioSDKDeploymentModeSpecV39(
            mode=BioSDKDeploymentModeV39.LOCAL_REPLAY.value,
            purpose="Offline evaluation on public/exported datasets and mock traces.",
            allowed_actions=("load exported data", "run replay benchmark", "generate result bundle", "run safety checks"),
            denied_actions=("live device write", "environment control", "wet-lab operation", "unverified performance claim"),
            required_artifacts=("dataset manifest", "audit log", "result bundle", "claim boundary"),
            minimum_customer_readiness="developer workstation or cloud VM",
            commercialization_status="developer/evaluation tier",
        ),
        BioSDKDeploymentModeSpecV39(
            mode=BioSDKDeploymentModeV39.ENTERPRISE_READ_ONLY.value,
            purpose="Enterprise read-only connection to vendor/API/exported wetware data.",
            allowed_actions=("metadata read", "spike/trace read", "BioGPUTrace export", "readout", "SLA audit bundle"),
            denied_actions=("stimulation command", "device actuation", "closed-loop output", "vendor SOP replacement"),
            required_artifacts=("API config", "access-mode manifest", "permission report", "audit log", "result bundle"),
            minimum_customer_readiness="enterprise security review and data access approval",
            commercialization_status="paid enterprise tier",
        ),
        BioSDKDeploymentModeSpecV39(
            mode=BioSDKDeploymentModeV39.LIVE_SHADOW.value,
            purpose="Observe a live data stream and compute online predictions without affecting the experiment.",
            allowed_actions=("live read stream", "online features", "readout prediction", "drift report", "operator dashboard"),
            denied_actions=("write to electrodes", "change experiment state", "automated biological control", "unapproved feedback loop"),
            required_artifacts=("operator approval", "shadow-mode manifest", "latency report", "safety audit", "rollback plan"),
            minimum_customer_readiness="lab or vendor-supervised data stream with read-only credentials",
            commercialization_status="premium enterprise/lab partner tier",
        ),
        BioSDKDeploymentModeSpecV39(
            mode=BioSDKDeploymentModeV39.LAB_APPROVED_CLOSED_LOOP.value,
            purpose="Future premium module for approved lab/vendor closed-loop research only.",
            allowed_actions=("approved manifest validation", "operator-supervised closed-loop orchestration", "result bundle"),
            denied_actions=("unsupervised actuation", "home wet-lab use", "unsafe parameter injection", "non-SOP operation"),
            required_artifacts=("vendor/lab SOP reference", "ethics/biosafety approval if applicable", "operator signoff", "full audit trail"),
            minimum_customer_readiness="formal lab/vendor partnership and documented approvals",
            commercialization_status="future add-on, not enabled by v3.9",
        ),
    )


def default_support_levels_v39() -> tuple[BioSDKSupportSpecV39, ...]:
    return (
        BioSDKSupportSpecV39(
            level=BioSDKSupportLevelV39.COMMUNITY.value,
            response_boundary="best effort; no production SLA",
            included_services=("documentation", "example manifests", "local replay scripts"),
            excluded_services=("enterprise integration", "custom connector", "live lab support"),
            enterprise_artifacts=("README", "examples"),
        ),
        BioSDKSupportSpecV39(
            level=BioSDKSupportLevelV39.STANDARD.value,
            response_boundary="business-hours support for read-only deployments",
            included_services=("onboarding call", "read-only connector guidance", "result-bundle review"),
            excluded_services=("live actuation", "wet-lab SOP design", "medical/clinical claims"),
            enterprise_artifacts=("partner onboarding checklist", "deployment guide", "safety report"),
        ),
        BioSDKSupportSpecV39(
            level=BioSDKSupportLevelV39.PREMIUM.value,
            response_boundary="priority support for enterprise read-only/live-shadow workflows",
            included_services=("custom adapter planning", "security review support", "latency/throughput review", "dashboard planning"),
            excluded_services=("unapproved closed-loop", "device warranty", "clinical validation"),
            enterprise_artifacts=("SLA boundary", "architecture review", "integration report"),
        ),
        BioSDKSupportSpecV39(
            level=BioSDKSupportLevelV39.LAB_PARTNER.value,
            response_boundary="project-based support under lab/vendor-approved scope",
            included_services=("lab pilot planning", "manifest review", "audit/result-bundle discipline", "claim-ladder review"),
            excluded_services=("unsupervised live control", "wet-lab execution by SDK", "regulatory certification guarantee"),
            enterprise_artifacts=("lab pilot package", "operator checklist", "claim boundary"),
        ),
    )


def default_enterprise_license_tiers_v39() -> tuple[BioSDKLicenseTierV39, ...]:
    """Return commercial tiers without enabling live actuation by default."""
    return (
        BioSDKLicenseTierV39(
            tier_id="developer_eval",
            display_name="Developer Evaluation BioSDK",
            intended_customer="individual developers, academic reviewers, early partners",
            allowed_deployment_modes=(BioSDKDeploymentModeV39.LOCAL_REPLAY.value,),
            included_components=("replay pipeline", "mock API clients", "BioLLM tool interface", "local result bundles"),
            blocked_components=("enterprise API credentials", "live stream", "closed-loop add-on"),
            monetization_model="free, low-cost, or time-limited evaluation license",
            support_level=BioSDKSupportLevelV39.COMMUNITY.value,
            compliance_boundary="software/replay only; no live lab claims",
            suggested_price_band="$0–$5k/year equivalent or evaluation-only",
            notes="Best for distribution, demos, hackathons, academic review, and non-production validation.",
        ),
        BioSDKLicenseTierV39(
            tier_id="enterprise_readonly",
            display_name="Enterprise Read-Only BioSDK",
            intended_customer="MEA vendors, wetware startups, pharma/neurotox teams, AI research groups",
            allowed_deployment_modes=(BioSDKDeploymentModeV39.LOCAL_REPLAY.value, BioSDKDeploymentModeV39.ENTERPRISE_READ_ONLY.value),
            included_components=("read-only API adapters", "BioGPUTrace export", "audit/result bundle", "benchmark reports", "enterprise onboarding"),
            blocked_components=("live actuation", "closed-loop output", "wet-lab operation"),
            monetization_model="annual license + onboarding fee + optional connector work",
            support_level=BioSDKSupportLevelV39.STANDARD.value,
            compliance_boundary="read-only customer data access; all writes denied by SDK safety gate",
            suggested_price_band="$25k–$250k/year depending on scope and connectors",
            notes="Primary first commercial tier.",
        ),
        BioSDKLicenseTierV39(
            tier_id="enterprise_live_shadow",
            display_name="Enterprise Live Shadow BioSDK",
            intended_customer="labs and vendors with live streams who need online analysis without device control",
            allowed_deployment_modes=(
                BioSDKDeploymentModeV39.LOCAL_REPLAY.value,
                BioSDKDeploymentModeV39.ENTERPRISE_READ_ONLY.value,
                BioSDKDeploymentModeV39.LIVE_SHADOW.value,
            ),
            included_components=("live read stream", "online readout", "latency report", "operator dashboard planning", "premium support"),
            blocked_components=("closed-loop actuation", "unapproved experiment control", "home wet-lab use"),
            monetization_model="premium annual license + integration services + support/SLA",
            support_level=BioSDKSupportLevelV39.PREMIUM.value,
            compliance_boundary="live read-only/shadow mode only; no biological actuation from SDK",
            suggested_price_band="$100k–$750k/year plus integration services",
            notes="High-value enterprise tier before lab-approved closed-loop.",
        ),
        BioSDKLicenseTierV39(
            tier_id="lab_approved_closed_loop_addon",
            display_name="Lab-Approved Closed Loop Add-on",
            intended_customer="formal lab/vendor partners after approved pilot scope",
            allowed_deployment_modes=(BioSDKDeploymentModeV39.LAB_APPROVED_CLOSED_LOOP.value,),
            included_components=("manifest gating", "operator-supervised orchestration", "full audit", "claim-ladder reporting"),
            blocked_components=("unsupervised control", "non-SOP operation", "general consumer use"),
            monetization_model="project license + milestone payments + possible royalty/revenue share",
            support_level=BioSDKSupportLevelV39.LAB_PARTNER.value,
            compliance_boundary="future module only; requires lab/vendor SOP, operator signoff and documented approvals",
            suggested_price_band="$250k–$2M+ pilot/add-on depending on lab scope and IP terms",
            notes="Not enabled by default; commercial upside tier after evidence and approvals.",
        ),
    )


def default_onboarding_checklist_v39() -> tuple[BioSDKPartnerOnboardingItemV39, ...]:
    return (
        BioSDKPartnerOnboardingItemV39("qualification", "Confirm customer use case: replay, read-only, live shadow, or lab pilot.", "commercial/technical lead", True, "signed discovery notes"),
        BioSDKPartnerOnboardingItemV39("data", "Confirm dataset/API source and ownership/permission to process.", "customer + BioSDK lead", True, "data access memo"),
        BioSDKPartnerOnboardingItemV39("security", "Review credential handling and read-only access scope.", "customer security", True, "security checklist"),
        BioSDKPartnerOnboardingItemV39("safety", "Run safety boundary validation against all manifests/configs.", "BioSDK lead", True, "safety report"),
        BioSDKPartnerOnboardingItemV39("technical", "Run smoke test and generate result bundle.", "integration engineer", True, "result bundle"),
        BioSDKPartnerOnboardingItemV39("commercial", "Select license tier, support level and paid add-ons.", "commercial lead", True, "order form / SOW"),
        BioSDKPartnerOnboardingItemV39("lab", "For live-shadow/lab pilot, require operator signoff and approved scope.", "lab partner", False, "operator/lab approval"),
        BioSDKPartnerOnboardingItemV39("claims", "Approve public/private claim boundary before external sharing.", "legal/scientific review", True, "claim-ladder memo"),
    )


def build_commercial_package_v39(extra_metadata: dict[str, Any] | None = None) -> BioSDKCommercialPackageV39:
    safety = safety_boundary_summary_v35().to_dict()
    return BioSDKCommercialPackageV39(
        version="v3.9",
        product_name="BioGPU-Core Enterprise BioSDK",
        positioning=(
            "Commercial SDK/runtime layer for living neural compute workflows: replay, read-only APIs, "
            "BioGPUTrace export, benchmark/readout, BioLLM tool integration, audit logs and result bundles."
        ),
        license_tiers=default_enterprise_license_tiers_v39(),
        deployment_modes=default_deployment_modes_v39(),
        support_levels=default_support_levels_v39(),
        onboarding_checklist=default_onboarding_checklist_v39(),
        safety_summary=safety,
        claim_boundary=(
            "v3.9 is commercial packaging, not proof of live BioGPU operation.",
            "No live actuation is enabled by default.",
            "No GPU replacement claim is made without matched-task measurements.",
            "Enterprise closed-loop remains future lab/vendor-approved scope.",
        ),
        revenue_logic=(
            "Use developer evaluation for adoption and technical validation.",
            "Sell read-only enterprise SDK as first real commercial product.",
            "Upsell live-shadow analytics to labs/vendors with existing live data streams.",
            "Reserve closed-loop modules for high-value, approved lab partner contracts.",
        ),
        next_version="v4.0_lab_pilot_package_or_v3.10_powerpc_results",
        metadata=extra_metadata or {},
    )
