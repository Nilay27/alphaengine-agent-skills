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
baseUrl = https://api.alphaengine.dev
x-api-key = <real-api-key>
```

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
4. Callers do not submit raw `datasetRef` or dataset component ids in arena mode.
5. Callers may omit `executionConfig`; when supplied in arena mode it is ignored in favor of the server-owned execution profile.
6. Strategy detail and parameter endpoints may surface canonical defaults. When they do, callers may use `strategyParams: {}` for baseline simulations.
7. Some strategies may still fail with `STRATEGY_MISSING_REQUIRED_FEATURE` because the current arena dataset/profile does not provide every required feature family.

## Strategy Discovery Sequence

For a first-time user or agent, the safe public sequence is:
1. `GET /v1/families/strategy-arena`
2. `GET /v1/families/strategy-arena/strategies`
3. `GET /v1/families/strategy-arena/strategies/{strategyId}` or `/parameters`
4. `GET /v1/families/strategy-arena/markets`
5. `POST /v1/families/strategy-arena/simulations/summary`
6. `POST /v1/families/strategy-arena/evaluations`

This avoids assuming internal ids, hidden datasets, or operator knobs.

## Simulation Response Views

1. `POST /simulations`
- returns the full canonical simulation payload
- includes the full per-bar ledger and portfolio series
- use this when you need the full trace

2. `POST /simulations/summary`
- returns the compact comparison view
- best default for broad sweeps, UI cards, and agent loops

3. `POST /simulations/trades`
- returns only event-filtered rows
- includes:
  - executed trades where `turnover != 0`
  - skipped signals where `signalTarget != executedPosition` and no turnover occurred
- use this when you need to inspect why a strategy traded or was blocked

All three execute a fresh simulation run in v1.

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
4. run one or more simulations
5. run evaluations over `simulation.data`
6. compare scores and diagnostics
7. refine the promising candidates

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

Run a full simulation:

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

Run an evaluation:

```bash
curl -s "$BASE_URL/v1/families/strategy-arena/evaluations" \
  -H "content-type: application/json" \
  -H "x-api-key: $ALPHAENGINE_API_KEY" \
  -d '{
    "simulation": { "...": "simulation.data from the prior call" }
  }'
```

## Common Failure Interpretation

1. `REQUEST_VALIDATION_FAILED`
- request body shape is wrong or contains unsupported fields

2. `DATA_DATASET_NOT_FOUND`
- the server could not resolve the official dataset for the selected market/profile

3. `STRATEGY_MISSING_REQUIRED_FEATURE`
- the chosen strategy needs feature families the current arena dataset/profile does not provide
- this is usually a support-gap signal, not a malformed request

4. `INTERNAL_UNEXPECTED`
- the server hit an unexpected runtime issue; retry only after checking deploy/config state

## Non-Idempotency Note

`POST /simulations`, `POST /simulations/summary`, `POST /simulations/trades`, and `POST /evaluations` should be treated as compute requests, not as idempotent ledger mutations.
Repeated calls may rerun computation.
