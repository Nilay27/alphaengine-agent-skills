# alphaengine-agent-skills

<div align="center">

Public agent skills for exploring AlphaEngine surfaces through Codex and Claude.

[![Codex](https://img.shields.io/badge/Codex-supported-black)](https://github.com/Nilay27/alphaengine-agent-skills)
[![Claude](https://img.shields.io/badge/Claude-supported-6C47FF)](https://github.com/Nilay27/alphaengine-agent-skills)
[![AlphaEngine API](https://img.shields.io/badge/API-public_router-0A7F5A)](https://github.com/Nilay27/api-router)
[![Pendle](https://img.shields.io/badge/Domain-Pendle_yield_trading-1E90FF)](https://docs.pendle.finance/)

</div>

This repo publishes shared public agent skills for AlphaEngine.

The first live skill, `alphaengine-strategy-arena-agent`, teaches agents how to:
- query AlphaEngine's public `api-router`,
- explore the Pendle yield strategy catalog,
- analyse cached market snapshots on hourly or daily timelines,
- run simulations and evaluations,
- compare candidates using the beta scoring model,
- search broadly without collapsing everyone onto the same canned ideas.

It is intentionally **not** a recipe book for guaranteed winners.

## Quick Links

- [What You Get](#what-you-get)
- [How It Works](#how-it-works)
- [Install](#install)
- [Current Public API Scope](#current-public-api-scope)
- [Why Pendle](#why-pendle)
- [Search Philosophy](#search-philosophy)
- [Repo Layout](#repo-layout)

## What You Get

With the current skill, an agent can:
- enumerate the live strategy arena catalog,
- inspect parameter schemas and surfaced defaults,
- inspect available markets and discover usable `marketId` values,
- fetch public historical market data only when needed and reuse it locally,
- run compact, trade-focused, or full simulation requests,
- understand why signals may be skipped under the official arena guardrails,
- run evaluation requests over full simulation payloads,
- sort candidates by `evaluation.data.score`,
- explain tradeoffs using return, drawdown, CVaR, turnover, cost, and eligibility,
- return paste-ready strategy JSON for `beta.alphaengine.trade` when a user asks what to submit.

This is useful for:
- fast exploration of Pendle yield strategies,
- comparing different combinations and parameter sets,
- building UI-side workflows on top of the same public API,
- letting users or AI agents spend real search effort instead of following a fixed template.

## How It Works

```mermaid
flowchart LR
    A[User question] --> B[Use cached context or fetch missing market data once]
    B --> C[Explain market or form diverse hypotheses]
    C --> D[Bounded search using cached catalogs and parameters]
    D --> E[POST full simulation once per new candidate]
    E --> F[POST evaluation using saved simulation]
    F --> G[Compare scores and diagnostics]
    G --> H[Adapt combinations and refine within budget]
    H --> D
```

This diagram illustrates a search, not a mandatory sequence for every question. General explanations need no network calls or simulation; market analysis uses the public BFF GETs only as needed. Simulation and evaluation use the authenticated public `api-router`.

The skill does **not** require the thin client. Use a confirmed reachable router base URL and a valid `x-api-key` for compute. The previously advertised `https://api-router.alphaengine.trade` failed DNS resolution in the October 2026 client check; this instruction update does not deploy or repair that hostname. Report connectivity failures and obtain the correct public base rather than bypassing authentication through dashboard POSTs.

## Install

### Codex

Use the Codex skill installer against this repo and install the skill path:

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo Nilay27/alphaengine-agent-skills \
  --path skills/alphaengine-strategy-arena-agent
```

After installation, start a fresh Codex session if your client does not auto-refresh skills.

### Claude

Claude can use the same shared skill folder directly. Install by copying the skill directory into your Claude skills directory:

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/Nilay27/alphaengine-agent-skills.git /tmp/alphaengine-agent-skills
cp -R /tmp/alphaengine-agent-skills/skills/alphaengine-strategy-arena-agent ~/.claude/skills/
```

If you prefer project-local installation, copy the same folder into:

```text
.claude/skills/alphaengine-strategy-arena-agent
```

After installation, start a fresh Claude session if your client does not auto-refresh skills.

## Current Public API Scope

The shipped skill assumes AlphaEngine's public router currently exposes:
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

All listed `/v1` requests are authenticated with:
- header: `x-api-key`

For historical market analysis, the skill additionally uses these existing anonymous GETs at `https://beta.alphaengine.trade`:

- `GET /api/app/markets`
- `GET /api/app/market-series?marketKey={key}&timeframe=hourly` (or `daily`)

Fetch the catalog once when needed and each relevant market/timeframe series once per search; save successful responses and snapshot metadata in a temporary directory. Reuse them for local analysis and candidate generation. Fetch again only for missing/corrupt data, another market/timeframe, an explicit refresh or a detected dataset change. These BFF reads have no per-user BFF HTTP limiter; this is agent guidance, not an enforced quota. Never send the API key with these reads.

Current public arena assumptions:
- callers discover `marketId` from `GET /v1/families/strategy-arena/markets`
- numeric `marketId` values are deployment config, so agents should not hardcode them
- callers send `capital` as a decimal string and typically start with `weightBps: 10000` for single-strategy baselines
- callers do not submit internal dataset or component identifiers; the server resolves them internally
- callers may use `strategyParams: {}` when strategy metadata surfaces defaults
- both `hourly` (1H) and `daily` (1D) are supported; send the chosen timeframe explicitly, and read returned dataset/execution/scoring profiles rather than assuming fixed warmup/scoring windows
- for official score comparisons, save a full `/simulations` result and pass its `simulation.data` to `/evaluations`; summary/trades views cost the same simulation CU and cannot be evaluated directly
- the server-owned arena guardrails can block trades even when signals are present
- dashboard recommendations pin the tested `marketKey` and `timeframe`, retain tested components/parameters, and use weights summing to `10000`; the UI can fill `config`
- some strategies may still fail with `STRATEGY_MISSING_REQUIRED_FEATURE` because the current arena dataset/profile does not provide every required feature family

The skill does **not** assume any public ranking endpoint exists.

### Default Compute Limits

| Operation or limit | Default |
|---|---:|
| Shared budget per API key | 50 CU per fixed one-second window |
| Authenticated GET | 1 CU |
| Simulation, any view | 10 CU per component |
| Evaluation | 1 CU |
| Concurrent simulations / evaluations | 2 / 4 |

Limits currently operate per key within each router process, with no daily quota from this limiter; configured key-specific limits may differ. A three-component simulation plus evaluation costs 31 CU. Five components consume 50 CU, so the evaluation needs a later window; more than five cannot fit a default single request. Start with one simulation in flight, pace the shared queue, deduplicate candidates, and honour bounded `Retry-After` handling. See [API workflow](./skills/alphaengine-strategy-arena-agent/references/api-workflow.md) for details and failure codes.

Choose a finite task budget: up to 100 unique simulations is a reasonable initial open-ended search, not a required target or server quota. Allocate it adaptively across requested markets and timeframes, and stop at sufficient evidence or diminishing improvements. A deeper search may use more when requested. Explain trials used and report the best tested result rather than claiming a guaranteed optimum.

## Example Usage

Example prompt:

```text
Use the alphaengine-strategy-arena-agent skill with my securely configured API key and a confirmed reachable public router base URL.
Analyse the relevant cached hourly or daily market data, explore plausible categories and combinations, then refine promising candidates within a finite budget.
Optimize for evaluation.data.score and show the supporting diagnostics.
```

For normal public usage, point the skill at the deployed AlphaEngine API endpoint.

The `http://localhost:8080` form is only for:
- AlphaEngine maintainers,
- contributors testing against a locally running `api-router`.

## Example Evaluation Shape

The skill is optimized around the current beta evaluation response shape.

Important fields under `evaluation.data` include `score`, `scenarioResult` (return/risk/cost diagnostics), `eligibility`, and `capitalScore`.

Illustrative excerpt from `evaluation.data`; other response fields are omitted:

```json
{
  "score": 12.575,
  "primaryScoreKind": "benchmark_adjusted_score",
  "scenarioResult": {
    "utilityScore": 0.12574986621080966,
    "annualizedMeanReturn": 0.13384547326881926,
    "maxDrawdown": 0.0003996003996003769,
    "cvar": 0.0003996003996003996,
    "turnover": 0.023333333333333334,
    "executionCost": 0.00005664601904857751
  },
  "eligibility": {
    "eligible": true,
    "reasons": []
  }
}
```

In beta, the main leaderboard key is:
- `evaluation.data.score`

The primary score is the returned benchmark-adjusted score. Raw utility remains a diagnostic under the scenario result.

## Why Pendle

Pendle is a yield-trading protocol built around tokenized principal and yield exposure.

Useful context:
- [Pendle Docs](https://docs.pendle.finance/)
- [Pendle Yield Tokenization](https://docs.pendle.finance/pendle-v2/ProtocolMechanics/YieldTokenization/Minting)

The skill uses a practical intuition:
- **PT** behaves like the principal or zero-coupon leg,
- **YT** behaves like the stripped yield or coupon leg,
- Pendle opportunities often fall into `technical-analysis`, `convergence`, `relative-value`, `curve`, and `liquidity` categories.

The full Pendle/PT/YT reasoning lives in:
- [pendle-intuition.md](./skills/alphaengine-strategy-arena-agent/references/pendle-intuition.md)

## Platform Compatibility

This repo is designed around the shared skill layout both Codex and Claude understand:
- one skill directory,
- one `SKILL.md`,
- optional `references/` files.

The skill body is shared. There is no separate Codex-vs-Claude version of the strategy-arena skill.

Platform-specific differences are limited to:
- install location,
- discovery/refresh behavior,
- optional repo-level guidance files such as `AGENTS.md` and `CLAUDE.md`.

## Search Philosophy

This repo deliberately avoids publishing a short list of "best" strategy combinations.

The skill is designed to create differentiated outcomes by teaching agents:
- how to explore the search space,
- how to compare candidates,
- how to reject weak or fragile ideas,
- how to use score plus diagnostics,
- how to spend search budget in stages.

These are broad search heuristics, not a fixed sequence or identical recipe for every user. More effort can improve the tested result, but repeated historical optimisation can overfit and does not guarantee future performance.

## What The Skill Does Not Do

It does not:
- call private AlphaEngine operator/runtime modules,
- invent unsupported endpoints,
- assume cross-submission ranking exists,
- claim that one Pendle strategy family is always best,
- replace human review of promising candidates.

## Repo Layout

- `skills/alphaengine-strategy-arena-agent/SKILL.md`: shared installable agent skill
- `skills/alphaengine-strategy-arena-agent/references/api-workflow.md`: public API usage rules
- `skills/alphaengine-strategy-arena-agent/references/pendle-intuition.md`: Pendle/PT/YT intuition and STRIPS-style analogy
- `skills/alphaengine-strategy-arena-agent/references/search-playbook.md`: broad search process and anti-convergence guidance
- `CLAUDE.md`: repo-level Claude guidance for maintaining cross-platform skill compatibility
- `docs/development-log.md`: repo change log
