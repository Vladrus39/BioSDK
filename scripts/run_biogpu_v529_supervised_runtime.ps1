param(
    [string]$Python = "python",
    [string]$OutDir = "outputs/v529_supervised_local_runtime"
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "."
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"

Write-Host "====================================================="
Write-Host " BioGPU-Core v5.29  Supervised Local Runtime"
Write-Host "====================================================="
Write-Host "Python: $Python"
Write-Host "Root  : ."
Write-Host "OutDir: $OutDir"
Write-Host ""

Write-Host "--- Running v529 supervised local runtime proof ---"
& $Python -m biogpu.benchmarks.biogpu_v529_supervised_runtime --root . --out-dir $OutDir

Write-Host ""
Write-Host "--- Supervised runtime summary ---"
$summaryPath = Join-Path $OutDir "V529_SUPERVISED_RUNTIME_SUMMARY.json"
$summary = Get-Content $summaryPath -Raw | ConvertFrom-Json
Write-Host "overall_status       : $($summary.overall_status)"
Write-Host "runtime_ready        : $($summary.supervised_local_runtime_ready)"
Write-Host "heartbeat_index      : $($summary.heartbeat_index)"
Write-Host "worker_ticks         : $($summary.worker_tick_semantics_passed)"
Write-Host "graceful_shutdown    : $($summary.graceful_shutdown_semantics_passed)"
Write-Host "audit_export         : $($summary.audit_export_semantics_passed)"
Write-Host "production_runtime   : $($summary.production_runtime_ready)"
Write-Host "bic_os_phase_locked  : $($summary.bic_os_phase_locked)"

if (-not $summary.supervised_local_runtime_ready) {
    throw "v5.29 supervised local runtime proof failed"
}
if ($summary.production_runtime_ready) {
    throw "v5.29 must not claim production runtime readiness"
}
if (-not $summary.bic_os_phase_locked) {
    throw "v5.29 must keep BiC OS phase locked"
}

Write-Host ""
Write-Host "--- Running v529 tests ---"
& $Python -m pytest -q tests/current/test_biogpu_v529_supervised_runtime.py

Write-Host ""
Write-Host "====================================================="
Write-Host " v5.29 Supervised Local Runtime PASSED"
Write-Host "====================================================="