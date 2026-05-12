param(
    [string]$Python = "",
    [string]$V15Dir = "evidence/outputs/realdata_zenodo_14363732_v15_readout",
    [string]$OutDir = "outputs/powerpc_extended_methods_5000",
    [int]$ShuffleCount = 5000,
    [int]$BootstrapIterations = 5000,
    [string]$SplitOffsets = "0,1,2,3,4,5,6,7,8,9",
    [ValidateSet("Core", "Methods", "FullSklearn")]
    [string]$Profile = "Core"
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

    if ($Profile -eq "FullSklearn") {
        $decoders = "centroid_euclidean,centroid_cosine,diag_gaussian,logistic_l2,linear_svm"
        $ablations = "all_features,response_delta_count,response_count,pre_response_count,exact_features"
    }
    elseif ($Profile -eq "Methods") {
        $decoders = "centroid_euclidean,centroid_cosine,diag_gaussian"
        $ablations = "all_features,response_delta_count,response_count,pre_response_count,exact_features"
    }
    else {
        $decoders = "centroid_euclidean,diag_gaussian"
        $ablations = "response_delta_count,exact_features"
    }

    $manifestPath = Join-Path $OutDir "RUN_MANIFEST_EXTENDED_METHODS_5000_WINDOWS.json"
    $manifest = [pscustomobject]@{
        run_name = "BioGPU v5.0 Windows extended_methods_5000"
        profile = $Profile
        v15_dir = $V15Dir
        out_dir = $OutDir
        decoders = $decoders
        ablations = $ablations
        split_offsets = $SplitOffsets
        shuffle_count = $ShuffleCount
        bootstrap_iterations = $BootstrapIterations
        seed = 4750
        safety_boundary = "offline public-data replay only; lineage-strict statistical validation; no live actuation; no GPU advantage claim"
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
        --ablations $ablations `
        --split-offsets $SplitOffsets `
        --seed 4750
    if ($LASTEXITCODE -ne 0) {
        throw "extended_methods_5000 failed with exit code $LASTEXITCODE"
    }
    $ended = Get-Date

    $summaryPath = Join-Path $OutDir "WINDOWS_EXTENDED_METHODS_5000_RUN_SUMMARY.json"
    [pscustomobject]@{
        status = "ok"
        profile = $Profile
        elapsed_seconds = [math]::Round(($ended - $started).TotalSeconds, 3)
        started_utc = $started.ToUniversalTime().ToString("o")
        ended_utc = $ended.ToUniversalTime().ToString("o")
        manifest = $manifestPath
        v36_summary = (Join-Path $OutDir "v36_summary.json")
    } | ConvertTo-Json -Depth 6 | Set-Content -Path $summaryPath -Encoding UTF8

    Write-Host "Windows extended_methods_5000 OK: $summaryPath"
}
finally {
    Pop-Location
}