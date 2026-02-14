# Remediation Feature Plan (Strict SDLC)

## Scope
Complete post-readiness remediation tasks for packaging metadata stability, live-test safety, and release process polish.

## Design approach
- Modernize package license metadata to PEP 621 style and add explicit license-files.
- Add a deterministic CI guard script that fails on known setuptools license deprecation warnings.
- Provide pinned live-test dependency group and strict opt-in guard logic for live API tests.
- Add one-command release dry-run target and QA summary stub generator.

## API changes
- No runtime SDK API changes.
- Build/release tooling and test-safety behavior are enhanced.

## Edge cases
- Live tests accidentally run with placeholder API keys.
- Build warnings reintroduced by metadata drift.
- Release readiness checks run in environments without explicit test intent flags.

## Failure modes
- CI fails when targeted packaging deprecation warnings appear.
- Live tests refuse to run without explicit confirmation env vars.

## Test plan
- Run quality gates (`make ci`).
- Run explicit build + twine + wheel smoke checks.
- Run live-test file in safe mode to verify opt-in guard behavior.
