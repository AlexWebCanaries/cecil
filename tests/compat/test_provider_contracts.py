from __future__ import annotations

import os
from importlib.metadata import version

import pytest

RUN_COMPAT = os.getenv("CECIL_RUN_COMPAT") == "1"
pytestmark = pytest.mark.skipif(
    not RUN_COMPAT,
    reason="Compatibility checks run in dedicated provider-compat CI workflow.",
)


def test_openai_contract_path_exists() -> None:
    import openai

    assert hasattr(openai, "__version__")
    expected = os.getenv("EXPECTED_OPENAI_VERSION")
    if expected:
        assert version("openai") == expected
    module = __import__("openai.resources.chat.completions", fromlist=["Completions"])
    assert hasattr(module, "Completions")
    assert hasattr(module.Completions, "create")


def test_anthropic_contract_path_exists() -> None:
    import anthropic

    assert hasattr(anthropic, "__version__")
    expected = os.getenv("EXPECTED_ANTHROPIC_VERSION")
    if expected:
        assert version("anthropic") == expected
    module = __import__("anthropic.resources.messages", fromlist=["Messages"])
    assert hasattr(module, "Messages")
    assert hasattr(module.Messages, "create")
