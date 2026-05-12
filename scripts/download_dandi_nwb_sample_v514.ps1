<#
.SYNOPSIS
    Selectively downloads one capped NWB sample from DANDI for v5.14 BioSDK proof.

.DESCRIPTION
    This script queries DANDI asset metadata, selects the smallest .nwb asset under
    MaxMB, and downloads only that one asset. Use -PlanOnly to inspect the chosen
    asset without downloading.
#>
param(
    [string]$DandisetId = "000469",
    [string]$Version = "draft",
    [string]$OutDir = "data/external/nwb/dandi_000469",
    [int]$MaxMB = 512,
    [switch]$PlanOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
Push-Location $ProjectRoot

try {
    $maxBytes = [int64]$MaxMB * 1MB
    $apiUrl = "https://api.dandiarchive.org/api/dandisets/$DandisetId/versions/$Version/assets/?page_size=100"
    $manifestDir = "outputs/v514_sample_acquisition_gate"
    $manifestPath = Join-Path $manifestDir "DANDI_${DandisetId}_SELECTED_NWB_SAMPLE.json"
    New-Item -ItemType Directory -Force -Path $manifestDir | Out-Null
    New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

    Write-Host "Querying DANDI metadata: $apiUrl" -ForegroundColor Cyan
    Write-Host "Size cap: $MaxMB MB"

    $assets = @()
    $nextUrl = $apiUrl
    while ($nextUrl) {
        $page = Invoke-RestMethod -Uri $nextUrl -Headers @{ Accept = "application/json" } -TimeoutSec 60
        foreach ($asset in $page.results) {
            $assetPath = [string]$asset.path
            $assetId = [string]$asset.asset_id
            if (-not $assetId) { $assetId = [string]$asset.identifier }
            $size = [int64]0
            if ($null -ne $asset.size) { $size = [int64]$asset.size }
            if ($assetPath.ToLowerInvariant().EndsWith(".nwb") -and $assetId -and $size -gt 0 -and $size -le $maxBytes) {
                $downloadUrl = "https://api.dandiarchive.org/api/assets/$assetId/download/"
                $assets += [pscustomobject]@{
                    dandiset_id = $DandisetId
                    version = $Version
                    asset_id = $assetId
                    asset_path = $assetPath
                    size_bytes = $size
                    size_mb = [math]::Round($size / 1MB, 2)
                    download_url = $downloadUrl
                }
            }
        }
        $nextUrl = [string]$page.next
    }

    if ($assets.Count -eq 0) {
        $manifest = [pscustomobject]@{
            status = "no_nwb_asset_under_size_cap"
            dandiset_id = $DandisetId
            version = $Version
            max_mb = $MaxMB
            next_action = "Increase MaxMB or choose another curated DANDI dataset after checking local bandwidth/storage."
        }
        $manifest | ConvertTo-Json -Depth 8 | Set-Content -Path $manifestPath -Encoding UTF8
        Write-Host "No NWB asset under $MaxMB MB found. Manifest: $manifestPath" -ForegroundColor Yellow
        exit 0
    }

    $selected = $assets | Sort-Object size_bytes | Select-Object -First 1
    $fileName = Split-Path -Leaf $selected.asset_path
    if (-not $fileName) { $fileName = "$($selected.asset_id).nwb" }
    $outFile = Join-Path $OutDir $fileName

    $manifest = [pscustomobject]@{
        status = if ($PlanOnly) { "plan_only" } else { "selected_for_download" }
        selected = $selected
        local_path = $outFile
        plan_only = [bool]$PlanOnly
    }
    $manifest | ConvertTo-Json -Depth 8 | Set-Content -Path $manifestPath -Encoding UTF8

    Write-Host "Selected NWB asset:" -ForegroundColor Green
    Write-Host "  Path: $($selected.asset_path)"
    Write-Host "  Size: $($selected.size_mb) MB"
    Write-Host "  URL : $($selected.download_url)"
    Write-Host "  Out : $outFile"
    Write-Host "Manifest: $manifestPath"

    if ($PlanOnly) {
        Write-Host "PlanOnly set; no download performed." -ForegroundColor Yellow
        exit 0
    }

    curl.exe --retry 5 --retry-delay 10 --retry-connrefused -L -C - --progress-bar -o $outFile $selected.download_url
    if ($LASTEXITCODE -ne 0) {
        Write-Host "curl failed with exit code $LASTEXITCODE. Re-run the script to resume." -ForegroundColor Yellow
        exit $LASTEXITCODE
    }

    $downloadedBytes = (Get-Item $outFile).Length
    $finalManifest = [pscustomobject]@{
        status = "downloaded"
        selected = $selected
        local_path = $outFile
        downloaded_bytes = $downloadedBytes
        next_action = "Run scripts/run_biogpu_v514_sample_acquisition_gate.ps1 to validate local NWB presence."
    }
    $finalManifest | ConvertTo-Json -Depth 8 | Set-Content -Path $manifestPath -Encoding UTF8
    Write-Host "Downloaded $downloadedBytes bytes to $outFile" -ForegroundColor Green
} finally {
    Pop-Location
}
