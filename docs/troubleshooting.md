# Troubleshooting

## No telemetry is sent
- Check `CECIL_ENABLED=true`.
- Ensure both `CECIL_API_KEY` and `CECIL_ENDPOINT` are set.
- Verify endpoint is reachable.

## Provider SDK behavior changes unexpectedly
- SDK is designed fail-open. If you see call regressions, disable patching and report stack trace.

## Unknown model cost output
- `cost_label` is set to `unknown_model` when no pricing fixture exists.
- This is non-fatal and request processing continues.
