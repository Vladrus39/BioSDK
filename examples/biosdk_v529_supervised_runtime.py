from biogpu.runtime.supervised_runtime_v529 import run_supervised_runtime_workflow_v529, write_supervised_runtime_outputs_v529


if __name__ == "__main__":
    audit = run_supervised_runtime_workflow_v529()
    paths = write_supervised_runtime_outputs_v529(audit)
    print(audit["overall_status"])
    print(paths["summary_json"])