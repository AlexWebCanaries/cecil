from __future__ import annotations

from typing import Any


def build_recommendation(event: dict[str, Any]) -> dict[str, Any]:
    breakers = event.get("cache_breakers", [])
    if not isinstance(breakers, list):
        breakers = []

    top_breakers: list[dict[str, Any]] = []
    for item in breakers:
        if isinstance(item, dict):
            top_breakers.append(
                {
                    "category": item.get("category", "unknown"),
                    "confidence": item.get("confidence", 0.0),
                    "hint": item.get("hint", ""),
                }
            )
    top_breakers = sorted(
        top_breakers, key=lambda x: float(x.get("confidence", 0.0)), reverse=True
    )[:3]

    savings = event.get("cache_savings", {})
    if not isinstance(savings, dict):
        savings = {}

    return {
        "top_cache_breakers": top_breakers,
        "potential_savings_range_usd": {
            "low": float(savings.get("low_usd", 0.0)),
            "high": float(savings.get("high_usd", 0.0)),
        },
        "confidence": float(savings.get("confidence", 0.0)),
        "suggested_actions": [b.get("hint", "") for b in top_breakers if b.get("hint")],
    }
