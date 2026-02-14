from __future__ import annotations

from cecil.canonicalize import canonicalize_prompt
from cecil.privacy import hash_prefix_blocks


def test_canonicalize_is_stable() -> None:
    raw = "  time=2025-01-01T12:00:00Z  id=550e8400-e29b-41d4-a716-446655440000\\nhello "
    one = canonicalize_prompt(raw)
    two = canonicalize_prompt(raw)
    assert one == two
    assert "<ts>" in one
    assert "<uuid>" in one


def test_prefix_hashing_is_deterministic() -> None:
    value = "a" * 190
    first = hash_prefix_blocks(value)
    second = hash_prefix_blocks(value)
    assert first == second
    assert len(first) == 3
