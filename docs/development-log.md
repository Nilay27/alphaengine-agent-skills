# Development Log

## 2026-10-23

- Updated the shared skill and all three references for current hourly/daily arena support, explicit timeframe output, returned dataset/execution/scoring profiles, and server-owned computation.
- Added existing anonymous BFF market catalog/series GETs, fetch-once temporary caching, snapshot-aware result reuse and ordered candidate deduplication. Kept API keys restricted to the confirmed authenticated router origin.
- Documented current default compute costs (50 CU/second, reads/evaluations 1 CU, simulation 10 CU/component), concurrency ceilings (2 simulations/4 evaluations), fixed-window/per-process accounting, five-component constraints and bounded typed-error retry handling.
- Replaced the automatic summary-then-full search path with saved full simulation/evaluation reuse when comparing official scores; summary/trades remain available when those views alone are needed.
- Added flexible market-informed exploration, combinations, deeper refinement, sensitivity checks and finite task budgets, without a prescribed winning recipe. Final recommendations pin tested market/timeframe and disclose trial counts, diagnostics and limits.
- Updated README capabilities, examples and workflow. Documented the previously reported router-hostname DNS failure as an unresolved connectivity prerequisite; no backend, DNS, deployment or installed skill copies were changed.
- Validation: checked endpoint/auth/response examples against `api-router/src/routes/`, `src/contracts/v1/strategyArena.ts`, `src/middleware/`, `src/rateLimit/`, BFF `src/createServer.ts` and `src/services/dashboardCompatService.ts`, and `simulation-service/src/arena/officialArena.ts`. Passed the skill validator using cached PyYAML, local-reference/JSON/shell-syntax checks, and eight offline HTTP-example fixture flows covering hourly/daily success and stopping on transport, catalog, availability, duplicate-ID and simulation-response failures. Verified saved-payload evaluation and credential separation without live compute, network calls or real keys; `git diff --check` passed.

## 2026-04-26

- Updated `alphaengine-strategy-arena-agent` for arena-final market and scoring behavior.
- Clarified that live markets must be discovered from `GET /v1/families/strategy-arena/markets`; expected beta market keys may include `susde`, `susdf`, and `ghousd`, but numeric IDs are not stable guidance.
- Replaced stale "last 30 bars" scoring-window guidance with server-owned scoring-profile guidance for 30 warmup bars plus roughly 60 scored/evaluation bars.
- Added Final Strategy Output Mode for "give me a strategy" and similar submit-intent requests.
- Documented minimal paste-ready dashboard JSON and the UI's self-validating defaults for `marketKey`, `timeframe`, and `config`.
- Clarified that `evaluation.data.score` is the scaled public leaderboard score while raw utility remains diagnostic.

## 2026-04-16

- Initialized `alphaengine-agent-skills` as a public GitHub-installable skill repo.
- Added repo-level `AGENTS.md` to lock public-boundary and anti-convergence rules.
- Added first public skill: `alphaengine-strategy-arena-agent`.
- Split supporting knowledge into three references:
  - public API workflow,
  - Pendle intuition,
  - strategy search playbook.
- Added cross-platform packaging guidance so the same shared skill can be installed in both Codex and Claude.
- Added root `CLAUDE.md` and dual install instructions in `README.md`.
- Chose to keep the repo as a plain shared skill repo instead of a Claude marketplace repo so the structure stays equally natural for Codex and Claude users.
- Refreshed the README with richer Markdown structure:
  - hero and platform badges,
  - quick links,
  - workflow diagram,
  - example evaluation block,
  - Pendle links and context,
  - clearer sectioning for public users.

## 2026-04-22

- Refreshed `alphaengine-strategy-arena-agent` to match the current public `api-router` arena contract.
- Removed stale guidance that told users to submit raw `datasetRef` or caller-owned execution config.
- Added current public response-view guidance for:
  - `/simulations`,
  - `/simulations/summary`,
  - `/simulations/trades`.
- Made market discovery explicit so first-time users know `marketId` comes from `GET /v1/families/strategy-arena/markets`.
- Corrected evaluation examples to post `{ "simulation": simulation.data }`.
- Documented current arena support caveat that some strategies still fail with `STRATEGY_MISSING_REQUIRED_FEATURE` when the server dataset/profile lacks required feature families.

- Added first-time-user guidance for the public arena request flow:
  - where `marketId` comes from,
  - why `capital` is a string,
  - why `weightBps: 10000` is the default single-strategy baseline,
  - and why `/evaluations` needs the full `/simulations` payload rather than the summary/trades views.
- Documented the current official arena guardrail values and explained them in plain language for non-DeFi-native users.
- Added explicit guidance for interpreting blocked trades via `skipped_signal` events and `skippedByReason` diagnostics.
- Added explicit explanation of the current scored-window policy and `resolvedScoringProfile` fields.
