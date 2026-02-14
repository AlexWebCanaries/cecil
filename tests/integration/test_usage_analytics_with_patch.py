from __future__ import annotations

import importlib
import json

import cecil
from cecil.config import ObserverConfig
from cecil.patcher import patch


def _config() -> ObserverConfig:
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
        retry_budget=1,
        history_size=512,
        savings_factor=0.3,
        savings_min_similarity=0.15,
    )


def test_usage_session_captures_openai_events(fake_openai_module) -> None:  # type: ignore[no-untyped-def]
    session = cecil.start_session(auto_patch=True, max_events=5)

    module = importlib.import_module("openai.resources.chat.completions")
    client = module.Completions()
    client.create(model="gpt-4o-mini", messages=[{"role": "user", "content": "hello"}])

    report = session.report_dict(usd_decimals=8)
    session.close()

    assert report["event_count"] == 1
    providers = report["providers"]
    assert isinstance(providers, dict)
    assert "openai" in providers
    openai_stats = providers["openai"]
    assert isinstance(openai_stats, dict)
    assert openai_stats["events"] == 1


def test_usage_session_captures_anthropic_with_manual_patch(
    fake_anthropic_module,
) -> None:  # type: ignore[no-untyped-def]
    session = cecil.start_session(auto_patch=False, max_events=5)
    patch(_config())

    module = importlib.import_module("anthropic.resources.messages")
    client = module.Messages()
    client.create(model="claude-3-5-haiku", messages=[{"role": "user", "content": "hello"}])

    report = session.report_dict()
    session.close()

    assert report["event_count"] == 1
    providers = report["providers"]
    assert isinstance(providers, dict)
    assert "anthropic" in providers


def test_usage_session_retention_and_json_save(fake_openai_module, tmp_path) -> None:  # type: ignore[no-untyped-def]
    session = cecil.start_session(auto_patch=True, max_events=2)

    module = importlib.import_module("openai.resources.chat.completions")
    client = module.Completions()
    client.create(model="gpt-4o-mini", messages=[{"role": "user", "content": "run1"}])
    client.create(model="gpt-4o-mini", messages=[{"role": "user", "content": "run2"}])
    client.create(model="gpt-4o-mini", messages=[{"role": "user", "content": "run3"}])

    report = session.report_dict()
    destination = tmp_path / "usage_report.json"
    saved_path = session.save_json(destination, usd_decimals=8)
    session.close()

    assert report["event_count"] == 3
    assert report["retained_event_count"] == 2
    assert saved_path == destination

    loaded = json.loads(destination.read_text())
    assert loaded["event_count"] == 3


def test_usage_session_print_table_has_money(fake_openai_module, capsys) -> None:  # type: ignore[no-untyped-def]
    session = cecil.start_session(auto_patch=True, max_events=5)

    module = importlib.import_module("openai.resources.chat.completions")
    client = module.Completions()
    client.create(model="gpt-4o-mini", messages=[{"role": "user", "content": "hello"}])

    session.print_report(usd_decimals=8)
    session.close()

    output = capsys.readouterr().out
    assert "Cecil Usage Analytics" in output
    assert "Estimated cost:" in output
    assert "$" in output


def test_usage_session_reports_cache_breakers_by_category(fake_openai_module) -> None:  # type: ignore[no-untyped-def]
    session = cecil.start_session(auto_patch=True, max_events=5)

    module = importlib.import_module("openai.resources.chat.completions")
    client = module.Completions()
    client.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": "system guidance request_id=ABCD1234EFGH5678 now=2026-01-01T00:00:00",
            }
        ],
    )

    report = session.report_dict()
    session.close()

    cache = report["cache"]
    assert isinstance(cache, dict)
    top_breakers = cache["top_cache_breakers"]
    assert isinstance(top_breakers, list)
    types = [item.get("type") for item in top_breakers if isinstance(item, dict)]
    assert "random_id" in types
    assert "timestamp" in types
