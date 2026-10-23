# Pendle Intuition

Pendle is a yield-trading protocol.

A useful mental model is that it is **similar to TradFi bond stripping / STRIPS**, but not identical.

## STRIPS-Style Analogy

In fixed income, stripping separates:
- the principal claim,
- from the interest or coupon claim.

Pendle is economically similar:
- **PT (Principal Token)** is closer to the principal / zero-coupon leg
- **YT (Yield Token)** is closer to the stripped yield / coupon leg

This is an analogy, not an identity:
- Treasury STRIPS come from fixed-income coupon cashflows
- Pendle comes from tokenized DeFi yield sources with expiry, AMM trading, rewards, and potentially variable yield

## Practical Math Intuition

1. **PT converges toward redemption value at maturity**
- PT often trades below redemption value before expiry
- this creates convergence-style opportunities

2. **YT captures future yield exposure**
- YT value depends on expected future yield, rewards, and points until expiry
- this makes it more sensitive to yield expectations

3. **Pendle opportunities are often category-shaped**
Useful categories include:
- `technical-analysis`
- `convergence`
- `relative-value`
- `curve`
- `liquidity`

4. **Cost and churn matter**
High turnover can destroy otherwise attractive raw-return ideas.
Do not optimize only for return.

## Interpreting the Cached Market Series

- Identify the instrument before interpreting a chart. These arena markets use Pendle PT market data; explaining YT does not imply the simulation is trading YT or a generic spot token.
- The public chart exposes OHLCV price fields and a separate `apy` field. Price changes and implied-yield/APY changes are different observations; check field units and metadata rather than presenting APY as token price or assuming a display percentage convention.
- Use the cached observation period to discuss trends, ranges, volatility and volume. These are historical snapshots, not guaranteed live quotes. Do not infer current liquidity, spreads or pool depth from volume alone; discuss liquidity only when the returned data/profile supports it.
- A rising implied yield is not automatically a rising PT price. Expiry, redemption denomination and the yield convention matter; explain the relationship qualitatively unless the inputs support a calculation.
- Keep 1H and 1D analysis explicit. A lookback or holding period in bars spans different elapsed time on each timeframe, and the official scoring window excludes the warmup specified in the response.
- Treat momentum, mean reversion, convergence and other categories as hypotheses motivated by observations, not certain winners. Only simulations/evaluations establish the tested score.

## Evaluation Metrics To Respect

For beta exploration, agents should inspect:
- annualized return,
- max drawdown,
- CVaR,
- turnover,
- execution cost,
- eligibility,
- score.

CVaR is the tail-risk measure in the evaluation breakdown.
