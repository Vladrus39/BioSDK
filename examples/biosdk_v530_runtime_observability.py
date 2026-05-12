from biogpu.runtime.observability_v530 import run_runtime_observability_workflow_v530, write_runtime_observability_outputs_v530


if __name__ == "__main__":
    audit = run_runtime_observability_workflow_v530()
    paths = write_runtime_observability_outputs_v530(audit)
    print(audit["overall_status"])
    print(paths["summary_json"])