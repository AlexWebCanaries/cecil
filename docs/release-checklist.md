# Release Checklist

1. Run `make ci`.
2. Validate distribution metadata with `twine check dist/*`.
3. Run wheel smoke install in clean venv:
   - `pip install dist/*.whl`
   - `python scripts/smoke_check_wheel.py`
4. Verify changelog generation source:
   - primary: git history
   - fallback: `RELEASE_NOTES_INPUT.txt`
5. Run TestPyPI rehearsal workflow (`release-testpypi.yml`) and verify install from TestPyPI.
6. Update `CHANGELOG.md`.
7. Confirm schema version and package version alignment.
8. Tag release and publish artifact via `release.yml`.
