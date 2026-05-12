import subprocess, sys
from pathlib import Path

bundle = Path(r"C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap\outputs\v86_evidence_bundle")
venv_python = Path(r"C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap\.venv\Scripts\python.exe")

result = subprocess.run(
    [str(venv_python), str(bundle / "verify_v86_bundle.py")],
    capture_output=True, text=True, timeout=30, cwd=str(bundle)
)
print(result.stdout)
if result.returncode != 0:
    print(f"STDERR: {result.stderr}")
sys.exit(result.returncode)
