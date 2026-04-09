# git-n-rust-skills

> Skill library for building **Stageira** — a local-first git repository analytics tool.
> No GitHub API. No data exfiltration. Single Rust binary.

## Directory Map

```
git-n-rust-skills/
├── skill-creator/               ← Bootstrap new skills (generate_skill.py)
│
├── 00-productivity-meta/        ← AI dev workflow speedups
│   ├── token-saver/             ← 10-20x token reduction protocol
│   └── binary-tree-analyzer/   ← Efficient codebase traversal
│
├── 01-core-systems/             ← Git + Rust + Polars foundation
│   ├── git-internals-master/   ← .git/ parsing, scanner.py, objects.py
│   └── data-processing-polars/ ← Analytics: churn, bus factor, temporal coupling
│
├── 02-analytics-engineering/    ← Metrics algorithms
│   ├── software-metrics/       ← churn.py, bus_factor.py, temporal_coupling.py
│   └── statistical-analysis/   ← trends.py, anomalies.py
│
├── 03-cli-devx/                 ← CLI UX + config
│   └── cli-design/             ← Typer commands: analyze, compare, export
│                                  + stageira.toml config system
│
├── 04-system-integration/       ← File-based exports (no APIs)
│   ├── cicd-pipelines/         ← GitHub Actions: test.yml + release.yml
│   └── file-based-integration/ ← Datadog, Prometheus, Slack webhook
│
├── 05-performance/              ← Speed + memory for monorepos
│   ├── large-repo-optimization/ ← Parallel, lazy, streaming
│   └── benchmarking/           ← profiler.py, memory_tracker.py
│
├── 06-enterprise-security/      ← Offline-first + compliance
│   └── security-first-design/  ← offline_validator.py, compliance_checker.py
│
├── 07-testing-reliability/      ← Tests + fuzzing
│   ├── python-testing/         ← pytest patterns, fixtures, coverage
│   └── fuzz-testing/           ← cargo-fuzz + Hypothesis
│
├── 08-devops-release/           ← Publishing + distribution
│   ├── ci-cd-setup/            ← .github/workflows/
│   └── distribution/           ← crates.io, Homebrew, PyPI
│
├── 09-product-monetization/     ← Pricing + tiers
│   ├── pricing-strategy/       ← tiers.json (Free/Pro/Enterprise)
│   └── saas-positioning/       ← local-first.md messaging
│
├── 10-go-to-market/             ← Marketing + outreach
│   ├── content-engineering/    ← HN post, technical blog templates
│   └── b2b-outreach/           ← CTO cold email template
│
└── 11-project-management/       ← GitHub Issues + workflow
    └── github-issues-system/   ← SKILL.md + label_config.yml + issue templates
```

## Quick Reference: Most Critical Skills

| Priority | Skill | Why |
|----------|-------|-----|
| 1 | `01-core-systems/git-internals-master` | Core engine — replaces GitHub API |
| 2 | `01-core-systems/data-processing-polars` | Analytics layer |
| 3 | `02-analytics-engineering/software-metrics` | What to compute |
| 4 | `03-cli-devx/cli-design` | Customer-facing interface |
| 5 | `04-system-integration/file-based-integration` | How "integrations" work |

## Productivity Skills (Use First)

Before doing any large codebase analysis:

1. **`00-productivity-meta/token-saver`** — Read 15% of files, understand 95%
2. **`00-productivity-meta/binary-tree-analyzer`** — Divide-and-conquer traversal

## Create a New Skill

```bash
python skill-creator/generate_skill.py 01-core-systems my-new-skill
```

## The Data Flow

```
.git/objects/
    ↓ (scan_repo)
CommitRecord[]
    ↓ (records_to_dataframe)
Polars DataFrame
    ↓ (compute_churn / bus_factor / temporal_coupling)
MetricsReport
    ↓ (exporter)
JSON / CSV / Datadog / Prometheus
```

Everything runs locally. Zero network calls (except optional Slack webhook).
