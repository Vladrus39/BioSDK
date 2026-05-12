"""BioGPU v4.6 clean release metadata and PC transfer plan."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List


@dataclass(frozen=True)
class DeferredPowerPCItemV46:
    item_id: str
    title: str
    stage: str
    where: str
    command_hint: str
    required_before_beta: bool

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def get_powerpc_deferred_items_v46() -> List[DeferredPowerPCItemV46]:
    return [
        DeferredPowerPCItemV46('PC0', 'Repeat reduced smoke tests on target PC', 'stage_0_smoke', 'power_pc', 'bash scripts/run_biogpu_v46_powerpc_smoke.sh', True),
        DeferredPowerPCItemV46('PC1', 'Validate Pre_processed_MEA_data.zip full asset checksum/import', 'stage_0_data', 'power_pc', 'bash scripts/import_preprocessed_mea_data_v46.sh data/external/Pre_processed_MEA_data.zip', True),
        DeferredPowerPCItemV46('PC2', 'Repeat compact lineage-strict sweep using real sklearn readouts', 'stage_1_replay', 'power_pc', 'bash scripts/run_biogpu_v46_powerpc_stage1_compact.sh', True),
        DeferredPowerPCItemV46('PC3', 'Run full_shuffle_1000 with lineage-strict split', 'stage_2_full_stats', 'power_pc', 'bash scripts/run_biogpu_v46_powerpc_full_shuffle_1000.sh', True),
        DeferredPowerPCItemV46('PC4', 'Run extended_methods_5000 for supplementary methods', 'stage_3_extended', 'power_pc_or_server', 'bash scripts/run_biogpu_v46_powerpc_extended_methods_5000.sh', False),
        DeferredPowerPCItemV46('PC5', 'Download and inspect Zenodo raw HDF5/TTL data', 'stage_4_raw_hdf5', 'power_pc_or_server', 'bash scripts/download_zenodo_14363732_raw_hdf5_v46.sh', True),
        DeferredPowerPCItemV46('PC6', 'Build raw-derived pulse/stimulus windows and compare with preprocessed features', 'stage_4_raw_hdf5', 'power_pc_or_server', 'python -m biogpu.benchmarks.biogpu_v46_raw_hdf5_ttl_placeholder', True),
        DeferredPowerPCItemV46('PC7', 'DANDI/NWB discovery and task-aligned parser validation', 'stage_5_dataset_expansion', 'power_pc_or_server', 'python -m biogpu.benchmarks.biogpu_v46_dandi_discovery_placeholder', False),
        DeferredPowerPCItemV46('PC8', 'AllenSDK visual coding orientation benchmark', 'stage_5_dataset_expansion', 'power_pc_or_server', 'python -m biogpu.benchmarks.biogpu_v46_allen_orientation_placeholder', False),
        DeferredPowerPCItemV46('PC9', 'Measure latency and host energy for fixed benchmark runs', 'stage_6_measurement', 'power_pc', 'bash scripts/run_biogpu_v46_latency_energy_measurement.sh', True),
        DeferredPowerPCItemV46('PC10', 'Package final PC result bundle for beta access decision', 'stage_7_release_gate', 'power_pc', 'python -m biogpu.benchmarks.biogpu_v46_pc_result_bundle_placeholder', True),
    ]


def get_clean_release_policy_v46() -> Dict[str, object]:
    return {
        'release_name': 'BioGPU-Core v4.6 Clean Release Candidate',
        'purpose': 'PC-ready clean SDK package with official data asset integration and power-PC validation runbook.',
        'full_dataset_embedded': False,
        'sample_subset_embedded': True,
        'historical_outputs_embedded': False,
        'historical_root_inventory_files_embedded': False,
        'test_policy': 'current-only tests under tests/current; historical tests are excluded from clean release.',
        'pytest_env': 'PYTEST_DISABLE_PLUGIN_AUTOLOAD=1',
        'live_actuation': 'blocked_by_default',
        'next_mandatory_environment': 'power_pc_or_server',
    }


def build_v46_summary() -> Dict[str, object]:
    return {
        'policy': get_clean_release_policy_v46(),
        'deferred_powerpc_items': [x.to_dict() for x in get_powerpc_deferred_items_v46()],
    }
