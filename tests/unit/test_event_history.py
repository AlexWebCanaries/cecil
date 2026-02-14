from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from llm_observer.config import ObserverConfig
from llm_observer.event_model import EventContext, _history_for_size, build_event, reset_history


def _config(history_size: int) -> ObserverConfig:
    return ObserverConfig(
        enabled=False,
        api_key=None,
        endpoint=None,
        sampling_rate=1.0,
        privacy_mode="hash_only",
        redaction_mode="strict",
        snippets_enabled=False,
        queue_size=16,
        timeout_seconds=1.0,
        retry_budget=0,
        history_size=history_size,
        savings_factor=0.3,
        savings_min_similarity=0.15,
    )


def test_history_is_bounded() -> None:
    reset_history()
    config = _config(history_size=5)
    for i in range(50):
        build_event(
            EventContext(
                provider="openai",
                model=f"model-{i}",
                prompt="hello",
                prompt_tokens=1,
                completion_tokens=1,
                latency_ms=1,
            ),
            config,
        )

    assert _history_for_size(5).size() <= 5


def test_history_thread_safe_under_concurrency() -> None:
    reset_history()
    config = _config(history_size=10)

    def work(i: int) -> float:
        event = build_event(
            EventContext(
                provider="openai",
                model=f"model-{i % 12}",
                prompt=f"content {i}",
                prompt_tokens=1,
                completion_tokens=1,
                latency_ms=1,
            ),
            config,
        )
        return float(event["prefix_similarity"])

    with ThreadPoolExecutor(max_workers=8) as pool:
        scores = list(pool.map(work, range(200)))

    assert len(scores) == 200
    assert all(0.0 <= s <= 1.0 for s in scores)
    assert _history_for_size(10).size() <= 10
