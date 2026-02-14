from __future__ import annotations

from llm_observer.adapters.common import extract_prompt


def test_extract_prompt_handles_structured_content_blocks() -> None:
    kwargs = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "hello"},
                    {"type": "input_text", "text": "world"},
                    {"type": "image_url", "url": "http://image"},
                ],
            }
        ]
    }
    prompt, cache_pos = extract_prompt(kwargs)
    assert "hello" in prompt
    assert "world" in prompt
    assert cache_pos is None


def test_extract_prompt_input_list_and_cache_boundary() -> None:
    kwargs = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "prefix", "cache_control": {"type": "ephemeral"}}
                ],
            }
        ],
        "input": [{"type": "text", "text": "fallback input"}],
    }
    prompt, cache_pos = extract_prompt(kwargs)
    assert "prefix" in prompt
    assert cache_pos == 0
