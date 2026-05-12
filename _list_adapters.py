import sys
sys.path.insert(0, r"C:\Users\vladi\Desktop\Braine\BiC OS\biogpu-core-v5_0_bic_os_first_mover_roadmap")
from biogpu.nsi.adapters import list_adapters
adapters = list_adapters()
print(f"Adapters ({len(adapters)}):")
for a in adapters:
    print(f"  - {a}")
