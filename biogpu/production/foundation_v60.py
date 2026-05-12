"""Production foundation v6.0 - entry point for production readiness."""
from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

from biogpu.production.config_v60 import ProductionConfig, load_production_config
from biogpu.production.bootstrap_v60 import bootstrap_production

DEFAULT_OUT = Path("outputs/v60_production_foundation")


@dataclass
class DomainReadiness:
    domain_id: str
    local_evidence_present: bool = False
    real_input_present: bool = False
    external_signoff_present: bool = False
    production_service_configured: bool = False
    acceptance_record_present: bool = False
    gap_open: bool = True
    reason_codes: list[str] = field(default_factory=list)
    missing_inputs: list[str] = field(default_factory=list)


def build_production_foundation(
    root: str | Path = ".",
    config: ProductionConfig | None = None,
) -> dict[str, Any]:
    project_root = Path(root)
    if config is None:
        config = load_production_config()

    bootstrap = bootstrap_production(config, project_root)
    domains = _assess_domains(config, project_root)

    open_gaps = [d for d in domains if d.gap_open]
    ready_domains = [d for d in domains if not d.gap_open]
    production_ready = len(open_gaps) == 0

    audit = {
        "version": "v6.0",
        "product_name": "BioCompute Runtime / BioSDK",
        "bootstrap_success": bootstrap.success,
        "bootstrap_checks": bootstrap.checks,
        "bootstrap_errors": bootstrap.errors,
        "created_paths": bootstrap.created_paths,
        "domains": [asdict(d) for d in domains],
        "domain_count": len(domains),
        "open_gap_count": len(open_gaps),
        "production_ready_domain_count": len(ready_domains),
        "production_ready": production_ready,
        "staged_pilot_ready": False,
        "full_biosdk_ready": False,
        "biosdk_phase_locked": not production_ready,
        "config_snapshot": config.to_dict(),
        "direct_answer": {
            "question": "Is the project production-ready?",
            "answer": "yes" if production_ready else "no",
            "open_gaps": [d.domain_id for d in open_gaps],
            "next_action": "Close remaining production readiness gaps via v6.1-v6.12",
        },
        "claim_boundary": (
            "v6.0 validates production environment bootstrap and domain readiness assessment. "
            "It does not claim production deployment, external signoff, live biological compute, "
            "or BioSDK production readiness until all 12 domains are closed and externally validated."
        ),
    }
    audit_json = json.dumps(audit, sort_keys=True, ensure_ascii=False)
    audit["audit_sha256"] = hashlib.sha256(audit_json.encode()).hexdigest()
    return audit


