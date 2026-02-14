from __future__ import annotations

import sys
import types

from llm_observer.config import ObserverConfig
from llm_observer.patcher import patch


def _config() -> ObserverConfig:
    return ObserverConfig(
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
        history_size=128,
        savings_factor=0.3,
        savings_min_similarity=0.15,
    )


def _install_fake_openai() -> None:
    openai = types.ModuleType("openai")
    resources = types.ModuleType("openai.resources")
    chat = types.ModuleType("openai.resources.chat")
    completions = types.ModuleType("openai.resources.chat.completions")

    class Completions:
        def create(self, **kwargs: object) -> dict[str, object]:
            return {"usage": {"prompt_tokens": 1, "completion_tokens": 1}, "model": "gpt-4o-mini"}

    completions.Completions = Completions
    sys.modules["openai"] = openai
    sys.modules["openai.resources"] = resources
    sys.modules["openai.resources.chat"] = chat
    sys.modules["openai.resources.chat.completions"] = completions


def test_patch_truthful_when_no_providers() -> None:
    sys.modules.pop("openai.resources.chat.completions", None)
    sys.modules.pop("anthropic.resources.messages", None)

    first = patch(_config())
    second = patch(_config())

    assert first.openai_patched is False
    assert first.anthropic_patched is False
    assert second.openai_patched is False
    assert second.anthropic_patched is False


def test_patch_one_provider_available(fake_openai_module) -> None:  # type: ignore[no-untyped-def]
    result = patch(_config())
    assert result.openai_patched is True
    assert result.anthropic_patched is False


def test_patch_late_provider_availability(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    state = {"count": 0}

    def patch_openai_late(config, telemetry):  # type: ignore[no-untyped-def]
        state["count"] += 1
        return state["count"] >= 2

    monkeypatch.setattr("llm_observer.patcher.patch_openai", patch_openai_late)

    first = patch(_config())
    assert first.openai_patched is False

    second = patch(_config())
    assert second.openai_patched is True
