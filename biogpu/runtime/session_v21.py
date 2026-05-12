from __future__ import annotations

import json, os, platform, shutil, time, zipfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Literal, Any

RunMode = Literal['replay_local','power_pc_full','live_mea_dry_run','live_mea_vendor']

@dataclass(frozen=True)
class BioGPUSessionConfig:
    session_id: str
    version: str = 'v2.1'
    mode: RunMode = 'replay_local'
    substrate: str = 'RealDataReplayBioGPUSubstrate'
    dataset_ref: str | None = None
    benchmark_ids: list[str] = field(default_factory=list)
    readouts: list[str] = field(default_factory=list)
    safety_class: str = 'offline_or_dry_run_only'
    created_unix: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)
    def to_dict(self): return asdict(self)

@dataclass(frozen=True)
class BioGPUResultBundleManifest:
    bundle_id: str
    created_unix: float
    session: dict[str, Any]
    files: list[str]
    environment: dict[str, Any]
    def to_dict(self): return asdict(self)


def default_v21_session(mode: RunMode = 'replay_local') -> BioGPUSessionConfig:
    sid = f"biogpu_{mode}_{int(time.time())}"
    return BioGPUSessionConfig(
        session_id=sid,
        mode=mode,
        dataset_ref='Zenodo 14363732 preprocessed pulse-feature replay' if mode.startswith('replay') or mode == 'power_pc_full' else None,
        benchmark_ids=['B0_target_vs_random_electrode','B1_spot_localization','B2_temporal_pattern_classification','B4_adaptive_closed_loop'],
        readouts=['centroid','logistic_l2','linear_svm'],
        metadata={'note':'v2.1 session schema; live modes require vendor backend and lab SOPs'}
    )


def write_session_file(session: BioGPUSessionConfig, out_dir: str | Path) -> Path:
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    p = out / 'biogpu_session_v21.json'
    p.write_text(json.dumps(session.to_dict(), indent=2, ensure_ascii=False), encoding='utf-8')
    return p


def collect_result_bundle(session: BioGPUSessionConfig, source_dirs: list[str | Path], out_dir: str | Path, bundle_name: str = 'biogpu_result_bundle_v21.zip') -> dict:
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    bundle_root = out / 'bundle_staging_v21'
    if bundle_root.exists(): shutil.rmtree(bundle_root)
    bundle_root.mkdir(parents=True)
    files: list[str] = []
    (bundle_root / 'session.json').write_text(json.dumps(session.to_dict(), indent=2, ensure_ascii=False), encoding='utf-8')
    files.append('session.json')
    for src in source_dirs:
        srcp = Path(src)
        if not srcp.exists():
            continue
        dest_base = bundle_root / srcp.name
        if srcp.is_dir():
            def _ignore(dirpath, names):
                ignored = set()
                for name in names:
                    if name == bundle_root.name or name == bundle_name:
                        ignored.add(name)
                return ignored
            shutil.copytree(srcp, dest_base, dirs_exist_ok=True, ignore=_ignore)
            for p in dest_base.rglob('*'):
                if p.is_file(): files.append(str(p.relative_to(bundle_root)))
        else:
            shutil.copy2(srcp, dest_base)
            files.append(dest_base.name)
    manifest = BioGPUResultBundleManifest(
        bundle_id=bundle_name.replace('.zip',''),
        created_unix=time.time(),
        session=session.to_dict(),
        files=sorted(set(files)),
        environment={'python': platform.python_version(), 'platform': platform.platform(), 'cwd': os.getcwd()}
    )
    (bundle_root / 'manifest.json').write_text(json.dumps(manifest.to_dict(), indent=2, ensure_ascii=False), encoding='utf-8')
    zip_path = out / bundle_name
    if zip_path.exists(): zip_path.unlink()
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for p in bundle_root.rglob('*'):
            if p.is_file(): zf.write(p, p.relative_to(bundle_root))
    return {'bundle_path': str(zip_path), 'file_count': len(manifest.files), 'manifest': manifest.to_dict()}
