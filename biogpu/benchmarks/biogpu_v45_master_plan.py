from __future__ import annotations

from pathlib import Path
import json

from biogpu.beta.master_plan_v45 import (
    VERSION,
    access_tiers,
    build_cleanup_md,
    build_document_index,
    build_master_markdown,
    cleanup_items,
    dataset_sources,
    generate_outputs,
    roadmap_items,
)
from biogpu.enterprise.security_data_v45 import rules_as_dicts

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs" / "realdata_zenodo_14363732_v45_master_plan"


def write_docs() -> None:
    (ROOT / "docs").mkdir(exist_ok=True)
    (ROOT / "beta").mkdir(exist_ok=True)
    (ROOT / "data" / "templates").mkdir(parents=True, exist_ok=True)
    (ROOT / "docs" / "MASTER_PROJECT_PLAN_V45.md").write_text(build_master_markdown(), encoding="utf-8")
    (ROOT / "docs" / "DOCUMENT_INDEX_V45.md").write_text(build_document_index(), encoding="utf-8")
    (ROOT / "docs" / "REPOSITORY_CLEANUP_AUDIT_V45.md").write_text(build_cleanup_md(), encoding="utf-8")
    (ROOT / "docs" / "V45_SECURITY_DATA_HANDLING_ENTERPRISE_PILOT.md").write_text(build_security_md(), encoding="utf-8")
    (ROOT / "docs" / "POWERPC_VALIDATION_RUNBOOK_V45.md").write_text(build_powerpc_md(), encoding="utf-8")
    (ROOT / "docs" / "DATASET_API_COMPLETION_CHECKLIST_V45.md").write_text(build_dataset_checklist_md(), encoding="utf-8")
    (ROOT / "docs" / "ENTERPRISE_PILOT_PACK_V45.md").write_text(build_enterprise_pilot_md(), encoding="utf-8")
    (ROOT / "README_BIOGPU_CORE_V45.md").write_text(build_readme_md(), encoding="utf-8")
    (ROOT / "beta" / "PRIVATE_BETA_QUICKSTART.md").write_text(build_beta_quickstart_md(), encoding="utf-8")
    (ROOT / "beta" / "BETA_FEEDBACK_FORM.md").write_text(build_feedback_md(), encoding="utf-8")
    template = {
        "version": VERSION,
        "run_mode": "replay_or_readonly",
        "access_tier": "Research/Lab Evaluation",
        "dataset_id": "zenodo_14363732_preprocessed",
        "split_policy": "lineage_strict",
        "decoder": "logistic_l2_v27",
        "shuffle_controls": 100,
        "bootstrap": False,
        "blocked_live_actuation": True,
    }
    (ROOT / "data" / "templates" / "v45_master_beta_manifest_template.json").write_text(json.dumps(template, indent=2), encoding="utf-8")


def build_readme_md() -> str:
    return """# BioGPU-Core v4.5

BioGPU-Core is an enterprise-oriented BioSDK for living neural compute. This release creates a single source of truth and enterprise/security package.

Start with:

1. `docs/MASTER_PROJECT_PLAN_V45.md`
2. `docs/DOCUMENT_INDEX_V45.md`
3. `beta/PRIVATE_BETA_QUICKSTART.md`
4. `docs/POWERPC_VALIDATION_RUNBOOK_V45.md`
5. `docs/V45_SECURITY_DATA_HANDLING_ENTERPRISE_PILOT.md`

Current status: ready for private technical preview, not yet ready for broad external beta claims. Heavy power-PC validation is still required.
"""


def build_security_md() -> str:
    lines = ["# v4.5 Security / Data Handling / Enterprise Pilot\n"]
    lines.append("## Principle\nEarly testers receive maximum safe software-level access. Live biological actuation remains blocked unless a lab/vendor-approved protocol exists.\n")
    lines.append("## Data handling rules\n")
    for r in rules_as_dicts():
        lines.append(f"- **{r['id']} ({r['scope']})**: {r['rule']} Required for: {', '.join(r['required_for'])}.")
    lines.append("\n## Enterprise pilot boundary\nThe first paid enterprise product should be read-only/replay/on-prem or hosted read-only. Live shadow is premium. Closed-loop actuation is a separate approved add-on.\n")
    return "\n".join(lines) + "\n"


