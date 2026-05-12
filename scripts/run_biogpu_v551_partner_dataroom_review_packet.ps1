param(
    [string]$Python = "python",
    [string]$OutDir = "outputs/v551_partner_dataroom_review_packet"
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "."
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"

Write-Host "====================================================="
Write-Host " BioGPU-Core v5.51  Partner Data-Room Review Packet"
Write-Host "====================================================="
Write-Host "Python: $Python"
Write-Host "Root  : ."
Write-Host "OutDir: $OutDir"
Write-Host ""

Write-Host "--- Running v551 partner data-room review packet proof ---"
& $Python -m biogpu.benchmarks.biogpu_v551_partner_dataroom_review_packet --root . --out-dir $OutDir

Write-Host ""
Write-Host "--- Partner data-room review packet summary ---"
$summaryPath = Join-Path $OutDir "V551_PARTNER_DATAROOM_REVIEW_PACKET_SUMMARY.json"
$summary = Get-Content $summaryPath -Raw | ConvertFrom-Json
Write-Host "overall_status       : $($summary.overall_status)"
Write-Host "contract_ready       : $($summary.partner_dataroom_review_packet_contract_ready)"
Write-Host "v550_dependency      : $($summary.v550_dependency_ready)"
Write-Host "manifest_ready       : $($summary.partner_dataroom_manifest_ready)"
Write-Host "review_packet_ready  : $($summary.external_review_packet_ready)"
Write-Host "review_gate_ready    : $($summary.external_review_gate_ready)"
Write-Host "real_dataroom_items  : $($summary.real_dataroom_item_ready_count)"
Write-Host "external_review_ready: $($summary.real_external_review_ready)"
Write-Host "external_pilot_ready : $($summary.real_external_pilot_ready)"
Write-Host "production_ready     : $($summary.production_ready)"
Write-Host "full_biosdk_ready    : $($summary.full_biosdk_ready)"
Write-Host "bic_os_phase_locked  : $($summary.bic_os_phase_locked)"

if (-not $summary.partner_dataroom_review_packet_contract_ready) {
    throw "v5.51 partner data-room review packet contract failed"
}
if ($summary.real_dataroom_item_ready_count -ne 0) {
    throw "v5.51 must not claim real data-room items"
}
if ($summary.real_external_review_ready) {
    throw "v5.51 must not claim real external review readiness"
}
if ($summary.real_external_pilot_ready) {
    throw "v5.51 must not claim real external pilot readiness"
}
if ($summary.production_ready) {
    throw "v5.51 must not claim production readiness"
}
if ($summary.full_biosdk_ready) {
    throw "v5.51 must not claim full BioSDK readiness"
}
if (-not $summary.bic_os_phase_locked) {
    throw "v5.51 must keep BiC OS phase locked"
}

Write-Host ""
Write-Host "--- Running v551 tests ---"
& $Python -m pytest -q tests/current/test_biogpu_v551_partner_dataroom_review_packet.py

Write-Host ""
Write-Host "====================================================="
Write-Host " v5.51 Partner Data-Room Review Packet Contract PASSED"
Write-Host "====================================================="