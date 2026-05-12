<#
.SYNOPSIS
    Selectively downloads one Allen Visual Coding session-level NWB sample.

.DESCRIPTION
    DANDI 000021 contains small per-probe LFP NWB assets that are useful for
    acquisition parsing but do not contain the full session units/stimulus table
    needed by the v5.18 Allen orientation gate. This script prefers session-level
    NWB files (paths without probe-) under MaxMB and downloads only one asset.
#>
param(
    [string]$DandisetId = "000021",
    [string]$Version = "draft",
    [string]$OutDir = "data/external/allen/dandi_000021_session",
    [int]$MaxMB = 2048,
    [switch]$AllowProbeAssets,
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
    $manifestDir = "outputs/v518_allen_orientation_gate"
    $manifestPath = Join-Path $manifestDir "ALLEN_DANDI_${DandisetId}_SELECTED_SESSION_NWB.json"
    New-Item -ItemType Directory -Force -Path $manifestDir | Out-Null
    New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

    Write-Host "Querying Allen/DANDI metadata: $apiUrl" -ForegroundColor Cyan
    Write-Host "Size cap: $MaxMB MB"
    Write-Host "Allow probe assets: $([bool]$AllowProbeAssets)"

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
            $isNwb = $assetPath.ToLowerInvariant().EndsWith(".nwb")
            $isProbeAsset = $assetPath -match "probe-"
            if ($isNwb -and $assetId -and $size -gt 0 -and $size -le $maxBytes -and ($AllowProbeAssets -or -not $isProbeAsset)) {
                $assets += [pscustomobject]@{
                    dandiset_id = $DandisetId
                    version = $Version
                    asset_id = $assetId
                    asset_path = $assetPath
                    size_bytes = $size
                    size_mb = [math]::Round($size / 1MB, 2)
                    is_probe_asset = [bool]$isProbeAsset
                    download_url = "https://api.dandiarchive.org/api/assets/$assetId/download/"
                }
            }
        }
        $nextUrl = [string]$page.next
    }

    if ($assets.Count -eq 0) {
        $manifest = [pscustomobject]@{
            status = "no_session_nwb_asset_under_size_cap"
            dandiset_id = $DandisetId
            version = $Version
            max_mb = $MaxMB
            allow_probe_assets = [bool]$AllowProbeAssets
            next_action = "Increase MaxMB or use -AllowProbeAssets only for LFP/acquisition smoke tests, not full Allen orientation proof."
        }
        $manifest | ConvertTo-Json -Depth 8 | Set-Content -Path $manifestPath -Encoding UTF8
        Write-Host "No matching Allen session NWB under $MaxMB MB found. Manifest: $manifestPath" -ForegroundColor Yellow
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
        proof_intent = "Allen visual-coding session-level NWB for v5.18 units/stimulus/orientation validation"
    }
    $manifest | ConvertTo-Json -Depth 8 | Set-Content -Path $manifestPath -Encoding UTF8

    Write-Host "Selected Allen session NWB asset:" -ForegroundColor Green
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
        next_action = "Run scripts/run_biogpu_v518_allen_orientation_gate.ps1 to validate the Allen sample."
    }
    $finalManifest | ConvertTo-Json -Depth 8 | Set-Content -Path $manifestPath -Encoding UTF8
    Write-Host "Downloaded $downloadedBytes bytes to $outFile" -ForegroundColor Green
} finally {
    Pop-Location
}
