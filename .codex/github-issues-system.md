---
name: github-issues-system
description: Design and maintain Stageira's GitHub Issues workflow: labels, milestones, issue templates, project boards, and triage rhythm. Use when setting up project management, creating issue templates, writing label configs, planning milestones, or establishing a triage process. Triggers on \"github issues\", \"labels\", \"milestones\", \"issue template\", \"project board\", \"triage\", \"backlog\", or \"release planning\".
---


# GitHub Issues System — Stageira Project Management

Stageira uses GitHub Issues as its lightweight, enterprise-trustworthy project management layer.

## Label System

### Area labels
```
area: analytics    → metrics algorithms, Polars
area: cli          → CLI commands, UX
area: export       → JSON/CSV/Datadog/Prometheus output
area: ci-cd        → GitHub Actions, cargo-release
area: security     → offline validator, compliance
area: docs         → README, QUICK_START, blog posts
```

### Type labels
```
type: bug          → something broken
type: feature      → new capability
type: chore        → maintenance, deps, refactor
type: perf         → performance or memory improvement
type: question     → unclear, needs discussion
```

### Tier labels
```
tier: enterprise   → features for enterprise buyers
tier: pro          → Pro tier features
tier: oss          → Free / open source tier
```

## Milestones = Release Gates

```
v0.1 — MVP (current)
  Core: commit scanning, churn, bus factor
  Export: JSON, CSV
  CLI: analyze command
  
v0.2 — Pro Foundation
  compare command (period-over-period)
  Anonymized reports
  Temporal coupling
  Datadog + Prometheus export
  
v1.0 — Enterprise Ready
  SSO/SAML hooks
  Configurable alerts + webhook
  Web dashboard
  Compliance documentation
```

## Issue Template: Feature Request

```markdown
---
name: Feature Request
about: Suggest a new Stageira feature
labels: type: feature
---

## What metric / output changes?
<!-- Be specific: "add temporal coupling to the JSON output" not "more metrics" -->

## Which tier benefits?
- [ ] Free (OSS)
- [ ] Pro ($49/month)
- [ ] Enterprise (custom)

## Acceptance criteria
<!-- Example: "`stageira analyze` returns bus factor in <2s on a 100k-commit repo" -->
1. 
2. 

## Alternatives considered
<!-- Did you look at building this differently? -->
```

## Issue Template: Bug Report

```markdown
---
name: Bug Report
about: Something isn't working
labels: type: bug
---

## Command run
```bash
stageira analyze /path/to/repo
```

## Expected behavior

## Actual behavior

## Error output (if any)
```

## Environment
- OS:
- Stageira version (`stageira --version`):
- Repo size (approx. commits):
```

## Triage Rhythm (Weekly)

1. Label all new unlabeled issues
2. Assign to a milestone or "Backlog"
3. Move stale "In Progress" back to Backlog
4. Close issues invalidated by merged PRs

## Commit Linking Rules

- ✅ Use `Relates to #12` in commits — keeps issue open until release time
- ❌ Avoid `Closes #12` in commits — closes prematurely (issue shows "done" before users get it)
- ✅ Use `Closes #12` only in the release commit or tag message

## Parking Lot Issue

Create one issue titled "💡 Ideas / maybe later" with a checkbox list:
```markdown
- [ ] Web dashboard (v0.2)
- [ ] VS Code extension
- [ ] GitLab CI native integration
```
Promote items to real issues when serious, not before.
