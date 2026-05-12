from biogpu.runtime.recovery_v531 import run_recovery_alerting_workflow_v531, write_recovery_alerting_outputs_v531


if __name__ == "__main__":
    audit = run_recovery_alerting_workflow_v531()
    paths = write_recovery_alerting_outputs_v531(audit)
    print(audit["overall_status"])
    print(paths["summary_json"])