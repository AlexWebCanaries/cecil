from __future__ import annotations

from dataclasses import dataclass

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
    global _TELEMETRY, _OPENAI_PATCHED, _ANTHROPIC_PATCHED
    if _TELEMETRY is not None:
        _TELEMETRY.stop(timeout=timeout, drain=drain)
    _TELEMETRY = None
    _OPENAI_PATCHED = False
    _ANTHROPIC_PATCHED = False
