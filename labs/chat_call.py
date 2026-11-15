# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "openai>=2",
# ]
# ///
"""Send one system message and one user message to OpenRouter.

Prints the assistant text, the token usage, and the cost computed from the
per-token price list below. No LangChain.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from decimal import Decimal
from pathlib import Path

from openai import OpenAI

_REPO_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_MODEL = "nvidia/nemotron-3.5-lightning:free"

# USD per token, from GET https://openrouter.ai/api/v1/models on 2026-11-15.
# The free variants report 0 for both prompt and completion.
_PRICE_USD_PER_TOKEN: dict[str, tuple[Decimal, Decimal]] = {
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free": (Decimal(0), Decimal(0)),
    "nvidia/nemotron-3-ultra-550b-a55b:free": (Decimal(0), Decimal(0)),
    "nvidia/nemotron-3.5-lightning:free": (Decimal(0), Decimal(0)),
}

_SYSTEM = "You are a concise assistant. Answer in one sentence."
_USER = "In one sentence, what is a token in a language model?"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--starve",
        action="store_true",
        help="Use an 80-token completion budget and leave reasoning uncapped.",
    )
    args = parser.parse_args()
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
    # The OpenAI SDK drops OpenRouter's reasoning field. Read the raw body.
    # The normal call caps reasoning. --starve is the 80-token run: reasoning
    # stays on and shares that whole budget, so the visible answer can be empty.
    if args.starve:
        max_tokens = 80
        extra_body = None
    else:
        max_tokens = 400
        extra_body = {"reasoning": {"max_tokens": 120}}
    raw_http = client.chat.completions.with_raw_response.create(
        model=model,
        temperature=0,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": _USER},
        ],
        extra_body=extra_body,
    )
    completion = raw_http.parse()
    payload = json.loads(raw_http.text)
    raw_message = payload["choices"][0]["message"]
    reasoning = raw_message.get("reasoning") or raw_message.get("reasoning_content")

    choice = completion.choices[0]
    usage = completion.usage
    if usage is None:
        sys.exit("OpenRouter returned no usage object, so the cost cannot be computed.")

    prompt_tokens = usage.prompt_tokens
    completion_tokens = usage.completion_tokens
    prompt_price, completion_price = prices
    cost = prompt_tokens * prompt_price + completion_tokens * completion_price
    details = usage.completion_tokens_details
    reasoning_tokens = details.reasoning_tokens if details is not None else None

    print(f"model: {completion.model}")
    print(f"max_tokens: {max_tokens}")
    print(f"finish_reason: {choice.finish_reason}")
    print(f"reasoning: {reasoning or '(none)'}")
    print(f"response: {choice.message.content}")
    if not choice.message.content:
        print(
            "No visible reply. Reasoning tokens count toward max_tokens, "
            "so a short budget can be spent before the answer starts."
        )
    print(f"prompt_tokens: {prompt_tokens}")
    print(f"completion_tokens: {completion_tokens}")
    print(f"reasoning_tokens: {reasoning_tokens}")
    print(f"total_tokens: {usage.total_tokens}")
    print(f"prompt_usd_per_token: {prompt_price}")
    print(f"completion_usd_per_token: {completion_price}")
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
