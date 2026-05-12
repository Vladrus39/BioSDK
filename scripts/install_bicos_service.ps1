# BiC OS Windows Service installer (requires NSSM)
# Download NSSM from https://nssm.cc/download
# Usage: powershell -ExecutionPolicy Bypass -File scripts/install_bicos_service.ps1

param(
    [string]$NssmPath = "nssm.exe",
    [string]$PythonExe = "c:/Users/vladi/Desktop/Braine/BiC OS/.venv-1/Scripts/python.exe",
    [string]$ProjectRoot = "C:/Users/vladi/Desktop/Braine/BiC OS/biogpu-core-v5_0_bic_os_first_mover_roadmap"
)

$serviceName = "BiCOS"
$displayName = "BiC OS Production Runtime v6.12"
$description = "BioCompute Runtime production daemon for living neural compute workflows"

Write-Host "Installing BiC OS Windows Service..."
Write-Host "  Service: $serviceName"
Write-Host "  Display: $displayName"

# Stop and remove existing service if present
& $NssmPath stop $serviceName 2>$null
& $NssmPath remove $serviceName confirm 2>$null

# Install new service
& $NssmPath install $serviceName $PythonExe "-m biogpu.production.daemon_v612 --root `"$ProjectRoot`""
& $NssmPath set $serviceName DisplayName $displayName
& $NssmPath set $serviceName Description $description
& $NssmPath set $serviceName AppDirectory $ProjectRoot
& $NssmPath set $serviceName Start SERVICE_AUTO_START
& $NssmPath set $serviceName AppStdout "$ProjectRoot/data/production/logs/bicos_stdout.log"
& $NssmPath set $serviceName AppStderr "$ProjectRoot/data/production/logs/bicos_stderr.log"

Write-Host "Service installed. Starting..."
& $NssmPath start $serviceName
Write-Host "Service started. Check status: nssm status $serviceName"
