# Local Recommendations API

Each event includes `recommendation` with:
- `top_cache_breakers`
- `potential_savings_range_usd`
- `confidence`
- `suggested_actions`

Usage:

```python
from cecil.event_model import EventContext, build_event
from cecil.config import load_config

event = build_event(
    EventContext(
        provider="openai",
        model="gpt-4o-mini",
        prompt="...",
        prompt_tokens=120,
        completion_tokens=90,
        latency_ms=350,
    ),
    load_config(),
)
print(event["recommendation"])
```
