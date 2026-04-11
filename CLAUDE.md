# Stageira Skills

This project includes an AI skill library. Scoped rules live in `.claude/rules/` — Claude Code reads them automatically.

## Available Skills

- **binary-tree-analyzer** (00-productivity-meta): Read and analyze the Stageira project (or any uploaded codebase) using a binary tree divide-and-conquer traversal strate
- **project-architect** (00-productivity-meta): Read a project description in plain text or Markdown and produce a complete, grounded project structure (directory tree,
- **task-orchestrator** (00-productivity-meta): Read a project requirement carefully, decompose it into atomic sequential tasks, and write precise grounded prompts for 
- **token-saver** (00-productivity-meta): Slash token usage by 10-20x when analyzing, summarizing, or navigating the Stageira codebase. Use this skill immediately
- **data-processing-polars** (01-core-systems): Rust-first Polars DataFrames for Stageira's analytics engine. Use when computing churn, contributor stats, temporal patt
- **git-internals-master** (01-core-systems): Master skill for reading .git/ directory structure, walking commit graphs, extracting blobs/trees/diffs using libgit2 / 
- **software-metrics** (02-analytics-engineering): Implement and compute software engineering metrics for Stageira: code churn, bus factor, contribution distribution, temp
- **statistical-analysis** (02-analytics-engineering): Apply statistical methods to Stageira's git metrics: trend detection, time-series comparison (Q1 vs Q2), variance/anomal
- **cli-design** (03-cli-devx): Design and implement production-grade Stageira CLI commands using Typer (Python) and Clap (Rust). Use whenever building 
- **cicd-pipelines** (04-system-integration): Set up and configure GitHub Actions and GitLab CI pipelines for Stageira: multi-platform Rust builds, automated testing,
- **file-based-integration** (04-system-integration): Implement Stageira's file-based integration strategy: exporting metrics to Datadog, Prometheus, and Slack without using 
- **benchmarking** (05-performance): Measure and optimize Stageira's runtime performance and memory usage. Use when profiling slow analysis runs, measuring i
- **large-repo-optimization** (05-performance): Optimize Stageira's performance on massive git repos (100K+ commits, monorepos). Use when analyzing slow repositories, i
- **security-first-design** (06-enterprise-security): Implement and verify Stageira's offline-first, zero-data-exfiltration security architecture. Use when implementing any n
- **fuzz-testing** (07-testing-reliability): Apply fuzz testing to Stageira's git parsing code using cargo-fuzz (Rust) and Hypothesis (Python). Use when hardening ed
- **python-testing** (07-testing-reliability): Write and organize pytest tests for Stageira's Python analytics modules. Use when adding unit tests, integration tests, 
- **distribution** (08-devops-release): Handle Stageira's package distribution: publishing to crates.io, creating Homebrew tap formulas, and managing GitHub Rel
- **github-issues-system** (11-project-management): Design and maintain Stageira's GitHub Issues workflow: labels, milestones, issue templates, project boards, and triage r

## How To Use

Just describe what you need. Claude Code will match your request 
to the right skill via the rule files in `.claude/rules/`.
