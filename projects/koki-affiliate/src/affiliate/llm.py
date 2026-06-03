"""Thin Claude wrapper with graceful offline fallback.

If the anthropic SDK is installed *and* ANTHROPIC_API_KEY is set, we can call
Claude. Otherwise callers fall back to deterministic templates so the whole
pipeline still runs offline.
"""

from __future__ import annotations

import os


def have_llm() -> bool:
    """True when we can actually call Claude in this environment."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return False
    try:
        import anthropic  # noqa: F401
    except Exception:
        return False
    return True


def complete(prompt: str, *, system: str = "", model: str, max_tokens: int = 4096) -> str:
    """Single-turn completion. Raises if the SDK/key are unavailable."""
    from anthropic import Anthropic

    client = Anthropic()
    resp = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system or "You are a helpful assistant.",
        messages=[{"role": "user", "content": prompt}],
    )
    return "\n".join(
        b.text for b in resp.content if getattr(b, "type", None) == "text"
    ).strip()
