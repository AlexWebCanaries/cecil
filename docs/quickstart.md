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

3. Run your existing OpenAI/Anthropic code. SDK failures are fail-open and do not block LLM calls.

Expected first output time on a clean machine: under 5 minutes.
