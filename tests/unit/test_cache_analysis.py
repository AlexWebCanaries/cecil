from __future__ import annotations

from cecil.cache_analysis import detect_cache_breakers, prefix_similarity_score


def test_prefix_similarity_stable_for_equivalent_noise() -> None:
    baseline = "system policy: return JSON only"
    equivalent = "system policy: return JSON only\\n"
    assert prefix_similarity_score(baseline, equivalent.strip()) == 1.0


def test_detects_breaker_classes() -> None:
    prompt = (
        "now=2025-01-01T00:00:00 request_id=ABCD1234EFGH5678 "
        "uuid=550e8400-e29b-41d4-a716-446655440000"
    )
    findings = detect_cache_breakers(prompt)
    categories = {f.category for f in findings}
    assert "timestamp" in categories
    assert "uuid" in categories
    assert "random_id" in categories
