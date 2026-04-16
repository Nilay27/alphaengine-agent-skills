# alphaengine-agent-skills

Public, installable agent skills for working with AlphaEngine surfaces across Codex and Claude.

Current published skill:
- `alphaengine-strategy-arena-agent`

## Purpose

This repo is for users who want agents to work with AlphaEngine directly.

The skill is meant to work against AlphaEngine's public router directly. It does not require the thin client, although users can still wrap the same endpoints in their own client or SDK if they prefer.

The current skill teaches agents how to:
- call AlphaEngine's public `api-router`,
- explore the Pendle yield strategy catalog,
- run simulations and evaluations,
- compare strategies using the beta scoring model,
- search broadly without collapsing everyone onto the same canned ideas.

It is intentionally **not** a recipe book for guaranteed winners.

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

## Current Scope

The shipped skill assumes AlphaEngine's public router currently exposes:
- `GET /v1/families`
- `GET /v1/families/strategy-arena`
- `GET /v1/families/strategy-arena/strategies`
- `GET /v1/families/strategy-arena/strategies/{strategyId}`
- `GET /v1/families/strategy-arena/strategies/{strategyId}/parameters`
- `GET /v1/families/strategy-arena/markets`
- `POST /v1/families/strategy-arena/simulations`
- `POST /v1/families/strategy-arena/evaluations`

The skill assumes requests are authenticated with:
- header: `x-api-key`

The skill does **not** assume any public ranking endpoint exists.

## How To Use The Skill

Typical usage:
1. point the agent at the AlphaEngine router base URL,
2. provide a valid API key,
3. ask it to explore the strategy arena,
4. let it search, simulate, evaluate, and compare ideas.

Example prompt:

```text
Use the alphaengine-strategy-arena-agent skill against https://api.alphaengine.dev with my x-api-key.
Explore the Pendle yield strategy catalog, test broad categories first, then refine promising candidates.
Optimize for evaluation.data.score and show the supporting diagnostics.
```

For normal public usage, point the skill at the deployed AlphaEngine API endpoint.

The `http://localhost:8080` form is only for:
- AlphaEngine maintainers,
- contributors testing against a locally running `api-router`.

## Search Philosophy

This repo deliberately avoids publishing a short list of "best" strategy combinations.

The skill is designed to create differentiated outcomes by teaching agents:
- how to explore the search space,
- how to compare candidates,
- how to reject weak or fragile ideas,
- how to use score plus diagnostics,
- how to spend search budget in stages.

That way, users who spend more effort should get better results.

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
