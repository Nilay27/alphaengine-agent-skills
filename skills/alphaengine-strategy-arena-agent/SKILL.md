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
- Inspect parameter schemas for candidates you plan to test.
- Read markets before fixing a simulation hypothesis.

3. Build broad initial hypotheses.
- Start from multiple strategy categories.
- Do not spend the first budget only on tiny parameter tweaks of one idea.

4. Simulate.
- Use the public simulation endpoint to test concrete candidate requests.
- Keep requests valid and explicit.

5. Evaluate.
- Use the public evaluation endpoint after simulation.
- Treat `evaluation.data.score` as the beta primary sort key.

6. Compare with diagnostics.
- Check score first.
- Then inspect annualized return, drawdown, CVaR, turnover, execution cost, and eligibility.

7. Refine without collapsing the search.
- Narrow only after broad exploration.
- Prefer robustness over one lucky score.

## Hard Rules

1. Do not invent unsupported endpoints.
2. Do not assume a public ranking endpoint exists.
3. Do not claim one category is always superior.
4. Do not treat this skill as a recipe book.
5. Use score as the beta leaderboard key, not subjective preference.
6. Use diagnostics to explain tradeoffs, not to override score without reason.

## Output Expectations

When using this skill, produce:
1. the tested hypothesis set,
2. simulation/evaluation results for each candidate,
3. the top candidates sorted by `score`,
4. a short explanation of why the leading candidates are strong,
5. obvious caveats such as high turnover, poor eligibility, or fragile diagnostics.
