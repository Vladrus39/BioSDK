param(
    [string]$Python = "",
    [string]$V15Dir = "evidence/outputs/realdata_zenodo_14363732_v15_readout",
    [string]$OutDir = "outputs/powerpc_full_shuffle_1000",
    [int]$ShuffleCount = 1000,
    [int]$BootstrapIterations = 2000,
    [string]$SplitOffsets = "0,1,2,3,4,5",
    [switch]$IncludeSklearnReadouts
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Push-Location $ProjectRoot
try {
    if (-not $Python) {
        if ($env:VIRTUAL_ENV) {
            $candidate = Join-Path $env:VIRTUAL_ENV "Scripts/python.exe"
            if (Test-Path $candidate) { $Python = $candidate }
        }
        if (-not $Python) { $Python = "python" }
    }

    $env:PYTHONPATH = "."
    $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
    New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

    if ($IncludeSklearnReadouts) {
        $decoders = "centroid_euclidean,diag_gaussian,logistic_l2,linear_svm"
        $runMode = "full_with_sklearn_readouts"
    }
    else {
        $decoders = "centroid_euclidean,diag_gaussian"
        $runMode = "full_shuffle_centroid_diagonal"
    }

    $manifestPath = Join-Path $OutDir "RUN_MANIFEST_FULL_SHUFFLE_1000_WINDOWS.json"
    $manifest = [pscustomobject]@{
        run_name = "BioGPU v5.0 Windows full_shuffle_1000"
        run_mode = $runMode
        v15_dir = $V15Dir
        out_dir = $OutDir
        decoders = $decoders
        ablations = "response_delta_count,exact_features"
        split_offsets = $SplitOffsets
        shuffle_count = $ShuffleCount
        bootstrap_iterations = $BootstrapIterations
        seed = 4700
        include_sklearn_readouts = [bool]$IncludeSklearnReadouts
        safety_boundary = "offline public-data replay only; no live actuation; no GPU advantage claim"
        created_utc = (Get-Date).ToUniversalTime().ToString("o")
    }
    $manifest | ConvertTo-Json -Depth 6 | Set-Content -Path $manifestPath -Encoding UTF8

    $started = Get-Date
    & $Python -m biogpu.benchmarks.biogpu_v36_lineage_bootstrap `
        --v15-dir $V15Dir `
        --out-dir $OutDir `
        --shuffle-count $ShuffleCount `
        --bootstrap-iterations $BootstrapIterations `
        --decoders $decoders `
        --ablations "response_delta_count,exact_features" `
        --split-offsets $SplitOffsets `
        --seed 4700
    if ($LASTEXITCODE -ne 0) {
        throw "full_shuffle_1000 failed with exit code $LASTEXITCODE"
    }
    $ended = Get-Date

    $summaryPath = Join-Path $OutDir "WINDOWS_FULL_SHUFFLE_1000_RUN_SUMMARY.json"
    [pscustomobject]@{
        status = "ok"
        run_mode = $runMode
        elapsed_seconds = [math]::Round(($ended - $started).TotalSeconds, 3)
        started_utc = $started.ToUniversalTime().ToString("o")
        ended_utc = $ended.ToUniversalTime().ToString("o")
        manifest = $manifestPath
        v36_summary = (Join-Path $OutDir "v36_summary.json")
    } | ConvertTo-Json -Depth 6 | Set-Content -Path $summaryPath -Encoding UTF8

    Write-Host "Windows full_shuffle_1000 OK: $summaryPath"
}
finally {
    Pop-Location
}
