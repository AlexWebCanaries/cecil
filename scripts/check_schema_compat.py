from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / "shared" / "schema" / "telemetry_event_v1.json"
BASELINE = ROOT / "shared" / "schema" / "baseline" / "telemetry_event_v1_baseline.json"


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text())


def _required_fields(schema: dict[str, object]) -> set[str]:
    return set(schema.get("required", []))


def _property_types(schema: dict[str, object]) -> dict[str, object]:
    properties = schema.get("properties", {})
    if not isinstance(properties, dict):
        return {}
    result: dict[str, object] = {}
    for key, value in properties.items():
        if isinstance(value, dict):
            result[key] = value.get("type", value.get("const"))
    return result


def main() -> int:
    current = _load(CURRENT)
    baseline = _load(BASELINE)

    current_version = current.get("properties", {}).get("schema_version", {}).get("const")
    baseline_version = baseline.get("properties", {}).get("schema_version", {}).get("const")

    removed_required = _required_fields(baseline) - _required_fields(current)
    if removed_required and current_version == baseline_version:
        message = "Breaking schema change: removed required fields "
        print(f"{message}{sorted(removed_required)} without version bump")
        return 1

    baseline_types = _property_types(baseline)
    current_types = _property_types(current)

    changed: list[str] = []
    for field, baseline_type in baseline_types.items():
        if field in current_types and current_types[field] != baseline_type:
            changed.append(field)

    if changed and current_version == baseline_version:
        print(f"Breaking schema change: changed field types {sorted(changed)} without version bump")
        return 1

    if current_version != baseline_version:
        print(f"Schema version changed: {baseline_version} -> {current_version}")

    print("Schema compatibility check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
