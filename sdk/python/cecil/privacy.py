from __future__ import annotations

import hashlib
import re

_SECRET_PATTERN = re.compile(r"(api[_-]?key|authorization|bearer|secret)", re.IGNORECASE)
_EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_PHONE_PATTERN = re.compile(r"\b(?:\+?1[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?){2}\d{4}\b")
_LONG_NUMBER_PATTERN = re.compile(r"\b\d{9,}\b")


def hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def hash_prefix_blocks(
    canonical_prompt: str, block_size: int = 64, max_blocks: int = 3
) -> list[str]:
    blocks: list[str] = []
    for i in range(0, min(len(canonical_prompt), block_size * max_blocks), block_size):
        chunk = canonical_prompt[i : i + block_size]
        blocks.append(hash_text(chunk)[:16])
    return blocks


def redact_snippet(prompt: str, mode: str, snippets_enabled: bool) -> str | None:
    if mode != "redacted_snippets" or not snippets_enabled:
        return None
    preview = prompt[:120]
    redacted = _SECRET_PATTERN.sub("[REDACTED]", preview)
    redacted = _EMAIL_PATTERN.sub("[REDACTED_EMAIL]", redacted)
    redacted = _PHONE_PATTERN.sub("[REDACTED_PHONE]", redacted)
    return _LONG_NUMBER_PATTERN.sub("[REDACTED_NUMBER]", redacted)


def scrub_sensitive_dict(payload: dict[str, object]) -> dict[str, object]:
    blocked = {"api_key", "authorization", "headers", "prompt", "raw_prompt"}
    return {k: v for k, v in payload.items() if k.lower() not in blocked}
