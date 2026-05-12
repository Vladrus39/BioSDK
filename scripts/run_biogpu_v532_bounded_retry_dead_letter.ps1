param(
    [string]$Python = "python",
    [string]$OutDir = "outputs/v532_bounded_retry_dead_letter"
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "."
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"

Write-Host "====================================================="
Write-Host " BioGPU-Core v5.32  Bounded Retry / Dead Letter"
Write-Host "====================================================="
Write-Host "Python: $Python"
Write-Host "Root  : ."
Write-Host "OutDir: $OutDir"
Write-Host ""

Write-Host "--- Running v532 bounded retry/dead-letter proof ---"
& $Python -m biogpu.benchmarks.biogpu_v532_bounded_retry_dead_letter --root . --out-dir $OutDir

Write-Host ""
Write-Host "--- Bounded retry/dead-letter summary ---"
$summaryPath = Join-Path $OutDir "V532_BOUNDED_RETRY_DEAD_LETTER_SUMMARY.json"
$summary = Get-Content $summaryPath -Raw | ConvertFrom-Json
Write-Host "overall_status       : $($summary.overall_status)"
Write-Host "bounded_retry_ready  : $($summary.bounded_retry_dead_letter_ready)"
Write-Host "policy_ready         : $($summary.bounded_retry_policy_ready)"
Write-Host "dead_letter_ready    : $($summary.dead_letter_queue_ready)"
Write-Host "max_attempts         : $($summary.max_attempts_enforced)"
Write-Host "backoff_metadata     : $($summary.retry_backoff_metadata_ready)"
Write-Host "production_policy    : $($summary.production_retry_policy_ready)"
Write-Host "bic_os_phase_locked  : $($summary.bic_os_phase_locked)"

if (-not $summary.bounded_retry_dead_letter_ready) {
    throw "v5.32 bounded retry/dead-letter proof failed"
}
if ($summary.production_retry_policy_ready) {
    throw "v5.32 must not claim production retry policy readiness"
}
if ($summary.production_dead_letter_queue_ready) {
    throw "v5.32 must not claim production dead-letter queue readiness"
}
if (-not $summary.bic_os_phase_locked) {
    throw "v5.32 must keep BiC OS phase locked"
}

Write-Host ""
Write-Host "--- Running v532 tests ---"
& $Python -m pytest -q tests/current/test_biogpu_v532_bounded_retry_dead_letter.py

Write-Host ""
Write-Host "====================================================="
Write-Host " v5.32 Bounded Retry / Dead Letter PASSED"
Write-Host "====================================================="