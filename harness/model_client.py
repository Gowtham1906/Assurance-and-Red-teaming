"""Real model client (provider-flexible).

Uses whichever key is present in .env, preferring Groq (free tier). Both Groq
and OpenAI share the same OpenAI-compatible client, so only the base_url, key,
and model name differ. No mocks: ``generate`` makes a live API call.

.env keys (set one set):
    GROQ_API_KEY   + optional GROQ_MODEL   (default llama-3.3-70b-versatile)
    OPENAI_API_KEY + optional OPENAI_MODEL (default gpt-4o-mini)
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

_GROQ_BASE = "https://api.groq.com/openai/v1"


def _resolve() -> tuple[str, str, str | None]:
    """Return (api_key, model, base_url) based on which key is configured."""
    groq = os.getenv("GROQ_API_KEY")
    if groq and not groq.startswith("gsk-your"):
        return groq, os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"), _GROQ_BASE

    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key and not openai_key.startswith("sk-your-real-key"):
        return openai_key, os.getenv("OPENAI_MODEL", "gpt-4o-mini"), None

    raise RuntimeError(
        "No usable API key found. Set GROQ_API_KEY (free: https://console.groq.com) "
        "or OPENAI_API_KEY in .env."
    )


def _client() -> tuple[OpenAI, str]:
    key, model, base_url = _resolve()
    kwargs = {"api_key": key}
    if base_url:
        kwargs["base_url"] = base_url
    return OpenAI(**kwargs), model


def generate(prompt: str, system: str | None = None, temperature: float = 0.0) -> str:
    """Call the real model and return the text answer (temperature 0 = reproducible)."""
    client, model = _client()
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    resp = client.chat.completions.create(
        model=model, messages=messages, temperature=temperature,
    )
    return resp.choices[0].message.content or ""


def model_name() -> str:
    return _resolve()[1]
