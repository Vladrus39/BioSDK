param(
    [string]$Python = "python",
    [string]$OutDir = "outputs/v534_tamper_evident_incident_ledger"
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "."
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"

Write-Host "====================================================="
Write-Host " BioGPU-Core v5.34  Tamper-Evident Incident Ledger"
Write-Host "====================================================="
Write-Host "Python: $Python"
Write-Host "Root  : ."
Write-Host "OutDir: $OutDir"
Write-Host ""

Write-Host "--- Running v534 tamper-evident incident ledger proof ---"
& $Python -m biogpu.benchmarks.biogpu_v534_tamper_evident_incident_ledger --root . --out-dir $OutDir

Write-Host ""
Write-Host "--- Tamper-evident incident ledger summary ---"
$summaryPath = Join-Path $OutDir "V534_TAMPER_EVIDENT_INCIDENT_LEDGER_SUMMARY.json"
$summary = Get-Content $summaryPath -Raw | ConvertFrom-Json
Write-Host "overall_status       : $($summary.overall_status)"
Write-Host "ledger_ready         : $($summary.tamper_evident_incident_ledger_ready)"
Write-Host "chain_valid          : $($summary.incident_ledger_chain_valid)"
Write-Host "signature_valid      : $($summary.local_signature_validation_ready)"
Write-Host "retention_anchor     : $($summary.retention_manifest_anchored)"
Write-Host "tamper_detection     : $($summary.tamper_detection_passed)"
Write-Host "production_ledger    : $($summary.production_incident_ledger_ready)"
Write-Host "bic_os_phase_locked  : $($summary.bic_os_phase_locked)"

if (-not $summary.tamper_evident_incident_ledger_ready) {
    throw "v5.34 tamper-evident incident ledger proof failed"
}
if ($summary.production_incident_ledger_ready) {
    throw "v5.34 must not claim production incident ledger readiness"
}
if (-not $summary.bic_os_phase_locked) {
    throw "v5.34 must keep BiC OS phase locked"
}

Write-Host ""
Write-Host "--- Running v534 tests ---"
& $Python -m pytest -q tests/current/test_biogpu_v534_tamper_evident_incident_ledger.py

Write-Host ""
Write-Host "====================================================="
Write-Host " v5.34 Tamper-Evident Incident Ledger PASSED"
Write-Host "====================================================="