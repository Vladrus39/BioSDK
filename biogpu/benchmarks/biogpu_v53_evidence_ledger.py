"""BioGPU-Core v5.3 Evidence Ledger runner."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from biogpu.evidence.ledger_v53 import build_evidence_ledger, validate_evidence_bundle, validate_ledger_chain
from biogpu.runtime.session_manager_v24 import write_v24_session_outputs


DEFAULT_OUT = Path("outputs/v53_evidence_ledger")


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _render_report(summary: dict[str, Any]) -> str:
    lines = [
        "# BioGPU-Core v5.3 Evidence Ledger Report",
        "",
        "## Summary",
        "",
        f"- Audited bundles: {summary['audited_bundle_count']}",
        f"- Valid bundles: {summary['valid_bundle_count']}",
        f"- Ledger entries: {summary['ledger_entry_count']}",
        f"- Chain valid: {summary['ledger_chain_valid']}",
        f"- Reference bundle valid: {summary['reference_bundle_valid']}",
        "",
        "## Boundary",
        "",
        "v5.3 signs local integrity snapshots only. It does not provide external identity attestation, legal notarization, or live biological validation.",
        "",
    ]
    return "\n".join(lines)


def candidate_bundle_paths(project_root: Path, reference_bundle: Path) -> list[Path]:
    candidates = [reference_bundle]
    v50_bundle = project_root / "outputs" / "v50_pc_validation_bundle" / "biogpu_v50_pc_validation_bundle.zip"
    if v50_bundle.exists():
        candidates.append(v50_bundle)
    return candidates


def run(project_root: str | Path = ".", out_dir: str | Path = DEFAULT_OUT) -> dict[str, Any]:
    root = Path(project_root).resolve()
    out = Path(out_dir)
    if not out.is_absolute():
        out = root / out
    out.mkdir(parents=True, exist_ok=True)

    reference_dir = out / "reference_v24_session"
    reference_summary = write_v24_session_outputs(reference_dir, run_mode="dry_run", hardware_profile="software_only_v53_reference")
    reference_bundle = reference_dir / str(reference_summary["result_bundle"])

    reports = [validate_evidence_bundle(path) for path in candidate_bundle_paths(root, reference_bundle)]
    ledger = build_evidence_ledger(reports)
    chain_report = validate_ledger_chain(ledger)
    reports_data = [report.to_dict() for report in reports]
    ledger_data = ledger.to_dict()

    reference_report = next(report for report in reports if Path(report.bundle_path).resolve() == reference_bundle.resolve())
    valid_bundle_count = sum(1 for report in reports if report.valid)
    summary = {
        "phase": "evidence_ledger",
        "milestone": "v5.3",
        "audited_bundle_count": len(reports),
        "valid_bundle_count": valid_bundle_count,
        "ledger_entry_count": ledger.entry_count,
        "ledger_chain_valid": bool(chain_report["valid"]),
        "reference_bundle_valid": bool(reference_report.valid),
        "chain_root": ledger.chain_root,
        "gate": {
            "reference_bundle_validated": bool(reference_report.valid),
            "ledger_chain_validated": bool(chain_report["valid"]),
            "local_signatures_present": all(entry.local_signature for entry in ledger.entries),
        },
    }

    _write_json(out / "V53_EVIDENCE_BUNDLE_VALIDATION_REPORTS.json", reports_data)
    _write_json(out / "V53_EVIDENCE_LEDGER.json", ledger_data)
    _write_json(out / "V53_EVIDENCE_LEDGER_CHAIN_VALIDATION.json", chain_report)
    _write_json(out / "V53_EVIDENCE_LEDGER_SUMMARY.json", summary)
    (out / "BIOGPU_V53_EVIDENCE_LEDGER_REPORT.md").write_text(_render_report(summary), encoding="utf-8")

    print(f"v53_evidence_ledger audited_bundles={summary['audited_bundle_count']}")
    print(f"valid_bundles={summary['valid_bundle_count']}")
    print(f"ledger_chain_valid={summary['ledger_chain_valid']}")
    return summary


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="BioGPU-Core v5.3 evidence ledger runner")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    args = parser.parse_args()
    run(args.project_root, args.out_dir)


if __name__ == "__main__":
    main()
