.PHONY: install lint format typecheck test build ci schema-compat

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
