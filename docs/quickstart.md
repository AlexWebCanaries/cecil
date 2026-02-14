# Quickstart (Local-only default)

1. Create a virtual environment and install:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

2. Patch provider SDKs:

```python
import cecil
cecil.patch()
```

Note: current SDK instrumentation targets synchronous provider client methods.

3. Run your existing OpenAI/Anthropic code. SDK failures are fail-open and do not block LLM calls.

4. Print and save local usage analytics:

```python
import cecil

session = cecil.start_session()

# run normal provider calls here

session.print_report(usd_decimals=8)
session.save_json("cecil_usage_report.json", usd_decimals=8)
session.close()
```

Expected first output time on a clean machine: under 5 minutes.
