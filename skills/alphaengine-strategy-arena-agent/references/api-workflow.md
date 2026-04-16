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
3. list markets
4. run one or more simulations
5. run evaluations
6. compare scores and diagnostics
7. refine the promising candidates

## Example HTTP Calls

List strategies:

```bash
curl -s "$BASE_URL/v1/families/strategy-arena/strategies" \
  -H "x-api-key: $ALPHAENGINE_API_KEY"
```

Run a simulation:

```bash
curl -s "$BASE_URL/v1/families/strategy-arena/simulations" \
  -H "content-type: application/json" \
  -H "x-api-key: $ALPHAENGINE_API_KEY" \
  -d '{
    "marketId": 1,
    "timeframe": "daily",
    "datasetRef": "dataset-ref",
    "capital": 100000,
    "components": [],
    "executionConfig": {
      "costModel": "none",
      "rebalancePolicy": "bar-close"
    }
  }'
```

Run an evaluation:

```bash
curl -s "$BASE_URL/v1/families/strategy-arena/evaluations" \
  -H "content-type: application/json" \
  -H "x-api-key: $ALPHAENGINE_API_KEY" \
  -d '{
    "marketId": 1,
    "timeframe": "daily",
    "datasetRef": "dataset-ref",
    "capital": 100000,
    "components": [],
    "executionConfig": {
      "costModel": "none",
      "rebalancePolicy": "bar-close"
    }
  }'
```

## Non-Idempotency Note

`POST /simulations` and `POST /evaluations` should be treated as normal compute requests, not as idempotent ledger mutations.
Repeated calls may rerun computation.
