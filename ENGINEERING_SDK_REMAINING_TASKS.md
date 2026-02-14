# Remaining Engineering Tasks: Public Python SDK

## Goal
Ship a production-ready, privacy-first open source SDK with reliable cost/cache insights and a publish flow that is enforceable in CI.

References:
- `/Users/alexmilman/Dev/cecil/prd.md`
- `/Users/alexmilman/Dev/cecil/design-doc.md`
- `/Users/alexmilman/Dev/cecil/agents/skills/planner_principal_architect_pm/SKILL.md`
- `/Users/alexmilman/Dev/cecil/agents/skills/open_source_python_sdk_expert/SKILL.md`

---

## Review Snapshot
- [x] Core SDK architecture, privacy defaults, fail-open behavior, and telemetry schema are implemented.
- [x] Local gates pass: `make ci` (lint, typecheck, schema-compat, tests, build).
- [x] Gap-closure features (recommendations, savings model, bounded history, shutdown accounting) are implemented.
- [x] Remaining work is primarily publish-hardening, metadata completeness, and compatibility enforcement.

---

## Priority P0: Publish-Blocking Tasks

### 1) Add OSS license file
- [x] Add `/Users/alexmilman/Dev/cecil/LICENSE` (MIT text matching `pyproject.toml`).
- [x] Add license mention in `/Users/alexmilman/Dev/cecil/README.md`.

Acceptance criteria:
- `LICENSE` file exists at repo root.
- License in file and package metadata are consistent.

### 2) Enforce artifact sanity in CI/release
- [x] Add `twine check dist/*` step after build in CI or release workflow.
- [x] Add wheel install smoke test from built artifact in clean venv:
  - `pip install dist/*.whl`
  - `python -c "import llm_observer; print(llm_observer.__all__)"`
- [x] Verify packaged data files load from wheel (`pricing_v1.json`, `telemetry_event_v1.json`).

Acceptance criteria:
- Release pipeline fails on invalid package metadata/distribution artifacts.
- Built wheel imports and data resource loading pass in isolated environment.

### 3) Add missing package metadata for discoverability
- [x] Add `[project.urls]` in `/Users/alexmilman/Dev/cecil/pyproject.toml`:
  - Homepage
  - Repository
  - Issues
  - Documentation
- [x] Add missing trove classifiers for license and intended audience.

Acceptance criteria:
- `pyproject.toml` contains complete, accurate project URLs and classifiers.

---

## Priority P1: Compatibility and Contract Enforcement

### 4) Make provider compatibility checks real, not mostly skipped
- [x] Add dedicated CI workflow/job that installs pinned provider SDK versions from `/Users/alexmilman/Dev/cecil/docs/compatibility-matrix.md`.
- [x] Ensure `/Users/alexmilman/Dev/cecil/tests/compat/test_provider_contracts.py` runs unskipped in that job.
- [x] Add explicit version assertions in compat tests so matrix claims are enforced.

Acceptance criteria:
- CI has at least one job where compat tests run with real `openai` and `anthropic` packages.
- Failing provider import path or version mismatch breaks CI.

### 5) Close doc-vs-CI drift for compatibility claims
- [x] Update `/Users/alexmilman/Dev/cecil/docs/compatibility-matrix.md` to map each claimed range to exact CI job(s).
- [x] Add link in docs to workflow file(s).

Acceptance criteria:
- Every compatibility claim is traceable to an automated test job.

---

## Priority P2: Release Process Hardening

### 6) Add TestPyPI staging path
- [x] Add manual/dispatch workflow to publish to TestPyPI before production PyPI.
- [x] Add install verification against TestPyPI artifact.

Acceptance criteria:
- Team can run a non-production publish+install rehearsal before live release.

### 7) Improve release checklist fidelity
- [x] Update `/Users/alexmilman/Dev/cecil/docs/release-checklist.md` with:
  - `twine check`
  - wheel install smoke test
  - TestPyPI rehearsal
  - changelog generation source verification (`git` vs fallback file)

Acceptance criteria:
- Checklist covers all release-critical validation steps already automated or explicitly manual.

---

## Suggested Execution Order
1. P0 tasks 1-3
2. P1 tasks 4-5
3. P2 tasks 6-7

---

## Completion Gate
Only mark this file complete when all items below are true:
- [x] `LICENSE` exists and matches metadata.
- [x] CI/release validates built distributions (`twine check` + wheel install smoke).
- [x] Compat matrix claims are enforced by non-skipped CI jobs with pinned provider versions.
- [x] Release docs reflect actual enforced process.
