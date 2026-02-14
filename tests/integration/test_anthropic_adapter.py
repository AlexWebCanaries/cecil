from __future__ import annotations

import importlib

from cecil.config import ObserverConfig
from cecil.patcher import patch


def test_anthropic_adapter_emits_event(fake_anthropic_module, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    captured: list[dict[str, object]] = []

    def capture_emit(self, event: dict[str, object]) -> None:  # type: ignore[no-untyped-def]
        captured.append(event)

    monkeypatch.setattr("cecil.telemetry.TelemetryClient.emit", capture_emit)

    config = ObserverConfig(
        enabled=False,
        api_key=None,
        endpoint=None,
        sampling_rate=1.0,
        privacy_mode="hash_only",
        redaction_mode="strict",
        snippets_enabled=False,
        queue_size=16,
        timeout_seconds=1.0,
        retry_budget=1,
        history_size=512,
        savings_factor=0.3,
        savings_min_similarity=0.15,
    )

    result = patch(config)
    assert result.anthropic_patched is True

    module = importlib.import_module("anthropic.resources.messages")
    client = module.Messages()
    response = client.create(
        model="claude-3-5-haiku", messages=[{"role": "user", "content": "hello"}]
    )

    assert response.model == "claude-3-5-haiku"
    assert len(captured) == 1
    assert captured[0]["provider"] == "anthropic"
