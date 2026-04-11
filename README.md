# git-n-rust-skills

> A personal skills library for building **Stageira** — a local-first git repository analytics tool built in Rust.
> Connect all skills to your AI coding agent with a single command.

[![License: Personal](https://img.shields.io/badge/License-Personal%20Use-red.svg)](./LICENSE)

---

## What Is This?

This repo is a collection of **SKILL.md files** — structured instruction documents that teach AI coding agents (Claude, Cursor, Windsurf, etc.) how to work on specific parts of the Stageira project.

Instead of re-explaining your architecture every session, each skill permanently encodes:
- **What** a module does
- **How** to implement it (with real code patterns)
- **When** to use it (trigger phrases the agent matches)

---

## Quick Start — Project-Level Skills (Claude Code, Codex, Cursor)

The easiest way to activate the skills is to add them directly to your project. This generates instruction files that agents will auto-discover — no background MCP server needed. The script will automatically pull the absolute latest skill definitions directly from GitHub, so there are never any outdated NPM caches!

```bash
npx git-n-rust-skills
```

This creates:

| Agent | Files Generated | How the Agent Uses Them |
|-------|----------------|------------------------|
| **Claude Code** | `CLAUDE.md` | Auto-reads on session start; matches request to the skills in `.rustskills/` |
| **Codex & Others** | `AGENTS.md` | Reads hierarchically; loads full instructions per skill from `.rustskills/` |

Both configuration files point to a single unified **`.rustskills/`** folder containing all your agent markdown instructions.

Commit these files (`CLAUDE.md`, `AGENTS.md`, and `.rustskills/`) to your repo so every teammate's agent gets the skills automatically out of the box!

---

## Supported Coding Agents

| Agent | Method | Status |
|-------|--------|--------|
| Claude Desktop | MCP Server | ✅ Supported |
| Claude Code | Project files (`.claude/`) | ✅ Supported |
| Cursor | MCP Server | ✅ Supported |
| Windsurf | MCP Server | ✅ Supported |
| VS Code + Cline | MCP Server | ✅ Supported |
| Zed | MCP Server | ✅ Supported |
| Continue.dev | MCP Server | ✅ Supported |
| OpenAI Codex CLI | Project files (`.codex/`) | ✅ Supported |
| Antigravity (Gemini) | MCP Server | ✅ Supported |

---

## What Your Agent Can Do After Activation

Every MCP-connected agent gets **4 new tools**:

```
list_skills()                      → browse all skills by category
search_skills("code churn")        → find the right skill by keyword
read_skill("git-internals-master") → load full instructions for a skill
reload_skills()                    → pull latest skills from GitHub
```

**Example session:**

> You: *"Help me implement bus factor calculation"*
>
> Agent: calls `search_skills("bus factor")` → finds `software-metrics`
> → calls `read_skill("software-metrics")` → follows the implementation guide

For **Claude Code** and **Codex**, the agent reads the skill index on session start and loads the matching rule file directly from the `.rustskills/` directory — no tool calls needed.

---

## Skill Categories

```
git-n-rust-skills/
│
├── 00-productivity-meta/       AI workflow speedups
│   ├── token-saver/            Read codebases using 10-20x fewer tokens
│   ├── binary-tree-analyzer/   Divide-and-conquer file traversal
│   └── task-orchestrator/      Decompose requirements into agent tasks (anti-hallucination)
│
├── 01-core-systems/            Git + Rust + Polars foundation
│   ├── git-internals-master/   .git/ parsing, commit graph walking (libgit2 / gitpython)
│   └── data-processing-polars/ Analytics: churn, bus factor, temporal coupling
│
├── 02-analytics-engineering/   Metrics algorithms
│   ├── software-metrics/       churn.py, bus_factor.py, temporal_coupling.py
│   └── statistical-analysis/   Trend detection, period comparison, anomaly detection
│
├── 03-cli-devx/                CLI UX + config
│   └── cli-design/             Typer commands (analyze, compare, export) + stageira.toml
│
├── 04-system-integration/      File-based exports (no APIs)
│   ├── cicd-pipelines/         GitHub Actions: test + release workflows
│   └── file-based-integration/ Datadog, Prometheus, Slack without any API keys
│
├── 05-performance/             Speed + memory for monorepos
│   ├── large-repo-optimization/ Parallel processing, lazy loading, streaming
│   └── benchmarking/           Profiler, memory tracker, cargo bench
│
├── 06-enterprise-security/     Offline-first + compliance
│   └── security-first-design/  Offline validator, compliance checker, air-gapped deployment
│
├── 07-testing-reliability/     Tests + fuzzing
│   ├── python-testing/         pytest patterns, fixtures, coverage targets
│   └── fuzz-testing/           cargo-fuzz (Rust) + Hypothesis (Python)
│
├── 08-devops-release/          Publishing + distribution
│   ├── ci-cd-setup/            .github/workflows/ (test.yml + release.yml)
│   └── distribution/           crates.io, Homebrew formula, PyPI
│
├── 09-product-monetization/    Pricing + positioning
│   ├── pricing-strategy/       Free / Pro / Enterprise tiers (tiers.json)
│   └── saas-positioning/       Local-first messaging vs GitHub Insights, SonarQube
│
├── 10-go-to-market/            Marketing templates
│   ├── content-engineering/    Hacker News post, technical blog template
│   └── b2b-outreach/           Cold email template for CTOs
│
└── 11-project-management/      GitHub Issues workflow
    └── github-issues-system/   Labels, milestones, issue templates, triage rhythm
```

---

## Add a New Skill

```powershell
# Generate boilerplate for a new skill
python skill-creator/generate_skill.py 01-core-systems my-new-skill
```

This creates the full folder structure:

```
01-core-systems/my-new-skill/
├── SKILL.md          ← Fill in name, description, instructions
├── run.sh            ← Entry point
├── requirements.txt
├── src/__init__.py
├── src/main.py
├── tests/
└── docs/QUICK_START.md
```

Edit `SKILL.md`, push, then tell your agent:

```
reload_skills()
```

---

## How Skills Are Triggered

Each `SKILL.md` starts with a YAML block:

```yaml
---
name: software-metrics
description: Implement code churn, bus factor, temporal coupling...
  Triggers on "code churn", "bus factor", "metrics"...
---
```

The agent reads the `description` field of every skill and matches it to your request. **The more specific your description, the more reliably it triggers.**

---

## Deactivate

To remove all the skills from your project, simply delete the generated index files and the skills folder:
```bash
rm -rf .rustskills/ CLAUDE.md AGENTS.md
```
That's it! Your agent will no longer read the local Stageira knowledge base.

---

## Test Without an Agent

Verify all skills are readable before opening any editor:

```powershell
python mcp_server/test_server.py
```

---

## License

[Personal Use Only](./LICENSE) — not for commercial use or redistribution.
