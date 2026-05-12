# BioGPU-Core v5.32 Bounded Retry and Dead Letter Queue

v5.32 adds a local recovery policy proof over the durable scheduler facade.

It validates three narrow runtime properties:

- bounded retry attempts are enforced;
- retry jobs carry deterministic backoff metadata;
- jobs that exhaust the policy are terminally recorded in a local dead-letter audit entry.

## Run

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_biogpu_v532_bounded_retry_dead_letter.ps1
```

## Outputs

- `outputs/v532_bounded_retry_dead_letter/V532_BOUNDED_RETRY_DEAD_LETTER_SUMMARY.json`
- `outputs/v532_bounded_retry_dead_letter/V532_RETRY_POLICY.json`
- `outputs/v532_bounded_retry_dead_letter/V532_RETRY_POLICY_ACTIONS.json`
- `outputs/v532_bounded_retry_dead_letter/V532_DEAD_LETTER_QUEUE.json`
- `outputs/v532_bounded_retry_dead_letter/V532_RETRY_POLICY_AUDIT_BUNDLE.json`
- `outputs/v532_bounded_retry_dead_letter/BIOGPU_V532_BOUNDED_RETRY_DEAD_LETTER_REPORT.md`

## Boundary

This is a deterministic local retry-policy proof. It is not a production retry scheduler, hosted dead-letter queue, paging system, worker crash supervisor, live external API controller or BiC OS readiness claim.
