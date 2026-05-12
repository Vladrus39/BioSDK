"""BioGPU-Core v5.0 differentiation and first-mover roadmap.

This module is intentionally non-operational: it defines the project targets,
competitive moat candidates, proof obligations, and OS capabilities that should
shape development from BioSDK/Runtime toward BiC OS.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Literal

ClaimStatus = Literal["proven_now", "partially_proven", "needs_power_pc", "needs_api_partner", "needs_lab"]


@dataclass(frozen=True)
class Differentiator:
    id: str
    title: str
    plain_language: str
    why_it_matters: str
    proof_path: list[str]
    status: ClaimStatus
    first_mover_claim: str


@dataclass(frozen=True)
class OSCapability:
    id: str
    title: str
    target_layer: str
    required_components: list[str]
    beta_form: str
    mature_form: str


@dataclass(frozen=True)
class ProofTarget:
    id: str
    claim: str
    can_prove_before_lab: bool
    required_assets: list[str]
    minimum_evidence: list[str]
    release_gate: str


PROJECT_POSITIONING = {
    "technical_kernel": "BioGPU-Core",
    "sdk_layer": "BioSDK / Living Compute SDK",
    "runtime_product": "BioCompute Runtime",
    "interface_standard": "NSI-1.0 / Neural Substrate Interface",
    "control_plane": "BioCompute Control Plane",
    "os_codename": "BiC OS",
    "primary_claim": (
        "Vendor-neutral BioCompute Runtime and future OS-like control plane "
        "for living neural compute, LLM-agent workflows, reproducible benchmarks, "
        "safety policies, adapter conformance, and auditable evidence bundles."
    ),
}


def differentiators() -> list[Differentiator]:
    return [
        Differentiator(
            id="DIF-001",
            title="Vendor-neutral Neural Substrate Interface",
            plain_language="Один интерфейс для разных источников: Zenodo, NWB/DANDI, Allen, FinalSpark, CL-like APIs, MCS, 3Brain, Axion и пользовательские данные.",
            why_it_matters="Большинство платформ вертикальны и привязаны к своему железу/API; enterprise-клиенту нужен слой сравнения и переносимости.",
            proof_path=["NSI schema", "reference adapters", "adapter conformance tests", "same benchmark across >=3 datasets"],
            status="partially_proven",
            first_mover_claim="Not first biological OS; potentially first vendor-neutral interface/runtime focused on living compute evidence and AI workflows.",
        ),
        Differentiator(
            id="DIF-002",
            title="Evidence Ledger / Result Bundle Standard",
            plain_language="Каждый запуск даёт воспроизводимый bundle: manifest, данные/ссылки/checksum, split, модель, метрики, shuffle baseline, графики и audit log.",
            why_it_matters="Без evidence bundle biological-compute claims выглядят как демонстрации; с bundle они становятся проверяемыми инженерными результатами.",
            proof_path=["result bundle spec", "bundle validator", "signed checksums", "re-run report"],
            status="partially_proven",
            first_mover_claim="A dedicated reproducibility/evidence layer for living-compute AI benchmarks, not just acquisition or stimulation API.",
        ),
        Differentiator(
            id="DIF-003",
            title="LLM/Agent Bridge for BioCompute",
            plain_language="LLM не управляет живой системой напрямую; он вызывает BioCompute tool, получает структурированный результат и safety/claim-level метку.",
            why_it_matters="AI-агенты смогут планировать эксперименты, анализировать ответы и формировать отчёты без небезопасного live-control.",
            proof_path=["BioLLM task schema", "tool interface", "safe replay/API mode", "agent-generated experiment manifest review"],
            status="partially_proven",
            first_mover_claim="A structured LLM-to-wetware runtime bridge with safety and evidence claims built in from the beginning.",
        ),
        Differentiator(
            id="DIF-004",
            title="Safety-graded Access Ladder",
            plain_language="Максимальный software-доступ для тестеров, но live-stimulation только через lab/vendor approval, allowlist и audit.",
            why_it_matters="Даёт коммерческую проверяемость без риска неконтролируемого воздействия на живую систему.",
            proof_path=["safety policy", "unsafe-field rejection", "permission tiers", "approval workflow"],
            status="partially_proven",
            first_mover_claim="Enterprise-friendly access ladder combining broad SDK evaluation with conservative biological actuation governance.",
        ),
        Differentiator(
            id="DIF-005",
            title="Cross-dataset Biological Compute Benchmark Suite",
            plain_language="Один benchmark-подход на MEA, NWB, Allen, organoid/API и vendor-export данных.",
            why_it_matters="Позволяет сравнивать платформы и декодеры не по рекламе, а по одинаковым задачам и baseline.",
            proof_path=["Zenodo preprocessed", "Zenodo raw HDF5", "DANDI/NWB", "AllenSDK", "FinalSpark/CL-like export"],
            status="needs_power_pc",
            first_mover_claim="A vendor-neutral benchmark suite for living neural compute across replay, public neurodata, and API/live-shadow modes.",
        ),
        Differentiator(
            id="DIF-006",
            title="Conformance Tests for BioCompute Adapters",
            plain_language="Любой новый адаптер должен пройти одинаковые тесты: metadata, trace, feature batch, safety, bundle.",
            why_it_matters="Так можно строить marketplace/экосистему адаптеров, а не вручную поддерживать каждую платформу.",
            proof_path=["adapter contract", "mock adapter", "conformance CLI", "certification report"],
            status="needs_power_pc",
            first_mover_claim="A testable adapter-certification approach for biological compute platforms.",
        ),
        Differentiator(
            id="DIF-007",
            title="BiC OS Control Plane Path",
            plain_language="Не просто SDK, а будущая OS-like среда: daemon, scheduler, permissions, storage, dashboard, telemetry, lab approvals.",
            why_it_matters="Коммерческая ценность появляется не только от алгоритмов, а от управления workflow предприятий и лабораторий.",
            proof_path=["hosted server scaffold", "job queue", "dataset storage", "dashboard", "enterprise pilot"],
            status="needs_power_pc",
            first_mover_claim="A full-stack path from BioSDK to operating/control-plane layer for living compute workflows.",
        ),
        Differentiator(
            id="DIF-008",
            title="Claim Ladder Built Into the Product",
            plain_language="Каждый результат получает честный уровень: replay-only, public-data validated, API read-only, live-shadow, lab-approved closed-loop.",
            why_it_matters="Это снижает риск завышенных обещаний и делает продукт привлекательнее для серьёзных партнёров.",
            proof_path=["claim-level schema", "bundle annotation", "documentation", "external audit"],
            status="partially_proven",
            first_mover_claim="A biological-compute product where claim maturity is machine-readable and enforced by release tooling.",
        ),
    ]


def os_capabilities() -> list[OSCapability]:
    return [
        OSCapability(
            id="OS-001",
            title="NSI Kernel",
            target_layer="standard/runtime",
            required_components=["Trace schema", "Task manifest", "Feature batch", "Readout result", "Safety profile", "Bundle spec"],
            beta_form="Pydantic/JSON schemas + validators",
            mature_form="Versioned NSI kernel with conformance suite and adapter certification",
        ),
        OSCapability(
            id="OS-002",
            title="LLM/Agent Operating Bridge",
            target_layer="AI workflow",
            required_components=["BioLLM tool", "agent-safe task manifest", "claim-level result", "human approval gates"],
            beta_form="Replay/read-only tool calls",
            mature_form="Agent plans experiments, OS validates/schedules, lab operator approves live actions",
        ),
        OSCapability(
            id="OS-003",
            title="Experiment Orchestrator",
            target_layer="research workflow",
            required_components=["dataset registry", "job scheduler", "split policy", "decoder registry", "negative controls"],
            beta_form="CLI + hosted job scaffold",
            mature_form="Multi-dataset, multi-adapter scheduler with reproducible experiment templates",
        ),
        OSCapability(
            id="OS-004",
            title="Safety Supervisor",
            target_layer="governance",
            required_components=["unsafe field rejection", "permission tier", "allowlist", "audit log", "operator confirmation"],
            beta_form="blocked-by-default live actuation",
            mature_form="policy engine controlling live-shadow and lab-approved actuation workflows",
        ),
        OSCapability(
            id="OS-005",
            title="Evidence Ledger",
            target_layer="trust/reproducibility",
            required_components=["result bundle", "checksums", "audit log", "rerun manifest", "claim ladder"],
            beta_form="zip result bundles",
            mature_form="signed, queryable evidence ledger with external audit support",
        ),
        OSCapability(
            id="OS-006",
            title="Adapter Marketplace",
            target_layer="ecosystem",
            required_components=["plugin API", "conformance tests", "adapter metadata", "permission declaration"],
            beta_form="built-in mock/read-only adapters",
            mature_form="third-party adapters for vendor platforms, public datasets, private labs and enterprise data",
        ),
        OSCapability(
            id="OS-007",
            title="BioCompute Dashboard",
            target_layer="enterprise UI",
            required_components=["runs", "datasets", "metrics", "quota", "audit", "downloads"],
            beta_form="API scaffold + docs",
            mature_form="hosted/on-prem UI for jobs, datasets, evidence, users and approvals",
        ),
    ]


def proof_targets() -> list[ProofTarget]:
    return [
        ProofTarget(
            id="PROOF-001",
            claim="BioGPU-Core can reproduce its v12/v15/v32/v33/v36 evidence chain on a clean machine.",
            can_prove_before_lab=True,
            required_assets=["v4.7/v5.0 archive", "Pre_processed_MEA_data.zip", "evidence pack"],
            minimum_evidence=["smoke tests pass", "dataset checksum", "v33 compact result", "v36 lineage result"],
            release_gate="Must pass before any external beta.",
        ),
        ProofTarget(
            id="PROOF-002",
            claim="Lineage-strict performance is above shuffled controls with confidence intervals across multiple split offsets.",
            can_prove_before_lab=True,
            required_assets=["pulse_feature_matrix.npz", "full_shuffle_1000", "bootstrap CI"],
            minimum_evidence=["1000 shuffles", "bootstrap CI", "balanced accuracy", "negative controls"],
            release_gate="Required before serious scientific claims.",
        ),
        ProofTarget(
            id="PROOF-003",
            claim="NSI can normalize at least three independent data sources into one trace/feature/result-bundle workflow.",
            can_prove_before_lab=True,
            required_assets=["Zenodo", "DANDI/NWB", "AllenSDK or FinalSpark export"],
            minimum_evidence=["adapter conformance reports", "same bundle schema", "cross-dataset benchmark table"],
            release_gate="Required before claiming vendor-neutral interface leadership.",
        ),
        ProofTarget(
            id="PROOF-004",
            claim="LLM/Agent bridge can generate safe BioCompute manifests and consume structured result bundles.",
            can_prove_before_lab=True,
            required_assets=["BioLLM tool", "safe-task examples", "result bundle examples"],
            minimum_evidence=["unsafe request rejected", "safe task runs", "LLM-readable structured result"],
            release_gate="Required before AI workflow beta.",
        ),
        ProofTarget(
            id="PROOF-005",
            claim="Live read-only/shadow mode works against a real external platform or vendor export.",
            can_prove_before_lab=True,
            required_assets=["FinalSpark token/export or CL/MEA HDF5", "read-only adapter"],
            minimum_evidence=["metadata read", "trace conversion", "bundle generation"],
            release_gate="Required before live-shadow enterprise tier.",
        ),
        ProofTarget(
            id="PROOF-006",
            claim="Lab-approved live closed-loop can be controlled safely via BiC OS approval workflow.",
            can_prove_before_lab=False,
            required_assets=["approved lab", "approved protocol", "operator", "vendor platform"],
            minimum_evidence=["approval record", "safe allowlist", "live logs", "post-run biological QC"],
            release_gate="Required before any live-actuation commercial module.",
        ),
    ]


def project_summary() -> dict:
    return {
        "positioning": PROJECT_POSITIONING,
        "differentiators": [asdict(x) for x in differentiators()],
        "os_capabilities": [asdict(x) for x in os_capabilities()],
        "proof_targets": [asdict(x) for x in proof_targets()],
        "non_claims": [
            "We are not claiming to be the first biological computer.",
            "We are not claiming to replace GPUs for LLM inference.",
            "We are not claiming live BioGPU proof before laboratory validation.",
            "We are not replacing NWB; NSI should interoperate with NWB/HDF5/API/vendor exports.",
        ],
    }
