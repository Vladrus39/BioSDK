# BioGPU-Core v5.47 Registry Revoke/Yank Notification Contract

v5.47 adds a local registry revoke/yank and recipient notification drill over the v5.46 private registry auth/feed proof.

It validates:

- local revoke/yank policy and trigger matrix;
- local token/feed disable manifest;
- denial of unauthorized trigger, unauthorized role, missing incident link, missing recipient acknowledgement, live registry yank, public registry yank and production distribution requests;
- recipient notification acknowledgement trail;
- post-yank access denial probe;
- incident linkage export.

## Run

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_biogpu_v547_registry_revoke_yank_notification.ps1
```

## Outputs

- `outputs/v547_registry_revoke_yank_notification/V547_REGISTRY_REVOKE_YANK_NOTIFICATION_SUMMARY.json`
- `outputs/v547_registry_revoke_yank_notification/V547_REGISTRY_REVOKE_YANK_POLICY.json`
- `outputs/v547_registry_revoke_yank_notification/V547_REVOKE_YANK_MATRIX.json`
- `outputs/v547_registry_revoke_yank_notification/V547_LOCAL_YANK_MANIFEST.json`
- `outputs/v547_registry_revoke_yank_notification/V547_RECIPIENT_NOTIFICATION_ACK_TRAIL.json`
- `outputs/v547_registry_revoke_yank_notification/V547_REVOKE_YANK_EFFECT_PROBE.json`
- `outputs/v547_registry_revoke_yank_notification/V547_INCIDENT_LINKAGE_EXPORT.json`
- `outputs/v547_registry_revoke_yank_notification/V547_REVOKE_YANK_AUDIT_BUNDLE.json`
- `outputs/v547_registry_revoke_yank_notification/V547_REVOKE_YANK_MATRIX.csv`
- `outputs/v547_registry_revoke_yank_notification/V547_RECIPIENT_NOTIFICATION_ACK_TRAIL.csv`

## Missing real inputs

This proof does not perform a real private registry yank. Real readiness still needs a live registry revoke/yank endpoint, production token revocation and package yank authority, notification provider integration, real recipient acknowledgements, registry log retention/export and production incident workflow.

## Boundary

This is a local revoke/yank and notification drill only. It is not production yank authority, live private registry revocation, real notification delivery, public distribution, full BioSDK, production BioCompute Runtime or BiC OS readiness.
