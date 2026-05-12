from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from biogpu.data_ingest.stimulus_windows import StimulusWindow, write_stimulus_windows_csv
from biogpu.data_ingest.dandi_discovery import write_candidate_manifest
from biogpu.data_ingest.brc_import import write_brc_spec_template

root = Path("data/templates")
root.mkdir(parents=True, exist_ok=True)
write_stimulus_windows_csv([
    StimulusWindow(0.0, 0.5, label="A", stimulus_id="stim_001", split="train"),
    StimulusWindow(0.6, 1.1, label="B", stimulus_id="stim_002", split="train"),
    StimulusWindow(1.2, 1.7, label="A", stimulus_id="stim_003", split="test"),
    StimulusWindow(1.8, 2.3, label="B", stimulus_id="stim_004", split="test"),
], root / "stimulus_windows_example.csv")
write_candidate_manifest(root / "dandi_candidates.json")
write_brc_spec_template(root / "brc_experiment_spec_template.json")
print(f"Wrote templates under {root}")
