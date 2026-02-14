# Release Checklist

1. Run one-command pre-tag rehearsal: `make release-dry-run`.
2. Run `make ci`.
3. Validate distribution metadata with `twine check dist/*`.
4. Run wheel smoke install in clean venv:
   - `pip install dist/*.whl`
   - `python scripts/smoke_check_wheel.py`
5. Verify changelog generation source:
   - primary: git history
   - fallback: `RELEASE_NOTES_INPUT.txt`
6. Run TestPyPI rehearsal workflow (`release-testpypi.yml`) and verify install from TestPyPI.
7. Generate QA summary stub with `make qa-stub` and fill workflow links/status.
8. Update `CHANGELOG.md`.
9. Confirm schema version and package version alignment.
10. Tag release and publish artifact via `release.yml`.
