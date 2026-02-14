# llm-observer

Privacy-first Python SDK for local LLM cost and cache analysis with optional telemetry export.

## Install

```bash
pip install llm-observer
```

## Quickstart

```python
import llm_observer

llm_observer.patch()
```

By default, SDK runs in local-only mode and does not send telemetry.

## Quality gates

```bash
pip install -e '.[dev]'
make lint
make typecheck
make test
make build
```

## Documentation

- `docs/quickstart.md`
- `docs/telemetry-opt-in.md`
- `docs/troubleshooting.md`
- `docs/compatibility-matrix.md`
- `docs/security-checklist.md`
- `docs/release-checklist.md`
- `docs/privacy-contract.md`
- `docs/pricing-policy.md`
- `docs/recommendations.md`
- `docs/performance-budget.md`
- `docs/savings-model.md`
