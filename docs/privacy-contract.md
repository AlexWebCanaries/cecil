# Privacy Contract Boundaries

Prohibited from telemetry payload by default:
- raw prompts (`prompt`, `raw_prompt`)
- API keys
- authorization/header material

Enforced by:
- emitter design (`build_event` only emits allowlisted fields)
- schema `additionalProperties: false`
- test coverage validating prohibited fields are absent/rejected

Snippet mode:
- disabled by default
- requires `CECIL_REDACTION_MODE=redacted_snippets` and `CECIL_SNIPPETS_ENABLED=true`
- deterministic redaction for secret markers, emails, phone-like values, and long numeric strings
