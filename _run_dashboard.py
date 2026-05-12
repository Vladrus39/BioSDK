"""BioSDK Dashboard Starter — uses resonance .venv Python."""
import sys
from pathlib import Path

BIOSDK = Path(r"C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap")
if str(BIOSDK) not in sys.path:
    sys.path.insert(0, str(BIOSDK))

print("Starting BioSDK Dashboard v7.1 on http://127.0.0.1:8420")
print(f"Python: {sys.executable}")

from biogpu.dashboard.server_v71 import create_dashboard_app
app = create_dashboard_app()

import uvicorn
uvicorn.run(app, host="127.0.0.1", port=8420, log_level="info")
