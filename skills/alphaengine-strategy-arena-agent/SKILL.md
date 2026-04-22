---
name: alphaengine-strategy-arena-agent
description: Use AlphaEngine's public strategy-arena API to explore Pendle yield strategies, run simulations and evaluations, and refine candidate ideas without converging on one canned recipe. Use when an agent should query the public AlphaEngine router directly with an API key and search for promising strategies or combinations.
---

# AlphaEngine Strategy Arena Agent

Use this skill when an agent should work against AlphaEngine's public `strategy-arena` API.

## Required Context

Read these files first:
1. `references/api-workflow.md`
2. `references/search-playbook.md`

Read `references/pendle-intuition.md` when:
- selecting initial hypotheses,
- explaining why a category may matter,
- or reasoning about PT/YT behavior and Pendle-specific opportunity structure.

## Workflow

1. Confirm router access.
- You need a base URL and a valid `x-api-key`.
- Use only the public HTTP API surface.

2. Enumerate the current search space.
- Read families.
- Read strategy-arena metadata.
- List strategies.
- Inspect strategy details and parameter schemas for candidates you plan to test.
- Read markets before fixing a simulation hypothesis.
- The current public simulation request requires `marketId`, so the agent must obtain it from `GET /v1/families/strategy-arena/markets`.

3. Build broad initial hypotheses.
- Start from multiple strategy categories.
- Do not spend the first budget only on tiny parameter tweaks of one idea.
- If strategy details surface defaults, treat `strategyParams: {}` as the baseline request shape rather than inventing arbitrary first-pass parameters.

4. Simulate.
- Use the public simulation endpoints to test concrete candidate requests.
- Prefer `/simulations/summary` for broad sweeps and quick comparisons.
- Use `/simulations/trades` when you need event-level trade and skipped-signal inspection.
- Use full `/simulations` only when you need the full ledger and portfolio trace.
- Current arena mode is server-owned: callers do not supply raw `datasetRef`, dataset component ids, or authoritative execution/scoring knobs.

5. Evaluate.
- Use the public evaluation endpoint after simulation.
- Post `{"simulation": simulation.data}`.
- Treat `evaluation.data.score` as the beta primary sort key.

6. Compare with diagnostics.
- Check score first.
- Then inspect annualized return, drawdown, CVaR, turnover, execution cost, and eligibility.

7. Refine without collapsing the search.
- Narrow only after broad exploration.
- Prefer robustness over one lucky score.
- When a strategy fails with `STRATEGY_MISSING_REQUIRED_FEATURE`, treat that as “not runnable on the current arena dataset/profile” unless the user explicitly wants to investigate feature support.

## Hard Rules

1. Do not invent unsupported endpoints.
2. Do not assume a public ranking endpoint exists.
3. Do not claim one category is always superior.
4. Do not treat this skill as a recipe book.
5. Use score as the beta leaderboard key, not subjective preference.
6. Use diagnostics to explain tradeoffs, not to override score without reason.
7. Do not send raw `datasetRef` or dataset component ids in current arena mode.
8. Do not assume caller-owned execution/scoring knobs are active in current arena mode.

## Current Arena Mode Assumptions

1. Public competition simulation is daily-only.
2. The server resolves the official dataset internally.
3. The server resolves the official execution profile internally.
4. The server resolves the official scoring window internally.
5. Strategy defaults may be surfaced publicly; when they are, `strategyParams: {}` is a valid baseline request shape.
6. Some strategies may still fail with `STRATEGY_MISSING_REQUIRED_FEATURE` because the current arena dataset/profile does not provide every required feature family.

## Output Expectations

When using this skill, produce:
1. the tested hypothesis set,
2. simulation/evaluation results for each candidate,
3. the top candidates sorted by `score`,
4. a short explanation of why the leading candidates are strong,
5. obvious caveats such as high turnover, poor eligibility, or fragile diagnostics.
