from __future__ import annotations

import sys
import types

import pytest
from llm_observer.event_model import reset_history
from llm_observer.patcher import shutdown


@pytest.fixture(autouse=True)
def cleanup_patcher() -> None:
    shutdown()
    reset_history()
    yield
    shutdown()
    reset_history()


@pytest.fixture
def fake_openai_module() -> list[dict[str, object]]:
    records: list[dict[str, object]] = []

    openai = types.ModuleType("openai")
    resources = types.ModuleType("openai.resources")
    chat = types.ModuleType("openai.resources.chat")
    completions = types.ModuleType("openai.resources.chat.completions")

    class Response:
        def __init__(self) -> None:
            self.model = "gpt-4o-mini"
            self.usage = {"prompt_tokens": 12, "completion_tokens": 8}

    class Completions:
        def create(self, **kwargs: object) -> Response:
            records.append(kwargs)
            return Response()

    completions.Completions = Completions

    sys.modules["openai"] = openai
    sys.modules["openai.resources"] = resources
    sys.modules["openai.resources.chat"] = chat
    sys.modules["openai.resources.chat.completions"] = completions

    return records


@pytest.fixture
def fake_anthropic_module() -> list[dict[str, object]]:
    records: list[dict[str, object]] = []

    anthropic = types.ModuleType("anthropic")
    resources = types.ModuleType("anthropic.resources")
    messages = types.ModuleType("anthropic.resources.messages")

    class Response:
        def __init__(self) -> None:
            self.model = "claude-3-5-haiku"
            self.usage = {"input_tokens": 30, "output_tokens": 20}

    class Messages:
        def create(self, **kwargs: object) -> Response:
            records.append(kwargs)
            return Response()

    messages.Messages = Messages

    sys.modules["anthropic"] = anthropic
    sys.modules["anthropic.resources"] = resources
    sys.modules["anthropic.resources.messages"] = messages

    return records
