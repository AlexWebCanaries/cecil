from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Callable

from cecil.adapters.anthropic_adapter import patch_anthropic
from cecil.adapters.openai_adapter import patch_openai
from cecil.config import ObserverConfig, load_config
from cecil.logging import get_logger
from cecil.telemetry import TelemetryClient


@dataclass(frozen=True)
class PatchResult:
    openai_patched: bool
    anthropic_patched: bool
    telemetry_enabled: bool


_TELEMETRY: TelemetryClient | None = None
_OPENAI_PATCHED = False
_ANTHROPIC_PATCHED = False
_EVENT_LISTENERS: dict[int, Callable[[dict[str, object]], None]] = {}
_EVENT_LISTENER_LOCK = threading.Lock()
_NEXT_LISTENER_ID = 1


def register_event_listener(listener: Callable[[dict[str, object]], None]) -> int:
    global _NEXT_LISTENER_ID
    with _EVENT_LISTENER_LOCK:
        listener_id = _NEXT_LISTENER_ID
        _NEXT_LISTENER_ID += 1
        _EVENT_LISTENERS[listener_id] = listener
    return listener_id


def unregister_event_listener(listener_id: int) -> None:
    with _EVENT_LISTENER_LOCK:
        _EVENT_LISTENERS.pop(listener_id, None)


def emit_event(event: dict[str, object], telemetry: TelemetryClient) -> None:
    logger = get_logger()
    with _EVENT_LISTENER_LOCK:
        listeners = list(_EVENT_LISTENERS.values())

    for listener in listeners:
        try:
            listener(event)
        except Exception as exc:
            logger.debug("local event listener failed err=%s", type(exc).__name__)

    telemetry.emit(event)


def patch(config: ObserverConfig | None = None) -> PatchResult:
    global _TELEMETRY, _OPENAI_PATCHED, _ANTHROPIC_PATCHED
    logger = get_logger()

    if config is None:
        config = load_config()

    if _TELEMETRY is None:
        _TELEMETRY = TelemetryClient(config)

    if not _OPENAI_PATCHED:
        try:
            _OPENAI_PATCHED = patch_openai(config, _TELEMETRY)
        except Exception as exc:
            logger.debug("openai patch failed err=%s", type(exc).__name__)

    if not _ANTHROPIC_PATCHED:
        try:
            _ANTHROPIC_PATCHED = patch_anthropic(config, _TELEMETRY)
        except Exception as exc:
            logger.debug("anthropic patch failed err=%s", type(exc).__name__)

    return PatchResult(
        openai_patched=_OPENAI_PATCHED,
        anthropic_patched=_ANTHROPIC_PATCHED,
        telemetry_enabled=not config.local_only,
    )


def shutdown(timeout: float = 1.0, drain: bool = True) -> None:
    global _TELEMETRY, _OPENAI_PATCHED, _ANTHROPIC_PATCHED, _NEXT_LISTENER_ID
    if _TELEMETRY is not None:
        _TELEMETRY.stop(timeout=timeout, drain=drain)
    _TELEMETRY = None
    _OPENAI_PATCHED = False
    _ANTHROPIC_PATCHED = False
    with _EVENT_LISTENER_LOCK:
        _EVENT_LISTENERS.clear()
        _NEXT_LISTENER_ID = 1
