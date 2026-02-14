from __future__ import annotations

from llm_observer.cost import estimate_cost_usd, load_pricing_catalog
from llm_observer.savings import estimate_cache_savings


def test_pricing_catalog_is_versioned() -> None:
    catalog = load_pricing_catalog()
    assert catalog.version.startswith("pricing-")
    assert "gpt-4o-mini" in catalog.models


def test_cost_estimate_includes_source_metadata() -> None:
    estimate = estimate_cost_usd("gpt-4o-mini", prompt_tokens=1000, completion_tokens=1000)
    assert estimate.usd is not None
    assert estimate.label is None
    assert estimate.pricing_version.startswith("pricing-")
    assert "pricing_v1.json" in estimate.pricing_source


def test_savings_model_calibrated_outputs() -> None:
    savings = estimate_cache_savings(
        cost_estimate_usd=1.0,
        similarity=0.8,
        savings_factor=0.3,
        min_similarity=0.15,
    )
    assert savings.estimated_usd == 0.24
    assert savings.low_usd == 0.144
    assert savings.high_usd == 0.288
    assert 0.0 <= savings.confidence <= 1.0
