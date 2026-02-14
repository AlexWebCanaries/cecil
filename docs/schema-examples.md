# Telemetry Schema Examples

```json
{
  "schema_version": "v1",
  "event_id": "88cf8490-b401-4423-a5c4-e7dbb84f472e",
  "timestamp_ms": 1739495101000,
  "provider": "openai",
  "model": "gpt-4o-mini",
  "token_counts": {"prompt": 120, "completion": 80, "total": 200},
  "latency_ms": 452,
  "cost_estimate_usd": 0.000066,
  "cost_label": null,
  "pricing": {"version": "pricing-v1", "source": ".../shared/pricing/pricing_v1.json"},
  "prefix_hash_blocks": ["a3aab91d3d7ef0d1", "34be25a4f8a4d38f"],
  "prefix_similarity": 0.87,
  "cache_savings_estimate_usd": 0.0000172,
  "cache_savings": {"estimated_usd": 0.0000172, "low_usd": 0.0000103, "high_usd": 0.0000206, "confidence": 0.809},
  "cache_breakers": [{"category": "timestamp", "confidence": 0.92, "hint": "Move timestamps to suffix or metadata fields."}],
  "cache_boundary": {"present": true, "position": 0},
  "privacy": {"mode": "hash_only", "redaction_mode": "strict", "snippet": null},
  "recommendation": {
    "top_cache_breakers": [{"category": "timestamp", "confidence": 0.92, "hint": "Move timestamps to suffix or metadata fields."}],
    "potential_savings_range_usd": {"low": 0.0000103, "high": 0.0000206},
    "confidence": 0.809,
    "suggested_actions": ["Move timestamps to suffix or metadata fields."]
  }
}
```
