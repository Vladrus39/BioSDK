from biogpu.runtime.local_service_v528 import run_authenticated_local_service_workflow_v528, write_authenticated_local_service_outputs_v528


if __name__ == "__main__":
    audit = run_authenticated_local_service_workflow_v528()
    paths = write_authenticated_local_service_outputs_v528(audit)
    print(audit["overall_status"])
    print(paths["summary_json"])