def build_powerpc_md() -> str:
    return """# v4.5 Power-PC Validation Runbook

## Goal
Before broad beta claims, run the project on a workstation/server and produce paper-grade result bundles.

## Required runs
1. Re-run v3.5/v3.6 smoke checks.
2. Run `full_shuffle_1000` with lineage-strict splits.
3. Run `extended_methods_5000` if compute budget permits.
4. Run bootstrap confidence intervals.
5. Compare centroid, diag-gaussian, logistic regression, and linear SVM.
6. Produce global paper table: dataset/task/split/decoder/ablation/accuracy/balanced accuracy/shuffle mean/p-value/95% CI.
7. Mark negative findings honestly.

## Required data expansion
- Zenodo raw HDF5 / TTL reconstruction.
- DANDI/NWB task-aligned parser.
- AllenSDK visual coding/orientation benchmark.
- User-uploaded beta data import.

## Gate
The project may enter broader beta only after the power-PC result bundle is generated and reviewed.
"""


def build_dataset_checklist_md() -> str:
    lines = ["# v4.5 Dataset/API Completion Checklist\n"]
    for ds in dataset_sources():
        lines.append(f"- [ ] **{ds.id}** — {ds.purpose}. Required before beta: `{ds.required_before_beta}`. Power-PC required: `{ds.power_pc_required}`.")
    return "\n".join(lines) + "\n"


def build_enterprise_pilot_md() -> str:
    return """# v4.5 Enterprise Pilot Pack

## Pilot objective
Validate BioGPU-Core as a BioSDK for replay/read-only neural data workflows, result bundles, and safe enterprise integration.

## What pilot users receive
- SDK or Docker/on-prem package.
- Hosted server access if selected.
- Sample manifests and curated datasets.
- Own-data import path.
- Read-only/mock API connectors.
- BioLLM tool interface.
- Result bundle and audit log export.

## What is not included by default
- Live stimulation.
- Electrode actuation.
- Vendor write commands.
- Wet-lab control.
- Free-form closed-loop.

## Success criteria
- Tester can install/run SDK or hosted workflow.
- Tester can import data or use sample dataset.
- Tester can generate result bundle.
- Tester can verify safety rejection of unsafe fields.
- Tester provides feedback through beta form.
"""


def build_beta_quickstart_md() -> str:
    return """# Private Beta Quickstart v4.5

## Local SDK smoke
```bash
python -m pytest tests/test_biogpu_v45_master_plan.py
python -m biogpu.benchmarks.biogpu_v45_master_plan
```

## What to test
1. Read `docs/MASTER_PROJECT_PLAN_V45.md`.
2. Run sample manifest from `data/templates/v45_master_beta_manifest_template.json`.
3. Import sample or own neural data through safe import mode.
4. Run replay/read-only benchmark.
5. Download/check result bundle.
6. Confirm unsafe live-control fields are rejected.
7. Fill `beta/BETA_FEEDBACK_FORM.md`.
"""


def build_feedback_md() -> str:
    return """# BioGPU-Core Private Beta Feedback Form

## Tester
- Organization:
- Role:
- Deployment mode: hosted / local / Docker / on-prem

## Results
- Dataset tested:
- Benchmark manifest:
- Result bundle path/hash:
- Did the run complete? yes/no
- Were unsafe commands blocked? yes/no

## Feedback
- Installation issues:
- Data import issues:
- Metrics/reporting issues:
- Missing enterprise features:
- Would you evaluate a paid read-only/on-prem license? yes/no
"""


def main() -> None:
    write_docs()
    generate_outputs(OUT)
    (OUT / "security_rules_v45.json").write_text(json.dumps(rules_as_dicts(), indent=2), encoding="utf-8")
    print(json.dumps({
        "version": VERSION,
        "status": "ok",
        "single_source_of_truth": "docs/MASTER_PROJECT_PLAN_V45.md",
        "roadmap_items": len(roadmap_items()),
        "cleanup_items": len(cleanup_items()),
        "access_tiers": len(access_tiers()),
        "dataset_sources": len(dataset_sources()),
    }, indent=2))


if __name__ == "__main__":
    main()
