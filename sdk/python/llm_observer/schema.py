from __future__ import annotations

import json
from importlib import resources
from pathlib import Path
from typing import Any, cast

import jsonschema


def schema_path() -> Path:
    with resources.as_file(resources.files("llm_observer.data") / "telemetry_event_v1.json") as p:
        return p


def load_schema() -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(schema_path().read_text()))


def validate_event(event: dict[str, object]) -> None:
    jsonschema.validate(event, load_schema())
