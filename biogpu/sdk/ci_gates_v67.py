"""CI/CD Gate Runner v6.7."""
from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class GateResult:
    gate_id: str
    passed: bool
    output: str = ""
    exit_code: int = -1


def load_gate_matrix(path: str | Path = "configs/ci_gate_matrix.json") -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def run_gate(gate: dict[str, Any]) -> GateResult:
    try:
        result = subprocess.run(gate["command"], shell=True, capture_output=True, text=True, timeout=300)
        return GateResult(
            gate_id=gate["id"],
            passed=result.returncode == 0,
            output=result.stdout[-2000:] + result.stderr[-2000:],
            exit_code=result.returncode,
        )
    except Exception as exc:
        return GateResult(gate_id=gate["id"], passed=False, output=str(exc))


def run_pipeline(matrix_path: str | Path = "configs/ci_gate_matrix.json") -> dict[str, Any]:
    matrix = load_gate_matrix(matrix_path)
    results = []
    for gate_id in matrix["pipeline_order"]:
        gate = next((g for g in matrix["gates"] if g["id"] == gate_id), None)
        if gate is None:
            continue
        result = run_gate(gate)
        results.append({"gate_id": result.gate_id, "passed": result.passed, "exit_code": result.exit_code})
        if gate.get("required") and not result.passed:
            break
    passed = all(r["passed"] for r in results)
    return {
        "version": "v6.7",
        "gates_run": len(results),
        "gates_passed": sum(1 for r in results if r["passed"]),
        "all_required_passed": passed,
        "results": results,
    }


if __name__ == "__main__":
    pipeline = run_pipeline()
    print(f"CI/CD v6.7: {pipeline['gates_passed']}/{pipeline['gates_run']} gates passed")
    print(f"All required: {pipeline['all_required_passed']}")
    sys.exit(0 if pipeline["all_required_passed"] else 1)
