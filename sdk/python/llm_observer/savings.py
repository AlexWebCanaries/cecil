from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SavingsEstimate:
    estimated_usd: float
    low_usd: float
    high_usd: float
    confidence: float


def estimate_cache_savings(
    cost_estimate_usd: float | None,
    similarity: float,
    savings_factor: float,
    min_similarity: float,
) -> SavingsEstimate:
    if cost_estimate_usd is None or similarity < min_similarity:
        return SavingsEstimate(estimated_usd=0.0, low_usd=0.0, high_usd=0.0, confidence=0.0)

    effective_similarity = max(0.0, min(1.0, similarity))
    factor = max(0.0, min(1.0, savings_factor))
    estimated = round(cost_estimate_usd * effective_similarity * factor, 10)

    # Range is intentionally conservative because this model is heuristic.
    low = round(estimated * 0.6, 10)
    high = round(estimated * 1.2, 10)
    confidence = round(min(1.0, 0.2 + effective_similarity * 0.7), 4)
    return SavingsEstimate(
        estimated_usd=estimated, low_usd=low, high_usd=high, confidence=confidence
    )
