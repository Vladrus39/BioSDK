# DANDI Task-Aligned Workflow

DANDI/NWB is the best public path for task-aligned spike benchmarks because NWB can contain units, intervals, stimuli, and behavior.

Candidate datasets:

- DANDI `000469`: human single-neuron Sternberg working-memory task.
- DANDI `000673`: human hippocampal working-memory intracranial dataset candidate.

Workflow:

```bash
pip install dandi
dandi download https://dandiarchive.org/dandiset/000469
python -m biogpu.cli public-data nwb-discover path/to/session.nwb --output outputs/reports/nwb_discovery.json
```

Then inspect the discovery report and map real intervals/stimuli to:

```csv
start_s,end_s,label,stimulus_id,split
```

Finally run:

```bash
python -m biogpu.cli public-data task-aligned path/to/session.nwb data/stimulus_windows.csv --source-type nwb
```

Do not create labels after looking at spike activity. Labels must come from task metadata.
