from __future__ import annotations

import time

from llm_observer.config import ObserverConfig
from llm_observer.event_model import EventContext, build_event, reset_history
from llm_observer.telemetry import TelemetryClient


def _config(local_only: bool = True) -> ObserverConfig:
    return ObserverConfig(
        enabled=not local_only,
        api_key=None if local_only else "lok_test.secret",
        endpoint=None if local_only else "http://127.0.0.1:1/unreachable",
        sampling_rate=1.0,
        privacy_mode="hash_only",
        redaction_mode="strict",
        snippets_enabled=False,
        queue_size=128,
        timeout_seconds=0.01,
        retry_budget=0,
        history_size=256,
        savings_factor=0.3,
        savings_min_similarity=0.15,
    )


def test_build_event_overhead_budget() -> None:
    reset_history()
    config = _config(local_only=True)

    start = time.perf_counter()
    for i in range(2000):
        build_event(
            EventContext(
                provider="openai",
                model="gpt-4o-mini",
                prompt=f"hello {i}",
                prompt_tokens=10,
                completion_tokens=5,
                latency_ms=20,
            ),
            config,
        )
    elapsed = time.perf_counter() - start
    avg_ms = (elapsed / 2000) * 1000

    # Budget target: event construction should stay below 1.5ms avg on CI/dev hardware.
    assert avg_ms < 1.5


def test_emit_backpressure_non_blocking() -> None:
    config = _config(local_only=False)
    client = TelemetryClient(config)

    start = time.perf_counter()
    for i in range(5000):
        client.emit({"n": i})
    elapsed = time.perf_counter() - start
    client.stop(timeout=0.2, drain=False)

    # put_nowait+drop strategy should avoid significant blocking under pressure.
    assert elapsed < 0.25
