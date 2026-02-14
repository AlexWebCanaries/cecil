from __future__ import annotations

from pathlib import Path


def test_provider_compat_workflow_uses_current_env_var() -> None:
    root = Path(__file__).resolve().parents[2]
    workflow = (root / ".github" / "workflows" / "provider-compat.yml").read_text()

    assert "CECIL_RUN_COMPAT" in workflow
    assert "LLM_OBSERVER_RUN_COMPAT" not in workflow
