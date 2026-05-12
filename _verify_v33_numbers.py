"""Verify the discrepancy: HANDOFF says MLP 47.0%, sweep_summary says 25.52%."""
import json, csv
from pathlib import Path

BASE = Path(r"C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap")
v33 = BASE / "outputs" / "powerpc_stage1_v33_compact"

# 1. Read the aggregate CSV
print("=" * 70)
print("1. paper_table_aggregate_by_decoder_v33.csv")
print("=" * 70)
agg_csv = v33 / "paper_table_aggregate_by_decoder_v33.csv"
if agg_csv.exists():
    reader = csv.DictReader(agg_csv.read_text(encoding="utf-8").splitlines())
    for row in reader:
        print(json.dumps(row, indent=2))
        print("---")

# 2. Re-read sweep_summary carefully
print("\n" + "=" * 70)
print("2. sweep_summary_v33.json — aggregate_by_decoder")
print("=" * 70)
ss = json.loads((v33 / "sweep_summary_v33.json").read_text())
for d in ss["aggregate_by_decoder"]:
    print(f"  {d['decoder_id']}:")
    for k, v in d.items():
        print(f"    {k}: {v}")

# 3. Best run details
print("\n" + "=" * 70)
print("3. Best run")
print("=" * 70)
best = ss["best_run"]
for k, v in best.items():
    print(f"  {k}: {v}")

# 4. Check if there's a DIFFERENT sweep or metric
# Maybe "47.0%" comes from balanced_accuracy, or from a specific ablation
print("\n" + "=" * 70)
print("4. Paper table sweep results — ALL 90 rows (first 15)")
print("=" * 70)
sweep_csv = v33 / "paper_table_sweep_results_v33.csv"
reader = csv.DictReader(sweep_csv.read_text(encoding="utf-8").splitlines())
rows = list(reader)
for i, row in enumerate(rows[:15]):
    acc = float(row['accuracy'])
    bal = float(row['balanced_accuracy'])
    print(f"  [{i}] {row['split_id']:30s} | {row['decoder_id']:20s} | {row['ablation_id']:25s} | labels={row['n_labels']} | acc={acc:.4f} | bal={bal:.4f}")

# 5. Find diag_gaussian rows and compute mean per ablation
print("\n" + "=" * 70)
print("5. diag_gaussian per ablation")
print("=" * 70)
from collections import defaultdict
dg = defaultdict(list)
for row in rows:
    if row['decoder_id'] == 'diag_gaussian':
        dg[row['ablation_id']].append(float(row['accuracy']))
for abl, accs in sorted(dg.items()):
    print(f"  {abl}: mean={sum(accs)/len(accs):.4f}, best={max(accs):.4f}, n={len(accs)}")

# 6. Also check: maybe 47.0% is from a specific split/ablation combo?
print("\n" + "=" * 70)
print("6. Highest diag_gaussian accuracies (top 10)")
print("=" * 70)
dg_rows = [(float(r['accuracy']), r) for r in rows if r['decoder_id'] == 'diag_gaussian']
dg_rows.sort(key=lambda x: -x[0])
for acc, r in dg_rows[:10]:
    print(f"  acc={acc:.4f} | {r['split_id']} | {r['ablation_id']} | labels={r['n_labels']} | features={r['n_features']}")
