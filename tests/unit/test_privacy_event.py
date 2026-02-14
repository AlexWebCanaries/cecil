from __future__ import annotations

from cecil.config import ObserverConfig
from cecil.event_model import EventContext, build_event


def _config(redaction_mode: str = "strict", snippets_enabled: bool = False) -> ObserverConfig:
    return ObserverConfig(
        enabled=False,
        api_key=None,
        endpoint=None,
        sampling_rate=1.0,
        privacy_mode="hash_only",
        redaction_mode=redaction_mode,
        snippets_enabled=snippets_enabled,
        queue_size=8,
        timeout_seconds=1.0,
        retry_budget=1,
        history_size=512,
        savings_factor=0.3,
        savings_min_similarity=0.15,
    )


def test_default_event_has_no_raw_prompt() -> None:
    event = build_event(
        EventContext(
            provider="openai",
            model="gpt-4o-mini",
            prompt="my secret content",
            prompt_tokens=20,
            completion_tokens=10,
            latency_ms=12,
        ),
        _config(),
    )

    assert "prompt" not in event
    assert event["privacy"] == {
        "mode": "hash_only",
        "redaction_mode": "strict",
        "snippet": None,
    }


def test_opt_in_redacted_snippet() -> None:
    event = build_event(
        EventContext(
            provider="openai",
            model="gpt-4o-mini",
            prompt="authorization bearer secret=abcd",
            prompt_tokens=10,
            completion_tokens=10,
            latency_ms=10,
        ),
        _config(redaction_mode="redacted_snippets"),
    )

    privacy = event["privacy"]
    assert isinstance(privacy, dict)
    assert privacy["snippet"] is None


def test_opt_in_redacted_snippet_with_secondary_flag() -> None:
    event = build_event(
        EventContext(
            provider="openai",
            model="gpt-4o-mini",
            prompt="authorization bearer email test@example.com",
            prompt_tokens=10,
            completion_tokens=10,
            latency_ms=10,
        ),
        _config(redaction_mode="redacted_snippets", snippets_enabled=True),
    )

    privacy = event["privacy"]
    assert isinstance(privacy, dict)
    assert "[REDACTED]" in str(privacy["snippet"])
