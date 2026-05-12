# v4.5 Security / Data Handling / Enterprise Pilot

## Principle
Early testers receive maximum safe software-level access. Live biological actuation remains blocked unless a lab/vendor-approved protocol exists.

## Data handling rules

- **DH1 (uploaded_data)**: Customer neural data must be stored in isolated workspaces with job-level audit logs. Required for: hosted_beta, enterprise_on_prem.
- **DH2 (exports)**: Result bundles must include manifest, parameters, metrics, and audit log; raw customer data should not be redistributed unless explicitly requested. Required for: all.
- **DH3 (api_credentials)**: External API credentials must never be stored in generated result bundles or committed to repository. Required for: external_api, hosted_beta.
- **DH4 (live_systems)**: Live actuation is blocked by default and requires lab/vendor approval, allowlisted schema, and operator confirmation. Required for: live_shadow, closed_loop.
- **DH5 (claims)**: Reports must distinguish replay, read-only live shadow, and approved live closed-loop evidence. Required for: all.

## Enterprise pilot boundary
The first paid enterprise product should be read-only/replay/on-prem or hosted read-only. Live shadow is premium. Closed-loop actuation is a separate approved add-on.

