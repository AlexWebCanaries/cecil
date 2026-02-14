# Live OpenAI Integration Tests

These tests are opt-in and make real API calls.

## Install dependencies

```bash
pip install -e '.[live_openai]'
```

## Safety requirements
- Use an ephemeral key only.
- Rotate/revoke the key immediately after test run.
- Never use production long-lived keys.

## Required env vars

```bash
export LLM_OBSERVER_RUN_LIVE_OPENAI=1
export LLM_OBSERVER_LIVE_TEST_CONFIRM=I_UNDERSTAND_AND_ACCEPT_LIVE_API_RISK
export OPENAI_API_KEY='sk-...'
```

Optional caps:

```bash
export OPENAI_LIVE_TEST_MODEL='gpt-4o-mini'
export OPENAI_LIVE_TEST_MAX_TOKENS=24
export OPENAI_LIVE_TEST_MAX_CASE_USD=0.01
export OPENAI_LIVE_TEST_MAX_TOTAL_USD=0.03
```

## Run

```bash
pytest -q tests/integration/test_openai_live_api.py
```
