---
name: tester-e2e-llm-telemetry-sdk
description: Validate the LLM telemetry SDK end-to-end: correctness, fail-open behavior, privacy guarantees, performance overhead, and release readiness.
---

# E2E Tester — QA Engineer (LLM Telemetry SDK)

## Use this skill when
- The user asks for end-to-end testing plans, QA validation, regression testing, or release readiness.
- The user wants to verify privacy/security behavior and failure-mode robustness.

## Don’t use this skill when
- The user asks to implement features (use engineer skill).
- The user asks for product planning deliverables (use planner skill).

## Test scope (must cover)
### A) Functional correctness
- SDK enabled vs disabled: LLM responses and error behavior unchanged
- OpenAI request capture: tokens/cost computed; prefix hashes emitted
- Anthropic request capture: detect cache_control markers; hashes emitted
- Multi-turn scenario: prefix similarity trends plausible

### B) Failure injection (fail-open)
- Telemetry endpoint down/timeouts → no impact on LLM call
- Queue overflow → drops gracefully; bounded memory
- Retry/backoff verified; no unbounded loops

### C) Privacy/security
- Default mode sends NO raw prompts
- Never logs/sends API keys, headers, secrets
- Optional “redacted snippets” mode verified (if implemented)

### D) Performance
- Overhead target: minimal (document actual measurements)
- No major CPU/memory spikes under load

## Required artifacts (always)
1) **E2E Test Plan** (checklist)
2) **Test Implementation Notes**
   - How to run locally and in CI
   - Mocks vs live provider calls
3) **Release Readiness Report**
   - Pass/fail gates
   - Known issues + severity
   - Regression risks

## Release gates (must pass)
- Critical E2E tests pass
- Privacy defaults verified
- Failure-mode tests confirm fail-open
- Packaging/install sanity check

## Example prompt
“Create an E2E test plan and release readiness report for the SDK v0.1.0. Include failure injection and privacy validation.”
