from __future__ import annotations

from pathlib import Path

from biogpu.runtime.retry_policy_v532 import run_bounded_retry_dead_letter_workflow_v532, write_bounded_retry_dead_letter_outputs_v532


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "outputs" / "v532_bounded_retry_dead_letter_example"
    audit = run_bounded_retry_dead_letter_workflow_v532(root, out)
    write_bounded_retry_dead_letter_outputs_v532(audit, out)
    print(audit["overall_status"])
    print(f"bounded_retry_dead_letter_ready={audit['bounded_retry_dead_letter_ready']}")
    print(f"dead_letter_job_id={audit['dead_letter_job_id']}")
    print(f"production_retry_policy_ready={audit['production_retry_policy_ready']}")


if __name__ == "__main__":
    main()