# Feature Plan: Public LLM Observer SDK Implementation

## Scope
Implement the public Python SDK for local LLM observability, optional telemetry export, and versioned telemetry contract artifacts.

## Design approach
- Privacy-first event normalization with default hash-only prompt handling.
- Best-effort provider patching for OpenAI and Anthropic.
- Fail-open telemetry transport using an async bounded queue and retries.
- Contract-first schema validation with CI compatibility checks.

## API changes
- Added `llm_observer.patch()` and `llm_observer.shutdown()`.
- Added event construction helpers and schema validation support.

## Edge cases
- Unknown model pricing.
- Provider SDK modules unavailable.
- Telemetry queue overflow.
- Telemetry endpoint unavailable or timing out.

## Failure modes
- Analyzer and transport failures are swallowed and logged.
- Provider request path is preserved under SDK failures.

## Test plan
- Unit tests for config, canonicalization, hashing, cache breakers, cost, schema.
- Integration tests for mocked OpenAI/Anthropic adapters and transport behavior.
- Failure tests for endpoint down, queue overflow, and fail-open behavior.
- Golden tests for similarity stability.
