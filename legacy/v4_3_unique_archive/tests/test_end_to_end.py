from pathlib import Path
from biogpu.benchmarks.orientation import main

def test_end_to_end(tmp_path):
    cfg = tmp_path / "cfg.yaml"
    cfg.write_text('''
seed: 1
image_size: 8
num_samples_per_class: 5
noise_levels: [0.0, 0.1]
train_fraction: 0.7
encoder:
  mode: spatial_rate
  max_events_per_pixel: 2
substrate:
  type: simulated_mea
  num_electrodes: 64
  reservoir_units: 64
  connectivity_density: 0.08
  noise_level: 0.03
  spontaneous_rate: 0.01
  latency_mean: 2.0
  latency_std: 0.5
  burst_probability: 0.01
  state_decay: 0.85
  gain: 1.1
features:
  bins: 8
outputs:
  root: ''' + str(tmp_path / 'outputs') + '''
''')
    results = main(str(cfg))
    assert "metrics" in results
    assert "accuracy" in results["metrics"]
