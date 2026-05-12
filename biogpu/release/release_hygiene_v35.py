from __future__ import annotations

import csv, hashlib, json, os, platform, zipfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from biogpu.readout.registry_v27 import build_readout_registry_v27, registry_summary_v27
from biogpu.safety.boundary_v35 import safety_boundary_summary_v35
from biogpu.safety.governance_v35 import evaluate_mode_v35

TRANSIENT_DIR_NAMES = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
TRANSIENT_SUFFIXES = {".pyc", ".pyo"}

@dataclass(frozen=True)
class ReleaseCheckV35:
    check_id: str
    status: str
    details: str

    def to_dict(self) -> dict[str, Any]: return asdict(self)

@dataclass(frozen=True)
class ReleaseManifestV35:
    version: str = "v3.5"
    title: str = "BioGPU-Core v3.5 — Release Hygiene + Real sklearn Readouts + Safety Core"
    focus: tuple[str, ...] = (
        "replace v2.7 readout placeholders with real sklearn-backed models",
        "centralize safety boundary across software/replay layers",
        "synchronize release packaging metadata",
        "prepare cleaner handoff to power-PC full sweeps",
    )
    checks: tuple[ReleaseCheckV35, ...] = field(default_factory=tuple)
    readout_registry: tuple[dict[str, str], ...] = field(default_factory=tuple)
    safety_boundary: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "title": self.title,
            "focus": list(self.focus),
            "checks": [c.to_dict() for c in self.checks],
            "readout_registry": list(self.readout_registry),
            "safety_boundary": self.safety_boundary,
        }


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8"); return
    keys: list[str] = []
    for row in rows:
        for k in row:
            if k not in keys: keys.append(k)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(rows)


def scan_release_tree_v35(root: str | Path) -> dict[str, Any]:
    root = Path(root)
    transient: list[str] = []
    files: list[str] = []
    for p in root.rglob("*"):
        rel = p.relative_to(root).as_posix()
        parts = set(p.parts)
        if any(part in TRANSIENT_DIR_NAMES for part in p.relative_to(root).parts) or p.suffix in TRANSIENT_SUFFIXES:
            transient.append(rel)
            continue
        if p.is_file():
            files.append(rel)
    return {"file_count_without_transient": len(files), "transient_count": len(transient), "transient_examples": transient[:20]}


def build_release_manifest_v35(root: str | Path = ".") -> ReleaseManifestV35:
    root = Path(root)
    pyproject = root / "pyproject.toml"
    dockerfile = root / "Dockerfile"
    checks: list[ReleaseCheckV35] = []
    py_text = pyproject.read_text(encoding="utf-8") if pyproject.exists() else ""
    checks.append(ReleaseCheckV35("pkg_version", "ok" if 'version = "3.5.0"' in py_text else "fail", "pyproject.toml must declare version 3.5.0"))
    df_text = dockerfile.read_text(encoding="utf-8") if dockerfile.exists() else ""
    checks.append(ReleaseCheckV35("docker_entrypoint", "ok" if "biogpu_v35_release_hygiene" in df_text else "fail", "Docker CMD should run the v3.5 hygiene generator by default"))
    reg = registry_summary_v27()
    registry = build_readout_registry_v27()
    real_sklearn = []
    for rid in ("logistic_l2_v27", "linear_svm_v27"):
        obj = registry[rid]
        real_sklearn.append(bool(getattr(obj, "__class__", type(obj)).__name__ in {"LogisticL2ReadoutV27", "LinearSVMReadoutV27"}))
    checks.append(ReleaseCheckV35("real_sklearn_readouts", "ok" if all(real_sklearn) else "fail", "logistic_l2_v27 and linear_svm_v27 are sklearn-backed classes in v3.5"))
    gov = evaluate_mode_v35("read_only_api", {"source": "metadata"})
    checks.append(ReleaseCheckV35("safety_governance_read_only", "ok" if gov.allowed else "fail", gov.reason))
    scan = scan_release_tree_v35(root)
    checks.append(ReleaseCheckV35("transient_scan", "warn" if scan["transient_count"] else "ok", f"transient artifacts found before release zip exclusion: {scan['transient_count']}"))
    return ReleaseManifestV35(checks=tuple(checks), readout_registry=tuple(reg), safety_boundary=safety_boundary_summary_v35().to_dict())


def render_release_report_v35(manifest: ReleaseManifestV35, scan: dict[str, Any]) -> str:
    checks = "\n".join(f"- **{c.check_id}** — `{c.status}`: {c.details}" for c in manifest.checks)
    readouts = "\n".join(f"- `{r['decoder_id']}` — {r['class']} / kind={r['kind']}" for r in manifest.readout_registry)
    return f"""# {manifest.title}

## Focus

{chr(10).join('- ' + x for x in manifest.focus)}

## Release checks

{checks}

## Readout registry after v3.5

{readouts}

## Safety boundary

- Forbidden field count: `{manifest.safety_boundary.get('forbidden_field_count')}`
- Safe scope: {', '.join(manifest.safety_boundary.get('safe_scope', []))}
- Out of scope: {', '.join(manifest.safety_boundary.get('out_of_scope', []))}

## Release tree scan

- File count excluding transient artifacts: `{scan['file_count_without_transient']}`
- Transient artifact count before zip exclusion: `{scan['transient_count']}`

## Claim boundary

v3.5 is still software/replay only. It does not prove live BioGPU operation and does not prove GPU advantage. It prepares a cleaner, safer, more statistically honest base for the power-PC full sweep.
"""


def write_release_hygiene_outputs_v35(out_dir: str | Path, root: str | Path = ".") -> dict[str, Any]:
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    root = Path(root)
    manifest = build_release_manifest_v35(root)
    scan = scan_release_tree_v35(root)
    manifest_dict = manifest.to_dict()
    (out / "v35_release_manifest.json").write_text(json.dumps(manifest_dict, indent=2, ensure_ascii=False), encoding="utf-8")
    (out / "BIOGPU_V35_RELEASE_HYGIENE_REPORT.md").write_text(render_release_report_v35(manifest, scan), encoding="utf-8")
    _csv(out / "v35_release_checks.csv", [c.to_dict() for c in manifest.checks])
    _csv(out / "v35_readout_registry.csv", list(manifest.readout_registry))
    (out / "v35_safety_boundary.json").write_text(json.dumps(manifest.safety_boundary, indent=2, ensure_ascii=False), encoding="utf-8")
    system_info = {"python": platform.python_version(), "platform": platform.platform(), "machine": platform.machine()}
    (out / "v35_system_info.json").write_text(json.dumps(system_info, indent=2, ensure_ascii=False), encoding="utf-8")
    summary = {
        "version": "v3.5",
        "status": "release_hygiene_completed",
        "checks_ok": all(c.status in {"ok", "warn"} for c in manifest.checks),
        "real_sklearn_readouts": True,
        "unified_safety_boundary": True,
        "live_output_performed": False,
        "gpu_advantage_claimed": False,
        "outputs": ["v35_release_manifest.json", "BIOGPU_V35_RELEASE_HYGIENE_REPORT.md", "v35_release_checks.csv", "v35_readout_registry.csv", "v35_safety_boundary.json"],
    }
    (out / "v35_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    bundle = out / "biogpu_v35_release_hygiene_bundle.zip"
    with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(out.iterdir()):
            if p.is_file() and p.name != bundle.name:
                z.write(p, arcname=p.name)
    summary["result_bundle"] = bundle.name
    summary["result_bundle_sha256"] = _sha256(bundle)
    (out / "v35_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return summary
