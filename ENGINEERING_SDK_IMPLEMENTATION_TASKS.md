# Public SDK Implementation Tasks (Engineering Agent)

## Purpose
Implement the **public open-source Python SDK only** for LLM observability and optional telemetry export.

This plan is derived from:
- `/Users/alexmilman/Dev/cecil/prd.md`
- `/Users/alexmilman/Dev/cecil/design-doc.md`

Do not implement private SaaS services, AWS backend modules, dashboard UI, or cloud infrastructure in this workstream.

---

## Status Rules
- Update each task checkbox as work completes.
- Add linked PR/commit references under each completed task.
- Do not mark a task complete unless all acceptance criteria pass.

Legend:
- `[x]` Completed
- `[ ]` Not completed
- Commit/PR reference note: this workspace was provided without a `.git` directory, so commit links are not available for this execution.

---

## Completed Planning Tasks
- [x] Review PRD and design doc and extract SDK-only scope.
- [x] Produce implementation-ready task breakdown with milestones.
- [x] Create this engineering execution checklist for tracking and verification.

---

## Milestone M1: Foundation and Contract

### 1) Repository and package skeleton
Reference: N/A (no `.git` metadata). Evidence: `pyproject.toml`, `.github/workflows/ci.yml`, `/Users/alexmilman/Dev/cecil/sdk/python/llm_observer`.
- [x] Create SDK structure:
  - `sdk/python/llm_observer/`
  - `tests/`
  - `examples/`
  - `shared/schema/`
  - `docs/`
- [x] Add package metadata and installable setup.
- [x] Add CI entrypoint for tests and lint.

Acceptance criteria:
- Package installs in clean virtual environment.
- `pytest` discovers and runs baseline tests.

### 2) Versioned telemetry schema (`v1`)
Reference: N/A (no `.git` metadata). Evidence: `/Users/alexmilman/Dev/cecil/shared/schema/telemetry_event_v1.json`, `/Users/alexmilman/Dev/cecil/docs/schema-examples.md`.
- [x] Add `shared/schema/telemetry_event_v1.json`.
- [x] Define required, optional, and privacy-safe fields.
- [x] Include schema version field in event envelope.
- [x] Add schema examples under docs.

Acceptance criteria:
- Sample events validate against schema.
- SDK emits schema-compliant envelope in tests.

### 3) Configuration and mode handling
Reference: N/A (no `.git` metadata). Evidence: `/Users/alexmilman/Dev/cecil/sdk/python/llm_observer/config.py`, `/Users/alexmilman/Dev/cecil/tests/unit/test_config.py`.
- [x] Implement env var config:
  - `LLM_OBSERVER_ENABLED`
  - `LLM_OBSERVER_API_KEY`
  - `LLM_OBSERVER_ENDPOINT`
- [x] Default to local-only mode when telemetry is not enabled.
- [x] Add explicit disable switch behavior.

Acceptance criteria:
- Config precedence and defaults are unit-tested.
- Telemetry is never sent in default local-only mode.

---

## Milestone M2: Core SDK Behavior

### 4) Minimal onboarding API
Reference: N/A (no `.git` metadata). Evidence: `/Users/alexmilman/Dev/cecil/sdk/python/llm_observer/patcher.py`, `/Users/alexmilman/Dev/cecil/examples/quickstart_local.py`.
- [x] Implement `llm_observer.patch()` as the primary setup API.
- [x] Ensure integration remains 1-2 lines in consuming app.
- [x] Preserve existing app behavior when patching fails.

Acceptance criteria:
- Quickstart example runs with one import + one function call.
- Patch failures do not break downstream LLM calls.

### 5) Provider instrumentation adapters
Reference: N/A (no `.git` metadata). Evidence: `/Users/alexmilman/Dev/cecil/sdk/python/llm_observer/adapters/openai_adapter.py`, `/Users/alexmilman/Dev/cecil/sdk/python/llm_observer/adapters/anthropic_adapter.py`, `/Users/alexmilman/Dev/cecil/tests/integration`.
- [x] Implement OpenAI adapter for request/response metadata capture.
- [x] Implement Anthropic adapter if in MVP scope; otherwise gate behind feature flag with TODO marker.
- [x] Normalize metadata to internal event model.

Acceptance criteria:
- Adapter integration tests pass with provider SDK mocks.
- Normalized event fields are consistent across providers.