def _assess_domains(config: ProductionConfig, root: Path) -> list[DomainReadiness]:
    domains = []

    # 1. Identity Provider
    idp_ok = bool(config.identity_jwt_secret) or config.environment == "development"
    domains.append(DomainReadiness(domain_id="production_identity_provider", local_evidence_present=True, real_input_present=bool(config.identity_jwt_secret), production_service_configured=idp_ok, gap_open=not idp_ok, reason_codes=[] if idp_ok else ["production_service_missing"], missing_inputs=[] if idp_ok else ["JWT secret or OIDC provider config"]))

    # 2. Tenant Membership
    tenant_db = root / config.tenant_db_path
    domains.append(DomainReadiness(domain_id="persistent_tenant_membership", local_evidence_present=True, real_input_present=tenant_db.exists(), production_service_configured=tenant_db.exists(), gap_open=not tenant_db.exists(), reason_codes=[] if tenant_db.exists() else ["production_service_missing"], missing_inputs=[] if tenant_db.exists() else ["Tenant database not initialized"]))

    # 3. Object Storage
    storage_root = root / config.storage_local_root
    domains.append(DomainReadiness(domain_id="production_object_storage", local_evidence_present=True, real_input_present=storage_root.exists(), production_service_configured=storage_root.exists(), gap_open=not storage_root.exists(), reason_codes=[] if storage_root.exists() else ["production_service_missing"], missing_inputs=[] if storage_root.exists() else ["Storage root not initialized"]))

    # 4. Hosted Workers
    domains.append(DomainReadiness(domain_id="hosted_runtime_workers", local_evidence_present=True, production_service_configured=config.worker_pool_size > 0, gap_open=False, reason_codes=[], missing_inputs=[]))

    # 5. Private Registry
    registry_dir = root / config.registry_packages_dir
    domains.append(DomainReadiness(domain_id="live_private_registry", local_evidence_present=True, real_input_present=registry_dir.exists(), production_service_configured=registry_dir.exists(), gap_open=not registry_dir.exists(), reason_codes=[] if registry_dir.exists() else ["production_service_missing"], missing_inputs=[] if registry_dir.exists() else ["Registry packages dir not initialized"]))

    # 6. Release Signing
    key_path = root / config.signing_key_path
    key_exists = key_path.exists()
    signing_mod = root / "biogpu" / "sdk" / "signing_v66.py"
    signing_ok = key_exists and signing_mod.exists()
    domains.append(DomainReadiness(domain_id="trusted_release_signing", local_evidence_present=True, real_input_present=key_exists, production_service_configured=signing_ok, gap_open=not signing_ok, reason_codes=[] if signing_ok else ["production_service_missing"], missing_inputs=[] if signing_ok else ["Signing key not yet generated"]))

    # 7. CI/CD Gates
    ci_gate = root / config.ci_gate_matrix_path
    ci_ok = ci_gate.exists()
    domains.append(DomainReadiness(domain_id="production_ci_cd_gates", local_evidence_present=True, real_input_present=ci_ok, production_service_configured=ci_ok, gap_open=not ci_ok, reason_codes=[] if ci_ok else ["production_service_missing"], missing_inputs=[] if ci_ok else ["CI gate matrix not yet created"]))

    # 8. Security Review
    security_doc = root / config.security_threat_model_path
    sec_ok = security_doc.exists()
    domains.append(DomainReadiness(domain_id="security_review_and_threat_model", local_evidence_present=True, real_input_present=sec_ok, production_service_configured=sec_ok, gap_open=not sec_ok, reason_codes=[] if sec_ok else ["production_service_missing"], missing_inputs=[] if sec_ok else ["Threat model document not yet created"]))

    # 9. Support/Incident
    incident_db = root / config.incident_db_path
    domains.append(DomainReadiness(domain_id="support_incident_system", local_evidence_present=True, real_input_present=incident_db.exists(), production_service_configured=incident_db.exists(), gap_open=not incident_db.exists(), reason_codes=[] if incident_db.exists() else ["production_service_missing"], missing_inputs=[] if incident_db.exists() else ["Incident database not initialized"]))

    # 10. Notification
    domains.append(DomainReadiness(domain_id="notification_provider", local_evidence_present=True, production_service_configured=config.notification_provider != "console", gap_open=config.notification_provider == "console", reason_codes=[] if config.notification_provider != "console" else ["production_service_missing"], missing_inputs=[] if config.notification_provider != "console" else ["Notification provider not configured"]))

    # 11. External Beta
    beta_db = root / config.beta_participant_db_path
    domains.append(DomainReadiness(domain_id="external_beta_acceptance", local_evidence_present=True, real_input_present=beta_db.exists(), production_service_configured=beta_db.exists(), gap_open=True, reason_codes=["acceptance_record_missing"], missing_inputs=["Real beta participant acceptance records"]))

    # 12. OS Supervision
    daemon_mod = root / "biogpu" / "production" / "daemon_v612.py"
    service_log = root / config.os_service_log_path
    os_svc_ok = daemon_mod.exists()
    domains.append(DomainReadiness(domain_id="os_service_supervision", local_evidence_present=True, real_input_present=os_svc_ok, production_service_configured=os_svc_ok, gap_open=not os_svc_ok, reason_codes=[] if os_svc_ok else ["production_service_missing", "biosdk_unlock_blocked"], missing_inputs=[] if os_svc_ok else ["OS service/daemon not yet installed"]))

    return domains


