param(
    [string]$Python = "python",
    [string]$OutDir = "outputs/v530_runtime_observability"
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "."
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"

Write-Host "====================================================="
Write-Host " BioGPU-Core v5.30  Runtime Observability"
Write-Host "====================================================="
Write-Host "Python: $Python"
Write-Host "Root  : ."
Write-Host "OutDir: $OutDir"
Write-Host ""

Write-Host "--- Running v530 runtime observability proof ---"
& $Python -m biogpu.benchmarks.biogpu_v530_runtime_observability --root . --out-dir $OutDir

Write-Host ""
Write-Host "--- Runtime observability summary ---"
$summaryPath = Join-Path $OutDir "V530_RUNTIME_OBSERVABILITY_SUMMARY.json"
$summary = Get-Content $summaryPath -Raw | ConvertFrom-Json
Write-Host "overall_status      : $($summary.overall_status)"
Write-Host "observability_ready : $($summary.runtime_observability_ready)"
Write-Host "metrics_ready       : $($summary.local_metrics_snapshot_ready)"
Write-Host "status_snapshots    : $($summary.status_snapshot_count)"
Write-Host "retention_ready     : $($summary.retention_policy_contract_ready)"
Write-Host "pruned_events       : $($summary.pruned_audit_event_count)"
Write-Host "production_metrics  : $($summary.production_metrics_ready)"
Write-Host "bic_os_phase_locked : $($summary.bic_os_phase_locked)"

if (-not $summary.runtime_observability_ready) {
    throw "v5.30 runtime observability proof failed"
}
if ($summary.production_metrics_ready) {
    throw "v5.30 must not claim production metrics readiness"
}
if (-not $summary.bic_os_phase_locked) {
    throw "v5.30 must keep BiC OS phase locked"
}

Write-Host ""
Write-Host "--- Running v530 tests ---"
& $Python -m pytest -q tests/current/test_biogpu_v530_runtime_observability.py

Write-Host ""
Write-Host "====================================================="
Write-Host " v5.30 Runtime Observability PASSED"
Write-Host "====================================================="