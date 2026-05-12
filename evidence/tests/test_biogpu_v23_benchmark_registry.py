from pathlib import Path

from biogpu.benchmarks.registry_v23 import (
    build_biogpu_v23_benchmark_registry,
    validate_registry,
    write_v23_outputs,
)


def test_v23_registry_has_required_tasks():
    registry = build_biogpu_v23_benchmark_registry()
    ids = {task.task_id for task in registry.tasks}
    required = {
        "B0_target_vs_random_electrode",
        "B1_spot_localization",
        "B2_temporal_pattern_classification",
        "B3_orientation_like_encoding",
        "B4_adaptive_closed_loop",
        "B5_energy_latency_comparison",
        "B6_substrate_stability",
    }
    assert required.issubset(ids)


def test_v23_registry_validates_cleanly():
    registry = build_biogpu_v23_benchmark_registry()
    assert validate_registry(registry) == []


def test_v23_each_task_has_core_contracts():
    registry = build_biogpu_v23_benchmark_registry()
    for task in registry.tasks:
        assert task.input_spec.format
        assert task.input_spec.required_fields
        assert task.encoder.name
        assert task.encoder.output_contract
        assert task.encoder.dry_run_checks
        assert task.substrate.hardware_components
        assert task.readout.name
        assert any(metric.primary for metric in task.metrics)
        assert task.controls
        assert task.success_gates


def test_v23_energy_task_has_fairness_gate():
    registry = build_biogpu_v23_benchmark_registry()
    energy = next(task for task in registry.tasks if task.task_id == "B5_energy_latency_comparison")
    gates = {gate.gate_id for gate in energy.success_gates}
    controls = {control.name for control in energy.controls}
    assert "gate_b5_matched_accuracy" in gates
    assert "matched_accuracy_gate" in controls


def test_v23_outputs_are_written(tmp_path: Path):
    summary = write_v23_outputs(tmp_path)
    assert summary["version"] == "v2.3"
    assert summary["tasks"] >= 7
    assert summary["validation_errors"] == []
    assert (tmp_path / "biogpu_v23_benchmark_registry.json").exists()
    assert (tmp_path / "BIOGPU_V23_BENCHMARK_REGISTRY.md").exists()
    assert (tmp_path / "biogpu_v23_benchmark_registry.csv").exists()
    assert (tmp_path / "biogpu_v23_hardware_readiness_matrix.csv").exists()
