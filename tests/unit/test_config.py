from __future__ import annotations

from cecil.config import load_config


def test_config_defaults_local_only(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.delenv("CECIL_ENABLED", raising=False)
    monkeypatch.delenv("CECIL_API_KEY", raising=False)
    monkeypatch.delenv("CECIL_ENDPOINT", raising=False)

    config = load_config()

    assert config.enabled is False
    assert config.local_only is True
    assert config.api_key is None
    assert config.endpoint is None


def test_config_opt_in(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("CECIL_ENABLED", "true")
    monkeypatch.setenv("CECIL_API_KEY", "lok_x.y")
    monkeypatch.setenv("CECIL_ENDPOINT", "https://collector")

    config = load_config()

    assert config.enabled is True
    assert config.local_only is False


def test_explicit_disable_overrides_values(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("CECIL_ENABLED", "false")
    monkeypatch.setenv("CECIL_API_KEY", "lok_x.y")
    monkeypatch.setenv("CECIL_ENDPOINT", "https://collector")

    config = load_config()

    assert config.local_only is True
    assert config.api_key is None
    assert config.endpoint is None
