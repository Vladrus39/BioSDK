from __future__ import annotations

from pathlib import Path

from biogpu.benchmarks.biogpu_v537_identity_provider_contract import run
from biogpu.runtime.identity_provider_contract_v537 import (
    build_identity_provider_contract_v537,
    build_identity_token_fixtures_v537,
    build_jwks_contract_v537,
    build_oidc_discovery_contract_v537,
    run_identity_provider_contract_workflow_v537,
    run_identity_validation_matrix_v537,
    validate_identity_claims_v537,
    validate_identity_provider_contract_v537,
    write_identity_provider_contract_outputs_v537,
)


def test_v537_contract_validates_oidc_and_jwks_shape():
    contract = build_identity_provider_contract_v537()
    discovery = build_oidc_discovery_contract_v537(contract)
    jwks = build_jwks_contract_v537(contract)
    validation = validate_identity_provider_contract_v537(contract, discovery, jwks)

    assert validation["identity_provider_contract_ready"] is True
    assert validation["issuer_https"] is True
    assert validation["jwks_rotation_contract_ready"] is True
    assert validation["private_key_material_absent"] is True
    assert validation["production_identity_claims_absent"] is True


def test_v537_accepts_valid_operator_and_denies_bad_tokens():
    contract = build_identity_provider_contract_v537()
    jwks = build_jwks_contract_v537(contract)
    fixtures = build_identity_token_fixtures_v537()

    operator = validate_identity_claims_v537(fixtures["operator_valid"].to_claims(), contract, jwks)
    wrong_audience = validate_identity_claims_v537(fixtures["wrong_audience"].to_claims(), contract, jwks)
    expired = validate_identity_claims_v537(fixtures["expired"].to_claims(), contract, jwks)

    assert operator.accepted is True
    assert operator.role == "operator"
    assert wrong_audience.accepted is False
    assert "audience_mismatch" in wrong_audience.errors
    assert expired.accepted is False
    assert "token_expired" in expired.errors


def test_v537_validation_matrix_passes_all_expected_decisions():
    matrix = run_identity_validation_matrix_v537()

    assert matrix["identity_validation_matrix_ready"] is True
    assert matrix["accepted_count"] >= 4
    assert matrix["denied_count"] >= 4
    assert matrix["passed_count"] == matrix["decision_count"]


def test_v537_workflow_ready_but_not_production_auth(tmp_path):
    audit = run_identity_provider_contract_workflow_v537(tmp_path)

    assert audit["overall_status"] == "identity_provider_contract_proof_ready_runtime_not_claimed"
    assert audit["identity_provider_contract_ready"] is True
    assert audit["oidc_discovery_contract_ready"] is True
    assert audit["jwks_rotation_contract_ready"] is True
    assert audit["identity_validation_matrix_ready"] is True
    assert audit["identity_dashboard_access_ready"] is True
    assert audit["production_auth_ready"] is False
    assert audit["production_identity_ready"] is False
    assert audit["production_biocompute_runtime_ready"] is False
    assert audit["bic_os_phase_locked"] is True


def test_v537_outputs_are_written(tmp_path):
    audit = run_identity_provider_contract_workflow_v537(tmp_path)

    paths = write_identity_provider_contract_outputs_v537(audit, tmp_path / "out")
    assert Path(paths["summary_json"]).exists()
    assert Path(paths["discovery_json"]).exists()
    assert Path(paths["jwks_json"]).exists()
    assert Path(paths["identity_decisions_json"]).exists()
    assert Path(paths["dashboard_probe_json"]).exists()
    assert Path(paths["identity_decisions_csv"]).exists()
    assert "Identity Provider Contract" in Path(paths["markdown_report"]).read_text(encoding="utf-8")


def test_v537_runner_writes_summary(tmp_path):
    result = run(root=tmp_path, out_dir=tmp_path / "out")

    assert result["summary"]["identity_provider_contract_ready"] is True
    assert (tmp_path / "out" / "V537_IDENTITY_PROVIDER_CONTRACT_SUMMARY.json").exists()


def test_v537_reports_missing_real_identity_inputs(tmp_path):
    audit = run_identity_provider_contract_workflow_v537(tmp_path)

    assert audit["direct_answer"]["did_we_find_real_identity_provider_config"] == "no"
    assert len(audit["missing_real_inputs"]) >= 5