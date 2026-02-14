from __future__ import annotations

import os
from importlib.metadata import version as pkg_version

import pytest
from cecil.adapters.common import extract_token_counts
from cecil.config import ObserverConfig
from cecil.cost import estimate_cost_usd
from cecil.patcher import patch

RUN_LIVE = os.getenv("CECIL_RUN_LIVE_OPENAI") == "1"
LIVE_CONFIRM = (
    os.getenv("CECIL_LIVE_TEST_CONFIRM") == "I_UNDERSTAND_AND_ACCEPT_LIVE_API_RISK"
)
pytestmark = pytest.mark.skipif(
    not RUN_LIVE,
    reason="Live OpenAI API tests are opt-in. Set CECIL_RUN_LIVE_OPENAI=1 to run.",
)


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _looks_placeholder_key(api_key: str) -> bool:
    lowered = api_key.strip().lower()
    if len(lowered) < 20:
        return True
    markers = ("placeholder", "your_key", "example", "changeme", "dummy", "test")
    if any(m in lowered for m in markers):
        return True
    return lowered.startswith("sk-test")


@pytest.fixture
def live_openai_settings() -> dict[str, object]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY is required for live OpenAI tests")
    if not LIVE_CONFIRM:
        pytest.skip(
            "Set CECIL_LIVE_TEST_CONFIRM="
            "I_UNDERSTAND_AND_ACCEPT_LIVE_API_RISK to run live tests."
        )
    if _looks_placeholder_key(api_key):
        pytest.skip(
            "OPENAI_API_KEY appears to be placeholder/test key; refusing to run live API tests."
        )
    try:
        installed_httpx = pkg_version("httpx")
    except Exception:  # pragma: no cover
        pytest.skip("httpx is not installed. Run: pip install -e '.[live_openai]'")
    if installed_httpx != "0.27.2":
        pytest.skip(
            f"httpx==0.27.2 required for pinned live tests (found {installed_httpx}). "
            "Run: pip install -e '.[live_openai]'"
        )

    model = os.getenv("OPENAI_LIVE_TEST_MODEL", "gpt-4o-mini")
    max_tokens = max(1, _env_int("OPENAI_LIVE_TEST_MAX_TOKENS", 24))
    max_case_usd = max(0.0, _env_float("OPENAI_LIVE_TEST_MAX_CASE_USD", 0.01))
    max_total_usd = max(0.0, _env_float("OPENAI_LIVE_TEST_MAX_TOTAL_USD", 0.03))
    return {
        "api_key": api_key,
        "model": model,
        "max_tokens": max_tokens,
        "max_case_usd": max_case_usd,
        "max_total_usd": max_total_usd,
    }


@pytest.fixture
def budget_tracker() -> dict[str, float]:
    return {"total_usd": 0.0}


def _assert_within_budget(
    *,
    model: str,
    response: object,
    per_case_limit: float,
    total_limit: float,
    tracker: dict[str, float],
) -> float:
    prompt_tokens, completion_tokens = extract_token_counts(response)
    estimate = estimate_cost_usd(
        model=model,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
    )
    assert estimate.label is None, (
        f"Model {model!r} missing from pricing catalog; set OPENAI_LIVE_TEST_MODEL "
        "to a priced model before running live spend-capped tests."
    )
    assert estimate.usd is not None
    assert estimate.usd <= per_case_limit, (
        f"Estimated per-test cost ${estimate.usd:.6f} exceeded cap ${per_case_limit:.6f}"
    )
    tracker["total_usd"] += estimate.usd
    assert tracker["total_usd"] <= total_limit, (
        f"Estimated total live-test cost ${tracker['total_usd']:.6f} exceeded "
        f"cap ${total_limit:.6f}"
    )
    return estimate.usd


def _patch_and_capture(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, object]]:
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
    assert result.openai_patched is True
    return captured


def test_live_openai_chat_completion_emits_expected_event(
    monkeypatch: pytest.MonkeyPatch,
    live_openai_settings: dict[str, object],
    budget_tracker: dict[str, float],
) -> None:
    openai = pytest.importorskip("openai")
    captured = _patch_and_capture(monkeypatch)

    client = openai.OpenAI(api_key=live_openai_settings["api_key"])
    response = client.chat.completions.create(
        model=live_openai_settings["model"],
        messages=[{"role": "user", "content": "Reply with exactly: OK"}],
        max_tokens=live_openai_settings["max_tokens"],
        temperature=0,
    )

    text = response.choices[0].message.content
    assert isinstance(text, str)
    assert text.strip() != ""

    _assert_within_budget(
        model=live_openai_settings["model"],
        response=response,
        per_case_limit=float(live_openai_settings["max_case_usd"]),
        total_limit=float(live_openai_settings["max_total_usd"]),
        tracker=budget_tracker,
    )

    assert len(captured) == 1
    event = captured[0]
    assert event["provider"] == "openai"
    assert event["model"] == live_openai_settings["model"]
    assert "raw_prompt" not in event
    assert event["privacy"]["mode"] == "hash_only"


def test_live_openai_prefix_similarity_moves_up_for_related_prompt(
    monkeypatch: pytest.MonkeyPatch,
    live_openai_settings: dict[str, object],
    budget_tracker: dict[str, float],
) -> None:
    openai = pytest.importorskip("openai")
    captured = _patch_and_capture(monkeypatch)

    client = openai.OpenAI(api_key=live_openai_settings["api_key"])
    common = "Project note: latency budget is 200ms."
    prompts = [
        f"{common} Return exactly: ALPHA",
        f"{common} Return exactly: BETA",
    ]

    for prompt in prompts:
        response = client.chat.completions.create(
            model=live_openai_settings["model"],
            messages=[{"role": "user", "content": prompt}],
            max_tokens=live_openai_settings["max_tokens"],
            temperature=0,
        )
        _assert_within_budget(
            model=live_openai_settings["model"],
            response=response,
            per_case_limit=float(live_openai_settings["max_case_usd"]),
            total_limit=float(live_openai_settings["max_total_usd"]),
            tracker=budget_tracker,
        )

    assert len(captured) == 2
    first_similarity = float(captured[0]["prefix_similarity"])
    second_similarity = float(captured[1]["prefix_similarity"])
    assert first_similarity == pytest.approx(0.0)
    assert second_similarity > 0.0
