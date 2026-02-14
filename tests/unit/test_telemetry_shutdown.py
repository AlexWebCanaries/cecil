from __future__ import annotations

import time

from cecil.config import ObserverConfig
from cecil.telemetry import TelemetryClient


def _config(queue_size: int = 64) -> ObserverConfig:
    return ObserverConfig(
        enabled=True,
        api_key="lok_test.secret",
        endpoint="http://127.0.0.1:1/unreachable",
        sampling_rate=1.0,
        privacy_mode="hash_only",
        redaction_mode="strict",
        snippets_enabled=False,
        queue_size=queue_size,
        timeout_seconds=0.01,
        retry_budget=0,
        history_size=64,
        savings_factor=0.3,
        savings_min_similarity=0.15,
    )


def test_immediate_shutdown_accounts_abandoned(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(
        "cecil.telemetry.TelemetryClient._send_once", lambda self, event: False
    )
    client = TelemetryClient(_config(queue_size=200))

    attempts = 100
    for i in range(attempts):
        client.emit({"n": i})

    client.stop(timeout=0.01, drain=False)

    total = (
        client.counters.sent
        + client.counters.failures
        + client.counters.dropped
        + client.counters.abandoned_on_shutdown
    )
    assert total == attempts


def test_bounded_drain_timeout(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    def slow_send(self, event):  # type: ignore[no-untyped-def]
        time.sleep(0.02)
        return True

    monkeypatch.setattr("cecil.telemetry.TelemetryClient._send_once", slow_send)
    client = TelemetryClient(_config(queue_size=100))

    attempts = 40
    for i in range(attempts):
        client.emit({"n": i})

    client.stop(timeout=0.05, drain=True)

    total = (
        client.counters.sent
        + client.counters.failures
        + client.counters.dropped
        + client.counters.abandoned_on_shutdown
    )
    assert total == attempts
    assert client.counters.abandoned_on_shutdown >= 1


def test_large_queue_accounting(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(
        "cecil.telemetry.TelemetryClient._send_once", lambda self, event: True
    )
    client = TelemetryClient(_config(queue_size=1000))

    attempts = 500
    for i in range(attempts):
        client.emit({"n": i})

    client.stop(timeout=2.0, drain=True)
    total = (
        client.counters.sent
        + client.counters.failures
        + client.counters.dropped
        + client.counters.abandoned_on_shutdown
    )
    assert total == attempts
