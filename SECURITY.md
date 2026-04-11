# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.0.x   | ✅ Yes    |

## Reporting a Vulnerability

If you discover a security vulnerability in tradezero-sdk, please **do not** open a public GitHub issue — this could expose the vulnerability before a fix is available.

Instead, report it privately:

1. Open a [GitHub Security Advisory](https://github.com/shadyemad/tradezero-sdk/security/advisories/new) on this repository.
2. Alternatively, contact the maintainer directly via the email on the GitHub profile.

Please include:

- A description of the vulnerability and its potential impact
- Steps to reproduce the issue (minimal example preferred)
- The SDK version tested against

You can expect an acknowledgement within 48 hours and a resolution timeline within 7 days for confirmed vulnerabilities.

## Credential Safety

This SDK handles sensitive API credentials. **Never commit credentials to version control.**

Use environment variables instead:

```bash
export TZ_API_KEY="your-api-key"
export TZ_API_SECRET="your-api-secret"
```

The `.gitignore` in this repository blocks `api_keys.py`, `secrets.py`, `.env`, and `.env.*`. The live test fixtures read credentials from environment variables only — no hardcoded values exist in the repository.
