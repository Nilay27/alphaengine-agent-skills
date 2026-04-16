# CLAUDE.md

This repo publishes shared public agent skills for AlphaEngine.

## Purpose

Keep the actual skill body platform-neutral wherever possible so the same skill folder can be used by:
- Codex
- Claude
- other agents that support the `SKILL.md` + supporting-files pattern

## Rules For This Repo

1. Prefer one shared `SKILL.md` per skill, not separate Claude-vs-Codex copies.
2. Keep platform-specific differences in:
- `README.md` install instructions,
- this `CLAUDE.md`,
- or optional repo-level metadata,
not in duplicated skill logic.
3. Do not add Claude-only frontmatter unless it is clearly needed and does not break portability.
4. Keep public API guidance aligned with the canonical `api-router` contract.
5. Do not teach agents to call private/operator-only AlphaEngine surfaces.
6. Keep the skill a search framework, not a recipe book for converging on identical strategies.

## Current Canonical Skill

The first public skill is:
- `skills/alphaengine-strategy-arena-agent`

It teaches agents to:
- call AlphaEngine's public `api-router`,
- enumerate Pendle yield strategies,
- run simulations and evaluations,
- optimize for `evaluation.data.score`,
- compare diagnostics without assuming a public ranking endpoint.
