"""LLM backends: Anthropic (paid) or Ollama (local & free), with offline fallback.

Provider is chosen by the env var KOKI_LLM:
  - "auto" (default): Anthropic if key+SDK present, else local Ollama if running,
    else "none" (callers fall back to templates).
  - "anthropic" / "ollama" / "none": force a specific backend.

Ollama is called over its local HTTP API using only the standard library, so
there is no extra dependency and no API key — it runs entirely on your machine.
"""

from __future__ import annotations

import json
import os
import urllib.request

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
DEFAULT_OLLAMA_MODEL = "llama3.1"


def _anthropic_ready() -> bool:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return False
    try:
        import anthropic  # noqa: F401
    except Exception:
        return False
    return True


def _ollama_up() -> bool:
    try:
        with urllib.request.urlopen(OLLAMA_HOST + "/api/tags", timeout=2) as r:
            return getattr(r, "status", 200) == 200
    except Exception:
        return False


def provider() -> str:
    """Return the active backend: 'anthropic' | 'ollama' | 'none'."""
    forced = os.environ.get("KOKI_LLM", "auto").lower()
    if forced in ("anthropic", "ollama", "none"):
        return forced
    if _anthropic_ready():
        return "anthropic"
    if _ollama_up():
        return "ollama"
    return "none"


def have_llm() -> bool:
    return provider() in ("anthropic", "ollama")


def complete(prompt: str, *, system: str = "", model: str, max_tokens: int = 4096) -> str:
    p = provider()
    if p == "anthropic":
        return _complete_anthropic(prompt, system=system, model=model, max_tokens=max_tokens)
    if p == "ollama":
        return _complete_ollama(prompt, system=system, max_tokens=max_tokens)
    raise RuntimeError(
        "No LLM provider available. Set ANTHROPIC_API_KEY, or run Ollama "
        "(https://ollama.com) and `ollama pull llama3.1`."
    )


def _complete_anthropic(prompt: str, *, system: str, model: str, max_tokens: int) -> str:
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


def _complete_ollama(prompt: str, *, system: str, max_tokens: int) -> str:
    model = os.environ.get("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL)
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    payload = json.dumps(
        {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {"num_predict": max_tokens},
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_HOST + "/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=300) as r:
        data = json.loads(r.read().decode("utf-8"))
    return (data.get("message", {}).get("content") or "").strip()
