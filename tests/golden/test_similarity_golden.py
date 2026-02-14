from __future__ import annotations

from llm_observer.cache_analysis import prefix_similarity_score
from llm_observer.canonicalize import canonicalize_prompt


def test_similarity_with_formatting_noise_is_stable() -> None:
    prompt_a = "System: Return JSON only.\\nUser: summarize account activity."
    prompt_b = "  System: Return JSON only. User: summarize account activity.  "

    a = canonicalize_prompt(prompt_a)
    b = canonicalize_prompt(prompt_b)

    score = prefix_similarity_score(a, b)
    assert score >= 0.95
