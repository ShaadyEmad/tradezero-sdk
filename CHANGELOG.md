# Changelog

All notable changes to this project will be documented in this file.

Follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.1] — 2026-04-11

### Fixed

- Pinned `httpx < 0.28` to restore compatibility with `respx` mock transport.
- Resolved all 37 strict `mypy` type errors across 5 source files.
- Rewrote unit tests to use `with respx.mock` context manager pattern (fixes `AllMockedAssertionError` on respx 0.21).
- Removed unused `# type: ignore[misc]` comments from HTTP client retry decorators.
- Added `plugins = ["pydantic.mypy"]` to mypy config for correct Pydantic v2 field validation.
- CI workflow now installs Poetry via pip for reliable cross-platform builds.

---

## [1.0.0] — 2026-04-11

This is the first stable public release of tradezero-sdk. The package is now
considered production-ready and follows semantic versioning from this point forward.

### Added

- First stable public release — the API surface is now stable.
- Professional `README.md` with full API reference, enum table, exception guide, and retry documentation.
- Comprehensive `DOCUMENTATION.md` covering every class, method, model, and enum in full detail.
- `SECURITY.md` with vulnerability reporting policy and credential safety guidelines.
- GitHub issue templates for bug reports and feature requests (`.github/ISSUE_TEMPLATE/`).
- `examples/basic_sync.py` and `examples/basic_async.py` — runnable usage examples.
- PayPal sponsorship link in README.
- Re-exports added to `tradezero/client/__init__.py`, `tradezero/http/__init__.py`,
  and `tradezero/modules/__init__.py`.

### Changed

- `pyproject.toml` development status set to `Production/Stable`.
- Author email set to `ShadyEmadContact@gmail.com`.
- All live test fixtures read credentials from environment variables
  (`TZ_API_KEY`, `TZ_API_SECRET`) — no hardcoded values anywhere in the repository.
