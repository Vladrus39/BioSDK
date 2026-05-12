"""List all registered NSI-1.0 adapters."""
import sys
sys.path.insert(0, '.')
from biogpu.nsi.adapters import list_adapters, get_adapter
for aid in list_adapters():
    a = get_adapter(aid)
    print(f"  {aid}: vendor={a.vendor}, modality={a.modality}, channels={a.nominal_channels}")
