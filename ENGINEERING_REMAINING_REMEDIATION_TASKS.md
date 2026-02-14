# Engineering Remediation Tasks (Post-Readiness Cleanup)

## Goal
Resolve remaining non-blocking issues before/alongside first public release, with focus on packaging deprecation warnings and long-term publish stability.

Repo: `/Users/alexmilman/Dev/cecil`

---

## Priority P0: Packaging Metadata Deprecation Cleanup

### 1) Migrate license metadata to modern PEP 621 style
- [x] Update `/Users/alexmilman/Dev/cecil/pyproject.toml`:
  - Change `project.license` from TOML table to SPDX string (for example `license = "MIT"`).
  - Add `project.license-files` with `["LICENSE"]` if not already inferred.
- [x] Remove deprecated license classifier if setuptools continues warning about it.

Acceptance criteria:
- `python -m build` runs with no setuptools license deprecation warnings.
- Built wheel metadata includes correct license expression and license file.

### 2) Add guard test/check for packaging warning regressions
- [x] Add CI check that fails if build emits targeted setuptools deprecation warnings.
- [x] Keep this check scoped to known warning patterns to avoid noisy false failures.

Acceptance criteria:
- CI fails when deprecated license metadata style is reintroduced.

---

## Priority P1: Live-Test Hardening and Safety

### 3) Pin live-test dependency compatibility explicitly
- [x] Add dedicated optional dependency group or requirements file for live OpenAI tests, including compatible `openai` + `httpx` versions.
- [x] Document exact install command in `/Users/alexmilman/Dev/cecil/docs`.

Acceptance criteria:
- New contributors can run live test setup without resolver ambiguity.

### 4) Improve live-test secret safety
- [x] Add explicit warning section in live-test docs:
  - keys must be ephemeral,
  - key rotation required after run.
- [x] Add optional test guard that refuses to run unless `OPENAI_API_KEY` appears to be non-placeholder and env flag confirms user intent.

Acceptance criteria:
- Live tests remain opt-in and include clear anti-leak controls.

---

## Priority P2: Release Process Polish

### 5) Add release dry-run command
- [x] Add a single scripted command (Makefile target or script) to run:
  - `make ci`
  - `twine check`
  - wheel smoke check
  - changelog generation check
- [x] Reference this command in `/Users/alexmilman/Dev/cecil/docs/release-checklist.md`.

Acceptance criteria:
- Release manager can run one deterministic pre-tag command locally.

### 6) Ensure QA report automation hook
- [x] Add template or script to auto-generate a release QA summary stub including:
  - commit SHA,
  - workflow links,
  - pass/fail matrix placeholders.

Acceptance criteria:
- QA reporting overhead is reduced and standardized.

---

## Verification Commands
- [x] `make ci`
- [x] `python -m build`
- [x] `python -m twine check dist/*`
- [x] `python /Users/alexmilman/Dev/cecil/scripts/smoke_check_wheel.py`

For live-test related updates:
- [x] `pytest -q tests/integration/test_openai_live_api.py` (only with explicit opt-in env vars)

---

## Definition of Done
- [x] Packaging build completes without current setuptools deprecation warnings.
- [x] CI enforces packaging metadata style to prevent regression.
- [x] Live-test setup and secret-safety guidance are documented and reproducible.
- [x] Release dry-run path is one-command and documented.
