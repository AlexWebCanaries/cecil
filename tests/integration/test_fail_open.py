from __future__ import annotations

import importlib

from cecil.config import ObserverConfig
from cecil.patcher import patch


def test_provider_call_survives_analyzer_failure(fake_openai_module, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    def boom(*args: object, **kwargs: object) -> dict[str, object]:
        raise RuntimeError("boom")

    monkeypatch.setattr("cecil.adapters.openai_adapter.build_event", boom)

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
        retry_budget=0,
        history_size=512,
        savings_factor=0.3,
        savings_min_similarity=0.15,
    )

    patch(config)
    module = importlib.import_module("openai.resources.chat.completions")
    client = module.Completions()

    response = client.create(
        model="gpt-4o-mini", messages=[{"role": "user", "content": "still works"}]
    )
    assert response.model == "gpt-4o-mini"


def test_provider_call_survives_sender_failure(fake_anthropic_module, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    def emit_fail(self, event: dict[str, object]) -> None:  # type: ignore[no-untyped-def]
        raise RuntimeError("send fail")

    monkeypatch.setattr("cecil.telemetry.TelemetryClient.emit", emit_fail)

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
        retry_budget=0,
        history_size=512,
        savings_factor=0.3,
        savings_min_similarity=0.15,
    )

    patch(config)
    module = importlib.import_module("anthropic.resources.messages")
    client = module.Messages()

    response = client.create(
        model="claude-3-5-haiku", messages=[{"role": "user", "content": "still works"}]
    )
    assert response.model == "claude-3-5-haiku"
