from __future__ import annotations

from llm_observer.cost import estimate_cost_usd


def test_cost_estimate_known_model() -> None:
    estimate = estimate_cost_usd("gpt-4o-mini", prompt_tokens=1_000, completion_tokens=500)
    assert estimate.usd is not None
    assert estimate.usd > 0
    assert estimate.label is None


def test_cost_estimate_unknown_model_non_fatal() -> None:
    estimate = estimate_cost_usd("missing-model", prompt_tokens=100, completion_tokens=100)
    assert estimate.usd is None
    assert estimate.label == "unknown_model"
