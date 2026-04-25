---
name: alphaengine-strategy-arena-agent
description: Use AlphaEngine's public strategy-arena API to explore Pendle yield strategies, run simulations and evaluations, refine candidate ideas without converging on one canned recipe, or produce paste-ready beta strategy JSON when a user asks for a final strategy, submission, best strategy, or JSON to submit. Use when an agent should query the public AlphaEngine router directly with an API key and search for promising strategies or combinations.
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
- You need the public base URL and a valid `x-api-key`.
- Use only the public HTTP API surface.

2. Enumerate the current search space.
- Read families.
- Read strategy-arena metadata.
- List strategies.
- Inspect strategy details and parameter schemas for candidates you plan to test.
- Read markets before fixing a simulation hypothesis.
- The current public simulation request requires `marketId`, so the agent must obtain it from `GET /v1/families/strategy-arena/markets`.
- Do not hardcode `marketId` values. For user-facing dashboard output, map the chosen market to `marketKey` if you decide to include it.

3. Build broad initial hypotheses.
- Start from multiple strategy categories.
- Do not spend the first budget only on tiny parameter tweaks of one idea.
- If strategy details surface defaults, treat `strategyParams: {}` as the baseline request shape rather than inventing arbitrary first-pass parameters.
- For a single-strategy baseline, use `weightBps = 10000`.

4. Simulate.
- Use the public simulation endpoints to test concrete candidate requests.
- Prefer `/simulations/summary` for broad sweeps and quick comparison.
- Use `/simulations/trades` when you need event-level trade and skipped-signal inspection.
- Use full `/simulations` when you need the full ledger and portfolio trace or when you plan to run `/evaluations` next.
- Current arena mode is server-owned: callers submit only public simulation inputs and the server resolves dataset, component, execution, and scoring details internally.

5. Evaluate.
- Use the public evaluation endpoint only after a full simulation call.
- Post `{"simulation": simulation.data}` from the full `/simulations` response.
- Do not post `/simulations/summary` or `/simulations/trades` payloads to `/evaluations`.
- Treat `evaluation.data.score` as the beta primary sort key. It is the public scaled leaderboard score; raw utility remains a diagnostic under the scenario result.

6. Compare with diagnostics.
- Check score first.
- Then inspect annualized return, drawdown, CVaR, turnover, execution cost, and eligibility.
- If a strategy produced signals but no trades, inspect skipped-signal diagnostics rather than assuming the strategy is broken.

7. Refine without collapsing the search.
- Narrow only after broad exploration.
- Prefer robustness over one lucky score.
- When a strategy fails with `STRATEGY_MISSING_REQUIRED_FEATURE`, treat that as a current arena support gap rather than a malformed request.

## Final Strategy Output Mode

Use this mode whenever the user asks for a submit-ready idea, including phrasing like:
- "give me a strategy",
- "give me a submission",
- "what should I submit",
- "final strategy",
- "best strategy",
- "pasteable JSON",
- "strategy for beta",
- "give me the JSON",
- "ready to submit",
- "what should I put in AlphaEngine".

In this mode, produce:
1. a short rationale,
2. the recommended market in text when relevant,
3. one fenced `json` block,
4. an instruction to paste the JSON into `beta.alphaengine.trade`, click simulate, review the UI-filled defaults, and submit.

Prefer minimal dashboard JSON unless the user asks for a full object or the market/defaults must be pinned:

```json
{
  "components": [
    {
      "strategyId": "yield-rsi",
      "weightBps": 10000,
      "strategyParams": {}
    }
  ]
}
```

The beta UI self-validates and can fill `marketKey`, `timeframe`, and `config` when omitted. If you include a full object, use dashboard shape (`marketKey`, `timeframe`, `components`, `config`), not the public API simulation shape (`marketId`, `capital`).

## Hard Rules

1. Do not invent unsupported endpoints.
2. Do not assume a public ranking endpoint exists.
3. Do not claim one category is always superior.
4. Do not treat this skill as a recipe book.
5. Use score as the beta leaderboard key, not subjective preference.
6. Use diagnostics to explain tradeoffs, not to override score without reason.
7. Do not assume caller-owned execution or scoring knobs are active in current arena mode.
8. In Final Strategy Output Mode, ensure component `weightBps` values sum to `10000` and each component includes `strategyId`, `weightBps`, and `strategyParams`.

## Current Arena Mode Assumptions

1. Public competition simulation is daily-only.
2. The server resolves the official dataset internally.
3. The server resolves the official execution profile internally.
4. The server resolves the official scoring window internally.
5. Strategy defaults may be surfaced publicly; when they are, `strategyParams: {}` is a valid baseline request shape.
6. Some strategies may still fail with `STRATEGY_MISSING_REQUIRED_FEATURE` because the current arena dataset/profile does not provide every required feature family.
7. Current beta markets may include `susde`, `susdf`, and `ghousd`, but agents must discover live markets from the API because IDs and availability can change.

## Output Expectations

For exploratory use, produce:
1. the tested hypothesis set,
2. simulation/evaluation results for each candidate,
3. the top candidates sorted by `score`,
4. a short explanation of why the leading candidates are strong,
5. obvious caveats such as high turnover, poor eligibility, blocked trades, or fragile diagnostics.

For final strategy requests, switch to Final Strategy Output Mode and keep the answer centered on the paste-ready dashboard JSON.
