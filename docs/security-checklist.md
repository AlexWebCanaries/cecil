# Security and Privacy Checklist

Mapped to PRD/design requirements:

- [x] Raw prompts are excluded from default telemetry payloads.
- [x] API keys are never included in event payloads.
- [x] Authorization headers are scrubbed from logs.
- [x] SDK supports full disable via `CECIL_ENABLED=false`.
- [x] Telemetry sender is fail-open and non-blocking for provider calls.
- [x] Bounded queue with drop strategy prevents unbounded memory growth.
- [x] Retry and timeout constraints are enforced.
- [x] Contract schema is versioned (`v1`) and validated in CI.
