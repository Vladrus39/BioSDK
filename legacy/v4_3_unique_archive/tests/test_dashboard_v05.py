from pathlib import Path
from biogpu.dashboard.generate_static import generate_dashboard


def test_dashboard_generates_index():
    path = generate_dashboard('outputs')
    assert Path(path).exists()
    assert 'BioGPU Core Dashboard' in Path(path).read_text(encoding='utf-8')
