param(
    [string]$Python = "c:/Users/vladi/Desktop/Braine/BiC OS/.venv-1/Scripts/python.exe",
    [string]$Root = ".",
    [string]$OutDir = "outputs/v60_production_foundation"
)

Write-Host "BioGPU-Core v6.0 Production Foundation"
Write-Host "========================================="

$runner = "biogpu/benchmarks/biogpu_v60_production_foundation.py"

if (-not (Test-Path $runner)) {
    Write-Error "Runner not found: $runner"
    exit 1
}

& $Python -m pytest tests/current/test_biogpu_v60_production_foundation.py -q --tb=short 2>&1
$testExit = $LASTEXITCODE

& $Python $runner --root $Root --out-dir $OutDir
$runExit = $LASTEXITCODE

Write-Host ""
Write-Host "Test exit: $testExit"
Write-Host "Run exit: $runExit"

if ($testExit -ne 0 -or $runExit -ne 0) {
    Write-Host "V60 GATE FAILED" -ForegroundColor Red
    exit 1
}
Write-Host "V60 GATE PASSED" -ForegroundColor Green
exit 0
