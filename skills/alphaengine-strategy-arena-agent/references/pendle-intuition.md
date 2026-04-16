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
