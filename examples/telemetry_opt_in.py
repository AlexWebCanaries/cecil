import os

import llm_observer

os.environ.setdefault("LLM_OBSERVER_ENABLED", "true")
os.environ.setdefault("LLM_OBSERVER_API_KEY", "lok_example.secret")
os.environ.setdefault("LLM_OBSERVER_ENDPOINT", "https://collector.example/v1/events")

llm_observer.patch()
print("llm-observer patched with telemetry opt-in")
