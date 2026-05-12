<#
.SYNOPSIS
    BioGPU-Core v5.1 — Dataset & API expansion probe runner (Windows PowerShell).

.DESCRIPTION
    Runs the v51 dataset/API expansion probe on all configured sources and
    writes a machine-readable status report to outputs/v51_dataset_expansion/.

    Probes covered (all safe offline, no network calls):
      1. Zenodo 14363732 raw HDF5 / TTL gate
      2. DANDI curated-candidate manifest
      3. DANDI/NWB offline gate
      4. AllenSDK-style orientation benchmark (synthetic)
      5. Vendor registry v4.2
      6. User-upload importer skeleton v4.2

.PARAMETER Python
    Path to the Python interpreter to use.
    Defaults to 'python' (system PATH).

.PARAMETER OutDir
    Output directory for probe results.
    Defaults to 'outputs/v51_dataset_expansion'.

.EXAMPLE
    .\scripts\run_biogpu_v51_dataset_api_expansion.ps1 `
        -Python 'c:/Users/vladi/Desktop/Braine/BiC OS/.venv-1/Scripts/python.exe'
#>
param(
    [string]$Python  = "python",
    [string]$OutDir  = "outputs/v51_dataset_expansion"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir  = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Push-Location $ProjectRoot
try {
    $env:PYTHONPATH = "."

    Write-Host "======================================================" -ForegroundColor Cyan
    Write-Host " BioGPU-Core v5.1  Dataset/API Expansion Probe" -ForegroundColor Cyan
    Write-Host "======================================================" -ForegroundColor Cyan
    Write-Host "Python  : $Python"
    Write-Host "OutDir  : $OutDir"
    Write-Host "Root    : $ProjectRoot"
    Write-Host ""

    # ------------------------------------------------------------------ #
    # 1. Run the probe module                                              #
    # ------------------------------------------------------------------ #
    Write-Host "--- Running v51 dataset/API expansion probe ---" -ForegroundColor Yellow
    & $Python -m biogpu.benchmarks.biogpu_v51_dataset_api_expansion `
        --project-root "." `
        --out-dir $OutDir
    if ($LASTEXITCODE -ne 0) { throw "v51 dataset expansion probe failed (exit $LASTEXITCODE)" }

    # ------------------------------------------------------------------ #
    # 2. Print summary JSON                                                #
    # ------------------------------------------------------------------ #
    $summaryPath = Join-Path $OutDir "V51_DATASET_EXPANSION_SUMMARY.json"
    if (Test-Path $summaryPath) {
        Write-Host ""
        Write-Host "--- Probe summary ---" -ForegroundColor Yellow
        $summary = Get-Content $summaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
        Write-Host "milestone    : $($summary.milestone)"
        Write-Host "probe_count  : $($summary.probes.Count)"
        $gate = $summary.gate
        Write-Host "raw_hdf5_available         : $($gate.raw_hdf5_available)"
        Write-Host "nwb_available              : $($gate.nwb_available)"
        Write-Host "orientation_synthetic_avail: $($gate.orientation_synthetic_available)"
        Write-Host "vendor_registry_loaded     : $($gate.vendor_registry_loaded)"
    }

    # ------------------------------------------------------------------ #
    # 3. Run pytest for the new tests only (fast gate)                    #
    # ------------------------------------------------------------------ #
    Write-Host ""
    Write-Host "--- Running v51 dataset expansion tests ---" -ForegroundColor Yellow
    $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
    & $Python -m pytest -q tests/current/test_biogpu_v51_dataset_api_expansion.py
    if ($LASTEXITCODE -ne 0) { throw "v51 dataset expansion tests failed (exit $LASTEXITCODE)" }

    Write-Host ""
    Write-Host "======================================================" -ForegroundColor Green
    Write-Host " v51 dataset/API expansion probe PASSED" -ForegroundColor Green
    Write-Host "======================================================" -ForegroundColor Green

} finally {
    Pop-Location
}
