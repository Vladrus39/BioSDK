param(
    [string]$Python = "python",
    [string]$OutDir = "outputs/v542_signed_artifact_provenance"
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "."
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"

Write-Host "====================================================="
Write-Host " BioGPU-Core v5.42  Signed Artifact Provenance"
Write-Host "====================================================="
Write-Host "Python: $Python"
Write-Host "Root  : ."
Write-Host "OutDir: $OutDir"
Write-Host ""

Write-Host "--- Running v542 signed artifact provenance proof ---"
& $Python -m biogpu.benchmarks.biogpu_v542_signed_artifact_provenance --root . --out-dir $OutDir

Write-Host ""
Write-Host "--- Signed artifact provenance summary ---"
$summaryPath = Join-Path $OutDir "V542_SIGNED_ARTIFACT_PROVENANCE_SUMMARY.json"
$summary = Get-Content $summaryPath -Raw | ConvertFrom-Json
Write-Host "overall_status       : $($summary.overall_status)"
Write-Host "contract_ready       : $($summary.signed_artifact_provenance_contract_ready)"
Write-Host "v541_dependency      : $($summary.v541_dependency_ready)"
Write-Host "artifact_manifest    : $($summary.artifact_manifest_ready)"
Write-Host "local_signature      : $($summary.local_signature_ready)"
Write-Host "signature_validation : $($summary.signature_validation_ready)"
Write-Host "tamper_detection     : $($summary.tamper_detection_ready)"
Write-Host "external_signature   : $($summary.trusted_external_signature_ready)"
Write-Host "full_biosdk_ready    : $($summary.full_biosdk_ready)"
Write-Host "bic_os_phase_locked  : $($summary.bic_os_phase_locked)"

if (-not $summary.signed_artifact_provenance_contract_ready) {
    throw "v5.42 signed artifact provenance contract failed"
}
if (-not $summary.local_signature_ready) {
    throw "v5.42 local signature did not pass"
}
if (-not $summary.tamper_detection_ready) {
    throw "v5.42 tamper detection did not pass"
}
if ($summary.trusted_external_signature_ready) {
    throw "v5.42 must not claim trusted external signature readiness"
}
if ($summary.full_biosdk_ready) {
    throw "v5.42 must not claim full BioSDK readiness"
}
if (-not $summary.bic_os_phase_locked) {
    throw "v5.42 must keep BiC OS phase locked"
}

Write-Host ""
Write-Host "--- Running v542 tests ---"
& $Python -m pytest -q tests/current/test_biogpu_v542_signed_artifact_provenance.py

Write-Host ""
Write-Host "====================================================="
Write-Host " v5.42 Signed Artifact Provenance Contract PASSED"
Write-Host "====================================================="