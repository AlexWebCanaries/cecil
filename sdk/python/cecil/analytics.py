from __future__ import annotations

import json
import threading
from collections import Counter, deque
from dataclasses import dataclass
from pathlib import Path

from cecil.patcher import patch, register_event_listener, unregister_event_listener


@dataclass
class _Aggregate:
    events: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost_usd: float = 0.0
    savings_estimated_usd: float = 0.0
    savings_low_usd: float = 0.0
    savings_high_usd: float = 0.0

    def as_dict(self, usd_decimals: int) -> dict[str, object]:
        return {
            "events": self.events,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "cost_usd": round(self.cost_usd, usd_decimals),
            "savings_estimated_usd": round(self.savings_estimated_usd, usd_decimals),
            "savings_low_usd": round(self.savings_low_usd, usd_decimals),
            "savings_high_usd": round(self.savings_high_usd, usd_decimals),
        }


@dataclass(frozen=True)
class UsageReportOptions:
    usd_decimals: int = 8
    top_breakers_limit: int = 5


@dataclass(frozen=True)
class UsageReport:
    data: dict[str, object]


class UsageSession:
    def __init__(self, max_events: int = 2000) -> None:
        self._lock = threading.Lock()
        self._max_events = max(1, max_events)
        self._events: deque[dict[str, object]] = deque(maxlen=self._max_events)

        self._total = _Aggregate()
        self._providers: dict[str, _Aggregate] = {}
        self._models: dict[str, _Aggregate] = {}

        self._breaker_counts: Counter[str] = Counter()
        self._prefix_similarity_sum = 0.0
        self._boundary_present_count = 0
        self._unknown_model_count = 0
        self._priced_event_count = 0
        self._pricing_versions_seen: set[str] = set()

        self._listener_id = register_event_listener(self._on_event)
        self._closed = False

    def close(self) -> None:
        with self._lock:
            if self._closed:
                return
            self._closed = True
            listener_id = self._listener_id
        unregister_event_listener(listener_id)

    def _on_event(self, event: dict[str, object]) -> None:
        with self._lock:
            if self._closed:
                return

            self._events.append(event)
            self._total.events += 1

            provider = event.get("provider")
            provider_key = provider if isinstance(provider, str) and provider else "unknown"
            provider_agg = self._providers.setdefault(provider_key, _Aggregate())
            provider_agg.events += 1

            model = event.get("model")
            model_key = model if isinstance(model, str) and model else "unknown"
            model_agg = self._models.setdefault(model_key, _Aggregate())
            model_agg.events += 1

            token_counts = event.get("token_counts")
            prompt_tokens = 0
            completion_tokens = 0
            if isinstance(token_counts, dict):
                prompt_raw = token_counts.get("prompt")
                completion_raw = token_counts.get("completion")
                if isinstance(prompt_raw, int):
                    prompt_tokens = prompt_raw
                if isinstance(completion_raw, int):
                    completion_tokens = completion_raw

            for agg in (self._total, provider_agg, model_agg):
                agg.prompt_tokens += prompt_tokens
                agg.completion_tokens += completion_tokens

            cost_raw = event.get("cost_estimate_usd")
            if isinstance(cost_raw, (int, float)):
                cost = float(cost_raw)
                self._priced_event_count += 1
                for agg in (self._total, provider_agg, model_agg):
                    agg.cost_usd += cost
            else:
                self._unknown_model_count += 1

            cache_savings = event.get("cache_savings")
            if isinstance(cache_savings, dict):
                estimated = cache_savings.get("estimated_usd")
                low = cache_savings.get("low_usd")
                high = cache_savings.get("high_usd")

                estimated_value = float(estimated) if isinstance(estimated, (int, float)) else 0.0
                low_value = float(low) if isinstance(low, (int, float)) else 0.0
                high_value = float(high) if isinstance(high, (int, float)) else 0.0

                for agg in (self._total, provider_agg, model_agg):
                    agg.savings_estimated_usd += estimated_value
                    agg.savings_low_usd += low_value
                    agg.savings_high_usd += high_value

            similarity_raw = event.get("prefix_similarity")
            if isinstance(similarity_raw, (int, float)):
                self._prefix_similarity_sum += float(similarity_raw)

            boundary_raw = event.get("cache_boundary")
            if isinstance(boundary_raw, dict) and boundary_raw.get("present") is True:
                self._boundary_present_count += 1

            breakers_raw = event.get("cache_breakers")
            if isinstance(breakers_raw, list):
                for item in breakers_raw:
                    if isinstance(item, dict):
                        # Current schema uses "category"; keep "type" for backward compatibility.
                        breaker_type = item.get("category")
                        if not isinstance(breaker_type, str) or not breaker_type:
                            breaker_type = item.get("type")
                        if isinstance(breaker_type, str) and breaker_type:
                            self._breaker_counts[breaker_type] += 1

            pricing_raw = event.get("pricing")
            if isinstance(pricing_raw, dict):
                version = pricing_raw.get("version")
                if isinstance(version, str) and version:
                    self._pricing_versions_seen.add(version)

    def _sorted_breakdown(
        self, values: dict[str, _Aggregate], usd_decimals: int
    ) -> dict[str, dict[str, object]]:
        entries = sorted(values.items(), key=lambda item: (-item[1].cost_usd, item[0]))
        return {name: aggregate.as_dict(usd_decimals) for name, aggregate in entries}

    def report_dict(self, usd_decimals: int = 8) -> dict[str, object]:
        options = UsageReportOptions(usd_decimals=max(0, usd_decimals))
        with self._lock:
            event_count = self._total.events
            avg_similarity = self._prefix_similarity_sum / event_count if event_count else 0.0
            boundary_rate = self._boundary_present_count / event_count if event_count else 0.0

            top_breakers = [
                {"type": name, "count": count}
                for name, count in self._breaker_counts.most_common(options.top_breakers_limit)
            ]

            return {
                "event_count": event_count,
                "retained_event_count": len(self._events),
                "retention_limit": self._max_events,
                "totals": self._total.as_dict(options.usd_decimals),
                "providers": self._sorted_breakdown(self._providers, options.usd_decimals),
                "models": self._sorted_breakdown(self._models, options.usd_decimals),
                "cache": {
                    "average_prefix_similarity": round(avg_similarity, 4),
                    "boundary_present_rate": round(boundary_rate, 4),
                    "top_cache_breakers": top_breakers,
                },
                "costing": {
                    "unknown_model_count": self._unknown_model_count,
                    "priced_event_count": self._priced_event_count,
                    "pricing_versions_seen": sorted(self._pricing_versions_seen),
                },
            }

    def report_json(self, indent: int = 2, usd_decimals: int = 8) -> str:
        report = self.report_dict(usd_decimals=usd_decimals)
        return json.dumps(report, indent=indent, sort_keys=True)

    def save_json(self, path: str | Path, indent: int = 2, usd_decimals: int = 8) -> Path:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        temp_path = destination.with_suffix(destination.suffix + ".tmp")
        temp_path.write_text(self.report_json(indent=indent, usd_decimals=usd_decimals) + "\n")
        temp_path.replace(destination)
        return destination

    def print_report(self, format: str = "table", usd_decimals: int = 8) -> None:
        report = self.report_dict(usd_decimals=usd_decimals)
        if format == "json":
            print(json.dumps(report, indent=2, sort_keys=True))
            return
        if format != "table":
            raise ValueError("format must be either 'table' or 'json'")
        print(_render_table(report, usd_decimals=max(0, usd_decimals)))


