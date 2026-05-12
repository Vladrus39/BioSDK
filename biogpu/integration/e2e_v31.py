"""BioGPU v3.1 end-to-end integration pass.

This module wires together the existing BioGPU-Core layers:

    run manifest -> encoder -> replay/dry feature substrate -> readout ->
    energy/latency accounting -> audit log -> result bundle

It is intentionally software-only. It does not emit live stimulation settings,
wet-lab recipes, vendor pinouts, wiring instructions, or MEA safety limits.
"""
from __future__ import annotations

import csv
import json
import math
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal

from biogpu.safety.boundary_v35 import assert_no_forbidden_payload_v35

from biogpu.encoding.base_v26 import AbstractBioPattern, EncoderInput
from biogpu.encoding.registry_v26 import encode_with_registry_v26
from biogpu.metrics.baseline_v29 import compare_baselines_v29
from biogpu.metrics.energy_model_v29 import default_biogpu_a1_energy_input_v29, estimate_energy_v29
from biogpu.metrics.latency_model_v29 import default_biogpu_a1_latency_v29, estimate_latency_v29
from biogpu.readout.base_v27 import ReadoutFeatureBatch, ReadoutPrediction
from biogpu.readout.registry_v27 import build_readout_registry_v27
from biogpu.runtime.session_manager_v24 import (
    BioGPUAuditLog,
    BioGPUResultBundler,
    BioGPURunManifest,
    artifact_ref,
    build_v24_manifest,
    validate_manifest,
)

RunModeV31 = Literal["replay", "dry_run", "power_pc"]

UNSAFE_TERMS_V31 = {
    "voltage",
    "amplitude",
    "pulse_width",
    "frequency",
    "current",
    "charge_density",
    "pinout",
    "wiring",
    "wet_lab_recipe",
    "media_recipe",
    "incubation_formula",
}


@dataclass(frozen=True)
class E2EConfigV31:
    version: str = "v3.1"
    run_mode: RunModeV31 = "replay"
    encoder_id: str = "spatial_v26"
    decoder_id: str = "centroid_v27"
    task_id: str = "B0_target_vs_random_electrode:e2e_demo"
    payload: list[float] = field(default_factory=lambda: [0.0, 1.0, 2.0, 3.0, 2.0, 1.0])
    task_count_for_energy: int = 1000
    run_duration_s_for_energy: float = 60.0
    operator_note: str = "v3.1 deterministic software-only E2E integration pass"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ReplayObservationV31:
    observation_id: str
    feature_names: list[str]
    features: list[float]
    source_pattern_id: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class E2ERunSummaryV31:
    version: str
    session_id: str
    run_mode: str
    encoder_id: str
    decoder_id: str
    pattern_id: str
    prediction: Any
    confidence: float | None
    success: bool
    validation_errors: list[str]
    artifact_count: int
    result_bundle: str
    safety_boundary: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _assert_no_unsafe_payload(obj: Any) -> None:
    assert_no_forbidden_payload_v35(obj, context="v3.1 E2E payload")

def build_manifest_v31(config: E2EConfigV31) -> BioGPURunManifest:
    manifest = build_v24_manifest(
        run_mode=config.run_mode,
        benchmark_ids=[
            "B0_target_vs_random_electrode",
            "B5_energy_latency_comparison",
        ],
        hardware_profile="software_only_v31_e2e",
        operator_note=config.operator_note,
    )
    manifest.config["v31_e2e"] = {
        "encoder_id": config.encoder_id,
        "decoder_id": config.decoder_id,
        "task_id": config.task_id,
        "software_only": True,
        "live_output_performed": False,
    }
    return manifest


def pattern_to_replay_observation_v31(pattern: AbstractBioPattern) -> ReplayObservationV31:
    pattern.validate()
    weights = [float(w) for w in pattern.weights]
    n = len(weights)
    abs_sum = sum(abs(w) for w in weights)
    signed_sum = sum(weights)
    mean = signed_sum / n if n else 0.0
    max_w = max(weights) if weights else 0.0
    min_w = min(weights) if weights else 0.0
    energy_like = sum(w * w for w in weights)
    sparsity_like = sum(1 for w in weights if abs(w) > 1e-9) / n if n else 0.0
    time_span = max(pattern.time_bins) - min(pattern.time_bins) if pattern.time_bins else 0.0
    features = [
        float(n),
        abs_sum,
        signed_sum,
        mean,
        max_w,
        min_w,
        energy_like,
        sparsity_like,
        float(len(set(pattern.target_groups))),
        time_span,
    ]
    names = [
        "n_weights",
        "abs_sum",
        "signed_sum",
        "mean_weight",
        "max_weight",
        "min_weight",
        "energy_like_weight_sum_sq",
        "sparsity_like_nonzero_fraction",
        "n_unique_target_groups",
        "abstract_time_span",
    ]
    obs = ReplayObservationV31(
        observation_id=f"obs:{pattern.pattern_id}",
        feature_names=names,
        features=features,
        source_pattern_id=pattern.pattern_id,
        metadata={
            "replay_substrate": "deterministic_v31_feature_projection",
            "note": "Software-only replay observation derived from abstract pattern. No live hardware output.",
        },
    )
    _assert_no_unsafe_payload(obs.to_dict())
    return obs


