from __future__ import annotations

import os
from dataclasses import dataclass


def _read_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _read_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


@dataclass(frozen=True)
class ObserverConfig:
    enabled: bool
    api_key: str | None
    endpoint: str | None
    sampling_rate: float
    privacy_mode: str
    redaction_mode: str
    snippets_enabled: bool
    queue_size: int
    timeout_seconds: float
    retry_budget: int
    history_size: int
    savings_factor: float
    savings_min_similarity: float

    @property
    def local_only(self) -> bool:
        return not (self.enabled and self.api_key and self.endpoint)


def load_config() -> ObserverConfig:
    enabled = _read_bool("CECIL_ENABLED", False)
    api_key = os.getenv("CECIL_API_KEY")
    endpoint = os.getenv("CECIL_ENDPOINT")

    sampling_rate = max(0.0, min(1.0, _read_float("CECIL_SAMPLING_RATE", 1.0)))
    raw_privacy_mode = os.getenv("CECIL_PRIVACY_MODE", "hash_only").strip().lower()
    privacy_mode = raw_privacy_mode if raw_privacy_mode in {"hash_only"} else "hash_only"
    redaction_mode = os.getenv("CECIL_REDACTION_MODE", "strict")
    snippets_enabled = _read_bool("CECIL_SNIPPETS_ENABLED", False)

    queue_size_raw = os.getenv("CECIL_QUEUE_SIZE", "256")
    timeout_raw = os.getenv("CECIL_TIMEOUT_SECONDS", "2.0")
    retry_raw = os.getenv("CECIL_RETRY_BUDGET", "3")
    history_raw = os.getenv("CECIL_HISTORY_SIZE", "512")
    savings_factor_raw = os.getenv("CECIL_SAVINGS_FACTOR", "0.3")
    savings_min_similarity_raw = os.getenv("CECIL_SAVINGS_MIN_SIMILARITY", "0.15")

    try:
        queue_size = max(1, int(queue_size_raw))
    except ValueError:
        queue_size = 256
    try:
        timeout_seconds = max(0.1, float(timeout_raw))
    except ValueError:
        timeout_seconds = 2.0
    try:
        retry_budget = max(0, int(retry_raw))
    except ValueError:
        retry_budget = 3
    try:
        history_size = max(1, int(history_raw))
    except ValueError:
        history_size = 512
    try:
        savings_factor = max(0.0, min(1.0, float(savings_factor_raw)))
    except ValueError:
        savings_factor = 0.3
    try:
        savings_min_similarity = max(0.0, min(1.0, float(savings_min_similarity_raw)))
    except ValueError:
        savings_min_similarity = 0.15

    if not enabled:
        api_key = None
        endpoint = None
        snippets_enabled = False

    return ObserverConfig(
        enabled=enabled,
        api_key=api_key,
        endpoint=endpoint,
        sampling_rate=sampling_rate,
        privacy_mode=privacy_mode,
        redaction_mode=redaction_mode,
        snippets_enabled=snippets_enabled,
        queue_size=queue_size,
        timeout_seconds=timeout_seconds,
        retry_budget=retry_budget,
        history_size=history_size,
        savings_factor=savings_factor,
        savings_min_similarity=savings_min_similarity,
    )
