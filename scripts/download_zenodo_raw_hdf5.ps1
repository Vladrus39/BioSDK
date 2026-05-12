<#
.SYNOPSIS
    Скачивает Raw_data_MEA_data.zip с Zenodo 14363732 с поддержкой resume.

.DESCRIPTION
    Использует встроенный curl.exe с флагом -C - (HTTP Range).
    Если скачивание прервалось — запусти скрипт снова, он продолжит с того места.
    После завершения проверяет MD5-сумму.

.PARAMETER OutDir
    Куда сохранить файл. По умолчанию data/external/

.EXAMPLE
    .\scripts\download_zenodo_raw_hdf5.ps1
    .\scripts\download_zenodo_raw_hdf5.ps1 -OutDir "D:\data\zenodo"
#>
param(
    [string]$OutDir = "data/external"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
Push-Location $ProjectRoot

try {
    $url      = "https://zenodo.org/records/14363732/files/Raw_data_MEA_data.zip?download=1"
    $md5Known = "189bf2fc0ce858fd1308d683e1e8c323"
    $outFile  = Join-Path $OutDir "Raw_data_MEA_data.zip"

    New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

    $existingMB = 0
    if (Test-Path $outFile) {
        $existingMB = [math]::Round((Get-Item $outFile).Length / 1MB, 1)
        Write-Host "Найден частичный файл: $existingMB MB — продолжаем с этого места." -ForegroundColor Yellow
    } else {
        Write-Host "Новое скачивание." -ForegroundColor Cyan
    }

    Write-Host ""
    Write-Host "URL  : $url"
    Write-Host "Файл : $outFile"
    Write-Host "MD5  : $md5Known"
    Write-Host "Размер: ~35.9 GB"
    Write-Host ""
    Write-Host "Нажми Ctrl+C чтобы прервать. Запусти скрипт снова чтобы продолжить." -ForegroundColor Green
    Write-Host ""

    # curl.exe -C - : resume от текущего размера файла
    # --retry 5     : авто-повтор при обрыве сети
    # --retry-delay : задержка между попытками
    # -L            : следовать редиректам
    # -o            : выходной файл
    # --progress-bar: прогресс-бар
    curl.exe `
        --retry 5 `
        --retry-delay 10 `
        --retry-connrefused `
        -L `
        -C - `
        --progress-bar `
        -o $outFile `
        $url

    $curlExit = $LASTEXITCODE
    if ($curlExit -ne 0) {
        Write-Host ""
        Write-Host "curl завершился с кодом $curlExit." -ForegroundColor Yellow
        Write-Host "Запусти скрипт снова чтобы продолжить скачивание." -ForegroundColor Yellow
        exit $curlExit
    }

    # ------------------------------------------------------------------ #
    # Проверка MD5                                                         #
    # ------------------------------------------------------------------ #
    Write-Host ""
    Write-Host "Проверяем MD5..." -ForegroundColor Cyan
    $md5Actual = (Get-FileHash -Algorithm MD5 $outFile).Hash.ToLower()
    Write-Host "Ожидается : $md5Known"
    Write-Host "Получено  : $md5Actual"

    if ($md5Actual -eq $md5Known) {
        Write-Host ""
        Write-Host "MD5 совпадает. Файл скачан корректно." -ForegroundColor Green
        Write-Host "Теперь распакуй: Expand-Archive '$outFile' -DestinationPath data/external/raw_hdf5"
    } else {
        Write-Host ""
        Write-Host "MD5 НЕ совпадает! Файл повреждён. Удали и скачай заново." -ForegroundColor Red
        exit 1
    }

} finally {
    Pop-Location
}
