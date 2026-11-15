# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "openai>=2",
# ]
# ///
"""Stream one reply and measure time to first token and tokens per second.

No LangChain. Time to first token is the wait until the first visible content
chunk. Tokens per second are completion tokens divided by the whole call.
"""

from __future__ import annotations

import os
import sys
import time
from decimal import Decimal
from pathlib import Path

from openai import OpenAI

_REPO_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_MODEL = "nvidia/nemotron-3.5-lightning:free"
_PRICE_USD_PER_TOKEN: dict[str, tuple[Decimal, Decimal]] = {
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free": (Decimal(0), Decimal(0)),
    "nvidia/nemotron-3-ultra-550b-a55b:free": (Decimal(0), Decimal(0)),
    "nvidia/nemotron-3.5-lightning:free": (Decimal(0), Decimal(0)),
}

_SYSTEM = "Answer in about ten sentences."
_USER = "What is the difference between waiting for a full reply and seeing it stream?"


def main() -> None:
    _load_env_file(_REPO_ROOT / ".env")
    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        sys.exit(
            "Set OPENROUTER_API_KEY in .env. Copy .env.example if you do not have one."
        )

    model = os.environ.get("OPENROUTER_MODEL", _DEFAULT_MODEL).strip() or _DEFAULT_MODEL
    prices = _PRICE_USD_PER_TOKEN.get(model)
    if prices is None:
        known = ", ".join(sorted(_PRICE_USD_PER_TOKEN))
        sys.exit(f"No price-list entry for {model}. This lab only calls: {known}")

    client = OpenAI(
        base_url=os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        api_key=api_key,
        default_headers={
            "HTTP-Referer": "https://github.com/konradporeba/agents_learning",
            "X-OpenRouter-Title": "Triage Copilot labs",
        },
    )

    started = time.perf_counter()
    stream = client.chat.completions.create(
        model=model,
        temperature=0,
        max_tokens=1200,
        stream=True,
        stream_options={"include_usage": True},
        messages=[
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": _USER},
        ],
        extra_body={"reasoning": {"max_tokens": 120}},
    )

    parts: list[str] = []
    first_content_at: float | None = None
    finish_reason: str | None = None
    usage = None
    # Each iteration is one server-sent chunk. Nothing is printed until a chunk arrives.
    for chunk in stream:
        now = time.perf_counter()
        # The last chunk carries token counts. It is not more reply text.
        if chunk.usage is not None:
            usage = chunk.usage
        # Some chunks have no choices, so there is no delta to read.
        if not chunk.choices:
            continue
        choice = chunk.choices[0]
        # finish_reason is empty until the model stops. The usage chunk repeats it.
        if choice.finish_reason:
            finish_reason = choice.finish_reason
        # delta.content is the new piece of the reply, often one token or a few words.
        text = choice.delta.content or ""
        if text and first_content_at is None:
            # First visible text. The wait up to here is time to first token.
            first_content_at = now
        if text:
            parts.append(text)
            # flush=True draws this chunk now, instead of waiting for a newline.
            print(text, end="", flush=True)
    print()
    ended = time.perf_counter()

    if usage is None:
        sys.exit("OpenRouter returned no usage object, so the cost cannot be computed.")
    if first_content_at is None:
        sys.exit(
            "The stream ended with no visible content, so time to first token is unknown."
        )

    prompt_price, completion_price = prices
    total_s = ended - started
    time_to_first_s = first_content_at - started
    tokens_per_second = usage.completion_tokens / total_s
    cost = (
        usage.prompt_tokens * prompt_price + usage.completion_tokens * completion_price
    )
    details = usage.completion_tokens_details
    reasoning_tokens = details.reasoning_tokens if details is not None else None

    print(f"model: {model}")
    print(f"finish_reason: {finish_reason}")
    print(f"response: {''.join(parts)}")
    print(f"time_to_first_content_s: {time_to_first_s:.3f}")
    print(f"total_s: {total_s:.3f}")
    print(f"prompt_tokens: {usage.prompt_tokens}")
    print(f"completion_tokens: {usage.completion_tokens}")
    print(f"reasoning_tokens: {reasoning_tokens}")
    print(f"tokens_per_second: {tokens_per_second:.2f}")
    print(f"cost_usd: {cost}")


def _load_env_file(path: Path) -> None:
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.removeprefix("export ").strip()
        os.environ.setdefault(key, value.strip().strip("'\""))


if __name__ == "__main__":
    main()
