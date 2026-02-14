from __future__ import annotations

import jsonschema
import pytest
from llm_observer.config import ObserverConfig
from llm_observer.event_model import EventContext, build_event
from llm_observer.schema import validate_event


def test_event_validates_against_schema() -> None:
    config = ObserverConfig(
        enabled=False,
        api_key=None,
        endpoint=None,
        sampling_rate=1.0,
        privacy_mode="hash_only",
        redaction_mode="strict",
        snippets_enabled=False,
        queue_size=8,
        timeout_seconds=1.0,
        retry_budget=1,
        history_size=512,
        savings_factor=0.3,
        savings_min_similarity=0.15,
    )
    event = build_event(
        EventContext(
            provider="openai",
            model="gpt-4o-mini",
            prompt="hello",
            prompt_tokens=1,
            completion_tokens=1,
            latency_ms=1,
        ),
        config,
    )

    validate_event(event)


def test_schema_rejects_prohibited_raw_prompt_field() -> None:
    config = ObserverConfig(
        enabled=False,
        api_key=None,
        endpoint=None,
        sampling_rate=1.0,
        privacy_mode="hash_only",
        redaction_mode="strict",
        snippets_enabled=False,
        queue_size=8,
        timeout_seconds=1.0,
        retry_budget=1,
        history_size=512,
        savings_factor=0.3,
        savings_min_similarity=0.15,
    )
    event = build_event(
        EventContext(
            provider="openai",
            model="gpt-4o-mini",
            prompt="hello",
            prompt_tokens=1,
            completion_tokens=1,
            latency_ms=1,
        ),
        config,
    )
    event["raw_prompt"] = "not allowed"
    with pytest.raises(jsonschema.ValidationError):
        validate_event(event)
