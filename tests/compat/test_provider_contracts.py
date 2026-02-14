from __future__ import annotations

import pytest


def test_openai_contract_path_exists() -> None:
    openai = pytest.importorskip("openai")
    assert hasattr(openai, "__version__")
    module = __import__("openai.resources.chat.completions", fromlist=["Completions"])
    assert hasattr(module, "Completions")
    assert hasattr(module.Completions, "create")


def test_anthropic_contract_path_exists() -> None:
    anthropic = pytest.importorskip("anthropic")
    assert hasattr(anthropic, "__version__")
    module = __import__("anthropic.resources.messages", fromlist=["Messages"])
    assert hasattr(module, "Messages")
    assert hasattr(module.Messages, "create")
