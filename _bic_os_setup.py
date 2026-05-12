"""Read replay job results for accuracy numbers."""
import json
from pathlib import Path

BASE = Path(r"C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap")

# Read replay job results
for rj_name in ["replay-23b9b053.json", "replay-3c78d36b.json", "replay-45422b55.json", 
                "replay-6c8df010.json", "replay-ef72e273.json"]:
    fp = BASE / "data" / "production" / "replay_jobs" / rj_name
    if fp.exists():
        print(f"\n=== {rj_name} ===")
        data = json.loads(fp.read_text())
        if isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, (int, float, str, bool)):
                    print(f"  {k}: {v}")
                elif isinstance(v, dict):
                    s = json.dumps(v, default=str)
                    if len(s) < 400:
                        print(f"  {k}: {s}")
                    else:
                        print(f"  {k}: {s[:300]}...")

# Read v18 replay demo results
v18 = BASE / "evidence" / "outputs" / "realdata_zenodo_14363732_v18_biogpu_core" / "v18_replay_demo_results.json"
if v18.exists():
    print(f"\n=== v18_replay_demo_results.json ===")
    data = json.loads(v18.read_text())
    if isinstance(data, dict):
        for k, v in list(data.items())[:15]:
            print(f"  {k}: {str(v)[:200]}")

# Read external API traces that contain 0.470
for trace in [
    "evidence/outputs/realdata_zenodo_14363732_v37_external_api/trace_mcs_mea2100_v37.json",
    "evidence/outputs/realdata_zenodo_14363732_v37_external_api/trace_finalspark_remote_wetware_v37.json",
]:
    fp = BASE / trace
    if fp.exists():
        print(f"\n=== {Path(trace).name} ===")
        data = json.loads(fp.read_text())
        for k, v in data.items():
            if isinstance(v, (int, float, str, bool)):
                print(f"  {k}: {v}")
            elif isinstance(v, dict):
                for k2, v2 in v.items():
                    if isinstance(v2, (int, float)):
                        if 'acc' in str(k2).lower() or v2 == 0.470 or v2 == 0.437:
                            print(f"  {k}.{k2}: {v2}")
