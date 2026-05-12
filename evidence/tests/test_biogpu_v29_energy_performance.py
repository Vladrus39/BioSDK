from pathlib import Path
from biogpu.metrics.energy_model_v29 import EnergyRunInputV29, PowerComponentV29, estimate_energy_v29
from biogpu.metrics.latency_model_v29 import LatencyComponentsV29, estimate_latency_v29
from biogpu.metrics.baseline_v29 import build_baseline_catalog_v29, compare_baselines_v29
from biogpu.benchmarks.biogpu_v29_energy_performance import write_outputs


def test_energy_formula_joules_per_task():
    run = EnergyRunInputV29(100, 10.0, (PowerComponentV29("x", 20.0, "test"),))
    estimate = estimate_energy_v29(run)
    assert estimate.total_energy_j == 200.0
    assert estimate.joules_per_task == 2.0
    assert estimate.tasks_per_joule == 0.5


def test_latency_total_and_throughput():
    lat = estimate_latency_v29(LatencyComponentsV29(1, 2, 3, 4, 5, 6, 7))
    assert lat.total_ms == 28
    assert round(lat.throughput_tasks_per_s_if_serial, 6) == round(1000/28, 6)


def test_baseline_catalog_contains_gpu_and_biogpu():
    ids = {b.baseline_id for b in build_baseline_catalog_v29()}
    assert "gpu_workstation_placeholder" in ids
    assert "biogpu_a1_live_budget_placeholder" in ids


def test_comparison_has_ratios():
    result = compare_baselines_v29()
    assert result["version"] == "v2.9"
    assert all("ratios_vs_gpu_placeholder" in b for b in result["baselines"])
    assert "placeholder" in result["comparison_boundary"].lower()


def test_write_outputs(tmp_path: Path):
    summary = write_outputs(tmp_path, task_count=50, run_duration_s=5.0)
    assert summary["baseline_count"] >= 4
    assert (tmp_path / "v29_energy_performance_comparison.json").exists()
    assert (tmp_path / "v29_baseline_comparison.csv").exists()
