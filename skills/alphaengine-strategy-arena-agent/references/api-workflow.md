# API Workflow

Use AlphaEngine's public router directly.

## Auth

Every `/v1/**` request requires:
- header: `x-api-key`

The skill assumes the user provides:
- `baseUrl`
- `apiKey`

Example:

```text
baseUrl = https://api-router.alphaengine.trade
x-api-key = <real-api-key>
```

Plain-language auth failures:
- `401` means the key is missing or invalid.
- `403` means the key is valid, but inactive or missing the required scope.

## Supported Endpoints

Use only these public routes unless the router adds more and this repo is updated:

- `GET /v1/families`
- `GET /v1/families/strategy-arena`
- `GET /v1/families/strategy-arena/strategies`
- `GET /v1/families/strategy-arena/strategies/{strategyId}`
- `GET /v1/families/strategy-arena/strategies/{strategyId}/parameters`
- `GET /v1/families/strategy-arena/markets`
- `POST /v1/families/strategy-arena/simulations`
- `POST /v1/families/strategy-arena/simulations/summary`
- `POST /v1/families/strategy-arena/simulations/trades`
- `POST /v1/families/strategy-arena/evaluations`

Do not assume any public endpoint exists for:
- live on-chain execution,
- listener/operator control,
- ranking tournaments,
- private data-plane or decrypt-for-tx workflows.

## Response Shape

Successful responses use this envelope:

```json
{
  "requestId": "...",
  "status": "ok",
  "data": {}
}
```

Error responses use RFC 9457 problem details with AlphaEngine extensions such as:
- `code`
- `family`
- `requestId`
- `fieldErrors` when relevant

## Current Arena Request Semantics

1. Current public competition simulation is daily-only.
2. Callers submit:
- `marketId`
- `timeframe`
- `capital`
- `components`
3. `marketId` is discovered from `GET /v1/families/strategy-arena/markets`.
4. `timeframe` should be sent as `"daily"` for clarity.
5. `capital` must be sent as a decimal string, for example `"100000"`, not as a JSON number.
6. `components` is an array of strategy sleeves. For a single-strategy baseline, use one component with `weightBps: 10000`.
7. `strategyParams` should still be sent as an object. When strategy defaults are surfaced publicly, `strategyParams: {}` is the correct default baseline request.
8. Callers do not submit internal dataset or component identifiers in arena mode; the server resolves those internally.
9. Callers may omit `executionConfig`; when supplied in arena mode it is ignored in favor of the server-owned execution profile.
10. `submissionId` is optional correlation metadata only; it does not make simulations idempotent.
11. Some strategies may still fail with `STRATEGY_MISSING_REQUIRED_FEATURE` because the current arena dataset/profile does not provide every required feature family.

## Strategy Discovery Sequence

For a first-time user or agent, the safe public sequence is:
1. `GET /v1/families/strategy-arena`
2. `GET /v1/families/strategy-arena/strategies`
3. `GET /v1/families/strategy-arena/strategies/{strategyId}` or `/parameters`
4. `GET /v1/families/strategy-arena/markets`
5. `POST /v1/families/strategy-arena/simulations/summary`
6. `POST /v1/families/strategy-arena/simulations`
7. `POST /v1/families/strategy-arena/evaluations`

This avoids assuming internal ids, hidden datasets, or operator knobs.

## Simulation Response Views

1. `POST /simulations`
- returns the full canonical simulation payload
- includes the full per-bar ledger and portfolio series
- use this when you need the full trace
- use this before calling `/evaluations`

2. `POST /simulations/summary`
- returns the compact comparison view
- best default for broad sweeps, UI cards, and agent loops
- includes metrics, execution diagnostics, and resolved profile metadata
- does not include bar-by-bar ledgers or portfolio series

3. `POST /simulations/trades`
- returns only event-filtered rows
- includes:
  - executed trades where `turnover != 0`
  - skipped signals where `signalTarget != executedPosition` and no turnover occurred
- use this when you need to inspect why a strategy traded or was blocked

## Official Arena Execution Profile

Current public arena runs use a server-owned execution profile. The important current values are:
- `fillRule = close`
- `feeBps = 2`
- `slippageBps = 0`
- `positionMode = long_only`
- `maxAbsPosition = 1`
- `initialPosition = 0`
- `ammExecutionMode = pool_state`
- `ammAdjustmentBps = 0`
- `maxEstimatedSlippageBps = 100`
- `maxTradeNotional = capital`
- `maxTradePctLiquidity = 0.05`
- `minHoldBars = 3`
- `minEdgeToCostRatio = 2.5`

