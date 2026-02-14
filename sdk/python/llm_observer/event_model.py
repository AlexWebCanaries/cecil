from __future__ import annotations

import threading
import time
import uuid
from collections import OrderedDict
from dataclasses import asdict, dataclass

from llm_observer.cache_analysis import detect_cache_breakers, prefix_similarity_score
from llm_observer.canonicalize import canonicalize_prompt
from llm_observer.config import ObserverConfig
from llm_observer.cost import estimate_cost_usd
from llm_observer.privacy import hash_prefix_blocks, redact_snippet
from llm_observer.recommendations import build_recommendation
from llm_observer.savings import estimate_cache_savings


@dataclass
class EventContext:
    provider: str
    model: str
    prompt: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: int
    cache_control_position: int | None = None


class PrefixHistory:
    def __init__(self, max_models: int = 512) -> None:
        self._max_models = max(1, max_models)
        self._by_model: OrderedDict[str, str] = OrderedDict()
        self._lock = threading.Lock()

    def similarity(self, model: str, canonical_prompt: str) -> float:
        with self._lock:
            previous = self._by_model.get(model, "")
            if model in self._by_model:
                self._by_model.pop(model)
            self._by_model[model] = canonical_prompt
            if len(self._by_model) > self._max_models:
                self._by_model.popitem(last=False)
        return prefix_similarity_score(previous, canonical_prompt)

    def size(self) -> int:
        with self._lock:
            return len(self._by_model)


_HISTORY_BY_SIZE: dict[int, PrefixHistory] = {}
_HISTORY_LOCK = threading.Lock()


def _history_for_size(history_size: int) -> PrefixHistory:
    normalized = max(1, history_size)
    with _HISTORY_LOCK:
        history = _HISTORY_BY_SIZE.get(normalized)
        if history is None:
            history = PrefixHistory(max_models=normalized)
            _HISTORY_BY_SIZE[normalized] = history
    return history


def reset_history() -> None:
    with _HISTORY_LOCK:
        _HISTORY_BY_SIZE.clear()


def build_event(context: EventContext, config: ObserverConfig) -> dict[str, object]:
    canonical_prompt = canonicalize_prompt(context.prompt)
    similarity = _history_for_size(config.history_size).similarity(context.model, canonical_prompt)
    breakers = detect_cache_breakers(context.prompt)

    cost = estimate_cost_usd(
        context.model,
        prompt_tokens=context.prompt_tokens,
        completion_tokens=context.completion_tokens,
    )
    savings = estimate_cache_savings(
        cost_estimate_usd=cost.usd,
        similarity=similarity,
        savings_factor=config.savings_factor,
        min_similarity=config.savings_min_similarity,
    )

    payload: dict[str, object] = {
        "schema_version": "v1",
        "event_id": str(uuid.uuid4()),
        "timestamp_ms": int(time.time() * 1000),
        "provider": context.provider,
        "model": context.model,
        "token_counts": {
            "prompt": context.prompt_tokens,
            "completion": context.completion_tokens,
            "total": context.prompt_tokens + context.completion_tokens,
        },
        "latency_ms": context.latency_ms,
        "cost_estimate_usd": cost.usd,
        "cost_label": cost.label,
        "pricing": {
            "version": cost.pricing_version,
            "source": cost.pricing_source,
        },
        "prefix_hash_blocks": hash_prefix_blocks(canonical_prompt),
        "prefix_similarity": similarity,
        "cache_savings_estimate_usd": savings.estimated_usd,
        "cache_savings": asdict(savings),
        "cache_breakers": [asdict(f) for f in breakers],
        "cache_boundary": {
            "present": context.cache_control_position is not None,
            "position": context.cache_control_position,
        },
        "privacy": {
            "mode": config.privacy_mode,
            "redaction_mode": config.redaction_mode,
            "snippet": redact_snippet(
                context.prompt,
                mode=config.redaction_mode,
                snippets_enabled=config.snippets_enabled,
            ),
        },
    }
    payload["recommendation"] = build_recommendation(payload)
    return payload
