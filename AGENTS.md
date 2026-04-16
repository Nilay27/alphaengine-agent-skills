# AGENTS.md — alphaengine-agent-skills

This repo publishes installable public agent skills for AlphaEngine.

## 1. Engineering Goals

1. Keep shipped skills installable directly from GitHub with minimal setup.
2. Teach agents how to use AlphaEngine public surfaces correctly without leaking internal runtime boundaries.
3. Preserve bounded search freedom: agents should learn how to explore, not converge on one hardcoded recipe.
4. Keep skill instructions concise and reference-driven so they remain usable in real agent contexts.

## 2. Runtime Safety And Non-Negotiables

1. Skills must not instruct agents to use private/operator-only modules such as `listener-service` or operator-side `cofhe` as public interfaces.
2. Skills must not claim unsupported endpoints or capabilities.
3. Skills must not encourage storing secrets in repos or prompts.
4. Skills must not present speculative strategy combinations as canonical winners.
5. Public API usage must align with the live `api-router` contract and `x-api-key` auth model.

## 3. Architecture Boundaries

1. Public-agent skills may target `api-router` and other explicitly public AlphaEngine surfaces only.
2. Thin-client, wallet, encryption, listener, and operator-runtime flows are separate concerns and must be described accurately when relevant.
3. Strategy exploration skills may explain Pendle mechanics and search heuristics, but they do not own evaluation formulas or endpoint contracts.
4. When public API behavior changes, this repo must be updated in lockstep with the canonical source repo.

## 4. Testing And Validation Requirements

1. Any behavior or endpoint reference change must be checked against the current source docs or code in the owning repo.
2. Example requests in docs must be syntactically valid and use currently supported routes.
3. If a skill defines a scoring rule, the rule must match the canonical source exactly.
4. Public install instructions must be kept runnable.

## 5. Contract And Change Hygiene

1. `api-router` remains the canonical owner of public HTTP contract semantics.
2. This repo must not redefine public contracts in conflicting ways.
3. Changes that alter public-surface guidance must update:
- the relevant skill,
- repo README if install/usage changes,
- `docs/development-log.md`.
4. If AlphaEngine adds new public families, prefer adding new bounded skills rather than bloating one generic skill.
