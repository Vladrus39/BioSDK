"""BioGPU v4.7 final PC runner patch and handoff checklist."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List


@dataclass(frozen=True)
class FinalPCRunStepV47:
    step_id: str
    title: str
    command: str
    expected_output: str
    required_before_beta: bool
    estimated_environment: str

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def get_first_72h_steps_v47() -> List[FinalPCRunStepV47]:
    """Ordered PC handoff sequence. Heavy commands are explicit wrappers, not TODO placeholders."""
    return [
        FinalPCRunStepV47('H00', 'Unpack and create Python environment', 'python3.11 -m venv .venv && source .venv/bin/activate && pip install -U pip && pip install -r requirements.txt && pip install -e .', 'Editable BioGPU-Core install passes pip check or reports dependency issues.', True, 'power_pc'),
        FinalPCRunStepV47('H01', 'Run current smoke tests', 'bash scripts/run_biogpu_v47_powerpc_smoke.sh', 'py_compile OK, current pytest OK, v4.7 patch summary generated.', True, 'power_pc'),
        FinalPCRunStepV47('H02', 'Copy and validate full preprocessed MEA asset', 'mkdir -p data/external && cp /path/to/Pre_processed_MEA_data.zip data/external/Pre_processed_MEA_data.zip && bash scripts/import_preprocessed_mea_data_v46.sh data/external/Pre_processed_MEA_data.zip', 'SHA256 matches 502afab... and archive profile matches expected structure.', True, 'power_pc'),
        FinalPCRunStepV47('H03', 'Reproduce compact old-style v3.3 sweep', 'bash scripts/run_biogpu_v47_powerpc_stage1_v33_compact.sh', 'Best compact result should be in the same family as v3.3 evidence; exact shuffle numbers may differ by seed.', True, 'power_pc'),
        FinalPCRunStepV47('H04', 'Reproduce compact lineage-strict v3.6 sweep', 'bash scripts/run_biogpu_v47_powerpc_stage2_v36_lineage_compact.sh', 'Lineage-strict results generated with lineages held out as groups.', True, 'power_pc'),
        FinalPCRunStepV47('H05', 'Run full_shuffle_1000', 'bash scripts/run_biogpu_v47_powerpc_full_shuffle_1000.sh', 'outputs/powerpc_full_shuffle_1000 contains JSON/CSV result tables and shuffled controls.', True, 'power_pc'),
        FinalPCRunStepV47('H06', 'Run extended_methods_5000 after full run is stable', 'bash scripts/run_biogpu_v47_powerpc_extended_methods_5000.sh', 'outputs/powerpc_extended_methods_5000 contains supplementary method sweeps.', False, 'power_pc_or_server'),
        FinalPCRunStepV47('H07', 'Prepare raw HDF5 download manifest', 'cp data/templates/v47_raw_hdf5_download_manifest_template.json data/external/raw_hdf5_download_manifest.json && $EDITOR data/external/raw_hdf5_download_manifest.json', 'Manifest has official URL/checksum/size fields filled before download.', True, 'power_pc_or_server'),
        FinalPCRunStepV47('H08', 'Download/inspect Zenodo raw HDF5 package', 'bash scripts/download_zenodo_14363732_raw_hdf5_v47.sh data/external/raw_hdf5_download_manifest.json', 'Raw package downloaded or clear manual-download instruction emitted; HDF5 inspection next.', True, 'power_pc_or_server'),
        FinalPCRunStepV47('H09', 'Measure latency and energy for fixed benchmark', 'bash scripts/run_biogpu_v47_latency_energy_measurement.sh', 'outputs/powerpc_latency_energy contains timing report and reproducibility manifest.', True, 'power_pc'),
        FinalPCRunStepV47('H10', 'Package final PC result bundle', 'bash scripts/package_biogpu_v47_powerpc_results.sh', 'outputs/biogpu_v47_powerpc_final_result_bundle.zip generated.', True, 'power_pc'),
    ]


def get_required_evidence_paths_v47() -> List[str]:
    return [
        'evidence/outputs/realdata_zenodo_14363732_v15_readout/pulse_feature_matrix.npz',
        'evidence/outputs/realdata_zenodo_14363732_v15_readout/pulse_feature_metadata.csv',
        'evidence/outputs/realdata_zenodo_14363732_v15_readout/pulse_feature_columns.txt',
        'evidence/outputs/realdata_zenodo_14363732_v33_paper_sweep/sweep_summary_v33.json',
        'evidence/outputs/realdata_zenodo_14363732_v36_lineage_bootstrap/v36_summary.json',
        'EVIDENCE_INDEX_V46.md',
    ]


def get_v47_patch_policy() -> Dict[str, object]:
    return {
        'release': 'BioGPU-Core v4.7 Final PC Runner Patch',
        'purpose': 'Make v4.6 evidence package directly actionable on a power PC without recovering commands from chat history.',
        'full_dataset_embedded': False,
        'full_dataset_required_external_file': 'Pre_processed_MEA_data.zip',
        'expected_preprocessed_sha256': '502afab79d3a843dc16a65d02432ed1d3bcb77bd38179952e74399b420c122f6',
        'unsafe_live_control': 'blocked_by_default',
        'access_policy': 'maximum_safe_software_access; live actuation remains approval-gated',
        'heavy_scripts_are_placeholders': False,
        'raw_hdf5_download': 'manifest-driven; URL/checksum must be filled from official source before download',
        'pytest_policy': 'PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 and tests/current only for release validation',
    }


def validate_v47_project(root: str | Path = '.') -> Dict[str, object]:
    root = Path(root)
    required = get_required_evidence_paths_v47()
    script_paths = [
        'scripts/run_biogpu_v47_powerpc_smoke.sh',
        'scripts/run_biogpu_v47_powerpc_stage1_v33_compact.sh',
        'scripts/run_biogpu_v47_powerpc_stage2_v36_lineage_compact.sh',
        'scripts/run_biogpu_v47_powerpc_full_shuffle_1000.sh',
        'scripts/run_biogpu_v47_powerpc_extended_methods_5000.sh',
        'scripts/download_zenodo_14363732_raw_hdf5_v47.sh',
        'scripts/run_biogpu_v47_latency_energy_measurement.sh',
        'scripts/package_biogpu_v47_powerpc_results.sh',
    ]
    doc_paths = [
        'docs/POWERPC_FIRST_72_HOURS_V47.md',
        'docs/FINAL_HANDOFF_CHECKLIST_V47.md',
        'docs/RAW_HDF5_DOWNLOAD_MANIFEST_V47.md',
        'docs/MASTER_PROJECT_PLAN_V47.md',
        'beta/BETA_TESTER_CHECKLIST.md',
        'beta/API_EXAMPLES_V47.md',
        'beta/ON_PREM_DOCKER_RUNBOOK.md',
        'beta/PRIVATE_BETA_ACCEPTANCE_CRITERIA.md',
    ]
    missing = [p for p in required + script_paths + doc_paths if not (root / p).exists()]
    todo_scripts = []
    for sp in script_paths:
        path = root / sp
        if path.exists():
            txt = path.read_text(encoding='utf-8', errors='ignore')
            if 'TODO' in txt and 'not a TODO placeholder' not in txt:
                todo_scripts.append(sp)
    return {
        'policy': get_v47_patch_policy(),
        'missing_paths': missing,
        'todo_scripts': todo_scripts,
        'evidence_paths_present': [p for p in required if (root / p).exists()],
        'first_72h_steps': [s.to_dict() for s in get_first_72h_steps_v47()],
        'ready_for_power_pc_handoff': not missing and not todo_scripts,
    }
