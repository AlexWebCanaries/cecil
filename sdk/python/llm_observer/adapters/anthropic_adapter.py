from __future__ import annotations

import importlib
import time
from typing import Any, cast

from llm_observer.adapters.common import extract_model, extract_prompt, extract_token_counts
from llm_observer.config import ObserverConfig
from llm_observer.event_model import EventContext, build_event
from llm_observer.logging import get_logger
from llm_observer.telemetry import TelemetryClient


def patch_anthropic(config: ObserverConfig, telemetry: TelemetryClient) -> bool:
    logger = get_logger()
    try:
        module = importlib.import_module("anthropic.resources.messages")
        messages_cls = module.Messages
        original = messages_cls.create
    except Exception:
        return False

    if getattr(original, "_llm_observer_wrapped", False):
        return True

    def wrapped(self: object, *args: object, **kwargs: object) -> Any:
        start = time.monotonic()
        try:
            result = original(self, *args, **kwargs)
        except Exception:
            raise

        try:
            data = dict(kwargs)
            prompt, cache_pos = extract_prompt(data)
            prompt_tokens, completion_tokens = extract_token_counts(result)
            model = extract_model(data, result)
            event = build_event(
                EventContext(
                    provider="anthropic",
                    model=model,
                    prompt=prompt,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    latency_ms=int((time.monotonic() - start) * 1000),
                    cache_control_position=cache_pos,
                ),
                config=config,
            )
            telemetry.emit(event)
        except Exception as exc:
            logger.debug("anthropic instrumentation failed err=%s", type(exc).__name__)

        return result

    wrapped_fn = cast(Any, wrapped)
    wrapped_fn._llm_observer_wrapped = True
    messages_cls.create = wrapped
    return True