Plain-language meaning for non-DeFi-native users:
- the system only trades long, not short
- the system assumes close-price fills for current public arena mode
- a trade can be skipped if the estimated slippage is too high
- a trade can be skipped if it would be too large relative to the pool liquidity proxy
- a strategy can generate a signal and still not trade because the guardrails veto the trade
- a position may be held through a signal change if the minimum hold period or edge-vs-cost hurdle says churn is not worth it

## Skipped Signals And Trade Diagnostics

A signal is not the same thing as an executed trade.

Important places to inspect:
- `summary.result.componentRuns[].executionDiagnostics`
- `summary.result.componentRuns[].executionDiagnostics.skippedByReason`
- `trades.result.componentRuns[].events`
- `eventKind = "skipped_signal"`

If a strategy produces signals but few or zero trades, that often means the official guardrails blocked the proposed trades rather than the strategy producing no signal at all.

## Official Scoring Window

Current public arena scoring is server-owned.

The current policy is:
- the full dataset is used for signal warmup
- the scored window is the last 30 bars, or the full dataset if it is shorter than 30 bars

Important interpretation points:
- full simulation traces may include warmup bars before the scored window
- evaluation trims to the scored window internally
- `resolvedScoringProfile` tells you:
  - `totalBars`
  - `warmupBars`
  - `scoredBars`
  - `tradeStartIndex`
  - `scoreStartTimestamp`
  - `scoreEndTimestamp`

## Beta Scoring Rule

For strategy comparisons in beta:
- primary sort key: `evaluation.data.score`

Important diagnostics to inspect alongside score:
- `annualizedMeanReturn`
- `maxDrawdown`
- `cvar`
- `turnover`
- `executionCost`
- `eligibility`
- `capitalScore`

Use `capitalScore` as a secondary diagnostic, not the primary leaderboard key, unless the user explicitly asks for a stricter evidence-oriented ranking.

## Example Sequence

1. list strategies
2. inspect parameters for a shortlist
3. list markets and choose a public `marketId`
4. run broad comparisons with `/simulations/summary`
5. rerun shortlisted candidates with full `/simulations`
6. post the full `simulation.data` into `/evaluations`
7. compare scores and diagnostics
8. refine the promising candidates

## Example HTTP Calls

List strategies:

```bash
curl -s "$BASE_URL/v1/families/strategy-arena/strategies" \
  -H "x-api-key: $ALPHAENGINE_API_KEY"
```

List markets and get a usable `marketId`:

```bash
curl -s "$BASE_URL/v1/families/strategy-arena/markets" \
  -H "x-api-key: $ALPHAENGINE_API_KEY"
```

Run a compact simulation for a baseline sweep:

```bash
curl -s "$BASE_URL/v1/families/strategy-arena/simulations/summary" \
  -H "content-type: application/json" \
  -H "x-api-key: $ALPHAENGINE_API_KEY" \
  -d '{
    "marketId": 1,
    "timeframe": "daily",
    "capital": "100000",
    "components": [
      {
        "strategyId": "yield-rsi",
        "strategyParams": {},
        "weightBps": 10000
      }
    ]
  }'
```

Run a full simulation for one shortlisted candidate:

```bash
curl -s "$BASE_URL/v1/families/strategy-arena/simulations" \
  -H "content-type: application/json" \
  -H "x-api-key: $ALPHAENGINE_API_KEY" \
  -d '{
    "marketId": 1,
    "timeframe": "daily",
    "capital": "100000",
    "components": [
      {
        "strategyId": "yield-rsi",
        "strategyParams": {},
        "weightBps": 10000
      }
    ]
  }'
```

Run an evaluation using the full simulation payload:

```bash
curl -s "$BASE_URL/v1/families/strategy-arena/evaluations" \
  -H "content-type: application/json" \
  -H "x-api-key: $ALPHAENGINE_API_KEY" \
  -d '{
    "simulation": { "...": "full simulation.data from the prior /simulations call" }
  }'
```

## Common Failure Interpretation

1. `REQUEST_VALIDATION_FAILED`
- request body shape is wrong or contains unsupported fields
- common causes include sending numbers instead of strings for decimal fields like `capital`

2. `DATA_DATASET_NOT_FOUND`
- the server could not resolve the official dataset for the selected market/profile
- this is a server dataset/config issue, not usually a caller mistake

3. `STRATEGY_MISSING_REQUIRED_FEATURE`
- the chosen strategy needs feature families the current arena dataset/profile does not provide
- this is usually a support-gap signal, not a malformed request

4. `INTERNAL_UNEXPECTED`
- the server hit an unexpected runtime issue; retry only after checking deploy/config state

## Non-Idempotency Note

`POST /simulations`, `POST /simulations/summary`, `POST /simulations/trades`, and `POST /evaluations` should be treated as compute requests, not as idempotent ledger mutations.
Repeated calls may rerun computation.
