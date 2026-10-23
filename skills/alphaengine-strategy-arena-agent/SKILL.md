---
name: alphaengine-strategy-arena-agent
description: Explore AlphaEngine Pendle markets and hourly or daily strategies through public APIs. Use for market explanations, bounded simulation and evaluation searches, or paste-ready beta strategy JSON. Analyse cached market data and refine diverse candidates without prescribing one winning recipe.
---

# AlphaEngine Strategy Arena Agent

Use public AlphaEngine HTTP surfaces for market understanding and strategy exploration.

## Choose the Work Needed

- For general explanations, answer without network requests when current data is unnecessary. Read [Pendle intuition](references/pendle-intuition.md) as needed.
- For a particular market's behaviour, read the public GET/caching sections of [API workflow](references/api-workflow.md), fetch only the missing catalog/series and analyse the cached observations. Do not automatically start a simulation search.
- For strategy recommendations, read [API workflow](references/api-workflow.md) for endpoints, auth, caching, compute costs and failures, then [search playbook](references/search-playbook.md) for adaptive exploration.

## Workflow

1. Establish the task and access.
   - Respect the requested market, timeframe and effort. Both `hourly` (1H) and `daily` (1D) are supported; hourly is the server default. Send the selected timeframe explicitly.
   - Public BFF market GETs need no key. Simulations/evaluations use a confirmed public router base URL and the user's `x-api-key`; follow the API reference's connectivity checks and credential boundaries.

2. Discover only what is needed and cache it.
   - Read the market catalog once when discovery is needed; obtain router `marketId` values rather than hardcoding IDs.
   - Fetch a historical series once per selected market/timeframe, save the complete response in a temporary directory, and reuse it throughout the search. No market GET inside candidate loops.
   - Cache strategy metadata and parameter schemas too. Fetch details for candidates you plan to test, not every detail on every iteration.
   - Retain dataset/snapshot metadata and observation dates. Refresh only for missing data, another market/timeframe, an explicit update, or evidence that the dataset changed; keep different snapshots separate.

3. Form market-specific hypotheses.
   - Analyse the cached market's price/yield behaviour and available context before selecting candidates. Distinguish historical observations from live prices and PT price from implied yield/APY.
   - Broad exploration of plausible categories, simple baselines, combinations and deeper refinement is useful guidance, not an exact required algorithm or fixed recipe.
   - Do not assume recent market strength implies the highest strategy score, or eliminate entire categories solely from a trend label.

4. Search within a finite budget.
   - State a budget suited to the request; up to 100 unique simulations across the task is a reasonable initial search, not a server quota or a target that must be exhausted.
   - Start with one simulation in flight, pace all authenticated requests within the shared compute budget, and deduplicate tested requests. See the API reference for exact limits.
   - Use surfaced defaults (`strategyParams: {}` when supported) for initial baselines; a single component has `weightBps: 10000`.
   - When comparing official scores, run full `/simulations` once per candidate, save the response, then post `{ "simulation": simulation.data }` to `/evaluations`.
   - Full, summary and trades views have the same simulation compute cost. Use compact views only when their diagnostics suffice; do not rerun identical work just to switch views.

5. Compare and refine adaptively.
   - Sort tested candidates by `evaluation.data.score`, then explain drawdown, CVaR, turnover, costs, eligibility and skipped-trade diagnostics.
   - Explore combinations and parameter neighbourhoods where results justify more work, while retaining alternative hypotheses. Test nearby variations to identify fragile outliers.
   - Stop at the chosen budget, sufficient evidence, diminishing improvements or a blocking failure. Go deeper when the user's requested effort supports it; never start an unbounded loop.
   - Report typed errors and incomplete searches honestly. Honour bounded rate-limit retries; do not repeatedly retry invalid, unsupported or inherently over-budget requests.

## Final Strategy Output Mode

When the user asks what to submit, for the best strategy found, or for paste-ready JSON, return:

1. the selected market/timeframe, best tested score and a short rationale;
2. the number of unique simulations performed and material limitations;
3. one dashboard-compatible JSON block with the tested `marketKey` and `timeframe` pinned;
4. an instruction to paste it into `beta.alphaengine.trade`, simulate, review and submit themselves.

Illustrative shape only; discover the market and validate strategy parameters before recommending it:

```json
{
  "marketKey": "susde",
  "timeframe": "hourly",
  "components": [
    {
      "strategyId": "yield-rsi",
      "weightBps": 10000,
      "strategyParams": {}
    }
  ]
}
```

Use the selected `daily` timeframe instead when that is what was tested. Each component needs `strategyId`, `weightBps` and `strategyParams`; weights must sum to `10000`. The dashboard can fill `config`; do not invent settings that suggest overriding the official server-owned profile. API request fields (`marketId`, string `capital`) are distinct from dashboard JSON.

## Hard Rules

- Use documented public endpoints only. No private/operator modules, wallet signing or automatic on-chain submission.
- Keep API keys out of prompts, repository files, URLs and cached responses; send them only to the confirmed router origin.
- Official datasets, execution and scoring profiles remain server-owned. Cached chart analysis is hypothesis generation, not a replacement official score.
- Both timeframes use their returned `resolvedDataset`, `resolvedExecutionProfile` and `resolvedScoringProfile`; do not hardcode scoring windows or treat hourly bars as days.
- Do not invent a cross-submission ranking API or a new scoring formula. Public BFF market reads supplement the authenticated router workflow.
- Do not present one category or parameter set as universally superior. Say "best among the candidates tested", with no guarantee of future performance.

## Exploratory Output

Summarise the hypotheses, dataset period, trials used, top scored candidates, diagnostics and what deeper work might resolve. Keep complete per-candidate results in temporary files rather than flooding the answer. If connectivity or authentication blocks computation, offer only clearly labelled market analysis or untested ideas, not fabricated scores.
