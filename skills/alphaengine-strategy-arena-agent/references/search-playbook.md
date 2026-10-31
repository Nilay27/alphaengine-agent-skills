# Search Playbook

## Adaptive Guidance, Not an Exact Algorithm

Choose an approach that fits the user's question, market observations, preferences and search budget. A useful broad pattern is:

**Understand the market -> explore plausible strategies -> try complementary combinations -> refine promising candidates -> check nearby variations.**

This is an example direction, not a required stage sequence, fixed split of trials, prescribed parameter grid or universal winning portfolio. A user who already has a hypothesis may need focused refinement rather than a fresh broad search.

## Understand Before Computing

- General explanations need no simulation. For a market-specific question, use the cached catalog/series and the [Pendle interpretation guide](pendle-intuition.md). Fetch only missing market/timeframe data, following [API caching and compute rules](api-workflow.md).
- Establish what price/yield series is being analysed, which historical period it covers and whether the question concerns 1H or 1D behaviour. Do not treat a historical snapshot as a live quote.
- State the capital and public API scoring target before computing. Private correlated-market/stress evaluation is a different target whose final score is unknown from these API simulations. Keep capital fixed for comparisons and record any deliberately changed context.
- For an open-ended cross-market task, compare the requested markets with a few informative baselines. Market returns, implied yields and strategy scores answer different questions; do not label a market a winner solely because one raw measure is high.
- Use observations to form diverse hypotheses. Sideways behaviour may motivate mean reversion, trending behaviour may motivate momentum, and expiry may motivate convergence, but these are hypotheses to test, not rules that exclude other categories.

## Broad Exploration and Deeper Refinement

Follow the [component-count rule](../SKILL.md#workflow): search and recommend at most five components by default. A user must explicitly request a larger basket before exploring 6–16 components. Explain the extra search time/CU use, per-component encryption time and submission gas first; keep the expanded search within the agreed budget.

- Discover supported strategies and read parameter schemas only for candidates worth testing. Begin with simple category baselines where useful; surfaced defaults avoid arbitrary initial tweaks. Materialize those defaults before simulation using [candidate validation](candidate-validation.md) in an available runtime or the optional Python helper. Save and deduplicate the complete request, not just parameter overrides.
- Use full simulations plus saved-payload evaluations when comparing `evaluation.data.score`. Summary/trades are alternative views with equal simulation CU cost, not cheaper score shortcuts.
- Compare the early results and diagnostics to decide where the next simulations are most informative. Retain more than one plausible direction rather than tuning only the first good result.
- Try combinations when their exposures, signals or trading patterns plausibly complement each other. Preserve valid weight totals and evaluate the combination; averaging component scores does not establish its score.
- Refine parameters and weights around promising candidates, then test nearby alternatives for sensitivity. Move budget away from branches with repeated weak results, missing features or blocked trades that cannot be resolved by supported parameters.
- Stop when the evidence and requested effort are sufficient. Deeper search should follow the results rather than exhaust every combination.

## Budget, Pacing and Saved Results

- State a finite simulation/time budget suited to the task. Up to 100 unique simulations across all selected markets/timeframes is a useful initial allowance for an open-ended recommendation, not 100 mandatory runs per market. Use much less for a narrow question; accommodate a larger search when the user requests it.
- Explain the budget and relevant component costs briefly before starting. Avoid promising an exact duration: payloads, component counts, evaluations, limits and network latency affect runtime.
- Default to one simulation in flight and pace the combined GET/simulation/evaluation queue under the current CU limits. Concurrent requests are optional, never required to use the full allowance.
- Cache successful market data and canonical simulation/evaluation responses in temporary files. Keep a candidate ledger of the actual computation inputs, returned snapshot/profile identity, score, diagnostics and failures.
- Do not repeat already tested candidates under the same computation settings and dataset/profile context. Keep ordered components intact; exclude correlation-only IDs from duplicate detection. Separate changed snapshots/profiles and relabel comparisons.
- Count unique successful candidates separately from failed attempts, retries and evaluations. Stop at the chosen budget, a meaningful improvement plateau, the requested quality/time goal or a blocking failure; report what was left unexplored.

## Differentiated and Honest Recommendations

Do not publish a canonical winner list, identical starting portfolio or compulsory parameter grid. Let market evidence, the user's goals and intermediate results shape each search. Preserve alternative categories and explain why more testing may change the result.

For beta score comparisons:

- Sort by `evaluation.data.score`; select the best eligible tested candidate and disclose higher-scoring ineligible candidates separately. Diagnose raw utility and `capitalScore` separately. If none are eligible, report that outcome.
- Show eligibility, executed-trade count, drawdown, CVaR, turnover, cost and relevant skipped-trade reasons alongside the score. Few executed entries and many skipped signals constrain the evidence. If a higher score comes with worse diagnostics, explain that tension rather than hiding it or silently inventing another ranking formula.
- Compare identical contexts where possible. Label different markets/timeframes and snapshots explicitly. A single-market candidate score is not the user's overall multi-market leaderboard average.
- Nearby-parameter stability is useful sensitivity evidence, not proof of out-of-sample profitability. Repeated optimisation on one dataset can overfit; do not claim that the highest historical score guarantees future performance.

## Final Recommendation

Return the best among the eligible tested candidates, the selected market/timeframe, tested capital, public API evaluation score, short rationale and trial count. Mention unresolved errors or important coverage/sensitivity limits. Keep the full candidate ledger in the temporary cache; a concise shortlist is enough in the answer.

For a strategy export, return dashboard JSON with the tested `marketKey`, `timeframe` and ordered `components`, including valid `strategyId`, every public parameter in `strategyParams`, and weights totalling `10000`. Export the saved complete request; do not add defaults after testing. Describe metadata validation and simulation acceptance separately from private submission acceptance. The user handles all dashboard interaction; never inspect or control a browser. End with the exact required note in `SKILL.md` about simulation and private correlated-market/stress scoring.
