param(
    [string]$Python = "",
    [string]$V15Dir = "evidence/outputs/realdata_zenodo_14363732_v15_readout",
    [string]$Stage1OutDir = "outputs/powerpc_stage1_v33_compact",
    [string]$Stage2OutDir = "outputs/powerpc_stage2_v36_lineage_compact",
    [int]$V33ShuffleCount = 12,
    [int]$V36ShuffleCount = 24,
    [int]$V36BootstrapIterations = 500,
    [string]$SplitOffsets = "0,1,2,3,4,5",
    [switch]$FastCentroidOnly
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
    New-Item -ItemType Directory -Force -Path $Stage1OutDir, $Stage2OutDir | Out-Null

    if ($FastCentroidOnly) {
        $v33Decoders = "centroid_euclidean,centroid_cosine,diag_gaussian"
        $v36Decoders = "centroid_euclidean,diag_gaussian"
    }
    else {
        $v33Decoders = "centroid_euclidean,centroid_cosine,diag_gaussian,logistic_l2,linear_svm"
        $v36Decoders = "centroid_euclidean,diag_gaussian,logistic_l2,linear_svm"
    }

    $steps = @()
    function Invoke-Step {
        param(
            [string]$Name,
            [scriptblock]$Command
        )
        $started = Get-Date
        Write-Host "== $Name =="
        & $Command
        $code = $LASTEXITCODE
        $ended = Get-Date
        $script:steps += [pscustomobject]@{
            name = $Name
            exit_code = $code
            started = $started.ToUniversalTime().ToString("o")
            ended = $ended.ToUniversalTime().ToString("o")
            elapsed_seconds = [math]::Round(($ended - $started).TotalSeconds, 3)
        }
        if ($code -ne 0) {
            throw "Step failed: $Name exit_code=$code"
        }
    }

    Invoke-Step "v33-compact-sweep" {
        & $Python -m biogpu.benchmarks.biogpu_v33_realdata_sweep `
            --v15-dir $V15Dir `
            --out-dir $Stage1OutDir `
            --shuffle-count $V33ShuffleCount `
            --seed 33 `
            --decoders $v33Decoders `
            --split-offsets $SplitOffsets
    }

    Invoke-Step "v36-lineage-compact" {
        & $Python -m biogpu.benchmarks.biogpu_v36_lineage_bootstrap `
            --v15-dir $V15Dir `
            --out-dir $Stage2OutDir `
            --shuffle-count $V36ShuffleCount `
            --bootstrap-iterations $V36BootstrapIterations `
            --decoders $v36Decoders `
            --ablations "response_delta_count,exact_features" `
            --split-offsets $SplitOffsets `
            --seed 36
    }

    $summary = [pscustomobject]@{
        status = "ok"
        project_root = $ProjectRoot.Path
        python = $Python
        v15_dir = $V15Dir
        stage1_out_dir = $Stage1OutDir
        stage2_out_dir = $Stage2OutDir
        fast_centroid_only = [bool]$FastCentroidOnly
        steps = $steps
        created_utc = (Get-Date).ToUniversalTime().ToString("o")
    }
    $summaryDir = "outputs/v50_pc_validation_compact"
    New-Item -ItemType Directory -Force -Path $summaryDir | Out-Null
    $summaryPath = Join-Path $summaryDir "windows_pc_validation_compact_summary.json"
    $summary | ConvertTo-Json -Depth 8 | Set-Content -Path $summaryPath -Encoding UTF8
    Write-Host "Windows PC validation compact OK: $summaryPath"
}
finally {
    Pop-Location
}
