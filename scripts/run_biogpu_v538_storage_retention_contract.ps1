param(
    [string]$Python = "python",
    [string]$OutDir = "outputs/v538_storage_retention_contract"
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "."
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"

Write-Host "====================================================="
Write-Host " BioGPU-Core v5.38  Storage Retention Contract"
Write-Host "====================================================="
Write-Host "Python: $Python"
Write-Host "Root  : ."
Write-Host "OutDir: $OutDir"
Write-Host ""

Write-Host "--- Running v538 storage retention contract proof ---"
& $Python -m biogpu.benchmarks.biogpu_v538_storage_retention_contract --root . --out-dir $OutDir

Write-Host ""
Write-Host "--- Storage retention summary ---"
$summaryPath = Join-Path $OutDir "V538_STORAGE_RETENTION_CONTRACT_SUMMARY.json"
$summary = Get-Content $summaryPath -Raw | ConvertFrom-Json
Write-Host "overall_status       : $($summary.overall_status)"
Write-Host "storage_ready        : $($summary.storage_retention_contract_ready)"
Write-Host "integrity_ready      : $($summary.storage_object_integrity_ready)"
Write-Host "retention_manifest   : $($summary.retention_manifest_ready)"
Write-Host "immutable_denial     : $($summary.immutable_overwrite_denial_ready)"
Write-Host "production_storage   : $($summary.production_object_storage_ready)"
Write-Host "bic_os_phase_locked  : $($summary.bic_os_phase_locked)"

if (-not $summary.storage_retention_contract_ready) {
    throw "v5.38 storage retention contract proof failed"
}
if ($summary.production_object_storage_ready) {
    throw "v5.38 must not claim production object storage readiness"
}
if ($summary.production_retention_backend_ready) {
    throw "v5.38 must not claim production retention backend readiness"
}
if (-not $summary.bic_os_phase_locked) {
    throw "v5.38 must keep BiC OS phase locked"
}

Write-Host ""
Write-Host "--- Running v538 tests ---"
& $Python -m pytest -q tests/current/test_biogpu_v538_storage_retention_contract.py

Write-Host ""
Write-Host "====================================================="
Write-Host " v5.38 Storage Retention Contract PASSED"
Write-Host "====================================================="