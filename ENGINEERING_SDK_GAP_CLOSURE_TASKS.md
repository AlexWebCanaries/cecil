# Engineering Gap-Closure Tasks: Robust Privacy-First SDK

## Objective
Close remaining gaps to ship a robust public SDK that is:
- privacy-first by default,
- fail-open under all telemetry failures,
- genuinely useful for cost analysis and cache optimization.

This review applies:
- `planner-llm-telemetry-sdk` (planning and measurable outcomes)
- `architect-repo-reviewer` (complexity/risk reduction and repo hardening)

Reference docs:
- `/Users/alexmilman/Dev/cecil/prd.md`
- `/Users/alexmilman/Dev/cecil/design-doc.md`

---

## Current State (Validated)
- [x] Core SDK exists with patching, event model, telemetry transport, schema, docs, and CI workflows.
- [x] Local quality gates pass (`make lint`, `make typecheck`, `make test`).
- [x] Default telemetry payload excludes raw prompt text.
- [x] Basic cost estimation and cache-breaker analysis are implemented.

---

## Key Gaps Found (Why More Work Is Required)

1. Incorrect patch status/idempotency behavior
- Evidence: `/Users/alexmilman/Dev/cecil/sdk/python/llm_observer/patcher.py:33` returns `openai_patched=True` and `anthropic_patched=True` whenever `_PATCHED` is true, even if no provider was actually patched on initial call.
- Repro validated in this workspace: first `patch()` returned false/false, second returned true/true without provider modules available.

2. Telemetry queue shutdown can silently lose events
- Evidence: `/Users/alexmilman/Dev/cecil/sdk/python/llm_observer/telemetry.py:48` sets stop and joins thread without draining queue.
- Repro validated: emitted 100 events, stop returned with only 1 counted event (`sent + failures + dropped = 1`).

3. Prefix history is global, unbounded, and not concurrency-safe
- Evidence: `/Users/alexmilman/Dev/cecil/sdk/python/llm_observer/event_model.py:25` uses a process-global dict without locks and no max size.
- Impact: race risk in multi-threaded apps and memory growth for unbounded model IDs.

4. Prompt extraction support is narrow for provider message shapes
- Evidence: `/Users/alexmilman/Dev/cecil/sdk/python/llm_observer/adapters/common.py:15` only extracts `content[].text` in list-content mode.
- Impact: misses tokens/text for newer content block formats, reducing analytics quality.

5. Value quality for cache/cost insights is still heuristic-only
- Evidence: similarity is strict character-prefix compare and savings multiplier is fixed (`0.3`) in `/Users/alexmilman/Dev/cecil/sdk/python/llm_observer/event_model.py:50`.
- Impact: useful baseline exists, but recommendations are not yet calibrated for robust decision-making.

---

## Execution Plan (Engineer Tasks)

Legend:
- `[x]` completed
- `[ ]` pending
- Commit/PR reference note: this workspace has no `.git` metadata, so commit links are unavailable; file-level evidence is included in implementation output.

## Phase 1: Correctness and Reliability (P0)

### 1) Fix patch idempotency and truthful status reporting
- [x] Track provider patch state separately (`openai_patched`, `anthropic_patched`) instead of single `_PATCHED`.
- [x] Return factual status on every `patch()` call.
- [x] Allow late provider availability to be patched on subsequent calls.
- [x] Add deterministic tests for:
  - no providers available,
  - one provider available,
  - provider becomes available after first call,
  - repeated patch calls.

Acceptance criteria:
- `patch()` never reports patched provider unless wrapper is actually installed.
- Repeat calls are idempotent and state-accurate.

### 2) Implement graceful telemetry drain semantics on shutdown
- [x] Add `shutdown_mode` or equivalent behavior: bounded flush before stop.
- [x] Track `abandoned_on_shutdown` counter for unsent queued events.
- [x] Ensure no silent loss: all emitted events are either `sent`, `failures`, `dropped`, or `abandoned_on_shutdown`.
- [x] Add tests for immediate shutdown, bounded-time shutdown, and large queue.

Acceptance criteria:
- Event accounting is complete and auditable at shutdown.
- `shutdown()` remains bounded and fail-open.

### 3) Make event history thread-safe and bounded
- [x] Protect prefix history updates with lock or single-writer design.
- [x] Replace unbounded dict with bounded LRU/TTL store.
- [x] Add tests for concurrent `build_event` calls and bounded memory behavior.

Acceptance criteria:
- No data race under concurrent load tests.
- Memory usage for history does not grow unbounded.

