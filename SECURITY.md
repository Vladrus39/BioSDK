# Security Policy

## Reporting a Vulnerability

Email: vladimoryachok@gmail.com
GitHub: https://github.com/Vladrus39/BioSDK/issues

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.4   | Yes       |
| 0.1.3   | Yes       |
| < 0.1.3 | No        |

## Security Practices

- **API keys**: All keys use environment variables with fixture defaults for local development. Production deployments must override via env vars.
- **Signing**: Evidence bundles use HMAC-SHA256 with `BIOSDK_SIGNING_KEY` env var. Default is for development only.
- **Dependencies**: Pinned with minimum versions in `pyproject.toml`. Run `pip audit` periodically.
- **Closed-loop**: Safety gates block live actuation by default. Hardware stimulation requires lab approval.
- **Wheel**: Tests, legacy, and data directories are excluded from published wheels.

## What Is NOT Security-Ready

- The `biogpu/runtime/local_service_v528.py` module is a local contract proof — not a production API server
- HMAC signing is for integrity verification, not cryptographic authentication
- No TLS, no OAuth, no production secret management
- The project does not claim production security readiness

## System-Hardening Checklist (for Production)

- [ ] Replace all fixture keys with production secrets
- [ ] Enable TLS on dashboard/API endpoints
- [ ] Implement proper OIDC/OAuth instead of header API keys
- [ ] Add rate limiting on API endpoints
- [ ] Regular dependency vulnerability scanning
- [ ] Signed git commits (GPG)
- [ ] Container image signing
- [ ] Audit logging to immutable storage
