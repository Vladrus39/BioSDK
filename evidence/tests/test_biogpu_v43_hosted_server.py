from biogpu.beta.job_model_v43 import (
    AccessTier,
    BioGPUJobSpecV43,
    InMemoryJobStoreV43,
    JobType,
    UserContextV43,
    UserRole,
    find_unsafe_fields,
    default_server_capabilities,
)
from biogpu.benchmarks.biogpu_v43_hosted_server import generate_outputs


def test_unsafe_manifest_fields_are_detected():
    hits = find_unsafe_fields({"nested": {"voltage": 1.0, "ok": True}, "items": [{"pinout": "x"}]})
    assert "nested.voltage" in hits
    assert "items[0].pinout" in hits


def test_researcher_can_create_safe_benchmark_job():
    store = InMemoryJobStoreV43()
    ctx = UserContextV43("u1", "w1", UserRole.RESEARCHER, AccessTier.RESEARCH_PILOT)
    job = store.create_job(ctx, BioGPUJobSpecV43(JobType.BENCHMARK_RUN, {"mode": "replay", "shuffle_controls": 25}))
    assert job.status.value == "queued"
    assert job.validation_errors == []


def test_viewer_cannot_create_benchmark_job():
    store = InMemoryJobStoreV43()
    ctx = UserContextV43("u2", "w1", UserRole.VIEWER, AccessTier.DEVELOPER_EVALUATION)
    job = store.create_job(ctx, BioGPUJobSpecV43(JobType.BENCHMARK_RUN, {"mode": "replay"}))
    assert job.status.value == "failed"
    assert any("job_type_not_allowed_for_role" in e for e in job.validation_errors)


def test_live_actuation_is_disabled_even_for_lab_tier():
    store = InMemoryJobStoreV43()
    ctx = UserContextV43("lab", "w2", UserRole.ADMIN, AccessTier.LAB_APPROVED_CLOSED_LOOP)
    job = store.create_job(ctx, BioGPUJobSpecV43(JobType.BENCHMARK_RUN, {"live_actuation": True}))
    assert job.status.value == "failed"
    assert any("live_actuation" in e or "unsafe_manifest_fields" in e for e in job.validation_errors)


def test_server_capabilities_and_output_generation(tmp_path):
    caps = default_server_capabilities()
    assert caps["live_actuation_enabled"] is False
    summary = generate_outputs(tmp_path)
    assert summary["endpoint_count"] >= 8
    assert (tmp_path / "v43_endpoint_catalog.csv").exists()
    assert (tmp_path / "BIOGPU_V43_HOSTED_SERVER_REPORT.md").exists()
