# Cecil Python SDK

`cecil-sdk` is a privacy-first Python SDK for LLM cost visibility and cache optimization insights.

## Install

```bash
pip install cecil-sdk
```

## Quickstart

```python
import cecil

cecil.patch()
```

Default behavior is local-only. No telemetry is sent unless explicitly enabled.

## Why Cecil

- Privacy-first defaults (hashed metadata, no raw prompt export by default)
- Fail-open instrumentation (SDK failures do not break provider calls)
- Actionable cost and cache opportunity analytics
- Lightweight integration (`import cecil; cecil.patch()`)

## Development

```bash
pip install -e ".[dev]"
make lint
make typecheck
make test
make build
python -m twine check dist/*
python scripts/smoke_check_wheel.py
```

## Documentation

- `docs/quickstart.md`
- `docs/telemetry-opt-in.md`
- `docs/privacy-contract.md`
- `docs/recommendations.md`
- `docs/release-checklist.md`

## License

MIT. See `LICENSE`.
