# Telemetry Opt-in

Telemetry is disabled by default.

Enable telemetry explicitly:

```bash
export CECIL_ENABLED=true
export CECIL_API_KEY='lok_xxx.yyy'
export CECIL_ENDPOINT='https://example.ingest/v1/events'
```

Optional:

```bash
export CECIL_SAMPLING_RATE=1.0
export CECIL_PRIVACY_MODE=hash_only
export CECIL_REDACTION_MODE=strict
export CECIL_SNIPPETS_ENABLED=false
```

Default privacy posture:
- Sends metadata, timings, token counts, hashed prefix blocks, cache metadata.
- Does not send raw prompt text by default.
