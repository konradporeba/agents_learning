# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "openai>=2",
# ]
# ///
"""Show that the model does not remember a previous call.

Asks for a secret word with no history, then asks again with the first turn
resent. No LangChain.
"""

from __future__ import annotations

import json
import os
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any

from openai import OpenAI

_REPO_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_MODEL = "nvidia/nemotron-3.5-lightning:free"
_PRICE_USD_PER_TOKEN: dict[str, tuple[Decimal, Decimal]] = {
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free": (Decimal(0), Decimal(0)),
    "nvidia/nemotron-3-ultra-550b-a55b:free": (Decimal(0), Decimal(0)),
    "nvidia/nemotron-3.5-lightning:free": (Decimal(0), Decimal(0)),
}

_SYSTEM = "Answer in one sentence."
_SECRET = "The secret word is mangrove. Repeat that word back to me."
_FOLLOW_UP = (
    "What secret word did I give you? If this conversation does not contain it, "
    "say you do not know."
)


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

    first = _complete(
        client,
        model,
        [
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": _SECRET},
        ],
    )
    _print_turn("1. tell the secret", first, prices)

    alone = _complete(
        client,
        model,
        [
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": _FOLLOW_UP},
        ],
    )
    _print_turn("2. follow-up with no history", alone, prices)

    remembered = _complete(
        client,
        model,
        [
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": _SECRET},
            {"role": "assistant", "content": first["content"] or ""},
            {"role": "user", "content": _FOLLOW_UP},
        ],
    )
    _print_turn("3. same follow-up with history resent", remembered, prices)


def _complete(
    client: OpenAI, model: str, messages: list[dict[str, str]]
) -> dict[str, Any]:
    raw_http = client.chat.completions.with_raw_response.create(
        model=model,
        temperature=0,
        max_tokens=400,
        messages=messages,  # type: ignore[arg-type]
        extra_body={"reasoning": {"max_tokens": 120}},
    )
    completion = raw_http.parse()
    payload = json.loads(raw_http.text)
    raw_message = payload["choices"][0]["message"]
    usage = completion.usage
    if usage is None:
        sys.exit("OpenRouter returned no usage object, so the cost cannot be computed.")
    details = usage.completion_tokens_details
    return {
        "content": completion.choices[0].message.content,
        "finish_reason": completion.choices[0].finish_reason,
        "reasoning": raw_message.get("reasoning")
        or raw_message.get("reasoning_content"),
        "prompt_tokens": usage.prompt_tokens,
        "completion_tokens": usage.completion_tokens,
        "reasoning_tokens": details.reasoning_tokens if details is not None else None,
    }


def _print_turn(
    label: str,
    turn: dict[str, Any],
    prices: tuple[Decimal, Decimal],
) -> None:
    prompt_price, completion_price = prices
    cost = (
        turn["prompt_tokens"] * prompt_price
        + turn["completion_tokens"] * completion_price
    )
    print(f"--- {label}")
    print(f"finish_reason: {turn['finish_reason']}")
    print(f"response: {turn['content']}")
    print(f"prompt_tokens: {turn['prompt_tokens']}")
    print(f"completion_tokens: {turn['completion_tokens']}")
    print(f"reasoning_tokens: {turn['reasoning_tokens']}")
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
