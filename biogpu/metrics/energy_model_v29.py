from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import Dict, Any

@dataclass(frozen=True)
class PowerComponentV29:
    name: str
    watts: float
    role: str
    measurement_status: str = "estimated_or_placeholder"

    def validate(self) -> None:
        if self.watts < 0:
            raise ValueError(f"power must be non-negative for {self.name}")

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass(frozen=True)
class EnergyRunInputV29:
    task_count: int
    run_duration_s: float
    components: tuple[PowerComponentV29, ...]
    notes: str = ""

    def validate(self) -> None:
        if self.task_count <= 0:
            raise ValueError("task_count must be positive")
        if self.run_duration_s <= 0:
            raise ValueError("run_duration_s must be positive")
        if not self.components:
            raise ValueError("at least one power component is required")
        for component in self.components:
            component.validate()

    def total_power_w(self) -> float:
        self.validate()
        return sum(c.watts for c in self.components)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_count": self.task_count,
            "run_duration_s": self.run_duration_s,
            "components": [c.to_dict() for c in self.components],
            "notes": self.notes,
        }

@dataclass(frozen=True)
class EnergyEstimateV29:
    total_power_w: float
    run_duration_s: float
    total_energy_j: float
    joules_per_task: float
    millijoules_per_task: float
    mwh_per_task: float
    tasks_per_joule: float
    notes: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def estimate_energy_v29(run: EnergyRunInputV29) -> EnergyEstimateV29:
    """Estimate energy for a run.

    Formulae:
    E_total[J] = P_total[W] * T_run[s]
    E_task[J/task] = E_total / N_tasks
    mWh/task = E_task / 3600 * 1000

    This is an accounting model, not a live power measurement.
    """
    run.validate()
    p = run.total_power_w()
    e_total = p * run.run_duration_s
    e_task = e_total / run.task_count
    return EnergyEstimateV29(
        total_power_w=p,
        run_duration_s=run.run_duration_s,
        total_energy_j=e_total,
        joules_per_task=e_task,
        millijoules_per_task=e_task * 1000.0,
        mwh_per_task=e_task / 3600.0 * 1000.0,
        tasks_per_joule=(run.task_count / e_total) if e_total > 0 else 0.0,
        notes=run.notes,
    )


def default_biogpu_a1_energy_input_v29(task_count: int = 1000, run_duration_s: float = 60.0) -> EnergyRunInputV29:
    """Conservative placeholder for BioGPU-A1 accounting.

    Values are placeholders until measured with a power meter / telemetry in a real lab.
    They intentionally include host + electronics + environmental overhead.
    """
    return EnergyRunInputV29(
        task_count=task_count,
        run_duration_s=run_duration_s,
        components=(
            PowerComponentV29("host_controller_pc", 65.0, "runtime, encoder, readout", "placeholder"),
            PowerComponentV29("mea_acquisition_stimulation_electronics", 25.0, "recording/stimulation interface", "placeholder"),
            PowerComponentV29("environment_control_share", 15.0, "incubator/stage-top/environment share", "placeholder"),
            PowerComponentV29("storage_and_network_share", 5.0, "trace storage / logging", "placeholder"),
        ),
        notes="BioGPU-A1 placeholder power budget; replace with measured telemetry in live_lab mode.",
    )
