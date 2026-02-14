# Gap-Closure Feature Plan (Strict SDLC)

## Scope
Close reliability, privacy, analytics-value, and release-hardening gaps identified in `ENGINEERING_SDK_GAP_CLOSURE_TASKS.md`.

## Design approach
- Keep patching fail-open but make patch state factual and idempotent.
- Add auditable shutdown accounting in telemetry sender.
- Make prefix history lock-protected and bounded.
- Enforce strict privacy defaults and opt-in snippet gating.
- Improve extraction coverage for structured provider message blocks.
- Externalize savings and pricing data/logic for explainability and maintainability.
- Add actionable recommendation object in local analysis output.
- Harden changelog generation and add compatibility/performance checks in CI.

## API changes
- Extend config with additional safe tuning fields.
- Add pricing metadata and recommendation fields in event output.
- Add optional shutdown drain behavior controls.

## Edge cases
- Providers unavailable at first patch and later become available.
- Shutdown called under queue backlog.
- Invalid privacy config values.
- Structured mixed-content prompts with non-text blocks.
- Missing git metadata in release environments.

## Failure modes
- All telemetry/send/analyzer errors remain non-fatal.
- Queue accounting remains complete even under early shutdown.
- Invalid privacy/savings config values fail-safe to strict defaults.

## Test plan
- Deterministic patch-idempotency tests.
- Shutdown accounting tests (immediate, bounded flush, large queue).
- Concurrency tests for bounded prefix history.
- Privacy/schema tests for strict defaults and redaction coverage.
- Calibration tests for savings model and pricing metadata.
- Changelog git-present and git-absent tests.
- Perf/stress checks and provider compatibility matrix tests.