def build_training_batch_v31(observation: ReplayObservationV31) -> ReadoutFeatureBatch:
    x = [float(v) for v in observation.features]
    # Build a tiny deterministic target/control training set around the observation.
    # This is for integration testing only; it is not a scientific benchmark score.
    target_1 = x
    target_2 = [v * 0.98 + 0.02 for v in x]
    control_1 = [(-v if i not in {0, 7, 8} else max(0.0, v * 0.5)) for i, v in enumerate(x)]
    control_2 = [v * 0.10 for v in x]
    batch = ReadoutFeatureBatch(
        feature_names=observation.feature_names,
        X=[target_1, target_2, control_1, control_2],
        y=["target_response", "target_response", "control_response", "control_response"],
        metadata={
            "source": "v31 deterministic integration training scaffold",
            "scientific_status": "integration_test_only_not_publication_metric",
        },
    )
    batch.validate()
    _assert_no_unsafe_payload(batch.to_dict())
    return batch


def run_readout_v31(batch: ReadoutFeatureBatch, observation: ReplayObservationV31, decoder_id: str) -> ReadoutPrediction:
    registry = build_readout_registry_v27()
    if decoder_id not in registry:
        raise KeyError(f"Unknown decoder_id: {decoder_id}")
    decoder = registry[decoder_id]
    decoder.fit(batch)
    prediction = decoder.predict_one(observation.features, observation.feature_names)
    _assert_no_unsafe_payload(prediction.to_dict())
    return prediction


def render_e2e_report_v31(summary: E2ERunSummaryV31, manifest_errors: list[str]) -> str:
    status = "PASS" if summary.success and not manifest_errors else "CHECK"
    return f"""# BioGPU-Core v3.1 End-to-End Integration Report

## Status

`{status}`

## Chain executed

```text
run_manifest
→ EncoderInput
→ encoder `{summary.encoder_id}`
→ AbstractBioPattern `{summary.pattern_id}`
→ deterministic replay observation
→ ReadoutFeatureBatch
→ decoder `{summary.decoder_id}`
→ ReadoutPrediction
→ energy/latency/baseline accounting
→ audit log
→ result bundle
```

## Prediction

- prediction: `{summary.prediction}`
- confidence: `{summary.confidence}`
- success: `{summary.success}`

## Validation errors

{json.dumps(manifest_errors, indent=2, ensure_ascii=False)}

## Result bundle

`{summary.result_bundle}`

## Boundary

This is a software-only integration pass. It proves that the project layers can be wired together under one manifest and result bundle. It does not prove live BioGPU operation and does not prove GPU advantage.
"""


