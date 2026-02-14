# Cache-breaker Tradeoffs

Current breaker detection favors recall over precision for clearly dynamic prefixes.

- Timestamp detection can produce false positives for static historical examples in prompts.
- UUID detection has low false-positive risk but may miss non-standard IDs.
- Random-id/nonce detection may miss short IDs and may flag stable identifiers.
- Hex-blob detection can flag content hashes used intentionally in static prompts.

Mitigation:
- Use confidence scoring in emitted findings.
- Prefer hints as recommendations, not hard policy enforcement.
- Keep fail-open behavior: detections never block provider calls.
