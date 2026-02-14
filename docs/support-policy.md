# Support and Deprecation Policy

## Support policy
- New SDK releases target active Python minor versions listed in `docs/compatibility-matrix.md`.
- Security/privacy bugs are prioritized over feature requests.

## Deprecation policy
- Breaking telemetry contract changes require a new schema version.
- Breaking API changes require a major version bump.
- Deprecated behavior is announced in changelog before removal.

## Migration policy
- Any breaking release must include:
  - migration notes,
  - upgrade examples,
  - explicit behavior changes.
