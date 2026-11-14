# 0002. Use OpenRouter as the LLM provider

- Status: accepted
- Date: 2026-11-14

## Context

Phase 01 labs call a provider directly. Development, production, and eval judging each need a model, and those models are not chosen yet. Later phases keep the application able to swap models.

## Decision

Use OpenRouter. The model ids for development, production, and eval judging stay unset until a later decision.

## Alternatives

None were compared when this was accepted.

## Consequences

Labs and the default client call OpenRouter, so picking a model later does not require a new provider. A hard spending cap on the OpenRouter account is still required before the first real call. No cap has been confirmed.
