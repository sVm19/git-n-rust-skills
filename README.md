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

### Windows

```powershell
# Clone the repo (or use GitHub mode below — no clone needed)
git clone https://github.com/sVm19/git-n-rust-skills
cd git-n-rust-skills

# Activate for all detected coding agents
.\activate.git-n-rust-skills.ps1
```

### macOS / Linux

```bash
git clone https://github.com/sVm19/git-n-rust-skills
cd git-n-rust-skills
bash activate.git-n-rust-skills.sh
```

**Then restart your editor.** Done.

---

## GitHub Mode — No Clone Needed

Activate on any machine without cloning the repo first:

```powershell
# Windows — fetches skills directly from GitHub
.\activate.git-n-rust-skills.ps1 -GithubRepo "sVm19/git-n-rust-skills"
```

```bash
# macOS / Linux
bash activate.git-n-rust-skills.sh --github-repo sVm19/git-n-rust-skills
```

Skills are cached locally after the first fetch. When you push new skills to GitHub, your agent calls `reload_skills()` and gets them instantly — no restart needed.

---

## Supported Coding Agents

The activation script auto-detects which agents are installed and configures **all of them**:

| Agent | Status |
|-------|--------|
| Claude Desktop | ✅ Supported |
| Cursor | ✅ Supported |
| Windsurf | ✅ Supported |
| VS Code + Cline | ✅ Supported |
| Zed | ✅ Supported |
| Continue.dev | ✅ Supported |

---

## What Your Agent Can Do After Activation

Every connected agent gets **4 new tools**:

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

```powershell
# Remove from all agents
.\deactivate.git-n-rust-skills.ps1
```

---

## Test Without an Agent

Verify all skills are readable before opening any editor:

```powershell
python mcp_server/test_server.py
```

---

## License

[Personal Use Only](./LICENSE) — not for commercial use or redistribution.
