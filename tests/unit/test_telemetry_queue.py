from __future__ import annotations

from cecil.config import ObserverConfig
from cecil.telemetry import TelemetryClient


def test_queue_overflow_drops_events() -> None:
    config = ObserverConfig(
        enabled=True,
        api_key="lok_k.s",
        endpoint="http://127.0.0.1:1/never",
        sampling_rate=1.0,
        privacy_mode="hash_only",
        redaction_mode="strict",
        snippets_enabled=False,
        queue_size=1,
        timeout_seconds=0.01,
        retry_budget=0,
        history_size=512,
        savings_factor=0.3,
        savings_min_similarity=0.15,
    )
    client = TelemetryClient(config)
    for i in range(40):
        client.emit({"n": i})
    client.stop()
    assert client.counters.dropped > 0
