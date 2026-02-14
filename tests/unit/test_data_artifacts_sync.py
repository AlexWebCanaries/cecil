from __future__ import annotations

from pathlib import Path


def test_schema_artifact_synced() -> None:
    root = Path(__file__).resolve().parents[2]
    shared = (root / "shared" / "schema" / "telemetry_event_v1.json").read_text()
    packaged = (
        root / "sdk" / "python" / "llm_observer" / "data" / "telemetry_event_v1.json"
    ).read_text()
    assert shared == packaged


def test_pricing_artifact_synced() -> None:
    root = Path(__file__).resolve().parents[2]
    shared = (root / "shared" / "pricing" / "pricing_v1.json").read_text()
    packaged = (root / "sdk" / "python" / "llm_observer" / "data" / "pricing_v1.json").read_text()
    assert shared == packaged