def _format_usd(value: object, decimals: int) -> str:
    if not isinstance(value, (int, float)):
        return "$0"
    return f"${float(value):.{decimals}f}"


def _render_table(report: dict[str, object], usd_decimals: int) -> str:
    totals = report.get("totals")
    cache = report.get("cache")
    costing = report.get("costing")

    lines = [
        "Cecil Usage Analytics",
        "====================",
        (
            f"Events: {report.get('event_count', 0)} "
            f"(retained {report.get('retained_event_count', 0)})"
        ),
    ]

    if isinstance(totals, dict):
        lines.extend(
            [
                "",
                "Totals",
                f"- Prompt tokens: {totals.get('prompt_tokens', 0)}",
                f"- Completion tokens: {totals.get('completion_tokens', 0)}",
                f"- Estimated cost: {_format_usd(totals.get('cost_usd'), usd_decimals)}",
                (
                    "- Estimated cache savings: "
                    f"{_format_usd(totals.get('savings_estimated_usd'), usd_decimals)}"
                ),
                (
                    "- Savings range: "
                    f"{_format_usd(totals.get('savings_low_usd'), usd_decimals)}"
                    " to "
                    f"{_format_usd(totals.get('savings_high_usd'), usd_decimals)}"
                ),
            ]
        )

    if isinstance(cache, dict):
        lines.extend(
            [
                "",
                "Cache",
                f"- Average prefix similarity: {cache.get('average_prefix_similarity', 0.0)}",
                f"- Cache boundary present rate: {cache.get('boundary_present_rate', 0.0)}",
            ]
        )

        breakers = cache.get("top_cache_breakers")
        if isinstance(breakers, list) and breakers:
            lines.append("- Top cache breakers:")
            for breaker in breakers:
                if isinstance(breaker, dict):
                    lines.append(
                        f"  - {breaker.get('type', 'unknown')}: {breaker.get('count', 0)}"
                    )

    if isinstance(costing, dict):
        lines.extend(
            [
                "",
                "Costing",
                f"- Priced events: {costing.get('priced_event_count', 0)}",
                f"- Unknown model events: {costing.get('unknown_model_count', 0)}",
            ]
        )

    providers = report.get("providers")
    if isinstance(providers, dict) and providers:
        lines.extend(["", "Provider breakdown"])
        for name, stats in providers.items():
            if isinstance(stats, dict):
                lines.append(
                    f"- {name}: events={stats.get('events', 0)}, "
                    f"cost={_format_usd(stats.get('cost_usd'), usd_decimals)}, "
                    "savings="
                    f"{_format_usd(stats.get('savings_estimated_usd'), usd_decimals)}"
                )

    models = report.get("models")
    if isinstance(models, dict) and models:
        lines.extend(["", "Model breakdown"])
        for name, stats in models.items():
            if isinstance(stats, dict):
                lines.append(
                    f"- {name}: events={stats.get('events', 0)}, "
                    f"cost={_format_usd(stats.get('cost_usd'), usd_decimals)}, "
                    "savings="
                    f"{_format_usd(stats.get('savings_estimated_usd'), usd_decimals)}"
                )

    return "\n".join(lines)


def start_session(*, auto_patch: bool = True, max_events: int = 2000) -> UsageSession:
    if auto_patch:
        patch()
    return UsageSession(max_events=max_events)
