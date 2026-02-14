from llm_observer.config import load_config
from llm_observer.event_model import EventContext, build_event

config = load_config()
event = build_event(
    EventContext(
        provider="openai",
        model="gpt-4o-mini",
        prompt="System instruction nonce=ABCD1234EFGH5678",
        prompt_tokens=120,
        completion_tokens=80,
        latency_ms=250,
    ),
    config,
)

print(event["recommendation"])
