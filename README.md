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
Current instrumentation targets synchronous provider clients.

## Usage Analytics Report

```python
import cecil
from openai import OpenAI

session = cecil.start_session()
client = OpenAI()
client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Summarize this SDK in one sentence."}],
)

session.print_report(usd_decimals=8)
session.save_json("cecil_usage_report.json", usd_decimals=8)
session.close()
```

## Why Cecil

- Privacy-first defaults (hashed metadata, no raw prompt export by default)
- Fail-open instrumentation (SDK failures do not break provider calls)
- Actionable cost and cache opportunity analytics
- Lightweight integration (`import cecil; cecil.patch()`)

## Current Scope

- OpenAI sync path: `openai.resources.chat.completions.Completions.create`
- Anthropic sync path: `anthropic.resources.messages.Messages.create`
- Async provider clients are not instrumented in the current release.

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
