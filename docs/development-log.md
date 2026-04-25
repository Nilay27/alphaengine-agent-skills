# Development Log

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