### 6) Privacy-first normalization
Reference: N/A (no `.git` metadata). Evidence: `/Users/alexmilman/Dev/cecil/sdk/python/llm_observer/privacy.py`, `/Users/alexmilman/Dev/cecil/tests/unit/test_privacy_event.py`.
- [x] Hash prompt-derived content by default.
- [x] Block raw prompt exfiltration by default.
- [x] Support explicit opt-in mode for redacted snippets (if product approves).

Acceptance criteria:
- Tests prove raw prompt content is absent in default telemetry payloads.
- Sensitive fields are scrubbed in logs.

### 7) Local cost estimation engine
Reference: N/A (no `.git` metadata). Evidence: `/Users/alexmilman/Dev/cecil/sdk/python/llm_observer/cost.py`, `/Users/alexmilman/Dev/cecil/tests/unit/test_cost.py`.
- [x] Implement cost estimate per request from model and token metadata.
- [x] Add fallback behavior for unknown models.
- [x] Expose estimate outputs in structured local result object.

Acceptance criteria:
- Deterministic unit tests for known pricing fixtures.
- Unknown model path is non-fatal and well-labeled.

### 8) Prefix similarity and cache opportunity analysis
Reference: N/A (no `.git` metadata). Evidence: `/Users/alexmilman/Dev/cecil/sdk/python/llm_observer/canonicalize.py`, `/Users/alexmilman/Dev/cecil/sdk/python/llm_observer/cache_analysis.py`, `/Users/alexmilman/Dev/cecil/tests/golden/test_similarity_golden.py`.
- [x] Implement prompt prefix canonicalization.
- [x] Compute similarity scores for cache opportunity estimation.
- [x] Emit recommended savings estimate fields.

Acceptance criteria:
- Golden tests pass for canonicalization and similarity scoring.
- Equivalent prompts with formatting noise produce stable similarity values.

### 9) Cache-breaker detection
Reference: N/A (no `.git` metadata). Evidence: `/Users/alexmilman/Dev/cecil/sdk/python/llm_observer/cache_analysis.py`, `/Users/alexmilman/Dev/cecil/docs/cache-breaker-tradeoffs.md`.
- [x] Detect common breakers (timestamps, UUIDs, random IDs, nonce-like patterns).
- [x] Emit breaker categories and confidence score.
- [x] Attach mitigation hint text for local recommendations.

Acceptance criteria:
- Fixture-based tests cover each breaker class.
- False-positive and false-negative tradeoffs are documented.

---

## Milestone M3: Telemetry Transport and Reliability

### 10) Telemetry transport client (opt-in)
Reference: N/A (no `.git` metadata). Evidence: `/Users/alexmilman/Dev/cecil/sdk/python/llm_observer/telemetry.py`, `/Users/alexmilman/Dev/cecil/tests/integration/test_telemetry_transport.py`.
- [x] Implement HTTP sender for telemetry endpoint.
- [x] Use machine auth format from design docs (`Authorization: Bearer ...`).
- [x] Add backoff/retry budget and timeouts.

Acceptance criteria:
- Mock-server integration tests validate auth header and payload shape.
- Sender respects timeout and retry limits.

### 11) Fail-open guarantees
Reference: N/A (no `.git` metadata). Evidence: `/Users/alexmilman/Dev/cecil/tests/integration/test_fail_open.py`, `/Users/alexmilman/Dev/cecil/tests/integration/test_transport_failures.py`.
- [x] Ensure no telemetry error can block or alter provider call behavior.
- [x] Swallow and log non-fatal SDK internal failures.
- [x] Add defensive guards around analyzer and sender modules.

Acceptance criteria:
- Chaos tests verify provider calls succeed during sender/analyzer failures.
- Error paths are observable but non-breaking.

### 12) SDK internal observability
Reference: N/A (no `.git` metadata). Evidence: `/Users/alexmilman/Dev/cecil/sdk/python/llm_observer/logging.py`, `/Users/alexmilman/Dev/cecil/sdk/python/llm_observer/telemetry.py`.
- [x] Add debug logging hooks with privacy scrubbing.
- [x] Add counters/metrics for dropped events and send failures.
- [x] Add structured diagnostic context for troubleshooting.

Acceptance criteria:
- Debug logs never contain API key secrets or raw prompt text.
- Operational counters are available in test assertions.