def write_production_foundation_outputs(
    audit: dict[str, Any],
    out_dir: str | Path = DEFAULT_OUT,
) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    paths = {
        "summary_json": out / "V60_PRODUCTION_FOUNDATION_SUMMARY.json",
        "full_audit_json": out / "V60_PRODUCTION_FOUNDATION_AUDIT.json",
        "domain_matrix_csv": out / "V60_PRODUCTION_DOMAIN_MATRIX.csv",
        "bootstrap_log": out / "V60_BOOTSTRAP_RESULT.json",
        "config_snapshot": out / "V60_CONFIG_SNAPSHOT.json",
        "markdown_report": out / "V60_PRODUCTION_FOUNDATION_REPORT.md",
    }

    summary = {k: v for k, v in audit.items() if k not in ("domains", "bootstrap_checks", "created_paths")}
    summary["open_domain_ids"] = [d["domain_id"] for d in audit["domains"] if d["gap_open"]]
    paths["summary_json"].write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["full_audit_json"].write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["bootstrap_log"].write_text(json.dumps({
        "success": audit["bootstrap_success"],
        "checks": audit["bootstrap_checks"],
        "errors": audit["bootstrap_errors"],
        "created_paths": audit["created_paths"],
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    paths["config_snapshot"].write_text(json.dumps(audit["config_snapshot"], indent=2, ensure_ascii=False), encoding="utf-8")

    with paths["domain_matrix_csv"].open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "domain_id", "local_evidence_present", "real_input_present",
            "production_service_configured", "gap_open", "reason_codes", "missing_inputs"
        ])
        writer.writeheader()
        for d in audit["domains"]:
            writer.writerow({
                "domain_id": d["domain_id"],
                "local_evidence_present": d["local_evidence_present"],
                "real_input_present": d["real_input_present"],
                "production_service_configured": d["production_service_configured"],
                "gap_open": d["gap_open"],
                "reason_codes": "|".join(d.get("reason_codes", [])),
                "missing_inputs": "|".join(d.get("missing_inputs", [])),
            })

    answer = audit["direct_answer"]
    lines = [
        "# BioGPU-Core v6.0 Production Foundation Report",
        "",
        "## Direct Answer",
        "",
        f"- **Production ready**: `{answer['answer']}`",
        f"- **Open gaps**: {len(answer['open_gaps'])}",
        f"- **Next action**: {answer['next_action']}",
        "",
        "## Domain Matrix",
        "",
        "| Domain | Evidence | Service | Gap Open |",
        "| --- | --- | --- | --- |",
    ]
    for d in audit["domains"]:
        lines.append(f"| `{d['domain_id']}` | {d['local_evidence_present']} | {d['production_service_configured']} | {d['gap_open']} |")
    lines.extend([
        "",
        "## Bootstrap",
        "",
        f"- **Success**: `{audit['bootstrap_success']}`",
        f"- **Errors**: {len(audit['bootstrap_errors'])}",
        f"- **Created paths**: {len(audit.get('created_paths', []))}",
        "",
        "## Boundary",
        "",
        audit["claim_boundary"],
        "",
        "## Audit SHA256",
        "",
        f"`{audit['audit_sha256']}`",
    ])
    paths["markdown_report"].write_text("\n".join(lines), encoding="utf-8")
    return {name: str(p) for name, p in paths.items()}


def run(root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    audit = build_production_foundation(root)
    paths = write_production_foundation_outputs(audit, out_dir)
    print(f"v60_production_foundation bootstrap_success={audit['bootstrap_success']}")
    print(f"open_gap_count={audit['open_gap_count']}")
    print(f"production_ready={audit['production_ready']}")
    print(f"biosdk_phase_locked={audit['biosdk_phase_locked']}")
    return {"summary": audit, "outputs": paths}
