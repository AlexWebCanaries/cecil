from __future__ import annotations

from llm_observer.config import load_config
from llm_observer.privacy import redact_snippet


def test_invalid_privacy_mode_falls_back(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("LLM_OBSERVER_PRIVACY_MODE", "unsafe_mode")
    config = load_config()
    assert config.privacy_mode == "hash_only"


def test_snippet_requires_secondary_opt_in() -> None:
    snippet = redact_snippet(
        "email test@example.com phone 415-555-1111 secret token",
        mode="redacted_snippets",
        snippets_enabled=False,
    )
    assert snippet is None


def test_snippet_redacts_sensitive_patterns() -> None:
    snippet = redact_snippet(
        "contact me at test@example.com or +1 (415) 555-1111 id 123456789123 secret=abc",
        mode="redacted_snippets",
        snippets_enabled=True,
    )
    assert snippet is not None
    assert "test@example.com" not in snippet
    assert "555-1111" not in snippet
    assert "123456789123" not in snippet
    assert "[REDACTED]" in snippet
