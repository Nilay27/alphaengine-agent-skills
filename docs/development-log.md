# Development Log

## 2026-10-28 — Reliable strategy preparation and API-only operation

- Materialize every public strategy parameter from cached metadata before simulation, deduplication and export. Preserve explicit overrides, component order and the saved tested object; reject missing defaults and invalid metadata instead of inventing values. Add runtime-neutral candidate validation and an optional standard-library Python helper with structured local errors. Python is not an end-user requirement; agents use available JSON/runtime tools without installing a language runtime.
- Add private macOS Keychain and Windows PowerShell DPAPI setup, actual-process loading, boolean-only access verification and a preflight that separates local permissions, transport, authentication and scopes. Keep credentials out of command arguments, files containing plaintext secrets and logs; authenticated curl examples take headers through stdin.
- Prohibit all browser inspection/control in this skill, including setup and score investigation. Keep dashboard actions and submission with the user. Label public single-simulation scores separately from private correlated-market/perturbation/stress evaluation, require the agreed closing note, and avoid unsupported explanations of individual score discrepancies.
- State tested capital before searching; report eligibility, executed trades, skipped signals and sensitivity with the selected eligible result. Retain existing adaptive exploration, caching, snapshot/profile separation and compute limits.
- Contract references: `api-router/src/contracts/v1/strategyArena.ts`, `src/families/strategy-arena/publicCatalog.ts` (`min`/`max`/`enum`, surfaced defaults) and `evaluationAdapter.ts` (one-simulation score); `strategies-ts/spot-strategies/src/strategies/defaults.ts`; `simulation-service/src/usecases/validateSubmission.ts`; `mintlify-docs/arena/scoring-and-benchmarks.mdx`. No public API, strategy, execution or scoring formulas changed.
- Validation: 20 offline helper regression tests pass, covering omitted `numStd`, actual bounds, zero values, required/unknown parameters, invalid types/enums/non-finite values, capital/weights, unique market mapping, replay, unchanged export and structured CLI failures. Skill validator passes with PyYAML installed only in a temporary validation directory. Local references, three JSON examples, eleven Bash/zsh syntax checks and the mocked HTTP prepare/simulate/evaluate/export flow pass, including private header handling and a credential-loader fixture. macOS setup syntax was checked against native `security help`; Windows DPAPI/secure input guidance was checked against Microsoft documentation but has not been executed on Windows. No real credentials, browser sessions, live simulations or private submissions were used for validation.

## 2026-10-26 — Custom API hostname enabled

- Set `https://api-router.alphaengine.trade` as the documented agent compute base after owner DNS validation, ACM issuance and CloudFront certificate/alias attachment. Remove pending-domain guidance; retain credential-origin checks and no automatic cross-origin fallback. Existing keys, public API contracts and rate limits are unchanged.
- Verify HTTPS and typed missing-key 401, authenticated market discovery and one small single-component daily `yield-rsi` simulation on sUSDe. The simulation returned HTTP 200 in about 670 ms with request ID `f7d862e7-bd5f-45e2-9e5e-88bcc5f78e1b`. Validate the skill/references/examples and refresh the installed copy from the published update.

## 2026-10-26

- Set the current authenticated router base to `https://d2e5kbmhk8dosc.cloudfront.net` after the existing AWS ingress was connected to `/v1/*` and OpenAPI. Explain that the custom API hostname/profile label awaits DNS validation, while the same user key works at the current base. Preserve credential-origin checks, bounded search, caching and all existing compute limits.
- Verified a profile-generated user key against the public endpoint: market discovery and strategy parameters, full simulation plus evaluation for hourly and daily data, and public chart reads succeed. Missing/invalid keys return typed 401 errors, an over-budget request returns 429 with `Retry-After`, private routes return 404 and BFF market reads remain available. Two small simulation runs were used; no wallets or on-chain transactions were involved.
- Validate the skill structure, references, JSON/shell examples and diff; refresh the older local installation from the published skill. The branded API hostname remains pending its owner's DNS records and subsequent CloudFront certificate attachment.

## 2026-10-23

- Added direct API-key onboarding at `https://beta.alphaengine.trade/#profile/api-key` (with manual Profile -> Settings -> API keys fallback for older dashboard releases). Documented one-time copying, regeneration for an unsaved/invalid key, immediate replacement of the single active account key, and updating every integration. Invalid-key guidance links this setup view and resumes after secure configuration; network, quota and scope failures retain their own remedies. No recoverable-key/reveal backend is required. Paired dashboard coverage passes eight focused tests, type checking/build and signed-out in-app Browser checks; refreshed skill structure/reference/JSON/shell and diff checks pass locally.
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
