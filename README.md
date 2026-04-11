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

## Quick Start — Activate All Skills in One Command

### Option A: MCP Server (Claude Desktop, Cursor, Windsurf, etc.)

Registers a background MCP server that gives every connected agent 4 new tools (`list_skills`, `search_skills`, `read_skill`, `reload_skills`).

```bash
npx -y github:sVm19/git-n-rust-skills
```

**Then restart your editor.** Done.

### Option B: Project-Level Files (Claude Code, Codex)

If you use **Claude Code** or **OpenAI Codex CLI**, you can generate project-level instruction files that agents auto-discover — no MCP server needed:

```bash
npx -y github:sVm19/git-n-rust-skills -- --init .
```

This creates:

| Agent | Files Generated | How the Agent Uses Them |
|-------|----------------|------------------------|
| **Claude Code** | `CLAUDE.md` + `.claude/rules/<skill>.md` | Auto-reads rules on session start; matches request → skill |
| **Codex** | `AGENTS.md` + `.codex/<skill>.md` | Reads hierarchically; loads full instructions per skill |

Commit these files to your repo so every teammate's agent gets the skills automatically.

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

For **Claude Code** and **Codex**, the agent reads the skill index on session start and loads the matching rule file directly — no tool calls needed.

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

To remove the skills, uninstall the python package:
```bash
pip uninstall git-n-rust-skills
```
And manually remove the `"stageira-skills"` entry from your agent's MCP JSON configuration file.

For project-level files, simply delete the generated `CLAUDE.md`, `AGENTS.md`, `.claude/`, and `.codex/` directories.

---

## Test Without an Agent

Verify all skills are readable before opening any editor:

```powershell
python mcp_server/test_server.py
```

---

## License

[Personal Use Only](./LICENSE) — not for commercial use or redistribution.
