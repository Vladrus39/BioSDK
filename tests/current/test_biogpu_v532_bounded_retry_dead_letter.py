from __future__ import annotations

from pathlib import Path

from biogpu.benchmarks.biogpu_v532_bounded_retry_dead_letter import run
from biogpu.runtime.retry_policy_v532 import (
    RetryPolicyV532,
    evaluate_retry_decision_v532,
    run_bounded_retry_dead_letter_probe_v532,
    run_bounded_retry_dead_letter_workflow_v532,
    write_bounded_retry_dead_letter_outputs_v532,
)


def test_v532_retry_decision_allows_attempt_before_limit():
    job = {"job_id": "job-a", "status": "failed", "metadata": {"retry_attempt": 1}, "validation_errors": ["worker_timeout_exceeded"]}
    decision = evaluate_retry_decision_v532(job, RetryPolicyV532(max_retry_attempts=2))

    assert decision.action == "retry"
    assert decision.accepted is True
    assert decision.next_attempt == 2
    assert decision.backoff_seconds == 30
    assert decision.production_retry_policy_ready is False


def test_v532_retry_decision_dead_letters_at_limit():
    job = {"job_id": "job-a", "status": "failed", "metadata": {"retry_attempt": 2}, "validation_errors": ["worker_timeout_exceeded"]}
    decision = evaluate_retry_decision_v532(job, RetryPolicyV532(max_retry_attempts=2))

    assert decision.action == "dead_letter"
    assert decision.accepted is True
    assert decision.status == "max_attempts_exhausted"
    assert decision.next_attempt is None


def test_v532_probe_enforces_bounded_retry_and_dead_letter(tmp_path):
    probe = run_bounded_retry_dead_letter_probe_v532(tmp_path, tmp_path / "out")

    assert probe["bounded_retry_dead_letter_probe_ready"] is True
    assert probe["max_attempts_enforced"] is True
    assert probe["retry_backoff_metadata_ready"] is True
    assert len(probe["dead_letter_queue"]) == 1
    assert probe["policy_actions"][0]["decision"]["action"] == "retry"
    assert probe["policy_actions"][1]["decision"]["action"] == "retry"
    assert probe["policy_actions"][2]["decision"]["action"] == "dead_letter"
    assert probe["dead_letter_jobs"][0]["metadata"]["dead_lettered"] is True


def test_v532_workflow_ready_but_not_production_retry_policy(tmp_path):
    audit = run_bounded_retry_dead_letter_workflow_v532(tmp_path)

    assert audit["overall_status"] == "bounded_retry_dead_letter_proof_ready_runtime_not_claimed"
    assert audit["bounded_retry_dead_letter_ready"] is True
    assert audit["dead_letter_queue_ready"] is True
    assert audit["max_attempts_enforced"] is True
    assert audit["retry_backoff_metadata_ready"] is True
    assert audit["recovery_dependency_ready"] is True
    assert audit["production_retry_policy_ready"] is False
    assert audit["production_biocompute_runtime_ready"] is False
    assert audit["bic_os_phase_locked"] is True


def test_v532_write_outputs(tmp_path):
    audit = run_bounded_retry_dead_letter_workflow_v532(tmp_path)

    paths = write_bounded_retry_dead_letter_outputs_v532(audit, tmp_path / "out")

    assert Path(paths["summary_json"]).exists()
    assert Path(paths["policy_json"]).exists()
    assert Path(paths["policy_actions_json"]).exists()
    assert Path(paths["dead_letter_queue_json"]).exists()
    assert Path(paths["events_json"]).exists()
    assert Path(paths["jobs_csv"]).exists()
    assert "Bounded Retry" in Path(paths["markdown_report"]).read_text(encoding="utf-8")


def test_v532_runner_writes_summary(tmp_path):
    result = run(root=tmp_path, out_dir=tmp_path / "out")

    assert result["summary"]["bounded_retry_dead_letter_ready"] is True
    assert (tmp_path / "out" / "V532_BOUNDED_RETRY_DEAD_LETTER_SUMMARY.json").exists()