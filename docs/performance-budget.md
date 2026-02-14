# Performance Budget

Target budgets enforced by tests:
- Average `build_event` overhead < 1.5 ms/event for local analysis benchmark workload.
- Telemetry `emit` remains non-blocking under queue pressure via drop strategy.

Scope notes:
- These are guardrail tests for regressions, not full production benchmarks.
- For production sizing, run dedicated perf jobs with representative workloads.
