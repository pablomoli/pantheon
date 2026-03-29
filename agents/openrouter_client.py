"""OpenRouter access via the OpenAI-compatible API (AsyncOpenAI)."""

from __future__ import annotations

import base64
import os
from typing import Any, Final

from openai import AsyncOpenAI

_DEFAULT_BASE: Final[str] = "https://openrouter.ai/api/v1"


def _require_openrouter_api_key(api_key: str | None) -> str:
    if api_key and api_key.strip():
        return api_key.strip()
    env_key = os.getenv("OPENROUTER_API_KEY") or ""
    key = env_key.strip()
    if not key:
        msg = (
            "OPENROUTER_API_KEY is not set. Add it to your environment or .env file "
            "(OpenRouter dashboard → API keys)."
        )
        raise RuntimeError(msg)
    return key


def get_openrouter_async_client(*, api_key: str | None = None) -> AsyncOpenAI:
    """Return an AsyncOpenAI client pointed at OpenRouter with optional ranking headers."""
    key = _require_openrouter_api_key(api_key)
    referer = os.getenv("OPENROUTER_HTTP_REFERER", "https://github.com/pantheon").strip()
    title = os.getenv("OPENROUTER_TITLE", "Pantheon").strip()
    base = os.getenv("OPENROUTER_API_BASE", _DEFAULT_BASE).strip() or _DEFAULT_BASE
    return AsyncOpenAI(
        base_url=base,
        api_key=key,
        default_headers={
            "HTTP-Referer": referer,
            "X-OpenRouter-Title": title,
        },
    )


def normalize_openrouter_model_id(model: str) -> str:
    """Strip ``openrouter/`` so the id matches the API (e.g. ``openai/gpt-5.2``)."""
    if model.startswith("openrouter/"):
        return model[len("openrouter/") :]
    return model


async def openrouter_chat(
    *,
    model: str,
    user_prompt: str,
    temperature: float,
    max_tokens: int,
    json_mode: bool = False,
    api_key: str | None = None,
) -> str:
    """Run a single user-message chat completion and return assistant text."""
    client = get_openrouter_async_client(api_key=api_key)
    mid = normalize_openrouter_model_id(model)
    kwargs: dict[str, Any] = {
        "model": mid,
        "messages": [{"role": "user", "content": user_prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    response = await client.chat.completions.create(**kwargs)
    choice = response.choices[0]
    content = choice.message.content
    return (content or "").strip()


def audio_format_from_mime(mime_type: str) -> str:
    """Map MIME type to OpenRouter ``input_audio.format`` values."""
    lower = mime_type.lower()
    if "ogg" in lower or "opus" in lower:
        return "ogg"
    if "webm" in lower:
        return "webm"
    if "wav" in lower:
        return "wav"
    if "mpeg" in lower or "mp3" in lower:
        return "mp3"
    return "wav"


async def openrouter_transcribe_audio(
    *,
    model: str,
    audio_bytes: bytes,
    mime_type: str,
    api_key: str | None = None,
) -> str:
    """Transcribe audio using a model that accepts ``input_audio`` (OpenRouter multimodal)."""
    client = get_openrouter_async_client(api_key=api_key)
    mid = normalize_openrouter_model_id(model)
    b64 = base64.b64encode(audio_bytes).decode("ascii")
    fmt = audio_format_from_mime(mime_type)
    response = await client.chat.completions.create(
        model=mid,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Transcribe the following audio into plain text. "
                            "Do not add commentary."
                        ),
                    },
                    {"type": "input_audio", "input_audio": {"data": b64, "format": fmt}},
                ],
            }
        ],
        temperature=0.0,
        max_tokens=4096,
    )
    choice = response.choices[0]
    content = choice.message.content
    text = (content or "").strip()
    if not text:
        msg = "OpenRouter transcription returned empty text"
        raise RuntimeError(msg)
    return text
