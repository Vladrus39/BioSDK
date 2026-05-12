from __future__ import annotations

import csv, json, platform, zipfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class PowerPCPresetV34:
    preset_id: str
    description: str
    split_offsets: tuple[int, ...]
    decoders: tuple[str, ...]
    ablations: tuple[str, ...]
    shuffle_count: int
    seed_count: int
    expected_run_count: int
    recommended_machine: str
    command: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PowerPCChecklistItemV34:
    item_id: str
    title: str
    status: str
    details: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PowerPCPackageV34:
    version: str = 'v3.4'
    purpose: str = 'Transfer BioGPU-Core from the current lightweight environment to a stronger PC for full real-data sweeps.'
    presets: tuple[PowerPCPresetV34, ...] = field(default_factory=tuple)
    checklist: tuple[PowerPCChecklistItemV34, ...] = field(default_factory=tuple)
    completed_here: tuple[str, ...] = field(default_factory=tuple)
    must_run_on_power_pc: tuple[str, ...] = field(default_factory=tuple)
    lab_only_future: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            'version': self.version,
            'purpose': self.purpose,
            'presets': [p.to_dict() for p in self.presets],
            'checklist': [c.to_dict() for c in self.checklist],
            'completed_here': list(self.completed_here),
            'must_run_on_power_pc': list(self.must_run_on_power_pc),
            'lab_only_future': list(self.lab_only_future),
        }


def build_powerpc_presets_v34() -> tuple[PowerPCPresetV34, ...]:
    decoders = ('centroid_euclidean', 'centroid_cosine', 'diag_gaussian')
    ablations = ('all_features', 'response_delta_count', 'response_count', 'pre_response_count', 'exact_features')
    return (
        PowerPCPresetV34(
            preset_id='smoke',
            description='Fast sanity run after unpacking on a new machine.',
            split_offsets=(0, 1), decoders=('centroid_euclidean',), ablations=('response_delta_count',), shuffle_count=2, seed_count=1,
            expected_run_count=2,
            recommended_machine='Any laptop/desktop with Python 3.10+ and NumPy.',
            command='python -m biogpu.benchmarks.biogpu_v33_realdata_sweep --shuffle-count 2 --seed 3401 --out-dir outputs/powerpc_smoke_v34'
        ),
        PowerPCPresetV34(
            preset_id='compact_paper_repeat',
            description='Repeat v3.3 compact paper sweep on the strong PC for reproducibility.',
            split_offsets=tuple(range(0, 6)), decoders=decoders, ablations=ablations, shuffle_count=12, seed_count=1,
            expected_run_count=6 * len(decoders) * len(ablations),
            recommended_machine='Modern desktop; no GPU required; SSD recommended.',
            command='python -m biogpu.benchmarks.biogpu_v33_realdata_sweep --shuffle-count 12 --seed 33 --out-dir outputs/powerpc_compact_repeat_v34'
        ),
        PowerPCPresetV34(
            preset_id='full_shuffle_1000',
            description='Paper-grade shuffle control sweep. This is the first serious power-PC target.',
            split_offsets=tuple(range(0, 18)), decoders=decoders, ablations=ablations, shuffle_count=1000, seed_count=3,
            expected_run_count=18 * len(decoders) * len(ablations) * 3,
            recommended_machine='Strong desktop/workstation, 32GB+ RAM, SSD; GPU optional but not required for current NumPy implementation.',
            command='bash scripts/run_biogpu_v34_powerpc_full.sh'
        ),
        PowerPCPresetV34(
            preset_id='extended_methods_5000',
            description='Extended robustness run for a future paper supplement; run only after full_shuffle_1000 passes.',
            split_offsets=tuple(range(0, 18)), decoders=decoders, ablations=ablations, shuffle_count=5000, seed_count=5,
            expected_run_count=18 * len(decoders) * len(ablations) * 5,
            recommended_machine='Workstation/server; long runtime; archive all result bundles.',
            command='bash scripts/run_biogpu_v34_powerpc_extended.sh'
        ),
    )


def build_powerpc_checklist_v34() -> tuple[PowerPCChecklistItemV34, ...]:
    return (
        PowerPCChecklistItemV34('pc01', 'Install Python', 'required', 'Use Python 3.10+; tested here with current environment. Create a virtual environment before running.'),
        PowerPCChecklistItemV34('pc02', 'Install dependencies', 'required', 'Run: python -m pip install -r requirements.txt pytest matplotlib scikit-learn'),
        PowerPCChecklistItemV34('pc03', 'Verify real-data matrix', 'required', 'Check that outputs/realdata_zenodo_14363732_v15_readout contains the v1.5 feature matrix used by v3.2/v3.3.'),
        PowerPCChecklistItemV34('pc04', 'Run smoke test', 'required', 'Run scripts/run_biogpu_v34_powerpc_smoke.sh before any long sweep.'),
        PowerPCChecklistItemV34('pc05', 'Run compact repeat', 'recommended', 'Reproduce v3.3 compact sweep first; compare best run and aggregate tables.'),
        PowerPCChecklistItemV34('pc06', 'Run full shuffle', 'required_for_paper', 'Run 1000-shuffle preset with multiple seeds; keep all logs and bundles.'),
        PowerPCChecklistItemV34('pc07', 'Do not claim live BioGPU/GPU advantage', 'boundary', 'Power-PC replay results are not live MEA proof and not GPU advantage proof.'),
    )


