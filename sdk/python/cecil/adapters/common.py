from __future__ import annotations

from typing import Any

_TEXT_TYPES = {"text", "input_text", "output_text"}


def _extract_text_from_block(block: Any) -> str:
    if isinstance(block, str):
        return block
    if not isinstance(block, dict):
        return ""

    text_value = block.get("text")
    if isinstance(text_value, str) and (block.get("type") in _TEXT_TYPES or "type" not in block):
        return text_value

    content_value = block.get("content")
    if isinstance(content_value, str):
        return content_value

    if isinstance(content_value, list):
        texts = [_extract_text_from_block(item) for item in content_value]
        return " ".join(t for t in texts if t)

    return ""


def extract_prompt(kwargs: dict[str, Any]) -> tuple[str, int | None]:
    messages = kwargs.get("messages")
    cache_pos: int | None = None
    if isinstance(messages, list):
        parts: list[str] = []
        for idx, item in enumerate(messages):
            if not isinstance(item, dict):
                continue

            content = item.get("content", "")
            if isinstance(content, list):
                text_parts = [_extract_text_from_block(p) for p in content]
                joined = " ".join(part for part in text_parts if part)
                if joined:
                    parts.append(joined)
            elif isinstance(content, dict):
                text = _extract_text_from_block(content)
                if text:
                    parts.append(text)
            elif isinstance(content, str):
                parts.append(content)

            if item.get("cache_control") is not None and cache_pos is None:
                cache_pos = idx
            if isinstance(content, list) and cache_pos is None:
                for block in content:
                    if isinstance(block, dict) and block.get("cache_control") is not None:
                        cache_pos = idx
                        break

        return "\n".join(parts), cache_pos

    input_value = kwargs.get("input")
    if isinstance(input_value, list):
        text_parts = [_extract_text_from_block(item) for item in input_value]
        text = "\n".join(part for part in text_parts if part)
        return text, None

    prompt = kwargs.get("prompt", "")
    if isinstance(prompt, str):
        return prompt, None

    if isinstance(input_value, str):
        return input_value, None

    return "", None


def extract_token_counts(response: Any) -> tuple[int, int]:
    usage = getattr(response, "usage", None)
    if usage is None and isinstance(response, dict):
        usage = response.get("usage")

    if usage is None:
        return 0, 0

    if isinstance(usage, dict):
        prompt = int(usage.get("prompt_tokens", usage.get("input_tokens", 0)) or 0)
        completion = int(usage.get("completion_tokens", usage.get("output_tokens", 0)) or 0)
        return prompt, completion

    prompt = int(getattr(usage, "prompt_tokens", getattr(usage, "input_tokens", 0)) or 0)
    completion = int(getattr(usage, "completion_tokens", getattr(usage, "output_tokens", 0)) or 0)
    return prompt, completion


def extract_model(kwargs: dict[str, Any], response: Any) -> str:
    model = kwargs.get("model")
    if isinstance(model, str) and model:
        return model

    if isinstance(response, dict):
        model = response.get("model")
        if isinstance(model, str):
            return model

    model_attr = getattr(response, "model", None)
    if isinstance(model_attr, str):
        return model_attr

    return "unknown"