---

## Phase 2: Privacy Hardening (P0/P1)

### 4) Enforce explicit privacy modes and safe defaults
- [x] Validate `LLM_OBSERVER_PRIVACY_MODE` against allowed enum.
- [x] Ignore/fail-safe invalid privacy mode values to strict hash-only behavior.
- [x] Add tests for invalid/missing/edge env values.

Acceptance criteria:
- Unknown privacy config cannot widen data exposure.
- Privacy mode behavior is documented and tested.

### 5) Harden optional snippet mode
- [x] Gate `redacted_snippets` behind explicit secondary opt-in flag.
- [x] Improve snippet redaction beyond secret-key terms (emails, phone-like patterns, long numbers).
- [x] Add tests proving sensitive patterns are removed.

Acceptance criteria:
- Default mode remains snippet-free.
- Optional snippet mode has deterministic privacy scrubbing guarantees.

### 6) Strengthen schema-level privacy guarantees
- [x] Add schema constraints/patterns for identifiers where appropriate (`event_id` UUID format, bounded string lengths).
- [x] Document prohibited fields and prove they cannot appear with schema + emitter tests.

Acceptance criteria:
- Schema and emitter jointly enforce privacy contract boundaries.

---

## Phase 3: Analytics Value Improvements (P1)

### 7) Improve prompt normalization and extraction fidelity
- [x] Expand `extract_prompt` to support common list-content variants from provider SDKs.
- [x] Add fixtures for mixed structured content blocks.
- [x] Preserve cache-boundary signal fidelity when present.

Acceptance criteria:
- Prompt extraction coverage includes current OpenAI/Anthropic structured message shapes used by supported versions.

### 8) Replace static savings heuristic with explicit model
- [x] Move `cache_savings_estimate_usd` logic into isolated module with documented assumptions.
- [x] Support tunable factors via config (with safe defaults).
- [x] Add calibration fixtures and expected outputs.

Acceptance criteria:
- Savings math is explainable, testable, and configurable without code edits.

### 9) Expand and version pricing data strategy
- [x] Move pricing table to versioned data artifact (instead of hardcoded dict only).
- [x] Add update workflow and stale-data policy.
- [x] Emit pricing-source metadata in local analysis output.

Acceptance criteria:
- Unknown-model rate is measurable.
- Pricing updates do not require core logic rewrites.

### 10) Add actionable recommendation surface
- [x] Expose local recommendation API/object summarizing:
  - top cache breakers,
  - potential savings range,
  - confidence level,
  - concrete fix hints.
- [x] Add docs/examples showing how app teams consume recommendations.

Acceptance criteria:
- SDK provides directly actionable output, not just raw telemetry fields.

---

## Phase 4: Operational and Release Hardening (P1)

### 11) Harden release/changelog flow for non-git and CI environments
- [x] Make `scripts/generate_changelog.py` degrade safely when git metadata is unavailable.
- [x] Add fallback mode from tagged release notes or provided input file.
- [x] Add tests for both git-present and git-absent execution.

Acceptance criteria:
- Release prep does not fail solely due to missing local git metadata.

### 12) Add performance and stress tests
- [x] Add benchmark/stress tests for telemetry queue throughput and backpressure.
- [x] Add tests ensuring instrumentation overhead remains within target budget.

Acceptance criteria:
- Measured overhead budget is documented and enforced in CI (or scheduled perf job).

### 13) Add compatibility contract tests against pinned provider SDK versions
- [x] Add matrix tests for supported OpenAI/Anthropic SDK version ranges.
- [x] Fail CI on adapter breakage due to provider SDK changes.

Acceptance criteria:
- Compatibility matrix in docs is enforced by automated tests.

---

## Implementation Order
1. Phase 1 (P0 correctness/reliability)
2. Phase 2 (P0/P1 privacy hardening)
3. Phase 3 (P1 analytics value)
4. Phase 4 (P1 release/operational hardening)

---

## Final Verification Protocol (Run Before Marking Done)

1. Reliability correctness
- `make test` plus new idempotency and shutdown-accounting tests.

2. Privacy guarantees
- Verify default mode emits no raw prompt/snippet fields.
- Validate redaction tests for optional snippet mode.

3. Value quality
- Run calibration fixtures for savings model and prompt extraction.

4. Operational readiness
- Run release/changelog flow in both git and git-less environments.

5. Full quality gates
- `make lint`
- `make typecheck`
- `make ci`

Only mark the phase complete when all acceptance criteria and verification checks pass.
