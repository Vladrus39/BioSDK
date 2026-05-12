import subprocess, sys
from pathlib import Path

BIO = Path(r"C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap")
python_exe = BIO / ".venv" / "Scripts" / "python.exe"
script = Path(r"C:\Users\vladi\Desktop\Braine\resonance_theory_research_pack_v0_5\_bic_os_cross_dataset.py")

r = subprocess.run([str(python_exe), str(script)], capture_output=True, text=True, timeout=120, cwd=str(BIO))
print(r.stdout)
if r.stderr: print("ERR:", r.stderr[-500:])
