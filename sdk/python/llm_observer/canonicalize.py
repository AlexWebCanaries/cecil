from __future__ import annotations

import re

_UUID_RE = re.compile(
    r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}\b"
)
_TS_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?\b")
_NONCE_RE = re.compile(
    r"\b(?:nonce|request[_-]?id|session[_-]?id)[:=]\s*[A-Za-z0-9_-]{8,}\b", re.IGNORECASE
)
_WS_RE = re.compile(r"\s+")


def canonicalize_prompt(prompt: str) -> str:
    text = prompt.strip()
    text = text.replace("\\n", " ")
    text = _TS_RE.sub("<ts>", text)
    text = _UUID_RE.sub("<uuid>", text)
    text = _NONCE_RE.sub("<id>", text)
    text = _WS_RE.sub(" ", text)
    return text
