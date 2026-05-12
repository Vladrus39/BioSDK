"""BioGPU v4.6 dataset asset integration utilities.

This module intentionally treats full experimental datasets as external assets.
The SDK release contains checksums, import/validation logic and a small sample
subset, while full archives are placed under data/external/ by the user.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import json
import re
import zipfile
from typing import Dict, Iterable, List, Optional


@dataclass(frozen=True)
class ZipDatasetProfileV46:
    path: str
    exists: bool
    size_bytes: int
    sha256: str
    md5: str
    zip_entries: int
    electrode_csv_count: int
    metadata_csv_count: int
    recording_count: int
    culture_label_count: int
    base_lineage_count: int
    sample_recordings: List[str]

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class ExtractedDatasetProfileV46:
    path: str
    exists: bool
    file_count: int
    size_bytes: int
    content_sha256: str
    electrode_csv_count: int
    metadata_csv_count: int
    recording_count: int
    culture_label_count: int
    base_lineage_count: int
    sample_recordings: List[str]

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def _hash_file(path: Path, algorithm: str) -> str:
    h = hashlib.new(algorithm)
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def _recording_stats_from_relative_names(names: Iterable[str]) -> Dict[str, object]:
    recordings = set()
    cultures = set()
    lineages = set()
    electrode_csv_count = 0
    metadata_csv_count = 0

    for name in names:
        parts = name.replace('\\', '/').split('/')
        if len(parts) >= 5:
            culture = parts[2]
            recording = '/'.join(parts[:4])
            recordings.add(recording)
            cultures.add(culture)
            lineage_match = re.match(r'([^_]+)', culture)
            if lineage_match:
                lineages.add(lineage_match.group(1))
        if re.search(r'electrode\d+\.csv$', name):
            electrode_csv_count += 1
        if name.endswith('meta_data.csv'):
            metadata_csv_count += 1

    return {
        'electrode_csv_count': electrode_csv_count,
        'metadata_csv_count': metadata_csv_count,
        'recording_count': len(recordings),
        'culture_label_count': len(cultures),
        'base_lineage_count': len(lineages),
        'sample_recordings': sorted(recordings)[:5],
    }


def _hash_extracted_tree(root: Path, files: List[Path]) -> str:
    digest = hashlib.sha256()
    for file_path in files:
        relative_name = file_path.relative_to(root).as_posix()
        digest.update(relative_name.encode('utf-8'))
        digest.update(b'\0')
        with file_path.open('rb') as file_handle:
            for chunk in iter(lambda: file_handle.read(1024 * 1024), b''):
                digest.update(chunk)
        digest.update(b'\0')
    return digest.hexdigest()


def profile_preprocessed_mea_zip(path: str | Path) -> ZipDatasetProfileV46:
    p = Path(path)
    if not p.exists():
        return ZipDatasetProfileV46(str(p), False, 0, '', '', 0, 0, 0, 0, 0, 0, [])

    with zipfile.ZipFile(p) as z:
        files = [i.filename for i in z.infolist() if not i.is_dir()]
        stats = _recording_stats_from_relative_names(files)

    return ZipDatasetProfileV46(
        path=str(p),
        exists=True,
        size_bytes=p.stat().st_size,
        sha256=_hash_file(p, 'sha256'),
        md5=_hash_file(p, 'md5'),
        zip_entries=len(files),
        electrode_csv_count=int(stats['electrode_csv_count']),
        metadata_csv_count=int(stats['metadata_csv_count']),
        recording_count=int(stats['recording_count']),
        culture_label_count=int(stats['culture_label_count']),
        base_lineage_count=int(stats['base_lineage_count']),
        sample_recordings=list(stats['sample_recordings']),
    )


def profile_preprocessed_mea_extracted_dir(path: str | Path) -> ExtractedDatasetProfileV46:
    root = Path(path)
    if not root.exists() or not root.is_dir():
        return ExtractedDatasetProfileV46(str(root), False, 0, 0, '', 0, 0, 0, 0, 0, [])

    files = sorted([file_path for file_path in root.rglob('*') if file_path.is_file()], key=lambda item: item.as_posix())
    relative_names = [file_path.relative_to(root).as_posix() for file_path in files]
    stats = _recording_stats_from_relative_names(relative_names)

    return ExtractedDatasetProfileV46(
        path=str(root),
        exists=True,
        file_count=len(files),
        size_bytes=sum(file_path.stat().st_size for file_path in files),
        content_sha256=_hash_extracted_tree(root, files),
        electrode_csv_count=int(stats['electrode_csv_count']),
        metadata_csv_count=int(stats['metadata_csv_count']),
        recording_count=int(stats['recording_count']),
        culture_label_count=int(stats['culture_label_count']),
        base_lineage_count=int(stats['base_lineage_count']),
        sample_recordings=list(stats['sample_recordings']),
    )


def load_asset_manifest(path: str | Path) -> Dict[str, object]:
    return json.loads(Path(path).read_text(encoding='utf-8'))


def validate_asset_against_manifest(zip_path: str | Path, manifest_path: str | Path) -> Dict[str, object]:
    profile = profile_preprocessed_mea_zip(zip_path)
    manifest = load_asset_manifest(manifest_path)
    checks = {
        'exists': profile.exists,
        'sha256_matches': profile.sha256 == manifest.get('sha256'),
        'md5_matches': profile.md5 == manifest.get('md5'),
        'size_matches': profile.size_bytes == manifest.get('size_bytes'),
        'recording_count_matches': profile.recording_count == manifest.get('recording_count'),
        'electrode_csv_count_matches': profile.electrode_csv_count == manifest.get('electrode_csv_count'),
        'metadata_csv_count_matches': profile.metadata_csv_count == manifest.get('metadata_csv_count'),
    }
    return {
        'valid': all(checks.values()),
        'checks': checks,
        'profile': profile.to_dict(),
        'manifest_asset_id': manifest.get('asset_id'),
    }


def validate_extracted_asset_against_manifest(extracted_path: str | Path, manifest_path: str | Path) -> Dict[str, object]:
    profile = profile_preprocessed_mea_extracted_dir(extracted_path)
    manifest = load_asset_manifest(manifest_path)
    checks = {
        'exists': profile.exists,
        'file_count_matches_zip_entries': profile.file_count == manifest.get('zip_entries'),
        'recording_count_matches': profile.recording_count == manifest.get('recording_count'),
        'electrode_csv_count_matches': profile.electrode_csv_count == manifest.get('electrode_csv_count'),
        'metadata_csv_count_matches': profile.metadata_csv_count == manifest.get('metadata_csv_count'),
        'culture_label_count_matches': profile.culture_label_count == manifest.get('culture_label_count'),
        'base_lineage_count_matches': profile.base_lineage_count == manifest.get('base_lineage_count'),
    }
    return {
        'valid': all(checks.values()),
        'validation_level': 'extracted_content_profile_only',
        'does_not_validate_original_zip_hash': True,
        'checks': checks,
        'profile': profile.to_dict(),
        'manifest_asset_id': manifest.get('asset_id'),
    }


def expected_external_data_path(project_root: str | Path = '.') -> Path:
    return Path(project_root) / 'data' / 'external' / 'Pre_processed_MEA_data.zip'


def expected_extracted_data_path(project_root: str | Path = '.') -> Path:
    return Path(project_root) / 'Pre_processed_MEA_data'
