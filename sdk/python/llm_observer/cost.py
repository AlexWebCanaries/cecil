from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from importlib import resources
from pathlib import Path


@dataclass(frozen=True)
class Pricing:
    input_per_million: float
    output_per_million: float


@dataclass(frozen=True)
class PricingCatalog:
    version: str
    updated_at: str
    source: str
    models: dict[str, Pricing]


@dataclass(frozen=True)
class CostEstimate:
    usd: float | None
    label: str | None
    pricing_version: str
    pricing_source: str


def _pricing_path() -> Path:
    with resources.as_file(resources.files("llm_observer.data") / "pricing_v1.json") as p:
        return p


@lru_cache(maxsize=1)
def load_pricing_catalog() -> PricingCatalog:
    path = _pricing_path()
    data = json.loads(path.read_text())
    models_raw = data.get("models", {})

    models: dict[str, Pricing] = {}
    if isinstance(models_raw, dict):
        for model, item in models_raw.items():
            if not isinstance(model, str) or not isinstance(item, dict):
                continue
            input_cost = item.get("input_per_million")
            output_cost = item.get("output_per_million")
            if not isinstance(input_cost, (int, float)) or not isinstance(
                output_cost, (int, float)
            ):
                continue
            models[model] = Pricing(
                input_per_million=float(input_cost), output_per_million=float(output_cost)
            )

    version = data.get("version", "pricing-unknown")
    updated_at = data.get("updated_at", "unknown")
    return PricingCatalog(
        version=str(version),
        updated_at=str(updated_at),
        source=str(path),
        models=models,
    )


def estimate_cost_usd(model: str, prompt_tokens: int, completion_tokens: int) -> CostEstimate:
    catalog = load_pricing_catalog()
    pricing = catalog.models.get(model)
    if pricing is None:
        return CostEstimate(
            usd=None,
            label="unknown_model",
            pricing_version=catalog.version,
            pricing_source=catalog.source,
        )

    input_cost = (prompt_tokens / 1_000_000) * pricing.input_per_million
    output_cost = (completion_tokens / 1_000_000) * pricing.output_per_million
    return CostEstimate(
        usd=round(input_cost + output_cost, 10),
        label=None,
        pricing_version=catalog.version,
        pricing_source=catalog.source,
    )
