from __future__ import annotations

import re
from dataclasses import dataclass

_BREAKERS: list[tuple[str, re.Pattern[str], float]] = [
    ("timestamp", re.compile(r"\b\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}"), 0.92),
    (
        "uuid",
        re.compile(
            r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}\b"
        ),
        0.99,
    ),
    (
        "random_id",
        re.compile(r"\b(?:nonce|request[_-]?id|session[_-]?id)[:=]\s*[A-Za-z0-9_-]{8,}\b", re.I),
        0.86,
    ),
    ("hex_blob", re.compile(r"\b[0-9a-f]{24,}\b", re.I), 0.72),
]

_HINTS = {
    "timestamp": "Move timestamps to suffix or metadata fields.",
    "uuid": "Avoid UUIDs in reusable prompt prefix sections.",
    "random_id": "Remove nonce/request IDs from static instruction prefix.",
    "hex_blob": "Trim long random blobs from cached prefix region.",
}


@dataclass(frozen=True)
class Breaker:
    category: str
    confidence: float
    hint: str


def prefix_similarity_score(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    max_len = min(len(a), len(b))
    i = 0
    while i < max_len and a[i] == b[i]:
        i += 1
    return round(i / max_len, 4)


def detect_cache_breakers(prompt: str) -> list[Breaker]:
    findings: list[Breaker] = []
    for category, pattern, confidence in _BREAKERS:
        if pattern.search(prompt):
            findings.append(
                Breaker(category=category, confidence=confidence, hint=_HINTS[category])
            )
    return findings
