from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class EnergyComponent:
    name: str
    watts: float
    seconds: float
    note: str = ""

    @property
    def joules(self) -> float:
        return float(self.watts) * float(self.seconds)


@dataclass
class EnergyAccountingReport:
    mode: str
    components: list[EnergyComponent]
    proxy: dict[str, Any]
    task_count: int
    notes: list[str]

    def to_dict(self) -> dict[str, Any]:
        total_j = sum(c.joules for c in self.components)
        return {
            "mode": self.mode,
            "components": [{**asdict(c), "joules": c.joules} for c in self.components],
            "total_joules": total_j,
            "task_count": int(self.task_count),
            "joules_per_task": total_j / max(1, int(self.task_count)),
            "proxy": self.proxy,
            "notes": self.notes,
        }


def estimate_system_energy(
    proxy: dict[str, Any],
    task_count: int,
    seconds: float,
    host_watts: float = 15.0,
    mea_watts: float = 0.0,
    stimulator_watts: float = 0.0,
    life_support_watts: float = 0.0,
    mode: str = "simulation_proxy",
) -> dict[str, Any]:
    """Create a transparent energy accounting hook.

    This is not a lab measurement. It keeps the accounting structure honest by
    explicitly separating host, MEA device, stimulator and life-support budgets.
    For simulation, only host_watts is normally non-zero.
    """
    components = [
        EnergyComponent("host_compute", host_watts, seconds, "CPU/GPU host running BioGPU software"),
        EnergyComponent("mea_device", mea_watts, seconds, "0 in simulation; measured in real MEA stage"),
        EnergyComponent("stimulator", stimulator_watts, seconds, "0 in simulation; measured in real MEA stage"),
        EnergyComponent("life_support", life_support_watts, seconds, "0 in simulation; incubator/perfusion in wetware stage"),
    ]
    report = EnergyAccountingReport(
        mode=mode,
        components=components,
        proxy=proxy,
        task_count=task_count,
        notes=[
            "Simulation energy accounting is a transparent estimate, not a physical measurement.",
            "Real BioGPU comparison must include host + MEA + stimulator + life-support.",
        ],
    )
    return report.to_dict()