### 13) Contract compatibility checks
Reference: N/A (no `.git` metadata). Evidence: `/Users/alexmilman/Dev/cecil/scripts/check_schema_compat.py`, `/Users/alexmilman/Dev/cecil/tests/integration/test_contract_compat.py`.
- [x] Add schema validation tests in CI.
- [x] Add compatibility guardrails for future schema versions.
- [x] Fail CI on breaking contract changes without version bump.

Acceptance criteria:
- Breaking field removal/change fails CI.
- Non-breaking additions pass CI.

---

## Milestone M4: Quality, DX, and Release

### 14) Test suite completeness
Reference: N/A (no `.git` metadata). Evidence: `/Users/alexmilman/Dev/cecil/tests`, coverage threshold in `pyproject.toml`.
- [x] Unit tests for config, analyzers, privacy, and transport.
- [x] Integration tests for provider adapters with mocks.
- [x] Golden tests for similarity/cache analysis.

Acceptance criteria:
- CI is green on target Python versions.
- Coverage threshold is met (set threshold in CI config).

### 15) Developer onboarding artifacts
Reference: N/A (no `.git` metadata). Evidence: `/Users/alexmilman/Dev/cecil/docs/quickstart.md`, `/Users/alexmilman/Dev/cecil/docs/telemetry-opt-in.md`, `/Users/alexmilman/Dev/cecil/docs/troubleshooting.md`.
- [x] Add quickstart docs for local-only mode.
- [x] Add telemetry opt-in docs with env var setup.
- [x] Add troubleshooting and common failure docs.

Acceptance criteria:
- Clean machine setup to first output under 5 minutes.
- Docs examples are tested or smoke-validated in CI.

### 16) Security and privacy checklist
Reference: N/A (no `.git` metadata). Evidence: `/Users/alexmilman/Dev/cecil/docs/security-checklist.md`.
- [x] Add repo-level security checklist aligned with PRD requirements.
- [x] Document data handling and default privacy posture.
- [x] Document key handling and log scrubbing guarantees.

Acceptance criteria:
- Checklist maps to explicit PRD and design doc requirements.
- Security review artifacts are ready for internal review.

### 17) Packaging and release automation
Reference: N/A (no `.git` metadata). Evidence: `/Users/alexmilman/Dev/cecil/.github/workflows/release.yml`, `/Users/alexmilman/Dev/cecil/CHANGELOG.md`, `/Users/alexmilman/Dev/cecil/scripts/generate_changelog.py`.
- [x] Configure build/publish workflow for package release.
- [x] Add semantic versioning and changelog generation.
- [x] Add release checklist for schema/version compatibility.

Acceptance criteria:
- Tagged release produces installable package artifact.
- Release notes include behavior and contract changes.

### 18) Support policy and compatibility matrix
Reference: N/A (no `.git` metadata). Evidence: `/Users/alexmilman/Dev/cecil/docs/compatibility-matrix.md`, `/Users/alexmilman/Dev/cecil/docs/support-policy.md`, `/Users/alexmilman/Dev/cecil/docs/non-goals.md`.
- [x] Document supported Python versions and provider SDK ranges.
- [x] Document non-goals and known limitations.
- [x] Add deprecation and migration policy section.

Acceptance criteria:
- Compatibility matrix is present in docs.
- Upgrade path is documented for breaking changes.

---

## Explicit Non-Goals (Do Not Implement Here)
- Private SaaS ingestion backend (`ingest-service`, `analytics-service`, `admin-service`, `authz-service`).
- Frontend/dashboard implementation.
- AWS infra provisioning and Cognito setup.
- Multi-tenant SaaS runtime operations.

---

## Verification Protocol (For Later Completion Audit)
When implementation is claimed complete, perform verification in this exact order:

1. Scope compliance check
- Confirm only public SDK files were changed.
- Confirm no private SaaS implementation leaked into repo.

2. Contract and privacy check
- Validate emitted telemetry against `telemetry_event_v1.json`.
- Verify default mode sends no raw prompt text.

3. Reliability check
- Run failure-path tests to confirm fail-open behavior.
- Confirm provider calls still succeed under telemetry failures.

4. Quality gate
- Run full test suite and CI-equivalent checks locally.
- Confirm docs examples execute successfully.

5. Release readiness
- Confirm package builds, versioning is consistent, and changelog updated.
- Confirm compatibility matrix and security checklist are present.

Only after all five steps pass, mark remaining tasks complete.
