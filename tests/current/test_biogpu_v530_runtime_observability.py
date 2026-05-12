from __future__ import annotations

from pathlib import Path

from biogpu.benchmarks.biogpu_v530_runtime_observability import run
from biogpu.runtime.observability_v530 import (
    RuntimeRetentionPolicyV530,
    apply_audit_retention_policy_v530,
    build_runtime_metrics_snapshot_v530,
    build_runtime_status_snapshots_v530,
    run_runtime_observability_workflow_v530,
    write_runtime_observability_outputs_v530,
)
from biogpu.runtime.supervised_runtime_v529 import run_supervised_runtime_workflow_v529


def test_v530_metrics_snapshot_from_supervisor_audit(tmp_path):
    supervisor = run_supervised_runtime_workflow_v529(tmp_path)

    metrics = build_runtime_metrics_snapshot_v530(supervisor)
    snapshots = build_runtime_status_snapshots_v530(supervisor)

    assert metrics["local_metrics_snapshot_ready"] is True
    assert metrics["event_counts"]["worker_tick"] >= 3
    assert metrics["job_status_counts"]["succeeded"] == 2
    assert metrics["result_bundle_count"] == 2
    assert len(snapshots) >= 7


def test_v530_retention_policy_exports_before_non_destructive_prune(tmp_path):
    supervisor = run_supervised_runtime_workflow_v529(tmp_path)

    manifest = apply_audit_retention_policy_v530(supervisor["audit_events"], tmp_path / "retention", RuntimeRetentionPolicyV530(max_retained_events=4))

    assert manifest["retention_policy_contract_ready"] is True
    assert manifest["source_event_count"] > manifest["retained_event_count"]
    assert manifest["retained_event_count"] <= 4
    assert manifest["pruned_event_count"] >= 1
    assert len(manifest["full_export_sha256"]) == 64
    assert len(manifest["retained_events_sha256"]) == 64
    assert Path(manifest["full_export_path"]).exists()
    assert Path(manifest["retained_events_path"]).exists()


def test_v530_workflow_ready_but_not_production_observability(tmp_path):
    audit = run_runtime_observability_workflow_v530(tmp_path)

    assert audit["overall_status"] == "runtime_observability_retention_ready_runtime_not_claimed"
    assert audit["runtime_observability_ready"] is True
    assert audit["local_metrics_snapshot_ready"] is True
    assert audit["retention_policy_contract_ready"] is True
    assert audit["retention_pruning_non_destructive"] is True
    assert audit["pruned_audit_event_count"] >= 1
    assert audit["production_metrics_ready"] is False
    assert audit["production_biocompute_runtime_ready"] is False
    assert audit["bic_os_phase_locked"] is True


def test_v530_write_outputs(tmp_path):
    audit = run_runtime_observability_workflow_v530(tmp_path)

    paths = write_runtime_observability_outputs_v530(audit, tmp_path / "out")

    assert Path(paths["summary_json"]).exists()
    assert Path(paths["metrics_json"]).exists()
    assert Path(paths["status_snapshots_json"]).exists()
    assert Path(paths["retention_manifest_json"]).exists()
    assert Path(paths["metrics_csv"]).exists()
    assert "Runtime Observability" in Path(paths["markdown_report"]).read_text(encoding="utf-8")


def test_v530_runner_writes_summary(tmp_path):
    result = run(root=tmp_path, out_dir=tmp_path / "out")

    assert result["summary"]["runtime_observability_ready"] is True
    assert (tmp_path / "out" / "V530_RUNTIME_OBSERVABILITY_SUMMARY.json").exists()