def write_csv_dicts(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    keys: list[str] = []
    for row in rows:
        for key in row.keys():
            if key not in keys:
                keys.append(key)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=keys)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def run_e2e_v31(output_dir: str | Path, config: E2EConfigV31 | None = None) -> E2ERunSummaryV31:
    cfg = config or E2EConfigV31()
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    audit = BioGPUAuditLog()

    _assert_no_unsafe_payload(cfg.to_dict())
    audit.add("config_loaded", "ok", config=cfg.to_dict())

    manifest = build_manifest_v31(cfg)
    manifest_errors = validate_manifest(manifest)
    (out / "run_manifest_v31.json").write_text(json.dumps(manifest.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    audit.add("manifest_created", "ok" if not manifest_errors else "warning", validation_errors=manifest_errors)

    encoder_input = EncoderInput(task_id=cfg.task_id, payload=cfg.payload, metadata={"v31": True, "software_only": True})
    pattern = encode_with_registry_v26(cfg.encoder_id, encoder_input)
    (out / "encoded_pattern_v31.json").write_text(pattern.to_json(), encoding="utf-8")
    audit.add("encoded_pattern_created", "ok", pattern_id=pattern.pattern_id, encoder_id=cfg.encoder_id)

    observation = pattern_to_replay_observation_v31(pattern)
    (out / "replay_observation_v31.json").write_text(json.dumps(observation.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    audit.add("replay_observation_created", "ok", observation_id=observation.observation_id)

    batch = build_training_batch_v31(observation)
    (out / "readout_feature_batch_v31.json").write_text(json.dumps(batch.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    audit.add("readout_feature_batch_created", "ok", rows=len(batch.X), features=len(batch.feature_names))

    prediction = run_readout_v31(batch, observation, cfg.decoder_id)
    (out / "readout_prediction_v31.json").write_text(json.dumps(prediction.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    success = prediction.prediction == "target_response"
    audit.add("readout_prediction_created", "ok" if success else "warning", prediction=prediction.prediction, confidence=prediction.confidence)

    energy_input = default_biogpu_a1_energy_input_v29(cfg.task_count_for_energy, cfg.run_duration_s_for_energy)
    energy = estimate_energy_v29(energy_input)
    latency = estimate_latency_v29(default_biogpu_a1_latency_v29())
    baseline_comparison = compare_baselines_v29(cfg.task_count_for_energy, cfg.run_duration_s_for_energy)
    energy_report = {
        "version": "v3.1",
        "energy": energy.to_dict(),
        "latency": latency.to_dict(),
        "baseline_comparison": baseline_comparison,
        "claim_boundary": "Accounting scaffold only; replace placeholders with measured power/latency before any advantage claim.",
    }
    (out / "energy_latency_report_v31.json").write_text(json.dumps(energy_report, indent=2, ensure_ascii=False), encoding="utf-8")
    audit.add("energy_latency_accounting_created", "ok", joules_per_task=energy.joules_per_task, latency_ms=latency.total_ms)

    baseline_rows = []
    for row in baseline_comparison["baselines"]:
        baseline_rows.append({
            "baseline_id": row["baseline_id"],
            "substrate_class": row["substrate_class"],
            "joules_per_task": row["energy"]["joules_per_task"],
            "total_latency_ms": row["latency"]["total_ms"],
            "energy_ratio_vs_gpu_placeholder": row["ratios_vs_gpu_placeholder"]["energy_per_task_ratio"],
            "latency_ratio_vs_gpu_placeholder": row["ratios_vs_gpu_placeholder"]["latency_ratio"],
        })
    write_csv_dicts(out / "baseline_comparison_v31.csv", baseline_rows)

    artifacts = []
    # Write audit before calculating artifact refs.
    audit.write_jsonl(out / "audit_log_v31.jsonl")

    interim_summary = {
        "version": "v3.1",
        "session_id": manifest.session_id,
        "run_mode": cfg.run_mode,
        "encoder_id": cfg.encoder_id,
        "decoder_id": cfg.decoder_id,
        "pattern_id": pattern.pattern_id,
        "prediction": prediction.prediction,
        "confidence": prediction.confidence,
        "success": success,
        "validation_errors": manifest_errors,
        "live_output_performed": False,
        "gpu_advantage_proven": False,
        "live_biogpu_prototype_proven": False,
    }
    (out / "e2e_summary_v31.json").write_text(json.dumps(interim_summary, indent=2, ensure_ascii=False), encoding="utf-8")

    for p in sorted(out.glob("*")):
        if p.is_file() and p.suffix in {".json", ".jsonl", ".csv"}:
            artifacts.append(artifact_ref(p, out, "v31_e2e_artifact", required=p.name in {"run_manifest_v31.json", "e2e_summary_v31.json"}))

    summary = E2ERunSummaryV31(
        version="v3.1",
        session_id=manifest.session_id,
        run_mode=cfg.run_mode,
        encoder_id=cfg.encoder_id,
        decoder_id=cfg.decoder_id,
        pattern_id=pattern.pattern_id,
        prediction=prediction.prediction,
        confidence=prediction.confidence,
        success=success and not manifest_errors,
        validation_errors=manifest_errors,
        artifact_count=len(artifacts),
        result_bundle="biogpu_v31_e2e_result_bundle.zip",
        safety_boundary=[
            "software-only replay/dry integration",
            "no live stimulation settings",
            "no wet-lab recipe",
            "no vendor pinout or wiring procedure",
            "no GPU advantage claim",
        ],
    )
    (out / "e2e_summary_v31.json").write_text(json.dumps(summary.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    (out / "BIOGPU_V31_E2E_REPORT.md").write_text(render_e2e_report_v31(summary, manifest_errors), encoding="utf-8")
    audit.add("report_created", "ok", report="BIOGPU_V31_E2E_REPORT.md")
    audit.write_jsonl(out / "audit_log_v31.jsonl")

    bundler = BioGPUResultBundler(out)
    bundle = bundler.build_bundle("biogpu_v31_e2e_result_bundle.zip")
    summary = E2ERunSummaryV31(
        **{**summary.to_dict(), "result_bundle": bundle.name, "artifact_count": len(list(out.glob("*"))) - 1}
    )
    (out / "e2e_summary_v31.json").write_text(json.dumps(summary.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return summary
