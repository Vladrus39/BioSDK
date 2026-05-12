"""Investigate OpenNeuro ds007558 BIDS structure."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
import json, csv

data_dir = Path('data/external/eeg_ds007558')

# Check first subject
subj = data_dir / 'sub-001'
all_files = list(subj.rglob('*'))
print(f"Subject 001: {len(all_files)} files")
for f in all_files:
    print(f"  {f.relative_to(subj)} ({f.stat().st_size} bytes)")

# Check for events TSV across all subjects
events_files = list(data_dir.rglob('*_events.tsv'))
print(f"\nTotal _events.tsv files: {len(events_files)}")

if events_files:
    print(f"\nSample events file: {events_files[0]}")
    with open(events_files[0], 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        headers = reader.fieldnames
        print(f"  Columns: {headers}")
        for i, row in enumerate(reader):
            if i < 5:
                print(f"  Row {i}: {dict(row)}")
            else:
                break
        # Count total rows
        f.seek(0)
        total = sum(1 for _ in reader) - 1
        print(f"  Total rows: {total}")

# Check dataset description
desc = data_dir / 'dataset_description.json'
if desc.exists():
    desc_data = json.loads(desc.read_text())
    print(f"\nDataset description: {json.dumps(desc_data, indent=2)}")

# Check participants
part = data_dir / 'participants.tsv'
if part.exists():
    with open(part, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        print(f"\nParticipants columns: {reader.fieldnames}")
        for i, row in enumerate(reader):
            if i < 3:
                print(f"  {dict(row)}")
            else:
                break
