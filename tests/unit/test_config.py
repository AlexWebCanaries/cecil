from __future__ import annotations

from llm_observer.config import load_config


def test_config_defaults_local_only(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.delenv("LLM_OBSERVER_ENABLED", raising=False)
    monkeypatch.delenv("LLM_OBSERVER_API_KEY", raising=False)
    monkeypatch.delenv("LLM_OBSERVER_ENDPOINT", raising=False)

    config = load_config()

    assert config.enabled is False
    assert config.local_only is True
    assert config.api_key is None
    assert config.endpoint is None


def test_config_opt_in(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("LLM_OBSERVER_ENABLED", "true")
    monkeypatch.setenv("LLM_OBSERVER_API_KEY", "lok_x.y")
    monkeypatch.setenv("LLM_OBSERVER_ENDPOINT", "https://collector")

    config = load_config()

    assert config.enabled is True
    assert config.local_only is False


def test_explicit_disable_overrides_values(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("LLM_OBSERVER_ENABLED", "false")
    monkeypatch.setenv("LLM_OBSERVER_API_KEY", "lok_x.y")
    monkeypatch.setenv("LLM_OBSERVER_ENDPOINT", "https://collector")

    config = load_config()

    assert config.local_only is True
    assert config.api_key is None
    assert config.endpoint is None
