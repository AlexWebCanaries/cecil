from __future__ import annotations

from cecil.cost import estimate_cost_usd


def test_cost_estimate_known_model() -> None:
    estimate = estimate_cost_usd("gpt-4o-mini", prompt_tokens=1_000, completion_tokens=500)
    assert estimate.usd is not None
    assert estimate.usd > 0
    assert estimate.label is None


def test_cost_estimate_unknown_model_non_fatal() -> None:
    estimate = estimate_cost_usd("missing-model", prompt_tokens=100, completion_tokens=100)
    assert estimate.usd is None
    assert estimate.label == "unknown_model"


def test_cost_estimate_anthropic_latest_alias_is_priced() -> None:
    estimate = estimate_cost_usd(
        "claude-3-5-haiku-latest", prompt_tokens=1_000, completion_tokens=1_000
    )
    assert estimate.usd is not None
    assert estimate.usd > 0
    assert estimate.label is None


def test_cost_estimate_gpt5_is_priced() -> None:
    estimate = estimate_cost_usd("gpt-5", prompt_tokens=1_000, completion_tokens=500)
    assert estimate.usd is not None
    assert estimate.usd > 0
    assert estimate.label is None
