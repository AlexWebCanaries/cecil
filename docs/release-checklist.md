# Release Checklist

1. Run `make ci`.
2. Verify schema compatibility gate passes.
3. Update `CHANGELOG.md`.
4. Validate package build artifact with `python -m build`.
5. Confirm schema version and package version alignment.
6. Tag release and publish artifact.
