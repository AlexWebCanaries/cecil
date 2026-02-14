import os

import cecil

os.environ.setdefault("CECIL_ENABLED", "true")
os.environ.setdefault("CECIL_API_KEY", "lok_example.secret")
os.environ.setdefault("CECIL_ENDPOINT", "https://collector.example/v1/events")

cecil.patch()
print("cecil-sdk patched with telemetry opt-in")
