"""Generate v4.2 dataset registry and import skeleton outputs."""

from __future__ import annotations

from pathlib import Path
import csv
import json
import platform
import sys
import zipfile

from biogpu.datasets.registry_v42 import build_default_dataset_registry_v42, DatasetAccessModeV42
from biogpu.datasets.importers_v42 import DatasetImportRequestV42, build_importer_catalog_v42


def _write_markdown_report(outdir: Path, registry, import_results):
    lines = []
    lines.append("# BioGPU-Core v4.2 — Dataset Registry + Import Skeleton")
    lines.append("")
    lines.append("v4.2 adds the data expansion layer needed before private beta: curated public datasets, external read-only/API sources, vendor exports, and user uploads.")
    lines.append("")
    lines.append("## Registry summary")
    lines.append("")
    lines.append(f"- Dataset entries: **{len(registry.entries)}**")
    lines.append(f"- P0 entries: **{len(registry.by_priority('P0'))}**")
    lines.append(f"- P1 entries: **{len(registry.by_priority('P1'))}**")
    lines.append(f"- Read-only replay entries: **{len(registry.by_access_mode(DatasetAccessModeV42.READ_ONLY_REPLAY))}**")
    lines.append(f"- Live-shadow read-only entries: **{len(registry.by_access_mode(DatasetAccessModeV42.LIVE_SHADOW_READ_ONLY))}**")
    lines.append("")
    lines.append("## What is safe in v4.2")
    lines.append("")
    lines.append("Early beta testers can receive maximum software-level access: replay, uploads, registry, read-only imports, BioLLM tool interface, result bundles, and power-PC scripts.")
    lines.append("")
    lines.append("v4.2 still blocks live biological actuation: no electrode stimulation, no pinout/wiring, no wet-lab environment control, and no uncontrolled closed-loop.")
    lines.append("")
    lines.append("## Priority datasets")
    lines.append("")
    lines.append("| Priority | Dataset | Status | Importer | Produces | Blockers |")
    lines.append("|---|---|---|---|---|---|")
    for entry in registry.entries.values():
        lines.append(
            f"| {entry.beta_release_priority} | `{entry.dataset_id}` | {entry.status} | `{entry.import_plan.importer_id}` | {entry.import_plan.produces} | {'; '.join(entry.blockers) or '-'} |"
        )
    lines.append("")
    lines.append("## Import dry-run results")
    lines.append("")
    lines.append("| Dataset | Importer | Status | Live control performed | Warnings |")
    lines.append("|---|---|---|---:|---|")
    for r in import_results:
        lines.append(f"| `{r['dataset_id']}` | `{r['importer_id']}` | {r['status']} | {r['live_control_performed']} | {'; '.join(r['warnings']) or '-'} |")
    lines.append("")
    lines.append("## Power-PC handoff")
    lines.append("")
    lines.append("The next heavy work remains outside this lightweight environment: Zenodo raw HDF5/TTL reconstruction, DANDI/Allen downloads, full shuffles, extended methods, and bootstrap confidence intervals.")
    (outdir / "BIOGPU_V42_DATASET_REGISTRY_REPORT.md").write_text("\n".join(lines), encoding="utf-8")


def main(output_dir: str = "outputs/realdata_zenodo_14363732_v42_dataset_registry") -> dict:
    outdir = Path(output_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    registry = build_default_dataset_registry_v42()
    errors = registry.validate()

    registry.write_json(outdir / "v42_dataset_registry.json")
    registry.write_csv(outdir / "v42_dataset_registry.csv")

    catalog = build_importer_catalog_v42()
    importer_rows = []
    for importer_id, imp in sorted(catalog.items()):
        importer_rows.append({
            "importer_id": importer_id,
            "produces": imp.produces,
            "supported_extensions": ";".join(imp.supported_extensions),
            "supported_modes": ";".join(sorted(imp.supported_modes)),
        })
    with (outdir / "v42_importer_catalog.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["importer_id", "produces", "supported_extensions", "supported_modes"])
        w.writeheader(); w.writerows(importer_rows)

    import_results = []
    for entry in registry.entries.values():
        imp = catalog[entry.import_plan.importer_id]
        mode = entry.access_mode.value
        options = {"read_only_token_expected": True} if entry.import_plan.importer_id == "finalspark_export_v42" else {}
        req = DatasetImportRequestV42(
            dataset_id=entry.dataset_id,
            importer_id=entry.import_plan.importer_id,
            source_uri=f"registry://{entry.dataset_id}",
            mode=mode,
            options=options,
        )
        import_results.append(imp.inspect(req).to_dict())
    (outdir / "v42_import_dryrun_results.json").write_text(json.dumps(import_results, indent=2, ensure_ascii=False), encoding="utf-8")

    summary = {
        "version": "v4.2",
        "dataset_count": len(registry.entries),
        "importer_count": len(catalog),
        "validation_errors": errors,
        "live_control_performed": any(r["live_control_performed"] for r in import_results),
        "p0_datasets": [e.dataset_id for e in registry.by_priority("P0")],
        "p1_datasets": [e.dataset_id for e in registry.by_priority("P1")],
        "system_info": {"python": sys.version, "platform": platform.platform()},
    }
    (outdir / "v42_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    _write_markdown_report(outdir, registry, import_results)

    bundle_path = outdir / "biogpu_v42_dataset_registry_bundle.zip"
    with zipfile.ZipFile(bundle_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in outdir.iterdir():
            if p.name != bundle_path.name and p.is_file():
                zf.write(p, arcname=p.name)
    summary["bundle"] = str(bundle_path)
    return summary


if __name__ == "__main__":
    print(json.dumps(main(), indent=2, ensure_ascii=False))
