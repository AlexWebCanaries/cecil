.PHONY: install lint format typecheck test build ci schema-compat release-dry-run qa-stub

install:
	python3 -m pip install -e '.[dev]'

lint:
	ruff check .

format:
	black .
	ruff format .

typecheck:
	mypy sdk/python

test:
	pytest

schema-compat:
	python3 scripts/check_schema_compat.py

build:
	python3 -m build

ci: lint typecheck schema-compat test build

release-dry-run:
	make ci
	python3 -m twine check dist/*
	python3 -m venv .venv-release-dry-run
	. .venv-release-dry-run/bin/activate && python -m pip install --upgrade pip && pip install dist/*.whl && python scripts/smoke_check_wheel.py
	python3 scripts/generate_changelog.py --fallback-file RELEASE_NOTES_INPUT.txt

qa-stub:
	python3 scripts/generate_release_qa_stub.py
