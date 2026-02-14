# Telemetry Opt-in

Telemetry is disabled by default.

Enable telemetry explicitly:

```bash
export LLM_OBSERVER_ENABLED=true
export LLM_OBSERVER_API_KEY='lok_xxx.yyy'
export LLM_OBSERVER_ENDPOINT='https://example.ingest/v1/events'
```

Optional:

```bash
export LLM_OBSERVER_SAMPLING_RATE=1.0
export LLM_OBSERVER_PRIVACY_MODE=hash_only
export LLM_OBSERVER_REDACTION_MODE=strict
export LLM_OBSERVER_SNIPPETS_ENABLED=false
```

Default privacy posture:
- Sends metadata, timings, token counts, hashed prefix blocks, cache metadata.
- Does not send raw prompt text by default.
