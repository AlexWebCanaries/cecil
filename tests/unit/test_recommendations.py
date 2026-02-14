from __future__ import annotations

from llm_observer.recommendations import build_recommendation


def test_recommendation_surface_contains_actions() -> None:
    event = {
        "cache_breakers": [
            {"category": "uuid", "confidence": 0.99, "hint": "Remove UUID from prefix."},
            {"category": "timestamp", "confidence": 0.8, "hint": "Move timestamps to suffix."},
        ],
        "cache_savings": {"low_usd": 0.1, "high_usd": 0.4, "confidence": 0.88},
    }

    recommendation = build_recommendation(event)
    assert recommendation["confidence"] == 0.88
    assert recommendation["potential_savings_range_usd"]["high"] == 0.4
    assert len(recommendation["top_cache_breakers"]) == 2
    assert recommendation["suggested_actions"]
