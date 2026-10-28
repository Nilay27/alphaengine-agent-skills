# API Workflow

## Public Surfaces and Authentication

Use separate bases:

- `BFF_BASE_URL=https://beta.alphaengine.trade`: public market reads below, with no API key or Privy token.
- `ROUTER_BASE_URL=https://api-router.alphaengine.trade`: the public router base. All `/v1/**` routes require the user's `x-api-key`.

The custom hostname is live over verified HTTPS, with CloudFront and Caddy forwarding requests to the API router. Use this documented hostname for agent compute; do not automatically switch origins on failure or forward credentials across redirects. Existing account keys remain valid when upgrading from the earlier CloudFront base. A DNS/TLS/network failure is not API-key rejection: stop compute and explain the failing base. Never work around it through anonymous dashboard POSTs, private service addresses or operator endpoints.

Use an environment variable or the host's secret mechanism for the key; never ask the user to paste it into chat, embed it in files or log it. Send it only to the confirmed router origin, not to the BFF GETs. Do not forward credentials across redirects.

This skill has no browser workflow. Never inspect or control tabs, log in, click settings, or submit through a UI. The user performs dashboard actions. Public documentation may be fetched over HTTP.

### Obtaining or Replacing the User's Key

- When compute needs a key and none is configured, provide [AlphaEngine API-key settings](https://beta.alphaengine.trade/#profile/api-key). The direct route opens Profile -> Settings -> API keys; the user signs in themselves if needed. On a dashboard version predating this route, follow those tabs manually.
- With no active key, click **Generate**, then **Copy** and save it in the agent host's secure secret/configuration input (for example `ALPHAENGINE_API_KEY`). Ask the user to complete that setup and then resume. Do not ask for the value in ordinary chat or automate their login.
- The full key is shown only when generated and cannot be retrieved later. If hidden, keep using an already saved valid key. If it was not saved or is invalid, the user can click **Regenerate** anytime, copy the replacement once, and update the configuration to continue.
- Only one key is active per account. Regenerating replaces the old key immediately; every agent, script or service using the old value must be updated. **Disable Key** revokes access. Do not regenerate a working saved key merely because the dashboard masks it.
- For `AUTH_INVALID_API_KEY`, first check the local configuration has the full key rather than the masked prefix. If still rejected, link the user to the same settings to regenerate and securely configure the replacement. Missing keys need setup; DNS/network failures, 429 limits and missing-scope errors have different remedies below and should not trigger key rotation.

For concrete macOS Keychain and Windows PowerShell instructions, read [private credential setup](credential-setup.md). Load the key in the actual API client's process, check only accessibility, and perform the small access preflight there. A successful catalog GET verifies authentication/read access; compute scopes remain independently enforced.

### Public BFF Market Reads

| Method and path | Purpose |
|---|---|
| `GET /api/app/markets` | Market catalog, metadata and `availableTimeframes` |
| `GET /api/app/market-series?marketKey={key}&timeframe={timeframe}` | Historical chart series; `hourly` or `daily` |

These reads have no BFF per-user HTTP rate limiter. The fetch-once rules below reduce agent requests; they are not an enforced server quota.

Successful responses have `{ "requestId": "...", "status": "ok", "data": ... }`:

- Markets: `data.markets[]` includes `key`, `marketId`, `chainId`, `marketAddress`, `name`, `symbol`, `expiry`, `datasetRef`, and `availableTimeframes`.
- Series: `data` includes `market`, `timeframe`, `available`, `datasetRef`, `snapshotHash`, and `chart[]` points (`timestamp`, `open`, `high`, `low`, `close`, `volume`, `apy`).
- `available: false` with an empty chart means that timeframe has no chart dataset. Do not silently substitute another timeframe or repeatedly fetch the same unavailable series.
- BFF errors use `{ "requestId": "...", "status": "error", "error": { "code": "...", "message": "..." } }`, not router problem details.

### Authenticated Router Routes

Every route below requires `x-api-key` and the appropriate scope:

| Routes | Scope |
|---|---|
| `GET /v1/families` | `strategy:read` |
| `GET /v1/families/strategy-arena` | `strategy:read` |
| `GET /v1/families/strategy-arena/strategies` | `strategy:read` |
| `GET /v1/families/strategy-arena/strategies/{strategyId}` | `strategy:read` |
| `GET /v1/families/strategy-arena/strategies/{strategyId}/parameters` | `strategy:read` |
| `GET /v1/families/strategy-arena/markets` | `strategy:read` |
| `POST /v1/families/strategy-arena/simulations` | `strategy:simulate` |
| `POST /v1/families/strategy-arena/simulations/summary` | `strategy:simulate` |
| `POST /v1/families/strategy-arena/simulations/trades` | `strategy:simulate` |
| `POST /v1/families/strategy-arena/evaluations` | `evaluation:run` |

Router successes use the same `status: "ok"` envelope. Router market `data` is an array with `marketId`, `marketKey`, `chainId`, `protocol`, and `marketAddress`, unlike the BFF's `data.markets` object. Discover the router mapping once for simulation; match market identity using chain/address and the key, not array position or a guessed numeric ID. BFF `key` is the dashboard `marketKey`.

Router failures use RFC 9457 `application/problem+json`, with typed `code`, `requestId`, and sometimes `fieldErrors`/`family`. Inspect status and structured codes rather than parsing message text.

## Fetch Once and Reuse

1. Reuse an existing valid temporary cache for the current task. General explanations need no GET; historical analysis needs only the relevant catalog/series. Read-only analysis can proceed without a simulation API key.
2. When data is missing, fetch the catalog once and the selected historical series once per market/timeframe. Fetch additional markets only if the task calls for comparison. Cache router catalogs and parameter schemas too.
3. Save complete successful JSON responses in a task-specific temporary directory, not a repository. Keep a small manifest with source base, market key/ID, timeframe, fetch time, dataset reference, snapshot hash and observation period. Do not put credentials or request headers in it.
4. Perform trend/indicator analysis and generate all candidate hypotheses from these local files. Do not put market GETs inside a simulation loop. Fetch again only for missing/corrupt data, a different market/timeframe, an explicit refresh, or evidence that the dataset changed.
5. Store full simulation/evaluation responses and complete candidate inputs alongside the analysis. Resolve defaults before deduplication, so omitted defaults and the same explicit defaults do not become separate trials. Deduplicate using the computation inputs: router base, market, timeframe, capital, ordered components/weights/parameters, relevant request settings and deterministic seed if used. Ignore correlation-only `submissionId`; preserve component order, because execution may depend on it. Canonicalize object keys and reject non-finite numbers before hashing.
6. Bind saved results to returned `resolvedDataset.snapshotHash` and execution/scoring profile metadata. Never mix results from different snapshots/profiles as an identical replay. If chart and simulation snapshots differ, label the chart analysis separately and use the simulation's metadata for score comparisons. If a change is detected mid-search, separate the cohorts or rerun a shortlist within the remaining budget.

A repeated local analysis, parameter calculation or comparison needs no GET. A local cache does not pin the backend dataset: each new simulation resolves the official server dataset.

## Hourly and Daily Requests

- Both `"hourly"` (1H) and `"daily"` (1D) are supported. Hourly is the current server default, but always send the chosen value explicitly.
- Check BFF `availableTimeframes` before requesting a series. Treat unavailable data as unavailable, not as permission to change timeframe silently.
- Required simulation fields: `marketId` (discovered integer), `timeframe`, `capital` (positive decimal string such as `"100000"`) and `components`.
- Each component has `strategyId`, object `strategyParams` and positive integer `weightBps`; weights sum to `10000`. Although the API accepts omitted defaulted values, this skill always fills every public parameter before simulation. Use the helper below and the cached metadata's actual `min`/`max`/`enum` constraint fields.
- State the tested capital before searching. Use requested capital or disclose the assumption, then hold it fixed across comparisons. Capital and per-component allocations affect notional size, slippage and guardrail skips; do not silently lower capital or override guardrails to obtain a better score. Explain allocation-driven changes in execution.
- Callers do not supply raw datasets or internal dataset component IDs. The server resolves its official dataset, execution and scoring profiles. Supplied `executionConfig` does not override the official arena execution profile; omit it for ordinary searches.
- Use returned `resolvedDataset` for the snapshot and dates, `resolvedExecutionProfile` for actual fills/costs/guardrails, and `resolvedScoringProfile` for `totalBars`, `warmupBars`, `scoredBars`, `tradeStartIndex`, `scoreStartTimestamp` and `scoreEndTimestamp`.
- Full traces may contain warmup bars; evaluation scores the returned official window. Do not hardcode warmup/scored bar counts. Windows and holding periods measured in bars have different elapsed durations on 1H versus 1D.
- Scanning the same historical snapshot repeatedly is parameter search, not new out-of-sample evidence. Keep hourly and daily comparisons labelled separately.

## Compute Units, Concurrency and Pacing

Default limits, checked against the router policy:

| Operation or limit | Default |
|---|---:|
| Shared allowance per API key | 50 CU per fixed one-second window |
| Authenticated GET | 1 CU |
| Any simulation view | 10 CU per component |
| Evaluation | 1 CU |
| Simultaneous simulation requests | 2 |
| Simultaneous evaluation requests | 4 |

- Reads, simulations and evaluations share the same allowance. Limits are per key and currently maintained in memory per router process; they are not a global account or cross-replica quota. Key-specific configured limits may differ. No daily, hourly or lifetime quota is currently defined by this limiter.
- Full, summary and trades simulations all execute the simulation. Summary reduces response size, not CU or simulation work. Each evaluation request also consumes compute; save its result.
- A full simulation plus evaluation costs `10 * componentCount + 1`: 11 CU for one component, 31 for three and 41 for four. Two three-component simulations in the same window need 60 CU and exceed the default allowance, even if concurrency permits two.
- Five components consume all 50 CU; evaluation or catalog reads must use a later window if no allowance remains. More than five components cost over 50 CU in one request and cannot succeed under the default limit merely by waiting. Explain the constraint and propose a smaller combination, not silent truncation or endless retries.
- Default agent behaviour: one simulation in flight, a local queue/accounting of all authenticated request costs, and pacing below the shared ceiling. A conservative option is at most one simulation/evaluation pair per second for up to four components, with discovery completed beforehand; reserve a later window for a five-component evaluation.
- Concurrency ceilings are limits, not targets. Include retries in the task's finite request/time budget, and do not create more keys or switch routes to evade limits.

## Simulation Views and Evaluation

- `/simulations`: full canonical ledger/portfolio output. When scoring candidates, call this once, save it, and send `{ "simulation": simulation.data }` to `/evaluations`.
- `/simulations/summary`: compact metrics/diagnostics; useful when those alone answer the question. It cannot be submitted to `/evaluations`.
- `/simulations/trades`: trade/skipped-signal events. Use only if event diagnostics are needed and not already derivable from saved full results. It cannot be submitted to `/evaluations`.

For beta score comparisons, prefer full simulation plus evaluation directly rather than summary followed by an identical full rerun. Treat these POSTs as compute requests: repeated calls may rerun computation, and `submissionId` is correlation metadata, not an idempotency key.

The primary comparison key is `evaluation.data.score` (the returned benchmark-adjusted score). Raw utility and `capitalScore` are separate diagnostics, not substitute primary scores. Explain eligibility, return, drawdown, CVaR, turnover and execution costs from the returned evaluation. Do not rewrite the scoring formula locally.

### Score Provenance

Label that number **public API evaluation score** from the start of the search. It evaluates one supplied simulation on its resolved dataset/window. Private official evaluation uses hidden correlated-market, perturbation and stress scenarios; the public score is not a prediction of that final result. See [scoring and benchmarks](https://docs.alphaengine.trade/arena/scoring-and-benchmarks).

Persist the score source, simulation/output identity, complete tested request, capital, dataset hash and resolved profiles together. Sensitivity on the visible dataset is useful but does not reproduce private stress evaluation. No documented public route here retrieves a completed private submission report. If a user's score differs, compare saved inputs and available reports, distinguish facts from hypotheses, and leave the precise cause unresolved without the relevant evidence. Do not inspect their browser or invent access to private/operator services.

A signal may be vetoed by guardrails: inspect `result.componentRuns[].executionDiagnostics`, including `skippedByReason`; trades views additionally expose `eventKind: "skipped_signal"`. Read the resolved profile rather than assuming that every signal trades or changing official execution settings to force a fill.

## HTTP Examples

This optional Bash recipe uses `curl`, `jq`, the Python 3 helper and a real key loaded securely outside chat. The skill does not require these tools or Python: use the host's available HTTP/JSON tools and the same [candidate validation rules](candidate-validation.md). Native Windows PowerShell can make HTTP requests and process JSON without Python; see credential setup. Commands write task data only to temporary files. The example market/strategy are illustrative, not a recommendation. Never put a literal key in these commands.

Fetch public catalog and one series; do not repeat these commands in candidate loops:

```bash
set -euo pipefail
BFF_BASE_URL='https://beta.alphaengine.trade'
SEARCH_DIR=$(mktemp -d "${TMPDIR:-/tmp}/alphaengine-search.XXXXXX")
MARKET_KEY='susde'
TIMEFRAME='hourly' # use 'daily' for 1D
curl --fail-with-body --silent --show-error \
  "$BFF_BASE_URL/api/app/markets" --output "$SEARCH_DIR/bff-markets.json"
jq -e --arg key "$MARKET_KEY" --arg timeframe "$TIMEFRAME" \
  '.status == "ok" and any(.data.markets[];
    .key == $key and .availableTimeframes[$timeframe] != null)' \
  "$SEARCH_DIR/bff-markets.json"
curl --fail-with-body --silent --show-error --get \
  "$BFF_BASE_URL/api/app/market-series" \
  --data-urlencode "marketKey=$MARKET_KEY" \
  --data-urlencode "timeframe=$TIMEFRAME" \
  --output "$SEARCH_DIR/market-series.json"
jq -e '.status == "ok" and .data.available == true and (.data.chart | length > 0)' \
  "$SEARCH_DIR/market-series.json"
```

The jq check must pass before using the series. Stop on curl failure; do not treat an error response as cached market data. Select the market from the catalog before using it; write source/fetch metadata to the cache manifest as described above.

Discover router IDs once with the key; configure `ALPHAENGINE_API_KEY` securely first. Never enable shell tracing or curl verbose output with the key:

```bash
ROUTER_BASE_URL='https://api-router.alphaengine.trade'
: "${ALPHAENGINE_API_KEY:?Configure the API key securely outside chat}"
case "$ALPHAENGINE_API_KEY" in
  *$'\r'*|*$'\n'*) printf '%s\n' 'Malformed API key' >&2; exit 1 ;;
esac
printf 'x-api-key: %s\n' "$ALPHAENGINE_API_KEY" | \
curl --disable --fail-with-body --silent --show-error \
  "$ROUTER_BASE_URL/v1/families/strategy-arena/markets" \
  --header @- \
  --output "$SEARCH_DIR/router-markets.json"
MARKET_ID=$(jq -er --arg key "$MARKET_KEY" \
  '[.data[] | select(.marketKey == $key)] |
    if length == 1 then .[0].marketId else error("Expected one market") end' \
  "$SEARCH_DIR/router-markets.json")
```

Check that discovery returned exactly one intended market with matching chain/address. Fetch needed strategy details and parameters once from the documented GETs before testing. No simulation request should run if discovery or validation failed.

## Prepare and Export Candidates

Follow [candidate validation](candidate-validation.md) using the runtime already available to the agent. Python is optional. If Python 3 is available, use `scripts/prepare_candidate.py` from this installed skill folder; set `SKILL_DIR` to its actual location. Import its `prepare_candidate` function in a candidate loop or use its CLI. The helper is offline and consumes a draft API request, cached router market response, and a map from strategy IDs to their cached `/parameters` responses. For every component, it fills documented defaults, overlays explicit values, and rejects missing/unknown parameters, invalid types, non-finite values, bounds/enums and invalid weights. It does not own strategy cross-field rules or private codec validation; server validation remains authoritative.

Fetch each needed schema once. For this example, cache RSI metadata and build the schema map:

```bash
printf 'x-api-key: %s\n' "$ALPHAENGINE_API_KEY" | \
curl --disable --fail-with-body --silent --show-error \
  "$ROUTER_BASE_URL/v1/families/strategy-arena/strategies/yield-rsi/parameters" \
  --header @- --output "$SEARCH_DIR/params-yield-rsi.json"
jq -n --slurpfile rsi "$SEARCH_DIR/params-yield-rsi.json" \
  '{"yield-rsi": $rsi[0]}' > "$SEARCH_DIR/schemas.json"
```

Build an illustrative complete baseline, then validate it against the fetched schema. Future defaults must come from metadata rather than this example. A draft may omit defaulted parameters; only the helper's complete output is simulated:

```bash
: "${SKILL_DIR:?Set SKILL_DIR to the installed alphaengine-strategy-arena-agent folder}"
jq -n --argjson marketId "$MARKET_ID" --arg timeframe "$TIMEFRAME" \
  '{marketId: $marketId, timeframe: $timeframe, capital: "100000", components: [
    {strategyId: "yield-rsi", weightBps: 10000,
     strategyParams: {field: "logYield", window: 14, overbought: 70, oversold: 30}}
  ]}' > "$SEARCH_DIR/draft.json"
python3 "$SKILL_DIR/scripts/prepare_candidate.py" prepare \
  --candidate "$SEARCH_DIR/draft.json" --schemas "$SEARCH_DIR/schemas.json" \
  --markets "$SEARCH_DIR/router-markets.json" --output "$SEARCH_DIR/candidate.json"
```

Run the full simulation once, then evaluate its saved data. Pace these requests using the limits above; stop on any failed command or non-ok response:

```bash
printf 'x-api-key: %s\n' "$ALPHAENGINE_API_KEY" | \
curl --disable --fail-with-body --silent --show-error \
  "$ROUTER_BASE_URL/v1/families/strategy-arena/simulations" \
  --header @- -H 'content-type: application/json' \
  --data-binary "@$SEARCH_DIR/candidate.json" --output "$SEARCH_DIR/simulation.json"
jq -e '.status == "ok" and (.data | type == "object")' "$SEARCH_DIR/simulation.json"
jq '{simulation: .data}' "$SEARCH_DIR/simulation.json" > "$SEARCH_DIR/evaluation-request.json"
printf 'x-api-key: %s\n' "$ALPHAENGINE_API_KEY" | \
curl --disable --fail-with-body --silent --show-error \
  "$ROUTER_BASE_URL/v1/families/strategy-arena/evaluations" \
  --header @- -H 'content-type: application/json' \
  --data-binary "@$SEARCH_DIR/evaluation-request.json" --output "$SEARCH_DIR/evaluation.json"
jq -e '.status == "ok"' "$SEARCH_DIR/evaluation.json"
```

## Dashboard Output

Use dashboard shape, not the public API request: `marketKey`, `timeframe`, and `components` (`strategyId`, `weightBps`, `strategyParams`). Export from the saved request associated with the winning evaluation, retaining the exact ordered components and complete parameters:

```bash
python3 "$SKILL_DIR/scripts/prepare_candidate.py" export \
  --candidate "$SEARCH_DIR/candidate.json" --schemas "$SEARCH_DIR/schemas.json" \
  --markets "$SEARCH_DIR/router-markets.json" --output "$SEARCH_DIR/strategy.json"
```

In a real search, replace `candidate.json` with the winner's saved request. Export fails if it would need to add parameters after testing. It validates public metadata and shape, not proof that a simulation occurred, private codec acceptance, or a final score. If parameters change, prepare and simulate the changed candidate within budget before quoting a score for it. Keep the schemas used for that candidate; changed metadata is a new context, not an invisible upgrade.

Pin the actual tested market and timeframe so UI defaults cannot change the recommendation. Weights sum to `10000`; retain every tested parameter. Omit `config` unless required to reproduce supported dashboard inputs; it cannot override official scoring/execution. `SKILL.md` shows 1H output; this is an illustrative 1D shape, not a tested recommendation:

```json
{
  "marketKey": "susdf",
  "timeframe": "daily",
  "components": [
    {
      "strategyId": "yield-rsi",
      "strategyParams": { "field": "logYield", "window": 14, "overbought": 70, "oversold": 30 },
      "weightBps": 10000
    }
  ]
}
```

Report tested capital separately, along with eligibility, executed trades, skipped-signal reasons and sensitivity. Verify the exported components match the saved tested input. End the final recommendation with the exact simulation/private-scoring note in `SKILL.md` after any file links. Users review and submit themselves.

## Failures and Bounded Retries

- `401` / `AUTH_MISSING_API_KEY` / `AUTH_INVALID_API_KEY`: stop compute and follow the setup/replacement section above. Link the user to API-key settings, explain that regeneration replaces the old key, and resume only after they securely configure the full new value. Do not repeatedly retry the rejected key or rotate it automatically.
- `403` / `AUTH_INACTIVE_API_KEY` / `AUTH_INSUFFICIENT_SCOPE`: stop and explain the permission required.
- `429` / `RATE_LIMIT_EXCEEDED` or `RATE_LIMIT_CONCURRENCY_EXCEEDED`: inspect `Retry-After` and `x-ratelimit-limit`, `x-ratelimit-remaining`, `x-ratelimit-reset`. They accompany rejections; do not assume every success contains them. Honour the wait, pace the shared queue, and allow at most three retries of an otherwise valid request within the time budget. Stop if it remains blocked. An over-budget request must change before retrying.
- `REQUEST_VALIDATION_FAILED`: fix the structured `fieldErrors` (router) or `error.details` (BFF) before another attempt.
- `DATA_DATASET_NOT_FOUND`: record the market/timeframe dataset gap and stop that branch. Do not change timeframe silently.
- `STRATEGY_MISSING_REQUIRED_FEATURE`: record the support gap; skip that strategy for the affected dataset rather than retrying nearby parameters that require the same missing feature.
- `INTERNAL_UNEXPECTED`, unavailable upstream/auth services or other 5xx: retain the request ID and report the blocker. Do not run an automatic retry storm or invent results.
- DNS/TLS/network failures: distinguish sandbox/network permissions from origin reachability and TLS trust-store errors using the credential preflight. Never disable TLS verification. Stop unresolved automated calls and report the failing base; do not label transport failure as an invalid key. Offline reasoning may continue, clearly labelled as untested.

Match typed codes/statuses; never infer canonical failures from message strings. In request helpers, retain `httpStatus`, `code`, `requestId` and `fieldErrors` as structured data on the failure; do not serialize them into a generic exception and later parse its text. Candidate-helper errors are local validation codes, not server codes. If a simulation response was lost, a retry may recompute: account for that uncertainty and never claim an exact server execution count from client attempts alone.
