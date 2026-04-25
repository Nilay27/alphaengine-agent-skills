# Search Playbook

This skill is a search framework, not a recipe book.

The objective is to help users search intelligently while still leaving room for differentiated outcomes.

## Core Principle

Teach the agent **how to think**, not **what exact strategy to pick**.

## Search Stages

### 1. Broad exploration
- Start with multiple categories.
- Build single-strategy baselines first.
- Avoid spending all early budget on one narrow family of parameter tweaks.

### 2. Early filtering
- Use `score` as the primary beta filter.
- Drop obviously weak, fragile, or high-friction candidates.

### 3. Shortlist refinement
- Inspect parameters of promising candidates more closely.
- Try adjacent parameter choices.
- Try small combinations where appropriate.

### 4. Robustness-oriented comparison
- Prefer candidates that remain attractive across nearby variations.
- Do not overreact to one lucky outlier result.

## Anti-Convergence Rules

Do not:
- hardcode a universal top-10 list,
- publish a canonical winning combo set,
- assume one Pendle category always dominates,
- stop after the first strong score.

Do:
- preserve diversity in the candidate pool,
- test across categories,
- use diagnostics to explain why one candidate is stronger,
- let additional effort produce better outcomes.

## Comparison Heuristics

When two ideas have similar scores, prefer the one with better tradeoffs in:
- drawdown,
- CVaR,
- turnover,
- execution cost,
- eligibility quality.

When one idea has a much higher score but clearly worse frictions or risk diagnostics, surface that tension explicitly rather than hiding it.

## Beta Leaderboard Rule

If a leaderboard or top-candidate list is needed in beta:
- sort by `evaluation.data.score`
- display diagnostics alongside it
- do not introduce cross-submission penalty logic unless the public API explicitly adds it

## Final Recommendation Rule

When the user asks for a final or submit-ready strategy, stop the exploratory report format and return a concise recommendation with paste-ready dashboard JSON.

Use minimal JSON by default:
- `components`
- `strategyId`
- `weightBps`
- `strategyParams`

Only include `marketKey`, `timeframe`, and `config` when the user asks for the full object or when pinning those values prevents ambiguity.
