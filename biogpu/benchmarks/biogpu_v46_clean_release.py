from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path
from datetime import datetime, timezone

from biogpu.datasets.asset_integration_v46 import (
    expected_extracted_data_path,
    profile_preprocessed_mea_extracted_dir,
    profile_preprocessed_mea_zip,
    validate_asset_against_manifest,
    validate_extracted_asset_against_manifest,
)
from biogpu.release.clean_release_v46 import build_v46_summary


def _write(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding='utf-8')


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description='BioGPU v4.6 clean release validation and data asset check')
    parser.add_argument('--project-root', default='.', help='Project root')
    parser.add_argument('--dataset-zip', default='', help='Optional full Pre_processed_MEA_data.zip path')
    parser.add_argument('--dataset-dir', default='', help='Optional extracted Pre_processed_MEA_data directory path')
    parser.add_argument('--out-dir', default='outputs/v46_clean_release')
    args = parser.parse_args(argv)

    root = Path(args.project_root)
    out = Path(args.out_dir)
    manifest_path = root / 'data' / 'assets' / 'zenodo_14363732_preprocessed.asset.json'
    sample_manifest_path = root / 'data' / 'assets' / 'zenodo_14363732_preprocessed_sample.asset.json'
    sample_zip = root / 'data' / 'samples' / 'zenodo_14363732_preprocessed_sample.zip'

    summary = build_v46_summary()
    sample_profile = profile_preprocessed_mea_zip(sample_zip)
    full_profile = profile_preprocessed_mea_zip(args.dataset_zip) if args.dataset_zip else None
    extracted_path = Path(args.dataset_dir) if args.dataset_dir else expected_extracted_data_path(root)
    extracted_profile = profile_preprocessed_mea_extracted_dir(extracted_path)

    result = {
        'release': 'v4.6_clean_release_candidate',
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'python': platform.python_version(),
        'platform': platform.platform(),
        'master_plan': 'docs/MASTER_PROJECT_PLAN_V46.md',
        'pc_runbook': 'docs/POWERPC_TRANSFER_AND_VALIDATION_RUNBOOK_V46.md',
        'asset_manifest': str(manifest_path),
        'sample_asset_manifest': str(sample_manifest_path),
        'sample_profile': sample_profile.to_dict(),
        'full_dataset_profile': full_profile.to_dict() if full_profile else None,
        'extracted_dataset_profile': extracted_profile.to_dict(),
        'summary': summary,
        'ready_for_power_pc': sample_profile.exists and manifest_path.exists(),
    }

    if args.dataset_zip:
        result['full_dataset_validation'] = validate_asset_against_manifest(args.dataset_zip, manifest_path)
    if extracted_profile.exists:
        result['extracted_dataset_validation'] = validate_extracted_asset_against_manifest(extracted_path, manifest_path)

    result['data_gate_status'] = 'missing_full_dataset'
    if result.get('full_dataset_validation', {}).get('valid'):
        result['data_gate_status'] = 'zip_checksum_validated'
    elif result.get('extracted_dataset_validation', {}).get('valid'):
        result['data_gate_status'] = 'extracted_content_profile_validated_zip_hash_pending'

    _write(out / 'v46_clean_release_summary.json', result)
    _write(out / 'v46_powerpc_deferred_items.json', summary['deferred_powerpc_items'])
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
