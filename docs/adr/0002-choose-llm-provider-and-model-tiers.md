# 0002. Choose the LLM provider and model tiers

- Status: proposed
- Date: 2026-11-14

## Context

Phase 01 labs call a provider SDK directly. Later phases keep application code provider-agnostic, but development, production, and eval judging still each need a model.

## Decision

Open: which provider, and which models for development, production, and eval judging.

## Alternatives

Not chosen yet.

## Consequences

Lab scripts that call a model stay blocked until this is accepted. A hard spending cap on the provider account is still required before the first real call.
