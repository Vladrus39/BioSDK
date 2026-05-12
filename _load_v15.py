import numpy as np
from pathlib import Path
import json, csv

BASE = Path(r"C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap")

# Load sweep results CSV to understand how labels work
csv_path = BASE / "outputs" / "powerpc_stage1_v33_compact" / "paper_table_sweep_results_v33.csv"
with open(csv_path) as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    print(f"Total rows: {len(rows)}")
    if rows:
        print(f"Columns: {list(rows[0].keys())}")
        # Show a few rows
        for row in rows[:3]:
            print(json.dumps(row, indent=2))
            print("---")

# Check the best run in detail
print("\n=== Looking for best run (acc=0.524) ===")
for row in rows:
    if float(row.get('accuracy', 0)) > 0.52:
        print(json.dumps(row, indent=2))
        print("---")

# Also check dataset_profile
profile = json.loads((BASE / "outputs" / "powerpc_stage1_v33_compact" / "dataset_profile_v33.json").read_text())
print("\n=== DATASET PROFILE KEYS ===")
for k in list(profile.keys())[:20]:
    v = profile[k]
    s = str(v)
    print(f"  {k}: {s[:200]}")
