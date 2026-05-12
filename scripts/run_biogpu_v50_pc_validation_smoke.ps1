param(
    [string]$Python = "",
    [string]$OutDir = "outputs/v50_pc_validation_smoke"
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

    Invoke-Step "pip-check" { & $Python -m pip check }
    Invoke-Step "compileall-biogpu" { & $Python -m compileall -q biogpu }
    Invoke-Step "pytest-current" { & $Python -m pytest -q tests/current }
    Invoke-Step "v47-final-pc-patch" { & $Python -m biogpu.benchmarks.biogpu_v47_final_pc_patch --project-root . --out-dir $OutDir }
    Invoke-Step "v50-differentiation-report" { & $Python -m biogpu.benchmarks.biogpu_v50_differentiation_roadmap --out-dir $OutDir }

    $summary = [pscustomobject]@{
        status = "ok"
        project_root = $ProjectRoot.Path
        python = $Python
        out_dir = $OutDir
        steps = $steps
        created_utc = (Get-Date).ToUniversalTime().ToString("o")
    }
    $summaryPath = Join-Path $OutDir "windows_pc_validation_smoke_summary.json"
    $summary | ConvertTo-Json -Depth 8 | Set-Content -Path $summaryPath -Encoding UTF8
    Write-Host "Windows PC validation smoke OK: $summaryPath"
}
finally {
    Pop-Location
}
