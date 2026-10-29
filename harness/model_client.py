"""Real model client (provider-flexible).

Uses whichever key is present in .env, preferring Groq (free tier). Both Groq
and OpenAI share the same OpenAI-compatible client, so only the base_url, key,
and model name differ. No mocks: ``generate`` makes a live API call.

.env keys (set one set):
    GROQ_API_KEY   + optional GROQ_MODEL   (default openai/gpt-oss-20b)
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
        return groq, os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"), _GROQ_BASE

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

    # Retry on rate-limit (429) AND transient connection/API errors with backoff,
    # so free-tier TPM limits or network blips don't abort a long run.
    import re as _re
    import time as _time
    from openai import APIConnectionError, APIError, RateLimitError

    for attempt in range(6):
        try:
            resp = client.chat.completions.create(
                model=model, messages=messages, temperature=temperature,
                timeout=60,
            )
            return resp.choices[0].message.content or ""
        except RateLimitError as exc:
            m = _re.search(r"try again in ([\d.]+)s", str(exc))
            wait = float(m.group(1)) + 0.5 if m else 2.0 * (attempt + 1)
            if attempt == 5:
                raise
            _time.sleep(wait)
        except (APIConnectionError, APIError) as exc:
            if attempt == 5:
                raise
            _time.sleep(2.0 * (attempt + 1))  # backoff on transient network errors
    return ""  # unreachable


def model_name() -> str:
    return _resolve()[1]


def judge_model_name() -> str:
    """Judge model (plan section 7: use a DIFFERENT model family from the system
    under test). Override with JUDGE_MODEL in .env."""
    return os.getenv("JUDGE_MODEL", "qwen/qwen3.8-27b")


def generate_with_usage(prompt: str, system: str | None = None, model: str | None = None,
                        temperature: float = 0.0) -> tuple[str, dict]:
    """Like generate(), but for an explicit model and returning token usage.

    Returns (text, {"prompt_tokens", "completion_tokens"}). Same retry policy.
    """
    import re as _re
    import time as _time
    from openai import APIConnectionError, APIError, RateLimitError

    key, default_model, base_url = _resolve()
    kwargs = {"api_key": key}
    if base_url:
        kwargs["base_url"] = base_url
    client = OpenAI(**kwargs)
    messages = ([{"role": "system", "content": system}] if system else []) + \
               [{"role": "user", "content": prompt}]
    for attempt in range(6):
        try:
            resp = client.chat.completions.create(
                model=model or default_model, messages=messages,
                temperature=temperature, timeout=60,
            )
            u = resp.usage
            usage = {"prompt_tokens": getattr(u, "prompt_tokens", 0) or 0,
                     "completion_tokens": getattr(u, "completion_tokens", 0) or 0}
            return resp.choices[0].message.content or "", usage
        except RateLimitError as exc:
            m = _re.search(r"try again in ([\d.]+)s", str(exc))
            if attempt == 5:
                raise
            _time.sleep(float(m.group(1)) + 0.5 if m else 2.0 * (attempt + 1))
        except (APIConnectionError, APIError):
            if attempt == 5:
                raise
            _time.sleep(2.0 * (attempt + 1))
    return "", {"prompt_tokens": 0, "completion_tokens": 0}
