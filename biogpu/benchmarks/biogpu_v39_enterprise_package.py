from __future__ import annotations

import csv
import json
import platform
import zipfile
from pathlib import Path
from typing import Iterable

from biogpu.enterprise.licensing_v39 import build_commercial_package_v39


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def write_csv(path: Path, rows: Iterable[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def make_bundle(out: Path, files: list[Path], bundle_name: str) -> Path:
    bundle = out / bundle_name
    with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in files:
            if p.exists() and p.is_file() and p != bundle:
                zf.write(p, arcname=p.name)
    return bundle


def run_v39(output_dir: str = "outputs/realdata_zenodo_14363732_v39_enterprise_package") -> dict:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    package = build_commercial_package_v39({"python": platform.python_version(), "system": platform.system()})
    errors = package.validate()
    if errors:
        raise RuntimeError("v3.9 package validation failed: " + "; ".join(errors))
    data = package.to_dict()

    write_json(out / "v39_enterprise_package_manifest.json", data)

    tier_rows = []
    for t in data["license_tiers"]:
        tier_rows.append({
            "tier_id": t["tier_id"],
            "display_name": t["display_name"],
            "allowed_deployment_modes": ";".join(t["allowed_deployment_modes"]),
            "support_level": t["support_level"],
            "monetization_model": t["monetization_model"],
            "suggested_price_band": t["suggested_price_band"],
            "compliance_boundary": t["compliance_boundary"],
        })
    write_csv(out / "v39_license_tiers.csv", tier_rows, list(tier_rows[0].keys()))

    mode_rows = []
    for m in data["deployment_modes"]:
        mode_rows.append({
            "mode": m["mode"],
            "purpose": m["purpose"],
            "allowed_actions": ";".join(m["allowed_actions"]),
            "denied_actions": ";".join(m["denied_actions"]),
            "minimum_customer_readiness": m["minimum_customer_readiness"],
            "commercialization_status": m["commercialization_status"],
        })
    write_csv(out / "v39_deployment_modes.csv", mode_rows, list(mode_rows[0].keys()))

    support_rows = []
    for s in data["support_levels"]:
        support_rows.append({
            "level": s["level"],
            "response_boundary": s["response_boundary"],
            "included_services": ";".join(s["included_services"]),
            "excluded_services": ";".join(s["excluded_services"]),
        })
    write_csv(out / "v39_support_sla_boundaries.csv", support_rows, list(support_rows[0].keys()))

    onboarding_rows = [
        {
            "phase": i["phase"],
            "item": i["item"],
            "owner": i["owner"],
            "required_before_paid_use": i["required_before_paid_use"],
            "evidence": i["evidence"],
        }
        for i in data["onboarding_checklist"]
    ]
    write_csv(out / "v39_partner_onboarding_checklist.csv", onboarding_rows, list(onboarding_rows[0].keys()))

    license_doc = """# BioGPU-Core Enterprise License Tiers v3.9

BioGPU-Core v3.9 packages the project as an enterprise BioSDK for living neural compute.
It is not a live-lab control release and does not claim GPU replacement.

## Commercial tiers

| Tier | Target customer | Modes | Commercial model | Price band |
|---|---|---|---|---|
"""
    for t in data["license_tiers"]:
        license_doc += f"| {t['display_name']} | {t['intended_customer']} | {', '.join(t['allowed_deployment_modes'])} | {t['monetization_model']} | {t['suggested_price_band']} |\n"
    license_doc += """

## Safety boundary

All enterprise tiers inherit the BioGPU safety boundary: no unapproved live actuation,
no wet-lab recipe, no physical wiring/pinout procedure, and no GPU-advantage claim
without matched-task measurements.

## Intended commercial path

1. Developer evaluation drives adoption.
2. Enterprise Read-Only BioSDK becomes the first paid product.
3. Live Shadow becomes premium analytics for labs/vendors.
4. Lab-Approved Closed Loop remains a future, project-based add-on.
"""
    write_text(out / "LICENSE_TIERS_V39.md", license_doc)

    enterprise_readme = """# BioGPU-Core Enterprise BioSDK v3.9

## Positioning

BioGPU-Core is a BioSDK/runtime layer for living neural compute workflows.
It connects replay datasets, read-only external API sources, BioGPUTrace export,
readout/benchmark modules, BioLLM tool integration, audit logs and result bundles.

## What enterprises can do now

- Run replay validation on exported/public datasets.
- Connect mock/read-only API clients.
- Convert traces into BioGPUTrace format.
- Run readout/benchmark pipelines.
- Produce audit/result bundles for internal scientific review.
- Integrate the BioLLM tool interface in agent workflows.

## What v3.9 does not allow

- Unapproved live biological actuation.
- Vendor pinout/wiring procedures.
- Wet-lab recipes or culture execution steps.
- Claims that BioGPU replaces GPU/LLM hardware.

## Recommended sales motion

Start with Developer Evaluation, convert serious partners to Enterprise Read-Only,
then upsell Live Shadow where a lab/vendor has supervised live stream access.
Closed-loop is sold only as a scoped lab-approved project.
"""
    write_text(out / "ENTERPRISE_README_V39.md", enterprise_readme)

    pricing_doc = """# BioGPU-Core Pricing Assumptions v3.9

These are planning assumptions, not binding quotes.

- Developer Evaluation: free, low-cost, time-limited or academic evaluation.
- Enterprise Read-Only BioSDK: annual license plus onboarding/connectors.
- Enterprise Live Shadow: premium annual license plus integration/SLA.
- Lab-Approved Closed Loop Add-on: project license, milestones and possible royalty/revenue share.

Commercial value should be tied to evidence:

1. working replay/read-only integration,
2. customer data result bundles,
3. power-PC statistical validation,
4. live-shadow performance,
5. lab-approved live pilot.
"""
    write_text(out / "PRICING_ASSUMPTIONS_V39.md", pricing_doc)

    investor_summary = """# BioGPU-Core v3.9 Investor / Partner Summary

BioGPU-Core has evolved from a GPU-replacement idea into a BioSDK for living neural
compute. The commercial product is not a consumer wet-lab tool; it is an enterprise
software layer for replay, read-only wetware APIs, trace standardization, benchmark,
BioLLM integration and auditable results.

## Near-term monetizable product

Enterprise Read-Only BioSDK: connect to exported/read-only MEA/HD-MEA/wetware data,
standardize to BioGPUTrace, run benchmark/readout, produce result bundles.

## Upside

Live Shadow analytics and future lab-approved closed-loop modules.

## Claim discipline

No live BioGPU proof and no GPU advantage claim are made by v3.9. The package is
structured so those claims can be tested later under power-PC and lab/vendor validation.
"""
    write_text(out / "INVESTOR_PARTNER_SUMMARY_V39.md", investor_summary)

    deployment_doc = """# BioGPU-Core Deployment Modes v3.9

1. local_replay — offline replay and mock validation.
2. enterprise_read_only — paid read-only API/export integration.
3. live_shadow — live stream observation with no actuation.
4. lab_approved_closed_loop — future gated add-on under lab/vendor-approved scope.

Default v3.9 release enables only safe software/read modes. Commercial closed-loop
is a future controlled module, not a default SDK capability.
"""
    write_text(out / "DEPLOYMENT_MODES_V39.md", deployment_doc)

    report = f"""# BioGPU-Core v3.9 — Enterprise Packaging / Licensing Layer

## Purpose

v3.9 turns BioGPU-Core into an enterprise-facing BioSDK package with license tiers,
deployment modes, support/SLA boundaries, onboarding checklist, pricing assumptions,
and investor/lab-facing summaries.

## Product name

{data['product_name']}

## Positioning

{data['positioning']}

## License tiers

"""
    for t in data["license_tiers"]:
        report += f"- **{t['display_name']}** — {t['suggested_price_band']} — {t['compliance_boundary']}\n"
    report += """

## Validation

- Commercial package validation: OK
- Safety boundary validation: OK
- Live output performed: false
- Closed-loop enabled by default: false

## Next step

v4.0 can become the lab pilot package, or v3.10 can focus on power-PC statistical
results after the full lineage/shuffle sweep.
"""
    write_text(out / "BIOGPU_V39_ENTERPRISE_PACKAGE_REPORT.md", report)

    summary = {
        "version": "v3.9",
        "component": "Enterprise Packaging / Licensing Layer",
        "status": "ok",
        "tier_count": len(data["license_tiers"]),
        "deployment_mode_count": len(data["deployment_modes"]),
        "support_level_count": len(data["support_levels"]),
        "commercial_first_product": "Enterprise Read-Only BioSDK",
        "closed_loop_enabled_by_default": False,
        "live_output_performed": False,
        "validation_errors": errors,
        "outputs": [],
    }
    write_json(out / "v39_summary.json", summary)

    files = sorted([p for p in out.iterdir() if p.is_file()])
    bundle = make_bundle(out, files, "biogpu_v39_enterprise_package_bundle.zip")
    summary["outputs"] = sorted(p.name for p in out.iterdir() if p.is_file())
    summary["bundle"] = bundle.name
    write_json(out / "v39_summary.json", summary)
    return summary


if __name__ == "__main__":
    print(json.dumps(run_v39(), indent=2, ensure_ascii=False))
