from __future__ import annotations

import time

from llm_observer.config import ObserverConfig
from llm_observer.telemetry import TelemetryClient


def test_endpoint_down_respects_retry_budget() -> None:
    config = ObserverConfig(
        enabled=True,
        api_key="lok_test.secret",
        endpoint="http://127.0.0.1:1/unreachable",
        sampling_rate=1.0,
        privacy_mode="hash_only",
        redaction_mode="strict",
        snippets_enabled=False,
        queue_size=4,
        timeout_seconds=0.01,
        retry_budget=2,
        history_size=512,
        savings_factor=0.3,
        savings_min_similarity=0.15,
    )

    client = TelemetryClient(config)
    client.emit({"schema_version": "v1", "provider": "openai"})
    time.sleep(0.7)
    client.stop()

    assert client.counters.failures >= 1
    assert client.counters.sent == 0