def build_powerpc_package_v34() -> PowerPCPackageV34:
    return PowerPCPackageV34(
        presets=build_powerpc_presets_v34(),
        checklist=build_powerpc_checklist_v34(),
        completed_here=(
            'v3.3 compact real-data replay sweep on 11,547 pulse windows / 354 features',
            'machine-readable result bundle generation',
            'culture-heldout split logic',
            'feature ablation catalog',
            'decoder comparison: centroid_euclidean, centroid_cosine, diag_gaussian',
            'small shuffled-label controls',
        ),
        must_run_on_power_pc=(
            'full 18-offset culture-heldout sweep',
            '1000+ shuffled-label controls per split/decoder/ablation',
            'multi-seed reproducibility runs',
            'bootstrap confidence intervals and publication-grade plots',
            'optional sklearn baselines and calibration curves',
            'archived final result bundles with system info',
        ),
        lab_only_future=(
            'live MEA/HD-MEA stimulation',
            'wetware cultivation and biological protocol validation',
            'live latency measurement',
            'real energy-per-task measurement on hardware',
            'GPU/CPU/BioGPU comparison under matched task and energy boundaries',
        ),
    )


def _write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text('', encoding='utf-8'); return
    keys: list[str] = []
    for row in rows:
        for key in row:
            if key not in keys:
                keys.append(key)
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def render_powerpc_guide_v34(package: PowerPCPackageV34) -> str:
    preset_lines = []
    for p in package.presets:
        preset_lines.append(f"### {p.preset_id}\n\n{p.description}\n\n- Expected run count: `{p.expected_run_count}`\n- Shuffle count: `{p.shuffle_count}`\n- Seed count: `{p.seed_count}`\n- Machine: {p.recommended_machine}\n\n```bash\n{p.command}\n```\n")
    checklist_lines = '\n'.join(f"- **{c.item_id} / {c.status}** — {c.title}: {c.details}" for c in package.checklist)
    done = '\n'.join(f"- {x}" for x in package.completed_here)
    todo = '\n'.join(f"- {x}" for x in package.must_run_on_power_pc)
    lab = '\n'.join(f"- {x}" for x in package.lab_only_future)
    return f"""# BioGPU-Core v3.4 — Power-PC Runner Package

## Purpose

{package.purpose}

## Completed in the current environment

{done}

## What must move to a stronger PC

{todo}

## Presets

{''.join(preset_lines)}

## Checklist

{checklist_lines}

## Future lab-only work

{lab}

## Claim boundary

This package does **not** prove live BioGPU operation and does **not** prove GPU advantage. It prepares reproducible heavy replay runs and result-bundle discipline for the next compute phase.
"""


def write_powerpc_outputs_v34(out_dir: str | Path) -> dict[str, Any]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    package = build_powerpc_package_v34()
    manifest = package.to_dict()
    system_info = {
        'python_version': platform.python_version(),
        'platform': platform.platform(),
        'processor': platform.processor(),
        'machine': platform.machine(),
    }
    _write_json(out / 'v34_powerpc_manifest.json', manifest)
    _write_json(out / 'v34_system_info.json', system_info)
    _write_csv(out / 'v34_powerpc_presets.csv', [p.to_dict() for p in package.presets])
    _write_csv(out / 'v34_powerpc_checklist.csv', [c.to_dict() for c in package.checklist])
    guide = render_powerpc_guide_v34(package)
    (out / 'BIOGPU_V34_POWERPC_RUNNER_GUIDE.md').write_text(guide, encoding='utf-8')
    summary = {
        'version': package.version,
        'status': 'completed_powerpc_transfer_package',
        'preset_count': len(package.presets),
        'required_next_phase': 'run full_shuffle_1000 on strong PC',
        'live_output_performed': False,
        'gpu_advantage_claimed': False,
        'outputs': ['v34_powerpc_manifest.json','v34_powerpc_presets.csv','v34_powerpc_checklist.csv','BIOGPU_V34_POWERPC_RUNNER_GUIDE.md'],
    }
    _write_json(out / 'v34_summary.json', summary)
    bundle_path = out / 'biogpu_v34_powerpc_runner_bundle.zip'
    with zipfile.ZipFile(bundle_path, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for p in out.iterdir():
            if p.is_file() and p.name != bundle_path.name:
                z.write(p, arcname=p.name)
    summary['result_bundle'] = bundle_path.name
    _write_json(out / 'v34_summary.json', summary)
    return summary
